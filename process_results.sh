#!/usr/bin/env bash
# Assemble a summary CSV from per-instance result files produced by
# run_cpu_solve.sh or run_cpu_greedy_k.sh.
#
# Output format (tab-separated, one line per instance per N):
#   instance_path  N  nvert  nedges  expectation  cpu  cache_size
#
# Missing or timed-out instances produce "None" fields.
#
# Usage:
#   TYPE=solve   RESULTS=RESULTS/solve-pypy3.10-<date>-<host>   bash process_results.sh > summary_solve.csv
#   TYPE=greedy-k RESULTS=RESULTS/greedy-k-pypy3.10-<date>-<host> bash process_results.sh > summary_greedy-k.csv
#
# TYPE and RESULTS can also be set by editing the defaults below.

set -euo pipefail

TYPE="${TYPE:-greedy-k}"
RESULTS="${RESULTS:-RESULTS/greedy-k_pypy3.10_<date>_<host>}"
INF=inf

for N in 1 2 3 4 $INF; do
    for sz in 10 20 30 40 50; do
        for r in $(seq -f "%02g" 1 50); do
            idx="${sz}_${r}"
            inst="${idx}.input.gz"
            outf="$RESULTS/${TYPE}_${N}_${idx}.txt"

            if [ -f "$outf" ]; then
                echo -n -e "$inst\t$N\t"
                OUTPUT=$(tail -1 "$outf" | cut -f1-5)
                if [[ $OUTPUT ]]; then
                    echo "$OUTPUT"
                else
                    echo -e "None\tNone\tNone\tNone\tNone"
                fi
            else
                echo "File $outf does NOT exist" >&2
                exit 1
            fi
        done
    done
done
