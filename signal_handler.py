# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : signal_handler.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : simulator signal handler module
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import os
import sys
import time
import signal
import threading
from sim_exit import *
from peer import h2_peer

class signal_handler:
    signal_recv_time = 0
    def __init__(self):
        self.signal_init()

    def signal_init(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        hThread = threading.Thread(target=self.signal_wait)
        hThread.daemon = True
        hThread.start()

    def signal_wait(self):
        signal.pause()

    def signal_handler(self, signal, frame):

        if time.time() - self.signal_recv_time > 1:
            print('\nYou pressed Ctrl+C!! If once again input within 1 sec, will quit.')
            self.signal_recv_time = time.time()
            return

        exit_handler()

