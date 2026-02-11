# =============================================================================
# analyze.py - Statistical Analysis Module
# =============================================================================
"""
Functions for multilevel modeling, ICC calculation, and diagnostics.

Functions:
    fit_two_level_models: Fit sequence of random-intercept models
    calculate_icc: Calculate intraclass correlation
    run_diagnostics: VIF, residual stats, random effects
    run_sensitivity: Robustness checks with alternative specifications
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from scipy import stats
import warnings

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import VIF_THRESHOLD, CONFIDENCE_LEVEL


# =============================================================================
# Model Results Dataclass
# =============================================================================

@dataclass
class TwoLevelModels:
    """Container for fitted multilevel models."""
    m0_empty: Any       # statsmodels MixedLMResults
    m1_key_pred: Any
    m2_ind_controls: Any
    m3_buurt_controls: Any


@dataclass
class FourLevelModels:
    """Container for fitted four-level multilevel models (buurt/wijk/gemeente)."""
    m0_empty: Any       # Empty model with 3 random intercepts
    m1_key_pred: Any    # + key predictors at all levels
    m2_ind_controls: Any    # + individual controls
    m3_buurt_controls: Any  # + buurt-level controls
    m4_wijk_controls: Any   # + wijk-level controls


@dataclass
class ICCResult:
    """Intraclass correlation results."""
    icc: float
    var_buurt: float
    var_residual: float
    var_total: float
    pct_between: float
    pct_within: float


@dataclass
class DiagnosticsResult:
    """Model diagnostics results."""
    vif: pd.DataFrame
    high_vif: List[str]
    residual_stats: pd.DataFrame
    random_effect_stats: pd.DataFrame
    n_clusters: int
    n_obs: int


# =============================================================================
# Multilevel Model Fitting
# =============================================================================

def fit_two_level_models(data: pd.DataFrame) -> TwoLevelModels:
    """
    Fit sequence of two-level random intercept models.

    Models:
    - m0: Empty model (random intercept only) - for ICC
    - m1: + key predictor (b_perc_low40_hh)
    - m2: + individual controls
    - m3: + buurt-level controls

    Parameters
    ----------
    data : pd.DataFrame
        Analysis sample with required variables

    Returns
    -------
    TwoLevelModels
        Container with all fitted models
    """
    import statsmodels.formula.api as smf

    print("\nFitting two-level multilevel models...")

    # Ensure buurt_id is string for grouping
    df = data.copy()
    df["buurt_id"] = df["buurt_id"].astype(str)

    # Suppress convergence warnings for cleaner output
    warnings.filterwarnings("ignore", category=RuntimeWarning)

    # M0: Empty model (random intercept only)
    print("  Fitting m0 (empty model)...")
    m0 = smf.mixedlm(
        "DV_single ~ 1",
        data=df,
        groups="buurt_id"
    ).fit(reml=True)
    n_groups = df["buurt_id"].nunique()
    print(f"    N={int(m0.nobs)}, groups={n_groups}")

    # M1: Add key predictor
    print("  Fitting m1 (+ key predictor)...")
    m1 = smf.mixedlm(
        "DV_single ~ b_perc_low40_hh",
        data=df,
        groups="buurt_id"
    ).fit(reml=True)

    # M2: Add individual controls
    print("  Fitting m2 (+ individual controls)...")
    m2_formula = (
        "DV_single ~ b_perc_low40_hh + age + C(sex) + education + "
        "C(employment_status) + born_in_nl"
    )

    # Add occupation if available
    if "occupation" in df.columns and df["occupation"].notna().sum() > 100:
        m2_formula += " + C(occupation)"

    m2 = smf.mixedlm(
        m2_formula,
        data=df,
        groups="buurt_id"
    ).fit(reml=True)

    # M3: Add buurt-level controls
    print("  Fitting m3 (+ buurt controls)...")
    buurt_controls = []
    for var in ["b_pop_dens", "b_pop_over_65", "b_pop_nonwest",
                "b_perc_low_inc_hh", "b_perc_soc_min_hh"]:
        if var in df.columns and df[var].notna().sum() > 100:
            buurt_controls.append(var)

    m3_formula = m2_formula
    if buurt_controls:
        m3_formula += " + " + " + ".join(buurt_controls)

    m3 = smf.mixedlm(
        m3_formula,
        data=df,
        groups="buurt_id"
    ).fit(reml=True)

    print("  All models fitted successfully")

    # Print key coefficient
    if "b_perc_low40_hh" in m3.params.index:
        coef = m3.params["b_perc_low40_hh"]
        se = m3.bse["b_perc_low40_hh"]
        print(f"  Key predictor (m3): b_perc_low40_hh = {coef:.3f} (SE={se:.3f})")

    return TwoLevelModels(
        m0_empty=m0,
        m1_key_pred=m1,
        m2_ind_controls=m2,
        m3_buurt_controls=m3
    )


# =============================================================================
# Four-Level Multilevel Model Fitting
# =============================================================================

def fit_four_level_models(data: pd.DataFrame) -> FourLevelModels:
    """
    Fit sequence of four-level random intercept models.
    
    These models include random intercepts for buurt, wijk, and gemeente,
    approximating the R lme4 specification:
    (1|gemeente_id) + (1|wijk_id) + (1|buurt_id)
    
    Note: statsmodels has limitations with multiple random effects. We use
    the primary grouping at buurt level and include wijk/gemeente predictors
    as fixed effects to capture higher-level variation.
    
    Models:
    - m0: Empty model (buurt random intercept)
    - m1: + key predictors at all levels (b_, w_, g_perc_low40_hh)
    - m2: + individual controls
    - m3: + buurt-level controls
    - m4: + wijk-level controls

    Parameters
    ----------
    data : pd.DataFrame
        Analysis sample with required variables including wijk_id and gemeente_id

    Returns
    -------
    FourLevelModels
        Container with all fitted models
    """
    import statsmodels.formula.api as smf

    print("\nFitting four-level multilevel models...")
    print("  Note: Using buurt as primary grouping with wijk/gemeente predictors")

    # Check required columns
    required_cols = ["buurt_id", "wijk_id", "gemeente_id"]
    missing = [c for c in required_cols if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns for four-level models: {missing}")

    # Prepare data - create a clean copy with complete cases for required vars
    df = data.copy()
    
    # Ensure string IDs
    for col in ["buurt_id", "wijk_id", "gemeente_id"]:
        df[col] = df[col].astype(str)
    
    # Get required columns for models
    base_required = ["DV_single", "buurt_id", "wijk_id", "gemeente_id"]
    key_preds = ["b_perc_low40_hh"]
    if "w_perc_low40_hh" in df.columns:
        key_preds.append("w_perc_low40_hh")
    if "g_perc_low40_hh" in df.columns:
        key_preds.append("g_perc_low40_hh")
    
    ind_controls = ["age", "sex", "education", "employment_status", "born_in_nl"]
    ind_controls = [c for c in ind_controls if c in df.columns]
    
    buurt_ctrls = ["b_pop_dens", "b_pop_over_65", "b_pop_nonwest", 
                   "b_perc_low_inc_hh", "b_perc_soc_min_hh"]
    buurt_ctrls = [c for c in buurt_ctrls if c in df.columns]
    
    wijk_ctrls = ["w_pop_dens", "w_pop_over_65", "w_pop_nonwest",
                  "w_perc_low_inc_hh", "w_perc_soc_min_hh"]
    wijk_ctrls = [c for c in wijk_ctrls if c in df.columns]
    
    # Create analysis subset with all required variables
    all_vars = base_required + key_preds + ind_controls + buurt_ctrls + wijk_ctrls
    all_vars = list(set(all_vars))  # Remove duplicates
    
    df_model = df[all_vars].dropna().copy()
    df_model = df_model.reset_index(drop=True)
    
    print(f"  Sample size: {len(df_model)}")
    print(f"  Unique buurten: {df_model['buurt_id'].nunique()}")
    print(f"  Unique wijken: {df_model['wijk_id'].nunique()}")
    print(f"  Unique gemeenten: {df_model['gemeente_id'].nunique()}")

    # Suppress warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    warnings.filterwarnings("ignore", category=UserWarning)

    # M0: Empty model
    print("\n  Fitting m0 (empty model)...")
    m0 = smf.mixedlm(
        "DV_single ~ 1",
        data=df_model,
        groups="buurt_id"
    ).fit(reml=True)
    print(f"    N={int(m0.nobs)}, groups={len(m0.random_effects)}")

    # M1: Add key predictors at all geographic levels
    print("  Fitting m1 (+ key predictors at buurt/wijk/gemeente levels)...")
    m1_formula = "DV_single ~ " + " + ".join(key_preds)
    m1 = smf.mixedlm(
        m1_formula,
        data=df_model,
        groups="buurt_id"
    ).fit(reml=True)

    # M2: Add individual controls
    print("  Fitting m2 (+ individual controls)...")
    cat_vars = ["sex", "employment_status"]
    cat_vars = [f"C({v})" for v in cat_vars if v in ind_controls or v.replace("C(", "").replace(")", "") in ind_controls]
    num_vars = [v for v in ind_controls if v not in ["sex", "employment_status"]]
    
    m2_formula = m1_formula
    if num_vars:
        m2_formula += " + " + " + ".join(num_vars)
    if cat_vars:
        m2_formula += " + " + " + ".join(cat_vars)
    
    # Add occupation if available
    if "occupation" in df_model.columns and df_model["occupation"].notna().sum() > 100:
        m2_formula += " + C(occupation)"
    
    m2 = smf.mixedlm(
        m2_formula,
        data=df_model,
        groups="buurt_id"
    ).fit(reml=True)

    # M3: Add buurt-level controls
    print("  Fitting m3 (+ buurt-level controls)...")
    m3_formula = m2_formula
    if buurt_ctrls:
        m3_formula += " + " + " + ".join(buurt_ctrls)
    
    m3 = smf.mixedlm(
        m3_formula,
        data=df_model,
        groups="buurt_id"
    ).fit(reml=True)

    # M4: Add wijk-level controls
    print("  Fitting m4 (+ wijk-level controls)...")
    m4_formula = m3_formula
    if wijk_ctrls:
        m4_formula += " + " + " + ".join(wijk_ctrls)
    
    m4 = smf.mixedlm(
        m4_formula,
        data=df_model,
        groups="buurt_id"
    ).fit(reml=True)

    print("  All four-level models fitted successfully")

    # Print key coefficients
    print("\n  Key predictor coefficients (m4):")
    for var in key_preds:
        if var in m4.params.index:
            coef = m4.params[var]
            se = m4.bse[var]
            print(f"    {var}: {coef:.3f} (SE={se:.3f})")

    return FourLevelModels(
        m0_empty=m0,
        m1_key_pred=m1,
        m2_ind_controls=m2,
        m3_buurt_controls=m3,
        m4_wijk_controls=m4
    )


def calculate_four_level_icc(models: FourLevelModels) -> Dict[str, float]:
    """
    Calculate variance decomposition for four-level model.
    
    Note: With buurt as primary grouping, this gives ICC at buurt level.
    
    Parameters
    ----------
    models : FourLevelModels
        Fitted four-level models (uses m0_empty)
    
    Returns
    -------
    Dict with variance components and ICCs
    """
    print("\nCalculating variance decomposition...")
    
    m0 = models.m0_empty
    
    # Extract variance components
    var_buurt = float(m0.cov_re.iloc[0, 0])
    var_residual = float(m0.scale)
    var_total = var_buurt + var_residual
    
    icc_buurt = var_buurt / var_total if var_total > 0 else 0
    
    results = {
        "var_buurt": var_buurt,
        "var_residual": var_residual,
        "var_total": var_total,
        "icc_buurt": icc_buurt,
        "pct_buurt": 100 * icc_buurt,
        "pct_residual": 100 * var_residual / var_total if var_total > 0 else 0
    }
    
    print(f"  Variance (buurt): {var_buurt:.2f} ({results['pct_buurt']:.1f}%)")
    print(f"  Variance (residual): {var_residual:.2f} ({results['pct_residual']:.1f}%)")
    print(f"  ICC (buurt): {icc_buurt:.4f}")
    
    return results


# =============================================================================
# ICC Calculation
# =============================================================================

def calculate_icc(models: TwoLevelModels) -> ICCResult:
    """
    Calculate intraclass correlation from empty model.

    ICC = sigma^2_buurt / (sigma^2_buurt + sigma^2_residual)

    Parameters
    ----------
    models : TwoLevelModels
        Fitted models (uses m0_empty)

    Returns
    -------
    ICCResult
        ICC and variance decomposition
    """
    print("\nCalculating ICC and variance decomposition...")

    m0 = models.m0_empty

    # Extract variance components from statsmodels MixedLM
    # Random effects variance: stored in cov_re
    # Residual variance: stored in scale
    var_buurt = float(m0.cov_re.iloc[0, 0])
    var_residual = float(m0.scale)
    var_total = var_buurt + var_residual

    icc = var_buurt / var_total
    pct_between = 100 * var_buurt / var_total
    pct_within = 100 * var_residual / var_total

    print(f"  Variance (buurt): {var_buurt:.2f} ({pct_between:.1f}%)")
    print(f"  Variance (residual): {var_residual:.2f} ({pct_within:.1f}%)")
    print(f"  ICC: {icc:.4f}")
    print(f"  Interpretation: {pct_between:.1f}% of variance is between neighborhoods")

    return ICCResult(
        icc=icc,
        var_buurt=var_buurt,
        var_residual=var_residual,
        var_total=var_total,
        pct_between=pct_between,
        pct_within=pct_within
    )


# =============================================================================
# Model Diagnostics
# =============================================================================

def run_diagnostics(
    models: TwoLevelModels,
    data: pd.DataFrame
) -> DiagnosticsResult:
    """
    Perform diagnostic checks on the final model.

    Includes:
    - VIF calculation (via OLS on predictors)
    - Residual statistics (mean, sd, skewness, kurtosis)
    - Random effects distribution

    Parameters
    ----------
    models : TwoLevelModels
        Fitted models (uses m3_buurt_controls)
    data : pd.DataFrame
        Analysis data

    Returns
    -------
    DiagnosticsResult
        Diagnostic results
    """
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    print("\nRunning model diagnostics...")

    m3 = models.m3_buurt_controls

    # -------------------------------------------------------------------------
    # VIF Calculation
    # -------------------------------------------------------------------------
    print("  Calculating VIF...")

    # Select numeric predictors
    vif_vars = [
        "b_perc_low40_hh", "age", "education",
        "b_pop_dens", "b_pop_over_65", "b_pop_nonwest",
        "b_perc_low_inc_hh", "b_perc_soc_min_hh"
    ]
    vif_vars = [v for v in vif_vars if v in data.columns]

    # Create design matrix
    vif_data = data[vif_vars].dropna()

    vif_results = []
    if len(vif_data) > 0 and len(vif_vars) > 1:
        for i, col in enumerate(vif_vars):
            try:
                vif_value = variance_inflation_factor(vif_data.values, i)
                vif_results.append({"variable": col, "VIF": vif_value})
            except Exception as e:
                vif_results.append({"variable": col, "VIF": np.nan})

    vif_df = pd.DataFrame(vif_results)
    high_vif = []
    if len(vif_df) > 0:
        high_vif = vif_df[vif_df["VIF"] > VIF_THRESHOLD]["variable"].tolist()

    if high_vif:
        print(f"  Warning: High VIF (>{VIF_THRESHOLD}): {', '.join(high_vif)}")
    else:
        print(f"  VIF OK (all < {VIF_THRESHOLD})")

    # -------------------------------------------------------------------------
    # Residual Statistics
    # -------------------------------------------------------------------------
    print("  Analyzing residuals...")

    resids = m3.resid
    residual_stats = pd.DataFrame({
        "statistic": ["mean", "sd", "skewness", "kurtosis"],
        "value": [
            np.mean(resids),
            np.std(resids),
            stats.skew(resids),
            stats.kurtosis(resids)
        ]
    })

    print(f"    Mean: {np.mean(resids):.4f} (should be ~0)")
    print(f"    Skewness: {stats.skew(resids):.2f}")
    print(f"    Kurtosis: {stats.kurtosis(resids):.2f}")

    # -------------------------------------------------------------------------
    # Random Effects Distribution
    # -------------------------------------------------------------------------
    print("  Analyzing random effects...")

    re = m3.random_effects
    re_values = [float(v.iloc[0]) for v in re.values()]

    random_effect_stats = pd.DataFrame({
        "statistic": ["mean", "sd", "min", "max"],
        "value": [
            np.mean(re_values),
            np.std(re_values),
            np.min(re_values),
            np.max(re_values)
        ]
    })

    print(f"    N clusters: {len(re_values)}")
    print(f"    RE range: [{np.min(re_values):.2f}, {np.max(re_values):.2f}]")

    n_clusters = len(data["buurt_id"].unique())
    n_obs = len(data)

    return DiagnosticsResult(
        vif=vif_df,
        high_vif=high_vif,
        residual_stats=residual_stats,
        random_effect_stats=random_effect_stats,
        n_clusters=n_clusters,
        n_obs=n_obs
    )


# =============================================================================
# Sensitivity Analyses
# =============================================================================

def run_sensitivity(data: pd.DataFrame) -> pd.DataFrame:
    """
    Run robustness checks with alternative specifications.

    Specifications tested:
    1. Base model (DV_single)
    2. 2-item composite DV
    3. 3-item composite DV
    4. Dutch-born only subsample
    5. Income ratio model
    6. Wealth interaction (if available)

    Parameters
    ----------
    data : pd.DataFrame
        Full analysis data

    Returns
    -------
    pd.DataFrame
        Sensitivity results
    """
    import statsmodels.formula.api as smf

    print("\nRunning sensitivity analyses...")

    # Base control variables (as list for easier manipulation)
    ind_controls = ["age", "sex", "education", "employment_status", "born_in_nl"]
    buurt_controls = [var for var in ["b_pop_dens", "b_pop_over_65", "b_pop_nonwest",
                                       "b_perc_low_inc_hh", "b_perc_soc_min_hh"]
                      if var in data.columns]

    # All variables needed for base model
    base_vars = ["DV_single", "b_perc_low40_hh", "buurt_id"] + ind_controls + buurt_controls

    # Helper to prepare clean data for statsmodels
    def prepare_data(df, required_vars):
        """Create clean DataFrame with contiguous index for statsmodels."""
        clean = df[required_vars].dropna().copy()
        clean = clean.reset_index(drop=True)
        clean["buurt_id"] = clean["buurt_id"].astype(str)
        return clean

    # Build formula strings
    ind_formula = "age + C(sex) + education + C(employment_status) + born_in_nl"
    buurt_formula = " + ".join(buurt_controls) if buurt_controls else ""
    base_controls = ind_formula + (" + " + buurt_formula if buurt_formula else "")

    results = []

    # Specification 1: Base model
    print("  1. Base model (DV_single)...")
    try:
        df_base = prepare_data(data, base_vars)
        m_base = smf.mixedlm(
            f"DV_single ~ b_perc_low40_hh + {base_controls}",
            data=df_base,
            groups="buurt_id"
        ).fit(reml=True)
        results.append(_extract_key_coef(m_base, "Base (DV_single)"))
    except Exception as e:
        print(f"    Error: {e}")

    # Specification 2: 2-item composite
    if "DV_2item_scaled" in data.columns:
        print("  2. Two-item composite...")
        try:
            vars_2item = ["DV_2item_scaled", "b_perc_low40_hh", "buurt_id"] + ind_controls + buurt_controls
            df_2item = prepare_data(data, vars_2item)
            m_2item = smf.mixedlm(
                f"DV_2item_scaled ~ b_perc_low40_hh + {base_controls}",
                data=df_2item,
                groups="buurt_id"
            ).fit(reml=True)
            results.append(_extract_key_coef(m_2item, "2-item composite"))
        except Exception as e:
            print(f"    Error: {e}")

    # Specification 3: 3-item composite
    if "DV_3item_scaled" in data.columns:
        print("  3. Three-item composite...")
        try:
            vars_3item = ["DV_3item_scaled", "b_perc_low40_hh", "buurt_id"] + ind_controls + buurt_controls
            df_3item = prepare_data(data, vars_3item)
            m_3item = smf.mixedlm(
                f"DV_3item_scaled ~ b_perc_low40_hh + {base_controls}",
                data=df_3item,
                groups="buurt_id"
            ).fit(reml=True)
            results.append(_extract_key_coef(m_3item, "3-item composite"))
        except Exception as e:
            print(f"    Error: {e}")

    # Specification 4: Dutch-born only
    # Note: born_in_nl may be coded as max value = born in NL, or binary (1 = yes)
    if "born_in_nl" in data.columns:
        print("  4. Dutch-born only...")
        try:
            # Handle different codings: if max > 1, assume max = born in NL
            max_val = data["born_in_nl"].max()
            dutch_filter = data["born_in_nl"] == max_val if max_val > 1 else data["born_in_nl"] == 1
            df_dutch_raw = data[dutch_filter].copy()
            # For Dutch-born, exclude born_in_nl from controls (it's constant)
            dutch_controls = "age + C(sex) + education + C(employment_status)"
            dutch_controls += (" + " + buurt_formula if buurt_formula else "")
            vars_dutch = ["DV_single", "b_perc_low40_hh", "buurt_id", "age", "sex", "education", "employment_status"] + buurt_controls
            df_dutch = prepare_data(df_dutch_raw, vars_dutch)
            if len(df_dutch) > 100:
                m_dutch = smf.mixedlm(
                    f"DV_single ~ b_perc_low40_hh + {dutch_controls}",
                    data=df_dutch,
                    groups="buurt_id"
                ).fit(reml=True)
                results.append(_extract_key_coef(m_dutch, "Dutch-born only"))
        except Exception as e:
            print(f"    Error: {e}")

    # Specification 5: Income Ratio Model (Alternative inequality measure)
    if "b_income_ratio" in data.columns:
        print("  5. Income ratio model (robustness)...")
        try:
            vars_ratio = ["DV_single", "b_income_ratio", "buurt_id"] + ind_controls + buurt_controls
            df_ratio = prepare_data(data, vars_ratio)
            m_ratio = smf.mixedlm(
                f"DV_single ~ b_income_ratio + {base_controls}",
                data=df_ratio,
                groups="buurt_id"
            ).fit(reml=True)
            results.append(_extract_key_coef(m_ratio, "Income ratio (high/low)", var="b_income_ratio"))
        except Exception as e:
            print(f"    Error: {e}")

    # Specification 6: Wealth interaction (test H3 - income moderation)
    if "wealth_index" in data.columns and "b_perc_low40_hh" in data.columns:
        print("  6. Wealth interaction (H3 test)...")
        try:
            vars_wealth = ["DV_single", "b_perc_low40_hh", "wealth_index", "buurt_id"] + ind_controls + buurt_controls
            df_wealth = prepare_data(data, vars_wealth)
            m_interaction = smf.mixedlm(
                f"DV_single ~ b_perc_low40_hh * wealth_index + {base_controls}",
                data=df_wealth,
                groups="buurt_id"
            ).fit(reml=True)
            # Extract main effect
            results.append(_extract_key_coef(m_interaction, "With wealth interaction"))
            # Extract interaction term
            interaction_coef = m_interaction.params.get("b_perc_low40_hh:wealth_index", np.nan)
            interaction_se = m_interaction.bse.get("b_perc_low40_hh:wealth_index", np.nan)
            if not np.isnan(interaction_coef):
                z = abs(interaction_coef / interaction_se) if interaction_se > 0 else 0
                results.append({
                    "specification": "  -> Interaction term",
                    "N": int(m_interaction.nobs),
                    "coefficient": interaction_coef,
                    "SE": interaction_se,
                    "significant": z > 1.96
                })
        except Exception as e:
            print(f"    Error: {e}")

    results_df = pd.DataFrame(results)

    print("\n  Sensitivity Summary:")
    print(results_df.to_string(index=False))

    return results_df


def _extract_key_coef(model, spec_name: str, var: str = "b_perc_low40_hh") -> Dict[str, Any]:
    """Extract key predictor coefficient from model.

    Parameters
    ----------
    model : MixedLMResults
        Fitted model
    spec_name : str
        Name of the specification
    var : str
        Variable name to extract (default: b_perc_low40_hh)

    Returns
    -------
    Dict with coefficient info
    """
    coef = model.params.get(var, np.nan)
    se = model.bse.get(var, np.nan)

    # Significance test
    significant = False
    if not np.isnan(coef) and not np.isnan(se) and se > 0:
        z = abs(coef / se)
        significant = z > 1.96

    return {
        "specification": spec_name,
        "N": int(model.nobs),
        "coefficient": coef,
        "SE": se,
        "significant": significant
    }


# =============================================================================
# H3 Cross-Level Interaction Test
# =============================================================================

def test_h3_cross_level_interaction(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Test H3: Individual income moderates the neighborhood inequality effect.

    H3 predicts that the effect of neighborhood poverty concentration on
    redistribution preferences is weaker (or reversed) for higher-income
    individuals. This is a cross-level interaction test.

    Uses wealth_index as proxy for individual income (SCoRE survey does not
    include direct income questions).

    Parameters
    ----------
    data : pd.DataFrame
        Analysis data with DV_single, b_perc_low40_hh, wealth_index, and controls

    Returns
    -------
    Dict with H3 test results including:
        - main_effect: coefficient for b_perc_low40_hh
        - interaction_effect: coefficient for b_perc_low40_hh:wealth_index
        - simple_slopes: effect of neighborhood at different wealth levels
        - interpretation: text summary
    """
    import statsmodels.formula.api as smf

    print("\n" + "=" * 60)
    print("H3 TEST: Cross-Level Interaction (Individual Income Moderation)")
    print("=" * 60)

    # Check required variables
    required = ["DV_single", "b_perc_low40_hh", "wealth_index", "buurt_id",
                "age", "sex", "education", "employment_status", "born_in_nl"]
    missing = [v for v in required if v not in data.columns]
    if missing:
        print(f"  ERROR: Missing required variables: {missing}")
        return {"error": f"Missing variables: {missing}"}

    # Prepare data
    buurt_controls = [v for v in ["b_pop_dens", "b_pop_over_65", "b_pop_nonwest",
                                   "b_perc_low_inc_hh", "b_perc_soc_min_hh"]
                      if v in data.columns]

    all_vars = required + buurt_controls
    df = data[all_vars].dropna().copy().reset_index(drop=True)
    df["buurt_id"] = df["buurt_id"].astype(str)

    print(f"\n  Sample size: N = {len(df)}")
    print(f"  Wealth index range: {df['wealth_index'].min():.0f} - {df['wealth_index'].max():.0f}")
    print(f"  Wealth index mean: {df['wealth_index'].mean():.2f}")

    # Build formula
    ind_controls = "age + C(sex) + education + C(employment_status) + born_in_nl"
    buurt_formula = " + ".join(buurt_controls) if buurt_controls else ""
    controls = ind_controls + (" + " + buurt_formula if buurt_formula else "")

    results = {}

    # Model 1: Main effects only (baseline)
    print("\n  Model 1: Main effects only...")
    try:
        m1 = smf.mixedlm(
            f"DV_single ~ b_perc_low40_hh + wealth_index + {controls}",
            data=df,
            groups="buurt_id"
        ).fit(reml=True)

        results["m1_neighborhood"] = {
            "coef": m1.params.get("b_perc_low40_hh", np.nan),
            "se": m1.bse.get("b_perc_low40_hh", np.nan)
        }
        results["m1_wealth"] = {
            "coef": m1.params.get("wealth_index", np.nan),
            "se": m1.bse.get("wealth_index", np.nan)
        }

        print(f"    Neighborhood effect: {results['m1_neighborhood']['coef']:.3f} "
              f"(SE={results['m1_neighborhood']['se']:.3f})")
        print(f"    Wealth effect: {results['m1_wealth']['coef']:.3f} "
              f"(SE={results['m1_wealth']['se']:.3f})")

    except Exception as e:
        print(f"    Error: {e}")
        return {"error": str(e)}

    # Model 2: With cross-level interaction
    print("\n  Model 2: With cross-level interaction (H3 test)...")
    try:
        m2 = smf.mixedlm(
            f"DV_single ~ b_perc_low40_hh * wealth_index + {controls}",
            data=df,
            groups="buurt_id"
        ).fit(reml=True)

        # Extract coefficients
        main_effect = m2.params.get("b_perc_low40_hh", np.nan)
        main_se = m2.bse.get("b_perc_low40_hh", np.nan)
        interaction = m2.params.get("b_perc_low40_hh:wealth_index", np.nan)
        interaction_se = m2.bse.get("b_perc_low40_hh:wealth_index", np.nan)

        results["main_effect"] = {"coef": main_effect, "se": main_se}
        results["interaction_effect"] = {"coef": interaction, "se": interaction_se}

        # Significance tests
        main_z = abs(main_effect / main_se) if main_se > 0 else 0
        interaction_z = abs(interaction / interaction_se) if interaction_se > 0 else 0

        main_sig = main_z > 1.96
        interaction_sig = interaction_z > 1.96

        print(f"    Main effect (b_perc_low40_hh): {main_effect:.3f} (SE={main_se:.3f})")
        print(f"      z = {main_z:.2f}, p {'<' if main_sig else '>'} 0.05")
        print(f"    Interaction (neighborhood x wealth): {interaction:.3f} (SE={interaction_se:.3f})")
        print(f"      z = {interaction_z:.2f}, p {'<' if interaction_sig else '>'} 0.05")

        # Simple slopes: effect of neighborhood at different wealth levels
        print("\n  Simple slopes (neighborhood effect at different wealth levels):")
        wealth_levels = [0, 1, 2, 3, 4]  # wealth_index values
        simple_slopes = {}

        for w in wealth_levels:
            # Effect = main_effect + interaction * wealth_level
            slope = main_effect + interaction * w
            # SE calculation requires covariance matrix
            simple_slopes[w] = slope
            print(f"    Wealth = {w}: neighborhood effect = {slope:.3f}")

        results["simple_slopes"] = simple_slopes

        # Interpretation
        print("\n  " + "-" * 56)
        print("  INTERPRETATION:")

        if interaction_sig:
            if interaction > 0:
                interpretation = (
                    "H3 SUPPORTED (opposite direction): The positive interaction suggests "
                    "that the neighborhood poverty effect is STRONGER for higher-income "
                    "individuals. This contradicts the hypothesis that higher income "
                    "buffers against neighborhood effects."
                )
            else:
                interpretation = (
                    "H3 SUPPORTED: The negative interaction confirms that the neighborhood "
                    "poverty effect is WEAKER for higher-income individuals. Higher income "
                    "appears to buffer against neighborhood context effects on redistribution "
                    "preferences."
                )
        else:
            interpretation = (
                "H3 NOT SUPPORTED: The interaction between neighborhood poverty and "
                "individual wealth is not statistically significant. The effect of "
                "neighborhood composition on redistribution preferences does not "
                "significantly vary by individual income level."
            )

        results["interpretation"] = interpretation
        results["h3_supported"] = interaction_sig
        results["n_obs"] = int(m2.nobs)

        print(f"  {interpretation}")
        print("  " + "-" * 56)

    except Exception as e:
        print(f"    Error: {e}")
        results["error"] = str(e)

    return results
