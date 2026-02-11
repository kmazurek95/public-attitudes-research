# =============================================================================
# 5_About_Project.py - Project Overview and Portfolio Context
# =============================================================================
"""
About page providing project overview, skills demonstrated, and documentation links.
Designed for recruiters, researchers, and anyone wanting to understand the project.
"""

import streamlit as st
import sys
from pathlib import Path

# Add paths for imports
DASHBOARD_DIR = Path(__file__).parent.parent
PYTHON_DIR = DASHBOARD_DIR.parent
sys.path.insert(0, str(PYTHON_DIR))
sys.path.insert(0, str(DASHBOARD_DIR))

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="About | Income Inequality",
    page_icon="ℹ️",
    layout="wide"
)

st.title("ℹ️ About This Project")
st.markdown("Project overview, technical skills demonstrated, and documentation links.")

# =============================================================================
# 30-Second Pitch
# =============================================================================

st.header("30-Second Pitch")

st.info("""
I built a complete data science pipeline—from raw survey data to interactive dashboards—to test
whether where you live affects what you believe about inequality. Using 8,000+ survey responses
linked to official neighborhood statistics, I applied multilevel regression models and found that
neighborhoods explain only **3.4% of attitude variation**. The project demonstrates end-to-end
analytics skills: API integration, data engineering, statistical modeling, and visualization in
both Python and R.
""")

# =============================================================================
# Technical Skills
# =============================================================================

st.header("Technical Skills Demonstrated")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Statistical Methods")
    st.markdown("""
    | Skill | Application |
    |-------|-------------|
    | **Multilevel Modeling** | Random intercept models (2-4 levels) |
    | **Variance Decomposition** | ICC calculation at multiple geographic levels |
    | **Sensitivity Analysis** | Alternative DVs, subgroups, robustness checks |
    | **Cross-Level Interactions** | Individual × neighborhood interaction tests |
    """)

    st.subheader("Data Engineering")
    st.markdown("""
    | Skill | Application |
    |-------|-------------|
    | **API Integration** | CBS StatLine Dutch national statistics |
    | **Data Merging** | Survey + administrative data linkage |
    | **Variable Construction** | Composite indices, transformations |
    | **Missing Data Handling** | Complete case analysis, diagnostics |
    """)

with col2:
    st.subheader("Software Development")
    st.markdown("""
    | Skill | Application |
    |-------|-------------|
    | **Python** | pandas, statsmodels, Streamlit, plotly |
    | **R** | tidyverse, lme4, Shiny, targets |
    | **Dashboard Development** | Interactive multi-page applications |
    | **Pipeline Orchestration** | Reproducible analysis workflows |
    """)

    st.subheader("Research Skills")
    st.markdown("""
    | Skill | Application |
    |-------|-------------|
    | **Literature Review** | Theoretical framework contextualization |
    | **Hypothesis Testing** | Pre-registered H1, H2, H3 |
    | **Academic Writing** | Full paper draft (~410 lines) |
    | **Limitations Discussion** | Comprehensive self-critique |
    """)

# =============================================================================
# Key Findings Summary
# =============================================================================

st.divider()
st.header("Key Findings")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### Variance Decomposition

    | Level | ICC |
    |-------|-----|
    | **Neighborhood** | 3.4% |
    | **Individual** | 96.6% |

    Attitudes are primarily driven by
    individual factors, not neighborhood context.
    """)

with col2:
    st.markdown("""
    ### Hypothesis Testing

    | Hypothesis | Result |
    |------------|--------|
    | **H1** Neighborhood effect | Not Supported |
    | **H2** Proximity matters | Inconclusive |
    | **H3** Effect persists | Not Supported |

    Effect disappears after controlling for confounds.
    """)

with col3:
    st.markdown("""
    ### Model Progression

    | Model | Poverty β | Sig? |
    |-------|-----------|------|
    | Bivariate | 3.46 | Yes |
    | + Individual | 2.94 | Yes |
    | + Neighborhood | 0.28 | No |

    Compositional, not contextual effects.
    """)

# =============================================================================
# Research Contribution
# =============================================================================

st.divider()
st.header("Research Contribution")

st.markdown("""
**For Academics:** This study provides an empirical test of Mijs' (2018) "inferential spaces"
hypothesis using high-quality Dutch administrative data.

**Key contributions:**
1. **Cross-national extension**: Tests whether US findings replicate in a European welfare state
2. **Multi-level variance decomposition**: Partitions variance across neighborhoods, districts, and municipalities
3. **Dual-software implementation**: Results validated in both Python (statsmodels) and R (lme4)
4. **Null finding with implications**: Limited neighborhood effects suggest individual factors dominate in the Dutch context

**Theoretical implication**: In relatively egalitarian societies with strong welfare states, local
socioeconomic composition may matter less for attitude formation than in more unequal contexts.
""")

# =============================================================================
# Technical Stack
# =============================================================================

st.divider()
st.header("Technical Stack")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Languages**
    - Python 3.9+
    - R 4.2+
    """)

with col2:
    st.markdown("""
    **Analysis**
    - statsmodels (MixedLM)
    - lme4 (multilevel)
    - pandas / tidyverse
    """)

with col3:
    st.markdown("""
    **Visualization**
    - Streamlit / Shiny
    - plotly / ggplot2
    - CBS StatLine API
    """)

# =============================================================================
# Documentation Links
# =============================================================================

st.divider()
st.header("Full Documentation")

st.markdown("View complete documentation on GitHub:")

GITHUB_BASE = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main"

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"""
    **Portfolio Materials**
    - [Project Summary]({GITHUB_BASE}/PROJECT_SUMMARY.md) - Executive overview
    - [Case Study]({GITHUB_BASE}/docs/portfolio/CASE_STUDY.md) - Problem/Approach/Results format
    - [Skills Matrix]({GITHUB_BASE}/docs/portfolio/SKILLS_MATRIX.md) - Competencies demonstrated
    - [Business Value]({GITHUB_BASE}/docs/portfolio/BUSINESS_VALUE.md) - Industry applications
    """)

with col2:
    st.markdown(f"""
    **Academic & Technical**
    - [Full Paper]({GITHUB_BASE}/docs/academic/DRAFT_PAPER.md) - Complete manuscript
    - [Literature Review]({GITHUB_BASE}/docs/academic/LITERATURE_REVIEW.md) - Theoretical background
    - [Technical Overview]({GITHUB_BASE}/docs/technical/TECHNICAL_OVERVIEW.md) - Architecture details
    - [Reproducibility Guide]({GITHUB_BASE}/docs/technical/REPRODUCIBILITY.md) - How to reproduce
    """)

# =============================================================================
# Data Sources
# =============================================================================

st.divider()
st.header("Data Sources")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **SCoRE Survey Netherlands 2017**
    - N = 8,013 respondents
    - Attitudes toward redistribution
    - Individual socioeconomic characteristics
    - Geographic identifiers (buurt, wijk, gemeente)
    """)

with col2:
    st.markdown("""
    **CBS StatLine Table 84286NED**
    - 2018 neighborhood income statistics
    - % low-income households
    - % high-income households
    - Income distribution ratios
    """)

# =============================================================================
# Author & Links
# =============================================================================

st.divider()

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.markdown("""
    ### Author

    **Kaleb Mazurek**

    University of Amsterdam Internship (2023)
    Supervised by Dr. Wouter Schakel

    *All errors and omissions are solely my own responsibility.*
    """)

with col2:
    st.markdown("### Links")
    st.link_button(
        "GitHub Repository",
        "https://github.com/kmazurek95/attitudes-toward-income-inequality",
        use_container_width=True
    )
    st.link_button(
        "R Dashboard",
        "https://kmazurek-analytics.shinyapps.io/income-inequality-attitudes/",
        use_container_width=True
    )

with col3:
    st.markdown("### Contact")
    st.markdown("""
    Feel free to reach out for questions
    about the methodology, code, or findings.
    """)

# =============================================================================
# Footer
# =============================================================================

st.divider()

st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p><em>Last updated: February 2025</em></p>
    <p>Navigate using the sidebar to explore the data, models, and findings in detail.</p>
</div>
""", unsafe_allow_html=True)
