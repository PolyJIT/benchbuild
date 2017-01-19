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
    (scops_0.sum / (T_0.duration - codegen_0.sum) * 100) AS dyncov_0,
    (scops_1.sum / (T_1.duration - codegen_1.sum) * 100) AS dyncov_1,
    ch_0.sum                                        AS cachehits_0,
    ch_1.sum                                        AS cachehits_1,
    variants_0.sum                                  AS variants_0,
    variants_1.sum                                  AS variants_1,
    codegen_0.sum                                   AS codegen_0,
    codegen_1.sum                                   AS codegen_1,
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
  speedup(coverage.t_0 - coverage.o_0, coverage.t_1 - coverage.o_1) AS speedup
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