"""
InsightPilot-style LangGraph agent that orchestrates QuickInsights, MetaInsight,
and XInsight over a CSV dataset. The agent consumes a natural-language question,
iteratively decides which analytical engine to invoke, and emits a notebook with
markdown/code cells capturing the exploration.

Requires OPENAI_API_KEY when using the default ChatOpenAI backend.
"""

from __future__ import annotations

import argparse
import collections
import json
import operator
import time
from pathlib import Path
from typing import Annotated, Any, Literal, Sequence

import pandas as pd
import nbformat
from nbformat.v4 import new_markdown_cell, new_code_cell, new_notebook

from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
import re

import helpers.hdataframe as hdatafr
import helpers.hmarkdown_formatting as hmarkdo

try:
    import agentic_eda.advanced_insightpilot_recreation.qin as qin_module
except ModuleNotFoundError:  # pragma: no cover - fallback for direct script execution
    import qin as qin_module  # type: ignore

try:
    import agentic_eda.advanced_insightpilot_recreation.metain as metain_module
except ModuleNotFoundError:  # pragma: no cover
    import metain as metain_module  # type: ignore

try:
    import agentic_eda.advanced_insightpilot_recreation.xin as xin_module
except ModuleNotFoundError:  # pragma: no cover
    import xin as xin_module  # type: ignore

run_quickinsights = qin_module.run_quickinsights
load_qin_dataset = qin_module._load_dataset
InsightSubject = qin_module.InsightSubject
Insight = qin_module.Insight
generate_meta_insights = metain_module.generate_meta_insights
explain_difference = xin_module.explain_difference
Explanation = xin_module.Explanation

DEFAULT_MAX_STEPS = 10


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _dataset_brief(path: Path, max_rows: int = 5) -> str:
    df = load_qin_dataset(path)
    summary = [f"Rows: {len(df)}"]
    dimension_candidates: list[str] = []
    measure_candidates: list[str] = []
    schema_lines = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        nunique = df[col].nunique(dropna=True)
        schema_lines.append(f"- {col}: {dtype}, unique={nunique}")
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            measure_candidates.append(col)
        else:
            dimension_candidates.append(col)
    preview = df.head(max_rows).to_markdown(index=False)
    return (
        "Dataset summary:\n"
        + "\n".join(summary)
        + "\nCandidate dimensions: "
        + (", ".join(dimension_candidates[:15]) or "(none detected)")
        + "\nCandidate measures: "
        + (", ".join(measure_candidates[:15]) or "(none detected)")
        + "\nColumns:\n"
        + "\n".join(schema_lines)
        + "\nSample rows:\n"
        + preview
    )


def _cells_to_nb(cells: list[dict[str, Any]], path: Path) -> None:
    nb = new_notebook()
    for cell in cells:
        if cell["type"] == "markdown":
            nb.cells.append(new_markdown_cell(cell["source"]))
        elif cell["type"] == "code":
            nb.cells.append(new_code_cell(cell["source"]))
    nbformat.write(nb, path)


def _resolve_column_name(df: pd.DataFrame, name: str | None) -> str | None:
    if name is None:
        return None
    if name in df.columns:
        return name
    sanitized = re.sub(r"[^a-z0-9]", "", name.lower())
    mapping: dict[str, str] = {}
    for col in df.columns:
        key = re.sub(r"[^a-z0-9]", "", col.lower())
        mapping.setdefault(key, col)
    return mapping.get(sanitized)


def _ensure_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Enrich the dataframe with basic temporal features (Year, Month, Quarter, Date, Hour)
    when a datetime-like column is present but those columns are absent.
    """
    required = ("Year", "Month", "Quarter", "Date", "Hour")
    if all(column in df.columns for column in required):
        return df

    candidate = None
    for col in df.columns:
        lower = col.lower()
        if any(token in lower for token in ("date", "time", "timestamp")):
            candidate = col
            break
    if candidate is None:
        return df

    parsed = None
    series = df[candidate]
    if not pd.api.types.is_datetime64_any_dtype(series):
        for dayfirst in (True, False):
            parsed_candidate = pd.to_datetime(series, errors="coerce", dayfirst=dayfirst, infer_datetime_format=True)
            if parsed_candidate.notna().mean() >= 0.5:
                parsed = parsed_candidate
                break
    else:
        parsed = series

    if parsed is None or parsed.notna().mean() < 0.5:
        return df

    df = df.copy()
    df[candidate] = parsed
    if "Year" not in df.columns:
        df["Year"] = pd.Categorical(parsed.dt.year.astype("Int64").astype(str))
    if "Month" not in df.columns:
        df["Month"] = pd.Categorical(parsed.dt.month.astype("Int64").astype(str))
    if "Quarter" not in df.columns:
        df["Quarter"] = pd.Categorical(parsed.dt.quarter.astype("Int64").astype(str))
    if "Date" not in df.columns:
        df["Date"] = pd.Categorical(parsed.dt.date.astype(str))
    if "Hour" not in df.columns:
        df["Hour"] = pd.Categorical(parsed.dt.hour.astype("Int64").astype(str))
    return df


def _format_insight_entry(ins: dict[str, Any]) -> str:
    if "insight_type" in ins:
        subject = ins.get("subject", {})
        measure = subject.get("measure", "")
        breakdown = subject.get("breakdown", "")
        highlight = ins.get("highlight", {})
        top_cat = highlight.get("top_category") or highlight.get("outlier_category")
        category_mean = highlight.get("category_mean") or highlight.get("band_mean_kw") or highlight.get("mean")
        global_mean = highlight.get("global_mean") or highlight.get("threshold")
        if highlight.get("description"):
            return highlight["description"]
        measure_label = measure or "(measure)"
        breakdown_label = breakdown or "(dimension)"
        if top_cat is not None and category_mean is not None:
            return (
                f"{measure_label} peaks when {breakdown_label} = {top_cat}, averaging {category_mean}, "
                f"versus {global_mean} overall."
            )
        summary_bits: list[str] = []
        if highlight:
            for key, value in highlight.items():
                if isinstance(value, (dict, list)):
                    continue
                summary_bits.append(f"{key}={value}")
        highlight_txt = ", ".join(summary_bits) if summary_bits else ""
        base = f"{ins.get('insight_type')} insight on {measure_label} by {breakdown_label}"
        return f"{base}: {highlight_txt}".rstrip(": ")
    if "variable" in ins and "quantitative" in ins:
        quant = ins["quantitative"]
        predicate = quant.get("predicate", "")
        responsibility = quant.get("responsibility", "")
        delta = quant.get("delta_effect", {})
        overall = delta.get("overall_difference")
        conditioned = delta.get("conditioned_difference")
        return (
            f"Conditioning on {predicate} explains the gap: responsibility ≈ {responsibility}; "
            f"difference shrinks from {overall} to {conditioned}."
        )
    return str(ins)


def _format_explanation_entry(exp: dict[str, Any]) -> str:
    quant = exp.get("quantitative", {})
    predicate = quant.get("predicate", "")
    responsibility = quant.get("responsibility")
    delta = quant.get("delta_effect", {})
    overall = delta.get("overall_difference")
    conditioned = delta.get("conditioned_difference")
    responsibility_txt = f" (resp≈{responsibility})" if responsibility is not None else ""
    delta_txt = (
        f" shrinking the difference from {overall} to {conditioned}"
        if overall is not None and conditioned is not None
        else ""
    )
    return f"conditioning on {predicate}{delta_txt}{responsibility_txt}".strip()


def _compose_report(
    insights: list[dict[str, Any]],
    explanations: list[dict[str, Any]] | None = None,
) -> str:
    if not insights:
        return "No insights were generated."
    lines = [_format_insight_entry(ins) for ins in insights]
    if explanations:
        lines.append("Supporting explanations:")
        for exp in explanations:
            kind = "causal" if exp.get("kind") == "causal" else "associated"
            variable = exp.get("variable", "(unknown)")
            lines.append(f"  - ({kind}) {variable}: {_format_explanation_entry(exp)}")
    intro = "Key findings from the automated exploration:"
    return intro + "\n" + "\n".join(f"- {line}" for line in lines)


def _insight_description(ins: dict[str, Any]) -> str:
    highlight = ins.get("highlight")
    if isinstance(highlight, dict) and highlight.get("description"):
        return str(highlight["description"])
    text = ins.get("text")
    if isinstance(text, str) and text.strip():
        return text.strip()
    try:
        desc = _format_insight_entry(ins)
    except Exception:
        desc = ""
    desc = (desc or "").strip()
    if desc:
        return desc
    subject = ins.get("subject") or {}
    measure = subject.get("measure")
    breakdown = subject.get("breakdown")
    insight_type = ins.get("insight_type") or "Insight"
    bits = [insight_type]
    if measure:
        bits.append(str(measure))
    if breakdown:
        bits.append(f"by {breakdown}")
    highlight = ins.get("highlight")
    if isinstance(highlight, dict) and highlight:
        hl_bits = []
        for key, value in highlight.items():
            if isinstance(value, (dict, list)):
                continue
            hl_bits.append(f"{key}={value}")
        if hl_bits:
            bits.append("(" + ", ".join(hl_bits) + ")")
    return " ".join(bits) or "Insight"


def _build_measure_visual_cells(
    insight: dict[str, Any],
    dataset_path: str,
) -> list[dict[str, Any]]:
    subject = insight.get("subject") or {}
    measure = subject.get("measure")
    breakdown = subject.get("breakdown")
    if not measure or not breakdown:
        return []
    subspace = subject.get("subspace") or {}
    insight_id = insight.get("insight_id")
    title = f"Insight {insight_id}: {measure} by {breakdown}"
    md = {
        "type": "markdown",
        "source": f"#### Visualization · Insight {insight_id}\n{_insight_description(insight)}",
    }
    dataset_literal = json.dumps(str(dataset_path))
    measure_literal = json.dumps(measure)
    breakdown_literal = json.dumps(breakdown)
    title_literal = json.dumps(title)
    code_lines = [
        "import pandas as pd",
        "import plotly.express as px",
        "from pathlib import Path",
        "from qin import _load_dataset as load_dataset",
        f"df = load_dataset(Path({dataset_literal}))",
        "subset = df.copy()",
    ]
    for dim, value in subspace.items():
        value_literal = json.dumps(str(value))
        code_lines.append(f"if '{dim}' in subset.columns:")
        code_lines.append(f"    subset = subset[subset['{dim}'].astype(str) == {value_literal}]")
    code_lines.extend(
        [
            "subset = subset.dropna(subset=[" + breakdown_literal + "])",
            f"numeric_measure = pd.api.types.is_numeric_dtype(subset[{measure_literal}])",
            "if numeric_measure:",
            f"    agg = subset.groupby({breakdown_literal}, dropna=False)[{measure_literal}].mean().reset_index()",
            f"    value_col = {measure_literal}",
            "else:",
            f"    agg = subset.groupby({breakdown_literal}, dropna=False).size().reset_index(name='count')",
            "    value_col = 'count'",
            "agg = agg.sort_values(value_col, ascending=False).reset_index(drop=True)",
            "agg['value_display'] = agg[value_col].round(4)",
            "fig = px.bar(",
            "    agg,",
            f"    x={breakdown_literal},",
            "    y=value_col,",
            "    text='value_display',",
            f"    title={title_literal},",
        ]
    )
    code_lines.extend(
        [
            ")",
            "fig.update_traces(textposition='outside')",
            "fig.update_layout(template='plotly_white', xaxis_title=" + breakdown_literal + ", yaxis_title=value_col)",
            "fig.show()",
            "agg",
        ]
    )
    return [md, {"type": "code", "source": "\n".join(code_lines)}]


def _build_explanation_visual_cells(
    insight: dict[str, Any],
    dataset_path: str,
) -> list[dict[str, Any]]:
    normalized = insight.get("normalized_args") or {}
    dimension = normalized.get("dimension")
    left = normalized.get("left")
    right = normalized.get("right")
    measure = normalized.get("measure")
    agg = normalized.get("agg", "avg")
    if not all([dimension, left, right, measure]):
        return []
    insight_id = insight.get("insight_id")
    md = {
        "type": "markdown",
        "source": f"#### Visualization · Insight {insight_id}\n{_insight_description(insight)}",
    }
    dataset_literal = json.dumps(str(dataset_path))
    dimension_literal = json.dumps(dimension)
    left_literal = json.dumps(str(left))
    right_literal = json.dumps(str(right))
    measure_literal = json.dumps(measure)
    agg_literal = json.dumps(str(agg))
    title = f"Insight {insight_id}: {measure} comparison ({left} vs {right})"
    title_literal = json.dumps(title)
    code_lines = [
        "import pandas as pd",
        "import plotly.express as px",
        "from pathlib import Path",
        "from qin import _load_dataset as load_dataset",
        f"df = load_dataset(Path({dataset_literal}))",
        "df = df.copy()",
    ]
    for step in insight.get("prep_steps", []):
        kind = step.get("kind")
        target = step.get("target")
        source = step.get("source")
        if not target or not source:
            continue
        target_lit = json.dumps(target)
        source_lit = json.dumps(source)
        if kind == "qcut":
            labels = step.get("labels", ["q1", "q2", "q3", "q4"])
            labels_literal = json.dumps(labels)
            code_lines.append(f"if {target_lit} not in df.columns:")
            code_lines.append(
                f"    df[{target_lit}] = pd.qcut(df[{source_lit}], q={len(labels)}, labels={labels_literal}, duplicates='drop')"
            )
        elif kind == "bucket":
            match_value = json.dumps(str(step.get("match_value", "")))
            code_lines.append(f"if {target_lit} not in df.columns:")
            code_lines.append(
                f"    df[{target_lit}] = df[{source_lit}].astype(str).apply(lambda v: 'target' if v == {match_value} else 'other')"
            )
        elif kind == "datetime_year":
            year = step.get("year")
            code_lines.append(f"if {target_lit} not in df.columns:")
            code_lines.append(f"    col = pd.to_datetime(df[{source_lit}], errors='coerce')")
            code_lines.append(
                f"    df[{target_lit}] = col.dt.year.apply(lambda y: 'target' if y == {year} else 'other')"
            )
    code_lines.extend(
        [
            f"dimension = {dimension_literal}",
            f"left_val = {left_literal}",
            f"right_val = {right_literal}",
            f"measure_col = {measure_literal}",
            f"agg_key = {agg_literal}",
            "agg_map = {'avg': 'mean', 'mean': 'mean', 'sum': 'sum', 'median': 'median', 'count': 'count'}",
            "func_name = agg_map.get(agg_key.lower(), 'mean')",
            "def _compute(series, func):",
            "    if func == 'count':",
            "        return float(series.count())",
            "    return float(getattr(series, func)())",
            "left_series = df[df[dimension].astype(str) == str(left_val)][measure_col].dropna()",
            "right_series = df[df[dimension].astype(str) == str(right_val)][measure_col].dropna()",
            "summary = pd.DataFrame({",
            "    dimension: [str(left_val), str(right_val)],",
            "    'value': [_compute(left_series, func_name), _compute(right_series, func_name)]",
            "})",
            "fig = px.bar(",
            "    summary,",
            "    x=dimension,",
            "    y='value',",
            "    text='value',",
            f"    title={title_literal},",
            "    labels={'value': measure_col},",
        ]
    )
    code_lines.extend(
        [
            ")",
            "fig.update_traces(texttemplate='%{text:.4g}', textposition='outside', marker_color=['#4C72B0', '#C44E52'])",
            "fig.update_layout(template='plotly_white', yaxis_title=measure_col)",
            "fig.show()",
            "summary",
        ]
    )
    return [md, {"type": "code", "source": "\n".join(code_lines)}]


def _visual_cells_for_insight(insight: dict[str, Any], dataset_path: str) -> list[dict[str, Any]]:
    if insight.get("normalized_args"):
        return _build_explanation_visual_cells(insight, dataset_path)
    subject = insight.get("subject") or {}
    if subject.get("measure") and subject.get("breakdown"):
        return _build_measure_visual_cells(insight, dataset_path)
    return []


def _question_tokens(question: str) -> set[str]:
    tokens = set()
    for raw in re.split(r"[^a-z0-9]+", question.lower()):
        if len(raw) >= 3:
            tokens.add(raw)
    return tokens


def _column_tokens(name: str) -> set[str]:
    spaced = re.sub(r"(?<=[a-z0-9])([A-Z])", r" \1", name)
    return _question_tokens(spaced)


def _auto_detect_columns(
    df: pd.DataFrame,
    question: str,
    measure_hint: str | None,
    breakdown_hint: str | None,
) -> tuple[str | None, str | None]:
    question_key = re.sub(r"[^a-z0-9]", "", question.lower())
    question_tokens = _question_tokens(question)
    if not question_key and not question_tokens:
        return measure_hint, breakdown_hint

    if not measure_hint:
        best_col = None
        best_score = 0
        for col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
            col_tokens = _column_tokens(col)
            score = len(col_tokens & question_tokens)
            bare_col = col.split("(")[0].strip()
            bare_key = re.sub(r"[^a-z0-9]", "", bare_col.lower())
            if bare_key and bare_key in question_key:
                score += 2
            if score > best_score:
                best_col = col
                best_score = score
        if best_col:
            measure_hint = best_col
    if not measure_hint and question_key:
        for col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
            bare_col = col.split("(")[0].strip()
            col_key = re.sub(r"[^a-z0-9]", "", bare_col.lower())
            if col_key and col_key in question_key:
                measure_hint = col
                break

    if not breakdown_hint:
        best_col = None
        best_score = 0
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                continue
            col_tokens = _column_tokens(col)
            score = len(col_tokens & question_tokens)
            bare_col = col.split("(")[0].strip()
            bare_key = re.sub(r"[^a-z0-9]", "", bare_col.lower())
            if bare_key and bare_key in question_key:
                score += 2
            if score > best_score:
                best_col = col
                best_score = score
        if best_col:
            breakdown_hint = best_col
    if not breakdown_hint and question_key:
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                continue
            bare_col = col.split("(")[0].strip()
            col_key = re.sub(r"[^a-z0-9]", "", bare_col.lower())
            if col_key and col_key in question_key:
                breakdown_hint = col
                break

    return measure_hint, breakdown_hint


def _insight_relevance(
    insight: Insight,
    tokens: set[str],
    measure_hint: str | None,
    breakdown_hint: str | None,
) -> float:
    score = 0.0
    measure = insight.subject.measure.lower()
    breakdown = insight.subject.breakdown.lower()
    if measure_hint and measure_hint.lower() in measure:
        score += 2.0
    if breakdown_hint and breakdown_hint.lower() in breakdown:
        score += 1.0
    highlight_blob = json.dumps(insight.highlight, default=str).lower()
    for token in tokens:
        if token in measure:
            score += 1.0
        if token in breakdown:
            score += 0.6
        if token in highlight_blob:
            score += 0.4
    return score


def _normalize_insight(raw: dict[str, Any]) -> dict[str, Any]:
    entry = dict(raw)
    subject = entry.get("subject")
    if isinstance(subject, dict):
        subject_copy = dict(subject)
        subspace = subject_copy.get("subspace")
        if isinstance(subspace, dict):
            subject_copy["subspace"] = {
                key: val if isinstance(val, (str, int, float, bool, type(None))) else str(val)
                for key, val in subspace.items()
            }
        entry["subject"] = subject_copy
    highlight = entry.get("highlight")
    if isinstance(highlight, dict):
        highlight = dict(highlight)
        for key in ("top_category", "outlier_category"):
            if key in highlight and not isinstance(highlight[key], (str, int, float, bool, type(None))):
                highlight[key] = str(highlight[key])
        for key, value in list(highlight.items()):
            if isinstance(value, dict):
                highlight[key] = {
                    k: v if isinstance(v, (str, int, float, bool, type(None))) else str(v)
                    for k, v in value.items()
                }
            elif isinstance(value, list):
                highlight[key] = [
                    item if isinstance(item, (str, int, float, bool, type(None))) else str(item)
                    for item in value
                ]
            elif not isinstance(value, (str, int, float, bool, type(None))):
                highlight[key] = str(value)
        entry["highlight"] = highlight
    entry.setdefault("insight_type", entry.get("insight_type", "Insight"))
    return entry


def _prepare_explanations(
    df: pd.DataFrame,
    dimension: str,
    left: str,
    right: str | None,
    measure: str,
    agg: str = "avg",
) -> tuple[list[Explanation], str, str, list[dict[str, Any]], str, str]:
    df_work = df.copy()
    resolved_measure = _resolve_column_name(df_work, measure) or measure
    resolved_dimension = _resolve_column_name(df_work, dimension) or dimension

    if resolved_dimension not in df_work.columns:
        raise ValueError(f"Dimension '{dimension}' not found.")

    prep_steps: list[dict[str, Any]] = []

    # Datetime columns: if the user references a year, bucket that year vs others.
    left_str = str(left)
    if left_str.replace(".", "", 1).isdigit():
        try:
            left_numeric = int(float(left_str))
        except Exception:
            left_numeric = None
    else:
        left_numeric = None

    if pd.api.types.is_datetime64_any_dtype(df_work[resolved_dimension]) and left_numeric is not None:
        target_year = left_numeric
        group_col = f"{resolved_dimension}_year_group"
        df_work[group_col] = df_work[resolved_dimension].dt.year.apply(
            lambda y: "target" if y == target_year else "other"
        )
        prep_steps.append(
            {
                "kind": "datetime_year",
                "source": resolved_dimension,
                "target": group_col,
                "year": target_year,
            }
        )
        resolved_dimension = group_col
        left, right = "target", "other"

    if not right:
        right = "other"

    # Handle "rest/others/overall" by bucketing into target vs other categories.
    unique_vals = set(map(str, df_work[resolved_dimension].dropna().unique()))
    if str(left) in unique_vals and str(right).lower() in {"overall", "others", "rest", "remaining", "other"}:
        bucket_col = f"{resolved_dimension}_group"
        source_col = resolved_dimension
        df_work[bucket_col] = df_work[resolved_dimension].astype(str).apply(
            lambda v: "target" if v == str(left) else "other"
        )
        prep_steps.append(
            {
                "kind": "bucket",
                "source": source_col,
                "target": bucket_col,
                "match_value": str(left),
            }
        )
        resolved_dimension = bucket_col
        left, right = "target", "other"

    # Numeric dimensions: compare top vs bottom quartiles.
    if pd.api.types.is_numeric_dtype(df_work[resolved_dimension]):
        source_col = resolved_dimension
        binned_dim = f"{resolved_dimension}_binned"
        labels = ["q1", "q2", "q3", "q4"]
        df_work[binned_dim] = pd.qcut(
            df_work[resolved_dimension], q=4, labels=labels, duplicates="drop"
        )
        prep_steps.append(
            {
                "kind": "qcut",
                "source": source_col,
                "target": binned_dim,
                "labels": labels,
            }
        )
        resolved_dimension = binned_dim
        left, right = "q4", "q1"

    explanations = explain_difference(df_work, resolved_dimension, left, right, resolved_measure, agg=agg)
    return explanations, resolved_dimension, resolved_measure, prep_steps, str(left), str(right)


# ---------------------------------------------------------------------------
# Tool input schemas
# ---------------------------------------------------------------------------

class QuickInsightsInput(BaseModel):
    measure: str | None = Field(
        default=None,
        description="Optional measure to prioritise (e.g. 'Sales').",
    )
    breakdown: str | None = Field(
        default=None,
        description="Optional breakdown dimension to prioritise (e.g. 'Region').",
    )
    filters: dict[str, str] | None = Field(
        default=None,
        description="Optional equality filters expressed as {dimension: value}.",
    )
    max_insights: int = Field(default=5, ge=1, le=20)


class MetaInsightsInput(BaseModel):
    measure: str | None = Field(default=None)
    breakdown: str | None = Field(default=None)
    tau: float = Field(default=0.5, ge=0.1, le=0.9)
    mode: Literal["summarize", "compare"] = Field(
        default="summarize",
        description="Use 'summarize' to confirm a common pattern or 'compare' to highlight differences across peer groups.",
    )


class XInsightInput(BaseModel):
    dimension: str
    left: str
    right: str
    measure: str
    agg: str = Field(default="avg")


# ---------------------------------------------------------------------------
# State definition
# ---------------------------------------------------------------------------


class PilotState(TypedDict):
    dataset_path: str
    question: str
    insights: Annotated[list[dict[str, Any]], operator.add]
    notebook_cells: Annotated[list[dict[str, Any]], operator.add]
    final_report: str | None
    status: Literal["ongoing", "done"]
    step_count: int
    max_steps: int
    failed_attempts: Annotated[list[str], operator.add]
    trace: Annotated[list[dict[str, Any]], operator.add]
    messages: Annotated[Sequence, add_messages]
    meta_done: bool
    thought_log: Annotated[list[str], operator.add]


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------

def _load_df(path: str) -> pd.DataFrame:
    return load_qin_dataset(Path(path))


@tool("quick_insights_tool", args_schema=QuickInsightsInput)
def quick_insights_tool(
    dataset_path: str,
    measure: str | None = None,
    breakdown: str | None = None,
    filters: dict[str, str] | None = None,
    max_insights: int = 5,
    question: str | None = None,
) -> str:
    """Mine high-impact basic insights aligned with the user question."""
    df = _load_df(dataset_path)
    df_view = df
    print(f"[InsightPilot] quick_insights_tool called on {dataset_path} shape={df_view.shape}")
    applied_filters: dict[str, str] = {}
    if filters:
        df_view = df_view.copy()
        mask_df = _ensure_temporal_features(df_view.copy())
        filter_spec: dict[str, tuple[str, ...]] = {}
        for raw_dim, raw_val in filters.items():
            resolved_dim = _resolve_column_name(df_view, raw_dim)
            if not resolved_dim:
                resolved_dim = _resolve_column_name(mask_df, raw_dim)
            if not resolved_dim or resolved_dim not in mask_df.columns:
                return json.dumps({
                    "error": f"Filter dimension '{raw_dim}' not recognised.",
                    "available_dimensions": list(df.columns),
                })
            mask_df[resolved_dim] = mask_df[resolved_dim].astype(str)
            filter_spec[resolved_dim] = (str(raw_val),)
            applied_filters[raw_dim] = str(raw_val)
        info = collections.OrderedDict()
        filtered_mask_df = hdatafr.filter_data_by_values(mask_df, filter_spec, mode="and", info=info)
        if filtered_mask_df.empty:
            return json.dumps({
                "error": "No rows remain after applying the requested filters.",
                "filters": applied_filters,
            })
        df_view = df_view.loc[filtered_mask_df.index]

    resolved_measure = _resolve_column_name(df_view, measure) if measure else None
    resolved_breakdown = _resolve_column_name(df_view, breakdown) if breakdown else None

    # If the dataset is wide, keep the most variant numeric measures to prevent blow-ups.
    numeric_cols = df_view.select_dtypes(include="number").columns.tolist()
    preserved_measures: set[str] = set(filter(None, [resolved_measure]))
    if len(numeric_cols) > 60:
        variances = df_view[numeric_cols].var().sort_values(ascending=False)
        keep = set(variances.head(60).index) | preserved_measures
        drop = [col for col in numeric_cols if col not in keep]
        if drop:
            df_view = df_view.drop(columns=drop)
            print(f"[InsightPilot] quick_insights_tool dropped {len(drop)} low-variance measures; remaining columns={df_view.shape[1]}")

    # For very tall datasets sample a stable subset to keep QuickInsights tractable.
    if len(df_view) > 2000:
        df_view = df_view.sample(2000, random_state=0)
        print(f"[InsightPilot] quick_insights_tool sampled rows; new shape={df_view.shape}")

    auto_measure, auto_breakdown = _auto_detect_columns(
        df_view,
        question or "",
        resolved_measure,
        resolved_breakdown,
    )
    resolved_measure = resolved_measure or auto_measure
    resolved_breakdown = resolved_breakdown or auto_breakdown

    # Mine a generous pool before ranking for relevance.
    pool_size = max(max_insights * 3, 10)
    candidates = run_quickinsights(df_view, max_insights=pool_size)

    if not candidates:
        print("[InsightPilot] quick_insights_tool -> no candidates found")
        return json.dumps({"error": "QuickInsights could not surface any insights for the current scope."})

    tokens = _question_tokens(question or "")
    ranked: list[tuple[float, Insight]] = []
    for ins in candidates:
        if resolved_measure and ins.subject.measure != resolved_measure:
            continue
        if resolved_breakdown and ins.subject.breakdown != resolved_breakdown:
            continue
        rel_bonus = _insight_relevance(ins, tokens, resolved_measure, resolved_breakdown)
        ranked.append((ins.score + rel_bonus, ins))

    if not ranked:
        ranked = [
            (ins.score + _insight_relevance(ins, tokens, resolved_measure, resolved_breakdown), ins)
            for ins in candidates
        ]

    ranked.sort(key=lambda pair: pair[0], reverse=True)
    selected = [ins for _, ins in ranked[:max_insights]]

    summary_lines = []
    notebook_cells = []
    auto_explanations: list[dict[str, Any]] = []
    filter_suffix = ""
    if applied_filters:
        filter_suffix = " | filters: " + ", ".join(f"{k}={v}" for k, v in applied_filters.items())

    for idx, ins in enumerate(selected, start=1):
        highlight = ins.highlight or {}
        top_cat = highlight.get("top_category") or highlight.get("outlier_category")
        top_desc = ""
        if top_cat is not None:
            top_desc = f"; key category={top_cat}"
        line = (
            f"{idx}. [{ins.insight_type}] {ins.subject.measure} by {ins.subject.breakdown}"
            f" (impact={ins.impact}, score={ins.score}){top_desc}{filter_suffix}"
        )
        summary_lines.append(line)

        if top_cat is not None:
            try:
                (
                    explanations,
                    dim_used,
                    meas_used,
                    prep_steps,
                    norm_left,
                    norm_right,
                ) = _prepare_explanations(
                    df_view,
                    ins.subject.breakdown,
                    str(top_cat),
                    "other",
                    ins.subject.measure,
                )
            except Exception:
                explanations = []
                prep_steps = []
                norm_left = str(top_cat)
                norm_right = "other"
            for explanation in explanations[:2]:
                entry = explanation.__dict__
                entry["subject"] = {"subspace": applied_filters, "breakdown": dim_used, "measure": meas_used}
                if prep_steps:
                    entry["prep_steps"] = prep_steps
                entry.setdefault("normalized_args", {"dimension": dim_used, "left": norm_left, "right": norm_right})
                entry.setdefault("insight_type", "AutoExplain")
                entry.setdefault("supporting_insight_id", idx)
                auto_explanations.append(entry)

    notebook_cells.append(
        {
            "type": "markdown",
            "source": "### QuickInsights\n" + "\n".join(f"- {line}" for line in summary_lines),
        }
    )
    insights_payload: list[dict[str, Any]] = []
    for ins in selected:
        ins_record = {
            "insight_type": ins.insight_type,
            "impact": ins.impact,
            "significance": ins.significance,
            "score": ins.score,
            "highlight": dict(ins.highlight or {}),
            "subject": {
                "subspace": {k: (v if isinstance(v, (str, int, float, bool, type(None))) else str(v)) for k, v in ins.subject.subspace.items()},
                "breakdown": ins.subject.breakdown,
                "measure": ins.subject.measure,
            },
        }
        insights_payload.append(_normalize_insight(ins_record))

    payload = {
        "insights": insights_payload,
        "explanations": auto_explanations,
        "notebook_cells": notebook_cells,
        "summary": "\n".join(summary_lines),
        "applied_filters": applied_filters,
    }
    return json.dumps(payload, default=str)


@tool("meta_insights_tool", args_schema=MetaInsightsInput)
def meta_insights_tool(
    dataset_path: str,
    measure: str | None = None,
    breakdown: str | None = None,
    tau: float = 0.5,
    mode: str = "summarize",
) -> str:
    """Summarise homogeneous scopes into commonnesses and exceptions."""
    df = _load_df(dataset_path)
    mode_clean = "compare" if str(mode).lower().startswith("comp") else "summarize"
    print(
        f"[InsightPilot] meta_insights_tool called mode={mode_clean} measure={measure} breakdown={breakdown} "
        f"tau={tau} shape={df.shape}"
    )
    resolved_measure = _resolve_column_name(df, measure)
    resolved_breakdown = _resolve_column_name(df, breakdown)
    quick = run_quickinsights(df, max_insights=25)
    if resolved_measure and resolved_measure in df.columns:
        candidate_breakdown = resolved_breakdown
        if not candidate_breakdown:
            for col in ("Year", "Quarter", "Month", "Date"):
                if col in df.columns:
                    candidate_breakdown = col
                    break
        if candidate_breakdown and candidate_breakdown in df.columns:
            has_scope = any(
                ins.subject.measure == resolved_measure and ins.subject.breakdown == candidate_breakdown
                for ins in quick
            )
            if not has_scope:
                quick.append(
                    Insight(
                        subject=InsightSubject(subspace={}, breakdown=candidate_breakdown, measure=resolved_measure),
                        insight_type="Seed",
                        impact=0.0,
                        significance=0.0,
                        score=0.0,
                        highlight={},
                    )
                )
                resolved_breakdown = candidate_breakdown
    if resolved_measure:
        quick = [ins for ins in quick if ins.subject.measure == resolved_measure]
    metas = generate_meta_insights(df, quick, tau=tau)
    if not metas and tau > 0.15:
        metas = generate_meta_insights(df, quick, tau=max(0.1, tau * 0.5))

    metas_filtered = metas
    if resolved_measure:
        metas_filtered = [m for m in metas_filtered if m.homogeneous_scope["root_scope"].get("measure") == resolved_measure]
    if resolved_breakdown:
        metas_filtered = [m for m in metas_filtered if m.homogeneous_scope["root_scope"].get("breakdown") == resolved_breakdown]

    if not metas_filtered and metas:
        metas_filtered = metas

    metas_filtered = metas_filtered[:3]
    md_lines: list[str] = []
    entries: list[dict[str, Any]] = []
    for meta in metas_filtered:
        scope = meta.homogeneous_scope
        root = scope["root_scope"]
        measure_name = root.get("measure", "")
        breakdown_name = root.get("breakdown", "")
        mode_label = "Comparison" if mode_clean == "compare" else "Summary"
        description = f"[{mode_label}] Exploring {measure_name} by {breakdown_name}."
        if meta.commonnesses:
            common = meta.commonnesses[0]
            members = ", ".join(
                str(m.get(breakdown_name, m))
                for m in common.members[:5]
            )
            highlight = common.highlight
            pattern_name = highlight.get("pattern") or common.type
            detail_bits: list[str] = []
            if "direction" in highlight:
                detail_bits.append(f"direction={highlight['direction']}")
            if "peak_category" in highlight:
                detail_bits.append(f"peak={highlight['peak_category']}")
            if "support_categories" in highlight:
                detail_bits.append(f"support≈{len(highlight['support_categories'])} groups")
            detail_txt = f" ({', '.join(detail_bits)})" if detail_bits else ""
            description += (
                f" Commonness: {pattern_name} covering {common.support_ratio * 100:.1f}% of "
                f"{breakdown_name} values; representative members: {members}.{detail_txt}"
            )
        highlight_change = meta.exceptions.get("HighlightChange") or []
        type_change = meta.exceptions.get("TypeChange") or []
        no_pattern = meta.exceptions.get("NoPattern") or []
        if highlight_change:
            ex_members = ", ".join(
                str(item.get(breakdown_name, item))
                for item in highlight_change[:3]
            )
            description += f" Highlight-change exceptions: {ex_members}."
        if type_change:
            ex_members = ", ".join(
                str(item.get(breakdown_name, item))
                for item in type_change[:3]
            )
            description += f" Type-change exceptions: {ex_members}."
        if no_pattern:
            ex_members = ", ".join(
                str(item.get(breakdown_name, item))
                for item in no_pattern[:3]
            )
            description += f" No-pattern cases: {ex_members}."
        description = hmarkdo.md_clean_up(description)
        md_lines.append(f"*Scope:* measure={measure_name}, breakdown={breakdown_name}\n  - {description}")
        entries.append(
            {
                "insight_type": "MetaInsight",
                "subject": root,
                "highlight": {"description": description},
                "mode": mode_clean,
            }
        )
    if not md_lines:
        detail = []
        if resolved_measure:
            detail.append(f"measure={resolved_measure}")
        if resolved_breakdown:
            detail.append(f"breakdown={resolved_breakdown}")
        detail.append(f"tau={tau}")
        md_lines.append("No MetaInsights discovered at the requested granularity (" + ", ".join(detail) + ").")
    md_lines = hmarkdo.remove_empty_lines_from_markdown(md_lines)
    cell = {
        "type": "markdown",
        "source": "### MetaInsights\n" + "\n".join(md_lines),
    }
    payload = {
        "meta_insights": entries,
        "notebook_cells": [cell],
        "summary": "\n".join(md_lines),
    }
    return json.dumps(payload)


@tool("xinsight_tool", args_schema=XInsightInput)
def xinsight_tool(
    dataset_path: str,
    dimension: str,
    left: str,
    right: str,
    measure: str,
    agg: str = "avg",
) -> str:
    """Explain a Why Query via responsibility-style predicates."""
    print(
        f"[InsightPilot] xinsight_tool called dimension={dimension} left={left} right={right} measure={measure} agg={agg}"
    )
    try:
        base_df = _load_df(dataset_path)
        explanations, resolved_dimension, resolved_measure, prep_steps, norm_left, norm_right = _prepare_explanations(
            base_df, dimension, left, right, measure, agg=agg
        )
    except ValueError as e:
        available = []
        df = _load_df(dataset_path)
        resolved_dimension = _resolve_column_name(df, dimension) or dimension
        if resolved_dimension in df.columns:
            sample_vals = df[resolved_dimension].dropna().unique()
            available = [str(v) for v in sample_vals[:10]]
        return json.dumps({
            "error": str(e),
            "dimension": resolved_dimension,
            "left": left,
            "right": right,
            "available_values_sample": available,
        })

    md_lines = [
        f"*Overall difference on {resolved_measure} ({agg}) between {resolved_dimension}={norm_left} and {resolved_dimension}={norm_right}*"
    ]
    for exp in explanations:
        md_lines.append(f"- ({exp.kind}) {exp.variable}: {exp.qualitative} [resp={exp.quantitative['responsibility']}]")

    enriched_explanations = []
    for exp in explanations:
        data = exp.__dict__.copy()
        data["prep_steps"] = prep_steps
        data["normalized_args"] = {
            "dimension": resolved_dimension,
            "left": norm_left,
            "right": norm_right,
            "measure": resolved_measure,
            "agg": agg,
        }
        enriched_explanations.append(data)
    payload = {
        "explanations": enriched_explanations,
        "notebook_cells": [
            {"type": "markdown", "source": "### XInsight Explanations\n" + "\n".join(md_lines)},
        ],
        "summary": "\n".join(md_lines),
    }
    return json.dumps(payload)


TOOLS = [quick_insights_tool, meta_insights_tool, xinsight_tool]


def call_tools(state: PilotState) -> dict:
    """Custom tool node that passes dataset_path to each tool call."""
    last_message = state["messages"][-1]
    tool_invocations = []
    if hasattr(last_message, "tool_calls"):
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool_to_call = next((t for t in TOOLS if t.name == tool_name), None)
            if tool_to_call:
                tool_args = tool_call["args"]
                # Invoke the tool's underlying function directly, passing the dataset_path
                extra_kwargs: dict[str, Any] = {"dataset_path": state["dataset_path"], **tool_args}
                if tool_to_call.name == "quick_insights_tool":
                    extra_kwargs.setdefault("question", state.get("question"))
                print(f"[InsightPilot] call_tools invoking {tool_name} with args={tool_args}")
                observation = tool_to_call.func(**extra_kwargs)
                tool_invocations.append(
                    ToolMessage(content=str(observation), tool_call_id=tool_call["id"])
                )
    return {"messages": tool_invocations}

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are InsightPilot, an automated EDA analyst.\n"
        "Goal: craft a coherent, reader-friendly story that answers the user's question using the InsightPilot workflow.\n"
        "Action palette:\n"
        "- quick_insights_tool (`UNDERSTAND`): surface headline patterns by measure/breakdown. Start with this unless the user forbids it, and revisit when you need fresh context.\n"
        "- meta_insights_tool (`SUMMARIZE/COMPARE`): consolidate related insights about a measure/breakdown into commonnesses and exceptions.\n"
        "- xinsight_tool (`EXPLAIN`): investigate Why-queries that compare two slices of a measure.\n"
        "Guidance:\n"
        "1. Use at most one tool per turn and justify every call. Keep cycling through understand/summarise/compare/explain actions until you have a complete mental model.\n"
        "2. Avoid retrying a tool with identical arguments after an error or empty result—pivot to a new angle instead.\n"
        "3. Track discovered insight IDs; cite them when cross-referencing evidence or selecting items for visualisation.\n"
        "4. Prefer substantive findings; skip repeating trivial facts (e.g., 'all years form a trend' without nuance).\n"
        "5. When ready to conclude, respond exactly with:\n"
        "   `FINAL_REPORT:` followed by a concise natural-language narrative that synthesises the key findings into a story.\n"
        "   On the next line add `VISUALIZE: <comma-separated insight IDs>` (or `VISUALIZE: none`) listing only the insights that need supporting charts.\n"
        "6. Do not request further tools after emitting the final report."
    )
)


def _initial_messages(state: PilotState) -> list:
    brief = _dataset_brief(Path(state["dataset_path"]))
    question = state["question"]
    return [
        SYSTEM_PROMPT,
        HumanMessage(content=f"User question: {question}\n\nDataset briefing:\n{brief}"),
    ]


def build_agent(model_name: str = "gpt-4o") -> Any:
    if model_name == "debug-fake":
        class _DebugQuickModel:
            def __init__(self) -> None:
                self._calls = 0
                self._tools = TOOLS

            def bind_tools(self, tools, parallel_tool_calls: bool = False):
                self._tools = tools
                return self

            def invoke(self, messages):
                self._calls += 1
                if self._calls == 1:
                    return AIMessage(
                        content="Probing QuickInsights for headline patterns.",
                        tool_calls=[
                            {
                                "id": "debug_call_0",
                                "name": "quick_insights_tool",
                                "args": {"max_insights": 3},
                            }
                        ],
                    )
                return AIMessage(content="FINAL_REPORT: Debug summary based on mined quick insights.")

        return _DebugQuickModel()

    return ChatOpenAI(model=model_name, temperature=0).bind_tools(
        TOOLS, parallel_tool_calls=False
    )


def llm_agent(state: PilotState, model: ChatOpenAI):
    msgs = list(state.get("messages", []))
    if not msgs:
        root_msgs = _initial_messages(state)
        msgs = root_msgs
    else:
        insights = state.get("insights", [])
        if insights:
            catalog = "\n".join(
                f"{ins.get('insight_id')}: {_format_insight_entry(ins)}"
                for ins in insights[-6:]
            )
            inventory = f"Current insight inventory (ID : description):\n{catalog}"
        else:
            inventory = "No insights collected yet."
        thoughts = state.get("thought_log", [])
        if thoughts:
            recent_thoughts = thoughts[-5:]
            thoughts_block = "Recent thought log:\n" + "\n".join(f"- {t}" for t in recent_thoughts)
        else:
            thoughts_block = "Recent thought log:\n- (empty)"
        step = state.get("step_count", 0)
        user_prompt = HumanMessage(
            content=(
                f"Step {step}. User question: {state['question']}\n"
                f"{inventory}\n"
                f"{thoughts_block}\n"
                "Pick your next action (understand/summarize/compare/explain) and explain your reasoning before any tool call."
            )
        )
        msgs = [SYSTEM_PROMPT, user_prompt, *(msgs if msgs else [])]

    print("\n[Thinking...]")
    time.sleep(5)
    ai = model.invoke(msgs)
    return {"messages": [ai]}


def _pp_trace_event(entry: dict[str, Any]) -> None:
    """Pretty-print a trace event to the console."""
    event = entry.get("event")
    if event == "llm_plan":
        plan = entry.get("plans", [])[0]
        tool = plan.get("tool")
        args = plan.get("args", {})
        arg_str = ", ".join(f"{k}='{v}'" for k, v in args.items())
        print(f"[Tool Call] PLAN: Call `{tool}` with args: {arg_str}")
    elif event == "tool_result":
        tool = entry.get("tool")
        summary = str(entry.get("summary", "")).replace('\n', ' ')
        print(f"[Tool Result] for `{tool}`: {summary}")
    elif event == "llm_final":
        summary = str(entry.get("summary", "")).replace('\n', ' ')
        print(f"[Finish] FINAL REPORT: {summary}")
    elif event == "auto_finalize":
        summary = str(entry.get("summary", "")).replace('\n', ' ')
        print(f"[Finish] AUTO-FINALIZE: {summary}")
    elif event == "llm_nudge":
        print(f"[Nudge] Invalid response detected. Asking model to retry.")


tool_node = ToolNode(TOOLS)


def observe(state: PilotState):
    updates: dict[str, Any] = {}
    step = state.get("step_count", 0) + 1
    updates["step_count"] = step
    updates.setdefault("trace", [])
    last = state["messages"][-1]
    content_text = str(last.content) if isinstance(last, (AIMessage, ToolMessage)) else ""

    def _queue_thought(text: str) -> None:
        trimmed = text.strip()
        if not trimmed:
            return
        updates.setdefault("thought_log", []).append(trimmed[:1000])

    # Comprehensive tracing and loop correction
    trace_entry = None
    if isinstance(last, AIMessage):
        tool_calls = getattr(last, "tool_calls", None)
        if tool_calls:
            plans = [{"tool": tc.get("name"), "args": tc.get("args")} for tc in tool_calls]
            trace_entry = {"step": step, "event": "llm_plan", "plans": plans}
            _queue_thought(content_text)
        elif "FINAL_REPORT:" not in content_text:
            nudge_msg = HumanMessage(content="Invalid response. You must either call one of the available tools or respond with 'FINAL_REPORT:'.")
            updates["messages"] = [nudge_msg]
            trace_entry = {"step": step, "event": "llm_nudge", "bad_response": content_text}

    if trace_entry:
        updates["trace"].append(trace_entry)
        _pp_trace_event(trace_entry)

    existing_count = len(state.get("insights", []))
    
    if isinstance(last, ToolMessage):
        try:
            payload = json.loads(last.content)
        except Exception as e:
            print(f"🚨 ERROR: Failed to parse tool output. Error: {e}")
            print(f"   Content: {last.content}")
            payload = {}

        # Find the tool name from the previous AIMessage
        tool_name = "unknown_tool"
        for msg in reversed(state["messages"]):
            if isinstance(msg, AIMessage) and msg.tool_calls:
                tool_name = msg.tool_calls[0]["name"]
                break

        new_items: list[dict[str, Any]] = []
        if not payload.get("error"):
            for key in ("insights", "meta_insights", "explanations"):
                items = payload.get(key) or []
                for raw in items:
                    entry = _normalize_insight(raw)
                    if not entry.get("insight_type"):
                        entry["insight_type"] = key.rstrip("s").title()
                    new_items.append(entry)
        
        if new_items:
            buffer = updates.setdefault("insights", [])
            base = existing_count + len(buffer)
            for offset, entry in enumerate(new_items, 1):
                entry["insight_id"] = base + offset
                entry["text"] = _format_insight_entry(entry)
            buffer.extend(new_items)
        else:
            # This was a failed or empty tool call, record it.
            updates.setdefault("failed_attempts", []).append(f"{tool_name} with args {state['messages'][-2].tool_calls[0]['args']}")

        if payload.get("notebook_cells"):
            updates.setdefault("notebook_cells", []).extend(payload["notebook_cells"])
        
        summary = payload.get("summary")
        if not summary:
            for key in ("insights", "meta_insights", "explanations"):
                if payload.get(key):
                    summary = _compose_report(payload[key][:3])
                    break
        
        trace_entry = {
            "step": step,
            "event": "tool_result",
            "tool": tool_name,
            "summary": summary,
            "raw_content": last.content,
        }
        updates["trace"].append(trace_entry)
        _pp_trace_event(trace_entry)

        if tool_name == "meta_insights_tool":
            updates["meta_done"] = True

    elif isinstance(last, AIMessage) and not getattr(last, "tool_calls", None):
        final_idx = content_text.find("FINAL_REPORT:")
        if final_idx != -1:
            reasoning = content_text[:final_idx].strip()
            if reasoning:
                _queue_thought(reasoning)
            final_block = content_text[final_idx + len("FINAL_REPORT:") :].strip()
            report_lines: list[str] = []
            visualize_ids: list[int] = []
            vis_processed = False
            for raw_line in final_block.splitlines():
                stripped = raw_line.strip()
                if stripped.lower().startswith("visualize:"):
                    vis_processed = True
                    parts = stripped.split(":", 1)
                    if len(parts) == 2:
                        for token in parts[1].split(","):
                            tok = token.strip()
                            if not tok or tok.lower() == "none":
                                continue
                            try:
                                visualize_ids.append(int(tok))
                            except ValueError:
                                continue
                    break
                else:
                    report_lines.append(raw_line)
            if not vis_processed:
                nudge_msg = HumanMessage(
                    content=(
                        "Please conclude with the required format. After `FINAL_REPORT:` include your narrative, "
                        "then add a separate line `VISUALIZE: <comma-separated insight IDs>` or `VISUALIZE: none` to "
                        "indicate which findings need supporting charts. Try again."
                    )
                )
                updates["messages"] = [nudge_msg]
                trace_entry = {
                    "step": step,
                    "event": "llm_nudge",
                    "bad_response": final_block,
                    "reason": "missing_visualize_directive",
                }
                updates["trace"].append(trace_entry)
                _pp_trace_event(trace_entry)
                return updates
            report_text = "\n".join(report_lines).strip()
            if report_text:
                report_text = hmarkdo.md_clean_up(report_text)
            updates["final_report"] = report_text
            updates["status"] = "done"
            updates.setdefault("notebook_cells", []).append(
                {"type": "markdown", "source": "### Final Report\n" + report_text}
            )
            dataset_path = state.get("dataset_path", "")
            visuals: list[dict[str, Any]] = []
            if visualize_ids:
                seen: set[int] = set()
                for vid in visualize_ids:
                    if vid in seen:
                        continue
                    seen.add(vid)
                    target = next((ins for ins in state.get("insights", []) if ins.get("insight_id") == vid), None)
                    if target:
                        visuals.extend(_visual_cells_for_insight(target, dataset_path))
            if visuals:
                updates.setdefault("notebook_cells", []).extend(visuals)
            trace_entry = {
                "step": step,
                "event": "llm_final",
                "summary": report_text,
                "visualize": visualize_ids,
            }
            updates["trace"].append(trace_entry)
            _pp_trace_event(trace_entry)

    max_steps = state.get("max_steps", 0)
    if max_steps and step >= max_steps and state["status"] != "done":
        summary = "Auto-finalized after reaching step limit.\n\n" + _compose_report(state.get("insights", [])[-5:])
        updates["final_report"] = summary
        updates["status"] = "done"
        updates.setdefault("notebook_cells", []).append(
            {"type": "markdown", "source": "### Final Report\n" + summary}
        )
        trace_entry = {"step": step, "event": "auto_finalize", "summary": summary}
        updates["trace"].append(trace_entry)
        _pp_trace_event(trace_entry)
        return updates

    return updates

def _ai_wants_tool(state: PilotState) -> bool:
    last = state["messages"][-1]
    return isinstance(last, AIMessage) and bool(getattr(last, "tool_calls", None))

def route_from_llm(state: PilotState):
    return "tools" if _ai_wants_tool(state) else "observe"

def next_step(state: PilotState):
    if state["status"] == "done":
        return "end"
    last_msg = state["messages"][-1] if state["messages"] else None
    if isinstance(last_msg, AIMessage) and getattr(last_msg, "tool_calls", None):
        return "tools"
    return "continue"

def run_insightpilot(
    dataset_path: Path,
    question: str,
    output_notebook: Path,
    model_name: str = "gpt-4o",
    max_steps: int | None = DEFAULT_MAX_STEPS,
    trace_path: Path | None = None,
) -> PilotState:
    state: PilotState = {
        "dataset_path": str(dataset_path),
        "question": question,
        "insights": [],
        "notebook_cells": [],
        "final_report": None,
        "status": "ongoing",
        "step_count": 0,
        "max_steps": max_steps or 0,
        "failed_attempts": [],
        "trace": [],
        "messages": [],
        "thought_log": [],
        "meta_done": False,
    }

    graph = StateGraph(PilotState)
    model = build_agent(model_name)
    graph.add_node("llm_agent", lambda s: llm_agent(s, model))
    graph.add_node("tools", call_tools)
    graph.add_node("observe", observe)

    graph.add_edge(START, "llm_agent")
    graph.add_conditional_edges("llm_agent", route_from_llm, {"tools": "tools", "observe": "observe"})
    graph.add_edge("tools", "observe")
    graph.add_conditional_edges("observe", next_step, {"continue": "llm_agent", "tools": "tools", "end": END})

    app = graph.compile()
    if max_steps:
        base_steps = max_steps
        recursion_limit = max(40, base_steps * 4)
    else:
        recursion_limit = 500
    final_state: PilotState = app.invoke(state, config={"recursion_limit": recursion_limit})

    if final_state["notebook_cells"]:
        _cells_to_nb(final_state["notebook_cells"], output_notebook)

    if trace_path:
        lines = [json.dumps(entry) for entry in final_state.get("trace", [])]
        trace_path.write_text("\n".join(lines))

    return final_state


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run InsightPilot agent on a CSV.")
    parser.add_argument("--path", type=Path, required=True, help="Path to CSV dataset.")
    parser.add_argument("--question", required=True, help="EDA question to explore.")
    parser.add_argument("--output", type=Path, required=True, help="Notebook path to write.")
    parser.add_argument("--model", default="gpt-4o", help="OpenAI chat model name.")
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS, help="Maximum agent steps before auto-finalising (0 disables).")
    parser.add_argument("--trace", type=Path, default=None, help="Path to save execution trace.")
    args = parser.parse_args(argv)

    state = run_insightpilot(
        args.path,
        args.question,
        args.output,
        args.model,
        max_steps=None if args.max_steps == 0 else args.max_steps,
        trace_path=args.trace,
    )
    print("\n\n---\nFinal report:\n", state.get("final_report"))
    print(f"Notebook written to {args.output}")


if __name__ == "__main__":
    main()
