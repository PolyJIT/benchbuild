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
      compilestats.name AS variable,
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
      component TEXT,
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
    P1.variable AS component,

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
    component
  ;
END
$BODY$ LANGUAGE plpgsql;
