library(shiny)
library(reshape)
library(ggplot2)
library(RPostgres)
library(polyjit)

source("./shiny-data.R")

con <- dbConnect(RPostgres::Postgres(),
                 dbname="pprof",
                 user="pprof",
                 host="debussy.fim.uni-passau.de",
                 port=32769,
                 password="pprof")

options(repr.plot.family = 'mono', repr.plot.width = 8, repr.plot.height = 6, warn = -1)
mytheme <- theme(plot.title = element_text(family="Fantasque Mono", size = 10))

getSelections <- function(name, exps) {
  exps.filtered <- exps[exps$experiment_name == name, ]
  newNames <- paste0(exps.filtered[,"experiment_name"],
                     rep(" @ ", nrow(exps.filtered)),
                     exps.filtered[,"completed"])
  groups <- exps.filtered[, "experiment_group"]
  names(groups) <- newNames
  return(groups)
}

timingPlot <- function(id, exps) {
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

papiPlot <- function(id, exps) {
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

papiBoxplot <- function(id, exps) {
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

polyjitPlot <- function(id, metric, aggregation, exps) {
  exp.name <- exps[exps$experiment_group == id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == id, "completed"]

  lw.total <- likwid.total(con, id, aggregation, metric)
  lw.runtime <- likwid.runtime(con, id, aggregation, metric)
  lw.overhead <- likwid.overhead(con, id, aggregation, metric)

  lw <- rbind(lw.runtime, lw.overhead)

  p <- ggplot(data = lw, aes(x = project_name, y = value, fill = variable))
  p <- p + ggtitle(sprintf("Overhead vs. Runtime of jitte'd functions '%s' @ '%s'\nMetric '%s' (%s)",
                           exp.name, exp.date, metric, id))
  p <- p + labs(y = metric, x = "Project")
  p <- p + geom_bar(position = "dodge", stat= "identity")
  p <- p + theme(axis.text.x = element_text(angle = 90, hjust = 1), plot.title = element_text(size = 8))
  p <- p + mytheme
  return(p)
}

shinyServer(function(input, output, session) {
  experiments <- reactive({ get_experiments(con) })
  likwid.metrics <- reactive({ likwid.get_metrics(con) })

  observe({
    exps <- experiments()
    updateSelectInput(session, "rawExperiments",
                      choices = c(getSelections("raw", exps),
                                  getSelections("polly", exps),
                                  getSelections("polly-openmp", exps),
                                  getSelections("polly-vectorize", exps),
                                  getSelections("polly-openmpvect", exps),
                                  getSelections("papi", exps),
                                  getSelections("papi-std", exps)))
    updateSelectInput(session, "papiExperiments",
                      choices = c(getSelections("papi", exps),
                                  getSelections("papi-std", exps)))
    updateSelectInput(session, "papiStdExperiments",
                      choices = getSelections("papi-std", exps))
    updateSelectInput(session, "polyjitExperiments",
                      choices = getSelections("polyjit", exps))
  })

  observe({
    metrics <- likwid.metrics()
    updateSelectInput(session, "polyjitMetrics", choices = metrics)
  })

  output$timingTable <- renderDataTable({
    exps <- experiments()
    exp.name <- exps[exps$experiment_group == input$rawExperiments, "experiment_name"]
    timingPlotData(input$rawExperiments, exp.name, con)
  })

  output$timing <- renderPlot({ timingPlot(input$rawExperiments, experiments()) })

  output$papi <- renderPlot({ papiPlot(input$papiExperiments, experiments()) })
  output$papiTable <- renderDataTable({ papiPlotData(input$papiExperiments, con) })
  output$papiBoxplot <- renderPlot({ papiBoxplot(input$papiExperiments, experiments()) })
  output$papiStd <- renderPlot({ papiPlot(input$papiStdExperiments, experiments()) })
  output$papiStdBoxplot <- renderPlot({ papiBoxplot(input$papiStdExperiments, experiments()) })
  output$polyjit <- renderPlot({ polyjitPlot(input$polyjitExperiments,
                                             input$polyjitMetrics,
                                             input$polyjitAggregation,
                                             experiments())
  })
})
