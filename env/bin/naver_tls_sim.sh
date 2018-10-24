#!/bin/bash

#HTTP/2 Simulator Launcher

# -- Parameters --
SIM_IDX_=1
NUM_PROC=0
CONF_DIR=./cfg
SIM_NAME=naver
DATA_CFG=data/udr_data.cfg
PEER_CFG=peer/naver_call_tls.cfg
cd ../
source ~/.bash_profile
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
