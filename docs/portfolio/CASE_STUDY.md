# Case Study: Neighborhood Effects on Redistribution Preferences

A data science portfolio project demonstrating end-to-end analytics from research question to interactive dashboard.

---

## The Problem

### The Puzzle

Income inequality has risen across Western democracies, yet public support for redistribution has not increased proportionally. This contradicts classic economic models (Meltzer & Richard, 1981) predicting that higher inequality should generate greater demand for redistributive policies.

### The Hypothesis

Mijs (2018) proposes that people form beliefs about inequality based on their immediate "inferential spaces"—the neighborhoods, workplaces, and social circles where daily life unfolds. In homogeneous environments, inequality is less visible; in diverse environments, structural barriers become apparent.

### Research Questions

1. Does neighborhood income composition predict redistribution preferences?
2. Are neighborhood-level effects stronger than municipality-level effects?
3. Does individual income moderate the neighborhood effect?

---

## The Approach

### Methodological Strategy

**Multilevel Modeling**: Individuals are "nested" within neighborhoods—standard regression would ignore this clustering and produce biased standard errors. Multilevel models correctly partition variance and test contextual hypotheses.

```
Level 1: Individuals (n = 4,748)
    └── Level 2: Neighborhoods (n = 1,572)
            └── Level 3: Districts (n = 869)
                    └── Level 4: Municipalities (n = 295)
```

### Model Sequence

| Model | Purpose |
|-------|---------|
| M0: Empty | Calculate ICC—how much variance is between neighborhoods? |
| M1: + Key predictor | Test bivariate neighborhood effect |
| M2: + Individual controls | Is effect compositional or contextual? |
| M3: + Neighborhood controls | Robustness to alternative explanations |

### Data Linkage

Survey responses (attitudes, demographics) linked to official neighborhood statistics (income distribution, population composition) via geographic identifiers.

---

## The Tools

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Data Extraction** | cbsodataR, pandas | API calls to CBS StatLine |
| **Data Processing** | tidyverse, pandas | Cleaning, recoding, merging |
| **Statistical Models** | lme4, statsmodels | Multilevel regression |
| **Pipeline Orchestration** | targets, Python modules | Reproducible workflow |
| **Dashboards** | Shiny, Streamlit | Interactive visualization |
| **Visualization** | ggplot2, plotly | Publication-quality figures |

### Dual Implementation

The analysis is implemented in both R and Python:

- **R**: Gold standard for multilevel modeling (lme4), true nested random effects
- **Python**: Broader accessibility, modern dashboard ecosystem (Streamlit)

Results are validated across both implementations to ensure robustness.

---

## The Results

### Key Finding: Limited Neighborhood Effects

**Only 3.4% of variance in redistribution preferences occurs between neighborhoods.**

This means 96.6% of the variation in attitudes is driven by individual-level factors—not where people live.

### Hypothesis Testing Results

| Hypothesis | Finding | Interpretation |
|------------|---------|----------------|
| H1: Neighborhood poverty → support | NOT SUPPORTED | Effect disappears after individual controls |
| H2: Neighborhood > municipality effects | INCONCLUSIVE | Variance minimal at all levels |
| H3: Income moderates effect | NOT SUPPORTED | No significant cross-level interaction |

### Effect Attenuation

The neighborhood poverty effect follows a clear pattern:

```
Bivariate:    β = 3.46 *** (significant)
+ Individual: β = 2.94 *** (still significant)
+ Neighborhood: β = 0.28    (non-significant)
```

**Interpretation**: The apparent neighborhood effect is compositional—it reflects who lives where, not neighborhood influence on attitudes.

### Sensitivity Analyses

| Specification | Coefficient | Significant? |
|--------------|-------------|--------------|
| Base (single-item DV) | 0.28 | No |
| 2-item composite DV | 0.31 | No |
| 3-item composite DV | 0.29 | No |
| Dutch-born only | 0.19 | No |
| Income ratio predictor | -1.84 | Yes* |

*Alternative specification with income polarization measure shows weak effect in opposite direction.

---

## The Impact

### For Policy

- **Local interventions may not shift attitudes**: Neighborhood-based programs targeting redistribution support are unlikely to be effective
- **Individual targeting matters more**: Age and education are stronger predictors than neighborhood context
- **Context-dependent findings**: Results may differ in more unequal societies (US, UK)

### For Research

- **Extends inferential spaces literature**: First test using Dutch administrative data
- **Supports compositional interpretation**: Selection effects may dominate contextual effects
- **Calls for longitudinal designs**: Cross-sectional data cannot establish causality

### For Methods

- **Demonstrates multilevel framework**: Proper handling of nested data structures
- **Shows dual-software validation**: Cross-validated in R and Python
- **Illustrates null finding value**: Non-effects are substantively meaningful

---

## Project Deliverables

| Deliverable | Description |
|-------------|-------------|
| **Python Dashboard** | [Streamlit app](https://attitudes-toward-income-inequality-7unora4rhffxtelwombehc.streamlit.app) with interactive results |
| **R Dashboard** | [Shiny app](https://kmazurek-analytics.shinyapps.io/income-inequality-attitudes/) with nested RE results |
| **Academic Paper** | Full manuscript draft ([DRAFT_PAPER.md](../academic/DRAFT_PAPER.md)) |
| **Documentation** | Literature review, limitations, technical overview |
| **Reproducible Pipeline** | Both R (targets) and Python implementations |

---

## Skills Demonstrated

- **Statistical**: Multilevel modeling, variance decomposition, sensitivity analysis
- **Engineering**: ETL pipelines, API integration, data merging
- **Software**: R, Python, Shiny, Streamlit, Git
- **Communication**: Academic writing, interactive visualization, documentation

---

## Learn More

- [Full Project Summary](../../PROJECT_SUMMARY.md)
- [Technical Overview](../technical/TECHNICAL_OVERVIEW.md)
- [Skills Matrix](SKILLS_MATRIX.md)
- [Complete Paper](../academic/DRAFT_PAPER.md)

---

*Author: Kaleb Mazurek | University of Amsterdam Internship | Supervised by Dr. Wouter Schakel*
