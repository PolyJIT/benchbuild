DROP FUNCTION IF EXISTS polly_mse_eval(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION polly_mse_eval(exp_ids UUID[])
  RETURNS
    TABLE(project_name VARCHAR,
          name  VARCHAR,
          bvalue FLOAT,
          mvalue FLOAT
         )
AS $BODY$
BEGIN
  RETURN QUERY
select
  baseline.project_name,
  baseline.name,
  baseline.value as bvalue,
  measurement.value as mvalue
from
  (select run.project_name as project_name,
          metrics.name as name,
          SUM(metrics.value) as value
   from run, metrics, config
   where run.id = metrics.run_id and
         run.id = config.run_id and
	 config.name = 'baseline' and config.value = 'True' and
	 run.status = 'completed' and
         run.experiment_group = ANY (exp_ids)
   group by
         run.project_name,
         metrics.name
  ) as baseline
LEFT JOIN
  (select run.project_name as project_name,
          metrics.name as name,
          SUM(metrics.value) as value
   from run, metrics, config
   where run.id = metrics.run_id and run.id = config.run_id and
	 config.name = 'baseline' and config.value = 'False' and
	 run.status = 'completed' and
         run.experiment_group = ANY (exp_ids)
   group by
         run.project_name,
         metrics.name
  ) as measurement
ON
(baseline.project_name = measurement.project_name and baseline.name = measurement.name);
END
$BODY$ LANGUAGE plpgsql;
