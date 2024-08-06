#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import

import csv
import pandas as pd
import sys
import os
import warnings
warnings.filterwarnings("ignore")

# Parameters

del_acct = ["acct-hpc", "acct-stu"] # 不计入分析的账户名称
data_folder = "../data/" # 数据文件路径
template_folder = "../template/"

# Functions

# 整理日期date_new文件夹中的作业信息与作业id列表
def generate_job_id(date_new, del_acct):
    df = pd.read_csv(data_folder + date_new + "/jobs.csv", low_memory=False)
    df = df[['job_id', 'account_name', 'queue', 'queue_state', 'ncpus', 'run_time']]
    rename_map = {
    'job_id': 'JobID',
    'account_name': 'Account',
    'queue': 'Partition',
    'queue_state': 'State',
    'ncpus': 'NCPUS',
    'run_time': 'CPUTime'
    }
    df.rename(columns=rename_map, inplace=True)
    df = df[~df["Account"].isin(del_acct)]
    df.to_csv(data_folder + date_new + "/jobs_end.csv", index=False)
    job_id = df['JobID'].drop_duplicates()
    job_id.to_csv(data_folder + date_new + "/job_id.csv", index=False)

# 生成用于资源利用率查询的slurm脚本
def generate_slurm_file(date_new):
    source_file = template_folder + "cpu_seff.slurm"
    destination_file = data_folder + date_new + "/cpu_seff.slurm"
    with open(source_file, 'r') as source:
        with open(destination_file, 'w') as destination:
            for line in source:
                destination.write(line)
            write_date = " " + date_new
            destination.write(write_date)
    source_file = template_folder + "memory_seff.slurm"
    destination_file = data_folder + date_new + "/memory_seff.slurm"
    with open(source_file, 'r') as source:
        with open(destination_file, 'w') as destination:
            for line in source:
                destination.write(line)
            write_date = " " + date_new
            destination.write(write_date)

# Main

if __name__ == "__main__":

    # 确定执行操作的日期
    if len(sys.argv) > 2:
        print("参数错误。")
        sys.exit(1)
    elif len(sys.argv) == 2:
        dates = [0, sys.argv[1]]
    else:
        csv_filename = data_folder + 'info/dates_all.csv'
        dates = []
        with open(csv_filename, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                dates.append(row[0])
    print(dates)
    print("")

    for i in range(1,len(dates)):
        date = dates[i]
        print(f"日期：{date}")
        
        folder_name = data_folder + date
        if not os.path.exists(folder_name):
            print(f"错误：文件夹 '{folder_name}' 不存在。")
            sys.exit(1)
        file_name = folder_name + "/jobs.csv"
        if not os.path.isfile(file_name):
            print(f"错误：文件 '{file_name}' 不存在。")
            sys.exit(1)

        generate_job_id(date, del_acct)
        generate_slurm_file(date)