# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : main.py
  Release  : 1
  Date     : 2018-07-09
 
  Description : subprocess module
 
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

from mmc import *
from log import *
from peer import h2_peer
from config import *
from interwork import *
from signal_handler import *

import subprocess

from singleton import *

class child(singleton_instance):
    is_child = False
    pid_list = []
    def __init__(self, n_child_proc):
        for i in range (n_child_proc):
            pid = os.fork()
            if pid == 0:
                self.is_child = True
                break
            else:
                self.pid_list.append(pid)
        if self.is_child == False:
            sleep(0.25)


#class child_ipc

