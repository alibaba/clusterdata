"""Plot asw_available_slots.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from . import common as c


def plot() -> None:
    df = c.read_csv("asw_available_slots")
    output = c.OUT_DIR / "asw_available_slots.pdf"
    summary = c.OUT_DIR / "asw_available_slots.summary.csv"
    c.save_summary(df, summary)

    avg = (
        df.groupby(["gpu_spec_public", "gpu_set_size"], as_index=False)[
            ["total_slots_across_cluster", "total_slots_across_asw"]
        ]
        .mean()
    )
    selected_gpus = ["A100", "L20", "H20", "XPU-A", "heterogenous"]
    fig, axs = plt.subplots(figsize=(15, 4), nrows=1, ncols=2)
    fontsize = 24
    bar_width = 0.32
    plot_x_axis_cluster = np.arange(len(selected_gpus)) - 0.5 * bar_width
    plot_x_axis_asw = np.arange(len(selected_gpus)) + 0.5 * bar_width

    def values(gpu_set_size: int, column: str) -> list[float]:
        out = []
        for gpu_spec in selected_gpus:
            cur = avg[(avg["gpu_spec_public"] == gpu_spec) & (avg["gpu_set_size"] == gpu_set_size)]
            out.append(float(cur[column].iloc[0]) if not cur.empty else 0.0)
        return out

    for ax, gpu_set_size in zip(axs, [128, 256]):
        total_slots_across_cluster = values(gpu_set_size, "total_slots_across_cluster")
        total_slots_across_asw = values(gpu_set_size, "total_slots_across_asw")
        bars_cluster = ax.bar(plot_x_axis_cluster, total_slots_across_cluster, bar_width, label="Across ASW")
        bars_asw = ax.bar(plot_x_axis_asw, total_slots_across_asw, bar_width, label="Within ASW")
        for bars, vals in [(bars_cluster, total_slots_across_cluster), (bars_asw, total_slots_across_asw)]:
            for bar, val in zip(bars, vals):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{val:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=fontsize - 2,
                )
        ax.set_title(f"Jobs request {gpu_set_size} GPUs", fontsize=fontsize)
        ax.set_xlabel("Requested GPU Spec", fontsize=fontsize)
        ax.set_xticks(np.arange(len(selected_gpus)))
        xlabels = [gpu_spec if gpu_spec != "heterogenous" else "Hetero." for gpu_spec in selected_gpus]
        ax.set_xticklabels(xlabels, fontsize=fontsize)
        ax.tick_params(axis="y", labelsize=fontsize)
    axs[0].set_ylabel("#Jobs could be fulfilled", fontsize=fontsize, loc="top")
    axs[0].yaxis.set_label_coords(-0.1, 1.15)
    axs[0].legend(fontsize=fontsize)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)
    c.write_manifest("asw_available_slots", ["asi_opensource_asw_available_slots"], summary, output)
