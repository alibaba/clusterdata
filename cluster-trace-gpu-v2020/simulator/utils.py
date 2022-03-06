import logging
import csv
import numpy as np
from matplotlib import pyplot as plt

ALLOC_POLICY_DICT = {
    0: 'SJF',  # 'short job first', SJF
    1: 'SJU',  # SJF with estimator using USER feature
    2: 'SJG',  # SJF with estimator using GROUP, USER feature
    4: 'SJGG',  # SJF with estimator using GROUP, USER, GPU feature
    8: 'FIFO',  # FIFO, the default
}

PREEMPT_POLICY_DICT = {
    0: 'SDF',  # 'smallest_duration_first'
    1: 'SSF',  # 'smallest_size_first
    2: 'LGF',  # 'large_gpu_first', # LGF, size:num_gpu
}

GPU_TYPE_INT_DICT = {
    "CPU":  0,
    "MISC": 1,
    "T4":   2,
    "P100": 3,
    "V100": 4
}


def print_fn(log, level=1):
    LOG_LEVEL_DEBUG = 0
    LOG_LEVEL_INFO = 1
    LOG_LEVEL_WARNING = 2
    LOG_LEVEL_ERROR = 3
    if level == LOG_LEVEL_DEBUG:
        logging.debug(log)
    elif level == LOG_LEVEL_INFO:
        logging.info(log)
    elif level == LOG_LEVEL_WARNING:
        logging.warning(log)
    elif level == LOG_LEVEL_ERROR:
        logging.error(log)
        exit()


def _repr_job_concise(job_dict):
    return "J %s([G %s,C %s]-D %s)" % (job_dict['job_id'], job_dict['num_gpu'], job_dict['num_cpu'], job_dict['duration'])


def _repr_job_preempt(job_dict):
    return "J %s-[G %s,C %s]-O:%3s/D:%3s" % (job_dict['job_id'], job_dict['num_gpu'], job_dict['num_cpu'], job_dict['on_time'], job_dict['duration'])


def _repr_job_done(job_dict):
    job_repr_concise = "J %s([G %s,C %s]-D %s-N %s)" % (job_dict['job_id'], job_dict['num_gpu'], job_dict['num_cpu'], job_dict['duration'], job_dict['node'])
    return "%25s: %4s ---> %4s" % (job_repr_concise, job_dict['jct'] - job_dict['duration'], job_dict['jct'])


def _add_describe(describe_file):
    if describe_file is None:
        return None
    describe_dict = {}
    with open(describe_file, 'r') as fd:
        reader = csv.DictReader(fd, delimiter=',')
        for row in reader:
            for k, v in row.items():
                if k=='count':
                    row[k] = int(v)
                elif k in ['mean', 'std', 'min', '25%', '50%', '75%', 'max']:
                    if v == '':
                        v = 0
                    row[k] = float(v)
            describe_dict[row['user']] = row
    return describe_dict  # dd['ae8ed1']['50%']==38.4 


def _add_job(job_list, job_dict, describe_dict=None):
    # Add job (job_dict) into job_list
    for key, value in job_dict.items():
        if value is not None and value.isdigit() and key != 'user':
            if type(value) == str:
                job_dict[key] = round(float(value))
            else:  # duration becomes an int
                job_dict[key] = round(value)
        elif key in ['wait_time','user_dur','user_gpu_dur','group_dur','group_gpu_dur']:
            try:
                job_dict[key] = float(value)
            except:
                pass

    keys = ['num_cpu', 'num_gpu', 'submit_time', 'num_inst']
    for key in keys:
        if key not in job_dict or job_dict[key] == '':
            if key in ['num_cpu', 'num_gpu']:
                job_dict[key] = 0
            else:  # key in ['submit_time', 'num_inst']
                job_dict[key] = 1
        else:
            if key in ['num_cpu', 'num_gpu']:  # in %
                job_dict[key] = round(100 * float(job_dict[key]))
            else:
                job_dict[key] = round(float(job_dict[key]))

    # Add entries to be used in scheduling
    job_dict['duration'] = int(float(job_dict['duration']))
    if job_dict['duration'] <= 0:
        job_dict['duration'] = 1  # fix duration == 0 problem.
    job_dict['size'] = int((job_dict['num_gpu'] + job_dict['num_cpu']) * job_dict['duration']) # (gpu + cpu) x duration
    job_dict['on_time'] = 0
    job_dict['wasted'] = 0
    job_dict['jct'] = -1
    job_dict['resource'] = [job_dict['num_gpu'], job_dict['num_cpu']] # list of resources
    job_dict['node'] = None

    # Add duration estimation
    if describe_dict is not None:
        jd_user = describe_dict.get(job_dict['user'])
        if jd_user is not None:
            job_dict['dur_avg'] = float(jd_user['mean'])  # expectation
            job_dict['dur_std'] = float(jd_user['std'])  # standard deviation
            job_dict['dur_med'] = float(jd_user['50%'])  # median
            job_dict['dur_trim_mean'] = float(jd_user['trim_mean'])  # discard 10% top and 10% tail when calc. mean

    # Remove original unused entries
    for drop_col in ['fuxi_job_name','fuxi_task_name','inst_id','running_cluster','model_name','iterations','interval','vc','jobid','status']:
        if drop_col in job_dict: job_dict.pop(drop_col)

    job_list.append(job_dict)


def add_user_round_robin_id(job_list):
    # Add a new sorting metrics, user_rrid, to enforce scheduler picking jobs from multiple users
    # when all users' primary metrics are the same (e.g., 0).
    user_rrid_dict = {}  # a new dict each time
    for job in job_list:
        user = job['user']
        rrid = user_rrid_dict.get(user, None)
        if rrid is None:
            rrid = 0
            user_rrid_dict[user] = 1
        else:
            user_rrid_dict[user] += 1
        job['user_rrid'] = rrid


def large_job_pruning(job_list, gpu_limit, cpu_limit):
    if job_list is None:
        return []
    for job in job_list:
        if 'num_gpu' in job and job['num_gpu'] > gpu_limit:
            gpu_was = job['num_gpu']
            job['num_gpu'] = gpu_limit
            print_fn("{:s}: GPU {:d} ==> {:d}".format(_repr_job_concise(job), gpu_was, gpu_limit))
        if 'num_cpu' in job and job['num_cpu'] > cpu_limit:
            cpu_was = job['num_cpu']
            job['num_cpu'] = cpu_limit
            print_fn("{:s}: CPU {:d} ==> {:d}".format(_repr_job_concise(job), cpu_was, cpu_limit))
    return job_list


def plot_cluster_util(npyfile, to_date=False):
    cluster_util = np.load(npyfile)
    cluster_time, cluster_cpu, cluster_gpu = cluster_util[0], cluster_util[1], cluster_util[2]

    plt.clf()
    plt.plot(cluster_time, cluster_cpu / 10, label='10CPU')
    plt.plot(cluster_time, cluster_gpu, label='GPU')
    plt.legend()
    try:
        plt.savefig(str(npyfile).split('.npy')[0]+".png")
    except:
        plt.savefig("cluster_util")


def plot_job_stats(npyfile, to_date=False):
    plt.figure(figsize=(16, 6), dpi=120)
    job_stats = np.load(npyfile)
    job_submit_time, job_duration, job_jct, job_gpu_type, job_num_inst, job_id = job_stats[0], job_stats[1], job_stats[2], job_stats[3], job_stats[4], job_stats[5]
    job_queue_delay = job_jct - job_duration

    plt.clf()
    plt.plot(job_submit_time, job_queue_delay, color='orange', label='queue_delay')
    plt.plot(job_submit_time, job_duration, color='black', alpha=0.3, label='duration')
    plt.legend()
    try:
        plt.savefig(str(npyfile).split('.npy')[0]+".png")
    except:
        plt.savefig("job_stats")


def plot_multi_job_stats(npyfiles, to_date=False):
    plt.clf()
    plt.figure(figsize=(12, 6), dpi=120)
    
    for npyfile in npyfiles:
        job_stats = np.load(npyfile)
        job_submit_time, job_duration, job_jct, job_gpu_type, job_num_inst, job_id = job_stats[0], job_stats[1], job_stats[2], job_stats[3], job_stats[4], job_stats[5]
        job_queue_delay = job_jct - job_duration

        try:
            label=ALLOC_POLICY_DICT[int(str(npyfile).split('.log.a')[1].split('-p')[0])]
        except KeyError:
            label = str(npyfile).split('.log.')[1].split('-job_stats.npy')[0]
        plt.plot(job_submit_time, job_queue_delay, alpha=0.5, label=label+'-queue_delay')
        plt.plot(job_submit_time, job_duration, color='grey', alpha=0.3, label='job duration')
    plt.legend(loc='upper left')
    plt.title("Arrival jobs' duration and queueing delay")
    plt.xlabel("Submitted Time")
    plt.ylabel("Run/Wait Time")
    try:
        plt.savefig(str(npyfile).split('.log.')[0]+"-job_stats.png")
    except:
        plt.savefig("job_stats")


def plot_multi_cluster_util(npyfiles, to_date=False):
    plt.clf()
    plt.figure(figsize=(12, 6), dpi=120)
    
    for npyfile in npyfiles:
        cluster_util = np.load(npyfile)
        cluster_time, cluster_cpu, cluster_gpu = cluster_util[0], cluster_util[1], cluster_util[2]

        try:
            label=ALLOC_POLICY_DICT[int(str(npyfile).split('.log.a')[1].split('-p')[0])]
        except KeyError:
            label = str(npyfile).split('.log.')[1].split('-cluster_util.npy')[0]
        plt.plot(cluster_time, cluster_gpu, alpha=0.5, label=label+'-GPU')
    plt.legend(loc='upper left')
    plt.title("Cluster Utilization")
    plt.xlabel("Time")
    plt.ylabel("Resource")
    try:
        plt.savefig(str(npyfile).split('.log.')[0]+"-cluster_util.png")
    except:
        plt.savefig("cluster_util")
