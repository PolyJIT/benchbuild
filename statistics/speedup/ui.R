library(shiny)
library(DT)

shinyUI(
  navbarPage(
    "PolyJIT", theme="css/bootstrap.min.css",
    # Raw Experiment
    tabPanel(
      "Speedup",
      fluidPage(
        fluidRow(
          column(width = 4, selectInput("db", label = "Database", choices = c("buildbot", "develop"), multiple = FALSE, selected = 0)),
          column(width = 4,
                 selectInput("baseline", label = "Baseline", multiple = FALSE, choices = NULL, width = '100%'))
        ),
        fluidRow(
          column(width = 12,
                 wellPanel(
                   dataTableOutput("summary-table")
                 ))
        ),
        tabsetPanel(
          tabPanel("Per Experiment",
                   fluidRow(
                     column(width = 4,
                            selectInput("jitExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'))
                   ),
                   fluidRow(
                     column(width = 4,
                            selectInput("papiExperiments", label = "Dyn Cov", multiple = FALSE, choices = NULL, width = '100%')),
                     column(width = 4,
                            checkboxInput("plotAmdahl", label = "Plot Amdahl speedup", value = TRUE))
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
                                                       numericInput("plotSize", label = "Plot Height (px):", 2400, min = 480, max = 64000)),
                                                column(width = 4,
                                                       numericInput("numCols", label = "Number of facet columns:", 4, min = 1, max = 42)),
                                                column(width = 2,
                                                       checkboxInput("plotTime", label = "Plot absolute timings", value = FALSE))
                                              ),
                                              fluidRow(
                                                column(width = 4,
                                                       numericInput("minY", label = "Y-Axis min:", -10, min = -1, max = 1000)),
                                                column(width = 4,
                                                       numericInput("maxY", label = "Y-Axis max:", 10, min = 1, max = 1000))
                                              ),
                                              fluidRow(
                                                uiOutput("speedup.ui")
                                              )
                                     )
                                   )
                   )
                   )
          ),
          tabPanel("Per Project",
                   fluidRow(
                     column(width = 4,
                            selectInput("projects_per", label = "Project", multiple = FALSE, choices = NULL, width = '100%'))),
                   fluidRow(
                     column(width = 12,
                            h4("Speedup measurements"),
                            plotOutput("t1Plot"))),
                   fluidRow(
                     column(width = 12,
                            h4("Available experiments"))),
                   fluidRow(
                     column(width = 12, dataTableOutput("t1"))
                   )
          )
        )
      )
    ),
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
    )
  ))