#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import
import sys
import os
import csv
from scipy.stats import skew
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.rc("font",family='FangSong')
plt.rcParams['font.size'] = 14
import warnings
warnings.filterwarnings("ignore")

columns = ['job_size', 'cpu_efficiency', 'memory_efficiency', 'percentage_exception', 'job_ncore']
names = ['作业总机时数', '平均CPU利用率', '平均内存利用率', '作业完成率', '平均作业规模']
quantiles = [0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
colors = ['r', 'pink', 'orange', 'g', 'b', 'purple']
score_columns = ["score_job", "score_cpu_efficiency", "score_memory_efficiency", "score_exception", "score_ncore"]

data_folder = "../data/" # 数据文件路径
fig_folder = "../figures" # 图片文件路径

print("--------------导入参考数据的日期--------------")
print("")
dates = []
demo = False
if len(sys.argv) == 2:
    print(sys.argv)
    dates = [0, sys.argv[1]]
    if sys.argv[1] == "demo":
        demo = True
else:
    csv_filename = data_folder + 'info/dates_all_ref.csv'
    dates = []
    with open(csv_filename, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            dates.append(row[0])
print(dates)
print("")

# 导入指标数据
final_result = pd.DataFrame()
for i in range(1,len(dates)):
    date_new = dates[i]
    tmp = pd.read_csv(data_folder + date_new + "/metrics_user.csv")
    final_result = pd.concat([final_result,tmp])
del final_result['Unnamed: 0']

# 将每个指标的数据转换为一个列表
all_data = []
for i in range(0,5):
    the_column = columns[i]
    the_name = names[i]
    the_title = '用户' + the_name + '统计'
    all_data.append(final_result[the_column])

# 对于每个指标，输出数据分布图
print("--------------计算数据分布--------------")
print("")
for i in range(0,5):
    the_column = columns[i]
    the_name = names[i]
    file_name = "1." + str(i+1) + "." + the_name + '.png'
    the_title = '用户' + the_name + '统计'
    column_data = all_data[i]
    column_data = column_data[column_data != 0]
    plt.hist(column_data, bins=50, log=True, color='deepskyblue', edgecolor='grey')
    print(the_name)
    for j in range(0,6):
        the_quantile = column_data.quantile(quantiles[j])
        print_msg = str(quantiles[j]) + ": " + str(the_quantile)
        print(print_msg)
        plt.axvline(x=the_quantile, color=colors[j], linestyle='--')
        plt.text(x=the_quantile, y=1000, s=quantiles[j], color=colors[j], rotation=90)
    print("")
    plt.xlabel(the_name)
    plt.ylabel('频次')
    if demo == False:
        plt.savefig(os.path.join(fig_folder, file_name))
    plt.close()

# 计算指标数据分布偏度，如果偏度大于1，则使用log
print("--------------偏度计算，是否需要对数化--------------")
print("")
if_log = []
for i in range(0,5):
    the_column = columns[i]
    the_name = names[i]
    the_title = '用户' + the_name + '统计'
    column_data = all_data[i]
    column_data = column_data[column_data != 0]
    bias = skew(column_data)
    print(the_name + ": " + str(bias))
    if bias > 1:
        if_log.append(True)
    else:
        if_log.append(False)
print(if_log)
print("")

# 进行log化后的数据分布情况
print("--------------对数化后的数据分布情况--------------")
print("")
for i in range(0,5):
    the_column = columns[i]
    the_name = names[i]
    file_name = "2." + str(i+1) + "." + the_name + '.png'
    the_title = '用户' + the_name + '统计'
    column_data = all_data[i]
    column_data = column_data[column_data != 0]
    if if_log[i]:
        column_data = np.log10(1 + column_data)
    plt.hist(column_data, bins=50, log=True, color='deepskyblue', edgecolor='grey')
    print(the_name)
    for j in range(0,6):
        the_quantile = column_data.quantile(quantiles[j])
        print_msg = str(quantiles[j]) + ": " + str(the_quantile)
        print(print_msg)
        plt.axvline(x=the_quantile, color=colors[j], linestyle='--')
        plt.text(x=the_quantile, y=100, s=quantiles[j], color=colors[j], rotation=90)
    print("")
    if if_log[i]:
        the_name = "log10(" + the_name + " + 1)"
    plt.xlabel(the_name)
    plt.ylabel('频次')
    if demo == False:
        plt.savefig(os.path.join(fig_folder, file_name))
    plt.close()

# 参考值计算
print("--------------参考值计算--------------")
print("")
references = []
for i in range(0,5):
    the_name = names[i]
    column_data = all_data[i]
    column_data = column_data[column_data != 0]
    if if_log[i]:
        column_data = np.log10(1 + column_data)
    the_max = max(column_data)
    q3 = column_data.quantile(0.75)
    q1 = column_data.quantile(0.25)
    iq2 = q3 - q1
    bound = q3 + 1.5 * iq2
    print(the_name)
    print("max = ", str(the_max))
    print("1.5 * iq2 = ", str(bound))
    if the_max > bound:
        print("max > 1.5 * iq2")
        print("参考值取1.5 * iq2：" + str(bound))
        references.append(bound)
    else:
        print("max < 1.5* iq2")
        print("参考值取max：" + str(the_max))
        references.append(the_max)
    print("")
print("")
print("参考值：")
print(references)
print("")


# 熵权法赋权
print("--------------熵权法赋权--------------")
print("")
all_data_normalized = []
p = []
d = []
for i in range(0,5):
    # 数据标准化
    the_column = columns[i]
    the_name = names[i]
    column_data = all_data[i]
    column_data = column_data[column_data != 0]
    if if_log[i]:
        column_data = np.log10(1 + column_data)
    the_max = max(column_data)
    the_min = min(column_data)
    column_data = (column_data - the_min) / (the_max - the_min)
    all_data_normalized.append(column_data)

    # 计算每个样本在该指标下的比重
    the_sum = sum(column_data)
    column_p = column_data / the_sum
    p.append(column_p)

    # 计算指标的信息熵和熵冗余度
    k = 1.0 / np.log(len(column_p))
    entropy = -k * (column_p * np.log(column_p)).sum(axis=0, skipna=True) # 信息熵
    d.append(1 - entropy) # 信息熵冗余度

sum_weight = sum(d)
# 计算指标权重
weight = []
for i in range(0,5):
    weight.append(d[i]/sum_weight)
print("熵权法指标权重")
print(names)
print(weight)
print("")



# 层次分析法赋权
print("--------------层次分析法赋权--------------")
print("")

# 创建指标相对重要性的矩阵
df = pd.DataFrame()
data = [#机时数    CPU利用率    内存利用率  作业完成度  作业并行度
        [1,         1/2,        2,          3,      3],# 机时数
        [2,         1,          4,          5,      5],# CPU利用率
        [1/2,       1/4,        1,          1,      1],# 内存利用率
        [1/3,       1/5,        1,          1,      1],# 作业完成度
        [1/3,       1/5,        1,          1,      1] # 作业并行度
]
df = pd.DataFrame(data)

# 计算每列的总和
column_sums = df.sum(axis=0)

# 按列求每个元素在该列中的占比
df_proportions = df.div(column_sums, axis=1)

# 计算每行的平均值
weight2 = df_proportions.mean(axis=1)
weight2 = weight2.tolist()
print("层次分析法指标权重")
print(names)
print(weight2)
print("")


# 计算最终权重
print("--------------最终权重--------------")
print("")

subjective = 0.5
objective = 1 - subjective

final_weight = []
for i in range(0,5):
    print(names[i])
    print("客观赋权：")
    print(weight[i])
    print("主观赋权：")
    print(weight2[i])
    the_weight = objective * weight[i] + subjective * weight2[i]
    print("最终权重：")
    print(the_weight)
    print("")
    final_weight.append(the_weight)
print(names)
print(final_weight)
print("")


# 数据输出
print("--------------数据归纳--------------")
print("")

ref_df = {
    'if_log': if_log,
    'references': references,
    'final_weight': final_weight
}

# 使用字典创建DataFrame
ref_df = pd.DataFrame(ref_df)
if len(sys.argv) == 2:
    ref_df.to_csv(data_folder + "info/references_" + sys.argv[1] + ".csv", index=False)
else:
    ref_df.to_csv(data_folder + "info/references.csv", index=False)
print(ref_df)