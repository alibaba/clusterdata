"""Plot model_type_distribution.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from . import common as c


def plot() -> None:
    df = c.read_csv("model_type_distribution")
    output = c.OUT_DIR / "model_type_distribution.pdf"
    summary = c.OUT_DIR / "model_type_distribution.summary.csv"
    c.save_summary(df, summary)

    job_types = ["training", "online_inference", "offline_inference", "dev"]
    gpu_specs = ["A10", "L20", "H20", "A100", "H800", "XPU-A"]
    model_types = ["genai", "rec", "cv", "embedding", "dev"]
    model_type_labels = {
        "embedding": "Embed.",
        "rec": "Rec",
        "genai": "GenAI",
        "cv": "CV",
        "dev": "Dev",
    }
    bar_color_model_type = {
        "rec": "tab:blue",
        "genai": "tab:orange",
        "cv": "tab:green",
        "dev": "tab:red",
        "embedding": "tab:purple",
    }
    job_label_conversion = {
        "training": "Training",
        "online_inference": "On-Infer",
        "offline_inference": "Off-Infer",
        "dev": "Dev",
    }

    def percentage(group_kind: str, group_col: str, group_value: str, model_type: str) -> float:
        cur = df[
            (df["group_kind"] == group_kind)
            & (df[group_col] == group_value)
            & (df["model_type"] == model_type)
        ]
        return float(cur["percentage"].sum()) if not cur.empty else 0.0

    fig, ax = plt.subplots(figsize=(14, 4), nrows=1, ncols=2, sharey=True)
    fontsize = 24
    x_job_type = np.arange(len(job_types))
    x_gpu_spec = np.arange(len(gpu_specs))
    bar_width = 0.8 / len(model_types)
    legend_handles = []
    legend_labels = []

    for model_id, model_type in enumerate(model_types):
        offset = (model_id - len(model_types) / 2) * bar_width + bar_width / 2
        label = model_type_labels[model_type]
        plot_y = [percentage("job_type", "job_type", job_type, model_type) for job_type in job_types]
        bars = ax[0].bar(
            x_job_type + offset,
            plot_y,
            bar_width,
            label=label,
            color=bar_color_model_type[model_type],
        )
        if len(bars) > 0:
            legend_handles.append(bars[0])
            legend_labels.append(label)
        for bar, value in zip(bars, plot_y):
            ax[0].text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{value:.0f}",
                ha="center",
                va="bottom",
                fontsize=fontsize - 4,
            )

    for model_id, model_type in enumerate(model_types):
        offset = (model_id - len(model_types) / 2) * bar_width + bar_width / 2
        plot_y = [percentage("server_gpu_spec", "server_gpu_spec", gpu_spec, model_type) for gpu_spec in gpu_specs]
        bars = ax[1].bar(
            x_gpu_spec + offset,
            plot_y,
            bar_width,
            label=model_type_labels[model_type],
            color=bar_color_model_type[model_type],
        )
        for bar, value in zip(bars, plot_y):
            if value > 0:
                ax[1].text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{value:.0f}",
                    ha="center",
                    va="bottom",
                    fontsize=fontsize - 4,
                )

    ax[0].set_ylabel("Percentage (%)", fontsize=fontsize)
    ax[0].set_xticks(x_job_type)
    ax[1].set_xticks(x_gpu_spec)
    ax[0].set_xticklabels([job_label_conversion[job_type] for job_type in job_types], fontsize=fontsize - 2)
    ax[1].set_xticklabels(gpu_specs, fontsize=fontsize - 2)
    ax[0].grid(axis="y", linestyle="--")
    ax[1].grid(axis="y", linestyle="--")
    ax[0].set_ylim([0, 100])
    ax[1].set_ylim([0, 100])
    ax[0].tick_params(axis="both", labelsize=fontsize - 2)
    ax[1].tick_params(axis="both", labelsize=fontsize - 2)
    fig.legend(
        legend_handles,
        legend_labels,
        fontsize=fontsize - 2,
        ncol=5,
        bbox_to_anchor=(0.5, 0.83),
        loc="lower center",
        frameon=False,
        handlelength=1.5,
        handletextpad=0.5,
    )
    plt.subplots_adjust(wspace=0.1)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(output, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    c.write_manifest("model_type_distribution", ["asi_opensource_model_type_distribution"], summary, output)
