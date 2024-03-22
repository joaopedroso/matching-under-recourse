#!/usr/bin/env bash

PYTHON=python3.11
CPUDB=RESULTS/cpu_greedy_DB.json
if [ -f $CPUDB ]; then
   echo "File $CPUDB exists; using is to avoid repeating long computations"
   cat $CPUDB
else
   echo "File $CPUDB does not exist, creating empty database of long computations"
   echo "{}" > $CPUDB
fi

for N in 0 9999; do
    echo
    echo "N=$N"
    echo
    for sz in 10 20 30 40 50; do
        for r in `seq -f "%02g" 1 50`; do
            inst="DATA/small/${sz}_${r}.input.gz"
            echo -n -e "$inst\t$N\t"
            $PYTHON cpu_greedy.py $inst $N 3600 | tail -1
        done
    done
done
