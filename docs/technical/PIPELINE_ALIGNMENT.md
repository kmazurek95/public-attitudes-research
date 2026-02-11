# Pipeline Alignment: R and Python

## Overview

This project includes both **Python** and **R** implementations of the analysis pipeline. Both pipelines make **identical analytical decisions** to ensure reproducibility across platforms. The R pipeline additionally includes robustness analyses using lme4's true nested random effects, which Python's statsmodels cannot replicate.

## Why Two Implementations?

### 1. Reproducibility

Running the same analysis in two different statistical environments confirms that results are not artifacts of a particular software implementation. This is particularly important for multilevel models, where different packages may use slightly different estimation algorithms.

### 2. Best Practices

R's lme4 package is the **gold standard** for multilevel modeling in social science research:
- Widely used and extensively tested
- Supports complex random effects structures
- Well-documented with active community support
- Required for many academic publications

### 3. Accessibility

Python is increasingly popular for data analysis and provides:
- Broader audience reach
- Integration with modern data science workflows
- Streamlit for interactive dashboards
- Easier deployment in non-academic contexts

### 4. Complementary Capabilities

| Capability | Python | R |
|------------|--------|---|
| Two-level random intercepts | Yes (statsmodels) | Yes (lme4) |
| Nested random effects | No | Yes |
| Interactive dashboard | Streamlit | Shiny |
| Geographic visualization | geopandas/folium | sf/leaflet |
| Pipeline orchestration | Custom script | targets |

## Identical Decisions

The following analytical decisions are **identical** across both pipelines:

### Data Processing

| Decision | Specification |
|----------|---------------|
| Survey data source | SCoRE Netherlands 2017 (score.dta) |
| Admin data source | CBS StatLine Table 84286NED |
| Geographic ID creation | Buurtcode → buurt_id (8 digits), wijk_id (6), gemeente_id (4) |
| Missing value handling | Listwise deletion for model variables |

### Variable Transformations

#### Dependent Variable Construction

The dependent variable measures support for government redistribution:

| Variable | Source | Transformation | Scale |
|----------|--------|----------------|-------|
| DV_single | red_inc_diff | (value - 1) / 6 × 100 | 0-100 |
| DV_2item | red_inc_diff + gov_int | Mean → rescale 0-100 | 0-100 |
| DV_3item | red_inc_diff + gov_int + union_pref | Mean → rescale 0-100 | 0-100 |

**Original survey item (red_inc_diff):**
> "The government should reduce differences in income levels."
> 1 = Strongly disagree, 7 = Strongly agree

#### Individual Controls

| Variable | Transformation |
|----------|----------------|
| Age | Z-score standardized |
| Education | Z-score standardized (years) |
| Sex | Factor: Male, Female, Other |
| Employment | 8-level factor |
| born_in_nl | Categorical (1-6 scale) |

#### Income Proxy (for H3)

| Variable | Construction |
|----------|--------------|
| wealth_index | Sum of homeownership + financial assets (0-4) |
| high_wealth | Binary: wealth_index >= 2 |

#### Context Variables

| Variable | Transformation |
|----------|----------------|
| All b_*, w_*, g_* | Z-score standardized |

### Inequality Indices

Both pipelines create identical inequality measures:

```
b_income_polarization = b_perc_low40_hh + b_perc_high20_hh
b_income_ratio = b_perc_high20_hh / (|b_perc_low40_hh| + 0.01)
```

### Model Specifications

**Two-Level Models** (identical in both):

| Model | Formula |
|-------|---------|
| M0 | `DV_single ~ 1 + (1\|buurt_id)` |
| M1 | `DV_single ~ b_perc_low40_hh + (1\|buurt_id)` |
| M2 | `+ age + sex + education + employment_status + occupation + born_in_nl` |
| M3 | `+ b_pop_dens + b_pop_over_65 + b_pop_nonwest + b_perc_low_inc_hh + b_perc_soc_min_hh` |

### Estimation

| Setting | Value |
|---------|-------|
| Estimation method | REML (Restricted Maximum Likelihood) |
| Optimizer | Default for each package |
| Convergence criteria | Package defaults |

### H3 Test: Cross-Level Interaction

Both pipelines test whether individual income (proxied by wealth_index) moderates the neighborhood effect:

```
DV_single ~ b_perc_low40_hh * wealth_index + controls + (1|buurt_id)
```

**Interpretation:**
- Negative interaction → H3 supported (neighborhood effect weaker for high-income)
- Non-significant interaction → H3 not supported

### Sensitivity Analyses

Both pipelines test the same robustness specifications:

1. Base model (DV_single)
2. 2-item composite DV
3. 3-item composite DV
4. Dutch-born only subsample
5. **Income ratio model** (alternative inequality measure)
6. **Wealth interaction** (H3 cross-level interaction test)

## R-Specific Extensions

The R pipeline includes additional analyses that Python cannot replicate:

### True Nested Random Effects

```r
DV_single ~ predictors + (1|gemeente_id) + (1|wijk_id) + (1|buurt_id)
```

This properly partitions variance across all geographic levels, providing:

- ICC at gemeente level
- ICC at wijk level
- ICC at buurt level
- Proper variance decomposition

### Why Python Can't Do This

Python's statsmodels `mixedlm()` function:
- Only supports a single grouping variable
- Cannot specify crossed or nested random effects
- Would require using PyMC3/Stan for Bayesian multilevel models (computationally intensive)

The Python four-level models use a workaround:
- Buurt as the primary grouping variable
- Wijk and gemeente predictors as **fixed effects**
- This understates higher-level random variation

## File Correspondence

| Python | R |
|--------|---|
| `python/src/extract.py` | `R/01_extract.R` |
| `python/src/transform.py` | `R/02_transform.R` |
| `python/src/merge.py` | `R/03_merge.R` |
| `python/src/analyze.py` | `R/04_analysis.R` |
| `python/run_pipeline.py` | `_targets.R` |
| `python/dashboard/` | `R/shiny/` |

## Expected Results

If both pipelines are correct, they should produce:

### Identical or Near-Identical

- Sample sizes (after listwise deletion)
- ICC values (within rounding error)
- Fixed effect coefficients
- Standard errors
- Significance conclusions

### Potentially Different

- Exact optimization results (different algorithms)
- Random effect estimates (numerical precision)
- AIC/BIC values (different baseline calculations)

## Verification

To verify pipeline alignment:

```bash
# Run Python pipeline
cd python
python run_pipeline.py

# Run R pipeline
Rscript -e "targets::tar_make()"

# Compare key outputs
```

Key metrics to compare:
- N observations
- N clusters (buurten)
- ICC from empty model
- Key predictor coefficient in M3
- Sensitivity analysis results

## When to Use Which Pipeline

### Use Python When:

- Integrating with modern data science workflows
- Building web-based dashboards for non-technical audiences
- Rapid prototyping and exploration
- Geographic visualization with geopandas

### Use R When:

- Publication in academic journals (reviewers expect lme4)
- True nested random effects are needed
- Complex random effects structures
- Using established R ecosystem (tidyverse, targets)

### Use Both When:

- Maximum reproducibility is required
- Results need to be confirmed across platforms
- Different audiences need different interfaces

---

*Last updated: February 2025*
