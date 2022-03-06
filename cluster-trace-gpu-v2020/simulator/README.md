# Simulator of GPU Cluster Scheduling

## Code Overview
### Structure
```python
simulator
└── run_simulator.py
    └── simulator.py: Simulator()
        ├── cluster.py: Cluster()
        │   ├── node.py: Node()
        │   └── job_history.py: JobHistory()
        └── scheduler.py: Scheduler()
            └── node.py: Node()
```

### Key call path
```python
simulator
└── run_simulator.py
    └── simulator.py
        └── simulator_go()
            ├── init_go()
            │   ├── cluster = Cluster()
            │   └── simulator = Simulator()
            ├── while not exit
            │   └── tic()
            │       ├── scheduler.preempt_job()
            │       └── scheduler.alloc_job()
            │           └── scheduler.alloc_job_sort()
            │               ├── SDF
            │               ├── FIFO
            │               └── ...
            └── exp_summary()
```

### Key data structure
- Job: an `OrderedDict` with keys of `user`, `duration`, estimated duration (`group_gpu_dur`), etc.
- JobHistory: `self.user_job_stats` is a dict storing job statistics of each user, e.g., `num_job`, `dur_avg`.

## Usage
```bash
python3 run_simulator.py  # compare multiple job scheduling policies (scheduler prefers load-balancing among nodes)
# OR 
python3 run_simulator_fifo.py --pack  # apply FIFO policy (scheduler prefers packing)
```

### Output
```bash
log_file: ./logs/0228-pai_job_duration_estimate_100K.csv-99163-6500g_1n_h0_0p_3sn_0gt-1000ar-20000j-1x-42r.log
==========
20000_Jobs_repeated_1_times
alloc,preempt,avg_jct,wait_time,makespan,jobs_done,runtime
(SJF , LGF),5988.61,949.91,535706,20000,51.96
(SJU , LGF),6278.33,1239.62,535706,20000,65.80
(SJG , LGF),6071.01,1032.31,535706,20000,50.86
(SJGG, LGF),6001.94,963.23,535706,20000,51.11
(FIFO, LGF),7918.47,2879.77,535706,20000,110.53

# Sort by JCT
(SJF , LGF),5988.61,949.91,535706,20000,51.96
(SJGG, LGF),6001.94,963.23,535706,20000,51.11
(SJG , LGF),6071.01,1032.31,535706,20000,50.86
(SJU , LGF),6278.33,1239.62,535706,20000,65.80
(FIFO, LGF),7918.47,2879.77,535706,20000,110.53

log_file: ./logs/0228-pai_job_duration_estimate_100K.csv-99163-6500g_1n_h0_0p_3sn_0gt-1000ar-20000j-1x-42r.log
```
### Headers
- `alloc`: name of the allocation policy
- `preempt`: name of the preemption policy, not used in this demo
- `avg_jct`: average job completion time (jct)
- `wait_time`: average job wait time (scheduling delay)
- `makespan`: completion time when all jobs are finished
- `jobs_done`: number of jobs done over all repeated experiments
- `runtime`: wall clock time taken to run the experiments

### Allocation policies
- `SJF`: 'Shortest Job First', SJF + Oracle, knowing each job's duration beforehand.
- `SJU`: SJF + Duration Estimator using USER feature
- `SJG`: SJF + Duration Estimator using GROUP, USER feature
- `SJGG`: SJF + Duration Estimator using GROUP, USER, GPU feature
- `FIFO`: FIFO, the default. Respect jobs' original arrival order, or random order in shuffled cases.

### Log file name explanation
- `0228`: experiment date.
- `pai_job_duration_estimate_100K.csv`: name of the traces file input.
- `47996`: timestamp.
- `6500g`: 6500 GPUs in the cluster.
- `1n`: 1 Node (i.e., no topology, jobs can run on any GPU).
- `h0`: heterogeneity: nil.
- `0p`: resource dynamic pattern: nil (always 6500 GPUs).
- `3sn`: scheduler policy: 3 is packing, 0 is load-balancing
- `1000ar`: job arrival rate: 1000 jobs / minutes (60 seconds); `-1` is to use the original submit time. 
- `20000j`: 20000 jobs
- `1x`: repeat 1 times
- `42r`: random seed: 42
