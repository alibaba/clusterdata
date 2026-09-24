# Data Download

The MaaS trace datasets are hosted separately from GitHub:

```text
https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-v2026-maas/data/
```

Download the three ZIP archives into `cluster-trace-v2026-maas/data/`:

| Archive | Size | Contents |
| --- | ---: | --- |
| `instance_daily.zip` | 10,528,173,427 bytes | `instance_daily/` |
| `instance_week_5min.zip` | 4,812,189,789 bytes | `instance_week_5min/` |
| `app_metrics.csv.zip` | 99,947 bytes | `app_metrics.csv` |

Run from `cluster-trace-v2026-maas/`:

```sh
cd data
curl -fL -O https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-v2026-maas/data/instance_daily.zip
curl -fL -O https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-v2026-maas/data/instance_week_5min.zip
curl -fL -O https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-v2026-maas/data/app_metrics.csv.zip
unzip instance_daily.zip
unzip instance_week_5min.zip
unzip app_metrics.csv.zip
cd ..
```

After extraction, the data directory should contain:

```text
data/
  instance_daily/part_*.parquet
  instance_week_5min/part_*.parquet
  app_metrics.csv
  app_cases.json
  manifest.json
```

The JSON files are included in the repository. Parquet shards are read directly
and do not need to be merged.

Follow [figure_reproduction.md](figure_reproduction.md) to reproduce the tables
and figures.
