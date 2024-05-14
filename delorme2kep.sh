#!/usr/bin/env bash

# PYTHON=python3.11
PYTHON=pypy3.10
DATA="DATA/DelormeInstances"


for r in `seq -f "%g" 0 29`; do
    inst=$DATA/DelormeInstances_50_$r.txt
    echo "making kep format file for delorme instance $inst"
    $PYTHON -u delorme2kep.py $inst
done

for r in `seq -f "%g" 0 29`; do
    inst=$DATA/DelormeInstances_100_$r.txt
    echo "making kep format file for delorme instance $inst"
    $PYTHON -u delorme2kep.py $inst
done
