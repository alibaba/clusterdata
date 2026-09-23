from common import query, save
from collections import defaultdict
from math import fsum

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

SQL = """
WITH src AS (
    SELECT gpu_type, cluster_id, workload,
           gpu_hours AS hours,
           sm_util AS sm
    FROM daily
    WHERE workload IN ('online', 'offline')
      AND starts_with(gpu_type, 'gpu_')
      AND cluster_id IS NOT NULL AND cluster_id <> ''
)
SELECT gpu_type, cluster_id,
       CASE WHEN sm IS NULL THEN -2
            WHEN sm BETWEEN 0 AND 100 THEN least(CAST(floor(sm / 0.1) AS INTEGER), 999)
            ELSE -1 END AS bucket,
       fsum(hours) AS gpu_hours,
       fsum(CASE WHEN workload = 'online' THEN hours ELSE 0 END) AS online_hours,
       count(*) AS records
FROM src WHERE hours > 0
GROUP BY gpu_type, cluster_id, bucket
ORDER BY gpu_type, cluster_id, bucket;
"""
COLORS = plt.get_cmap("tab10").colors[:5]
MARKERS = ["o", "s", "^", "D", "P"]


def load_data():
    return query("fig4", SQL)


def ranking(rows):
    weights = defaultdict(list)
    for gpu, cluster, bucket, hours, online, records in rows:
        if bucket != -2:
            weights[gpu].append(hours)
    totals = {gpu: fsum(values) for gpu, values in weights.items()}
    return sorted(totals, key=lambda gpu: (-totals[gpu], gpu))


def prepare(rows):
    top = ranking(rows)[:5]
    if len(top) != 5:
        raise ValueError("Expected at least five GPU types with non-NULL SM")
    pairs = defaultdict(list)
    for gpu, cluster, bucket, hours, online, records in rows:
        if gpu in top:
            pairs[gpu, cluster].append((bucket, hours, online, records))
    result = []
    for (gpu, cluster), bins in pairs.items():
        total = fsum(b[1] for b in bins)
        valid = sorted(b for b in bins if b[0] >= 0)
        weight = fsum(b[1] for b in valid)
        count = sum(b[3] for b in valid)
        if total < 1000 or weight < 100 or count < 20:
            continue
        index = np.searchsorted(np.cumsum([b[1] for b in valid]), weight / 2)
        median = (valid[index][0] + 0.5) * 0.1
        result.append(dict(gpu=gpu, cluster=cluster, hours=total,
                           online=100 * fsum(b[2] for b in bins) / total,
                           median=median))
    result.sort(key=lambda r: (top.index(r["gpu"]), -r["hours"], r["cluster"]))
    if any(not any(r["gpu"] == gpu for r in result) for gpu in top):
        raise ValueError("A selected GPU has no clusters passing the filters")
    sizes = np.sqrt([r["hours"] for r in result])
    sizes = 10 + 55 * (sizes - sizes.min()) / np.ptp(sizes) if np.ptp(sizes) else np.full(len(sizes), 80)
    for row, size in zip(result, sizes):
        row["size"] = size
    return top, result


def legend(ax):
    handles = [Line2D([], [], marker=m, color="none", markerfacecolor=c,
                      markeredgecolor="white", markersize=5, label=f"GPU-{chr(65+i)}")
               for i, (c, m) in enumerate(zip(COLORS, MARKERS))]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 1.16),
              ncol=5, frameon=False)


def plot_left(top, rows):
    fig, ax = plt.subplots(figsize=(7, 4))
    values = [[r["median"] for r in rows if r["gpu"] == gpu] for gpu in top]
    boxes = ax.boxplot(values, patch_artist=True, showfliers=False, whis=(5, 95),
                       medianprops={"color": "black"})
    for patch, color in zip(boxes["boxes"], COLORS):
        patch.set_facecolor(color)
        patch.set_alpha(0.55)
    ax.set_xticks(range(1, 6), [f"GPU-{chr(65+i)}" for i in range(5)])
    ax.set(xlabel="(a) Top 5 GPUs", ylabel="SM Utilization (%)", ylim=(0, 80))
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    legend(ax)
    return fig


def plot_right(top, rows):
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, gpu in enumerate(top):
        group = [r for r in rows if r["gpu"] == gpu]
        threshold = 0.01 * fsum(r["hours"] for r in group)
        shown = [r for r in group if r["hours"] >= threshold]
        ax.scatter([r["online"] for r in shown], [r["median"] for r in shown],
                   s=[r["size"] for r in shown], color=COLORS[i], marker=MARKERS[i],
                   alpha=0.78, edgecolors="white", linewidths=0.5)
    ax.set(xlabel="Online GPU Time Ratio (%)\n(b) GPU Type per Cluster",
           ylabel="Median SM Util. (%)", xlim=(-2, 102), ylim=(0, 80))
    ax.grid(alpha=0.2)
    ax.set_axisbelow(True)
    legend(ax)
    return fig


if __name__ == "__main__":
    top, rows = prepare(load_data())
    save(plot_left(top, rows), "fig04a")
    save(plot_right(top, rows), "fig04b")
