DROP FUNCTION IF EXISTS total_dyncov(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION total_dyncov(exp_ids UUID[])
	returns
    table(project VARCHAR,
          total numeric,
          scops numeric,
          dyncov numeric)
AS $BODY$
BEGIN
  RETURN QUERY
select scops.project_name, total.sum as total, scops.sum as scops, (scops.sum / total.sum * 100) as dyncov from
(
  SELECT
    run.project_name,
    sum(benchbuild_events.duration)
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
) as total,
(
  SELECT
    run.project_name,
    sum(benchbuild_events.duration)
  FROM run, config, benchbuild_events, recompilation((exp_ids) , 'disabled') AS recomp
  WHERE
    run.id = config.run_id AND run.id = benchbuild_events.run_id AND
    run.experiment_group = ANY (exp_ids) AND
    config.name = 'cores' AND
    config.value = '1' AND
    run.id = recomp.run_id AND
    benchbuild_events.name <> 'START'
  GROUP BY
    run.project_name
) as scops
where
  total.project_name = scops.project_name;
  END
$BODY$ language plpgsql;
