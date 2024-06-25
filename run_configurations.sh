#!/usr/bin/env bash

PYTHON=pypy3.10
RESULTS="RESULTS"
FAILED=""
TIMELIM=3600
INF=999999
NVERT=3

$PYTHON cpu_vs_nedges.py $NVERT $TIMELIM > $RESULTS/configurations_pypy3.10_2024-05-08_khn.csv
$PYTHON mk_plot_configurations.py $RESULTS/configurations_pypy3.10_2024-05-08_khn.csv cpu_graphs.pdf  # produces PDF