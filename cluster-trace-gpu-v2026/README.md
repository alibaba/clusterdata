# Alibaba Cluster Trace GPU v2026

## Introduction

This release provides an anonymized GPU cluster trace from Alibaba Serverless
Infrastructure (ASI), a hyperscale production AI cluster that serves
heterogeneous workloads including ad-hoc development, training, online
inference, and offline inference.  The trace spans about six months and, at the
hourly peak, covers 155,410 GPUs across 37,707 GPU servers.

The trace accompanies the paper [*Heterogeneity at Hyperscale:
Characterization and Scheduling of Large Production AI Clusters at
Alibaba*](https://www.usenix.org/conference/osdi26/presentation/li-suyi).  The
paper studies six months of production behavior from a large heterogeneous GPU
fleet, including workload mix, GPU and CPU requests, priority classes, resource
utilization, network traffic, standby capacity, and scheduler-facing topology.
The released dataset is intended to support research on AI cluster
characterization, heterogeneous GPU scheduling, resource fragmentation,
priority-aware resource sharing, and trace-driven simulation.

If you use this trace, please cite the paper:

```bibtex
@inproceedings{asi_trace_2026,
  title = {Heterogeneity at Hyperscale: Characterization and Scheduling of Large Production AI Clusters at Alibaba},
  author = {Suyi Li and Lingyun Yang and Haoxuan Yu and Sheng Yao and Tianyuan Wu and Xiaoxiao Jiang and Hanfeng Lu and Kangjin Wang and Chenhao Wang and Shenglin Xu and Lun Wang and Qingyang Duan and Shenghao Liang and Xiu Lin and Wenchao Wu and Yinghao Yu and Guodong Yang and Liping Zhang and Wei Wang},
  booktitle = {20th USENIX Symposium on Operating Systems Design and Implementation (OSDI 26)},
  year = {2026}
}
```

## Data Download

The fact tables are hosted separately from GitHub at:

```text
https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-gpu-v2026/data/
```

Download the four ZIP archives, place them under `data/`, and unzip them before
running the reproduction workflow.  The archive list, sizes, and expected
directory layout are documented in [docs/data_download.md](docs/data_download.md).

## Dataset Contents

The public release contains four fact tables:

| Table | Coverage | Purpose |
| --- | --- | --- |
| `asi_opensource_pod_hourly` | `day=0..184`, all 24 hours | Hourly pod workload, request, utilization, priority, state, and public job/model buckets. |
| `asi_opensource_server_hourly` | `day=0..184`, all 24 hours | Hourly server inventory and anonymized ASW/rack topology. |
| `asi_opensource_network_hourly` | `day=109..115`, all 24 hours | Hourly node-level receive/transmit traffic samples for the network figure. |
| `asi_opensource_job_execution_summary` | Non-partitioned | Pod/workload execution-span summary for execution-time CDFs. |

Time is relative.  `day=0` is the trace start day.  The released fact tables do
not contain calendar dates, raw pod names, raw server serial numbers, raw
cluster names, raw owner names, raw pod YAML, or internal organization fields.

Detailed field definitions are in [docs/schema.md](docs/schema.md).

## Reproducing Figures

The release includes scripts for rebuilding the aggregate inputs and
trace-data figures used in the paper from the public fact tables.  Detailed
commands, figure-to-script mapping, and derived input locations are documented in
[docs/figure_reproduction.md](docs/figure_reproduction.md).
