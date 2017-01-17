DROP FUNCTION IF EXISTS total_speedup(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION total_speedup(exp_ids UUID[])
	returns
    table(project VARCHAR,
          baseline numeric,
          parallel numeric,
          bl_num bigint,
          p_num bigint,
          cores numeric,
          speedup numeric)
AS $BODY$
BEGIN
  RETURN QUERY
select baseline.project_name, baseline.sum as baseline, parallel.sum as parallel, baseline.num_events as bl_num, parallel.num_events as p_num, parallel.cores, speedup(baseline.sum, parallel.sum) from
(
  SELECT
    run.project_name,
    sum(benchbuild_events.duration),
    count(benchbuild_events.duration) as num_events
  FROM run, config, benchbuild_events, recompilation(exp_ids, 'disabled') AS recomp
  WHERE
    run.id = config.run_id AND run.id = benchbuild_events.run_id AND
    run.experiment_group = ANY (exp_ids) AND
    config.name = 'cores' AND
    config.value = '1' AND
    run.id = recomp.run_id and
    benchbuild_events.name = 'START'
  GROUP BY
    run.project_name
) as baseline,
(
  SELECT
    run.project_name,
    CAST(config.value AS numeric) as cores,
    sum(benchbuild_events.duration),
    count(benchbuild_events.duration) as num_events
  FROM run, config, benchbuild_events, recompilation((exp_ids) , 'enabled') AS recomp
  WHERE
    run.id = config.run_id AND run.id = benchbuild_events.run_id AND
    run.experiment_group = ANY (exp_ids) AND
    config.name = 'cores' AND
    run.id = recomp.run_id AND
    benchbuild_events.name = 'START'
  GROUP BY
    run.project_name,
    config.value
) as parallel
where
  baseline.project_name = parallel.project_name;
  END
$BODY$ language plpgsql;
