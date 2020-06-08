DROP FUNCTION IF EXISTS cs_config (exp_ids UUID[], cs_config_str VARCHAR);
CREATE OR REPLACE FUNCTION cs_config(exp_ids UUID[], cs_config_str VARCHAR)
  returns table(name VARCHAR, value VARCHAR, run_id INTEGER) as $BODY$
BEGIN
  RETURN QUERY
    SELECT config.name,
           config.value,
           config.run_id
    FROM config, run WHERE
        run.id = config.run_id AND
        run.status = 'completed' AND
        config.name = 'name' AND
        config.value = cs_config_str AND
        run.experiment_group = ANY (exp_ids);
END;
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS cs_component_vals_per_config(exp_ids UUID[], cs_components VARCHAR[], config VARCHAR);
CREATE OR REPLACE FUNCTION cs_component_vals_per_config(exp_ids UUID[], cs_components VARCHAR[], config VARCHAR)
  returns table(project VARCHAR, variable TEXT, value NUMERIC) as $BODY$
BEGIN
  RETURN QUERY
    SELECT
      run.project_name AS project,
      CAST(compilestats.name AS TEXT) AS variable,
      SUM(compilestats.value) AS value
    FROM
      run, compilestats, cs_config(exp_ids, config) AS cfg
    WHERE
      run.id = compilestats.run_id AND
      run.experiment_group = ANY (exp_ids) AND
      compilestats.component = ANY (cs_components) AND
      run.id = cfg.run_id
    GROUP BY
      run.project_name,
      compilestats.name;
END;
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS pollytest_eval(exp_ids UUID[], components VARCHAR[]);
CREATE OR REPLACE FUNCTION pollytest_eval(exp_ids UUID[], components VARCHAR[])
  RETURNS
    TABLE(
      project VARCHAR,
      variable TEXT,
      p     NUMERIC,
      pv    NUMERIC,
      pvu   NUMERIC,
      pu    NUMERIC
    )
AS $BODY$
BEGIN
  RETURN QUERY
  SELECT
    P1.project AS project,
    P1.variable AS variable,

    coalesce(P1.value, 0) AS p,
    coalesce(P2.value, 0) AS pv,
    coalesce(P3.value, 0) AS pvu,
    coalesce(P4.value, 0) AS pu
  FROM
              cs_component_vals_per_config(exp_ids, components,
                '-O3 -polly') as P1
    LEFT JOIN
              cs_component_vals_per_config(exp_ids, components,
                '-O3 -polly -polly-position=before-vectorizer') as P2
              ON (P2.project = P1.project AND P2.variable = P1.variable)
    LEFT JOIN
              cs_component_vals_per_config(exp_ids, components,
                '-O3 -polly -polly-position=before-vectorizer -polly-process-unprofitable') as P3
              ON (P3.project = P1.project AND P3.variable = P1.variable)
    LEFT JOIN
              cs_component_vals_per_config(exp_ids, components,
                '-O3 -polly -polly-process-unprofitable') as P4
              ON (P4.project = P1.project AND P4.variable = P1.variable)
  WHERE TRUE
  ORDER BY
    project,
    variable
  ;
END
$BODY$ LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS pollytest_eval_melted(exp_ids UUID[], components VARCHAR[]);
create or replace function pollytest_eval_melted(exp_ids uuid[], components character varying[])
  returns TABLE(project character varying, variable character varying, metric TEXT, value bigint)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    project.name AS project,
    config.value AS variable,
    compilestats.name AS metric,
    SUM(CAST(compilestats.value AS INTEGER)) AS value
  FROM
    project
    LEFT OUTER JOIN run
    ON (run.project_name = project.name)
    LEFT OUTER JOIN config
    ON (run.id = config.run_id)
    LEFT OUTER JOIN compilestats
    ON (run.id = compilestats.run_id)
  WHERE
    experiment_group = ANY (exp_ids) AND
    compilestats.component = ANY(components) AND
    config.name = 'name'
  group by
    project.name, config.value, compilestats.name
  order by
    project.name,
    config.value,
    compilestats.name;
END
$$;
