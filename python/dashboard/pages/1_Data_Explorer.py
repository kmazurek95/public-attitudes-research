# =============================================================================
# 1_Data_Explorer.py - Data Exploration Page
# =============================================================================
"""
Interactive exploration of survey and administrative data.
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
    get_column_info,
    get_existing_figures,
    get_filtered_data,
    is_demo_mode,
    get_demo_mode_message
)
from components.charts import (
    create_distribution_histogram,
    create_multi_distribution,
    create_boxplot_by_group
)
from utils.labels import get_label, VARIABLE_LABELS, FOOTNOTES

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Data Explorer | Income Inequality",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Data Explorer")
st.markdown("Explore the survey and administrative data used in this analysis.")

# =============================================================================
# Load Data
# =============================================================================

# Check for demo mode
if is_demo_mode():
    st.warning(get_demo_mode_message())
    st.info("""
    **Data Explorer requires raw data.**

    In demo mode, you can view:
    - [Model Results](/Model_Results) - Precomputed analysis results
    - [Key Findings](/Key_Findings) - Summary of conclusions

    To enable full data exploration, ensure the analysis data file is present.
    """)
    st.stop()

@st.cache_data
def get_data():
    return load_analysis_data()

try:
    df = get_data()
    if df is None:
        st.error("Data file not found. Running in demo mode.")
        st.stop()
    col_info = get_column_info(df)
    figures = get_existing_figures()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

if not data_loaded:
    st.stop()

# =============================================================================
# Sidebar Filters
# =============================================================================

with st.sidebar:
    st.header("Filters")

    # Municipality filter
    gemeenten = sorted(df['gemeente_id'].dropna().unique().astype(str).tolist())
    selected_gemeenten = st.multiselect(
        "Municipality (Gemeente)",
        options=gemeenten,
        default=[],
        help="Filter by municipality. Leave empty for all."
    )

    # Education filter
    if 'education' in df.columns:
        edu_min, edu_max = float(df['education'].min()), float(df['education'].max())
        education_range = st.slider(
            "Education (standardized)",
            min_value=edu_min,
            max_value=edu_max,
            value=(edu_min, edu_max),
            help="Filter by standardized education score"
        )
    else:
        education_range = None

    # Employment filter
    if 'employment_status' in df.columns:
        employment_options = df['employment_status'].dropna().unique().tolist()
        selected_employment = st.multiselect(
            "Employment Status",
            options=employment_options,
            default=employment_options,
            help="Filter by employment status"
        )
    else:
        selected_employment = None

    # Apply filters
    st.divider()
    if st.button("Apply Filters", type="primary"):
        st.session_state['filters_applied'] = True

# Apply filters to data
filtered_df = get_filtered_data(
    df,
    gemeente_filter=selected_gemeenten if selected_gemeenten else None,
    education_range=education_range,
    employment_filter=selected_employment
)

# Show filter status
if selected_gemeenten or (education_range and (education_range[0] > df['education'].min() or education_range[1] < df['education'].max())):
    st.info(f"Showing {len(filtered_df):,} of {len(df):,} observations after filtering.")

# =============================================================================
# Survey Data Section
# =============================================================================

st.header("📋 Survey Data: SCoRE Netherlands 2017")

tab_dv, tab_demo, tab_sample = st.tabs([
    "Dependent Variable",
    "Demographics",
    "Sample Overview"
])

# -----------------------------------------------------------------------------
# Dependent Variable Tab
# -----------------------------------------------------------------------------

with tab_dv:
    st.subheader("Distribution of Redistribution Preferences")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Check if we have existing figure
        if figures.get('dv_distribution'):
            st.image(str(figures['dv_distribution']), caption="Distribution of Support for Redistribution")
        else:
            # Create interactive chart
            if 'DV_single' in filtered_df.columns:
                fig = create_distribution_histogram(
                    filtered_df['DV_single'],
                    title="Support for Government Redistribution",
                    xaxis_label=get_label("DV_single"),
                    nbins=50,
                    source_note=FOOTNOTES.get("data_source")
                )
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Variable Description")
        st.markdown("""
        **DV_single** is a single-item measure of support for
        government redistribution, scaled from 0 to 100.

        Based on the survey item:
        > "The government should reduce income differences"

        Higher values indicate stronger support for redistribution.
        """)

        if 'DV_single' in filtered_df.columns:
            st.markdown("#### Summary Statistics")
            dv_stats = filtered_df['DV_single'].describe()
            st.dataframe(dv_stats.round(2), use_container_width=True)

    # Alternative DV measures
    st.subheader("Alternative Dependent Variable Specifications")

    dv_cols = ['DV_single', 'DV_2item_scaled', 'DV_3item_scaled']
    dv_cols = [c for c in dv_cols if c in filtered_df.columns]

    if len(dv_cols) > 1:
        labels = {
            'DV_single': 'Single item (0-100)',
            'DV_2item_scaled': '2-item composite (0-100)',
            'DV_3item_scaled': '3-item composite (0-100)'
        }
        fig = create_multi_distribution(
            filtered_df,
            dv_cols,
            labels=labels,
            title="Comparison of DV Specifications"
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# Demographics Tab
# -----------------------------------------------------------------------------

with tab_demo:
    st.subheader("Demographic Characteristics")

    # Check for existing figure
    if figures.get('individual_vars'):
        st.image(str(figures['individual_vars']), caption="Individual-level variable distributions")
    else:
        col1, col2 = st.columns(2)

        with col1:
            # Age distribution
            if 'age_raw' in filtered_df.columns:
                fig = create_distribution_histogram(
                    filtered_df['age_raw'],
                    title="Age Distribution",
                    xaxis_label="Age (years)",
                    nbins=30
                )
                st.plotly_chart(fig, use_container_width=True)

            # Education distribution
            if 'education' in filtered_df.columns:
                fig = create_distribution_histogram(
                    filtered_df['education'],
                    title="Education Distribution (Standardized)",
                    xaxis_label="Education (z-score)",
                    nbins=30
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Sex breakdown
            if 'sex' in filtered_df.columns:
                sex_counts = filtered_df['sex'].value_counts()
                st.markdown("#### Sex Distribution")
                st.bar_chart(sex_counts)

            # Employment breakdown
            if 'employment_status' in filtered_df.columns:
                emp_counts = filtered_df['employment_status'].value_counts()
                st.markdown("#### Employment Status")
                st.bar_chart(emp_counts)

    # DV by demographics
    st.subheader("Redistribution Preferences by Demographics")

    demo_var = st.selectbox(
        "Select demographic variable:",
        options=['sex', 'employment_status', 'born_in_nl'],
        format_func=lambda x: {
            'sex': 'Sex',
            'employment_status': 'Employment Status',
            'born_in_nl': 'Born in Netherlands'
        }.get(x, x)
    )

    if demo_var in filtered_df.columns and 'DV_single' in filtered_df.columns:
        fig = create_boxplot_by_group(
            filtered_df,
            y_col='DV_single',
            x_col=demo_var,
            title=f"Redistribution Preferences by {demo_var.replace('_', ' ').title()}"
        )
        st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# Sample Overview Tab
# -----------------------------------------------------------------------------

with tab_sample:
    st.subheader("Sample Overview")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Dataset Dimensions")
        st.metric("Rows", f"{len(filtered_df):,}")
        st.metric("Columns", f"{len(filtered_df.columns):,}")

        st.markdown("#### Column Categories")
        st.write(f"- **Buurt-level variables**: {len(col_info['buurt'])}")
        st.write(f"- **Wijk-level variables**: {len(col_info['wijk'])}")
        st.write(f"- **Gemeente-level variables**: {len(col_info['gemeente'])}")
        st.write(f"- **Individual-level variables**: {len(col_info['individual'])}")
        st.write(f"- **Dependent variables**: {len(col_info['dv'])}")

    with col2:
        st.markdown("#### Missing Data Summary")
        missing = filtered_df.isnull().sum()
        missing_pct = (missing / len(filtered_df) * 100).round(1)
        missing_df = pd.DataFrame({
            'Missing': missing,
            'Percent': missing_pct
        })
        missing_df = missing_df[missing_df['Missing'] > 0].sort_values('Missing', ascending=False).head(15)
        if len(missing_df) > 0:
            st.dataframe(missing_df, use_container_width=True)
        else:
            st.success("No missing data in selected columns!")

    # Data preview
    st.subheader("Data Preview")
    st.dataframe(filtered_df.head(100), use_container_width=True, height=400)


# =============================================================================
# Administrative Data Section
# =============================================================================

st.divider()
st.header("📊 Administrative Data: CBS Statistics")

tab_buurt, tab_wijk, tab_gemeente, tab_corr = st.tabs([
    "Buurt (Neighborhood)",
    "Wijk (District)",
    "Gemeente (Municipality)",
    "Correlations"
])

# -----------------------------------------------------------------------------
# Buurt Tab
# -----------------------------------------------------------------------------

with tab_buurt:
    st.subheader("Buurt-level Variables")

    st.markdown("""
    **Buurt** (neighborhood) is the smallest geographic unit in the Dutch administrative hierarchy.
    These variables are measured at the neighborhood level from CBS administrative data.
    """)

    # Key predictor distribution
    st.markdown("#### Key Predictor: % Low-Income Households")

    col1, col2 = st.columns([2, 1])

    with col1:
        if 'b_perc_low40_hh' in filtered_df.columns:
            fig = create_distribution_histogram(
                filtered_df['b_perc_low40_hh'],
                title="Distribution of Key Predictor",
                xaxis_label=get_label("b_perc_low40_hh") + " (standardized)",
                nbins=40,
                source_note=FOOTNOTES.get("data_source")
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
        **{get_label("b_perc_low40_hh")}**

        Percentage of households in the bottom 40%
        of the national income distribution.

        This is the **key predictor** in our models,
        capturing neighborhood socioeconomic composition.
        """)

        if 'b_perc_low40_hh' in filtered_df.columns:
            st.markdown("**Summary:**")
            st.dataframe(filtered_df['b_perc_low40_hh'].describe().round(3))

    # Other buurt variables
    st.markdown("#### Other Buurt-level Variables")

    buurt_vars = col_info['buurt']
    if buurt_vars:
        selected_buurt = st.multiselect(
            "Select variables to display:",
            options=buurt_vars,
            default=buurt_vars[:5] if len(buurt_vars) >= 5 else buurt_vars
        )

        if selected_buurt:
            st.dataframe(
                filtered_df[selected_buurt].describe().T.round(3),
                use_container_width=True
            )

# -----------------------------------------------------------------------------
# Wijk Tab
# -----------------------------------------------------------------------------

with tab_wijk:
    st.subheader("Wijk-level Variables")

    st.markdown("""
    **Wijk** (district) is an intermediate geographic level, aggregating multiple buurten.
    """)

    if 'w_perc_low40_hh' in filtered_df.columns:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = create_distribution_histogram(
                filtered_df['w_perc_low40_hh'],
                title="Distribution of % Low-Income Households (Wijk level)",
                xaxis_label="w_perc_low40_hh (standardized)",
                nbins=40
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**w_perc_low40_hh**")
            st.dataframe(filtered_df['w_perc_low40_hh'].describe().round(3))

    wijk_vars = col_info['wijk']
    if wijk_vars:
        st.markdown("#### All Wijk-level Variables")
        st.dataframe(
            filtered_df[wijk_vars].describe().T.round(3),
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# Gemeente Tab
# -----------------------------------------------------------------------------

with tab_gemeente:
    st.subheader("Gemeente-level Variables")

    st.markdown("""
    **Gemeente** (municipality) is the largest geographic level, representing local government units.
    """)

    if 'g_perc_low40_hh' in filtered_df.columns:
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = create_distribution_histogram(
                filtered_df['g_perc_low40_hh'],
                title="Distribution of % Low-Income Households (Gemeente level)",
                xaxis_label="g_perc_low40_hh (standardized)",
                nbins=40
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("**g_perc_low40_hh**")
            st.dataframe(filtered_df['g_perc_low40_hh'].describe().round(3))

    gemeente_vars = col_info['gemeente']
    if gemeente_vars:
        st.markdown("#### All Gemeente-level Variables")
        st.dataframe(
            filtered_df[gemeente_vars].describe().T.round(3),
            use_container_width=True
        )

# -----------------------------------------------------------------------------
# Correlations Tab
# -----------------------------------------------------------------------------

with tab_corr:
    st.subheader("Variable Correlations")

    # Show existing correlation figure if available
    if figures.get('buurt_correlations'):
        st.image(str(figures['buurt_correlations']), caption="Buurt-level variable correlations")
    else:
        st.markdown("#### Correlation Matrix (Buurt-level variables)")

        buurt_numeric = filtered_df[col_info['buurt']].select_dtypes(include=['float64', 'int64'])
        if len(buurt_numeric.columns) > 0:
            corr_matrix = buurt_numeric.corr().round(2)
            st.dataframe(corr_matrix, use_container_width=True)

    # Compare key predictors across levels
    st.markdown("#### Key Predictor Across Geographic Levels")

    key_pred_cols = ['b_perc_low40_hh', 'w_perc_low40_hh', 'g_perc_low40_hh']
    key_pred_cols = [c for c in key_pred_cols if c in filtered_df.columns]

    if len(key_pred_cols) > 1:
        labels = {
            'b_perc_low40_hh': 'Buurt (Neighborhood)',
            'w_perc_low40_hh': 'Wijk (District)',
            'g_perc_low40_hh': 'Gemeente (Municipality)'
        }
        fig = create_multi_distribution(
            filtered_df,
            key_pred_cols,
            labels=labels,
            title="% Low-Income Households by Geographic Level"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### Correlations Between Levels")
        level_corr = filtered_df[key_pred_cols].corr().round(3)
        level_corr.index = [labels.get(c, c) for c in level_corr.index]
        level_corr.columns = [labels.get(c, c) for c in level_corr.columns]
        st.dataframe(level_corr, use_container_width=True)
