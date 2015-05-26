library(RPostgreSQL)
library(ggplot2)
library(reshape)
library(scales)
library(plyr)

plot_dyncov <- function(experiment, connection) {
  cat(experiment)
  dyncov_query <- sprintf(paste("SELECT run.project_name, metrics.name, metrics.value",
                                "FROM public.run, public.metrics ",
                                "WHERE run.id = metrics.run_id ",
                                "AND experiment_group ='%s' ",
                                "AND metrics.name = 'pprof.dyncov'",
                                "AND project_name != '%s' ",
                                "AND project_name != '%s' ",
                                "AND project_name != '%s' ",
                                "AND project_name != '%s' ",
                                ";"),
                          experiment,
                          "MultiSourceApplications",
                          "SingleSourceApplications",
                          "SingleSourceBenchmarks",
                          "unknown")

  dyncov_data <- melt(dbGetQuery(connection, dyncov_query))
  if (nrow(dyncov_data) > 0) {
    # Summarize data using median(!) over all runs, check if that makes any sense.
    summarized <- ddply(dyncov_data, .(project_name, name), summarise, value=median(value))
    summarized <- subset(summarized, value > 0)

    plot <- ggplot(data = summarized, aes(x = project_name, y = value)) +
      geom_point(stat = "identity", aes(color=project_name)) +
      coord_flip() +
      ggtitle(paste("Dynamic SCoP coverage for experiment run ", experiment)) +
      theme(legend.position = "none",
            axis.title.x = element_blank(),
            axis.title.y = element_blank())
    plot
  }
}

plot_experiment <- function(experiment, connection) {
  cat(experiment)
  rt_query <- sprintf(paste("SELECT project_name, region, metric, SUM(value) ",
                            "FROM public.run, public.likwid ",
                            "WHERE run.id = likwid.run_id ",
                            "AND metric = 'RDTSC Runtime [s]'",
                            "AND NOT region = 'main' ",
                            "AND experiment_group='%s' ",
                            "GROUP BY project_name, region, metric;"), experiment)
  main_query<- sprintf(paste("SELECT project_name, region, metric, SUM(value) ",
                            "FROM public.run, public.likwid ",
                            "WHERE run.id = likwid.run_id ",
                            "AND metric = 'RDTSC Runtime [s]'",
                            "AND region = 'main' ",
                            "AND experiment_group='%s' ",
                            "GROUP BY project_name, region, metric;"), experiment)

  rt_data <- melt(dbGetQuery(connection, rt_query))
  main_data <- melt(dbGetQuery(connection, main_query))


  if (nrow(rt_data) > 0 && nrow(main_data) > 0) {
    rt_data[,3] <- "Runtime Breakdown"
    main_data[,3] <- "Total Runtime"
    all <- rbind(rt_data, main_data)
    plot <- ggplot() +
      #all, aes(x = metric, y = value, fill=region)) +
      scale_y_continuous(name="Time [s]") +
      geom_bar(stat = "identity") +
      geom_abline(data=main_data, mapping=aes(x = project_name, y=value)) +
      geom_abline(data=rt_data, mapping=aes(x = project_name, y=value)) +
      #facet_wrap(~ project_name, scales = "free_y", ncol = 8) +
      ggtitle(paste("Experiment ID ", experiment)) +
      theme(axis.text.x = element_text(angle = 90, hjust = 1))
    plot
   }
}

get_experiments <- function(connection) {
  rs <- dbGetQuery(connection, "SELECT DISTINCT experiment_group FROM run WHERE NOT experiment_group = '00000000-0000-0000-0000-000000000000'")
  return <- c(rs[,1])
}

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="pprof", user="pprof", host="localhost", port=32768, password="pprof")

exps = get_experiments(connection = con)
lapply(X = exps, FUN = plot_dyncov, connection = con)
lapply(X = exps, FUN = plot_experiment, connection = con)

dbDisconnect(con)
dbUnloadDriver(drv)
