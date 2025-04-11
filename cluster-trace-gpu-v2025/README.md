# Traces for GPU-Disaggregated Deep Learning Recommendation Models

## ℹ️ Overview

This repository contains a comprehensive trace dataset for GPU-disaggregated serving of Deep Learning Recommendation Models (DLRMs).
The dataset captures operational characteristics of **156 inference services**, comprising a total of **23,871 inference instances**. 
These instances are further divided into **16,485 CN (CPU Node) inference instances** and **7,386 HN (Heterogeneous GPU Node) inference instances**.

All instances in this dataset are categorized as *Latency-Sensitive (LS)* workloads, reflecting their critical performance requirements. These inference instances are typically **high-priority** and **long-running**, ensuring sustained availability and responsiveness for end users.

For a detailed description of the GPU-disaggregation scenario and system design, please refer to [our NSDI'25 paper](https://www.usenix.org/conference/nsdi25/presentation/yang).

## 🗄️ Dataset Details

The core dataset is provided in the file [`disaggregated_DLRM_trace.csv`](./disaggregated_DLRM_trace.csv).
Below is a sample excerpt from the dataset:

|  instance_sn   | role | app_name | cpu_request | cpu_limit | gpu_request | gpu_limit | rdma_request | rdma_limit | memory_request | memory_limit | disk_request | disk_limit | max_instance_per_node | creation_time | scheduled_time | deletion_time |
| :------------: | :--: | :------: | :---------: | :-------: | :---------: | :-------: | :----------: | :--------: | :------------: | :----------: | :----------: | :--------: | :-------------------: | :-----------: | :------------: | :-----------: |
|                |      |          |             |           |             |           |              |            |                |              |              |            |                       |               |                |               |
| instance_7185  |  HN  |  app_0   |     12      |    12     |      1      |     1     |      25      |     25     |     120.0      |    120.0     |    680.0     |   800.0    |           8           |               |                |               |
| instance_13574 |  CN  | app_130  |     64      |    64     |      0      |     0     |      1       |     1      |     320.0      |    320.0     |    255.0     |   300.0    |          -1           |   1435629.0   |   1435629.0    |   1435760.0   |

### Field Descriptions

- `instance_sn`: Unique identifier for the instance.
- `role`: Role of the instance.
  - `CN`: CPU Node
  - `HN`: Heterogeneous GPU Node
- `app_name`: Name of the application group to which the instance belongs. An application group is a collection of instances sharing the same application name. For example, `app_0` may contain multiple instances like `instance_0`, `instance_1`, etc.
- `cpu_request`: Number of CPU cores requested by the instance (in vCPUs).
- `cpu_limit`: Maximum number of CPU cores allowed for the instance (same as `cpu_request` in this scenario).
- `gpu_request`: Number of GPUs requested by the instance.
- `gpu_limit`: Maximum number of GPUs allowed for the instance (same as `gpu_request` in this scenario).
- `rdma_request`: Allocated percentage of the bandwidth of an RDMA Network Interface Card (RNIC), ranging from 0 to 100. Currently, this value is used as a constraint for scheduling density.
- `rdma_limit`: Maximum RDMA bandwidth allowed for the instance (same as `rdma_request` in this scenario).
- `memory_request`: Amount of main memory requested by the instance (in GiB).
- `memory_limit`: Maximum amount of main memory allowed for the instance (in GiB).
- `disk_request`: Amount of disk space requested by the instance (in GiB).
- `disk_limit`: Maximum amount of disk space allowed for the instance (in GiB).
- `max_instance_per_node`: Maximum number of instances of the same `app_name` that can be deployed on a single node. A value of `-1` indicates no deployment density limit.
- `creation_time`: Timestamp indicating when the instance was created, expressed as the difference in **seconds** from the trace start time. If the instance existed before the trace start time, this field is set to `NaN`.
- `scheduled_time`: Timestamp indicating when the instance was scheduled, expressed as the difference in **seconds** from the trace start time. If the instance was scheduled before the trace start time, this field is set to `NaN`.
- `deletion_time`: Timestamp indicating when the instance was deleted, expressed as the difference in seconds from the trace start time. If the instance was deleted after the trace end time, this field is set to `NaN`.

## 📝 Paper

Please cite our paper if it is helpful to your research.

```
@inproceedings{yang2025Prism,
    title = {GPU-Disaggregated Serving for Deep Learning Recommendation Models at Scale},
    author = {Lingyun Yang and Yongchen Wang and Yinghao Yu and Qizhen Weng and Jianbo Dong and Kan Liu and Chi Zhang and Yanyi Zi and Hao Li and Zechao Zhang and Nan Wang and Yu Dong and Menglei Zheng and Lanlan Xi and Xiaowei Lu and Liang Ye and Guodong Yang and Binzhang Fu and Tao Lan and Liping Zhang and Lin Qu and Wei Wang},
    booktitle = {22nd USENIX Symposium on Networked Systems Design and Implementation (NSDI 25)},
    year = {2025},
    series = {{USENIX} {NSDI} '25},
    url = {https://www.usenix.org/conference/nsdi25/presentation/yang},
    publisher = {{USENIX} Association}
}
```
