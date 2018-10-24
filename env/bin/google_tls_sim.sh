#!/bin/bash

#HTTP/2 Simulator Launcher

# -- Parameters --
SIM_IDX_=1
NUM_PROC=0
CONF_DIR=./cfg
SIM_NAME=google
DATA_CFG=udr_data.cfg
PEER_CFG=google_call_tls.cfg
cd ../
source $CONF_DIR/.env/run.env
$PYPY2 $TARGET $SIM_IDX_ $SIM_NAME $CONF_DIR/$PEER_CFG $CONF_DIR/$DATA_CFG $NUM_PROC
#                ^          ^                   ^                  ^        ^
#                |          |                   |                  |        |
#                |          |                   |                  |         `---> 5: Num of child instance, 0=Not fork child process
#                |          |                   |                   `------------> 4: Data configure
#                |          |                   `--------------------------------> 3: Peer configure
#                |           `---------------------------------------------------> 2: SIM name
#                 `--------------------------------------------------------------> 1: LOG Index
#
# -- End of script --
