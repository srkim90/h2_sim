# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : mmc.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : HTTP/2 mmc module
 
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

from h2_base import *
from abc import *
from perf import *
from h2_util import *
from sim_exit import *
from h2_trace import *
from time import sleep
from mmc_parse import *
from interwork import *
from dispatch_parse import *
from perf_scenario import *
from mmc_api import *
from mmc_api_notify import *
from expect import *
from collections import OrderedDict

if int(sys.version[0]) == 3 and get_python_runtime == PYTHON_TYPE_CPYTHON:
    import tracemalloc


class __mmc_quit(mmc):
    @staticmethod
    def run(command):
        exit_handler()


class __mmc_send_manual(mmc):
    @staticmethod
    def run(command):
        in_method       = command[3]
        in_path         = command[4]
        in_json_file    = command[5]
        json_data       = None
        if in_json_file == "NULL":
            in_json_file = None
            data = None
        else:
            try:
                json_data=open(in_json_file).read()
            except FileNotFoundError:
                PRINT("Err. Not found JSON file : %s" % (in_json_file))
                return
            try:
                data = json.loads(json_data, object_pairs_hook=OrderedDict)
            except :
                PRINT("Err. Fail to parsing JSON file : %s" % (in_json_file))
                return

        PRINT("send_manual: method=%s, path=%s, JSON-File=%s" % (in_method, in_path, in_json_file))

        check = h2_method_validation(in_method)
        if check[0] == False:
            PRINT(check[1], tab=2)
            return

        iwk = h2_interwork.getinstance()
        if command[1] == "request":
            iwk.h2_send_request(in_method, in_path, data)
        elif command[1] == "notify":
            iwk.h2_send_notify(in_method, in_path, data)



class __mmc_response_set(mmc):
    @staticmethod
    def run(command):
        if command[0] == "enable":
            PRINT("enable RESPONSE")
            h2_base.set_enable_response(True)
        else:
            PRINT("disable RESPONSE")
            h2_base.set_enable_response(False)


class __mmc_ping_set(mmc):
    @staticmethod
    def run(command):
        if command[0] == "enable":
            PRINT("enable PING")
            #h2_base.enable_ping = True
            h2_base.set_enable_ping(True)
        else:
            PRINT("disable PING")
            #h2_base.enable_ping = False
            h2_base.set_enable_ping(False)


class __mmc_expect_set(mmc):
    @staticmethod
    def run(command):
        ep = expect.getinstance()
        if command[0] == "enable":
            ep.init_expect()
        else:
            ep.del_expect()


class mmc_log_set(mmc):
    @staticmethod
    def run(command):
        log = sa_log.getinstance()
        if command[0] == "enable":
            PRINT("enable logging")
            log.is_trace_log = True
        else:
            PRINT("disable logging")
            log.is_trace_log = False


class __mmc_help(mmc):
    @classmethod
    def print_notify_command(cls):
        HELP_PRINT("send notify subscriber_id_data {ueId} GET", tab=2)
        HELP_PRINT("send notify authentication_data {ueId} GET ALL", tab=2)
        HELP_PRINT("send notify authentication_data {ueId} GET eps", tab=2)
        HELP_PRINT("send notify authentication_data {ueId} GET ims", tab=2)
        HELP_PRINT("send notify authentication_data {ueId} GET wifi", tab=2)
        HELP_PRINT("send notify authentication_data {ueId} PATCH", tab=2)
        HELP_PRINT("send notify eps_am_data {ueId} GET ALL", tab=2)
        HELP_PRINT("send notify eps_am_data {ueId} GET active_apn_data", tab=2)
        HELP_PRINT("send notify eps_am_data {ueId} POST active_apn_data {ActiveApnData:apnContextId}", tab=2)
        HELP_PRINT("send notify eps_am_data {ueId} PUT active_apn_data {ActiveApnData:apnContextId}", tab=2)
        HELP_PRINT("send notify eps_am_data {ueId} DELETE ALL", tab=2)
        HELP_PRINT("send notify eps_am_data {ueId} DELETE active_apn_data {ActiveApnData:apnContextId}", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} GET ALL", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} GET cscf_restore_data", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} GET as_notify_data", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} POST cscf_restore_data {ImsSubsData:imsPrivateUserId}", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} POST as_notify_data {AsNotifyData:asGroupId} {dataReferenceId}", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} PUT cscf_restore_data {ImsSubsData:imsPrivateUserId}", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} PUT as_notify_data {AsNotifyData:asGroupId} {dataReferenceId}", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} DELETE cscf_restore_dat", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} DELETE as_notify_data ALL", tab=2)
        HELP_PRINT("send notify ims_am_data {ueId} DELETE as_notify_data SELECT {AsNotifyData:asGroupId} {dataReferenceId} ", tab=2)
        HELP_PRINT("send notify location_data {ueId} GET  ALL", tab=2)
        HELP_PRINT("send notify location_data {ueId} GET SELECT CsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} GET SELECT PsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} GET SELECT EpsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} GET SELECT ImsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} GET SELECT AsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} GET BITMASK 1234", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH ALL", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH SELECT CommLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH SELECT CsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH SELECT PsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH SELECT EpsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH SELECT ImsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH SELECT AsLocationData", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH SELECT BSGServiceData", tab=2)
        HELP_PRINT("send notify location_data {ueId} PATCH BITMASK 0123456", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} GET ALL", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} GET SELECT BasicServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} GET SELECT CFServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} GET SELECT SNDServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} GET SELECT ImsServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} GET SELECT InServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} GET SELECT VirtualServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} GET BITMASK 123456", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} PATCH BasicServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} PATCH CFServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} PATCH SNDServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} PATCH ImsServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} PATCH InServiceData", tab=2)
        HELP_PRINT("send notify supplement_service_data {ueId} PATCH VirtualServiceData", tab=2)
        #HELP_PRINT("send notify tas_data {ueId} GET fields TasContextData", tab=2)
        #HELP_PRINT("send notify tas_data {ueId} GET fields TasNdubData", tab=2)
        HELP_PRINT("send notify tas_data {ueId} GET fields ALL", tab=2)
        HELP_PRINT("send notify tas_data {ueId} GET tas_context_data", tab=2)
        HELP_PRINT("send notify tas_data {ueId} GET tas_ndub_data ALL", tab=2)
        HELP_PRINT("send notify tas_data {ueId} GET tas_ndub_data targetId {targetId}", tab=2)
        HELP_PRINT("send notify tas_data {ueId} POST tas_ndub_data targetId {targetId}", tab=2)
        HELP_PRINT("send notify tas_data {ueId} PATCH tas_context_data", tab=2)
        HELP_PRINT("send notify tas_data {ueId} PATCH tas_ndub_data targetId {targetId}", tab=2)
        HELP_PRINT("send notify tas_data {ueId} DELETE tas_ndub_data ALL", tab=2)
        HELP_PRINT("send notify tas_data {ueId} DELETE tas_ndub_data targetId {targetId}", tab=2)
        HELP_PRINT("send notify manual GET / NULL", tab=2)

    @classmethod
    def print_request_command(cls):
        HELP_PRINT("send request subscriber_id_data {ueId} GET", tab=2)
        HELP_PRINT("send request authentication_data {ueId} GET ALL", tab=2)
        HELP_PRINT("send request authentication_data {ueId} GET eps", tab=2)
        HELP_PRINT("send request authentication_data {ueId} GET ims", tab=2)
        HELP_PRINT("send request authentication_data {ueId} GET wifi", tab=2)
        HELP_PRINT("send request authentication_data {ueId} PATCH", tab=2)
        HELP_PRINT("send request eps_am_data {ueId} GET ALL", tab=2)
        HELP_PRINT("send request eps_am_data {ueId} GET active_apn_data", tab=2)
        HELP_PRINT("send request eps_am_data {ueId} POST active_apn_data {ActiveApnData:apnContextId}", tab=2)
        HELP_PRINT("send request eps_am_data {ueId} PUT active_apn_data {ActiveApnData:apnContextId}", tab=2)
        HELP_PRINT("send request eps_am_data {ueId} DELETE ALL", tab=2)
        HELP_PRINT("send request eps_am_data {ueId} DELETE active_apn_data {ActiveApnData:apnContextId}", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} GET ALL", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} GET cscf_restore_data", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} GET as_notify_data", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} POST cscf_restore_data {ImsSubsData:imsPrivateUserId}", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} POST as_notify_data {AsNotifyData:asGroupId} {dataReferenceId}", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} PUT cscf_restore_data {ImsSubsData:imsPrivateUserId}", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} PUT as_notify_data {AsNotifyData:asGroupId} {dataReferenceId}", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} DELETE cscf_restore_dat", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} DELETE as_notify_data ALL", tab=2)
        HELP_PRINT("send request ims_am_data {ueId} DELETE as_notify_data SELECT {AsNotifyData:asGroupId} {dataReferenceId} ", tab=2)
        HELP_PRINT("send request location_data {ueId} GET  ALL", tab=2)
        HELP_PRINT("send request location_data {ueId} GET SELECT CsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} GET SELECT PsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} GET SELECT EpsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} GET SELECT ImsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} GET SELECT AsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} GET BITMASK 1234", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH ALL", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH SELECT CommLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH SELECT CsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH SELECT PsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH SELECT EpsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH SELECT ImsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH SELECT AsLocationData", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH SELECT BSGServiceData", tab=2)
        HELP_PRINT("send request location_data {ueId} PATCH BITMASK 0123456", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} GET ALL", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} GET SELECT BasicServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} GET SELECT CFServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} GET SELECT SNDServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} GET SELECT ImsServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} GET SELECT InServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} GET SELECT VirtualServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} GET BITMASK 123456", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} PATCH BasicServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} PATCH CFServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} PATCH SNDServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} PATCH ImsServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} PATCH InServiceData", tab=2)
        HELP_PRINT("send request supplement_service_data {ueId} PATCH VirtualServiceData", tab=2)
        #HELP_PRINT("send request tas_data {ueId} GET fields TasContextData", tab=2)
        #HELP_PRINT("send request tas_data {ueId} GET fields TasNdubData", tab=2)
        HELP_PRINT("send request tas_data {ueId} GET fields ALL", tab=2)
        HELP_PRINT("send request tas_data {ueId} GET tas_context_data", tab=2)
        HELP_PRINT("send request tas_data {ueId} GET tas_ndub_data ALL", tab=2)
        HELP_PRINT("send request tas_data {ueId} GET tas_ndub_data targetId {targetId}", tab=2)
        HELP_PRINT("send request tas_data {ueId} POST tas_ndub_data targetId {targetId}", tab=2)
        HELP_PRINT("send request tas_data {ueId} PATCH tas_context_data", tab=2)
        HELP_PRINT("send request tas_data {ueId} PATCH tas_ndub_data targetId {targetId}", tab=2)
        HELP_PRINT("send request tas_data {ueId} DELETE tas_ndub_data ALL", tab=2)
        HELP_PRINT("send request tas_data {ueId} DELETE tas_ndub_data targetId {targetId}", tab=2)
        HELP_PRINT("send request manual GET / NULL", tab=2)


    @classmethod
    def run(cls, command):
        HELP_PRINT("%s" % (LINE80))
        HELP_PRINT("  HTTP/2 Simulator", tab=1)
        HELP_PRINT("%s" % (line80))
        HELP_PRINT("  Send HTTP/2 Request Example")
        HELP_PRINT("send request manual GET /nudr-dr/v1/subscription-data/450081060000000/authentication-data NULL", tab=2)
        HELP_PRINT("send request manual PATCH /nudr-dr/v1/subscription-data/450081060000000/authentication-data/eps-auth-data ./h2_cfg/json/short.json", tab=2)
        HELP_PRINT("send notify manual GET /nudr-dr/v1/subscription-data/450081060000000/authentication-data NULL", tab=2)
        HELP_PRINT("send notify manual PATCH /nudr-dr/v1/subscription-data/450081060000000/authentication-data/eps-auth-data ./h2_cfg/json/short.json", tab=2)
        HELP_PRINT("")
        HELP_PRINT("  Enable or Disable HTTP/2 Trace")
        HELP_PRINT("enable log", tab=2)
        HELP_PRINT("disable log", tab=2)
        HELP_PRINT("")
        HELP_PRINT("  Send HTTP/2 performance")
        HELP_PRINT("perf start auth_get N", tab=2)
        HELP_PRINT("perf start location_patch N", tab=2)
        HELP_PRINT("perf start manual ./h2_cfg/perf/perf_get_test_api.cfg N", tab=2)
        HELP_PRINT("perf start manual ./h2_cfg/perf/perf_patch_test_api.cfg N", tab=2)
        HELP_PRINT("perf stop", tab=2)
        HELP_PRINT("")
        HELP_PRINT("  Print Information")
        HELP_PRINT("show data_cfg", tab=2)
        HELP_PRINT("show stat", tab=2)
        HELP_PRINT("")
        HELP_PRINT("  Example commands (ALL)")
        cls.print_notify_command()
        #cls.print_request_command()

        HELP_PRINT("")
        HELP_PRINT("  Example batch")
        HELP_PRINT("batch start from_file /sim/cfg/batch/1.authentication_data.bat", tab=2)
        HELP_PRINT("batch start from_file /sim/cfg/batch/2.eps_am_data.bat", tab=2)
        HELP_PRINT("batch start from_file /sim/cfg/batch/3.ims_am_data.bat", tab=2)
        HELP_PRINT("batch start from_file /sim/cfg/batch/4.location_data.bat", tab=2)
        HELP_PRINT("batch start from_file /sim/cfg/batch/5.supplement_service_data.bat", tab=2)
        HELP_PRINT("  Last update : 2018.08.10")
        HELP_PRINT("%s" % (LINE80))

'''
                          # URL                       RULE    HIGHEST-STREAM-ID   CONNECTED_TIME
show connection list      # http://222.99.178.9:9999  Client  1000001             2018-09-17 18:00:00
show connection all       #
show connection select S  # IB/OB_0HPACK_TABLE, HIGHEST-IB/OB-STREAM-ID, IB/OB_HPACK_TABLE_SIZE, MAX_STREAM_ID, IB/OB_SETTING, frames, MY_IP/Port Peer_Ip/Port 
set stream_timeout N    

# literal header field with incremental indexing
set header_indexing_rule incremental_indexing ALL
set header_indexing_rule incremental_indexing select S

# literal header field never indexed
set header_indexing_rule never_indexed ALL
set header_indexing_rule never_indexed SELECT S

show header_indexing_rule
'''

class __mmc_show_data_cfg(mmc):
    @staticmethod
    def run(command):
        e = cfg_data.getinstance()
        e.print_data_dictionary()
        print()

class __mmc_perf_halt(mmc):
    @staticmethod
    def run(command):
        e = h2_perf.getinstance()
        e.halt_perf()

class __mmc_show_echo(mmc):
    @staticmethod
    def run(command):
        echo_string = command[2]
        tockens = echo_string.split('_')
        echo_string = ""
        for item in tockens:
            echo_string += "%s " % item
        PRINT("%s" % (echo_string))

duration = 0
class mmc_show_stat(mmc):
    @staticmethod
    def run(command):
        global duration
        n_count    = 0
        old_timeit = 0
        max_wait_cnt = 40
        e = dispatch_util.getinstance()
        while True:
            ch = mmc_parse._getch()
            if ch != "":               
                return
            if n_count > 0:
                os.system('clear') 
            e.show_stat()
            duration   = timeit.default_timer() - old_timeit if old_timeit != 0 else float(max_wait_cnt) / 10
            old_timeit = timeit.default_timer()
            if command[1] != "continuous_stat":
                return
            for i in range(max_wait_cnt):
                n_remain_time = duration - (timeit.default_timer() - old_timeit)
                if n_remain_time < 0.0:
                    n_remain_time = 0.0
                mmc_print("\r     Statistic will be update after %d sec" % (n_remain_time + 1), end="", flush=True)
                ch = mmc_parse._getch(0.05)
                if ch != "":               
                    return
                sleep(0.05) 
            #PRINT("\n\n\n\n\n")
            n_count += 1

class __mmc_perf_start(mmc):
    @staticmethod
    def run(command):
        f_from_file      = False
        count            = int(command[-1])
        scenario         = command[2]
        perf_config_path = None
        e = h2_perf.getinstance()

        if count == -1:
            count = 5000000000

        if scenario == "auth_get":
            scenario_type = PERF_SCENARIO_AUTH_GET
        elif scenario == "location_patch":
            scenario_type = PERF_SCENARIO_LOCATION_PATCH
        elif scenario == "manual":
            scenario_type    = PERF_SCENARIO_FILE
            perf_config_path = command[3]
            f_from_file      = True
        else:
            PRINT("Err. Invalid performance type : %s" % (scenario))
            return
        '''
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        '''
        e.start_perf(scenario_type, count, f_from_file=f_from_file, perf_config_path=perf_config_path)

        sleep(3.5)
        mmc_show_stat.run([None, "continuous_stat"])
        '''
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        for stat in top_stats:
            stat = "%s" % stat
            stat = stat.split(' ')
            result_string = "%-82s " % (stat[0])
            for i_stat in stat[1:]:
                result_string += "%-15s " % (i_stat)
            PRINT("%s" % result_string)
        '''

class __mmc_perf_start_ex(mmc):
    @staticmethod
    def run(command):
        MAX_HTTP2_CONN=500
        count        = int(command[4])
        n_connection = int(command[3])
        e = h2_perf.getinstance()
        c = h2_peer.getinstance()
        iwf = h2_interwork.instance()
        old_connection = 0
    
        if n_connection <= 0 or n_connection > MAX_HTTP2_CONN:
            PRINT("Invalid input parameter : count=%d, must input number in (%d ~ %d)" % (n_connection, 1, MAX_HTTP2_CONN))
            return

        old_connection = c.h2_peer_list[0].conn_request_max
        if old_connection != n_connection:
            c.change_connection_count(iwf.h2_resume_callback, h2_conn_type.CONNTYPE_CLIENT_REQUEST, n_connection );

        sleep(0.11)
        PRINT("set %s per NF : %s --> %s" % (command[1], old_connection, n_connection))

        e.start_perf(PERF_SCENARIO_AUTH_REQ_MULTI, count)
        e = dispatch_util.getinstance()

        update_duration = 1.0
        silent_idx      = int(5.0 / update_duration)
        for i  in range(999999):
            ch = mmc_parse._getch()
            if ch != "":
                break
            if i >= silent_idx:
                if i == silent_idx:
                    PRINT("\n\n\n\n\n")
                e.show_stat(ln_sleep = update_duration)
            sleep(update_duration) 


class __mmc_show_python_memory(mmc):
    @staticmethod
    def run(command):
        if int(sys.version[0]) < 3 or get_python_runtime != PYTHON_TYPE_CPYTHON:
            PRINT("Python Version Error: This function is provided python version > 3.5 and NOT pypy, now version is = %s" % sys.version)
            return
        tracemalloc.start()
        snapshot1 = tracemalloc.take_snapshot()
        snapshot2 = tracemalloc.take_snapshot()
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')
        for stat in top_stats:
            stat = "%s" % stat
            stat = stat.split(' ')
            result_string = "%-82s " % (stat[0])
            for i_stat in stat[1:]:
                result_string += "%-15s " % (i_stat)
            PRINT("%s" % result_string)

class __mmc_show_mmc_tree(mmc):
    @staticmethod
    def run(command):
        e = mmc_parse.getinstance()
        e.show_mmc_tree()



class __mmc_set_hdr_indexing_rule (mmc):
    @staticmethod
    def run(command):
        rule_type   = command[2]
        rule_option = command[3]
        if rule_option == "ALL":
            fields = "__ALL__"
        else:
            fields = command[4]

        if rule_type == "inc_idx":
            is_indexed = True
        else:
            is_indexed = False

        str_rule = "literal header field with incremental indexing" if is_indexed == True else "literal header field never indexed"

        PRINT("set header indexing rule for field %s : %s" % (fields, str_rule))
        h2_base.set_head_tuple_by_name(fields, is_indexed)


class __mmc_set_parameters(mmc):
    @staticmethod
    def run(command):
        if command[1] == "ping_interval":
            value = float(command[2])
            PRINT("set ping_interval : %s --> %s" % (h2_base.get_ping_interval(), value))
            h2_base.set_ping_interval(value)
        elif command[1] == "ping_timeout":
            value = float(command[2])
            if h2_base.get_ping_interval() - 0.1 < value:
                PRINT("Invalid input parameter : ping_interval=%s, ping_timeout(input)=%s" % (h2_base.get_ping_timeout(), value))
                return
            PRINT("set ping_timeout : %s --> %s" % (h2_base.get_ping_timeout(), value))
            h2_base.set_ping_timeout(value)
        elif command[1] == "data_file":
            file_name = command[2]
            if not os.path.isfile(file_name):
                PRINT("Error. not found config file : name=%s" % (file_name))
                return
            cfg = cfg_data.getinstance()
            cfg.set_data_file(file_name)
            return
        elif command[1] == "reset_data_file":
            cfg = cfg_data.getinstance()
            cfg.reset_data_file()
        elif command[1] == "reset_stat":
            stat = dispatch_util.getinstance()
            stat.reset_api_stat()
        elif command[1] == "expect": #a if test else b
            mode         = JSON_IGNORE if command[3] == "IGNORE_JSON" else JSON_FIND_COINCIDE_ITEM
            expect_rcode =  int(command[2])
            s_method     =  command[4]
            e_method     =  command[5]
            ep = expect.getinstance()
            ep.set_expect_result(expect_rcode, mode, s_method, e_method)
        elif command[1] == "request_timeout":
            value = float(command[2])
            if h2_base.set_request_timeout() - 0.1 < value:
                PRINT("Invalid input parameter : request_timeout=%s, request_timeout(input)=%s" % (h2_base.get_request_timeout(), value))
                return
            PRINT("set request_timeout : %s --> %s" % (h2_base.get_request_timeout(), value))
            h2_base.set_request_timeout(value)
        elif command[1] == "responce_delay":
            value = float(command[2])
            PRINT("set responce delay : %s --> %s" % (h2_base.get_responce_delay(), value))
            h2_base.set_responce_delay(value)




class __mmc_show_hpack_table (mmc):
    @staticmethod
    def run(command):
        peer = h2_peer.getinstance()
        conn_list = peer.h2_get_connection_list()
        for h2_conns in conn_list:
            for conn_list2 in h2_conns.conn_list:
                h2_conn = conn_list2[2]
                h2_conn.show_hpack_index_table()


class __mmc_show_connection_list (mmc):
    @staticmethod
    def run(command):
        PRINT("Not implemented yet")
        return

        peer = h2_peer.getinstance()
        conn_list = peer.h2_get_connection_list()
        for h2_conns in conn_list:
            for conn_list2 in h2_conns.conn_list:
                h2_conn = conn_list2[2]
                h2_conn.show_hpack_index_table()

        #PRINT("Not implemented yet")
        #pass

class __mmc_show_header_indexing_rule(mmc):
    @staticmethod
    def run(command):
        h2_base.show_head_indxing_rule()

class mmc_set_connection_count(mmc):
    @staticmethod
    def run(command):
        MAX_HTTP2_CONN=500
        e = h2_peer.getinstance()
        iwf = h2_interwork.instance()
        value = int(command[2])
        old_value = 0
    
        if value <= 0 or value > MAX_HTTP2_CONN:
            PRINT("Invalid input parameter : count=%d, must input number in (%d ~ %d)" % (value, 1, MAX_HTTP2_CONN))
            return

        if command[1] == "request_conn":
            old_value = e.h2_peer_list[0].conn_request_max
            if old_value != value:
                e.change_connection_count(iwf.h2_resume_callback, h2_conn_type.CONNTYPE_CLIENT_REQUEST, value );
        elif command[1] == "notify_conn":
            old_value = e.h2_peer_list[0].conn_notify_max
            if old_value != value:
                e.change_connection_count(iwf.h2_resume_callback, h2_conn_type.CONNTYPE_CLIENT_NOTIFY, value );

        sleep(0.11)
        PRINT("set %s per NF : %s --> %s" % (command[1], old_value, value))


class __mmc_sleep(mmc):
    @staticmethod
    def run(command):
        ms_sleep = float(command[2]) / 1000.0
        sleep(ms_sleep)
        return

class __mmc_run_batch(mmc):
    @staticmethod
    def run(command):
        n_request = 0
        s_request = 0
        commands  = []
        file_name = command[3]
        if not os.path.isfile(file_name):
            PRINT("Error. not found batch file : name=%s" % (file_name))
            return

        for line in open(file_name, 'r').readlines():
            line = line.replace('\n', "")
            line = line.replace('\r', "")
            line = line.replace('\t', " ")
            line = line.split('::')[0]
            line = line.split('rem')[0]
            if len(line) <= 2:
                continue
            command = line
            commands.append(command)

            if command.find("send request") != -1:
                n_request += 1

        for command in commands:
            mmc = mmc_parse.getinstance()
            command = "%s      " % command
            n_error = mmc.run_command(command)
            if n_error == False:
                PRINT("Invalid batch command : %s" % (command))
            if command.find("send request") != -1:
                s_request += 1
                if n_request >= 10:
                   PRINT("%-90s (%02d/%02d)" % (command, s_request, n_request))
                else:
                   PRINT("%-90s (%d/%d)" % (command, s_request, n_request))
        return




__mmc = [
          ["set",                 0, "set"                                   , None                          ],
          ["quit",                0, "quit"                                  , __mmc_quit                    ],
          ["send",                0, "send"                                  , None                          ],
          ["help",                0, "help"                                  , __mmc_help                    ],
          ["show",                0, "show"                                  , None                          ],
          ["request",             1, "send-request"                          , None                          ],
          ["manual",              2, "send-request-manual"                   , None                          ],
          [":method",             3, "send-request-manual-S"                 , None                          ],
          [":path",               4, "send-request-manual-S-S"               , None                          ],
          ["JSON-File",           5, "send-request-manual-S-S-S"             , __mmc_send_manual             ],
          ["notify",              1, "send-notify"                           , None                          ],
          ["manual",              2, "send-notify-manual"                    , None                          ],
          [":method",             3, "send-notify-manual-S"                  , None                          ],
          [":path",               4, "send-notify-manual-S-S"                , None                          ],
          ["JSON-File",           5, "send-notify-manual-S-S-S"              , __mmc_send_manual             ],
          ["enable",              0, "enable"                                , None                          ],
          ["log",                 1, "enable-log"                            , mmc_log_set                   ],
          ["ping",                1, "enable-ping"                           , __mmc_ping_set                ],
          ["expect",              1, "enable-expect"                         , __mmc_expect_set              ],
          ["response",            1, "enable-response"                       , __mmc_response_set            ],
          ["disable",             0, "disable"                               , None                          ],
          ["log",                 1, "disable-log"                           , mmc_log_set                   ],
          ["ping",                1, "disable-ping"                          , __mmc_ping_set                ],
          ["expect",              1, "disable-expect"                        , __mmc_expect_set              ],
          ["response",            1, "disable-response"                      , __mmc_response_set            ],
          ["data_cfg",            1, "show-data_cfg"                         , __mmc_show_data_cfg           ],
          ["stat",                1, "show-stat"                             , mmc_show_stat                 ],
          ["header_indexing_rule",1, "show-header_indexing_rule"             , __mmc_show_header_indexing_rule ],
          ["continuous_stat",     1, "show-continuous_stat"                  , mmc_show_stat                 ],
          ["mmc_tree",            1, "show-mmc_tree"                         , __mmc_show_mmc_tree           ],
          ["python_memory",       1, "show-python_memory"                    , __mmc_show_python_memory      ],
          ["echo",                1, "show-echo"                             , None                          ],
          ["message",             2, "show-echo-S"                           , __mmc_show_echo               ],
          ["connection",          1, "show-connection"                       , None                          ],
          ["list",                2, "show-connection-list"                  , __mmc_show_connection_list    ],
          ["all" ,                2, "show-connection-all"                   , __mmc_show_connection_list    ],
          ["select",              2, "show-connection-select"                , None                          ],
          ["connection_id",       3, "show-connection-select-S"              , __mmc_show_connection_list    ],
          ["hpack_table",         1, "show-hpack_table"                      , __mmc_show_hpack_table        ],
          ["perf",                0, "perf"                                  , None                          ],
          ["start",               1, "perf-start"                            , None                          ],
          ["auth_get",            2, "perf-start-auth_get"                   , None                          ],
          ["count",               3, "perf-start-auth_get-N"                 , __mmc_perf_start              ],
          ["location_patch",      2, "perf-start-location_patch"             , None                          ],
          ["count",               3, "perf-start-location_patch-N"           , __mmc_perf_start              ],
          ["manual",              2, "perf-start-manual"                     , None                          ],
          ["conig_path",          3, "perf-start-manual-S"                   , None                          ],
          ["count",               4, "perf-start-manual-S-N"                 , __mmc_perf_start              ],
#         ["m_auth_request",      2, "perf-start-m_auth_request"             , None                          ],
#         ["n_connection",        3, "perf-start-m_auth_request-N"           , None                          ],
#         ["send_count",          4, "perf-start-m_auth_request-N-N"         , __mmc_perf_start_ex           ],
          ["halt",                1, "perf-halt"                             , __mmc_perf_halt               ],
          ["ping_interval",       1, "set-ping_interval"                     , None                          ],
          ["ping_timeout",        1, "set-ping_timeout"                      , None                          ],
          ["second",              2, "set-ping_interval-N"                   , __mmc_set_parameters          ],
          ["second",              2, "set-ping_timeout-N"                    , __mmc_set_parameters          ],
          ["request_conn",        1, "set-request_conn"                      , None                          ],
          ["notify_conn",         1, "set-notify_conn"                       , None                          ],
          ["count",               2, "set-request_conn-N"                    , mmc_set_connection_count      ],
          ["count",               2, "set-notify_conn-N"                     , mmc_set_connection_count      ],
          ["sleep",               1, "set-sleep"                             , None                          ],
          ["msec",                2, "set-sleep-N"                           , __mmc_sleep                   ],
          ["data_file",           1, "set-data_file"                         , None                          ],
          ["reset_data_file",     1, "set-reset_data_file"                   , __mmc_set_parameters          ],
          ["reset_data_file",     1, "set-reset_stat"                        , __mmc_set_parameters          ],
          ["file_path",           2, "set-data_file-S"                       , __mmc_set_parameters          ],
          ["request_timeout",     1, "set-request_timeout"                   , None                          ],
          ["sec/float_timeout",   2, "set-request_timeout-N"                 , __mmc_set_parameters          ],
          ["responce_delay",      1, "set-responce_delay"                    , None                          ],
          ["sec/float_timeout",   2, "set-responce_delay-N"                  , __mmc_set_parameters          ],
          ["expect",              1, "set-expect"                            , None                          ],
          ["r_code",              2, "set-expect-N"                          , None                          ],
          ["IGNORE_JSON",         3, "set-expect-N-IGNORE_JSON"              , None                          ],
          ["start_method",        4, "set-expect-N-IGNORE_JSON-S"            , None                          ],
          ["end_method",          5, "set-expect-N-IGNORE_JSON-S-S"          , __mmc_set_parameters          ],
          ["COMPARE_JSON",        3, "set-expect-N-COMPARE_JSON"             , None                          ],
          ["start_method",        4, "set-expect-N-COMPARE_JSON-S"           , None                          ],
          ["end_method",          5, "set-expect-N-COMPARE_JSON-S-S"         , __mmc_set_parameters          ],
          ["indexing_rule",       1, "set-indexing_rule"                     , None                          ],
          ["incremental_indexing",2, "set-indexing_rule-inc_idx"             , None                          ],
          ["ALL",                 3, "set-indexing_rule-inc_idx-ALL"         , __mmc_set_hdr_indexing_rule   ],
          ["select",              3, "set-indexing_rule-inc_idx-select"      , None                          ],
          ["HEADER_FIELD",        4, "set-indexing_rule-inc_idx-select-S"    , __mmc_set_hdr_indexing_rule   ],
          ["never_indexing"      ,2, "set-indexing_rule-naver_idx"           , None                          ],
          ["ALL",                 3, "set-indexing_rule-naver_idx-ALL"       , __mmc_set_hdr_indexing_rule   ],
          ["select",              3, "set-indexing_rule-naver_idx-select"    , None                          ],
          ["HEADER_FIELD",        4, "set-indexing_rule-naver_idx-select-S"  , __mmc_set_hdr_indexing_rule   ],
          ["batch",               0, "batch"                                 , None                          ],
          ["start",               1, "batch-start"                           , None                          ],
          ["from_file",           2, "batch-start-from_file"                 , None                          ],
          ["batch_path",          3, "batch-start-from_file-S"               , __mmc_run_batch               ],
         ]
__mmc.extend( get_api() )


def mmc_run(index, name):
    expect.instance()          
    mmc_parse.instance(__mmc, index, name)
    e = mmc_parse.getinstance()          
    sa_get_log_object().set_check_pos_fn(e.check_pos)

    e.run()
    return

    try:
        e.run()                              
    except:
        PRINT("Error. exit simulator!")
        exit_handler();


