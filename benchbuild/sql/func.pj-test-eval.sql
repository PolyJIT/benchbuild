DROP FUNCTION IF EXISTS specialization (exp_ids UUID[], spec_status VARCHAR);
CREATE OR REPLACE FUNCTION specialization(exp_ids UUID[], spec_status VARCHAR)
  returns table(name VARCHAR, value VARCHAR, run_id INTEGER) as $specialization$
BEGIN
  RETURN QUERY
    SELECT config.name,
           config.value,
           config.run_id
    FROM config, run WHERE
        run.id = config.run_id AND
        run.status = 'completed' AND
        config.name = 'specialization' AND
        config.value = spec_status AND
        run.experiment_group = ANY (exp_ids);
END;
$specialization$ language plpgsql;

DROP FUNCTION IF EXISTS pj_test_project_region_time(region_name VARCHAR, exp_ids UUID[], spec_status VARCHAR);
CREATE OR REPLACE FUNCTION pj_test_project_region_time(region_name VARCHAR, exp_ids UUID [], spec_status VARCHAR)
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
        specialization((exp_ids), spec_status) AS spec
  WHERE
    run.id = config.run_id AND run.id = regions.run_id AND
    run.experiment_group = ANY (exp_ids) AND
    run.id = spec.run_id AND
    regions.name = region_name
  GROUP BY
    run.project_name;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS pj_test_total_dyncov(exp_ids UUID []);
CREATE OR REPLACE FUNCTION pj_test_total_dyncov(exp_ids UUID [])
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
            specialization(exp_ids, 'disabled') AS recomp
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
                      specialization(exp_ids, 'disabled') AS spec
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
                      specialization(exp_ids, 'enabled') AS spec
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
                      specialization(exp_ids, 'disabled') AS spec
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
                      specialization(exp_ids, 'enabled') AS spec
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
                      specialization(exp_ids, 'disabled') AS spec
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
                      specialization(exp_ids, 'enabled') AS spec
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
                      specialization((exp_ids), 'disabled') AS spec
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
                      specialization((exp_ids), 'enabled') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name != ALL ('{START, CODEGEN, VARIANTS, CACHE_HIT}' :: VARCHAR [])
                GROUP BY
                  run.project_name
              ) AS scops_1 ON (scops_1.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_test_project_region_time('START', (exp_ids), 'disabled')) AS T_0
      ON (T_0.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_test_project_region_time('CODEGEN', (exp_ids), 'disabled')) AS O_0
      ON (O_0.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_test_project_region_time('START', (exp_ids), 'enabled')) AS T_1
      ON (T_1.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_test_project_region_time('CODEGEN', (exp_ids), 'enabled')) AS O_1
      ON (O_1.project_name = total.project_name)
  WHERE TRUE;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS pj_test_eval(exp_ids UUID []);
CREATE OR REPLACE FUNCTION pj_test_eval(exp_ids UUID [])
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
  p.domain                           AS domain,
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
  speedup(coverage.t_0, coverage.t_1) AS speedup
FROM
  pj_test_total_dyncov(exp_ids)       AS coverage
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

DROP FUNCTION IF EXISTS pj_test_run_regions(exp_ids UUID[], spec_status VARCHAR);
CREATE OR REPLACE FUNCTION pj_test_run_regions(exp_ids UUID[], spec_status VARCHAR)
  returns table(
    name VARCHAR,
    region VARCHAR,
    runtime NUMERIC,
    value VARCHAR,
    specialization VARCHAR) AS $BODY$
BEGIN
  RETURN QUERY
    SELECT
	    run.project_name AS project,
      regions.name AS region_name,
      SUM(regions.duration) AS runtime,
      config.value,
      spec.value AS specialization
	  FROM
	    run,
	    specialization(exp_ids, spec_status) AS spec,
	    config,
	    regions
	  WHERE
      run.experiment_group = ANY (exp_ids) AND
	    run.id = regions.run_id AND
	    run.id = config.run_id AND
	    run.id = spec.run_id AND
	    config.name = 'cores'
	  GROUP BY run.project_name, regions.name, config.value, spec.value
    ORDER BY project, runtime, config.value;
END
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS pj_test_region_wise(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION pj_test_region_wise(exp_ids UUID[])
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
      pj_test_run_regions(exp_ids, 'enabled') as spec_enabled,
      pj_test_run_regions(exp_ids, 'disabled') as spec_disabled
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

DROP FUNCTION IF EXISTS exp_status(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION exp_status(exp_ids UUID[])
	returns
    table(
      Name VARCHAR,
      _Group VARCHAR,
      Status VARCHAR,
      Runs BIGINT
    )
AS $pj_test_status$
BEGIN
  RETURN QUERY
SELECT
  project.name AS name,
  project.group_name AS group,
  CAST(run.status AS VARCHAR) AS status,
  count(run.id) AS runs
FROM project LEFT OUTER JOIN
  (SELECT * FROM run WHERE
    run.experiment_group = ANY (exp_ids)
  ) as run
ON project.name = run.project_name
  GROUP BY
    project.name,
    project.group_name,
    run.status
  ORDER BY
    run.status,
    project.group_name,
    project.name;
END
$pj_test_status$ language plpgsql;
