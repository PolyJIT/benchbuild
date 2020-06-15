DROP FUNCTION IF EXISTS run_regions(exp_ids UUID[], recomp_status VARCHAR);
CREATE OR REPLACE FUNCTION run_regions(exp_ids UUID[], recomp_status VARCHAR)
  returns table(name VARCHAR, region VARCHAR, runtime NUMERIC, value VARCHAR, recompilation VARCHAR) AS $BODY$
BEGIN
  RETURN QUERY
    SELECT
	    run.project_name AS project,
      regions.name AS region_name,
      SUM(regions.duration) AS runtime,
      config.value,
      recomp.value AS recompilation
	  FROM
	    run,
	    recompilation(exp_ids, recomp_status) AS recomp,
	    config,
	    regions
	  WHERE
      run.experiment_group = ANY (exp_ids) AND
	    run.id = regions.run_id AND
	    run.id = config.run_id AND
	    run.id = recomp.run_id AND
	    config.name = 'cores'
	  GROUP BY run.project_name, regions.name, config.value, recomp.value
    ORDER BY project, runtime, config.value;
END
$BODY$ language plpgsql;
