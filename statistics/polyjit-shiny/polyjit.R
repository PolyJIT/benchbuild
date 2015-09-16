library(ggplot2)
library(DBI)
library(RPostgres)
library(reshape2)
library(ggthemes)
library(scales)
library(sm)
library(vioplot)

get_experiments <- function(connection) {
  rs <- dbSendQuery(connection, strwrap(paste(
    "SELECT experiment_group, experiment_name, MAX(finished) as completed
         FROM run
         WHERE NOT experiment_group = '00000000-0000-0000-0000-000000000000'::uuid
         GROUP BY experiment_group, experiment_name ORDER BY completed;"), width=10000, simplify=TRUE))
  res <- dbFetch(rs)
  head(res)
  dbClearResult(rs)
  return(res)
}

get_raw_runtime <- function(name, experiment, connection) {
  query <- strwrap(sprintf(paste(
    "SELECT project_name, name, SUM(value) as sumval
     FROM run, metrics WHERE run.id = metrics.run_id
     AND experiment_name = '%s'
     AND experiment_group = '%s'::uuid
     GROUP BY run_group, project_name, name, value
     ORDER BY sumval DESC;
    "), name, experiment), width=10000, simplify=TRUE)
  query_res <- dbSendQuery(connection, query)
  res <- melt(dbFetch(query_res))
  dbClearResult(query_res)
  if (nrow(res) > 0) {
    res$project_name <- factor(res$project_name, levels = res$project_name)
  }

  return(res)
}

get_papi_dyncov <- function(experiment, connection, order_by) {
  query <- strwrap(sprintf(paste(
    "SELECT run.project_name, metrics.value, project.domain
    FROM run, metrics, project
    WHERE experiment_group = '%s'
    AND run.id = metrics.run_id
    AND run.project_name = project.name
    AND metrics.name = 'pprof.dyncov' ORDER BY %s;
    "), experiment, order_by), width=10000, simplify=TRUE)
  query_res <- dbSendQuery(connection, query)
  res <- melt(dbFetch(query_res))

  if (nrow(res) > 0) {
    res$project_name <- factor(res$project_name, levels = res$project_name)
  }
  dbClearResult(query_res)
  return(res)
}

papi_dyncov <- function(c, exp) {
  q <- strwrap(sprintf(paste("SELECT project_name, name, MAX(value)
                             FROM run, metrics
                             WHERE run.id = metrics.run_id
                             AND experiment_group = '%s'
                             AND experiment_name = 'papi'
                             AND name = 'pprof.dyncov'
                             GROUP BY project_name, name
                             ORDER BY project_name;"), exp), width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, q)
  res <- melt(dbFetch(qr))
  dbClearResult(qr)
  return(res)
}

papi_time <- function(c, exp) {
  q <- strwrap(sprintf(paste("SELECT project_name, name, SUM(value)
                             FROM run, metrics
                             WHERE run.id = metrics.run_id
                             AND experiment_group = '%s'
                             AND experiment_name = 'papi'
                             AND name = 'pprof.time.total_s'
                             GROUP BY project_name, name
                             ORDER BY project_name;"), exp), width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, q)
  res <- melt(dbFetch(qr))
  dbClearResult(qr)
  return(res)
}

papi_time_scops <- function(c, exp) {
  q <- strwrap(sprintf(paste("SELECT project_name, name, SUM(value)
                             FROM run, metrics
                             WHERE run.id = metrics.run_id
                             AND experiment_group = '%s'::uuid
                             AND experiment_name = 'papi'
                             AND name = 'pprof.time.scops_s'
                             GROUP BY project_name, name
                             ORDER BY project_name;"), exp), width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, q)
  res <- melt(dbFetch(qr))
  dbClearResult(qr)
  return(res)
}

likwid.get_metrics <- function(c) {
  q <- strwrap(paste("SELECT DISTINCT(metric) FROM likwid;"), width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, q)
  res <- melt(dbFetch(qr))
  dbClearResult(qr)
  return(res)
}

likwid.total <- function(c, exp, aggr, metric) {
  cat("likwid.total (input): ", exp, aggr, metric, "\n")
  q <- strwrap(sprintf(paste("

 SELECT project, num_cores, SUM(total) as total FROM
  (
    SELECT project_name as Project, region, CAST(num_cores as Integer), %s(value) as total
    FROM run_likwid
    WHERE metric = '%s'
    AND experiment_group = '%s'::uuid
    AND experiment_name = 'polyjit'
    AND (core != 'Min' AND core != 'Max' AND core != 'Avg')
    AND region = 'polyjit.main'
    GROUP BY Project, num_cores, region, metric ORDER BY project, num_cores
  ) as run_likwid_f
 GROUP BY project, num_cores;"), aggr, metric, exp), width=10000, simplify=TRUE)
  
  qr <- dbSendQuery(c, "REFRESH MATERIALIZED VIEW run_likwid WITH DATA;")
  dbFetch(qr)
  dbClearResult(qr)
  
  qr <- dbSendQuery(c, q)
  cat("likwid.total: ", dbGetRowCount(qr), "\n")
  res <- dbFetch(qr)
  if (dbGetRowCount(qr) > 0) {
    res <- melt(res, id.vars = c("project", "num_cores"))
  }
  dbClearResult(qr)
  return(res)
}

likwid.runtime <- function(c, exp, aggr, metric) {
  cat("likwid.runtime (input): ", exp, aggr, metric, "\n")
  q <- strwrap(sprintf(paste("
SELECT project, num_cores, SUM(runtime) as runtime FROM
  (
    SELECT project_name as Project, region, CAST(num_cores as Integer), %s(value) as runtime
    FROM run_likwid
    WHERE metric = '%s'
    AND experiment_group = '%s'::uuid
    AND experiment_name = 'polyjit'
    AND (core != 'Min' AND core != 'Max' AND core != 'Avg')
    AND region not like 'po%%yjit.%%'
    GROUP BY Project, num_cores, region, metric ORDER BY project, num_cores
  ) as run_likwid_f
GROUP BY project, num_cores;"), aggr, metric, exp), width=10000, simplify=TRUE)
  
  qr <- dbSendQuery(c, "REFRESH MATERIALIZED VIEW run_likwid WITH DATA;")
  dbFetch(qr)
  dbClearResult(qr)
  
  qr <- dbSendQuery(c, q)
  cat("likwid.runtime: ", dbGetRowCount(qr), "\n")
  res <- dbFetch(qr)
  if (dbGetRowCount(qr) > 0) {
    res <- melt(res, id.vars = c("project", "num_cores"))
  }
  dbClearResult(qr)
  return(res)
}

likwid.overhead <- function(c, exp, aggr, metric) {
  cat("likwid.overhead (input): ", exp, aggr, metric, "\n")
  q <- strwrap(sprintf(paste("
SELECT project, num_cores, SUM(overhead) as overhead FROM
    (
      SELECT project_name as Project, region, CAST(num_cores as Integer), %s(value) as overhead
      FROM run_likwid
      WHERE metric = '%s'
      AND experiment_group = '%s'::uuid
      AND experiment_name = 'polyjit'
      AND (core != 'Min' AND core != 'Max' AND core != 'Avg')
      AND region like 'po%%yjit%%' AND not region = 'polyjit.main'
      GROUP BY Project, num_cores, region, metric ORDER BY project, num_cores
    ) as run_likwid_f
GROUP BY project, num_cores;"), aggr, metric, exp), width=10000, simplify=TRUE)
  
  qr <- dbSendQuery(c, "REFRESH MATERIALIZED VIEW run_likwid WITH DATA;")
  dbFetch(qr)
  dbClearResult(qr)
  
  qr <- dbSendQuery(c, q)
  cat("likwid.overhead: ", dbGetRowCount(qr), "\n")

  res <- dbFetch(qr)
  if (dbGetRowCount(qr) > 0) {
    res <- melt(res, id.vars = c("project", "num_cores"))
  }
  dbClearResult(qr)
  return(res)
}

compilestats <- function(c, exp, name, component) {
  q <- strwrap(sprintf(paste("
    SELECT project_name, experiment_name, name, SUM(value)
    FROM run, compilestats
    WHERE run.id = compilestats.run_id AND
          experiment_group = '%s'::uuid AND
          component = '%s' AND
          name = '%s'
    GROUP BY project_name, experiment_name, name;"), exp, component, name),
               width = 10000, simplify = TRUE)
  qr <- dbSendQuery(c, q)
  res <- dbFetch(qr)
  dbClearResult(qr)
  return(res)
}

compilestats.names <- function(c, component) {
  if (is.null(component) || length(component) == 0)
    return (c("No data..."))

  q <- strwrap(sprintf(paste("SELECT DISTINCT(name) FROM compilestats WHERE component = '%s';"), component), width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, q)
  res <- melt(dbFetch(qr))
  dbClearResult(qr)
  return(res)
}

compilestats.components <- function(c) {
  q <- strwrap(paste("SELECT DISTINCT(component) FROM compilestats;"), width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, q)
  res <- melt(dbFetch(qr))
  dbClearResult(qr)
  return(res)
}

runlog <- function(c, exp) {
  q <- strwrap(sprintf(paste("SELECT status, project_name as project,
                                     experiment_name as experiment,
                                     (\"end\" - \"begin\") as duration,
                                     command FROM run_log
                              WHERE experiment_group = '%s'::uuid ORDER BY status, project ASC;"), exp),
               width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, "REFRESH MATERIALIZED VIEW run_log WITH DATA;")
  dbFetch(qr)
  dbClearResult(qr)

  qr <- dbSendQuery(c, q)
  res <- dbFetch(qr)
  dbClearResult(qr)
  return(res)
}
