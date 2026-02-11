# =============================================================================
# labels.py - Human-Readable Variable Labels and Formatting
# =============================================================================
"""
Centralized variable labels for professional visualization.
Use these labels consistently across all dashboard pages.
"""

# =============================================================================
# Variable Labels (Technical Name → Display Label)
# =============================================================================

VARIABLE_LABELS = {
    # Dependent Variables
    "DV_single": "Support for Redistribution (0-100)",
    "DV_2item_scaled": "Support for Redistribution (2-Item, 0-100)",
    "DV_3item_scaled": "Support for Redistribution (3-Item, 0-100)",

    # Key Predictors
    "b_perc_low40_hh": "% Low-Income Households (Neighborhood)",
    "w_perc_low40_hh": "% Low-Income Households (District)",
    "g_perc_low40_hh": "% Low-Income Households (Municipality)",
    "b_income_ratio": "Income Ratio (High/Low, Neighborhood)",

    # Buurt-level Controls
    "b_pop_dens": "Population Density (per km²)",
    "b_pop_over_65": "% Residents Age 65+",
    "b_pop_nonwest": "% Non-Western Background",
    "b_perc_low_inc_hh": "% Below Social Minimum",
    "b_perc_high20_hh": "% High-Income Households",

    # Wijk-level Variables
    "w_pop_dens": "Population Density (District)",
    "w_pop_over_65": "% Residents Age 65+ (District)",
    "w_pop_nonwest": "% Non-Western Background (District)",

    # Gemeente-level Variables
    "g_pop_dens": "Population Density (Municipality)",
    "g_pop_over_65": "% Residents Age 65+ (Municipality)",
    "g_pop_nonwest": "% Non-Western Background (Municipality)",

    # Individual-level Variables
    "age": "Age (Standardized)",
    "age_raw": "Age (Years)",
    "sex": "Sex",
    "education": "Education Level (Standardized)",
    "employment_status": "Employment Status",
    "born_in_nl": "Born in Netherlands",
    "wealth_index": "Wealth Index (0-4)",

    # Geographic Identifiers
    "buurt_id": "Neighborhood ID",
    "wijk_id": "District ID",
    "gemeente_id": "Municipality ID",
}

# Short labels for charts with limited space
VARIABLE_LABELS_SHORT = {
    "b_perc_low40_hh": "% Low-Income HH",
    "w_perc_low40_hh": "% Low-Income HH (Wijk)",
    "g_perc_low40_hh": "% Low-Income HH (Gem.)",
    "b_pop_dens": "Pop. Density",
    "b_pop_over_65": "% Age 65+",
    "b_pop_nonwest": "% Non-Western",
    "DV_single": "Redistribution Support",
}

# =============================================================================
# Geographic Level Labels
# =============================================================================

GEOGRAPHIC_LEVELS = {
    "buurt": "Neighborhood (Buurt)",
    "wijk": "District (Wijk)",
    "gemeente": "Municipality (Gemeente)",
    "individual": "Individual",
}

GEOGRAPHIC_LEVELS_SHORT = {
    "buurt": "Neighborhood",
    "wijk": "District",
    "gemeente": "Municipality",
}

# =============================================================================
# Model Labels
# =============================================================================

MODEL_LABELS = {
    "m0": "M0: Empty Model",
    "m1": "M1: + Key Predictor",
    "m2": "M2: + Individual Controls",
    "m3": "M3: + Neighborhood Controls",
    "m4": "M4: + District Controls",
}

MODEL_DESCRIPTIONS = {
    "m0": "Random intercept only",
    "m1": "Bivariate (% low-income HH)",
    "m2": "Age, sex, education, employment",
    "m3": "Full controls",
    "m4": "Full + wijk controls",
}

# =============================================================================
# Hypothesis Labels
# =============================================================================

HYPOTHESIS_LABELS = {
    "h1": "H1: Neighborhood Effect",
    "h2": "H2: Proximity Effect",
    "h3": "H3: Income Moderation",
}

HYPOTHESIS_RESULTS = {
    "supported": "Supported",
    "not_supported": "Not Supported",
    "inconclusive": "Inconclusive",
}

# =============================================================================
# Formatting Utilities
# =============================================================================

def get_label(var_name: str, short: bool = False) -> str:
    """
    Get human-readable label for a variable name.

    Parameters
    ----------
    var_name : str
        Technical variable name
    short : bool
        If True, return shorter label for constrained space

    Returns
    -------
    str
        Human-readable label
    """
    if short:
        return VARIABLE_LABELS_SHORT.get(var_name, VARIABLE_LABELS.get(var_name, var_name))
    return VARIABLE_LABELS.get(var_name, var_name)


def get_model_label(model_key: str) -> str:
    """Get display label for a model."""
    return MODEL_LABELS.get(model_key.lower(), model_key)


def get_geo_label(level: str, short: bool = False) -> str:
    """Get label for a geographic level."""
    if short:
        return GEOGRAPHIC_LEVELS_SHORT.get(level.lower(), level)
    return GEOGRAPHIC_LEVELS.get(level.lower(), level)


def format_coefficient(coef: float, se: float = None, p: float = None) -> str:
    """
    Format a coefficient for display with optional significance stars.

    Parameters
    ----------
    coef : float
        Coefficient value
    se : float, optional
        Standard error
    p : float, optional
        P-value for significance stars

    Returns
    -------
    str
        Formatted coefficient string
    """
    stars = ""
    if p is not None:
        if p < 0.001:
            stars = "***"
        elif p < 0.01:
            stars = "**"
        elif p < 0.05:
            stars = "*"

    if se is not None:
        return f"{coef:.3f}{stars} ({se:.3f})"
    return f"{coef:.3f}{stars}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a value as a percentage."""
    return f"{value * 100:.{decimals}f}%"


def format_number(value: float, decimals: int = 2, thousands_sep: bool = True) -> str:
    """Format a number with optional thousands separator."""
    if thousands_sep and abs(value) >= 1000:
        return f"{value:,.{decimals}f}"
    return f"{value:.{decimals}f}"


# =============================================================================
# Chart Configuration
# =============================================================================

CHART_CONFIG = {
    "font_family": "Arial, sans-serif",
    "title_font_size": 16,
    "axis_font_size": 12,
    "annotation_font_size": 10,
}

# Standard footnotes
FOOTNOTES = {
    "significance": "* p < 0.05, ** p < 0.01, *** p < 0.001",
    "data_source": "Data: SCoRE Netherlands 2017, CBS StatLine 2018",
    "ci": "Error bars show 95% confidence intervals",
    "standardized": "Variables standardized (mean=0, SD=1)",
}
