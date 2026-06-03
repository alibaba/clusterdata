"""Plot gpu_spec_priority_distribution.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from . import common as c


def plot() -> None:
    df = c.read_csv("gpu_spec_priority_pod_hours")
    df = df.set_index("server_gpu_spec").reindex(c.PAPER_GPU_ORDER).reset_index()
    df["display_gpu_spec"] = df["server_gpu_spec"].map(c.display_gpu_label)
    output = c.OUT_DIR / "gpu_spec_priority_distribution.pdf"
    summary = c.OUT_DIR / "gpu_spec_priority_distribution.summary.csv"
    c.save_summary(df, summary)

    fig, ax = plt.subplots(figsize=(7, 4))
    fontsize = 24
    x = np.arange(len(df))
    width = 0.35
    bars1 = ax.bar(x - width / 2, df["hp_pct"], width, label="HP")
    bars2 = ax.bar(x + width / 2, df["lp_pct"], width, label="LP")
    for bar in [*bars1, *bars2]:
        height = bar.get_height()
        if height > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height:.0f}%",
                ha="center",
                va="bottom",
                fontsize=fontsize - 3,
            )
    ax.set_ylabel("Percentage", fontsize=fontsize)
    ax.set_xticks(x)
    ax.set_xticklabels(df["display_gpu_spec"], fontsize=fontsize - 4)
    ax.tick_params(axis="both", which="major", labelsize=fontsize - 4)
    ax.legend(
        loc="upper center",
        fontsize=fontsize - 2,
        handlelength=1.5,
        bbox_to_anchor=(0.6, 1.1),
        frameon=True,
        handletextpad=0.5,
        ncol=2,
        framealpha=1.0,
        labelspacing=0.5,
        columnspacing=0.5,
    )
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    c.write_manifest("gpu_spec_priority_distribution", ["asi_opensource_gpu_spec_priority_pod_hours"], summary, output)
