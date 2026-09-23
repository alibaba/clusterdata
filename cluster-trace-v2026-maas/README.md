# cluster-trace-v2026-maas

## Introduction

This release provides an anonymized six-month LLM inference trace from xMaaS,
a production Model-as-a-Service platform at Alibaba serving both online
applications and offline batch jobs. The study covers over 100,000 GPUs across
56 clusters and 30 GPU types, with approximately 300,000 applications and
70,000 model variants.

The trace accompanies our paper **Model-as-a-Service in the Wild:
Characterizing Production LLM Inference Clusters at Scale** (ACM ATC 2026).
The paper analyzes production inference at the cluster, application, and model
levels, revealing heterogeneous resource allocation, differences between
online and offline workloads, GPU memory overprovisioning, persistent memory
residency of cold models, and prefill-decode resource imbalance. The released
dataset is intended to support research on heterogeneous GPU scheduling,
elastic scaling, capacity planning, and resource-efficient LLM inference.

If you use this trace, please cite the paper:

```bibtex
@inproceedings{inference_trace_2026,
  title = {Model-as-a-Service in the Wild: Characterizing Production {LLM} Inference Clusters at Scale},
  author = {Yiyun Zheng and Lingyun Yang and Yinghao Yu and Guodong Yang and Liping Zhang and Minchen Yu},
  booktitle = {2026 ACM SIGOPS Annual Technical Conference (ATC 26)},
  year = {2026}
}
```

## Data Download

The dataset is currently undergoing internal compliance review and is expected
to be released soon via Alibaba Cloud OSS. Download links will be added here
once the review is complete. Place the downloaded files in the layout below;
Parquet shards are read directly and do not need to be merged.

```text
data/
  instance_daily/part_*.parquet
  instance_week_5min/part_*.parquet
  app_metrics.csv
  app_cases.json
  manifest.json
docs/
  schema.md
  figure_reproduction.md
scripts/
output/                     # Generated tables and figures
requirements.txt
```

## Dataset Contents

| Dataset | Coverage | Rows | Files / size |
| --- | --- | ---: | --- |
| `instance_daily/` | Six months; daily instance segments | 145,083,117 | 61 Parquet files / 9.805 GiB |
| `instance_week_5min/` | One week; five-minute instance observations | 140,906,827 | 21 Parquet files / 4.482 GiB |
| `app_metrics.csv` | One week; hourly application cases | 7,401 | One CSV |

Field definitions are in [docs/schema.md](docs/schema.md).

## Reproducing Figures

Scripts reproduce Tables 2–4 and the supported panels of Figures 2–18.
See [docs/figure_reproduction.md](docs/figure_reproduction.md) for commands,
figure-to-script mapping, and reproduction scope.
