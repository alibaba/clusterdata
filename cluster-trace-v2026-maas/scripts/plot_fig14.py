from plot_common import HOT_COLORS, axes, draw_hot, hot_legend, query, finish
import numpy as np
from matplotlib.lines import Line2D

BUCKETS = " UNION ALL ".join(f"""
SELECT '{metric}' AS metric, s.workload, h.temperature,
       (least(floor(({value}) / 0.2), 499) + 0.5) * 0.2 AS x, fsum(s.hours)
    FROM src s JOIN hot_models h USING (workload, model_key)
    WHERE s.hours > 0 AND ({value}) BETWEEN 0 AND 100
GROUP BY s.workload, h.temperature, x
""" for metric, value in [
    ("sm", "s.sm_util"), ("memory", "s.gpu_mem_util"),
    ("zero", "CASE WHEN s.samples > 0 THEN 100.0 * s.zero_samples / s.samples END"),
]) + " ORDER BY metric, workload, temperature, x"
IDLE = """
WITH totals AS (
    SELECT s.workload, h.temperature, fsum(s.hours) AS hours,
           fsum(CASE WHEN s.sm_util < 5 AND s.gpu_mem_util > 80 THEN s.hours ELSE 0 END) AS a,
           fsum(CASE WHEN s.sm_util < 5 AND s.gpu_mem_util > 90 THEN s.hours ELSE 0 END) AS b,
           fsum(CASE WHEN s.sm_util < 10 AND s.gpu_mem_util > 80 THEN s.hours ELSE 0 END) AS c,
           fsum(CASE WHEN s.sm_util < 10 AND s.gpu_mem_util > 90 THEN s.hours ELSE 0 END) AS d
    FROM src s JOIN hot_models h USING (workload, model_key)
    WHERE s.hours > 0 GROUP BY s.workload, h.temperature
)
SELECT workload, temperature, t.sm, t.mem, 100.0 * t.idle / hours AS ratio
FROM totals CROSS JOIN LATERAL (VALUES (5, 80, a), (5, 90, b),
                                         (10, 80, c), (10, 90, d)) t(sm, mem, idle)
"""
THRESHOLDS = [(5, 80, "o"), (5, 90, "s"), (10, 80, "^"), (10, 90, "D")]


def main():
    rows = query("fig14_cdfs", BUCKETS, hot=True)
    for panel, metric, label in [("a", "sm", "SM Utilization (%)"),
                                  ("b", "zero", "Zero Utilization Ratio (%)"),
                                  ("c", "memory", "GPU Memory Utilization (%)")]:
        fig, ax = axes(14, panel, f"({panel}) {label}")
        draw_hot(ax, [r[1:] for r in rows if r[0] == metric])
        ax.set(xlim=(0, 100), xticks=np.arange(0, 101, 25))
        finish(fig, ax, legend=False)

    rows = query("fig14_d", IDLE, hot=True)
    fig, ax = axes(14, "d", "(d) Mem-Idle GPU Time Ratio", "Ratio (%)")
    groups = [(w, t) for w in ["online", "offline"] for t in ["Hot", "Cold"]]
    positions = np.linspace(-.18, .18, len(THRESHOLDS))
    values = {(r[0], r[1], r[2], r[3]): r[4] for r in rows}
    for i, (workload, temp) in enumerate(groups):
        for offset, (sm, mem, marker) in zip(positions, THRESHOLDS):
            value = values.get((workload, temp, sm, mem))
            if value is not None:
                ax.scatter(i + offset, value, marker=marker, color=HOT_COLORS[temp],
                           edgecolor="black", linewidth=.4, s=28, zorder=3)
    hot_legend(ax)
    ax.add_artist(ax.get_legend())
    handles = [Line2D([], [], marker=m, color="gray", markeredgecolor="black",
                      linestyle="none", label=f"{sm}/{mem}") for sm, mem, m in THRESHOLDS]
    ax.legend(handles=handles, title="SM/Mem", frameon=False, loc="upper right")
    ax.set(xticks=range(4), xticklabels=["Online", "Online", "Offline", "Offline"],
           ylim=(0, 75), yticks=np.arange(0, 76, 15))
    finish(fig, ax, legend=False)


if __name__ == "__main__":
    main()
