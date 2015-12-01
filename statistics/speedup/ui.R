if (!require("shinydashboard")) {
  install.packages("shinydashboard")
  library(shinydashboard)
}

library(shiny)
library(DT)

shinyUI(
  dashboardPage(
    dashboardHeader(title = "PolyJIT"),
    dashboardSidebar(
      sidebarMenu(
        menuItem("Summary", tabName = "summary"),
        menuItem("Comparison", tabName = "comparison"),
        selectInput("baseline", label = "Baseline", multiple = FALSE, choices = NULL, width = '100%'),
        menuItem("Speedup", tabName = "speedup",
                 menuSubItem("Per experiment", tabName = "speedupExperiment"),
                 menuSubItem("Per project", tabName = "speedupProject")),
        menuItem("Profiles", tabName = "profiles"),
        menuItem("Tasks", tabName = "tasks"),
        selectInput("db", label = "Database", choices = c("buildbot", "home", "develop", "uni"), multiple = FALSE, selected = 0)
      )
    ),
    dashboardBody(
      tabItems(
        tabItem(tabName = "summary",
                fluidRow(
                  h3("Experiments"),
                  p("The following experiments are available in this database instance of the pprof-study.")
                ),
                fluidRow(
                  column(width = 12,
                         dataTableOutput("experiments-table")
                  )
                ),
                fluidRow(
                  h3("Summary per experiment"),
                  p("This shows a quick summary for all projects that were executed for a given experiment")
                ),
                fluidRow(
                  column(width = 4,
                         selectInput("all", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%')),
                  column(width = 12,
                         wellPanel(
                           dataTableOutput("summary-table")
                         ))
                )
        ),
        tabItem(tabName = "comparison",
                fluidRow(
                  box(title = "Experiments", solidHeader = TRUE, width = 6,
                      selectInput("compBaselines", label = "Baselines", multiple = TRUE, choices = NULL, width = '100%'),
                      selectInput("compExperiments", label = "Experiments", multiple = TRUE, choices = NULL, width = '100%')),
                  box(title = "Filters", solidHeader = TRUE, width = 6,
                      selectInput("compProjects", label = "Projects", multiple = TRUE, choices = NULL, width = '100%'),
                      selectInput("compGroups", label = "Groups", multiple = TRUE, choices = NULL, width = '100%'))
                ),
                fluidRow(
                  tabBox(title = 'Compare experiments', width = 12,
                         tabPanel("Single-Core", id = "tabBox",
                                  paste("Comparison between the single-core configuration of each possible
                                         baseline and all configurations of the run-time experiments."),
                                  htmlOutput("comparison_single_ui")
                         ),
                         tabPanel("Pairwise",
                                  paste("For each configuration of each experiment compare it to a matching
                                         configuration for each experiment. A configuration matches, if it
                                         uses the same number of cores."),
                                  htmlOutput("comparison_pairwise_ui")
                         )
                  )
                )
        ),
        tabItem(tabName = "speedupExperiment",
                fluidRow(
                  box(title = "Experiment", status = "primary", solidHeader = TRUE, width = 4, height = 220,
                      selectInput("jitExperiments", label = "Time", multiple = FALSE, choices = NULL, width = '100%'),
                      paste("Compare the selected experiment to the selected baseline experiment. This takes the
                             single-core configuration of the given baseline and compares it to all configurations
                             of the selected experiment per project.")
                  ),
                  box(title = "PAPI Experiment", status = "primary", solidHeader = TRUE, width = 4, height = 220,
                      selectInput("papiExperiments", label = "PAPI", multiple = FALSE, choices = NULL, width = '100%'),
                      checkboxInput("plotAmdahl", label = "Draw Amdahl speedup", value = TRUE),
                      paste("You can pick an optional PAPI-based experiment to derive a theoretical upper limit
                             for the speedup factor using Amdahl's law.")
                  ),
                  box(title = "Filters", status = "primary", solidHeader = TRUE, width = 4, height = 220,
                      selectInput("projects", label = "Projects", multiple = TRUE, choices = NULL, width = '100%'),
                      selectInput("groups", label = "Groups", multiple = TRUE, choices = NULL, width = '100%')
                  )
                ),
                fluidRow(
                  tabBox(title = "Visualisation", width = 12,
                         tabPanel("Table",
                                  dataTableOutput("speedupTable")
                         ),
                         tabPanel("Plot",
                                  fluidRow(
                                    box(title = "Sizes",
                                        numericInput("plotSize", label = "Plot Height (px):", 2400, min = 480, max = 64000),
                                        numericInput("numCols", label = "Number of facet columns:", 4, min = 1, max = 42)
                                    ),
                                    box(title = "Layout",
                                        numericInput("minY", label = "Y-Axis min:", -10, min = -1, max = 1000),
                                        numericInput("maxY", label = "Y-Axis max:", 10, min = 1, max = 1000),
                                        checkboxInput("plotTime", label = "Plot absolute timings", value = FALSE)
                                    )
                                  ),
                                  fluidRow(
                                    uiOutput("speedup.ui")
                                  )
                         )
                  )
                )
        ),
        tabItem(tabName = "speedupProject",
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
        ),
        tabItem(tabName = "profiles",
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
                                htmlOutput("flamegraph"))),
                hr()
        ),
        tabItem(tabName = "tasks",
                fluidRow(
                  box(title = "Summary", width = 12,
                      infoBoxOutput("groupsCompleted"),
                      infoBoxOutput("groupsFailed"),
                      infoBoxOutput("groupsCount"),
                      infoBoxOutput("tasksCompleted"),
                      infoBoxOutput("tasksFailed"),
                      infoBoxOutput("tasksCount")
                  )
                ),
                fluidRow(
                  tabBox(title = "Tool status output", width = 12, height = 1200,
                         tabPanel("Filter",
                                  box(title = "Task Groups", width = 6,
                                      dataTableOutput("taskGroupTable")
                                  ),
                                  box(title = "Tasks", width = 6,
                                      dataTableOutput("taskTable")
                                  )
                                  
                         ),
                         tabPanel("stdout",
                                  verbatimTextOutput("stdout")),
                         tabPanel("stderr",
                                  verbatimTextOutput("stderr"))
                  )
                )
        )
      )
    )
  )
)