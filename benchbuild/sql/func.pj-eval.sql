drop function if exists pj_project_region_time(region_name VARCHAR, num_cores VARCHAR, exp_ids UUID[], recomp_status VARCHAR);
CREATE OR REPLACE FUNCTION pj_project_region_time(region_name   VARCHAR, num_cores VARCHAR, exp_ids UUID [],
                                                  recomp_status VARCHAR)
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
        recompilation((exp_ids), recomp_status) AS recomp
  WHERE
    run.id = config.run_id AND run.id = regions.run_id AND
    run.experiment_group = ANY (exp_ids) AND
    config.name = 'cores' AND
    config.value = num_cores AND
    run.id = recomp.run_id AND
    regions.name = region_name
  GROUP BY
    run.project_name;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS pj_total_dyncov_clean(exp_ids UUID [] );
CREATE OR REPLACE FUNCTION pj_total_dyncov_clean(exp_ids UUID [])
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
          t_2       NUMERIC,
          t_3       NUMERIC,
          t_4       NUMERIC,
          t_5       NUMERIC,
          o_1       NUMERIC,
          o_2       NUMERIC,
          o_3       NUMERIC,
          o_4       NUMERIC,
          o_5       NUMERIC)
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
    T_2.duration                                  AS t_2,
    T_3.duration                                  AS t_3,
    T_4.duration                                  AS t_4,
    T_5.duration                                  AS t_5,
    O_1.duration                                  AS o_1,
    O_2.duration                                  AS o_2,
    O_3.duration                                  AS o_3,
    O_4.duration                                  AS o_4,
    O_5.duration                                  AS o_5
  FROM
    (
      SELECT
        run.project_name,
        sum(regions.duration)
      FROM run, config, regions,
            recompilation(exp_ids, 'disabled') AS recomp
      WHERE
        run.id = config.run_id AND run.id = regions.run_id AND
        run.experiment_group = ANY (exp_ids) AND
        config.name = 'cores' AND
        config.value = '1' AND
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
                      recompilation(exp_ids, 'disabled') AS recomp
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  config.name = 'cores' AND
                  config.value = '1' AND
                  run.id = recomp.run_id AND
                  regions.name = 'CODEGEN'
                GROUP BY
                  run.project_name
              ) AS codegen ON (codegen.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      recompilation(exp_ids, 'enabled') AS recomp
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  config.name = 'cores' AND
                  config.value = '1' AND
                  run.id = recomp.run_id AND
                  regions.name = 'CACHE_HIT'
                GROUP BY
                  run.project_name
              ) AS ch ON (ch.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      recompilation(exp_ids, 'enabled') AS recomp
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  config.name = 'cores' AND
                  config.value = '1' AND
                  run.id = recomp.run_id AND
                  regions.name = 'VARIANTS'
                GROUP BY
                  run.project_name
              ) AS variants ON (variants.project_name = total.project_name)
    LEFT JOIN (
                SELECT
                  run.project_name,
                  sum(regions.duration)
                FROM run, config, regions,
                      recompilation((exp_ids), 'disabled') AS recomp
                WHERE
                  run.id = config.run_id AND run.id = regions.run_id AND
                  run.experiment_group = ANY (exp_ids) AND
                  config.name = 'cores' AND
                  config.value = '1' AND
                  run.id = recomp.run_id AND
                  regions.name != ALL ('{START, CODEGEN, VARIANTS, CACHE_HIT}' :: VARCHAR [])
                GROUP BY
                  run.project_name
              ) AS scops ON (scops.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('START', '1', (exp_ids), 'enabled')) AS T_1
      ON (T_1.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('START', '2', (exp_ids), 'enabled')) AS T_2
      ON (T_2.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('START', '3', (exp_ids), 'enabled')) AS T_3
      ON (T_3.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('START', '4', (exp_ids), 'enabled')) AS T_4
      ON (T_4.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('START', '5', (exp_ids), 'enabled')) AS T_5
      ON (T_5.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('CODEGEN', '1', (exp_ids), 'enabled')) AS O_1
      ON (O_1.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('CODEGEN', '2', (exp_ids), 'enabled')) AS O_2
      ON (O_2.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('CODEGEN', '3', (exp_ids), 'enabled')) AS O_3
      ON (O_3.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('CODEGEN', '4', (exp_ids), 'enabled')) AS O_4
      ON (O_4.project_name = total.project_name)
    LEFT JOIN
    (SELECT *
     FROM pj_project_region_time('CODEGEN', '5', (exp_ids), 'enabled')) AS O_5
      ON (O_5.project_name = total.project_name)
  WHERE TRUE;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS pj_total_dyncov(exp_ids UUID []);
CREATE OR REPLACE FUNCTION pj_total_dyncov(exp_ids UUID [])
  RETURNS
    TABLE(project     VARCHAR,
          domain      VARCHAR,
          T0          NUMERIC,
          TSCoPs      NUMERIC,
          O0          NUMERIC,

          OhCov0      NUMERIC,
          OhCov1      NUMERIC,
          DynCov0     NUMERIC,
          CH          NUMERIC,
          VARS        NUMERIC,

          S1          NUMERIC,
          S2          NUMERIC,
          S3          NUMERIC,
          S4          NUMERIC,
          S5          NUMERIC,

          T1          NUMERIC,
          O1          NUMERIC,
          T2          NUMERIC,
          O2          NUMERIC,
          T3          NUMERIC,
          O3          NUMERIC,
          T4          NUMERIC,
          O4          NUMERIC,
          T5          NUMERIC,
          O5          NUMERIC)
AS $BODY$
BEGIN
  RETURN QUERY
SELECT
  coverage.project                 AS project,
  p.domain                         AS domain,
  total / 1000000                  AS T0,
  scops / 1000000                  AS TS,
  overhead / 1000000               AS O0,

  ohcov_0                          AS OhCov0,
  ohcov_1                          AS OhCov1,
  dyncov                           AS DynCov0,
  cachehits                        AS CH,
  variants                         AS VARS,

  speedup(t_1 - o_1, t_1 - o_1) AS S1,
  speedup(t_1 - o_1, t_2 - o_2) AS S2,
  speedup(t_1 - o_1, t_3 - o_3) AS S3,
  speedup(t_1 - o_1, t_4 - o_4) AS S4,
  speedup(t_1 - o_1, t_5 - o_5) AS S5,

  t_1 / 1000000                    AS T1,
  o_1 / 1000000                    AS O1,
  t_2 / 1000000                    AS T2,
  o_2 / 1000000                    AS O2,
  t_3 / 1000000                    AS T3,
  o_3 / 1000000                    AS O3,
  t_4 / 1000000                    AS T4,
  o_4 / 1000000                    AS O4,
  t_5 / 1000000                    AS T5,
  o_5 / 1000000                    AS O5

FROM pj_total_dyncov_clean(exp_ids) AS coverage
  LEFT JOIN project AS p ON (coverage.project = p.name)
WHERE
  total > 1000 AND
  coverage.scops is not NULL and
  coverage.variants > 0 and
  coverage.t_1 is not NULL
order BY
  domain asc, dyncov desc;
END
$BODY$ language plpgsql;
