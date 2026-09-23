from plot_common import WORKLOADS, axes, query, finish
import numpy as np

VARIANTS = """
WITH variants AS (
    SELECT workload, base_id,
           max(CASE WHEN left(model_id, 2) IN ('b_', 'x_') THEN 1 ELSE 0 END)
           + count(DISTINCT CASE WHEN left(model_id, 2) IN ('s_', 'x_') THEN model_id END) AS n
    FROM src WHERE base_id IS NOT NULL AND model_id IS NOT NULL
    GROUP BY workload, base_id
)
SELECT workload, n, count(*) FROM variants WHERE n > 0
GROUP BY workload, n ORDER BY workload, n
"""
CONCENTRATION = """
SELECT workload, model_key, fsum(hours) AS hours
FROM src GROUP BY workload, model_key
ORDER BY workload, hours DESC NULLS LAST, model_key
"""


def main():
    fig, ax = axes(12, "a", "(a) # Variants per Base Model", "CDF of Base Models (%)")
    rows = query("fig12_a", VARIANTS)
    for group, label, color in WORKLOADS:
        values = np.array([r[1] for r in rows if r[0] == group])
        counts = np.array([r[2] for r in rows if r[0] == group], dtype=int)
        x = np.repeat(values, counts)
        if len(x):
            ax.plot(x, np.arange(1, len(x) + 1) / len(x) * 100, label=label, color=color)
    ax.set_xscale("symlog", linthresh=1)
    finish(fig, ax)

    rows = query("fig12_b", CONCENTRATION)
    fig, ax = axes(12, "b", "(b) Fraction of Model Variants (%)")
    for i, (group, label, color) in enumerate(WORKLOADS):
        weights = np.array([r[2] or 0 for r in rows if r[0] == group])
        if not len(weights) or weights.sum() <= 0:
            continue
        x = np.arange(1, len(weights) + 1) / len(weights) * 100
        y = np.cumsum(weights) / weights.sum() * 100
        ax.plot(x, y, label=label, color=color)
        value = np.interp(10, x, y)
        ax.scatter([10], [value], color=color, s=12)
        ax.annotate(f"{value:.1f}%", (10, value), xytext=(10, -12 if i == 0 else -2),
                    textcoords="offset points", va="bottom" if i == 0 else "top", color=color,
                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": .85},
                    arrowprops={"arrowstyle": "-", "color": color, "lw": .8})
    ax.axvline(10, color="gray", linestyle=":")
    ax.set(xlim=(0, 100), xticks=np.arange(0, 101, 20))
    finish(fig, ax)


if __name__ == "__main__":
    main()
