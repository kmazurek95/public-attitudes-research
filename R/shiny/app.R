# =============================================================================
# app.R - R Shiny Dashboard for Income Inequality Analysis
# =============================================================================
# Main entry point for the R Shiny dashboard.
#
# Run with: shiny::runApp("R/shiny")
# =============================================================================

library(shiny)
library(shinydashboard)
library(tidyverse)
library(plotly)
library(DT)
library(here)

# Source components
source("global.R")
source("ui.R")
source("server.R")

# Run the application
shinyApp(ui = ui, server = server)
