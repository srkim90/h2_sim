# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : interwork.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : HTTP/2 interworking module
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import os
import sys
import json
import threading
from peer import h2_peer
from time import sleep
sys.path.insert(0, './util')
from log import *
from singleton import *
from dispatch import *
from expect import *

class h2_interwork(singleton_instance):
    isClose       = False
    invoke_count  = 0
    resume_count  = 0
    notify_count  = 0
    request_count = 0
    stat_lock     = threading.Semaphore(1) 

    def __init__(self):
        init_dispatch()
        self.hThread        = threading.Thread(target=self._tps_proc)
        self.hThread.daemon = True
        self.hThread.start()

    def _tps_proc(self):
        old_invoke_count    = 0
        old_resume_count    = 0
        old_notify_count    = 0
        old_request_count   = 0
        while self.isClose == False:
            sleep(1)
            LOG(LOG_CRT, "TPS(invoke=%d, resume=%d, notify=%d, request=%d) TOTAL=(invoke=%d, resume=%d, notify=%d, request=%d)" %
                (self.invoke_count  - old_invoke_count,
                 self.resume_count  - old_resume_count,
                 self.notify_count  - old_notify_count,
                 self.request_count - old_request_count,
                 self.invoke_count ,
                 self.resume_count ,
                 self.notify_count ,
                 self.request_count
                ))

            old_invoke_count    = self.invoke_count
            old_resume_count    = self.resume_count
            old_notify_count    = self.notify_count
            old_request_count   = self.request_count

    def h2_invoke_callback(self, req_method, req_path, req_data):
        LOG (LOG_DBG, "method : %s" % req_method)
        LOG (LOG_DBG, "path   : %s" % req_path)
        LOG (LOG_DBG, "data   : %s" % req_data)

        stat = dispatch_util.getinstance()
        stat.set_api_stat(req_method, req_path, None, H2_STAT_TYPE_RECV_REQUEST)

        e = dispatch_util.getinstance()

        resultCode, resultData = e.do_request_dispatch(req_method, req_path, req_data)

        self.stat_lock.acquire()
        self.invoke_count += 1
        self.stat_lock.release()

        stat.set_api_stat(req_method, req_path, resultCode, H2_STAT_TYPE_SEND_ANSWER)

        return resultCode, resultData


    def h2_resume_callback(self, req_method, req_path, req_data, asw_code, asw_data):
        LOG (LOG_DBG, "req_method : %s" % req_method)
        LOG (LOG_DBG, "req_path   : %s" % req_path)
        LOG (LOG_DBG, "req_data   : %s" % req_data)
        LOG (LOG_DBG, "asw_code   : %d" % asw_code)
        LOG (LOG_DBG, "asw_data   : %s" % asw_data)

        stat = dispatch_util.getinstance()
        stat.set_api_stat(req_method, req_path, asw_code, H2_STAT_TYPE_RECV_ANSWER)

        ep = expect.getinstance()
        ep.on_recv_answer(req_path, req_method, asw_code, asw_data)

        self.stat_lock.acquire()
        self.resume_count += 1
        self.stat_lock.release()

        '''
        # TEST Code
        asw_imsi = asw_data["Subscription-Id"]["Subscription-Id-Data"]
        req_imsi = req_path.split('/')[4]
        #PRINT("asw_imsi=%s, req_imsi=%s" % (asw_imsi, req_imsi))
        if asw_imsi != req_imsi or len(asw_imsi) != 15 or len(asw_imsi) != 15:
            PRINT("ERROR!!..  asw_imsi=%s, req_imsi=%s" % (asw_imsi, req_imsi))
        '''

        return None


    def h2_send_request(self, method, uri, data, n_request=1):
        peer = h2_peer.getinstance()

        b_ret = peer.send_request(method, uri, data, n_request)

        if b_ret != False:
            stat = dispatch_util.getinstance()
            stat.set_api_stat(method, uri, None, H2_STAT_TYPE_SEND_REQUEST)
        else:
            return False

        ep = expect.getinstance()
        ep.on_send_request(uri, method, data)


        self.stat_lock.acquire()
        self.request_count += 1
        self.stat_lock.release()

        return b_ret


    def h2_send_notify(self, method, uri, data):
        peer = h2_peer.getinstance()
        b_ret = peer.send_notify(method, uri, data)

        if b_ret != False:
            stat = dispatch_util.getinstance()
            stat.set_api_stat(method, uri, None, H2_STAT_TYPE_SEND_REQUEST)

        self.stat_lock.acquire()
        self.notify_count += 1
        self.stat_lock.release()

        return b_ret


