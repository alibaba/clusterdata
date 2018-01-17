# Overview
The trace data, ClusterData201708,  contains cluster information of a production cluster in 12 hours period, and contains about 1.3k machines that run both online service and batch jobs.

The data is provided to address [the challenges Alibaba face](https://github.com/alibaba/clusterdata/wiki/About-Alibaba-cluster-and-why-we-open-the-data) in idcs where online services and batch jobs are co-allocated.  We distill the challenges as the following topics: 

1. Workload characterizations: How can we characterize Alibaba workloads in a way that we can simulate various production workload in a representative way for scheduler studies.
2. New algorithms to assign workload to machines and to cpu cores. How we can assign and re-adjust workload to different machines and cpus for better resource utilization and acceptable resource contention.
3. Online service and batch jobs scheduler cooperation: How we can adjust resource allocation between online service and batch jobs to improve throughput of batch jobs while maintain acceptable service quality and fast failure recovery for online service.

Please let us know if you have any issues, ideas, or papers about these data by sending email to us [aliababa-clusterdata](mailto:alibaba-clusterdata@list.alibaba-inc.com). The more specific the feedback, the more likely we are to be able to help you.

# Trace data 
The format of trace data is described in the [schema description](trace_201708.md), and defined in the specification file [schema.csv](schema.csv) in the repository.

# Downloading the trace
The data is stored in Alibaba Cloud Object Storage Service. You do not need to have an Alibaba account or sign up for Object Storage Service to download the data.

Downloading information can be found (after a short survey) in [this link](https://goo.gl/forms/eOoe6DwZQpd2H5n53). We use the contact information to keep in touch with you, and announce goodies such as new traces.
Included with the trace is a [SHA256SUM](SHA256SUM) file, which can be used to verify the integrity of a download, using the sha256sum command from GNU coreutils using a command like

```
sha256sum --check SHA256SUM
```




