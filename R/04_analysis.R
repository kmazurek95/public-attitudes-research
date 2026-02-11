# =============================================================================
# 04_analysis.R - Statistical Analysis Functions
# =============================================================================
# Functions for multilevel modeling, diagnostics, and output generation.
# =============================================================================

#' Fit Two-Level Models
#'
#' Fits the sequence of two-level multilevel models (individuals in buurten).
#'
#' @param data Analysis dataset
#' @return A list of fitted lmer models
fit_two_level_models <- function(data) {

message("Fitting two-level multilevel models...")

# m0: Empty model
message("  Fitting m0 (empty model)...")
m0 <- lme4::lmer(
  DV_single ~ 1 + (1 | buurt_id),
  data = data,
  REML = TRUE
)

# m1: Add key predictor
message("  Fitting m1 (+ key predictor)...")
m1 <- lme4::lmer(
  DV_single ~ b_perc_low40_hh + (1 | buurt_id),
  data = data,
  REML = TRUE
)

# m2: Add individual controls
message("  Fitting m2 (+ individual controls)...")
m2 <- lme4::lmer(
  DV_single ~ b_perc_low40_hh + age + sex + education +
    employment_status + occupation + born_in_nl +
    (1 | buurt_id),
  data = data,
  REML = TRUE
)

# m3: Add buurt controls
message("  Fitting m3 (+ buurt controls)...")
m3 <- lme4::lmer(
  DV_single ~ b_perc_low40_hh + age + sex + education +
    employment_status + occupation + born_in_nl +
    b_pop_dens + b_pop_over_65 + b_pop_nonwest +
    b_perc_low_inc_hh + b_perc_soc_min_hh +
    (1 | buurt_id),
  data = data,
  REML = TRUE
)

models <- list(
  m0_empty = m0,
  m1_key_pred = m1,
  m2_ind_controls = m2,
  m3_buurt_controls = m3
)

message("  All models fitted successfully")

return(models)
}


#' Calculate ICC and Variance Decomposition
#'
#' Calculates intraclass correlation from empty model.
#'
#' @param models List of fitted models
#' @return A list with ICC and variance components
calculate_icc <- function(models) {

message("Calculating ICC and variance decomposition...")

m0 <- models$m0_empty

# Use performance package
icc_result <- performance::icc(m0)

# Extract variance components manually
vc <- as.data.frame(lme4::VarCorr(m0))
var_buurt <- vc$vcov[vc$grp == "buurt_id"]
var_residual <- vc$vcov[vc$grp == "Residual"]
total_var <- var_buurt + var_residual

variance_decomposition <- tibble::tibble(
  level = c("Buurt", "Residual", "Total"),
  variance = c(var_buurt, var_residual, total_var),
  pct_variance = c(
    100 * var_buurt / total_var,
    100 * var_residual / total_var,
    100
  )
)

message(glue::glue(
  "  ICC (buurt): {round(icc_result$ICC_adjusted, 4)} ({round(icc_result$ICC_adjusted * 100, 1)}% of variance between neighborhoods)"
))

return(list(
  icc = icc_result,
  variance_decomposition = variance_decomposition
))
}


#' Run Model Diagnostics
#'
#' Performs diagnostic checks on the final model.
#'
#' @param model A fitted lmer model
#' @param data The analysis dataset
#' @return A list with diagnostic results
run_diagnostics <- function(model, data) {

message("Running model diagnostics...")

# VIF (using OLS equivalent)
message("  Calculating VIF...")
ols_formula <- DV_single ~ b_perc_low40_hh + age + sex + education +
  b_pop_dens + b_pop_over_65 + b_pop_nonwest +
  b_perc_low_inc_hh + b_perc_soc_min_hh

ols_fit <- lm(ols_formula, data = data)
vif_values <- car::vif(ols_fit)

high_vif <- vif_values[vif_values > 5]
if (length(high_vif) > 0) {
  warning("High VIF detected: ", paste(names(high_vif), collapse = ", "))
}

# Residual statistics
message("  Analyzing residuals...")
resids <- residuals(model)
resid_stats <- tibble::tibble(
  mean = mean(resids),
  sd = sd(resids),
  skewness = moments::skewness(resids),
  kurtosis = moments::kurtosis(resids)
)

# Random effects
message("  Analyzing random effects...")
re <- lme4::ranef(model)$buurt_id[, 1]
re_stats <- tibble::tibble(
  mean = mean(re),
  sd = sd(re),
  min = min(re),
  max = max(re)
)

diagnostics <- list(
  vif = vif_values,
  high_vif = high_vif,
  residual_stats = resid_stats,
  random_effect_stats = re_stats,
  n_clusters = length(unique(data$buurt_id)),
  n_obs = nrow(data)
)

message("  Diagnostics complete")

return(diagnostics)
}


#' Run Sensitivity Analyses
#'
#' Runs robustness checks with alternative specifications.
#'
#' @param data Full merged dataset
#' @return A tibble summarizing sensitivity results
run_sensitivity <- function(data) {

message("Running sensitivity analyses...")

results <- tibble::tibble(
  specification = character(),
  n = integer(),
  coefficient = numeric(),
  se = numeric(),
  significant = logical()
)

# Prepare analysis sample
analysis_vars <- c(
  "DV_single", "age", "sex", "education", "employment_status",
  "occupation", "born_in_nl", "b_perc_low40_hh", "b_pop_dens",
  "b_pop_over_65", "b_pop_nonwest", "b_perc_low_inc_hh",
  "b_perc_soc_min_hh", "buurt_id", "b_pop_total",
  "DV_2item_scaled", "DV_3item_scaled"
)

base_data <- data %>%
  dplyr::select(dplyr::any_of(analysis_vars)) %>%
  tidyr::drop_na()

# Base model
message("  Base model...")
m_base <- lme4::lmer(
  DV_single ~ b_perc_low40_hh + age + sex + education +
    employment_status + occupation +
    b_pop_dens + b_pop_over_65 + b_pop_nonwest +
    b_perc_low_inc_hh + b_perc_soc_min_hh +
    (1 | buurt_id),
  data = base_data
)

fe <- lme4::fixef(m_base)["b_perc_low40_hh"]
se <- sqrt(diag(vcov(m_base)))["b_perc_low40_hh"]

results <- results %>%
  dplyr::add_row(
    specification = "Base model",
    n = nrow(base_data),
    coefficient = fe,
    se = se,
    significant = abs(fe) > 1.96 * se
  )

# 2-item DV
if ("DV_2item_scaled" %in% names(base_data)) {
  message("  2-item composite DV...")
  m_2item <- lme4::lmer(
    DV_2item_scaled ~ b_perc_low40_hh + age + sex + education +
      employment_status + occupation +
      b_pop_dens + b_pop_over_65 + b_pop_nonwest +
      b_perc_low_inc_hh + b_perc_soc_min_hh +
      (1 | buurt_id),
    data = base_data
  )

  fe <- lme4::fixef(m_2item)["b_perc_low40_hh"]
  se <- sqrt(diag(vcov(m_2item)))["b_perc_low40_hh"]

  results <- results %>%
    dplyr::add_row(
      specification = "2-item composite DV",
      n = nrow(base_data),
      coefficient = fe,
      se = se,
      significant = abs(fe) > 1.96 * se
    )
}

# 3-item DV
if ("DV_3item_scaled" %in% names(base_data)) {
  message("  3-item composite DV...")
  m_3item <- lme4::lmer(
    DV_3item_scaled ~ b_perc_low40_hh + age + sex + education +
      employment_status + occupation +
      b_pop_dens + b_pop_over_65 + b_pop_nonwest +
      b_perc_low_inc_hh + b_perc_soc_min_hh +
      (1 | buurt_id),
    data = base_data
  )

  fe <- lme4::fixef(m_3item)["b_perc_low40_hh"]
  se <- sqrt(diag(vcov(m_3item)))["b_perc_low40_hh"]

  results <- results %>%
    dplyr::add_row(
      specification = "3-item composite DV",
      n = nrow(base_data),
      coefficient = fe,
      se = se,
      significant = abs(fe) > 1.96 * se
    )
}

# Dutch-born only
message("  Dutch-born only...")
dutch_data <- data %>%
  dplyr::filter(born_in_nl == 1) %>%
  dplyr::select(dplyr::any_of(analysis_vars)) %>%
  tidyr::drop_na()

if (nrow(dutch_data) > 100) {
  m_dutch <- lme4::lmer(
    DV_single ~ b_perc_low40_hh + age + sex + education +
      employment_status + occupation +
      b_pop_dens + b_pop_over_65 + b_pop_nonwest +
      b_perc_low_inc_hh + b_perc_soc_min_hh +
      (1 | buurt_id),
    data = dutch_data
  )

  fe <- lme4::fixef(m_dutch)["b_perc_low40_hh"]
  se <- sqrt(diag(vcov(m_dutch)))["b_perc_low40_hh"]

  results <- results %>%
    dplyr::add_row(
      specification = "Dutch-born only",
      n = nrow(dutch_data),
      coefficient = fe,
      se = se,
      significant = abs(fe) > 1.96 * se
    )
}

  # Income ratio model (alternative inequality measure)
  if ("b_income_ratio" %in% names(data)) {
    message("  Income ratio model...")
    ratio_data <- data %>%
      dplyr::select(dplyr::any_of(c(analysis_vars, "b_income_ratio"))) %>%
      dplyr::filter(!is.na(b_income_ratio)) %>%
      tidyr::drop_na()

    if (nrow(ratio_data) > 100) {
      m_ratio <- lme4::lmer(
        DV_single ~ b_income_ratio + age + sex + education +
          employment_status + occupation +
          b_pop_dens + b_pop_over_65 + b_pop_nonwest +
          b_perc_low_inc_hh + b_perc_soc_min_hh +
          (1 | buurt_id),
        data = ratio_data
      )

      fe <- lme4::fixef(m_ratio)["b_income_ratio"]
      se <- sqrt(diag(vcov(m_ratio)))["b_income_ratio"]

      results <- results %>%
        dplyr::add_row(
          specification = "Income ratio (high/low)",
          n = nrow(ratio_data),
          coefficient = fe,
          se = se,
          significant = abs(fe) > 1.96 * se
        )
    }
  }

  message("  Sensitivity analyses complete")

  return(results)
}


#' Fit True Nested Random Effects Models (R-Specific)
#'
#' Fits models with proper nested random intercepts using lme4.
#' This is an R-specific robustness analysis that Python cannot replicate
#' due to statsmodels limitations with crossed/nested random effects.
#'
#' Structure: (1|gemeente_id) + (1|wijk_id) + (1|buurt_id)
#'
#' @param data Analysis dataset with buurt_id, wijk_id, gemeente_id
#' @return A list containing:
#'   - models: List of fitted lmer models (m0-m3)
#'   - variance_decomposition: Tibble with ICC at each level
fit_nested_random_effects <- function(data) {

  message("Fitting true nested random effects models (R-specific)...")
  message("  Structure: (1|gemeente_id) + (1|wijk_id) + (1|buurt_id)")

  # Check required columns
  required <- c("buurt_id", "wijk_id", "gemeente_id", "DV_single")
  missing <- setdiff(required, names(data))
  if (length(missing) > 0) {
    warning(glue::glue("Missing required columns: {paste(missing, collapse = ', ')}"))
    return(NULL)
  }

  # Ensure factors for random effects
  data <- data %>%
    dplyr::mutate(
      buurt_id = as.factor(buurt_id),
      wijk_id = as.factor(wijk_id),
      gemeente_id = as.factor(gemeente_id)
    )

  # Prepare analysis sample
  analysis_vars <- c(
    "DV_single", "age", "sex", "education", "employment_status",
    "occupation", "born_in_nl", "b_perc_low40_hh", "b_pop_dens",
    "b_pop_over_65", "b_pop_nonwest", "b_perc_low_inc_hh",
    "b_perc_soc_min_hh", "buurt_id", "wijk_id", "gemeente_id"
  )

  nested_data <- data %>%
    dplyr::select(dplyr::any_of(analysis_vars)) %>%
    tidyr::drop_na()

  message(glue::glue("  Analysis sample: {nrow(nested_data)} observations"))

  # M0: Empty nested model
  message("  Fitting nested m0 (empty model)...")
  m0_nested <- lme4::lmer(
    DV_single ~ 1 + (1 | gemeente_id) + (1 | wijk_id) + (1 | buurt_id),
    data = nested_data,
    REML = TRUE,
    control = lme4::lmerControl(optimizer = "bobyqa")
  )

  # M1: + Key predictor
  message("  Fitting nested m1 (+ key predictor)...")
  m1_nested <- lme4::lmer(
    DV_single ~ b_perc_low40_hh +
      (1 | gemeente_id) + (1 | wijk_id) + (1 | buurt_id),
    data = nested_data,
    REML = TRUE
  )

  # M2: + Individual controls
  message("  Fitting nested m2 (+ individual controls)...")
  m2_nested <- lme4::lmer(
    DV_single ~ b_perc_low40_hh + age + sex + education +
      employment_status + occupation + born_in_nl +
      (1 | gemeente_id) + (1 | wijk_id) + (1 | buurt_id),
    data = nested_data,
    REML = TRUE
  )

  # M3: + Buurt controls
  message("  Fitting nested m3 (+ buurt controls)...")
  m3_nested <- lme4::lmer(
    DV_single ~ b_perc_low40_hh + age + sex + education +
      employment_status + occupation + born_in_nl +
      b_pop_dens + b_pop_over_65 + b_pop_nonwest +
      b_perc_low_inc_hh + b_perc_soc_min_hh +
      (1 | gemeente_id) + (1 | wijk_id) + (1 | buurt_id),
    data = nested_data,
    REML = TRUE
  )

  models <- list(
    m0_nested = m0_nested,
    m1_nested = m1_nested,
    m2_nested = m2_nested,
    m3_nested = m3_nested
  )

  # Calculate ICC at each level from empty model
  message("\n  Variance decomposition (from empty model):")
  vc <- as.data.frame(lme4::VarCorr(m0_nested))

  var_gemeente <- vc$vcov[vc$grp == "gemeente_id"]
  var_wijk <- vc$vcov[vc$grp == "wijk_id"]
  var_buurt <- vc$vcov[vc$grp == "buurt_id"]
  var_resid <- vc$vcov[vc$grp == "Residual"]
  var_total <- var_gemeente + var_wijk + var_buurt + var_resid

  icc_gemeente <- var_gemeente / var_total
  icc_wijk <- var_wijk / var_total
  icc_buurt <- var_buurt / var_total
  icc_resid <- var_resid / var_total

  message(glue::glue("    Gemeente: {round(100 * icc_gemeente, 2)}%"))
  message(glue::glue("    Wijk: {round(100 * icc_wijk, 2)}%"))
  message(glue::glue("    Buurt: {round(100 * icc_buurt, 2)}%"))
  message(glue::glue("    Residual (individual): {round(100 * icc_resid, 2)}%"))

  variance_decomposition <- tibble::tibble(
    level = c("Gemeente", "Wijk", "Buurt", "Residual", "Total"),
    variance = c(var_gemeente, var_wijk, var_buurt, var_resid, var_total),
    icc = c(icc_gemeente, icc_wijk, icc_buurt, icc_resid, 1.0),
    pct_variance = c(
      100 * icc_gemeente,
      100 * icc_wijk,
      100 * icc_buurt,
      100 * icc_resid,
      100
    )
  )

  # Key coefficient from full model
  fe_m3 <- lme4::fixef(m3_nested)["b_perc_low40_hh"]
  se_m3 <- sqrt(diag(vcov(m3_nested)))["b_perc_low40_hh"]
  message(glue::glue("\n  Key predictor (nested m3): {round(fe_m3, 3)} (SE = {round(se_m3, 3)})"))

  return(list(
    models = models,
    variance_decomposition = variance_decomposition,
    n_obs = nrow(nested_data),
    n_gemeente = length(unique(nested_data$gemeente_id)),
    n_wijk = length(unique(nested_data$wijk_id)),
    n_buurt = length(unique(nested_data$buurt_id))
  ))
}


#' Create Model Summary Table
#'
#' Creates a publication-ready regression table.
#'
#' @param models List of fitted models
#' @param output_path Path to save the table
#' @return A gt or modelsummary table object
create_model_table <- function(models, output_path = NULL) {

message("Creating model summary table...")

# Use modelsummary
table <- modelsummary::modelsummary(
  models,
  stars = c('*' = .05, '**' = .01, '***' = .001),
  coef_rename = c(
    "b_perc_low40_hh" = "% Low-income HH (buurt)",
    "age" = "Age (std)",
    "sexFemale" = "Female",
    "sexOther" = "Other gender",
    "education" = "Education (std)",
    "b_pop_dens" = "Population density",
    "b_pop_over_65" = "% Age 65+",
    "b_pop_nonwest" = "% Non-Western",
    "b_perc_low_inc_hh" = "% Low income HH",
    "b_perc_soc_min_hh" = "% Social minimum HH"
  ),
  gof_map = c("nobs", "aic", "bic"),
  output = if (!is.null(output_path)) output_path else "gt"
)

if (!is.null(output_path)) {
  message(glue::glue("  Table saved to: {output_path}"))
}

return(table)
}


#' Generate Analysis Report
#'
#' Creates a comprehensive summary of all analysis results.
#'
#' @param models List of fitted models
#' @param icc_results ICC and variance decomposition
#' @param diagnostics Diagnostic results
#' @param sensitivity Sensitivity analysis results
#' @param merge_validation Merge validation results
#' @return A list with all results formatted for reporting
generate_report <- function(models, icc_results, diagnostics, sensitivity, merge_validation) {

message("Generating analysis report...")

# Extract final model results
m3 <- models$m3_buurt_controls
fe <- lme4::fixef(m3)
se <- sqrt(diag(vcov(m3)))
ci_lower <- fe - 1.96 * se
ci_upper <- fe + 1.96 * se

fixed_effects <- tibble::tibble(
  term = names(fe),
  estimate = fe,
  se = se,
  ci_lower = ci_lower,
  ci_upper = ci_upper,
  significant = ci_lower > 0 | ci_upper < 0
)

# Model comparison
model_comparison <- tibble::tibble(
  model = names(models),
  n = sapply(models, function(m) nrow(m@frame)),
  aic = sapply(models, AIC),
  bic = sapply(models, BIC),
  loglik = sapply(models, function(m) as.numeric(logLik(m)))
)

report <- list(
  # Data summary
  n_obs = diagnostics$n_obs,
  n_clusters = diagnostics$n_clusters,

  # Merge quality
  merge_validation = merge_validation,

  # ICC
  icc = icc_results$icc$ICC_adjusted,
  variance_decomposition = icc_results$variance_decomposition,

  # Model results
  model_comparison = model_comparison,
  fixed_effects = fixed_effects,

  # Key finding
  key_coef = fe["b_perc_low40_hh"],
  key_se = se["b_perc_low40_hh"],
  key_ci = c(ci_lower["b_perc_low40_hh"], ci_upper["b_perc_low40_hh"]),

  # Diagnostics
  vif = diagnostics$vif,
  residual_stats = diagnostics$residual_stats,

  # Sensitivity
  sensitivity = sensitivity
)

message("  Report generated")

return(report)
}


#' Test H3: Cross-Level Interaction (Individual Income Moderation)
#'
#' Tests whether individual income (proxied by wealth_index) moderates the
#' effect of neighborhood poverty concentration on redistribution preferences.
#'
#' H3 predicts: The effect of neighborhood inequality is weaker for higher-income
#' individuals (negative interaction).
#'
#' @param data Analysis dataset with wealth_index variable
#' @return A list with H3 test results
test_h3_cross_level_interaction <- function(data) {

  message("\n", paste(rep("=", 60), collapse = ""))
  message("H3 TEST: Cross-Level Interaction (Individual Income Moderation)")
  message(paste(rep("=", 60), collapse = ""))

  # Check required variables
  required_vars <- c("DV_single", "b_perc_low40_hh", "wealth_index", "buurt_id",
                     "age", "sex", "education", "employment_status", "born_in_nl")

  missing_vars <- setdiff(required_vars, names(data))
  if (length(missing_vars) > 0) {
    message("  ERROR: Missing required variables: ", paste(missing_vars, collapse = ", "))
    return(list(error = paste("Missing variables:", paste(missing_vars, collapse = ", "))))
  }

  # Prepare analysis data
  buurt_controls <- c("b_pop_dens", "b_pop_over_65", "b_pop_nonwest",
                      "b_perc_low_inc_hh", "b_perc_soc_min_hh")
  buurt_controls <- intersect(buurt_controls, names(data))

  all_vars <- c(required_vars, buurt_controls)
  h3_data <- data %>%
    dplyr::select(dplyr::all_of(all_vars)) %>%
    tidyr::drop_na()

  message(glue::glue("\n  Sample size: N = {nrow(h3_data)}"))
  message(glue::glue("  Wealth index range: {min(h3_data$wealth_index)} - {max(h3_data$wealth_index)}"))
  message(glue::glue("  Wealth index mean: {round(mean(h3_data$wealth_index), 2)}"))

  results <- list()

  # Model 1: Main effects only (baseline)
  message("\n  Model 1: Main effects only...")
  tryCatch({
    m1 <- lme4::lmer(
      DV_single ~ b_perc_low40_hh + wealth_index + age + sex + education +
        employment_status + born_in_nl +
        b_pop_dens + b_pop_over_65 + b_pop_nonwest +
        b_perc_low_inc_hh + b_perc_soc_min_hh +
        (1 | buurt_id),
      data = h3_data,
      REML = TRUE
    )

    fe <- lme4::fixef(m1)
    se <- sqrt(diag(vcov(m1)))

    results$m1_neighborhood <- list(coef = fe["b_perc_low40_hh"], se = se["b_perc_low40_hh"])
    results$m1_wealth <- list(coef = fe["wealth_index"], se = se["wealth_index"])

    message(glue::glue("    Neighborhood effect: {round(results$m1_neighborhood$coef, 3)} (SE={round(results$m1_neighborhood$se, 3)})"))
    message(glue::glue("    Wealth effect: {round(results$m1_wealth$coef, 3)} (SE={round(results$m1_wealth$se, 3)})"))
  }, error = function(e) {
    message("    Error: ", e$message)
    return(list(error = e$message))
  })

  # Model 2: With cross-level interaction
  message("\n  Model 2: With cross-level interaction (H3 test)...")
  tryCatch({
    m2 <- lme4::lmer(
      DV_single ~ b_perc_low40_hh * wealth_index + age + sex + education +
        employment_status + born_in_nl +
        b_pop_dens + b_pop_over_65 + b_pop_nonwest +
        b_perc_low_inc_hh + b_perc_soc_min_hh +
        (1 | buurt_id),
      data = h3_data,
      REML = TRUE
    )

    fe <- lme4::fixef(m2)
    se <- sqrt(diag(vcov(m2)))

    main_effect <- fe["b_perc_low40_hh"]
    main_se <- se["b_perc_low40_hh"]
    interaction <- fe["b_perc_low40_hh:wealth_index"]
    interaction_se <- se["b_perc_low40_hh:wealth_index"]

    results$main_effect <- list(coef = main_effect, se = main_se)
    results$interaction_effect <- list(coef = interaction, se = interaction_se)

    # Significance tests
    main_z <- abs(main_effect / main_se)
    interaction_z <- abs(interaction / interaction_se)
    main_sig <- main_z > 1.96
    interaction_sig <- interaction_z > 1.96

    message(glue::glue("    Main effect (b_perc_low40_hh): {round(main_effect, 3)} (SE={round(main_se, 3)})"))
    message(glue::glue("      z = {round(main_z, 2)}, p {ifelse(main_sig, '<', '>')} 0.05"))
    message(glue::glue("    Interaction (neighborhood x wealth): {round(interaction, 3)} (SE={round(interaction_se, 3)})"))
    message(glue::glue("      z = {round(interaction_z, 2)}, p {ifelse(interaction_sig, '<', '>')} 0.05"))

    # Simple slopes: effect of neighborhood at different wealth levels
    message("\n  Simple slopes (neighborhood effect at different wealth levels):")
    wealth_levels <- 0:4
    simple_slopes <- sapply(wealth_levels, function(w) main_effect + interaction * w)
    names(simple_slopes) <- paste0("wealth_", wealth_levels)

    for (w in wealth_levels) {
      message(glue::glue("    Wealth = {w}: neighborhood effect = {round(simple_slopes[w + 1], 3)}"))
    }
    results$simple_slopes <- simple_slopes

    # Interpretation
    message("\n  ", paste(rep("-", 56), collapse = ""))
    message("  INTERPRETATION:")

    if (interaction_sig) {
      if (interaction > 0) {
        interpretation <- paste(
          "H3 SUPPORTED (opposite direction): The positive interaction suggests",
          "that the neighborhood poverty effect is STRONGER for higher-income",
          "individuals. This contradicts the hypothesis that higher income",
          "buffers against neighborhood effects."
        )
      } else {
        interpretation <- paste(
          "H3 SUPPORTED: The negative interaction confirms that the neighborhood",
          "poverty effect is WEAKER for higher-income individuals. Higher income",
          "appears to buffer against neighborhood context effects on redistribution",
          "preferences."
        )
      }
    } else {
      interpretation <- paste(
        "H3 NOT SUPPORTED: The interaction between neighborhood poverty and",
        "individual wealth is not statistically significant. The effect of",
        "neighborhood composition on redistribution preferences does not",
        "significantly vary by individual income level."
      )
    }

    results$interpretation <- interpretation
    results$h3_supported <- interaction_sig
    results$n_obs <- nrow(h3_data)

    message(glue::glue("  {interpretation}"))
    message("  ", paste(rep("-", 56), collapse = ""))

  }, error = function(e) {
    message("    Error: ", e$message)
    results$error <- e$message
  })

  return(results)
}
