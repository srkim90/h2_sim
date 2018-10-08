# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : proc_pool.py
  Release  : 1
  Date     : 2018-09-12
 
  Description : HTTP/2 multiprocess utility module
 
  Notes :
  ===================
  History
  ===================
  2018/09/12  created by Kim, Seongrae
'''

import threading
from log import *
from singleton import *
from multiprocessing.pool import Pool

class ProcPool(singleton_instance):
    def __init__(self, n_proc):
        self.working     = 0
        self.local_lock  = threading.Semaphore(n_proc)
        self.proc_pool   = Pool(processes=n_proc)

    def do_async_work(self, fn_work, param_list=None):
        if param_list == None:
            param_list = []

        self.local_lock.acquire()
        self.working += 1
        hProc = self.proc_pool.apply_async(fn_work, param_list)
        #print("%s" % param_list[0])
        ret = hProc.get()
        self.working -= 1
        self.local_lock.release()

        return ret


def init_proc_pool(n_proc=4):
    ProcPool.instance(n_proc)
    
def do_async_work(fn_work, param_list=None):
    e = ProcPool.getinstance()
    return e.do_async_work(fn_work,param_list)

