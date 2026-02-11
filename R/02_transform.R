# =============================================================================
# 02_transform.R - Data Transformation Functions
# =============================================================================
# Functions to transform raw data into analysis-ready format.
# Handles geocode creation, variable recoding, and standardization.
# =============================================================================

#' Create Geographic Identifiers
#'
#' Creates standardized geographic codes from Buurtcode for merging.
#' Buurt = 8 digits, Wijk = first 6, Gemeente = first 4.
#'
#' @param survey Survey data with Buurtcode column
#' @return Survey data with buurt_id, wijk_id, gemeente_id columns
create_geo_ids <- function(survey) {

message("Creating geographic identifiers...")

survey <- survey %>%
  dplyr::mutate(
    # Pad Buurtcode to 8 digits with leading zeros
    buurt_id = dplyr::case_when(
      is.na(Buurtcode) ~ NA_character_,
      Buurtcode > 9999 & Buurtcode < 100000 ~ paste0("000", Buurtcode),
      Buurtcode > 99999 & Buurtcode < 1000000 ~ paste0("00", Buurtcode),
      Buurtcode > 999999 & Buurtcode < 10000000 ~ paste0("0", Buurtcode),
      Buurtcode > 9999999 ~ as.character(Buurtcode),
      TRUE ~ NA_character_
    ),
    # Extract wijk (first 6 digits) and gemeente (first 4 digits)
    wijk_id = substr(buurt_id, 1, 6),
    gemeente_id = substr(buurt_id, 1, 4)
  )

# Validation
n_valid <- sum(!is.na(survey$buurt_id))
message(glue::glue("  Created geo IDs for {n_valid} of {nrow(survey)} respondents"))

return(survey)
}


#' Prepare Admin Data by Geographic Level
#'
#' Splits admin data into separate tibbles by level with appropriate prefixes.
#'
#' @param admin Admin data with region_type column
#' @return A list with buurt, wijk, gemeente tibbles
prepare_admin_by_level <- function(admin) {

message("Preparing admin data by geographic level...")

# Extract geographic code from the code column (strip 2-letter prefix)
# BU12345678 -> 12345678, WK123456 -> 123456, GM1234 -> 1234

# Buurt level
buurt <- admin %>%
  dplyr::filter(region_type == "Buurt") %>%
  dplyr::mutate(buurt_id = substr(code, 3, 10)) %>%
  dplyr::rename_with(~ paste0("b_", .), -buurt_id)

# Wijk level
wijk <- admin %>%
  dplyr::filter(region_type == "Wijk") %>%
  dplyr::mutate(wijk_id = substr(code, 3, 8)) %>%
  dplyr::rename_with(~ paste0("w_", .), -wijk_id)

# Gemeente level
gemeente <- admin %>%
  dplyr::filter(region_type == "Gemeente") %>%
  dplyr::mutate(gemeente_id = substr(code, 3, 6)) %>%
  dplyr::rename_with(~ paste0("g_", .), -gemeente_id)

message(glue::glue("  Buurt: {nrow(buurt)} units"))
message(glue::glue("  Wijk: {nrow(wijk)} units"))
message(glue::glue("  Gemeente: {nrow(gemeente)} units"))

return(list(
  buurt = buurt,
  wijk = wijk,
  gemeente = gemeente
))
}


#' Recode Survey Variables
#'
#' Recodes individual-level survey variables for analysis.
#'
#' @param data Merged survey data
#' @return Data with recoded variables
recode_survey_variables <- function(data) {

message("Recoding survey variables...")

data <- data %>%
  # Filter out invalid DV responses (8 = missing/refused)
  dplyr::filter(
    red_inc_diff != 8 | is.na(red_inc_diff),
    gov_int != 8 | is.na(gov_int),
    union_pref != 8 | is.na(union_pref)
  ) %>%

  # Create dependent variable transformations
  dplyr::mutate(
    # Single item scaled 0-100
    DV_single = 100 * (red_inc_diff - 1) / (7 - 1),

    # 2-item composite (gov_int + red_inc_diff)
    DV_2item = (gov_int + red_inc_diff) / 2,
    DV_2item_scaled = 100 * (DV_2item - 1) / (7 - 1),

    # 3-item composite (gov_int + red_inc_diff + union_pref)
    DV_3item = (gov_int + red_inc_diff + union_pref) / 3,
    DV_3item_scaled = 100 * (DV_3item - 1) / (7 - 1)
  ) %>%

  # Recode sex
  dplyr::mutate(
    sex = dplyr::case_when(
      sex == 1 ~ "Male",
      sex == 2 ~ "Female",
      sex == 3 ~ "Other",
      TRUE ~ NA_character_
    ),
    sex = factor(sex, levels = c("Male", "Female", "Other"))
  ) %>%

  # Calculate and standardize age (survey conducted in 2017)
  dplyr::mutate(
    age_raw = 2017 - birth_year,
    age = as.vector(scale(age_raw))
  ) %>%

  # Standardize education
dplyr::mutate(
  education = as.vector(scale(educyrs))
) %>%

# Recode employment status
dplyr::mutate(
  employment_status = dplyr::case_when(
    work_status == 1 ~ "Employed",
    work_status == 2 ~ "Student",
    work_status == 3 ~ "Unemployed (active)",
    work_status == 4 ~ "Unemployed (inactive)",
    work_status == 5 ~ "Disabled",
    work_status == 6 ~ "Retired",
    work_status == 7 ~ "Military/Service",
    work_status == 8 ~ "Homemaker",
    TRUE ~ NA_character_
  ),
  employment_status = factor(employment_status)
) %>%

# Recode occupation
dplyr::mutate(
  occupation = dplyr::case_when(
    work_type == 1 ~ "Modern professional",
    work_type == 2 ~ "Clerical/intermediate",
    work_type == 3 ~ "Senior manager",
    work_type == 4 ~ "Technical/craft",
    work_type == 5 ~ "Semi-routine",
    work_type == 6 ~ "Routine",
    work_type == 7 ~ "Junior manager",
    work_type == 8 ~ "Traditional professional",
    TRUE ~ NA_character_
  ),
  occupation = factor(occupation)
)

message(glue::glue("  Recoded {nrow(data)} observations"))

return(data)
}


#' Create Inequality Indices
#'
#' Creates composite inequality measures from low40 and high20 percentages.
#' This matches the Python implementation for pipeline alignment.
#'
#' @param data Data with perc_low40_hh and perc_high20_hh columns at each level
#' @return Data with added inequality indices:
#'   - income_polarization: sum of low40 + high20 (higher = more at extremes)
#'   - income_ratio: high20 / low40 (higher = more affluent relative to poor)
create_inequality_indices <- function(data) {

  message("Creating inequality indices...")

  # Buurt level
  if (all(c("b_perc_low40_hh", "b_perc_high20_hh") %in% names(data))) {
    data <- data %>%
      dplyr::mutate(
        # Income polarization: Higher when both extremes are large
        b_income_polarization = b_perc_low40_hh + b_perc_high20_hh,
        # Income ratio: Higher = more affluent relative to poor
        b_income_ratio = b_perc_high20_hh / (abs(b_perc_low40_hh) + 0.01)
      )
    message("  Created buurt-level inequality indices")
  }

  # Wijk level
  if (all(c("w_perc_low40_hh", "w_perc_high20_hh") %in% names(data))) {
    data <- data %>%
      dplyr::mutate(
        w_income_polarization = w_perc_low40_hh + w_perc_high20_hh,
        w_income_ratio = w_perc_high20_hh / (abs(w_perc_low40_hh) + 0.01)
      )
    message("  Created wijk-level inequality indices")
  }

  # Gemeente level
  if (all(c("g_perc_low40_hh", "g_perc_high20_hh") %in% names(data))) {
    data <- data %>%
      dplyr::mutate(
        g_income_polarization = g_perc_low40_hh + g_perc_high20_hh,
        g_income_ratio = g_perc_high20_hh / (abs(g_perc_low40_hh) + 0.01)
      )
    message("  Created gemeente-level inequality indices")
  }

  return(data)
}


#' Standardize Context Variables
#'
#' Standardizes (z-scores) the neighborhood-level context variables.
#'
#' @param data Merged data with context variables
#' @return Data with standardized context variables
standardize_context_vars <- function(data) {

message("Standardizing context variables...")

# Variables to standardize (all numeric context vars)
context_vars <- c(
  "b_perc_low40_hh", "b_pop_total", "b_pop_over_65", "b_pop_nonwest",
  "b_avg_inc_recip", "b_perc_low_inc_hh", "b_pop_dens", "b_perc_soc_min_hh",
  "w_perc_low40_hh", "w_pop_total", "w_pop_over_65", "w_pop_nonwest",
  "w_avg_inc_recip", "w_perc_low_inc_hh", "w_pop_dens", "w_perc_soc_min_hh",
  "g_perc_low40_hh", "g_pop_total", "g_pop_over_65", "g_pop_nonwest",
  "g_avg_inc_recip", "g_perc_low_inc_hh", "g_pop_dens", "g_perc_soc_min_hh"
)

# Only standardize vars that exist in data AND are numeric
existing_vars <- intersect(context_vars, names(data))
numeric_vars <- existing_vars[sapply(data[existing_vars], is.numeric)]

if (length(numeric_vars) < length(existing_vars)) {
  non_numeric <- setdiff(existing_vars, numeric_vars)
  warning(glue::glue("Skipping non-numeric variables: {paste(non_numeric, collapse = ', ')}"))
}

data <- data %>%
  dplyr::mutate(
    dplyr::across(
      dplyr::all_of(numeric_vars),
      ~ as.vector(scale(.)),
      .names = "{.col}"
    )
  )

message(glue::glue("  Standardized {length(numeric_vars)} context variables"))

return(data)
}
