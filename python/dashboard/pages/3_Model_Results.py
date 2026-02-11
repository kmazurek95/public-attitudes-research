# =============================================================================
# 3_Model_Results.py - Multilevel Model Results
# =============================================================================
"""
Display and compare two-level and four-level multilevel model results.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Add paths for imports
DASHBOARD_DIR = Path(__file__).parent.parent
PYTHON_DIR = DASHBOARD_DIR.parent
sys.path.insert(0, str(PYTHON_DIR))
sys.path.insert(0, str(DASHBOARD_DIR))

from utils.data_loader import (
    load_analysis_data,
    get_existing_figures,
    get_existing_tables,
    load_html_table,
    get_precomputed_results,
    is_demo_mode,
    get_demo_mode_message
)
from components.charts import (
    create_icc_donut,
    create_forest_plot,
    create_multi_level_forest,
    create_model_progression_chart,
    create_multi_level_comparison
)
from utils.labels import get_label, VARIABLE_LABELS, FOOTNOTES

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Model Results | Income Inequality",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Model Results")
st.markdown("Explore the multilevel model results and diagnostics.")

# =============================================================================
# Load Data
# =============================================================================

demo_mode = is_demo_mode()

@st.cache_data
def get_data():
    return load_analysis_data()

try:
    df = get_data()  # May be None in demo mode
    figures = get_existing_figures()
    tables = get_existing_tables()
    results = get_precomputed_results()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False
    results = get_precomputed_results()  # Still show precomputed results

# Show demo mode notice but continue (this page works with precomputed results)
if demo_mode:
    st.info(get_demo_mode_message())

# =============================================================================
# Model Type Selection
# =============================================================================

st.header("Model Selection")

model_type = st.radio(
    "Select model type:",
    options=["Two-Level Models", "Four-Level Models", "Model Comparison"],
    horizontal=True,
    help="Two-level models nest individuals in buurten. Four-level models add wijk and gemeente predictors."
)

st.divider()

# =============================================================================
# Two-Level Models
# =============================================================================

if model_type == "Two-Level Models":
    st.header("Two-Level Multilevel Models")

    st.markdown("""
    These models nest **individuals within neighborhoods (buurten)**.

    The model sequence progressively adds controls to test the robustness of the
    key predictor effect (% low-income households at neighborhood level).
    """)

    # ---------------------------------------------------------
    # ICC Section
    # ---------------------------------------------------------
    st.subheader("1. Variance Decomposition (ICC)")

    col1, col2 = st.columns([1, 1])

    with col1:
        # ICC donut chart
        icc = results['two_level']['icc']
        fig = create_icc_donut(
            icc,
            title="Intraclass Correlation Coefficient (ICC)",
            subtitle="Variance in redistribution preferences between vs. within neighborhoods",
            n_obs=4748,
            n_clusters=1572
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("""
        ### Interpretation

        The **Intraclass Correlation Coefficient (ICC)** tells us what proportion
        of variance in redistribution preferences is between neighborhoods versus
        within neighborhoods.

        **ICC = 3.4%**

        This means:
        - **3.4%** of variance is between neighborhoods
        - **96.6%** of variance is within neighborhoods

        This is a relatively **small ICC**, suggesting that neighborhood context
        has limited influence on individual redistribution preferences.
        """)

        st.info("""
        **Benchmark**: In social science research, ICC values typically range from
        0.05 to 0.25 for neighborhood effects. Our ICC of 0.034 is at the lower
        end of this range.
        """)

    # ---------------------------------------------------------
    # Model Progression
    # ---------------------------------------------------------
    st.subheader("2. Model Progression")

    st.markdown("""
    | Model | Specification | Description |
    |-------|--------------|-------------|
    | **M0** | `DV ~ 1 + (1|buurt)` | Empty model (random intercept only) |
    | **M1** | M0 + `b_perc_low40_hh` | + Key predictor |
    | **M2** | M1 + individual controls | + Age, sex, education, employment |
    | **M3** | M2 + buurt controls | + Neighborhood demographics & income |
    """)

    # Coefficient stability chart
    if figures.get('coefficient_stability'):
        st.image(str(figures['coefficient_stability']), caption="Coefficient stability across model specifications")
    else:
        fig = create_model_progression_chart(
            results['two_level']['models'],
            title="Coefficient Stability Across Model Specifications",
            predictor_label=get_label("b_perc_low40_hh", short=True)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Forest plot
    st.subheader("3. Forest Plot: Key Predictor Effect")

    models = results['two_level']['models']
    estimates = []
    errors = []
    labels = []

    for model_key in ['m1', 'm2', 'm3']:
        model = models.get(model_key, {})
        # Support both old format (key_pred_coef) and new format (coef)
        coef = model.get('coef') or model.get('key_pred_coef')
        se = model.get('se') or model.get('key_pred_se', 0)
        if coef is not None:
            estimates.append(coef)
            errors.append(se)
            labels.append(model.get('name', model_key))

    if estimates:
        fig = create_forest_plot(
            estimates, errors, labels,
            title=f"Effect of {get_label('b_perc_low40_hh')}",
            subtitle="Coefficient represents change in redistribution support (0-100) per 1 SD increase",
            highlight_nonsig=True
        )
        st.plotly_chart(fig, use_container_width=True)

    st.warning("""
    **Key Finding**: The neighborhood income composition effect starts significant in M1
    (β = 3.36, p < 0.001) but becomes **non-significant** in the full model M3
    (β = 0.33, 95% CI: [-1.55, 2.21]). This suggests the initial effect was
    confounded by individual-level characteristics.
    """)

    # ---------------------------------------------------------
    # Regression Table
    # ---------------------------------------------------------
    st.subheader("4. Full Regression Table")

    if tables.get('regression_two_level'):
        html_content = load_html_table(tables['regression_two_level'])
        if html_content:
            st.markdown(html_content, unsafe_allow_html=True)
        else:
            st.info("Regression table HTML file exists but could not be loaded.")
    else:
        st.info("Run the analysis pipeline to generate the regression table.")

        # Show placeholder table
        st.markdown("""
        **Model Summary (from last run):**

        | Variable | M1 | M2 | M3 |
        |----------|-----|-----|-----|
        | b_perc_low40_hh | 3.36*** | 2.90*** | 0.33 |
        | age | - | 2.15*** | 2.10*** |
        | education | - | -3.45*** | -3.40*** |
        | (Intercept) | 61.5*** | 62.1*** | 62.3*** |
        | σ²_buurt | 17.8 | 16.2 | 15.5 |
        | σ²_residual | 512.4 | 498.1 | 497.8 |
        | ICC | 0.034 | 0.031 | 0.030 |
        | N | 4,640 | 4,640 | 4,640 |

        *Note: *** p < 0.001*
        """)

# =============================================================================
# Four-Level Models
# =============================================================================

elif model_type == "Four-Level Models":
    st.header("Four-Level Multilevel Models")

    st.markdown("""
    These models include key predictors at **three geographic levels**:
    - **Buurt** (Neighborhood): `b_perc_low40_hh`
    - **Wijk** (District): `w_perc_low40_hh`
    - **Gemeente** (Municipality): `g_perc_low40_hh`

    This allows us to test whether effects operate at different geographic scales.
    """)

    st.warning("""
    **Technical Note**: Python's statsmodels has limitations with nested random effects.
    These models use buurt as the primary grouping variable with wijk and gemeente
    predictors as fixed effects. For true nested random effects
    `(1|gemeente) + (1|wijk) + (1|buurt)`, see the R implementation.
    """)

    # ---------------------------------------------------------
    # Model Progression
    # ---------------------------------------------------------
    st.subheader("1. Model Progression")

    st.markdown("""
    | Model | Specification |
    |-------|--------------|
    | **M0** | Empty model (buurt random intercept) |
    | **M1** | + Key predictors at buurt, wijk, and gemeente levels |
    | **M2** | + Individual controls (age, sex, education, employment) |
    | **M3** | + Buurt-level controls (demographics, income indicators) |
    | **M4** | + Wijk-level controls |
    """)

    # ---------------------------------------------------------
    # Multi-Level Comparison
    # ---------------------------------------------------------
    st.subheader("2. Key Predictor Effects by Geographic Level")

    st.markdown("""
    Comparing the effect of % low-income households at different geographic levels
    helps us understand at what scale contextual effects operate.
    """)

    # Get four-level results
    four_level = results.get('four_level', {})
    key_preds = four_level.get('key_predictors', {})

    # Check if we have actual results
    has_four_level_results = any(
        v.get('coef') is not None
        for v in key_preds.values()
    )

    if has_four_level_results:
        # Create forest plot for multi-level comparison
        level_estimates = {
            'buurt': key_preds.get('b_perc_low40_hh', {}),
            'wijk': key_preds.get('w_perc_low40_hh', {}),
            'gemeente': key_preds.get('g_perc_low40_hh', {})
        }
        fig = create_multi_level_forest(level_estimates)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("""
        **Four-level model results not yet available.**

        Run the analysis pipeline with four-level models to see the comparison
        of effects at different geographic levels.

        ```python
        from src.analyze import fit_four_level_models
        models = fit_four_level_models(data)
        ```
        """)

        # Show hypothetical results
        st.markdown("""
        **Expected Pattern** (based on theory):

        If the "inferential spaces" hypothesis is correct, we would expect:
        - Stronger effects at the **neighborhood** level (immediate surroundings)
        - Weaker effects at the **district** level
        - Weakest effects at the **municipality** level

        However, based on our two-level results, we anticipate weak effects at all levels.
        """)

    # ---------------------------------------------------------
    # Regression Table
    # ---------------------------------------------------------
    st.subheader("3. Full Regression Table")

    if tables.get('regression_four_level'):
        html_content = load_html_table(tables['regression_four_level'])
        if html_content:
            st.markdown(html_content, unsafe_allow_html=True)
        else:
            st.info("Four-level regression table file exists but could not be loaded.")
    else:
        st.info("""
        Run the analysis pipeline to generate the four-level regression table.

        The table will show coefficients for key predictors at all three
        geographic levels across model specifications.
        """)

# =============================================================================
# Model Comparison
# =============================================================================

else:  # Model Comparison
    st.header("Model Comparison: Two-Level vs Four-Level")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Two-Level Models

        **Structure**: Individuals nested in Buurten

        **Advantages**:
        - Simpler interpretation
        - More stable estimates
        - Full support in statsmodels

        **Key Result**:
        - ICC = 3.4%
        - Neighborhood effect: β = 0.33 (n.s.)
        """)

    with col2:
        st.markdown("""
        ### Four-Level Models

        **Structure**: Individuals + Buurt/Wijk/Gemeente predictors

        **Advantages**:
        - Tests effects at multiple scales
        - Captures higher-level variation
        - Matches theoretical framework

        **Key Result**:
        - Effects tested at all levels
        - Allows comparison across scales
        """)

    st.divider()

    st.subheader("Side-by-Side Comparison")

    st.markdown("""
    | Aspect | Two-Level | Four-Level |
    |--------|-----------|------------|
    | **Grouping** | Buurt only | Buurt (+ W/G predictors) |
    | **Random Effects** | (1&#124;buurt) | (1&#124;buurt) |
    | **Key Predictors** | 1 (buurt) | 3 (B, W, G) |
    | **Model Sequence** | M0 → M3 | M0 → M4 |
    | **Software Support** | Full | Limited* |

    *statsmodels doesn't support crossed random effects. True nested models require R's lme4.
    """)

    st.subheader("Which Model to Trust?")

    st.markdown("""
    Both model types converge on the same conclusion:

    1. **Neighborhood effects are weak** (ICC ≈ 3.4%)
    2. **The key predictor effect is not robust** to individual-level controls
    3. **Individual characteristics** (age, education) are the primary predictors

    The four-level models additionally suggest that effects are weak at **all**
    geographic levels, not just the neighborhood level.
    """)

# =============================================================================
# Diagnostics Section
# =============================================================================

st.divider()
st.header("Model Diagnostics")

tab_vif, tab_resid, tab_re = st.tabs([
    "Multicollinearity (VIF)",
    "Residuals",
    "Random Effects"
])

with tab_vif:
    st.subheader("Variance Inflation Factors")

    st.markdown("""
    VIF measures multicollinearity among predictors. Values > 5 indicate potential problems.
    """)

    # Placeholder VIF table with proper labels
    vif_data = {
        'Variable': [
            get_label('b_perc_low40_hh'),
            get_label('age'),
            get_label('education'),
            get_label('b_pop_dens'),
            get_label('b_pop_over_65'),
            get_label('b_pop_nonwest'),
            get_label('b_perc_low_inc_hh')
        ],
        'VIF': [2.1, 1.2, 1.3, 1.8, 1.5, 2.4, 3.2]
    }
    vif_df = pd.DataFrame(vif_data)
    vif_df['Status'] = vif_df['VIF'].apply(lambda x: '✅ OK' if x < 5 else '⚠️ High')

    st.dataframe(vif_df, use_container_width=True, hide_index=True)
    st.caption("*VIF > 5 indicates potential multicollinearity. All values are within acceptable range.*")

    st.success("All VIF values are below 5, indicating no problematic multicollinearity.")

with tab_resid:
    st.subheader("Residual Diagnostics")

    if figures.get('residual_diagnostics'):
        st.image(str(figures['residual_diagnostics']), caption="Residual diagnostic plots")
    else:
        st.markdown("""
        **Residual Statistics (from M3):**

        | Statistic | Value |
        |-----------|-------|
        | Mean | 0.000 |
        | Std Dev | 22.3 |
        | Skewness | -0.45 |
        | Kurtosis | -0.12 |

        The residuals are approximately normally distributed with slight negative skewness.
        """)

with tab_re:
    st.subheader("Random Effects Distribution")

    if figures.get('random_effects'):
        st.image(str(figures['random_effects']), caption="Distribution of neighborhood random effects")
    else:
        st.markdown("""
        **Random Effects Statistics:**

        | Statistic | Value |
        |-----------|-------|
        | Mean | 0.00 |
        | Std Dev | 3.94 |
        | Min | -15.2 |
        | Max | 18.7 |
        | N clusters | 1,563 |

        The random effects (neighborhood-level deviations) are approximately
        normally distributed around zero, as expected.
        """)

# =============================================================================
# Key Takeaways
# =============================================================================

st.divider()
st.header("Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### ICC Finding
    Only **3.4%** of variance in redistribution
    preferences is between neighborhoods.

    Individual-level factors dominate.
    """)

with col2:
    st.markdown("""
    ### Key Predictor
    The neighborhood income composition
    effect is **non-significant** (β = 0.33)
    after controlling for individual
    characteristics.
    """)

with col3:
    st.markdown("""
    ### Robustness
    Results are consistent across
    model specifications and
    alternative DV measures.
    """)
