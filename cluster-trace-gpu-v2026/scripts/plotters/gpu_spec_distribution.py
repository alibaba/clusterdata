"""Plot gpu_spec_distribution.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from . import common as c


def plot() -> None:
    df = c.read_csv("gpu_spec_distribution")
    output = c.OUT_DIR / "gpu_spec_distribution.pdf"
    summary = c.OUT_DIR / "gpu_spec_distribution.summary.csv"
    df = df.sort_values("gpu_spec_sum", ascending=False).copy()
    total = df["gpu_spec_sum"].sum()
    df["percentage"] = 100.0 * df["gpu_spec_sum"] / total if total else 0.0
    c.save_summary(df, summary)

    fig, ax = plt.subplots(figsize=(7, 4))
    fontsize = 24
    specs = df["display_gpu_spec"].tolist()
    counts = df["gpu_spec_sum"].astype(float).tolist()
    colors = plt.cm.Set3(np.linspace(0, 1, len(specs)))
    if c.squarify is not None and counts:
        rects = c.squarify.squarify(c.squarify.normalize_sizes(counts, 100, 100), 0, 0, 100, 100)
        ax.bar(
            [rect["x"] for rect in rects],
            [rect["dy"] for rect in rects],
            width=[rect["dx"] for rect in rects],
            bottom=[rect["y"] for rect in rects],
            color=colors,
            align="edge",
            linewidth=1.5,
            edgecolor="white",
        )
        label_y_offsets = {"XPU-C": -1.2, "A100": 1.0}
        for spec, count, rect in zip(specs, counts, rects):
            pct = 100.0 * count / total if total else 0.0
            if pct <= 2.5:
                continue
            ax.text(
                rect["x"] + rect["dx"] / 2,
                rect["y"] + rect["dy"] / 2 + label_y_offsets.get(spec, 0.0),
                f"{spec}\n{pct:.1f}%",
                ha="center",
                va="center",
                fontsize=fontsize - 2,
            )
        ax.text(97, 100, "Others", fontsize=fontsize - 2, ha="right", va="top", rotation=270)
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis("off")
    else:
        ax.bar(specs, counts, color=colors)
        ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.0)
    plt.close(fig)
    c.write_manifest("gpu_spec_distribution", ["asi_opensource_gpu_spec_distribution"], summary, output)
