#!/usr/bin/env bash
# Run exact solver on Delorme instances (Blom et al. format, converted by delorme2kep.sh).
# Reproduces Table 4 of the paper (exact solver columns).
# Instance data: DATA/DelormeInstances/DelormeInstances_<sz>_<r>.input
# Results written to: RESULTS/solve-delorme_<python>_<date>_<host>/solve_delorme_<N>_<sz>_<r>.txt
#
# Note: the original paper results were obtained on a different machine and CPU times
# were scaled to the reference machine used for all other experiments.

# PYTHON=python3.11
PYTHON=pypy3.10
DATA="DATA/DelormeInstances"
RESULTS="RESULTS/solve-delorme_pypy3.10_2024-05-08_khai"
mkdir -p "$RESULTS"
FAILED=""
TIMELIM=36000
INF=inf

for N in 1 2 3 4 $INF; do
    echo
    echo "N=$N"
    echo
    for sz in 50 100; do
        for r in $(seq -f "%g" 0 29); do
            idx="${sz}_${r}"
            inst="$DATA/DelormeInstances_${idx}.input"
            outf="$RESULTS/solve_delorme_${N}_${idx}.txt"

            if [ -f "$outf" ]; then
                echo "File $outf exists, not running anew"
            else
                if printf '%s\0' "$FAILED" | grep -aF -- "$idx"; then
                    echo "File $inst in black list, not solving for deeper recursion"
                else
                    S="$(date +%s)"
                    echo -n -e "solving $inst\t$N\t"
                    $PYTHON -u cpu_solve.py "$inst" $N $TIMELIM | tee "$outf" | tail -1
                    T="$(($(date +%s)-$S))"
                    if [ $T -gt $TIMELIM ]; then
                        echo "took longer than ${TIMELIM}s, adding $idx to the blacklist"
                        FAILED="$FAILED $idx"
                    fi
                fi
            fi
        done
    done
done
