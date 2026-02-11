# =============================================================================
# transform.py - Data Transformation Module
# =============================================================================
"""
Functions for creating geographic IDs, recoding variables, and standardization.

Functions:
    create_geo_ids: Create hierarchical geographic identifiers
    prepare_admin_by_level: Split admin data by geographic level
    recode_survey_variables: Create DVs and recode demographics
    standardize_context_vars: Z-score standardize neighborhood variables
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SURVEY_YEAR


# =============================================================================
# Geographic ID Creation
# =============================================================================

def create_geo_ids(survey: pd.DataFrame) -> pd.DataFrame:
    """
    Create standardized geographic codes from Buurtcode.

    Dutch geographic hierarchy:
    - Buurt (neighborhood): 8-digit code
    - Wijk (district): first 6 digits
    - Gemeente (municipality): first 4 digits

    Parameters
    ----------
    survey : pd.DataFrame
        Survey data with Buurtcode column

    Returns
    -------
    pd.DataFrame
        Survey with buurt_id, wijk_id, gemeente_id columns
    """
    print("Creating geographic IDs...")

    df = survey.copy()

    # Ensure Buurtcode is string, pad to 8 digits
    df["buurt_id"] = (
        df["Buurtcode"]
        .astype(str)
        .str.replace(r"\.0$", "", regex=True)  # Remove decimal if present
        .str.zfill(8)
    )

    # Handle missing values
    df.loc[df["Buurtcode"].isna(), "buurt_id"] = np.nan

    # Create wijk (6 digits) and gemeente (4 digits) codes
    df["wijk_id"] = df["buurt_id"].str[:6]
    df["gemeente_id"] = df["buurt_id"].str[:4]

    # Set to NaN where buurt_id is NaN
    df.loc[df["buurt_id"].isna(), ["wijk_id", "gemeente_id"]] = np.nan

    # Report
    n_valid = df["buurt_id"].notna().sum()
    print(f"  Created geo IDs for {n_valid} respondents ({n_valid/len(df)*100:.1f}%)")
    print(f"  Unique buurten: {df['buurt_id'].nunique()}")
    print(f"  Unique wijken: {df['wijk_id'].nunique()}")
    print(f"  Unique gemeenten: {df['gemeente_id'].nunique()}")

    return df


# =============================================================================
# Admin Data Preparation
# =============================================================================

def prepare_admin_by_level(admin: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Split admin data into separate DataFrames by geographic level.

    Adds level-specific prefixes to variable names:
    - Buurt: b_*
    - Wijk: w_*
    - Gemeente: g_*

    Parameters
    ----------
    admin : pd.DataFrame
        CBS administrative data with region_type and region_id columns

    Returns
    -------
    dict
        Dictionary with 'buurt', 'wijk', 'gemeente' DataFrames
    """
    print("Preparing admin data by geographic level...")

    admin = admin.copy()

    # Find the region code column
    region_col = None
    for col in ["region_code", "Codering_3", "WijkenEnBuurten"]:
        if col in admin.columns:
            region_col = col
            break

    if region_col is None:
        raise ValueError("Cannot identify region code column in admin data")

    # Create region_type from the code prefix (BU/WK/GM)
    admin["region_code_clean"] = admin[region_col].astype(str).str.strip()
    admin["region_type"] = admin["region_code_clean"].str[:2].map({
        "BU": "Buurt",
        "WK": "Wijk",
        "GM": "Gemeente"
    })
    admin["region_id"] = admin["region_code_clean"].str[2:].str.strip()

    # Map CBS column names to standard names
    # Based on actual CBS 84286NED column names (2018+)
    col_rename = {
        "AantalInwoners_5": "pop_total",
        "k_65JaarOfOuder_12": "pop_over_65",
        "WestersTotaal_17": "pop_west",
        "NietWestersTotaal_18": "pop_nonwest",
        "Bevolkingsdichtheid_33": "pop_dens",
        "GemiddeldeWoningwaarde_35": "avg_home_value",
        "GemiddeldInkomenPerInkomensontvanger_68": "avg_inc_recip",
        "GemiddeldInkomenPerInwoner_69": "avg_inc_pers",
        "k_40PersonenMetLaagsteInkomen_70": "perc_low40_pers",
        "k_20PersonenMetHoogsteInkomen_71": "perc_high20_pers",
        "k_40HuishoudensMetLaagsteInkomen_73": "perc_low40_hh",
        "k_20HuishoudensMetHoogsteInkomen_74": "perc_high20_hh",
        "HuishoudensMetEenLaagInkomen_75": "perc_low_inc_hh",
        "HuishoudensTot110VanSociaalMinimum_77": "perc_soc_min_hh",
    }

    # Rename columns that exist
    admin = admin.rename(columns={k: v for k, v in col_rename.items() if k in admin.columns})

    # Variables to keep (common indicators)
    indicator_vars = [
        "pop_total", "pop_over_65", "pop_west", "pop_nonwest", "pop_dens",
        "avg_home_value", "avg_inc_recip", "avg_inc_pers",
        "perc_low40_pers", "perc_high20_pers", "perc_low40_hh", "perc_high20_hh",
        "perc_low_inc_hh", "perc_soc_min_hh"
    ]

    # Filter to available indicators
    available_indicators = [v for v in indicator_vars if v in admin.columns]
    print(f"  Available indicators: {len(available_indicators)}")

    result = {}

    for level, prefix, id_length in [
        ("Buurt", "b_", 8),
        ("Wijk", "w_", 6),
        ("Gemeente", "g_", 4)
    ]:
        # Filter to this level
        level_data = admin[admin["region_type"] == level].copy()

        if len(level_data) == 0:
            print(f"  Warning: No {level} data found")
            result[level.lower()] = pd.DataFrame()
            continue

        # Create ID column with correct length
        id_col = f"{level.lower()}_id"
        level_data[id_col] = level_data["region_id"].str.zfill(id_length)

        # Select and rename columns with prefix
        cols_to_keep = [id_col]
        rename_dict = {}

        for var in available_indicators:
            if var in level_data.columns:
                new_name = f"{prefix}{var}"
                rename_dict[var] = new_name
                cols_to_keep.append(new_name)

        level_data = level_data.rename(columns=rename_dict)
        level_data = level_data[[id_col] + list(rename_dict.values())]

        # Drop duplicates
        level_data = level_data.drop_duplicates(subset=[id_col])

        result[level.lower()] = level_data
        print(f"  {level}: {len(level_data)} units")

    return result


# =============================================================================
# Variable Recoding
# =============================================================================

def recode_survey_variables(data: pd.DataFrame) -> pd.DataFrame:
    """
    Recode survey variables and create analysis-ready measures.

    Creates:
    - DV_single: Single item redistribution support (0-100 scale)
    - DV_2item, DV_3item: Composite measures
    - age, education: Standardized (z-score)
    - sex, employment_status, occupation: Categorical

    Parameters
    ----------
    data : pd.DataFrame
        Merged survey data

    Returns
    -------
    pd.DataFrame
        Data with recoded variables
    """
    print("Recoding survey variables...")

    df = data.copy()

    # -------------------------------------------------------------------------
    # Dependent Variables
    # -------------------------------------------------------------------------

    # Filter out missing/refused (coded as 8)
    dv_vars = ["gov_int", "red_inc_diff", "union_pref"]
    for var in dv_vars:
        if var in df.columns:
            df.loc[df[var] == 8, var] = np.nan

    # DV_single: Primary DV - redistribution support (red_inc_diff)
    # Scale from 1-7 to 0-100
    if "red_inc_diff" in df.columns:
        df["DV_single"] = (df["red_inc_diff"] - 1) / 6 * 100
        print(f"  DV_single: mean={df['DV_single'].mean():.1f}, "
              f"sd={df['DV_single'].std():.1f}")

    # DV_2item: Average of gov_int and red_inc_diff
    if "gov_int" in df.columns and "red_inc_diff" in df.columns:
        df["DV_2item"] = df[["gov_int", "red_inc_diff"]].mean(axis=1)
        df["DV_2item_scaled"] = (df["DV_2item"] - 1) / 6 * 100

    # DV_3item: Average of all three items
    if all(v in df.columns for v in dv_vars):
        df["DV_3item"] = df[dv_vars].mean(axis=1)
        df["DV_3item_scaled"] = (df["DV_3item"] - 1) / 6 * 100

    # -------------------------------------------------------------------------
    # Demographics
    # -------------------------------------------------------------------------

    # Sex (categorical)
    if "sex" in df.columns:
        df["sex"] = df["sex"].map({1: "Male", 2: "Female", 3: "Other"})
        df["sex"] = pd.Categorical(df["sex"], categories=["Male", "Female", "Other"])

    # Age (from birth year)
    if "birth_year" in df.columns:
        df["age_raw"] = SURVEY_YEAR - df["birth_year"]
        # Standardize
        df["age"] = (df["age_raw"] - df["age_raw"].mean()) / df["age_raw"].std()
        print(f"  Age: mean={df['age_raw'].mean():.1f}, range={df['age_raw'].min():.0f}-{df['age_raw'].max():.0f}")

    # Education (standardized years)
    if "educyrs" in df.columns:
        df["education"] = (df["educyrs"] - df["educyrs"].mean()) / df["educyrs"].std()

    # -------------------------------------------------------------------------
    # Employment
    # -------------------------------------------------------------------------

    if "work_status" in df.columns:
        employment_map = {
            1: "Employed",
            2: "Self-employed",
            3: "Unemployed",
            4: "Student",
            5: "Retired",
            6: "Homemaker",
            7: "Disabled",
            8: "Other"
        }
        df["employment_status"] = df["work_status"].map(employment_map)
        df["employment_status"] = pd.Categorical(df["employment_status"])

    if "work_type" in df.columns:
        occupation_map = {
            1: "Modern professional",
            2: "Clerical",
            3: "Senior manager",
            4: "Technical",
            5: "Semi-routine manual",
            6: "Routine manual",
            7: "Middle manager",
            8: "Traditional professional"
        }
        df["occupation"] = df["work_type"].map(occupation_map)
        df["occupation"] = pd.Categorical(df["occupation"])

    # -------------------------------------------------------------------------
    # Migration background
    # -------------------------------------------------------------------------

    if "born_in_nl" in df.columns:
        df["born_in_nl"] = df["born_in_nl"].astype(float)

    # -------------------------------------------------------------------------
    # Wealth/Income Proxy Variables (for H3 moderation test)
    # -------------------------------------------------------------------------

    # Create wealth index from asset ownership
    wealth_vars = ["owns_home", "owns_property", "has_savings", "owns_stocks"]
    available_wealth_vars = [v for v in wealth_vars if v in df.columns]

    if available_wealth_vars:
        # Sum of assets owned (0-4 scale)
        df["wealth_index"] = df[available_wealth_vars].fillna(0).sum(axis=1)

        # Binary: High wealth (2+ assets) vs. low wealth
        df["high_wealth"] = (df["wealth_index"] >= 2).astype(int)

        print(f"  Wealth index: mean={df['wealth_index'].mean():.2f}, "
              f"high_wealth={df['high_wealth'].mean()*100:.1f}%")

    # Create occupation class (socioeconomic status proxy)
    if "occupation_class" in df.columns:
        # Higher class = professional/managerial occupations (codes 1, 3, 7, 8)
        higher_class_codes = [1.0, 3.0, 7.0, 8.0]
        df["professional_class"] = df["occupation_class"].isin(higher_class_codes).astype(int)

        # Detailed class ranking (1=highest, 8=lowest)
        class_rank_map = {
            3.0: 1,  # Senior management → highest
            8.0: 2,  # Traditional professional
            1.0: 3,  # Modern professional
            7.0: 4,  # Middle management
            4.0: 5,  # Technical
            2.0: 6,  # Clerical
            5.0: 7,  # Semi-routine
            6.0: 8   # Routine → lowest
        }
        df["occupation_rank"] = df["occupation_class"].map(class_rank_map)

        print(f"  Professional class: {df['professional_class'].mean()*100:.1f}%")

    print(f"  Recoding complete. {len(df)} observations")
    return df


# =============================================================================
# Standardization
# =============================================================================

def standardize_context_vars(
    data: pd.DataFrame,
    prefixes: list = ["b_", "w_", "g_"]
) -> pd.DataFrame:
    """
    Z-score standardize neighborhood-level context variables.

    Parameters
    ----------
    data : pd.DataFrame
        Data with neighborhood variables
    prefixes : list
        Variable name prefixes to standardize (default: buurt, wijk, gemeente)

    Returns
    -------
    pd.DataFrame
        Data with standardized context variables
    """
    print("Standardizing context variables...")

    df = data.copy()

    standardized_count = 0
    for col in df.columns:
        if any(col.startswith(p) for p in prefixes):
            if df[col].dtype in [np.float64, np.int64, float, int]:
                mean_val = df[col].mean()
                std_val = df[col].std()
                if std_val > 0:
                    df[col] = (df[col] - mean_val) / std_val
                    standardized_count += 1

    print(f"  Standardized {standardized_count} context variables")
    return df


# =============================================================================
# Inequality Indices
# =============================================================================

def create_inequality_indices(data: pd.DataFrame) -> pd.DataFrame:
    """
    Create composite inequality measures from low40 and high20 percentages.

    Creates:
    - income_polarization: Sum of low40 + high20 (captures both ends)
    - income_ratio: Ratio of high20 to low40 (affluence relative to poverty)

    Parameters
    ----------
    data : pd.DataFrame
        Data with perc_low40_hh and perc_high20_hh columns

    Returns
    -------
    pd.DataFrame
        Data with added inequality indices
    """
    print("Creating inequality indices...")

    df = data.copy()
    indices_created = 0

    for prefix in ['b_', 'w_', 'g_']:
        low40_col = f'{prefix}perc_low40_hh'
        high20_col = f'{prefix}perc_high20_hh'

        if low40_col in df.columns and high20_col in df.columns:
            # Income polarization: Higher when both extremes are large
            pol_col = f'{prefix}income_polarization'
            df[pol_col] = df[low40_col] + df[high20_col]
            indices_created += 1

            # Income ratio: Higher = more affluent relative to poor
            # Add small constant to avoid division by zero
            ratio_col = f'{prefix}income_ratio'
            df[ratio_col] = df[high20_col] / (df[low40_col].abs() + 0.01)
            indices_created += 1

            print(f"  Created {pol_col} and {ratio_col}")

    print(f"  Created {indices_created} inequality indices")
    return df


# =============================================================================
# Geographic Names
# =============================================================================

def add_geographic_names_from_admin(
    data: pd.DataFrame,
    admin_data: pd.DataFrame
) -> pd.DataFrame:
    """
    Add geographic names (buurt_name, wijk_name, gemeente_name) to analysis data.

    Parameters
    ----------
    data : pd.DataFrame
        Analysis data with buurt_id, wijk_id, gemeente_id
    admin_data : pd.DataFrame
        Raw CBS admin data with WijkenEnBuurten and gemeente_name columns

    Returns
    -------
    pd.DataFrame
        Data with added name columns
    """
    print("\nAdding geographic names...")

    df = data.copy()

    # Check if admin data has required columns
    if 'region_code' not in admin_data.columns and 'Codering_3' not in admin_data.columns:
        print("  Warning: Cannot find region code column in admin data")
        return df

    # Use region_code or create it
    admin = admin_data.copy()
    if 'region_code' not in admin.columns:
        for col in ['Codering_3', 'WijkenEnBuurten']:
            if col in admin.columns:
                admin['region_code'] = admin[col].astype(str).str.strip()
                break

    # Create lookups for each level
    name_col = 'WijkenEnBuurten' if 'WijkenEnBuurten' in admin.columns else None
    gemeente_name_col = 'gemeente_name' if 'gemeente_name' in admin.columns else None

    # Buurt names
    if name_col:
        buurt_rows = admin[admin['region_code'].str.startswith('BU', na=False)].copy()
        if len(buurt_rows) > 0:
            buurt_rows['buurt_id'] = buurt_rows['region_code'].str[2:].str.strip()
            buurt_rows['buurt_name'] = buurt_rows[name_col].str.strip()
            buurt_lookup = buurt_rows[['buurt_id', 'buurt_name']].drop_duplicates('buurt_id')

            df['buurt_id'] = df['buurt_id'].astype(str).str.strip()
            df = df.merge(buurt_lookup, on='buurt_id', how='left')
            n_matched = df['buurt_name'].notna().sum()
            print(f"  Buurt names: {n_matched}/{len(df)} matched")

    # Wijk names
    if name_col:
        wijk_rows = admin[admin['region_code'].str.startswith('WK', na=False)].copy()
        if len(wijk_rows) > 0:
            wijk_rows['wijk_id'] = wijk_rows['region_code'].str[2:].str.strip()
            wijk_rows['wijk_name'] = wijk_rows[name_col].str.strip()
            wijk_lookup = wijk_rows[['wijk_id', 'wijk_name']].drop_duplicates('wijk_id')

            df['wijk_id'] = df['wijk_id'].astype(str).str.strip()
            df = df.merge(wijk_lookup, on='wijk_id', how='left')
            n_matched = df['wijk_name'].notna().sum()
            print(f"  Wijk names: {n_matched}/{len(df)} matched")

    # Gemeente names (from buurt rows or gemeente rows)
    if gemeente_name_col and 'gemeente_name' not in df.columns:
        # Get from buurt rows (they have gemeente_name)
        if name_col:
            buurt_rows = admin[admin['region_code'].str.startswith('BU', na=False)].copy()
            if len(buurt_rows) > 0 and gemeente_name_col in buurt_rows.columns:
                buurt_rows['gemeente_id'] = buurt_rows['region_code'].str[2:6].str.strip()
                buurt_rows['gemeente_name'] = buurt_rows[gemeente_name_col].str.strip()
                gemeente_lookup = buurt_rows[['gemeente_id', 'gemeente_name']].drop_duplicates('gemeente_id')

                df['gemeente_id'] = df['gemeente_id'].astype(str).str.strip()
                df = df.merge(gemeente_lookup, on='gemeente_id', how='left')
                n_matched = df['gemeente_name'].notna().sum()
                print(f"  Gemeente names: {n_matched}/{len(df)} matched")

    return df
