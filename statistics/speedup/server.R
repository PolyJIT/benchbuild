source("./polyjit.R")

if (!require("ggplot2")) {
  install.packages("ggplot2")
  library(ggplot2)
}
if (!require("reshape2")) {
  install.packages("reshape2")
  library("reshape2")
}
if (!require("scales")) {
  install.packages("scales")
  library(scales)
}
if (!require("DBI")) {
  devtools::install_github("rstats-db/DBI")
  library(DBI)
}
if (!require("RPostgres")) {
  devtools::install_github("rstats-db/RPostgres")
  library(RPostgres)
}
if (!require("shiny")) {
  install.packages("shiny")
  library(shiny)
}
if (!require("DT")) {
  devtools::install_github("rstudio/DT")
  library(DT)
}
if (!require("sm")) {
  install.packages('sm')
  library(sm)
}
if (!require("vioplot")) {
  install.packages('vioplot')
  library(vioplot)
}

shinyServer(function(input, output, session) {
  con <- dbConnect(RPostgres::Postgres(),
                   dbname="pprof", user="pprof", host="debussy.fim.uni-passau.de", port=32768, password="pprof")
  exps <- get_experiments(con)

  data.projects <- reactive({
    validate(
      need(input$rawExperiments, "Select a RAW-compatible experiment as baseline first."),
      need(input$jitExperiments, "Select a JIT-compatible experiment first.")
    )
    return(data.speedup()[, "project_name"])
  })


  output$speedup.ui = renderUI({
    plotOutput("speedup", width = "100%", height = input$plotSize)
  })
  output$speedup = renderPlot({
    validate(
      need(input$rawExperiments, "Select a RAW-compatible experiment as baseline first."),
      need(input$jitExperiments, "Select a JIT-compatible experiment first."),
      need(input$minY, "Select a minimum for y-axis."),
      need(input$minY, "Select a maximum for y-axis.")
    )
    d <- speedup(con,
                 input$rawExperiments,
                 input$jitExperiments,
                 input$projects,
                 input$groups)

    if (nrow(d) > 0) {
      p <- ggplot(data=d, aes(x = cores, y = speedup_corrected, fill = cores, color = cores))

      if (input$plotTime) {
        p <- p + geom_line(aes(y = time), color = "red") +
                 geom_line(aes(y = ptime), color = "green") +
                 ylab("Runtime in [s]")
      } else {
        p <- p + geom_line() +
                 geom_point(aes(color = cores)) +
                 geom_bar(aes(color = cores), stat = "identity") +
                 geom_smooth(color = "red") +
                 geom_hline(yintercept=1, colour="blue") +
                 geom_abline(slope=1, intercept=0, colour="green") +
                 coord_cartesian(ylim=c(input$minY, input$maxY)) +
                 scale_x_discrete() +
                 ylab("Speedup Factor")
      }

      p <- p + facet_wrap(~ project_name, ncol = input$numCols) + xlab("Number of cores")
      p
    }
  })

  output$speedupTable = renderDataTable({
      validate(
        need(input$rawExperiments, "Select a RAW-compatible experiment as baseline first."),
        need(input$jitExperiments, "Select a JIT-compatible experiment first.")
      )
      return(speedup(con,
                     input$rawExperiments,
                     input$jitExperiments,
                     input$projects,
                     input$groups))
    },
    options = list(
      style = 'bootstrap',
      class = 'table-condensed'
    )
  )

  output$flamegraph = renderText({
    validate(
      need(input$perfExperiments, "Select a PERF-compatible experiment first."),
      need(input$perfProjects, "Select a Project first.")
    )

    return(flamegraph(con, input$perfExperiments, input$perfProjects))
  })

  updateSelectInput(session, "rawExperiments", choices = c(getSelections("raw", exps),
                                               getSelections("polly", exps),
                                               getSelections("polly-openmp", exps),
                                               getSelections("polly-vectorize", exps),
                                               getSelections("polly-openmpvect", exps),
                                               getSelections("papi", exps),
                                               getSelections("papi-std", exps),
                                               getSelections("pj-papi", exps),
                                               getSelections("polyjit", exps),
                                               getSelections("pj-raw", exps)), selected = 0)
  updateSelectInput(session, "jitExperiments", choices = c(getSelections("polyjit", exps),
                                                           getSelections("pj-raw", exps)), selected = 0)
  updateSelectInput(session, "projects", choices = projects(con), selected = 0)
  updateSelectInput(session, "groups", choices = groups(con), selected = 0)
  updateSelectInput(session, "perfExperiments", choices = c(getSelections("pj-perf", exps)), selected = 0)
  updateSelectInput(session, "perfProjects", choices = perfProjects(con), selected = 0)
  updateSelectInput(session, "papiExperiments", choices = c(getSelections("pj-papi", exps),
                                                            getSelections("papi", exps)), selected = 0)

  observe({
    if (!is.null(input$perfExperiments)) {
      updateSelectInput(session, "perfProjects", choices = perfProjects(con, input$perfExperiments), selected = 0)
    }
  })

  session$onSessionEnded(function() {
    dbDisconnect(con)
  })
})
