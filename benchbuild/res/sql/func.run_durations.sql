DROP FUNCTION IF EXISTS run_durations(exp_ids UUID[], recomp_status VARCHAR);
CREATE OR REPLACE FUNCTION run_durations(exp_ids UUID[], recomp_status VARCHAR)
  returns table(name VARCHAR, region VARCHAR, runtime NUMERIC, value VARCHAR, recompilation VARCHAR) AS $run_durations$
BEGIN
  RETURN QUERY
    SELECT
	    run.project_name AS project,
      p.name AS region_name,
      SUM(p.duration) AS runtime,
      config.value,
      recomp.value AS recompilation
	  FROM
	    run,
	    recompilation(exp_ids, recomp_status) AS recomp,
	    config,
	    benchbuild_events AS p
	  WHERE
      run.experiment_group = ANY (exp_ids) AND
	    run.id = p.run_id AND
	    run.id = config.run_id AND
	    run.id = recomp.run_id AND
	    config.name = 'cores'
	  GROUP BY run.project_name, p.name, config.value, recomp.value
    ORDER BY project, runtime, config.value;
END
$run_durations$ language plpgsql;
