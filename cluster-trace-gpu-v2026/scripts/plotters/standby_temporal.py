"""Plot standby_temporal.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from . import common as c


def plot() -> None:
    df = c.read_csv("standby_temporal")
    df["day"] = c.pd.to_numeric(df["day"], errors="coerce").astype(int)
    df["hour"] = c.pd.to_numeric(df["hour"], errors="coerce").astype(int)
    df = df.sort_values(["day", "hour"]).reset_index(drop=True)
    output = c.OUT_DIR / "standby_temporal.pdf"
    summary = c.OUT_DIR / "standby_temporal.summary.csv"
    c.save_summary(df, summary)

    fig, ax1 = plt.subplots(figsize=(10, 3))
    fontsize = 20
    x = np.arange(len(df))

    line1 = ax1.plot(
        x,
        df["standby_used_card_hour"].to_numpy(dtype=float),
        label="Standby GPU hour",
        linestyle="solid",
        linewidth=3,
        color="tab:blue",
    )
    ax1.set_xlabel("Hours from the beginning of a week (Mon. to Sun.)", fontsize=fontsize)
    ax1.set_ylabel("Standby GPU hour", fontsize=fontsize, color="tab:blue", loc="top")
    ax1.tick_params(axis="y", labelsize=fontsize, labelcolor="tab:blue")
    ax1.tick_params(axis="x", labelsize=fontsize)
    ax1.set_ylim(0, 11000)
    ax1_yticks = ax1.get_yticks()
    ax1.set_yticks(ax1_yticks)
    ax1.set_yticklabels([f"{int(tick / 1000)}K" for tick in ax1_yticks])
    ax1.yaxis.set_label_coords(-0.08, 1.25)

    ax2 = ax1.twinx()
    standby_util_capped = np.minimum(df["standby_util_9300"].to_numpy(dtype=float), 1.0) * 100.0
    line2 = ax2.plot(
        x,
        standby_util_capped,
        label="Over-Subscription Ratio",
        linestyle="dashed",
        linewidth=3,
        color="tab:orange",
    )
    ax2.set_ylabel("Percentage (%)", fontsize=fontsize, color="tab:orange", loc="top")
    ax2.tick_params(axis="y", labelsize=fontsize, labelcolor="tab:orange")
    ax2.set_ylim(0, 105)
    ax2.set_yticks([40, 60, 80, 100])
    ax2.yaxis.set_label_coords(1.09, 1.1)

    ax1.grid(True, linestyle="-", alpha=0.7)
    ax2.grid(True, linestyle="--", alpha=0.7)
    lines = line1 + line2
    ax1.legend(
        lines,
        [line.get_label() for line in lines],
        fontsize=fontsize,
        bbox_to_anchor=(-0.05, 0.9, 1.0, 0.0),
        ncols=2,
        handlelength=1.5,
        handletextpad=0.5,
        columnspacing=0.5,
        frameon=False,
    )
    ax1.set_xticks(np.arange(0, len(df) + 1, 24))

    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.write_manifest("standby_temporal", ["asi_opensource_standby_temporal"], summary, output)
