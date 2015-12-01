createCounter <- function(value) {
  function(i) {
    value <<- value + i
  }
}

inc <- createCounter(0)

sql.get <- function(c, query) {
  n <- inc(1)
  cat(n,"-", "query: ", query, "\n")
  qr <- dbSendQuery(c, query)
  res <- dbFetch(qr)
  cat(n,"-", "result set: ", dbGetRowCount(qr), "\n")
  dbClearResult(qr)
  return(res)
}

getSelections <- function(name, exps) {
  if (is.null(exps))
    return(NULL)
  if (!is.null(name)) {
    exps <- exps[exps$name == name, ]
  }

  newNames <- paste0(exps[,"name"],
                     rep(" @ ", nrow(exps)),
                     exps[,"description"])
  groups <- exps[, "id"]
  names(groups) <- newNames
  return(groups)
}

get_experiments <- function(c) {
  q <- strwrap(paste(
    "SELECT name, cast(id as VARCHAR) as id, description FROM experiment ORDER BY name, begin ASC;"), width=10000, simplify=TRUE)
  return(sql.get(c, q))
}

get_experiments_per_project <- function(c, project) {
  q <- strwrap(sprintf(paste(
    "SELECT CAST(experiment_group AS VARCHAR) as \"UUID\", experiment_name as \"Name\", MAX(finished) as \"Completed at\"
         FROM run WHERE project_name = '%s'
         GROUP BY experiment_group, experiment_name ORDER BY \"Completed at\";"), project), width=10000, simplify=TRUE)
  return(sql.get(c, q))
}

get_projects_per_experiment <- function(c, exp_id) {
  q <- sprintf("SELECT project_name, status, MAX(finished) FROM run, log WHERE run.id = log.run_id AND experiment_group = '%s' GROUP BY project_name, status;", exp_id)
  return(sql.get(c, q))
}

query_speedup_papi <- function(extra_filter, base, jit, papi) {
  q <- sprintf(paste(
"SELECT spd.project_name, spd.cores, spd.ptime, spd.time, spd.speedup,
    CASE WHEN spd.speedup >= 0.5 OR spd.speedup = 0 THEN spd.speedup

    WHEN spd.speedup > 0 AND spd.speedup < 0.5 THEN -1/spd.speedup
    END AS speedup_corrected,
    (spd.t_all / (spd.t_all - spd.t_scops + spd.t_scops / spd.cores)) as speedup_amdahl
 FROM
 (
    SELECT pjit.project_name, pjit.cval AS cores,  pjit.sum AS ptime, raw.sum AS time,
           (raw.sum / pjit.sum) AS speedup, pprof_total.sum AS t_all, pprof_scops.sum AS t_scops
    FROM
    (
      SELECT project_name, metrics.name, SUM(metrics.value), config.name,
             cast ( config.value AS INTEGER) AS cval
      FROM run, metrics, config
      WHERE experiment_group = '%s' AND run.id = metrics.run_id AND run.id = config.run_id AND metrics.name = 'time.real_s'
      GROUP BY project_name, metrics.name, config.name, cval
    ) AS pjit,
    (
      SELECT project_name, metrics.name, SUM(metrics.value), config.name, cast ( config.value AS INTEGER) AS cval
      FROM run, metrics, config
      WHERE experiment_group = '%s' AND run.id = metrics.run_id AND run.id = config.run_id AND metrics.name = 'time.real_s' AND (experiment_name = 'raw' OR config.value = '1')
      GROUP BY project_name, metrics.name, config.name, cval
    ) AS raw,
    (
      SELECT project_name, metrics.name, SUM(metrics.value)
      FROM run, metrics
      WHERE experiment_group = '%s' AND run.id = metrics.run_id AND metrics.name = 'pprof.time.total_s' 
      GROUP BY project_name, metrics.name
    ) AS pprof_total,
    (
      SELECT project_name, metrics.name, SUM(metrics.value)
      FROM run, metrics
      WHERE experiment_group = '%s' AND run.id = metrics.run_id AND metrics.name = 'pprof.time.scops_s' 
      GROUP BY project_name, metrics.name
  ) AS pprof_scops
    WHERE pjit.project_name = raw.project_name AND pjit.project_name = pprof_total.project_name AND pjit.project_name = pprof_scops.project_name
    ORDER BY cores ASC
 ) AS spd, project
 WHERE spd.project_name = project.name %s ORDER BY speedup_corrected
;"), jit, base, papi, papi, extra_filter)
  return(q)
}
query_speedup_no_papi <- function(extra_filter, base, jit) {
    q <- sprintf(paste(
"SELECT spd.project_name, spd.cores, spd.ptime, spd.time, spd.speedup,
    CASE WHEN spd.speedup >= 0.5 OR spd.speedup = 0 THEN spd.speedup

    WHEN spd.speedup > 0 AND spd.speedup < 0.5 THEN -1/spd.speedup
    END AS speedup_corrected
 FROM
 (
    SELECT pjit.project_name, pjit.cval AS cores,  pjit.sum AS ptime, raw.sum AS time,
           (raw.sum / pjit.sum) AS speedup
    FROM
    (
      SELECT project_name, metrics.name, SUM(metrics.value), config.name,
             cast ( config.value AS INTEGER) AS cval
      FROM run, metrics, config
      WHERE experiment_group = '%s' AND run.id = metrics.run_id AND run.id = config.run_id AND metrics.name = 'time.real_s'
      GROUP BY project_name, metrics.name, config.name, cval
    ) AS pjit,
    (
      SELECT project_name, metrics.name, SUM(metrics.value), config.name, cast ( config.value AS INTEGER) AS cval
      FROM run, metrics, config
      WHERE experiment_group = '%s' AND run.id = metrics.run_id AND run.id = config.run_id AND metrics.name = 'time.real_s' AND (experiment_name = 'raw' OR config.value = '1')
      GROUP BY project_name, metrics.name, config.name, cval
    ) AS raw
    WHERE pjit.project_name = raw.project_name
    ORDER BY cores ASC
 ) AS spd, project
 WHERE spd.project_name = project.name %s ORDER BY speedup_corrected
;"), jit, base, extra_filter)
  return(q)
}

speedup <- function(c, base, jit, papi, projects = NULL, groups = NULL) {
  extra_filter <- ""
  range_filter <- ""
  if (!is.null(projects)) {
    extra_filter <- sprintf("AND project.name IN (%s)",
                            paste(lapply(as.vector(projects),
                                         function(x) sprintf("\'%s\'", x)),
                                  collapse=", "))
  }
  if (!is.null(groups)) {
    extra_filter <- paste(extra_filter,
                          sprintf(" AND project.group_name IN (%s)",
                            paste(lapply(as.vector(groups),
                                         function(x) sprintf("\'%s\'", x)),
                                  collapse=", ")))
  }

  q <- ""
  if (!is.null(papi)) {
    cat("query-speedup (papi)\n val: (", paste(papi), ")\n")
    q <- query_speedup_papi(extra_filter, base, jit, papi)
  } else {
    cat("query-speedup (no papi)\n")
    q <- query_speedup_no_papi(extra_filter, base, jit)
  }
  return(sql.get(c, q))
}

speedup_per_project <- function(c, project, base, exps = NULL) {
  exp_filter <- ""
  if (!is.null(exps) && length(exps) > 0) {
    exp_filter <- sprintf("AND experiment_group IN (%s)",
                          paste(lapply(as.vector(exps),
                                       function(x) sprintf("\'%s\'", x)),
                                collapse=", "))
  }
  cat(paste(exp_filter))
  q <- sprintf(paste(
"
SELECT CAST(spd.experiment_group AS VARCHAR), spd.project_name, spd.cores, spd.ptime, spd.time, spd.speedup,
    CASE WHEN spd.speedup >= 0.5 OR spd.speedup = 0 THEN spd.speedup

    WHEN spd.speedup > 0 AND spd.speedup < 0.5 THEN -1/spd.speedup
    END AS speedup_corrected
 FROM
 (
    SELECT pjit.experiment_group, pjit.project_name, pjit.cval AS cores,  pjit.sum AS ptime, raw.sum AS time,
           (raw.sum / pjit.sum) AS speedup
    FROM
    (
      SELECT experiment_group, project_name, metrics.name, SUM(metrics.value), config.name,
             cast ( config.value AS INTEGER) AS cval
      FROM run, metrics, config
      WHERE project_name = '%s' and run.id = metrics.run_id AND run.id = config.run_id AND metrics.name = 'time.real_s' %s
      GROUP BY experiment_group, project_name, metrics.name, config.name, cval
      ORDER BY project_name, cval
    ) AS pjit,
    (
      SELECT experiment_group, project_name, metrics.name, SUM(metrics.value), config.name, cast ( config.value AS INTEGER) AS cval
      FROM run, metrics, config
      WHERE project_name = '%s' and experiment_group = '%s' AND run.id = metrics.run_id AND run.id = config.run_id AND metrics.name = 'time.real_s' AND (experiment_name = 'raw' OR config.value = '1')
      GROUP BY experiment_group, project_name, metrics.name, config.name, cval
      ORDER BY project_name, cval
    ) AS raw
    WHERE pjit.project_name = raw.project_name
    ORDER BY cores ASC
 ) AS spd, project
 WHERE spd.project_name = project.name ORDER BY speedup_corrected
;
"), project, exp_filter, project, base)
  return(sql.get(c, q))
}

projects <- function(c) {
  q <- "SELECT name from project;"
  return(sql.get(c, q))
}

perfProjects <- function(c, exp = NULL) {
  if (is.null(exp) || (is.character(exp) && exp == ''))
    q <- "SELECT DISTINCT project.name FROM project, run, metadata WHERE run.id = metadata.run_id AND project.name = run.project_name and experiment_name = 'pj-perf';"
  else
    q <- sprintf(paste(
      "SELECT DISTINCT project.name FROM project, run, metadata
       WHERE run.id = metadata.run_id AND
             project.name = run.project_name AND
             experiment_name = 'pj-perf' AND
             experiment_group = '%s';"), exp)
  return(sql.get(c, q))
}

groups <- function(c) {
  q <- "SELECT DISTINCT group_name from project;"
  return(sql.get(c, q))
}

taskGroups <- function(c, exp) {
  q <- sprintf(paste(
    "SELECT
      CAST(id as VARCHAR) as id,
      project,
      to_char(\"end\" - \"begin\", 'HH24h MIm SSs') as \"Duration\",
      to_char(\"begin\", 'HH24:MI:SS') as \"Started\",
      to_char(\"end\", 'HH24:MI:SS') as \"Finished\",
      CAST(status as VARCHAR) as status
    FROM rungroup
    WHERE experiment = '%s'
    ORDER BY status, project;"), exp)
  return(sql.get(c, q))
}

tasks <- function(c, exp, groups = NULL) {
  run_filter <- ""
  if (!is.null(groups) && length(groups) > 0) {
    run_filter <- sprintf("AND run_group IN (%s)",
                          paste(lapply(as.vector(groups),
                                       function(x) sprintf("\'%s\'", x)),
                                collapse=", "))
  }

  q <- sprintf(paste(
    "SELECT id, command, CAST(status as VARCHAR) as Status, to_char(\"end\" - \"begin\", 'HH24h MIm SSs') as Duration
     FROM run
     WHERE experiment_group = '%s' %s;"), exp, run_filter)
  return(sql.get(c, q))
}

stdout <- function(c, run) {
  q <- sprintf("SELECT stderr FROM log where run_id = %s;", run)
  return(sql.get(c, q))
}

stderr <- function(c, run) {
  q <- sprintf("SELECT stdout FROM log where run_id = %s;", run)
  return(sql.get(c, q))
}

flamegraph <- function(c, exp, project) {
  q <- sprintf(paste(
    "SELECT metadata.value FROM run, metadata WHERE run.id = metadata.run_id AND run.experiment_group = '%s' AND run.project_name = '%s' AND metadata.name = 'perf.flamegraph'
;"), exp, project)
  return(sql.get(c, q)$value)
}

trim <- function (x) gsub("^\\s+|\\s+$", "", x)

in_set_expr <- function(key, elems = NULL) {
  set_expr <- ""
  if (!is.null(elems)) {
    set_expr <- paste(set_expr,
                      sprintf(" AND %s IN (%s)", key,
                              paste(lapply(as.vector(elems),
                                           function(x) sprintf("\'%s\'", x)),
                                    collapse=", ")))
  }
  return(set_expr)
}

baseline_vs_pivot <- function(c, baselines, experiments, projects, groups) {
  in_baselines <- in_set_expr("experiment_group", baselines)
  in_experiments <- in_set_expr("experiment_group", experiments)
  in_projects <- in_set_expr("project.name", projects)
  in_groups <- in_set_expr("project.group_name", groups)

  q <- sprintf(paste("
SELECT * FROM
(
SELECT
	baseline.project,
	baseline.description AS bdesc,
	pivot.name AS pname,
	baseline.name AS bname,
	FORMAT('%%s (%%s)', baseline.name, baseline.description) as bid,
    FORMAT('%%s (%%s)', pivot.name, pivot.description) as gname, 
	CAST(pivot.id AS TEXT) AS pid,
	baseline.time AS seq_time,
	pivot.time AS par_time,
    pivot.timestamp AS timestamp,
	CAST(pivot.num_cores AS INTEGER) AS num_cores,
	( baseline.time / pivot.time ) AS speedup
FROM
(
	SELECT 	project_name AS project,
		experiment.description,
		experiment.id AS id,
		experiment.name AS name,
        config.value AS num_cores,
		SUM(metrics.value) AS time
	FROM 	run,
		metrics,
		config,
		experiment,
    project
	WHERE 	experiment.id = run.experiment_group AND
		run.id = metrics.run_id AND 
		run.id = config.run_id AND
		metrics.name = 'time.real_s' AND
		config.name = 'cores' AND
    run.project_name = project.name AND
		experiment_name IN ('raw', 'pj-raw')
    %s
    %s
    %s
	GROUP BY experiment.name, experiment.id, project_name, config.value
) baseline JOIN
(
	SELECT 	project_name AS project,
		experiment.description,
		experiment.id AS id,
		experiment.name AS name,
		config.value as num_cores,
		SUM(metrics.value) AS time,
        MIN(run.end) AS timestamp
	FROM 	run,
		metrics,
		config,
		experiment
	WHERE 	experiment.id = run.experiment_group AND
		run.id = metrics.run_id AND 
		run.id = config.run_id AND
		metrics.name = 'time.real_s' AND
		config.name = 'cores' AND
    metrics.value <> 0 AND
		experiment_name IN ('pj-raw', 'polly-openmp')
    %s
	GROUP BY experiment.id, experiment.name, project_name, config.value
) pivot ON (baseline.project = pivot.project AND baseline.num_cores = pivot.num_cores)
ORDER BY baseline.project, baseline.description, pivot.project, pivot.description
) p;"
	 ), in_baselines, in_projects, in_groups, in_experiments)
	 return(sql.get(c, query = q))
}