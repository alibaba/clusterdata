
# 1 Introduction

As part of the Alibaba Open Cluster Trace Program, a new version of cluster trace, `cluster-trace-v2018`, is released this year. The trace is sampled from one of our production clusters. Similar to the trace from 2017, there are both online services (aka long running applications, LRA) and batch workloads colocated in every machine in the cluster. Over the past year, the scale of colocation of online services and batch workloads have greatly increased resulting in the improvement of our overall resource utilization.

The colocated workloads are managed by the coordination of two schedulers, Sigma for online services and Fuxi for batch workloads. The figure below depicts the architecture of Sigma and Fuxi coloation.

![Sigma-Fuxi-Colocation](./sigma-fuxi-collocation.jpg)

# 2 Data Files for The Trace

## 2.1 About

Cluster-trace-v2018 includes about 4000 machines in a perids of 8 days and is consisted of 6 tables (each is a file). Here is a brief introduction of the tables and the detail of each table is provided in section *2.2 Schema*.

* machine_meta.csv：the meta info and event infor of machines.
* machine_usage.csv: the resource usage of each machine.
* container_meta.csv：the meta info and event infor of containers.
* container_usage.csv：the resource usage of each container.
* batch_instance.csv：inforamtion about instances in the batch workloads.
* batch_task.csv：inforamtion about instances in the batch workloads. Note that the DAG information of each job's tasks is described in the task_name field.

### Downloading the data

The entire data set is about 48GB in .tar.gz format and 280GB after extraction. So we provide two download links.

* Download the all as one dataset:
  * [alibaba_clusterdata_v2018](http://openclusterdata.oss-cn-hangzhou-zmf.aliyuncs.com/clusterdata2018%2Fclusterdata2018.tar.gz)
* Download 6 files separately:
  * [machine_meta](http://openclusterdata.oss-cn-hangzhou-zmf.aliyuncs.com/clusterdata2018%2Fmachine_meta.tar.gz)
  * [machine_usage](http://openclusterdata.oss-cn-hangzhou-zmf.aliyuncs.com/clusterdata2018%2Fmachine_usage.tar.gz)
  * [container_meta](http://openclusterdata.oss-cn-hangzhou-zmf.aliyuncs.com/clusterdata2018%2Fcontainer_meta.tar.gz)
  * [container_usage](http://openclusterdata.oss-cn-hangzhou-zmf.aliyuncs.com/clusterdata2018%2Fcontainer_usage.tar.gz​​)
  * [batch_task](http://openclusterdata.oss-cn-hangzhou-zmf.aliyuncs.com/clusterdata2018%2Fbatch_task.tar.gz)
  ​* [batch_instance](http://openclusterdata.oss-cn-hangzhou-zmf.aliyuncs.com/clusterdata2018%2Fbatch_instance.tar.gz)

## 2.2 Schema

**Some explanation of common fields.**

* time_stamp, start_time and end_time: These fields in the tables are all with unit "second" and the number if the difference of between the actual time and the beginning of the period over which the trace is sampled. The beginning of period is 0.
* For confidential reason, we normalize some values such as memory size and disk size and rescale such field between [0, 100]. However, there are some invalid values and they are set to either -1 or 101.

**Explanation of tables.**

* machine_meta.csv

| column name | type | explanation | comments |
| -------- | -------- | -------- | -------- |
| machine_id     | string  | The unique ID (uid) of a machine     |  |
| time_stamp     |  int  | time index  | 0 means the time stamp is before or after the 8-day time span |
| disaster_level_1     |  enum  | 1st level of failure domain  |  We have multiple levels of failure domains of which two are provided in this version of trace. For any application that requires fault tolerance, their instances should be spread across many failure domains |
| disaster_level_2     |  enum  | 2nd level of failure domain    | Similar to disaster_level_1, this is just another level of failure domain  |
| cpu_num     |  int  | num of cpu of a machine     | Unit is "core", e.g. 4 means 4 cores on the machine |
| mem_size     |  int  | memory size of a machine     |  Normalized to the largest memory size of all machines |
| status     |  enum  | status of a machine at given time_stamp    | Status of the machine. See explanation below |

* machine_usage.csv

| column name | type | explanation | comments |
| -------- | -------- | -------- | -------- |
| machine_id     | string  | The unique ID (uid) of a machine     |  |
| time_stamp     |  int  | time stamp  | 0 means the time stamp is before or after the 8-day time span |
| cpu_util_percent     |  int  | cpu utilization percentage  | Both user and system are included, between [0, 100]. There are some invalid values and they are set to -1 or 101 |
| mem_util_percent     |  int  | memory utilization percentage | [0, 100]. There are some invalid values and they are set to -1 or 101  |
| mem_gps     |  int  | memory bandwidth usage | Normalized to maximum memory bandwith usage of all machines |
| mpki     |  int  | cache miss per thousand instruction |  |
| net_in     |  int  | number of incoming network packages  | Normalized to the maximum of this column |
| net_out     |  int  | number of outgoing network packages  | Normalized to the maximum of this column |
| disk_usage_percent     |  int  | disk space utilization percentage    | [0, 100]. There are some invalid values and they are set to -1 or 101  |
| disk_io_percent     |  int  | disk io utilization percentage  | [0, 100]. There are some invalid values and they are set to -1 or 101 |

* container_meta.csv

| column name | type | explanation | comments |
| -------- | -------- | -------- | -------- |
| container_id     | string  | The unique ID (uid) of a container     |   |
| machine_id     | string  | machine uid of a container's host     |   |
| deploy_unit | string  | deploy group of a container  | Containers belong to the same deploy unit provides one service, typically, they should be spread across failure domains |
| time_stamp     |  int  | time stamp  | 0 means the time stamp is before or after the 8-day time span |
| cpu_request     |  int  | planned cpushare request  | 100 means 1 core  |
| cpu_limit     |  int  | planned cpushare request    | 100 means 1 core  |
| mem_size     |  int  | planned memory size  | Normalized to the largest memory size of all machines |
| status     |  enum  | status of a container at given time_stamp  | Status of a container at given time stamp, see the state machine for details  |

* container_usage.csv

| column name | type | explanation | comments |
| -------- | -------- | -------- | -------- |
| container_id     | string  | The unique ID (uid) of a container     |   |
| machine_id     | string  | machine uid on which a container runs   |   |
| time_stamp     |  int  | time stamp  | 0 means the time stamp is before or after the 8-day time span |
| cpu_util_percent     |  int  | cpu utilization percentage  | [0, 100]. There are some invalid values and they are set to -1 or 101  |
| mpki     |  int  | cache miss per thousand instruction  |   |
| cpi     |  int  | cpi of a container at given time_stamp  |  |
| mem_util_percent     |  int  | memory utilization percentage | [0, 100]. There are some invalid values and they are set to -1 or 101  |
| mem_gps  |  int  | memory bandwidth usage | Normalized to maximum memory bandwith usage of all machines  |
| disk_usage_percent     |  int  | disk space utilization percentage | [0, 100]. There are some invalid values and they are set to -1 or 101  |
| disk_io_percent     |  int  | disk io utilization percentage | [0, 100]. There are some invalid values and they are set to -1 or 101  |
| net_in     |  int  | number of incoming network packages  |  Normalized to the largest net_in of all machines  |
| net_out     |  int  | number of outgoing network packages  | Normalized to the largest net_out of all machines  |

* batch_instance.csv

| column name | type | explanation | comments |
| -------- | -------- | -------- | -------- |
| inst_name  | string  | The unique ID (uid) of a batch instance     | Instance name is unique within a (job, task) pair |
| task_name  | string  | The task name to which an instance belongs    | Task name is uniqe within a job; note task name indicates the DAG information, see the explanation of batch workloads |
| task_type  | enum  | type of the task     | There are totally 12 types, and only some of them have DAG info |
| job_name  | string  | job_name of the task that an instance belongs to  | A job is consisted of many tasks. See the explanation of job-task-instance |
| status  | enum  | status of an instance  | Status of the instance  |
| start_time  | int  | start time of an instance  | 0 means the time stamp is before or after the 8-day time span  |
| end_time  | int  | end time of an instance  | 0 means the time stamp is before or after the 8-day time span  |
| machine_id  | string  | the machine id on which an instance runs  |  |
| seq_no  | int  | seq no of an instance     |   |
| total_seq_no  | int  | total seq no of an instance  |   |
| cpu_avg  | int  | average cpu utilization of cpu of an instance  | 100 means 1 core  |
| cpu_max  | int  | max cpu utilization of cpu of an instance  | 100 means 1 core  |
| mem_avg  | int  | average memory utilization of cpu of an instance  |  Normalized to the largest memory size of all machines |
| mem_max  | int  | max memory utilization of cpu of an instance  | Normalized to the largest memory size of all machines  |

* batch_task.csv

| column name | type | explanation | comments |
| -------- | -------- | -------- | -------- |
| task_name  | string  | The task name to which an instance belongs    | Note task name indicates the DAG information, see the explanation of batch workloads  |
| inst_num  | int  | number of instances a task has   |  |
| task_type  | enum  | type of the task   |   |
| job_name  | string  | job_name of a task  |   |
| status  | enum  | status of an instance  | status of the task  |
| start_time  | int  | start time of an instance  | 0 means the time stamp is before or after the 8-day time span  |
| end_time  | int  | end time of an instance   | 0 means the time stamp is before or after the 8-day time span  |
| plan_cpu  | int  | plan cpu of a task | 100 means 1 core |
| plan_mem  | int  | plan memory of a task | Normalized to the largest memory size of all machines |

## 2.3 DAG of batch worloads

*In this version of cluster data, we include many types of batch wokrloads. Most of them are DAGs while some of them are not. For those tasks that are not DAGs, we name them using random characters, such as `task_Nzg3ODAwNDgzMTAwNTc2NTQ2Mw==` or `task_Nzg3ODAwNDgzMTAwODc2NTQ3MQ==`. These tasks can be treated as independent tasks. In the remainder of this section, we explain how to deduce DAG of a job from the task names.*

A complete batch computation job can be described using "job-task-instance" model. We will describe the meaning of each term and how the DAG information is expressed in the trace.

A job is typically consisted of several tasks whose depencies are expressed by DAG (Directed Acyclic Graph). Each task has a number of instances, and only when all the instances of a task are completed can a task be considered as "finished", i.e. if task-2 is depending on task-1, any instance of task-2 cannot be started before all the instances of task-1 are completed. The DAG of tasks in a job can be deduced from the `task_name` field of all tasks of this job, and it is explained with the following example.

The DAG of Job-A is shown in the following figure. Job-A is consisted of 5 tasks with some dependencies. The DAG of the 5 tasks are expressed with their `task_name`. For each task:

* `task1`'s `task_name` is `M1`: means that `task1` is an independent task and can be started without waiting for any other task. Similarly for th rest
* `M2_1`: means that `task2` depends on the finishing of `task1`
* `M3_1`: means that `task3` depends on the finishing of `task1`
* `R4_2`: means that `task4` depends on the finishing of `task2`
* `M5_3_4`: means that `task5` depends on both `task3` and `task4`, that is, `task5` cannot start before all instances of both `task3` and `task4` are completed.

Note that for DAG information, only the numeric figure in the task_name matters, while the first charactor (e.g. `M`, `R` in the example) has nothing to do with dependency.

The number of instances for each task is expressed with another field `instance_num`.

![DAG](./DAG.png)

# 3 Known Issues

> Empty for now.

# 4 Frequent Questions

> Empty for now.