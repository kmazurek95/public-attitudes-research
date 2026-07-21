# Multilevel model summary (corrected geography)

Aggregate results for the two-level models (individuals nested in buurten). Outcome: support for
redistribution, rescaled 0–100. Key predictor: `b_perc_low40_hh`, the share of households in the
bottom 40% of the income distribution, z-scored, so coefficients are per standard deviation.
Estimated with `lmer(REML = TRUE)`.

A note on p-values: the headline specification is fitted with `lmerTest::lmer`, so its p-values use
the Satterthwaite approximation (with denominator degrees of freedom reported). The sensitivity
specification is fitted by `fit_two_level_models` in [`R/04_analysis.R`](../R/04_analysis.R), which
calls `lme4::lmer` namespaced and therefore returns no Satterthwaite column; its p-values use the
normal approximation (2 × Φ(−|t|)). With these degrees of freedom (> 1,400) the two methods agree to
about three decimal places, so the difference does not affect any conclusion here.

These are aggregate model summaries. No individual-level records are reproduced here or anywhere in
this repository.

---

## Headline specification

Individual controls: age, sex, education, employment status, country of birth. Buurt controls:
population density, share aged 65+, share non-Western, share low-income households. Singleton
buurten (n < 2 respondents) are excluded, as they cannot contribute to between-neighbourhood
variance. `b_perc_soc_min_hh` is excluded for collinearity (see *Sensitivity* below).

Corrected geography, N = 3,931 in 1,382 buurten (mean cluster size 2.84):

| Model | β (per SD) | SE | df | t | p | |
|---|---|---|---|---|---|---|
| M0 (empty) | | | | | | ICC = 0.0334 (τ² = 25.24, σ² = 729.26) |
| M1 (bivariate) | +3.294 | 0.465 | 1278.6 | +7.084 | < .001 | significant |
| M2 (+ individual controls) | +2.815 | 0.451 | 1285.4 | +6.247 | < .001 | significant |
| M3 (+ buurt controls) | +1.199 | 0.951 | 1431.3 | +1.261 | 0.207 | not significant |

M3 95% CI: [−0.664, +3.063].

The headline result is a null. Between-neighbourhood variance is small (ICC 3.3%; ~96.7% of
variation is within neighbourhoods), and the neighbourhood income-composition effect, strong
bivariately, does not survive individual and buurt-level controls.

### Effect of the geography correction

| | As-is geography | Corrected geography | Δ |
|---|---|---|---|
| N / buurten | 3,927 / 1,380 | 3,931 / 1,382 | +4 / +2 |
| ICC (M0) | 0.0331 | 0.0334 | +0.0003 |
| M1 | +3.277 [0.465] | +3.294 [0.465] | +0.017 |
| M2 | +2.801 [0.451] | +2.815 [0.451] | +0.014 |
| M3 | +1.128 [0.953], p = 0.237 | +1.199 [0.951], p = 0.207 | +0.071 |

The correction changes no conclusion. The null now holds *on* the corrected geography rather than
by inheritance from an earlier build.

---

## Sensitivity: pipeline specification

The pipeline specification in [`R/04_analysis.R`](../R/04_analysis.R) (`fit_two_level_models`)
gives a significant M3. It adds occupation as a control and retains `b_perc_soc_min_hh`
(VIF > 27, r = 0.98 with `b_perc_low_inc_hh`), which the headline model drops. It also retains
singleton buurten, giving N 5,679 against 3,931.

| Model | As-is geography | Corrected geography |
|---|---|---|
| ICC (M0) | 0.0334 | 0.0337 |
| M1 (bivariate) | +3.660 [0.371], p < .001 | +3.672 [0.371], p < .001 |
| M2 (+ individual controls) | +3.179 [0.362], p < .001 | +3.188 [0.362], p < .001 |
| M3 (+ buurt controls) | +1.889 [0.773], p = 0.015 | +1.929 [0.772], p = 0.012 |
| Analysis-sample N | 5,675 | 5,679 |

The divergence between +1.199 (p = 0.207) and +1.929 (p = 0.012) comes from the specification, not
the geography; it is present identically before and after the correction. Retaining a control with
VIF > 27 inflates the standard error on the key predictor without adding explanatory power, which
is why the headline model drops it.

---

## Geography correction

The neighbourhood identifier derivation was corrected in
[`R/02_transform.R`](../R/02_transform.R) (`create_geo_ids`). The previous implementation padded the
numeric `Buurtcode` with `paste0()`/`as.character()`, which R renders in scientific notation for
round values (`400000` → `"4e+05"`), producing 5 malformed buurt identifiers and 2 spurious
gemeente codes. `sprintf("%08d", as.integer(round(Buurtcode)))` is width-robust and
notation-proof.

| Metric | As-is | Corrected |
|---|---|---|
| Well-formed 8-character `buurt_id` | 7,982 (5 malformed) | 7,987 |
| Distinct survey buurt / wijk / gemeente | 4,043 / 1,784 / 388 | 4,043 / 1,783 / 386 |
| Survey→admin match (buurt / wijk / gemeente) | 89.3% / 94.5% / 98.1% | 89.4% / 94.6% / 98.2% |
| Codes where old and new derivation differ | — | 5 of 7,987 (0.06%) |

## Why the buurt match rate is ~89%

The cause is data vintage rather than a code defect. SCoRE was fielded in 2017; the CBS
administrative table (84286NED) is 2018. Roughly 316 well-formed survey buurten and ~10 gemeenten
do not exist in the 2018 table because of Dutch neighbourhood renumbering and municipal mergers
between the two years. This is addressable only by using a survey-year CBS table, not by any change
to the derivation code. The padding correction above is a footnote by comparison.
