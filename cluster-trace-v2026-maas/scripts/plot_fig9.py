from app_case_data import finish, line, load_case, new_axes, weekdays


def main():
    metadata, _, rows = load_case(9)
    fig, ax = new_axes(9, "a")
    right = ax.twinx()
    line(ax, rows, "gpu_mem_util", "steelblue", "GPU Mem")
    line(right, rows, "kv_cache_util", "darkorange", "KV Cache")
    ax.set(xlabel="(a) GPU Mem and KV Cache", ylabel="GPU Memory Util. (%)", ylim=(80, 101))
    right.set_ylabel("KV Cache Occ. (%)")
    right.margins(y=.08)
    weekdays(ax, metadata)
    ax.legend(handles=ax.lines + right.lines, frameon=False, loc="upper left")
    finish(fig)

    fig, ax = new_axes(9, "b")
    line(ax, rows, "sm_util", "seagreen")
    ax.set(xlabel="(b) SM Utilization", ylabel="SM Utilization (%)", ylim=(0, 40))
    weekdays(ax, metadata)
    finish(fig)


if __name__ == "__main__":
    main()
