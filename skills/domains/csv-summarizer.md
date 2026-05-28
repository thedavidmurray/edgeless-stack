---

name: csv-data-summarizer
title: CSV Data Summarizer
description: >
  Analyzes any CSV file and immediately produces a full report: column-type
  detection, summary statistics, missing-value audit, and matplotlib/seaborn
  visualizations — all in one shot, no follow-up questions.
version: 2.2.0
dependencies:
  - python 3.8+
  - pandas 2.0.0+
  - matplotlib 3.7.0+
  - seaborn 0.12.0+
tags:
  - csv
  - data-analysis
  - pandas
  - matplotlib
  - seaborn
  - statistics
  - visualization
metadata:
  tier: task-specific
  domain: knowledge
when_to_apply: >
  When summarizing or analyzing tabular CSV data.
---
# CSV Data Summarizer

A Claude Code skill that turns any CSV file into a structured analysis report
with statistics and visualizations — automatically, without asking the user
what they want.

---

## Trigger Phrases

Apply this skill whenever the user:

- Uploads or references a `.csv` file
- Says "summarize", "analyze", "explore", or "visualize" alongside tabular data
- Asks for "insights", "statistics", or "trends" from a file
- Drops a CSV path into the conversation with no other instruction

---

## CRITICAL BEHAVIOR: Act Immediately

**DO NOT ask the user what they want to do with the data.**
**DO NOT offer a menu of options.**
**DO NOT say "What would you like me to help you with?"**

**IMMEDIATELY:**
1. Run the full analysis script below
2. Generate ALL relevant visualizations
3. Present the complete markdown report
4. Zero questions, zero options, zero waiting

---

## Implementation

When this skill triggers, execute the following Python script.  
Replace `CSV_PATH` with the actual path provided by the user.

```python
import sys
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless — no display required
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from pathlib import Path
import json
import math

# ── Configuration ──────────────────────────────────────────────────────────────

CSV_PATH = "your_file.csv"     # ← replaced at runtime with actual path
OUTPUT_DIR = Path(CSV_PATH).parent / "csv_summary_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")

# ── Load ───────────────────────────────────────────────────────────────────────

df = pd.read_csv(CSV_PATH)
file_name = Path(CSV_PATH).name
n_rows, n_cols = df.shape

# ── Column-type detection ──────────────────────────────────────────────────────

def detect_column_types(df):
    numeric_cols, date_cols, categorical_cols, text_cols, bool_cols = [], [], [], [], []

    for col in df.columns:
        series = df[col].dropna()
        if series.empty:
            categorical_cols.append(col)
            continue

        # Boolean
        unique_vals = set(str(v).strip().lower() for v in series.unique())
        if unique_vals <= {"true", "false", "yes", "no", "1", "0"}:
            bool_cols.append(col)
            continue

        # Numeric
        if pd.api.types.is_numeric_dtype(series):
            numeric_cols.append(col)
            continue

        # Date/time (name-based heuristic + parse attempt)
        col_lower = col.lower()
        date_keywords = ("date", "time", "timestamp", "created", "updated",
                         "submitted", "occurred", "at")
        if any(kw in col_lower for kw in date_keywords):
            try:
                pd.to_datetime(series.iloc[:10], infer_datetime_format=True)
                date_cols.append(col)
                continue
            except Exception:
                pass

        # High-cardinality → free-text
        cardinality = series.nunique()
        if cardinality / len(series) > 0.8 and series.str.len().mean() > 30:
            text_cols.append(col)
        else:
            categorical_cols.append(col)

    return {
        "numeric":     numeric_cols,
        "date":        date_cols,
        "categorical": categorical_cols,
        "text":        text_cols,
        "boolean":     bool_cols,
    }

col_types = detect_column_types(df)

# Parse detected date columns
for col in col_types["date"]:
    try:
        df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
    except Exception:
        col_types["date"].remove(col)
        col_types["categorical"].append(col)

# ── Missing-value audit ────────────────────────────────────────────────────────

missing = df.isnull().sum()
missing_pct = (missing / n_rows * 100).round(1)
missing_df = pd.DataFrame({
    "missing_count": missing,
    "missing_pct":   missing_pct
}).query("missing_count > 0").sort_values("missing_pct", ascending=False)

# ── Summary statistics ─────────────────────────────────────────────────────────

numeric_summary = None
if col_types["numeric"]:
    numeric_summary = df[col_types["numeric"]].describe().T
    numeric_summary["median"] = df[col_types["numeric"]].median()
    numeric_summary["skew"]   = df[col_types["numeric"]].skew().round(3)

# ── Chart helpers ──────────────────────────────────────────────────────────────

chart_paths = []

def save_chart(fig, name):
    path = OUTPUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    chart_paths.append(str(path))
    return path

# ── Plot 1: numeric distributions (histograms) ────────────────────────────────

if col_types["numeric"]:
    cols = col_types["numeric"]
    n = len(cols)
    ncols_grid = min(3, n)
    nrows_grid = math.ceil(n / ncols_grid)
    fig, axes = plt.subplots(nrows_grid, ncols_grid,
                             figsize=(5 * ncols_grid, 4 * nrows_grid))
    axes = [axes] if n == 1 else axes.flatten()
    for ax, col in zip(axes, cols):
        sns.histplot(df[col].dropna(), kde=True, ax=ax, color="#4C72B0")
        ax.set_title(col, fontsize=11)
        ax.set_xlabel("")
    for ax in axes[n:]:
        ax.set_visible(False)
    fig.suptitle("Numeric Distributions", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    save_chart(fig, "01_numeric_distributions")

# ── Plot 2: correlation heatmap ───────────────────────────────────────────────

if len(col_types["numeric"]) >= 2:
    corr = df[col_types["numeric"]].corr()
    size = max(6, len(col_types["numeric"]))
    fig, ax = plt.subplots(figsize=(size, size * 0.8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                center=0, square=True, linewidths=0.5, ax=ax)
    ax.set_title("Correlation Matrix", fontsize=14, fontweight="bold")
    plt.tight_layout()
    save_chart(fig, "02_correlation_heatmap")

# ── Plot 3: categorical frequency charts ─────────────────────────────────────

if col_types["categorical"]:
    # Show at most 4 categorical columns; pick lowest cardinality first
    cat_cols = sorted(col_types["categorical"],
                      key=lambda c: df[c].nunique())[:4]
    n = len(cat_cols)
    ncols_grid = min(2, n)
    nrows_grid = math.ceil(n / ncols_grid)
    fig, axes = plt.subplots(nrows_grid, ncols_grid,
                             figsize=(7 * ncols_grid, 4 * nrows_grid))
    axes = [axes] if n == 1 else axes.flatten()
    for ax, col in zip(axes, cat_cols):
        counts = df[col].value_counts().head(15)
        sns.barplot(x=counts.values, y=counts.index.astype(str),
                    ax=ax, color="#55A868", orient="h")
        ax.set_title(f"{col} (top {len(counts)})", fontsize=11)
        ax.set_xlabel("Count")
    for ax in axes[n:]:
        ax.set_visible(False)
    fig.suptitle("Categorical Frequencies", fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    save_chart(fig, "03_categorical_frequencies")

# ── Plot 4: time-series trends ────────────────────────────────────────────────

if col_types["date"] and col_types["numeric"]:
    date_col  = col_types["date"][0]
    # Pick up to 2 numeric columns with highest variance for time-series
    num_cols_sorted = sorted(
        col_types["numeric"],
        key=lambda c: df[c].var(skipna=True),
        reverse=True
    )[:2]

    df_ts = df[[date_col] + num_cols_sorted].dropna(subset=[date_col])
    df_ts = df_ts.sort_values(date_col)

    fig, ax = plt.subplots(figsize=(10, 4))
    for col in num_cols_sorted:
        ax.plot(df_ts[date_col], df_ts[col], marker="o", markersize=3,
                linewidth=1.5, label=col)
    ax.xaxis.set_major_formatter(mdates.AutoDateFormatter(mdates.AutoDateLocator()))
    fig.autofmt_xdate()
    ax.set_title(f"Time-Series: {', '.join(num_cols_sorted)}", fontsize=13, fontweight="bold")
    ax.set_xlabel(date_col)
    ax.legend()
    plt.tight_layout()
    save_chart(fig, "04_time_series")

# ── Plot 5: missing-value bar chart ──────────────────────────────────────────

if not missing_df.empty:
    fig, ax = plt.subplots(figsize=(8, max(3, len(missing_df) * 0.5)))
    sns.barplot(x=missing_df["missing_pct"].values,
                y=missing_df.index, ax=ax, color="#C44E52", orient="h")
    ax.set_xlabel("Missing (%)")
    ax.set_title("Missing Values by Column", fontsize=13, fontweight="bold")
    plt.tight_layout()
    save_chart(fig, "05_missing_values")

# ── Markdown report ───────────────────────────────────────────────────────────

lines = [
    f"# CSV Analysis Report: `{file_name}`
",
    "---
",
    "## Dataset Overview
",
    f"| Property | Value |",
    f"|---|---|",
    f"| File | `{file_name}` |",
    f"| Rows | {n_rows:,} |",
    f"| Columns | {n_cols} |",
    f"| Numeric columns | {len(col_types['numeric'])} |",
    f"| Categorical columns | {len(col_types['categorical'])} |",
    f"| Date/time columns | {len(col_types['date'])} |",
    f"| Boolean columns | {len(col_types['boolean'])} |",
    f"| Free-text columns | {len(col_types['text'])} |",
    f"| Total missing cells | {int(missing.sum()):,} "
    f"({missing.sum() / (n_rows * n_cols) * 100:.1f}%) |
",
]

lines += [
    "## Column Types Detected
",
    "| Type | Columns |",
    "|---|---|",
]
for dtype, cols in col_types.items():
    if cols:
        lines.append(f"| {dtype.capitalize()} | {', '.join(f'`{c}`' for c in cols)} |")

if numeric_summary is not None:
    lines += [
        "
## Numeric Summary Statistics
",
        "| Column | Count | Mean | Std | Min | 25% | Median | 75% | Max | Skew |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for col_name, row in numeric_summary.iterrows():
        lines.append(
            f"| `{col_name}` "
            f"| {int(row['count']):,} "
            f"| {row['mean']:.2f} "
            f"| {row['std']:.2f} "
            f"| {row['min']:.2f} "
            f"| {row['25%']:.2f} "
            f"| {row['median']:.2f} "
            f"| {row['75%']:.2f} "
            f"| {row['max']:.2f} "
            f"| {row['skew']:.3f} |"
        )

if not missing_df.empty:
    lines += [
        "
## Missing Values
",
        "| Column | Missing Count | Missing % |",
        "|---|---|---|",
    ]
    for col_name, row in missing_df.iterrows():
        lines.append(
            f"| `{col_name}` | {int(row['missing_count']):,} | {row['missing_pct']}% |"
        )
else:
    lines += ["
## Missing Values
", "No missing values detected.
"]

if col_types["categorical"]:
    lines += ["
## Categorical Column Summaries
"]
    for col in col_types["categorical"]:
        top = df[col].value_counts().head(5)
        lines.append(f"**`{col}`** — {df[col].nunique()} unique values")
        lines.append("| Value | Count |")
        lines.append("|---|---|")
        for val, cnt in top.items():
            lines.append(f"| {val} | {cnt} |")
        lines.append("")

if col_types["date"]:
    lines += ["
## Temporal Coverage
"]
    for col in col_types["date"]:
        mn = df[col].min()
        mx = df[col].max()
        span = mx - mn
        lines.append(f"- **`{col}`**: {mn.date()} → {mx.date()} "
                     f"({span.days} days)")

lines += ["
## Visualizations Generated
"]
for path in chart_paths:
    name = Path(path).stem.replace("_", " ").title()
    lines.append(f"- **{name}**: `{path}`")

report_md = "
".join(lines)
report_path = OUTPUT_DIR / "report.md"
report_path.write_text(report_md, encoding="utf-8")

print(report_md)
print(f"
---
Charts saved to: {OUTPUT_DIR}")
print(f"Markdown report: {report_path}")
```

---

## Output Format

After running the script, present the analysis in this order:

1. **Dataset Overview** table (rows, cols, type breakdown, missing %)
2. **Column Types Detected** table
3. **Numeric Summary Statistics** table (if numeric cols exist)
4. **Missing Values** table or "none detected" message
5. **Categorical Column Summaries** (top-5 frequency for each)
6. **Temporal Coverage** (date range if date cols exist)
7. **Visualizations** — list each chart path and briefly describe what it shows

---

## Behavior Guidelines

**CORRECT responses — say these:**
- "Here is the complete analysis:"
- "I've identified this as [sales / survey / financial / operational] data."
- Then immediately present the full report.

**FORBIDDEN responses — never say these:**
- "What would you like me to help you with?"
- "Here are some options:"
- "I can do X if you'd like."
- Any sentence ending in `?` that asks for user direction.
- Any conditional "I could also..."

**NEVER:**
- Ask what the user wants before analyzing.
- Offer a choice of analysis depth.
- Provide a partial analysis that requires follow-up.
- Describe capabilities instead of executing them.

---

## Data Type Adaptations

| Data type detected | Primary focus |
|---|---|
| Sales / e-commerce | Revenue trends, product performance, regional breakdown |
| Customer / demographics | Segmentation, distribution by age/role/region |
| Financial / transactions | Temporal trend, amount distribution, correlation |
| Survey / responses | Frequency distributions, cross-tabs, satisfaction scores |
| Operational / metrics | Time-series, performance stats, status breakdown |
| Generic tabular | Full numeric + categorical summary, correlations |

---

## Dependencies

Install with pip:

```bash
pip install pandas matplotlib seaborn
```

Or with the provided requirements file:

```bash
pip install -r requirements.txt
```

`requirements.txt`:
```
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

---

## Example Prompts That Trigger This Skill

> "Here's `sales_data.csv` — can you summarize it?"

> "Analyze this survey CSV and show me trends."

> "What insights can you pull from `orders.csv`?"

> "Explore `sample_sales.csv` for me."

> *(User uploads any .csv with no further instruction)*

---

## Notes

- Charts are saved as PNG files alongside the CSV (in a `csv_summary_output/` subfolder).
- Date detection uses both column-name heuristics and parse attempts — no false positives.
- Categorical columns with more than 15 unique values show only the top 15.
- Time-series plot uses the highest-variance numeric columns to surface the most interesting signal.
- Script is self-contained and has no project-specific imports.
