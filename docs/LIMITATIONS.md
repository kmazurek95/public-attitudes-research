# Study Limitations

## Data

Survey data come from SCoRE, *Sub-national Context and Radical Right Support in Europe*. The
Netherlands sample was fielded in 2017 by the data provider GfK and is restricted-use.

SCoRE 2017 is cross-sectional. It observes neighbourhood composition and attitudes at the same
moment, so the results are associations rather than causal effects: temporal ordering is
unobserved, and residential self-selection on pre-existing preferences cannot be ruled out.

Cluster sizes are small. The survey averages roughly 3 respondents per buurt, with many singleton
clusters. This reduces the precision of the random-effects estimates, inflates standard errors on
neighbourhood-level predictors, and limits power. The ICC should be read as a lower bound.

The survey and the administrative data are from the same year: the CBS indicators are table
83765NED, *Kerncijfers wijken en buurten* 2017, matching the 2017 fielding.

Several variables are unavailable. There is no direct individual income measure, so a wealth proxy
built from asset ownership stands in. Residential tenure is not measured, so exposure duration is
unknown. Meritocratic belief, a candidate mediator, is not measured.

## Geography

About 89% of respondents match an administrative buurt at the neighbourhood level. The cause is not
data vintage: the administrative table is CBS 83765NED, *Kerncijfers wijken en buurten* 2017, the
same year the survey was fielded, so the survey-year table is already in use and does not close the
gap.

Of the 4,043 distinct well-formed survey buurtcodes, 311 appear in neither the 2017 nor the 2018
CBS table — 236 with a valid gemeente code but a buurt code CBS has never published, and 75 in
gemeenten retired before 2017. A further 5 are lost to a defect in the local CBS export, which
leaves all ten buurt rows for Nuenen, Gerwen en Nederwetten (GM0820) blank although CBS publishes
them in both years. Reconciling the 311 would require a CBS buurt-code crosswalk across years,
which is not attempted here; no change to the derivation code reaches them.

Cases that fail to match are dropped by listwise deletion, so the analysis sample is not a random
subset of respondents.

The identifier derivation issue is resolved. Padding in `create_geo_ids` was corrected to
`sprintf("%08d", ...)`; the previous approach corrupted round-numbered codes via scientific
notation. This affected 5 of 7,987 codes and 2 gemeente codes, and moved M3 by +0.071 (1.128 →
1.199, p 0.237 → 0.207). The conclusion is unchanged; the estimates are not. See
[`outputs/MODELS_SUMMARY_fixed.md`](../outputs/MODELS_SUMMARY_fixed.md) for the before/after
comparison.

Administrative units are not social ones. Buurten (~500–2,000 residents) may be smaller than the
areas residents themselves treat as their neighbourhood, and estimates may differ at other levels
of aggregation.

## Measurement

The dependent variable is a single item ("government should reduce income differences", 1–7,
rescaled to 0–100). Two- and three-item composites are tested as alternatives.

The key predictor is the percentage of households in the bottom 40% of the income distribution
(`b_perc_low40_hh`). It measures poverty concentration rather than dispersion; an income ratio
(high20/low40) is tested as an alternative.

All individual measures are self-reported, and so subject to social-desirability and
response-style effects, which may bias stated egalitarian attitudes upward.

## Generalizability

Results are specific to the Netherlands: comparatively low income inequality and residential
segregation, a strong welfare state, and a multi-party consensus system. Effects observed here (or
not observed) need not transfer to more unequal or more segregated contexts. The data also predates
COVID-19.

## Multiple specifications

The model sequence (M0–M3), the alternative DVs, the Dutch-born subgroup and the income-ratio
specification together raise the risk of a Type I error across the set. The reported conclusion
rests on the consistency of the pattern rather than on any single coefficient's p-value.

---

Research Master's in Social Sciences, University of Amsterdam, Amsterdam Institute for Social
Science Research (AISSR), February 2023.
