# Alibaba Cluster Trace Program

## Overview

The *Alibaba Cluster Trace Program* is published by Alibaba Group. By providing cluster trace from real production, the program helps the researchers, students and people who are interested in the field to get better understanding of the characterastics of modern internet data centers (IDC's) and the workloads.

So far, two versions of traces have been released:

* *cluster-trace-v2017* includes about 1300 machines in a period of 12 hours. The trace-v2017 firstly introduces the collocation of online services (aka long running applications) and batch workloads. To see more about this trace, see related documents.
* *cluster-trace-v2018* includes about 4000 machines in a perids of 8 days. Besides having larger scaler than trace-v2017, this piece trace also contains the DAG information of our production batch workloads. See related documents for more details.

We encourage anyone to use the traces for study or research purposes, and if you had any question when using the trace, please contact us via email: [aliababa-clusterdata](mailto:alibaba-clusterdata@list.alibaba-inc.com), or file an issue on Github. Filing an issue is recommanded as the discussion would help all the community. Note that the more clearly you ask the question, the more likely you would get a clear answer.

It would be much appreciated if you could tell us once any publication using our trace is available, as we are maintaining a list of related publicatioins for more researchers to better communicate with each other.

In future, we will try to release new traces at a regular pace, please stay tuned.

## Our motivation

As said at the beginning, our motivation on publishing the data is to help people in related field get a better understanding of modern data centers and provide production data for researchers to varify their ideas. You may use trace however you want as long as it is for reseach or study purpose.

From our perspective, the data is provided to address [the challenges Alibaba face](https://github.com/alibaba/clusterdata/wiki/About-Alibaba-cluster-and-why-we-open-the-data) in IDC's where online services and batch jobs are collocated.  We distill the challenges as the following topics:

1. **Workload characterizations**. How to characterize Alibaba workloads in a way that we can simulate various production workload in a representative way for scheduling and resource management strategy studies.
2. **New algorithms to assign workload to machines**. How to assign and reschedule workloads to machines for better resource utilization and ensuring the performance SLA for different applications (e.g. by reducing resource contention and defining proper proirities).
3. **Collaboration between online service scheduler (Sigma) and batch jobs scheduler (Fuxi)**. How to adjust resource allocation between online service and batch jobs to improve throughput of batch jobs while maintain acceptable QoS (Quolity of Service) and fast failure recovery for online service. As the scale of collocation (workloads managed by different schedulers) keeps growing, the design of collaboration mechanism is becoming more and more critical.

Last but not least, we are always open to work together with researchers to improve the efficiency of our clusters, and there are positions open for research interns. If you had any idea in your mind, please contact us via [aliababa-clusterdata](mailto:alibaba-clusterdata@list.alibaba-inc.com) or [Haiyang Ding](mailto:haiyang.dhy@alibaba-inc.com) (Haiyang maintains this cluster trace and works for Alibaba's resource management & scheduling group).

## Outcomes from the trace

### Papers using Alibaba cluster trace

The fundemental idea of our releasing cluster data is to enable researchers & practitioners doing resaerch, simulation with more realistic data and thus making the result closer to industry adoption. It is a huge encouragement to us to see more works using our data. Here is a list of existing works using Alibaba cluster data. If your paper uses our trace, it would be great if you let us know by sending us email ([aliababa-clusterdata](mailto:alibaba-clusterdata@list.alibaba-inc.com)).

* LegoOS: A Disseminated, Distributed OS for Hardware Resource Disaggregation, Yizhou Shan, Yutong Huang, Yilun Chen, and Yiying Zhang, Purdue University. OSDI'18 (Best paper award!)
* The Elasticity and Plasticity in Semi-Containerized Co-locating Cloud Workload: a View from Alibaba Trace, Qixiao Liu and Zhibin Yu. SoCC2018
* Zeno: A Straggler Diagnosis System for Distributed Computing Using Machine Learning, Huanxing Shen and Cong Li, Proceedings of the Thirty-Third International Conference, ISC High Performance 2018
* Characterizing Co-located Datacenter Workloads: An Alibaba Case Study, Yue Cheng, Zheng Chai, Ali Anwar. APSys2018
* [Imbalance in the Cloud: an Analysis on Alibaba Cluster Trace, Chengzhi Lu et al. BIGDATA 2017](http://cloud.siat.ac.cn/~ye/Imbalance_Ye_2017.pdf)

### Tech reports and projects on analysing the trace

So far this session is empty. In future, we are going to link some reports and open source repo on how to anaylsis the trace here, with the permission of the owner.

The purpose of this is to help more beginners to get start on learning either basic data analysis or how to inspect cluster from statistics perspective.