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
  con <- NULL

  db <- reactive({
    if (!is.null(con)) {
      dbDisconnect(conn = con)
    }
    validate(need(input$db, "Select a Database."))
    if (input$db == 'buildbot')
      con <- dbConnect(RPostgres::Postgres(), dbname='pprof-bb', user='bb', password='bb', port=32768, host='debussy.fim.uni-passau.de')
    else if (input$db == 'develop')
      con <- dbConnect(RPostgres::Postgres(), dbname='pprof', user='pprof', password='pprof', port=32768, host='debussy.fim.uni-passau.de')
    cat("DB:", input$db, "\n")
    return(con)
  })

  data.projects <- reactive({
    validate(
      need(input$baseline, "Select a RAW-compatible experiment as baseline first."),
      need(input$jitExperiments, "Select a JIT-compatible experiment first.")
    )
    return(data.speedup()[, "project_name"])
  })

  output$`summary-table` = DT::renderDataTable({
    validate(
      need( input$all, "Select an experiment first.")
    )
    get_projects_per_experiment(db(), input$all)
  })

  output$`experiments-table` = DT::renderDataTable({
    validate(
      need( input$db, "I need a database connection first.")
    )
    get_experiments(db())
  })

  output$speedup.ui = renderUI({
    plotOutput("speedup", width = "100%", height = input$plotSize)
  })
  output$speedup = renderPlot({
    validate(
      need(input$baseline, "Select a RAW-compatible experiment as baseline first."),
      need(input$jitExperiments, "Select a JIT-compatible experiment first."),
      need(input$minY, "Select a minimum for y-axis."),
      need(input$minY, "Select a maximum for y-axis.")
    )

    papi <- trim(input$papiExperiments)
    if (nchar(papi) <= 1 || !input$plotAmdahl) {
      papi <- NULL
    }

    d <- speedup(db(),
                 input$baseline,
                 input$jitExperiments,
                 papi,
                 input$projects,
                 input$groups)

    if (nrow(d) > 0) {
      p <- ggplot(data=d, aes(x = cores, y = speedup_corrected, fill = cores, color = cores))

      if (input$plotTime) {
        p <- p + geom_line(aes(y = time), color = "red") +
                 geom_line(aes(y = ptime), color = "green") +
                 ylab("Runtime in [s]")
      } else {
        p <- p + geom_bar(aes(color = cores), stat = "identity") +
          geom_point(aes(color = cores)) +
          geom_smooth(color = "red") +
          geom_hline(yintercept=1, colour="blue", label = "baseline") +
          geom_abline(slope=1, intercept=0, colour="green", label = "speedup")
        if (input$plotAmdahl && !is.null(papi)) {
          p <- p + geom_line(aes(x = cores, y = speedup_amdahl), color = "orange", label = "amdahl")
        }
        p <- p + coord_cartesian(ylim=c(input$minY, input$maxY)) +
          scale_x_discrete() +
          ylab("Speedup Factor")
      }

      p <- p + facet_wrap(~ project_name, ncol = input$numCols) + xlab("Number of cores")
      p
    }
  })

  output$speedupTable = renderDataTable({
      validate(
        need(input$baseline, "Select a RAW-compatible experiment as baseline first."),
        need(input$jitExperiments, "Select a JIT-compatible experiment first.")
      )
      papi <- trim(as.character(input$papiExperiments))

      cat("spd.table:", papi, "\n")
      if (nchar(papi) <= 1 || !input$plotAmdahl) {
        cat("spd.table:", length(papi), "\n")
        papi <- NULL
      }
      cat("spd.table:", papi, "\n")

      return(speedup(db(),
                     input$baseline,
                     input$jitExperiments,
                     papi,
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

    return(flamegraph(db(), input$perfExperiments, input$perfProjects))
  })


  expTable <- reactive({ get_experiments_per_project(db(), input$projects_per) })

  output$t1 = renderDataTable({
    validate(
      need(input$projects_per, "Select a project first.")
    )

    t <- expTable()
    rownames(t) <- t[,1]

    return(t[,2:3])
  },
  options = list(
    style = 'bootstrap',
    class = 'table-condensed',
    paging = FALSE,
    server = FALSE
  ))

  output$t1Plot = renderPlot({
    validate(
      need(input$baseline, "Select a baseline for plotting."),
      need(input$projects_per, "Select a project first.")
    )

    t <- expTable()
    if (length(input$t1_rows_selected) > 0) {
      t <- t[input$t1_rows_selected, ]
    }

    d <- speedup_per_project(db(), input$projects_per, input$baseline, t[, 1])

    if (nrow(d) > 0) {
      p <- ggplot(data=d, aes(x = cores, y = speedup_corrected, group=experiment_group, fill = cores, color = cores))
      p <- p + geom_line(aes(color = experiment_group)) +
        #geom_smooth(color = "red") +
        geom_hline(yintercept=1, colour="blue") +
        geom_abline(slope=1, intercept=0, colour="green") +
        coord_cartesian(ylim=c(input$minY, input$maxY)) +
        scale_x_discrete() +
        ylab("Speedup Factor")

      p <- p + facet_wrap(~ project_name, ncol = input$numCols) + xlab("Number of cores")
      p
    }
  })

  observe({
    db <- db()
    projects = projects(db)
    exps <- get_experiments(db)

    updateSelectInput(session, "all", choices = c(getSelections(NULL, exps)), selected = 0)
    updateSelectInput(session, "baseline", choices = c(getSelections("raw", exps),
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
                                                             getSelections("pj-raw", exps),
                                                             getSelections("polly-openmp", exps),
                                                             getSelections("polly-openmpvect", exps),
                                                             getSelections("polly-vectorize", exps),
                                                             getSelections("polly", exps)), selected = 0)
    updateSelectInput(session, "projects", choices = projects, selected = 0)

    updateSelectInput(session, "projects_per", choices = projects, selected = 0)
    updateSelectInput(session, "groups", choices = groups(db), selected = 0)
    updateSelectInput(session, "perfExperiments", choices = c(getSelections("pj-perf", exps)), selected = 0)
    updateSelectInput(session, "perfProjects", choices = perfProjects(db), selected = 0)
    updateSelectInput(session, "papiExperiments", choices = c(getSelections("pj-papi", exps),
                                                              getSelections("papi", exps)), selected = 0)
    if (!is.null(input$perfExperiments)) {
      updateSelectInput(session, "perfProjects", choices = perfProjects(db, input$perfExperiments), selected = 0)
    }
  })

  session$onSessionEnded(function() {
    if (!is.null(con))
      dbDisconnect(con)
  })
})
