# =============================================================================
# global.R - Shared data and functions for R Shiny Dashboard
# =============================================================================

library(shiny)
library(shinydashboard)
library(tidyverse)
library(plotly)
library(DT)
library(here)

# =============================================================================
# Data Loading
# =============================================================================

# Try multiple possible data paths
possible_paths <- c(
  here::here("data", "processed", "analysis_ready.csv"),
  here::here("..", "data", "processed", "analysis_ready.csv"),
  here::here("..", "..", "data", "processed", "analysis_ready.csv")
)

data_path <- NULL
for (path in possible_paths) {
  if (file.exists(path)) {
    data_path <- path
    break
  }
}

if (!is.null(data_path)) {
  analysis_data <- readr::read_csv(data_path, show_col_types = FALSE)
  message(paste("Loaded analysis data:", nrow(analysis_data), "rows"))
  DEMO_MODE <- FALSE
} else {
  analysis_data <- NULL
  message("Data file not found - using precomputed results")
  DEMO_MODE <- TRUE
}

# =============================================================================
# Precomputed Results (from last pipeline run)
# =============================================================================

# These are the key results that don't change with user interaction
# Updated from latest pipeline run (February 2025)
precomputed_results <- list(
  summary_stats = list(
    n_obs = 8013,
    n_complete = 4748,
    n_buurten = 1572,
    n_wijken = 869,
    n_gemeenten = 295,
    dv_mean = 70.79,
    dv_sd = 27.41
  ),
  two_level = list(
    icc = 0.0347,
    pct_between = 3.47,
    pct_within = 96.53,
    n_obs = 4748,
    n_clusters = 1572,
    models = list(
      m0 = list(name = "M0: Empty", coef = NA, se = NA),
      m1 = list(name = "M1: + Key Pred", coef = 3.459, se = 0.417),
      m2 = list(name = "M2: + Ind Ctrl", coef = 2.939, se = 0.405),
      m3 = list(name = "M3: + Buurt Ctrl", coef = 0.276, se = 0.947)
    )
  ),
  nested = list(
    icc_gemeente = 0.012,
    icc_wijk = 0.008,
    icc_buurt = 0.014,
    icc_residual = 0.966,
    note = "R-specific: True nested random effects (1|gemeente) + (1|wijk) + (1|buurt)"
  ),
  h3_test = list(
    main_effect_coef = 0.217,
    main_effect_se = 0.949,
    interaction_coef = 0.181,
    interaction_se = 0.343,
    significant = FALSE,
    interpretation = "H3 NOT SUPPORTED: No significant cross-level interaction"
  ),
  sensitivity = list(
    base = list(name = "Base (DV_single)", coef = 0.276, se = 0.947, sig = FALSE),
    two_item = list(name = "2-item composite", coef = 0.312, se = 0.891, sig = FALSE),
    three_item = list(name = "3-item composite", coef = 0.287, se = 0.823, sig = FALSE),
    dutch_only = list(name = "Dutch-born only", coef = 0.189, se = 1.012, sig = FALSE),
    income_ratio = list(name = "Income ratio", coef = -1.841, se = 0.892, sig = TRUE)
  ),
  hypotheses = list(
    h1 = list(
      name = "Neighborhood Inequality Effect",
      result = "NOT SUPPORTED",
      evidence = "Effect non-significant after controls (beta=0.28, p>0.05)"
    ),
    h2 = list(
      name = "Geographic Level Comparison",
      result = "INCONCLUSIVE",
      evidence = "Effects weak at all levels (ICC ~1-2% at each level)"
    ),
    h3 = list(
      name = "Income Moderation",
      result = "NOT SUPPORTED",
      evidence = "Interaction non-significant (beta=0.18, p=0.60)"
    )
  ),
  metadata = list(
    data_source = "SCoRE Netherlands 2017",
    admin_data = "CBS StatLine Table 84286NED (2018)",
    last_updated = "2025-02",
    pipeline_version = "1.0"
  )
)

# =============================================================================
# Variable Labels (for professional visualization)
# =============================================================================

VARIABLE_LABELS <- list(
  # Dependent Variables
  DV_single = "Support for Redistribution (0-100)",
  DV_2item_scaled = "Support for Redistribution (2-Item, 0-100)",
  DV_3item_scaled = "Support for Redistribution (3-Item, 0-100)",

  # Key Predictors
  b_perc_low40_hh = "% Low-Income Households (Neighborhood)",
  w_perc_low40_hh = "% Low-Income Households (District)",
  g_perc_low40_hh = "% Low-Income Households (Municipality)",
  b_income_ratio = "Income Ratio (High/Low, Neighborhood)",

  # Buurt-level Controls
  b_pop_dens = "Population Density (per km²)",
  b_pop_over_65 = "% Residents Age 65+",
  b_pop_nonwest = "% Non-Western Background",
  b_perc_low_inc_hh = "% Below Social Minimum",
  b_perc_high20_hh = "% High-Income Households",

  # Individual-level Variables
  age = "Age (Standardized)",
  age_raw = "Age (Years)",
  sex = "Sex",
  education = "Education Level (Standardized)",
  employment_status = "Employment Status",
  born_in_nl = "Born in Netherlands",
  wealth_index = "Wealth Index (0-4)"
)

# Short labels for constrained space
VARIABLE_LABELS_SHORT <- list(
  b_perc_low40_hh = "% Low-Income HH",
  w_perc_low40_hh = "% Low-Income HH (Wijk)",
  g_perc_low40_hh = "% Low-Income HH (Gem.)",
  b_pop_dens = "Pop. Density",
  b_pop_over_65 = "% Age 65+",
  b_pop_nonwest = "% Non-Western",
  DV_single = "Redistribution Support"
)

# Geographic level labels
GEOGRAPHIC_LABELS <- list(
  buurt = "Neighborhood (Buurt)",
  wijk = "District (Wijk)",
  gemeente = "Municipality (Gemeente)",
  individual = "Individual"
)

# Standard footnotes
FOOTNOTES <- list(
  significance = "* p < 0.05, ** p < 0.01, *** p < 0.001",
  data_source = "Data: SCoRE Netherlands 2017, CBS StatLine 2018",
  ci = "Error bars show 95% confidence intervals",
  standardized = "Variables standardized (mean=0, SD=1)"
)

#' Get human-readable label for a variable
#' @param var_name Variable name
#' @param short Whether to return short label
get_label <- function(var_name, short = FALSE) {
  if (short && var_name %in% names(VARIABLE_LABELS_SHORT)) {
    return(VARIABLE_LABELS_SHORT[[var_name]])
  }
  if (var_name %in% names(VARIABLE_LABELS)) {
    return(VARIABLE_LABELS[[var_name]])
  }
  return(var_name)
}

# =============================================================================
# Color Scheme (matching Python dashboard)
# =============================================================================

COLORS <- list(
  primary = "#1f77b4",     # Blue - main/buurt
  secondary = "#ff7f0e",   # Orange - wijk
  tertiary = "#2ca02c",    # Green - gemeente
  quaternary = "#d62728",  # Red - warnings/highlights
  neutral = "#7f7f7f",     # Gray - non-significant
  background = "#f5f5f5"
)

LEVEL_COLORS <- list(
  buurt = "#1f77b4",

wijk = "#ff7f0e",
  gemeente = "#2ca02c"
)

# =============================================================================
# Dashboard URLs for Cross-Linking
# =============================================================================

# Local development URLs
PYTHON_DASHBOARD_URL_LOCAL <- "http://localhost:8501"
R_DASHBOARD_URL_LOCAL <- "http://localhost:3838"

# Production URLs (update after deployment)
PYTHON_DASHBOARD_URL_PROD <- "https://public-attitudes-research-zcx3tbf4verisz7pavqgzb.streamlit.app/"
R_DASHBOARD_URL_PROD <- "https://kmazurek-analytics.shinyapps.io/income-inequality-attitudes/"

# Use production URLs if available, otherwise local
PYTHON_DASHBOARD_URL <- Sys.getenv("PYTHON_DASHBOARD_URL", PYTHON_DASHBOARD_URL_PROD)
R_DASHBOARD_URL <- Sys.getenv("R_DASHBOARD_URL", R_DASHBOARD_URL_PROD)

# =============================================================================
# Helper Functions
# =============================================================================

#' Get summary statistics for the dashboard
get_summary_stats <- function(data) {
  # If no data, use precomputed results
 if (is.null(data)) {
    return(precomputed_results$summary_stats)
  }

  list(
    n_obs = nrow(data),
    n_complete = sum(complete.cases(data[c("DV_single", "buurt_id", "b_perc_low40_hh")])),
    n_buurten = length(unique(data$buurt_id)),
    n_wijken = if ("wijk_id" %in% names(data)) length(unique(data$wijk_id)) else NA,
    n_gemeenten = if ("gemeente_id" %in% names(data)) length(unique(data$gemeente_id)) else NA,
    dv_mean = mean(data$DV_single, na.rm = TRUE),
    dv_sd = sd(data$DV_single, na.rm = TRUE)
  )
}

#' Check if running in demo mode
is_demo_mode <- function() {
  return(DEMO_MODE)
}

#' Get demo mode message
get_demo_mode_message <- function() {
  "Running in demo mode with precomputed results. Interactive data exploration is limited."
}

#' Create a value box with custom styling
create_metric_box <- function(value, subtitle, icon_name = "chart-bar", color = "blue") {
  valueBox(
    value = value,
    subtitle = subtitle,
    icon = icon(icon_name),
    color = color
  )
}

# Source utility functions
source("utils/charts.R")
