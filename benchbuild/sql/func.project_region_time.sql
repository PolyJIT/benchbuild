DROP FUNCTION IF EXISTS project_region_time(region_name VARCHAR, num_cores VARCHAR, exp_ids UUID[], recomp_status VARCHAR);
CREATE OR REPLACE FUNCTION project_region_time(region_name   VARCHAR, num_cores VARCHAR, exp_ids UUID [],
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
