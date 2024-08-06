#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import
import os
import sys
import csv
from scipy.stats import skew
import pandas as pd
import csv
import warnings
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rc("font",family='FangSong')
warnings.filterwarnings("ignore")
plt.rcParams['font.size'] = 14

columns = ['job_size', 'cpu_efficiency', 'memory_efficiency', 'percentage_exception', 'job_ncore']
names = ['作业总机时数', '平均CPU利用率', '平均内存利用率', '作业完成率', '平均作业规模']
quantiles = [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
colors = ['r', 'pink', 'orange', 'g', 'b', 'purple']
score_columns = ["score_job", "score_cpu_efficiency", "score_memory_efficiency", "score_exception", "score_ncore"]

data_folder = "../data/" # 数据文件路径

# 确定执行计算的日期
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

# 计算得分
ref_df = pd.read_csv(data_folder + "info/references.csv")
print(ref_df.loc[0, "if_log"])

for i in range(1,len(dates)):
    date_new = dates[i]
    df = pd.read_csv(data_folder + date_new + "/metrics_user.csv")

    for c in range(0,5):
        the_column = columns[c]
        the_log_column = "log_" + the_column
        the_score_column = score_columns[c]
        if ref_df.loc[c, "if_log"]:
            #df[the_log_column] = np.log10(1 + df[the_column])
            #df[the_score_column] = df[the_log_column]/ref_df.loc[c, "references"]*100
            df[the_score_column] = (np.log10(1 + df[the_column]))/ref_df.loc[c, "references"]*100
        else:
            df[the_score_column] = df[the_column]/ref_df.loc[c, "references"]*100
        df.loc[df[the_score_column] > 100, the_score_column] = 100

    # df["score_final"] = df["score_job"] * ref_df.loc[0, "final_weight"] +  df["score_cpu_efficiency"] * ref_df.loc[1, "final_weight"]
    # + df["score_memory_efficiency"] * ref_df.loc[2, "final_weight"] + df["score_exception"] * ref_df.loc[3, "final_weight"] 
    # + df["score_ncore"] * ref_df.loc[4, "final_weight"]

    df["score_final"] = (df["score_job"]** ref_df.loc[0, "final_weight"]) * (df["score_cpu_efficiency"]**ref_df.loc[1, "final_weight"]) * (df["score_memory_efficiency"]**ref_df.loc[2, "final_weight"]) * (df["score_exception"]**ref_df.loc[3, "final_weight"]) * (df["score_ncore"]**ref_df.loc[4, "final_weight"])

    df = df.sort_values("score_final",ascending=False)
    df['rank'] = df['score_final'].rank(method='min', ascending=False)
    df = df.reset_index()
    df = df.drop(['Unnamed: 0', 'index'], axis=1)
    
    active_account_num = (df['score_final'] != 0).sum()
    print("active number: ", active_account_num)
    df['percentage'] = df['rank']/active_account_num
    df['level'] = df.apply(lambda row: '中' if row['score_final'] != 0 else '不活跃', axis=1)
    df['level'] = df.apply(lambda row: '良' if row['percentage'] <= 0.25 else row['level'], axis=1)
    df['level'] = df.apply(lambda row: '优' if row['percentage'] <= 0.1 else row['level'], axis=1)

    df.to_csv(data_folder + date_new + "/scores_user.csv", index=True)
    
    print(date_new + "，指数前五用户: "
            + df.loc[0,"department"] + df.loc[0,"principal_name"] + "、" 
            + df.loc[1,"department"] + df.loc[1,"principal_name"] + "、" 
            + df.loc[2,"department"] + df.loc[2,"principal_name"] + "、" 
            + df.loc[3,"department"] + df.loc[3,"principal_name"] + "、" 
            + df.loc[4,"department"] + df.loc[4,"principal_name"])