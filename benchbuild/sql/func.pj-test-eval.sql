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
          total     NUMERIC,
          scops     NUMERIC,
          overhead  NUMERIC,
          ohcov_0   NUMERIC,
          ohcov_1   NUMERIC,
          dyncov    NUMERIC,
          cachehits NUMERIC,
          variants  NUMERIC,
          t_0       NUMERIC,
          t_1       NUMERIC,
          o_1       NUMERIC)
AS $BODY$
BEGIN
  RETURN QUERY
  SELECT
    total.project_name,
    total.sum                                     AS total,
    scops.sum                                     AS scops,
    codegen.sum                                   AS overhead,
    (codegen.sum / total.sum * 100)               AS ohcov_0,
    (O_1.duration / T_1.duration * 100)           AS ohcov_1,
    (scops.sum / (total.sum - codegen.sum) * 100) AS dyncov,
    ch.sum                                        AS cachehits,
    variants.sum                                  AS variants,
    total.sum - codegen.sum                       AS T_0,
    T_1.duration                                  AS t_1,
    O_1.duration                                  AS o_1
  FROM
    (
      SELECT
        run.project_name,
        sum(regions.duration)
      FROM run, config, regions,
            specialization(exp_ids, 'enabled') AS recomp
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
                      specialization(exp_ids, 'enabled') AS spec
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  run.id = spec.run_id AND
                  regions.name = 'CODEGEN'
                GROUP BY
                  run.project_name
              ) AS codegen ON (codegen.project_name = total.project_name)
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
              ) AS ch ON (ch.project_name = total.project_name)
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
              ) AS variants ON (variants.project_name = total.project_name)
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
              ) AS scops ON (scops.project_name = total.project_name)
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
