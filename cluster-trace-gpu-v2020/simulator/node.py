from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from utils import print_fn

'''
Class Node
'''


class Node(object):
    def __init__(self, id, num_gpus=8, num_cpus=96, mem=720,
                 job_runn_list=None, gpu_type=0):
        self.id = id
        self.num_gpus = num_gpus * 100  # in %
        self.idl_gpus = self.num_gpus  # in %
        self.svc_gpus = 0  # occupied by higher-priority services
        self.job_gpus = 0  # sum([j['num_gpu'] for j in self.job_runn_list])
        # num_gpus = svc_gpus + job_gpus + idl_gpus
        #          = svc_gpus + cur_gpus

        self.gpu_type = gpu_type

        self.num_cpus = num_cpus * 100  # in %
        self.idl_cpus = self.num_cpus  # in %
        self.svc_cpus = 0
        self.job_cpus = 0

        self.mem = mem
        self.idl_mem = mem
        self.svc_mem = 0
        self.job_mem = 0

        self.network_in = 0  # bw, or traffic amount
        self.network_out = 0

        if job_runn_list is None:
            self.job_runn_list = list()
        else:
            self.job_runn_list = list(job_runn_list)

        print_fn('    Node[%3d]:(%3d GPUs,%4d CPUs) %s' %
                 (id, num_gpus, num_cpus, gpu_type))

    @property
    def util_rate(self):
        cpus_util = 1 - self.idl_cpus / self.num_cpus
        if self.num_gpus > 0:
            gpus_util = 1 - self.idl_gpus / self.num_gpus
            util_rate = round(100 * (gpus_util + cpus_util) / 2)
        else:
            util_rate = round(100 * cpus_util)
        return util_rate

    def __repr__(self):
        self.update_idl_gpus()
        self.update_idl_cpus()
        return 'N[%3d]: [(j %3d,i %3d)/%3d GPUs, (j %4d,i %4d)/%4d CPUs -- %3d Util.] %s' % (
            self.id, self.job_gpus, self.idl_gpus, self.num_gpus, self.job_cpus, self.idl_cpus, self.num_cpus,
            self.util_rate, self.gpu_type)

    def check_rsrc(self):
        assert self.num_gpus == self.svc_gpus + self.idl_gpus + self.job_gpus
        assert self.num_cpus == self.svc_cpus + self.idl_cpus + self.job_cpus

    def update_idl_gpus(self):
        self.idl_gpus = self.num_gpus - self.svc_gpus - self.job_gpus

    def update_idl_cpus(self):
        self.idl_cpus = self.num_cpus - self.svc_cpus - self.job_cpus

    '''alloc/release job'''

    def alloc_job(self, job):
        if self.alloc_res(num_gpus=job['num_gpu'], num_cpus=job['num_cpu']):
            self.job_runn_list.append(job)
            self.job_gpus += job['num_gpu']
            self.job_cpus += job['num_cpu']
            return True
        else:
            return False

    def release_job(self, job):
        if self.release_res(num_gpus=job['num_gpu'], num_cpus=job['num_cpu']):
            self.job_runn_list.remove(job)
            self.job_gpus -= job['num_gpu']
            self.job_cpus -= job['num_cpu']
            return True
        else:
            return False

    '''alloc/release srv'''

    def set_svc_res_by_ratio(self, ratio=0):
        self.svc_gpus = int(ratio * self.num_gpus)
        self.svc_cpus = int(ratio * self.num_cpus)
        self.update_idl_gpus()
        self.update_idl_cpus()

    '''alloc/release resource'''

    def alloc_res(self, num_gpus=0, num_cpus=0):
        # alloc job resource
        gpu = self.alloc_gpus(num_gpus)
        cpu = self.alloc_cpus(num_cpus)

        if not cpu and not gpu:
            return False
        elif not cpu and gpu:
            self.release_gpus(num_gpus)
            return False
        elif cpu and not gpu:
            self.release_cpus(num_cpus)
            return False

        return True

    def release_res(self, num_gpus, num_cpus):
        # input is gpu and cpu
        cpu = self.release_cpus(num_cpus)
        gpu = self.release_gpus(num_gpus)

        return cpu and gpu

    '''alloc/release resource with best efforts'''

    def alloc_gpu_best_effort(self, num_gpus=0):
        """return: num_gpus_left_to_alloc"""
        assert num_gpus >= 0

        if num_gpus <= self.idl_gpus:
            self.svc_gpus += num_gpus
            self.idl_gpus -= num_gpus
            num_gpus = 0
        else:
            self.svc_gpus += self.idl_gpus
            num_gpus -= self.idl_gpus
            self.idl_gpus = 0
        return num_gpus

    def alloc_cpu_best_effort(self, num_cpus=0):
        """return: num_cpus_left_to_alloc"""
        assert num_cpus >= 0
        if num_cpus <= self.idl_cpus:
            self.svc_cpus += num_cpus
            self.idl_cpus -= num_cpus
            num_cpus = 0
        else:
            self.svc_cpus += self.idl_cpus
            num_cpus -= self.idl_cpus
            self.idl_cpus = 0
        return num_cpus

    def release_gpu_best_effort(self, num_gpus=0):
        """return: num_gpus_left_to_release"""
        assert num_gpus >= 0
        if num_gpus <= self.svc_gpus:
            self.idl_gpus += num_gpus
            self.svc_gpus -= num_gpus
            num_gpus = 0
        else:
            self.idl_gpus += self.svc_gpus
            num_gpus -= self.svc_gpus
            self.svc_gpus = 0
        return num_gpus

    def release_cpu_best_effort(self, num_cpus=0):
        """return: num_cpus_left_to_release"""
        assert num_cpus >= 0
        if num_cpus <= self.svc_cpus:
            self.idl_cpus += num_cpus
            self.svc_cpus -= num_cpus
            num_cpus = 0
        else:
            self.idl_cpus += self.svc_cpus
            num_cpus -= self.svc_cpus
            self.svc_cpus = 0
        return num_cpus

    ''' GPU  '''

    def get_idl_gpus(self):
        return self.idl_gpus

    def alloc_gpus(self, num_gpus=0):
        '''
        If enough free gpus, allocate gpus
        Return: True, for success;
                False, for failure
        '''
        if num_gpus > self.idl_gpus:
            return False
        else:
            self.idl_gpus -= num_gpus
            return True

    def release_gpus(self, num_gpus=0):
        '''
        release using gpus back to free list
        '''
        if self.idl_gpus + num_gpus > self.num_gpus:
            self.idl_gpus = self.num_gpus
            return False
        else:
            self.idl_gpus += num_gpus
            return True

    ''' CPU '''

    def get_idl_cpus(self):
        return self.idl_cpus

    def alloc_cpus(self, num_cpus=0):
        '''
        If enough free cpus, allocate gpus
        Return: True, for success;
                False, for failure
        '''
        if num_cpus > self.idl_cpus:
            return False
        else:
            self.idl_cpus -= num_cpus
            return True

    def release_cpus(self, num_cpus=0):
        '''
        release using cpus back to free list
        '''
        if self.idl_cpus + num_cpus > self.num_cpus:
            self.idl_cpus = self.num_cpus
            return False
        else:
            self.idl_cpus += num_cpus
            return True

    '''network'''

    def add_network_load(self, in_load=0, out_load=0):
        self.network_in += in_load
        self.network_out += out_load
        self.network_in = round(self.network_in, 1)
        self.network_out = round(self.network_in, 1)

    def release_network_load(self, in_load=0, out_load=0):
        self.network_in -= in_load
        self.network_out -= out_load
        self.network_in = round(self.network_in, 1)
        self.network_out = round(self.network_in, 1)

    def set_network_load(self, in_load=0, out_load=0):
        self.network_in = in_load
        self.network_out = out_load
        self.network_in = round(self.network_in, 1)
        self.network_out = round(self.network_in, 1)

    def init_node(self, num_gpus=0, num_cpus=0, mem=0):
        if num_gpus != 0:
            self.num_gpus = num_gpus
            self.idl_gpus = num_gpus
        if num_cpus != 0:
            self.num_cpus = num_cpus
            self.idl_cpus = num_cpus
        if mem != 0:
            self.mem = mem
            self.idl_mem = mem
