"""Plot gpu_spec_hourly_req_trend.pdf."""

from __future__ import annotations

import matplotlib.pyplot as plt

from . import common as c


def plot() -> None:
    df = c.read_csv("gpu_spec_hourly_req")
    df["day"] = c.pd.to_numeric(df["day"], errors="coerce")
    df = df.dropna(subset=["day"])
    df["display_gpu_spec"] = df["server_gpu_spec"].map(lambda value: str(value))
    plot_order = ["A10", "A100", "H20", "L20", "XPU-A"]
    df = df[df["display_gpu_spec"].isin(plot_order)].copy()
    order_rank = {spec: idx for idx, spec in enumerate(plot_order)}
    df["display_order"] = df["display_gpu_spec"].map(order_rank)
    df = df.sort_values(["display_order", "day"]).drop(columns=["display_order"])
    output = c.OUT_DIR / "gpu_spec_hourly_req_trend.pdf"
    summary = c.OUT_DIR / "gpu_spec_hourly_req_trend.summary.csv"
    c.save_summary(df, summary)

    line_style = {
        "XPU-A": "-",
        "A100": ":",
        "A10": "-.",
        "H20": "--",
        "L20": (0, (3, 1, 1, 1, 1, 1)),
    }
    line_color = {
        "XPU-A": "tab:red",
        "A100": "tab:blue",
        "A10": "tab:green",
        "H20": "tab:orange",
        "L20": "tab:purple",
    }
    plot_order = [spec for spec in plot_order if spec in set(df["display_gpu_spec"])]
    fig, ax = plt.subplots(figsize=(10, 3))
    fontsize = 20
    days = sorted(df["day"].unique().tolist())
    plot_x_by_day = {day: idx for idx, day in enumerate(days)}
    for spec in plot_order:
        group = df[df["display_gpu_spec"].eq(spec)].sort_values("day")
        plot_x = [plot_x_by_day[day] for day in group["day"]]
        plot_y = group["used_card_hour_sum_p9300"].to_numpy(dtype=float) / 100.0
        ax.plot(
            plot_x,
            plot_y,
            label=spec,
            linewidth=2.5,
            linestyle=line_style.get(spec, "solid"),
            color=line_color.get(spec),
        )
    ax.set_xlabel("Days from the first day of the trace", fontsize=fontsize)
    ax.set_ylabel("#GPU requested", fontsize=fontsize)
    ax.tick_params(axis="both", labelsize=fontsize)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.set_yticks([1000, 2000, 3000, 4000, 5000])
    ax.set_yticklabels(["1k", "2k", "3k", "4k", "5k"], fontsize=fontsize)
    ax.legend(
        fontsize=fontsize,
        ncols=min(5, max(1, len(plot_order))),
        bbox_to_anchor=(-0.01, 0.7, 1.0, 0.0),
        handlelength=1.5,
        handletextpad=0.5,
        columnspacing=0.5,
        frameon=False,
        labelspacing=0.5,
    )
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)
    c.write_manifest("gpu_spec_hourly_req_trend", ["asi_opensource_gpu_spec_hourly_req"], summary, output)
