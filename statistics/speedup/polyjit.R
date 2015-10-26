# get_raw_runtime <- function(name, experiment, connection) {
#   query <- strwrap(sprintf(paste(
#     "SELECT project_name, name, SUM(value) as sumval
#      FROM run, metrics WHERE run.id = metrics.run_id
#      AND experiment_name = '%s'
#      AND experiment_group = '%s'::uuid
#      GROUP BY run_group, project_name, name, value
#      ORDER BY sumval DESC;
#     "), name, experiment), width=10000, simplify=TRUE)
#   query_res <- dbSendQuery(connection, query)
#   res <- melt(dbFetch(query_res))
#   dbClearResult(query_res)
#   if (nrow(res) > 0) {
#     res$project_name <- factor(res$project_name, levels = res$project_name)
#   }
#
#   return(res)
# }
#
# get_papi_dyncov <- function(experiment, connection, order_by) {
#   query <- strwrap(sprintf(paste(
#     "SELECT run.project_name, metrics.value, project.domain
#     FROM run, metrics, project
#     WHERE experiment_group = '%s'
#     AND run.id = metrics.run_id
#     AND run.project_name = project.name
#     AND metrics.name = 'pprof.dyncov' ORDER BY %s;
#     "), experiment, order_by), width=10000, simplify=TRUE)
#   query_res <- dbSendQuery(connection, query)
#   res <- melt(dbFetch(query_res))
#
#   if (nrow(res) > 0) {
#     res$project_name <- factor(res$project_name, levels = res$project_name)
#   }
#   dbClearResult(query_res)
#   return(res)
# }
#
# papi_dyncov <- function(c, exp) {
#   q <- strwrap(sprintf(paste("SELECT project_name, name, MAX(value)
#                              FROM run, metrics
#                              WHERE run.id = metrics.run_id
#                              AND experiment_group = '%s'
#                              AND experiment_name = 'papi'
#                              AND name = 'pprof.dyncov'
#                              GROUP BY project_name, name
#                              ORDER BY project_name;"), exp), width=10000, simplify=TRUE)
#   return(sql.get(c, q))
# }
#
# papi_time <- function(c, exp) {
#   q <- strwrap(sprintf(paste("SELECT project_name, name, SUM(value)
#                              FROM run, metrics
#                              WHERE run.id = metrics.run_id
#                              AND experiment_group = '%s'
#                              AND experiment_name = 'papi'
#                              AND name = 'pprof.time.total_s'
#                              GROUP BY project_name, name
#                              ORDER BY project_name;"), exp), width=10000, simplify=TRUE)
#   return(sql.get(c, q))
# }
#
# papi_time_scops <- function(c, exp) {
#   q <- strwrap(sprintf(paste("SELECT project_name, name, SUM(value)
#                              FROM run, metrics
#                              WHERE run.id = metrics.run_id
#                              AND experiment_group = '%s'::uuid
#                              AND experiment_name = 'papi'
#                              AND name = 'pprof.time.scops_s'
#                              GROUP BY project_name, name
#                              ORDER BY project_name;"), exp), width=10000, simplify=TRUE)
#   return(sql.get(c, q))
# }
#
# likwid.get_metrics <- function(c) {
#   q <- strwrap(paste("SELECT DISTINCT(metric) FROM likwid;"), width=10000, simplify=TRUE)
#   return(sql.get(c, q))
# }
#
# likwid.total <- function(c, exp, aggr, metric) {
#   cat("likwid.total (input): ", exp, aggr, metric, "\n")
#   q <- strwrap(sprintf(paste("
#
#  SELECT project, num_cores, SUM(total) as total FROM
#   (
#     SELECT project_name as Project, region, CAST(num_cores as Integer), %s(value) as total
#     FROM run_likwid
#     WHERE metric = '%s'
#     AND experiment_group = '%s'::uuid
#     AND experiment_name = 'polyjit'
#     AND (core != 'Min' AND core != 'Max' AND core != 'Avg')
#     AND region = 'polyjit.main'
#     GROUP BY Project, num_cores, region, metric ORDER BY project, num_cores
#   ) as run_likwid_f
#  GROUP BY project, num_cores;"), aggr, metric, exp), width=10000, simplify=TRUE)
#
#   qr <- dbSendQuery(c, "REFRESH MATERIALIZED VIEW run_likwid WITH DATA;")
#   dbFetch(qr)
#   dbClearResult(qr)
#
#   qr <- dbSendQuery(c, q)
#   cat("likwid.total: ", dbGetRowCount(qr), "\n")
#   res <- dbFetch(qr)
#   if (dbGetRowCount(qr) > 0) {
#     res <- melt(res, id.vars = c("project", "num_cores"))
#   }
#   dbClearResult(qr)
#   return(res)
# }
#
# likwid.runtime <- function(c, exp, aggr, metric) {
#   cat("likwid.runtime (input): ", exp, aggr, metric, "\n")
#   q <- strwrap(sprintf(paste("
# SELECT project, num_cores, SUM(runtime) as runtime FROM
#   (
#     SELECT project_name as Project, region, CAST(num_cores as Integer), %s(value) as runtime
#     FROM run_likwid
#     WHERE metric = '%s'
#     AND experiment_group = '%s'::uuid
#     AND experiment_name = 'polyjit'
#     AND (core != 'Min' AND core != 'Max' AND core != 'Avg')
#     AND region not like 'po%%yjit.%%'
#     GROUP BY Project, num_cores, region, metric ORDER BY project, num_cores
#   ) as run_likwid_f
# GROUP BY project, num_cores;"), aggr, metric, exp), width=10000, simplify=TRUE)
#
#   qr <- dbSendQuery(c, "REFRESH MATERIALIZED VIEW run_likwid WITH DATA;")
#   dbFetch(qr)
#   dbClearResult(qr)
#
#   qr <- dbSendQuery(c, q)
#   cat("likwid.runtime: ", dbGetRowCount(qr), "\n")
#   res <- dbFetch(qr)
#   if (dbGetRowCount(qr) > 0) {
#     res <- melt(res, id.vars = c("project", "num_cores"))
#   }
#   dbClearResult(qr)
#   return(res)
# }
#
# likwid.overhead <- function(c, exp, aggr, metric) {
#   cat("likwid.overhead (input): ", exp, aggr, metric, "\n")
#   q <- strwrap(sprintf(paste("
# SELECT project, num_cores, SUM(overhead) as overhead FROM
#     (
#       SELECT project_name as Project, region, CAST(num_cores as Integer), %s(value) as overhead
#       FROM run_likwid
#       WHERE metric = '%s'
#       AND experiment_group = '%s'::uuid
#       AND experiment_name = 'polyjit'
#       AND (core != 'Min' AND core != 'Max' AND core != 'Avg')
#       AND region like 'po%%yjit%%' AND not region = 'polyjit.main'
#       GROUP BY Project, num_cores, region, metric ORDER BY project, num_cores
#     ) as run_likwid_f
# GROUP BY project, num_cores;"), aggr, metric, exp), width=10000, simplify=TRUE)
#
#   qr <- dbSendQuery(c, "REFRESH MATERIALIZED VIEW run_likwid WITH DATA;")
#   dbFetch(qr)
#   dbClearResult(qr)
#
#   qr <- dbSendQuery(c, q)
#   cat("likwid.overhead: ", dbGetRowCount(qr), "\n")
#
#   res <- dbFetch(qr)
#   if (dbGetRowCount(qr) > 0) {
#     res <- melt(res, id.vars = c("project", "num_cores"))
#   }
#   dbClearResult(qr)
#   return(res)
# }
#
# compilestats <- function(c, exp, name, component) {
#   q <- strwrap(sprintf(paste("
#     SELECT project_name, experiment_name, name, SUM(value)
#     FROM run, compilestats
#     WHERE run.id = compilestats.run_id AND
#           experiment_group = '%s'::uuid AND
#           component = '%s' AND
#           name = '%s'
#     GROUP BY project_name, experiment_name, name;"), exp, component, name),
#                width = 10000, simplify = TRUE)
#   return(sql.get(c, q))
# }
#
# compilestats.names <- function(c, component) {
#   if (is.null(component) || length(component) == 0)
#     return (c("No data..."))
#
#   q <- strwrap(sprintf(paste("SELECT DISTINCT(name) FROM compilestats WHERE component = '%s';"), component), width=10000, simplify=TRUE)
#   return(sql.get(c, q))
# }
#
# compilestats.components <- function(c) {
#   q <- strwrap(paste("SELECT DISTINCT(component) FROM compilestats;"), width=10000, simplify=TRUE)
#   return(sql.get(c, q))
# }
#
# runlog <- function(c, exp) {
#   q <- strwrap(sprintf(paste("SELECT status, project_name as project,
#                                      experiment_name as experiment,
#                                      (\"end\" - \"begin\") as duration,
#                                      command FROM run_log
#                               WHERE experiment_group = '%s'::uuid ORDER BY status, project ASC;"), exp),
#                width=10000, simplify=TRUE)
#   sql.get(c, "REFRESH MATERIALIZED VIEW run_log WITH DATA;")
#
#   return(sql.get(c, q))
# }

createCounter <- function(value) {
  function(i) {
    value <<- value + i
  }
}

inc <- createCounter(0)

sql.get <- function(c, query) {
  n <- inc(1)
  cat(n,"-", "query: ", query, "\n")
  cat(n,"-", "typeof(c):", typeof(c), " ", "typeof(query)", typeof(query), "\n")
  qr <- dbSendQuery(c, query)
  res <- dbFetch(qr)
  cat(n,"-", "nrow: ", dbGetRowCount(qr), "\n")
  dbClearResult(qr)
  return(res)
}

getSelections <- function(name, exps) {
  if (is.null(exps))
    return(NULL)
  if (!is.null(name)) {
    exps <- exps[exps$experiment_name == name, ]
  }

  newNames <- paste0(exps[,"experiment_name"],
                     rep(" @ ", nrow(exps)),
                     exps[,"completed"])
  groups <- exps[, "experiment_group"]
  names(groups) <- newNames
  return(groups)
}

get_experiments <- function(c) {
  q <- strwrap(paste(
    "SELECT CAST(experiment_group AS VARCHAR), experiment_name, MAX(finished) as completed
         FROM run
         WHERE NOT experiment_group = '00000000-0000-0000-0000-000000000000'::uuid
         GROUP BY experiment_group, experiment_name ORDER BY completed;"), width=10000, simplify=TRUE)
  return(sql.get(c, q))
}

get_experiments_per_project <- function(c, project) {
  q <- strwrap(sprintf(paste(
    "SELECT CAST(experiment_group AS VARCHAR) as \"UUID\", experiment_name as \"Name\", MAX(finished) as \"Completed at\"
         FROM run WHERE project_name = '%s'
         GROUP BY experiment_group, experiment_name ORDER BY \"Completed at\";"), project), width=10000, simplify=TRUE)
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

flamegraph <- function(c, exp, project) {
  q <- sprintf(paste(
    "SELECT metadata.value FROM run, metadata WHERE run.id = metadata.run_id AND run.experiment_group = '%s' AND run.project_name = '%s' AND metadata.name = 'perf.flamegraph'
;"), exp, project)
  return(sql.get(c, q)$value)
}

trim <- function (x) gsub("^\\s+|\\s+$", "", x)