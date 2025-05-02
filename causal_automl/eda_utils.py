import re
import textwrap
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

import helpers.hopenai as hopenai
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.collections import PatchCollection
from matplotlib.patches import Polygon
from matplotlib.ticker import FuncFormatter

# Notebook styling.
sns.set_theme(style="whitegrid")

# #############################################################################
# Preprocessing
# #############################################################################


def _infer_country(
    row: pd.Series, country2cont: Dict[str, str]
) -> Optional[Union[str, float]]:
    """
    Determine the country corresponding to the given row.

    Check the tags first for a matching country. If none is found,
    search the title, description, and notes fields.

    :param row: row with data including tags and text fields
    :param country2cont: mapping from country names to continents
    :return: first matching country if found, or nan if no match exists
    """
    for t in row["tags_list"] or []:
        tt = str(t).strip()
        if tt in country2cont:
            return tt
    for fld in ("title", "description", "notes"):
        for w in str(row.get(fld, "")).split():
            w0 = w.strip(",.()")
            if w0 in country2cont:
                return w0
    return np.nan


def preprocess_fred(
    df: pd.DataFrame, country_continent_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Preprocessing function.

    :param df: FRED metadata
    :param country_continent_df: DataFrame mapping countries to
        continents
    :return: preprocessed data
    """
    df = df.copy()
    # Parse dates & drop tzinfo.
    df["last_updated"] = pd.to_datetime(
        df["last_updated"], utc=True, errors="coerce"
    ).dt.tz_convert(None)
    df["start_date"] = pd.to_datetime(
        df["start_date"], format="%Y-%m-%d", errors="coerce"
    )
    df["end_date"] = pd.to_datetime(
        df["end_date"], format="%Y-%m-%d", errors="coerce"
    )
    # Extract base frequency.
    df["freq_base"] = (
        df["frequency"].fillna("Not Available").str.split(",", n=1).str[0]
    )
    # Split tags & categories into lists, count them.
    df["tags_list"] = df["tags"].str.split(";")
    df["categories_list"] = (
        df["categories"]
        .fillna("")
        .str.split(";")
        .map(lambda L: [c.strip().title() for c in L if c.strip()])
    )
    df["n_tags"] = df["tags_list"].str.len().fillna(0).astype(int)
    df["n_categories"] = df["categories_list"].str.len().fillna(0).astype(int)
    # Flag discontinued series.
    df["is_discontinued"] = df["tags_list"].map(
        lambda lst: any(
            str(t).strip().lower() == "discontinued" for t in (lst or [])
        )
    )
    # Compute staleness, years, decades, duration.
    today = pd.Timestamp.today().normalize()
    df["staleness_days"] = (today - df["last_updated"]).dt.days
    df["last_year"] = df["last_updated"].dt.year
    df["start_year"] = df["start_date"].dt.year
    df["end_year"] = df["end_date"].dt.year
    df["start_decade"] = (df["start_year"] // 10) * 10
    df["end_decade"] = (df["end_year"] // 10) * 10
    # Duration in years (only where both dates valid).
    mask = df["start_date"].notna() & df["end_date"].notna()
    dur_days = (
        df.loc[mask, "end_date"].values.astype("datetime64[D]")
        - df.loc[mask, "start_date"].values.astype("datetime64[D]")
    ).astype(int)
    df["duration_years"] = np.nan
    df.loc[mask, "duration_years"] = dur_days / 365.0
    # Infer country & continent.
    country_continent_df["Country_Name"] = country_continent_df[
        "Country_Name"
    ].str.strip()
    country_continent_df["Continent_Name"] = country_continent_df[
        "Continent_Name"
    ].str.strip()
    country2cont = dict(
        zip(
            country_continent_df["Country_Name"],
            country_continent_df["Continent_Name"],
        )
    )
    df["country"] = df.apply(
        lambda row: _infer_country(row, country2cont), axis=1
    )
    df["continent"] = df["country"].map(country2cont).fillna("Other")
    # Lengths of free‐text fields.
    df["title_len"] = df["title"].str.len().fillna(0).astype(int)
    df["desc_len"] = df["description"].str.len().fillna(0).astype(int)
    df["notes_len"] = df["notes"].str.len().fillna(0).astype(int)
    return df


# #############################################################################
# Visaulization Functions
# #############################################################################


def plot_top_n_annotated_bar(
    counts: pd.Series,
    total: int,
    top_n: int,
    *,
    wrap_width: Optional[int] = 30,
    cmap: Any = plt.cm.Spectral,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 100,
    xlabel: str = "",
    ylabel: str = "Count",
    title: str = "",
    note_prefix: str = "Top {n} cover ",
    note_pos: Tuple[float, float] = (0.95, 0.85),
    rotation: int = 45,
    fontsize_title: int = 16,
    fontsize_labels: int = 10,
    fontsize_annotation: int = 10,
    fontsize_note: int = 11,
    formatter: Optional[FuncFormatter] = None,
    annotation_fmt: str = "{pct:.1f}%",
    show_coverage_note: bool = True,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot the top N entries of counts as a bar chart.

    Annotate each bar with its percentage of total. Optionally add a
    coverage note.

    :param counts: count values keyed by label
    :param total: total to compute percentages against
    :param top_n: number of top entries to plot
    :param wrap_width: value to wrap long labels
    :param cmap: colormap for bars
    :param figsize: dimensions of the figure
    :param dpi: resolution of the figure
    :param xlabel: label for the x-axis
    :param ylabel: label for the y-axis
    :param title: title of the chart
    :param note_prefix: template for coverage note, must include {n}
    :param note_pos: coordinates for coverage note in axes space
    :param rotation: rotation angle for tick labels
    :param fontsize_title: font size for the chart title
    :param fontsize_labels: font size for axis labels
    :param fontsize_annotation: font size for bar annotations
    :param fontsize_note: font size for the coverage note
    :param formatter: custom formatter for y-axis ticks
    :param annotation_fmt: template for bar-label annotations, must
        include {pct}
    :param show_coverage_note: indicates whether to display the coverage
        note
    :return: figure and axes references
    """
    # Select the top entries.
    top = counts.head(top_n)
    # Check if label wrapping is required.
    if wrap_width:
        labels = [textwrap.fill(lbl, wrap_width) for lbl in top.index]
    else:
        labels = list(top.index)
    # Extract the values.
    values = top.values
    # Compute overall coverage percentage.
    coverage = values.sum() / total * 100.0
    # Compute x positions for the bars.
    x = np.arange(len(top))
    # Generate colors for the bars.
    colors = cmap(np.linspace(0, 1, len(top)))
    # Create the figure and axes.
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    # Draw the bar chart.
    bars = ax.bar(x, values, color=colors, edgecolor="gray", linewidth=1)
    # Calculate a vertical offset for annotations.
    offset = max(values) * 0.01
    # Annotate each bar with its percentage.
    for b, cnt in zip(bars, values):
        pct = cnt / total * 100.0
        txt = annotation_fmt.format(pct=pct)
        ax.text(
            b.get_x() + b.get_width() * 0.5,
            cnt + offset,
            txt,
            ha="center",
            va="bottom",
            fontsize=fontsize_annotation,
        )
    # Configure x-axis ticks and labels.
    ax.set_xticks(x)
    ax.set_xticklabels(
        labels, rotation=rotation, ha="right", fontsize=fontsize_labels
    )
    # Set the labels and title of the chart.
    ax.set_xlabel(xlabel, fontsize=fontsize_labels)
    ax.set_ylabel(ylabel, fontsize=fontsize_labels)
    ax.set_title(title, fontsize=fontsize_title, pad=12)
    # Format y-axis ticks.
    if formatter:
        ax.yaxis.set_major_formatter(formatter)
    else:
        ax.yaxis.set_major_formatter(FuncFormatter(lambda v, p: f"{int(v):,}"))
    # Add a coverage note if required.
    if show_coverage_note:
        note = note_prefix.format(n=top_n) + f"{coverage:.1f}%"
        ax.text(
            note_pos[0],
            note_pos[1],
            note,
            transform=ax.transAxes,
            ha="right",
            va="top",
            fontsize=fontsize_note,
            bbox={
                "boxstyle": "round,pad=0.3",
                "fc": "white",
                "ec": "gray",
                "alpha": 0.7,
            },
        )
    # Adjust the layout.
    plt.tight_layout()
    return fig, ax


def plot_histograms(
    data_series: List[pd.Series],
    labels: List[str],
    colors: List[str],
    *,
    bins: int = 50,
    kde: bool = True,
    figsize: Tuple[int, int] = (8, 5),
    xlabel: str = "",
    title: str = "",
    legend_title: Optional[str] = None,
    show_legend: bool = True,
    xticks: Optional[List[float]] = None,
    xtick_labels: Optional[List[str]] = None,
    xticks_shift: float = 0.0,
    xticks_rotation: float = 0,
    invert_xaxis: bool = False,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot overlaid histograms with KDE and advanced x-axis control.

    :param data_series: data to plot
    :param labels: legend labels corresponding to each data series
    :param colors: colors for each data series
    :param bins: number of bins or bin edges
    :param kde: flag indicating whether to plot kernel density estimate
    :param figsize: size of the figure
    :param xlabel: label for the x-axis
    :param title: title of the chart
    :param legend_title: title for the legend
    :param show_legend: flag indicating whether to display the legend
    :param xticks: positions for x-ticks
    :param xtick_labels: labels for x-ticks
    :param xticks_shift: offset to add to each x-tick position
    :param xticks_rotation: angle for rotating x-tick labels
    :param invert_xaxis: flag indicating whether to invert the x-axis
    :return: figure and axis objects
    """
    # Create chart objects.
    fig, ax = plt.subplots(figsize=figsize)
    # Plot each dataset.
    for series, lbl, col in zip(data_series, labels, colors):
        sns.histplot(series, bins=bins, kde=kde, color=col, label=lbl, ax=ax)
    # Include legend.
    if show_legend and labels and any(labels):
        ax.legend(title=legend_title)
    # Label x-axis.
    ax.set_xlabel(xlabel)
    # Title chart.
    ax.set_title(title)
    # Shift x-ticks.
    if xticks is not None:
        shifted = np.array(xticks) + xticks_shift
        ax.set_xticks(shifted)
    # Set tick labels.
    if xtick_labels is not None:
        ax.set_xticklabels(xtick_labels, rotation=xticks_rotation)
    # Reverse x-axis.
    if invert_xaxis:
        ax.invert_xaxis()
    # Optimize layout.
    plt.tight_layout()
    return fig, ax


def plot_stacked_bar(
    df: pd.DataFrame,
    index_labels: List[str],
    xlabel: str,
    ylabel: str,
    title: str,
    legend_labels: List[str],
    colormap: Any,
    *,
    width: float = 0.8,
    figsize: Tuple[int, int] = (14, 6),
    dpi: int = 100,
    bbox_to_anchor: Tuple[float, float, float, float] = (0, 0, 0.85, 1),
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot a stacked bar chart.

    :param df: input chart data to plot as stacked bars
    :param index_labels: labels for the x-axis corresponding to each row
    :param xlabel: label for the x-axis
    :param ylabel: label for the y-axis
    :param title: title of the chart
    :param legend_labels: entries for the legend in the order of the
        data columns
    :param colormap: either a colormap or a sequence of colors for the
        bars
    :param width: width of the bars
    :param figsize: size of the figure
    :param dpi: dots per inch of the figure
    :param bbox_to_anchor: dimensions for figure layout adjustment to
        accommodate the legend
    :return: figure and axes
    """
    # Create figure and axes.
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    # Define plotting parameters.
    plot_kwargs = {
        "kind": "bar",
        "stacked": True,
        "ax": ax,
        "width": width,
        "edgecolor": "white",
        "linewidth": 1,
        "legend": False,
    }
    if isinstance(colormap, (list, tuple)):
        plot_kwargs["color"] = colormap
    else:
        plot_kwargs["colormap"] = colormap
    # Render the stacked bar chart.
    df.plot(**plot_kwargs)
    ax.set_xticks(np.arange(len(index_labels)))
    ax.set_xticklabels(index_labels, rotation=45, ha="right", fontsize=10)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, pad=12)
    ax.yaxis.set_major_formatter(lambda x, pos: f"{int(x):,}")
    ax.legend(legend_labels, title="", loc="upper right", fontsize=10)
    fig.tight_layout(rect=bbox_to_anchor)
    return fig, ax


def plot_donut(
    sizes: List[float],
    labels: List[str],
    title: str,
    *,
    colors: Optional[List[str]] = None,
    explode: Optional[Tuple[float, ...]] = None,
    figsize: Tuple[int, int] = (6, 6),
    fontsize: int = 12,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Draw a donut-style pie chart.

    :param sizes: values for each slice
    :param labels: labels for each slice
    :param title: chart title
    :param colors: colors for slices
    :param explode: fractional offset for slices
    :param figsize: figure size
    :param fontsize: font size for slice annotations
    :return: figure and axes objects
    """
    # Create figure and axes.
    fig, ax = plt.subplots(figsize=figsize)
    # Set default colors if missing.
    if colors is None:
        colors = plt.cm.Set2(np.arange(len(sizes)))
    # Set default explosion if missing.
    if explode is None:
        explode = (0.05,) + (0,) * (len(sizes) - 1)
    # Draw pie chart with donut styling.
    ax.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        pctdistance=0.75,
        colors=colors,
        explode=explode,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
        textprops={"fontsize": fontsize},
    )
    # Draw center circle.
    centre_circle = plt.Circle((0, 0), 0.45, fc="white", linewidth=0)
    ax.add_artist(centre_circle)
    # Set title and equal aspect.
    ax.set_title(title, fontsize=16, pad=20)
    ax.axis("equal")
    # Adjust layout and return objects.
    plt.tight_layout()
    return fig, ax


def plot_cumulative_coverage(
    cum_coverage: pd.Series,
    cutoff_index: int,
    xlabel: str,
    ylabel: str,
    title: str,
    *,
    highlight_color: str = "red",
    linestyle: str = "--",
    figsize: tuple = (10, 6),
    dpi: int = 100,
    grid_alpha: float = 0.7,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot cumulative coverage curve and highlight the cutoff for the top
    categories.

    :param cum_coverage: cumulative coverage values sorted descending
    :param cutoff_index: index at which to draw and label the horizontal
        cutoff line
    :param xlabel: label for the x-axis
    :param ylabel: label for the y-axis
    :param title: title of the plot
    :param highlight_color: color of the cutoff line
    :param linestyle: linestyle of the cutoff line
    :param figsize: size of the figure
    :param dpi: figure dpi
    :param grid_alpha: alpha transparency for the horizontal grid
    :return: figure and axes objects
    """
    # Define x-axis positions.
    x = np.arange(1, len(cum_coverage) + 1)
    # Determine cutoff value.
    cutoff = cum_coverage.iloc[cutoff_index - 1]
    # Create figure and axes.
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.plot(x, cum_coverage.values, linewidth=2)
    ax.axhline(
        cutoff,
        color=highlight_color,
        linestyle=linestyle,
        label=f"Top {cutoff_index} Coverage: {cutoff:.1f}%",
    )
    # Set labels and title.
    ax.set_xlabel(xlabel, fontsize=13)
    ax.set_ylabel(ylabel, fontsize=13)
    ax.set_title(title, fontsize=16, pad=12)
    ax.legend(loc="lower right")
    ax.grid(axis="y", linestyle="--", alpha=grid_alpha)
    # Adjust layout and return figure.
    plt.tight_layout()
    return fig, ax


def plot_cumulative_count(
    series: pd.Series,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    color: str = "steelblue",
    linewidth: float = 2,
    grid: bool = True,
    grid_alpha: float = 0.3,
    figsize: tuple = (10, 6),
    dpi: int = 100,
    fontsize_title: int = 14,
    fontsize_labels: int = 12,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot cumulative values as a line graph with grid and labels.

    :param series: the Series with a sortable index to plot
    :param xlabel: the label for the x-axis
    :param ylabel: the label for the y-axis
    :param title: the title of the plot
    :param color: the color of the line
    :param linewidth: the width of the line
    :param grid: flag to display grid lines
    :param grid_alpha: the transparency level for the grid
    :param figsize: the size of the figure
    :param dpi: the resolution of the figure
    :param fontsize_title: the font size for the title
    :param fontsize_labels: the font size for axis labels
    :return: the figure and axes of the plot
    """
    # Initialize figure.
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    # Plot series.
    ax.plot(series.index, series.values, color=color, linewidth=linewidth)
    if grid:
        # Enable grid.
        ax.grid(True, alpha=grid_alpha)
    ax.set_xlabel(xlabel, fontsize=fontsize_labels)
    ax.set_ylabel(ylabel, fontsize=fontsize_labels)
    ax.set_title(title, fontsize=fontsize_title, pad=12)
    # Adjust layout.
    plt.tight_layout()
    return fig, ax


def plot_grouped_bars(
    df: pd.DataFrame,
    categories: list[str],
    series_names: list[str],
    colors: list[str],
    *,
    xlabel: str = "",
    ylabel: str = "",
    title: str = "",
    bar_width: float = 0.4,
    annotation_fmt: str = "{pct:.1f}%",
    fontsize_title: int = 15,
    fontsize_labels: int = 13,
    fontsize_annotation: int = 9,
    grid: bool = True,
    grid_kwargs: Optional[Dict[str, Any]] = None,
    figsize: tuple = (10, 5),
    dpi: int = 100,
    legend_title: Optional[str] = None,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot multiple series side by side for each category.

    :param df: source for series counts
    :param categories: category labels for x-axis
    :param series_names: series names to plot
    :param colors: color codes for series
    :return: figure and axes
    """
    # Compute x positions.
    x = np.arange(len(categories))
    # Create figure and axes.
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    # Compute number of series.
    n = len(series_names)
    # Loop through each series.
    for i, (name, color) in enumerate(zip(series_names, colors)):
        vals = df[name].loc[categories].values
        offset = (i - (n - 1) / 2) * bar_width
        bars = ax.bar(
            x + offset,
            vals,
            width=bar_width,
            label=name,
            color=color,
            edgecolor="white",
        )
        # Annotate bars.
        maxval = df.values.max()
        for b, v in zip(bars, vals):
            pct = v / df[series_names].values.sum() * 100
            txt = annotation_fmt.format(pct=pct)
            ax.text(
                b.get_x() + b.get_width() / 2,
                v + maxval * 0.005,
                txt,
                ha="center",
                va="bottom",
                fontsize=fontsize_annotation,
            )
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=fontsize_labels)
    ax.set_xlabel(xlabel, fontsize=fontsize_labels)
    ax.set_ylabel(ylabel, fontsize=fontsize_labels)
    ax.set_title(title, fontsize=fontsize_title, pad=12)
    if legend_title or series_names:
        ax.legend(title=legend_title)
    if grid:
        ax.grid(axis="y", **(grid_kwargs or {"linestyle": "--", "alpha": 0.7}))
    plt.tight_layout()
    return fig, ax


def print_category_hierarchy(
    root_ct: Counter,
    child_ct: Dict[str, Counter],
    grand_ct: Dict[Tuple[str, str], Counter],
    total: int,
    *,
    top_n: int = 20,
    indent_str: str = "  ",
    pct_fmt: str = "{:.2f}%",
) -> None:
    """
    Print a tree of the top N roots, their top-2 children, and so on.

   E.g.: CategoryA (45.0%)
          ├─ SubCategory1 (25.0%)   
          │   
          ├─ Detail1 (15.0%)   
          │   └─ SubDetail1 (10.0%)   
          └─ Others (20.0%)

    :param root_ct: counts for root categories
    :param child_ct: counts for children under each root
    :param grand_ct: counts for grandchildren under each child
    :param total: overall count
    :param top_n: number of root categories to print
    :param indent_str: character for indentation
    :param pct_fmt: format for percentages
    """
    for root, rc in root_ct.most_common(top_n):
        # Compute root percentage.
        pct_root = pct_fmt.format(rc / total * 100)
        print(f"{root} ({pct_root})")
        # Process top 2 children.
        cc = child_ct.get(root, Counter())
        top2_c = cc.most_common(2)
        for child, ccnt in top2_c:
            # Calculate and format the percentage for the child.
            pct_c = pct_fmt.format(ccnt / total * 100)
            print(f"{indent_str}├─ {child} ({pct_c})")
            # Retrieve the grandchild counts for this child.
            gc = grand_ct.get((root, child), Counter())
            top2_g = gc.most_common(2)
            for grand, gcnt in top2_g:
                # Calculate and format the percentage for the grandchild.
                pct_g = pct_fmt.format(gcnt / total * 100)
                print(f"{indent_str * 2}│   ├─ {grand} ({pct_g})")
            # Compute the count for remaining grandchildren.
            others_g = ccnt - sum(g for _, g in top2_g)
            if others_g > 0:
                pct_og = pct_fmt.format(others_g / total * 100)
                print(f"{indent_str * 2}│   └─ Others ({pct_og})")
        # Compute the count for remaining children not in the top 2.
        others_c = rc - sum(c for _, c in top2_c)
        if others_c > 0:
            pct_oc = pct_fmt.format(others_c / total * 100)
            print(f"{indent_str}└─ Others ({pct_oc})")
        # Print blank line.
        print()


def plot_choropleth_map(
    patches: List[Polygon],
    values: List[float],
    *,
    cmap: str = "viridis",
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
    style: str = "ggplot",
    figsize: Tuple[int, int] = (15, 10),
    dpi: int = 100,
    facecolor: str = "#f7f7f7",
    edgecolor: str = "white",
    linewidth: float = 0.5,
    cbar_orientation: str = "horizontal",
    cbar_fraction: float = 0.04,
    cbar_pad: float = 0.05,
    cbar_label: str = "",
    title: str = "",
    title_kwargs: Optional[Dict[str, Any]] = None,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot a choropleth given a list of patch objects and corresponding values.

    :param patches: collection of patch objects for geographical areas
    :param values: numerical values corresponding to patches
    :param cmap: colormap name to use
    :param vmin: minimum value for normalization
    :param vmax: maximum value for normalization
    :param style: style name for plot
    :param figsize: figure dimensions
    :param dpi: dots per inch resolution
    :param facecolor: background color for plot area
    :param edgecolor: color for patch boundaries
    :param linewidth: line thickness for patch outlines
    :param cbar_orientation: direction of colorbar
    :param cbar_fraction: fraction parameter for colorbar size
    :param cbar_pad: padding between plot and colorbar
    :param cbar_label: label for colorbar
    :param title: plot title
    :param title_kwargs: keyword arguments for title formatting
    :return: choropleth map
    """
    if style:
        plt.style.use(style)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_facecolor(facecolor)
    # Normalize color scale.
    norm = plt.Normalize(
        vmin=0 if vmin is None else vmin,
        vmax=(max(values) if vmax is None else vmax),
    )
    # Create patch collection.
    pc = PatchCollection(
        patches,
        array=np.array(values),
        cmap=cmap,
        norm=norm,
        edgecolor=edgecolor,
        linewidth=linewidth,
    )
    ax.add_collection(pc)
    ax.autoscale_view()
    # Colorbar.
    cbar = fig.colorbar(
        pc,
        ax=ax,
        orientation=cbar_orientation,
        fraction=cbar_fraction,
        pad=cbar_pad,
    )
    cbar.set_label(cbar_label, fontsize=12)
    cbar.ax.tick_params(labelsize=10)
    # Title.
    if title:
        ax.set_title(
            title,
            **(
                {"fontsize": 20, "fontweight": "bold", "pad": 20}
                if title_kwargs is None
                else title_kwargs
            ),
        )
    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()
    return fig, ax


def plot_heatmap(
    matrix: pd.DataFrame,
    *,
    annot: bool = True,
    cmap: str = "coolwarm",
    fmt: str = ".2f",
    cbar: bool = True,
    figsize: Tuple[int, int] = (8, 6),
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
    **heatmap_kwargs: Any,
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot a correlation (or any) matrix as a heatmap.

    :param matrix: the data to be plotted as a heatmap
    :param annot: whether to annotate cells with their values
    :param cmap: colormap name to use
    :param fmt: format for annotations
    :param cbar: whether to show the colorbar
    :param figsize: dimensions for the plot
    :param title: title of the plot
    :param xlabel: label for the x-axis
    :param ylabel: label for the y-axis
    :param heatmap_kwargs: additional keyword arguments passed to the
        heatmap function
    :return: the resulting heatmap figure and axis objects
    """
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(
        matrix,
        annot=annot,
        fmt=fmt,
        cmap=cmap,
        cbar=cbar,
        ax=ax,
        **heatmap_kwargs,
    )
    ax.set_title(title, pad=12)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    return fig, ax


def plot_scatterplot(
    df: pd.DataFrame,
    x: str,
    y: str,
    figsize: Tuple[int, int] = (8, 6),
    dpi: int = 100,
    alpha: float = 0.3,
    s: int = 10,
    title: str = "",
    xlabel: str = "",
    ylabel: str = "",
) -> Tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]:
    """
    Plot a scatterplot.

    :param df: data to plot
    :param x: column name for x-axis
    :param y: column name for y-axis
    :param figsize: size of the figure
    :param dpi: resolution of the figure
    :param alpha: transparency for the points
    :param s: marker size
    :param title: plot title
    :param xlabel: label for the x-axis
    :param ylabel: label for the y-axis
    :return: figure and axes objects for the scatterplot
    """
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    sns.scatterplot(data=df, x=x, y=y, alpha=alpha, s=s, ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    return fig, ax


# #############################################################################
# Filtering Functions
# #############################################################################


def prepare_top_counts(
    df: pd.DataFrame,
    column: str,
    *,
    top_n: Optional[int] = None,
    filter_mask: Optional[pd.Series] = None,
    explode: bool = False,
    split: Optional[Tuple[str, int]] = None,
    drop: Sequence[str] = (),
    rename: Optional[Dict[str, str]] = None,
    threshold: Optional[int] = None,
    include_other: bool = False,
    other_label: str = "Other",
) -> Tuple[pd.Series, int]:
    """
    Return a (counts, total) pair ready for plotting.

    :param df: data to count over
    :param column: column name to count over
    :param top_n: take only the top N after all other operations
    :param filter_mask: mask to pre‐filter df
    :param explode: if True, column must be list‐like and will be exploded first
    :param split: (separator, level) to split strings, e.g. (";", 0) for root
    :param drop: indices to drop
    :param rename: index renames
    :param threshold: if set, group any value with count < threshold into a single cell
    :param include_other: if True and top_n is set, append “Other” containing everything below top_n
    :param other_label: the label for that combined bucket

    :return:
        - counts: categories, with counts
        - total: total count over which percentages should be computed
    """
    # Get series, filter if needed.
    s = df[column]
    if filter_mask is not None:
        s = s[filter_mask]
    # Explode and split if applicable.
    if explode:
        s = s.explode()
    if split is not None:
        sep, lvl = split
        s = (
            s.fillna("")
            .astype(str)
            .str.split(sep)
            .apply(
                lambda L: (
                    L[lvl].strip()
                    if len(L) > abs(lvl) and L[lvl].strip()
                    else None
                )
            )
        )
    # Clean up, count values.
    s = s.dropna()
    counts = s.value_counts()
    # Adjust counts by dropping and renaming.
    if drop:
        counts.index = counts.index.str.strip()
        counts = counts.drop(index=drop, errors="ignore")
    if rename is not None:
        counts = counts.rename(index=rename)
    # Set total count and group minor values.
    total = len(s)
    if threshold is not None:
        major = counts[counts >= threshold]
        minor = counts[counts < threshold].sum()
        counts = pd.concat([major, pd.Series({other_label: minor})])
    # Limit to top_n; add "Other" if required.
    if top_n is not None:
        top = counts.head(top_n)
        if include_other and len(counts) > top_n:
            other = counts.iloc[top_n:].sum()
            top = top.append(pd.Series({other_label: other}))
        counts = top
    return counts, total


def get_binary_counts(
    df: pd.DataFrame,
    *,
    mask: Optional[pd.Series] = None,
    pattern: Optional[str] = None,
    search_cols: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
) -> Tuple[List[str], List[int]]:
    """
    Return binary counts from dataframe.

    :param df: input data
    :param mask: filter for rows
    :param pattern: regex pattern to match in columns
    :param search_cols: list of column names to search
    :param labels: two-element list with labels for positive and
        negative cases
    :return: labels and a two-element list with counts for positive and
        negative cases
    """
    if labels is None:
        labels = ["True", "False"]
    if mask is None:
        if pattern is None or not search_cols:
            raise ValueError(
                "Either mask or (pattern + search_cols) must be provided"
            )
        # Build the mask.
        mask = pd.Series(False, index=df.index)
        for col in search_cols:
            if col in df:
                mask |= (
                    df[col]
                    .fillna("")
                    .str.contains(pattern, case=False, regex=True)
                )
    else:
        # Ensure it's boolean.
        mask = mask.astype(bool)
    counts = mask.value_counts()
    true_count = int(counts.get(True, 0))
    false_count = int(counts.get(False, 0))
    return labels, [true_count, false_count]


def prepare_crosstab(
    df: pd.DataFrame,
    index_col: str,
    pivot_col: str,
    *,
    top_n: Optional[int] = None,
    index_list: Optional[List[str]] = None,
    wrap_width: int = 30,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Generate a contingency table and wrapped labels.

    :param df: input data
    :param index_col: field to group as rows
    :param pivot_col: field to pivot as columns
    :param top_n: number of top values of index_col to include
    :param index_list: specific index values to include
    :param wrap_width: number of letters before wrapping labels
    :return: the reindexed table and wrapped labels
    """
    # Check if index list is provided.
    if index_list is not None:
        idx = index_list
    else:
        # Select top entries for the index.
        idx = df[index_col].value_counts().head(top_n).index.tolist()
    # Generate the contingency table.
    ct = pd.crosstab(df[index_col], df[pivot_col]).reindex(idx).fillna(0)
    # Wrap index labels for display.
    labels = [textwrap.fill(lbl, wrap_width) for lbl in idx]
    # Return the table and wrapped labels.
    return ct, labels


def build_category_hierarchy_counts(
    cat_series: pd.Series, *, delimiter: str = ";"
) -> Tuple[Counter, Dict[str, Counter], Dict[Tuple[str, str], Counter], int]:
    """
    Build hierarchical count structures from category paths.

    :param cat_series: delimited category paths
    :param delimiter: delimiter used in the category paths
    :return:
        - count of roots
        - a mapping of child counts per root
        - a mapping of grandchild counts per root and child
        - the total count
    """
    # Process category paths.
    paths = (
        cat_series.fillna("")
        .str.split(delimiter)
        .apply(lambda L: [p.strip() for p in L if p.strip()])
    )
    # Initialize counters.
    root_ct: Counter[str] = Counter()
    child_ct: Dict[str, Counter[str]] = {}
    grand_ct: Dict[Tuple[str, str], Counter[str]] = {}
    for path in paths:
        if not path:
            continue
        root = path[0]
        root_ct[root] += 1
        if len(path) > 1:
            child = path[1]
            child_ct.setdefault(root, Counter())[child] += 1
            if len(path) > 2:
                grand = path[2]
                grand_ct.setdefault((root, child), Counter())[grand] += 1
    # Compute total series count.
    total = sum(root_ct.values())
    # Return counts and total.
    return root_ct, child_ct, grand_ct, total


def get_top_tags_by_root(
    df: pd.DataFrame,
    categories_col: str = "categories",
    tags_col: str = "tags_list",
    redundant: Optional[set[str]] = None,
    top_n: int = 10,
) -> pd.DataFrame:
    """
    For each root category, find the top-N most common tags.

    Find the most common tags up to a maximum of top_n per category and
    exclude redundant tags based on the provided parameter.

    :param df: the source data containing category and tags columns
    :param categories_col: the name of the column with category data
    :param tags_col: the name of the column with tags
    :param redundant: tags to exclude from the counts
    :param top_n: the maximum number of tags to return for each root
        category
    :return: results organized by root with associated tags and counts
    """
    if redundant is None:
        redundant = set()
    redundant_lower = {t.lower() for t in redundant}
    # Compute each series’ root category.
    root_series = (
        df[categories_col]
        .fillna("")
        .str.split(";", n=1)
        .str[0]
        .str.strip()
        .replace("", np.nan)
    )
    # For each series, tally up how often each tag appears under its corresponding root category.
    counts: Dict[str, Counter] = defaultdict(Counter)
    for tags, root in zip(df[tags_col], root_series):
        if pd.isna(root) or not tags:
            continue
        for tag in set(tags):
            t = tag.strip()
            if not t or t.lower() in redundant_lower:
                continue
            counts[root][t] += 1
    # Extract the top-N tags for each root.
    rows = []
    for root, ctr in counts.items():
        for tag, cnt in ctr.most_common(top_n):
            rows.append({"root": root, "tag": tag, "count": cnt})

    top10 = (
        pd.DataFrame(rows)
        .sort_values(["root", "count"], ascending=[True, False])
        .groupby("root", as_index=False)
        .head(top_n)
    )
    return top10


def get_patches_and_values(
    geo: Dict[str, Any], fred: pd.DataFrame
) -> Tuple[List[Polygon], List[int]]:
    """
    Map state count data to geographic patches from the GeoJSON.

    :param geo: mapping from the GeoJSON file
    :param fred: data to compute state counts
    :return: states and corresponding values
    """
    # Prepare data.
    raw_counts = fred["categories_list"].explode().value_counts().to_dict()
    geo_states = {feat["properties"]["name"] for feat in geo["features"]}
    state_series = {st: raw_counts.get(st, 0) for st in geo_states}
    # Build patches and values.
    patches = []
    values = []
    for feat in geo["features"]:
        name = feat["properties"]["name"]
        count = state_series.get(name, 0)
        geom = feat["geometry"]
        rings = (
            geom["coordinates"]
            if geom["type"] == "Polygon"
            else [r for poly in geom["coordinates"] for r in poly]
        )
        for ring in rings:
            patches.append(Polygon(ring, closed=True))
            values.append(count)
    return patches, values


def categorize_tags(
    column: pd.core.series.Series, model: str, batch_size: int = 50
) -> Dict[str, str]:
    """
    Categorize tags using the fixed categorization prompt.

    :param tags: tags to assign categories
    :param model: model name for classification
    :param batch_size: number of tags per API request
    :return: mapping from tag to category
    """
    SYSTEM_PROMPT = (
        "You are an expert economist. For each input tag, "
        "assign it to one of the following broad categories: "
        "Geography, Administrative Unit, Frequency & Time, Entity / Concept, "
        "Metric / Measure, Organization / Source, Demographics & Populations, "
        "Financial Instrument, Product / Commodity, Flags & Qualifiers. "
        "Don't add any new categories other than the ones mentioned."
        "Respond in the format “<index>: <Category>” for each numbered tag"
    )
    # Extract unique tags.
    unique_tags = list({tag.strip() for tags in column.dropna() for tag in tags})
    results = {}
    # Batch tags for API calls.
    for start in range(0, len(unique_tags), batch_size):
        batch = unique_tags[start : start + batch_size]
        user = "\n".join(f"{i + 1}: {tag}" for i, tag in enumerate(batch))
        response = hopenai.get_completion(
            user, system_prompt=SYSTEM_PROMPT, model=model
        )
        # Parse each line of the response.
        for line in response.splitlines():
            m = re.match(r"(\d+): (.*)", line)
            if m:
                idx = int(m.group(1)) - 1
                results[batch[idx]] = m.group(2).strip()
    return results
