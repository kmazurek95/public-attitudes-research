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
    # Pad Buurtcode to a robust 8-digit string.
    # BUG (fixed): the previous case_when applied paste0()/as.character() to the raw
    # numeric Buurtcode, which R renders in scientific notation for round numbers
    # (400000 -> "4e+05", 17000000 -> "1.7e+07"). That produced malformed ids
    # ("004e+05", "1.7e+07") and spurious gemeente codes ("004e", "1.7e"), fragmenting
    # the geography. sprintf("%08d", <integer>) is width-robust and notation-proof.
    buurt_id = dplyr::if_else(
      is.na(Buurtcode),
      NA_character_,
      sprintf("%08d", as.integer(round(Buurtcode)))
    ),
    # Wijk = first 6 digits, Gemeente = first 4 digits. Admin BU/WK/GM codes share this
    # 8/6/4-digit basis (BU16800000 -> 16800000, WK168000 -> 168000, GM1680 -> 1680).
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
) %>%

# Wealth index from asset ownership (questionnaire B12 = Stata b14_1:b14_5)
# Sum of owned asset types: real estate, further real estate, savings, stocks (0-4)
# asset_none (b14_5) codes "none of these" and is excluded from the sum
dplyr::mutate(
  wealth_index = dplyr::case_when(
    is.na(asset_realestate) | is.na(asset_savings) ~ NA_real_,
    TRUE ~ as.numeric(asset_realestate) + as.numeric(asset_realestate2) +
           as.numeric(asset_savings)    + as.numeric(asset_stocks)
  )
)

message(glue::glue("  Recoded {nrow(data)} observations"))

return(data)
}


#' Create Inequality Indices
#'
#' Creates a composite inequality measure from the buurt-level low40 and high20
#' percentages, used as an alternative key predictor in the sensitivity analyses.
#'
#' @param data Data with b_perc_low40_hh and b_perc_high20_hh columns
#' @return Data with b_income_ratio: high20 / low40 (higher = more affluent
#'   relative to poor)
create_inequality_indices <- function(data) {

  message("Creating inequality indices...")

  data <- data %>%
    dplyr::mutate(
      b_income_ratio = b_perc_high20_hh / (abs(b_perc_low40_hh) + 0.01)
    )

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

# Buurt-level context variables entering the models
context_vars <- c(
  "b_perc_low40_hh", "b_pop_total", "b_pop_over_65", "b_pop_nonwest",
  "b_perc_low_inc_hh", "b_pop_dens", "b_perc_soc_min_hh"
)

data <- data %>%
  dplyr::mutate(
    dplyr::across(dplyr::all_of(context_vars), ~ as.vector(scale(.)))
  )

message(glue::glue("  Standardized {length(context_vars)} context variables"))

return(data)
}
