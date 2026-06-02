"""Plot pod_resource_util_cdf.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import common as c


def plot() -> None:
    metrics = {
        "cpu_request_util": {
            "label": "CPU Request Utilization",
            "bins": np.linspace(0, 1.5, 601),
            "xlim": (-0.05, 1.5),
        },
        "memory_util": {
            "label": "Memory Utilization",
            "bins": np.linspace(0, 1.0, 501),
            "xlim": (-0.025, 1.0),
        },
        "gpu_sm_ratio": {
            "label": "GPU SM Utilization Ratio",
            "bins": np.linspace(0, 1.0, 501),
            "xlim": (-0.025, 1.0),
        },
        "gpu_memory_gib": {
            "label": "GPU Memory Used (GiB)",
            "bins": np.linspace(0, 1600, 801),
            "xlim": (-40, 1600),
        },
    }
    hists = {
        (job_type, metric): np.zeros(len(config["bins"]) - 1, dtype=np.int64)
        for job_type in c.PUBLIC_JOB_ORDER
        for metric, config in metrics.items()
    }
    stats = {
        (job_type, metric): {"count": 0, "sum": 0.0}
        for job_type in c.PUBLIC_JOB_ORDER
        for metric in metrics
    }
    for chunk in pd.read_csv(c.csv_path("pod_resource_util_samples"), chunksize=c.CSV_CHUNKSIZE):
        chunk = chunk[chunk["job_type"].isin(c.PUBLIC_JOB_ORDER)]
        for job_type, group in chunk.groupby("job_type", sort=False):
            for metric, config in metrics.items():
                c.update_hist(
                    hists[(job_type, metric)],
                    config["bins"],
                    group[metric],
                    stats[(job_type, metric)],
                )

    rows = []
    for job_type in c.PUBLIC_JOB_ORDER:
        for metric, config in metrics.items():
            rows.append(
                {
                    "job_type": job_type,
                    "metric": metric,
                    **c.hist_stats(hists[(job_type, metric)], config["bins"], stats[(job_type, metric)]),
                }
            )
    summary = pd.DataFrame(rows)
    output = c.OUT_DIR / "pod_resource_util_cdf.pdf"
    summary_path = c.OUT_DIR / "pod_resource_util_cdf.summary.csv"
    c.save_summary(summary, summary_path)

    fig, axs = plt.subplots(figsize=(10, 6), nrows=2, ncols=2)
    fontsize = 20
    positions = {
        "cpu_request_util": (0, 0),
        "memory_util": (0, 1),
        "gpu_sm_ratio": (1, 0),
        "gpu_memory_gib": (1, 1),
    }
    for metric, (row, col) in positions.items():
        ax = axs[row][col]
        config = metrics[metric]
        for job_type in c.PUBLIC_JOB_ORDER:
            x, y = c.cdf_from_hist(hists[(job_type, metric)], config["bins"])
            if x.size == 0:
                continue
            x = np.concatenate(([config["bins"][0]], x))
            y = np.concatenate(([0.0], y))
            ax.plot(x, y, label=c.JOB_LABELS[job_type], linestyle=c.LINE_STYLES[job_type], linewidth=2.5)
        ax.set_xlabel(config["label"], fontsize=fontsize)
        ax.set_xlim(*config["xlim"])
        ax.set_ylim(0, 1.05)
        ax.tick_params(axis="both", labelsize=fontsize - 2)
        ax.grid(True, alpha=0.3)
    axs[0][0].set_ylabel("CDF", fontsize=fontsize)
    axs[1][0].set_ylabel("CDF", fontsize=fontsize)
    axs[0][0].legend(loc="lower right", fontsize=fontsize - 2)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    c.write_manifest(
        "pod_resource_util_cdf",
        ["asi_opensource_pod_resource_util_samples"],
        summary_path,
        output,
        note="CDF curves are binned from downloaded sample rows; validation summaries are recomputed separately.",
    )
