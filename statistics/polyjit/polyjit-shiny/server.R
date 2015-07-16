library(shiny)
library(reshape)
library(ggplot2)
if (!require("RPostgres")) install.packages("RPostgres")
library(RPostgres)
if (!require("DT")) install.packages('DT')


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

  output$timing <- renderPlot({ timingPlot(input$rawExperiments, experiments(), con) })

  output$papi <- renderPlot({ papiPlot(input$papiExperiments, experiments(), con) })
  output$papiTable <- DT::renderDataTable({ papiPlotData(input$papiExperiments, con) })
  output$papiBoxplot <- renderPlot({ papiBoxplot(input$papiExperiments, experiments(), con) })
  output$papiStd <- renderPlot({ papiPlot(input$papiStdExperiments, experiments(), con) })
  output$papiStdBoxplot <- renderPlot({ papiBoxplot(input$papiStdExperiments, experiments(), con) })
  output$polyjit <- renderPlot({ polyjitPlot(input$polyjitExperiments,
                                             input$polyjitMetrics,
                                             input$polyjitAggregation,
                                             experiments(), con)
  output$polyjitTable <- DT::renderDataTable({ polyjitData(input$polyjitExperiments,
                                                           input$polyjitMetrics,
                                                           input$polyjitAggregation,
                                                           experiments(), con) },
                                             style = 'bootstrap',
                                             class = 'table-condensed'
                                             )

  # Log table.
  output$polyjitLog <- DT::renderDataTable({ runlog(con, input$polyjitExperiments) },
                                           style = 'bootstrap',
                                           class = 'table-condensed',
                                           options = list(
                                             pageLength = 50,
                                             rownames = FALSE,
                                             columnDefs = list(
                                               list(targets = 1, render = JS(
                                                 "function(data, type, row, meta) {",
                                                 "  if (type === 'display') {",
                                                 "    if (data === '0') {",
                                                 "      return '<span class=\"label label-success\" title=\"' + data + '\">OK</span>';",
                                                 "    }",
                                                 "    return '<span class=\"label label-danger\" title=\"' + data + '\">Failed</span>';",
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
                                          )
  })
})
