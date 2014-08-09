#!/bin/bash -x

P=/Users/admin/Documents/Programming/anaconda/anaconda/bin/python

cd marketsworld_martingale
export PYTHONPATH=.:$PYTHONPATH

# LIVE
$P ./main.py --username schemelab@gmail.com --password RLDrld111 --seed-bet 5

# DEMO
#python ./bin/mw_marty.py --username metaperl@gmail.com --password Metaperl1 --sessions 1 --max-hours 5 --seed-bet 1.0 --step-profit 1
