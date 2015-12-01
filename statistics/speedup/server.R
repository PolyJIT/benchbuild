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

if (!require("shinydashboard")) {
  install.packages("shinydashboard")
  library(shinydashboard)
}

taskTableRenderOpts <- JS(
        "function(data, type, row, meta) {",
        "  if (type === 'display') {",
        "    style = 'label-default'; icon = 'glyphicon-ok';",
        "    if (data === 'completed') { style = 'label-success'; icon = 'glyphicon-ok'; }",
        "    if (data === 'running') { style = 'label-primary'; icon = 'glyphicon-refresh'; }",
        "    if (data === 'failed') { style = 'label-danger'; icon = 'glyphicon-remove'; }",
        "    return '<span class=\"label '+ style +'\" title=\"' + data + '\"><span class=\"glyphicon '+ icon +'\"></span></span>';",
        "  } else {",
        "    return data;",
        "  }",
        "}")
taskTableOpts <- list(
    pageLength = 50,
    rownames = TRUE,
    columnDefs = list(
      list(targets = 5, render = taskTableRenderOpts
      )))

shinyServer(function(input, output, session) {
  con <- NULL

  db <- reactive({
    if (!is.null(con)) {
      dbDisconnect(conn = con)
    }
    validate(need(input$db, "Select a Database."))
    if (input$db == 'buildbot')
      con <- dbConnect(RPostgres::Postgres(), dbname='pprof-bb', user='bb', password='bb', port=5432, host='debussy.fim.uni-passau.de')
    else if (input$db == 'develop')
      con <- dbConnect(RPostgres::Postgres(), dbname='pprof', user='pprof', password='pprof', port=5432, host='debussy.fim.uni-passau.de')
    else if (input$db == 'home')
      con <- dbConnect(RPostgres::Postgres(), dbname='pprof', user='pprof', password='pprof', port=32769, host='192.168.1.107')
    else if (input$db == 'uni')
      con <- dbConnect(RPostgres::Postgres(), dbname='pprof', user='pprof', password='pprof', port=32769, host='132.231.65.195')
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

      if (nchar(papi) <= 1 || !input$plotAmdahl) {
        papi <- NULL
      }

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
    server = TRUE
  ))

  output$taskTable = renderDataTable({
    validate(
      need(input$baseline, "Select an experiment first.")
    )

    tg <- taskGroups(db(), input$baseline)
    if (length(input$taskGroupTable_rows_selected) > 0) {
      tg <- tg[input$taskGroupTable_rows_selected, ]
    }
    t <- tasks(db(), input$baseline, tg[, 1])
    return(t[,2:ncol(t)])
  }, options = list(
    pageLength = -1,
    rownames = FALSE,
    columnDefs = list(
      list(targets = 2, render = taskTableRenderOpts
      ))), style = 'bootstrap', class = 'table-c0ndensed', selection = 'single')

  output$taskGroupTable = renderDataTable({
      validate(
        need(input$baseline, "Select an experiment first.")
      )
      t <- taskGroups(db(), input$baseline)
      return(t[,2:ncol(t)])
    },
    options = list(
    pageLength = 50,
    rownames = FALSE,
    columnDefs = list(
      list(targets = 5, render = taskTableRenderOpts)
    )
  ), style = 'bootstrap', class = 'table-condensed')

  get_selected_run <- reactive({
    validate(
      need(input$baseline, "Select an experiment first.")
    )

    tg <- taskGroups(db(), input$baseline)
    if (length(input$taskGroupTable_rows_selected) > 0) {
      tg <- tg[input$taskGroupTable_rows_selected, ]
    }
    t <- tasks(db(), input$baseline, tg[, 1])
    r <- as.numeric(t[input$taskTable_rows_selected, 1])
    return(r)
  })

  output$stdout = renderText({
    validate(
      need(input$taskTable_rows_selected, "No selection yet.")
    )
    r <- get_selected_run()

    if (!is.null(r)) {
      return(paste("\n", stdout(db(), r)))
    }

    return("No stdout found.")
  })

  output$stderr = renderText({
    validate(
      need(input$taskTable_rows_selected, "No selection yet.")
    )
    r <- get_selected_run()

    if (!is.null(r)) {
      return(paste("\n", stderr(db(), r)))
    }

    return("No stderr found.")
  })

  base_vs_pivot <- reactive({
    validate(
      need(input$compBaselines, "Select baselines to compare."),
      need(input$compExperiments, "Select experiments to compare.")
    )
    if (length(input$compBaselines) == 0 ||
        length(input$compExperiments) == 0 )
      return(NULL)

    baseline_vs_pivot(db(), input$compBaselines, input$compExperiments, input$compProjects, input$compGroups)
  })

  compHeight <- reactive({
    if (is.null(input$compExperiments))
      h <- 0
    else
      h <- length(input$compExperiments)
    return(h)
  })

  output$comparison_single_ui <- renderUI({
    plotOutput("comparison_single", height = 400 * compHeight())
  })

  output$comparison_pairwise_ui <- renderUI({
    plotOutput("comparison_pairwise", height = 400 * compHeight())
  })


  output$comparison_single = renderPlot({
    d <- base_vs_pivot()
    p <- ggplot(data = d, aes(x = gname, y = speedup, colour = pid)) +
      geom_boxplot(aes(group = gname), outlier.size = 0) +
      facet_grid(bid ~ num_cores) +
      scale_x_discrete() +
      theme(axis.text.x = element_text(angle = 90, hjust = 1))
    p
  })

  output$comparison_pairwise = renderPlot({
    d <- base_vs_pivot()
    p <- ggplot(data = d, aes(x = num_cores, y = speedup, colour = pid)) +
      geom_boxplot(aes(group = num_cores), outlier.size = 0) +
      facet_grid(gname ~ bid) +
      scale_x_discrete() +
      theme(axis.text.x = element_text(angle = 90, hjust = 1))
    p
  })

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
      p <- ggplot(data=d, aes(x = cores, y = speedup_corrected, group=experiment_group))
      p <- p +
        geom_bar(aes(color = experiment_group,
                     fill = experiment_group),
                 stat = "identity", position = "dodge") +
        #geom_line(aes(color = experiment_group)) +
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

  output$groupsCompleted <- renderInfoBox({
    infoBox(
      "Completed (G)", icon = icon("thumbs-up", lib = "glyphicon"), color = "green"
    )
  })
  output$groupsFailed <- renderInfoBox({
    infoBox(
      "Failed (G)", icon = icon("thumbs-up", lib = "glyphicon"), color = "red"
    )
  })
  output$groupsCount <- renderInfoBox({
    infoBox(
      "Total (G)", icon = icon("thumbs-up", lib = "glyphicon"), color = "yellow"
    )
  })

  output$tasksCompleted <- renderInfoBox({
    infoBox(
      "Completed (T)", icon = icon("thumbs-up", lib = "glyphicon"), color = "green"
    )
  })
  output$tasksFailed <- renderInfoBox({
    infoBox(
      "Failed (T)", icon = icon("thumbs-up", lib = "glyphicon"), color = "red"
    )
  })
  output$tasksCount <- renderInfoBox({
    infoBox(
      "Count (T)", icon = icon("thumbs-up", lib = "glyphicon"), color = "yellow"
    )
  })

  observe({
    db <- db()
    projects = projects(db)
    exps <- get_experiments(db)

    updateSelectInput(session, "all", choices = c(getSelections(NULL, exps)), selected = 0)
    updateSelectInput(session, "baseline", choices = c(getSelections(NULL, exps)), selected = 0)
    updateSelectInput(session, "compBaselines", choices = c(getSelections(NULL, exps)), selected = 0)
    updateSelectInput(session, "compExperiments", choices = c(getSelections(NULL, exps)), selected = 0)
    updateSelectInput(session, "compProjects", choices = projects, selected = 0)
    updateSelectInput(session, "compGroups", choices = groups(db), selected = 0)

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
