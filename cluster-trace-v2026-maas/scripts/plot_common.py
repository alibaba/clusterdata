from common import query as cached_query, save

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

WORKLOADS = [("online", "Online", "#4C78A8"), ("offline", "Offline", "#F58518")]
ROLES = [("prefill", "Prefill", "steelblue"), ("decode", "Decode", "seagreen"),
         ("fused", "PD-Colloc", "darkorange")]
ARCHES = [("dense", "Dense", "steelblue"), ("moe", "MoE", "darkorange")]
HOT_COLORS = {"Hot": "firebrick", "Cold": "steelblue"}
MODEL_MARKS = [(3, 98), (8, 98), (32, 58), (235, 58)]

HOT_SQL = """
WITH usage AS (
    SELECT workload, model_key, fsum(hours) AS hours
    FROM src WHERE hours > 0 AND model_id IS NOT NULL AND model_id <> ''
    GROUP BY workload, model_key
)
SELECT workload, model_key,
       CASE WHEN percent_rank() OVER (PARTITION BY workload ORDER BY hours DESC)
                 <= 0.10 THEN 'Hot' ELSE 'Cold' END AS temperature
FROM usage
"""


def query(name, sql, hot=False):
    setup = "CREATE TEMP VIEW hot_models AS " + HOT_SQL if hot else ""
    return cached_query(name, sql, setup)


def cdf(points, origin=0, percentile=None):
    totals = {}
    for value, weight in points:
        if value is not None and weight is not None and weight >= 0:
            totals[value] = totals.get(value, 0.0) + weight
    x = np.array(sorted(totals), dtype=float)
    w = np.array([totals[v] for v in x])
    if not len(x) or w.sum() <= 0:
        return np.array([]), np.array([])
    y = np.cumsum(w) / w.sum() * 100
    if origin is not None and x[0] >= origin:
        x, y = np.r_[origin, x], np.r_[0.0, y]
    if percentile is not None:
        stop = min(np.searchsorted(y, percentile) + 1, len(x))
        x, y = x[:stop], y[:stop]
    return x, y


def axes(number, panel, xlabel, ylabel="CDF of GPU Time (%)"):
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.set_label(f"fig{number:02d}{panel}")
    ax.set(xlabel=xlabel, ylabel=ylabel, ylim=(0, 102))
    ax.grid(alpha=0.2)
    return fig, ax


def finish(fig, ax, legend=True):
    if legend:
        ax.legend(frameon=False, loc="lower right")
    save(fig)


def draw_groups(ax, rows, styles, marker=None, origin=0):
    for group, label, color in styles:
        x, y = cdf([(r[1], r[2]) for r in rows if r[0] == group], origin)
        if len(x):
            ax.plot(x, y, color=color, label=label, marker=marker)


def model_marks(ax, marks=MODEL_MARKS):
    ax.set_xscale("symlog", linthresh=1)
    for size, height in marks:
        ax.axvline(size, color="gray", linestyle=":", alpha=0.75)
        ax.annotate(f"{size}B", (size, height), xytext=(2, 0),
                    textcoords="offset points", rotation=90, va="top",
                    color="#333333", bbox={"facecolor": "white", "edgecolor": "none", "alpha": .7})


def hot_legend(ax):
    handles = [Line2D([], [], color=color, label=temp) for temp, color in HOT_COLORS.items()]
    handles += [Line2D([], [], color="black", linestyle=style, label=label)
                for label, style in [("Online", "-"), ("Offline", "--")]]
    ax.legend(handles=handles, frameon=False, loc="lower right")


def draw_hot(ax, rows, percentile=None):
    for workload, style in [("online", "-"), ("offline", "--")]:
        for temp, color in HOT_COLORS.items():
            x, y = cdf([(r[2], r[3]) for r in rows
                        if r[0] == workload and r[1] == temp], percentile=percentile)
            if len(x):
                ax.plot(x, y, color=color, linestyle=style)
    hot_legend(ax)
