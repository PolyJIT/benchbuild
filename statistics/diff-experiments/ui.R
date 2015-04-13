
# This is the user-interface definition of a Shiny web application.
# You can find out more about building applications with Shiny here:
#
# http://shiny.rstudio.com
#

library(shiny)

getCSVfiles<-function() {
  files<-list.files(path="data/", pattern="*.csv")
  return(files)
}

getExpList<-function() {

}

files<-getCSVfiles()

shinyUI(navbarPage("Polli Profiling",
  tabPanel("Single experiment",
           sidebarLayout(
             selectInput(inputId="ifiles", label="Result files:", choices=files, multiple=FALSE, selected=files[0]),
             mainPanel(
               tabsetPanel(
                 tabPanel("Raw Data", tableOutput("printTable")),
                 tabPanel("Plot by project", uiOutput("plots")),
                 tabPanel("Plot summary", plotOutput("experimentSummary", width = 1280, height = 800))
               )
           ))),
  tabPanel("Diff",
           verticalLayout(
             fluidRow(column(width=4,
                             radioButtons(inputId="leftFile", label="Left:", choices=files, selected=files[0])),
                      column(width=4, offset=4,
                             radioButtons(inputId="rightFile", label="Right:", choices=files, selected=files[0]))
                     )
          ))
))
