# Redistribution Preferences Analysis (Python)

Multilevel analysis of how neighborhood-level income inequality shapes individual redistribution preferences in the Netherlands.

## Overview

This pipeline:
1. Loads SCoRE survey data (Netherlands, 2017, ~8,000 respondents)
2. Downloads/loads CBS neighborhood statistics via the StatLine API
3. Merges data at three geographic levels (buurt → wijk → gemeente)
4. Fits two-level random intercept models (individuals nested in neighborhoods)
5. Generates publication-ready tables and diagnostics

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python run_pipeline.py

# Or download fresh CBS data
python run_pipeline.py --use-api
```

## Project Structure

```
redistribution_analysis_python/
├── run_pipeline.py          # Main entry point
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── README.md                # This file
│
├── src/
│   ├── __init__.py
│   ├── extract.py           # CBS API + survey loading
│   ├── transform.py         # Geographic IDs, recoding
│   ├── merge.py             # Multi-level merge, validation
│   ├── analyze.py           # Multilevel models, ICC
│   └── report.py            # Tables, reports
│
├── data/
│   ├── raw/                 # Input data (score.dta, indicators.csv)
│   └── processed/           # Output data
│
└── outputs/
    ├── tables/              # Regression tables (HTML)
    └── figures/             # Plots
```

## Data Requirements

Place these files in `data/raw/`:

1. **score.dta** - SCoRE survey data (Stata format)
   - Contains redistribution attitudes, demographics, Buurtcode

2. **indicators_buurt_wijk_gemeente.csv** - CBS administrative data
   - Or use `--use-api` flag to download from CBS StatLine

## CBS API

The pipeline can download neighborhood statistics directly from CBS (Statistics Netherlands):

```python
# Test the API connection
python run_pipeline.py --test-api

# Download fresh data
python run_pipeline.py --use-api
```

CBS Table used: **84286NED** ("Kerncijfers wijken en buurten")

## Pipeline Phases

### 1. EXTRACT
- Load SCoRE survey from Stata file
- Load CBS indicators (local CSV or API)
- Validate data completeness

### 2. TRANSFORM
- Create geographic IDs (buurt_id, wijk_id, gemeente_id)
- Split admin data by geographic level
- Add level prefixes (b_, w_, g_)

### 3. MERGE
- Left join survey ← buurt ← wijk ← gemeente
- Validate match rates (~89% buurt, ~95% wijk, ~98% gemeente)
- Analyze missingness patterns

### 4. TRANSFORM (Recode)
- Create dependent variables (0-100 scale)
- Standardize age, education (z-scores)
- Recode categorical variables

### 5. ANALYZE
- Fit 4 multilevel models (empty → full)
- Calculate ICC (~2-5% variance between neighborhoods)
- Run diagnostics (VIF, residuals, random effects)
- Sensitivity analyses (alternative DVs, subsamples)

### 6. REPORT
- Generate HTML regression table
- Create summary statistics
- Save analysis report

## Configuration

Edit `config.py` to customize:

```python
# Use CBS API instead of local file
USE_CBS_API = True

# CBS table and year
CBS_TABLE_ID = "84286NED"
CBS_YEAR = "2018"

# Model specification
KEY_PREDICTOR = "b_perc_low40_hh"
GROUPING_VAR = "buurt_id"
```

## Command Line Options

```bash
python run_pipeline.py --help

Options:
  --use-api        Download fresh data from CBS API
  --no-occupation  Exclude occupation (keeps more cases)
  --test-api       Test CBS API connection
```

## Expected Output

```
ANALYSIS SUMMARY
============================================================
Observations: 5,832
Clusters (buurten): 2,156
ICC: 0.0234 (2.3% between)

Key predictor (b_perc_low40_hh):
  Coefficient: 0.847
  SE: 0.412
  95% CI: [0.039, 1.655]
============================================================
```

## Dependencies

- **pandas** - Data manipulation
- **numpy** - Numerical operations
- **pyreadstat** - Read Stata .dta files
- **cbsodata** - CBS StatLine API client
- **statsmodels** - Multilevel models (MixedLM)
- **scipy** - Statistical functions
- **tabulate** - Table formatting

## R Equivalent

This pipeline replicates the R `targets` pipeline. Key equivalences:

| R | Python |
|---|--------|
| `cbsodataR::cbs_get_data()` | `cbsodata.get_data()` |
| `haven::read_dta()` | `pyreadstat.read_dta()` |
| `lme4::lmer()` | `statsmodels.mixedlm()` |
| `performance::icc()` | Manual: `var_re / (var_re + scale)` |
| `targets::tar_make()` | `python run_pipeline.py` |

## License

Research use only. Data from CBS StatLine is open data (CC BY 4.0).
