# Public Fact Table Schema

All identifiers are stable salted hashes within this release and are not meant
to be joined with identifiers from other datasets.  Time is exposed as relative
`day` and `hour` partitions; `day=0` is the first day of the released trace.
The public fact tables do not contain raw pod names, raw workload names, raw
server serial numbers, raw cluster names, raw ASW/rack names, raw pod YAML, raw
model names, organization fields, or calendar dates.

The schema is organized around the paper's main analysis dimensions: workload
type, model type, priority class, GPU model, resource requests, resource
utilization, server inventory, and ASW-level topology.  Most figure
reproduction scripts filter to GPU-requesting pods with `gpu_request > 0`.

## `asi_opensource_pod_hourly`

One row describes one pod observed on a GPU server during one hour.  The table
also contains pods with zero GPU request when they are observed on GPU servers;
GPU workload analyses filter these rows with `gpu_request > 0`.

| Field | Type | Description |
| --- | --- | --- |
| `pod_id` | string | Stable anonymized pod identifier. |
| `workload_id` | string | Stable anonymized workload identifier when source owner/workload metadata is available; otherwise null.  Multiple pods may share one `workload_id`. |
| `server_id` | string | Stable anonymized hosting server identifier. |
| `cluster_id` | string | Stable anonymized cluster identifier. |
| `state_public` | string | Public pod state bucket in this hour: `Standby`, `Running`, `Pending`, `Succeeded`, `Failed`, or `Unknown`.  `Standby` is used by the standby-capacity analysis in the paper. |
| `gpu_spec_public` | string | Public GPU model bucket. |
| `server_gpu_count` | double | Number of GPUs on the hosting server. |
| `server_cpu_capacity_cores` | double | CPU capacity of the hosting server in cores. |
| `priority_class` | string | Public priority bucket: `HP`, `LP`, or `Other`; this captures the high-priority versus low-priority/spot distinction used in the paper. |
| `job_type_public` | string | Public workload type: `training`, `online_inference`, `offline_inference`, `dev`, `other`, or `unknown`. |
| `model_type_public` | string | Public model type: `genai`, `rec`, `cv`, `embedding`, `dev`, or `unknown`. |
| `is_genai_request` | boolean | Whether the request matches the public GenAI detection rules used to form the `genai` model bucket. |
| `gpu_request` | double | Requested GPU-equivalent count.  `1.0` means one full GPU; fractional values are fractional-GPU requests. |
| `gpu_mem_request` | double | Source-reported accelerator memory request. |
| `cpu_request_cores` | double | Requested CPU cores. |
| `used_gpu_hours` | double | GPU-hours attributed to the pod in this hour.  A pod using one full GPU for a full hour contributes approximately `1.0`. |
| `avg_gpu_sm_util` | double | Source-reported average GPU SM utilization for the pod in this hour. |
| `avg_gpu_mem_gib` | double | Average GPU memory use in GiB. |
| `avg_cpu_request_util` | double | Average CPU utilization normalized by requested CPU. |
| `avg_memory_util` | double | Average memory utilization. |
| `ready_status` | boolean | Whether the pod became ready according to source metadata. |
| `schedule_delay_sec` | int64 | Scheduling delay in seconds when available. |
| `ready_delay_sec` | int64 | Delay from scheduling to ready state in seconds when available. |
| `day` | partition string | Relative day from trace start. |
| `hour` | partition string | Hour of day, `00` through `23`. |

## `asi_opensource_server_hourly`

One row describes one GPU server's inventory and topology in one hour.  This
table intentionally stores server facts only; HP/LP allocation, idle-resource,
and fragmentation aggregates are recomputed from `asi_opensource_pod_hourly`.

| Field | Type | Description |
| --- | --- | --- |
| `server_id` | string | Stable anonymized server identifier. |
| `cluster_id` | string | Stable anonymized cluster identifier. |
| `asw_id` | string | Stable anonymized access-switch/rack-domain identifier when available.  This field supports ASW-local placement and topology analyses. |
| `gpu_spec_public` | string | Public GPU model bucket for the server. |
| `gpu_count` | double | Number of GPUs on the server. |
| `cpu_capacity_cores` | double | Server CPU capacity in cores. |
| `day` | partition string | Relative day from trace start. |
| `hour` | partition string | Hour of day, `00` through `23`. |

## `asi_opensource_network_hourly`

One row describes one server's average network traffic in one hour.  The
released network table covers the shorter paper window used by the node-level
network utilization figure.

| Field | Type | Description |
| --- | --- | --- |
| `server_id` | string | Stable anonymized server identifier. |
| `rx_gibps_avg` | double | Average receive traffic in GiB/s during the hour. |
| `tx_gibps_avg` | double | Average transmit traffic in GiB/s during the hour. |
| `day` | partition string | Relative day from trace start. |
| `hour` | partition string | Hour of day, `00` through `23`. |

## `asi_opensource_job_execution_summary`

One row describes one pod/workload execution span used by execution-time CDFs.
It uses the same `pod_id` and `workload_id` definitions as
`asi_opensource_pod_hourly`.  This table is non-partitioned and contains only
GPU-requesting execution spans.

| Field | Type | Description |
| --- | --- | --- |
| `pod_id` | string | Stable anonymized pod identifier. |
| `workload_id` | string | Stable anonymized workload identifier when source owner/workload metadata is available; otherwise null. |
| `server_id` | string | Stable anonymized server identifier when available. |
| `gpu_spec_public` | string | Public GPU model bucket. |
| `priority_class` | string | Public priority bucket: `HP`, `LP`, or `Other`. |
| `job_type_public` | string | Public workload type bucket. |
| `model_type_public` | string | Public model type bucket. |
| `is_genai_request` | boolean | Whether the request matches the public GenAI detection rules. |
| `gpu_request` | double | Requested GPU-equivalent count for the execution span. |
| `duration_hours` | double | Execution duration in hours, derived from the observed execution samples. |
| `schedule_delay_sec` | int64 | Scheduling delay in seconds when available. |
| `ready_delay_sec` | int64 | Delay from scheduling to ready state in seconds when available. |
| `ready_status` | boolean | Whether the pod became ready according to source metadata. |
| `schedule_status` | boolean | Whether scheduling metadata indicates a scheduled pod. |

## Public Value Sets

Priority:

| Value | Meaning |
| --- | --- |
| `HP` | High-priority workload with guaranteed resources. |
| `LP` | Low-priority/spot workload that can use flexible capacity. |
| `Other` | Priority outside the HP/LP bands. |

Job type:

| Value | Meaning |
| --- | --- |
| `training` | Training workloads. |
| `online_inference` | Online inference workloads. |
| `offline_inference` | Offline or batch inference workloads. |
| `dev` | Development workloads such as notebooks and IDE sessions. |
| `other` | Other known workload labels. |
| `unknown` | Missing or unavailable workload type. |

Model type:

| Value | Meaning |
| --- | --- |
| `genai` | LLM/VLM/diffusion/AIGC-style model requests detected by public rules. |
| `rec` | Recommendation models. |
| `cv` | Computer vision models. |
| `embedding` | Embedding models. |
| `dev` | Development model bucket. |
| `unknown` | Missing or unavailable model type. |

GPU model:

`gpu_spec_public` uses normalized public GPU model buckets.  The released fact
tables expose only these public labels.
