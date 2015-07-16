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
  q <- strwrap(sprintf(paste("SELECT project_name, %s(value) as Total
                             FROM run, likwid 
                             WHERE run.id = likwid.run_id 
                             AND experiment_group = '%s'::uuid
                             AND experiment_name = 'polyjit' 
                             AND metric = '%s'
                             AND region = 'polyjit.main'
                             GROUP BY project_name 
                             ORDER BY project_name;"),
                       aggr, exp, metric), width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, q)
  res <- melt(dbFetch(qr))
  dbClearResult(qr)
  return(res)
}

likwid.overhead <- function(c, exp, aggr, metric) {
  q <- strwrap(sprintf(paste("SELECT project_name, %s(value) as Overhead
                             FROM run, likwid 
                             WHERE run.id = likwid.run_id 
                             AND experiment_group = '%s'::uuid
                             AND experiment_name = 'polyjit' 
                             AND metric = '%s'
                             AND (    region = 'polyjit.params.select'
                             OR region = 'polyjit.codegen'
                             OR region = 'polyjit.prototype.get'
                             )
                             GROUP BY project_name 
                             ORDER BY project_name;"),
                       aggr, exp, metric), width=10000, simplify=TRUE)
    qr <- dbSendQuery(c, q)
    res <- melt(dbFetch(qr))
    dbClearResult(qr)
    return(res)
}

likwid.runtime <- function(c, exp, aggr, metric) {
    q <- strwrap(sprintf(paste("SELECT project_name, %s(value) as Runtime
                               FROM run, likwid 
                               WHERE run.id = likwid.run_id 
                               AND experiment_group = '%s'::uuid
                               AND experiment_name = 'polyjit' 
                               AND metric = '%s'
                               AND NOT (    region = 'polyjit.params.select'
                               OR region = 'polyjit.codegen'
                               OR region = 'polyjit.prototype.get'
                               OR region = 'polyjit.main'
                               )
                               GROUP BY project_name 
                               ORDER BY project_name;"),
                         aggr, exp, metric), width=10000, simplify=TRUE)
    qr <- dbSendQuery(c, q)
    res <- melt(dbFetch(qr))
    dbClearResult(qr)
    return(res)
}

runlog <- function(c, exp) {
  q <- strwrap(sprintf(paste("SELECT status as \"Exit Code\", project_name as \"Project\", experiment_name as \"Experiment\", \"begin\" as \"von\", \"end\" as \"bis\", command as \"Command\" FROM run_log
                              WHERE experiment_group = '%s'::uuid;"), exp),
               width=10000, simplify=TRUE)
  qr <- dbSendQuery(c, q)
  res <- dbFetch(qr)
  dbClearResult(qr)
  return(res)
}