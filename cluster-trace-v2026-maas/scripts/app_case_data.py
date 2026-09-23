from common import ROOT, save
import csv
import json

import matplotlib.pyplot as plt
import numpy as np


def load_case(figure):
    directory = ROOT / "data"
    metadata = json.loads((directory / "app_cases.json").read_text())
    case = metadata["figures"][str(figure)]
    apps = {item["app_id"] for item in case["apps"]}
    rows = []
    with (directory / "app_metrics.csv").open(newline="") as stream:
        for row in csv.DictReader(stream):
            if row["app_id"] not in apps:
                continue
            row["time_s"] = int(row["time_s"])
            row["value"] = None if row["value"] in ("", "\\N") else float(row["value"])
            rows.append(row)
    return metadata, case, rows


def points(rows, metric, role=None):
    selected = [r for r in rows if r["metric"] == metric and
                (role is None or r["pd_role"] == role)]
    return sorted(selected, key=lambda r: r["time_s"])


def weekdays(ax, metadata):
    start = metadata["week_start_s"]
    ax.set_xticks([start + d * 86400 for d in [0, 2, 4, 6]],
                  ["Mon", "Wed", "Fri", "Sun"])
    ax.set_xticks([start + d * 86400 for d in range(7)], minor=True)
    ax.set_xlim(start, start + 7 * 86400 - 3600)
    ax.ticklabel_format(axis="y", style="plain", useOffset=False)


def new_axes(figure, panel, title=None):
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.set_label(f"fig{figure:02d}_{panel}")
    if title:
        ax.set_title(title)
    ax.grid(alpha=.2)
    return fig, ax


def finish(fig):
    save(fig)


def line(ax, rows, metric, color, label=None, role=None):
    values = points(rows, metric, role)
    ax.plot([r["time_s"] for r in values],
            [np.nan if r["value"] is None else r["value"] for r in values],
            color=color, label=label, linewidth=1)
