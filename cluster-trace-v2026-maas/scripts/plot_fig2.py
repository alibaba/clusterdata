from common import query, save
from math import fsum

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator

SQL = """
SELECT cluster_id,
       fsum(gpu_hours) AS gpu_hours
FROM daily
GROUP BY cluster_id
ORDER BY gpu_hours DESC NULLS LAST, cluster_id
"""


def load_data():
    return query("fig2", SQL)


def plot(rows):
    valid = [r for r in rows if r[0] not in (None, "")]
    if not valid or any(r[1] is None or not np.isfinite(r[1]) or r[1] < 0 for r in valid):
        raise ValueError("Expected nonnegative GPU-hours for identified clusters")
    hours = np.array([r[1] for r in valid])
    total = fsum(hours)
    if total <= 0:
        raise ValueError("Total GPU-hours must be positive")
    x = np.arange(1, len(valid) + 1)
    cumulative = np.cumsum(hours) / total * 100

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, cumulative, color="#F40519", label="GPU Time")
    ax.set(xlabel="Clusters Sorted by GPU Time", ylabel="CDF of GPU Time (%)",
           xlim=(0.5, len(valid) + 0.5), ylim=(0, 100))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="y", alpha=0.2)
    ax.legend(loc="upper left", frameon=False)
    return fig


if __name__ == "__main__":
    save(plot(load_data()), "fig02")
