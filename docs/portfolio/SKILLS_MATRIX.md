# Skills Matrix

A mapping of competencies demonstrated in this project to specific files and evidence.

---

## Statistical Methods

| Skill | Level | Evidence | Files |
|-------|-------|----------|-------|
| **Multilevel Modeling** | Advanced | Random intercept models with 2-4 nesting levels; variance decomposition; ICC calculation | [R/04_analysis.R](../R/04_analysis.R), [python/src/analyze.py](../python/src/analyze.py) |
| **Variance Decomposition** | Advanced | Partitioning variance across geographic levels (buurt, wijk, gemeente) | Dashboard Model Results page |
| **Sensitivity Analysis** | Intermediate | Alternative DV specifications, subgroup analyses, robustness checks | `run_sensitivity()` functions in both pipelines |
| **Cross-Level Interactions** | Intermediate | Testing moderation of neighborhood effects by individual characteristics | H3 test in analysis scripts |
| **Regression Diagnostics** | Intermediate | Residual checks, influential observations, model fit statistics | Embedded in analysis code |

---

## Data Engineering

| Skill | Level | Evidence | Files |
|-------|-------|----------|-------|
| **API Integration** | Intermediate | CBS StatLine data extraction via cbsodataR/cbsodata packages | [R/01_extract.R](../R/01_extract.R), [python/src/extract.py](../python/src/extract.py) |
| **Data Merging** | Advanced | Linking survey data to administrative records via geographic identifiers | [python/src/merge.py](../python/src/merge.py), [R/03_merge.R](../R/03_merge.R) |
| **Missing Data Handling** | Intermediate | Complete case analysis, missingness diagnostics, listwise deletion | Transform modules |
| **Variable Construction** | Advanced | Composite indices, scale transformations, geographic ID creation | [R/02_transform.R](../R/02_transform.R), [python/src/transform.py](../python/src/transform.py) |
| **ETL Pipeline Design** | Intermediate | Modular extraction → transformation → loading workflow | Pipeline architecture |

---

## Software Development

| Skill | Level | Evidence | Files |
|-------|-------|----------|-------|
| **Dashboard Development** | Intermediate | Multi-page Streamlit app with interactive visualizations | [python/dashboard/](../python/dashboard/) |
| **Shiny Development** | Intermediate | Modular Shiny app with shinydashboard | [R/shiny/](../R/shiny/) |
| **Pipeline Orchestration** | Intermediate | targets (R) for dependency management, modular Python | [_targets.R](../_targets.R), [run_pipeline.py](../python/run_pipeline.py) |
| **Version Control** | Intermediate | Git workflow, .gitignore for sensitive data, branching | Repository history |
| **Configuration Management** | Basic | Centralized config files, environment detection | [python/config.py](../python/config.py) |
| **Code Organization** | Intermediate | Modular structure, separation of concerns, reusable functions | Project structure |

---

## Programming Languages

| Language | Proficiency | Applications in Project |
|----------|-------------|------------------------|
| **Python** | Proficient | Data processing, statistical modeling, Streamlit dashboards |
| **R** | Proficient | Multilevel modeling, targets pipeline, Shiny dashboards |
| **SQL** | Basic | Data querying concepts (applied via pandas/dplyr) |
| **Markdown** | Proficient | Documentation, README, academic writing |

---

## Data Visualization

| Skill | Level | Evidence | Files |
|-------|-------|----------|-------|
| **Interactive Charts** | Intermediate | Plotly charts in both dashboards | Dashboard pages |
| **Static Visualization** | Intermediate | ggplot2 for publication figures | R visualization code |
| **Dashboard Design** | Intermediate | Multi-page layout, user-friendly navigation | Dashboard structure |
| **Data Storytelling** | Intermediate | Key Findings page, progressive disclosure | [4_Key_Findings.py](../python/dashboard/pages/4_Key_Findings.py) |

---

## Research Skills

| Skill | Level | Evidence | Files |
|-------|-------|----------|-------|
| **Literature Review** | Advanced | Comprehensive theoretical framework contextualization | [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md) |
| **Hypothesis Development** | Advanced | Theory-driven H1, H2, H3 with clear operationalization | [DRAFT_PAPER.md](DRAFT_PAPER.md) |
| **Academic Writing** | Advanced | Full paper draft with standard sections | [DRAFT_PAPER.md](DRAFT_PAPER.md) |
| **Critical Analysis** | Advanced | Thorough limitations discussion, alternative interpretations | [LIMITATIONS.md](LIMITATIONS.md) |
| **Research Design** | Intermediate | Cross-sectional multilevel design, variable operationalization | Methods section |

---

## Domain Knowledge

| Area | Depth | Application |
|------|-------|-------------|
| **Political Attitudes** | Intermediate | Redistribution preferences, inequality beliefs |
| **Survey Methodology** | Intermediate | Sampling, weighting, measurement |
| **Geographic Analysis** | Basic | Nested geographic units, MAUP awareness |
| **Dutch Administrative Data** | Basic | CBS StatLine, buurt/wijk/gemeente hierarchy |
| **Welfare State Research** | Basic | Comparative context, institutional factors |

---

## Tools & Technologies

| Category | Tools |
|----------|-------|
| **Statistical Software** | R (lme4, tidyverse), Python (statsmodels, pandas) |
| **Dashboards** | Streamlit, Shiny, shinydashboard |
| **Visualization** | ggplot2, plotly, matplotlib |
| **Data Storage** | CSV, Stata (.dta), JSON |
| **Version Control** | Git, GitHub |
| **Documentation** | Markdown, R Markdown |
| **IDEs** | RStudio, VS Code |

---

## Soft Skills Demonstrated

| Skill | Evidence |
|-------|----------|
| **Project Management** | End-to-end project delivery with documentation |
| **Communication** | Technical writing for multiple audiences (academic, professional) |
| **Problem Solving** | Addressing data limitations, software constraints |
| **Attention to Detail** | Sensitivity analyses, robustness checks |
| **Independent Learning** | Multilevel methods, dashboard frameworks |

---

## Certifications & Training

*Note: This section is for you to add your relevant certifications*

| Certification | Provider | Date |
|--------------|----------|------|
| *Add your certifications here* | | |

---

## How This Maps to Job Requirements

### Data Scientist Roles

| Common Requirement | This Project |
|-------------------|--------------|
| Statistical modeling | Multilevel regression, variance decomposition |
| Python/R proficiency | Dual implementation |
| Data visualization | Interactive dashboards |
| Communication | Academic paper, documentation |

### Research Analyst Roles

| Common Requirement | This Project |
|-------------------|--------------|
| Survey analysis | SCoRE survey data processing |
| Report writing | Full paper draft, key findings |
| Statistical software | R and Python |
| Data management | ETL pipeline, data merging |

### PhD Programs

| Admission Criteria | This Project |
|-------------------|--------------|
| Research experience | Supervised research internship |
| Methodological skills | Advanced multilevel modeling |
| Writing sample | Academic paper draft |
| Independent work | Full project ownership |

---

*Author: Kaleb Mazurek*
*Last updated: February 2025*
