#!/usr/bin/env bash

# PYTHON=python3.11
PYTHON=pypy3.10
DATA="DATA/small"
RESULTS="RESULTS/greedy-pypy3.10_2024-04-19"
mkdir -p $RESULTS
TIMELIM=3600

for N in inf; do
    echo
    echo "N=$N"
    echo
    for sz in 10 20 30 40 50; do
        for r in `seq -f "%02g" 1 50`; do
            inst="$DATA/${sz}_${r}.input.gz"
            outf="$RESULTS/solve_${sz}_${r}.txt"

            if [ -f $outf ]; then
                echo "File $outf exists, not running anew"
            else
                echo -n -e "$inst\t$N\t"
                $PYTHON -u cpu_greedy.py $inst $N $TIMELIM | tee $outf | tail -1
            fi
        done
    done
done
