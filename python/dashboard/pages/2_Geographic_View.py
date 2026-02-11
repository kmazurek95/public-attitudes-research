# =============================================================================
# 2_Geographic_View.py - Geographic Hierarchy Visualization
# =============================================================================
"""
Visualization of the Dutch administrative geographic hierarchy.
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
    load_analysis_data, get_existing_figures,
    is_demo_mode, get_demo_mode_message
)
from components.charts import (
    create_geographic_treemap,
    create_cluster_size_histogram
)

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Geographic View | Income Inequality",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Geographic View")
st.markdown("Explore the spatial hierarchy of the Dutch administrative system.")

# =============================================================================
# Load Data
# =============================================================================

# Check for demo mode
if is_demo_mode():
    st.warning(get_demo_mode_message())
    st.info("""
    **Geographic View requires raw data.**

    In demo mode, you can view:
    - [Model Results](/Model_Results) - Precomputed analysis results
    - [Key Findings](/Key_Findings) - Summary of conclusions

    To enable full geographic exploration, ensure the analysis data file is present.
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
    figures = get_existing_figures()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False

if not data_loaded:
    st.stop()

# =============================================================================
# Geographic Hierarchy Explanation
# =============================================================================

st.header("Dutch Administrative Hierarchy")

st.markdown("""
The Netherlands uses a hierarchical geographic classification system for administrative purposes.
Our analysis leverages this structure for multilevel modeling.
""")

# Visual hierarchy diagram
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    ### 🇳🇱 Country
    **Netherlands**

    The entire nation.
    """)

with col2:
    n_gemeenten = df['gemeente_id'].nunique()
    st.markdown(f"""
    ### 🏛️ Gemeente
    **Municipality**

    Local government unit.
    Responsible for local services.

    **N = {n_gemeenten:,}** in sample
    """)

with col3:
    n_wijken = df['wijk_id'].nunique()
    st.markdown(f"""
    ### 🏙️ Wijk
    **District**

    Sub-municipal area.
    Groups of neighborhoods.

    **N = {n_wijken:,}** in sample
    """)

with col4:
    n_buurten = df['buurt_id'].nunique()
    st.markdown(f"""
    ### 🏘️ Buurt
    **Neighborhood**

    Smallest unit.
    ~500-2000 residents.

    **N = {n_buurten:,}** in sample
    """)

# Arrow diagram
st.markdown("""
<div style="text-align: center; font-size: 1.5rem; margin: 20px 0;">
    Country → Gemeente → Wijk → Buurt → <strong>Individual</strong>
</div>
""", unsafe_allow_html=True)

st.info("""
**Geographic ID Structure**: Dutch geographic codes follow a hierarchical pattern.
- **Gemeente** (4 digits): e.g., `0363` (Amsterdam)
- **Wijk** (6 digits): e.g., `036301` (first district in Amsterdam)
- **Buurt** (8 digits): e.g., `03630100` (first neighborhood in that district)
""")

# =============================================================================
# Nesting Statistics
# =============================================================================

st.divider()
st.header("Nesting Structure")

col1, col2, col3 = st.columns(3)

with col1:
    # Respondents per gemeente
    resp_per_gemeente = df.groupby('gemeente_id').size()
    st.metric("Avg. Respondents per Gemeente", f"{resp_per_gemeente.mean():.1f}")
    st.metric("Min - Max", f"{resp_per_gemeente.min()} - {resp_per_gemeente.max()}")

with col2:
    # Respondents per wijk
    resp_per_wijk = df.groupby('wijk_id').size()
    st.metric("Avg. Respondents per Wijk", f"{resp_per_wijk.mean():.1f}")
    st.metric("Min - Max", f"{resp_per_wijk.min()} - {resp_per_wijk.max()}")

with col3:
    # Respondents per buurt
    resp_per_buurt = df.groupby('buurt_id').size()
    st.metric("Avg. Respondents per Buurt", f"{resp_per_buurt.mean():.1f}")
    st.metric("Min - Max", f"{resp_per_buurt.min()} - {resp_per_buurt.max()}")

# Additional nesting info
st.markdown("### Nesting Ratios")

col1, col2, col3 = st.columns(3)

with col1:
    wijken_per_gemeente = df.groupby('gemeente_id')['wijk_id'].nunique()
    st.metric("Avg. Wijken per Gemeente", f"{wijken_per_gemeente.mean():.1f}")

with col2:
    buurten_per_wijk = df.groupby('wijk_id')['buurt_id'].nunique()
    st.metric("Avg. Buurten per Wijk", f"{buurten_per_wijk.mean():.1f}")

with col3:
    buurten_per_gemeente = df.groupby('gemeente_id')['buurt_id'].nunique()
    st.metric("Avg. Buurten per Gemeente", f"{buurten_per_gemeente.mean():.1f}")

# =============================================================================
# Cluster Size Distribution
# =============================================================================

st.divider()
st.header("Cluster Size Distributions")

st.markdown("""
For multilevel modeling, it's important to understand the distribution of observations
across clusters. Small clusters can lead to estimation problems.
""")

tab_buurt, tab_wijk, tab_gemeente = st.tabs([
    "Buurt (Neighborhood)",
    "Wijk (District)",
    "Gemeente (Municipality)"
])

with tab_buurt:
    # Check for existing figure
    if figures.get('cluster_sizes'):
        st.image(str(figures['cluster_sizes']), caption="Respondents per Neighborhood")
    else:
        fig = create_cluster_size_histogram(
            df,
            group_col='buurt_id',
            title="Distribution of Cluster Sizes (Buurt level)"
        )
        st.plotly_chart(fig, use_container_width=True)

    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        n_singletons = (resp_per_buurt == 1).sum()
        st.metric("Singleton clusters", f"{n_singletons:,}")
    with col2:
        n_small = (resp_per_buurt <= 2).sum()
        st.metric("Clusters with ≤2 obs", f"{n_small:,}")
    with col3:
        pct_small = n_small / len(resp_per_buurt) * 100
        st.metric("% Small clusters", f"{pct_small:.1f}%")

with tab_wijk:
    fig = create_cluster_size_histogram(
        df,
        group_col='wijk_id',
        title="Distribution of Cluster Sizes (Wijk level)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        n_singletons = (resp_per_wijk == 1).sum()
        st.metric("Singleton clusters", f"{n_singletons:,}")
    with col2:
        n_small = (resp_per_wijk <= 2).sum()
        st.metric("Clusters with ≤2 obs", f"{n_small:,}")
    with col3:
        pct_small = n_small / len(resp_per_wijk) * 100
        st.metric("% Small clusters", f"{pct_small:.1f}%")

with tab_gemeente:
    fig = create_cluster_size_histogram(
        df,
        group_col='gemeente_id',
        title="Distribution of Cluster Sizes (Gemeente level)"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        n_singletons = (resp_per_gemeente == 1).sum()
        st.metric("Singleton clusters", f"{n_singletons:,}")
    with col2:
        n_small = (resp_per_gemeente <= 5).sum()
        st.metric("Clusters with ≤5 obs", f"{n_small:,}")
    with col3:
        pct_small = n_small / len(resp_per_gemeente) * 100
        st.metric("% Small clusters", f"{pct_small:.1f}%")

# =============================================================================
# Geographic Treemap
# =============================================================================

st.divider()
st.header("Geographic Distribution")

st.markdown("""
This treemap shows the hierarchical distribution of respondents across
municipalities and districts. The size of each rectangle represents the
number of respondents.
""")

fig = create_geographic_treemap(df, title="Respondents by Municipality and District")
st.plotly_chart(fig, use_container_width=True)

st.caption("Showing top 20 municipalities by sample size. Click to zoom into districts.")

# =============================================================================
# Top Locations Table
# =============================================================================

st.divider()
st.header("Sample Distribution by Location")

tab_top_gem, tab_top_wijk, tab_top_buurt = st.tabs([
    "Top Gemeenten",
    "Top Wijken",
    "Top Buurten"
])

with tab_top_gem:
    top_gemeenten = df.groupby('gemeente_id').agg(
        n_respondents=('respondent_id', 'count'),
        n_wijken=('wijk_id', 'nunique'),
        n_buurten=('buurt_id', 'nunique'),
        mean_dv=('DV_single', 'mean')
    ).reset_index()
    top_gemeenten = top_gemeenten.sort_values('n_respondents', ascending=False).head(20)
    top_gemeenten['mean_dv'] = top_gemeenten['mean_dv'].round(1)
    top_gemeenten.columns = ['Gemeente ID', 'Respondents', 'Wijken', 'Buurten', 'Mean DV']
    st.dataframe(top_gemeenten, use_container_width=True, hide_index=True)

with tab_top_wijk:
    top_wijken = df.groupby(['gemeente_id', 'wijk_id']).agg(
        n_respondents=('respondent_id', 'count'),
        n_buurten=('buurt_id', 'nunique'),
        mean_dv=('DV_single', 'mean')
    ).reset_index()
    top_wijken = top_wijken.sort_values('n_respondents', ascending=False).head(20)
    top_wijken['mean_dv'] = top_wijken['mean_dv'].round(1)
    top_wijken.columns = ['Gemeente ID', 'Wijk ID', 'Respondents', 'Buurten', 'Mean DV']
    st.dataframe(top_wijken, use_container_width=True, hide_index=True)

with tab_top_buurt:
    top_buurten = df.groupby(['gemeente_id', 'wijk_id', 'buurt_id']).agg(
        n_respondents=('respondent_id', 'count'),
        mean_dv=('DV_single', 'mean'),
        mean_key_pred=('b_perc_low40_hh', 'mean')
    ).reset_index()
    top_buurten = top_buurten.sort_values('n_respondents', ascending=False).head(20)
    top_buurten['mean_dv'] = top_buurten['mean_dv'].round(1)
    top_buurten['mean_key_pred'] = top_buurten['mean_key_pred'].round(2)
    top_buurten.columns = ['Gemeente', 'Wijk', 'Buurt', 'Respondents', 'Mean DV', 'Key Predictor']
    st.dataframe(top_buurten, use_container_width=True, hide_index=True)

# =============================================================================
# Implications for Multilevel Modeling
# =============================================================================

st.divider()
st.header("Implications for Multilevel Modeling")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Advantages of This Structure

    - **Rich nesting**: Clear hierarchy allows for multilevel analysis
    - **Administrative relevance**: Geographic units correspond to policy-relevant boundaries
    - **CBS data availability**: Administrative data available at all levels

    ### Modeling Considerations

    - **Primary grouping**: Buurt (neighborhood) used as main cluster variable
    - **Sample size**: ~3 respondents per buurt on average
    - **Singleton clusters**: Many neighborhoods with only 1 respondent
    """)

with col2:
    st.markdown("""
    ### Limitations

    - **Small cluster sizes**: May reduce precision of random effects estimates
    - **Selection**: Survey sampling may not be representative within buurten
    - **Boundary effects**: Administrative boundaries may not reflect social reality

    ### Statistical Approach

    - **Two-level models**: Individuals nested in buurten
    - **Four-level models**: Add wijk and gemeente level predictors
    - **Note**: True nested random effects require R's lme4
    """)

st.info("""
**Key Insight**: With an average of ~3 respondents per neighborhood and many singleton clusters,
the precision of neighborhood-level random effects is limited. This may contribute to the
relatively small ICC observed in our models.
""")
