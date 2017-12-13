CREATE OR REPLACE VIEW ijpp_runs AS
  SELECT
    run.*
  FROM run LEFT JOIN config ON (run.id = config.run_id)
  WHERE
    config.name = 'baseline' AND
    config.value = 'False';

DROP FUNCTION IF EXISTS ijpp_total_runtime(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION ijpp_total_runtime(exp_ids UUID [])
RETURNS TABLE(
	project VARCHAR,
	"group" VARCHAR,
        domain VARCHAR,
	config VARCHAR,
	"time" DOUBLE PRECISION,
	variants NUMERIC,
        cachehits NUMERIC
      )
AS $BODY$ BEGIN
RETURN QUERY
  SELECT
	project_name AS project,
	project_group AS "group",
        prj.domain AS "domain",
	config.value AS config,
    	SUM(coalesce(r.duration / 1000000, metrics.value)) AS time,
    	SUM(COALESCE(vars.duration, 0)) AS variants,
        SUM(COALESCE(chits.duration, 0)) AS cachehits
  FROM ijpp_runs AS rrun
      RIGHT JOIN config ON (rrun.id = config.run_id)
      LEFT JOIN metrics ON (rrun.id = metrics.run_id)
      FULL OUTER JOIN
	(SELECT * FROM regions WHERE regions.name = 'VARIANTS') AS vars
      ON (rrun.id = vars.run_id)
      FULL OUTER JOIN
	(SELECT * FROM regions WHERE regions.name = 'CACHE_HIT') AS chits
      ON (rrun.id = chits.run_id)
      FULL OUTER JOIN
	(SELECT * FROM regions WHERE regions.name = 'START') AS r
      ON (rrun.id = r.run_id)
      LEFT JOIN project AS prj ON (rrun.project_name = prj.name AND
                                   rrun.project_group = prj.group_name)
  WHERE
	config.name = 'name' AND
	metrics.name = 'time.real_s' AND
        rrun.experiment_group = ANY (exp_ids)
  GROUP BY
	project, "group", prj.domain, config
  ORDER BY
	project, config;
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_region_wise(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION ijpp_region_wise(exp_ids UUID [])
RETURNS TABLE(
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
	config.value AS config,
	SUM(regions.duration) AS runtime
  FROM ijpp_runs AS rrun
      LEFT JOIN config ON (rrun.id = config.run_id)
      LEFT JOIN regions ON (rrun.id = regions.run_id)
  WHERE
    rrun.experiment_group = ANY (exp_ids) AND
    config.name = 'name' AND
    regions.name != ALL ('{START, CODEGEN, CACHE_HIT, VARIANTS}'::VARCHAR[])
  GROUP BY
    rrun.project_name, regions.name, config.value
  ORDER BY project, region, config;
END $BODY$ LANGUAGE plpgsql;


DROP FUNCTION IF EXISTS ijpp_db_export_per_config(exp_ids UUID[], configs VARCHAR[]);
CREATE OR REPLACE FUNCTION ijpp_db_export_per_config(exp_ids UUID [], configs VARCHAR[])
RETURNS TABLE(
	project    VARCHAR,
	"group"    VARCHAR,
        "function" VARCHAR,
	"ast" 	   VARCHAR,
	"schedule" VARCHAR,
        "stderr"   VARCHAR,
	"cfg"	   VARCHAR)
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
      experiment_group = ANY (exp_ids);
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_db_export(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION ijpp_db_export(exp_ids UUID [])
RETURNS TABLE(
	project            VARCHAR,
	"group"            VARCHAR,
        "function"         VARCHAR,
	"jit_ast" 	   VARCHAR,
	"jit_schedule" 	   VARCHAR,
	"jit_stderr" 	   VARCHAR,
	"polly_ast" 	   VARCHAR,
	"polly_schedule"   VARCHAR,
	"polly_stderr" 	   VARCHAR
)
AS $BODY$ BEGIN
RETURN QUERY
  select
    coalesce(t1."project", t2."project") as "project",
    coalesce(t1."group", t2."group") as "group",
    coalesce(t1."function", t2."function") as "function",
    t1.ast AS jit_ast, t1.schedule AS jit_schedule,
    t1.stderr AS jit_stderr,
    t2.ast AS polly_ast, t2.schedule AS polly_ast,
    t2.stderr AS polly_stderr
  from
	ijpp_db_export_per_config(exp_ids, '{PolyJIT}') AS t1
	FULL OUTER JOIN
	ijpp_db_export_per_config(exp_ids, '{polly.inside}') AS t2
	on (t1.project = t2.project AND t1."function" = t2."function");
END $BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_runs_by_config(exp_ids UUID[], config_name VARCHAR);
CREATE OR REPLACE FUNCTION ijpp_runs_by_config(exp_ids UUID[], config_name VARCHAR)
  returns table(name VARCHAR, value VARCHAR, run_id INTEGER) as $BODY$
BEGIN
  RETURN QUERY
    SELECT config.name,
           config.value,
           config.run_id
    FROM ijpp_runs as rrun LEFT JOIN config ON (rrun.id = config.run_id)
    WHERE
      rrun.experiment_group = ANY (exp_ids) AND
      rrun.status = 'completed' AND
      config.name = 'name' AND config.value = config_name;
END $BODY$ language plpgsql;

DROP FUNCTION IF EXISTS ijpp_project_region_time(region_name VARCHAR, exp_ids UUID[], config_name VARCHAR);
CREATE OR REPLACE FUNCTION ijpp_project_region_time(region_name VARCHAR, exp_ids UUID [], config_name VARCHAR)
  RETURNS
    TABLE(project_name VARCHAR,
          duration     NUMERIC)
AS $BODY$
BEGIN
  RETURN QUERY
  SELECT
    run.project_name,
    sum(regions.duration)
  FROM run, config, regions,
        ijpp_runs_by_config((exp_ids), config_name) AS spec
  WHERE
    run.id = config.run_id AND run.id = regions.run_id AND
    run.experiment_group = ANY (exp_ids) AND
    run.id = spec.run_id AND
    regions.name = region_name
  GROUP BY
    run.project_name;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_total_dyncov(exp_ids UUID []);
CREATE OR REPLACE FUNCTION ijpp_total_dyncov(exp_ids UUID [])
  RETURNS
    TABLE(project   VARCHAR,
          ohcov_0   NUMERIC,
          ohcov_1   NUMERIC,
          dyncov_0   NUMERIC,
          dyncov_1   NUMERIC,
          cachehits_0 NUMERIC,
          cachehits_1 NUMERIC,
          variants_0 NUMERIC,
          variants_1 NUMERIC,
          codegen_0   NUMERIC,
          codegen_1   NUMERIC,
          scops_0   NUMERIC,
          scops_1   NUMERIC,
          t_0       NUMERIC,
          o_0       NUMERIC,
          t_1       NUMERIC,
          o_1       NUMERIC)
AS $BODY$
BEGIN
  RETURN QUERY
  SELECT
    total.project_name                            AS project,
    (O_0.duration / T_0.duration * 100)           AS ohcov_0,
    (O_1.duration / T_1.duration * 100)           AS ohcov_1,
    (scops_0.sum / T_0.duration * 100)            AS dyncov_0,
    (scops_1.sum / T_1.duration * 100)            AS dyncov_1,
    ch_0.sum                                      AS cachehits_0,
    ch_1.sum                                      AS cachehits_1,
    variants_0.sum                                AS variants_0,
    variants_1.sum                                AS variants_1,
    codegen_0.sum                                 AS codegen_0,
    codegen_1.sum                                 AS codegen_1,
    scops_0.sum                                   AS scops_0,
    scops_1.sum                                   AS scops_1,
    T_0.duration                                  AS t_0,
    O_0.duration                                  AS o_0,
    T_1.duration                                  AS t_1,
    O_1.duration                                  AS o_1
  FROM
    (
      SELECT
        run.project_name,
        sum(regions.duration)
      FROM run, config, regions,
            ijpp_runs_by_config(exp_ids, 'polly.inside.no-delin') AS recomp
      WHERE
        run.id = config.run_id AND run.id = regions.run_id AND
        run.experiment_group = ANY (exp_ids) AND
        run.id = recomp.run_id AND
        regions.name = 'START'
      GROUP BY
        run.project_name
    ) AS total
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      ijpp_runs_by_config(exp_ids, 'polly.inside.no-delin') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name = 'CODEGEN'
                GROUP BY
                  run.project_name
              ) AS codegen_0 ON (codegen_0.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      ijpp_runs_by_config(exp_ids, 'PolyJIT') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name = 'CODEGEN'
                GROUP BY
                  run.project_name
              ) AS codegen_1 ON (codegen_1.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      ijpp_runs_by_config(exp_ids, 'polly.inside.no-delin') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name = 'CACHE_HIT'
                GROUP BY
                  run.project_name
              ) AS ch_0 ON (ch_0.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      ijpp_runs_by_config(exp_ids, 'PolyJIT') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name = 'CACHE_HIT'
                GROUP BY
                  run.project_name
              ) AS ch_1 ON (ch_1.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      ijpp_runs_by_config(exp_ids, 'polly.inside.no-delin') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name = 'VARIANTS'
                GROUP BY
                  run.project_name
              ) AS variants_0 ON (variants_0.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      ijpp_runs_by_config(exp_ids, 'PolyJIT') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name = 'VARIANTS'
                GROUP BY
                  run.project_name
              ) AS variants_1 ON (variants_1.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      ijpp_runs_by_config((exp_ids), 'polly.inside.no-delin') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name != ALL ('{START, CODEGEN, VARIANTS, CACHE_HIT}' :: VARCHAR [])
                GROUP BY
                  run.project_name
              ) AS scops_0 ON (scops_0.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      ijpp_runs_by_config((exp_ids), 'PolyJIT') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name != ALL ('{START, CODEGEN, VARIANTS, CACHE_HIT}' :: VARCHAR [])
                GROUP BY
                  run.project_name
              ) AS scops_1 ON (scops_1.project_name = total.project_name)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('START', (exp_ids), 'polly.inside.no-delin')) AS T_0 ON (T_0.project_name = total.project_name)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CODEGEN', (exp_ids), 'polly.inside.no-delin')) AS O_0 ON (O_0.project_name = total.project_name)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('START', (exp_ids), 'PolyJIT')) AS T_1 ON (T_1.project_name = total.project_name)
    LEFT JOIN (SELECT * FROM ijpp_project_region_time('CODEGEN', (exp_ids), 'PolyJIT')) AS O_1 ON (O_1.project_name = total.project_name)
  WHERE TRUE;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_eval(exp_ids UUID []);
CREATE OR REPLACE FUNCTION ijpp_eval(exp_ids UUID [])
  RETURNS
    TABLE(project   VARCHAR,
          domain    VARCHAR,
          ohcov_0   NUMERIC,
          ohcov_1   NUMERIC,
          dyncov_0   NUMERIC,
          dyncov_1   NUMERIC,
          cachehits_0 NUMERIC,
          cachehits_1 NUMERIC,
          variants_0 NUMERIC,
          variants_1 NUMERIC,
          codegen_0   NUMERIC,
          codegen_1   NUMERIC,
          scops_0   NUMERIC,
          scops_1   NUMERIC,
          t_0       NUMERIC,
          o_0       NUMERIC,
          t_1       NUMERIC,
          o_1       NUMERIC,
          speedup   NUMERIC)
AS $BODY$
BEGIN
  RETURN QUERY
SELECT
  coverage.project,
  p.domain                                    AS domain,
  coverage.ohcov_0                            AS OhCov_POLLY,
  coverage.ohcov_1                            AS OhCov_PJIT,
  coverage.dyncov_0                           AS DynCov_POLLY,
  coverage.dyncov_1                           AS DynCov_PJIT,
  coverage.cachehits_0                        AS CH_POLLY,
  coverage.cachehits_1                        AS CH_PJIT,
  coverage.variants_0                         AS VARS_POLLY,
  coverage.variants_1                         AS VARS_PJIT,
  coverage.codegen_0 / 1000000                AS Oh_POLLY,
  coverage.codegen_1 / 1000000                AS Oh_PJIT,
  coverage.scops_0 / 1000000                  AS Scop_POLLY,
  coverage.scops_1 / 1000000                  AS Scops_PJIT,
  coverage.t_0 / 1000000                      AS T_POLLY,
  coverage.o_0 / 1000000                      AS OH_POLLY,
  coverage.t_1 / 1000000                      AS T_PJIT,
  coverage.o_1 / 1000000                      AS OH_PJIT,
  speedup(coverage.t_0, coverage.t_1)         AS speedup
FROM
  ijpp_total_dyncov(exp_ids)                  AS coverage
  LEFT JOIN
    project AS p ON (coverage.project = p.name)
WHERE
  coverage.t_0 > 1000 AND
  coverage.scops_1 is not NULL and
  coverage.variants_1 > 0 and
  coverage.t_1 is not NULL
ORDER BY
  p.domain ASC,
  coverage.dyncov_1 DESC;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS ijpp_run_regions(exp_ids UUID[], config_name VARCHAR);
CREATE OR REPLACE FUNCTION ijpp_run_regions(exp_ids UUID[], config_name VARCHAR)
  returns table(
    name VARCHAR,
    region VARCHAR,
    runtime NUMERIC,
    value VARCHAR,
    specialization VARCHAR) AS $BODY$
BEGIN
  RETURN QUERY
    SELECT
      rrun.project_name AS project,
      regions.name AS region_name,
      SUM(regions.duration) AS runtime,
      config.value,
      spec.value AS specialization
    FROM
        ijpp_runs AS rrun,
        ijpp_runs_by_config(exp_ids, config_name) AS spec,
        config,
        regions
    WHERE
    rrun.experiment_group = ANY (exp_ids) AND
    rrun.id = regions.run_id AND
    rrun.id = config.run_id AND
    rrun.id = spec.run_id AND
    config.name = 'cores'
    GROUP BY rrun.project_name, regions.name, config.value, spec.value
    ORDER BY project, runtime, config.value;
END
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS ijpp_region_wise_compare(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION ijpp_region_wise_compare(exp_ids UUID[])
	returns
    table(Project VARCHAR,
          Region VARCHAR,
          Cores VARCHAR,
          T_Polly NUMERIC,
          T_PolyJIT NUMERIC,
          speedup NUMERIC)
AS $compare_region_wise$
BEGIN
  RETURN QUERY
select * from
(
select
  results.project,
  results.region,
  results.cores,
  results.runtime_polly,
  results.runtime_polyjit,
  speedup(results.runtime_polly, results.runtime_polyjit) as speedup FROM
  (
    SELECT
      spec_enabled.name AS project,
      spec_enabled.region,
      spec_enabled.value AS cores,
      spec_enabled.runtime AS runtime_polly,
      spec_disabled.runtime AS runtime_polyjit
    FROM
      ijpp_run_regions(exp_ids, 'PolyJIT') as spec_enabled,
      ijpp_run_regions(exp_ids, 'polly.inside.no-delin') as spec_disabled
    WHERE
	    spec_enabled.name = spec_disabled.name and
	    spec_enabled.region = spec_disabled.region and
	    spec_enabled.value = spec_disabled.value and
	    spec_enabled.region != ALL ('{START, CODEGEN, VARIANTS, CACHE_HIT}'::VARCHAR[])
    order by
      project, cores, region
  ) as results
) as reulsts_f
order by speedup desc;
end
$compare_region_wise$ language plpgsql;
