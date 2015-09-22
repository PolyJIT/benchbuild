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


  output$speedup = renderPlot({
    validate(
      need(input$rawExperiments, "Select a RAW-compatible experiment as baseline first."),
      need(input$jitExperiments, "Select a JIT-compatible experiment first.")
    )
    d <- speedup(con, input$rawExperiments, input$jitExperiments, input$projects, input$groups)
    
    if (nrow(d) > 0) {
      ggplot(data=d,
             aes(x = cores, y = speedup_corrected, fill = cores, color = cores)) +
        geom_point(aes(color = cores)) +
        geom_line() +
        facet_grid(project_name ~ .)
    }
  })

  output$speedupTable = renderDataTable({
      validate(
        need(input$rawExperiments, "Select a RAW-compatible experiment as baseline first."),
        need(input$jitExperiments, "Select a JIT-compatible experiment first.")
      )
      return(speedup(con, input$rawExperiments, input$jitExperiments, input$projects, input$groups))
    },
    options = list(
      style = 'bootstrap',
      class = 'table-condensed'
    )
  )

  updateSelectInput(session, "rawExperiments", choices = c(getSelections("raw", exps),
                                               getSelections("polly", exps),
                                               getSelections("polly-openmp", exps),
                                               getSelections("polly-vectorize", exps),
                                               getSelections("polly-openmpvect", exps),
                                               getSelections("papi", exps),
                                               getSelections("papi-std", exps)), selected = 0)
  updateSelectInput(session, "jitExperiments", choices = getSelections("polyjit", exps), selected = 0)
  updateSelectInput(session, "projects", choices = projects(con), selected = 0)
  updateSelectInput(session, "groups", choices = groups(con), selected = 0)
  
  session$onSessionEnded(function() {
    dbDisconnect(con)
  })
})
