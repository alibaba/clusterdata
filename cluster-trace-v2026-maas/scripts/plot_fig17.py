from plot_common import ARCHES, axes, draw_groups, model_marks, query, finish

SIZE = """
SELECT model_arch, params_b, fsum(hours)
FROM src WHERE params_b > 0 AND params_b <= 1050 AND model_arch IN ('dense', 'moe')
GROUP BY model_arch, params_b HAVING fsum(hours) >= 0
ORDER BY model_arch, params_b
"""
GPUS = """
SELECT model_arch, trunc(gpu_count) AS n, fsum(hours)
FROM src WHERE hours > 0 AND model_arch IN ('dense', 'moe')
    AND trunc(gpu_count) BETWEEN 0 AND 8 AND trunc(gpu_count) <> 7
GROUP BY model_arch, n ORDER BY model_arch, n
"""

MEMORY = """
SELECT model_arch, (least(floor(gpu_mem_alloc / 3.2), 499) + 0.5) * 3.2 AS x,
       fsum(hours)
FROM src WHERE hours > 0 AND model_arch IN ('dense', 'moe')
    AND gpu_mem_alloc BETWEEN 0 AND 1600
GROUP BY model_arch, x ORDER BY model_arch, x
"""


def main():
    fig, ax = axes(17, "a", "(a) Model Size (B)")
    draw_groups(ax, query("fig17_a", SIZE), ARCHES)
    model_marks(ax, [(3, 86), (8, 86), (32, 86), (235, 46), (706, 46)])
    finish(fig, ax)

    fig, ax = axes(17, "c", "(c) GPU Memory Alloc. (GB)")
    draw_groups(ax, query("fig17_c", MEMORY), ARCHES)
    ax.set(xlim=(0, 1600), xticks=range(0, 1601, 400))
    finish(fig, ax)

    fig, ax = axes(17, "d", "(d) # GPUs Alloc. per Instance")
    draw_groups(ax, query("fig17_d", GPUS), ARCHES, marker="o")
    ax.set(xlim=(0, 8), xticks=range(9))
    finish(fig, ax)


if __name__ == "__main__":
    main()
