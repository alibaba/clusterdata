"""Plot idle_gpu_fragmentation.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from . import common as c


def plot() -> None:
    df = c.read_csv("idle_gpu_fragmentation")
    output = c.OUT_DIR / "idle_gpu_fragmentation.pdf"
    summary = c.OUT_DIR / "idle_gpu_fragmentation.summary.csv"
    c.save_summary(df, summary)

    fig, ax = plt.subplots(figsize=(12, 4))
    fontsize = 22
    config_names = df["job_config"].tolist()
    config_labels = [name.replace("gpu", "").replace("_cpu", "G") + "C" for name in config_names]
    fractional_vals = df["fractional_unallocatable"].to_numpy(dtype=float)
    insufficient_whole_vals = df["insufficient_whole_unallocatable"].to_numpy(dtype=float)
    insufficient_cpu_vals = df["insufficient_cpu_unallocatable"].to_numpy(dtype=float)
    insufficient_cpu_pct = df["insufficient_cpu_pct"].to_numpy(dtype=float)
    x = np.arange(len(df))
    width = 0.3
    bars1 = ax.bar(x - width, fractional_vals, width, label="Fractional GPU")
    bars2 = ax.bar(x, insufficient_whole_vals, width, label="Stranded GPUs")
    bars3 = ax.bar(x + width, insufficient_cpu_vals, width, label="Insufficient CPUs")
    ax.set_ylabel("#Unallocatable Idle GPUs", fontsize=fontsize - 2, loc="top")
    ax.yaxis.set_label_coords(-0.05, 1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(config_labels, rotation=0, ha="center", fontsize=fontsize)
    ax.set_yticks(np.arange(0, 10000, 2000))
    ax.set_yticklabels([f"{int(y / 1000)}k" for y in np.arange(0, 10000, 2000)], fontsize=fontsize)
    ax.set_ylim(0, 10500)
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    def add_value_labels(bars, percentages=None):
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if percentages is None:
                text = f"{height / 1000:.0f}k"
                x_offset = 0.0
            else:
                text = f"{height / 1000:.0f}k\n({percentages[i]:.0f}%)"
                x_offset = 0.13
            ax.text(
                bar.get_x() + bar.get_width() / 2.0 + x_offset,
                height,
                text,
                ha="center",
                va="bottom",
                fontsize=fontsize - 2,
            )

    add_value_labels(bars1)
    add_value_labels(bars2)
    add_value_labels(bars3, insufficient_cpu_pct)
    ax.text(0.5, 5000, "Percentage of\nidle GPUs", ha="center", va="bottom", fontsize=fontsize - 2)
    ax.annotate(
        "",
        xy=(0.8, 5000),
        xytext=(1.2, 2500),
        arrowprops=dict(arrowstyle="->", color="black", linewidth=2),
    )
    ax.legend(
        loc="upper left",
        fontsize=fontsize,
        labelspacing=0.2,
        ncol=2,
        bbox_to_anchor=(0, 1.03),
        handlelength=1.5,
        columnspacing=0.5,
        borderaxespad=0.2,
    )
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.write_manifest("idle_gpu_fragmentation", ["asi_opensource_idle_gpu_fragmentation"], summary, output)
