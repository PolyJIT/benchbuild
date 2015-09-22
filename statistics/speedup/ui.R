library(shiny)

shinyUI(
  navbarPage(
    "PolyJIT Speedup Measurements", theme="css/bootstrap.min.css",
    # Raw Experiment
    tabPanel(
      "Home",
      fluidPage(
        fluidRow(
          column(width = 4,
            selectInput("rawExperiments", label = "Baseline", multiple = FALSE, choices = NULL, width = '100%')),
          column(width = 4,
            selectInput("jitExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'))
        ),
        fluidRow(column(width = 8,
            p("Compare PolyJIT Runtime to a Baseline experiment of your choice."))
        ),
        fluidRow(
          column(width = 4,
            selectInput("projects", label = "Projects", multiple = TRUE, choices = NULL, width = '100%')),
          column(width = 4,
            selectInput("groups", label = "Groups", multiple = TRUE, choices = NULL, width = '100%'))
        ),
        fluidRow(
        ),
        fluidRow(column(width = 8,
            tabsetPanel(
              "Visualisation",
              tabPanel("Table", dataTableOutput("speedupT")),
              tabPanel("Plot", plotOutput("speedup", width = "100%", height = "700px"))
            )
          )
        )))))