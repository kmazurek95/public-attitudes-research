# =============================================================================
# 00_packages.R - Package Management
# =============================================================================
# This script handles all package installation and loading for the project.
# Run this first to ensure all dependencies are available.
# =============================================================================

# Required packages
required_packages <- c(
  # Pipeline orchestration
  "targets",
  "tarchetypes",

  # Data manipulation
  "tidyverse",
  "haven",       # Read Stata files
  "janitor",     # Clean column names
  "stringr",     # String manipulation

  # Data collection
  "cbsodataR",   # CBS StatLine API

  # Statistical modeling
  "lme4",        # Mixed effects models
  "lmerTest",    # P-values for lmer
  "performance", # Model diagnostics (ICC)
  "car",         # VIF calculation

  # Reporting
  "modelsummary", # Regression tables
  "gtsummary",    # Descriptive tables
  "gt",           # Table formatting
  "knitr",        # Report generation

  # Visualization
  "ggplot2",
  "patchwork",   # Combine plots
  "corrr",       # Correlation matrices

  # Utilities
  "here",        # Relative paths
  "fs",          # File system operations
  "glue",        # String interpolation
  "moments"      # Skewness/kurtosis
)

# -----------------------------------------------------------------------------
# Install missing packages
# -----------------------------------------------------------------------------
install_if_missing <- function(packages) {
  missing <- packages[!(packages %in% installed.packages()[, "Package"])]
  if (length(missing) > 0) {
    message("Installing missing packages: ", paste(missing, collapse = ", "))
    install.packages(missing, repos = "https://cloud.r-project.org")
  } else {
    message("All packages already installed.")
  }
}

# Run installation FIRST (before any loading)
install_if_missing(required_packages)

# -----------------------------------------------------------------------------
# Load packages
# -----------------------------------------------------------------------------
load_packages <- function(packages) {
  for (pkg in packages) {
    suppressPackageStartupMessages(library(pkg, character.only = TRUE))
  }
  message("All packages loaded successfully.")
}

# -----------------------------------------------------------------------------
# Check package versions (for reproducibility)
# -----------------------------------------------------------------------------
check_versions <- function(packages) {
  versions <- sapply(packages, function(pkg) {
    as.character(packageVersion(pkg))
  })
  data.frame(
    package = packages,
    version = versions,
    row.names = NULL
  )
}

# -----------------------------------------------------------------------------
# Run on source
# -----------------------------------------------------------------------------
if (interactive()) {
  load_packages(required_packages)
  cat("\nPackage versions:\n")
  print(check_versions(required_packages))
}
