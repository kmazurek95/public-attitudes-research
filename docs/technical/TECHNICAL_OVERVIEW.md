# Technical Overview

Architecture, pipeline design, and implementation details.

---

## System Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA SOURCES                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   SCoRE Survey (.dta)          CBS StatLine (API)                  │
│   └── 8,013 respondents        └── Table 84286NED                  │
│   └── Attitudes, demographics  └── Neighborhood income stats       │
│                                                                     │
└───────────────┬─────────────────────────────┬───────────────────────┘
                │                             │
                ▼                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         EXTRACT LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│   Python: src/extract.py       R: 01_extract.R                     │
│   └── Load .dta via pandas     └── Load via haven                  │
│   └── CBS API via cbsodata     └── CBS API via cbsodataR           │
└───────────────┬─────────────────────────────┬───────────────────────┘
                │                             │
                ▼                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        TRANSFORM LAYER                              │
├─────────────────────────────────────────────────────────────────────┤
│   Python: src/transform.py     R: 02_transform.R                   │
│   └── Geographic ID creation   └── Geographic ID creation          │
│   └── Variable recoding        └── Variable recoding               │
│   └── DV construction          └── DV construction                 │
│   └── Standardization          └── Standardization                 │
└───────────────┬─────────────────────────────┬───────────────────────┘
                │                             │
                ▼                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          MERGE LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│   Python: src/merge.py         R: 03_merge.R                       │
│   └── Survey + CBS linkage     └── Survey + CBS linkage            │
│   └── Multi-level join         └── Multi-level join                │
│   └── Output: analysis_ready   └── Output: analysis_ready          │
└───────────────┬─────────────────────────────┬───────────────────────┘
                │                             │
                ▼                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        ANALYSIS LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│   Python: src/analyze.py       R: 04_analysis.R                    │
│   └── statsmodels MixedLM      └── lme4 multilevel                 │
│   └── 2-level models           └── 2-4 level models                │
│   └── Sensitivity tests        └── Nested random effects           │
└───────────────┬─────────────────────────────┬───────────────────────┘
                │                             │
                ▼                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PRESENTATION LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│   Python: dashboard/           R: shiny/                           │
│   └── Streamlit multi-page     └── Shiny + shinydashboard          │
│   └── Plotly visualizations    └── Plotly + ggplot2                │
│   └── Precomputed fallback     └── Precomputed fallback            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

### Python Implementation

```
python/
├── src/                        # Core processing modules
│   ├── extract.py              # Data loading (survey + CBS API)
│   ├── transform.py            # Variable construction, geographic IDs
│   ├── merge.py                # Survey + administrative data linkage
│   ├── analyze.py              # Multilevel models, sensitivity tests
│   ├── report.py               # Output generation (tables, figures)
│   └── geography.py            # Geographic utilities
│
├── dashboard/                  # Streamlit application
│   ├── app.py                  # Entry point
│   ├── pages/                  # Multi-page components
│   │   ├── 1_Data_Explorer.py
│   │   ├── 2_Geographic_View.py
│   │   ├── 3_Model_Results.py
│   │   └── 4_Key_Findings.py
│   ├── components/             # Reusable UI components
│   │   └── charts.py
│   ├── utils/                  # Helper functions
│   │   └── data_loader.py
│   └── data/                   # Precomputed results
│       └── precomputed_results.json
│
├── config.py                   # Configuration settings
├── run_pipeline.py             # Orchestration script
└── requirements.txt            # Dependencies
```

### R Implementation

```
R/
├── 00_packages.R               # Package loading
├── 01_extract.R                # Data extraction
├── 02_transform.R              # Variable transformation
├── 03_merge.R                  # Data merging
├── 04_analysis.R               # Multilevel models
│
├── shiny/                      # Shiny application
│   ├── app.R                   # Entry point
│   ├── global.R                # Shared data, precomputed results
│   ├── ui.R                    # User interface
│   ├── server.R                # Server logic
│   ├── modules/                # Modular components
│   └── utils/                  # Helper functions
│
└── _targets.R                  # Pipeline definition (project root)
```

---

## Model Specifications

### Two-Level Model (Primary)

**Structure**:
- Level 1: Individuals (n = 4,748)
- Level 2: Neighborhoods/buurt (n = 1,572)

**Specification** (R notation):
```r
# M0: Empty model
lmer(DV_single ~ 1 + (1 | buurt_id), data = df)

# M1: Key predictor
lmer(DV_single ~ b_perc_low40_hh_z + (1 | buurt_id), data = df)

# M2: + Individual controls
lmer(DV_single ~ b_perc_low40_hh_z + age_z + sex + education +
     employment + migration + (1 | buurt_id), data = df)

# M3: + Neighborhood controls
lmer(DV_single ~ b_perc_low40_hh_z + age_z + sex + education +
     employment + migration + b_pop_density_z + b_pct_65plus_z +
     b_pct_nonwestern_z + (1 | buurt_id), data = df)
```

**Python equivalent** (statsmodels):
```python
# M0
smf.mixedlm("DV_single ~ 1", data=df, groups="buurt_id").fit(reml=True)

# M1-M3: Add predictors progressively
smf.mixedlm(formula, data=df, groups="buurt_id").fit(reml=True)
```

### Four-Level Model (R Only)

**Structure**:
- Level 1: Individuals
- Level 2: Buurt (neighborhood)
- Level 3: Wijk (district)
- Level 4: Gemeente (municipality)

**Specification**:
```r
lmer(DV_single ~ b_perc_low40_hh_z + controls +
     (1 | gemeente_id) + (1 | wijk_id) + (1 | buurt_id),
     data = df)
```

**Note**: Python's statsmodels cannot fit true nested random effects. The R implementation provides this as a robustness check.

### Cross-Level Interaction (H3)

```r
lmer(DV_single ~ b_perc_low40_hh_z * wealth_index + controls +
     (1 | buurt_id), data = df)
```

---

## Variable Transformations

### Dependent Variable

**Construction** (rescaling to 0-100):
```python
# Original: 1-7 scale
# Formula: ((response - 1) / 6) * 100
df['DV_single'] = ((df['red_inc_diff'] - 1) / 6) * 100
```

**Alternative DVs**:
- `DV_2item`: Mean of redistribution + government intervention
- `DV_3item`: Mean of redistribution + government intervention + union preference

### Key Predictor

**Variable**: `b_perc_low40_hh` (% households in bottom 40% of national income)

**Standardization**:
```python
df['b_perc_low40_hh_z'] = (df['b_perc_low40_hh'] - df['b_perc_low40_hh'].mean()) / df['b_perc_low40_hh'].std()
```

### Geographic Identifiers

**Hierarchy**:
```
gemeente_id (municipality) → wijk_id (district) → buurt_id (neighborhood)
```

**Construction**:
- CBS codes: 8-digit numeric
- Format: `GM0363WK00BU01` → `gemeente_id = "GM0363"`, `wijk_id = "WK00"`, `buurt_id = "BU01"`

---

## API Integration

### CBS StatLine

**Table**: 84286NED (Income Statistics by Neighborhood)

**R**:
```r
library(cbsodataR)
cbs_data <- cbs_get_data("84286NED")
```

**Python**:
```python
import cbsodata
cbs_data = cbsodata.get_data("84286NED")
```

**Key Variables Retrieved**:
| CBS Variable | Description | Level |
|--------------|-------------|-------|
| `AantalInwoners_5` | Population | Buurt |
| `k_40PercentHuishoudensMetLaagsteInkomen_71` | % low-income HH | Buurt |
| `k_20PercentHuishoudensMetHoogsteInkomen_72` | % high-income HH | Buurt |

---

## Deployment Architecture

### Streamlit Cloud

```
GitHub Repository
       │
       ▼
Streamlit Cloud (auto-deploy on push)
       │
       ├── Reads: python/dashboard/app.py
       ├── Data: Precomputed JSON (fallback)
       └── URL: *.streamlit.app
```

**Configuration**:
- Main file: `python/dashboard/app.py`
- Requirements: `python/requirements.txt`
- Secrets: Optional cloud data URL

### ShinyApps.io

```
Local R Environment
       │
       ▼
rsconnect::deployApp()
       │
       ▼
ShinyApps.io Server
       │
       ├── Reads: R/shiny/app.R
       ├── Data: Precomputed in global.R
       └── URL: *.shinyapps.io
```

**Deployment**:
```r
rsconnect::deployApp(
  appDir = "R/shiny",
  appName = "income-inequality-attitudes"
)
```

---

## Performance Considerations

### Pipeline Runtime

| Stage | Approximate Time |
|-------|-----------------|
| CBS API download | 1-2 minutes (first run) |
| Data transformation | 30 seconds |
| Model fitting | 2-3 minutes |
| Dashboard startup | 5-10 seconds |

### Memory Usage

| Component | Memory |
|-----------|--------|
| Raw survey data | ~50 MB |
| CBS data | ~200 MB |
| Merged dataset | ~100 MB |
| Model objects | ~50 MB |

### Optimization Notes

- **CBS data caching**: Downloaded data is cached locally
- **Precomputed results**: Dashboards can run without re-fitting models
- **targets (R)**: Incremental builds only re-run changed steps

---

## Testing & Validation

### Cross-Software Validation

Results are validated across R and Python implementations:

| Metric | Python | R | Tolerance |
|--------|--------|---|-----------|
| ICC | 0.0347 | 0.0347 | ±0.001 |
| M1 coefficient | 3.459 | 3.461 | ±0.01 |
| M3 coefficient | 0.276 | 0.279 | ±0.01 |

### Robustness Checks

1. **Alternative DVs**: 1-item, 2-item, 3-item specifications
2. **Subgroup analysis**: Dutch-born respondents only
3. **Alternative predictor**: Income ratio vs. poverty concentration
4. **Nested effects**: R-only 4-level model

---

## Security Considerations

### Sensitive Data

**Protected files** (in `.gitignore`):
- `*.dta` - Survey microdata
- `data/raw/` - Raw data directory
- `*.csv` - Most processed data (except allowed files)

**Allowed files**:
- `data/processed/analysis_ready.csv` - For dashboard functionality
- `python/dashboard/data/*.csv` - Dashboard-specific data

### No Credentials in Code

- CBS API is public (no authentication)
- No database credentials stored
- No personal information in repository

---

*Last updated: February 2025*
