# Operationalization Analysis: Theory vs. Implementation

## Overview

This document compares the theoretical framework in your draft writeup with the current implementation, identifies gaps, and recommends improvements.

---

## 1. Key Theoretical Concepts from Draft Writeup

### The "Inferential Spaces" Framework (Mijs, 2018)

> "Environments that shape the development of a person's inequality beliefs by exposing that person to a certain type and range of information, but not to their counterfactuals"

**Core Mechanism:**
1. Local social context → Shapes information exposure
2. Information exposure → Forms beliefs about inequality
3. Beliefs (meritocracy vs. structural) → Drive redistribution preferences

### Three Hypotheses

| Hypothesis | Statement | Current Operationalization |
|------------|-----------|---------------------------|
| **H1** | Neighborhoods with higher income inequality → greater redistribution support | ✓ `b_perc_low40_hh` as key predictor |
| **H2** | Neighborhood effects > City/Regional effects | ✓ Four-level models compare buurt/wijk/gemeente |
| **H3** | Individual income moderates the neighborhood effect | ⚠️ **NOT IMPLEMENTED** - no income variable |

---

## 2. Implementation Gaps

### Critical Gap: Missing Mediator Variables

Your theoretical framework emphasizes **meritocracy beliefs** and **structural inequality beliefs** as key mediators:

```
Neighborhood inequality → Beliefs → Redistribution preferences
```

**Current Implementation:**
```
Neighborhood inequality → Redistribution preferences (direct effect only)
```

**Problem:** Without measuring beliefs, you can only test the reduced-form relationship, not the theoretical mechanism.

**Possible Solutions:**
1. Acknowledge this as a limitation in your writeup
2. Frame the analysis as testing the "net effect" rather than the mechanism
3. Search for proxy variables in SCoRE (e.g., political ideology items)

### Critical Gap: Missing Moderator (Individual Income)

H3 proposes that individual income moderates the neighborhood effect:

> "Income level will negatively moderate the relationship between neighborhood inequality and support for redistribution"

**Current Data:** The SCoRE survey does not include individual/household income in the extracted variables.

**Check:** Review the original SCoRE documentation to confirm if income was measured but not extracted.

### Gap: Inequality vs. Poverty Concentration

**Theory:** "Neighborhood income inequality" suggests a measure of dispersion (rich vs. poor).

**Implementation:** `b_perc_low40_hh` measures poverty concentration, not inequality per se.

**Better Operationalization:**
```python
# Create an inequality index using both ends of the distribution
inequality_index = b_perc_low40_hh + b_perc_high20_hh

# Or: Ratio of high to low income households
income_polarization = b_perc_high20_hh / (b_perc_low40_hh + 0.01)
```

---

## 3. Recommended Variable Additions

### From CBS Data (Currently Available but Unused)

| Variable | CBS Column | Theoretical Relevance |
|----------|-----------|----------------------|
| **% High-income HH** | `perc_high20_hh` | Captures top-end inequality |
| **Median wealth** | `MediaanVermogenVanParticuliereHuish_79` | Asset inequality |
| **Home value (WOZ)** | `GemiddeldeWOZWaardeVanWoningen_35` | Visible wealth indicator |
| **Home ownership** | `owner_occupied` | Tenure inequality |
| **Cars per HH** | `PersonenautoSPerHuishouden_102` | Visible consumption inequality |
| **Welfare recipients** | `PersonenPerSoortUitkeringBijstand_80` | Social deprivation |

### Recommended Inequality Indices to Create

```python
# 1. Income Polarization Index
# Combines low and high income percentages
b_income_polarization = b_perc_low40_hh + b_perc_high20_hh

# 2. Gini-like Approximation
# Higher when both extremes are large
b_income_gini_approx = (b_perc_low40_hh * b_perc_high20_hh) ** 0.5

# 3. Affluence-Poverty Ratio
# Higher values = more affluent relative to poor
b_affluence_ratio = b_perc_high20_hh / (b_perc_low40_hh + 1)

# 4. Wealth Inequality (using home values)
# Compare neighborhood avg home value to national average
b_wealth_index = b_avg_home_value / national_avg_home_value
```

---

## 4. Model Specification Comparison

### As Described in Theory

```
DV: Redistribution Preferences
Key Predictor: Neighborhood Income Inequality
Mediators: Meritocracy Beliefs, Structural Inequality Beliefs
Moderator: Individual Income
Controls: Age, Education, Employment, Religion, Class
Hierarchy: Individual → Neighborhood → District → Municipality
```

### Current Implementation

```
DV: DV_single (government should reduce income differences, 0-100)
Key Predictor: b_perc_low40_hh (% low-income households)
Mediators: NONE
Moderator: NONE
Controls: age, sex, education, employment_status, occupation, born_in_nl
Hierarchy: Individual → Buurt (with wijk/gemeente predictors)
```

### Recommended Implementation

```python
# Enhanced Model Specification
DV: DV_single (or multi-item composite)

Key Predictors (all levels):
- b_perc_low40_hh: % low-income households (buurt)
- b_perc_high20_hh: % high-income households (buurt)  # ADD
- b_income_polarization: Combined inequality index     # ADD
- w_perc_low40_hh: % low-income households (wijk)
- g_perc_low40_hh: % low-income households (gemeente)

Individual Controls:
- age (z-scored)
- sex
- education (z-scored)
- employment_status
- occupation
- born_in_nl

Neighborhood Controls:
- b_pop_dens: Population density
- b_pop_over_65: % seniors
- b_pop_nonwest: % non-Western immigrants
- b_avg_home_value: Average home value              # ADD
- b_owner_occupied: % homeowners                    # ADD

Interaction Terms (if individual income available):
- b_perc_low40_hh × individual_income               # H3 test
```

---

## 5. Alignment Recommendations

### Short-term (Align with Current Data)

1. **Add `perc_high20_hh`** to capture both ends of income distribution
2. **Create inequality indices** combining low40 and high20 percentages
3. **Frame the analysis** as testing reduced-form effects (not mechanisms)
4. **Acknowledge limitations** regarding missing mediator/moderator variables

### Medium-term (Enhance Analysis)

1. **Add geographic names** for interpretability (use `src/geography.py`)
2. **Create map visualizations** to show spatial patterns
3. **Test alternative DVs** (2-item and 3-item composites)
4. **Run sensitivity analyses** with different inequality measures

### Long-term (Future Data Collection)

1. **Include meritocracy belief items** in future surveys
2. **Measure individual income** for moderation tests
3. **Add subjective inequality perception** items
4. **Consider longitudinal design** for causal inference

---

## 6. Updated Hypotheses for Current Analysis

Given data limitations, reframe hypotheses:

### H1 (Revised)
> Neighborhoods with higher concentrations of low-income households will be associated with stronger support for redistribution, net of individual characteristics.

**Test:** Coefficient on `b_perc_low40_hh` in M3 (full controls)

### H2 (Retained)
> The effect of neighborhood income composition on redistribution support will be stronger at the buurt level than at wijk or gemeente levels.

**Test:** Compare coefficients on `b_perc_low40_hh`, `w_perc_low40_hh`, `g_perc_low40_hh` in four-level models

### H3 (Deferred)
> Cannot test income moderation without individual income data.

**Alternative:** Test whether education (as SES proxy) moderates the neighborhood effect:
- `b_perc_low40_hh × education` interaction term

---

## 7. Code Changes Needed

### Update `config.py`

```python
# Additional key predictors
KEY_PREDICTORS = [
    "b_perc_low40_hh",   # Original
    "b_perc_high20_hh",  # ADD: top-end concentration
]

# Additional buurt controls
BUURT_CONTROLS = [
    "b_pop_dens",
    "b_pop_over_65",
    "b_pop_nonwest",
    "b_perc_low_inc_hh",
    "b_perc_soc_min_hh",
    "b_avg_home_value",    # ADD
    "owner_occupied",      # ADD (will need prefix)
]
```

### Update `transform.py`

Add function to create inequality indices:

```python
def create_inequality_indices(df):
    """Create composite inequality measures."""
    # Income polarization (both ends of distribution)
    if 'b_perc_low40_hh' in df.columns and 'b_perc_high20_hh' in df.columns:
        df['b_income_polarization'] = df['b_perc_low40_hh'] + df['b_perc_high20_hh']

    # Similar for wijk and gemeente levels
    for prefix in ['w_', 'g_']:
        low_col = f'{prefix}perc_low40_hh'
        high_col = f'{prefix}perc_high20_hh'
        if low_col in df.columns and high_col in df.columns:
            df[f'{prefix}income_polarization'] = df[low_col] + df[high_col]

    return df
```

---

## Summary

| Aspect | Status | Action Needed |
|--------|--------|---------------|
| **Key Predictor** | Partial | Add `perc_high20_hh`, create inequality indices |
| **Mediators** | Missing | Acknowledge limitation; cannot test mechanism |
| **Moderator (income)** | Missing | Test education as proxy; defer H3 |
| **Geographic hierarchy** | Good | Already implemented in four-level models |
| **Geographic names** | Missing | Use new `geography.py` module |
| **Map visualizations** | Missing | Use new `geography.py` module |
| **Controls** | Good | Consider adding home value, ownership |
