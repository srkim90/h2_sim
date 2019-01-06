# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : peer.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : HTTP/2 peer module
 
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

sys.path.insert(0, './util')
sys.path.insert(0, './h2_core')

import random
from abc import *
from time import sleep
from log import *
from h2_base import *
from singleton import *
from h2_trace import *
from config import cfgConnection

class h2_peer(singleton_instance):
    __instance      = None
    rr_index        = 0
    h2_peer_list    = []
    bind_port_list  = []

    def __init__(self, cfg):
        self.cfg = cfg
        sim_config = cfgConnection.getinstance()
        self.imsi_prefix, self.start_sub, self.max_sub, self.tps, self.max_stream_id, nConn, is_trace = sim_config.getTpsCfg()

    def create_peer(self):
        peer_list    = self.cfg.getPeerCfgList()
        local_list   = self.cfg.getLocalCfgList()
        setting_list = self.cfg.getInitalSettingDict()

        h2_base.set_inital_setting_list(setting_list)

        serverCert, serverKey, clientCerts, clientKey = self.cfg.getSSLCfg()

        for local_cfg in local_list:
            l_ip            = local_cfg[0]
            l_service_port  = int(local_cfg[1])
            l_notify_port   = int(local_cfg[2])
            l_transport     = True if local_cfg[3] == '1' else False
            l_conn_type     = int(local_cfg[4])

            for peer_cfg in peer_list:
                p_ip            = peer_cfg[0]
                p_service_port  = int(peer_cfg[1])
                p_notify_port   = int(peer_cfg[2])
                p_transport     = True if peer_cfg[3] == '1' else False
                p_conn_type     = int(peer_cfg[4])

                if p_transport != l_transport:
                    continue

                if p_transport == 1:
                    isTls = True
                else:
                    isTls = False


                h2_peer = h2_base(l_ip, p_ip, l_service_port, l_notify_port, p_service_port, p_notify_port, l_conn_type,
                                 isTls, serverCert, serverKey, clientCerts, clientKey, max_stream_id=self.max_stream_id )
                h2_peer.h2_set_print_method(PRINT)
                h2_peer.h2_set_trace_method(h2_trace.getinstance().h2_print_trase)

                self.h2_peer_list.append(h2_peer)

    def close_peer(self):
        n_session_cnt = 0
        for h2_peer in self.h2_peer_list:
            h2_peer.isClose=True

        PRINT ("")
        for i in range (100):
            #print ("." ,end='', flush=True)
            sleep(0.025)
            n_session_cnt = 0
            for h2_peer in self.h2_peer_list:
                n_session_cnt += h2_peer.h2_get_conn_cnt()
            if n_session_cnt == 0:
                break

        PRINT ("")
        if n_session_cnt != 0:
            PRINT ("Remain HTTP/2 Session : %d, Try Force Quit" % (n_session_cnt))

        sleep(0.1)

    def start_peer(self, invoke_callback, resume_callback):
        for h2_peer in self.h2_peer_list:
            s_port_used = self._is_port_aleady_bind(h2_peer.LocalServicePort)
            n_port_used = self._is_port_aleady_bind(h2_peer.LocalNotifyPort)
            if s_port_used == False and n_port_used == False:
                h2_peer.h2OpenServer(invoke_callback)
                self.bind_port_list.append(s_port_used)
                if s_port_used != n_port_used:
                    self.bind_port_list.append(n_port_used)

            h2_peer.h2OpenClient(resume_callback, nConnection = 1)

    def change_connection_count(self, resume_callback, conn_type, count):
        for h2_peer in self.h2_peer_list:
            h2_peer.h2SetClientCount(resume_callback, conn_type, count)

    def send_request(self, method, uri, json_object, n_request=1):
        return self._send_message(h2_conn_type.CONNTYPE_CLIENT_REQUEST, method, uri, json_object, n_request=n_request)

    def send_notify(self, method, uri, json_object, n_request=1):
        return self._send_message(h2_conn_type.CONNTYPE_CLIENT_NOTIFY, method, uri, json_object, n_request=n_request)

    def h2_get_connection_list(self):
        target_peer_list = []
        for peer in self.h2_peer_list:
            target_peer_list.append(peer)

        return target_peer_list

    def get_connection_count(self, request_type=0):
        if request_type == 0:
            request_type = h2_conn_type.CONNTYPE_CLIENT_REQUEST
        else:
            request_type = h2_conn_type.CONNTYPE_CLIENT_NOTIFY

        nErr = 0
        for peer in self.h2_peer_list:
            nErr += peer.h2_get_conn_cnt(request_type)

        return nErr

    def _send_message(self, request_type, method, uri, json_object, n_request=1):
        target_peer_list = []
        for peer in self.h2_peer_list:
            #PRINT(peer.h2_get_conn_cnt(request_type))
            if peer.h2_get_conn_cnt(request_type) > 0:
               target_peer_list.append(peer)
        h2_peer_cnt = len(target_peer_list)
        
        if h2_peer_cnt == 0:
            #PRINT ("Err. count of alive peer is 0")
            return False

        '''
        MAX_RANGE = 50
        #print("h2_peer_cnt:%d" % h2_peer_cnt)
        while True:
            self.rr_index += 1
            seleted_idx      = (self.rr_index - 1) % h2_peer_cnt
            neo_seleted_idx  = seleted_idx if seleted_idx < MAX_RANGE/2 else MAX_RANGE/2

            n_rand = random.randrange(1,MAX_RANGE)

            if n_rand < neo_seleted_idx:
                continue
            else:
                break
        '''
        seleted_idx    = (self.rr_index - 1) % h2_peer_cnt
        self.rr_index += 1

        peer = target_peer_list[ seleted_idx ]

        if n_request == 1:
            return peer.h2_send_request(request_type, method, uri, json_object)
        else:
            return peer.h2_send_request_N(request_type, method, uri, json_object, n_request=n_request)

    def _is_port_aleady_bind(self, port):
        for used_port in self.bind_port_list:
            if used_port == port:
                return True
        return False
