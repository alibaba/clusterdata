import os
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

########### Data Constants ###########
DATA_DIR = '../data/'
if not os.access('/tmp/figures', os.F_OK):
    os.mkdir('/tmp/figures')
if not os.access('/tmp/figures', os.W_OK):
    print('Cannot write to /tmp/figures, please fix it.')
    exit()
else:
    print('figures saved to /tmp/figures')

########### Prepare Functions ###########
def get_df(file, header=None):
    df = pd.read_csv(file, header=None)
    # df.columns = DF_HEADER.get(key, df.columns)
    df.columns = pd.read_csv("{}.header".format(file.split('.csv')[0])).columns if header is None else header
    return df

def load_all_df():
    dfj = get_df(DATA_DIR + 'pai_job_table.csv')
    dft = get_df(DATA_DIR + 'pai_task_table.csv')
    dfi = get_df(DATA_DIR + 'pai_instance_table.csv')
    dfs = get_df(DATA_DIR + 'pai_sensor_table.csv')
    dfg = get_df(DATA_DIR + 'pai_group_tag_table.csv')
    dfp = get_df(DATA_DIR + 'pai_machine_spec.csv')
    dfm = get_df(DATA_DIR + 'pai_machine_metric.csv')
    return dfj,dft,dfi,dfs,dfg,dfp,dfm

def get_dfiw(dfi):
    dfiw = dfi.sort_values(['status','start_time','end_time'])
    dfiw.drop_duplicates(subset=['worker_name'], keep='last', inplace=True)
    dfiw.dropna(subset=['worker_name'], inplace=True)
    dfiw['runtime'] = dfiw[(dfiw.start_time>0)&(dfiw.end_time>0)]['end_time'] \
                    - dfiw[(dfiw.start_time>0)&(dfiw.end_time>0)]['start_time']
    dfiw.loc[dfiw.start_time==0, 'start_time'] = np.nan
    dfiw.loc[dfiw.start_time==0, 'end_time'] = np.nan
    return dfiw

def get_dfw(dfi, dft, dfg):
    dfw = get_dfiw(dfi)
    dfw['start_date']=dfw.start_time.apply(pd.Timestamp, unit='s', tz='Asia/Shanghai')
    print('dfi + dft ...')
    dfw = dfw.merge(dft, on=['job_name','task_name'], how='left', suffixes=['', '_t'])
    print('dfi + dft + dfg ...')
    dfw = dfw.merge(dfg, on='inst_id', how='left')  # reserve NaN ones by how='left'
    dfw.loc[dfw.group.isnull(),'group'] = dfw.loc[dfw.group.isnull(), 'user']  # fill group==NaN ones with user
    return dfw

def get_dfia(dfi):
    dfi_s = dfi[dfi.start_time > 0][['job_name','task_name','start_time']].groupby(['job_name','task_name']).min()  # start_time
    dfi_e = dfi[dfi.end_time > 0][['job_name','task_name','end_time']].groupby(['job_name','task_name']).max()  # end_time
    dfi_m = dfi[(dfi.start_time > 0) & (dfi.end_time > 0)][['job_name','task_name','end_time','start_time']]
    dfi_m['runtime'] = dfi_m.end_time-dfi_m.start_time
    dfi_m = dfi_m.groupby(['job_name','task_name']).mean()[['runtime']].reset_index() # runtime
    dfi_u = dfi[['job_name','task_name','status']].drop_duplicates().groupby(['job_name','task_name']).max() # status
    dfia = dfi_u
    for df in [dfi_s, dfi_e, dfi_m]:
        dfia = dfia.merge(df, on=['job_name','task_name'], how='left')
    return dfia

def get_dfa(dft, dfj, dfi, dfg):
    print('dft + dfj ...')
    dfa = dft.merge(dfj, on=['job_name'], suffixes = ['','_j'])
    dfa.loc[dfa.start_time==0, 'start_time'] = np.nan
    dfa.loc[dfa.start_time==0, 'end_time'] = np.nan
    dfa['runtime'] = dfa.end_time - dfa.start_time
    print('dft + dfj + dfi ...')
    dfia = get_dfia(dfi)
    dfa = dfa.merge(dfia, on=['job_name','task_name'], suffixes=['','_i'])
    dfa['duration_min'] = dfa.runtime_i / 60  # duration of instances
    dfa['wait_time'] = dfa.start_time_i - dfa.start_time # task wait time
    dfa['start_date']=dfa.start_time.apply(pd.Timestamp, unit='s', tz='Asia/Shanghai') # task start time
    # dfa = dfa[dfa.status=='Terminated']
    print('dft + dfj + dfi + dfg ...')
    dfa = dfa.merge(dfg[[x for x in dfg.columns if x != 'user']], on='inst_id', how='left')  # reserve NaN ones by how='left'
    dfa.loc[dfa.group.isnull(),'group'] = dfa.loc[dfa.group.isnull(), 'user']  # fill group==NaN ones with user
    return dfa

def get_dfwitm(dfwit, csv_file='intermediate_data/machine_metric_shennong_machine_all.csv'):
    res_df = pd.read_csv(csv_file, index_col=0)
    dfwitm = dfwit.merge(res_df.loc[:, ~res_df.columns.isin(['start_time','end_time','machine'])], on='worker_name', how='left')
    return dfwitm

########### Plot Functions ###########
linestyle_list = [
     ('solid', 'solid'),       # Same as (0, ()) or '-'
     ('dotted', 'dotted'),     # Same as (0, (1, 1)) or '.'
     ('dashed', 'dashed'),     # Same as '--'
     ('dashdot', 'dashdot'),   # Same as '-.'
     ('densely dashdotdotted', (0, (3, 1, 1, 1, 1, 1))),
     ('densely dashdotted',    (0, (3, 1, 1, 1))),
     ('densely dotted',        (0, (1, 1))),
     ('densely dashed',        (0, (5, 1))),
     ('dashdotdotted',         (0, (3, 5, 1, 5, 1, 5))),
     ('loosely dashed',        (0, (5, 10))),
     ('loosely dashdotted',    (0, (3, 10, 1, 10))),
     ('loosely dashdotdotted', (0, (3, 10, 1, 10, 1, 10))),
     ('loosely dotted',        (0, (1, 10))),
     ('dashed',                (0, (5, 5))),
     ('dashdotted',            (0, (3, 5, 1, 5))),
     ('dotted',                (0, (1, 1))),
]

def get_cdf(data, inverse=False):
    sorted_data = sorted(data)
    p = 100. * np.arange(len(sorted_data))/(len(sorted_data)-1)
    p = 100. - p if inverse else p # CCDF
    return sorted_data, p

def plot_data_cdf(data, inverse=False, datalabel=None, xlabel=None, title=None, xlog=False, xlim=None, ylog=False, xticks=None, figsize=(4,3), dpi=120, savefig=None, ylabel=None):
    plt.figure(figsize=figsize, dpi=dpi)
    if type(data) == pd.DataFrame:
        data.dropna(inplace=True)
    x, y = get_cdf(data, inverse)
    plt.plot(x, y, label=datalabel, color='green', linestyle='-')
    if datalabel is not None: plt.legend(loc='lower right')
    if xlog: plt.xscale('log')
    if ylog: plt.yscale('log')
    if xlim is not None: plt.xlim(xlim)
    plt.ylim(0, 100)
    if xlabel is not None: plt.xlabel(xlabel)
    plt.ylabel(ylabel) if ylabel is not None else plt.ylabel('CCDF') if inverse is True else plt.ylabel('CDF')
    if title is not None: plt.title(title)
    if xticks is not None: plt.xticks(xticks)
    plt.grid(alpha=.3, linestyle='--')
    if savefig is not None:
        plt.savefig('/tmp/figures/{}.pdf'.format(savefig),bbox_inches='tight')
    else:
        plt.show()

def plot_data_cdfs(data, datalabel=None, inverse=False, xlabel=None, title=None, xlog=False, ylog=False, xticks=None, figsize=(4,3), dpi=120, xlim=None, ylim=None, ylabel=None, yticks=None, savefig=None, loc='best', fontsize=None):
    plt.figure(figsize=figsize, dpi=dpi)
    for i, d in enumerate(data):
        if type(data) == pd.DataFrame:
            d.dropna(inplace=True)
        x, y = get_cdf(d, inverse)
        label = datalabel[i] if datalabel is not None else None
        plt.plot(x, y, label=label, linestyle=linestyle_list[i % len(linestyle_list)][1])
    if datalabel is not None: plt.legend(loc=loc, fontsize=fontsize)
    if xlog: plt.xscale('log')
    if ylog: plt.yscale('log')
    plt.ylim(0, 100) if ylim is None else plt.ylim(ylim)
    if xlim is not None: plt.xlim(xlim)
    if xlabel is not None: plt.xlabel(xlabel)
    if ylabel is None:
        plt.ylabel('CCDF') if inverse is True else plt.ylabel('CDF')
    else:
        plt.ylabel(ylabel)
    if title is not None: plt.title(title)
    if xticks is not None: plt.xticks(xticks)
    if yticks is not None: plt.yticks(yticks)
    plt.grid(alpha=.3, linestyle='--')
    if savefig is not None:
        plt.savefig('/tmp/figures/{}.pdf'.format(savefig),bbox_inches='tight')
    else:
        plt.show()

def draw_bar_plot(odf, col, figsize=(4,4), dpi=120, portion=False, title=None, limit=30):
    dfout=odf.reset_index().groupby(col).count()[['index']].sort_values('index', ascending=False).head(limit)
    dfout['portion'] = 100 * dfout['index'] / dfout['index'].sum()
    plt.figure(figsize=figsize, dpi=dpi)
    if portion:
        plt.barh(y=dfout.index, width=dfout['portion'])
        plt.xlabel('Percentage (total: %.2f)'%(dfout['index'].sum()))
    else:
        plt.barh(y=dfout.index, width=dfout['index'])
    plt.grid(alpha=.3, linestyle='--')
    return dfout

########### Process Functions ###########

def get_inst_task_num_ratio(dfa, inst_num_list=[2, 8, 20, 64, 100, 256, 512]):
    total_num_task, total_num_inst = len(dfa), sum(dfa['inst_num'])
    data_df = []
    for i in inst_num_list:
        temp_df = dfa[dfa['inst_num'] >= i]
        task_num_ratio = len(temp_df) / total_num_task
        inst_num_ratio = sum(temp_df['inst_num']) / total_num_inst
        data_df.append([task_num_ratio, inst_num_ratio])
    out_df = pd.DataFrame(data_df, columns=['num_task_ratio','num_inst_ratio'])
    out_df = out_df.T.rename(columns=dict(zip(range(len(inst_num_list)), inst_num_list)))
    return out_df


def add_hour_date(df):
    if 'start_date' not in df:
        if 'start_time_t' in df:
            target_col = 'start_time_t'
        elif 'start_time' in df:
            target_col = 'start_time'
        else:
            print('start_time, start_time_t, dayofyear unfound in df')
            return None
        df['start_date'] = df[target_col].apply(lambda x: pd.Timestamp(x, unit='s', tz='Asia/Shanghai'))
    if 'date' not in df:
        df['date'] = df['start_date'].apply(lambda x: x.date())
    if 'hour' not in df:
        df['hour'] = df['start_date'].apply(lambda x: x.hour)
    return df

def get_hourly_task_request(df): # df = dftjkix
    sum_df_list = []
    df = add_hour_date(df.copy())
    # for day in sorted(df.dayofyear.unique()):
    for date in sorted(df.date.unique()):
        # tempdf = df[df.dayofyear==day]
        tempdf = df[df.date==date]
        res_df = tempdf.groupby('hour').count()[['job_name']]
        res_df.rename(columns={'job_name':date}, inplace=True)
        sum_df_list.append(res_df.T)
    out_df = pd.DataFrame().append(sum_df_list)
    return out_df.dropna() # if a day contains hours of NaN, it is not a typical day

def get_hourly_task_resource_request(df, metrics='cpu'): # df = dftjkix
    sum_df_list = []
    df = add_hour_date(df)
    if metrics == 'cpu':
        df['plan_resource'] = df.plan_cpu.apply(lambda x: x/100)
    elif metrics == 'gpu':
        df['plan_resource'] = df.plan_gpu.apply(lambda x: x/100)
    elif metrics == 'mem':
        df['plan_resource'] = df.plan_mem.apply(lambda x: x/1000)
    else:
        exit()
    # for day in sorted(df.dayofyear.unique()):
    for date in sorted(df.date.unique()):
        # tempdf = df[df.dayofyear==day]
        tempdf = df[df.date==date]
        res_df = tempdf.groupby('hour').sum()[['plan_resource']]
        res_df.rename(columns={'job_name':date}, inplace=True)
        sum_df_list.append(res_df.T)
    out_df = pd.DataFrame().append(sum_df_list)
    return out_df.dropna() # if a day contains hours of NaN, it is not a typical day

def plan_minus_usg_over_cap_task(dfas):
    dfas['plan_gpu_minus_usage_over_capacity'] = (dfas['plan_gpu'] - dfas['gpu_wrk_util']) / (100 * dfas['cap_gpu'])
    dfas['plan_cpu_minus_usage_over_capacity'] = (dfas['plan_cpu'] - dfas['cpu_usage']) / (100 * dfas['cap_cpu'] )
    dfas['plan_mem_minus_usage_over_capacity'] = (dfas['plan_mem'] - dfas['avg_mem']) / dfas['cap_mem']

    dfas_task = dfas.groupby(['job_name','task_name'])[['plan_gpu_minus_usage_over_capacity','plan_cpu_minus_usage_over_capacity','plan_mem_minus_usage_over_capacity']].mean()

    pgu_datas, pgu_label, ugp_datas, ugp_label = [], [], [], []
    for device in ['cpu','gpu','mem']:
        apu = dfas_task[~dfas_task['plan_{}_minus_usage_over_capacity'.format(device)].isnull()]
        pgu = dfas_task[dfas_task['plan_{}_minus_usage_over_capacity'.format(device)] > 0]
        ugp = dfas_task[dfas_task['plan_{}_minus_usage_over_capacity'.format(device)] < 0]
        print("{}: plan > usage: {:.2f}%, plan < usage: {:.2f}%".format(
            device, 100 * len(pgu) / len(apu), 100 * len(ugp) / len(apu)    ))
        pgu_label.append("{} {:.2f}%".format(device, 100 * len(pgu) / len(apu)))
        pgu_datas.append(pgu['plan_{}_minus_usage_over_capacity'.format(device)])
        ugp_label.append("{} {:.2f}%".format(device, 100 * len(ugp) / len(apu)))
        ugp_datas.append(-ugp['plan_{}_minus_usage_over_capacity'.format(device)])

    return pgu_datas, ugp_datas, pgu_label, ugp_label