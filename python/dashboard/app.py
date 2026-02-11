# =============================================================================
# app.py - Main Dashboard Entry Point
# =============================================================================
"""
Streamlit dashboard for Attitudes Toward Income Inequality research.

Run with: streamlit run dashboard/app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add paths for imports
DASHBOARD_DIR = Path(__file__).parent
PYTHON_DIR = DASHBOARD_DIR.parent
sys.path.insert(0, str(PYTHON_DIR))
sys.path.insert(0, str(DASHBOARD_DIR))

from utils.data_loader import (
    load_analysis_data, get_summary_stats, get_precomputed_results,
    is_demo_mode, get_demo_mode_message
)

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Income Inequality Attitudes",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """
        # Attitudes Toward Income Inequality
        A multilevel analysis of redistribution preferences in the Netherlands.

        **Author:** Kaleb Mazurek

        **Data Sources:**
        - SCoRE Survey Netherlands 2017
        - CBS Statistics Netherlands
        """
    }
)

# =============================================================================
# Custom CSS
# =============================================================================

st.markdown("""
<style>
    /* Main header styling */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }

    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }

    /* Metric card styling */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        border-left: 4px solid #1f77b4;
    }

    div[data-testid="stMetric"] label {
        color: #666;
    }

    /* Info box styling */
    .stAlert {
        border-radius: 10px;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Sidebar
# =============================================================================

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Flag_of_the_Netherlands.svg/125px-Flag_of_the_Netherlands.svg.png", width=60)
    st.markdown("### Navigation")
    st.markdown("""
    Use the pages in the sidebar to explore:

    1. **Data Explorer** - Survey & administrative data
    2. **Geographic View** - Spatial hierarchy
    3. **Model Results** - Multilevel analysis
    4. **Key Findings** - Summary & conclusions
    5. **About Project** - Skills & documentation
    """)

    st.divider()

    st.markdown("### About This Research")
    st.markdown("""
    This study examines how **neighborhood-level socioeconomic composition**
    influences individual **redistribution preferences** in the Netherlands.

    Based on Mijs' (2018) "inferential spaces" framework.
    """)

    st.divider()

    st.markdown("### Data Sources")
    st.markdown("""
    - **SCoRE Survey** (2017)
    - **CBS StatLine** (2018)
    """)

    st.divider()

    st.markdown("### R Implementation")
    st.markdown("""
    For R-specific analyses including **true nested random effects**:

    `(1|gemeente) + (1|wijk) + (1|buurt)`
    """)

    r_dashboard_url = "https://kmazurek-analytics.shinyapps.io/income-inequality-attitudes/"
    st.link_button(
        "Open R Dashboard",
        r_dashboard_url,
        help="R Shiny dashboard with lme4 nested random effects"
    )

    st.caption("Note: R dashboard must be running locally")

# =============================================================================
# Main Content - Home Page
# =============================================================================

# Header
st.markdown('<p class="main-header">Attitudes Toward Income Inequality</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">A Multilevel Analysis of Redistribution Preferences in the Netherlands</p>', unsafe_allow_html=True)

# Load data
demo_mode = is_demo_mode()
try:
    df = load_analysis_data()
    stats = get_summary_stats(df)
    results = get_precomputed_results()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading data: {e}")
    data_loaded = False
    stats = get_summary_stats(None)  # Use precomputed stats
    results = get_precomputed_results()

# Show demo mode notice
if demo_mode:
    st.info(get_demo_mode_message())

# =============================================================================
# Key Metrics Row
# =============================================================================

if data_loaded:
    st.markdown("### Key Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            label="Respondents",
            value=f"{stats.get('n_obs', 0):,}",
            help="Total survey respondents"
        )

    with col2:
        st.metric(
            label="Analysis Sample",
            value=f"{stats.get('n_complete', 0):,}",
            help="Complete cases for analysis"
        )

    with col3:
        st.metric(
            label="Neighborhoods",
            value=f"{stats.get('n_buurten', 0):,}",
            help="Unique buurten (neighborhoods)"
        )

    with col4:
        st.metric(
            label="Districts",
            value=f"{stats.get('n_wijken', 0):,}",
            help="Unique wijken (districts)"
        )

    with col5:
        st.metric(
            label="Municipalities",
            value=f"{stats.get('n_gemeenten', 0):,}",
            help="Unique gemeenten (municipalities)"
        )

    with col6:
        icc = results.get('two_level', {}).get('icc', 0.034)
        st.metric(
            label="ICC",
            value=f"{icc*100:.1f}%",
            delta=f"{(1-icc)*100:.1f}% within",
            delta_color="off",
            help="Intraclass Correlation Coefficient"
        )

# =============================================================================
# Research Overview
# =============================================================================

st.divider()

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### Research Question")
    st.markdown("""
    > **Do neighborhood characteristics influence attitudes toward income redistribution,
    > and at what geographic level do contextual effects operate?**

    This study tests the "inferential spaces" hypothesis (Mijs, 2018), which suggests that
    people's attitudes toward inequality are shaped by the socioeconomic composition of
    their immediate surroundings.

    We examine this using **multilevel models** that account for the nested structure of
    individuals within neighborhoods (buurten), districts (wijken), and municipalities (gemeenten).
    """)

    st.markdown("### Methodology")
    st.markdown("""
    - **Data**: Dutch SCoRE Survey (2017) merged with CBS administrative statistics (2018)
    - **Dependent Variable**: Support for government redistribution (0-100 scale)
    - **Key Predictor**: % low-income households in neighborhood
    - **Models**: Two-level and four-level random intercept models
    """)

with col_right:
    st.markdown("### Key Finding")

    # Create a simple metric display
    st.info("""
    **Only 3.4%** of variance in redistribution preferences
    is between neighborhoods.

    The neighborhood income composition effect becomes
    **non-significant** after controlling for individual
    characteristics.
    """)

    st.markdown("### Interpretation")
    st.markdown("""
    Individual-level factors (age, education, employment)
    are the primary drivers of redistribution preferences,
    not neighborhood context.

    This suggests limited support for the "inferential spaces"
    framework in the Dutch context.
    """)

# =============================================================================
# Geographic Hierarchy Explanation
# =============================================================================

st.divider()

st.markdown("### Geographic Hierarchy")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    #### 👤 Individual
    Survey respondents from the
    SCoRE Netherlands 2017 study.
    """)
    if data_loaded:
        st.metric("N", f"{stats.get('n_obs', 0):,}")

with col2:
    st.markdown("""
    #### 🏘️ Buurt (Neighborhood)
    Smallest geographic unit.
    ~500-2000 residents each.
    """)
    if data_loaded:
        st.metric("N", f"{stats.get('n_buurten', 0):,}")

with col3:
    st.markdown("""
    #### 🏙️ Wijk (District)
    Groups of neighborhoods.
    Intermediate administrative level.
    """)
    if data_loaded:
        st.metric("N", f"{stats.get('n_wijken', 0):,}")

with col4:
    st.markdown("""
    #### 🗺️ Gemeente (Municipality)
    Largest geographic unit.
    Local government level.
    """)
    if data_loaded:
        st.metric("N", f"{stats.get('n_gemeenten', 0):,}")

# =============================================================================
# Model Overview
# =============================================================================

st.divider()

st.markdown("### Model Specifications")

tab1, tab2 = st.tabs(["Two-Level Models", "Four-Level Models"])

with tab1:
    st.markdown("""
    **Two-level models** nest individuals within neighborhoods (buurten):

    | Model | Specification |
    |-------|--------------|
    | **M0** | Empty model (random intercept only) |
    | **M1** | + Key predictor (% low-income HH at buurt level) |
    | **M2** | + Individual controls (age, sex, education, employment) |
    | **M3** | + Buurt-level controls (demographics, income indicators) |

    These models estimate the **ICC** and test whether neighborhood income composition
    predicts redistribution preferences.
    """)

with tab2:
    st.markdown("""
    **Four-level models** include predictors at buurt, wijk, and gemeente levels:

    | Model | Specification |
    |-------|--------------|
    | **M0** | Empty model |
    | **M1** | + Key predictors at all geographic levels |
    | **M2** | + Individual controls |
    | **M3** | + Buurt-level controls |
    | **M4** | + Wijk-level controls |

    These models test whether effects operate at different geographic scales.

    ⚠️ **Note**: Python's statsmodels uses buurt as primary grouping with
    wijk/gemeente predictors as fixed effects. For true nested random effects,
    see the R implementation.
    """)

# =============================================================================
# Footer
# =============================================================================

st.divider()

st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>
        <strong>Author:</strong> Kaleb Mazurek |
        <strong>Framework:</strong> Mijs (2018) "Inferential Spaces" |
        <strong>Tools:</strong> Python, statsmodels, Streamlit
    </p>
    <p>Navigate using the sidebar to explore the data, models, and findings in detail.</p>
</div>
""", unsafe_allow_html=True)
