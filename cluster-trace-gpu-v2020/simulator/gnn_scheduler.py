
from scheduler import Scheduler


class GNN_Scheduler(Scheduler):

    def __init__(self, alloc_policy=0, preempt_policy=0, sort_node_policy=0, cluster=None, gpu_type_matching=0, verbose=0):
        super().__init__(alloc_policy, preempt_policy,
                         sort_node_policy, cluster, gpu_type_matching, verbose)

    def alloc_job(self, cluster=None):
        return super().alloc_job(cluster)

    def alloc_job_sort(self, job_list, job_runn_list=None):
        return super().alloc_job_sort(job_list, job_runn_list)

    def try_allocate_job_to_cluster(self, job_a, cluster):
        return super().try_allocate_job_to_cluster(job_a, cluster)

    def sorted_node_list(self, node_list):
        return super().sorted_node_list(node_list)

    def preempt_job(self, cluster=None):
        return super().preempt_job(cluster)

    def preempt_job_node(self, node, preempted_job_list):
        return super().preempt_job_node(node, preempted_job_list)

    def preempt_job_sort_node(self, node, preempt_policy):
        return super().preempt_job_sort_node(node, preempt_policy)

    def display_node_status(self, cur_node_id):
        return super().display_node_status(cur_node_id)
