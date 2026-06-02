"""Plot job_type_distribution.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import common as c


def plot() -> None:
    df = c.read_csv("job_type_used_hours")
    output = c.OUT_DIR / "job_type_distribution.pdf"
    summary = c.OUT_DIR / "job_type_distribution.summary.csv"

    values = {
        c.PAPER_JOB_LABELS[job_type]: float(df.loc[df["job_type"].eq(job_type), "sum_used_card_hour"].sum())
        for job_type in c.PAPER_JOB_ORDER
    }
    values["Other"] = float(df["sum_used_card_hour"].sum()) - sum(values.values())
    sorted_data = sorted(values.items(), key=lambda kv: kv[1], reverse=True)
    total = sum(value for _label, value in sorted_data)
    summary_df = pd.DataFrame(
        [
            {"job_type": label, "used_card_hour": value, "percentage": 100.0 * value / total if total else 0.0}
            for label, value in sorted_data
        ]
    )
    c.save_summary(summary_df, summary)

    fig, ax = plt.subplots(figsize=(7, 4))
    fontsize = 24
    labels = [f"{label}\n{100.0 * value / total:.1f}%" for label, value in sorted_data]
    sizes = [value for _label, value in sorted_data]
    colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
    if c.squarify is not None:
        c.squarify.plot(
            sizes=sizes,
            label=labels,
            color=colors,
            ax=ax,
            text_kwargs={"fontsize": fontsize - 2},
            linewidth=1.5,
            edgecolor="white",
        )
        ax.axis("off")
    else:
        ax.bar(labels, sizes, color=colors)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.0)
    plt.close(fig)
    c.write_manifest("job_type_distribution", ["asi_opensource_job_type_used_hours"], summary, output)
