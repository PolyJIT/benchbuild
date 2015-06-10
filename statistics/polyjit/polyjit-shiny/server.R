
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)
library(reshape)
library(ggplot2)
library(RPostgres)
library(polyjit)

options(repr.plot.family = 'mono', repr.plot.width = 8, repr.plot.height = 6, warn = -1)
mytheme <- theme(plot.title = element_text(family="Fantasque Mono", size = 10))

ex

getSelections <- function(name, exps) {
  exps.filtered <- exps[exps$experiment_name == name, ]
  newNames <- paste0(exps.filtered[,"experiment_name"],
                     rep(" @ ", nrow(exps.filtered)),
                     exps.filtered[,"completed"])
  groups <- exps.filtered[, "experiment_group"]
  names(groups) <- newNames
  return(groups)
}

papiPlot <- function(id, exps) {
  exp.id <- id
  exp.name <- exps[exps$experiment_group == exp.id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == exp.id, "completed"]
  
  cov.dom <- get_papi_dyncov(exp.id, con, "project.domain")
  cov.value <- get_papi_dyncov(exp.id, con, "metrics.value")
  
  cov.dom <- subset(cov.dom, value > 0)
  p <- ggplot(data = cov.dom, aes(x = project_name))
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
  
  cov.dom <- get_papi_dyncov(exp.id, con, "project.domain")
  cov0 <- cov.dom[cov.dom$value > 1,]
  
  p <- qplot(data = cov0, x = domain, y = value)
  p <- p + ggtitle(sprintf(" Runtime breakdown '%s' @ '%s' (%s)", exp.name, exp.date, exp.id))
  p <- p + theme(plot.title = element_text(size = 10))
  p <- p + mytheme
  p <- p + geom_boxplot(outlier.size = 1, fill = "white")
  return(p)
}

polyjitPlot <- function(id, metric, exps) {
  exp.name <- exps[exps$experiment_group == id, "experiment_name"]
  exp.date <- exps[exps$experiment_group == id, "completed"]
  
  lw.total <- likwid.total(con, id, metric)
  lw.runtime <- likwid.runtime(con, id, metric)
  lw.overhead <- likwid.overhead(con, id, metric)
  
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

shinyServer(function(input, output, clientData, session) {
  experiments <- reactive({
    get_experiments(con)
  })
  
  likwid.metrics <- reactive({
    likwid.get_metrics(con)
  })

  observe({
    exps <- experiments()
    
    raw <- getSelections("raw", exps)
    polly <- getSelections("polly",  exps)

    updateSelectInput(session, "rawExperiments", choices = getSelections("raw", exps))
    updateSelectInput(session, "papiExperiments", choices = getSelections("papi", exps))
    updateSelectInput(session, "papiStdExperiments", choices = getSelections("papi-std", exps))
    updateSelectInput(session, "polyjitExperiments", choices = getSelections("polyjit", exps))
  })
  
  observe({
    metrics <- likwid.metrics()
    
    updateSelectInput(session, "polyjitMetrics", choices = metrics)
  })
  
  output$raw <- renderPlot({
    exps <- experiments()
    exp.id <- input$rawExperiments
    exp.name <- exps[exps$experiment_group == exp.id, "experiment_name"]
    exp.date <- exps[exps$experiment_group == exp.id, "completed"]
    
    d <- get_raw_runtime(exp.id, con)
    d.cast <- subset(d, value < 100)
    d.cast <- cast(data = d.cast, project_name ~ name, fun.aggregate = sum) 
    
    p <- ggplot(data = d.cast, aes(x = project_name))
    p <- p + theme(axis.ticks.x = element_blank(),
                   axis.title.x = element_blank(),
                   axis.text.x  = element_blank(),
                   axis.title.y = element_blank(),
                   legend.position = "none",
                   plot.title = element_text(size = 10))
    p <- p + mytheme
    p <- p + ggtitle(sprintf(" Runtime breakdown '%s' @ '%s'\n(%s)", exp.name, exp.date, exp.id))
    p <- p + geom_point(aes(y = raw.time.real_s), size = 1.5, colour = "blue")
    p <- p + geom_point(aes(y = raw.time.user_s), size = 1.5, colour = "red")
    p
  })
  
  output$papi <- renderPlot({
    exps <- experiments()
    papiPlot(input$papiExperiments, exps)
  })
  
  output$papiBoxplot <- renderPlot({
    exps <- experiments()
    papiBoxplot(input$papiExperiments, exps)
  })
  
  output$papiStd <- renderPlot({
    exps <- experiments()
    papiPlot(input$papiStdExperiments, exps)
  })
  
  output$papiStdBoxplot <- renderPlot({
    exps <- experiments()
    papiBoxplot(input$papiStdExperiments, exps)
  })
  
  output$polyjit <- renderPlot({
    exps <- experiments()
    polyjitPlot(input$polyjitExperiments, input$polyjitMetrics, exps)
  })
})
