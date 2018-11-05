**Below is for cluster trace released in 2017. There will be no more updates for this file.**

# Introduction

As datacenter grows in scale, large-scale online service and batch jobs co-allocation is used to increase the datacenter efficiency. The co-allocation brings great challenge to existing cluster management system, in particularly to the services and jobs scheduler, which must work together to increase the cluster utilization and efficiency.

We distill the challenge to the following research topics that we think are interested to both academic community and industry:

* *Workload characterizations*: How can we characterize Alibaba workloads in a way that we can simulate various production workload in a representative way for scheduler studies.
* *New algorithms to assign workload to machines and to cpu cores*. How we can assign and re-adjust workload to different machines and cpus for better resource utilization and acceptable resource contention.
* *Online service and batch jobs scheduler cooperation*: How we can adjust resource allocation between online service and batch jobs to improve throughput of batch jobs while maintain acceptable service quality and fast failure recovery for online service.

To help researchers to address the above questions, we provide trace data taken from a production cluster in 24 hour period. The data includes part of machines and workload of the whole cluster. All machines includes can run both online services and batch jobs.

# Common techniques and fields

For confidentiality reasons, we have obfuscated certain information in the trace.

## Time and timestamps

Each record in the trace contains a timestamp, which are in seconds and relative to the start of trace period. Additionally, a time of 0 represents the event occur before the trace period. In some of the files, there are a small fraction of entries (e.g. less then 0.1% in `batch_instance.csv`) with negative timestamp, and they also indicate the events happen before the start time of trace.

Measurements of usages, include instances and machine usages, are taken in 60 seconds intervals and average over 300 seconds.
For confidentiality reasons, we disclose usage data only for 12 consecutive hours.

## Unique identifiers

Every machine, online and service workload is given a numeric id which is unique in the trace period. No service and task names are given.

## Resource units

Most resource utilization measurements and requests have been normalized, including:

* memory size
* disk space

Cpu core count is NOT normalized

# Data tables

Below we desribe the provided table. Reminder: not all traces will include all the types of data described here. The columns might occur in a different order, or have different names than reported here: the definitive specification of such details can be found in the schema.csv file.

## Machines

Machines are described by two tables: the machine events table and the machine resource utilization table

### Machine events(server_event.csv)

1. timestamp
2. machineID
3. event type
4. event detail
5. capacity:CPU
6. capacity:memory
7. capacity:disk

This trace include three types of machine events:

* add. A machine became available to the cluster. All machines in the trace have an ADD event, and has timestamp of value 0 since all machines are added before the trace collection.
* softerror. A machine becomes temporarily unavailable due to software failures, such as low disk space and agent failures.
* harderror. A machine becomes unavailable due to hardware failures, such as disk failures.

In the case of software and hardware errors, New online services and batch jobs should not be placed in the machines, but existing services and jobs may still function normally. Error reasons can be infered from the event detail field.

Machine capacities reflect the normalized physical capacity of each machine along each dimension. Each dimension (CPU cores, RAM size) is normalized independently.

### Machine utilization(server_usage.csv)

1. timestamp
2. machineID
3. util:CPU
4. util:memory
5. util:disk
6. load1: linux cpu load average of 1 minute
7. load5: linux cpu load average of 5 minute
8. load15: linux cpu load average of 15 minute

Machine utilization is the fraction of 100, reflects the total resource usage of all workload including the one for operating systems.

## Batch workload

Batch workload are described by these tables:

* Instance table
* Task table

Users submit batch workload in the form of Job (which is not included in the trace). A job contains multiple tasks, different tasks executes different computing logics. Tasks form a DAG according to the data dependency. Instance is the smallest scheduling unit of batch workload. All instances within a task execute exactly the same binary with the same resource request, but with different input data.

### Task table(batch_task.csv)

1. create_timestamp: the create time of a task
2. modify_timestamp: latest state modification time
3. job_id
4. task_id
5. instance_num: number of instances for the task
6. status: Task states includes Ready | Waiting | Running | Terminated | Failed | Cancelled
7. plan_cpu: cpu requested for each instane of the task
8. plan_mem: normalized memory requested for each instance of the task

### Instance table(batch_instance.csv)

1. start_timestamp:  instance start time if the instance is started
2. end_timestamp: instance end time if the instance ended
3. job_id
4. task_id
5. machineID: the host machine running the instance
6. status: Instance states includes Ready | Waiting | Running | Terminated | Failed | Cancelled | Interupted
7. seq_no: running trials number, starts from 1 and increase by 1 for each retry
8. total_seq_no: total number of retries
9. real_cpu_max: maximum cpu numbers of actual instance running
10. real_cpu_avg: average cpu numbers of actual instance running
11. real_mem_max: maximum normalized memory of actual instance running
12. real_mem_avg: average normalized memory of actual instance running

A batch instance may fail due to machine failures or network problems. Each record in instance table record one try run. The start and end timestamp can be 0 for some instance status. For example, for instance in ready and waiting status, all timestamp is zero; for instance in running and failed status, start time is non-zero but end time is zero.

## online service

online service are described by these tables:

* service instance event
* service instance usage

### service instance event (container_event.csv)

1. ts: timestamp of event
2. event: event type includes: Create and Remove
3. instance_id: online instance id
4. machine_id
5. plan_cpu: cpu number requested
6. plan_mem: normalized memory requested
7. plan_disk: normalized disk space requested
8. cpuset: assigned cpuset by online scheduler, cpus delimited by '|'

This trace includes only two type of instance event. Each create event records the finish of an online instance creation, and each remove event records the finish of an online instance removal. For containers created before the trace period, the ts field has a value of zero. The start time of instance creation and removal can be inferred from the finish time , since creation and removal usually finish in a few minutes.

Each online instance is given a unique cpuset allocation by online scheduler according to cpu topology and service constraints. For the 64 cpus machine in the dataset, cpus from 0 to 31 are in the same cpu package, while cpus from 32-63 are in another cpu package. cpus 0 and 32 belongs to the same cpu cores, cpu 1 and 33 belongs to another cpu cores, et cetera. The cpuset allocation far from ideal and can be improved for example by considering the difference levels of interference between instances sharing the same cpu core and package.

### service instance usage (container_usage.csv)

1. ts: start time of measurement interval
2. instance_id: online instance id
3. cpu_util: used percent of requested cpus
4. mem_util: used percent of requested memory
5. disk_util: used percent of requested disk space
6. load1
7. load5
8. load15
9. avg_cpi, average cycles per instructions
10. avg_mpki: average last-level cache misses per 1000 instructions
11. max_cpi: maximum CPI
12. max_mpki: maximum MPKI

The cpu/mem/disk utilization of service instance is relative to the requested resource, and the maximum utilization is 100 (full usage). The Load metric is relative to the assigned cpus. The CPI and MPKI metrics is measured in 1 seconds, and 5 samples is taken to compute the average and maximum values.

## State machine of batch task and instance

* Task
  * Terminated: A task goes to ‘Terminated’ when all its instances are done
  * Waiting: A task in not initialized yet
  * Failed: Task fails
  * Running: The Task is being processed
* Instance
  * Terminated: An instance is done
  * Waiting: The instance can not run because some of its dependencies have not finished
  * Running: An Instance is ‘Running’ on a worker
  * Failed: An instance fails
  * Interrupted: It is feature we introduced for backup instance, the instance stops due to some reason

# File format

Each data table is given in CSV format, using Unix-style line endings (ASCII LF). The CSV files have no header.  The schema for all tables are also given in CSV format in a file called schema.csv

# Known issues

Here are the known issues to current version of dataset, and we will try to fix them in the next version of dataset.

* Some task_id and / or job_id missing in batch_instance.csv. As mentioned in issue [#10](https://github.com/alibaba/clusterdata/issues/10), about 85% of the entries with missing task_id and job_id are of `start_timestamp` in the range between \[60K, 89K\[.
* There are some instance_id in container_usage.csv not appearing in container_event.csv, for example, instance_id = 9088 and some others.
* There are some missing data in usage information in batch_instance.csv.

# Frequently asked questions

Q: Any plan on releasing more data with DAG info?

Yes. If you have any suggestions, please go to this [issue #3](https://github.com/alibaba/clusterdata/issues/3)

Q: Any plan on releasing data on GPU and/or heterogeneous cluster data?

We are thinking about this, but there is no guarantee that such information can be included in the next version of data. There are some difficulties and we will try to solve them. Please post your ideas at [this issue](https://github.com/alibaba/clusterdata/issues/1) if you are interested in such data.

Q: Any more information about Fuxi in the Sigma.png?

Fuxi has a paper [here](http://www.vldb.org/pvldb/vol7/p1393-zhang.pdf). As for Sigma, here is some [introduction](http://www.infoq.com/cn/news/2017/12/Cloud-Sigma-Pouch-Alibaba) in Chinese and a paper about Sigma can be expected soon.
