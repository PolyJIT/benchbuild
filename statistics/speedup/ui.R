library(shiny)
library(DT)

shinyUI(
  navbarPage(
    "PolyJIT Speedup Measurements", theme="css/bootstrap.min.css",
    # Raw Experiment
    tabPanel(
      "Profiles",
      fluidPage(
        fluidRow(
          column(width = 4,
                 selectInput("perfExperiments", label = "Profile Experiment", multiple = FALSE, choices = NULL, width = '100%')),
          column(width = 4,
                 selectInput("perfProjects", label = "Projects", multiple = FALSE, choices = NULL, width = '100%'))
        ),
        fluidRow(
          p("Run-time profile per project, presented as flamegraph.")
        ),
        fluidRow(column(width = 12,
                        htmlOutput("flamegraph")))
      )
    ),
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
        fluidRow(column(width = 12,
            tabsetPanel(
              "Visualisation",
              tabPanel("Table", dataTableOutput("speedupTable")),
              tabPanel("Plot",
                       fluidRow(
                         column(width = 4,
                                numericInput("plotSize", label = "Plot Height (px):", 1200, min = 480, max = 64000)),
                         column(width = 4,
                                numericInput("numCols", label = "Number of facet columns:", 4, min = 1, max = 42)),
                         column(width = 2,
                                checkboxInput("plotTime", label = "Plot absolute timings", value = FALSE))
                       ),
                       fluidRow(
                         uiOutput("speedup.ui"))
                      )
            )
          )
        )))))