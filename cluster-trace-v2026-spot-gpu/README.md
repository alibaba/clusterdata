# Traces for AI jobs leveraging spot GPU resources
## ℹ️ Overview
This repository contains a comprehensive trace dataset for AI jobs leveraging spot GPU resources.   
The node dataset captures the operational characteristics of **4278 GPU nodes** and contains a total of **6 GPU card types**.

We categorize AI jobs as as _High-Priority_ (HP) workloads with **strict SLOs** and _Spot_ workloads that used  **spot instances as opportunistic resources**. The job details are presented in the workload dataset.

Based on such traces, we have also developed a scheduling framework that maximizes the SLO guarantee for spot workloads with spot GPU provisioning predictions. For detailed description, please refer to [our ASPLOS'26 paper](https://www.xxx).

## 🗄️ Dataset Details
The node dataset is provided in the file `node_info_df.csv`.  
Below is a sample excerpt from the dataset:

| <font style="color:black;">node_name</font> | <font style="color:black;">gpu_model</font> | <font style="color:black;">gpu_capacity_num</font> | <font style="color:black;">cpu_num</font> |
| --- | --- | --- | --- |
| <font style="color:black;">0</font> | <font style="color:black;">GPU-series-1</font> | <font style="color:black;">4</font> | <font style="color:black;">192</font> |
| <font style="color:black;">1</font> | <font style="color:black;">GPU-series-1</font> | <font style="color:black;">1</font> | <font style="color:black;">192</font> |
| <font style="color:black;">2</font> | <font style="color:black;">A10</font> | <font style="color:black;">1</font> | <font style="color:black;">128</font> |
| <font style="color:black;">3</font> | <font style="color:black;">A100-SXM4-80GB</font> | <font style="color:black;">8</font> | <font style="color:black;">128</font> |


### Field Descriptions
+ `node_name`: Unique identifier for the node.
+ `gpu_model`: Type of GPU cards. For example, A10, A100-SXM4-80GB, etc.
+ `gpu_capacity_num`: GPU capacity of the node. A node may exhibit heterogeneous GPU configurations.  For example, `node_0` have `4` GPUs and `node_3` have `8` GPUs, etc.
+ `cpu_num`: Number of CPU cores in a node (in vCPUs).



The node dataset is provided in the file `job_info_df.csv`.  
Below is a sample excerpt from the dataset:

| <font style="color:black;">job_name</font> | <font style="color:black;">organization</font> | <font style="color:black;">gpu_model</font> | <font style="color:black;">cpu_request</font> | <font style="color:black;">gpu_request</font> | <font style="color:black;">worker_num</font> | <font style="color:black;">submit_time</font> | <font style="color:black;">duration</font> | <font style="color:black;">job_type</font> |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| <font style="color:black;">239255</font> | <font style="color:black;">13</font> | <font style="color:black;">A10</font> | <font style="color:black;">20</font> | <font style="color:black;">1</font> | <font style="color:black;">1</font> | <font style="color:black;">0</font> | <font style="color:black;">2764799</font> | <font style="color:black;">HP</font> |
| <font style="color:black;">253689</font> | <font style="color:black;">13</font> | <font style="color:black;">A10</font> | <font style="color:black;">8</font> | <font style="color:black;">1</font> | <font style="color:black;">1</font> | <font style="color:black;">0</font> | <font style="color:black;">15897599</font> | <font style="color:black;">HP</font> |
| <font style="color:black;">437260</font> | <font style="color:black;">57</font> | <font style="color:black;">A100-SXM4-80GB</font> | <font style="color:black;">15</font> | <font style="color:black;">1</font> | <font style="color:black;">16</font> | <font style="color:black;">9589663</font> | <font style="color:black;">41060</font> | <font style="color:black;">Spot</font> |
| <font style="color:black;">437261</font> | <font style="color:black;">57</font> | <font style="color:black;">A100-SXM4-80GB</font> | <font style="color:black;">15</font> | <font style="color:black;">1</font> | <font style="color:black;">94</font> | <font style="color:black;">9589663</font> | <font style="color:black;">71718</font> | <font style="color:black;">Spot</font> |


### Field Descriptions
+ `job_name`: Unique identifier for the job.
+ `organization`: Cost organizations, which encompass various administrative units, like departments, agencies, etc.
+ `gpu_model`: Type of GPU cards requested by the job.
+ `cpu_request`: Number of CPU cores requested by the job (in vCPUs).
+ `gpu_request`: Number of GPU requested by the job.
+ `worker_num`: Number of instances requested by the job.
+ `submit_time`: Timestamp indicating when the job requests, expressed as the difference in seconds from the first submitted job.
+ `duration`: Duration of job (in seconds)
+ `job_type`: Type of job:
    - High-priority job
    - Spot job

## 📝 Paper
Please cite our paper if it is helpful to your research.

```plain
@inproceedings{duan2026GFS,
    title = {GFS: A Preemptive Scheduling Framework for GPU Clusters with Predictive Spot Management},
    author = {Jiaang Duan and Shenglin Xu and Shiyou Qian and Dingyu Yang and Kangjin Wang and Chenzhi Liao and Yinghao Yu and Qin Hua and Hanwen Hu and Qi Wang and Wenchao Wu and Dongqing Bao and Tianyu Lu and Jian Cao and Guangtao Xue and Guodong Yang and Liping Zhang and Gang Chen},
    booktitle = {Proceedings of the 31th {ACM} International Conference on Architectural
                  Support for Programming Languages and Operating Systems,{ASPLOS} 2026},
    year = {2026},
    url = {},
    publisher = {ACM}
}
```

