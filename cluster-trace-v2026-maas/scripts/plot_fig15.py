from plot_common import axes, draw_groups, model_marks, query, finish

SQL = """
SELECT CASE WHEN pd_role IN ('prefill', 'decode') THEN 'disagg' ELSE 'colloc' END AS mode,
       params_b, fsum(hours)
FROM src WHERE workload = 'online' AND params_b > 0 AND params_b <= 1050
GROUP BY mode, params_b HAVING fsum(hours) >= 0
ORDER BY mode, params_b
"""


def main():
    fig, ax = axes(15, "a", "(a) Model Size (B)")
    draw_groups(ax, query("fig15_a", SQL),
                [("disagg", "PD-Disagg", "steelblue"), ("colloc", "PD-Colloc", "darkorange")])
    model_marks(ax, [(4, 62), (32, 62), (235, 38), (706, 38)])
    finish(fig, ax)


if __name__ == "__main__":
    main()
