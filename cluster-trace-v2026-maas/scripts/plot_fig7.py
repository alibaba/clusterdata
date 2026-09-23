from plot_common import WORKLOADS, axes, cdf, query, finish
from matplotlib.ticker import MaxNLocator

SQL = """
WITH app_day AS (
    SELECT workload, app_id, day, count(DISTINCT {column}) AS n, fsum(hours) AS hours
    FROM src WHERE cluster_id IS NOT NULL AND {gpu_filter}
    GROUP BY workload, app_id, day
)
SELECT workload, n, fsum(hours) AS hours
FROM app_day WHERE n > 0 AND hours > 0
GROUP BY workload, n ORDER BY workload, n
"""


def main():
    for panel, column, label, gpu_filter in [
        ("a", "cluster_id", "# Clusters per App", "gpu_type IS NOT NULL"),
        ("b", "gpu_type", "# GPU Types per App", "starts_with(gpu_type, 'gpu_')"),
    ]:
        rows = query(f"fig7_{panel}", SQL.format(column=column, gpu_filter=gpu_filter))
        fig, ax = axes(7, panel, f"({panel}) {label}")
        xmax = 1
        for group, legend, color in WORKLOADS:
            x, y = cdf([(r[1], r[2]) for r in rows if r[0] == group])
            if not len(x):
                continue
            ax.plot(x, y, label=legend, color=color)
            xmax = max(xmax, x[-1])
            at_one = y[x <= 1][-1]
            ax.scatter([1], [at_one], color=color, s=12)
            offset = (4, 5) if group == "online" else ((8, 6) if panel == "b" else (4, 12))
            ax.annotate(f"{at_one:.1f}%", (1, at_one), xytext=offset,
                        textcoords="offset points", color=color,
                        bbox={"facecolor": "white", "edgecolor": "none", "alpha": .8})
        ax.axvline(1, color="gray", linestyle="--", alpha=.8)
        ax.set_xlim(0, xmax)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=6))
        finish(fig, ax)


if __name__ == "__main__":
    main()
