# Project Summary: Attitudes Toward Income Inequality

A multilevel analysis of neighborhood effects on redistribution preferences in the Netherlands.

---

## 30-Second Pitch

**For Recruiters/Hiring Managers:**

I built a complete data science pipeline—from raw survey data to interactive dashboards—to test whether where you live affects what you believe about inequality. Using 8,000+ survey responses linked to official neighborhood statistics, I applied multilevel regression models and found that neighborhoods explain only 3.4% of attitude variation. The project demonstrates end-to-end analytics skills: API integration, data engineering, statistical modeling, and visualization in both Python and R.

---

## Research Contribution

**For Academics:**

This study provides an empirical test of Mijs' (2018) "inferential spaces" hypothesis using high-quality Dutch administrative data. Key contributions:

1. **Cross-national extension**: Tests whether US findings (Newman et al., 2015) replicate in a European welfare state
2. **Multi-level variance decomposition**: Partitions variance across neighborhoods, districts, and municipalities
3. **Dual-software implementation**: Results validated in both Python (statsmodels) and R (lme4)
4. **Null finding with implications**: Limited neighborhood effects suggest individual factors dominate in the Dutch context

**Theoretical implication**: In relatively egalitarian societies with strong welfare states, local socioeconomic composition may matter less for attitude formation than in more unequal contexts.

---

## Technical Stack

| Category | Technologies |
|----------|--------------|
| **Languages** | Python 3.9+, R 4.2+ |
| **Statistical Modeling** | statsmodels (MixedLM), lme4 (multilevel) |
| **Data Engineering** | pandas, tidyverse, cbsodataR |
| **Visualization** | Streamlit, Shiny, plotly, ggplot2 |
| **Pipeline Orchestration** | targets (R), modular Python |
| **APIs** | CBS StatLine (Dutch national statistics) |
| **Version Control** | Git, GitHub |

---

## Key Findings at a Glance

### Variance Decomposition

| Level | ICC | Interpretation |
|-------|-----|----------------|
| Neighborhood (buurt) | 3.4% | Minimal between-neighborhood variance |
| Individual | 96.6% | Attitudes primarily driven by personal factors |

### Hypothesis Testing

| Hypothesis | Result | Evidence |
|------------|--------|----------|
| **H1**: Neighborhood poverty → redistribution support | NOT SUPPORTED | Effect non-significant after controls (β = 0.28, p > 0.05) |
| **H2**: Neighborhood effects > municipality effects | INCONCLUSIVE | Variance minimal at all geographic levels |
| **H3**: Income moderates neighborhood effect | NOT SUPPORTED | Cross-level interaction non-significant (β = 0.18, p = 0.60) |

### Model Progression

| Model | Poverty Effect (β) | SE | Significant? |
|-------|-------------------|-----|--------------|
| M1: Bivariate | 3.46 | 0.42 | Yes |
| M2: + Individual controls | 2.94 | 0.41 | Yes |
| M3: + Neighborhood controls | 0.28 | 0.95 | No |

**Key insight**: The apparent neighborhood effect is explained by compositional factors (who lives where), not contextual effects (neighborhood influence on residents).

---

## Live Demos

- **Python Dashboard (Streamlit)**: [attitudes-toward-income-inequality.streamlit.app](https://attitudes-toward-income-inequality-7unora4rhffxtelwombehc.streamlit.app)
- **R Dashboard (Shiny)**: [kmazurek-analytics.shinyapps.io/income-inequality-attitudes](https://kmazurek-analytics.shinyapps.io/income-inequality-attitudes/)

Both dashboards present interactive visualizations of the analysis with precomputed results.

---

## Quick Links

| Resource | Description |
|----------|-------------|
| [Full Paper](docs/academic/DRAFT_PAPER.md) | Complete academic manuscript |
| [Literature Review](docs/academic/LITERATURE_REVIEW.md) | Theoretical background |
| [Methodology](README.md#methods) | Data and methods overview |
| [Limitations](docs/academic/LIMITATIONS.md) | Study constraints and caveats |
| [Technical Overview](docs/technical/TECHNICAL_OVERVIEW.md) | Architecture and pipeline details |
| [Skills Matrix](docs/portfolio/SKILLS_MATRIX.md) | Competencies demonstrated |
| [Documentation Index](docs/index.md) | Full documentation navigation |

---

## Data Sources

- **Survey**: SCoRE Netherlands 2017 (N = 8,013)
- **Administrative**: CBS StatLine Table 84286NED (2018 neighborhood statistics)
- **Geographic Units**: 1,572 neighborhoods (buurten), 869 districts (wijken), 295 municipalities (gemeenten)

---

## Author

**Kaleb Mazurek**

University of Amsterdam Internship (2023)
Supervised by Dr. Wouter Schakel

*All errors and omissions are solely my own responsibility.*

---

*Last updated: February 2025*
