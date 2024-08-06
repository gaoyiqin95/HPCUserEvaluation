#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import
import pandas as pd
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

# 计算得分

ref_cluster_df = pd.read_csv(data_folder + "cluster/references_cluster.csv")

df_cluster = pd.read_csv(data_folder + "cluster/metrics_cluster.csv")
for c in range(0,5):
    the_column = columns[c]
    the_log_column = "log_" + the_column
    the_score_column = score_columns[c]
    if ref_cluster_df.loc[c, "if_log_cluster"]:
        df_cluster[the_score_column] = (np.log10(1 + df_cluster[the_column]))/ref_cluster_df.loc[c, "references_cluster"]*100
    else:
        df_cluster[the_score_column] = df_cluster[the_column]/ref_cluster_df.loc[c, "references_cluster"]*100
    df_cluster.loc[df_cluster[the_score_column] > 100, the_score_column] = 100

df_cluster["score_final"] = (df_cluster["score_job"]** ref_cluster_df.loc[0, "final_weight_cluster"]) * (df_cluster["score_cpu_efficiency"]**ref_cluster_df.loc[1, "final_weight_cluster"]) * (df_cluster["score_memory_efficiency"]**ref_cluster_df.loc[2, "final_weight_cluster"]) * (df_cluster["score_exception"]**ref_cluster_df.loc[3, "final_weight_cluster"]) * (df_cluster["score_ncore"]**ref_cluster_df.loc[4, "final_weight_cluster"])

df_cluster.to_csv(data_folder + "cluster/scores_cluster.csv", index=False)


score_final = df_cluster.iloc[-1]["score_final"]
score_old = df_cluster.iloc[-2]["score_final"]
compare = score_final-score_old

if compare >= 0:
    text = "本周集群整体水平指数为" + str(round(score_final,1)) + "，相比上周提升了" + str(round(compare,1)) + "。"
else:
    compare = -1 * compare
    text = "本周集群整体水平指数为" + str(round(score_final,1)) + "，相比上周下降了" + str(round(compare,1)) + "。"
print(text)