# =============================================================================
# merge.py - Data Merging and Validation Module
# =============================================================================
"""
Functions for merging survey and administrative data at multiple geographic levels.

Functions:
    merge_survey_admin: Left join survey with admin at all levels
    validate_merge: Check match rates at each level
    analyze_missingness: Detailed missingness analysis
    compare_matched_unmatched: Test for systematic differences
    create_analysis_sample: Create complete cases sample
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from scipy import stats

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import INDIVIDUAL_CONTROLS, BUURT_CONTROLS, MIN_CLUSTER_SIZE


# =============================================================================
# Data Merging
# =============================================================================

def merge_survey_admin(
    survey: pd.DataFrame,
    admin_by_level: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """
    Merge survey with administrative data at all three geographic levels.

    Performs sequential left joins:
    1. survey + buurt (on buurt_id)
    2. result + wijk (on wijk_id)
    3. result + gemeente (on gemeente_id)

    Parameters
    ----------
    survey : pd.DataFrame
        Survey data with geographic IDs
    admin_by_level : dict
        Dictionary with 'buurt', 'wijk', 'gemeente' DataFrames

    Returns
    -------
    pd.DataFrame
        Merged data
    """
    print("Merging survey with administrative data...")

    merged = survey.copy()
    initial_n = len(merged)

    # Merge buurt level
    if "buurt" in admin_by_level and len(admin_by_level["buurt"]) > 0:
        buurt_data = admin_by_level["buurt"]
        merged = merged.merge(buurt_data, on="buurt_id", how="left")
        print(f"  + Buurt: {len(buurt_data)} units")

    # Merge wijk level
    if "wijk" in admin_by_level and len(admin_by_level["wijk"]) > 0:
        wijk_data = admin_by_level["wijk"]
        merged = merged.merge(wijk_data, on="wijk_id", how="left")
        print(f"  + Wijk: {len(wijk_data)} units")

    # Merge gemeente level
    if "gemeente" in admin_by_level and len(admin_by_level["gemeente"]) > 0:
        gemeente_data = admin_by_level["gemeente"]
        merged = merged.merge(gemeente_data, on="gemeente_id", how="left")
        print(f"  + Gemeente: {len(gemeente_data)} units")

    # Check row count didn't change
    if len(merged) != initial_n:
        print(f"  Warning: Row count changed from {initial_n} to {len(merged)}")

    print(f"  Final merged data: {len(merged)} rows, {len(merged.columns)} columns")
    return merged


# =============================================================================
# Merge Validation
# =============================================================================

@dataclass
class MergeValidation:
    """Results of merge validation for one level."""
    level: str
    n_matched: int
    n_missing: int
    pct_matched: float


def validate_merge(data: pd.DataFrame) -> List[MergeValidation]:
    """
    Check merge success rates at each geographic level.

    Parameters
    ----------
    data : pd.DataFrame
        Merged data

    Returns
    -------
    list
        List of MergeValidation results
    """
    print("\nValidating merge quality...")

    results = []
    total_n = len(data)

    # Check each level
    level_checks = [
        ("Buurt", "b_pop_total"),
        ("Wijk", "w_pop_total"),
        ("Gemeente", "g_pop_total")
    ]

    for level, indicator_col in level_checks:
        if indicator_col in data.columns:
            n_matched = data[indicator_col].notna().sum()
            n_missing = total_n - n_matched
            pct_matched = n_matched / total_n * 100

            result = MergeValidation(
                level=level,
                n_matched=n_matched,
                n_missing=n_missing,
                pct_matched=pct_matched
            )
            results.append(result)

            status = "OK" if pct_matched >= 80 else "LOW"
            print(f"  {level}: {n_matched}/{total_n} matched ({pct_matched:.1f}%) [{status}]")
        else:
            print(f"  {level}: indicator column '{indicator_col}' not found")

    return results


# =============================================================================
# Missingness Analysis
# =============================================================================

@dataclass
class MissingnessReport:
    """Detailed missingness analysis results."""
    geo_pattern: pd.DataFrame
    var_missingness: pd.DataFrame
    key_missingness: pd.DataFrame


def analyze_missingness(data: pd.DataFrame) -> MissingnessReport:
    """
    Create detailed missingness report.

    Parameters
    ----------
    data : pd.DataFrame
        Merged data

    Returns
    -------
    MissingnessReport
        Missingness analysis results
    """
    print("\nAnalyzing missingness patterns...")

    # Geographic pattern (cross-tab of which levels matched)
    geo_pattern = pd.DataFrame({
        "has_buurt": data.get("b_pop_total", pd.Series()).notna(),
        "has_wijk": data.get("w_pop_total", pd.Series()).notna(),
        "has_gemeente": data.get("g_pop_total", pd.Series()).notna()
    }).value_counts().reset_index(name="count")

    print(f"  Geographic patterns:")
    print(geo_pattern.to_string(index=False))

    # Variable-level missingness
    missing_pct = data.isna().mean() * 100
    var_missingness = pd.DataFrame({
        "variable": missing_pct.index,
        "pct_missing": missing_pct.values
    }).sort_values("pct_missing", ascending=False)

    # Key variables
    key_vars = ["DV_single", "age", "education", "b_perc_low40_hh", "buurt_id"]
    key_vars = [v for v in key_vars if v in data.columns]
    key_missingness = var_missingness[var_missingness["variable"].isin(key_vars)]

    print(f"  Key variable missingness:")
    for _, row in key_missingness.iterrows():
        print(f"    {row['variable']}: {row['pct_missing']:.1f}%")

    return MissingnessReport(
        geo_pattern=geo_pattern,
        var_missingness=var_missingness,
        key_missingness=key_missingness
    )


# =============================================================================
# Matched vs Unmatched Comparison
# =============================================================================

def compare_matched_unmatched(data: pd.DataFrame) -> pd.DataFrame:
    """
    Test for systematic differences between matched and unmatched cases.

    Parameters
    ----------
    data : pd.DataFrame
        Merged data

    Returns
    -------
    pd.DataFrame
        Comparison statistics
    """
    print("\nComparing matched vs unmatched cases...")

    if "b_pop_total" not in data.columns:
        print("  Cannot compare: no buurt indicator found")
        return pd.DataFrame()

    # Create matched indicator
    data = data.copy()
    data["matched"] = data["b_pop_total"].notna()

    # Compare groups
    comparison_vars = ["DV_single", "age_raw", "education"]
    comparison_vars = [v for v in comparison_vars if v in data.columns]

    results = []
    for var in comparison_vars:
        matched_vals = data.loc[data["matched"], var].dropna()
        unmatched_vals = data.loc[~data["matched"], var].dropna()

        if len(matched_vals) > 0 and len(unmatched_vals) > 0:
            t_stat, p_val = stats.ttest_ind(matched_vals, unmatched_vals)

            results.append({
                "variable": var,
                "matched_mean": matched_vals.mean(),
                "matched_n": len(matched_vals),
                "unmatched_mean": unmatched_vals.mean(),
                "unmatched_n": len(unmatched_vals),
                "t_statistic": t_stat,
                "p_value": p_val,
                "significant": p_val < 0.05
            })

    results_df = pd.DataFrame(results)

    if len(results_df) > 0:
        print("  Results:")
        for _, row in results_df.iterrows():
            sig = "*" if row["significant"] else ""
            print(f"    {row['variable']}: matched={row['matched_mean']:.2f}, "
                  f"unmatched={row['unmatched_mean']:.2f}, p={row['p_value']:.3f}{sig}")

    return results_df


# =============================================================================
# Analysis Sample Creation
# =============================================================================

def create_analysis_sample(
    data: pd.DataFrame,
    include_occupation: bool = True
) -> pd.DataFrame:
    """
    Create final analysis sample with complete cases.

    Parameters
    ----------
    data : pd.DataFrame
        Full merged data
    include_occupation : bool
        Whether to require occupation (drops more cases if True)

    Returns
    -------
    pd.DataFrame
        Analysis-ready sample with complete cases
    """
    print("\nCreating analysis sample...")

    # Required variables
    required = [
        "DV_single",
        "age",
        "sex",
        "education",
        "employment_status",
        "born_in_nl",
        "buurt_id"
    ]

    # Add buurt-level predictors
    buurt_vars = [v for v in BUURT_CONTROLS if v in data.columns]
    required.extend(buurt_vars)

    # Add key predictor
    if "b_perc_low40_hh" in data.columns:
        required.append("b_perc_low40_hh")

    # Optionally add occupation
    if include_occupation and "occupation" in data.columns:
        required.append("occupation")

    # Filter to available columns
    required = [v for v in required if v in data.columns]
    print(f"  Required variables: {len(required)}")

    # Create complete cases
    initial_n = len(data)
    sample = data.dropna(subset=required).copy()
    final_n = len(sample)

    print(f"  Complete cases: {final_n}/{initial_n} ({final_n/initial_n*100:.1f}%)")

    # Filter to clusters with minimum size
    cluster_sizes = sample["buurt_id"].value_counts()
    valid_clusters = cluster_sizes[cluster_sizes >= MIN_CLUSTER_SIZE].index
    sample = sample[sample["buurt_id"].isin(valid_clusters)]

    print(f"  After cluster filter (min={MIN_CLUSTER_SIZE}): {len(sample)} observations")
    print(f"  Unique buurten: {sample['buurt_id'].nunique()}")

    return sample
