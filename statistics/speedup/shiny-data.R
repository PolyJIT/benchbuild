library(RPostgres)

options(repr.plot.family = 'mono', repr.plot.width = 8, repr.plot.height = 6, warn = -1)
mytheme <- theme(plot.title = element_text(family="Fantasque Mono", size = 10))

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

timingPlot <- function(id, exps, con) {
  exp.id <- id
  exp.name <- exps[exps$experiment_group == exp.id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == exp.id, "completed"]

  d <- timingPlotData(exp.id, exp.name, con)
  p <- ggplot(data = d, aes(x = project_name))
  p <- p + theme(axis.ticks.x = element_blank(),
                 axis.title.x = element_blank(),
                 axis.text.x  = element_blank(),
                 axis.title.y = element_blank(),
                 legend.position = "none",
                 plot.title = element_text(size = 10))
  p <- p + mytheme
  p <- p + ggtitle(sprintf("Runtime breakdown '%s' @ '%s'\n(%s)", exp.name, exp.date, exp.id))
  if (is.element("raw.time.real_s", names(d))) {
    p <- p + geom_point(aes(y = raw.time.real_s), size = 1.5, colour = "red")
  }
  if (is.element("raw.time.user_s", names(d))) {
    p <- p + geom_point(aes(y = raw.time.user_s), size = 1.5, colour = "blue")
  }

  if (is.element("papi.time.real_s", names(d))) {
    p <- p + geom_point(aes(y = papi.time.real_s), size = 1.5, colour = "red")
  }
  if (is.element("papi.time.user_s", names(d))) {
    p <- p + geom_point(aes(y = papi.time.user_s), size = 1.5, colour = "blue")
  }

  if (is.element("time.real_s", names(d))) {
    p <- p + geom_point(aes(y = time.real_s), size = 1.5, colour = "red")
  }
  if (is.element("time.user_s", names(d))) {
    p <- p + geom_point(aes(y = time.user_s), size = 1.5, colour = "blue")
  }
  return(p)
}

papiPlot <- function(id, exps, con) {
  exp.id <- id
  exp.name <- exps[exps$experiment_group == exp.id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == exp.id, "completed"]

  d <- papiPlotData(exp.id, con)
  p <- ggplot(data = d, aes(x = project_name))
  p <- p + theme(axis.ticks.x = element_blank(),
                 axis.text.x = element_blank(),
                 legend.position = "right",
                 plot.title = element_text(size = 10))
  p <- p + mytheme
  p <- p + ggtitle(sprintf(" Dynamic SCoP coverage ordered by domain '%s'\n'%s' (%s)", exp.name, exp.date, exp.id))
  p <- p + labs(y = "Dynamic SCoP coverage [%]", x = "Project")
  p <- p + geom_point(aes(y = value, color = domain), size = 1.5)
  return(p)
}

papiBoxplot <- function(id, exps, con) {
  exp.id <- id
  exp.name <- exps[exps$experiment_group == exp.id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == exp.id, "completed"]

  d <- papiPlotData(exp.id, con)
  cov0 <- d[d$value > 1,]

  p <- qplot(data = cov0, x = domain, y = value)
  p <- p + ggtitle(sprintf(" Runtime breakdown '%s' @ '%s' (%s)", exp.name, exp.date, exp.id))
  p <- p + theme(plot.title = element_text(size = 10))
  p <- p + mytheme
  p <- p + geom_boxplot(outlier.size = 1, fill = "white")
  return(p)
}

polyjitData <- function(id, metric, aggregation, exps, con) {
  cat("polyjit.data\n")
  exp.name <- exps[exps$experiment_group == id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == id, "completed"]

  #lw.total <- likwid.total(con, id, aggregation, metric)
  lw.runtime <- likwid.runtime(con, id, aggregation, metric)
  lw.overhead <- likwid.overhead(con, id, aggregation, metric)

  lw <- rbind(lw.overhead, lw.runtime)
  #lw <- rbind(lw, lw.total)
  return(lw)
}

polyjitPlot <- function(id, metric, aggregation, exps, con) {
  exp.name <- exps[exps$experiment_group == id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == id, "completed"]

#  lw.total <- likwid.total(con, id, aggregation, metric)
  lw.runtime <- likwid.runtime(con, id, aggregation, metric)
  lw.overhead <- likwid.overhead(con, id, aggregation, metric)

  cat("polyjit.plot (fetch)\n")
  lw <- rbind(lw.runtime, lw.overhead)
  cat("polyjit.plot (rbind): ", nrow(lw))
#  lw <- rbind(lw, lw.total)

  options(repr.plot.family = 'mono', repr.plot.width = 10, repr.plot.height = 64, warn = -1)
  p <- ggplot(data=lw, aes(x=num_cores, y=value, fill=variable))
  p <- p + geom_bar(position="dodge", stat="identity")
  p <- p + facet_wrap( ~ project, scales = "free", ncol = 3)
  p <- p + ggtitle(label = "Runtime vs. Overhead per run group")
  p <- p + theme(plot.title = element_text(size = 8))

  return(p)
}

compilestatsData <- function(id, name, component, con) {
  return(compilestats(con, id, name, component))
}

