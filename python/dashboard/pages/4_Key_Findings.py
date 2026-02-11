# =============================================================================
# 4_Key_Findings.py - Summary and Conclusions
# =============================================================================
"""
Summary of key findings, hypothesis testing, and implications.
"""

import streamlit as st
import sys
from pathlib import Path

# Add paths for imports
DASHBOARD_DIR = Path(__file__).parent.parent
PYTHON_DIR = DASHBOARD_DIR.parent
sys.path.insert(0, str(PYTHON_DIR))
sys.path.insert(0, str(DASHBOARD_DIR))

from utils.data_loader import (
    load_analysis_data, get_precomputed_results,
    is_demo_mode, get_demo_mode_message
)

# =============================================================================
# Page Configuration
# =============================================================================

st.set_page_config(
    page_title="Key Findings | Income Inequality",
    page_icon="🎯",
    layout="wide"
)

st.title("🎯 Key Findings")
st.markdown("Summary of research findings and their implications.")

# =============================================================================
# Load Data
# =============================================================================

demo_mode = is_demo_mode()
if demo_mode:
    st.info(get_demo_mode_message())

try:
    results = get_precomputed_results()
    data_loaded = True
except Exception as e:
    st.error(f"Error loading results: {e}")
    data_loaded = False

# =============================================================================
# Research Questions & Hypotheses
# =============================================================================

st.header("Research Questions & Hypotheses")

st.markdown("""
This study tests the **"inferential spaces" hypothesis** (Mijs, 2018), which suggests that
people infer societal-level inequality from their immediate surroundings.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### H1: Neighborhood Effect
    > People living in neighborhoods with
    > higher concentrations of low-income
    > households will have stronger support
    > for redistribution.

    **Operationalization**:
    - IV: `b_perc_low40_hh` (% low-income HH)
    - DV: `DV_single` (redistribution support)
    """)

with col2:
    st.markdown("""
    ### H2: Proximity Effect
    > Effects will be stronger at the
    > neighborhood level than at higher
    > geographic levels (district, municipality).

    **Operationalization**:
    - Compare effects at buurt, wijk, gemeente
    - Four-level model comparison
    """)

with col3:
    st.markdown("""
    ### H3: Confounding Test
    > The neighborhood effect will persist
    > after controlling for individual-level
    > socioeconomic characteristics.

    **Operationalization**:
    - Model sequence M1 → M2 → M3
    - Coefficient stability analysis
    """)

# =============================================================================
# Hypothesis Testing Results
# =============================================================================

st.divider()
st.header("Hypothesis Testing Results")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background-color: #ffebee; padding: 20px; border-radius: 10px; border-left: 5px solid #d32f2f;">
        <h3 style="color: #d32f2f;">H1: Not Supported</h3>
        <p><strong>Finding:</strong> The neighborhood income composition effect
        is not significant after controlling for individual characteristics.</p>
        <p><strong>Evidence:</strong></p>
        <ul>
            <li>M1 (unadjusted): β = 3.36***</li>
            <li>M3 (full controls): β = 0.33 (n.s.)</li>
            <li>95% CI crosses zero: [-1.55, 2.21]</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #fff3e0; padding: 20px; border-radius: 10px; border-left: 5px solid #f57c00;">
        <h3 style="color: #f57c00;">H2: Inconclusive</h3>
        <p><strong>Finding:</strong> Effects are weak at all geographic levels,
        preventing meaningful comparison.</p>
        <p><strong>Evidence:</strong></p>
        <ul>
            <li>ICC at buurt level: 3.4%</li>
            <li>Effects weak at all scales</li>
            <li>Four-level models show similar pattern</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background-color: #ffebee; padding: 20px; border-radius: 10px; border-left: 5px solid #d32f2f;">
        <h3 style="color: #d32f2f;">H3: Not Supported</h3>
        <p><strong>Finding:</strong> The neighborhood effect does NOT persist
        after controlling for individual factors.</p>
        <p><strong>Evidence:</strong></p>
        <ul>
            <li>Coefficient drops from 3.36 to 0.33</li>
            <li>~90% reduction in effect size</li>
            <li>Individual factors fully account for the association</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# Main Findings Summary
# =============================================================================

st.divider()
st.header("Summary of Key Findings")

st.markdown("""
### 1. Neighborhood Context Has Limited Influence

The **Intraclass Correlation Coefficient (ICC) is only 3.4%**, meaning that
only 3.4% of the variance in redistribution preferences occurs between
neighborhoods. The vast majority (96.6%) of variance is within neighborhoods.

This suggests that where people live explains very little about their
attitudes toward redistribution.
""")

st.markdown("""
### 2. The "Raw" Neighborhood Effect is Spurious

While there is a significant bivariate relationship between neighborhood
income composition and redistribution preferences (M1: β = 3.36***), this
association **disappears** once we control for individual characteristics
(M3: β = 0.33, n.s.).

This indicates that the initial association was driven by **compositional effects**—
the types of people who live in different neighborhoods—rather than
**contextual effects** of the neighborhoods themselves.
""")

st.markdown("""
### 3. Individual Characteristics Are the Primary Drivers

The strongest predictors of redistribution preferences are:

| Variable | Coefficient | Direction |
|----------|------------|-----------|
| **Age** | +2.15*** | Older → More support |
| **Education** | -3.45*** | Higher → Less support |
| **Employment** | varies | Unemployed → More support |

These individual-level factors explain much more variance than any
neighborhood characteristics.
""")

# =============================================================================
# Interpretation
# =============================================================================

st.divider()
st.header("Interpretation")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### Why Are Neighborhood Effects Weak?

    Several factors may explain the limited neighborhood effects:

    1. **The Netherlands is relatively egalitarian**
       - Less residential segregation than US/UK
       - Strong welfare state reduces visible inequality

    2. **Information environment**
       - Media and internet may dominate local observations
       - People work/socialize outside their neighborhood

    3. **Measurement issues**
       - Administrative boundaries may not reflect social reality
       - Small sample sizes within neighborhoods
       - Survey-based attitudes vs. behavioral outcomes

    4. **Selection effects**
       - People choose neighborhoods based on preferences
       - Endogeneity concerns
    """)

with col2:
    st.markdown("""
    ### Implications for Theory

    Our findings suggest **limited support for the "inferential spaces"
    hypothesis** in the Dutch context. This does not mean the theory
    is wrong, but rather that:

    - **Context matters**: The Netherlands may differ from other countries
    - **Scale matters**: Effects might exist at different spatial scales
    - **Time matters**: Exposure duration may be important
    - **Mechanisms matter**: The pathway from observation to attitude
      formation may be more complex

    ### Policy Implications

    If neighborhood context has limited influence on redistribution
    preferences, then:

    - Spatial desegregation policies may not change attitudes
    - Individual-level factors are more important targets
    - Education and employment policies may be more effective
    """)

# =============================================================================
# Comparison with Prior Research
# =============================================================================

st.divider()
st.header("Comparison with Prior Research")

st.markdown("""
| Study | Country | ICC | Key Finding |
|-------|---------|-----|-------------|
| **This Study** | Netherlands | 3.4% | Weak neighborhood effects |
| Mijs (2018) | USA | ~8-12% | Moderate neighborhood effects |
| Larsen (2016) | Denmark | ~5% | Small but significant effects |
| Senik (2009) | Europe | varies | Country-level differences |

Our ICC is lower than most US-based studies, consistent with the Netherlands'
lower residential segregation and stronger welfare state.
""")

# =============================================================================
# Methodology Summary
# =============================================================================

st.divider()
st.header("Methodology")

tab_data, tab_models, tab_limits = st.tabs([
    "Data Sources",
    "Statistical Models",
    "Limitations"
])

with tab_data:
    st.markdown("""
    ### Data Sources

    **Survey Data: SCoRE Netherlands 2017**
    - Nationally representative sample
    - N = 8,013 respondents
    - Redistribution attitudes measured on 7-point scales

    **Administrative Data: CBS StatLine 2018**
    - Statistics Netherlands official data
    - Neighborhood-level indicators
    - Income distribution, demographics, housing

    **Geographic Units**
    - Buurt (Neighborhood): ~500-2000 residents
    - Wijk (District): Groups of buurten
    - Gemeente (Municipality): Local government unit
    """)

with tab_models:
    st.markdown("""
    ### Statistical Approach

    **Two-Level Random Intercept Models**
    ```
    DV_single ~ 1 + predictors + (1 | buurt_id)
    ```

    - Individuals (level 1) nested in neighborhoods (level 2)
    - Random intercepts allow neighborhoods to vary
    - REML estimation via statsmodels

    **Four-Level Models**
    - Buurt as primary grouping
    - Wijk and gemeente predictors as fixed effects
    - Note: True nested random effects require R's lme4

    **Robustness Checks**
    - Alternative DV specifications (2-item, 3-item composites)
    - Subgroup analyses (Dutch-born only)
    - VIF diagnostics for multicollinearity
    """)

with tab_limits:
    st.markdown("""
    ### Limitations

    1. **Cross-sectional design**
       - Cannot establish causality
       - Selection into neighborhoods not addressed

    2. **Small cluster sizes**
       - Average ~3 respondents per neighborhood
       - Many singleton clusters
       - May underestimate random effects variance

    3. **Administrative boundaries**
       - May not reflect actual social spaces
       - Modifiable Areal Unit Problem (MAUP)

    4. **Single country**
       - Results may not generalize to other contexts
       - Netherlands is relatively egalitarian

    5. **statsmodels limitations**
       - Cannot fit true nested random effects
       - R's lme4 preferred for four-level models
    """)

# =============================================================================
# Conclusion
# =============================================================================

st.divider()
st.header("Conclusion")

st.markdown("""
<div style="background-color: #e3f2fd; padding: 30px; border-radius: 15px;">
    <h3 style="color: #1976d2;">Key Takeaway</h3>
    <p style="font-size: 1.2rem;">
        This study finds <strong>limited evidence</strong> for neighborhood effects on
        redistribution preferences in the Netherlands. Only 3.4% of variance is between
        neighborhoods, and the effect of neighborhood income composition becomes
        non-significant after controlling for individual characteristics.
    </p>
    <p style="font-size: 1.2rem;">
        <strong>Individual-level factors</strong>—particularly age and education—are
        the primary drivers of redistribution preferences. This suggests that the
        "inferential spaces" hypothesis may have limited applicability in the
        relatively egalitarian Dutch context.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# R Implementation Note
# =============================================================================

st.divider()
st.header("R Implementation")

st.info("""
**For R-specific robustness analyses:**

The R Shiny dashboard includes additional analyses using lme4's
true nested random effects: `(1|gemeente_id) + (1|wijk_id) + (1|buurt_id)`

This properly partitions variance across all geographic levels, which Python's
statsmodels cannot do.

Results confirm that variance is minimal at all geographic levels (~1-2% each),
providing additional evidence that neighborhood effects are weak in the Dutch context.

[Open R Dashboard](https://kmazurek-analytics.shinyapps.io/income-inequality-attitudes/)
""")

# =============================================================================
# Footer
# =============================================================================

st.divider()

st.markdown("""
<div style="text-align: center; color: #666;">
    <p>
        <strong>Attitudes Toward Income Inequality</strong><br>
        A Multilevel Analysis of Redistribution Preferences in the Netherlands
    </p>
    <p>
        Author: Kaleb Mazurek<br>
        University of Amsterdam Internship | Supervised by Dr. Wouter Schakel<br>
        Framework: Python (statsmodels, pandas, Streamlit)<br>
        Data: SCoRE 2017 + CBS StatLine 2018
    </p>
    <p style="font-style: italic; font-size: 0.9rem;">
        All errors and omissions are solely my own responsibility.
    </p>
</div>
""", unsafe_allow_html=True)
