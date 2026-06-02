"""Plot cpu_gpu_ratio.pdf."""

from __future__ import annotations

from collections import defaultdict

import matplotlib.pyplot as plt
import pandas as pd

from . import common as c


def plot() -> None:
    counters: dict[str, defaultdict[float, int]] = {
        job_type: defaultdict(int) for job_type in c.PUBLIC_JOB_ORDER
    }
    for chunk in pd.read_csv(c.csv_path("cpu_gpu_ratio_samples"), chunksize=c.CSV_CHUNKSIZE):
        chunk = chunk[chunk["job_type"].isin(c.PUBLIC_JOB_ORDER)]
        for job_type, group in chunk.groupby("job_type", sort=False):
            c.update_counter(counters[job_type], group["cpu_gpu_ratio"])

    summary = pd.DataFrame(
        [{"job_type": job_type, **c.counter_stats(counters[job_type])} for job_type in c.PUBLIC_JOB_ORDER]
    )
    output = c.OUT_DIR / "cpu_gpu_ratio.pdf"
    summary_path = c.OUT_DIR / "cpu_gpu_ratio.summary.csv"
    c.save_summary(summary, summary_path)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    fontsize = 24
    ax.text(0.2, 0.5, "Median", fontsize=fontsize, transform=ax.transAxes)
    text_y = {
        "training": 0.38,
        "online_inference": 0.26,
        "offline_inference": 0.14,
        "dev": 0.02,
    }
    for job_type in c.PUBLIC_JOB_ORDER:
        x, y = c.cdf_from_counter(counters[job_type])
        if x.size == 0:
            continue
        ax.plot(
            x,
            y,
            linewidth=2.5,
            linestyle=c.LINE_STYLES[job_type],
            color=c.LINE_COLORS[job_type],
            label=c.JOB_LABELS[job_type],
        )
        stats = c.counter_stats(counters[job_type])
        ax.text(
            0.2,
            text_y[job_type],
            f"{c.JOB_LABELS[job_type]}: {stats['median']:.0f}",
            fontsize=fontsize,
            transform=ax.transAxes,
        )
    ax.tick_params(axis="both", labelsize=fontsize)
    ax.set_xlim(0, 128)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Requested CPU/GPU Ratio", fontsize=fontsize)
    ax.set_ylabel("CDF", fontsize=fontsize)
    ax.legend(
        fontsize=fontsize,
        ncol=1,
        loc="lower right",
        handlelength=1.5,
        handletextpad=0.5,
        frameon=False,
        borderaxespad=0.03,
        labelspacing=0.05,
    )
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.write_manifest("cpu_gpu_ratio", ["asi_opensource_cpu_gpu_ratio_samples"], summary_path, output)
