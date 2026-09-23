from common import query, save

import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator
import numpy as np

STYLES = [("online", "Online", "#4C78A8"), ("offline", "Offline", "#F58518")]
SOURCE = """
SELECT day, app_id, instance_id, workload, cluster_id, gpu_type,
       gpu_hours AS hours
FROM daily
WHERE workload IN ('online', 'offline')
"""
QUERIES = {
    "left": f"""
        WITH src AS ({SOURCE})
        SELECT workload, fsum(hours) AS hours
        FROM src GROUP BY workload, app_id
        ORDER BY workload, hours DESC NULLS LAST, app_id
    """,
    "right": f"""
        WITH src AS ({SOURCE}), app_day AS (
            SELECT workload, app_id, day,
                   count(DISTINCT instance_id) AS instances, fsum(hours) AS hours
            FROM src WHERE cluster_id IS NOT NULL AND gpu_type IS NOT NULL
            GROUP BY workload, app_id, day
        )
        SELECT workload, instances, fsum(hours) AS hours
        FROM app_day WHERE instances > 0 AND hours > 0
        GROUP BY workload, instances ORDER BY workload, instances
    """,
}


def load_data(panel):
    return query(f"fig6_{panel}", QUERIES[panel])


def plot_left(rows):
    fig, ax = plt.subplots(figsize=(7, 4))
    for i, (group, label, color) in enumerate(STYLES):
        hours = np.array([r[1] if r[1] is not None else 0 for r in rows if r[0] == group])
        x = np.arange(1, len(hours) + 1) / len(hours) * 100
        y = np.cumsum(hours) / hours.sum() * 100
        ax.plot(x, y, color=color, label=label)
        value = np.interp(10, x, y)
        ax.scatter([10], [value], color=color, s=12, zorder=4)
        ax.annotate(f"{value:.1f}%", (10, value), xytext=(10, -12 if i == 0 else -2),
                    textcoords="offset points", ha="left", va="bottom" if i == 0 else "top",
                    color=color, bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.85},
                    arrowprops={"arrowstyle": "-", "color": color, "lw": 0.8})
    ax.axvline(10, color="gray", linestyle=":", alpha=0.9)
    ax.set(xlabel="(a) Fraction of Apps (%)", ylabel="CDF of GPU Time (%)",
           xlim=(0, 100), ylim=(0, 102), xticks=np.arange(0, 101, 20))
    ax.grid(alpha=0.2)
    ax.legend(loc="lower right", frameon=False)
    return fig


def plot_right(rows):
    fig, ax = plt.subplots(figsize=(7, 4))
    xmax = 1
    for group, label, color in STYLES:
        points = [r for r in rows if r[0] == group]
        x = np.array([r[1] for r in points])
        weights = np.array([r[2] for r in points])
        ax.plot(x, np.cumsum(weights) / weights.sum() * 100, color=color, label=label)
        xmax = max(xmax, x.max())
    ax.set(xlabel="(b) # Instances per App", ylabel="CDF of GPU Time (%)",
           xscale="log", xlim=(1, xmax if xmax > 1 else 10), ylim=(0, 102))
    ax.xaxis.set_major_locator(FixedLocator([1, 10, 100, 1000, 10000, 100000]))
    ax.grid(which="both", alpha=0.2)
    ax.legend(loc="lower right", frameon=False)
    return fig


if __name__ == "__main__":
    save(plot_left(load_data("left")), "fig06a")
    save(plot_right(load_data("right")), "fig06b")
