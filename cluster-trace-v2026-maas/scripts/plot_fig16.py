from plot_common import ROLES, axes, cdf, draw_groups, query, finish
import numpy as np

RESOURCES = """
WITH metrics AS (
    SELECT pd_role, hours, v.metric, v.value
    FROM src CROSS JOIN LATERAL (VALUES
        ('sm', sm_util), ('memory', gpu_mem_alloc), ('gpus', trunc(gpu_count))
    ) v(metric, value)
    WHERE workload = 'online' AND hours > 0
)
SELECT metric, pd_role,
       CASE WHEN metric = 'sm' THEN (least(floor(value / 0.2), 499) + 0.5) * 0.2
            WHEN metric = 'memory' THEN (least(floor(value / 3.2), 499) + 0.5) * 3.2
            ELSE value END AS x, fsum(hours)
FROM metrics
WHERE (metric = 'sm' AND value BETWEEN 0 AND 100)
   OR (metric = 'memory' AND value BETWEEN 0 AND 1600)
   OR (metric = 'gpus' AND value BETWEEN 0 AND 8 AND value <> 7)
GROUP BY metric, pd_role, x ORDER BY metric, pd_role, x
"""
RATIO = """
WITH app_site_day AS (
    SELECT day, app_id, site_id, fsum(hours) AS hours,
           fsum(CASE WHEN pd_role = 'prefill' THEN hours ELSE 0 END) AS prefill,
           fsum(CASE WHEN pd_role = 'decode' THEN hours ELSE 0 END) AS decode
    FROM src WHERE workload = 'online' AND pd_role IN ('prefill', 'decode')
    GROUP BY day, app_id, site_id
)
SELECT greatest(0.1, least(10.0, prefill / decode)) AS ratio, fsum(hours)
FROM app_site_day WHERE prefill > 0 AND decode > 0 AND hours > 0
GROUP BY ratio ORDER BY ratio
"""


def main():
    rows = query("fig16_resources", RESOURCES)
    for panel, metric, label, maximum, step in [
        ("a", "sm", "SM Utilization (%)", 100, 25),
        ("b", "memory", "GPU Memory Alloc. (GB)", 1600, 400),
        ("c", "gpus", "# GPUs Alloc. per Instance", 8, 1),
    ]:
        points = [r[1:] for r in rows if r[0] == metric]
        fig, ax = axes(16, panel, f"({panel}) {label}")
        draw_groups(ax, points, ROLES, marker="o" if metric == "gpus" else None)
        ax.set(xlim=(0, maximum), xticks=np.arange(0, maximum + 1, step))
        finish(fig, ax)

    fig, ax = axes(16, "d", "(d) P/D GPU Time Ratio")
    points = query("fig16_d", RATIO)
    origin = 0.1 if points and points[0][0] > 0.1 else None
    x, y = cdf(points, origin=origin)
    ax.plot(x, y, color="firebrick")
    ax.axvline(1, color="gray", linestyle=":", alpha=.8)
    ax.set(xscale="log", xlim=(.1, 10), xticks=[.1, .2, .5, 1, 2, 5, 10],
           xticklabels=["1:10", "1:5", "1:2", "1:1", "2:1", "5:1", "10:1"])
    ax.minorticks_off()
    finish(fig, ax, legend=False)


if __name__ == "__main__":
    main()
