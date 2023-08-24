# Traces for [Kubernetes Scheduler Simulator](https://github.com/hkust-adsl/kubernetes-scheduler-simulator)

## ℹ️ Basics

This repo contains trace data for the [Kubernetes Scheduler Simulator](https://github.com/hkust-adsl/kubernetes-scheduler-simulator), which evaluates different scheduling policies in GPU-sharing clusters.
It includes the Fragmentation Gradient Descent (FGD) policy proposed in the [USENIX ATC 2023](https://www.usenix.org/conference/atc23) paper "[Beware of Fragmentation: Scheduling GPU-Sharing Workloads with Fragmentation Gradient Descent](https://www.usenix.org/conference/atc23/presentation/weng)", along with other baseline policies (e.g., Best-fit, Dot-product, GPU Packing, GPU Clustering, Random-fit). 

## 🗄️ Traces

Key data is in the csv folder, while yaml files can be generated from this data.

### [openb_node_list_all_node.csv](./csv/openb_node_list_all_node.csv)

This file contains 1523 nodes of a heterogeneous GPU cluster in production, listing their CPU, main memory, GPU specifications and GPU types.

[openb_node_list_gpu_node.csv](./csv/openb_node_list_gpu_node.csv) is a subset excluding non-GPU nodes. [openb_node_list_gpu_node.yaml](./node_yaml/openb_node_list_gpu_node.yaml) contains the same data in YAML format.

Here's a sample output:

|    | sn              |   cpu_milli |   memory_mib |   gpu | model   |
|---:|:----------------|------------:|-------------:|------:|:--------|
|  0 | openb-node-0227 |       32000 |       262144 |     0 | nan     |
|  1 | openb-node-0228 |      128000 |       786432 |     8 | G3      |
|  2 | openb-node-0229 |       96000 |       786432 |     8 | V100M32 |

- `cpu_milli`: Number of CPUs (in milli)
- `memory_mib`: Main memory (in MiB)
- `gpu`: Number of GPUs
- `model`: GPU type. G1, G2, G3 are undisclosed internal GPU codes.

### [openb_pod_list_default.csv](./csv/openb_pod_list_default.csv)

This file contains 8152 tasks submitted to the GPU cluster, listing their resource specifications, QoS, phase and creation/deletion/scheduled times. 

The other openb_pod_list_*.csv files (excluding the gpuspec ones) are sampled from the default one, emphasizing certain types of workloads (e.g., CPU-only tasks, GPU-sharing tasks, multi-GPU tasks).

Trace files with `gpuspec` augment tasks with GPU type requirements. About 33% of GPU tasks in our production cluster have GPU type constraints (see [openb_pod_list_gpuspec33.csv](./csv/openb_pod_list_gpuspec33.csv) and Sec. 6.5 in the "[Beware of Fragmentation](https://www.usenix.org/conference/atc23/presentation/weng)" paper).

Here's a sample output:

|    | name           |   cpu_milli |   memory_mib |   num_gpu |   gpu_milli | gpu_spec        | qos       | pod_phase   |   creation_time |   deletion_time |   scheduled_time |
|---:|:---------------|------------:|-------------:|----------:|------------:|:----------------|:----------|:------------|----------------:|----------------:|-----------------:|
|  0 | openb-pod-0017 |       88000 |       327680 |         8 |        1000 | nan             | Burstable | Succeeded   |         9437497 |        10769854 |          9437497 |
|  1 | openb-pod-0022 |        4000 |        15258 |         1 |         220 | nan             | BE        | Running     |         9679175 |         9973826 |          9679175 |
|  2 | openb-pod-0035 |       16000 |        32768 |         1 |        1000 | V100M16\|V100M32 | LS        | Running     |         9967058 |         9968575 |          9967063 |

- `cpu_milli`: Number of CPUs requested (in milli)
- `memory_mib`: Main memory requested (in MiB)
- `num_gpu`: Number of GPUs requested (integers from 0 to 8)
- `gpu_milli`: Detailed GPU requested for GPU-sharing workloads (i.e., `num_gpu==1`) (in milli).
- `gpu_spec`: Required GPU types, For example, `nan` means no GPU type constraints while `V100M16|V100M32` means the task can run on [NVIDIA V100](https://www.nvidia.com/en-us/data-center/v100/) with either 16GB VRAM or 32GB VRAM.
- `qos`: [Quality of Service](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/) (e.g., Burstable, Best Effort (BE), Latency Sensitive (LS))
- `pod_phrase`: Succeeded, Running, Pending, Failed
- `creation_time`: Timestamp of creation (in seconds)
- `deletion_time`: Timestamp of deletion (in seconds)
- `scheduled_time`: Timestamp of being scheduled (in seconds)

## 🛠 Usage

Generate the YAML files needed for the simulation experiment based on the original CSV files.

```bash
$ bash prepare_input.sh
```

For cluster scheduling simulation on Kubernetes, refer to the Kubernetes Scheduler Simulator repo: https://github.com/hkust-adsl/kubernetes-scheduler-simulator.

## 📝 Paper

Please cite our paper if it is helpful to your research.

```
@inproceedings{FGD2023,
    title = {Beware of Fragmentation: Scheduling GPU-Sharing Workloads with Fragmentation Gradient Descent},
    author = {Qizhen Weng and Lingyun Yang and Yinghao Yu and Wei Wang and Xiaochuan Tang and Guodong Yang and Liping Zhang},
    booktitle = {2023 {USENIX} Annual Technical Conference},
    year = {2023},
    series = {{USENIX} {ATC} '23},
    url = {https://www.usenix.org/conference/atc23/presentation/weng},
    publisher = {{USENIX} Association}
}
```
