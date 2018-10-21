# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : h2_trace.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : HTTP/2 trace module
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import os
import ssl
import sys
import socket

import pprint
import json
import h2.events
import h2.config
import h2.connection
import threading
import zlib
import select
from enum import Enum
from time import sleep
from h2_TLS import *
from h2_util import *
from log import *
from singleton import *
from multiprocessing import Process
from collections import OrderedDict

line80="--------------------------------------------------------------------------------"
LINE80="================================================================================"

C_END     = "\033[0m"
C_BOLD    = "\033[1m"
C_INVERSE = "\033[7m"
C_ITALIC  = "\033[3m"

C_BLACK  = "\033[30m"
C_RED    = "\033[31m"
C_GREEN  = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE   = "\033[34m"
C_PURPLE = "\033[35m"
C_CYAN   = "\033[36m"
C_WHITE  = "\033[37m"

C_BGBLACK  = "\033[40m"
C_BGRED    = "\033[41m"
C_BGGREEN  = "\033[42m"
C_BGYELLOW = "\033[43m"
C_BGBLUE   = "\033[44m"
C_BGPURPLE = "\033[45m"
C_BGCYAN   = "\033[46m"
C_BGWHITE  = "\033[47m"

TRACE_DIR_SEND  = 0
TRACE_DIR_RECV  = 1

def my_print(s):
    print (s)

class h2_trace(singleton_instance):
    fn_print = my_print

    def __init__(self, fn_print):
        self.log = sa_log.getinstance()
        self.fn_print = fn_print

    def h2_frame_trace(self, direction, frame):

        if self.log.is_trace_log == False:
            return

        data_list    = []
        n_frame_type = frame.type

        if direction == TRACE_DIR_RECV:
            direction = "[%sRECV%s]" % (C_RED, C_END)
        else:
            direction = "[%sSEND%s]" % (C_GREEN, C_END)
         
        if n_frame_type == FRAME_TYPE_DATA:
            return
        elif n_frame_type == FRAME_TYPE_HEADERS:
            return
            #data_list.append("%s" % (line80))
            #if len(frame.flags) > 0:
            #    data_list.append("[flags]")
            #    for flag_at in frame.flags:
            #        data_list.append("  %-18s: %s" % (flag_at, "SET"))
            #data_list.append("%s" % (LINE80))
            #pass
        elif n_frame_type == FRAME_TYPE_PRIORITY:
            return
        elif n_frame_type == FRAME_TYPE_RST_STREAM:
            data_list.append("%s" % (line80))
            data_list.append("%-20s: %s" % ("error_code", frame.error_code))
            data_list.append("%s" % (LINE80))
            pass
        elif n_frame_type == FRAME_TYPE_SETTINGS:
            return
        elif n_frame_type == FRAME_TYPE_PUSH_PROMISE:
            data_list.append("%s" % (line80))
            if len(frame.flags) > 0:
                data_list.append("[flags]")
                for flag_at in frame.flags:
                    data_list.append("  %-18s: %s" % (flag_at, "SET"))
            data_list.append("%-20s: %s" % ("promised_stream_id", frame.promised_stream_id))
            data_list.append("%s" % (LINE80))
            pass
        elif n_frame_type == FRAME_TYPE_PING:
            return
        elif n_frame_type == FRAME_TYPE_GOAWAY:
            data_list.append("%s" % (line80))
            data_list.append("%-20s: %s" % ("last_stream_id", frame.last_stream_id))
            data_list.append("%-20s: %s" % ("error_code", frame.error_code))
            data_list.append("%-20s: %s" % ("additional_data", frame.additional_data))
            data_list.append("%s" % (LINE80))
            pass
        elif n_frame_type == FRAME_TYPE_WINDOW_UPDATE:
            data_list.append("%s" % (line80))
            data_list.append("%-20s: %s" % ("window_increment", frame.window_increment))
            data_list.append("%s" % (LINE80))
            pass
        elif n_frame_type == FRAME_TYPE_CONTINUATION:
            if len(frame.flags) > 0:
                data_list.append("%s" % (line80))
                data_list.append("[flags]")
                for flag_at in frame.flags:
                    data_list.append("  %-18s: %s" % (flag_at, "SET"))
            data_list.append("%s" % (LINE80))
            pass
        else:
            PRINT("Err. Recv unknown frames=%d" % (n_frame_type))
            return
           
        frame_name = h2_frame_type_string(n_frame_type)

        self.fn_print("%s" % LINE80)
        self.fn_print("%s Frame %s (stream_id=%d)" % (direction, frame_name, frame.stream_id))
        if len(data_list) > 0:
            for line in data_list:
                self.fn_print("%s" % line)

    def h2_print_trase(self, event=None, stream_id=None, headers=None, end_stream=None, data=None):

        if self.log.is_trace_log == False:
            return

        if self.fn_print("", check=True) == False:
            return

        if event != None:
            if isinstance(event, h2.events.ResponseReceived):
                self._event_handler_response_received(event)
            elif isinstance(event, h2.events.RequestReceived):
                self._event_handler_request_received(event)
            elif isinstance(event, h2.events.DataReceived):
                self._event_handler_data_received(event)
        elif headers != None:
            self._event_handler_response_sent(stream_id, headers, end_stream)
        elif data != None:
            self._event_handler_data_sent(stream_id, data, end_stream)

    def _event_handler_response_received(self, event):
       self.fn_print("%s" % LINE80)
       self.fn_print("[%sRECV%s] HTTP/2 RESPONSE RECEIVED (stream_id=%d)" % (C_RED, C_END,event.stream_id))
       self.fn_print("%s" % line80)
       #self.fn_print("[FIELD]")
       for h_para in event.headers:
           tag   = h_para[0].decode(encoding="utf-8")
           value = h_para[1].decode(encoding="utf-8")
           self.fn_print("%-20s: %s" % (tag, value))
       self.fn_print("%s" % LINE80)

    def _event_handler_request_received(self, event):
       self.fn_print("%s" % LINE80)
       self.fn_print("[%sRECV%s] HTTP/2 REQUEST RECEIVED (stream_id=%d)" % (C_RED, C_END, event.stream_id))
       self.fn_print("%s" % line80)
       for h_para in event.headers:
           tag   = h_para[0].decode(encoding="utf-8")
           value = h_para[1].decode(encoding="utf-8")
           self.fn_print("%-20s: %s" % (tag, value))
       self.fn_print("%s" % LINE80)

    def _event_handler_data_received(self, event):
        try:
            data = event.data.decode(encoding="utf-8")
        except:
            z_data = zlib.decompress(event.data)
            data = z_data.decode(encoding="utf-8")
 
        try:
            data = data.replace('\\"', '"')
            data = data.replace('\\n', '')
            data = data.replace('\\r', '')
            if data[0] == '"':
                data = data[1:-1]
            if data[-1] == '"':
                data = data[0:-2]

            jObject = json.loads(data, object_pairs_hook=OrderedDict)
            data = json.dumps(jObject, indent=4)
        except:
            pass
            
        self.fn_print("%s" % LINE80)
        self.fn_print("[%sRECV%s] HTTP/2 DATA RECEIVED (stream_id=%d)" % (C_RED, C_END, event.stream_id))
        self.fn_print("%s" % line80)
        s_data = data.split('\n')
        for item in s_data:
            item = h2_string_decoding(item)
            self.fn_print("%s" % (item))
        self.fn_print("%s" % LINE80)

    def _event_handler_response_sent(self, stream_id, headers, end_stream):
       self.fn_print("%s" % LINE80)
       self.fn_print("[%sSEND%s] HTTP/2 RESPONSE SENT (stream_id=%d, end_stream=%s)" % (C_GREEN, C_END, stream_id, end_stream))
       self.fn_print("%s" % line80)
       for h_para in headers:
           tag   = h_para[0]
           value = h_para[1]
           self.fn_print("%-20s: %s" % (tag, value))
       self.fn_print("%s" % LINE80)

    def _event_handler_request_sent(self, stream_id, headers, end_stream):
       self.fn_print("%s" % LINE80)
       self.fn_print("[%sSEND%s] HTTP/2 REQUEST SENT (stream_id=%d, end_stream=%s)" % (C_GREEN, C_END, stream_id, end_stream))
       self.fn_print("%s" % line80)
       for h_para in headers:
           tag   = h_para[0]
           value = h_para[1]
           self.fn_print("%-20s: %s" % (tag, value))
       self.fn_print("%s" % LINE80)

    def _event_handler_data_sent(self, stream_id, data, end_stream):
        try:
            data = data.decode(encoding="utf-8")
        except:
            z_data = zlib.decompress(data)
            data = z_data.decode(encoding="utf-8")

        try:
            data = data.replace('\\"', '"')
            data = data.replace('\\n', '')
            data = data.replace('\\r', '')
            if data[0] == '"':
                data = data[1:-1]
            if data[-1] == '"':
                data = data[0:-2]

            jObject = json.loads(data, object_pairs_hook=OrderedDict)
            data = json.dumps(jObject, indent=4)
        except:
            pass

        #__data = data.decode(encoding="utf-8")
        self.fn_print("%s" % LINE80)
        self.fn_print("[%sSEND%s] HTTP/2 DATA SENT (stream_id=%d, end_stream=%s)" % (C_GREEN, C_END, stream_id, end_stream))
        self.fn_print("%s" % line80)
        s_data = data.split('\n')
        for item in s_data:
            self.fn_print("%s" % (item))
        self.fn_print("%s" % LINE80)

















