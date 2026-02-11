# Business Value Statement

*How My Academic Research Translates to Industry Impact*

---

## Executive Summary

During my internship at the University of Amsterdam, I built a complete data science pipeline from scratch — linking survey data to government statistics, running multilevel models, and delivering interactive dashboards on two platforms. The research question was academic, but everything I built mirrors what data teams do in industry every day.

**The short version:** I take messy, ambiguous problems, structure them into something testable, build the infrastructure to answer them, and communicate what I find to people who aren't statisticians.

---

## What I Built (and What It Maps To)

| What I Delivered | Industry Equivalent |
|------------------|---------------------|
| Linked 8,000+ survey responses to CBS neighborhood statistics | Customer data integration (CRM + behavioral + third-party) |
| Multilevel regression models across 1,572 neighborhoods | Segmentation analysis with nested structures (users in cohorts, stores in regions) |
| Two interactive dashboards (Streamlit + Shiny) | Self-service BI tools for non-technical stakeholders |
| Reproducible pipeline in both Python and R | Production-grade ETL with validation and monitoring |
| 10+ documentation pages for different audiences | Handoff materials, onboarding docs, stakeholder briefs |

---

## How My Skills Transfer

### 1. Data Engineering

**What I did:** I pulled survey microdata (Stata format) and CBS administrative statistics (via API), cleaned geographic identifiers across three administrative levels (neighborhood, district, municipality), handled missing data and type mismatches, and merged everything into an analysis-ready dataset.

**Where this applies:**
- Building Customer 360 views from CRM, transaction, and behavioral data
- Third-party data enrichment (demographics, firmographics, geolocation)
- Data quality pipelines that catch problems before they reach production

### 2. Advanced Analytics

**What I did:** I built multilevel regression models that correctly account for the fact that individuals are grouped within neighborhoods — ignoring this structure would produce misleading standard errors and wrong conclusions. I tested 10+ model specifications to make sure findings held up.

**Where this applies:**
- A/B testing where users are clustered (by region, cohort, or device)
- Marketing mix modeling with regional or seasonal effects
- Churn prediction that separates individual risk from segment-level patterns
- Customer lifetime value with proper cohort adjustments

### 3. Statistical Rigor

**What I did:** My main hypothesis didn't survive robustness checks — the neighborhood effect disappeared once I controlled for individual-level confounders. I documented this honestly rather than cherry-picking specifications that looked good. I also ran alternative dependent variable transformations and subgroup analyses.

**Where this applies:**
- Separating real signals from noise in experimentation programs
- Communicating uncertainty and confidence intervals to decision-makers
- Avoiding the false positives that come from running dozens of tests
- Building credibility with stakeholders through transparent methodology

### 4. Full-Stack Implementation

**What I did:** I implemented the entire pipeline twice — once in Python (pandas, statsmodels, Streamlit) and once in R (tidyverse, lme4, Shiny). Both produce matching results within rounding error. I deployed both dashboards to cloud platforms with demo-mode fallbacks for when raw data isn't available.

**Where this applies:**
- Working across tech stacks depending on what the team uses
- Moving from prototype to deployment without handing off to a separate engineering team
- Building self-service tools that reduce the "Can you pull this data?" bottleneck

### 5. Communication

**What I did:** I wrote for three audiences simultaneously: academic reviewers (full paper with literature review), technical collaborators (pipeline docs, reproducibility guide), and general audiences (interactive dashboards with progressive disclosure — key findings up front, methodology available for those who want it).

**Where this applies:**
- Executive summaries that actually drive decisions
- Technical documentation that lets someone else pick up your work
- Stakeholder presentations calibrated to the audience's technical level
- Data storytelling that moves people from "interesting" to "let's act on this"

---

## Project at a Glance

| Metric | Value | What It Demonstrates |
|--------|-------|----------------------|
| Data sources integrated | 2 (survey + government API) | Multi-source data merging |
| Observations analyzed | 8,013 (4,748 in final models) | Handling real-world attrition and missing data |
| Geographic units linked | 1,572 neighborhoods | Hierarchical data expertise |
| Model specifications | 10+ | Thoroughness in sensitivity analysis |
| Dashboards deployed | 2 (Streamlit + Shiny) | Multi-platform delivery |
| Documentation pages | 10+ | Professional standards for reproducibility |
| Languages used | 2 (Python + R) | Technical versatility |

---

## Industry Contexts Where This Work Is Relevant

### Tech / Product Analytics
- **User segmentation:** How does user context (geography, plan type, cohort) shape behavior?
- **Experimentation:** Multilevel models for A/B tests with clustered users
- **Churn analysis:** Disentangling individual risk factors from contextual ones

### Marketing Analytics
- **Campaign measurement:** Regional variation in response rates
- **Customer journey modeling:** Hierarchical data (touchpoints within sessions within customers)
- **Survey research:** Designing and analyzing customer satisfaction studies

### Consulting / Strategy
- **Due diligence:** Rapid assessment of unfamiliar datasets
- **Market analysis:** Geographic variation in opportunity or risk
- **Benchmarking:** Putting client metrics in proper context

### Public Sector / Policy
- **Program evaluation:** Estimating effects from observational data
- **Needs assessment:** Geographic targeting of resources
- **Impact measurement:** Separating who participates from what the program does

---

## Interview Talking Points

### "Tell me about a complex analysis you've done."

> I studied whether neighborhood poverty levels influence how people think about income redistribution, using 8,000 survey responses linked to official Dutch statistics. The core challenge was that standard regression ignores the fact that people are grouped within neighborhoods — that violates the independence assumption and produces wrong standard errors. I used multilevel models to properly partition variance and found that only 3.4% of attitude variation occurs between neighborhoods. That's a near-null finding, but it was important: it challenged a prominent theory that had mostly been tested in the US and UK.

### "How do you handle ambiguous problems?"

> This project started with a broad question: "Does where you live shape what you believe about inequality?" I broke that into three testable hypotheses, identified the right data sources, chose a method that matched the nested structure of the data, and built in sensitivity checks from the start. When my key predictor lost significance after adding controls, I didn't go looking for a different specification that "worked" — I investigated why, documented what it meant, and adjusted my conclusions.

### "How do you communicate technical findings?"

> I built two dashboards — one in Streamlit, one in Shiny — where someone with no statistics background can explore the results. The design uses progressive disclosure: key findings and plain-language interpretations first, with the option to drill into model coefficients and diagnostics. I also wrote a full academic paper, a case study for non-technical readers, and pipeline documentation for anyone who wants to reproduce or extend the work.

### "What's your approach to data quality?"

> I documented every transformation, validated all geographic linkages between datasets, ran diagnostics on missing data patterns, and implemented the entire analysis in two languages independently. When the Python and R results matched within rounding error, I knew the pipeline was sound. I also built demo modes for the dashboards that use precomputed results, so the tools work even when the underlying data isn't available.

---

## Technical Stack

| Category | Technologies |
|----------|--------------|
| **Languages** | Python, R |
| **Data Processing** | pandas, tidyverse, pyreadstat, cbsodata |
| **Statistics** | statsmodels, lme4, scipy |
| **Visualization** | Plotly, ggplot2, Streamlit, Shiny |
| **Pipeline** | targets (R), modular Python scripts, config management |
| **Deployment** | Streamlit Cloud, ShinyApps.io |
| **Version Control** | Git, GitHub |

---

## Live Demos

- **Python Dashboard:** [Streamlit app](https://attitudes-toward-income-inequality-7unora4rhffxtelwombehc.streamlit.app)
- **R Dashboard:** [Shiny app](https://kmazurek-analytics.shinyapps.io/income-inequality-attitudes/)
- **Repository:** [github.com/kmazurek95/public-attitudes-research](https://github.com/kmazurek95/public-attitudes-research)
