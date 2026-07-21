# =============================================================================
# _targets.R - Pipeline Definition
# =============================================================================
# Published as a record of the model specifications and variable construction;
# not runnable — no data build step is included.
# =============================================================================

library(targets)
library(tarchetypes)

tar_source("R")

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
  "moments"
)
)

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
    path = here::here("data", "raw", "indicators_buurt_wijk_gemeente.csv")
  ),
  format = "rds"
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

# Robustness check: nested random intercepts at all three geographic levels
tar_target(
  name = models_nested,
  command = fit_nested_random_effects(data_final)
),

# ===========================================================================
# PHASE 6: REPORT
# ===========================================================================

tar_target(
  name = model_table,
  command = create_model_table(models_two_level)
)
)
