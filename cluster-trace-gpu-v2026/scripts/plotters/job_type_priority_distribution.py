"""Plot job_type_priority_distribution.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import common as c


def plot() -> None:
    df = c.read_csv("job_type_priority_used_hours")
    output = c.OUT_DIR / "job_type_priority_distribution.pdf"
    summary = c.OUT_DIR / "job_type_priority_distribution.summary.csv"

    rows = []
    for job_type in c.PAPER_JOB_ORDER:
        cur = df[df["job_type"].eq(job_type)]
        hp = float(cur["used_card_hour_sum_p9300"].sum())
        lp = float(cur["used_card_hour_sum_p9200_9300"].sum())
        total = hp + lp
        rows.append(
            {
                "job_type": c.PAPER_JOB_LABELS[job_type],
                "hp_used_card_hour": hp,
                "lp_used_card_hour": lp,
                "hp_percentage": 100.0 * hp / total if total else 0.0,
                "lp_percentage": 100.0 * lp / total if total else 0.0,
            }
        )
    summary_df = pd.DataFrame(rows)
    c.save_summary(summary_df, summary)

    fig, ax = plt.subplots(figsize=(7, 4))
    fontsize = 28
    x = np.arange(len(summary_df))
    width = 0.35
    bars1 = ax.bar(x - width / 2, summary_df["hp_percentage"], width, label="HP")
    bars2 = ax.bar(x + width / 2, summary_df["lp_percentage"], width, label="LP")
    label_x_offsets = {
        ("LP", "Offline-inference"): -0.08,
        ("HP", "Dev"): 0.08,
    }
    for priority_name, bars in [("HP", bars1), ("LP", bars2)]:
        for idx, bar in enumerate(bars):
            height = bar.get_height()
            job_type_label = summary_df.iloc[idx]["job_type"]
            ax.text(
                bar.get_x() + bar.get_width() / 2 + label_x_offsets.get((priority_name, job_type_label), 0.0),
                height + 0.8,
                f"{height:.1f}%",
                ha="center",
                va="bottom",
                fontsize=fontsize - 6,
                clip_on=False,
            )
    ax.tick_params(axis="both", labelsize=fontsize - 6)
    ax.set_ylabel("Percentage", fontsize=fontsize)
    ax.set_ylim(0, 106)
    ax.set_xticks(x)
    ax.set_xticklabels([c.PAPER_SHORT_JOB_LABELS[job_type] for job_type in c.PAPER_JOB_ORDER], fontsize=fontsize - 2)
    ax.legend(
        loc="upper center",
        fontsize=fontsize - 2,
        handlelength=1.5,
        bbox_to_anchor=(0.5, 0.8),
        frameon=True,
        handletextpad=0.5,
    )
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.write_manifest("job_type_priority_distribution", ["asi_opensource_job_type_priority_used_hours"], summary, output)
