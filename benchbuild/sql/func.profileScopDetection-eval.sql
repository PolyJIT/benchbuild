DROP FUNCTION public.profile_scops_exec_times(exp_ids uuid[]);
CREATE OR REPLACE FUNCTION public.profile_scops_exec_times(exp_ids uuid[])
  RETURNS TABLE(project character varying, execTime_us DOUBLE PRECISION) AS
$BODY$
BEGIN
  RETURN QUERY
        select sub.project, sub.execTime_us from (
          select
              run.project_name as project,
              run.run_group,
              SUM(metrics.value * 1000000) as execTime_us
          from run, metrics
          where run.id = metrics.run_id and
                run.experiment_group = ANY (exp_ids) and
                metrics.name = 'time.real_s'
          group by
                run.project_name, run.run_group
        ) as sub;
end
$BODY$
  LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS profile_scops_valid_regions(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION profile_scops_valid_regions(exp_ids UUID[])
	returns
    table(run_id INTEGER,
          duration NUMERIC,
	  id NUMERIC,
	  name VARCHAR,
	  events BIGINT)
AS $BODY$
BEGIN
  RETURN QUERY
	select
		regions.run_id,
		regions.duration,
		regions.id,
		regions.name,
		regions.events
	from
		run, regions, metrics
	where
		run.id = regions.run_id and
		run.id = metrics.run_id and
		metrics.name = 'time.real_s' and
		metrics.value * 1000000 >= regions.duration and
		run.experiment_group = ANY (exp_ids);
end
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS profile_scops_count_invalid_regions(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION profile_scops_count_invalid_regions(exp_ids UUID[])
	returns INTEGER
AS $BODY$
BEGIN
  RETURN
	(select
		count(*) as num_invalid
	from
		run, regions, metrics
	where
		run.id = regions.run_id and
		run.id = metrics.run_id and
		metrics.name = 'time.real_s' and
		metrics.value * 1000000 < regions.duration and
		run.experiment_group = ANY (exp_ids));
end
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS profile_scops_ratios(exp_ids UUID[], filter_str VARCHAR);
CREATE OR REPLACE FUNCTION profile_scops_ratios(exp_ids UUID[], filter_str VARCHAR)
	returns
    table (
	project VARCHAR,
	T_SCoP NUMERIC,
	T_Total DOUBLE PRECISION,
	DynCov DOUBLE PRECISION)
AS $BODY$
BEGIN
  RETURN QUERY
	select
		total.project,
		scops.t_scop,
		total.exectime_us,
		(scops.t_scop * 100/ total.exectime_us) as DynCov_pct
	from
		profile_scops_exec_times(exp_ids) as total,
		(
		  select
			run.project_name as project,
			SUM(valid_regions.duration) as T_SCoP
		  from
			profile_scops_valid_regions(exp_ids) as valid_regions,
			run
		  where
			  valid_regions.name like filter_str and
			  run.id = valid_regions.run_id
		  group by
			  run.project_name
		) as scops
	where
		total.project = scops.project;
end
$BODY$ language plpgsql;
