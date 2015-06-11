library(shiny)

shinyUI(navbarPage("PolyJIT Experiments",
  tabPanel("Raw Timings",
    p("Simple timing plots that have been generated using Raw-like experiments."),
    tabsetPanel("Plots",
      tabPanel("Single Plots",
        sidebarPanel(
         selectInput("rawExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'), width = 3
        ),
        mainPanel(
          tabsetPanel("Visualisation Type",
            tabPanel("Table",
                    dataTableOutput("timingTable")
            ),
            tabPanel("Single",
                    plotOutput("timing", width = "100%", height = "700px")
            )
          )
        )
      ),
      tabPanel("Diffs",
               wellPanel()
      )
    )
  ),
  tabPanel("papi",
    # Sidebar with a slider input for number of bins
    sidebarLayout(
      sidebarPanel(
        selectInput("papiExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'), width = 3
      ),
      mainPanel(
        plotOutput("papi", width = "100%", height = "700px"),
        plotOutput("papiBoxplot", width = "100%", height = "700px")
      )
    )
  ),
  tabPanel("papi-std",
    # Sidebar with a slider input for number of bins
    sidebarLayout(
      sidebarPanel(
        selectInput("papiStdExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'), width = 3
      ),
      mainPanel(
        plotOutput("papiStd", width = "100%", height = "700px"),
        plotOutput("papiStdBoxplot", width = "100%", height = "700px")
      )
    )
  ),
  tabPanel("polyjit",
    # Sidebar with a slider input for number of bins
    sidebarLayout(
      sidebarPanel(
        selectInput("polyjitExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'),
        selectInput("polyjitMetrics", label = "Metric", multiple = FALSE, choices = NULL, width = '100%'),
        selectInput("polyjitAggregation", label = "Aggregation", multiple = FALSE,
                    choices = c("SUM", "MAX", "MIN", "AVG")),
        width = 3
      ),
      mainPanel(
        plotOutput("polyjit", width = "100%", height = "700px")
      )
    )
  )
))
