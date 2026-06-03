"""Shared helpers for final public figure plotting."""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42

from matplotlib.ticker import LogFormatterMathtext, LogLocator
import numpy as np
import pandas as pd

try:
    import squarify
except ModuleNotFoundError:  # pragma: no cover
    squarify = None


RELEASE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = RELEASE_ROOT
DATA_ROOT = RELEASE_ROOT / "data" / "derived"
OUT_DIR = RELEASE_ROOT / "figures"
CSV_CHUNKSIZE = 1_000_000

RELEASE_INPUTS = {
    "job_type_used_hours": "aggregates/job_type_used_hours.csv",
    "job_type_priority_used_hours": "aggregates/job_type_priority_used_card_hours.csv",
    "gpu_spec_distribution": "aggregates/gpu_spec_distribution.csv",
    "gpu_spec_priority_pod_hours": "aggregates/gpu_spec_priority_pod_hours.csv",
    "gpu_spec_hourly_req": "aggregates/gpu_spec_hourly_req.csv",
    "model_type_distribution": "figure_inputs/fig_model_type_dist/summary.csv",
    "temporal_gpu_req_sm_util": "figure_inputs/fig_temporal_gpu_req_sm_util/hourly.csv",
    "gpu_spec_alloc_ratio": "figure_inputs/fig_gpu_spec_alloc_ratio/server_alloc_summary.csv",
    "idle_gpu_fragmentation": "figure_inputs/fig_idle_gpu_fragmentation/summary.csv",
    "standby_temporal": "figure_inputs/fig_standby_temporal/hourly.csv",
    "asw_available_slots": "figure_inputs/fig_asw_available_slots/summary.csv",
    "fractional_gpu_summary": "figure_inputs/fig_compare_frac_gpu/asi_summary.csv",
    "cpu_gpu_ratio_samples": "figure_inputs/fig_cpu_gpu_ratio/samples.csv",
    "pod_resource_util_samples": "figure_inputs/fig_pod_resource_util_cdf/resource_util_samples.csv",
    "server_network_samples": "figure_inputs/fig_server_network_cdf/server_network_samples.csv",
    "job_execution_hours": "figure_inputs/fig_execution_time_cdf/job_execution_hours.csv",
    "gpu_cpu_request_samples": "figure_inputs/fig_gpu_cpu_request_num/asi_samples.csv",
}

PUBLIC_JOB_ORDER = ["training", "online_inference", "offline_inference", "dev"]
JOB_LABELS = {
    "training": "Training",
    "online_inference": "On-Infer.",
    "offline_inference": "Off-Infer.",
    "dev": "Dev",
    "other": "Other",
}
EXEC_PUBLIC_JOB_ORDER = ["offline_inference", "dev", "online_inference", "training"]
LINE_STYLES = {
    "training": "dashdot",
    "online_inference": "solid",
    "offline_inference": "dashed",
    "dev": "dotted",
}
MODEL_TYPES = ["genai", "rec", "cv", "embedding", "dev"]
MODEL_LABELS = {
    "embedding": "Embed.",
    "rec": "Rec",
    "genai": "GenAI",
    "cv": "CV",
    "dev": "Dev",
}
MODEL_LINE_STYLES = {
    "rec": "dashdot",
    "genai": "solid",
    "cv": "dashed",
    "dev": "dotted",
    "embedding": (0, (3, 1, 1, 1, 1, 1)),
}
MODEL_LINE_COLORS = {
    "rec": "tab:blue",
    "genai": "tab:orange",
    "cv": "tab:green",
    "dev": "tab:red",
    "embedding": "tab:purple",
}
EXEC_PUBLIC_MODEL_ORDER = ["cv", "dev", "embedding", "genai", "rec"]
PAPER_GPU_ORDER = ["A10", "L20", "H20", "A100", "H800", "XPU-A"]
PAPER_JOB_ORDER = ["online_inference", "training", "offline_inference", "dev"]
PAPER_JOB_LABELS = {
    "online_inference": "Online-inference",
    "training": "Training",
    "offline_inference": "Offline-inference",
    "dev": "Dev",
    "other": "Other",
}
PAPER_SHORT_JOB_LABELS = {
    "online_inference": "On-Inf.",
    "training": "Train",
    "offline_inference": "Off-Inf.",
    "dev": "Dev",
}
LINE_COLORS = {
    "training": "tab:blue",
    "online_inference": "tab:orange",
    "offline_inference": "tab:green",
    "dev": "tab:red",
}
NETWORK_JOB_ORDER = [
    "online_inference",
    "offline_inference",
    "training",
    "offline_inference,online_inference",
    "offline_inference,training",
    "dev",
]
NETWORK_JOB_LABELS = {
    "training": "Training",
    "online_inference": "On-Infer.",
    "offline_inference": "Off-Infer.",
    "dev": "Dev",
    "offline_inference,online_inference": "Off-Infer.+On-Infer.",
    "offline_inference,training": "Off-Infer.+Training",
}
NETWORK_LINE_STYLES = {
    "training": "dashdot",
    "online_inference": "solid",
    "offline_inference": "dashed",
    "dev": "dotted",
    "offline_inference,online_inference": (0, (3, 1, 1, 1, 1, 1)),
    "offline_inference,training": (5, (10, 3)),
}
NETWORK_LINE_COLORS = {
    "training": "tab:blue",
    "online_inference": "tab:orange",
    "offline_inference": "tab:green",
    "dev": "tab:red",
    "offline_inference,online_inference": "tab:purple",
    "offline_inference,training": "tab:brown",
}

EXEC_DURATION_XLIM = (1e-3, 1e5)
EXEC_DURATION_XTICKS = [1e-3, 1e-1, 1e1, 1e3, 1e5]


def configure(data_root: Path, out_dir: Path) -> None:
    global DATA_ROOT, OUT_DIR
    DATA_ROOT = data_root.resolve()
    OUT_DIR = out_dir.resolve()


def display_gpu_label(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    base = text.split("-", 1)[0]
    return base if base in PAPER_GPU_ORDER else text


def csv_path(name: str) -> Path:
    release_rel = RELEASE_INPUTS.get(name)
    if release_rel is None:
        raise KeyError(f"Unknown release input: {name}")
    return DATA_ROOT / release_rel


def read_csv(name: str) -> pd.DataFrame:
    path = csv_path(name)
    if not path.is_file():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def display_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path)


def write_manifest(stem: str, inputs: list[str], summary: Path, output: Path, note: str = "") -> None:
    manifest = {
        "output": display_path(output),
        "summary": display_path(summary),
        "inputs": inputs,
        "source": display_path(DATA_ROOT),
    }
    if note:
        manifest["note"] = note
    (output.parent / f"{stem}.manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def save_summary(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def cdf_from_array(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return np.array([]), np.array([])
    x = np.sort(arr)
    y = np.arange(1, arr.size + 1) / arr.size
    return x, y


def update_counter(counter: defaultdict[float, int], values: pd.Series) -> None:
    arr = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    arr = arr[np.isfinite(arr)]
    arr = arr[arr >= 0]
    if arr.size == 0:
        return
    unique, counts = np.unique(arr, return_counts=True)
    for value, count in zip(unique, counts):
        counter[float(value)] += int(count)


def cdf_from_counter(counter: dict[float, int]) -> tuple[np.ndarray, np.ndarray]:
    if not counter:
        return np.array([]), np.array([])
    x = np.array(sorted(counter), dtype=float)
    counts = np.array([counter[v] for v in x], dtype=float)
    y = np.cumsum(counts) / counts.sum()
    return x, y


def counter_stats(counter: dict[float, int]) -> dict[str, float]:
    if not counter:
        return {"count": 0, "median": np.nan, "mean": np.nan, "p90": np.nan}
    x = np.array(sorted(counter), dtype=float)
    counts = np.array([counter[v] for v in x], dtype=float)
    total = counts.sum()
    cdf = np.cumsum(counts) / total
    return {
        "count": int(total),
        "median": float(x[np.searchsorted(cdf, 0.5)]),
        "mean": float((x * counts).sum() / total),
        "p90": float(x[np.searchsorted(cdf, 0.9)]),
    }


def update_hist(
    hist: np.ndarray,
    bins: np.ndarray,
    values: pd.Series,
    stats: dict[str, float],
) -> None:
    arr = pd.to_numeric(values, errors="coerce").to_numpy(dtype=float)
    arr = arr[np.isfinite(arr)]
    arr = arr[arr >= 0]
    if arr.size == 0:
        return
    stats["count"] += int(arr.size)
    stats["sum"] += float(arr.sum())
    clipped = np.clip(arr, bins[0], bins[-1])
    hist += np.histogram(clipped, bins=bins)[0]


def cdf_from_hist(hist: np.ndarray, bins: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    total = hist.sum()
    if total == 0:
        return np.array([]), np.array([])
    return bins[1:], np.cumsum(hist) / total


def hist_quantile(hist: np.ndarray, bins: np.ndarray, q: float) -> float:
    total = hist.sum()
    if total == 0:
        return float("nan")
    cdf = np.cumsum(hist) / total
    return float(bins[1:][np.searchsorted(cdf, q)])


def hist_stats(hist: np.ndarray, bins: np.ndarray, stats: dict[str, float]) -> dict[str, float]:
    count = int(stats["count"])
    return {
        "count": count,
        "median": hist_quantile(hist, bins, 0.5),
        "mean": float(stats["sum"] / count) if count else float("nan"),
        "p90": hist_quantile(hist, bins, 0.9),
    }


def configure_execution_time_axis(ax) -> None:
    ax.set_xscale("log")
    ax.set_xlim(*EXEC_DURATION_XLIM)
    ax.set_xticks(EXEC_DURATION_XTICKS)
    ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10))
    ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10), numticks=100))
    ax.grid(True, alpha=0.3)
