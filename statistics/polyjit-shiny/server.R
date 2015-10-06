if (!require("shiny")) install.packages("shiny")
library(shiny)
if (!require("reshape")) install.packages("reshape")
library(reshape)
if (!require("ggplot2")) install.packages("ggplot2")
library(ggplot2)
if (!require("RPostgres")) install.packages("RPostgres")
library(RPostgres)
if (!require("DT")) install.packages('DT')
library(DT)

# options(
#  shiny.error = recover
# )

con <- dbConnect(RPostgres::Postgres(),
                 dbname="pprof",
                 user="pprof",
                 host="debussy.fim.uni-passau.de",
                 port=32768,
                 password="pprof")

source("./polyjit.R")
source("./shiny-data.R")

log.tableOptions <- list(
  pageLength = 50,
  rownames = FALSE,
  columnDefs = list(
    list(targets = 1, render = JS(
      "function(data, type, row, meta) {",
      "  if (type === 'display') {",
      "    if (data == 0) {",
      "      return '<span class=\"label label-success\" title=\"' + data + '\">OK (' + data + ')</span>';",
      "    }",
      "    if (data === null) {",
      "      return '<span class=\"label label-info\" title=\"' + data + '\"> Launched</span>';",
      "    }",
      "    return '<span class=\"label label-danger\" title=\"' + data + '\">Failed ('+ data + ')</span>';",
      "  } else {",
      "    return data;",
      "  }",
      "}")
    ),
    list(targets = 5, render = JS(
      "function(data, type, row, meta) {",
      "return type === 'display' && data.length > 80 ?",
      "'<span title=\"' + data + '\">' + data.substr(0, 80) + '...</span>' : data;",
      "}")
    )
  ))

shinyServer(function(input, output, session) {
  experiments <- reactive({ get_experiments(con) })
  likwid.metrics <- reactive({ likwid.get_metrics(con) })
  
  observe({
    exps <- experiments()
    updateSelectInput(
      session, "rawExperiments",
      choices = c(getSelections("raw", exps),
                  getSelections("polly", exps),
                  getSelections("polly-openmp", exps),
                  getSelections("polly-vectorize", exps),
                  getSelections("polly-openmpvect", exps),
                  getSelections("papi", exps),
                  getSelections("papi-std", exps)))
    updateSelectInput(
      session, "papiExperiments",
      choices = c(getSelections("papi", exps),
                  getSelections("papi-std", exps)))
    updateSelectInput(
      session, "papiStdExperiments",
      choices = getSelections("papi-std", exps))
    updateSelectInput(
      session, "polyjitExperiments",
      choices = getSelections("polyjit", exps))
    updateSelectInput(
      session, "csExperiments",
      choices = c(getSelections("polyjit", exps),
                  getSelections("compilestats", exps)))
    updateSelectInput(
      session, "logExperiments",
      choices = getSelections(NULL, exps))
  })
  
  observe({
    csComponents <- compilestats.components(con)
    updateSelectInput(session, "csComponent", choices = csComponents)
  })
  
  observe({
    metrics <- likwid.metrics()
    updateSelectInput(session, "polyjitMetrics", choices = metrics)
  })

  observe({
    updateSelectInput(session, "csName", choices = data.compilestats.names())
  })
  
  
  data.time <- reactive({
    validate(
      need(input$rawExperiments, "Select a raw experiment first")
    )
    exps <- experiments()
    exp.name <- exps[exps$experiment_group == input$rawExperiments, "experiment_name"]
    timingPlotData(input$rawExperiments, exp.name, con)
  })
  output$timingTable <- DT::renderDataTable({ data.time() })
  output$timing <- renderPlot({ timingPlot(input$rawExperiments, experiments(), con) })
  
  data.papi <- reactive({
    validate(
      need(input$papiExperiments, 'Select a papi experiment first')
    )
    papiPlotData(input$papiExperiments, con)
  })
  output$papiTable <- DT::renderDataTable({ data.papi()  })
  output$papi <- renderPlot({ papiPlot(input$papiExperiments, experiments(), con) })
  output$papiBoxplot <- renderPlot({ papiBoxplot(input$papiExperiments, experiments(), con) })
  
  data.papi.std <- reactive({
    validate(
      need(input$papiStdExperiments, 'Select a papi (std) experiment first')
    )
    papiPlotData(input$papiStdExperiments, con)
  })
  output$papiStd <- renderPlot({ papiPlot(input$papiStdExperiments, experiments(), con) })
  output$papiStdBoxplot <- renderPlot({ papiBoxplot(input$papiStdExperiments, experiments(), con) })

  data.polyjit <- reactive({
    validate(
      need(input$polyjitExperiments, 'Select a polyjit experiment first'),
      need(input$polyjitMetrics, 'Select a metric first'),
      need(input$polyjitAggregation, 'Select an aggregation function first')
    )
    polyjitData(input$polyjitExperiments,
                input$polyjitMetrics,
                input$polyjitAggregation,
                experiments(), con)
  })
  output$polyjit <- renderPlot({
    polyjitPlot(
      input$polyjitExperiments,
      input$polyjitMetrics,
      input$polyjitAggregation,
      experiments(), con)
  })
  output$polyjitTable <- DT::renderDataTable({ data.polyjit() },
    style = 'bootstrap',
    class = 'table-condensed',
    options = list(
      pageLength = 50
    )
  )
  
  data.log <- reactive({
    validate(
      need(input$logExperiments, 'Select an experiment first')
    )
    runlog(con, input$logExperiments)
  })
  output$log <- DT::renderDataTable({ data.log() },
    style = 'bootstrap', class = 'table-condensed', options = log.tableOptions
  )
  
  data.compilestats.names <- reactive({
    validate(
      need(input$csComponent, "Select a Compilestats component first")
    )
    compilestats.names(con, input$csComponent)
  })
  
  data.compilestats <- reactive({
    validate(
      need(input$csExperiments, "Select a CompileStats experiment"),
      need(input$csName, "Select a name"),
      need(input$csComponent, "Select a component")
    )
    compilestatsData(input$csExperiments, input$csName, input$csComponent, con)
  })
  output$csTable <-   DT::renderDataTable({ data.compilestats() },
    style = 'bootstrap',
    class = 'table-condensed'
  )
})
