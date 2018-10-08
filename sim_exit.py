# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : sim_exit.py
  Release  : 1
  Date     : 2018-07-09
 
  Description : HTTP/2 simulator exit module
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import os
import sys
from child import *
from peer import h2_peer
sys.path.insert(0, './util')

def exit_handler():
    peer = h2_peer.getinstance()
    peer.close_peer()
    os.system('stty echo')

    ch = child.getinstance()
    if ch.is_child == False:
        for pid in ch.pid_list:
            os.system("kill -9 %d" % (pid))
            os.system("kill -9 %d" % (pid))

    sleep(0.15)
    quit()

