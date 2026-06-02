"""Plot gpu_cpu_request_num_box_plot.eps and .pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import common as c


def plot() -> None:
    df = c.read_csv("gpu_cpu_request_samples")
    is_genai = df["is_genai"].astype(str).str.lower().isin(["1", "true"])
    groups = {
        "ASI": df,
        "ASI(GenAI)": df[is_genai],
    }
    rows = []
    for source, group in groups.items():
        for metric in ["gpu_request", "cpu_request_cores"]:
            arr = pd.to_numeric(group[metric], errors="coerce").dropna().to_numpy(dtype=float)
            rows.append(
                {
                    "source": source,
                    "metric": metric,
                    "count": int(arr.size),
                    "median": float(np.median(arr)) if arr.size else np.nan,
                    "mean": float(np.mean(arr)) if arr.size else np.nan,
                    "p90": float(np.percentile(arr, 90)) if arr.size else np.nan,
                }
            )
    summary_path = c.OUT_DIR / "gpu_cpu_request_num_box_plot.summary.csv"
    c.save_summary(pd.DataFrame(rows), summary_path)

    output_eps = c.OUT_DIR / "gpu_cpu_request_num_box_plot.eps"
    output_pdf = c.OUT_DIR / "gpu_cpu_request_num_box_plot.pdf"
    fig, axes = plt.subplots(figsize=(14, 3.5), nrows=1, ncols=2)
    fontsize = 24
    palette = ["tab:orange", "tab:green"]
    for ax, metric, ylabel in [
        (axes[0], "gpu_request", "# GPU request"),
        (axes[1], "cpu_request_cores", "# CPU request"),
    ]:
        data = [
            pd.to_numeric(groups[source][metric], errors="coerce").dropna().to_numpy(dtype=float)
            for source in ["ASI", "ASI(GenAI)"]
        ]
        data = [arr[arr > 0] for arr in data]
        bp = ax.boxplot(
            data,
            showfliers=True,
            widths=0.55,
            patch_artist=True,
            medianprops=dict(color="red", alpha=1.0, linewidth=3),
            flierprops=dict(
                marker="x",
                markerfacecolor="grey",
                markeredgecolor="grey",
                markersize=4,
                alpha=0.8,
                linestyle="none",
            ),
        )
        for patch, color in zip(bp["boxes"], palette):
            patch.set_facecolor(color)
            patch.set_alpha(0.85)
        ax.set_xticks([1, 2], ["ASI", "ASI\nGenAI"])
        ax.set_yscale("log")
        ax.set_ylabel(ylabel, fontsize=fontsize)
        ax.set_xlabel("")
        ax.tick_params(axis="x", labelsize=fontsize - 2)
        ax.tick_params(axis="y", labelsize=fontsize - 2)
    fig.tight_layout()
    fig.savefig(output_eps, bbox_inches="tight", pad_inches=0.03)
    fig.savefig(output_pdf, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.write_manifest(
        "gpu_cpu_request_num_box_plot",
        ["asi_opensource_gpu_cpu_request_samples"],
        summary_path,
        output_eps,
        note="ASI trace side only; paper figure also includes external PAI and ACME baselines.",
    )
