# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : perf.py
  Release  : 1
  Date     : 2018-07-13
 
  Description : HTTP/2 performance module
 
  Notes :
  ===================
  History
  ===================
  2018/07/13  created by Kim, Seongrae
'''
import re
import os
import sys    
import termios
import fcntl

sys.path.insert(0, './')
sys.path.insert(0, './util')
sys.path.insert(0, './h2_core')

from interwork import *
import threading
from abc import *
from time import sleep
from log import *
from h2_base import *
from singleton import *
from h2_trace import *
from config import *
from perf_scenario import *

class h2_perf(singleton_instance):
    tps             = 0
    max_sub         = 0
    is_close        = False
    start_sub       = 0
    imsi_prefix     = ""
    is_perf_doing   = False
    max_stream_id   = 0

    fn_get_perf_scenario_entry = None

    def __init__(self):
        sim_config = cfgConnection.getinstance()
        self.imsi_prefix, self.start_sub, self.max_sub, self.tps, self.max_stream_id, nConn, is_trace = sim_config.getTpsCfg()  
        pass

    def start_perf(self, scenario_idx, count, f_from_file=False, perf_config_path=None):
        if self.is_perf_doing == True:
            PRINT("Performance already on going")
            return
        self.is_close = False
        cfg_dict = None
        if f_from_file == True:
            cfg_dict = self.load_perf_cfg(perf_config_path)
            if cfg_dict == None:
                PRINT("Invalid HTTP/2 Simulator Performance configuration: %s" % (perf_config_path))
                return


        hThread = threading.Thread(target=self._perf_th, args=(scenario_idx, count, cfg_dict))
        hThread.daemon = True
        hThread.start()
        

    def halt_perf(self):
        if self.is_perf_doing == False:
            PRINT("No performance in progress")
            return
        self.is_close = True


    def load_perf_cfg(self, perf_config_path):
        PRINT("Loading performance configuration: path=%s" % (perf_config_path))

        f_data=0
        f_head=0
        json_str = ""
        perf_dict = {}

        if not os.path.isfile(perf_config_path):
            PRINT("Err. Not exist perf config file : %s" % (perf_config_path))
            return None

        for line in open(perf_config_path, 'r').readlines():
            line  = line.split('#')[0]
            line  = line.replace("\r",'')
            line  = line.replace("\n",'')
            line2 = line.replace(' ','')
            line2 = line2.replace('\t','')
            if len(line) == 0 or len(line2) == 0:

                continue

            if line.find("[HEADERS]") != -1:
                if len(line2) == len("[HEADERS]"):
                    f_head = 1
                    f_data = 0
                    continue

            if line.find("[DATA]") != -1:
                if len(line2) == len("[DATA]"):
                    f_head = 0
                    f_data = 1
                    continue
    
            if f_head == 1:
                items = line2.split("=")
                if len(items) < 2:
                    continue
                if items[0] == "method":
                    perf_dict["method"] = items[1]
                elif items[0] == "path":
                    path = ""
                    for idx in range(1,len(items)):
                        path += "%s=" % (items[idx])
                    path = path[0:-1]
                    #path = path.replace("{udId}", "%s")
                    perf_dict["path"] = path

            if f_data == 1:
                json_str += "%s\n" % (line)

        if json_str.find('{') != -1:
            try:
                data = json.loads(json_str)
                perf_dict["json"] = data
            except:
                PRINT("Err. Fail to parsing JSON file : %s" % (perf_config_path))
                return None

        else:
            perf_dict["json"] = None

        if "method" not in perf_dict.keys():
            PRINT("Not found config item : [method] in config file=%s" % (perf_config_path))
            return None

        if "path" not in perf_dict.keys():
            PRINT("Not found config item : [path] in config file=%s" % (perf_config_path))
            return None

        return perf_dict


    def _perf_th(self, scenario_idx, count, additional_opt):
        log = sa_log.getinstance() 
        HZ = (1.00 /self.tps)# * 0.165
        iwk = h2_interwork.getinstance()
        h2_base.set_perf_mode(True)

        self.is_perf_doing = True
        log.is_trace_log = False

        if additional_opt != None:
            scenario_idx = PERF_SCENARIO_FILE
        
        PRINT ("-- Performance Thread Start : ( Count : %d , TPS = %s ) After 3 Sec Starting... --" % (count, self.tps))

        for i in range(3):
            PRINT ("-- Start Remain Time .................................... [ %s%d%s ]" % (C_GREEN, i, C_END) )
            sleep(1.0)

        fn = self.fn_get_perf_scenario_entry(scenario_idx)
        if fn != None:
            fn(count, HZ, self.tps, iwk, self, additional_opt=additional_opt)
        else:
            PRINT("Invalid performance scenario index :%d" % (scenario_idx))

        PRINT ("-- Performance Thread End  --")
        h2_base.set_perf_mode(False)
        self.is_perf_doing = False
        #log.is_trace_log = True
  
    def get_perf_status(self):
        return self.is_perf_doing

def init_perf():
    e = h2_perf.instance()
    s = perf_scenario.instance()
    e.fn_get_perf_scenario_entry = s.get_perf_scenario_entry
    




