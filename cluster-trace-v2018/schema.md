# 1. Schema

This file describes the schema of each data file. 

The index below is aligned with the data column in each file.

## 1.1 Machine Meta

| Field            | Type       | Label | Comment                                     |
|------------------|------------|-------|---------------------------------------------|
| machine_id       | string     |       | uid of machine                              |
| time_stamp       | bigint     |       | time stamp, in second                       |
| failure_domain_1 | bigint     |       | one level of container failure domain       |
| failure_domain_2 | string     |       | another level of container failure domain   |
| cpu_num          | bigint     |       | number of cpu on a machine                  |
| mem_size         | bigint     |       | normalized memory size. [0, 100]            |
| status           | string     |       | status of a machine                         |

* About `failure_domain_1`: We have multiple levels of failure domains of which two are provided in this version of trace. For any application that requires fault tolerance, their instances should be spread across many failure domains. This is an enumerate value.

## 1.2 Machine Usage

| Field            | Type       | Label | Comment                                     |
|------------------|------------|-------|---------------------------------------------|
| machine_id       | string     |       | uid of the machine                              |
| time_stamp       | double     |       | time stamp, in second                       |
| cpu_util_percent | bigint     |       | [0, 100]                                   |
| mem_util_percent | bigint     |       | [0, 100]                                   |
| mem_gps          | double     |       | normalized memory bandwidth, [0, 100]      |
| mkpi             | bigint     |       | cache miss per thousand instruction        |
| net_in           | double     |       | normarlized incoming network traffic, [0, 100]   |
| net_out          | double     |       | normarlized outgoing network traffic, [0, 100]   |
| disk_io_percent  | double     |       | [0, 100], abnormal values are of -1 or 101 |


## 1.3 Container Meta

| Field           | Type       | Label | Comment                                     |
|-----------------|------------|-------|---------------------------------------------|
| container_id    | string     |       | uid of the container                          |
| machine_id      | string     |       | uid of container's host machine             |
| time_stamp      | bigint     |       |                                             |
| app_du          | string     |       | containers with same app_du belong to same application group |
| status          | string     |       |                                             |
| cpu_request     | bigint     |       | 100 is 1 core                               |
| cpu_limit       | bigint     |       | 100 is 1 core                               |
| mem_size        | double     |       | normarlized memory, [0, 100]                |

* About `app_du`: Containers belong to the same deploy unit provides one service, typically, they should be spread across failure domains

## 1.4 Container Usage

| Field            | Type       | Label | Comment                                     |
|------------------|------------|-------|---------------------------------------------|
| container_id     | string     |       | uid of the container                          |
| machine_id       | string     |       | uid of container's host machine             |
| time_stamp       | double     |       | time stamp, in second                       |
| cpu_util_percent | bigint     |       |                                             |
| mem_util_percent | bigint     |       |                                             |
| cpi              | double     |       |                                             |
| mem_gps          | double     |       | normalized memory bandwidth, [0, 100]       |
| mpki             | bigint     |       |                                             |
| net_in           | double     |       | normalized incoming network traffic, [0, 100] |
| net_out          | double     |       | normalized outgoing network traffic, [0, 100] |
| disk_io_percent  | double     |       | [0, 100], abnormal values are -1 or 101  |

## 1.5 Batch Task

| Field           | Type       | Label | Comment                                     |
|-----------------|------------|-------|---------------------------------------------|
| task_name       | string     |       | task name. unique within a job              |
| instance_num    | bigint     |       | number of instances                         |
| job_name        | string     |       | job name                                    |
| task_type       | string     |       | task type                                   |
| status          | string     |       | task status                                 |
| start_time      | bigint     |       | start time of the task                      |
| end_time        | bigint     |       | end of time the task                        |
| plan_cpu        | double     |       | number of cpu needed by the task, 100 is 1 core |
| plan_mem        | double     |       | normalized memory size, [0, 100]           |

* The `task_name` field indicates the DAG information, see the explanation of batch workloads

## 1.6 Batch Instance

| Field           | Type       | Label | Comment                                     |
|-----------------|------------|-------|---------------------------------------------|
| instance_name   | string     |       | instance name of the instance               |
| task_name       | string     |       | name of task to which the instance belongs   |
| job_name        | string     |       | name of job to which the instance belongs    |
| task_type       | string     |       | task type                                   |
| status          | string     |       | instance status                             |
| start_time      | bigint     |       | start time of the instance                  |
| end_time        | bigint     |       | end time of the instance                    |
| machine_id      | string     |       | uid of the host machine of the instance         |
| seq_no          | bigint     |       | sequence number of this instance            |
| total_seq_no    | bigint     |       | total sequence number of this instance      |
| cpu_avg         | double     |       | average cpu used by the instance, 100 is 1 core  |
| cpu_max         | double     |       | average memory used by the instance (normalized) |
| mem_avg         | double     |       | max cpu used by the instance, 100 is 1 core      |
| mem_max         | double     |       | max memory used by the instance (normalized, [0, 100]) |

* The `task_name` field is uniqe within a job; note task name indicates the DAG information, see the explanation of batch workloads
* There are totally 12 types, and only some of them have DAG info
