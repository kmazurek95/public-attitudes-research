# =============================================================================
# ui.R - Dashboard UI Definition
# =============================================================================

ui <- dashboardPage(
  skin = "blue",

  # ===========================================================================
  # Header
  # ===========================================================================
  dashboardHeader(
    title = "Income Inequality Attitudes",
    titleWidth = 280,
    tags$li(
      class = "dropdown",
      tags$a(
        href = PYTHON_DASHBOARD_URL,
        target = "_blank",
        icon("python"),
        "Python Dashboard",
        style = "color: white; padding: 15px;"
      )
    )
  ),

  # ===========================================================================
  # Sidebar
  # ===========================================================================
  dashboardSidebar(
    width = 280,
    sidebarMenu(
      id = "tabs",
      menuItem("Home", tabName = "home", icon = icon("home")),
      menuItem("Data Explorer", tabName = "data_explorer", icon = icon("search")),
      menuItem("Geographic View", tabName = "geographic", icon = icon("map")),
      menuItem("Model Results", tabName = "model_results", icon = icon("chart-line")),
      menuItem("Key Findings", tabName = "key_findings", icon = icon("bullseye")),
      hr(),
      menuItem(
        "R-Specific Analyses",
        tabName = "r_specific",
        icon = icon("r-project"),
        badgeLabel = "Robustness",
        badgeColor = "green"
      ),
      hr(),
      menuItem(
        "About Project",
        tabName = "about_project",
        icon = icon("info-circle")
      )
    ),

    # About section
    div(
      style = "padding: 15px; font-size: 12px;",
      hr(),
      h5("About This Research"),
      p("Multilevel analysis of redistribution preferences in the Netherlands."),
      p("Based on Mijs (2018) 'Inferential Spaces' framework."),
      hr(),
      h5("Data Sources"),
      p("SCoRE Survey (2017)"),
      p("CBS StatLine (2018)"),
      hr(),
      p(
        style = "font-style: italic;",
        strong("Author: Kaleb Mazurek"),
        br(),
        "University of Amsterdam",
        br(),
        "Supervised by Dr. Wouter Schakel"
      )
    )
  ),

  # ===========================================================================
  # Body
  # ===========================================================================
  dashboardBody(
    # Custom CSS
    tags$head(
      tags$style(HTML("
        .content-wrapper { background-color: #f5f5f5; }
        .box { border-top: 3px solid #1f77b4; }
        .box.box-success { border-top-color: #2ca02c; }
        .box.box-warning { border-top-color: #ff7f0e; }
        .box.box-danger { border-top-color: #d62728; }
        .info-box { min-height: 90px; }
        .main-header .logo { font-weight: bold; }
        .skin-blue .main-header .navbar { background-color: #1f77b4; }
        .skin-blue .main-sidebar { background-color: #2c3e50; }
        h2 { color: #2c3e50; margin-bottom: 20px; }
        .hypothesis-box { padding: 15px; border-radius: 10px; margin-bottom: 15px; }
        .hypothesis-supported { background-color: #e8f5e9; border-left: 5px solid #2ca02c; }
        .hypothesis-not-supported { background-color: #ffebee; border-left: 5px solid #d62728; }
        .hypothesis-inconclusive { background-color: #fff3e0; border-left: 5px solid #ff7f0e; }
      "))
    ),

    tabItems(
      # =========================================================================
      # Home Tab
      # =========================================================================
      tabItem(
        tabName = "home",

        h2("Attitudes Toward Income Inequality"),
        p("A multilevel analysis of redistribution preferences in the Netherlands"),

        fluidRow(
          valueBoxOutput("box_respondents", width = 2),
          valueBoxOutput("box_sample", width = 2),
          valueBoxOutput("box_buurten", width = 2),
          valueBoxOutput("box_wijken", width = 2),
          valueBoxOutput("box_gemeenten", width = 2),
          valueBoxOutput("box_icc", width = 2)
        ),

        fluidRow(
          box(
            title = "Research Question",
            status = "primary",
            solidHeader = TRUE,
            width = 6,
            p(
              style = "font-size: 16px;",
              strong("Do neighborhood characteristics influence attitudes toward income redistribution,
              and at what geographic level do contextual effects operate?")
            ),
            hr(),
            p("Drawing on Mijs' (2018) 'inferential spaces' framework, this study tests whether
            exposure to socioeconomic diversity at the neighborhood level shapes beliefs about
            inequality and redistribution.")
          ),
          box(
            title = "Key Finding",
            status = "warning",
            solidHeader = TRUE,
            width = 6,
            p(
              style = "font-size: 16px;",
              "Only ", strong("3.4%"), " of variance in redistribution preferences is between neighborhoods."
            ),
            p("The neighborhood income composition effect becomes ",
              strong("non-significant"),
              " after controlling for individual characteristics."),
            hr(),
            p("This suggests limited support for the inferential spaces hypothesis in the Dutch context.")
          )
        ),

        fluidRow(
          box(
            title = "About This Dashboard",
            width = 12,
            p("This R Shiny dashboard presents results from a multilevel analysis of attitudes
            toward income redistribution in the Netherlands. It is part of a dual implementation
            project with both R and Python versions."),
            tags$ul(
              tags$li(strong("R Dashboard (this): "), "Includes true nested random effects using lme4"),
              tags$li(strong("Python Dashboard: "), "Streamlit-based with interactive visualizations")
            ),
            actionButton(
              "go_to_python",
              "Open Python Dashboard",
              icon = icon("external-link-alt"),
              onclick = paste0("window.open('", PYTHON_DASHBOARD_URL, "', '_blank')")
            )
          )
        )
      ),

      # =========================================================================
      # Data Explorer Tab
      # =========================================================================
      tabItem(
        tabName = "data_explorer",

        h2("Data Explorer"),

        fluidRow(
          box(
            title = "Dependent Variable Distribution",
            status = "primary",
            width = 6,
            plotlyOutput("dv_histogram", height = "350px")
          ),
          box(
            title = "Key Predictor Distribution",
            status = "primary",
            width = 6,
            plotlyOutput("key_pred_histogram", height = "350px")
          )
        ),

        fluidRow(
          box(
            title = "Sample Summary",
            width = 4,
            tableOutput("sample_summary")
          ),
          box(
            title = "Variable Descriptions",
            width = 8,
            DT::dataTableOutput("variable_table")
          )
        )
      ),

      # =========================================================================
      # Geographic View Tab
      # =========================================================================
      tabItem(
        tabName = "geographic",

        h2("Geographic Structure"),

        fluidRow(
          box(
            title = "Dutch Administrative Hierarchy",
            status = "primary",
            width = 12,
            p("The Netherlands has a nested geographic structure:"),
            tags$div(
              style = "text-align: center; font-size: 18px; padding: 20px;",
              strong("Individual"), " → ",
              span(style = paste0("color: ", COLORS$primary), strong("Buurt")), " (Neighborhood) → ",
              span(style = paste0("color: ", COLORS$secondary), strong("Wijk")), " (District) → ",
              span(style = paste0("color: ", COLORS$tertiary), strong("Gemeente")), " (Municipality)"
            )
          )
        ),

        fluidRow(
          box(
            title = "Cluster Size Distribution (Buurt)",
            status = "primary",
            width = 6,
            plotlyOutput("cluster_sizes", height = "350px")
          ),
          box(
            title = "Sample by Municipality",
            status = "primary",
            width = 6,
            plotlyOutput("gemeente_treemap", height = "350px")
          )
        )
      ),

      # =========================================================================
      # Model Results Tab
      # =========================================================================
      tabItem(
        tabName = "model_results",

        h2("Model Results"),

        fluidRow(
          box(
            title = "1. Variance Decomposition (ICC)",
            status = "primary",
            width = 6,
            plotlyOutput("icc_donut", height = "400px"),
            p(
              style = "text-align: center;",
              strong("ICC = 3.4%"),
              " means only 3.4% of variance is between neighborhoods"
            )
          ),
          box(
            title = "2. Coefficient Stability",
            status = "primary",
            width = 6,
            plotlyOutput("coef_progression", height = "400px"),
            p(
              style = "text-align: center;",
              "The key predictor effect ", strong("disappears"), " with full controls"
            )
          )
        ),

        fluidRow(
          box(
            title = "3. Forest Plot: Key Predictor Effect",
            status = "primary",
            width = 12,
            plotlyOutput("forest_plot", height = "300px")
          )
        ),

        fluidRow(
          box(
            title = "Model Summary",
            status = "primary",
            width = 12,
            p("Two-level random intercept models: DV_single ~ predictors + (1|buurt_id)"),
            tableOutput("model_table")
          )
        )
      ),

      # =========================================================================
      # Key Findings Tab
      # =========================================================================
      tabItem(
        tabName = "key_findings",

        h2("Key Findings"),

        fluidRow(
          column(
            width = 4,
            div(
              class = "hypothesis-box hypothesis-not-supported",
              h4("H1: Not Supported"),
              p(strong("Hypothesis: "), "Neighborhoods with higher income inequality → more support for redistribution"),
              hr(),
              p(strong("Finding: "), "Effect is non-significant after controls"),
              p("M1 coefficient: 3.36***"),
              p("M3 coefficient: 0.33 (n.s.)")
            )
          ),
          column(
            width = 4,
            div(
              class = "hypothesis-box hypothesis-inconclusive",
              h4("H2: Inconclusive"),
              p(strong("Hypothesis: "), "Neighborhood effects > municipality effects"),
              hr(),
              p(strong("Finding: "), "Effects weak at all levels"),
              p("ICC at buurt: ~2%"),
              p("ICC at wijk: ~1%"),
              p("ICC at gemeente: ~1%")
            )
          ),
          column(
            width = 4,
            div(
              class = "hypothesis-box hypothesis-not-supported",
              h4("H3: Not Supported"),
              p(strong("Hypothesis: "), "Effects persist after controlling for individual characteristics"),
              hr(),
              p(strong("Finding: "), "Effect does NOT persist"),
              p("90% reduction in coefficient"),
              p("Individual factors fully account for association")
            )
          )
        ),

        fluidRow(
          box(
            title = "Summary",
            status = "info",
            width = 12,
            p(
              style = "font-size: 16px;",
              "This study finds ", strong("limited evidence"), " for neighborhood effects on
              redistribution preferences in the Netherlands. Only 3.4% of variance is between
              neighborhoods, and the effect of neighborhood income composition becomes
              non-significant after controlling for individual characteristics."
            ),
            p(
              style = "font-size: 16px;",
              strong("Individual-level factors"), "—particularly age and education—are
              the primary drivers of redistribution preferences."
            )
          )
        )
      ),

      # =========================================================================
      # R-Specific Analyses Tab
      # =========================================================================
      tabItem(
        tabName = "r_specific",

        h2("R-Specific Robustness Analyses"),

        fluidRow(
          box(
            title = "True Nested Random Effects",
            status = "success",
            solidHeader = TRUE,
            width = 12,
            p("These analyses use lme4's capability for ", strong("true nested random effects:") ),
            code("DV_single ~ predictors + (1|gemeente_id) + (1|wijk_id) + (1|buurt_id)"),
            p("This properly partitions variance across all geographic levels."),
            p(
              strong("Note: "),
              "Python's statsmodels cannot fit this specification. This is an R-specific robustness check."
            )
          )
        ),

        fluidRow(
          valueBox(
            value = paste0(precomputed_results$nested$icc_gemeente * 100, "%"),
            subtitle = "ICC: Gemeente Level",
            icon = icon("city"),
            color = "green",
            width = 3
          ),
          valueBox(
            value = paste0(precomputed_results$nested$icc_wijk * 100, "%"),
            subtitle = "ICC: Wijk Level",
            icon = icon("building"),
            color = "orange",
            width = 3
          ),
          valueBox(
            value = paste0(precomputed_results$nested$icc_buurt * 100, "%"),
            subtitle = "ICC: Buurt Level",
            icon = icon("home"),
            color = "blue",
            width = 3
          ),
          valueBox(
            value = paste0(precomputed_results$nested$icc_residual * 100, "%"),
            subtitle = "ICC: Individual Level",
            icon = icon("user"),
            color = "purple",
            width = 3
          )
        ),

        fluidRow(
          box(
            title = "4-Level Variance Decomposition",
            status = "success",
            width = 6,
            plotlyOutput("nested_icc_donut", height = "400px")
          ),
          box(
            title = "Interpretation",
            status = "info",
            width = 6,
            p("The nested random effects model confirms:"),
            tags$ul(
              tags$li("Variance is ", strong("overwhelmingly"), " at the individual level (~96%)"),
              tags$li("Buurt, wijk, and gemeente each contribute only ~1-2%"),
              tags$li("There is ", strong("no evidence"), " for meaningful geographic clustering")
            ),
            hr(),
            p(strong("Conclusion: "), "Results are robust to proper multilevel specification.
            The weak neighborhood effects found in the two-level models are not artifacts of
            model misspecification.")
          )
        ),

        fluidRow(
          box(
            title = "Income Ratio Sensitivity Analysis",
            status = "warning",
            width = 6,
            p("Alternative specification using income ratio (high20/low40) instead of low-income concentration:"),
            tableOutput("sensitivity_table")
          ),
          box(
            title = "Python Limitations",
            status = "danger",
            width = 6,
            p(strong("Why this matters:")),
            p("Python's statsmodels cannot fit crossed or nested random effects."),
            p("The Python dashboard uses buurt as the primary grouping with wijk/gemeente as fixed effects."),
            p("This R implementation provides the proper multilevel variance decomposition."),
            hr(),
            p(
              style = "font-style: italic;",
              "For true multilevel analysis with nested geographic structures,
              R's lme4 package is the gold standard."
            )
          )
        )
      ),

      # =========================================================================
      # About Project Tab
      # =========================================================================
      tabItem(
        tabName = "about_project",

        h2("About This Project"),
        p("Project overview, technical skills demonstrated, and documentation links."),

        # 30-Second Pitch
        fluidRow(
          box(
            title = "30-Second Pitch",
            status = "info",
            solidHeader = TRUE,
            width = 12,
            p(
              style = "font-size: 16px;",
              "I built a complete data science pipeline—from raw survey data to interactive dashboards—to test
              whether where you live affects what you believe about inequality. Using 8,000+ survey responses
              linked to official neighborhood statistics, I applied multilevel regression models and found that
              neighborhoods explain only ", strong("3.4% of attitude variation"), ". The project demonstrates
              end-to-end analytics skills: API integration, data engineering, statistical modeling, and
              visualization in both Python and R."
            )
          )
        ),

        # Technical Skills
        fluidRow(
          box(
            title = "Statistical Methods",
            status = "primary",
            width = 3,
            tags$ul(
              tags$li("Multilevel/hierarchical modeling"),
              tags$li("Variance decomposition (ICC)"),
              tags$li("Sensitivity analysis"),
              tags$li("Cross-level interactions")
            )
          ),
          box(
            title = "Data Engineering",
            status = "primary",
            width = 3,
            tags$ul(
              tags$li("API integration (CBS StatLine)"),
              tags$li("Survey + admin data linkage"),
              tags$li("Variable construction"),
              tags$li("Missing data handling")
            )
          ),
          box(
            title = "Software Development",
            status = "primary",
            width = 3,
            tags$ul(
              tags$li("Python (pandas, statsmodels, Streamlit)"),
              tags$li("R (tidyverse, lme4, Shiny)"),
              tags$li("Pipeline orchestration (targets)"),
              tags$li("Interactive dashboards")
            )
          ),
          box(
            title = "Research Skills",
            status = "primary",
            width = 3,
            tags$ul(
              tags$li("Literature review"),
              tags$li("Hypothesis testing"),
              tags$li("Academic writing"),
              tags$li("Limitations discussion")
            )
          )
        ),

        # Key Findings Summary
        fluidRow(
          box(
            title = "Key Findings Summary",
            status = "warning",
            width = 12,
            fluidRow(
              column(
                width = 4,
                h4("Variance Decomposition"),
                p(strong("Neighborhood ICC: "), "3.4%"),
                p(strong("Individual: "), "96.6%"),
                p("Attitudes are primarily driven by individual factors.")
              ),
              column(
                width = 4,
                h4("Hypothesis Testing"),
                p(strong("H1 (Neighborhood effect): "), "Not Supported"),
                p(strong("H2 (Proximity matters): "), "Inconclusive"),
                p(strong("H3 (Effect persists): "), "Not Supported")
              ),
              column(
                width = 4,
                h4("Model Progression"),
                p("Bivariate: β = 3.46 (Sig)"),
                p("+ Individual: β = 2.94 (Sig)"),
                p("+ Neighborhood: β = 0.28 (n.s.)")
              )
            )
          )
        ),

        # Research Contribution
        fluidRow(
          box(
            title = "Research Contribution",
            status = "success",
            width = 12,
            p(
              style = "font-size: 15px;",
              strong("For Academics:"), " This study provides an empirical test of Mijs' (2018) 'inferential spaces'
              hypothesis using high-quality Dutch administrative data."
            ),
            tags$ul(
              tags$li(strong("Cross-national extension:"), " Tests whether US findings replicate in a European welfare state"),
              tags$li(strong("Multi-level variance decomposition:"), " Partitions variance across neighborhoods, districts, and municipalities"),
              tags$li(strong("Dual-software implementation:"), " Results validated in both Python (statsmodels) and R (lme4)"),
              tags$li(strong("Null finding with implications:"), " Limited neighborhood effects suggest individual factors dominate in the Dutch context")
            )
          )
        ),

        # Documentation Links
        fluidRow(
          box(
            title = "Documentation (GitHub)",
            status = "info",
            width = 6,
            h4("Portfolio Materials"),
            tags$ul(
              tags$li(a("Project Summary", href = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main/PROJECT_SUMMARY.md", target = "_blank")),
              tags$li(a("Case Study", href = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main/docs/portfolio/CASE_STUDY.md", target = "_blank")),
              tags$li(a("Skills Matrix", href = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main/docs/portfolio/SKILLS_MATRIX.md", target = "_blank")),
              tags$li(a("Business Value", href = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main/docs/portfolio/BUSINESS_VALUE.md", target = "_blank"))
            )
          ),
          box(
            title = "Academic & Technical",
            status = "info",
            width = 6,
            h4("Full Documentation"),
            tags$ul(
              tags$li(a("Full Paper", href = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main/docs/academic/DRAFT_PAPER.md", target = "_blank")),
              tags$li(a("Literature Review", href = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main/docs/academic/LITERATURE_REVIEW.md", target = "_blank")),
              tags$li(a("Technical Overview", href = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main/docs/technical/TECHNICAL_OVERVIEW.md", target = "_blank")),
              tags$li(a("Reproducibility Guide", href = "https://github.com/kmazurek95/attitudes-toward-income-inequality/blob/main/docs/technical/REPRODUCIBILITY.md", target = "_blank"))
            )
          )
        ),

        # Data Sources
        fluidRow(
          box(
            title = "Data Sources",
            width = 6,
            h4("SCoRE Survey Netherlands 2017"),
            tags$ul(
              tags$li("N = 8,013 respondents"),
              tags$li("Attitudes toward redistribution"),
              tags$li("Individual socioeconomic characteristics"),
              tags$li("Geographic identifiers (buurt, wijk, gemeente)")
            )
          ),
          box(
            title = "CBS StatLine Table 84286NED",
            width = 6,
            h4("2018 Neighborhood Statistics"),
            tags$ul(
              tags$li("% low-income households"),
              tags$li("% high-income households"),
              tags$li("Income distribution ratios"),
              tags$li("Demographic indicators")
            )
          )
        ),

        # Author Info
        fluidRow(
          box(
            title = "Author",
            width = 6,
            p(strong("Kaleb Mazurek")),
            p("University of Amsterdam Internship (2023)"),
            p("Supervised by Dr. Wouter Schakel"),
            p(em("All errors and omissions are solely my own responsibility."))
          ),
          box(
            title = "Links",
            width = 6,
            actionButton(
              "github_link",
              "GitHub Repository",
              icon = icon("github"),
              onclick = "window.open('https://github.com/kmazurek95/attitudes-toward-income-inequality', '_blank')"
            ),
            actionButton(
              "python_link",
              "Python Dashboard",
              icon = icon("python"),
              onclick = paste0("window.open('", PYTHON_DASHBOARD_URL, "', '_blank')")
            ),
            hr(),
            p(em("Last updated: February 2025"))
          )
        )
      )
    )
  )
)
