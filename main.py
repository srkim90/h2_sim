# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : main.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : HTTP/2 simulator main function
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import re
import os
import sys    
import termios
import fcntl
from abc  import *
from time import sleep

sys.path.insert(0, './util')
sys.path.insert(0, './h2_core')

from mmc import *
from log import *
from perf import *
from peer import h2_peer
from h2_trace import *
from child import *
from config import *
from proc_pool import *
from interwork import *
from signal_handler import *

# usage  : python ./main.py [index] [name] [connection-config] [data-config] [count-fork]
#    ex> : python ./main.py 1 TEST ./cfg/peer.cfg ./test.dat 0

def main():
    
    ''' 1. Run Child Process'''
    if len(sys.argv) == 6:
        n_child_proc = int(sys.argv[5])
        child.instance(n_child_proc)
    else:
        child.instance(0)

    ''' 2. Init Log'''
    log_name  = "%s" % (sys.argv[2])
    log_index = int(sys.argv[1])
    sa_initlog(log_name, log_index, is_visible_log = not child.getinstance().is_child)

    ''' 3. Load Config'''
    cfg = loadConfig(sys.argv[3], sys.argv[4])
    printConfig(cfg, None, PRINT2)

    ''' 4. Create PEERs'''
    init_perf()
    #init_proc_pool(n_proc=4)
    h2_trace.instance(TRACE)
    iwf = h2_interwork.instance()
    peer = h2_peer.instance(cfg)
    peer.create_peer()
    peer.start_peer(iwf.h2_invoke_callback, iwf.h2_resume_callback)

    ''' 5. SIGNAL Init'''
    hSignal = signal_handler()

    ''' 6. Apply Configuration '''
    tps_cfg  = cfg.getTpsCfg()
    n_conn   = tps_cfg[5]
    is_trace = tps_cfg[6]
    if n_conn > 1:
        mmc_set_connection_count.run([None, "notify_conn",  n_conn] )
        mmc_set_connection_count.run([None, "request_conn", n_conn]  )
    if is_trace != "ON":
        mmc_log_set.run(["disable"])

    ''' 7. Run MMC'''
    if child.getinstance().is_child == False:
        mmc_run(int(sys.argv[1]), sys.argv[2])
    else:
        while True:
            sleep(1)

main()
