#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import

import pandas as pd
import sys
import os
import csv
import warnings
warnings.filterwarnings("ignore")

# Parameters

data_folder = "../data/" # 数据文件路径
template_folder = "../template/"


# Functions

#1.总机时
def calculate_job_size(df):
    user_job_size = df[['JobID', 'Account', 'CPUTime', 'NCPUS']] # , 'ngpus'
    user_job_size["job_size"] = user_job_size['CPUTime']/1000/3600*(user_job_size['NCPUS']) # +user_job_size['ngpus']
    user_job_size = user_job_size[['JobID', 'Account', 'job_size']]
    user_job_size = user_job_size.groupby(['Account']).agg({"JobID":"count", "job_size":"sum"})
    user_job_size = user_job_size.reset_index()
    user_job_size = user_job_size.rename(columns={"JobID":"job_count"})
    user_job_size.set_index("Account", inplace=True)
    user_job_size = user_job_size.sort_values("job_size",ascending=False)
    return user_job_size

#2.CPU利用率
def calculate_cpu_efficiency(df, date_new):
    user_cpu_efficiency = df[["JobID", "Account", "NCPUS"]]
    cpu_efficiency = pd.read_csv(data_folder + date_new + "/cpu_efficiency.csv")
    cpu_efficiency.columns = ["efficiency", "JobID"]
    cpu_efficiency['efficiency'] = cpu_efficiency['efficiency'].str.rstrip('%').astype('float') / 100.0
    cpu_efficiency['efficiency'] = cpu_efficiency['efficiency'].astype(float)
    cpu_efficiency.loc[cpu_efficiency['efficiency'] > 1, 'efficiency'] = 1
    cpu_efficiency["JobID"] = cpu_efficiency["JobID"].str.strip()
    user_cpu_efficiency = pd.merge(cpu_efficiency, user_cpu_efficiency, on="JobID")
    user_cpu_efficiency["cpu_efficiency"] = user_cpu_efficiency["efficiency"]*user_cpu_efficiency["NCPUS"]
    user_cpu_efficiency = user_cpu_efficiency.groupby(['Account']).sum()
    user_cpu_efficiency = user_cpu_efficiency.drop(['JobID', 'efficiency'], axis=1)
    user_cpu_efficiency["cpu_efficiency"] = user_cpu_efficiency["cpu_efficiency"]/user_cpu_efficiency["NCPUS"]*100
    user_cpu_efficiency = user_cpu_efficiency.drop(['NCPUS'], axis=1)
    return user_cpu_efficiency


#3.内存利用率
def calculate_memory_efficiency(df, date_new):
    user_memory_efficiency = df[["JobID", "Account", "NCPUS"]]
    memory_efficiency = pd.read_csv(data_folder + date_new + "/memory_efficiency.csv")
    memory_efficiency.columns = ["efficiency", "JobID"]
    memory_efficiency['efficiency'] = memory_efficiency['efficiency'].str.rstrip('%').astype('float') / 100.0
    memory_efficiency['efficiency'] = memory_efficiency['efficiency'].astype(float)
    memory_efficiency.loc[memory_efficiency['efficiency'] > 1, 'efficiency'] = 1
    memory_efficiency["JobID"] = memory_efficiency["JobID"].str.strip()
    user_memory_efficiency = pd.merge(memory_efficiency, user_memory_efficiency, on="JobID")
    user_memory_efficiency["memory_efficiency"] = user_memory_efficiency["efficiency"]*user_memory_efficiency["NCPUS"]
    user_memory_efficiency = user_memory_efficiency.groupby(['Account']).sum()
    user_memory_efficiency = user_memory_efficiency.drop(['JobID', 'efficiency'], axis=1)
    user_memory_efficiency["memory_efficiency"] = user_memory_efficiency["memory_efficiency"]/user_memory_efficiency["NCPUS"]*100
    user_memory_efficiency = user_memory_efficiency.drop(['NCPUS'], axis=1)
    return user_memory_efficiency

#4.完成率
def calculate_exception(df):
    df_exception = df[["Account", "State"]]
    df_exception = df_exception.groupby("Account").count()
    df_exception.rename(columns={"State": "job_count"}, inplace=True)
    df_exception = df_exception.reset_index()

    df_exception2 = df[["Account", "State"]]
    df_exception2["State"] = df_exception2["State"].astype(str)
    df_exception2 = df_exception2[df_exception2['State'].isin(["FAILED", "TIMEOUT", "CANCELLED"])]
    df_exception2 = df_exception2.groupby("Account").count()
    df_exception2.rename(columns={"State": "exception_count"}, inplace=True)
    df_exception2 = df_exception2.reset_index()

    user_exception_all = df_exception.merge(df_exception2, on="Account", how='left')
    user_exception_all.fillna(0,inplace=True)
    user_exception_all["percentage_exception"] = 100*(1 - user_exception_all["exception_count"]/user_exception_all["job_count"])
    user_exception_all.set_index("Account", inplace=True)
    user_exception_all = user_exception_all.drop(['job_count', 'exception_count'], axis=1)
    return user_exception_all

#5.作业规模
def calculate_job_ncore(df):
    user_job_ncore = df[['JobID', 'Account', 'NCPUS']] # , 'ngpus'
    user_job_ncore["job_ncore"] = user_job_ncore['NCPUS'] # +user_job_ncore['ngpus']
    user_job_ncore = user_job_ncore[['Account', 'job_ncore']]
    user_job_ncore = user_job_ncore.groupby(['Account']).agg({"job_ncore":"mean"})
    user_job_ncore = user_job_ncore.reset_index()
    user_job_ncore.set_index("Account", inplace=True)
    return user_job_ncore

#输出文件
def export_result(dataframes, date_new):
    result = pd.concat(dataframes, axis=1)

    df_acct=pd.read_excel(data_folder + "info/account_list.xlsx")
    df_acct = df_acct[['account_name','department', 'principal_name']]
    df_acct.set_index("account_name", inplace=True)

    result = pd.concat([result,df_acct], axis=1)
    result = result.fillna(0)
    result["date"] = date_new
    result['account'] = result.index 
    result = result.reset_index()

    result.to_csv(data_folder + date_new + "/metrics_user.csv", index=True)


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
        file_name = folder_name + "/jobs_end.csv"
        if not os.path.isfile(file_name):
            print(f"错误：文件 '{file_name}' 不存在。")
            sys.exit(1)
        file_name = folder_name + "/cpu_efficiency.csv"
        if not os.path.isfile(file_name):
            print(f"错误：文件 '{file_name}' 不存在。")
            sys.exit(1)
        file_name = folder_name + "/memory_efficiency.csv"
        if not os.path.isfile(file_name):
            print(f"错误：文件 '{file_name}' 不存在。")
            sys.exit(1)

        df = pd.read_csv(data_folder + date + "/jobs_end.csv")
        job_size_account = calculate_job_size(df)
        cpu_efficiency_account = calculate_cpu_efficiency(df, date)
        memory_efficiency_account = calculate_memory_efficiency(df, date)
        exception_account = calculate_exception(df)
        job_ncore_account = calculate_job_ncore(df)
        dataframes = [job_size_account, cpu_efficiency_account, memory_efficiency_account, exception_account, job_ncore_account]
        export_result(dataframes, date)