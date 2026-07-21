# Neighbourhood effects on support for redistribution (Netherlands)

A multilevel analysis of whether the income composition of a person's neighbourhood is associated
with their support for redistribution. Individuals are nested in neighbourhoods (buurten), using
the SCoRE Netherlands 2017 survey linked to CBS StatLine neighbourhood indicators.

## Data

The SCoRE survey data is restricted-use and is not included in this repository. Access is through
the data provider, GfK, under its terms. N = 8,013. The CBS neighbourhood indicators (table
84286NED, *Kerncijfers wijken en buurten* 2018) are open data.

## What's here

- [`r-pipeline-demo/`](r-pipeline-demo/): a self-contained R demo of the multilevel pipeline on
  synthetic data generated locally. This is the part that runs.
- [`R/`](R/) and [`_targets.R`](_targets.R): published as a code record of the model specifications
  and variable construction; not runnable, as no data build step is included. Note that
  [`R/04_analysis.R`](R/04_analysis.R) implements the *sensitivity* specification, not the headline
  one: it retains occupation and the collinear `b_perc_soc_min_hh`, and keeps singleton buurten, so
  its M3 is +1.93 rather than the headline +1.20. See
  [`outputs/MODELS_SUMMARY_fixed.md`](outputs/MODELS_SUMMARY_fixed.md) for both.
- [`outputs/MODELS_SUMMARY_fixed.md`](outputs/MODELS_SUMMARY_fixed.md): the aggregate M0–M3 model
  table on the corrected geography.
- [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md): study limitations.

## Running the demo

Requires `lme4`:

```
cd r-pipeline-demo && Rscript run_all.R
```

The synthetic generator plants a zero neighbourhood-context effect, so the demo cannot produce
anything else. It shows that the pipeline executes; it is not evidence for any result.

## What the analysis found

All estimates below are on the analysis sample: **N = 3,931 respondents in 1,382 buurten** —
complete cases that match a 2018 CBS buurt, excluding singleton buurten. That is a subset of the
8,013 respondents surveyed, for the reasons in *Main limitation* below.

Between-neighbourhood variance in support for redistribution is small. The empty model puts the ICC
at 0.033, so roughly 96.7% of the variation sits within neighbourhoods rather than between them,
and that holds across specifications.

Neighbourhood income composition is a strong bivariate predictor that attenuates as controls enter:
+3.29 per SD alone, +2.82 after individual controls, and +1.20 per SD (p = 0.21) once collinear
buurt-level controls are added. The headline is a null. No contextual effect of neighbourhood
income composition survives once who lives there is accounted for.

The geography correction changes no conclusion, and the null now holds *on* the corrected geography
rather than by inheritance from an earlier build: correcting the identifier derivation moved the M3
coefficient by +0.071 (1.128 → 1.199) and the p-value from 0.237 to 0.207.

A sensitivity specification that retains occupation and the collinear `b_perc_soc_min_hh`
(VIF > 27, r = 0.98 with `b_perc_low_inc_hh`), and keeps singleton buurten, gives +1.93 per SD
(p = 0.012) on a larger sample of N = 5,679. Full comparison in
[`outputs/MODELS_SUMMARY_fixed.md`](outputs/MODELS_SUMMARY_fixed.md).

### Main limitation

About 89% of respondents match to a 2018 CBS buurt. The cause is data vintage, not a code defect:
SCoRE was fielded in 2017, and Dutch neighbourhood renumbering and municipal mergers occurred
before the 2018 administrative table was compiled. Only a survey-year CBS table would close the
gap. The identifier padding correction is a footnote by comparison; it affected 5 of 7,987 codes.
Unmatched cases are dropped by listwise deletion, so the analysis sample is not a random subset of
respondents.

## Credit

Research Master's in Social Sciences, University of Amsterdam, Amsterdam Institute for Social
Science Research (AISSR), February 2023.
All errors are my own.

## License

MIT (code). The survey data is not covered by this license and is not included.
