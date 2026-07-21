# =============================================================================
# 01_extract.R - Data Extraction Functions
# =============================================================================
# Functions to load raw data from source files.
# Each function returns a clean tibble ready for transformation.
# =============================================================================

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

    # Asset ownership (B14 in Stata = questionnaire B12)
    # Binary 0/1: 1=real estate, 2=further real estate, 3=savings, 4=stocks, 5=none
    asset_realestate   = b14_1,
    asset_realestate2  = b14_2,
    asset_savings      = b14_3,
    asset_stocks       = b14_4,
    asset_none         = b14_5,

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
#' Loads CBS neighborhood indicators (table 84286NED) from a local CSV export.
#'
#' @param path Path to local CSV file
#' @return A tibble with administrative indicators at all geographic levels
load_admin_data <- function(path = here::here("data", "raw", "indicators_buurt_wijk_gemeente.csv")) {

message("Loading CBS administrative indicators from local file...")

if (!file.exists(path)) {
  stop(glue::glue("File not found: {path}"))
}

admin_raw <- readr::read_csv(path, na = ".", show_col_types = FALSE)

# Rename columns to English (handles the pre-downloaded format)
admin <- admin_raw %>%
  dplyr::select(
    # Cols 1-4: identifiers
    id           = 1,   # ID
    code         = 2,   # WijkenEnBuurten
    municipality = 3,   # Gemeentenaam_1
    region_type  = 4,   # SoortRegio_2
    # Cols 5-6 are Codering_3 and IndelingswijzigingWijkenEnBuurten_4 — skipped
    # Cols 7-13: population and housing
    pop_total      = 7,   # AantalInwoners_5
    pop_over_65    = 8,   # k_65JaarOfOuder_12
    pop_west       = 9,   # WestersTotaal_17
    pop_nonwest    = 10,  # NietWestersTotaal_18
    pop_dens       = 13,  # Bevolkingsdichtheid_33
    avg_home_value = 14,  # GemiddeldeWoningwaarde_35
    avg_inc_recip  = 15,  # GemiddeldInkomenPerInkomensontvanger_65
    avg_inc_pers   = 16,  # GemiddeldInkomenPerInwoner_66
    # Income distribution
    perc_low40_pers  = 17,  # k_40PersonenMetLaagsteInkomen_67
    perc_high20_pers = 18,  # k_20PersonenMetHoogsteInkomen_68
    perc_low40_hh    = 19,  # k_40HuishoudensMetLaagsteInkomen_70
    perc_high20_hh   = 20,  # k_20HuishoudensMetHoogsteInkomen_71
    perc_low_inc_hh  = 21,  # HuishoudensMetEenLaagInkomen_72
    perc_soc_min_hh  = 22   # HuishOnderOfRondSociaalMinimum_73
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
