from common import query, save
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

METRICS = [("sm_util", "SM Utilization (%)"),
           ("gpu_mem_util", "GPU Memory Utilization (%)"),
           ("cpu_usage", "CPU Cores Usage"),
           ("mem_usage", "Host Memory Usage (GB)")]
MEANS = ", ".join(
    f"fsum({c} * gpu_hours) / nullif(fsum(CASE WHEN {c} IS NOT NULL THEN gpu_hours ELSE 0 END), 0) AS {c}"
    for c, _ in METRICS)
DAILY = f"""
SELECT day, workload, {MEANS}
FROM src WHERE gpu_hours > 0
GROUP BY day, workload ORDER BY day, workload
"""
WORKLOAD = """
CREATE TEMP TABLE week_workload AS
SELECT instance_id, day, min(workload) AS workload,
       count(DISTINCT workload) AS labels, count(*) - count(workload) AS null_labels
FROM daily WHERE day BETWEEN 140 AND 146 GROUP BY instance_id, day;
SELECT CASE WHEN count(*) > 0 THEN error('Ambiguous instance-day workload') ELSE 0 END
FROM week_workload WHERE labels <> 1 OR null_labels > 0;
"""
WEEK_MEANS = ", ".join(
    f"fsum(CASE WHEN weight > 0 THEN {c} * weight END) / "
    f"nullif(fsum(CASE WHEN weight > 0 AND {c} IS NOT NULL THEN weight END), 0) AS {c}"
    for c, _ in METRICS)
WEEK = f"""
WITH labeled AS (
    SELECT w.*, d.workload, w.gpu_count * w.samples AS weight
    FROM week w LEFT JOIN week_workload d
      ON w.instance_id = d.instance_id AND w.time_s // 86400 = d.day
)
SELECT (time_s // 1800) * 1800 AS time_30m, workload, {WEEK_MEANS}
FROM labeled GROUP BY time_30m, workload ORDER BY time_30m, workload
"""


def plot(rows, metric_index):
    field, title = METRICS[metric_index]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    for group, label, color in [("online", "Online", "#4C78A8"),
                                 ("offline", "Offline", "#F58518")]:
        values = [r for r in rows if r[1] == group]
        ax.plot([r[0] for r in values], [r[metric_index + 2] for r in values],
                color=color, linewidth=1, alpha=0.85, label=label)
    ax.axvspan(140, 147, color="gray", alpha=0.2)
    ax.set(title=title, xlabel="6-Month", xticks=[],
           xlim=(min(r[0] for r in rows), max(r[0] for r in rows)))
    ax.margins(y=0.08)
    if field == "sm_util":
        ax.set(ylim=(10, 70), yticks=[10, 30, 50, 70])
    ax.grid(axis="y", alpha=0.2)
    ax.legend(frameon=False)
    return fig


def plot_week(rows, metric_index):
    field, title = METRICS[metric_index]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    times = list(range(min(r[0] for r in rows), max(r[0] for r in rows) + 1800, 1800))
    for group, label, color in [("online", "Online", "#4C78A8"),
                                 ("offline", "Offline", "#F58518")]:
        values = {r[0]: r[metric_index + 2] for r in rows if r[1] == group}
        ax.plot(times, [values.get(t) for t in times],
                color=color, linewidth=1, label=label)
    ax.set(title=title, xlim=(times[0], times[-1]))
    ticks = list(range((times[0] + 86399) // 86400 * 86400, times[-1] + 1, 86400))
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    ax.set_xticks(ticks, [weekdays[t // 86400 % 7] for t in ticks])
    ax.xaxis.get_offset_text().set_visible(False)
    ax.margins(y=.08)
    if field == "sm_util":
        ax.set(ylim=(10, 70), yticks=[10, 30, 50, 70])
    elif field in ("cpu_usage", "mem_usage"):
        ax.yaxis.set_major_locator(MaxNLocator(nbins=4))
    ax.grid(alpha=.2)
    ax.legend(frameon=False)
    return fig


if __name__ == "__main__":
    weekly = query("fig5_week", WEEK, WORKLOAD, ("instance_daily", "instance_week_5min"))
    if any(r[1] is None for r in weekly):
        raise ValueError("Weekly records without a matching daily workload")
    daily = query("fig5_daily", DAILY)
    for i, (metric, _) in enumerate(METRICS):
        save(plot_week(weekly, i), f"fig05_week_{metric}")
        save(plot(daily, i), f"fig05_daily_{metric}")
