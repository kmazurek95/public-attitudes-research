# =============================================================================
# extract.py - Data Extraction Module
# =============================================================================
"""
Functions for loading data from CBS API and local files.

Functions:
    download_cbs_data: Download neighborhood statistics from CBS StatLine API
    get_cbs_metadata: Get variable descriptions from CBS
    load_survey_data: Load SCoRE survey from Stata file
    load_admin_data: Load CBS administrative data (local or API)
    validate_raw_data: Basic validation of loaded data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    SURVEY_COLUMNS, CBS_TABLE_ID, CBS_YEAR,
    SURVEY_PATH, ADMIN_PATH
)


# =============================================================================
# CBS API Functions
# =============================================================================

def download_cbs_data(
    table_id: str = CBS_TABLE_ID,
    year: str = CBS_YEAR,
    save_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Download CBS neighborhood indicators from StatLine API.

    Parameters
    ----------
    table_id : str
        CBS table identifier (default: "84286NED" for Kerncijfers wijken en buurten)
    year : str
        Year filter for Perioden column (e.g., "2018")
    save_path : Path, optional
        Path to save downloaded CSV

    Returns
    -------
    pd.DataFrame
        CBS indicators with standardized column names
    """
    try:
        import cbsodata
    except ImportError:
        raise ImportError("cbsodata not installed. Run: pip install cbsodata")

    print(f"Downloading CBS table {table_id}...")

    # Download full table
    data = pd.DataFrame(cbsodata.get_data(table_id))
    print(f"  Downloaded {len(data)} rows")

    # Filter by year if Perioden column exists
    if "Perioden" in data.columns:
        # CBS year format can vary: "2018JJ00", "2018", etc.
        year_mask = data["Perioden"].astype(str).str.contains(year)
        data = data[year_mask].copy()
        print(f"  Filtered to year {year}: {len(data)} rows")

    # Standardize column names
    data = _standardize_cbs_columns(data)

    # Save if path provided
    if save_path:
        data.to_csv(save_path, index=False)
        print(f"  Saved to {save_path}")

    return data


def _standardize_cbs_columns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize CBS column names to match expected format.

    CBS column names can vary between years/tables. This function
    maps common variations to standard names.
    """
    # First, handle region_code specially - only rename ONE column
    # Prefer Codering_3 as it contains the clean code (BU/WK/GM prefix)
    if "Codering_3" in data.columns:
        data = data.rename(columns={"Codering_3": "region_code"})
    elif "WijkenEnBuurten" in data.columns:
        data = data.rename(columns={"WijkenEnBuurten": "region_code"})

    # Column name mappings (CBS Dutch -> English standard)
    # Note: region_code is handled above, not here
    # Based on actual CBS 84286NED column names (2018+)
    col_mapping = {
        "Gemeentenaam_1": "gemeente_name",
        "AantalInwoners_5": "pop_total",
        "k_65JaarOfOuder_12": "pop_over_65",
        "Bevolkingsdichtheid_33": "pop_dens",
        "WestersTotaal_17": "pop_west",
        "NietWestersTotaal_18": "pop_nonwest",
        "GemiddeldInkomenPerInkomensontvanger_68": "avg_inc_recip",
        "GemiddeldInkomenPerInwoner_69": "avg_inc_pers",
        "HuishoudensTotaal_28": "hh_total",
        "Koopwoningen_40": "owner_occupied",
        "GemiddeldeWoningwaarde_35": "avg_home_value",
        "k_40PersonenMetLaagsteInkomen_70": "perc_low40_pers",
        "k_20PersonenMetHoogsteInkomen_71": "perc_high20_pers",
        "k_40HuishoudensMetLaagsteInkomen_73": "perc_low40_hh",
        "k_20HuishoudensMetHoogsteInkomen_74": "perc_high20_hh",
        "HuishoudensMetEenLaagInkomen_75": "perc_low_inc_hh",
        "HuishoudensTot110VanSociaalMinimum_77": "perc_soc_min_hh",
    }

    # Rename columns that exist
    renamed = {k: v for k, v in col_mapping.items() if k in data.columns}
    data = data.rename(columns=renamed)

    # Extract region type from code (BU=buurt, WK=wijk, GM=gemeente)
    if "region_code" in data.columns:
        region_code_str = data["region_code"].astype(str).str.strip()
        data["region_type"] = region_code_str.str[:2].map({
            "BU": "Buurt",
            "WK": "Wijk",
            "GM": "Gemeente"
        })
        # Extract numeric code (everything after the 2-char prefix)
        data["region_id"] = region_code_str.str[2:].str.strip()

    return data


def get_cbs_metadata(table_id: str = CBS_TABLE_ID) -> pd.DataFrame:
    """
    Retrieve variable descriptions for a CBS table.

    Parameters
    ----------
    table_id : str
        CBS table identifier

    Returns
    -------
    pd.DataFrame
        Variable names and descriptions
    """
    try:
        import cbsodata
    except ImportError:
        raise ImportError("cbsodata not installed. Run: pip install cbsodata")

    meta = cbsodata.get_meta(table_id, "DataProperties")
    return pd.DataFrame(meta)[["Key", "Title", "Description", "Unit"]]


# =============================================================================
# Survey Data Loading
# =============================================================================

def load_survey_data(path: Path = SURVEY_PATH) -> pd.DataFrame:
    """
    Load SCoRE survey data from Stata file.

    Selects and renames key variables for analysis.

    Parameters
    ----------
    path : Path
        Path to .dta file

    Returns
    -------
    pd.DataFrame
        Survey data with English column names
    """
    try:
        import pyreadstat
    except ImportError:
        raise ImportError("pyreadstat not installed. Run: pip install pyreadstat")

    print(f"Loading survey data from {path}...")

    # Read Stata file
    df, meta = pyreadstat.read_dta(str(path))
    print(f"  Loaded {len(df)} respondents, {len(df.columns)} variables")

    # Select and rename columns
    cols_to_select = list(SURVEY_COLUMNS.keys())
    available_cols = [c for c in cols_to_select if c in df.columns]
    missing_cols = [c for c in cols_to_select if c not in df.columns]

    if missing_cols:
        print(f"  Warning: Missing columns: {missing_cols}")

    df = df[available_cols].copy()
    df = df.rename(columns=SURVEY_COLUMNS)

    # Add respondent ID
    df["respondent_id"] = range(1, len(df) + 1)

    print(f"  Selected {len(df.columns)} columns")
    return df


# =============================================================================
# Administrative Data Loading
# =============================================================================

def load_admin_data(
    path: Path = ADMIN_PATH,
    use_api: bool = False,
    table_id: str = CBS_TABLE_ID
) -> pd.DataFrame:
    """
    Load CBS administrative indicators.

    Can load from local CSV file or download from CBS API.

    Parameters
    ----------
    path : Path
        Path to local CSV file
    use_api : bool
        If True, download fresh data from CBS API
    table_id : str
        CBS table ID for API download

    Returns
    -------
    pd.DataFrame
        Administrative indicators
    """
    if use_api:
        # Download and save to the local path
        return download_cbs_data(table_id, save_path=path)

    print(f"Loading admin data from {path}...")
    df = pd.read_csv(path)
    print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
    return df


# =============================================================================
# Data Validation
# =============================================================================

def validate_raw_data(
    survey: pd.DataFrame,
    admin: pd.DataFrame
) -> Dict[str, Any]:
    """
    Perform basic validation checks on extracted data.

    Parameters
    ----------
    survey : pd.DataFrame
        Survey data
    admin : pd.DataFrame
        Administrative data

    Returns
    -------
    dict
        Validation results with counts and pass/fail status
    """
    print("\nValidating raw data...")

    results = {
        "survey_n": len(survey),
        "survey_complete_geo": 0,
        "admin_n": len(admin),
        "admin_buurt": 0,
        "admin_wijk": 0,
        "admin_gemeente": 0,
        "issues": [],
        "passed": True
    }

    # Survey checks
    if "Buurtcode" in survey.columns:
        results["survey_complete_geo"] = survey["Buurtcode"].notna().sum()
        geo_pct = results["survey_complete_geo"] / len(survey) * 100
        print(f"  Survey: {len(survey)} respondents, {geo_pct:.1f}% with geocode")

        if geo_pct < 90:
            results["issues"].append(f"Low geocode coverage: {geo_pct:.1f}%")
            results["passed"] = False
    else:
        results["issues"].append("No Buurtcode column in survey")
        results["passed"] = False

    # Admin checks
    if "region_type" in admin.columns:
        type_counts = admin["region_type"].value_counts()
        results["admin_buurt"] = type_counts.get("Buurt", 0)
        results["admin_wijk"] = type_counts.get("Wijk", 0)
        results["admin_gemeente"] = type_counts.get("Gemeente", 0)
        print(f"  Admin: {results['admin_buurt']} buurt, "
              f"{results['admin_wijk']} wijk, {results['admin_gemeente']} gemeente")
    else:
        # Try to infer from region_code or other columns
        print(f"  Admin: {len(admin)} total rows (region type not identified)")

    # Check minimum counts
    if results["survey_n"] < 5000:
        results["issues"].append(f"Survey N too low: {results['survey_n']}")
        results["passed"] = False

    if results["passed"]:
        print("  Validation PASSED")
    else:
        print(f"  Validation FAILED: {results['issues']}")

    return results
