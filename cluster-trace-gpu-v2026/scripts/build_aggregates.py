#!/usr/bin/env python3
"""Build paper aggregate and figure inputs from public ASI trace fact tables."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


RELEASE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_ROOT = RELEASE_ROOT / "data"
DEFAULT_OUT_ROOT = RELEASE_ROOT / "data" / "derived"

PAPER_START_DAY = 109
PAPER_END_DAY = 115
JOB_TYPE_START_DAY = 109
JOB_TYPE_END_DAY = 184
JOB_TYPES = ["training", "online_inference", "offline_inference", "dev"]
MODEL_TYPES = ["genai", "rec", "cv", "embedding", "dev"]
GPU_SPECS = ["A10", "L20", "H20", "A100", "H800", "XPU-A"]
ASW_GPU_SPECS = {"H20", "XPU-A", "L20", "A100"}
NETWORK_JOB_TYPES = [
    "online_inference",
    "offline_inference",
    "training",
    "offline_inference,online_inference",
    "offline_inference,training",
    "dev",
]
JOB_CONFIGS = [
    (1, 8, "gpu1_cpu8"),
    (1, 12, "gpu1_cpu12"),
    (4, 32, "gpu4_cpu32"),
    (4, 48, "gpu4_cpu48"),
    (4, 64, "gpu4_cpu64"),
    (8, 64, "gpu8_cpu64"),
    (8, 96, "gpu8_cpu96"),
    (8, 128, "gpu8_cpu128"),
]


PARTITION_RE = re.compile(r"day=(?P<day>\d+)/hour=(?P<hour>\d+)")


def fact_table_root(data_root: Path, logical_name: str) -> Path:
    """Return a public fact table directory under the local data root."""

    candidates = [
        data_root / f"asi_opensource_{logical_name}",
        data_root / logical_name,
        data_root / "tables" / logical_name,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def normalize_spec(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    base = text.split("-", 1)[0]
    return base if base in GPU_SPECS else text


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1"])


def partition_files(table_root: Path) -> list[tuple[int, str, Path]]:
    rows = []
    for path in sorted(table_root.glob("day=*/hour=*/part-000.parquet")):
        match = PARTITION_RE.search(path.as_posix())
        if not match:
            continue
        rows.append((int(match.group("day")), f"{int(match.group('hour')):02d}", path))
    return rows


def day_ranges(days: Iterable[int]) -> list[list[int]]:
    ranges: list[list[int]] = []
    start = prev = None
    for day in sorted(set(days)):
        if start is None:
            start = prev = day
        elif day == prev + 1:
            prev = day
        else:
            ranges.append([int(start), int(prev)])
            start = prev = day
    if start is not None:
        ranges.append([int(start), int(prev)])
    return ranges


def partition_coverage(files: list[tuple[int, str, Path]]) -> dict:
    hours_by_day: defaultdict[int, set[str]] = defaultdict(set)
    for day, hour, _path in files:
        hours_by_day[day].add(hour)
    complete_days = [day for day, hours in hours_by_day.items() if len(hours) == 24]
    return {
        "partition_count": len(files),
        "day_ranges": day_ranges(hours_by_day),
        "complete_day_ranges": day_ranges(complete_days),
        "complete_day_count": len(complete_days),
    }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_csv(df: pd.DataFrame, path: Path) -> None:
    ensure_parent(path)
    df.to_csv(path, index=False)


def append_csv(df: pd.DataFrame, path: Path) -> None:
    ensure_parent(path)
    df.to_csv(path, index=False, mode="a", header=not path.exists())


def to_numeric(df: pd.DataFrame, cols: Iterable[str], *, fillna: bool = True) -> None:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if fillna:
                df[col] = df[col].fillna(0.0)


def in_day_range(day: int, start: int, end: int) -> bool:
    return start <= day <= end


def hour_even(hour: str) -> bool:
    return int(hour) % 2 == 0


def aggregate_pod_partitions(data_root: Path, out_root: Path) -> dict:
    pod_root = fact_table_root(data_root, "pod_hourly")
    files = partition_files(pod_root)
    if not files:
        raise FileNotFoundError(f"No pod_hourly parquet partitions found under {pod_root}")

    for rel in [
        "figure_inputs/fig_cpu_gpu_ratio/samples.csv",
        "figure_inputs/fig_pod_resource_util_cdf/resource_util_samples.csv",
    ]:
        path = out_root / rel
        if path.exists():
            path.unlink()

    job_type_used: defaultdict[str, float] = defaultdict(float)
    job_type_priority: defaultdict[str, list[float]] = defaultdict(lambda: [0.0, 0.0])
    gpu_priority: defaultdict[str, list[int]] = defaultdict(lambda: [0, 0])
    gpu_hourly_req: defaultdict[tuple[str, str], list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    model_used: defaultdict[tuple[str, str, str], float] = defaultdict(float)
    temporal: defaultdict[tuple[str, str, str], list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    frac_hourly: defaultdict[tuple[str, str], list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    workload_hourly: list[pd.DataFrame] = []
    server_pod: defaultdict[tuple[str, str, str], list[float]] = defaultdict(lambda: [0.0] * 8)

    paper_columns = [
        "workload_id",
        "server_id",
        "state_public",
        "gpu_spec_public",
        "priority_class",
        "job_type_public",
        "model_type_public",
        "is_genai_request",
        "gpu_request",
        "gpu_mem_request",
        "cpu_request_cores",
        "used_gpu_hours",
        "avg_gpu_sm_util",
        "avg_gpu_mem_gib",
        "avg_cpu_request_util",
        "avg_memory_util",
        "ready_status",
    ]
    job_type_columns = [
        "gpu_spec_public",
        "priority_class",
        "job_type_public",
        "gpu_mem_request",
        "used_gpu_hours",
    ]
    gpu_hourly_columns = [
        "gpu_spec_public",
        "priority_class",
        "gpu_mem_request",
        "used_gpu_hours",
    ]

    for day, hour, path in files:
        if in_day_range(day, PAPER_START_DAY, PAPER_END_DAY):
            read_columns = paper_columns
        elif in_day_range(day, JOB_TYPE_START_DAY, JOB_TYPE_END_DAY):
            read_columns = job_type_columns
        else:
            read_columns = gpu_hourly_columns

        df = pd.read_parquet(path, columns=read_columns)
        to_numeric(
            df,
            [
                "gpu_request",
                "gpu_mem_request",
                "cpu_request_cores",
                "used_gpu_hours",
            ],
        )
        to_numeric(
            df,
            [
                "avg_gpu_sm_util",
                "avg_gpu_mem_gib",
                "avg_cpu_request_util",
                "avg_memory_util",
            ],
            fillna=False,
        )

        gpu_mem_pod = df["gpu_mem_request"] > 0

        if in_day_range(day, JOB_TYPE_START_DAY, JOB_TYPE_END_DAY):
            cur = df[gpu_mem_pod & df["used_gpu_hours"].notna() & df["job_type_public"].notna()]
            cur = cur[cur["job_type_public"] != "unknown"]
            for job_type, group in cur.groupby("job_type_public", sort=False):
                job_type_used[str(job_type)] += float(group["used_gpu_hours"].sum())
                job_type_priority[str(job_type)][0] += float(group.loc[group["priority_class"].eq("HP"), "used_gpu_hours"].sum())
                job_type_priority[str(job_type)][1] += float(group.loc[group["priority_class"].eq("LP"), "used_gpu_hours"].sum())

        if in_day_range(day, PAPER_START_DAY, PAPER_END_DAY):
            ready = bool_series(df["ready_status"])
            is_genai = bool_series(df["is_genai_request"])
            df["display_gpu_spec"] = df["gpu_spec_public"].map(normalize_spec)

            gpu_pod = df["gpu_request"] > 0
            hp = df["priority_class"].eq("HP")
            standby = df["state_public"].fillna("").eq("Standby")
            active = ~standby

            cur = df[gpu_pod & df["priority_class"].isin(["HP", "LP"])]
            for spec, group in cur.groupby("display_gpu_spec", sort=False):
                if spec in GPU_SPECS:
                    gpu_priority[str(spec)][0] += int(group["priority_class"].eq("HP").sum())
                    gpu_priority[str(spec)][1] += int(group["priority_class"].eq("LP").sum())

            base = df[gpu_pod & df["used_gpu_hours"].notna()].copy()
            for (job_type, spec, model), group in base.groupby(
                ["job_type_public", "display_gpu_spec", "model_type_public"], sort=False
            ):
                model_used[(str(job_type), str(spec), str(model))] += float(group["used_gpu_hours"].sum())

            temp = df[
                gpu_pod
                & hp
                & ready
                & active
                & df["job_type_public"].isin(JOB_TYPES)
            ].copy()
            temp = temp[temp["gpu_request"] > 0]
            if not temp.empty:
                temp["sm_per_gpu"] = temp["avg_gpu_sm_util"] / (temp["gpu_request"] * 100.0)
                for job_type, group in temp.groupby("job_type_public", sort=False):
                    item = temporal[(str(day), hour, str(job_type))]
                    item[0] += float(group["sm_per_gpu"].sum(skipna=True))
                    item[1] += float(group["sm_per_gpu"].count())
                    item[2] += float(group["gpu_request"].sum())

            if hour_even(hour):
                cur_hp = df[hp]
                item = frac_hourly[(str(day), hour)]
                item[0] += float((cur_hp["gpu_request"] > 0).sum())
                item[1] += float(((cur_hp["gpu_request"] > 0) & (cur_hp["gpu_request"] < 1.0)).sum())
                item[2] += float(cur_hp.loc[cur_hp["gpu_request"] > 0, "gpu_request"].sum())
                item[3] += float(
                    cur_hp.loc[(cur_hp["gpu_request"] > 0) & (cur_hp["gpu_request"] < 1.0), "gpu_request"].sum()
                )

                cpu_ratio = df[gpu_pod & df["job_type_public"].isin(JOB_TYPES)].copy()
                if not cpu_ratio.empty:
                    cpu_ratio["cpu_gpu_ratio"] = np.ceil(
                        cpu_ratio["cpu_request_cores"] / np.ceil(cpu_ratio["gpu_request"])
                    )
                    append_csv(
                        cpu_ratio.assign(day=str(day), hour=hour)[["day", "hour", "job_type_public", "cpu_gpu_ratio"]].rename(
                            columns={"job_type_public": "job_type"}
                        ),
                        out_root / "figure_inputs/fig_cpu_gpu_ratio/samples.csv",
                    )

            resource = df[gpu_pod & ready & df["job_type_public"].isin(JOB_TYPES)].copy()
            resource = resource[resource["gpu_request"] > 0]
            if not resource.empty:
                resource["gpu_sm_ratio"] = resource["avg_gpu_sm_util"] / (resource["gpu_request"] * 100.0)
                append_csv(
                    resource.assign(day=str(day), hour=hour)[
                        [
                            "day",
                            "hour",
                            "job_type_public",
                            "avg_cpu_request_util",
                            "avg_memory_util",
                            "gpu_sm_ratio",
                            "avg_gpu_mem_gib",
                        ]
                    ].rename(
                        columns={
                            "job_type_public": "job_type",
                            "avg_cpu_request_util": "cpu_request_util",
                            "avg_memory_util": "memory_util",
                            "avg_gpu_mem_gib": "gpu_memory_gib",
                        }
                    ),
                    out_root / "figure_inputs/fig_pod_resource_util_cdf/resource_util_samples.csv",
                )

            workload = df[gpu_pod & df["workload_id"].notna()].copy()
            if not workload.empty:
                tmp = (
                    workload.groupby("workload_id", as_index=False)
                    .agg(
                        gpu_request=("gpu_request", "sum"),
                        cpu_request_cores=("cpu_request_cores", "sum"),
                        is_genai=("is_genai_request", lambda x: bool(bool_series(x).any())),
                    )
                    .assign(day=str(day), hour=hour)
                )
                workload_hourly.append(tmp)

            pod_server = df.copy()
            if not pod_server.empty:
                pod_server["hp_active"] = np.where(
                    (pod_server["gpu_request"] > 0) & pod_server["priority_class"].eq("HP") & ~pod_server["state_public"].eq("Standby"),
                    pod_server["used_gpu_hours"],
                    0.0,
                )
                pod_server["hp_standby"] = np.where(
                    (pod_server["gpu_request"] > 0) & pod_server["priority_class"].eq("HP") & pod_server["state_public"].eq("Standby"),
                    pod_server["used_gpu_hours"],
                    0.0,
                )
                pod_server["lp_alloc"] = np.where(
                    (pod_server["gpu_request"] > 0) & pod_server["priority_class"].eq("LP"),
                    pod_server["used_gpu_hours"],
                    0.0,
                )
                pod_server["hp_lp_active"] = np.where(
                    (pod_server["gpu_request"] > 0)
                    & pod_server["priority_class"].isin(["HP", "LP"])
                    & ~pod_server["state_public"].eq("Standby"),
                    pod_server["used_gpu_hours"],
                    0.0,
                )
                pod_server["requested_cpu_hp"] = np.where(
                    pod_server["priority_class"].eq("HP"), pod_server["cpu_request_cores"], 0.0
                )
                pod_server["requested_gpu_hp"] = np.where(
                    (pod_server["gpu_request"] > 0) & pod_server["priority_class"].eq("HP"),
                    pod_server["gpu_request"],
                    0.0,
                )
                pod_server["hp_pod_rows"] = np.where(pod_server["priority_class"].eq("HP"), 1, 0)
                grouped = pod_server.groupby("server_id", as_index=False).agg(
                    hp_active=("hp_active", "sum"),
                    hp_standby=("hp_standby", "sum"),
                    lp_alloc=("lp_alloc", "sum"),
                    hp_lp_active=("hp_lp_active", "sum"),
                    requested_cpu_hp=("requested_cpu_hp", "sum"),
                    requested_gpu_hp=("requested_gpu_hp", "sum"),
                    hp_pod_rows=("hp_pod_rows", "sum"),
                )
                for row in grouped.itertuples(index=False):
                    item = server_pod[(str(day), hour, row.server_id)]
                    item[0] += float(row.hp_active)
                    item[1] += float(row.hp_standby)
                    item[2] += float(row.lp_alloc)
                    item[3] += float(row.hp_lp_active)
                    item[4] += float(row.requested_cpu_hp)
                    item[5] += float(row.requested_gpu_hp)
                    item[6] += float(row.hp_pod_rows)

        if df["used_gpu_hours"].notna().any():
            cur = df[gpu_mem_pod & df["used_gpu_hours"].notna()]
            for spec, group in cur.groupby("gpu_spec_public", sort=False):
                if spec in {"A10", "A100", "H20", "L20", "XPU-A"}:
                    item = gpu_hourly_req[(str(spec), str(day))]
                    item[0] += float(group.loc[group["priority_class"].eq("HP"), "used_gpu_hours"].sum())
                    item[1] += float(group.loc[group["priority_class"].eq("LP"), "used_gpu_hours"].sum())
                    item[2] += float(group["used_gpu_hours"].sum())

    write_job_type_outputs(job_type_used, job_type_priority, out_root)
    write_gpu_priority(gpu_priority, out_root)
    write_gpu_hourly_req(gpu_hourly_req, out_root)
    write_model_distribution(model_used, out_root)
    write_temporal(temporal, out_root)
    write_fractional(frac_hourly, out_root)
    write_gpu_cpu_samples(workload_hourly, out_root)
    return {
        "pod_partitions": len(files),
        "pod_coverage": partition_coverage(files),
        "server_pod": server_pod,
    }


def write_job_type_outputs(
    job_type_used: dict[str, float],
    job_type_priority: dict[str, list[float]],
    out_root: Path,
) -> None:
    rows = [
        {"job_type": job_type, "sum_used_card_hour": value}
        for job_type, value in sorted(job_type_used.items())
    ]
    write_csv(pd.DataFrame(rows), out_root / "aggregates/job_type_used_hours.csv")
    rows = [
        {
            "job_type": job_type,
            "hp_used_gpu_hours": values[0],
            "lp_used_gpu_hours": values[1],
        }
        for job_type, values in sorted(job_type_priority.items())
    ]
    write_csv(pd.DataFrame(rows), out_root / "aggregates/job_type_priority_used_card_hours.csv")


def write_gpu_priority(gpu_priority: dict[str, list[int]], out_root: Path) -> None:
    rows = []
    for spec in GPU_SPECS:
        hp, lp = gpu_priority.get(spec, [0, 0])
        total = hp + lp
        rows.append(
            {
                "server_gpu_spec": spec,
                "display_gpu_spec": spec,
                "hp_pod_hours": hp,
                "lp_pod_hours": lp,
                "total_pod_hours": total,
                "hp_pct": 100.0 * hp / total if total else 0.0,
                "lp_pct": 100.0 * lp / total if total else 0.0,
            }
        )
    write_csv(pd.DataFrame(rows), out_root / "aggregates/gpu_spec_priority_pod_hours.csv")


def write_gpu_hourly_req(gpu_hourly_req: dict[tuple[str, str], list[float]], out_root: Path) -> None:
    rows = [
        {
            "server_gpu_spec": spec,
            "day": day,
            "hp_used_gpu_hours": vals[0],
            "lp_used_gpu_hours": vals[1],
            "total_used_gpu_hours": vals[2],
        }
        for (spec, day), vals in sorted(gpu_hourly_req.items())
    ]
    write_csv(pd.DataFrame(rows), out_root / "aggregates/gpu_spec_hourly_req.csv")


def write_model_distribution(model_used: dict[tuple[str, str, str], float], out_root: Path) -> None:
    rows = []
    job_totals = {
        job_type: sum(
            value
            for (jt, _spec, model), value in model_used.items()
            if jt == job_type and model != "unknown"
        )
        for job_type in JOB_TYPES
    }
    spec_totals = {
        spec: sum(
            value
            for (_jt, sp, model), value in model_used.items()
            if sp == spec and model != "unknown"
        )
        for spec in GPU_SPECS
    }
    for job_type in JOB_TYPES:
        total = job_totals[job_type]
        for model in MODEL_TYPES:
            value = sum(value for (jt, _sp, mt), value in model_used.items() if jt == job_type and mt == model)
            rows.append(
                {
                    "group_kind": "job_type",
                    "job_type": job_type,
                    "model_type": model,
                    "used_card_hour": value,
                    "percentage": 100.0 * value / total if total else 0.0,
                    "total_used_card_hour": total,
                    "server_gpu_spec": np.nan,
                }
            )
    for spec in GPU_SPECS:
        total = spec_totals[spec]
        for model in MODEL_TYPES:
            value = sum(value for (_jt, sp, mt), value in model_used.items() if sp == spec and mt == model)
            rows.append(
                {
                    "group_kind": "server_gpu_spec",
                    "job_type": np.nan,
                    "model_type": model,
                    "used_card_hour": value,
                    "percentage": 100.0 * value / total if total else 0.0,
                    "total_used_card_hour": total,
                    "server_gpu_spec": spec,
                }
            )
    write_csv(pd.DataFrame(rows), out_root / "figure_inputs/fig_model_type_dist/summary.csv")


def write_temporal(temporal: dict[tuple[str, str, str], list[float]], out_root: Path) -> None:
    rows = []
    for (day, hour, job_type), vals in sorted(temporal.items()):
        sm_sum, sm_count, gpu_sum = vals
        rows.append(
            {
                "day": day,
                "hour": hour,
                "job_type": job_type,
                "avg_gpu_sm_util_per_gpu": sm_sum / sm_count if sm_count else np.nan,
                "num_gpu_request": gpu_sum,
                "num_pods": int(sm_count),
            }
        )
    write_csv(pd.DataFrame(rows), out_root / "figure_inputs/fig_temporal_gpu_req_sm_util/hourly.csv")


def write_fractional(frac_hourly: dict[tuple[str, str], list[float]], out_root: Path) -> None:
    task_ratios = []
    gpu_ratios = []
    for vals in frac_hourly.values():
        pod_count, frac_pod_count, gpu_sum, frac_gpu_sum = vals
        if pod_count > 0:
            task_ratios.append(frac_pod_count / pod_count)
        if gpu_sum > 0:
            gpu_ratios.append(frac_gpu_sum / gpu_sum)
    rows = [
        {"source": "ASI", "metric": "ratio_task_num", "value": float(np.mean(task_ratios)) if task_ratios else np.nan},
        {"source": "ASI", "metric": "ratio_gpu_req", "value": float(np.mean(gpu_ratios)) if gpu_ratios else np.nan},
    ]
    write_csv(pd.DataFrame(rows), out_root / "figure_inputs/fig_compare_frac_gpu/asi_summary.csv")


def write_gpu_cpu_samples(workload_hourly: list[pd.DataFrame], out_root: Path) -> None:
    output = out_root / "figure_inputs/fig_gpu_cpu_request_num/asi_samples.csv"
    if not workload_hourly:
        write_csv(pd.DataFrame(columns=["workload_id", "gpu_request", "cpu_request_cores", "is_genai"]), output)
        return
    all_rows = pd.concat(workload_hourly, ignore_index=True)
    all_rows = all_rows.sort_values(["workload_id", "gpu_request", "day", "hour"], ascending=[True, False, True, True])
    chosen = all_rows.drop_duplicates("workload_id", keep="first")
    write_csv(chosen[["workload_id", "gpu_request", "cpu_request_cores", "is_genai"]], output)


def aggregate_server_partitions(data_root: Path, out_root: Path, server_pod: dict[tuple[str, str, str], list[float]]) -> dict:
    server_root = fact_table_root(data_root, "server_hourly")
    files = partition_files(server_root)
    if not files:
        print(f"No server_hourly parquet partitions found under {server_root}; skipping server-derived outputs.")
        return {"server_partitions": 0, "server_coverage": partition_coverage(files)}

    inventory: dict[tuple[str, str], float] = {}
    alloc_hourly: defaultdict[tuple[str, str, str], list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    idle_hourly: defaultdict[tuple[str, str, str], list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    asw_rows = []

    for day, hour, path in files:
        df = pd.read_parquet(
            path,
            columns=["server_id", "cluster_id", "asw_id", "gpu_spec_public", "gpu_count", "cpu_capacity_cores"],
        )
        to_numeric(df, ["gpu_count", "cpu_capacity_cores"])
        df["display_gpu_spec"] = df["gpu_spec_public"].map(normalize_spec)
        for row in df[df["gpu_count"] > 0][["server_id", "display_gpu_spec", "gpu_count"]].itertuples(index=False):
            inventory[(row.server_id, row.display_gpu_spec)] = float(row.gpu_count)

        if not in_day_range(day, PAPER_START_DAY, PAPER_END_DAY):
            continue
        for row in df.itertuples(index=False):
            vals = server_pod.get((str(day), hour, row.server_id), [0.0] * 8)
            hp_active, hp_standby, lp_alloc, hp_lp_active, requested_cpu_hp, requested_gpu_hp, hp_pod_rows, _unused = vals
            gpu_count = float(row.gpu_count) if not pd.isna(row.gpu_count) else 0.0
            cpu_capacity = float(row.cpu_capacity_cores) if not pd.isna(row.cpu_capacity_cores) else 0.0
            residual = max(hp_standby - lp_alloc, 0.0)
            if gpu_count > 0 and (hour_even(hour) or hour == "23"):
                ratio_hp = round((hp_active + residual) / gpu_count, 6)
                ratio_hp_lp = round((min(hp_lp_active, gpu_count) + residual) / gpu_count, 6)
                item = alloc_hourly[(str(day), hour, row.display_gpu_spec)]
                item[0] += ratio_hp
                item[1] += ratio_hp_lp
                item[2] += 1.0
            if gpu_count > 0 and hour_even(hour):
                if gpu_count == 16:
                    continue
                idle_gpus = max(gpu_count - (hp_active + residual), 0.0)
                idle_cpus = max(cpu_capacity - requested_cpu_hp, 0.0)
                for gpu_req, cpu_req, config in JOB_CONFIGS:
                    fractional = (
                        idle_gpus - math.floor(idle_gpus)
                        if idle_cpus >= cpu_req
                        and idle_gpus >= gpu_req
                        and idle_gpus - math.floor(idle_gpus) > 0
                        and math.floor(idle_gpus) >= gpu_req
                        else 0.0
                    )
                    insufficient_whole = (
                        math.floor(idle_gpus)
                        if idle_cpus >= cpu_req and math.floor(idle_gpus) > 0 and math.floor(idle_gpus) < gpu_req
                        else 0.0
                    )
                    if idle_cpus < cpu_req and idle_gpus >= gpu_req:
                        insufficient_cpu = float(gpu_req)
                    elif idle_cpus < cpu_req and 0 < idle_gpus < gpu_req:
                        insufficient_cpu = idle_gpus
                    else:
                        insufficient_cpu = 0.0
                    item = idle_hourly[(str(day), hour, config)]
                    item[0] += fractional
                    item[1] += insufficient_whole
                    item[2] += insufficient_cpu
                    item[3] += idle_gpus
            if hour == "10" and hp_pod_rows > 0 and not pd.isna(row.asw_id):
                spec = row.display_gpu_spec
                if spec in ASW_GPU_SPECS:
                    num_slots = min(
                        max(gpu_count - math.floor(requested_gpu_hp), 0.0),
                        max(math.floor((cpu_capacity - requested_cpu_hp) / 12.0), 0.0),
                    )
                    asw_rows.append(
                        {
                            "day": str(day),
                            "hour": hour,
                            "cluster_id": row.cluster_id,
                            "asw_id": row.asw_id,
                            "gpu_spec_public": spec,
                            "num_slots": num_slots,
                        }
                    )
                    asw_rows.append(
                        {
                            "day": str(day),
                            "hour": hour,
                            "cluster_id": row.cluster_id,
                            "asw_id": row.asw_id,
                            "gpu_spec_public": "heterogenous",
                            "num_slots": num_slots,
                        }
                    )

    write_gpu_spec_distribution(inventory, out_root)
    write_alloc_ratio(alloc_hourly, out_root)
    write_idle(idle_hourly, out_root)
    write_standby(server_pod, out_root)
    write_asw(asw_rows, out_root)
    return {"server_partitions": len(files), "server_coverage": partition_coverage(files)}


def write_gpu_spec_distribution(inventory: dict[tuple[str, str], float], out_root: Path) -> None:
    sums: defaultdict[str, float] = defaultdict(float)
    for (_server, spec), gpu_count in inventory.items():
        sums[spec] += gpu_count
    total = sum(sums.values())
    rows = [
        {
            "display_gpu_spec": spec,
            "gpu_spec_sum": value,
            "percentage": 100.0 * value / total if total else 0.0,
        }
        for spec, value in sorted(sums.items())
    ]
    write_csv(pd.DataFrame(rows), out_root / "aggregates/gpu_spec_distribution.csv")


def write_alloc_ratio(alloc_hourly: dict[tuple[str, str, str], list[float]], out_root: Path) -> None:
    spec_hour_rows = []
    for (day, hour, spec), vals in alloc_hourly.items():
        count = vals[2] if len(vals) > 2 else 0.0
        if count:
            spec_hour_rows.append({"gpu_spec_public": spec, "ratio_9300": vals[0] / count, "ratio_9200": vals[1] / count})
    if not spec_hour_rows:
        write_csv(pd.DataFrame(columns=["gpu_spec_public", "ratio_9300", "ratio_9200"]), out_root / "figure_inputs/fig_gpu_spec_alloc_ratio/server_alloc_summary.csv")
        return
    df = pd.DataFrame(spec_hour_rows)
    out = df.groupby("gpu_spec_public", as_index=False)[["ratio_9300", "ratio_9200"]].mean()
    write_csv(out, out_root / "figure_inputs/fig_gpu_spec_alloc_ratio/server_alloc_summary.csv")


def write_idle(idle_hourly: dict[tuple[str, str, str], list[float]], out_root: Path) -> None:
    hourly = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0, 0])
    for (day, hour, config), vals in idle_hourly.items():
        item = hourly[config]
        item[0] += vals[0]
        item[1] += vals[1]
        item[2] += vals[2]
        item[3] += vals[3]
        item[4] += 1
    rows = []
    for _gpu, _cpu, config in JOB_CONFIGS:
        vals = hourly.get(config, [0.0, 0.0, 0.0, 0.0, 0])
        count = vals[4]
        fractional = vals[0] / count if count else 0.0
        insufficient_whole = vals[1] / count if count else 0.0
        insufficient_cpu = vals[2] / count if count else 0.0
        total_idle = vals[3] / count if count else 0.0
        rows.append(
            {
                "job_config": config,
                "fractional_unallocatable": fractional,
                "insufficient_whole_unallocatable": insufficient_whole,
                "insufficient_cpu_unallocatable": insufficient_cpu,
                "total_idle_gpus": total_idle,
                "fractional_pct": 100.0 * fractional / total_idle if total_idle else 0.0,
                "insufficient_whole_pct": 100.0 * insufficient_whole / total_idle if total_idle else 0.0,
                "insufficient_cpu_pct": 100.0 * insufficient_cpu / total_idle if total_idle else 0.0,
            }
        )
    write_csv(pd.DataFrame(rows), out_root / "figure_inputs/fig_idle_gpu_fragmentation/summary.csv")


def write_standby(server_pod: dict[tuple[str, str, str], list[float]], out_root: Path) -> None:
    hourly = defaultdict(lambda: [0.0, 0.0, 0])
    for (day, hour, _server), vals in server_pod.items():
        hp_standby = vals[1]
        lp_alloc = vals[2]
        item = hourly[(day, hour)]
        item[0] += hp_standby
        if hp_standby > 0:
            item[1] += lp_alloc / hp_standby
            item[2] += 1
    rows = []
    for (day, hour), vals in sorted(hourly.items()):
        rows.append(
            {
                "day": day,
                "hour": hour,
                "standby_used_card_hour": vals[0],
                "standby_util_9300": vals[1] / vals[2] if vals[2] else np.nan,
            }
        )
    write_csv(pd.DataFrame(rows), out_root / "figure_inputs/fig_standby_temporal/hourly.csv")


def write_asw(asw_rows: list[dict], out_root: Path) -> None:
    if not asw_rows:
        write_csv(
            pd.DataFrame(columns=["day", "hour", "gpu_spec_public", "gpu_set_size", "total_slots_across_cluster", "total_slots_across_asw"]),
            out_root / "figure_inputs/fig_asw_available_slots/summary.csv",
        )
        return
    df = pd.DataFrame(asw_rows)
    cluster = df.groupby(["day", "hour", "gpu_spec_public", "cluster_id"], as_index=False)["num_slots"].sum()
    asw = df.groupby(["day", "hour", "gpu_spec_public", "asw_id"], as_index=False)["num_slots"].sum()
    rows = []
    for gpu_set_size in [128, 256]:
        c = cluster.copy()
        c["slots"] = np.floor(c["num_slots"] / gpu_set_size)
        csum = c.groupby(["day", "hour", "gpu_spec_public"], as_index=False)["slots"].sum()
        a = asw.copy()
        a["slots"] = np.floor(a["num_slots"] / gpu_set_size)
        asum = a.groupby(["day", "hour", "gpu_spec_public"], as_index=False)["slots"].sum()
        merged = csum.merge(asum, on=["day", "hour", "gpu_spec_public"], how="left", suffixes=("_cluster", "_asw"))
        merged["gpu_set_size"] = gpu_set_size
        for row in merged.itertuples(index=False):
            rows.append(
                {
                    "day": row.day,
                    "hour": row.hour,
                    "gpu_spec_public": row.gpu_spec_public,
                    "gpu_set_size": gpu_set_size,
                    "total_slots_across_cluster": row.slots_cluster,
                    "total_slots_across_asw": 0.0 if pd.isna(row.slots_asw) else row.slots_asw,
                }
            )
    write_csv(pd.DataFrame(rows), out_root / "figure_inputs/fig_asw_available_slots/summary.csv")


def summarize_network_samples(samples: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for job_type in NETWORK_JOB_TYPES:
        cur = samples[samples["job_types"].eq(job_type)]
        rx = pd.to_numeric(cur["server_receive_bps"], errors="coerce").to_numpy(dtype=float)
        tx = pd.to_numeric(cur["server_transmit_bps"], errors="coerce").to_numpy(dtype=float)
        rx = rx[np.isfinite(rx) & (rx > 0.001)]
        tx = tx[np.isfinite(tx) & (tx > 0.001)]
        rows.append(
            {
                "job_types": job_type,
                "server_count": int(len(cur)),
                "rx_p50_gibps": float(np.percentile(rx, 50)) if rx.size else np.nan,
                "rx_p95_gibps": float(np.percentile(rx, 95)) if rx.size else np.nan,
                "tx_p50_gibps": float(np.percentile(tx, 50)) if tx.size else np.nan,
                "tx_p95_gibps": float(np.percentile(tx, 95)) if tx.size else np.nan,
            }
        )
    return pd.DataFrame(rows)


def build_network_samples(data_root: Path, out_root: Path) -> int:
    pod_root = fact_table_root(data_root, "pod_hourly")
    server_root = fact_table_root(data_root, "server_hourly")
    network_root = fact_table_root(data_root, "network_hourly")
    network_files = [
        item for item in partition_files(network_root)
        if in_day_range(item[0], PAPER_START_DAY, PAPER_END_DAY)
    ]

    output = out_root / "figure_inputs/fig_server_network_cdf/server_network_samples.csv"
    summary = out_root / "figure_inputs/fig_server_network_cdf/summary.csv"
    for path in [output, summary]:
        if path.exists():
            path.unlink()

    columns = [
        "day",
        "hour",
        "server_id",
        "job_types",
        "server_gpu_spec",
        "server_gpu_amount",
        "server_receive_bps",
        "server_transmit_bps",
    ]
    if not network_files:
        write_csv(pd.DataFrame(columns=columns), output)
        write_csv(summarize_network_samples(pd.DataFrame(columns=columns)), summary)
        print(f"No network_hourly parquet partitions found under {network_root}; skipping network CDF input.")
        return 0

    row_count = 0
    for day, hour, network_path in network_files:
        pod_path = pod_root / f"day={day}" / f"hour={hour}" / "part-000.parquet"
        server_path = server_root / f"day={day}" / f"hour={hour}" / "part-000.parquet"
        if not pod_path.is_file() or not server_path.is_file():
            continue

        pods = pd.read_parquet(pod_path, columns=["server_id", "job_type_public", "gpu_request"])
        to_numeric(pods, ["gpu_request"])
        pods = pods[(pods["gpu_request"] > 0) & pods["server_id"].notna()].copy()
        pods = pods[pods["job_type_public"].isin(JOB_TYPES)].copy()
        if pods.empty:
            continue
        job_types = (
            pods[["server_id", "job_type_public"]]
            .drop_duplicates()
            .groupby("server_id", as_index=False)["job_type_public"]
            .agg(lambda values: ",".join(sorted(set(values))))
            .rename(columns={"job_type_public": "job_types"})
        )
        job_types = job_types[job_types["job_types"].isin(NETWORK_JOB_TYPES)]
        if job_types.empty:
            continue

        servers = pd.read_parquet(server_path, columns=["server_id", "gpu_spec_public", "gpu_count"])
        to_numeric(servers, ["gpu_count"])
        servers = servers[servers["gpu_count"].eq(8)].copy()
        servers["server_gpu_spec"] = servers["gpu_spec_public"].map(normalize_spec)
        servers = servers[["server_id", "server_gpu_spec", "gpu_count"]].rename(
            columns={"gpu_count": "server_gpu_amount"}
        )
        if servers.empty:
            continue

        network = pd.read_parquet(network_path, columns=["server_id", "rx_gibps_avg", "tx_gibps_avg"])
        to_numeric(network, ["rx_gibps_avg", "tx_gibps_avg"])
        network = network.rename(
            columns={
                "rx_gibps_avg": "server_receive_bps",
                "tx_gibps_avg": "server_transmit_bps",
            }
        )

        merged = job_types.merge(servers, on="server_id", how="inner").merge(network, on="server_id", how="inner")
        if merged.empty:
            continue
        merged = merged.assign(day=str(day), hour=hour)[columns]
        append_csv(merged, output)
        row_count += len(merged)

    if output.exists():
        samples = pd.read_csv(output)
    else:
        samples = pd.DataFrame(columns=columns)
        write_csv(samples, output)
    write_csv(summarize_network_samples(samples), summary)
    return row_count


def build_job_execution(data_root: Path, out_root: Path) -> int:
    job_root = fact_table_root(data_root, "job_execution_summary")
    candidates = [
        job_root / "part-000.parquet",
        job_root / "part-000.csv",
    ]
    path = next((p for p in candidates if p.is_file()), None)
    if path is None:
        print("No local job_execution_summary fact table found; skipping execution-time CDF input.")
        return 0
    public_columns = ["pod_id", "workload_id", "job_type_public", "model_type_public", "gpu_request", "duration_hours"]
    if path.suffix == ".parquet":
        df = pd.read_parquet(path, columns=public_columns)
    else:
        df = pd.read_csv(path, usecols=public_columns)
    to_numeric(df, ["gpu_request", "duration_hours"])
    df = df[(df["gpu_request"] > 0) & df["duration_hours"].notna() & (df["duration_hours"] >= 0)]
    id_columns = ["pod_id", "workload_id"]
    job = df[df["job_type_public"].isin(JOB_TYPES)].assign(
        group_type="job_type",
        group_name=lambda frame: frame["job_type_public"],
    )
    model = df[df["model_type_public"].isin(MODEL_TYPES)].assign(
        group_type="model_type",
        group_name=lambda frame: frame["model_type_public"],
    )
    output_columns = id_columns + ["group_type", "group_name", "duration_hours"]
    job = job[output_columns]
    model = model[output_columns]
    out = pd.concat([job, model], ignore_index=True)
    write_csv(out, out_root / "figure_inputs/fig_execution_time_cdf/job_execution_hours.csv")
    return len(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, default=DEFAULT_DATA_ROOT)
    parser.add_argument(
        "--out-root",
        type=Path,
        default=DEFAULT_OUT_ROOT,
        help="output root for aggregates and figure inputs; defaults to data/derived",
    )
    args = parser.parse_args()

    data_root = args.data_root.resolve()
    out_root = args.out_root.resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    pod_info = aggregate_pod_partitions(data_root, out_root)
    server_info = aggregate_server_partitions(data_root, out_root, pod_info["server_pod"])
    network_rows = build_network_samples(data_root, out_root)
    execution_rows = build_job_execution(data_root, out_root)
    manifest = {
        "source": "public ASI trace fact tables",
        "data_root": str(data_root.relative_to(RELEASE_ROOT) if data_root.is_relative_to(RELEASE_ROOT) else data_root),
        "out_root": str(out_root.relative_to(RELEASE_ROOT) if out_root.is_relative_to(RELEASE_ROOT) else out_root),
        "pod_partitions": pod_info["pod_partitions"],
        "pod_coverage": pod_info["pod_coverage"],
        "server_partitions": server_info["server_partitions"],
        "server_coverage": server_info["server_coverage"],
        "network_rows": network_rows,
        "execution_rows": execution_rows,
    }
    (out_root / "fact_derived_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
