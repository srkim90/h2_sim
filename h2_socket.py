# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : h2_socket.py
  Release  : 1
  Date     : 2018-07-09
 
  Description : HTTP/2 socket module
 
  Notes :
  ===================
  History
  ===================
  2018/07/09  created by Kim, Seongrae
'''
import socket
import ssl
import sys
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

class h2_socket():
    sock
    def __init__(self, ipaddr, port, is_server, is_tls):
        self.ipaddr     = ipaddr
        self.port       = port
        self.is_server  = is_server
        self.is_tls     = is_tls

#    if 
