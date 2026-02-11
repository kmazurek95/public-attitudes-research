# Attitudes Toward Income Inequality

A multilevel analysis examining how neighborhood-level socioeconomic composition influences individual redistribution preferences in the Netherlands.

## Project Background

This research project originated during an internship at the **University of Amsterdam** under the supervision of **Dr. Wouter Schakel** (Department of Political Science). The project investigates contextual effects on political attitudes using multilevel modeling techniques.

> **Disclaimer**: All errors and omissions in this work are solely my own responsibility.

### Academic Context

This work contributes to the growing literature on:
- **Perceptions and misperceptions** of inequality (Hauser & Norton, 2017; Cruces et al., 2013)
- **Beliefs and meritocracy** legitimizing inequality (Mijs, 2021)
- **Experiential/inferential spaces** shaping attitudes (Mijs, 2018)

### Documentation

**Start here:** [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Executive summary with key findings

| Category | Documents |
|----------|-----------|
| **Portfolio** | [Case Study](docs/portfolio/CASE_STUDY.md) &#183; [Business Value](docs/portfolio/BUSINESS_VALUE.md) &#183; [Skills Matrix](docs/portfolio/SKILLS_MATRIX.md) |
| **Academic** | [Full Paper](docs/academic/DRAFT_PAPER.md) &#183; [Research Statement](docs/academic/RESEARCH_STATEMENT.md) &#183; [Literature Review](docs/academic/LITERATURE_REVIEW.md) &#183; [Limitations](docs/academic/LIMITATIONS.md) |
| **Technical** | [Technical Overview](docs/technical/TECHNICAL_OVERVIEW.md) &#183; [Reproducibility](docs/technical/REPRODUCIBILITY.md) &#183; [Pipeline Alignment](docs/technical/PIPELINE_ALIGNMENT.md) |

See [docs/index.md](docs/index.md) for complete navigation.

## Research Question

> **Do neighborhood characteristics influence attitudes toward income redistribution, and at what geographic level do contextual effects operate?**

Drawing on Mijs' (2018) "inferential spaces" framework, this study tests whether exposure to socioeconomic diversity at the neighborhood level shapes beliefs about inequality and redistribution.

### Hypotheses

- **H1**: Higher neighborhood poverty concentration → more support for redistribution
- **H2**: Neighborhood-level effects explain more variance than municipality/regional effects
- **H3**: Individual income negatively moderates the neighborhood effect (cross-level interaction)
  - Higher-income individuals are less affected by neighborhood context

## Key Findings

| Metric | Value |
|--------|-------|
| ICC (Buurt level) | ~3.4% |
| N (analysis sample) | ~4,600 |
| Neighborhoods | ~1,500 |

**Main Result**: Only ~3-4% of variance in redistribution preferences is between neighborhoods. The neighborhood income composition effect becomes **non-significant** after controlling for individual characteristics, suggesting limited support for the inferential spaces hypothesis in the Dutch context.

## Data Sources

- **SCoRE Survey (2017)**: Dutch nationally representative survey (N=8,013)
- **CBS StatLine**: Neighborhood-level administrative statistics via API

## Dual Implementation: Python and R

This project includes both **Python** and **R** implementations to ensure reproducibility and leverage the strengths of each platform.

| Feature | Python | R |
|---------|--------|---|
| Pipeline orchestration | `run_pipeline.py` | `targets` |
| Multilevel models | statsmodels | lme4 |
| Dashboard | Streamlit | Shiny |
| Nested random effects | No* | Yes |

*Python's statsmodels cannot fit crossed/nested random effects. The R implementation provides these as robustness checks.

### Why Two Implementations?

1. **Reproducibility**: Confirms results across statistical software
2. **Best practices**: R (lme4) is the gold standard for multilevel modeling
3. **Accessibility**: Python version for broader audience
4. **Extensions**: R provides true nested random effects that Python lacks

See [docs/PIPELINE_ALIGNMENT.md](docs/PIPELINE_ALIGNMENT.md) for details on how the pipelines are aligned.

## Project Structure

```
public-attitudes-research/
│
├── R/                          # R implementation (targets pipeline)
│   ├── 00_packages.R           # Package dependencies
│   ├── 01_extract.R            # Data loading (survey + CBS API)
│   ├── 02_transform.R          # Variable recoding, geo IDs, inequality indices
│   ├── 03_merge.R              # Multilevel merge
│   ├── 04_analysis.R           # Multilevel models + nested RE
│   └── shiny/                  # R Shiny dashboard
│
├── python/                     # Python implementation
│   ├── src/                    # Source modules
│   │   ├── extract.py          # CBS API + survey loading
│   │   ├── transform.py        # Geographic ID creation
│   │   ├── merge.py            # Data merging
│   │   ├── analyze.py          # Multilevel models (statsmodels)
│   │   ├── report.py           # Output generation
│   │   └── geography.py        # Geographic utilities
│   ├── dashboard/              # Streamlit dashboard
│   ├── run_pipeline.py         # Main entry point
│   ├── config.py               # Configuration settings
│   └── requirements.txt        # Python dependencies
│
├── _targets.R                  # R targets pipeline definition
│
├── PROJECT_SUMMARY.md          # Executive summary (start here!)
│
├── docs/                       # Documentation (organized by audience)
│   ├── index.md                # Navigation guide
│   ├── portfolio/              # For employers/recruiters
│   │   ├── CASE_STUDY.md
│   │   ├── BUSINESS_VALUE.md
│   │   └── SKILLS_MATRIX.md
│   ├── academic/               # For researchers/PhD programs
│   │   ├── DRAFT_PAPER.md
│   │   ├── RESEARCH_STATEMENT.md
│   │   ├── LITERATURE_REVIEW.md
│   │   └── LIMITATIONS.md
│   ├── technical/              # For developers/collaborators
│   │   ├── TECHNICAL_OVERVIEW.md
│   │   ├── REPRODUCIBILITY.md
│   │   ├── PIPELINE_ALIGNMENT.md
│   │   └── ACKNOWLEDGMENTS.md
│   └── reference/              # Supporting materials
│
├── data/                       # Data files (not tracked in git)
│   ├── raw/                    # Original data (score.dta, CBS indicators)
│   └── processed/              # Analysis-ready datasets
│
├── outputs/                    # Generated outputs (not tracked)
│   ├── figures/
│   └── tables/
│
├── legacy/                     # Old code from internship (archived)
│
└── README.md
```

## Quick Start

### Python

```bash
cd python
pip install -r requirements.txt
python run_pipeline.py              # Use local data files
python run_pipeline.py --use-api    # Download fresh CBS data
```

**Start the dashboard:**
```bash
streamlit run dashboard/app.py
```

### R

```r
# Install dependencies
install.packages(c("targets", "tidyverse", "lme4", "cbsodataR", "shiny"))

# Run the pipeline
library(targets)
tar_make()

# View pipeline status
tar_visnetwork()
```

**Start the R dashboard:**
```r
shiny::runApp("R/shiny")
```

## Interactive Dashboards

Both dashboards present the same core findings with cross-links:

### Live Demos

- **Python (Streamlit)**: [attitudes-toward-income-inequality.streamlit.app](https://attitudes-toward-income-inequality-7unora4rhffxtelwombehc.streamlit.app)
- **R (Shiny)**: [kmazurek-analytics.shinyapps.io/income-inequality-attitudes](https://kmazurek-analytics.shinyapps.io/income-inequality-attitudes/)

> **Note**: The processed analysis data (`data/processed/analysis_ready.csv`) is temporarily included in the repository for dashboard functionality. This will be migrated to cloud storage in a future update.

### Local Development

- **Python (Streamlit)**: `http://localhost:8501`
- **R (Shiny)**: `http://localhost:3838`

The R dashboard includes an additional page for **R-specific robustness analyses** showing true nested random effects results.

## Methods

### Statistical Approach

- **Two-level models**: Random intercept models with individuals nested in neighborhoods (buurt)
- **Four-level models**: Extended specification with wijk and gemeente predictors
- **R-specific**: True nested random effects `(1|gemeente) + (1|wijk) + (1|buurt)`

### Key Variables

#### Dependent Variable Construction

The primary dependent variable (**DV_single**) measures support for government redistribution on a 0-100 scale, constructed from the SCoRE survey item:

> *"The government should reduce differences in income levels."*
> Original scale: 1 (strongly disagree) to 7 (strongly agree)

**Transformation formula:**
```
DV_single = (red_inc_diff - 1) / 6 * 100
```

This rescales the 1-7 response to a 0-100 scale where:
- 0 = Strongly oppose redistribution
- 100 = Strongly support redistribution

**Alternative DV specifications (sensitivity analyses):**

| Variable | Construction | Source Items |
|----------|--------------|--------------|
| DV_single | (red_inc_diff - 1) / 6 × 100 | Single item |
| DV_2item | Mean of red_inc_diff + gov_int, rescaled | 2 items |
| DV_3item | Mean of red_inc_diff + gov_int + union_pref, rescaled | 3 items |

#### Key Predictors

- **b_perc_low40_hh**: % households in bottom 40% of income distribution (neighborhood-level, standardized)
- **b_income_ratio**: Ratio of high-income to low-income households (alternative inequality measure)

#### Income Proxy (for H3 test)

Since SCoRE lacks direct income questions, we use **wealth_index** as a proxy:
- Constructed from homeownership and financial asset questions
- Scale: 0-4 (higher = more wealth)
- Used to test cross-level interaction (H3 hypothesis)

### Controls

- **Individual**: Age, sex, education, employment status, migration background
- **Neighborhood**: Population density, age composition, ethnic diversity, income indicators

## Acknowledgments

- **Dr. Wouter Schakel** (University of Amsterdam) - Research supervision
- **SCoRE Survey** - Netherlands data access via GESIS
- **CBS Statistics Netherlands** - Administrative data via StatLine API

See [docs/ACKNOWLEDGMENTS.md](docs/ACKNOWLEDGMENTS.md) for full acknowledgments.

## Dependencies

### Python
- pandas, numpy, scipy
- statsmodels (multilevel models)
- streamlit (dashboard)
- plotly (visualizations)
- geopandas (maps)
- cbsodata (CBS API)

### R
- targets (pipeline)
- tidyverse
- lme4 (multilevel models)
- shiny, shinydashboard
- plotly
- cbsodataR (CBS API)

## Author

**Kaleb Mazurek**
University of Amsterdam Internship (2023)
Supervised by Dr. Wouter Schakel

## Deployment

### Streamlit Cloud (Python Dashboard)

1. Fork/clone this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select repository, branch: `main`, main file: `python/dashboard/app.py`
5. Click "Deploy"

The dashboard will run in demo mode with precomputed results. To enable full functionality with raw data, configure Streamlit secrets with a cloud data URL.

### ShinyApps.io (R Dashboard)

```r
# Install rsconnect
install.packages("rsconnect")

# Configure account (one-time)
rsconnect::setAccountInfo(
  name = "your-account",
  token = "your-token",
  secret = "your-secret"
)

# Deploy
rsconnect::deployApp(
  appDir = "R/shiny",
  appName = "attitudes-inequality-r"
)
```

## License

MIT
