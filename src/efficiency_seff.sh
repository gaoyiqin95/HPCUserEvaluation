#!/bin/bash
set=$1
date=$2

job="../data/$date/job_id.csv"

if [ "${set}" = "cpu" ];then
  text="CPU Efficiency"
  effic="../data/$date/cpu_efficiency.csv"
else
  text="Memory Efficiency"
  effic="../data/$date/memory_efficiency.csv"
fi

cat "$job" | while read -r line; do
  jobid="$line"
  efficiency=`seff $jobid | grep "$text" | cut -d ' ' -f3`
  echo "$efficiency, $jobid" >> $effic
  # echo "$jobid, $effic, $text"
done