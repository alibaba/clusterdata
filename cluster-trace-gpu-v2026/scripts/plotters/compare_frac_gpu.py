"""Plot compare_frac_gpu.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import common as c


def plot() -> None:
    df = c.read_csv("fractional_gpu_summary")
    output = c.OUT_DIR / "compare_frac_gpu.pdf"
    summary = c.OUT_DIR / "compare_frac_gpu.summary.csv"
    asi_task = float(df.loc[df["metric"].eq("ratio_task_num"), "value"].sum())
    asi_gpu = float(df.loc[df["metric"].eq("ratio_gpu_req"), "value"].sum())
    pai_task = 0.8065861502233936
    pai_gpu = 0.45169500764376797
    summary_df = pd.DataFrame(
        [
            {"source": "PAI", "metric": "ratio_task_num", "value": pai_task},
            {"source": "PAI", "metric": "ratio_gpu_req", "value": pai_gpu},
            {"source": "ASI", "metric": "ratio_task_num", "value": asi_task},
            {"source": "ASI", "metric": "ratio_gpu_req", "value": asi_gpu},
        ]
    )
    c.save_summary(summary_df, summary)

    fig, ax = plt.subplots(figsize=(7, 3.5))
    fontsize = 24
    bars_1 = ax.bar(np.arange(2), [pai_task, pai_gpu], width=0.4, label="PAI")
    bars_2 = ax.bar(np.arange(2) + 0.4, [asi_task, asi_gpu], width=0.4, label="ASI")
    for bar in [*bars_1, *bars_2]:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{bar.get_height() * 100:.0f}",
            ha="center",
            va="bottom",
            fontsize=fontsize - 4,
        )
    ax.set_xticks(np.arange(2) + 0.2)
    ax.set_xticklabels(["# Task", "# GPU Request"], fontsize=fontsize)
    ax.set_ylabel("Percentage of\nFractional GPU (%)", fontsize=fontsize - 2)
    ax.set_yticks(np.arange(0, 1.1, 0.2))
    ax.set_yticklabels(["0", "20", "40", "60", "80", "100"], fontsize=fontsize)
    ax.grid(axis="y", zorder=0)
    ax.legend(
        fontsize=fontsize,
        ncol=1,
        loc="upper right",
        handlelength=1.5,
        handletextpad=0.5,
        borderaxespad=0.1,
    )
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.write_manifest("compare_frac_gpu", ["asi_opensource_fractional_gpu_summary"], summary, output)
