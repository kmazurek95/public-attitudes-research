# =============================================================================
# charts.R - Plotly/ggplot2 Chart Functions for R Shiny Dashboard
# =============================================================================
# These functions mirror the Python dashboard charts.py for consistency.
# =============================================================================

library(plotly)
library(ggplot2)

# =============================================================================
# ICC and Variance Charts
# =============================================================================

#' Create ICC Donut Chart
#'
#' @param icc_value ICC value (0-1)
#' @param title Chart title
#' @param subtitle Chart subtitle (optional)
#' @param n_obs Number of observations (optional)
#' @param n_clusters Number of clusters (optional)
#' @return Plotly figure
create_icc_donut <- function(icc_value, title = "Variance Decomposition",
                              subtitle = NULL, n_obs = NULL, n_clusters = NULL) {
  pct_between <- round(icc_value * 100, 1)
  pct_within <- round(100 - pct_between, 1)

  data <- data.frame(
    category = c("Between Neighborhoods", "Within Neighborhoods"),
    value = c(pct_between, pct_within),
    color = c(COLORS$primary, COLORS$secondary)
  )

  # Build title with optional subtitle
  full_title <- paste0("<b>", title, "</b>")
  if (!is.null(subtitle)) {
    full_title <- paste0(full_title, "<br><span style='font-size:12px;color:gray'>", subtitle, "</span>")
  } else if (!is.null(n_obs) && !is.null(n_clusters)) {
    full_title <- paste0(full_title, "<br><span style='font-size:12px;color:gray'>n = ",
                         format(n_obs, big.mark = ","), " individuals in ",
                         format(n_clusters, big.mark = ","), " neighborhoods</span>")
  }

  plot_ly(data,
    labels = ~category,
    values = ~value,
    type = "pie",
    hole = 0.6,
    marker = list(colors = c(COLORS$primary, COLORS$secondary)),
    textinfo = "label+percent",
    textposition = "outside"
  ) %>%
    layout(
      title = list(text = full_title, x = 0.5),
      annotations = list(
        text = paste0("ICC<br>", pct_between, "%"),
        x = 0.5, y = 0.5,
        font = list(size = 20, color = COLORS$primary),
        showarrow = FALSE
      ),
      showlegend = TRUE,
      legend = list(orientation = "h", y = -0.1),
      margin = list(t = 80, b = 60)
    )
}

#' Create Multi-Level ICC Donut
#'
#' @param icc_list List with ICC values for each level
#' @param title Chart title
#' @param n_obs Number of observations (optional)
#' @return Plotly figure
create_multilevel_icc_donut <- function(icc_list, title = "4-Level Variance Decomposition", n_obs = NULL) {
  data <- data.frame(
    level = c(
      GEOGRAPHIC_LABELS$gemeente,
      GEOGRAPHIC_LABELS$wijk,
      GEOGRAPHIC_LABELS$buurt,
      GEOGRAPHIC_LABELS$individual
    ),
    value = c(
      icc_list$icc_gemeente * 100,
      icc_list$icc_wijk * 100,
      icc_list$icc_buurt * 100,
      icc_list$icc_residual * 100
    ),
    color = c(COLORS$tertiary, COLORS$secondary, COLORS$primary, COLORS$neutral)
  )

  # Build title
  full_title <- paste0("<b>", title, "</b>")
  if (!is.null(n_obs)) {
    full_title <- paste0(full_title, "<br><span style='font-size:12px;color:gray'>n = ",
                         format(n_obs, big.mark = ","), "</span>")
  }

  plot_ly(data,
    labels = ~level,
    values = ~value,
    type = "pie",
    hole = 0.5,
    marker = list(colors = c(COLORS$tertiary, COLORS$secondary, COLORS$primary, COLORS$neutral)),
    textinfo = "label+percent"
  ) %>%
    layout(
      title = list(text = full_title, x = 0.5),
      showlegend = TRUE,
      legend = list(orientation = "h", y = -0.1),
      margin = list(t = 80, b = 60)
    )
}

# =============================================================================
# Effect Plots
# =============================================================================

#' Create Forest Plot
#'
#' @param estimates Vector of coefficient estimates
#' @param errors Vector of standard errors
#' @param labels Vector of model labels
#' @param title Chart title
#' @param subtitle Chart subtitle (optional)
#' @param xaxis_label X-axis label
#' @param show_footnote Whether to show footnote
#' @return Plotly figure
create_forest_plot <- function(estimates, errors, labels, title = "Coefficient Estimates",
                                subtitle = NULL, xaxis_label = "Coefficient (95% CI)",
                                show_footnote = TRUE) {
  ci_lower <- estimates - 1.96 * errors
  ci_upper <- estimates + 1.96 * errors

  # Determine significance (CI crosses zero)
  significant <- !(ci_lower <= 0 & ci_upper >= 0)
  colors <- ifelse(significant, COLORS$primary, COLORS$neutral)

  data <- data.frame(
    label = factor(labels, levels = rev(labels)),
    estimate = estimates,
    ci_lower = ci_lower,
    ci_upper = ci_upper,
    color = colors,
    significant = significant
  )

  # Remove NA rows
  data <- data[!is.na(data$estimate), ]

  # Build title
  plot_title <- title
  if (!is.null(subtitle)) {
    plot_title <- paste0(title, "\n", subtitle)
  }

  p <- ggplot(data, aes(x = estimate, y = label, color = color)) +
    geom_vline(xintercept = 0, linetype = "dashed", color = COLORS$quaternary, size = 0.8) +
    geom_errorbarh(aes(xmin = ci_lower, xmax = ci_upper), height = 0.2, size = 1) +
    geom_point(size = 4, shape = 18) +
    scale_color_identity() +
    labs(
      title = plot_title,
      x = xaxis_label,
      y = "",
      caption = if (show_footnote) FOOTNOTES$ci else NULL
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
      plot.caption = element_text(size = 9, color = "gray50"),
      axis.text.y = element_text(size = 11),
      legend.position = "none"
    )

  ggplotly(p) %>%
    layout(
      xaxis = list(zeroline = FALSE),
      yaxis = list(zeroline = FALSE)
    )
}

#' Create Model Progression Chart
#'
#' @param model_list List of models with coef and se
#' @param title Chart title
#' @param predictor_label Label for the key predictor
#' @param show_footnote Whether to show footnote
#' @return Plotly figure
create_model_progression <- function(model_list, title = "Coefficient Stability Across Models",
                                      predictor_label = NULL, show_footnote = TRUE) {
  # Extract data from model list
  models <- names(model_list)
  labels <- sapply(model_list, function(x) x$name)
  coefs <- sapply(model_list, function(x) x$coef)
  ses <- sapply(model_list, function(x) x$se)

  # Remove NA values (empty model)
  valid <- !is.na(coefs)
  models <- models[valid]
  labels <- labels[valid]
  coefs <- coefs[valid]
  ses <- ses[valid]

  if (length(coefs) == 0) {
    return(NULL)
  }

  ci_lower <- coefs - 1.96 * ses
  ci_upper <- coefs + 1.96 * ses

  data <- data.frame(
    model = factor(labels, levels = labels),
    coef = coefs,
    ci_lower = ci_lower,
    ci_upper = ci_upper
  )

  # Use get_label if predictor_label not provided
  if (is.null(predictor_label)) {
    predictor_label <- get_label("b_perc_low40_hh", short = TRUE)
  }

  p <- ggplot(data, aes(x = model, y = coef, group = 1)) +
    geom_hline(yintercept = 0, linetype = "dashed", color = COLORS$quaternary) +
    geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper), fill = COLORS$primary, alpha = 0.2) +
    geom_line(color = COLORS$primary, size = 1) +
    geom_point(size = 4, color = COLORS$primary) +
    labs(
      title = title,
      subtitle = paste("Effect of", predictor_label),
      x = "Model Specification",
      y = "Coefficient (change in DV per 1 SD)",
      caption = if (show_footnote) "Shaded area shows 95% confidence interval" else NULL
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold"),
      plot.subtitle = element_text(hjust = 0.5, size = 10, color = "gray50"),
      plot.caption = element_text(size = 9, color = "gray50"),
      axis.text.x = element_text(angle = 45, hjust = 1)
    )

  ggplotly(p)
}

# =============================================================================
# Distribution Charts
# =============================================================================

#' Create Distribution Histogram
#'
#' @param data Data frame
#' @param column Column name to plot
#' @param title Chart title
#' @param xaxis_label X-axis label (uses get_label if NULL)
#' @param bins Number of bins
#' @param show_n Whether to show sample size in title
#' @param source_note Source note for caption
#' @return Plotly figure
create_distribution_histogram <- function(data, column, title = "Distribution",
                                           xaxis_label = NULL, bins = 30,
                                           show_n = TRUE, source_note = NULL) {
  if (is.null(data) || !column %in% names(data)) {
    return(NULL)
  }

  # Get label if not provided
  if (is.null(xaxis_label)) {
    xaxis_label <- get_label(column)
  }

  n <- sum(!is.na(data[[column]]))

  # Build title with sample size
  plot_title <- title
  plot_subtitle <- NULL
  if (show_n) {
    plot_subtitle <- paste("n =", format(n, big.mark = ","))
  }

  p <- ggplot(data, aes_string(x = column)) +
    geom_histogram(bins = bins, fill = COLORS$primary, color = "white", alpha = 0.7) +
    labs(
      title = plot_title,
      subtitle = plot_subtitle,
      x = xaxis_label,
      y = "Frequency",
      caption = source_note
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold"),
      plot.subtitle = element_text(hjust = 0.5, size = 10, color = "gray50"),
      plot.caption = element_text(size = 9, color = "gray50")
    )

  ggplotly(p)
}

#' Create Cluster Size Histogram
#'
#' @param data Data frame
#' @param group_col Grouping column (e.g., buurt_id)
#' @param title Chart title
#' @param geo_label Label for the geographic level
#' @return Plotly figure
create_cluster_size_histogram <- function(data, group_col = "buurt_id",
                                           title = "Cluster Size Distribution",
                                           geo_label = "Neighborhood") {
  if (is.null(data) || !group_col %in% names(data)) {
    return(NULL)
  }

  cluster_sizes <- data %>%
    group_by(across(all_of(group_col))) %>%
    summarise(n = n(), .groups = "drop")

  n_clusters <- nrow(cluster_sizes)
  n_obs <- nrow(data)

  p <- ggplot(cluster_sizes, aes(x = n)) +
    geom_histogram(bins = 30, fill = COLORS$primary, color = "white", alpha = 0.7) +
    geom_vline(xintercept = mean(cluster_sizes$n), linetype = "dashed",
               color = COLORS$secondary, size = 1) +
    labs(
      title = title,
      subtitle = paste(format(n_obs, big.mark = ","), "individuals in",
                       format(n_clusters, big.mark = ","), tolower(geo_label), "s"),
      x = paste("Respondents per", geo_label),
      y = paste("Number of", geo_label, "s")
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold"),
      plot.subtitle = element_text(hjust = 0.5, size = 10, color = "gray50")
    )

  ggplotly(p)
}

# =============================================================================
# Geographic Charts
# =============================================================================

#' Create Geographic Treemap
#'
#' @param data Data frame with geographic IDs
#' @param title Chart title
#' @return Plotly figure
create_geographic_treemap <- function(data, title = "Sample Distribution by Geography") {
  if (is.null(data) || !"gemeente_id" %in% names(data)) {
    return(NULL)
  }

  # Aggregate by gemeente
  gemeente_counts <- data %>%
    filter(!is.na(gemeente_id)) %>%
    group_by(gemeente_id) %>%
    summarise(n = n(), .groups = "drop") %>%
    arrange(desc(n)) %>%
    head(50)  # Top 50 for readability

  # Add gemeente names if available
  if ("gemeente_name" %in% names(data)) {
    names_lookup <- data %>%
      select(gemeente_id, gemeente_name) %>%
      distinct()
    gemeente_counts <- gemeente_counts %>%
      left_join(names_lookup, by = "gemeente_id")
  } else {
    gemeente_counts$gemeente_name <- gemeente_counts$gemeente_id
  }

  plot_ly(
    gemeente_counts,
    type = "treemap",
    labels = ~gemeente_name,
    parents = "",
    values = ~n,
    textinfo = "label+value",
    marker = list(
      colors = ~n,
      colorscale = "Blues",
      showscale = TRUE
    )
  ) %>%
    layout(
      title = list(text = title, x = 0.5)
    )
}
