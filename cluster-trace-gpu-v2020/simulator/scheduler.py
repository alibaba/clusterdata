import utils
from utils import print_fn, ALLOC_POLICY_DICT, PREEMPT_POLICY_DICT, _repr_job_concise


class Scheduler:
    def __init__(self, alloc_policy=0, preempt_policy=0, sort_node_policy=0, cluster=None, gpu_type_matching=0, verbose=0):
        self.cluster = cluster
        self.alloc_policy = alloc_policy
        self.preempt_policy = preempt_policy
        self.sort_node_policy = sort_node_policy
        self.node_rotate_counter = 0
        self.verbose = verbose
        self.gpu_type_matching = gpu_type_matching
        # To skip unnecessary self.alloc_job_sort()
        self.last_time_snapshot = [0, 0, 0, 0]  # [idle_gpu, idle_cpu, len(job_list), len(job_to_allocate_cache)]
        self.cannot_counter = 0

    def alloc_job(self, cluster=None):
        cluster = cluster if cluster is not None else self.cluster
        job_list = cluster.job_list  # Take cluster.job_list

        # Trying skipping allocation as early as possible
        if len(job_list) <= 0:
            return 0
        ig, ic = cluster.idl_gpus, cluster.idl_cpus
        this_time_snapshot = [ig, ic, len(job_list), 0]  # 0: no job allocated.
        if self.last_time_snapshot == this_time_snapshot:  # exactly the same
            if self.verbose:
                print_fn("[{}] Last time snapshot == this time snapshot: {}. Bypass.".format(self.cluster.cur_time, this_time_snapshot))
            return 0
        job_min_gpu, job_min_cpu = min(job_list, key=lambda j: j['num_inst'] * j['num_gpu']), min(job_list, key=lambda j: j['num_inst'] * j['num_cpu'])
        if (ig <= 0 or job_min_gpu['num_inst'] * job_min_gpu['num_gpu'] > ig) and (ic <= 0 or job_min_cpu['num_inst'] * job_min_cpu['num_cpu'] > ic):
            self.last_time_snapshot = this_time_snapshot
            return 0

        if self.verbose:
            print_fn("job_min_gpu, job_min_cpu = {:.1f}, {:.1f}".format(job_min_gpu['num_gpu'], job_min_cpu['num_cpu']))

        job_to_allocate_cache = []
        # Greedy algorithm or Greedy + load balancing
        if self.alloc_policy in ALLOC_POLICY_DICT.keys():
            # Heavy action
            self.alloc_job_sort(job_list, cluster.job_runn_list)
            for job_a in job_list:
                succ_alloc = self.try_allocate_job_to_cluster(job_a, cluster)
                if succ_alloc == 1:
                    job_to_allocate_cache.append(job_a)
                elif succ_alloc == -1:
                    break
                # else, e.g., succ_alloc == 0: pass/continue
        else:
            raise KeyError("Uncaptured Allocation Policy Input: %d" % self.alloc_policy)

        this_time_snapshot[-1] = len(job_to_allocate_cache)  # num of jobs allocated
        self.last_time_snapshot = this_time_snapshot
        for job_a in job_to_allocate_cache:
            cluster.job_list.remove(job_a)

    def alloc_job_sort(self, job_list, job_runn_list=None):
        if self.alloc_policy == 0:  # short_duration_first
            job_list.sort(key=lambda e: (e['duration'], e['job_id']))
        elif self.alloc_policy == 8:  # FIFO, remains the original order
            job_list.sort(key=lambda e: (e['submit_time'], e['job_id']))
        elif self.alloc_policy in [1, 2, 4]:  # SJF with duration estimation
            est_feature = {1: 'user_dur', 2: 'group_dur', 4: 'group_gpu_dur'}[self.alloc_policy]
            job_list.sort(key=lambda e: (e[est_feature], e['job_id']))
        else:
            raise Exception("Unexpected alloc policy: %d" % self.alloc_policy)

        if self.verbose:
            for i, j in enumerate(job_list):
                print_fn("%2d %s" % (i, j))
                if i > 20:
                    break

    def try_allocate_job_to_cluster(self, job_a, cluster):
        """
        job_a: job to allocate
        cluster: target cluster

        return:
            -1: the cluster is full, stop job picking
             0: the current job cannot be placed, try next
             1: the current job has been successfully deployed, need record.
        """
        ig, ic = cluster.idl_gpus, cluster.idl_cpus
        if ig <= 0 and ic <= 0:
            return -1
        elif job_a['num_inst'] * job_a['num_gpu'] > ig or job_a['num_inst'] * job_a['num_cpu'] > ic:
            return 0
        else:  # with in gpu and cpu limits
            assigned_node_map = {}
            assigned_inst_num = 0
            sorted_node_list = self.sorted_node_list(cluster.node_list)
            for nid, node in enumerate(sorted_node_list):
                # <Node-job label matching>
                if self.gpu_type_matching == 1:  # GPU type perfect match
                    if job_a['gpu_type'] != 'CPU' and job_a['gpu_type'] != node.gpu_type:
                        continue  # cannot on this node
                elif self.gpu_type_matching == 2:  # Only V100 cannot compromise
                    if job_a['gpu_type'] == 'V100' and job_a['gpu_type'] != node.gpu_type:
                        continue  # cannot on this node
                # </Node-job label matching>

                if job_a['num_inst'] == 1:
                    if job_a['num_gpu'] <= node.idl_gpus and job_a['num_cpu'] <= node.idl_cpus:
                        succ_alloc = node.alloc_job(job_a)
                        assert succ_alloc
                        job_a['node'] = node.id
                        print_fn("%sON  : N[%d] %s" % (cluster.log_prefix, job_a['node'], job_a))
                        self.display_node_status(cur_node_id=job_a['node'])
                        return 1
                else:  # gang-scheduling: all or nothing
                    node_idle_gpus, node_idle_cpus = node.idl_gpus, node.idl_cpus
                    node_inst_num_gpu, node_inst_num_cpu = job_a['num_inst'], job_a['num_inst']  # init.
                    if job_a['num_gpu'] != 0:
                        node_inst_num_gpu = node_idle_gpus // job_a['num_gpu']
                    if job_a['num_cpu'] != 0:
                        node_inst_num_cpu = node_idle_cpus // job_a['num_cpu']
                    node_inst_num = min(node_inst_num_gpu, node_inst_num_cpu)

                    if assigned_inst_num + node_inst_num >= job_a['num_inst']:
                        node_inst_num = job_a['num_inst'] - assigned_inst_num
                        assigned_node_map[nid] = node_inst_num
                        assigned_inst_num += node_inst_num
                        break
                    elif node_inst_num > 0:
                        assigned_node_map[nid] = node_inst_num
                        assigned_inst_num += node_inst_num

            if assigned_inst_num < job_a['num_inst']:
                print_fn("Cannot allocate all instances (%d/%d) of %s." % (assigned_inst_num, job_a['num_inst'], _repr_job_concise(job_a)))
                self.cannot_counter += 1
                if self.cannot_counter % 100000 == 0:
                    print_fn("[%s] %d rejects. len(job_done_list) = %d. Current job: %s." % (cluster.log_prefix, self.cannot_counter, len(self.cluster.job_history.job_done_list), _repr_job_concise(job_a)))
                return 0  # No successful allocation, for num_inst=1 and >1 cases
            else:
                # Successfully Scheduled. Assigning instances to nodes according to the map
                inst_id = 0
                for nid, num_inst in assigned_node_map.items():
                    node = sorted_node_list[nid]
                    job_tmp = {'node': -1}
                    for _ in range(num_inst):
                        job_tmp = job_a.copy()
                        job_tmp['inst_id'] = inst_id
                        succ_alloc = node.alloc_job(job_tmp)
                        assert succ_alloc
                        job_tmp['node'] = node.id
                        print_fn("%sON  : N[%d] %s Inst[%d]" % (cluster.log_prefix, job_tmp['node'], job_tmp, inst_id))
                        inst_id += 1
                    self.display_node_status(cur_node_id=job_tmp['node'])
                assert inst_id == job_a['num_inst']
                return 1

    def sorted_node_list(self, node_list):
        policy = self.sort_node_policy
        if policy == 0:
            node_list.sort(key=lambda n: n.id)  # by id
        elif policy == 1:
            node_list.sort(key=lambda n: n.idl_gpus)  # smallest idle gpus first
        elif policy == 2:
            node_list.sort(key=lambda n: -n.idl_gpus)  # largest idle gpus first
        elif policy == 3:
            node_list.sort(key=lambda n: n.util_rate)  # lowest avg. util. first
        else:
            node_list.sort(key=lambda n: n.id)
        return node_list

    def preempt_job(self, cluster=None):
        cluster = cluster if cluster is not None else self.cluster
        if all([n.idl_gpus for n in cluster.node_list]) >= 0 and \
            all([n.idl_cpus for n in cluster.node_list]) >= 0:
            return 0  # No resource contention, bypass preemption

        preempted_job_list = []
        if self.preempt_policy in PREEMPT_POLICY_DICT.keys():
            # Pre node preemption: self.preempt_job_node(node)
            for node in cluster.node_list:
                # As long as the resources are sufficient, no proactive preempt for now.
                if node.idl_gpus < 0 or node.idl_cpus < 0 or len(preempted_job_list) > 0:
                    print_fn("%sPreempt jobs on %s" % (cluster.log_prefix, node))
                    preempted_job_list = self.preempt_job_node(node, preempted_job_list)
            for job in preempted_job_list:
                print_fn("%sOFF : %s" % (cluster.log_prefix, job))
        else:
            raise NotImplementedError("Preempting job policies not implemented")

        for job in preempted_job_list:
            cluster.job_list.append(job)
            # Update Job
            job['wasted'] += job['progress']
            job['on_time'] = 0
            job['progress'] = 0
            job['node'] = None

    def preempt_job_node(self, node, preempted_job_list):
        # Svc is updated, but the job is not
        node.update_idl_gpus()
        node.update_idl_cpus()

        if self.preempt_policy in PREEMPT_POLICY_DICT.keys():
            # Sort node.job_runn_list in place
            self.preempt_job_sort_node(node=node, preempt_policy=self.preempt_policy)

            for job_i in preempted_job_list:
                for job_j in node.job_runn_list:
                    if job_i['job_id'] == job_j['job_id']:  # these instances belong to the same job
                        succ = node.release_job(job_i)
                        assert succ is True
                        preempted_job_list.append(job_i)

            while node.idl_gpus < 0 or node.idl_cpus < 0:
                job_to_preempt = node.job_runn_list[0]
                succ = node.release_job(job_to_preempt)
                assert succ is True
                preempted_job_list.append(job_to_preempt)

        else:
            raise KeyError("Uncaptured Preemption Policy Input: %d" % self.preempt_policy)

        return preempted_job_list

    def preempt_job_sort_node(self, node, preempt_policy):
        if preempt_policy == 1: # small_size_first
            node.job_runn_list.sort(key=lambda e: (e['size'], e['job_id']))
        elif preempt_policy == 2: # large_gang_first
            node.job_runn_list.sort(key=lambda e: (-e['num_gpu'], e['job_id']))
        else: # preempt_policy==0 or others: short_duration_first
            node.job_runn_list.sort(key=lambda e: (e['duration'], e['job_id']))

    def display_node_status(self, cur_node_id):
        if cur_node_id >= 0:
            cur_node = self.cluster.node_dict[cur_node_id]
            print_fn(cur_node)
