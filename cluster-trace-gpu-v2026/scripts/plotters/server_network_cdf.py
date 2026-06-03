"""Plot server_network_cdf.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator
import numpy as np
import pandas as pd

from . import common as c


def plot() -> None:
    df = c.read_csv("server_network_samples")
    output = c.OUT_DIR / "server_network_cdf.pdf"
    summary = c.OUT_DIR / "server_network_cdf.summary.csv"

    rows = []
    fig, axs = plt.subplots(1, 2, figsize=(14, 3.5), sharey=True)
    fontsize = 24
    legend_handles = []
    legend_labels = []
    for job_type in c.NETWORK_JOB_ORDER:
        cur = df[df["job_types"].eq(job_type)]
        if cur.empty:
            continue
        rx = pd.to_numeric(cur["server_receive_bps"], errors="coerce").to_numpy(dtype=float)
        tx = pd.to_numeric(cur["server_transmit_bps"], errors="coerce").to_numpy(dtype=float)
        rx = rx[np.isfinite(rx) & (rx > 0.001)]
        tx = tx[np.isfinite(tx) & (tx > 0.001)]

        x, y = c.cdf_from_array(rx)
        if x.size:
            lines = axs[0].plot(
                x,
                y,
                label=c.NETWORK_JOB_LABELS[job_type],
                linestyle=c.NETWORK_LINE_STYLES[job_type],
                color=c.NETWORK_LINE_COLORS[job_type],
                linewidth=2.5,
            )
            if lines:
                legend_handles.append(lines[0])
                legend_labels.append(c.NETWORK_JOB_LABELS[job_type])

        x, y = c.cdf_from_array(tx)
        if x.size:
            axs[1].plot(
                x,
                y,
                label=c.NETWORK_JOB_LABELS[job_type],
                linestyle=c.NETWORK_LINE_STYLES[job_type],
                color=c.NETWORK_LINE_COLORS[job_type],
                linewidth=2.5,
            )

        rows.append(
            {
                "job_types": job_type,
                "server_count": int(len(cur)),
                "rx_p50_gibps": float(np.percentile(rx, 50)) if rx.size else np.nan,
                "rx_p95_gibps": float(np.percentile(rx, 95)) if rx.size else np.nan,
                "tx_p50_gibps": float(np.percentile(tx, 50)) if tx.size else np.nan,
                "tx_p95_gibps": float(np.percentile(tx, 95)) if tx.size else np.nan,
            }
        )

    for ax in axs:
        ax.set_xscale("log", base=10)
        ax.set_xlim(1e-3, 1e1)
        ax.set_xticks([1e-3, 1e-2, 1e-1, 1e0])
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10), numticks=100))
        ax.tick_params(axis="x", labelsize=fontsize, which="major")
        ax.tick_params(axis="y", labelsize=fontsize)
        ax.grid(True)
    axs[0].set_ylabel("CDF", fontsize=fontsize)
    axs[0].set_xlabel("Receive traffic (GiB/s)", fontsize=fontsize)
    axs[1].set_xlabel("Transmit traffic (GiB/s)", fontsize=fontsize)
    fig.legend(
        legend_handles,
        legend_labels,
        fontsize=fontsize - 2,
        ncol=6,
        bbox_to_anchor=(0.5, 0.92),
        loc="lower center",
        frameon=False,
        handlelength=1.5,
        handletextpad=0.1,
        columnspacing=0.3,
    )
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
    c.save_summary(pd.DataFrame(rows), summary)
    c.write_manifest(
        "server_network_cdf",
        ["asi_opensource_pod_hourly", "asi_opensource_server_hourly", "asi_opensource_network_hourly"],
        summary,
        output,
        note="Derived locally from final fact tables; network_hourly is not a pre-materialized paper aggregate.",
    )
