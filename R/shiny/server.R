# =============================================================================
# server.R - Dashboard Server Logic
# =============================================================================

server <- function(input, output, session) {

  # ===========================================================================
  # Home Tab - Value Boxes
  # ===========================================================================

  stats <- get_summary_stats(analysis_data)

  output$box_respondents <- renderValueBox({
    valueBox(
      value = format(stats$n_obs, big.mark = ","),
      subtitle = "Total Respondents",
      icon = icon("users"),
      color = "blue"
    )
  })

  output$box_sample <- renderValueBox({
    valueBox(
      value = format(stats$n_complete, big.mark = ","),
      subtitle = "Analysis Sample",
      icon = icon("user-check"),
      color = "green"
    )
  })

  output$box_buurten <- renderValueBox({
    valueBox(
      value = format(stats$n_buurten, big.mark = ","),
      subtitle = "Neighborhoods",
      icon = icon("home"),
      color = "blue"
    )
  })

  output$box_wijken <- renderValueBox({
    valueBox(
      value = format(stats$n_wijken, big.mark = ","),
      subtitle = "Districts",
      icon = icon("building"),
      color = "orange"
    )
  })

  output$box_gemeenten <- renderValueBox({
    valueBox(
      value = format(stats$n_gemeenten, big.mark = ","),
      subtitle = "Municipalities",
      icon = icon("city"),
      color = "green"
    )
  })

  output$box_icc <- renderValueBox({
    valueBox(
      value = paste0(precomputed_results$two_level$icc * 100, "%"),
      subtitle = "ICC (Buurt)",
      icon = icon("chart-pie"),
      color = "purple"
    )
  })

  # ===========================================================================
  # Data Explorer Tab
  # ===========================================================================

  output$dv_histogram <- renderPlotly({
    if (is.null(analysis_data)) return(NULL)
    create_distribution_histogram(
      analysis_data,
      "DV_single",
      "Support for Redistribution (0-100)"
    )
  })

  output$key_pred_histogram <- renderPlotly({
    if (is.null(analysis_data)) return(NULL)
    create_distribution_histogram(
      analysis_data,
      "b_perc_low40_hh",
      "% Low-Income Households (Buurt, standardized)"
    )
  })

  output$sample_summary <- renderTable({
    data.frame(
      Metric = c("Total N", "Analysis N", "Neighborhoods", "Mean DV", "SD DV"),
      Value = c(
        format(stats$n_obs, big.mark = ","),
        format(stats$n_complete, big.mark = ","),
        format(stats$n_buurten, big.mark = ","),
        round(stats$dv_mean, 2),
        round(stats$dv_sd, 2)
      )
    )
  })

  output$variable_table <- DT::renderDataTable({
    data.frame(
      Variable = c(
        "DV_single", "b_perc_low40_hh", "age", "education",
        "sex", "employment_status", "born_in_nl"
      ),
      Description = c(
        "Support for redistribution (0-100 scale)",
        "% households in bottom 40% of income (buurt, std)",
        "Age in years (standardized)",
        "Years of education (standardized)",
        "Sex (Male/Female/Other)",
        "Employment status (8 categories)",
        "Born in Netherlands (0/1)"
      ),
      Type = c("DV", "Key Predictor", "Control", "Control", "Control", "Control", "Control")
    )
  }, options = list(pageLength = 10, dom = 't'))

  # ===========================================================================
  # Geographic View Tab
  # ===========================================================================

  output$cluster_sizes <- renderPlotly({
    if (is.null(analysis_data)) return(NULL)
    create_cluster_size_histogram(analysis_data, "buurt_id", "Respondents per Neighborhood")
  })

  output$gemeente_treemap <- renderPlotly({
    if (is.null(analysis_data)) return(NULL)
    create_geographic_treemap(analysis_data, "Top 50 Municipalities by Sample Size")
  })

  # ===========================================================================
  # Model Results Tab
  # ===========================================================================

  output$icc_donut <- renderPlotly({
    create_icc_donut(
      precomputed_results$two_level$icc,
      "Two-Level Variance Decomposition"
    )
  })

  output$coef_progression <- renderPlotly({
    create_model_progression(
      precomputed_results$two_level$models,
      "Key Predictor: % Low-Income HH"
    )
  })

  output$forest_plot <- renderPlotly({
    models <- precomputed_results$two_level$models

    # Extract coefficients and SEs (skip m0 which has NA)
    labels <- c("M1: + Key Pred", "M2: + Ind Ctrl", "M3: + Buurt Ctrl")
    estimates <- c(models$m1$coef, models$m2$coef, models$m3$coef)
    errors <- c(models$m1$se, models$m2$se, models$m3$se)

    create_forest_plot(estimates, errors, labels, "Key Predictor Effect Across Models")
  })

  output$model_table <- renderTable({
    models <- precomputed_results$two_level$models
    data.frame(
      Model = c("M0: Empty", "M1: + Key Pred", "M2: + Ind Ctrl", "M3: + Buurt Ctrl"),
      Coefficient = c(NA, models$m1$coef, models$m2$coef, models$m3$coef),
      SE = c(NA, models$m1$se, models$m2$se, models$m3$se),
      Significant = c(NA, "***", "***", "n.s.")
    )
  }, na = "-")

  # ===========================================================================
  # R-Specific Analyses Tab
  # ===========================================================================

  output$nested_icc_donut <- renderPlotly({
    create_multilevel_icc_donut(precomputed_results$nested)
  })

  output$sensitivity_table <- renderTable({
    sens <- precomputed_results$sensitivity
    data.frame(
      Specification = c(
        sens$base$name, sens$two_item$name, sens$three_item$name,
        sens$dutch_only$name, sens$income_ratio$name
      ),
      Coefficient = c(
        sens$base$coef, sens$two_item$coef, sens$three_item$coef,
        sens$dutch_only$coef, sens$income_ratio$coef
      ),
      SE = c(
        sens$base$se, sens$two_item$se, sens$three_item$se,
        sens$dutch_only$se, sens$income_ratio$se
      ),
      Significant = c(
        ifelse(sens$base$sig, "Yes", "No"),
        ifelse(sens$two_item$sig, "Yes", "No"),
        ifelse(sens$three_item$sig, "Yes", "No"),
        ifelse(sens$dutch_only$sig, "Yes", "No"),
        ifelse(sens$income_ratio$sig, "Yes", "No")
      )
    )
  })

}
