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

con <- dbConnect(RPostgres::Postgres(),
                 dbname="pprof",
                 user="pprof",
                 host="debussy.fim.uni-passau.de",
                 port=32768,
                 password="pprof")

source("./polyjit.R")
source("./shiny-data.R")

shinyServer(function(input, output, session) {
  experiments <- reactive({ get_experiments(con) })
  data.speedup <- reactive({
    validate(
      need(input$rawExperiments, "Select a RAW-compatible experiment as baseline first."),
      need(input$jitExperiments, "Select a JIT-compatible experiment first.")
    )
    speedup(con, input$rawExperiments, input$jitExperiments, input$projects, input$groups)
  })
  
  data.projects <- reactive({
    validate(
      need(input$rawExperiments, "Select a RAW-compatible experiment as baseline first."),
      need(input$jitExperiments, "Select a JIT-compatible experiment first.")
    )
    data.speedup()[, "project_name"]
  })

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
       session, "jitExperiments",
       choices = getSelections("polyjit", exps))
     updateSelectInput(
       session, "projects",
       choices = projects(con)
     )
     updateSelectInput(
       session, "groups",
       choices = groups(con)
     )
   })
  
  output$speedupT <- DT::renderDataTable({ data.speedup() }, style = 'bootstrap', class = 'table-condensed')
  output$speedup <- renderPlot({
    d <- data.speedup()
    
    if (nrow(d) > 0) {
      ggplot(data=data.speedup(),
             aes(x = cores, y = speedup_corrected, fill = cores, color = cores)) +
        geom_point(aes(color = cores)) +
        geom_line() +
        #geom_bar(stat="identity", position = "dodge") +
        #scale_y_continuous(limits = c(-20,20), breaks = c(-20,-15,-10,-5,-4,-3,-2,-1,0,1,2,3,4,5,10,15,20)) +
        facet_grid(project_name ~ .)
    }
  })
#   
#   observe({
#     csComponents <- compilestats.components(con)
#     updateSelectInput(session, "csComponent", choices = csComponents)
#   })
#   
#   observe({
#     metrics <- likwid.metrics()
#     updateSelectInput(session, "polyjitMetrics", choices = metrics)
#   })
#   
#   observe({
#     updateSelectInput(session, "csName", choices = data.compilestats.names())
#   })
#   
  
#   data.time <- reactive({
#     validate(
#       need(input$rawExperiments, "Select a raw experiment first")
#     )
#     exps <- experiments()
#     exp.name <- exps[exps$experiment_group == input$rawExperiments, "experiment_name"]
#     timingPlotData(input$rawExperiments, exp.name, con)
#   })
#   output$timingTable <- DT::renderDataTable({ data.time() })
#   output$timing <- renderPlot({ timingPlot(input$rawExperiments, experiments(), con) })
#   
#   data.papi <- reactive({
#     validate(
#       need(input$papiExperiments, 'Select a papi experiment first')
#     )
#     papiPlotData(input$papiExperiments, con)
#   })
#   output$papiTable <- DT::renderDataTable({ data.papi()  })
#   output$papi <- renderPlot({ papiPlot(input$papiExperiments, experiments(), con) })
#   output$papiBoxplot <- renderPlot({ papiBoxplot(input$papiExperiments, experiments(), con) })
#   
#   data.papi.std <- reactive({
#     validate(
#       need(input$papiStdExperiments, 'Select a papi (std) experiment first')
#     )
#     papiPlotData(input$papiStdExperiments, con)
#   })
#   output$papiStd <- renderPlot({ papiPlot(input$papiStdExperiments, experiments(), con) })
#   output$papiStdBoxplot <- renderPlot({ papiBoxplot(input$papiStdExperiments, experiments(), con) })
#   
#   data.polyjit <- reactive({
#     validate(
#       need(input$polyjitExperiments, 'Select a polyjit experiment first'),
#       need(input$polyjitMetrics, 'Select a metric first'),
#       need(input$polyjitAggregation, 'Select an aggregation function first')
#     )
#     polyjitData(input$polyjitExperiments,
#                 input$polyjitMetrics,
#                 input$polyjitAggregation,
#                 experiments(), con)
#   })
#   output$polyjit <- renderPlot({
#     polyjitPlot(
#       input$polyjitExperiments,
#       input$polyjitMetrics,
#       input$polyjitAggregation,
#       experiments(), con)
#   })
#   output$polyjitTable <- DT::renderDataTable({ data.polyjit() },
#                                              style = 'bootstrap',
#                                              class = 'table-condensed',
#                                              options = list(
#                                                pageLength = 50
#                                              )
#   )
#   
#   data.log <- reactive({
#     validate(
#       need(input$logExperiments, 'Select an experiment first')
#     )
#     runlog(con, input$logExperiments)
#   })
#   output$log <- DT::renderDataTable({ data.log() },
#                                     style = 'bootstrap', class = 'table-condensed', options = log.tableOptions
#   )
#   
#   data.compilestats.names <- reactive({
#     validate(
#       need(input$csComponent, "Select a Compilestats component first")
#     )
#     compilestats.names(con, input$csComponent)
#   })
#   
#   data.compilestats <- reactive({
#     validate(
#       need(input$csExperiments, "Select a CompileStats experiment"),
#       need(input$csName, "Select a name"),
#       need(input$csComponent, "Select a component")
#     )
#     compilestatsData(input$csExperiments, input$csName, input$csComponent, con)
#   })
#   output$csTable <-   DT::renderDataTable({ data.compilestats() },
#                                           style = 'bootstrap',
#                                           class = 'table-condensed'
#   )
})
