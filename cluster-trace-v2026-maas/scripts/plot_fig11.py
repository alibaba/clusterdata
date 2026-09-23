from plot_common import WORKLOADS, axes, draw_groups, model_marks, query, finish
import numpy as np

SIZE = """
SELECT workload, params_b, fsum(hours)
FROM src WHERE params_b > 0 AND params_b <= 1050
GROUP BY workload, params_b HAVING fsum(hours) >= 0
ORDER BY workload, params_b
"""
SM = """
SELECT workload, (least(floor(sm_util / 0.2), 499) + 0.5) * 0.2 AS x, fsum(hours)
FROM src WHERE hours > 0 AND sm_util BETWEEN 0 AND 100
GROUP BY workload, x ORDER BY workload, x
"""


def main():
    fig, ax = axes(11, "c", "(c) Model Size (B)")
    draw_groups(ax, query("fig11_c", SIZE),
                [("online", "Online", "steelblue"), ("offline", "Offline", "darkorange")])
    model_marks(ax)
    finish(fig, ax)

    fig, ax = axes(11, "d", "(d) SM Utilization (%)")
    draw_groups(ax, query("fig11_d", SM), WORKLOADS)
    ax.set(xlim=(0, 100), xticks=np.arange(0, 101, 25))
    finish(fig, ax)


if __name__ == "__main__":
    main()
