from common import save
from plot_common import query
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
import numpy as np

SQL = """
WITH top_models AS (
    SELECT model_key, fsum(hours) AS hours
    FROM src WHERE model_id IS NOT NULL AND model_id <> '' AND model_key IS NOT NULL
    GROUP BY model_key ORDER BY hours DESC, model_key LIMIT 30
)
SELECT t.model_key, t.hours, s.gpu_type, count(*) AS observations
FROM top_models t JOIN src s ON s.model_key = t.model_key
WHERE s.model_id IS NOT NULL AND s.model_id <> ''
GROUP BY t.model_key, t.hours, s.gpu_type
"""
GPU_SQL = """
SELECT gpu_type, fsum(hours) AS hours
FROM src WHERE starts_with(gpu_type, 'gpu_')
GROUP BY gpu_type ORDER BY hours DESC, gpu_type LIMIT 30
"""


def load_matrix():
    rows = query("fig18_model_gpu", SQL)
    model_hours = {model: hours for model, hours, gpu, count in rows}
    models = sorted(model_hours, key=lambda m: (-model_hours[m], m))
    gpus = [r[0] for r in query("fig18_gpu_order", GPU_SQL)]
    if not models or not gpus:
        raise ValueError("No valid models or GPU types in the daily table")
    mi, gi = {m: i for i, m in enumerate(models)}, {g: i for i, g in enumerate(gpus)}
    matrix = np.zeros((len(models), len(gpus)), dtype=int)
    for model, _, gpu, count in rows:
        if gpu in gi and count > 0:
            matrix[mi[model], gi[gpu]] = 1
    return models, gpus, matrix


def main():
    models, gpus, matrix = load_matrix()

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.imshow(matrix, cmap=ListedColormap(["#f0f0f0", "steelblue"]),
              vmin=0, vmax=1, aspect="auto", interpolation="nearest")
    ax.set_xticks(np.arange(-.5, len(gpus), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(models), 1), minor=True)
    ax.grid(which="minor", color="#cccccc", linewidth=.3)
    ax.tick_params(which="minor", length=0)
    xticks, yticks = np.arange(5, len(gpus) + 1, 5), np.arange(5, len(models) + 1, 5)
    ax.set(xticks=xticks - 1, xticklabels=xticks, yticks=yticks - 1, yticklabels=yticks,
           xlabel="GPU Types sorted by GPU time", ylabel="Top Models")
    ax.legend(handles=[Patch(facecolor="steelblue", label="Deployed"),
                       Patch(facecolor="#f0f0f0", edgecolor="#cccccc", label="Not Deployed")],
              loc="upper center", bbox_to_anchor=(.5, 1.12), ncol=2, frameon=False)
    save(fig, "fig18")


if __name__ == "__main__":
    main()
