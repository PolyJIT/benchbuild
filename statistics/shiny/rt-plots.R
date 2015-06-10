library(RPostgreSQL)
library(ggplot2)
library(reshape)
library(scales)
library(plyr)

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="pprof", user="pprof", host="debussy.fim.uni-passau.de", port=32769, password="pprof")

get_raw_runtime <- function(experiment, connection) {
  query <- strwrap(sprintf(paste(
    "SELECT project_name, name, SUM(value) as sumval
     FROM run, metrics WHERE run.id = metrics.run_id
     AND experiment_name = 'raw'
     AND experiment_group = '%s'
     GROUP BY run_group, project_name, name, value
     ORDER BY sumval DESC;
    "), experiment), width=10000, simplify=TRUE)
  query_res <- melt(dbGetQuery(connection, query))
  if (nrow(query_res) > 0) {
    query_res$project_name <- factor(query_res$project_name, levels = query_res$project_name)
  }
  return(query_res)
}

plot_runtime <- function(rt_data, experiment) {
  if (nrow(rt_data) > 0) {
    p <- ggplot(data = rt_data, aes(x=project_name, y=value))
    p <- p + ggtitle(paste("Raw run time in [s] for: ", experiment))
    p <- p + theme(axis.ticks.x = element_blank(),
                   axis.title.x = element_blank(),
                   axis.text.x  = element_blank(),
                   axis.title.y = element_blank(),
                   legend.position = "none")
    p <- p + geom_point()
    return(p)
  }
}

get_experiments <- function(connection) {
  rs <- dbGetQuery(connection, "SELECT DISTINCT experiment_group FROM run WHERE NOT experiment_group = '00000000-0000-0000-0000-000000000000'")
  return(c(rs[,1]))
}

# exps = get_experiments(connection = con)
# for (exp in exps) {
#   d = get_raw_runtime(exp, connection = con)
#   d <- d[d$value< 100,]
#   p = plot_runtime(d, exp)
#   print(p)
# }

# dbDisconnect(con)
# dbUnloadDriver(drv)