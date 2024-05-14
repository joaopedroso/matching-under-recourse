#!/usr/bin/env bash

# PYTHON=python3.11
PYTHON=pypy3.10
DATA="DATA/small"
RESULTS="RESULTS/greedy-k_pypy3.10_2024-05-10_khn"
mkdir -p $RESULTS
FAILED=""
TIMELIM=3600
INF=999999

#for N in 0 1 2 3 $INF; do
for N in $INF; do
   echo
   echo "N=$N"
   echo
   for sz in 10 20 30 40 50; do
        for r in `seq -f "%02g" 1 50`; do
           idx="${sz}_${r}"
           inst="$DATA/${idx}.input.gz"
           outf="$RESULTS/greedy-k_${N}_${idx}.txt"

           if [ -f $outf ]; then
               echo "File $outf exists, not running anew"
           else
               if printf '%s\0' "$FAILED" | grep -aF -- "$idx"; then
                   echo "File $inst in black list, not solving for deeper recursion"
                        touch $outf
               else
                   T="$(date +%s)"  # timestamp in seconds
                   echo -n -e "greedy-k $inst\t$N\t"
                   $PYTHON -u cpu_greedy_k.py $inst $N $TIMELIM | tee $outf | tail -1
                   T="$(($(date +%s)-$T))"
                   if [ $T -gt $TIMELIM ]; then
                       echo "took longer than $TIMELIM s, adding $idx to the blacklist"
                       FAILED="$FAILED $idx"
                   fi
               fi
           fi
       done
   done
done

#DATA="DATA/DelormeInstances"
#for N in 0 1 2 3 $INF; do
#    echo
#    echo "N=$N"
#    echo
#    # for sz in 50 100; do
#    for sz in 50; do
#        for r in `seq -f "%g" 0 29`; do
#            idx="${sz}_${r}"
#            inst="$DATA/DelormeInstances_${idx}.input"
#            outf="$RESULTS/greedy-k_delorme_${N}_${idx}.txt"
#
#            if [ -f $outf ]; then
#                echo "File $outf exists, not running anew"
#            else
#                if printf '%s\0' "$FAILED" | grep -aF -- "$idx"; then
#                    echo "File $inst in black list, not solving for deeper recursion"
#                else
#                    S="$(date +%s)"  # timestamp in seconds
#                    echo -n -e "solving $inst\t$N\t"
#                    $PYTHON -u cpu_greedy_k.py $inst $N $TIMELIM | tee $outf | tail -1
#                    T="$(($(date +%s)-$S))"
#                    if [ $T -gt $TIMELIM ]; then
#                        echo "took longer than $TIMELIM s, adding $idx to the blacklist"
#                        FAILED="$FAILED $idx"
#                    fi
#                fi
#            fi
#        done
#    done
#done
