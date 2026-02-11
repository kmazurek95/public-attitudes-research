# =============================================================================
# config.py - Pipeline Configuration
# =============================================================================
"""
Configuration settings for the redistribution preferences analysis pipeline.
Modify these settings to customize data paths, API options, and model specs.
"""

from pathlib import Path

# =============================================================================
# Path Configuration
# =============================================================================

# Project root (parent of this file)
PROJECT_ROOT = Path(__file__).parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

# Output directories
OUTPUT_DIR = PROJECT_ROOT / "outputs"
TABLES_DIR = OUTPUT_DIR / "tables"
FIGURES_DIR = OUTPUT_DIR / "figures"

# =============================================================================
# Data File Paths
# =============================================================================

# Survey data (SCoRE Netherlands 2017)
SURVEY_PATH = RAW_DIR / "score.dta"

# CBS administrative indicators
ADMIN_PATH = RAW_DIR / "indicators_buurt_wijk_gemeente.csv"

# Output paths
PROCESSED_DATA_PATH = PROCESSED_DIR / "analysis_ready.csv"
REGRESSION_TABLE_PATH = TABLES_DIR / "regression_table.html"

# =============================================================================
# CBS API Configuration
# =============================================================================

# Whether to download fresh data from CBS API (vs using local file)
USE_CBS_API = False

# CBS table ID for neighborhood statistics
# 84286NED = "Kerncijfers wijken en buurten" (Key figures neighborhoods)
CBS_TABLE_ID = "84286NED"

# Year filter for CBS data (Perioden column)
CBS_YEAR = "2018"

# =============================================================================
# Survey Configuration
# =============================================================================

# Survey year (for calculating age from birth year)
SURVEY_YEAR = 2017

# Column mappings: Stata variable names -> English names
SURVEY_COLUMNS = {
    # Dependent variables (redistribution attitudes, 1-7 scale)
    "a27_1": "gov_int",        # Government should intervene to reduce inequality
    "a27_2": "red_inc_diff",   # Government should reduce income differences
    "a27_3": "union_pref",     # Government should support unions

    # Demographics
    "b01": "sex",              # 1=Male, 2=Female, 3=Other
    "b02": "birth_year",       # Year of birth
    "b03": "educlvl",          # Education level (categorical)
    "b04": "educyrs",          # Years of education

    # Employment
    "b07": "work_status",      # Employment status
    "b09": "employee_type",    # Employee, self-employed, family business
    "b10": "org_type",         # Organization type (public/private sector)
    "b11": "has_supervisory",  # Has supervisory responsibility
    "b13": "occupation_class", # NS-SEC occupation classification

    # Asset ownership (income/wealth proxy for H3)
    "b14_1": "owns_home",      # Owns home (eigen huis)
    "b14_2": "owns_property",  # Owns other real estate
    "b14_3": "has_savings",    # Has savings account
    "b14_4": "owns_stocks",    # Owns stocks/bonds
    "b14_5": "no_assets",      # None of these

    # Migration background
    "b18": "born_in_nl",       # Born in Netherlands (1=Yes, 0=No)
    "b20": "father_dutch",     # Father born in NL
    "b21": "mother_dutch",     # Mother born in NL

    # Geographic identifier
    "Buurtcode": "Buurtcode",  # 8-digit neighborhood code

    # Weights
    "weegfac": "weight",       # Survey weight
}

# =============================================================================
# Model Specification
# =============================================================================

# Primary dependent variable
DV_VARIABLE = "DV_single"

# Key predictor of interest
KEY_PREDICTOR = "b_perc_low40_hh"

# Grouping variable for multilevel models
GROUPING_VAR = "buurt_id"

# Individual-level control variables
INDIVIDUAL_CONTROLS = [
    "age",
    "sex",
    "education",
    "employment_status",
    "occupation",
    "born_in_nl",
]

# Neighborhood-level control variables
BUURT_CONTROLS = [
    "b_pop_dens",
    "b_pop_over_65",
    "b_pop_nonwest",
    "b_perc_low_inc_hh",
    "b_perc_soc_min_hh",
]

# =============================================================================
# Analysis Options
# =============================================================================

# Whether to require occupation in analysis sample (drops more cases if True)
INCLUDE_OCCUPATION = True

# Minimum cluster size for multilevel models
MIN_CLUSTER_SIZE = 2

# VIF threshold for multicollinearity warning
VIF_THRESHOLD = 5.0

# Confidence level for intervals
CONFIDENCE_LEVEL = 0.95
