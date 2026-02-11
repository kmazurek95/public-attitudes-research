# Study Limitations

This document provides a comprehensive discussion of the limitations of this study on neighborhood effects and redistribution preferences.

## Data Limitations

### 1. Cross-Sectional Design

This study uses cross-sectional data (SCoRE 2017), which limits causal inference:

- **Cannot establish temporal ordering**: We observe neighborhood composition and attitudes at the same time, not whether neighborhood exposure *preceded* attitude formation
- **Cannot rule out reverse causality**: People may select into neighborhoods based on existing preferences
- **Cannot account for exposure duration**: Length of residence may matter, but is not measured

**Mitigation**: We interpret results as associations, not causal effects. The findings are consistent with multiple causal interpretations.

### 2. Small Cluster Sizes

The survey has an average of ~3 respondents per neighborhood (buurt), with many singleton clusters (only 1 respondent):

- **Reduces precision** of random effects estimates
- **May underestimate ICC** and neighborhood-level variance
- **Limits power** to detect neighborhood effects
- **Inflates standard errors** for neighborhood-level predictors

**Mitigation**:
- Focus on two-level models where estimation is more stable
- Interpret ICC as a lower bound for neighborhood effects
- Use REML estimation (more appropriate for small clusters)

### 3. Administrative Boundaries

Dutch geographic units (buurt, wijk, gemeente) are administrative boundaries that may not reflect actual social spaces:

- **Modifiable Areal Unit Problem (MAUP)**: Results may differ at different aggregation levels
- **Social boundaries ≠ administrative boundaries**: Neighbors may interact across buurt lines
- **"Neighborhood" perception varies**: What residents consider their neighborhood may differ from official boundaries

**Mitigation**: Test effects at multiple geographic levels (buurt, wijk, gemeente).

### 4. Survey Timing Mismatch

- **Survey data**: 2017
- **Administrative data**: 2018
- Slight temporal mismatch between individual attitudes and neighborhood characteristics

**Impact**: Minimal, as neighborhood characteristics change slowly.

### 5. Missing Variables

Some theoretically important variables are not available:

- **Meritocratic beliefs**: A key mediator in the theoretical model
- **Individual income**: Only wealth proxy variables available
- **Residential tenure**: How long respondent has lived in neighborhood
- **Social networks**: Extent of local vs. non-local ties

## Methodological Limitations

### 6. Python statsmodels Limitations

Python's statsmodels cannot fit true nested random effects:

- **Cannot specify**: `(1|gemeente) + (1|wijk) + (1|buurt)`
- **Approximation used**: Buurt as grouping variable with higher-level fixed effects
- **This understates** higher-level variance components

**Mitigation**: R implementation with lme4 provides true nested models as robustness check.

### 7. Operationalization of Key Variables

**Dependent Variable**:
- Single item: "Government should reduce income differences" (1-7 scale)
- Transformed to 0-100 scale
- May not capture full complexity of redistribution preferences
- Alternatives tested: 2-item and 3-item composites

**Key Predictor**:
- % households in bottom 40% of income distribution (`b_perc_low40_hh`)
- Measures **poverty concentration**, not inequality per se
- Alternative: Income ratio (high20/low40) tested in sensitivity analyses

**Individual SES**:
- No direct income measure; wealth proxy from asset ownership
- Occupation classification available but has missing data

### 8. Omitted Variable Bias

Cannot control for all individual-level confounders:

- **Personality traits**: Openness, conscientiousness may affect both neighborhood choice and attitudes
- **Political socialization**: Family political background
- **Social networks**: Quality and breadth of social connections
- **Media consumption**: News sources and exposure
- **Past experiences**: Economic shocks, mobility history

### 9. Measurement Error

All self-report measures subject to:

- **Social desirability bias**: May overstate egalitarian attitudes
- **Response style effects**: Acquiescence, extreme responding
- **Recall bias**: For retrospective items

## Generalizability Limitations

### 10. Single Country

Results specific to the Netherlands may not generalize:

- **Relatively egalitarian society**: Lower Gini than US, UK
- **Strong welfare state**: May reduce salience of redistribution issue
- **Low residential segregation**: Less variation in neighborhood composition
- **Specific political context**: Multi-party system, consensus democracy
- **Small geographic units**: Dutch buurten (~500-2000 residents) may be smaller than "neighborhoods" in other countries

### 11. Pre-COVID Data

Survey conducted in 2017, before COVID-19:

- **Post-pandemic attitudes may differ**: COVID highlighted inequalities
- **Inequality perceptions may have shifted**: Media coverage increased
- **Remote work** may change relevance of neighborhood for social exposure

## Statistical Limitations

### 12. Multiple Testing

Multiple model specifications and sensitivity analyses increase Type I error risk:

- M0, M1, M2, M3 model sequence
- Alternative DV specifications (1-item, 2-item, 3-item)
- Subgroup analyses (Dutch-born only)
- Income ratio alternative specification

**Mitigation**: Focus on overall pattern rather than individual p-values. Key finding (null effect in full model) is consistent across specifications.

### 13. Model Specification

Linear mixed models assume:

- **Normality of residuals**: May be violated with bounded DV
- **Homoscedasticity**: Constant variance across groups
- **Linear relationships**: May miss non-linear effects
- **Correct random effects structure**: True nesting may be more complex

Violations may affect inference, though MLM is relatively robust to moderate departures.

### 14. Variance Estimation

- **Random effects may be confounded** with unobserved individual heterogeneity
- **ICC interpretation** assumes all between-neighborhood variance is "contextual"
- Some variance may reflect **compositional effects** (who lives where) rather than **contextual effects** (neighborhood influence)

## Summary: Implications for Interpretation

Given these limitations, findings should be interpreted as:

1. **Suggestive** rather than definitive
2. **Context-specific** to the Netherlands
3. **Lower bounds** for neighborhood effects (due to small clusters)
4. **Associations** rather than causal effects
5. **Robust** to alternative specifications within data constraints

## Recommendations for Future Research

To address these limitations, future research should:

1. **Longitudinal designs**: Track individuals over time to establish temporal ordering
2. **Oversampling of neighborhoods**: Larger cluster sizes for more precise estimates
3. **Multi-country comparisons**: Test whether Dutch results generalize
4. **Natural experiments**: Exploit housing assignment or redistricting for causal identification
5. **Mediator measurement**: Include meritocratic beliefs as potential mediator
6. **Alternative boundaries**: Test self-reported neighborhood definitions
7. **Network data**: Measure actual social connections vs. physical proximity

---

*Last updated: February 2025*
