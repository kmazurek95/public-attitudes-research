# =============================================================================
# data_loader.py - Cached Data Loading for Dashboard
# =============================================================================
"""
Utility functions for loading and caching data in the Streamlit dashboard.
Uses @st.cache_data for efficient data loading across page refreshes.

Supports two modes:
1. Full mode: Raw data available (local development)
2. Demo mode: Only precomputed results (cloud deployment without data)
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import sys

# Add parent directories to path for imports
DASHBOARD_DIR = Path(__file__).parent.parent
PYTHON_DIR = DASHBOARD_DIR.parent
REPO_ROOT = PYTHON_DIR.parent  # Root of the repository
sys.path.insert(0, str(PYTHON_DIR))

# Precomputed results path (always available) - check multiple locations
def _find_precomputed_path() -> Path:
    """Find the precomputed results JSON file."""
    cwd = Path.cwd()
    possible_paths = [
        DASHBOARD_DIR / "data" / "precomputed_results.json",
        cwd / "python" / "dashboard" / "data" / "precomputed_results.json",
        cwd / "dashboard" / "data" / "precomputed_results.json",
    ]
    for path in possible_paths:
        if path.exists():
            return path
    return possible_paths[0]

PRECOMPUTED_RESULTS_PATH = _find_precomputed_path()

# Data path - check multiple locations for flexibility
# Priority: 1) repo root data/, 2) python/data/, 3) config path
def _find_data_path() -> Path:
    """Find the analysis data file in various possible locations."""
    # Get current working directory (works better on Streamlit Cloud)
    cwd = Path.cwd()

    possible_paths = [
        # From current working directory (Streamlit Cloud typically runs from repo root)
        cwd / "data" / "processed" / "analysis_ready.csv",
        # From __file__ relative paths
        REPO_ROOT / "data" / "processed" / "analysis_ready.csv",  # Repo root
        PYTHON_DIR / "data" / "processed" / "analysis_ready.csv",  # Python folder
        DASHBOARD_DIR / "data" / "analysis_ready.csv",  # Dashboard folder
        # Try going up from cwd
        cwd.parent / "data" / "processed" / "analysis_ready.csv",
        cwd.parent.parent / "data" / "processed" / "analysis_ready.csv",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # Try config as last resort
    try:
        from config import PROCESSED_DATA_PATH
        return Path(PROCESSED_DATA_PATH)
    except ImportError:
        pass

    # Return first option as default (will trigger demo mode if not found)
    return possible_paths[0]

PROCESSED_DATA_PATH = _find_data_path()

# Output directories (may not exist in cloud deployment)
try:
    from config import FIGURES_DIR, TABLES_DIR, OUTPUT_DIR
except ImportError:
    FIGURES_DIR = PYTHON_DIR / "outputs" / "figures"
    TABLES_DIR = PYTHON_DIR / "outputs" / "tables"
    OUTPUT_DIR = PYTHON_DIR / "outputs"


# =============================================================================
# Demo Mode Detection
# =============================================================================

def is_demo_mode() -> bool:
    """
    Check if dashboard is running in demo mode (no raw data available).

    Returns
    -------
    bool
        True if raw data is not available
    """
    # Re-check the path each time in case it wasn't found during import
    return not PROCESSED_DATA_PATH.exists()


def get_demo_mode_message() -> str:
    """Get message to display when in demo mode."""
    return (
        "Running in **demo mode** with precomputed results. "
        "Interactive data exploration is limited. "
        "Full functionality available when raw data is present."
    )


# =============================================================================
# Data Loading Functions
# =============================================================================

@st.cache_data(ttl=3600)
def load_analysis_data() -> Optional[pd.DataFrame]:
    """
    Load the analysis-ready dataset with caching.

    Returns
    -------
    pd.DataFrame or None
        The merged and transformed analysis dataset, or None if not available
    """
    if Path(PROCESSED_DATA_PATH).exists():
        df = pd.read_csv(PROCESSED_DATA_PATH)
        return df
    return None


@st.cache_data
def load_precomputed_results() -> Dict[str, Any]:
    """
    Load precomputed results from JSON file.

    Returns
    -------
    Dict with precomputed model results
    """
    if PRECOMPUTED_RESULTS_PATH.exists():
        with open(PRECOMPUTED_RESULTS_PATH, 'r') as f:
            return json.load(f)
    # Fallback to hardcoded defaults
    return get_precomputed_results()


@st.cache_data
def get_summary_stats(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Calculate summary statistics for the dashboard home page.

    Parameters
    ----------
    df : pd.DataFrame, optional
        The analysis dataset. If None, uses precomputed results.

    Returns
    -------
    Dict with summary statistics
    """
    # If no data, use precomputed results
    if df is None:
        precomputed = load_precomputed_results()
        return precomputed.get("summary_stats", {
            "n_obs": 0,
            "n_complete": 0,
            "n_buurten": 0,
            "n_wijken": 0,
            "n_gemeenten": 0,
            "dv_mean": 0,
            "dv_sd": 0,
        })

    # Geographic counts
    n_buurten = df['buurt_id'].nunique() if 'buurt_id' in df.columns else 0
    n_wijken = df['wijk_id'].nunique() if 'wijk_id' in df.columns else 0
    n_gemeenten = df['gemeente_id'].nunique() if 'gemeente_id' in df.columns else 0

    # DV statistics
    dv_col = 'DV_single'
    dv_mean = df[dv_col].mean() if dv_col in df.columns else 0
    dv_std = df[dv_col].std() if dv_col in df.columns else 0

    # Sample with complete cases for key variables
    key_vars = ['DV_single', 'buurt_id', 'b_perc_low40_hh', 'age', 'sex', 'education']
    key_vars = [v for v in key_vars if v in df.columns]
    n_complete = df[key_vars].dropna().shape[0]

    return {
        "n_obs": len(df),
        "n_complete": n_complete,
        "n_buurten": n_buurten,
        "n_wijken": n_wijken,
        "n_gemeenten": n_gemeenten,
        "dv_mean": dv_mean,
        "dv_sd": dv_std,
    }


@st.cache_data
def get_column_info(df: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Get column information organized by type.

    Returns
    -------
    Dict with lists of column names by category
    """
    all_cols = df.columns.tolist()

    # Categorize columns by prefix
    buurt_cols = [c for c in all_cols if c.startswith('b_')]
    wijk_cols = [c for c in all_cols if c.startswith('w_')]
    gemeente_cols = [c for c in all_cols if c.startswith('g_')]

    # Individual-level columns
    individual_cols = [
        'sex', 'birth_year', 'age', 'age_raw', 'educlvl', 'educyrs', 'education',
        'work_status', 'work_type', 'employment_status', 'occupation',
        'born_in_nl', 'father_dutch', 'mother_dutch'
    ]
    individual_cols = [c for c in individual_cols if c in all_cols]

    # Dependent variables
    dv_cols = [c for c in all_cols if c.startswith('DV_') or c in ['gov_int', 'red_inc_diff', 'union_pref']]

    # Geographic IDs
    geo_id_cols = ['buurt_id', 'wijk_id', 'gemeente_id', 'Buurtcode']
    geo_id_cols = [c for c in geo_id_cols if c in all_cols]

    return {
        "buurt": buurt_cols,
        "wijk": wijk_cols,
        "gemeente": gemeente_cols,
        "individual": individual_cols,
        "dv": dv_cols,
        "geo_ids": geo_id_cols,
        "all": all_cols
    }


def get_existing_figures() -> Dict[str, Optional[Path]]:
    """
    Get paths to existing figures from the outputs directory.

    Returns
    -------
    Dict mapping figure names to file paths (or None if not found)
    """
    figure_names = [
        'dv_distribution',
        'individual_vars',
        'buurt_correlations',
        'inequality_measures',
        'inequality_measure_comparison',
        'cluster_sizes',
        'coefficient_stability',
        'residual_diagnostics',
        'random_effects',
        'key_predictor',
        'weight_distribution'
    ]

    figures = {}
    for name in figure_names:
        path = FIGURES_DIR / f"{name}.png"
        figures[name] = path if path.exists() else None

    return figures


def get_existing_tables() -> Dict[str, Optional[Path]]:
    """
    Get paths to existing HTML tables from the outputs directory.

    Returns
    -------
    Dict mapping table names to file paths (or None if not found)
    """
    tables = {
        'regression_two_level': TABLES_DIR / 'regression_table.html',
        'regression_four_level': TABLES_DIR / 'regression_table_four_level.html',
    }

    return {name: path if path.exists() else None for name, path in tables.items()}


def load_html_table(table_path: Path) -> Optional[str]:
    """
    Load an HTML table file as a string.

    Parameters
    ----------
    table_path : Path
        Path to the HTML file

    Returns
    -------
    str or None
        HTML content or None if file doesn't exist
    """
    if table_path and table_path.exists():
        return table_path.read_text(encoding='utf-8')
    return None


@st.cache_data
def get_filtered_data(
    df: pd.DataFrame,
    gemeente_filter: Optional[List[str]] = None,
    education_range: Optional[tuple] = None,
    employment_filter: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Apply filters to the dataset.

    Parameters
    ----------
    df : pd.DataFrame
        The full dataset
    gemeente_filter : List[str], optional
        List of gemeente IDs to include
    education_range : tuple, optional
        (min, max) education values to include
    employment_filter : List[str], optional
        List of employment statuses to include

    Returns
    -------
    pd.DataFrame
        Filtered dataset
    """
    filtered = df.copy()

    if gemeente_filter and len(gemeente_filter) > 0:
        filtered = filtered[filtered['gemeente_id'].astype(str).isin(gemeente_filter)]

    if education_range and 'education' in filtered.columns:
        filtered = filtered[
            (filtered['education'] >= education_range[0]) &
            (filtered['education'] <= education_range[1])
        ]

    if employment_filter and len(employment_filter) > 0:
        if 'employment_status' in filtered.columns:
            filtered = filtered[filtered['employment_status'].isin(employment_filter)]

    return filtered


# =============================================================================
# Model Results Cache
# =============================================================================

@st.cache_data
def get_precomputed_results() -> Dict[str, Any]:
    """
    Load precomputed model results.

    First tries to load from JSON file, falls back to hardcoded defaults.

    Returns
    -------
    Dict with model results
    """
    # Try loading from JSON file first
    if PRECOMPUTED_RESULTS_PATH.exists():
        try:
            with open(PRECOMPUTED_RESULTS_PATH, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Fallback to hardcoded defaults
    return {
        "summary_stats": {
            "n_obs": 8013,
            "n_complete": 4748,
            "n_buurten": 1572,
            "n_wijken": 869,
            "n_gemeenten": 295,
            "dv_mean": 70.79,
            "dv_sd": 27.41
        },
        "two_level": {
            "icc": 0.0347,
            "pct_between": 3.47,
            "pct_within": 96.53,
            "n_obs": 4748,
            "n_clusters": 1572,
            "models": {
                "m0": {"name": "Empty Model", "coef": None, "se": None},
                "m1": {"name": "+ Key Predictor", "coef": 3.459, "se": 0.417, "significant": True},
                "m2": {"name": "+ Individual Controls", "coef": 2.939, "se": 0.405, "significant": True},
                "m3": {"name": "+ Buurt Controls", "coef": 0.276, "se": 0.947, "significant": False},
            }
        },
        "four_level": {
            "icc_buurt": 0.034,
            "n_obs": 4748,
            "n_buurten": 1572,
            "n_wijken": 869,
            "n_gemeenten": 295,
            "note": "Python uses buurt as primary grouping with wijk/gemeente as fixed effects"
        },
        "h3_test": {
            "interaction_coef": 0.181,
            "interaction_se": 0.343,
            "significant": False,
            "interpretation": "H3 NOT SUPPORTED: No significant cross-level interaction"
        },
        "sensitivity": {
            "base": {"name": "Base (DV_single)", "coef": 0.276, "se": 0.947, "significant": False},
            "two_item": {"name": "2-item DV", "coef": 0.312, "se": 0.891, "significant": False},
            "three_item": {"name": "3-item DV", "coef": 0.287, "se": 0.823, "significant": False},
            "dutch_only": {"name": "Dutch-born only", "coef": 0.189, "se": 1.012, "significant": False},
            "income_ratio": {"name": "Income Ratio", "coef": -1.841, "se": 0.892, "significant": True}
        },
        "hypotheses": {
            "h1": {"name": "Neighborhood Inequality Effect", "result": "NOT SUPPORTED"},
            "h2": {"name": "Geographic Level Comparison", "result": "INCONCLUSIVE"},
            "h3": {"name": "Income Moderation", "result": "NOT SUPPORTED"}
        }
    }
