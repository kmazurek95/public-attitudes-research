# =============================================================================
# 01_extract.R - Data Extraction Functions
# =============================================================================
# Functions to load raw data from source files or APIs.
# Each function returns a clean tibble ready for transformation.
# =============================================================================

# -----------------------------------------------------------------------------
# CBS API DATA COLLECTION
# -----------------------------------------------------------------------------

#' Download CBS Neighborhood Indicators from API
#'
#' Downloads the "Kerncijfers wijken en buurten" dataset from CBS StatLine.
#' This contains socioeconomic indicators at buurt/wijk/gemeente levels.
#'
#' @param table_id CBS table ID (default: "84286NED" for 2018 data)
#' @param year Year filter (used in Perioden column)
#' @param save_path Optional path to save the downloaded data
#' @return A tibble with CBS indicators
download_cbs_data <- function(table_id = "84286NED",
                              year = "2018",
                              save_path = NULL) {

  message("Downloading CBS data from StatLine API...")
  message(glue::glue("  Table: {table_id}"))

  # Check if cbsodataR is available

if (!requireNamespace("cbsodataR", quietly = TRUE)) {
  stop("Package 'cbsodataR' is required. Install with: install.packages('cbsodataR')")
}

# Download full dataset
cbs_raw <- cbsodataR::cbs_get_data(table_id)

message(glue::glue("  Downloaded {nrow(cbs_raw)} rows, {ncol(cbs_raw)} columns"))

# Get column names to find the right ones
col_names <- names(cbs_raw)

# Helper function to find column by partial match
find_col <- function(pattern, cols) {
  matches <- grep(pattern, cols, value = TRUE, ignore.case = TRUE)
  if (length(matches) > 0) matches[1] else NA_character_
}

# Build rename mapping dynamically
# This handles variations in CBS column naming across years
rename_map <- c(
  "code" = find_col("^Regio", col_names),
  "municipality" = find_col("Gemeentenaam", col_names),
  "region_type" = find_col("SoortRegio", col_names),
  "pop_total" = find_col("AantalInwoners", col_names),
  "pop_over_65" = find_col("65JaarOfOuder", col_names),
  "pop_west" = find_col("WestersTotaal|WesterseMigratwordenHerkom", col_names),
  "pop_nonwest" = find_col("NietWestersTotaal|NietWesterseMigrat", col_names),
  "pop_dens" = find_col("Bevolkingsdichtheid", col_names),
  "avg_home_value" = find_col("GemiddeldeWOZWaarde", col_names),
  "avg_inc_recip" = find_col("GemiddeldInkomenPerInkomensontv", col_names),
  "avg_inc_pers" = find_col("GemiddeldInkomenPerInwoner", col_names),
  "perc_low40_pers" = find_col("PersonenInHuishoudensMetLaagInk", col_names),
  "perc_high20_pers" = find_col("PersonenInHuishoudensMetHoogInk", col_names),
  "perc_low40_hh" = find_col("HuishoudensMetLaagInkomen", col_names),
  "perc_high20_hh" = find_col("HuishoudensMetHoogInkomen", col_names),
  "perc_low_inc_hh" = find_col("HuishoudensOnderOfRondSociaalMin", col_names),
  "perc_soc_min_hh" = find_col("PersonenMetEenUitkering", col_names)
)

# Remove NAs from mapping
rename_map <- rename_map[!is.na(rename_map)]

# Select and rename available columns
cbs_clean <- cbs_raw %>%
  dplyr::select(dplyr::all_of(rename_map)) %>%
  dplyr::rename_with(~ names(rename_map)[match(., rename_map)])

# Clean region type labels
if ("region_type" %in% names(cbs_clean)) {
  cbs_clean <- cbs_clean %>%
    dplyr::mutate(
      region_type = dplyr::case_when(
        stringr::str_detect(region_type, "Buurt") ~ "Buurt",
        stringr::str_detect(region_type, "Wijk") ~ "Wijk",
        stringr::str_detect(region_type, "Gemeente") ~ "Gemeente",
        stringr::str_detect(region_type, "Land") ~ "Land",
        TRUE ~ region_type
      )
    )
}

message(glue::glue("  Cleaned to {ncol(cbs_clean)} key variables"))
message(glue::glue("  Variables found: {paste(names(cbs_clean), collapse = ', ')}"))

# Count by region type
counts <- cbs_clean %>%
  dplyr::count(region_type)
message("  Counts by region type:")
for (i in seq_len(nrow(counts))) {
  message(glue::glue("    {counts$region_type[i]}: {counts$n[i]}"))
}

# Optionally save
if (!is.null(save_path)) {
  readr::write_csv(cbs_clean, save_path)
  message(glue::glue("  Saved to: {save_path}"))
}

return(cbs_clean)
}


#' Get CBS Table Metadata
#'
#' Retrieves variable descriptions for a CBS table.
#'
#' @param table_id CBS table ID
#' @return A tibble with variable names and descriptions
get_cbs_metadata <- function(table_id = "84286NED") {

if (!requireNamespace("cbsodataR", quietly = TRUE)) {
  stop("Package 'cbsodataR' is required.")
}

if (!requireNamespace("dplyr", quietly = TRUE)) {
  stop("Package 'dplyr' is required.")
}

meta <- cbsodataR::cbs_get_meta(table_id)

# Extract DataProperties (variable descriptions)
vars <- dplyr::select(
  meta$DataProperties,
  position = Position,
  key = Key,
  title = Title,
  description = Description,
  unit = Unit
)

return(vars)
}


# -----------------------------------------------------------------------------
# LOCAL FILE LOADING
# -----------------------------------------------------------------------------

#' Load SCoRE Survey Data
#'
#' Reads the SCoRE survey data from Stata format and selects relevant variables.
#'
#' @param path Path to the .dta file
#' @return A tibble with survey responses
load_survey_data <- function(path = here::here("data", "raw", "score.dta")) {

message("Loading SCoRE survey data...")

# Read Stata file
survey_raw <- haven::read_dta(path)

# Select and rename variables
survey <- survey_raw %>%
  dplyr::select(
    # Dependent variables (attitudes)
    gov_int = a27_1,           # Government intervention attitude (1-7)
    red_inc_diff = a27_2,      # Reduce income differences (1-7)
    union_pref = a27_3,        # Union support (1-7)

    # Demographics
    sex = b01,
    birth_year = b02,
    educlvl = b03,
    educyrs = b04,

    # Employment
    work_status = b07,
    work_type = b09,

    # Migration background
    born_in_nl = b18,
    father_dutch = b20,
    mother_dutch = b21,

    # Geographic identifier
    Buurtcode,

    # Weights
    weight = weegfac,

    # Respondent ID
    respondent_id = respnr
  )

message(glue::glue("  Loaded {nrow(survey)} survey respondents"))

return(survey)
}


#' Load CBS Administrative Indicators
#'
#' Loads CBS neighborhood indicators from local file or downloads from API.
#'
#' @param path Path to local CSV file (if NULL, downloads from API)
#' @param use_api If TRUE, download fresh data from CBS API
#' @param table_id CBS table ID for API download
#' @return A tibble with administrative indicators at all geographic levels
load_admin_data <- function(path = here::here("data", "raw", "indicators_buurt_wijk_gemeente.csv"),
                            use_api = FALSE,
                            table_id = "84286NED") {

# Option 1: Download from CBS API
if (use_api) {
  message("Downloading CBS indicators from API...")
  admin <- download_cbs_data(table_id = table_id)
  return(admin)
}

# Option 2: Load from local file
message("Loading CBS administrative indicators from local file...")

if (!file.exists(path)) {
  stop(glue::glue("File not found: {path}\nSet use_api = TRUE to download from CBS."))
}

admin_raw <- readr::read_csv(path, na = ".", show_col_types = FALSE)

# Rename columns to English (handles the pre-downloaded format)
admin <- admin_raw %>%
  dplyr::select(
    id = 1,
    code = 2,
    municipality = 3,
    region_type = 4,
    pop_total = 5,
    pop_over_65 = 6,
    pop_west = 7,
    pop_nonwest = 8,
    pop_dens = 9,
    avg_home_value = 10,
    avg_inc_recip = 11,
    avg_inc_pers = 12,
    perc_low40_pers = 13,
    perc_high20_pers = 14,
    perc_low40_hh = 15,
    perc_high20_hh = 16,
    perc_low_inc_hh = 17,
    perc_soc_min_hh = 18
  )

# Count by region type
counts <- admin %>%
  dplyr::count(region_type)

message("  Loaded indicators by level:")
for (i in seq_len(nrow(counts))) {
  message(glue::glue("    {counts$region_type[i]}: {counts$n[i]} units"))
}

return(admin)
}


#' Validate Raw Data
#'
#' Performs basic validation checks on the extracted data.
#'
#' @param survey Survey data tibble
#' @param admin Admin data tibble
#' @return A list with validation results
validate_raw_data <- function(survey, admin) {

message("Validating raw data...")

validation <- list(
  survey_n = nrow(survey),
  survey_complete_geo = sum(!is.na(survey$Buurtcode)),
  admin_n = nrow(admin),
  admin_buurt = sum(admin$region_type == "Buurt"),
  admin_wijk = sum(admin$region_type == "Wijk"),
  admin_gemeente = sum(admin$region_type == "Gemeente")
)

# Check for issues
issues <- c()

if (validation$survey_n < 7000) {
  issues <- c(issues, "Survey has fewer than 7000 respondents")
}

if (validation$survey_complete_geo / validation$survey_n < 0.95) {
  issues <- c(issues, "More than 5% of survey respondents missing geocodes")
}

if (validation$admin_buurt < 10000) {
  issues <- c(issues, "Fewer than 10000 buurt units in admin data")
}

validation$issues <- issues
validation$passed <- length(issues) == 0

if (validation$passed) {
  message("  All validation checks passed")
} else {
  warning("  Validation issues found: ", paste(issues, collapse = "; "))
}

return(validation)
}
