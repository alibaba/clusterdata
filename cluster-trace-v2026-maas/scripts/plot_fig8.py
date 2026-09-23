from app_case_data import finish, load_case, new_axes, weekdays
from collections import defaultdict

from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
import numpy as np


PANELS = [("qps_norm", "Normalized QPS"), ("gpu_count", "# GPUs"),
          ("input_tokens", "Input Length (CDF)"), ("output_tokens", "Output Length (CDF)"),
          ("ttft", "TTFT (ms)"), ("tpot", "TPOT (ms)")]


def main():
    metadata, case, rows = load_case(8)
    for app in case["apps"]:
        for metric, title in PANELS:
            selected = [r for r in rows if r["app_id"] == app["app_id"]
                        and r["metric"] == metric and r["value"] is not None]
            if not selected:
                raise ValueError(f"No data for {app['label']} / {metric}")
            seen = {r["gpu_type"] for r in selected}
            gpus = [g for g in case["gpus"] if g["gpu_type"] in seen]
            fig, ax = new_axes(8, f"{app['label'].lower()}_{metric}", f"{app['label']} — {title}")

            if metric in ("qps_norm", "gpu_count"):
                totals = defaultdict(float)
                for row in selected:
                    totals[row["time_s"], row["gpu_type"]] += row["value"]
                times = sorted({r["time_s"] for r in selected})
                series = [np.array([totals[t, g["gpu_type"]] for t in times]) for g in gpus]
                if metric == "qps_norm":
                    ax.stackplot(times, series, colors=[g["color"] for g in gpus], alpha=.8)
                    sums = [s.sum() for s in series]
                    total = sum(sums)
                    if total > 0:
                        for i, index in enumerate(np.argsort(sums)[::-1]):
                            g = gpus[index]
                            ax.text(.45, .96 - i * .10,
                                    f"{g['label']}: {sums[index] / total * 100:.0f}%",
                                    transform=ax.transAxes, va="top", color=g["color"],
                                    bbox={"facecolor": "white", "edgecolor": "none", "alpha": .75})
                    ax.set_ylim(top=ax.get_ylim()[1] * 1.18)
                else:
                    for g, values in zip(gpus, series):
                        ax.plot(times, values, color=g["color"])
                weekdays(ax, metadata)
            elif metric in ("input_tokens", "output_tokens"):
                for g in gpus:
                    values = np.sort([r["value"] for r in selected if r["gpu_type"] == g["gpu_type"]])
                    ax.plot(values, np.arange(1, len(values) + 1) / len(values) * 100,
                            color=g["color"])
                ax.set(ylabel="CDF (%)", ylim=(0, 102))
                ax.xaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
                if app["label"] == "App1" and metric == "output_tokens":
                    ax.set(xlim=(11.5, 13.5), xticks=[12, 13])
            else:
                series = [[r["value"] for r in selected if r["gpu_type"] == g["gpu_type"]] for g in gpus]
                boxes = ax.boxplot(series, tick_labels=[g["label"] for g in gpus],
                                   patch_artist=True, widths=.6, showfliers=False,
                                   medianprops={"color": "black"})
                for box, g in zip(boxes["boxes"], gpus):
                    box.set_facecolor(g["color"])
                    box.set_alpha(.65)
                limits = {("App1", "ttft"): (20, 60), ("App1", "tpot"): (2, 5),
                          ("App2", "ttft"): (0, 300)}
                if (app["label"], metric) in limits:
                    ax.set_ylim(*limits[app["label"], metric])

            ax.legend(handles=[Line2D([], [], color=g["color"], label=g["label"]) for g in gpus],
                      frameon=False)
            finish(fig)


if __name__ == "__main__":
    main()
