library(RPostgreSQL)
library(ggplot2)
library(reshape)
library(scales)
library(plyr)
if(!require("scales")) {
  install.packages("scales", dependencies = TRUE)
  library(scales)
}

if(!require("gplots")) {
  install.packages("gplots", dependencies = TRUE)
  library(gplots)
}

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

plot_heatmap_run <- function(run, connection) {
  heatmap_query <- sprintf(paste("SELECT r.project_name, pr.id, pr.type, pr.timestamp ",
                                 "FROM public.run AS r, public.papi_results AS pr",
                                 "WHERE r.id = pr.run_id ",
                                 "AND r.id = %s ",
                                 "AND type != 6 ",
                                 "ORDER BY run_id, timestamp ;"), run)
  heatmap_data <- dbGetQuery(connection, heatmap_query)

  buckets <- 50
  # Bucket Size depends on total runtime of the whole test.
  bucket_size <- sum(papi[papi$Region == "START",3]) %/% buckets
  papi[,1] <- sapply(papi[,1], function(x) x %/% bucket_size)
  papi <- melt(papi, id=1:2)
  #> head(papi_molten)
  #StartTime Region variable   value
  #1         0  START Duration 2357836
  #2         0      a Duration     752
  #3         0      b Duration     261
  #4         0      a Duration     477
  #5         0      b Duration     160
  #6         0      a Duration     473

  papi <- cast(papi, StartTime + variable ~ Region, sum)
  #> head(cast(papi_molten, StartTime + variable ~ Region, sum))
  #StartTime variable   START     a     b c
  #1         0 Duration 2357836 28750 11078 0
  #2         1 Duration       0 34014 11727 0
  #3         2 Duration       0 36060 12304 0
  #4         3 Duration       0 35677 12855 0
  #5         4 Duration       0 37503 13328 0
  #6         5 Duration       0 38061 13373 0
  papi[1,3] <- 0
  papi_matrix <- t(data.matrix(papi[,4:ncol(papi)]))

  rownames(papi) <- papi[,1]
  my_colors <- colorRampPalette(c("white", "yellow", "red"))(n = 299)
  heatmap.2(papi_matrix,
            notecol="black",
            main=opt$name,
            trace="none",
            col=my_colors,
            scale= c("none"),
            dendrogram="none",
            Colv=FALSE)
}

plot_heatmap <- function(experiment, connection) {
  run_query <- sprintf(paste("SELECT DISTINCT id FROM run WHERE experiment_group = '%s';"), experiment)
  runs <- dbGetQuery(connection, run_query)

  lapply(X = runs[,1], FUN = plot_heatmap_run, connection = con)
}

get_experiments <- function(connection) {
  rs <- dbGetQuery(connection, "SELECT DISTINCT experiment_group FROM run WHERE NOT experiment_group = '00000000-0000-0000-0000-000000000000'")
  return <- c(rs[,1])
}

drv <- dbDriver("PostgreSQL")
con <- dbConnect(drv, dbname="pprof", user="pprof", host="localhost", port=32768, password="pprof")

exps = get_experiments(connection = con)
#lapply(X = exps, FUN = plot_heatmap, connection = con)
lapply(X = exps, FUN = plot_dyncov, connection = con)
lapply(X = exps, FUN = plot_experiment, connection = con)

dbDisconnect(con)
dbUnloadDriver(drv)
