library(shiny)

shinyUI(
navbarPage(
  "PolyJIT Experiments", theme="css/bootstrap.css",
  
  # Raw Experiment
  tabPanel(
    "Raw",
    sidebarPanel(
      selectInput("rawExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'), width = 3
    ),
    mainPanel(
      p("Simple timing plots that have been generated using Raw-like experiments."),
      tabsetPanel(
        "Visualisation Type",
        tabPanel(
          "Table",
          dataTableOutput("timingTable")
        ),
        tabPanel(
          "Plot",
          plotOutput("timing", width = "100%", height = "700px")
        ),
        tabPanel(
          "Logs",
          wellPanel(p("Not implemented yet."))
        )
      )
    )
  ),
  
  # DynCov Experiment
  tabPanel(
    "DynCov",
    sidebarPanel(
      selectInput("papiExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'), width = 3
    ),
    mainPanel(
      p("Dynamic SCoP coverage grouped/sorted by domain, depending on the plot type."),
      p(withMathJax(strwrap(
        "Let \\(t_{SCoPs}\\) denote the time spent inside SCoPs and \\(t_{Total}\\)
         denote the total runtime of a program \\(P\\), dynamic SCoP coverage is
         then defined as: $$DynCov_{P} = \\frac{t_{SCoPs}}{t_{t_{Total}}}$$"))),
      tabsetPanel(
        "Visualisation Type",
        tabPanel("Table", dataTableOutput("papiTable")),
        tabPanel("Default", plotOutput("papi", width = "100%", height = "700px")),
        tabPanel("Boxplot", plotOutput("papiBoxplot", width = "100%", height = "700px")),
        tabPanel("Logs", wellPanel(p("Not implemented yet.")))
      )
    )
  ),
  
  # Likwid Experiment
  tabPanel(
    "Likwid",
    sidebarLayout(
      sidebarPanel(
        selectInput("polyjitExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'),
        selectInput("polyjitMetrics", label = "Metric", multiple = FALSE, choices = NULL, width = '100%'),
        selectInput("polyjitAggregation", label = "Aggregation", multiple = FALSE,
                    choices = c("SUM", "MAX", "MIN", "AVG")),
        width = 3
      ),
      mainPanel(
        p(withMathJax(strwrap(
          "Likwid measurements have to generated/submitted via the pprof helper
             functions. Nothing special is done with the measurements itself, we're
             just dumping them."))),
        tabsetPanel(
          "Items",
          tabPanel(
            "Plots",
            plotOutput("polyjit", width = "100%", height = "700px")
          ),
          tabPanel(
            "Log",
            mainPanel(dataTableOutput("polyjitLog"))
          )
        )
      )
    )
  )
))
