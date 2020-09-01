DROP FUNCTION IF EXISTS recompilation(exp_ids UUID[], recomp_status VARCHAR);
CREATE OR REPLACE FUNCTION recompilation(exp_ids UUID[], recomp_status VARCHAR)
  returns table(name VARCHAR, value VARCHAR, run_id INTEGER) as $recompilation$
BEGIN
  RETURN QUERY
    SELECT config.name,
           config.value,
           config.run_id
    FROM config, run WHERE
        run.id = config.run_id AND
        run.status = 'completed' AND
			  config.name = 'recompilation' AND
				config.value = recomp_status AND
				run.experiment_group = ANY (exp_ids);
END;
$recompilation$ language plpgsql;
