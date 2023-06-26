# Alibaba Cluster Trace Program

## Overview

The *Alibaba Cluster Trace Program* is published by Alibaba Group. By providing cluster trace from real production, the program helps the researchers, students and people who are interested in the field to get better understanding of the characterastics of modern internet data centers (IDC's) and the workloads.

So far, four versions of traces have been released:

* *cluster-trace-v2017* includes about 1300 machines in a period of 12 hours. The trace-v2017 firstly introduces the collocation of online services (aka long running applications) and batch workloads. To see more about this trace, see related documents ([trace_2017](./cluster-trace-v2017/trace_201708.md)). Download link is available after a short survey ([survey link](https://goo.gl/forms/eOoe6DwZQpd2H5n53)).
* *cluster-trace-v2018* includes about 4000 machines in a period of 8 days. Besides having larger scaler than trace-v2017, this piece trace also contains  the DAG information of our production batch workloads. See related documents for more details ([trace_2018](./cluster-trace-v2018/trace_2018.md)). Download link is available after a survey (less than a minute, [survey link](http://alibabadeveloper.mikecrm.com/BdJtacN)).
* *cluster-trace-gpu-v2020* includes over 6500 GPUs (on ~1800 machines)  in a period of 2 months. It describes the AI/ML workloads in the MLaaS (Machine-Learning-as-a-Service) provided by the [Alibaba PAI (Platform for Artificial Intelligence)](https://www.alibabacloud.com/product/machine-learning) on GPU clusters. See the subdirectory ([pai_gpu_trace_2020](./cluster-trace-gpu-v2020/README.md)) for the released data, schema, and scripts for processing and visualization. Our analysis paper published in USENIX NSDI '22 is available [here](https://www.usenix.org/conference/nsdi22/presentation/weng).
* *cluster-trace-microservices-v2021* contains 20000+ microservices in a period of 12 hours. The traces the first released to introduce the runtime metrics of microservices in the production cluster, including call dependencies, respond time, call rates, and so on. See the subdirectory ([trace_2021](./cluster-trace-microservices-v2021/README.md)) for more details. Our analysis paper, accepted by SoCC '21, is available [here](http://cloud.siat.ac.cn/pdca/socc2021-AlibabaTraceAnalysis.pdf).
* *cluster-trace-microarchitecture-v2022* first provides AMTrace (Alibaba Microarchitecutre Trace). AMTrace is the first fine-granulairty and large-scale microarchitectural metrics of Alibaba Colocation Datacenter. Based AMTrace, researchers can analysis: CPU performance, microarchitecture contention, memory bandwidth contention and so on. [Our paper](https://doi.org/10.1145/3545008.3545026) is accepted by ICPP'22. See the subdirectory ([trace_2022](./cluster-trace-microarchitecture-v2022/README.md)) for more details.
* *cluster-trace-gpu-v2023* includes over 6200 GPUs (on ~1200 machines). It describes the AI/ML workloads with diverse resource specifications in a heterogeneous GPU cluster. In our "[Beware of Fragmentation](https://www.usenix.org/conference/atc23/presentation/weng)" paper (published in USENIX ATC '23), we modeled this trace in a [Kubernetes Scheduler Simulator](https://github.com/hkust-adsl/kubernetes-scheduler-simulator) and demonstrated that our proposed Fragmentation Gradient Descent (FGD) policy outperforms classic scheduling policies like Best-Fit, Dot-Product, etc. See [fgd_gpu_trace_2023](./cluster-trace-gpu-v2023/README.md) for the released data, schema, and scripts for processing.

We encourage anyone to use the traces for study or research purposes, and if you had any question when using the trace, please contact us via email: [alibaba-clusterdata](mailto:alibaba-clusterdata@list.alibaba-inc.com), or file an issue on Github. Filing an issue is recommanded as the discussion would help all the community. Note that the more clearly you ask the question, the more likely you would get a clear answer.

It would be much appreciated if you could tell us once any publication using our trace is available, as we are maintaining a list of related publicatioins for more researchers to better communicate with each other.

In future, we will try to release new traces at a regular pace, please stay tuned.

## Our motivation

As said at the beginning, our motivation on publishing the data is to help people in related field get a better understanding of modern data centers and provide production data for researchers to varify their ideas. You may use trace however you want as long as it is for reseach or study purpose.

From our perspective, the data is provided to address [the challenges Alibaba face](https://github.com/alibaba/clusterdata/wiki/About-Alibaba-cluster-and-why-we-open-the-data) in IDC's where online services and batch jobs are collocated.  We distill the challenges as the following topics:

1. **Workload characterizations**. How to characterize Alibaba workloads in a way that we can simulate various production workload in a representative way for scheduling and resource management strategy studies.
2. **New algorithms to assign workload to machines**. How to assign and reschedule workloads to machines for better resource utilization and ensuring the performance SLA for different applications (e.g. by reducing resource contention and defining proper proirities).
3. **Collaboration between online service scheduler (Sigma) and batch jobs scheduler (Fuxi)**. How to adjust resource allocation between online service and batch jobs to improve throughput of batch jobs while maintain acceptable QoS (Quality of Service) and fast failure recovery for online service. As the scale of collocation (workloads managed by different schedulers) keeps growing, the design of collaboration mechanism is becoming more and more critical.

Last but not least, we are always open to work together with researchers to improve the efficiency of our clusters, and there are positions open for research interns. If you had any idea in your mind, please contact us via [aliababa-clusterdata](mailto:alibaba-clusterdata@list.alibaba-inc.com) or [Haiyang Ding](mailto:haiyang.dhy@alibaba-inc.com) (Haiyang maintains this cluster trace and works for Alibaba's resource management & scheduling group).

## Outcomes from the trace

### Papers using Alibaba cluster trace

The fundamental idea of our releasing cluster data is to enable researchers & practitioners doing resaerch, simulation with more realistic data and thus making the result closer to industry adoption. It is a huge encouragement to us to see more works using our data. Here is a list of existing works using Alibaba cluster data. **If your paper uses our trace, it would be great if you let us know by sending us email** ([aliababa-clusterdata](mailto:alibaba-clusterdata@list.alibaba-inc.com)).


* cluster trace GPU v2023
  * [Beware of Fragmentation: Scheduling GPU-Sharing Workloads with Fragmentation Gradient Descent](https://www.usenix.org/conference/atc23/presentation/weng), Qizhen Weng* and Lingyun Yang* (co-first author), Yinghao Yu, Wei Wang, Xiaochuan Tang, Guodong Yang, and Liping Zhang. In the 2023 USENIX Annual Technical Conference (ATC '23), Boston, MA, USA, July 2023.
* microarchitecture trace v2022
  * [Characterizing Job Microarchitectural Profiles at Alibaba Scale: Dataset and Analysis](https://doi.org/10.1145/3545008.3545026), Kangjin Wang, Ying Li, Cheng Wang, Tong Jia, Kingsum Chow, Yang Wen, Yaoyong Dou, Guoyao Xu, Chuanjia Hou, Jie Yao, and Liping Zhang. In 51st International Conference on Parallel Processing (ICPP ’22), August 29-September 1, 2022, Bordeaux, France. ACM, New York, NY, USA, 11 pages.
* microservices trace v2021
  * [Characterizing Microservice Dependency and Performance: Alibaba Trace Analysis](http://cloud.siat.ac.cn/pdca/socc2021-AlibabaTraceAnalysis.pdf), Shutian Luo, Huanle Xu, Chengzhi Lu, Kejiang Ye, Guoyao Xu, Liping Zhang, Yu Ding, Jian He, Chengzhong Xu. SoCC'21
  * [μBench: an open-source factory of benchmark microservice applications](http://netgroup.uniroma2.it/Andrea_Detti/papers/journals/Bench_an_open-source_factory_of_benchmark_microservice_applications.pdf), A. Detti, L. Funari and L. Petrucci,  IEEE Transactions on Parallel and Distributed Systems
* cluster trace GPU v2020
  * [MLaaS in the Wild: Workload Analysis and Scheduling in Large-Scale Heterogeneous GPU Clusters](https://www.usenix.org/conference/nsdi22/presentation/weng), Qizhen Weng, Wencong Xiao, Yinghao Yu, Wei Wang, Cheng Wang, Jian He, Yong Li, Liping Zhang, Wei Lin, and Yu Ding. In the 19th USENIX Symposium on Networked Systems Design and Implementation (NSDI '22), Renton, WA, USA, April 2022.
* cluster trace v2018
  * [Who Limits the Resource Efficiency of My Datacenter: An Analysis of Alibaba Datacenter Traces](https://dl.acm.org/citation.cfm?doid=3326285.3329074), Jing Guo, Zihao Chang, Sa Wang, Haiyang Ding, Yihui Feng, Liang Mao, Yungang Bao, IEEE/ACM International Symposium on Quality of Service, IWQoS 2019
  * [DeepJS: Job Scheduling Based on Deep Reinforcement Learning in Cloud Data Center](https://github.com/RobertLexis/CloudSimPy/blob/master/playground/paper/F0049-4.19.pdf), by Fengcun Li and Bo Hu.
    * There is an interesting simulator released with this paper: CloudSimPy. You can check it at [CloudSimPy](https://github.com/RobertLexis/CloudSimPy)
  * Characterizing and Synthesizing Task Dependencies of Data-Parallel Jobs in Alibaba Cloud, by Huangshi Tian, Yunchuan Zheng, and Wei Wang, to appear in ACM Symposium on Cloud Computing (SoCC '19), Santa Cruz, California, November 2019.
  * [Aladdin: Optimized Maximum Flow Management for Shared Production Clusters](https://ieeexplore.ieee.org/abstract/document/8821038), Heng WU, Wenbo ZHANG, Yuanjia XU, Hao XIANG, Tao HUANG, Haiyang DING, Zheng ZHANG, 2019 IEEE International Parallel and Distributed Processing Symposium (IPDPS).
* cluster trace v2017
  * [LegoOS: A Disseminated, Distributed OS for Hardware Resource Disaggregation](https://www.usenix.org/system/files/osdi18-shan.pdf), Yizhou Shan, Yutong Huang, Yilun Chen, and Yiying Zhang, Purdue University. OSDI'18 (Best paper award!)
  * [The Elasticity and Plasticity in Semi-Containerized Co-locating Cloud Workload: a View from Alibaba Trace](https://dl.acm.org/citation.cfm?id=3267830), Qixiao Liu and Zhibin Yu. SoCC2018
  * Zeno: A Straggler Diagnosis System for Distributed Computing Using Machine Learning, Huanxing Shen and Cong Li, Proceedings of the Thirty-Third International Conference, ISC High Performance 2018
  * [Characterizing Co-located Datacenter Workloads: An Alibaba Case Study](https://arxiv.org/pdf/1808.02919.pdf), Yue Cheng, Zheng Chai, Ali Anwar. APSys2018
  * [Imbalance in the Cloud: an Analysis on Alibaba Cluster Trace, Chengzhi Lu et al. BIGDATA 2017](http://cloud.siat.ac.cn/~ye/Imbalance_Ye_2017.pdf)
  * Jiang C, Han G, Lin J, et al. [Characteristics of Co-allocated Online Services and Batch Jobs in Internet Data Centers: A Case Study from Alibaba Cloud[J]](https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8636497). IEEE Access, 2019, 7: 22495-22508.

### Tech reports and projects on analysing the trace

So far this session is empty. In future, we are going to link some reports and open source repo on how to anaylsis the trace here, with the permission of the owner.

The purpose of this is to help more beginners to get start on learning either basic data analysis or how to inspect cluster from statistics perspective.
