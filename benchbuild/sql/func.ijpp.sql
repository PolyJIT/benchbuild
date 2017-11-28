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
  FROM (
	SELECT run.* FROM run LEFT JOIN config ON (run.id = config.run_id)
	WHERE
	  config.name = 'baseline' AND
	  config.value = 'False' AND
	  run.experiment_group = ANY (exp_ids)
       ) AS rrun
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
	metrics.name = 'time.real_s'
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
  FROM (
	SELECT run.* FROM run LEFT JOIN config ON (run.id = config.run_id)
	WHERE
	  config.name = 'baseline' AND
	  config.value = 'False' AND
	  run.experiment_group = ANY (exp_ids)
       ) as rrun
      LEFT JOIN config ON (rrun.id = config.run_id)
      LEFT JOIN regions ON (rrun.id = regions.run_id)
  WHERE
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
    coalesce(t1."project", t2."project") as "project", coalesce(t1."group", t2."group") as "group",
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
