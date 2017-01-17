--drop function experiments(exp_ids UUID[]);
CREATE OR REPLACE function experiments(exp_ids UUID[])
	returns
    table(project VARCHAR,
          runs BIGINT)
AS $BODY$
BEGIN
  RETURN QUERY
    SELECT run.project_name, count(run.id) FROM run
    WHERE run.experiment_group = ANY (exp_ids)
    GROUP BY
      run.project_name;
END
$BODY$ language plpgsql;