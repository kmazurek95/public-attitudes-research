# Neighbourhood effects on redistribution support (synthetic-data demo)

A small, self-contained multilevel-modelling pipeline in R that anyone can clone and run. It
reproduces the structure and method of the neighbourhood-effects analysis (individuals nested in
neighbourhoods; outcome = support for redistribution) on synthetic data generated locally.

> The study itself used restricted-use SCoRE Netherlands survey data, which is not included here.
> This demo exists to make the method inspectable and to show that the pipeline runs. It does not
> release data or reproduce the study's estimates.

## Run it

`lme4` is the only dependency beyond base R. From this directory:

```
Rscript run_all.R
```

Or interactively: `source("run_all.R")`.

## What it does

| Step | Script | Output |
|---|---|---|
| Simulate a neighbourhood-nested survey (300 neighbourhoods) | `R/00_simulate_data.R` | `data/synthetic_survey.csv` |
| Fit the multilevel sequence (null → + context → + controls) with `lme4` | `R/01_fit_models.R` | `data/models.rds` |
| Summarise fixed effects + ICC | `R/02_results.R` | `results/summary.txt` |

The generator plants a strong individual SES gradient and a neighbourhood-context effect of exactly
zero, with a small between-neighbourhood variance coming from the random intercept. The demo's null
is therefore built in, not found: it shows the pipeline runs and recovers what was planted, and it
is not evidence for any result about real neighbourhoods. Everything is seeded, so runs are
deterministic.

## Scope

Just the R modelling pipeline: no real data, no external services. Deliberately minimal.
