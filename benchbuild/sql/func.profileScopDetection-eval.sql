DROP FUNCTION public.profile_scops_exec_times(exp_ids uuid[]);
CREATE OR REPLACE FUNCTION public.profile_scops_exec_times(exp_ids uuid[])
  RETURNS TABLE(project character varying, execTime_us DOUBLE PRECISION) AS
$BODY$
BEGIN
  RETURN QUERY
        SELECT sub.project, sub.execTime_us FROM (
          SELECT
              run.project_name AS project,
              run.run_group,
              SUM(metrics.value * 1000000) AS execTime_us
          FROM run, metrics
          WHERE run.id = metrics.run_id and
                run.experiment_group = ANY (exp_ids) and
                metrics.name = 'time.real_s'
          GROUP BY
                run.project_name, run.run_group
        ) AS sub;
END
$BODY$
  LANGUAGE plpgsql;

DROP FUNCTION IF EXISTS profile_scops_valid_regions(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION profile_scops_valid_regions(exp_ids UUID[])
    RETURNS
    TABLE(run_id INTEGER,
          duration NUMERIC,
      id NUMERIC,
      name VARCHAR,
      events BIGINT)
AS $BODY$
BEGIN
  RETURN QUERY
    SELECT
        regions.run_id,
        regions.duration,
        regions.id,
        regions.name,
        regions.events
    FROM
        run, regions, metrics
    WHERE
        run.id = regions.run_id and
        run.id = metrics.run_id and
        metrics.name = 'time.real_s' and
        metrics.value * 1000000 >= regions.duration and
        run.experiment_group = ANY (exp_ids);
END
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS profile_scops_count_invalid_regions(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION profile_scops_count_invalid_regions(exp_ids UUID[])
    RETURNS INTEGER
AS $BODY$
BEGIN
  RETURN
    (SELECT
        count(*) AS num_invalid
    FROM
        run, regions, metrics
    WHERE
        run.id = regions.run_id and
        run.id = metrics.run_id and
        metrics.name = 'time.real_s' and
        metrics.value * 1000000 < regions.duration and
        run.experiment_group = ANY (exp_ids));
END
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS profile_scops_ratios(exp_ids UUID[], filter_str VARCHAR);
CREATE OR REPLACE FUNCTION profile_scops_ratios(exp_ids UUID[], filter_str VARCHAR)
    RETURNS
    TABLE (
    project VARCHAR,
    T_SCoP NUMERIC,
    T_Total DOUBLE PRECISION,
    DynCov DOUBLE PRECISION)
AS $BODY$
BEGIN
  RETURN QUERY
    SELECT
        total.project,
        scops.t_scop,
        total.exectime_us,
        (scops.t_scop * 100/ total.exectime_us) AS DynCov_pct
    FROM
        profile_scops_exec_times(exp_ids) AS total,
        (
          SELECT
            run.project_name AS project,
            SUM(valid_regions.duration) AS T_SCoP
          FROM
            profile_scops_valid_regions(exp_ids) AS valid_regions,
            run
          WHERE
              valid_regions.name LIKE filter_str AND
              run.id = valid_regions.run_id
          GROUP BY
              run.project_name
        ) AS scops
    WHERE
        total.project = scops.project;
END
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS profile_scops_toplevel_scops(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION profile_scops_toplevel_scops(exp_ids UUID[])
    RETURNS TABLE (
        run_id INTEGER,
        duration NUMERIC,
        id NUMERIC,
        name VARCHAR,
        events BIGINT
    )
AS $BODY$
BEGIN
  RETURN QUERY
    SELECT
        ValidRegions.run_id,
        ValidRegions.duration,
        ValidRegions.id,
        ValidRegions.name,
        ValidRegions.events
    FROM
        profile_scops_valid_regions(exp_ids) AS ValidRegions
    WHERE
        ValidRegions."name" IN (
            SELECT scopName
            FROM (
                SELECT (splitarray[1] || '::Parent') AS parentName, Splits."name" AS scopName
                FROM (
                    SELECT *, string_to_array(V1."name", '::SCoP') AS splitarray
                    FROM profile_scops_valid_regions(exp_ids) AS V1
                    WHERE V1."name" LIKE '%::SCoP'
                ) AS Splits
            ) AS Names
            WHERE parentName NOT IN (
                SELECT V2."name"
                FROM profile_scops_valid_regions(exp_ids) AS V2
                WHERE V2."name" LIKE '%::Parent'
            )
        );
END
$BODY$ language plpgsql;

DROP FUNCTION IF EXISTS profile_scops_ratios_max_regions(exp_ids UUID[]);
CREATE OR REPLACE FUNCTION profile_scops_ratios_max_regions(exp_ids UUID[])
    RETURNS TABLE (
        project VARCHAR,
        T_Parent NUMERIC,
        T_Total DOUBLE PRECISION,
        DynCov DOUBLE PRECISION
    )
AS $BODY$
BEGIN
  RETURN QUERY
    SELECT
        MaxParents.project,
        sum(MaxParents.t_parent) AS t_parent,
        sum(MaxParents.exectime_us) AS exectime_us,
        sum(MaxParents.dyncov_pct) AS dyncov_pct
    FROM (
        SELECT
            total.project,
            parents.t_parent,
            total.exectime_us,
            (parents.t_parent * 100/ total.exectime_us) AS DynCov_pct
        FROM
            profile_scops_exec_times(exp_ids) AS total,
            (
                SELECT
                    run.project_name AS project,
                    toplevel.duration AS t_parent
                FROM
                    profile_scops_toplevel_scops(exp_ids) AS toplevel,
                    run
                WHERE
                    run.id = toplevel.run_id
            ) AS parents
        WHERE
            total.project = parents.project
        UNION ALL
        SELECT *
        FROM
            profile_scops_ratios(exp_ids, '%::Parent')
    ) AS MaxParents
    GROUP BY MaxParents.project;
END
$BODY$ language plpgsql;
