# Date: 03.28
# Note: 2D: CPU + GPU

import random
import csv
import copy
import numpy as np
from utils import print_fn, _add_job, _repr_job_done, _add_describe, GPU_TYPE_INT_DICT
from cluster import Cluster
from node import Node
from scheduler import Scheduler

""" Jobs
OrderedDict
keys: job_id,duration,resource=[num_gpu, num_cpu]
      duration,size,on_time,wasted,jct,
      # submit_time,model_name,iterations,interval
"""


class Simulator:
    def __init__(self, csv_file, alloc_policy=0, preempt_policy=0,
                 sort_node_policy=0, oracle=False, random_seed=42,
                 max_time=int(1e10), num_gpus=None, num_cpus=None, num_nodes=4,
                 pattern=1, delta=1, num_spare_node=1,
                 hetero=False, describe_file=None, export_job_stats=False,
                 export_cluster_util=False, log_file=None, arrival_rate=None,
                 arrival_interval=60, arrival_shuffle=False,
                 num_jobs_limit=None, gpu_type_matching=0, verbose=0):
        self.cluster = None
        self.scheduler = None
        self.cur_time = None
        self.num_jobs = None
        self.job_list = []
        self.job_runn_list = []
        self.exit_flag = None
        self.max_time = max_time
        self.num_gpus = num_gpus
        self.num_cpus = num_cpus
        self.num_nodes = num_nodes
        self.csv_file = csv_file
        self.oracle = oracle  # know fluctuation?
        self.alloc_policy = alloc_policy
        self.preempt_policy = preempt_policy
        self.sort_node_policy = sort_node_policy
        self.describe_dict = _add_describe(describe_file)  # describe_file: each users' job distribution in csv format.
        self.arrival_rate = arrival_rate  # job arrival rate
        self.arrival_interval = arrival_interval
        self.arrival_shuffle = arrival_shuffle
        self.num_jobs_limit = num_jobs_limit
        self.job_origin_list = self.add_job(self.csv_file, self.describe_dict, limit=num_jobs_limit * 10)
        self.pattern = pattern  # which resource varying pattern?
        self.delta = delta  # time granularity, minimum: 1 second.
        self.num_spare_node = num_spare_node
        self.hetero = hetero
        self.gpu_type_matching = gpu_type_matching
        self.export_job_stats = export_job_stats
        self.export_cluster_util = export_cluster_util
        self.log_file = log_file  # just pass the path
        self.verbose = verbose
        random.seed(random_seed)

    @staticmethod
    def add_job(csv_file, describe_dict, limit=None):
        """
        limit: To avoid reading too many jobs when the sampled number << total number of jobs in trace file.
        """
        job_list = []
        with open(csv_file, 'r') as fd:
            reader = csv.DictReader(fd, delimiter=',')
            keys = reader.fieldnames
            for i, row in enumerate(reader):
                _add_job(job_list, row, describe_dict)
                if limit is not None and i >= limit:
                    break
        return job_list

    @staticmethod
    def set_job_list_arrival_time(job_list, arrival_rate=None, interval=60, shuffle_order=False):
        """
        job_list: jobs to execute in this run
        arrival_rate: num of jobs to arrive at each time interval (-1 or None means no changes)
        interval: time interval (default: 60)
        shuffle_order: bool, whether each user's inherent job order are shuffled (default: False)
        """
        if arrival_rate is None or arrival_rate < 0:
            return 0  # respect the original submit time
        if shuffle_order is True:
            np.random.shuffle(job_list)
        else:
            job_list.sort(key=lambda e: (e.get('submit_time', float('inf')), e['job_id']))

        arrival_counter = 0
        for job in job_list:
            arrival_time = (arrival_counter // arrival_rate) * interval
            job['submit_time'] = arrival_time
            arrival_counter += 1

    def init_node_list(self):
        return [Node(id=i) for i in range(self.num_nodes)]

    def init_node_list_hetero(self):
        node_list = []
        node_id = 0
        for _ in range(16):  # low-ended machines first
            node_list.append(Node(node_id, 0, 96, gpu_type='CPU'))
            node_id += 1
        for _ in range(56):  # low-ended machines first
            node_list.append(Node(node_id, 8, 96, gpu_type='MISC'))
            node_id += 1
        for _ in range(100):  # low-ended machines first
            node_list.append(Node(node_id, 2, 96, gpu_type='T4'))
            node_id += 1
        for _ in range(160):  # low-ended machines first
            node_list.append(Node(node_id, 2, 64, gpu_type='P100'))
            node_id += 1
        for _ in range(48):
            node_list.append(Node(node_id, 8, 96, gpu_type='V100'))
            node_id += 1
        return node_list

    def init_go(self, num_jobs=None):
        self.cur_time = 0
        self.job_list = copy.deepcopy(self.job_origin_list)  # copy each obj in the list
        num_jobs = num_jobs if num_jobs is not None else self.num_jobs_limit
        if (num_jobs is not None) and num_jobs <= len(self.job_list):
            random.shuffle(self.job_list)
            self.job_list = self.job_list[:num_jobs]
        self.set_job_list_arrival_time(self.job_list, self.arrival_rate, self.arrival_interval, self.arrival_shuffle)
        print_fn("----------------------------- RANDOM: %d" % random.randint(1000, 9999))
        print_fn("%d Job loaded" % len(self.job_list))

        # Init Cluster resources
        if self.hetero:
            node_list = self.init_node_list_hetero()
        elif self.num_nodes == 1 and self.num_gpus is not None:  # i.e., one big node formulation
            node_list = [Node(id=1, num_gpus=self.num_gpus, num_cpus=self.num_cpus)]
        else:
            node_list = self.init_node_list()
        self.cluster = Cluster(node_list=node_list, job_list=self.job_list, random_seed=random.randint(1000, 9999),
                               num_spare_node=self.num_spare_node, pattern=self.pattern,
                               export_cluster_util=self.export_cluster_util)

        self.scheduler = Scheduler(cluster=self.cluster, alloc_policy=self.alloc_policy,
                                   preempt_policy=self.preempt_policy, sort_node_policy=self.sort_node_policy,
                                   verbose=self.verbose, gpu_type_matching=self.gpu_type_matching)
        self.num_jobs = len(self.job_list)
        self.exit_flag = 0

        print_fn("Spared nodes: %s" % self.cluster.spare_node_id)

    def exp_summary(self, id=None):
        job_history = self.cluster.job_history
        num_jobs_done = job_history.num_jobs_done
        jct_summary = job_history.jct_summary
        wait_time_summary = job_history.wait_time_summary
        job_done_list = job_history.job_done_list
        wasted_summary = job_history.wasted_summary
        assert num_jobs_done == len(job_done_list)

        print_fn("Wasted progress in summary: %s" % wasted_summary)
        if num_jobs_done == self.num_jobs:
            print_fn("All Done (makespan) at %s" % self.cur_time)
        else:
            print_fn("%d of %d jobs Done (makespan) at %s" % (num_jobs_done, self.num_jobs, self.cur_time))
        print_fn("%d jobs' average JCT: %.4f, average wait time: %.4f" % (num_jobs_done, jct_summary / num_jobs_done, wait_time_summary / num_jobs_done))
        # Print job done breakdown
        job_done_list.sort(key=lambda e: e['job_id'])

        if self.export_job_stats is True:
            job_stats = np.zeros(shape=(6, len(job_done_list)), dtype=int)
            for i, job in enumerate(job_done_list):
                print_fn("%s || %s" % (_repr_job_done(job), job))
                job_stats[0][i] = job['submit_time']
                job_stats[1][i] = job['duration']
                job_stats[2][i] = job['jct']
                job_stats[3][i] = GPU_TYPE_INT_DICT.get(job.get('gpu_type', 'N/A'), -1)
                job_stats[4][i] = job.get('num_inst', 1)
                job_stats[5][i] = job['job_id']
            job_stats_name = "%s.a%s-p%s-i%s-job_stats.npy" % (
                self.log_file.name, self.alloc_policy, self.preempt_policy, id)
            job_stats_file = self.log_file.parent / job_stats_name
            np.save(job_stats_file, job_stats)
        else:
            for job in job_done_list:
                print_fn("%s || %s" % (_repr_job_done(job), job))
        print_fn("")

        if self.export_cluster_util is True:
            cluster_util = np.asarray([
                self.cluster.cluster_time,
                self.cluster.cluster_cpu,
                self.cluster.cluster_gpu
            ])
            cluster_util_name = "%s.a%s-p%s-i%s-cluster_util.npy" % (
                self.log_file.name, self.alloc_policy, self.preempt_policy, id)
            cluster_util_file = self.log_file.parent / cluster_util_name
            np.save(cluster_util_file, cluster_util)
        return num_jobs_done, jct_summary, wait_time_summary

    def simulator_go(self, repeat=1, num_jobs=None):
        """
        :return: [[num_jobs, avg_jct, wait_time, makespan], [], ... ]
        """
        result = []
        for repeat_id in range(repeat):
            self.init_go(num_jobs=num_jobs)

            while not self.exit_flag:
                self.tic(self.delta)

            num_jobs_done, jct_summary, wait_time_summary = self.exp_summary(repeat_id)
            result.append((num_jobs_done, jct_summary / num_jobs_done, wait_time_summary / num_jobs_done, self.cur_time))
        return result

    def tic(self, delta=1):
        if self.cur_time < self.max_time:
            self.cluster.tic_svc(self.cur_time)

            # Preempt job
            self.scheduler.preempt_job(self.cluster)

            # Allocate job
            self.scheduler.alloc_job(self.cluster)

            # Jobs tic and global cur_time += delta
            tic_return_value = self.cluster.tic_job(delta)
            if tic_return_value >= 0:
                self.cur_time = tic_return_value
            else:
                self.cur_time = self.cur_time + delta
                self.exit_flag = 1
        else:
            print_fn("TIMEOUT {} with jobs {}".format(self.cur_time, self.cluster.job_list))
            self.exit_flag = 1
            raise TimeoutError("TIMEOUT {} with jobs {}".format(self.cur_time, self.cluster.job_list))
