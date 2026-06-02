"""Plot job_type_model_type_execution_time_cdf.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import common as c


def plot() -> None:
    duration_bins = np.concatenate(([0.0], np.logspace(-3, 5, 1000)))
    groups = [("job_type", group) for group in c.EXEC_PUBLIC_JOB_ORDER] + [
        ("model_type", group) for group in c.EXEC_PUBLIC_MODEL_ORDER
    ]
    hists = {group: np.zeros(len(duration_bins) - 1, dtype=np.int64) for group in groups}
    stats = {group: {"count": 0, "sum": 0.0} for group in groups}
    for chunk in pd.read_csv(
        c.csv_path("job_execution_hours"),
        usecols=["group_type", "group_name", "duration_hours"],
        chunksize=c.CSV_CHUNKSIZE,
    ):
        for group in groups:
            group_type, group_name = group
            vals = chunk[(chunk["group_type"] == group_type) & (chunk["group_name"] == group_name)]["duration_hours"]
            c.update_hist(hists[group], duration_bins, vals, stats[group])

    rows = [
        {
            "group_type": group_type,
            "group": group_name,
            **c.hist_stats(hists[(group_type, group_name)], duration_bins, stats[(group_type, group_name)]),
        }
        for group_type, group_name in groups
        if stats[(group_type, group_name)]["count"] > 0
    ]
    output = c.OUT_DIR / "job_type_model_type_execution_time_cdf.pdf"
    summary_path = c.OUT_DIR / "job_type_model_type_execution_time_cdf.summary.csv"
    c.save_summary(pd.DataFrame(rows), summary_path)

    fig, axes = plt.subplots(1, 2, figsize=(14, 4))
    fontsize = 24
    job_handles = {}
    model_handles = {}
    for group in c.EXEC_PUBLIC_JOB_ORDER:
        x, y = c.cdf_from_hist(hists[("job_type", group)], duration_bins)
        if x.size:
            line = axes[0].plot(
                x,
                y,
                label=c.JOB_LABELS[group],
                linestyle=c.LINE_STYLES[group],
                color=c.LINE_COLORS[group],
                linewidth=2.5,
            )[0]
            job_handles[group] = line
    for group in c.EXEC_PUBLIC_MODEL_ORDER:
        x, y = c.cdf_from_hist(hists[("model_type", group)], duration_bins)
        if x.size:
            line = axes[1].plot(
                x,
                y,
                label=c.MODEL_LABELS[group],
                color=c.MODEL_LINE_COLORS[group],
                linestyle=c.MODEL_LINE_STYLES[group],
                linewidth=2.5,
            )[0]
            model_handles[group] = line
    axes[0].set_xlabel("Duration (Hours)", fontsize=fontsize)
    axes[1].set_xlabel("Duration (Hours)", fontsize=fontsize)
    axes[0].set_ylabel("CDF", fontsize=fontsize)
    axes[0].tick_params(labelsize=fontsize)
    axes[1].tick_params(labelsize=fontsize)
    job_legend_order = [group for group in c.EXEC_PUBLIC_JOB_ORDER if group in job_handles]
    model_legend_order = [group for group in c.EXEC_PUBLIC_MODEL_ORDER if group in model_handles]
    axes[0].legend(
        [job_handles[group] for group in job_legend_order],
        [c.JOB_LABELS[group] for group in job_legend_order],
        fontsize=fontsize,
        loc="upper left",
        handlelength=1.5,
        frameon=False,
        labelspacing=0.1,
        borderpad=0.1,
        handletextpad=0.1,
        borderaxespad=0.1,
    )
    axes[1].legend(
        [model_handles[group] for group in model_legend_order],
        [c.MODEL_LABELS[group] for group in model_legend_order],
        fontsize=fontsize,
        loc="lower right",
        handlelength=1.5,
        frameon=False,
        labelspacing=0.1,
        borderpad=0.1,
        handletextpad=0.1,
        borderaxespad=0.1,
    )
    for ax in axes:
        c.configure_execution_time_axis(ax)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    c.write_manifest(
        "job_type_model_type_execution_time_cdf",
        ["asi_opensource_job_execution_summary"],
        summary_path,
        output,
        note="CDF curves are binned from public-bucket duration rows generated from job_execution_summary.",
    )
