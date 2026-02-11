# =============================================================================
# report.py - Output Generation Module
# =============================================================================
"""
Functions for generating tables, figures, and reports.

Functions:
    create_model_table: Create regression table (HTML)
    create_summary_stats: Create descriptive statistics table
    plot_coefficient_forest: Forest plot of model coefficients
    generate_report: Comprehensive analysis report
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import TABLES_DIR, FIGURES_DIR


# =============================================================================
# Regression Table
# =============================================================================

def create_model_table(
    models,
    output_path: Optional[Path] = None
) -> str:
    """
    Create publication-ready regression table.

    Parameters
    ----------
    models : TwoLevelModels
        Fitted multilevel models
    output_path : Path, optional
        Path to save HTML table

    Returns
    -------
    str
        HTML table string
    """
    from tabulate import tabulate

    print("\nCreating regression table...")

    # Extract results from each model
    model_list = [
        ("Empty", models.m0_empty),
        ("+ Key Pred", models.m1_key_pred),
        ("+ Ind Controls", models.m2_ind_controls),
        ("+ Buurt Controls", models.m3_buurt_controls)
    ]

    # Get all parameter names
    all_params = set()
    for name, model in model_list:
        all_params.update(model.params.index)

    # Remove intercept for cleaner display, keep it separate
    all_params.discard("Intercept")
    all_params.discard("Group Var")

    # Sort parameters
    param_order = [
        "b_perc_low40_hh",
        "age",
        "education",
        "born_in_nl",
        "b_pop_dens",
        "b_pop_over_65",
        "b_pop_nonwest",
        "b_perc_low_inc_hh",
        "b_perc_soc_min_hh"
    ]
    sorted_params = [p for p in param_order if p in all_params]
    sorted_params.extend([p for p in all_params if p not in sorted_params])

    # Build table rows
    rows = []

    # Add intercept first
    intercept_row = ["Intercept"]
    for name, model in model_list:
        if "Intercept" in model.params.index:
            coef = model.params["Intercept"]
            se = model.bse["Intercept"]
            intercept_row.append(f"{coef:.2f} ({se:.2f})")
        else:
            intercept_row.append("")
    rows.append(intercept_row)

    # Add each parameter
    for param in sorted_params:
        row = [_clean_param_name(param)]
        for name, model in model_list:
            if param in model.params.index:
                coef = model.params[param]
                se = model.bse[param]
                stars = _get_stars(coef, se)
                row.append(f"{coef:.3f}{stars} ({se:.3f})")
            else:
                row.append("")
        rows.append(row)

    # Add model statistics
    rows.append(["---", "---", "---", "---", "---"])
    rows.append(["N"] + [str(int(m.nobs)) for _, m in model_list])
    rows.append(["Groups"] + [str(len(m.random_effects)) for _, m in model_list])
    rows.append(["AIC"] + [f"{m.aic:.1f}" for _, m in model_list])
    rows.append(["BIC"] + [f"{m.bic:.1f}" for _, m in model_list])

    # Create table
    headers = ["Variable"] + [name for name, _ in model_list]
    table_str = tabulate(rows, headers=headers, tablefmt="html")

    # Add styling
    html = f"""
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; font-family: Arial, sans-serif; }}
            th, td {{ padding: 8px 12px; text-align: right; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f5f5f5; font-weight: bold; }}
            td:first-child, th:first-child {{ text-align: left; }}
            tr:hover {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h2>Multilevel Regression Results</h2>
        <p><em>DV: Redistribution Preferences (0-100 scale)</em></p>
        {table_str}
        <p><small>* p&lt;0.05, ** p&lt;0.01, *** p&lt;0.001. Standard errors in parentheses.</small></p>
    </body>
    </html>
    """

    # Save if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html)
        print(f"  Saved to {output_path}")

    return html


def create_four_level_table(
    models,
    output_path: Optional[Path] = None
) -> str:
    """
    Create regression table for four-level models.

    Parameters
    ----------
    models : FourLevelModels
        Fitted four-level multilevel models
    output_path : Path, optional
        Path to save HTML table

    Returns
    -------
    str
        HTML table string
    """
    from tabulate import tabulate

    print("\nCreating four-level regression table...")

    # Extract results from each model
    model_list = [
        ("Empty", models.m0_empty),
        ("+ Key Preds", models.m1_key_pred),
        ("+ Ind Ctrls", models.m2_ind_controls),
        ("+ Buurt Ctrls", models.m3_buurt_controls),
        ("+ Wijk Ctrls", models.m4_wijk_controls)
    ]

    # Get all parameter names
    all_params = set()
    for name, model in model_list:
        all_params.update(model.params.index)

    all_params.discard("Intercept")
    all_params.discard("Group Var")

    # Sort parameters - key predictors first
    param_order = [
        "b_perc_low40_hh",
        "w_perc_low40_hh",
        "g_perc_low40_hh",
        "age",
        "education",
        "born_in_nl",
        "b_pop_dens",
        "b_pop_over_65",
        "b_pop_nonwest",
        "b_perc_low_inc_hh",
        "b_perc_soc_min_hh",
        "w_pop_dens",
        "w_pop_over_65",
        "w_pop_nonwest",
        "w_perc_low_inc_hh",
        "w_perc_soc_min_hh"
    ]
    sorted_params = [p for p in param_order if p in all_params]
    sorted_params.extend([p for p in all_params if p not in sorted_params])

    # Build table rows
    rows = []

    # Add intercept first
    intercept_row = ["Intercept"]
    for name, model in model_list:
        if "Intercept" in model.params.index:
            coef = model.params["Intercept"]
            se = model.bse["Intercept"]
            intercept_row.append(f"{coef:.2f} ({se:.2f})")
        else:
            intercept_row.append("")
    rows.append(intercept_row)

    # Add each parameter
    for param in sorted_params:
        row = [_clean_param_name_four_level(param)]
        for name, model in model_list:
            if param in model.params.index:
                coef = model.params[param]
                se = model.bse[param]
                stars = _get_stars(coef, se)
                row.append(f"{coef:.3f}{stars} ({se:.3f})")
            else:
                row.append("")
        rows.append(row)

    # Add model statistics
    rows.append(["---"] * 6)
    rows.append(["N"] + [str(int(m.nobs)) for _, m in model_list])
    rows.append(["Groups (buurt)"] + [str(len(m.random_effects)) for _, m in model_list])
    rows.append(["AIC"] + [f"{m.aic:.1f}" for _, m in model_list])
    rows.append(["BIC"] + [f"{m.bic:.1f}" for _, m in model_list])

    # Create table
    headers = ["Variable"] + [name for name, _ in model_list]
    table_str = tabulate(rows, headers=headers, tablefmt="html")

    # Add styling
    html = f"""
    <html>
    <head>
        <style>
            table {{ border-collapse: collapse; font-family: Arial, sans-serif; }}
            th, td {{ padding: 8px 12px; text-align: right; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f5f5f5; font-weight: bold; }}
            td:first-child, th:first-child {{ text-align: left; }}
            tr:hover {{ background-color: #f9f9f9; }}
        </style>
    </head>
    <body>
        <h2>Four-Level Multilevel Regression Results</h2>
        <p><em>DV: Redistribution Preferences (0-100 scale)</em></p>
        <p><em>Random intercepts: buurt, wijk, gemeente</em></p>
        {table_str}
        <p><small>* p&lt;0.05, ** p&lt;0.01, *** p&lt;0.001. Standard errors in parentheses.</small></p>
    </body>
    </html>
    """

    # Save if path provided
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(html)
        print(f"  Saved to {output_path}")

    return html


def _clean_param_name_four_level(param: str) -> str:
    """Convert parameter names to readable format for four-level models."""
    name_map = {
        "b_perc_low40_hh": "% Low income HH (buurt)",
        "w_perc_low40_hh": "% Low income HH (wijk)",
        "g_perc_low40_hh": "% Low income HH (gemeente)",
        "b_pop_dens": "Pop density (buurt)",
        "b_pop_over_65": "% Over 65 (buurt)",
        "b_pop_nonwest": "% Non-Western (buurt)",
        "b_perc_low_inc_hh": "% Low income (buurt)",
        "b_perc_soc_min_hh": "% Social min (buurt)",
        "w_pop_dens": "Pop density (wijk)",
        "w_pop_over_65": "% Over 65 (wijk)",
        "w_pop_nonwest": "% Non-Western (wijk)",
        "w_perc_low_inc_hh": "% Low income (wijk)",
        "w_perc_soc_min_hh": "% Social min (wijk)",
        "age": "Age (std)",
        "education": "Education (std)",
        "born_in_nl": "Born in Netherlands",
    }

    if param in name_map:
        return name_map[param]

    # Handle categorical variables
    if param.startswith("C("):
        parts = param.replace("C(", "").replace(")", "").replace("[T.", ": ").replace("]", "")
        return parts

    return param


def _clean_param_name(param: str) -> str:
    """Convert parameter names to readable format."""
    name_map = {
        "b_perc_low40_hh": "% Low income HH (buurt)",
        "b_pop_dens": "Population density",
        "b_pop_over_65": "% Over 65",
        "b_pop_nonwest": "% Non-Western",
        "b_perc_low_inc_hh": "% Low income HH",
        "b_perc_soc_min_hh": "% Social minimum",
        "age": "Age (std)",
        "education": "Education (std)",
        "born_in_nl": "Born in Netherlands",
    }

    if param in name_map:
        return name_map[param]

    # Handle categorical variables
    if param.startswith("C("):
        # Extract category name
        parts = param.replace("C(", "").replace(")", "").replace("[T.", ": ").replace("]", "")
        return parts

    return param


def _get_stars(coef: float, se: float) -> str:
    """Get significance stars based on z-test."""
    if se == 0 or np.isnan(se):
        return ""
    z = abs(coef / se)
    if z > 3.29:  # p < 0.001
        return "***"
    elif z > 2.58:  # p < 0.01
        return "**"
    elif z > 1.96:  # p < 0.05
        return "*"
    return ""


# =============================================================================
# Summary Statistics
# =============================================================================

def create_summary_stats(
    data: pd.DataFrame,
    output_path: Optional[Path] = None
) -> pd.DataFrame:
    """
    Create descriptive statistics table.

    Parameters
    ----------
    data : pd.DataFrame
        Analysis data
    output_path : Path, optional
        Path to save CSV

    Returns
    -------
    pd.DataFrame
        Summary statistics
    """
    print("\nCreating summary statistics...")

    # Variables to summarize
    continuous_vars = [
        "DV_single", "age_raw", "educyrs",
        "b_perc_low40_hh", "b_pop_dens", "b_pop_over_65"
    ]
    continuous_vars = [v for v in continuous_vars if v in data.columns]

    stats = []
    for var in continuous_vars:
        vals = data[var].dropna()
        stats.append({
            "Variable": var,
            "N": len(vals),
            "Mean": vals.mean(),
            "SD": vals.std(),
            "Min": vals.min(),
            "Max": vals.max()
        })

    stats_df = pd.DataFrame(stats)

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        stats_df.to_csv(output_path, index=False)
        print(f"  Saved to {output_path}")

    return stats_df


# =============================================================================
# Comprehensive Report
# =============================================================================

@dataclass
class AnalysisReport:
    """Container for complete analysis results."""
    n_obs: int
    n_clusters: int
    merge_validation: List[Any]
    icc: float
    variance_decomposition: Dict[str, float]
    model_comparison: pd.DataFrame
    fixed_effects: pd.DataFrame
    key_coef: float
    key_se: float
    key_ci: tuple
    diagnostics: Dict[str, Any]
    sensitivity: pd.DataFrame


def generate_report(
    models,
    icc_results,
    diagnostics,
    sensitivity: Optional[pd.DataFrame] = None,
    merge_validation: Optional[List] = None,
    output_path: Optional[Path] = None
) -> AnalysisReport:
    """
    Generate comprehensive analysis report.

    Parameters
    ----------
    models : TwoLevelModels
        Fitted models
    icc_results : ICCResult
        ICC calculation results
    diagnostics : DiagnosticsResult
        Model diagnostics
    sensitivity : pd.DataFrame, optional
        Sensitivity analysis results
    merge_validation : list, optional
        Merge validation results
    output_path : Path, optional
        Path to save report

    Returns
    -------
    AnalysisReport
        Complete analysis report
    """
    print("\nGenerating analysis report...")

    m3 = models.m3_buurt_controls

    # Extract key coefficient
    key_coef = m3.params.get("b_perc_low40_hh", np.nan)
    key_se = m3.bse.get("b_perc_low40_hh", np.nan)
    key_ci = (key_coef - 1.96 * key_se, key_coef + 1.96 * key_se)

    # Model comparison
    model_comparison = pd.DataFrame({
        "Model": ["Empty", "+ Key Pred", "+ Ind Controls", "+ Buurt Controls"],
        "AIC": [m.aic for m in [models.m0_empty, models.m1_key_pred,
                                 models.m2_ind_controls, models.m3_buurt_controls]],
        "BIC": [m.bic for m in [models.m0_empty, models.m1_key_pred,
                                 models.m2_ind_controls, models.m3_buurt_controls]],
        "N": [int(m.nobs) for m in [models.m0_empty, models.m1_key_pred,
                                     models.m2_ind_controls, models.m3_buurt_controls]]
    })

    # Fixed effects from final model
    fixed_effects = pd.DataFrame({
        "Parameter": m3.params.index,
        "Estimate": m3.params.values,
        "SE": m3.bse.values,
        "z": m3.tvalues.values,
        "p": m3.pvalues.values
    })

    # Create report object
    report = AnalysisReport(
        n_obs=diagnostics.n_obs,
        n_clusters=diagnostics.n_clusters,
        merge_validation=merge_validation or [],
        icc=icc_results.icc,
        variance_decomposition={
            "between": icc_results.pct_between,
            "within": icc_results.pct_within
        },
        model_comparison=model_comparison,
        fixed_effects=fixed_effects,
        key_coef=key_coef,
        key_se=key_se,
        key_ci=key_ci,
        diagnostics={
            "vif": diagnostics.vif,
            "high_vif": diagnostics.high_vif,
            "residual_stats": diagnostics.residual_stats,
            "random_effect_stats": diagnostics.random_effect_stats
        },
        sensitivity=sensitivity if sensitivity is not None else pd.DataFrame()
    )

    # Print summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"Observations: {report.n_obs}")
    print(f"Clusters (buurten): {report.n_clusters}")
    print(f"ICC: {report.icc:.4f} ({report.variance_decomposition['between']:.1f}% between)")
    print(f"\nKey predictor (b_perc_low40_hh):")
    print(f"  Coefficient: {report.key_coef:.3f}")
    print(f"  SE: {report.key_se:.3f}")
    print(f"  95% CI: [{report.key_ci[0]:.3f}, {report.key_ci[1]:.3f}]")
    print("=" * 60)

    # Save report if path provided
    if output_path:
        _save_report_text(report, output_path)

    return report


def _save_report_text(report: AnalysisReport, output_path: Path) -> None:
    """Save report as text file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write("REDISTRIBUTION PREFERENCES ANALYSIS REPORT\n")
        f.write("=" * 60 + "\n\n")

        f.write("SAMPLE\n")
        f.write("-" * 40 + "\n")
        f.write(f"Observations: {report.n_obs}\n")
        f.write(f"Clusters: {report.n_clusters}\n\n")

        f.write("VARIANCE DECOMPOSITION\n")
        f.write("-" * 40 + "\n")
        f.write(f"ICC: {report.icc:.4f}\n")
        f.write(f"Between neighborhoods: {report.variance_decomposition['between']:.1f}%\n")
        f.write(f"Within neighborhoods: {report.variance_decomposition['within']:.1f}%\n\n")

        f.write("KEY FINDING\n")
        f.write("-" * 40 + "\n")
        f.write(f"b_perc_low40_hh coefficient: {report.key_coef:.3f}\n")
        f.write(f"Standard error: {report.key_se:.3f}\n")
        f.write(f"95% CI: [{report.key_ci[0]:.3f}, {report.key_ci[1]:.3f}]\n\n")

        f.write("MODEL COMPARISON\n")
        f.write("-" * 40 + "\n")
        f.write(report.model_comparison.to_string(index=False))
        f.write("\n\n")

        if len(report.sensitivity) > 0:
            f.write("SENSITIVITY ANALYSES\n")
            f.write("-" * 40 + "\n")
            f.write(report.sensitivity.to_string(index=False))
            f.write("\n")

    print(f"  Report saved to {output_path}")
