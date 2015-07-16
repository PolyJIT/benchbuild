library(polyjit)
library(RPostgres)

timingPlotData <- function(id, name, con) {
  d <- get_raw_runtime(name, id, con)
  d.cast <- subset(d, value < 100)
  d.cast <- cast(data = d.cast, project_name ~ name, fun.aggregate = sum)
  
  return(d.cast)
}

papiPlotData <- function(id, con) {
  cov.dom <- get_papi_dyncov(id, con, "project.domain")
  cov.dom <- subset(cov.dom, value > 0)
  return(cov.dom)
}
polyjitData <- function(id, metric, aggregation, exps, con) {
  exp.name <- exps[exps$experiment_group == id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == id, "completed"]

  lw.total <- likwid.total(con, id, aggregation, metric)
  #lw.runtime <- likwid.runtime(con, id, aggregation, metric)
  lw.overhead <- likwid.overhead(con, id, aggregation, metric)

  lw <- lw.overhead
  return(lw)
}
