# 超算用户作业水平指数评测工具

## 数据采集与清理

- 采集指定日期的作业数据

```
sacct --allusers -S [start_date] -E [end_date] -o 'JobID%16,Account%16,Partition%16,NCPUS%16,CPUTime%16,State%32' > [end_date]/jobs.csv
```

- 运行预处理文件

    - 仅处理一周的数据
    ```
    python3 data_preprocess.py [date]
    ```

    - 处理所有日期的数据

    ```
    python3 data_preprocess.py
    ```

- 运行slurm作业（注意：该步骤必须在部署了Slurm的集群上运行）

```
sbatch cpu_seff.slurm
sbatch memory_seff.slurm
```

- 生成指标绝对值数据

    - 仅处理一周的数据
    ```
    python3 output_metrics.py [date]
    ```

    - 处理所有日期的数据
    ```
    python3 output_metrics.py
    ```

## 参考值与权重计算

```
python3 calculate_ref_weight.py
```

## 指数计算与分析

- 仅处理一周的数据
```
python3 output_score.py [date]
```

- 处理所有日期的数据
```
python3 output_score.py
```

## 集群整体指数评测

- 生成指标绝对值数据

```
python3 cluster_output_metrics.py
```

- 参考值与权重计算

```
python3 cluster_calculate_ref_weight.py
```

- 指数计算与分析

```
python3 cluster_output_score.py
```