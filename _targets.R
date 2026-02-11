# =============================================================================
# _targets.R - Pipeline Definition
# =============================================================================
# This file defines the reproducible analysis pipeline using the targets package.
#
# To run the pipeline:
#   library(targets)
#   tar_make()
#
# To visualize the pipeline:
#   tar_visnetwork()
#
# To check status:
#   tar_progress()
# =============================================================================

# Load packages
library(targets)
library(tarchetypes)

# Source all R functions
tar_source("R")

# =============================================================================
# CONFIGURATION
# =============================================================================
# Set USE_CBS_API = TRUE to download fresh data from CBS StatLine
# Set USE_CBS_API = FALSE to use local pre-downloaded files
USE_CBS_API <- FALSE

# Set options
tar_option_set(
packages = c(
  "tidyverse",
  "haven",
  "stringr",
  "lme4",
  "lmerTest",
  "performance",
  "car",
  "modelsummary",
  "gtsummary",
  "gt",
  "here",
  "glue",
  "moments",
  "cbsodataR"
)
)

# Define the pipeline
list(

# ===========================================================================
# PHASE 1: EXTRACT - Load raw data
# ===========================================================================

tar_target(
  name = survey_raw,
  command = load_survey_data(here::here("data", "raw", "score.dta")),
  format = "rds"
),

tar_target(
  name = admin_raw,
  command = load_admin_data(
    path = here::here("data", "raw", "indicators_buurt_wijk_gemeente.csv"),
    use_api = USE_CBS_API,
    table_id = "84286NED"
  ),
  format = "rds"
),

tar_target(
  name = raw_validation,
  command = validate_raw_data(survey_raw, admin_raw)
),

# ===========================================================================
# PHASE 2: TRANSFORM - Create geo IDs and prepare data
# ===========================================================================

tar_target(
  name = survey_with_geo,
  command = create_geo_ids(survey_raw),
  format = "rds"
),

tar_target(
  name = admin_by_level,
  command = prepare_admin_by_level(admin_raw)
),

# ===========================================================================
# PHASE 3: LOAD - Merge and validate
# ===========================================================================

tar_target(
  name = merged_data,
  command = merge_survey_admin(survey_with_geo, admin_by_level),
  format = "rds"
),

tar_target(
  name = merge_validation,
  command = validate_merge(merged_data)
),

tar_target(
  name = missingness_report,
  command = analyze_missingness(merged_data)
),

# ===========================================================================
# PHASE 4: TRANSFORM - Recode and standardize
# ===========================================================================

tar_target(
  name = data_recoded,
  command = recode_survey_variables(merged_data),
  format = "rds"
),

tar_target(
  name = matched_comparison,
  command = compare_matched_unmatched(data_recoded)
),

# NEW: Create inequality indices (matches Python pipeline)
tar_target(
  name = data_with_indices,
  command = create_inequality_indices(data_recoded),
  format = "rds"
),

tar_target(
  name = data_final,
  command = standardize_context_vars(data_with_indices),
  format = "rds"
),

tar_target(
  name = analysis_sample,
  command = create_analysis_sample(data_final, include_occupation = TRUE),
  format = "rds"
),

# ===========================================================================
# PHASE 5: ANALYZE - Fit models and run diagnostics
# ===========================================================================

tar_target(
  name = models_two_level,
  command = fit_two_level_models(analysis_sample)
),

tar_target(
  name = icc_results,
  command = calculate_icc(models_two_level)
),

tar_target(
  name = diagnostics,
  command = run_diagnostics(models_two_level$m3_buurt_controls, analysis_sample)
),

tar_target(
  name = sensitivity_results,
  command = run_sensitivity(data_final)
),

# R-SPECIFIC: True nested random effects models
# This is a robustness check using lme4's capability for nested random effects
# which Python's statsmodels cannot replicate
tar_target(
  name = models_nested,
  command = fit_nested_random_effects(data_final)
),

# H3 Test: Cross-level interaction (individual income moderation)
tar_target(
  name = h3_results,
  command = test_h3_cross_level_interaction(data_final)
),

# ===========================================================================
# PHASE 6: REPORT - Generate outputs
# ===========================================================================

tar_target(
  name = model_table,
  command = create_model_table(
    models_two_level,
    output_path = here::here("outputs", "tables", "regression_table.html")
  )
),

tar_target(
  name = analysis_report,
  command = generate_report(
    models_two_level,
    icc_results,
    diagnostics,
    sensitivity_results,
    merge_validation
  )
),

# Save final dataset
tar_target(
  name = save_final_data,
  command = {
    readr::write_csv(
      data_final,
      here::here("data", "processed", "analysis_ready.csv")
    )
    here::here("data", "processed", "analysis_ready.csv")
  },
  format = "file"
)
)
