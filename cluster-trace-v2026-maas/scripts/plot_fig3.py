from common import query, save
from collections import defaultdict
from math import fsum

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

SQL = """
SELECT gpu_type, workload,
       fsum(gpu_hours) AS gpu_hours
FROM daily
WHERE workload IN ('online', 'offline')
  AND starts_with(gpu_type, 'gpu_')
GROUP BY gpu_type, workload
ORDER BY gpu_type, workload
"""


def load_data():
    return query("fig3", SQL)


def series(rows):
    by_gpu = defaultdict(lambda: [0.0, 0.0])
    for gpu, workload, hours in rows:
        if hours is None or not np.isfinite(hours) or hours < 0:
            raise ValueError("Expected nonnegative GPU-hours")
        column = ("online", "offline").index(workload)
        by_gpu[gpu][column] += hours
    order = sorted(by_gpu, key=lambda gpu: (-fsum(by_gpu[gpu]), gpu))
    hours = np.array([by_gpu[gpu] for gpu in order], dtype=float).reshape(-1, 2)
    totals = np.array([fsum(hours[:, i]) for i in range(2)])
    if np.any(totals <= 0):
        raise ValueError("Both workloads must have positive total GPU-hours")
    cumulative = np.cumsum(hours, axis=0) / totals * 100
    return order, hours, cumulative


def plot_left(rows):
    order, _, cumulative = series(rows)
    x = np.arange(1, len(order) + 1)
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, label in enumerate(["Online", "Offline"]):
        ax.plot(x, cumulative[:, i], color=["#4C78A8", "#F58518"][i],
                marker="o", markersize=2, label=label)
    ax.set(xlabel="(a) GPU Types Sorted",
           ylabel="CDF of GPU Time (%)", xlim=(0.5, len(order) + 0.5), ylim=(0, 102))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="lower right", frameon=False)
    return fig


def online_share(rows):
    order, hours, _ = series(rows)
    keep = [i for i in range(len(order)) if fsum(hours[i]) > 0]
    known = hours[keep]
    return [order[i] for i in keep], known[:, 0] / known.sum(axis=1) * 100


def plot_right(rows):
    order, percentage = online_share(rows)
    if not order:
        raise ValueError("No known GPU types with positive GPU-hours")
    x = np.arange(1, len(order) + 1)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(x, percentage, color="#4C78A8", marker="o", markersize=2)
    ax.axhline(50, color="grey", linestyle=":", linewidth=1)
    ax.set(xlabel="(b) GPU Types Sorted",
           ylabel="Online GPU Time (%)", xlim=(0.5, len(order) + 0.5), ylim=(0, 100))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.2)
    return fig


if __name__ == "__main__":
    rows = load_data()
    save(plot_left(rows), "fig03a")
    save(plot_right(rows), "fig03b")
