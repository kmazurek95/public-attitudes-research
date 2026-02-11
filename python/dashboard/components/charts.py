# =============================================================================
# charts.py - Reusable Chart Components for Dashboard
# =============================================================================
"""
Plotly chart functions for the Streamlit dashboard.
All charts use a consistent color scheme and styling.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any

# Import centralized labels
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from utils.labels import (
        VARIABLE_LABELS, VARIABLE_LABELS_SHORT, GEOGRAPHIC_LEVELS,
        get_label, get_geo_label, FOOTNOTES, CHART_CONFIG
    )
except ImportError:
    # Fallback if labels module not available
    VARIABLE_LABELS = {}
    VARIABLE_LABELS_SHORT = {}
    GEOGRAPHIC_LEVELS = {}
    FOOTNOTES = {"data_source": "Data: SCoRE Netherlands 2017, CBS StatLine 2018"}
    CHART_CONFIG = {"title_font_size": 16, "axis_font_size": 12}
    def get_label(x, short=False): return x
    def get_geo_label(x, short=False): return x


# =============================================================================
# Color Scheme
# =============================================================================

COLORS = {
    "primary": "#1f77b4",      # Blue
    "secondary": "#ff7f0e",    # Orange
    "tertiary": "#2ca02c",     # Green
    "quaternary": "#d62728",   # Red
    "neutral": "#7f7f7f",      # Gray
    "background": "#f0f2f6",
    "text": "#262730",
}

LEVEL_COLORS = {
    "buurt": "#1f77b4",       # Blue for neighborhood
    "wijk": "#ff7f0e",        # Orange for district
    "gemeente": "#2ca02c",    # Green for municipality
}


# =============================================================================
# ICC / Variance Decomposition Charts
# =============================================================================

def create_icc_donut(
    icc_value: float,
    title: str = "Variance Decomposition",
    subtitle: str = None,
    n_clusters: int = None,
    n_obs: int = None,
    height: int = 400
) -> go.Figure:
    """
    Create a donut chart showing ICC variance decomposition.

    Parameters
    ----------
    icc_value : float
        ICC value (between 0 and 1)
    title : str
        Chart title
    subtitle : str, optional
        Chart subtitle (e.g., sample size info)
    n_clusters : int, optional
        Number of clusters (neighborhoods)
    n_obs : int, optional
        Number of observations
    height : int
        Chart height in pixels

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    pct_between = icc_value * 100
    pct_within = 100 - pct_between

    fig = go.Figure(data=[go.Pie(
        labels=['Between Neighborhoods', 'Within Neighborhoods'],
        values=[pct_between, pct_within],
        hole=0.6,
        marker_colors=[COLORS["primary"], COLORS["secondary"]],
        textinfo='label+percent',
        textposition='outside',
        textfont_size=12,
        pull=[0.02, 0]  # Slightly pull out the "between" slice
    )])

    # Build title with optional subtitle
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><span style='font-size:12px;color:gray'>{subtitle}</span>"
    elif n_obs and n_clusters:
        full_title += f"<br><span style='font-size:12px;color:gray'>n = {n_obs:,} individuals in {n_clusters:,} neighborhoods</span>"

    fig.update_layout(
        title=dict(text=full_title, x=0.5, xanchor='center', font_size=CHART_CONFIG.get("title_font_size", 16)),
        annotations=[dict(
            text=f'ICC<br>{pct_between:.1f}%',
            x=0.5, y=0.5,
            font_size=24,
            font_color=COLORS["primary"],
            showarrow=False
        )],
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        height=height,
        margin=dict(t=80, b=60, l=20, r=20)
    )

    return fig


# =============================================================================
# Forest Plots
# =============================================================================

def create_forest_plot(
    estimates: List[float],
    errors: List[float],
    labels: List[str],
    title: str = "Coefficient Estimates",
    subtitle: str = None,
    xaxis_title: str = "Coefficient (95% CI)",
    height: int = 400,
    highlight_nonsig: bool = True,
    show_footnote: bool = True
) -> go.Figure:
    """
    Create a forest plot with confidence intervals.

    Parameters
    ----------
    estimates : List[float]
        Point estimates
    errors : List[float]
        Standard errors (will be multiplied by 1.96 for 95% CI)
    labels : List[str]
        Labels for each estimate
    title : str
        Chart title
    subtitle : str, optional
        Chart subtitle
    xaxis_title : str
        X-axis label
    height : int
        Chart height in pixels
    highlight_nonsig : bool
        Whether to highlight non-significant estimates (CI crosses zero)
    show_footnote : bool
        Whether to show CI footnote

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Calculate confidence intervals
    ci_lower = [e - 1.96 * se for e, se in zip(estimates, errors)]
    ci_upper = [e + 1.96 * se for e, se in zip(estimates, errors)]

    # Determine colors based on significance
    colors = []
    for lower, upper in zip(ci_lower, ci_upper):
        if highlight_nonsig and lower <= 0 <= upper:
            colors.append(COLORS["neutral"])  # Non-significant
        else:
            colors.append(COLORS["primary"])  # Significant

    fig = go.Figure()

    # Add estimates with error bars
    fig.add_trace(go.Scatter(
        x=estimates,
        y=labels,
        mode='markers',
        marker=dict(size=12, color=colors, symbol='diamond'),
        error_x=dict(
            type='data',
            symmetric=False,
            array=[u - e for e, u in zip(estimates, ci_upper)],
            arrayminus=[e - l for e, l in zip(estimates, ci_lower)],
            color=colors[0] if len(set(colors)) == 1 else COLORS["neutral"],
            thickness=2,
            width=6
        ),
        name='Estimate',
        hovertemplate='%{y}<br>Coef: %{x:.3f}<br>95% CI: [%{customdata[0]:.3f}, %{customdata[1]:.3f}]<extra></extra>',
        customdata=list(zip(ci_lower, ci_upper))
    ))

    # Add zero line
    fig.add_vline(
        x=0,
        line_dash="dash",
        line_color=COLORS["quaternary"],
        annotation_text="No effect",
        annotation_position="top"
    )

    # Build title with optional subtitle
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><span style='font-size:12px;color:gray'>{subtitle}</span>"

    annotations = []
    if show_footnote:
        annotations.append(dict(
            text=FOOTNOTES.get("ci", "Error bars show 95% confidence intervals"),
            xref="paper", yref="paper",
            x=0, y=-0.15,
            showarrow=False,
            font=dict(size=10, color="gray"),
            align="left"
        ))

    fig.update_layout(
        title=dict(text=full_title, x=0.5, xanchor='center', font_size=CHART_CONFIG.get("title_font_size", 16)),
        xaxis_title=xaxis_title,
        yaxis_title="",
        height=height,
        margin=dict(t=80, b=80, l=150, r=40),
        showlegend=False,
        annotations=annotations
    )

    return fig


def create_multi_level_forest(
    level_estimates: Dict[str, Dict[str, float]],
    title: str = "Key Predictor Effects by Geographic Level",
    height: int = 350
) -> go.Figure:
    """
    Create a forest plot comparing effects at different geographic levels.

    Parameters
    ----------
    level_estimates : Dict
        Dict with keys 'buurt', 'wijk', 'gemeente', each containing
        'coef' and 'se' keys
    title : str
        Chart title
    height : int
        Chart height

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    levels = []
    estimates = []
    errors = []
    colors = []

    for level_name, level_label in [('buurt', 'Neighborhood'), ('wijk', 'District'), ('gemeente', 'Municipality')]:
        if level_name in level_estimates and level_estimates[level_name].get('coef') is not None:
            levels.append(f"{level_label}\n({level_name})")
            estimates.append(level_estimates[level_name]['coef'])
            errors.append(level_estimates[level_name]['se'])
            colors.append(LEVEL_COLORS[level_name])

    if not estimates:
        # Return empty figure if no data
        fig = go.Figure()
        fig.add_annotation(text="No data available", x=0.5, y=0.5, showarrow=False)
        return fig

    fig = go.Figure()

    for i, (level, est, err, color) in enumerate(zip(levels, estimates, errors, colors)):
        ci_lower = est - 1.96 * err
        ci_upper = est + 1.96 * err

        fig.add_trace(go.Scatter(
            x=[est],
            y=[level],
            mode='markers',
            marker=dict(size=14, color=color, symbol='diamond'),
            error_x=dict(
                type='data',
                symmetric=False,
                array=[ci_upper - est],
                arrayminus=[est - ci_lower],
                color=color,
                thickness=3,
                width=8
            ),
            name=level,
            hovertemplate=f'{level}<br>Coef: {est:.3f}<br>95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]<extra></extra>'
        ))

    fig.add_vline(x=0, line_dash="dash", line_color=COLORS["quaternary"])

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        xaxis_title="Coefficient (95% CI)",
        yaxis_title="",
        height=height,
        margin=dict(t=60, b=60, l=120, r=40),
        showlegend=False
    )

    return fig


# =============================================================================
# Distribution Charts
# =============================================================================

def create_distribution_histogram(
    data: pd.Series,
    title: str,
    xaxis_label: str = None,
    nbins: int = 50,
    height: int = 400,
    show_box: bool = True,
    show_n: bool = True,
    source_note: str = None
) -> go.Figure:
    """
    Create a histogram with optional box plot marginal.

    Parameters
    ----------
    data : pd.Series
        Data to plot
    title : str
        Chart title
    xaxis_label : str, optional
        X-axis label (will use data.name with get_label if not provided)
    nbins : int
        Number of bins
    height : int
        Chart height
    show_box : bool
        Whether to show box plot marginal
    show_n : bool
        Whether to show sample size in title
    source_note : str, optional
        Source note for footer

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    clean_data = data.dropna()
    n = len(clean_data)

    # Get label from variable name if not provided
    if xaxis_label is None:
        xaxis_label = get_label(data.name) if data.name else "Value"

    fig = px.histogram(
        clean_data,
        nbins=nbins,
        labels={'value': xaxis_label, 'count': 'Frequency'},
        marginal='box' if show_box else None,
        color_discrete_sequence=[COLORS["primary"]]
    )

    # Build title with sample size
    full_title = f"<b>{title}</b>"
    if show_n:
        full_title += f"<br><span style='font-size:12px;color:gray'>n = {n:,}</span>"

    annotations = []
    if source_note:
        annotations.append(dict(
            text=source_note,
            xref="paper", yref="paper",
            x=0, y=-0.12,
            showarrow=False,
            font=dict(size=10, color="gray"),
            align="left"
        ))

    fig.update_layout(
        title=dict(text=full_title, x=0.5, xanchor='center', font_size=CHART_CONFIG.get("title_font_size", 16)),
        xaxis_title=xaxis_label,
        yaxis_title="Frequency",
        height=height,
        showlegend=False,
        margin=dict(t=80, b=70, l=60, r=40),
        annotations=annotations
    )

    return fig


def create_multi_distribution(
    df: pd.DataFrame,
    columns: List[str],
    labels: Optional[Dict[str, str]] = None,
    title: str = "Distributions by Geographic Level",
    height: int = 400
) -> go.Figure:
    """
    Create overlapping histograms for multiple columns.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame
    columns : List[str]
        Column names to plot
    labels : Dict[str, str], optional
        Custom labels for columns
    title : str
        Chart title
    height : int
        Chart height

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    fig = go.Figure()

    color_map = {
        'b_': LEVEL_COLORS["buurt"],
        'w_': LEVEL_COLORS["wijk"],
        'g_': LEVEL_COLORS["gemeente"],
    }

    for col in columns:
        if col not in df.columns:
            continue

        # Determine color based on prefix
        color = COLORS["primary"]
        for prefix, c in color_map.items():
            if col.startswith(prefix):
                color = c
                break

        label = labels.get(col, col) if labels else col

        fig.add_trace(go.Histogram(
            x=df[col].dropna(),
            name=label,
            opacity=0.6,
            marker_color=color,
            nbinsx=30
        ))

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        xaxis_title="Value (standardized)",
        yaxis_title="Frequency",
        barmode='overlay',
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=60, b=80, l=60, r=40)
    )

    return fig


# =============================================================================
# Geographic Visualizations
# =============================================================================

def create_geographic_treemap(
    df: pd.DataFrame,
    title: str = "Geographic Hierarchy: Respondents by Location",
    height: int = 500
) -> go.Figure:
    """
    Create a treemap showing the geographic hierarchy.

    Parameters
    ----------
    df : pd.DataFrame
        Data with gemeente_id and wijk_id columns
    title : str
        Chart title
    height : int
        Chart height

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Aggregate counts
    geo_counts = df.groupby(['gemeente_id', 'wijk_id']).size().reset_index(name='count')
    geo_counts['gemeente_id'] = geo_counts['gemeente_id'].astype(str)
    geo_counts['wijk_id'] = geo_counts['wijk_id'].astype(str)

    # Limit to top 20 gemeenten for visibility
    top_gemeenten = df['gemeente_id'].value_counts().head(20).index.tolist()
    geo_filtered = geo_counts[geo_counts['gemeente_id'].astype(str).isin([str(g) for g in top_gemeenten])]

    if len(geo_filtered) == 0:
        geo_filtered = geo_counts.head(50)

    fig = px.treemap(
        geo_filtered,
        path=['gemeente_id', 'wijk_id'],
        values='count',
        title=title,
        color='count',
        color_continuous_scale='Blues'
    )

    fig.update_layout(
        height=height,
        margin=dict(t=60, b=20, l=20, r=20)
    )

    return fig


def create_cluster_size_histogram(
    df: pd.DataFrame,
    group_col: str = 'buurt_id',
    title: str = "Cluster Size Distribution",
    geo_label: str = "Neighborhood",
    height: int = 400
) -> go.Figure:
    """
    Create a histogram of cluster sizes.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame
    group_col : str
        Column to group by
    title : str
        Chart title
    geo_label : str
        Label for the geographic level
    height : int
        Chart height

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    cluster_sizes = df.groupby(group_col).size()
    n_clusters = len(cluster_sizes)
    n_obs = len(df)

    fig = px.histogram(
        cluster_sizes,
        nbins=30,
        labels={'value': f'Respondents per {geo_label}', 'count': f'Number of {geo_label}s'},
        color_discrete_sequence=[COLORS["primary"]]
    )

    # Add mean line
    mean_size = cluster_sizes.mean()
    fig.add_vline(
        x=mean_size,
        line_dash="dash",
        line_color=COLORS["secondary"],
        annotation_text=f"Mean: {mean_size:.1f}",
        annotation_position="top right"
    )

    # Build title with sample info
    full_title = f"<b>{title}</b>"
    full_title += f"<br><span style='font-size:12px;color:gray'>{n_obs:,} individuals in {n_clusters:,} {geo_label.lower()}s</span>"

    fig.update_layout(
        title=dict(text=full_title, x=0.5, xanchor='center', font_size=CHART_CONFIG.get("title_font_size", 16)),
        xaxis_title=f"Respondents per {geo_label}",
        yaxis_title=f"Number of {geo_label}s",
        height=height,
        showlegend=False,
        margin=dict(t=80, b=60, l=60, r=40)
    )

    return fig


# =============================================================================
# Model Comparison Charts
# =============================================================================

def create_model_progression_chart(
    model_data: Dict[str, Dict],
    title: str = "Coefficient Stability Across Models",
    subtitle: str = None,
    predictor_label: str = "% Low-Income Households (Neighborhood)",
    height: int = 400
) -> go.Figure:
    """
    Create a line chart showing coefficient stability across model specifications.

    Parameters
    ----------
    model_data : Dict
        Dict with model names as keys, containing 'key_pred_coef' and 'key_pred_se'
    title : str
        Chart title
    subtitle : str, optional
        Chart subtitle
    predictor_label : str
        Label for the key predictor
    height : int
        Chart height

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    models = []
    coefs = []
    ses = []

    for model_name, data in model_data.items():
        if data.get('key_pred_coef') is not None:
            models.append(data.get('name', model_name))
            coefs.append(data['key_pred_coef'])
            ses.append(data.get('key_pred_se', 0))

    if not coefs:
        fig = go.Figure()
        fig.add_annotation(text="No coefficient data available", x=0.5, y=0.5, showarrow=False)
        return fig

    ci_lower = [c - 1.96 * s for c, s in zip(coefs, ses)]
    ci_upper = [c + 1.96 * s for c, s in zip(coefs, ses)]

    fig = go.Figure()

    # Add CI band
    fig.add_trace(go.Scatter(
        x=models + models[::-1],
        y=ci_upper + ci_lower[::-1],
        fill='toself',
        fillcolor='rgba(31, 119, 180, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% CI',
        showlegend=True
    ))

    # Add coefficient line
    fig.add_trace(go.Scatter(
        x=models,
        y=coefs,
        mode='lines+markers',
        marker=dict(size=10, color=COLORS["primary"]),
        line=dict(color=COLORS["primary"], width=2),
        name='Coefficient'
    ))

    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["quaternary"])

    # Build title
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><span style='font-size:12px;color:gray'>{subtitle}</span>"
    else:
        full_title += f"<br><span style='font-size:12px;color:gray'>Effect of {predictor_label}</span>"

    fig.update_layout(
        title=dict(text=full_title, x=0.5, xanchor='center', font_size=CHART_CONFIG.get("title_font_size", 16)),
        xaxis_title="Model Specification",
        yaxis_title="Coefficient (change in DV per 1 SD)",
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=80, b=80, l=60, r=40),
        annotations=[dict(
            text=FOOTNOTES.get("ci", "Shaded area shows 95% confidence interval"),
            xref="paper", yref="paper",
            x=0, y=-0.18,
            showarrow=False,
            font=dict(size=10, color="gray"),
            align="left"
        )]
    )

    return fig


def create_multi_level_comparison(
    estimates: Dict[str, float],
    title: str = "Key Predictor Effect by Geographic Level",
    height: int = 350
) -> go.Figure:
    """
    Create a bar chart comparing effects at different geographic levels.

    Parameters
    ----------
    estimates : Dict
        Dict with keys like 'b_perc_low40_hh', 'w_perc_low40_hh', 'g_perc_low40_hh'
    title : str
        Chart title
    height : int
        Chart height

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    level_map = {
        'b_perc_low40_hh': ('Neighborhood (buurt)', LEVEL_COLORS["buurt"]),
        'w_perc_low40_hh': ('District (wijk)', LEVEL_COLORS["wijk"]),
        'g_perc_low40_hh': ('Municipality (gemeente)', LEVEL_COLORS["gemeente"]),
    }

    labels = []
    values = []
    colors = []

    for var, (label, color) in level_map.items():
        if var in estimates and estimates[var] is not None:
            labels.append(label)
            values.append(estimates[var])
            colors.append(color)

    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=[f'{v:.2f}' for v in values],
            textposition='outside'
        )
    ])

    fig.add_hline(y=0, line_dash="dash", line_color=COLORS["neutral"])

    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor='center'),
        xaxis_title="Geographic Level",
        yaxis_title="Coefficient",
        height=height,
        margin=dict(t=60, b=60, l=60, r=40)
    )

    return fig


# =============================================================================
# Demographic Charts
# =============================================================================

def create_boxplot_by_group(
    df: pd.DataFrame,
    y_col: str,
    x_col: str,
    title: str,
    yaxis_label: str = None,
    xaxis_label: str = None,
    show_n: bool = True,
    height: int = 400
) -> go.Figure:
    """
    Create box plots of a continuous variable by a categorical variable.

    Parameters
    ----------
    df : pd.DataFrame
        Data frame
    y_col : str
        Continuous variable column
    x_col : str
        Categorical variable column
    title : str
        Chart title
    yaxis_label : str, optional
        Y-axis label (uses get_label if not provided)
    xaxis_label : str, optional
        X-axis label (uses get_label if not provided)
    show_n : bool
        Whether to show sample size
    height : int
        Chart height

    Returns
    -------
    go.Figure
        Plotly figure object
    """
    # Get labels
    if yaxis_label is None:
        yaxis_label = get_label(y_col)
    if xaxis_label is None:
        xaxis_label = get_label(x_col)

    n = len(df[[y_col, x_col]].dropna())

    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        color_discrete_sequence=[COLORS["primary"]]
    )

    # Build title with sample size
    full_title = f"<b>{title}</b>"
    if show_n:
        full_title += f"<br><span style='font-size:12px;color:gray'>n = {n:,}</span>"

    fig.update_layout(
        title=dict(text=full_title, x=0.5, xanchor='center', font_size=CHART_CONFIG.get("title_font_size", 16)),
        xaxis_title=xaxis_label,
        yaxis_title=yaxis_label,
        height=height,
        margin=dict(t=80, b=60, l=60, r=40)
    )

    return fig
