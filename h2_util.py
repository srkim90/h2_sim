# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : h2_util.py
  Release  : 1
  Date     : 2018-07-10
 
  Description : HTTP/2 protocol utility module
 
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

import re
import json
import h2.events
import h2.config
import h2.connection
import zlib
from collections import OrderedDict
import select

FRAME_TYPE_DATA            =0
FRAME_TYPE_HEADERS         =1
FRAME_TYPE_PRIORITY        =2
FRAME_TYPE_RST_STREAM      =3
FRAME_TYPE_SETTINGS        =4
FRAME_TYPE_PUSH_PROMISE    =5
FRAME_TYPE_PING            =6
FRAME_TYPE_GOAWAY          =7
FRAME_TYPE_WINDOW_UPDATE   =8
FRAME_TYPE_CONTINUATION    =9

def h2_frame_type_string(frame_type):
    if frame_type == 0:
        return "DATA"
    elif frame_type == 1:
        return "HEADERS"
    elif frame_type == 2:
        return "PRIORITY"
    elif frame_type == 3:
        return "RST_STREAM"
    elif frame_type == 4:
        return "SETTINGS"
    elif frame_type == 5:
        return "PUSH_PROMISE"
    elif frame_type == 6:
        return "PING"
    elif frame_type == 7:
        return "GOAWAY"
    elif frame_type == 8:
        return "WINDOW_UPDATE"
    elif frame_type == 9:
        return "CONTINUATION"
    else:
        return "UNKNOWN_FRAME_TYPE"

HEADER_TABLE_SIZE = 0x01
ENABLE_PUSH = 0x02
MAX_CONCURRENT_STREAMS = 0x03
INITIAL_WINDOW_SIZE = 0x04
MAX_FRAME_SIZE = 0x05
MAX_HEADER_LIST_SIZE = 0x06


def h2_load_json_from_file(json_path):
    if json_path == None:
        return None
    else:
        try:
            json_data=open(json_path).read()
        except FileNotFoundError:
            print("Err. Not found JSON file : %s" % (json_path))
            return None
        try:
            data = json.loads(json_data, object_pairs_hook=OrderedDict)
        except Exception as e:
            print("Err. Fail to parsing JSON : reason=%s, file_name=%s, data=%s" % (e, json_path, json_data))
            return None
    return json.dumps(data)
   

def h2_setting_string(enum_setting):
    if enum_setting == HEADER_TABLE_SIZE:
        return "HEADER_TABLE_SIZE"
    elif enum_setting == ENABLE_PUSH:
        return "ENABLE_PUSH"
    elif enum_setting == MAX_CONCURRENT_STREAMS:
        return "MAX_CONCURRENT_STREAMS"
    elif enum_setting == INITIAL_WINDOW_SIZE:
        return "INITIAL_WINDOW_SIZE"
    elif enum_setting == MAX_FRAME_SIZE:
        return "MAX_FRAME_SIZE"
    elif enum_setting == MAX_HEADER_LIST_SIZE:
        return "MAX_HEADER_LIST_SIZE"
    else:
        return "?? Setting Item"

def h2_method_validation(method):
    if method == "GET":
        return True , ""
    if method == "HEAD":
        return True , ""
    if method == "POST":
        return True , ""
    if method == "PUT":
        return True , ""
    if method == "DELETE":
        return True , ""
    if method == "CONNECT":
        return True , ""
    if method == "OPTIONS":
        return True , ""
    if method == "TRACE":
        return True , ""
    if method == "PATCH":
        return True , ""
    return False, "Invalid method string : %s" % method

def h2_string_decoding(in_str):
    out_str = None
    try:
        out_str = in_str.decode('utf-8')
        return out_str
    except:
        pass

    try:
        out_str = in_str.decode('euc-kr')
        return out_str
    except:
        pass

    return "Unknown-String"

def is_valid_ip(ip):
    m = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", ip)
    return bool(m) and all(map(lambda n: 0 <= int(n) <= 255, m.groups()))

