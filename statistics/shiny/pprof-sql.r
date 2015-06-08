library(RPostgreSQL)
library(ggplot2)
library(reshape)
library(scales)
library(plyr)
library(Cairo)
if(!require("scales")) {
  install.packages("scales", dependencies = TRUE)
  library(scales)
}

if(!require("gplots")) {
  install.packages("gplots", dependencies = TRUE)
  library(gplots)
}

plot_dyncov <- function(experiment, connection) {
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
    summarized <- subset(summarized, value <= 100)

    ggplot(data = summarized, aes(x = project_name, y = value)) +
      geom_point(stat = "identity", aes(color=project_name)) +
      coord_flip() +
      ggtitle(paste("Dynamic SCoP coverage for experiment run ", experiment)) +
      theme(legend.position = "none",
            axis.title.x = element_blank(),
            axis.title.y = element_blank())
  }
}

plot_experiment <- function(experiment, connection) {
  jit_query <- strwrap(sprintf(paste(
    "SELECT
      project_name,
      region,
      metric,
      SUM(value)
    FROM run, likwid
    WHERE
      run.id = likwid.run_id AND
      metric = 'RDTSC Runtime [s]' AND
      ( region = 'CodgeGenJIT' OR
        region = 'GetOrParsePrototype' OR
        region = 'JitSelectParams' ) AND
      NOT region = 'main' AND experiment_group = '%s'
    GROUP BY command, project_name, region, metric;"), experiment), width=10000, simplify=TRUE)
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
  jit_data <- melt(dbGetQuery(connection, jit_query))

  if (nrow(rt_data) > 0 && nrow(main_data) > 0) {
    rt_data[,3] <- "Runtime Breakdown"
    main_data[,3] <- "Total Runtime"
    jit_data[,3] <- "Time in JIT"
    all <- rbind(rt_data, main_data)
    all <- rbind(all, jit_data)
    plot <- ggplot(data=all) +
      aes(x = metric, y = value, fill=region) +
      scale_y_continuous(name="Time [s]") +
      geom_bar(stat = "identity") +
      facet_wrap(~ project_name, scales = "free_y", ncol = 8) +
      ggtitle(paste("Experiment ID ", experiment)) +
      theme(legend.position="none", axis.ticks = element_blank(), axis.text.x = element_text(angle = 90, hjust = 1))
    plot
   }
}

plot_heatmap_run <- function(run_id, connection) {
  cat(sprintf("Working on run: %d\n", run_id))
  buckets <- 50
  heatmap_query <- strwrap(sprintf(paste(
    "SELECT
      ev.name,
      trunc(ev.start /
        (SELECT
          sum(ev.duration) / %d AS size
         FROM pprof_events ev
         WHERE ev.name='START' AND ev.run_id = %s
         GROUP BY ev.run_id
        )
      ) as bucket,
      sum(ev.duration) as duration
    FROM pprof_events AS ev WHERE ev.run_id = %s
    AND ev.type != 6 AND ev.name != 'START' GROUP BY ev.name, bucket;"), buckets, run_id, run_id), width=10000, simplify=TRUE)
  heatmap_data <- dbGetQuery(connection, heatmap_query)

  if (nrow(heatmap_data) < 10) {
    cat("Not enough data to plot.\n")
    return(NULL)
  }

  heatmap.m <- melt(heatmap_data, id = 1:2)
  heatmap.dd <- ddply(heatmap.m, .(variable), transform, rescale = scale(value))
  outfile <- sprintf("heatmap-%s-", run_id)
  cat(sprintf("Output to: %s\n", outfile))
  ggplot(heatmap.dd, aes(x = bucket, y = name)) +
    labs(x = "", y = "") + scale_x_discrete(expand = c(0,0)) + scale_y_discrete(expand = c(0,0)) +
    theme(legend.position = "none",
         axis.ticks = element_blank()) +
    geom_tile(aes(fill = rescale), colour = "white") +
    scale_fill_gradient(low = "white", high = "steelblue")
}

plot_heatmap <- function(experiment, connection) {
  run_query <- sprintf(paste("SELECT DISTINCT id FROM run WHERE experiment_group = '%s';"), experiment)
  runs <- dbGetQuery(connection, run_query)

  lapply(X = runs[,1], FUN = plot_heatmap_run, connection = con)
}

get_experiments <- function(connection) {
  rs <- dbGetQuery(connection, "SELECT DISTINCT experiment_group FROM run WHERE NOT experiment_group = '00000000-0000-0000-0000-000000000000'")
  return(c(rs[,1]))
}

get_experiment_table <- function(connection) {
  rs <- dbGetQuery(connection, "SELECT DISTINCT CONCAT(experiment_name, ' (', experiment_group, ')') FROM run WHERE NOT experiment_group = '00000000-0000-0000-0000-000000000000'")
  return(rs)
}