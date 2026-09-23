from plot_common import axes, draw_hot, model_marks, query, finish

DURATION = """
WITH durations AS (
    SELECT s.workload, h.temperature, s.instance_id,
           fsum(s.hours / s.gpu_count) AS duration
    FROM src s JOIN hot_models h USING (workload, model_key)
    WHERE s.instance_id IS NOT NULL AND s.hours IS NOT NULL AND s.gpu_count > 0
    GROUP BY s.workload, h.temperature, s.instance_id
)
SELECT workload, temperature, floor(duration * 100) / 100.0 + 0.005 AS x, count(*)
FROM durations WHERE floor(duration * 100) / 100.0 + 0.005 >= 0
GROUP BY workload, temperature, x ORDER BY workload, temperature, x
"""
SIZE = """
SELECT s.workload, h.temperature, s.params_b, fsum(s.hours)
FROM src s JOIN hot_models h USING (workload, model_key)
WHERE s.hours > 0 AND s.params_b > 0 AND s.params_b <= 1050
GROUP BY s.workload, h.temperature, s.params_b
ORDER BY s.workload, h.temperature, s.params_b
"""


def main():
    fig, ax = axes(13, "a", "(a) Instance Duration (Hours)", "CDF of Instances (%)")
    draw_hot(ax, query("fig13_a", DURATION, hot=True), percentile=99.9)
    ax.set_xscale("symlog", linthresh=1)
    endpoints = [line.get_xdata()[-1] for line in ax.lines if len(line.get_xdata())]
    if endpoints:
        ax.set_xlim(0, max(endpoints))
    finish(fig, ax, legend=False)
    fig, ax = axes(13, "b", "(b) Model Size (B)")
    draw_hot(ax, query("fig13_b", SIZE, hot=True))
    model_marks(ax)
    finish(fig, ax, legend=False)


if __name__ == "__main__":
    main()
