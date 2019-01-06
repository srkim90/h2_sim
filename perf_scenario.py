# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : perf_scenario.py
  Release  : 1
  Date     : 2018-07-13
 
  Description : HTTP/2 performance scenario module
 
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

sys.path.insert(0, './util')
sys.path.insert(0, './h2_core')

#from perf import *
from interwork import *
import threading
from sim_util import *
from abc import *
from time import sleep
from log import *
from h2_base import *
from singleton import *
from h2_trace import *
from config import *
from mmc_build_payload import payload_builder

#PERF_SCENARIO_AUTH_REQ_MULTI   = 0
PERF_SCENARIO_FILE              = 0
PERF_SCENARIO_AUTH_GET          = 1
PERF_SCENARIO_LOCATION_PATCH    = 2

def builder():
    b = payload_builder.getinstance()
    return b


class perf_scenario(singleton_instance):
    def __init__(self):
        self.s_time    = 0
        self.unix_time = 0
        self.n_send_in_tick = 0
        self.n_actual_tps = 0
        self.tps_adjust = 1.0


    def get_perf_scenario_entry(self, scenario_idx):
        if PERF_SCENARIO_FILE == scenario_idx:
            return self.__perf_scenario_from_config_file
        elif PERF_SCENARIO_AUTH_GET == scenario_idx:
            return self.__perf_scenario_auth_get
        elif PERF_SCENARIO_LOCATION_PATCH == scenario_idx:
            return self.__perf_scenario_location_patch
        #if PERF_SCENARIO_AUTH_REQ_MULTI == scenario_idx:
        #    return self.__perf_scenario_1
        else:
            PRINT("Err. Invalid performance index : %s" % (scenario_idx))
            return None

    def __tps_ctl(self, HZ, TPS, is_start=True):
        if is_start == True:
            self.s_time = timeit.default_timer()
            if int(self.s_time) != self.unix_time:
                self.unix_time = int(self.s_time)
                self.n_actual_tps = self.n_send_in_tick
                if self.n_actual_tps == 0:
                    return
                crt_rate = float(self.n_send_in_tick)/float(TPS)
                if crt_rate > 0.85 and crt_rate < 1.15:
                    if self.n_send_in_tick < TPS:
                        #print("1.1")
                        self.tps_adjust *= 0.95
                    else:
                        #print("1.2")
                        self.tps_adjust *= 1.15
                else:
                    #print("2: %d, %d, %f" % (self.n_send_in_tick, TPS, crt_rate))
                    self.tps_adjust *= crt_rate
                #print(self.tps_adjust)
                if self.tps_adjust < 0.04:
                    self.tps_adjust = 0.04
                elif self.tps_adjust > 1.5:
                    self.tps_adjust = 1.5
                self.n_send_in_tick = 0
        else:
            self.n_send_in_tick += 1
            run_time = timeit.default_timer() - self.s_time
            corrected_HZ = 0 if HZ <= run_time else (HZ - run_time) * self.tps_adjust
            #print("HZ:%f, run_time:%f" % (HZ, run_time))
            sleep(corrected_HZ)
            if self.n_send_in_tick >= TPS:
                #print("!!!!!!!!!!!!!!!!")
                while True:
                    if self.unix_time != int(timeit.default_timer()):
                        self.n_send_in_tick = 0
                        #self.unix_time = int(timeit.default_timer())
                        break
                    sleep(0.00001)



    '''
    def __perf_scenario_1(self, count, HZ, TPS, iwk, perf, additional_opt=None):
        n_request = 50
        for i in range(0, count, n_request):
            if perf.is_close != False:
                break;
            uri = []
        
            uri.append("/nudr-dr/v1/subscription-data/%s" % (perf.imsi_prefix))
            uri.append(perf.start_sub + (i%perf.max_sub))
            uri.append("/authentication-data")

            uri = "/nudr-dr/v1/subscription-data/%s%06d/authentication-data" % (perf.imsi_prefix, perf.start_sub + (i%perf.max_sub))

            while True:
                if iwk.h2_send_request("GET", uri, None, n_request=n_request) == 0 :
                    sleep(HZ * 10 * n_request)
                else:
                    break

            sleep(HZ)
    '''

    def __get_perf_fn(self, iwk):
        if 0 < iwk.get_connection_count(0): # check request connection ls alive?
            perf_fn = iwk.h2_send_request
        elif 0 < iwk.get_connection_count(1): # check notify connection ls alive?
            perf_fn = iwk.h2_send_notify
        else:
            PRINT("%s%sError. There is no client connection!!%s" % (C_BOLD, C_RED, C_END))
            PRINT("%s%sError. There is no client connection!!%s" % (C_BOLD, C_GREEN, C_END))
            PRINT("%s%sError. There is no client connection!!%s" % (C_BOLD, C_YELLOW, C_END))
            PRINT("%s%sError. There is no client connection!!%s" % (C_BOLD, C_BLUE, C_END))
            PRINT("%s%sError. There is no client connection!!%s" % (C_BOLD, C_PURPLE, C_END))
            return None
        return perf_fn

    def __perf_scenario_from_config_file(self, count, HZ, TPS, iwk, perf, additional_opt=None):
        # begin init
        perf_fn = self.__get_perf_fn(iwk)
        if perf_fn == None:
            return
        if additional_opt["json"] != None:
            #print(type(additional_opt["json"]))
            data = json.dumps(additional_opt["json"])
            data = str.encode(data)
        else:
            data = None
        h_path   = additional_opt["path"]
        h_method = additional_opt["method"]
        f_dynamic_ueid = False
        if h_path.find("{ueId}") != -1:
            f_dynamic_ueid = True
            h_path = h_path.replace("{ueId}", "%s")
        # end init
        
        for i in range(count):
            self.__tps_ctl(HZ, TPS, is_start=True)
            if perf.is_close != False:
                break;
            ## Start add

            if f_dynamic_ueid == True:
                ueId   = "%s%06d" % (perf.imsi_prefix, perf.start_sub + (i%perf.max_sub))
                uri    = h_path % (ueId)
            else:
                uri    = h_path

            while True:
                if perf_fn(h_method, uri, data) == 0 :
                    sleep(HZ * 1.0)
                else:
                    break

            ## End add
            self.__tps_ctl(HZ, TPS, is_start=False)


    def __perf_scenario_auth_get(self, count, HZ, TPS, iwk, perf, additional_opt=None):
        # TODO: init
        perf_fn = self.__get_perf_fn(iwk)
        if perf_fn == None:
            return
        for i in range(count):
            self.__tps_ctl(HZ, TPS, is_start=True)
            if perf.is_close != False:
                break;
            ## Start add
            uri = "/nudr-dr/v1/subscription-data/%s%06d/authentication-data" % (perf.imsi_prefix, perf.start_sub + (i%perf.max_sub))

            while True:
                if perf_fn("GET", uri, None) == 0 :
                    sleep(HZ * 1.0)
                else:
                    break

            ## End add
            self.__tps_ctl(HZ, TPS, is_start=False)


    def __perf_scenario_location_patch(self, count, HZ, TPS, iwk, perf, additional_opt=None):
        # begin init
        perf_fn = self.__get_perf_fn(iwk)
        if perf_fn == None:
            return
        data  = {}
        build = builder()
        ueId  = None
        data["CommLocationData"] = build.build_CommLocationData(ueId)
        #data["CsLocationData"  ] = build.build_CsLocationData(ueId)
        #data["PsLocationData"  ] = build.build_PsLocationData(ueId)
        #data["EpsLocationData" ] = build.build_EpsLocationData(ueId)
        #data["ImsLocationData" ] = build.build_ImsLocationData(ueId)
        #data["AsLocationData"  ] = build.build_AsLocationData(ueId)

        data = json.dumps(data)
        data = str.encode(data)
        # end init
        
        for i in range(count):
            self.__tps_ctl(HZ, TPS, is_start=True)
            if perf.is_close != False:
                break;
            ## Start add

            ueId   = "%s%06d" % (perf.imsi_prefix, perf.start_sub + (i%perf.max_sub))
            uri    = "/nudr-dr/v1/subscription-data/%s/location-data" % (ueId)

            while True:
                if perf_fn("PATCH", uri, data) != True :
                    sleep(HZ * 1.0)
                else:
                    break

            ## End add
            self.__tps_ctl(HZ, TPS, is_start=False)




