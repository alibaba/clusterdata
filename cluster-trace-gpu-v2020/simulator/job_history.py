from utils import add_user_round_robin_id
import numpy as np


class JobHistory:
    """
    As a class to record run jobs as "job history"
    Inc.: 1. job_done_list
          2. user_job_stats
          3. visualization
    """
    def __init__(self, job_done_list=None, window=10):
        self.job_done_list = list() if job_done_list is None else job_done_list.copy()
        self.user_job_stats = {}
        self.window = window
        self.job_window_list_dict = {}
        self.temp_user_stats = {}
        for job in self.job_done_list:
            self.stats_add_done_job(job)  # Only stats recorded
            # No jct summary here

    def alloc_job_sort(self, job_list, job_runn_list=None, metrics='dur_avg'):
        add_user_round_robin_id(job_list)
        # Early estimation: adding running jobs' on_time as sorting metrics
        if job_runn_list is not None:
            for job in job_runn_list:
                if job['user'] not in self.user_job_stats:
                    self.temp_user_stats[job['user']] = job['on_time']  # take job's current on_time as duration estimation
        job_list.sort(key=lambda j: (self.get_job_metrics(j, metrics), j['user_rrid']))

    def get_job_metrics(self, job, metrics):
        user = job['user']
        if user in self.user_job_stats:
            return self.user_job_stats[user][metrics]
        elif user in self.temp_user_stats:
            return self.temp_user_stats[user]
        else:
            return 0  # no history, no running job ==> duration = 0 ==> highest priority

    def stats_add_done_job(self, job):
        window_list = []  # Could use deque for better performance
        user = job['user']
        dur = job['duration']
        if user not in self.user_job_stats:
            assert user not in self.job_window_list_dict
            self.job_window_list_dict[user] = [dur]

            self.user_job_stats[user] = {
                'num_job': 1,
                'dur_avg': dur,
                'dur_mva': dur,
                'dur_har': min(1, 1 / dur)  # Harmonic mean
            }
        else:
            job_win_list = self.job_window_list_dict[user]
            length = len(job_win_list)
            if length >= self.window:
                job_win_list.pop(0)
            job_win_list.append(dur)
            
            dur_avg = self.user_job_stats[user]['dur_avg']
            dur_har = self.user_job_stats[user]['dur_har']
            num_job = self.user_job_stats[user]['num_job']
            dur_avg = dur_avg + (dur - dur_avg) / (num_job + 1)
            dur_har = dur_har + (min(1, 1/dur) - dur_har) / (num_job + 1)
            self.user_job_stats[user] = {
                'num_job': num_job + 1,
                'dur_avg': dur_avg,
                'dur_mva': sum(job_win_list)/len(job_win_list),
                'dur_har': dur_har
            }

    def add_done_job(self, job):
        self.job_done_list_add_job(job)
        self.stats_add_done_job(job)
        # self.jct_summary_v += job['jct']  # No jct summary here

    def job_done_list_add_job(self, job):
        """ form a more concise repr of job """
        job_dict = {}
        for k, v in job.items():
            if k in ['job_id', 'submit_time', 'duration', 'jct', 'wasted',
                     'num_inst', 'num_cpu', 'num_gpu', 'node', 'user', 'gpu_type']:
                job_dict[k] = v
        self.job_done_list.append(job_dict)

    @property
    def num_jobs_done(self):
        num_jobs_done = 0
        for stats in self.user_job_stats.values():
            num_jobs_done += stats['num_job']
        return num_jobs_done

    # Not recommended using job_done_list
    @property
    def jct_summary(self):
        jct_summary = 0
        for job in self.job_done_list:
            jct_summary += job['jct']
        # assert self.jct_summary_v == jct_summary
        return jct_summary
    
    @property
    def wait_time_summary(self):
        wait_time_summary = 0
        for job in self.job_done_list:
            wait_time_summary += job['jct'] - job['duration']
        return wait_time_summary

    @property
    def wasted_summary(self):
        wasted_summary = 0
        for job in self.job_done_list:
            wasted_summary += job['wasted']
        return wasted_summary

    def predict(self, user, metrics=None):
        """
        metrics: in ['dur_avg', 'dur_har', 'dur_mva']
        """

        metrics = 'dur_avg' if metrics is None else metrics
        assert metrics in ['dur_avg', 'dur_har', 'dur_mva']
        if user not in self.user_job_stats:
            return 0  # No record => optimistic est. as 0.
        else:
            res = self.user_job_stats[user][metrics]
            if np.isnan(res):
                raise TypeError
            return res
