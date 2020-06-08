DROP FUNCTION IF EXISTS compare_region_wise(exp_ids UUID[]);
CREATE OR REPLACE function compare_region_wise(exp_ids UUID[])
	returns
    table(project VARCHAR,
          region_name VARCHAR,
          cores VARCHAR,
          runtime_jit NUMERIC,
          runtime_no_recomp NUMERIC,
          speedup NUMERIC)
AS $compare_region_wise$
BEGIN
  RETURN QUERY
select * from
(
select
  results.project,
  results.region,
  results.cores,
  results.runtime_jit,
  results.runtime_no_recomp,
  speedup(results.runtime_no_recomp, results.runtime_jit) as speedup FROM
  (
    SELECT
      recomp_enabled.name AS project,
      recomp_enabled.region,
      recomp_enabled.value AS cores,
      recomp_enabled.runtime AS runtime_jit,
      recomp_disabled.runtime AS runtime_no_recomp
    FROM
      run_durations(exp_ids, 'enabled') as recomp_enabled,
      run_durations(exp_ids, 'disabled') as recomp_disabled
    WHERE
	    recomp_enabled.name = recomp_disabled.name and
	    recomp_enabled.region = recomp_disabled.region and
	    recomp_enabled.value = recomp_disabled.value and
	    recomp_enabled.region <> 'START'
    order by
      project, cores, region
  ) as results
) as reulsts_f
order by speedup desc;
end
$compare_region_wise$ language plpgsql;
