-- Create a list of runs that are valid for comparison by evaluation queries.
--
-- Runs from different configurations (distinguished by config.name = 'name' entries) that
-- are comparable are selected. We can (should) only work on a single experiment.
DROP FUNCTION IF EXISTS ijpp_run(exp_id UUID);
CREATE OR REPLACE FUNCTION ijpp_run(exp_id UUID)
RETURNS TABLE (
  id INTEGER,
  project_name VARCHAR,
  project_group VARCHAR,
  config VARCHAR
)
AS $BODY$ BEGIN
RETURN QUERY
  -- Filter runs that are bigger than the maximum valid rank.
  SELECT run_3.id, run_3.project_name, run_3.project_group, run_3.config FROM
  (
      -- Get the smallest maximum rank from previous window selection
      SELECT min(max_rank) OVER (PARTITION BY run_2.project_name, run_2.project_group) AS max_valid_rank, run_2.* FROM
      (
          -- Add column with the maximum rank within the partition, only get completed.
          SELECT max(rank) OVER (PARTITION BY run_1.project_name, run_1.project_group, run_1.config) AS max_rank, run_1.* FROM
          (
              -- Rank by configuration (Filtered by experiment, to speed things up)
              SELECT rank() OVER (PARTITION BY run.project_name, run.project_group, config_1.value ORDER BY run.begin),
                    run.id, run.project_name, run.project_group, run.status, config_1.value as config, run.run_group
              FROM run JOIN (SELECT * from config WHERE config.name = 'name') AS config_1 ON (run.id = config_1.run_id)
              WHERE run.experiment_group = exp_id
          ) as run_1 WHERE
          run_1.status = 'completed'
      ) as run_2
  ) as run_3
  WHERE
    run_3.rank <= run_3.max_valid_rank;
END $BODY$ LANGUAGE plpgsql;

-- Create the table of valid runs for ijpp evaluation.
--
-- For now this filters out all runs that are declared a 'baseline' run.
-- This is the case for some polybench project runs.
DROP FUNCTION IF EXISTS ijpp_valid_run(exp_id UUID);
CREATE OR REPLACE FUNCTION ijpp_valid_run(exp_id UUID)
RETURNS TABLE (
  id INTEGER,
  project_name VARCHAR,
  project_group VARCHAR,
  config VARCHAR
)
AS $BODY$ BEGIN
RETURN QUERY
  SELECT
    run_1.*
  FROM ijpp_run(exp_id) as run_1
       RIGHT JOIN config ON (run_1.id = config.run_id) AND
       config.name = 'baseline' AND config.value = 'False';
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_total_runtime(exp_id UUID);
CREATE OR REPLACE FUNCTION ijpp_total_runtime(exp_id UUID)
RETURNS TABLE(
  project VARCHAR,
  "group" VARCHAR,
  domain VARCHAR,
  config VARCHAR,
  "time" DOUBLE PRECISION,
  variants NUMERIC,
  cachehits NUMERIC,
  requests NUMERIC,
  blocked NUMERIC
)
AS $BODY$ BEGIN
RETURN QUERY
  SELECT
    rrun.project_name AS project,
    rrun.project_group AS "group",
    prj.domain AS "domain",
    rrun.config,
    SUM(COALESCE(r.duration / 1000000, metrics.value)) AS time,
    SUM(COALESCE(vars.duration, 0)) AS variants,
    SUM(COALESCE(chits.duration, 0)) AS cachehits,
    SUM(COALESCE(rqsts.duration, 0)) AS requests,
    SUM(COALESCE(blkd.duration, 0)) AS blocked
  FROM
         ijpp_valid_run(exp_id) AS rrun
    JOIN metrics ON (rrun.id = metrics.run_id)
    LEFT JOIN
         (SELECT * FROM regions WHERE regions.name = 'VARIANTS') AS vars ON (rrun.id = vars.run_id)
    LEFT JOIN
         (SELECT * FROM regions WHERE regions.name = 'CACHE_HIT') AS chits ON (rrun.id = chits.run_id)
    LEFT JOIN
         (SELECT * FROM regions WHERE regions.name = 'REQUESTS') AS rqsts ON (rrun.id = rqsts.run_id)
    LEFT JOIN
         (SELECT * FROM regions WHERE regions.name = 'BLOCKED') AS blkd ON (rrun.id = blkd.run_id)
    LEFT JOIN
         (SELECT * FROM regions WHERE regions.name = 'START') AS r ON (rrun.id = r.run_id)
    LEFT JOIN project AS prj ON (rrun.project_name = prj.name AND
                                 rrun.project_group = prj.group_name)
  WHERE
    metrics.name = 'time.real_s'
  GROUP BY
    rrun.project_name, rrun.project_group, prj.domain, rrun.config
  ORDER BY
    rrun.project_name, rrun.config;
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_region_wise(exp_id UUID);
CREATE OR REPLACE FUNCTION ijpp_region_wise(exp_id UUID)
RETURNS TABLE (
  project VARCHAR,
  "region" VARCHAR,
  "config" VARCHAR,
	"runtime" NUMERIC
)
AS $BODY$ BEGIN
RETURN QUERY
  SELECT
  rrun.project_name AS project,
  regions.name AS region,
  rrun.config AS config,
  SUM(regions.duration) AS runtime
  FROM ijpp_valid_run(exp_id) AS rrun
      LEFT JOIN regions ON (rrun.id = regions.run_id)
  WHERE
    regions.name != ALL ('{START, CODEGEN, CACHE_HIT, VARIANTS, REQUESTS, BLOCKED}'::VARCHAR[])
  GROUP BY
    rrun.project_name, regions.name, rrun.config
  ORDER BY project, region, config;
END $BODY$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS ijpp_db_export_per_config(exp_id UUID, configs VARCHAR[]);
CREATE OR REPLACE FUNCTION ijpp_db_export_per_config(exp_id UUID, configs VARCHAR[])
RETURNS TABLE (
	project    VARCHAR,
	"group"    VARCHAR,
        "function" VARCHAR,
	"ast" 	   VARCHAR,
	"schedule" VARCHAR,
        "stderr"   VARCHAR,
	"cfg"	   VARCHAR
)
AS $BODY$ BEGIN
RETURN QUERY
    SELECT DISTINCT
      project_name as project,
      project_group as "group",
      isl_asts.function as "function",
      isl_asts.ast,
      schedules.schedule,
      tiny_log.stderr AS stderr,
      config.value      AS cfg
    FROM run
      LEFT JOIN isl_asts ON (run.id = isl_asts.run_id)
      LEFT JOIN schedules ON (run.id = schedules.run_id)
      LEFT JOIN config ON (run.id = config.run_id)
      LEFT OUTER JOIN (
        SELECT log."run_id", CAST(left(log."stderr", 240) AS VARCHAR) as stderr FROM log
      ) AS tiny_log on (run.id = tiny_log.run_id)
    WHERE
      isl_asts.function = schedules.function AND
      config.value = ANY (configs) AND
      experiment_group = exp_id;
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_db_export(exp_id UUID);
CREATE OR REPLACE FUNCTION ijpp_db_export(exp_id UUID)
RETURNS TABLE(
  project            VARCHAR,
  "group"            VARCHAR,
  "function"         VARCHAR,
  "jit_ast"          VARCHAR,
  "jit_schedule"     VARCHAR,
  "jit_stderr"       VARCHAR,
  "polly_ast"        VARCHAR,
  "polly_schedule"   VARCHAR,
  "polly_stderr"     VARCHAR
)
AS $BODY$ BEGIN
RETURN QUERY
  SELECT
    COALESCE(t1."project", t2."project")   AS "project",
    COALESCE(t1."group", t2."group")       AS "group",
    COALESCE(t1."function", t2."function") AS "function",
    t1.ast                                 AS jit_ast,
    t1.schedule                            AS jit_schedule,
    t1.stderr                              AS jit_stderr,
    t2.ast                                 AS polly_ast,
    t2.schedule                            AS polly_ast,
    t2.stderr                              AS polly_stderr
  FROM
    ijpp_db_export_per_config(exp_id, '{PolyJIT}') AS t1
	FULL OUTER JOIN
    ijpp_db_export_per_config(exp_id, '{polly.inside}') AS t2
	ON (t1.project = t2.project AND
      t1."function" = t2."function");
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_runs_by_config(exp_id UUID, config_name VARCHAR);
CREATE OR REPLACE FUNCTION ijpp_runs_by_config(exp_id UUID, config_name VARCHAR)
RETURNS TABLE (
    id INTEGER,
    project_name VARCHAR,
    project_group VARCHAR,
    config VARCHAR
)
AS $BODY$ BEGIN
RETURN QUERY
    SELECT
    	run_1.id,
   		run_1.project_name,
      run_1.project_group,
      run_1.config
    FROM ijpp_valid_run(exp_id) as run_1
    WHERE
      run_1.config = config_name;
END $BODY$ language plpgsql;

DROP FUNCTION IF EXISTS ijpp_project_region_time(region_name VARCHAR, exp_id UUID, config_name VARCHAR);
CREATE OR REPLACE FUNCTION ijpp_project_region_time(region_name VARCHAR, exp_id UUID, config_name VARCHAR)
RETURNS TABLE (
  project_name VARCHAR,
  project_group VARCHAR,
  duration     NUMERIC
)
AS $BODY$ BEGIN
RETURN QUERY
  SELECT
    run_1.project_name,
    run_1.project_group,
    SUM(regions.duration)
  FROM
         ijpp_valid_run(exp_id)                    AS run_1
    JOIN ijpp_runs_by_config(exp_id, config_name)  AS run_2 ON (run_1.id = run_2.id)
    JOIN regions                                            ON (run_1.id = regions.run_id)
  WHERE
    regions.name = region_name
  GROUP BY
    run_1.project_name,
    run_1.project_group;
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_project_region_time_not_in(region_names VARCHAR[], exp_id UUID, config_name VARCHAR);
CREATE OR REPLACE FUNCTION ijpp_project_region_time_not_in(region_names VARCHAR[], exp_id UUID, config_name VARCHAR)
RETURNS TABLE (
  project_name VARCHAR,
  project_group VARCHAR,
  duration     NUMERIC
)
AS $BODY$ BEGIN
  RETURN QUERY
  SELECT
    run_1.project_name,
    run_1.project_group,
    SUM(regions.duration)
  FROM
         ijpp_valid_run(exp_id)                   AS run_1
    JOIN ijpp_runs_by_config(exp_id, config_name) AS run_2 ON (run_1.id = run_2.id)
    JOIN regions                                           ON (run_1.id = regions.run_id)
  WHERE
    regions.name != ALL (region_names)
  GROUP BY
    run_1.project_name,
    run_1.project_group;
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_total_dyncov(exp_id UUID);
CREATE OR REPLACE FUNCTION ijpp_total_dyncov(exp_id UUID)
RETURNS TABLE (
  project_name   VARCHAR,
  project_group  VARCHAR,
  ohcov_0   NUMERIC,
  ohcov_1   NUMERIC,
  ohcov_2   NUMERIC,
  dyncov_0   NUMERIC,
  dyncov_1   NUMERIC,
  dyncov_2   NUMERIC,
  cachehits_0 NUMERIC,
  cachehits_1 NUMERIC,
  cachehits_2 NUMERIC,
  variants_0 NUMERIC,
  variants_1 NUMERIC,
  variants_2 NUMERIC,
  blocked_0 NUMERIC,
  blocked_1 NUMERIC,
  blocked_2 NUMERIC,
  codegen_0   NUMERIC,
  codegen_1   NUMERIC,
  codegen_2   NUMERIC,
  scops_0   NUMERIC,
  scops_1   NUMERIC,
  scops_2   NUMERIC,
  t_0       NUMERIC,
  o_0       NUMERIC,
  t_1       NUMERIC,
  o_1       NUMERIC,
  t_2       NUMERIC,
  o_2       NUMERIC
  )
AS $BODY$ BEGIN
  RETURN QUERY
  SELECT
    T_0.project_name                              AS project_name,
    T_0.project_group                             AS project_group,
    (O_0.duration / T_0.duration * 100)           AS ohcov_0,
    (O_1.duration / T_1.duration * 100)           AS ohcov_1,
    (O_2.duration / T_2.duration * 100)           AS ohcov_2,
    (scops_0.duration / T_0.duration * 100)       AS dyncov_0,
    (scops_1.duration / T_1.duration * 100)       AS dyncov_1,
    (scops_2.duration / T_2.duration * 100)       AS dyncov_2,
    COALESCE(ch_0.duration, 0)                    AS cachehits_0,
    COALESCE(ch_1.duration, 0)                    AS cachehits_1,
    COALESCE(ch_2.duration, 0)                    AS cachehits_2,
    COALESCE(variants_0.duration, 0)              AS variants_0,
    COALESCE(variants_1.duration, 0)              AS variants_1,
    COALESCE(variants_2.duration, 0)              AS variants_2,
    COALESCE(B_0.duration, 0)                     AS blocked_0,
    COALESCE(B_1.duration, 0)                     AS blocked_1,
    COALESCE(B_2.duration, 0)                     AS blocked_2,
    COALESCE(codegen_0.duration, 0)               AS codegen_0,
    COALESCE(codegen_1.duration, 0)               AS codegen_1,
    COALESCE(codegen_2.duration, 0)               AS codegen_2,
    COALESCE(scops_0.duration, 0)                 AS scops_0,
    COALESCE(scops_1.duration, 0)                 AS scops_1,
    COALESCE(scops_2.duration, 0)                 AS scops_2,
    COALESCE(T_0.duration, 0)                     AS t_0,
    COALESCE(O_0.duration, 0)                     AS o_0,
    COALESCE(T_1.duration, 0)                     AS t_1,
    COALESCE(O_1.duration, 0)                     AS o_1,
    COALESCE(T_2.duration, 0)                     AS t_2,
    COALESCE(O_2.duration, 0)                     AS o_2
  FROM
              (SELECT * FROM ijpp_project_region_time('START',     exp_id, 'polly.inside.no-delin')) AS T_0
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('START',     exp_id, 'PolyJIT'))               AS T_1 ON (T_1.project_name = T_0.project_name AND T_1.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('START',     exp_id, 'polly.inside'))          AS T_2 ON (T_2.project_name = T_0.project_name AND T_2.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CODEGEN',   exp_id, 'polly.inside.no-delin')) AS codegen_0  ON (codegen_0.project_name = T_0.project_name AND codegen_0.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CODEGEN',   exp_id, 'PolyJIT'))               AS codegen_1  ON (codegen_1.project_name = T_0.project_name AND codegen_1.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CODEGEN',   exp_id, 'polly.inside'))          AS codegen_2  ON (codegen_2.project_name = T_0.project_name AND codegen_2.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CACHE_HIT', exp_id, 'polly.inside.no-delin')) AS ch_0       ON (ch_0.project_name = T_0.project_name AND ch_0.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CACHE_HIT', exp_id, 'PolyJIT'))               AS ch_1       ON (ch_1.project_name = T_0.project_name AND ch_1.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CACHE_HIT', exp_id, 'polly.inside'))          AS ch_2       ON (ch_2.project_name = T_0.project_name AND ch_2.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('VARIANTS',  exp_id, 'polly.inside.no-delin')) AS variants_0 ON (variants_0.project_name = T_0.project_name AND variants_0.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('VARIANTS',  exp_id, 'PolyJIT'))               AS variants_1 ON (variants_1.project_name = T_0.project_name AND variants_1.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('VARIANTS',  exp_id, 'polly.inside'))          AS variants_2 ON (variants_2.project_name = T_0.project_name AND variants_2.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CODEGEN',   exp_id, 'polly.inside.no-delin')) AS O_0 ON (O_0.project_name = T_0.project_name AND O_0.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CODEGEN',   exp_id, 'PolyJIT'))               AS O_1 ON (O_1.project_name = T_0.project_name AND O_1.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CODEGEN',   exp_id, 'polly.inside'))          AS O_2 ON (O_2.project_name = T_0.project_name AND O_2.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('BLOCKED',   exp_id, 'polly.inside.no-delin')) AS B_0 ON (B_0.project_name = T_0.project_name AND B_0.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('BLOCKED',   exp_id, 'PolyJIT'))               AS B_1 ON (B_1.project_name = T_0.project_name AND B_1.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('BLOCKED',   exp_id, 'polly.inside'))          AS B_2 ON (B_2.project_name = T_0.project_name AND B_2.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time_not_in('{START, CODEGEN, VARIANTS, CACHE_HIT, REQUESTS, BLOCKED}'::VARCHAR[], exp_id, 'polly.inside.no-delin'))
                                                                                                AS scops_0 ON (scops_0.project_name = T_0.project_name AND scops_0.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time_not_in('{START, CODEGEN, VARIANTS, CACHE_HIT, REQUESTS, BLOCKED}'::VARCHAR[], exp_id, 'PolyJIT'))
                                                                                                AS scops_1 ON (scops_1.project_name = T_0.project_name AND scops_1.project_group = T_0.project_group)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time_not_in('{START, CODEGEN, VARIANTS, CACHE_HIT, REQUESTS, BLOCKED}'::VARCHAR[], exp_id, 'polly.inside'))
                                                                                                AS scops_2 ON (scops_2.project_name = T_0.project_name AND scops_2.project_group = T_0.project_group)
  WHERE TRUE;--B_1.duration != variants_1.duration;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_eval(exp_ids UUID);
CREATE OR REPLACE FUNCTION ijpp_eval(exp_ids UUID)
RETURNS TABLE (
  project_name VARCHAR,
  project_group VARCHAR,
  domain VARCHAR,
  ohcov_0 NUMERIC,
  ohcov_1 NUMERIC,
  ohcov_2 NUMERIC,
  dyncov_0 NUMERIC,
  dyncov_1 NUMERIC,
  dyncov_2 NUMERIC,
  cachehits_0 NUMERIC,
  cachehits_1 NUMERIC,
  cachehits_2 NUMERIC,
  variants_0 NUMERIC,
  variants_1 NUMERIC,
  variants_2 NUMERIC,
  blocked_0 NUMERIC,
  blocked_1 NUMERIC,
  blocked_2 NUMERIC,
  codegen_0 NUMERIC,
  codegen_1 NUMERIC,
  codegen_2 NUMERIC,
  scops_0 NUMERIC,
  scops_1 NUMERIC,
  scops_2 NUMERIC,
  t_0 NUMERIC,
  o_0 NUMERIC,
  t_1 NUMERIC,
  o_1 NUMERIC,
  t_2 NUMERIC,
  o_2 NUMERIC,
  speedup_0 NUMERIC,
  speedup_2 NUMERIC
)
AS $BODY$ BEGIN
RETURN QUERY
  SELECT
    coverage.project_name                       AS project_name,
    coverage.project_group                      AS project_group,
    project.domain                              AS domain,
    coverage.ohcov_0                            AS OhCov_POLLY,
    coverage.ohcov_1                            AS OhCov_PJIT,
    coverage.ohcov_2                            AS OhCov_POLLY_1,
    coverage.dyncov_0                           AS DynCov_POLLY,
    coverage.dyncov_1                           AS DynCov_PJIT,
    coverage.dyncov_2                           AS DynCov_POLLY_1,
    coverage.cachehits_0                        AS CH_POLLY,
    coverage.cachehits_1                        AS CH_PJIT,
    coverage.cachehits_2                        AS CH_POLLY_1,
    coverage.variants_0                         AS VARS_POLLY,
    coverage.variants_1                         AS VARS_PJIT,
    coverage.variants_2                         AS VARS_POLLY_1,
    coverage.blocked_0                          AS BLKD_POLLY,
    coverage.blocked_1                          AS BLKD_PJIT,
    coverage.blocked_2                          AS BLKD_POLLY_1,
    coverage.codegen_0 / 1000000                AS Oh_POLLY,
    coverage.codegen_1 / 1000000                AS Oh_PJIT,
    coverage.codegen_2 / 1000000                AS Oh_POLLY_1,
    coverage.scops_0 / 1000000                  AS Scop_POLLY,
    coverage.scops_1 / 1000000                  AS Scops_PJIT,
    coverage.scops_2 / 1000000                  AS Scops_POLLY_1,
    coverage.t_0 / 1000000                      AS T_POLLY,
    coverage.o_0 / 1000000                      AS OH_POLLY,
    coverage.t_1 / 1000000                      AS T_PJIT,
    coverage.o_1 / 1000000                      AS OH_PJIT,
    coverage.t_2 / 1000000                      AS T_POLLY_1,
    coverage.o_2 / 1000000                      AS OH_POLLY_1,
    speedup(coverage.t_0, coverage.t_1)         AS speedup_0,
    speedup(coverage.t_2, coverage.t_1)         AS speedup_1
  FROM
    ijpp_total_dyncov(exp_ids)                  AS coverage
    LEFT JOIN
      project ON (coverage.project_name = project.name AND coverage.project_group = project.group_name)
  WHERE
    coverage.variants_1 > 0 and
    coverage.t_0 > 0 and
    coverage.t_1 > 0
  ORDER BY
    project.domain ASC,
    coverage.dyncov_1 DESC;
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_run_regions(exp_id UUID, config_name VARCHAR);
CREATE OR REPLACE FUNCTION ijpp_run_regions(exp_id UUID, config_name VARCHAR)
RETURNS TABLE (
  project_name   VARCHAR,
  project_group  VARCHAR,
  config         VARCHAR,
  cores          VARCHAR,
  region_name    VARCHAR,
  runtime        NUMERIC
)
AS $BODY$ BEGIN
RETURN QUERY
  SELECT
    run_1.project_name     AS project_name,
    run_1.project_group    AS project_group,
    run_1.config           AS config,
    config.value           AS cores,
    regions.name           AS region_name,
    SUM(regions.duration)  AS runtime
  FROM
      ijpp_runs_by_config(exp_id, config_name) AS run_1
      JOIN config                                           ON (run_1.id = config.run_id)
      JOIN regions                                          ON (run_1.id = regions.run_id)
  WHERE
    config.name = 'cores'
  GROUP BY
    run_1.project_name, run_1.project_group, run_1.config, regions.name, config.value, run_1.config
  ORDER BY
    run_1.project_name, run_1.project_group, run_1.config, runtime, config.value;

END $BODY$ language plpgsql;

DROP FUNCTION IF EXISTS ijpp_region_wise_compare(exp_id UUID);
CREATE OR REPLACE FUNCTION ijpp_region_wise_compare(exp_id UUID)
RETURNS TABLE (
  project_name  VARCHAR,
  project_group VARCHAR,
  Region VARCHAR,
  Cores VARCHAR,
  T_Polly NUMERIC,
  T_PolyJIT NUMERIC,
  Speedup NUMERIC
)
AS $BODY$ BEGIN
RETURN QUERY
  SELECT * from (
    SELECT
      results.project_name,
      results.project_group,
      results.region_name,
      results.cores,
      results.runtime_polly,
      results.runtime_polyjit,
      speedup(results.runtime_polly, results.runtime_polyjit) as speedup
    FROM (
      SELECT
        spec_enabled.project_name AS project_name,
        spec_enabled.project_group AS project_group,
        spec_enabled.region_name AS region_name,
        spec_enabled.cores AS cores,
        spec_enabled.runtime AS runtime_polyjit,
        spec_disabled.runtime AS runtime_polly
      FROM
             ijpp_run_regions(exp_id, 'PolyJIT')               as spec_enabled
        JOIN ijpp_run_regions(exp_id, 'polly.inside.no-delin') as spec_disabled
        ON (spec_enabled.project_name = spec_disabled.project_name AND
            spec_enabled.project_group = spec_disabled.project_group AND
            spec_enabled.region_name = spec_disabled.region_name AND
            spec_enabled.cores = spec_disabled.cores)
      WHERE
        spec_enabled.region_name != ALL ('{START, CODEGEN, VARIANTS, CACHE_HIT, REQUESTS, BLOCKED}'::VARCHAR[])
      ORDER BY
        project_name, project_group, cores, region
    ) AS results
  ) AS reulsts_f
  ORDER BY speedup DESC;
END $BODY$ LANGUAGE plpgsql;
