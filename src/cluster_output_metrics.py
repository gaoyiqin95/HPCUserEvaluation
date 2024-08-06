#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import

import pandas as pd
import sys
import csv
import warnings
warnings.filterwarnings("ignore")

# Parameters

data_folder = "../data/" # 数据文件路径


# Functions

#1.总机时
def calculate_job_size_all(df):
    job_size2 = df[['JobID', 'Account', 'CPUTime', 'NCPUS']]
    job_size2["job_size"] = job_size2['CPUTime']/1000/3600*(job_size2['NCPUS'])
    job_size_new = sum(job_size2["job_size"])
    return job_size_new

#2.CPU利用率
def calculate_cpu_efficiency_all(df, date_new):
    cpu_efficiency2 = df[["JobID", "NCPUS"]]
    cpu_efficiency = pd.read_csv(data_folder + date_new + "/cpu_efficiency.csv")
    cpu_efficiency.columns = ["efficiency", "JobID"]
    cpu_efficiency['efficiency'] = cpu_efficiency['efficiency'].str.rstrip('%').astype('float') / 100.0
    cpu_efficiency['efficiency'] = cpu_efficiency['efficiency'].astype(float)
    cpu_efficiency.loc[cpu_efficiency['efficiency'] > 1, 'efficiency'] = 1
    cpu_efficiency["JobID"] = cpu_efficiency["JobID"].str.strip()
    cpu_efficiency2 = pd.merge(cpu_efficiency, cpu_efficiency2, on="JobID")
    cpu_efficiency2["all_efficiency"] = cpu_efficiency2["efficiency"]*cpu_efficiency2["NCPUS"]
    cpu_efficiency_new = sum(cpu_efficiency2["all_efficiency"])/sum(cpu_efficiency2["NCPUS"])
    cpu_efficiency_new = cpu_efficiency_new*100
    return cpu_efficiency_new

#3.内存利用率
def calculate_memory_efficiency_all(df, date_new):
    memory_efficiency2 = df[["JobID", "NCPUS"]]
    memory_efficiency = pd.read_csv(data_folder + date_new + "/memory_efficiency.csv")
    memory_efficiency.columns = ["efficiency", "JobID"]
    memory_efficiency['efficiency'] = memory_efficiency['efficiency'].str.rstrip('%').astype('float') / 100.0
    memory_efficiency['efficiency'] = memory_efficiency['efficiency'].astype(float)
    memory_efficiency.loc[memory_efficiency['efficiency'] > 1, 'efficiency'] = 1
    memory_efficiency["JobID"] = memory_efficiency["JobID"].str.strip()
    memory_efficiency2 = pd.merge(memory_efficiency, memory_efficiency2, on="JobID")
    memory_efficiency2["all_efficiency"] = memory_efficiency2["efficiency"]*memory_efficiency2["NCPUS"]
    memory_efficiency_new = sum(memory_efficiency2["all_efficiency"])/sum(memory_efficiency2["NCPUS"])
    memory_efficiency_new = memory_efficiency_new * 100
    return memory_efficiency_new

#4.完成率
def calculate_exception_all(df):
    exception_job_new = 1-len(df[df['State'].isin(["FAILED", "TIMEOUT", "CANCELLED"])])/len(df)
    exception_job_new = exception_job_new * 100
    return exception_job_new

#5.作业规模
def calculate_job_ncore_all(df):
    job_ncore = df[['JobID', 'Account', 'NCPUS']]
    job_ncore["job_ncore"] = job_ncore['NCPUS']
    job_ncore_new = sum(job_ncore["job_ncore"])/len(job_ncore["job_ncore"])
    return job_ncore_new


# Main

if __name__ == "__main__":

    # 确定执行操作的日期
    if len(sys.argv) == 3:
        dates = [0, sys.argv[1], sys.argv[2]]
    elif len(sys.argv) == 1:
        csv_filename = data_folder + 'info/dates_all.csv'
        dates = []
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                dates.append(row[0])
    else:
        print("参数错误。")
        sys.exit(1)
    print(dates)
    print("")

    for i in range(1,len(dates)):
        date_new = dates[i]
        df = pd.read_csv(data_folder + date_new + "/jobs_end.csv")
        job_size_cluster = calculate_job_size_all(df)
        cpu_efficiency_cluster = calculate_cpu_efficiency_all(df, date_new)
        memory_efficiency_cluster = calculate_memory_efficiency_all(df, date_new)
        exception_cluster = calculate_exception_all(df)
        job_ncore_cluster = calculate_job_ncore_all(df)

        new_row = [date_new, job_size_cluster, cpu_efficiency_cluster, 
                memory_efficiency_cluster, exception_cluster, 
                job_ncore_cluster]
        print(new_row)
        filename = data_folder + 'cluster/metrics_cluster.csv'
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(new_row)    