"""Plot gpu_spec_alloc_ratio.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from . import common as c


def plot() -> None:
    df = c.read_csv("gpu_spec_alloc_ratio")
    output = c.OUT_DIR / "gpu_spec_alloc_ratio.pdf"
    summary = c.OUT_DIR / "gpu_spec_alloc_ratio.summary.csv"
    if "gpu_spec_public" in df.columns:
        df["display_gpu_spec"] = df["gpu_spec_public"].map(c.display_gpu_label)
    elif "display_gpu_spec" not in df.columns:
        df["display_gpu_spec"] = df.iloc[:, 0].map(c.display_gpu_label)
    df = df.sort_values("ratio_9300", ascending=False).reset_index(drop=True)
    c.save_summary(df, summary)

    fig, ax = plt.subplots(figsize=(12, 3))
    bar_width = 0.4
    fontsize = 20
    x = np.arange(len(df))
    bars_1 = ax.bar(x - bar_width / 2, df["ratio_9300"], bar_width, label="HP")
    bars_2 = ax.bar(x + bar_width / 2, df["ratio_9200"], bar_width, label="HP + LP")
    for bar in [*bars_1, *bars_2]:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{bar.get_height():.2f}",
            ha="center",
            va="bottom",
            fontsize=fontsize - 4,
        )
    ax.set_ylim(0, 1.3)
    ax.set_xticks(x)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_ylabel("Allocation Ratio", fontsize=fontsize)
    ax.set_xticklabels(df["display_gpu_spec"], fontsize=fontsize, rotation=15)
    ax.tick_params(axis="both", labelsize=fontsize)
    ax.legend(
        loc="upper right",
        fontsize=fontsize,
        frameon=False,
        borderpad=0.1,
        ncol=2,
        borderaxespad=0.1,
        labelspacing=0.05,
        handletextpad=0.05,
        columnspacing=1.0,
        handlelength=1.0,
    )
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.write_manifest("gpu_spec_alloc_ratio", ["asi_opensource_gpu_spec_alloc_ratio"], summary, output)
