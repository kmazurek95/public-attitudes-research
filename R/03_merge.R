# =============================================================================
# 03_merge.R - Data Merging and Validation Functions
# =============================================================================
# Functions to merge survey and administrative data, with validation.
# =============================================================================

#' Merge Survey with Admin Data
#'
#' Performs left joins to add buurt, wijk, and gemeente context to survey data.
#'
#' @param survey Survey data with geo IDs
#' @param admin_list List with buurt, wijk, gemeente tibbles
#' @return Merged dataset
merge_survey_admin <- function(survey, admin_list) {

message("Merging survey with administrative data...")

# Sequential left joins
merged <- survey %>%
  dplyr::left_join(admin_list$buurt, by = "buurt_id") %>%
  dplyr::left_join(admin_list$wijk, by = "wijk_id") %>%
  dplyr::left_join(admin_list$gemeente, by = "gemeente_id")

message(glue::glue("  Merged dataset: {nrow(merged)} rows, {ncol(merged)} columns"))

return(merged)
}


#' Validate Merge Quality
#'
#' Checks merge success rates at each geographic level.
#'
#' @param data Merged dataset
#' @return A tibble with validation statistics
validate_merge <- function(data) {

message("Validating merge quality...")

# Calculate match rates
n_total <- nrow(data)

validation <- tibble::tibble(
  level = c("Buurt", "Wijk", "Gemeente"),
  indicator_var = c("b_pop_total", "w_pop_total", "g_pop_total"),
  n_matched = c(
    sum(!is.na(data$b_pop_total)),
    sum(!is.na(data$w_pop_total)),
    sum(!is.na(data$g_pop_total))
  ),
  n_missing = n_total - n_matched,
  pct_matched = round(100 * n_matched / n_total, 1)
)

# Print summary
message("\n  Merge validation summary:")
message("  -------------------------")
for (i in seq_len(nrow(validation))) {
  message(glue::glue(
    "  {validation$level[i]}: {validation$n_matched[i]} of {n_total} matched ({validation$pct_matched[i]}%)"
  ))
}

# Check for issues
if (any(validation$pct_matched < 80)) {
  warning("Some geographic levels have < 80% match rate!")
}

return(validation)
}


#' Analyze Missingness Patterns
#'
#' Creates a detailed missingness report.
#'
#' @param data Merged dataset
#' @return A list with missingness statistics
analyze_missingness <- function(data) {

message("Analyzing missingness patterns...")

# Cross-tabulate geographic missingness
geo_pattern <- data %>%
  dplyr::mutate(
    has_buurt = !is.na(b_pop_total),
    has_wijk = !is.na(w_pop_total),
    has_gemeente = !is.na(g_pop_total)
  ) %>%
  dplyr::count(has_buurt, has_wijk, has_gemeente) %>%
  dplyr::arrange(dplyr::desc(n))

# Variable-level missingness
var_missingness <- data %>%
  dplyr::summarise(
    dplyr::across(
      dplyr::everything(),
      ~ sum(is.na(.)) / dplyr::n()
    )
  ) %>%
  tidyr::pivot_longer(
    dplyr::everything(),
    names_to = "variable",
    values_to = "pct_missing"
  ) %>%
  dplyr::filter(pct_missing > 0) %>%
  dplyr::arrange(dplyr::desc(pct_missing))

# Key predictors
key_vars <- c("DV_single", "age", "sex", "education",
              "b_perc_low40_hh", "w_perc_low40_hh", "g_perc_low40_hh")

key_missingness <- data %>%
  dplyr::select(dplyr::any_of(key_vars)) %>%
  dplyr::summarise(
    dplyr::across(dplyr::everything(), ~ sum(is.na(.)))
  )

message("  Geographic missingness patterns:")
print(geo_pattern)

return(list(
  geo_pattern = geo_pattern,
  var_missingness = var_missingness,
  key_missingness = key_missingness
))
}


#' Compare Matched vs Unmatched Cases
#'
#' Tests for systematic differences between matched and unmatched observations.
#'
#' @param data Merged dataset
#' @return A tibble with comparison statistics
compare_matched_unmatched <- function(data) {

message("Comparing matched vs unmatched cases...")

data <- data %>%
  dplyr::mutate(matched_buurt = !is.na(b_pop_total))

comparison <- data %>%
  dplyr::group_by(matched_buurt) %>%
  dplyr::summarise(
    n = dplyr::n(),
    mean_dv = mean(DV_single, na.rm = TRUE),
    sd_dv = sd(DV_single, na.rm = TRUE),
    mean_age = mean(age_raw, na.rm = TRUE),
    pct_female = 100 * mean(sex == "Female", na.rm = TRUE),
    mean_education = mean(educyrs, na.rm = TRUE),
    .groups = "drop"
  )

# T-test for DV difference
if (sum(!is.na(data$DV_single) & data$matched_buurt) > 0 &&
    sum(!is.na(data$DV_single) & !data$matched_buurt) > 0) {
  ttest <- t.test(DV_single ~ matched_buurt, data = data)
  comparison$ttest_pvalue <- ttest$p.value
} else {
  comparison$ttest_pvalue <- NA
}

message("\n  Matched (TRUE) vs Unmatched (FALSE):")
print(comparison)

return(comparison)
}


#' Create Analysis Sample
#'
#' Creates the final analysis sample with complete cases for key variables.
#'
#' @param data Full merged dataset
#' @param include_occupation Whether to require occupation (drops more cases)
#' @return Analysis-ready dataset
create_analysis_sample <- function(data, include_occupation = TRUE) {

message("Creating analysis sample...")

# Define required variables
required_vars <- c(
  "DV_single", "age", "sex", "education", "employment_status",
  "born_in_nl", "b_perc_low40_hh", "b_pop_total", "b_pop_over_65",
  "b_pop_nonwest", "b_perc_low_inc_hh", "b_pop_dens", "b_perc_soc_min_hh",
  "buurt_id"
)

if (include_occupation) {
  required_vars <- c(required_vars, "occupation")
}

# Select and filter
analysis_data <- data %>%
  dplyr::select(dplyr::all_of(required_vars)) %>%
  tidyr::drop_na()

message(glue::glue(
  "  Analysis sample: {nrow(analysis_data)} of {nrow(data)} observations ({round(100 * nrow(analysis_data) / nrow(data), 1)}%)"
))
message(glue::glue(
  "  Unique buurten: {length(unique(analysis_data$buurt_id))}"
))

return(analysis_data)
}
