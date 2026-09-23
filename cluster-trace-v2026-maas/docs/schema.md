# Data schema

IDs are anonymized and shared across tables. Time uses a common origin:
`day = floor(time_s / 86400)`. Daily coverage is days 0–181, excluding day 172;
weekly and application coverage is days 140–146.

NULL and empty strings are distinct. CSV `\N` denotes NULL; `base_id = '-'`
is a preserved placeholder. Parquet shards are not date partitions.

## Daily instances: `instance_daily/`

One row describes an instance segment within a day. Multiple segments per
instance-day are valid, and their GPU-hours are additive.

| Field | Meaning |
| --- | --- |
| `day` | Relative day, starting at 0. |
| `instance_id` | Instance identifier. |
| `app_id` | Application identifier. |
| `model_id` | `b_`: base-only; `s_`: SFT-only; `x_`: both; `o_`: other source name classes. |
| `base_id` | Base-model identifier. |
| `cluster_id` | Cluster identifier. |
| `site_id` | Site identifier. |
| `gpu_type` | Anonymized GPU type; `unknown_` IDs represent unknown source labels. |
| `workload` | `online` or `offline`. |
| `model_arch` | `dense` or `moe`; architecture grouping used by figures. |
| `params_b` | Total parameters in billions, not active MoE parameters; NULL if unavailable. |
| `pd_role` | `prefill`, `decode`, or `fused` (PD-collocated). |
| `gpu_count` | Allocated GPU equivalents; fractional values are allowed. |
| `gpu_hours` | Allocated GPU Time for the segment, in GPU-hours. |
| `samples` | Number of source telemetry observations in the segment. |
| `zero_samples` | Number of source observations with zero duty cycle. |
| `sm_util` | Mean SM utilization normalized by allocated GPU equivalents, %. |
| `gpu_mem_util` | Mean GPU memory used divided by allocated GPU memory, %. |
| `cpu_usage` | Mean CPU usage, in cores. |
| `mem_usage` | Mean host memory usage, in GiB. |
| `base_arch` | Base-model classification: `dense`, `moe`, or `unknown`. |
| `variant_arch` | Variant classification: `dense` or `moe`. |
| `gpu_mem_alloc` | Total allocated GPU memory for the instance segment, in GiB. |

## Weekly instances: `instance_week_5min/`

One row contains five-minute averages of source 20-second observations, grouped
by `(instance_id, time_s, cluster_id, gpu_count)`.

| Field | Meaning |
| --- | --- |
| `instance_id` | Instance identifier shared with the daily table. |
| `time_s` | Window start in relative seconds; covers `[time_s, time_s + 300)`. |
| `cluster_id` | Cluster identifier. |
| `gpu_count` | Allocated GPU equivalents. |
| `sm_util` | Mean SM utilization, %. |
| `gpu_mem_util` | Mean GPU memory utilization, %. |
| `cpu_usage` | Mean CPU usage, in cores. |
| `mem_usage` | Mean host memory usage, in GiB. |
| `samples` | Number of contributing 20-second records. |

## Application cases: `app_metrics.csv`

One row is an hourly metric for a monitoring series. Case IDs and QPS
normalization are specified in `app_cases.json`.

| Field | Meaning |
| --- | --- |
| `time_s` | Hourly observation timestamp in relative seconds. |
| `app_id` | Application identifier shared with the daily table. |
| `gpu_type` | GPU-type identifier, or NULL when unspecified. |
| `series_id` | Monitoring-series identifier; not an instance identifier. |
| `pd_role` | `prefill`, `decode`, or NULL for observations without a phase label. |
| `metric` | Metric name from the list below. |
| `value` | Numeric observation in the metric's units. |

| Metric | Meaning / unit |
| --- | --- |
| `qps_norm` | Normalized QPS; the absolute QPS scale is not released. |
| `gpu_count` | Allocated GPU equivalents. |
| `input_tokens`, `output_tokens` | Mean input/output token counts. |
| `ttft`, `tpot` | Mean time to first token / time per output token, ms. |
| `kv_cache_util` | KV-pool used-to-allocated ratio, %. |
| `prefill_latency`, `kv_transfer_latency` | Mean prefill / KV cache transfer latency, ms. |
| `sm_util`, `gpu_mem_util` | SM / GPU memory utilization, %. |

## Table relationships

Join weekly instances to a deduplicated daily `(instance_id, day, workload)`
mapping. Application cases share `app_id` and `gpu_type` with the daily table;
`series_id` identifies a monitoring series, not an instance.
