#!/usr/bin/env bash

# PYTHON=python3.11
PYTHON=pypy3.10
DATA="DATA/small"
RESULTS="RESULTS/solve-pypy3.10_2024-05-08_khai"
mkdir -p $RESULTS
FAILED=""
TIMELIM=3600
INF=inf

# for N in 1 2 3 4 $INF; do
#     echo
#     echo "N=$N"
#     echo
#     for sz in 10 20 30 40 50; do
#         # for r in `seq -f "%02g" 1 50`; do
#         for r in `seq -f "%02g" 1 2 50`; do  # odd numbers on khm
#         # for r in `seq -f "%02g" 2 2 50`; do  # even numbers on khn
#             idx="${sz}_${r}"
#             inst="$DATA/${idx}.input.gz"
#             outf="$RESULTS/solve_${N}_${idx}.txt"
#  
#             if [ -f $outf ]; then
#                 echo "File $outf exists, not running anew"
#             else
#                 if printf '%s\0' "$FAILED" | grep -aF -- "$idx"; then
#                     echo "File $inst in black list, not solving for deeper recursion"
#                 else
#                     S="$(date +%s)"  # timestamp in seconds
#                     echo -n -e "solving $inst\t$N\t"
#                     $PYTHON -u cpu_solve.py $inst $N $TIMELIM | tee $outf | tail -1
#                     T="$(($(date +%s)-$S))"
#                     if [ $T -gt $TIMELIM ]; then
#                         echo "took longer than 3600s, adding $idx to the blacklist"
#                         FAILED="$FAILED $idx"
#                     fi
#                 fi
#             fi
#         done
#     done
# done
