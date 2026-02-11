# Reproducibility Guide

Instructions for reproducing the analysis and running the dashboards.

---

## Quick Start (Precomputed Results)

If you just want to explore the results without running the full pipeline:

### Python Dashboard
```bash
git clone https://github.com/[username]/attitudes-toward-income-inequality.git
cd attitudes-toward-income-inequality
pip install -r python/requirements.txt
streamlit run python/dashboard/app.py
```

### R Dashboard
```r
# From R console
shiny::runApp("R/shiny")
```

Both dashboards include precomputed results and will work without the raw survey data.

---

## Environment Requirements

### Python

**Version**: Python 3.9 or higher

**Key Packages**:
| Package | Version | Purpose |
|---------|---------|---------|
| pandas | ≥2.0.0 | Data manipulation |
| numpy | ≥1.24.0 | Numerical operations |
| statsmodels | ≥0.14.0 | Multilevel regression |
| streamlit | ≥1.30.0 | Dashboard framework |
| plotly | ≥5.18.0 | Interactive charts |
| geopandas | ≥0.14.0 | Geographic data |
| scipy | ≥1.11.0 | Statistical functions |

**Installation**:
```bash
pip install -r python/requirements.txt
```

### R

**Version**: R 4.2 or higher

**Key Packages**:
| Package | Version | Purpose |
|---------|---------|---------|
| tidyverse | ≥2.0.0 | Data manipulation |
| lme4 | ≥1.1-35 | Multilevel models |
| targets | ≥1.4.0 | Pipeline orchestration |
| shiny | ≥1.8.0 | Dashboard framework |
| cbsodataR | ≥1.0.0 | CBS API access |
| broom.mixed | ≥0.2.9 | Model tidying |

**Installation**:
```r
install.packages(c(
  "tidyverse", "lme4", "targets", "shiny",
  "cbsodataR", "broom.mixed", "here", "plotly"
))
```

---

## Data Availability

### SCoRE Survey Data

**Source**: Social and Cultural Developments in the Netherlands (SCoRE) 2017

**Access**:
- The data contains geographic identifiers and is not publicly shareable
- Researchers can request access through DANS (Data Archiving and Networked Services)
- Contact: https://dans.knaw.nl/

**Required Files**:
- `score_nl_2017.dta` (Stata format) or equivalent

**Placement**:
```
data/raw/score_nl_2017.dta
```

### CBS Administrative Data

**Source**: Statistics Netherlands (CBS) StatLine

**Table**: 84286NED - Income Statistics by Neighborhood (2018)

**Access**: Public API, no authentication required

**Automatic Download**: The pipeline automatically fetches CBS data via API:
```r
# R
cbsodataR::cbs_get_data("84286NED")

# Python
import cbsodata
cbsodata.get_data("84286NED")
```

---

## Full Reproduction Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/[username]/attitudes-toward-income-inequality.git
cd attitudes-toward-income-inequality
```

### Step 2: Obtain Survey Data

1. Request SCoRE 2017 data from DANS
2. Place the Stata file in `data/raw/`
3. Ensure the filename matches what the pipeline expects (see `python/config.py` or `R/01_extract.R`)

### Step 3: Run Pipeline

**Python**:
```bash
cd python
python run_pipeline.py
```

**R**:
```r
# From project root
targets::tar_make()
```

### Step 4: View Results

**Output files**:
- `outputs/figures/` - Generated plots
- `outputs/tables/` - Model results tables
- `data/processed/analysis_ready.csv` - Merged analysis dataset

**Dashboards**:
```bash
# Python
streamlit run python/dashboard/app.py

# R
Rscript -e "shiny::runApp('R/shiny')"
```

---

## Computational Notes

| Metric | Value |
|--------|-------|
| Estimated runtime | ~5 minutes (full pipeline) |
| Memory requirements | ~2 GB RAM |
| Disk space | ~500 MB (including CBS data) |
| GPU required | No |

### Performance Tips

- **First run**: CBS API download may take several minutes
- **Subsequent runs**: Cached data loads faster
- **R targets**: Incremental rebuilds only re-run changed steps

---

## Verification

After running the pipeline, verify key outputs:

### Check 1: Sample Size
```python
import pandas as pd
df = pd.read_csv("data/processed/analysis_ready.csv")
print(f"N = {len(df)}")  # Should be ~8,013
print(f"Complete cases = {df.dropna().shape[0]}")  # Should be ~4,748
```

### Check 2: ICC Value
The intraclass correlation should be approximately 0.034 (3.4%)

### Check 3: Model Coefficients

| Model | Expected β (poverty) | Approximate |
|-------|---------------------|-------------|
| M1 | 3.46 | ±0.5 |
| M2 | 2.94 | ±0.5 |
| M3 | 0.28 | ±0.5 |

Minor variations are expected due to:
- Different random seeds
- Software version differences
- Floating-point precision

---

## Troubleshooting

### Common Issues

**"Data file not found"**
- Ensure survey data is placed in `data/raw/`
- Check filename matches expected pattern

**"CBS API error"**
- CBS StatLine may have temporary outages
- Retry after a few minutes
- Check https://opendata.cbs.nl/statline/ for status

**"Package not found"**
- Run `pip install -r python/requirements.txt` (Python)
- Run package installation commands (R)

**"Memory error"**
- Close other applications
- CBS data download requires ~1 GB temporarily

### Getting Help

- Open an issue on GitHub
- Check existing issues for similar problems

---

## Session Information

Record your environment for reproducibility:

**Python**:
```python
import sys
import pandas as pd
import statsmodels
print(f"Python: {sys.version}")
print(f"pandas: {pd.__version__}")
print(f"statsmodels: {statsmodels.__version__}")
```

**R**:
```r
sessionInfo()
```

---

## Citation

If you use this code or methodology, please cite:

```
Mazurek, K. (2025). Neighborhood Inequality and Redistribution Preferences:
Testing the Inferential Spaces Hypothesis in the Netherlands.
University of Amsterdam.
```

---

*Last updated: February 2025*
