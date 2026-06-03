# Data Download

The ASI GPU trace fact tables are hosted separately from GitHub:

```text
https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-gpu-v2026/data/
```

Download the four ZIP archives into `cluster-trace-gpu-v2026/data/`:

| Archive | Size | Contents |
| --- | ---: | --- |
| `asi_opensource_pod_hourly.zip` | 351,803,513,445 bytes | `asi_opensource_pod_hourly/` |
| `asi_opensource_server_hourly.zip` | 3,080,121,387 bytes | `asi_opensource_server_hourly/` |
| `asi_opensource_network_hourly.zip` | 203,904,100 bytes | `asi_opensource_network_hourly/` |
| `asi_opensource_job_execution_summary.zip` | 1,188,295,031 bytes | `asi_opensource_job_execution_summary/` |

Example:

```bash
mkdir -p data
cd data
curl -fL -O https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-gpu-v2026/data/asi_opensource_pod_hourly.zip
curl -fL -O https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-gpu-v2026/data/asi_opensource_server_hourly.zip
curl -fL -O https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-gpu-v2026/data/asi_opensource_network_hourly.zip
curl -fL -O https://tre-clusterdata.oss-cn-hangzhou.aliyuncs.com/cluster-trace-gpu-v2026/data/asi_opensource_job_execution_summary.zip
unzip asi_opensource_pod_hourly.zip
unzip asi_opensource_server_hourly.zip
unzip asi_opensource_network_hourly.zip
unzip asi_opensource_job_execution_summary.zip
cd ..
```

After extraction, the release directory should look like:

```text
cluster-trace-gpu-v2026/
  data/
    asi_opensource_pod_hourly/day=<day>/hour=<hour>/part-000.parquet
    asi_opensource_server_hourly/day=<day>/hour=<hour>/part-000.parquet
    asi_opensource_network_hourly/day=<day>/hour=<hour>/part-000.parquet
    asi_opensource_job_execution_summary/part-000.parquet
```

After the local `data/` directory is ready, follow
[figure_reproduction.md](figure_reproduction.md) to build aggregates and
generate figures.
