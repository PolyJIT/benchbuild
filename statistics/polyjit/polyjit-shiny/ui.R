library(shiny)

shinyUI(
  navbarPage(
    "PolyJIT Experiments", theme="css/bootstrap.min.css",
    # Raw Experiment
    tabPanel(
      "Raw",
      fluidPage(
        fluidRow(
          column(
            width = 4,
            selectInput("rawExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%')
          )
        ),
        fluidRow(
          column(
            width = 12,
            p("Simple timing plots that have been generated using Raw-like experiments.")
          )
        ),
        fluidRow(
          column(
            width = 12,
            tabsetPanel(
              "Visualisation Type",
              tabPanel(
                "Table",
                dataTableOutput("timingTable")
              ),
              tabPanel(
                "Plot",
                plotOutput("timing", width = "100%", height = "700px")
              )
            )
          )
        )
      )
    ),
    
    # DynCov Experiment
    tabPanel(
      "DynCov",
      fluidPage(
        fluidRow(
          column(width = 4, selectInput("papiExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'))
        ),
        fluidRow(
          column(
            width = 12,
            p("Dynamic SCoP coverage grouped/sorted by domain, depending on the plot type.")
          )
        ),
        fluidRow(
          column(
            width = 12,
            p(withMathJax(strwrap(
              "Let \\(t_{SCoPs}\\) denote the time spent inside SCoPs and \\(t_{Total}\\)
         denote the total runtime of a program \\(P\\), dynamic SCoP coverage is
         then defined as: $$DynCov_{P} = \\frac{t_{SCoPs}}{t_{t_{Total}}}$$")))
          )
        ),
        fluidRow(
          column(
            width = 12,
            tabsetPanel(
              "Visualisation Type",
              tabPanel("Table", dataTableOutput("papiTable")),
              tabPanel("Default", plotOutput("papi", width = "100%", height = "700px")),
              tabPanel("Boxplot", plotOutput("papiBoxplot", width = "100%", height = "700px"))
            )  
          )
        )
      )
    ),
    
    # Compilation Stats
    tabPanel(
      "CompStats",
      fluidPage(
        fluidRow(
          column(width = 4, selectInput("csExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%')),
          column(width = 4, selectInput("csComponent", label = "Component", multiple = FALSE, choices = NULL)),
          column(width = 4, selectInput("csName", label = "Name", multiple = FALSE, choices = NULL, width = '100%'))
        ),
        fluidRow(
          column(
            width = 12,
            p(withMathJax(strwrap(
              "Likwid measurements have to generated/submitted via the pprof helper
                 functions. Nothing special is done with the measurements itself, we're
                 just dumping them.")))
          )
        ),
        fluidRow(
          column(
            width = 12,
            tabsetPanel(
              "Items",
              tabPanel(
                "Table",
                dataTableOutput("csTable")
              )
            )
          )
        )
      )
    ),
    
    # Likwid Experiment
    tabPanel(
      "Likwid",
      fluidPage(
        fluidRow(
          column(width = 4, selectInput("polyjitExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%')),
          column(width = 4, selectInput("polyjitMetrics", label = "Metric", multiple = FALSE, choices = NULL, width = '100%')),
          column(width = 4, selectInput("polyjitAggregation", label = "Aggregation", multiple = FALSE,
                                        choices = c("SUM", "MAX", "MIN", "AVG")))
        ),
        fluidRow(
          column(
            width = 12,
            p(withMathJax(strwrap(
              "Likwid measurements have to generated/submitted via the pprof helper
             functions. Nothing special is done with the measurements itself, we're
             just dumping them.")))),
          column(
            width = 12,
            tabsetPanel(
              "Items",
              tabPanel(
                "Table",
                dataTableOutput("polyjitTable")
              ),
              tabPanel(
                "Plots",
                plotOutput("polyjit", width = "100%", height = "700px")
              )
            )
          )
        )
      )
    ),
    
    # Experiment Logs
    tabPanel(
      "Logs",
      fluidPage(
        fluidRow(
          column(width = 4, selectInput("logExperiments", label = "Experiment", multiple = FALSE, choices = NULL, width = '100%'))
        ),
        fluidRow(
          column(
            width = 12,
            dataTableOutput("log")
          )
        )
      )
    )
  ))
