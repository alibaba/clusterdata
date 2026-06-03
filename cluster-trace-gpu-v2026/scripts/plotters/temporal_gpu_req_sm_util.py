"""Plot temporal_gpu_req_sm_util.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from . import common as c


def plot() -> None:
    df = c.read_csv("temporal_gpu_req_sm_util")
    df["day"] = c.pd.to_numeric(df["day"], errors="coerce")
    df["hour"] = c.pd.to_numeric(df["hour"], errors="coerce")
    df = df.dropna(subset=["day", "hour"]).sort_values(["day", "hour", "job_type"])
    hour_keys = sorted(df[["day", "hour"]].drop_duplicates().itertuples(index=False, name=None))
    x_lookup = {key: idx for idx, key in enumerate(hour_keys)}
    df["x"] = [x_lookup[(row.day, row.hour)] for row in df.itertuples(index=False)]
    output = c.OUT_DIR / "temporal_gpu_req_sm_util.pdf"
    summary = c.OUT_DIR / "temporal_gpu_req_sm_util.summary.csv"
    c.save_summary(df, summary)

    fig, axes = plt.subplots(figsize=(10, 6), nrows=2, ncols=1)
    fontsize = 20
    for job_type in c.PUBLIC_JOB_ORDER:
        group = df[df["job_type"].eq(job_type)].sort_values("x")
        if group.empty:
            continue
        label = c.JOB_LABELS.get(job_type, job_type)
        axes[0].plot(
            group["x"],
            group["num_gpu_request"],
            label=label,
            linestyle=c.LINE_STYLES[job_type],
            linewidth=3,
        )
        axes[1].plot(
            group["x"],
            group["avg_gpu_sm_util_per_gpu"],
            label=label,
            linestyle=c.LINE_STYLES[job_type],
            linewidth=3,
        )
    x_ticks = np.arange(0, len(hour_keys) + 1, 24)
    for ax in axes:
        ax.set_xlim(-5, len(hour_keys) + 5)
        ax.set_xticks(x_ticks)
        ax.tick_params(axis="both", labelsize=fontsize)
    axes[0].set_ylabel("#GPU Requested", fontsize=fontsize)
    axes[1].set_ylabel("GPU SM Utilization", fontsize=fontsize)
    axes[1].set_xlabel("Hours from the beginning of a week (Mon. to Sun.)", fontsize=fontsize)
    max_tick = int(max(axes[0].get_yticks())) if len(axes[0].get_yticks()) else 0
    y_ticks = [item for item in range(0, max_tick, 20000)]
    if y_ticks:
        axes[0].set_yticks(y_ticks)
        axes[0].set_yticklabels([f"{tick // 1000}K" for tick in y_ticks])
    axes[0].legend(
        fontsize=fontsize,
        ncols=4,
        bbox_to_anchor=(-0.01, 0.95, 1.0, 0.0),
        handlelength=1.5,
        handletextpad=0.5,
    )
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.write_manifest("temporal_gpu_req_sm_util", ["asi_opensource_temporal_gpu_req_sm_util"], summary, output)
