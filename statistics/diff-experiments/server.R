
# This is the server logic for a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#
library(shiny)
library(reshape)
library(ggplot2)

options(shiny.usecairo=FALSE)

shinyServer(function(input, output) {
  experiment <- reactive({
    if (is.null(input$ifiles)) { return (NULL) }
    set <- read.csv(file.path("data", input$ifiles), header=T, sep=",")
    set <- melt(set, id=c("Name", "Domain"))
    set <- subset(set, set$variable != "T_SCoP_ns")
    set <- subset(set, set$variable != "T_all_ns")
    set <- subset(set, set$variable != "DynCov")
    set <- set[order(set$Name),]
    set
  })

  output$plots <- renderUI({
    exp <- experiment()
    projects <- unique(exp$Name)
    num_projects <- length(projects)
    for (i in 1:num_projects) {
      local({
        my_i <- i
        my_set <- subset(exp, exp$Name == projects[my_i])

        plotname <- paste("plot", my_i, sep="")
        output[[plotname]] <- renderPlot({
          p <- ggplot(data=my_set, aes(x=variable, y=value, fill=variable)) +
            geom_bar(stat="identity") + ggtitle(toString(projects[my_i]))
          p
        })
      })
    }

    plot_output_list <- lapply(1:length(unique(experiment()$Name)), function(i) {
      plotname <- paste("plot", i, sep="")
      plotOutput(plotname, width=600, height=300)
    })

    do.call(tagList, plot_output_list)
  })

  output$printTable <- renderTable({
    if (is.null(input$ifiles)) { return(NULL) }
    set <- read.csv(file.path("data", input$ifiles), header=T, sep=",")
    set <- set[order(set$Name),]
    set <- set[order(set$Domain),]
    set
  })

  output$experimentSummary <- renderPlot({
    plot(experiment())
  })
})
