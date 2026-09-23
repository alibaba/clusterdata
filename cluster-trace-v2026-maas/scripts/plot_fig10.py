from app_case_data import finish, line, load_case, new_axes, points, weekdays


def main():
    metadata, _, rows = load_case(10)
    fig, ax = new_axes(10, "a")
    line(ax, rows, "kv_cache_util", "steelblue", "Prefill", role="prefill")
    line(ax, rows, "kv_cache_util", "seagreen", "Decode", role="decode")
    prefill = [r["value"] for r in points(rows, "kv_cache_util", "prefill") if r["value"] is not None]
    if prefill:
        peak = max(prefill)
        ax.axhline(peak, color="black", linestyle="--", alpha=.6)
        ax.annotate(f"{peak:.1f}", (0, peak), xycoords=("axes fraction", "data"),
                    xytext=(-2, 0), textcoords="offset points", ha="right", va="center")
    ax.set(xlabel="(a) PD-Disagg KV Cache", ylabel="KV Cache Occ. (%)")
    weekdays(ax, metadata)
    ax.legend(frameon=False, loc="upper right")
    finish(fig)

    fig, ax = new_axes(10, "b")
    qps = {r["time_s"]: r["value"] for r in points(rows, "qps_norm") if r["value"] is not None}
    for metric, color, label in [("prefill_latency", "steelblue", "Prefill"),
                                  ("kv_transfer_latency", "darkorange", "KV Cache Transfer")]:
        aligned = [r for r in points(rows, metric) if r["time_s"] in qps and r["value"] is not None]
        aligned.sort(key=lambda r: qps[r["time_s"]])
        ax.scatter([qps[r["time_s"]] for r in aligned], [r["value"] for r in aligned],
                   color=color, label=label, alpha=.6, s=10, edgecolors="none")
    ax.set(xlabel="(b) Normalized QPS", ylabel="Latency (ms)", ylim=(0, 2000))
    ax.legend(frameon=False, loc="upper left")
    finish(fig)


if __name__ == "__main__":
    main()
