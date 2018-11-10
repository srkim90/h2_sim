# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : dispatch_parse.py
  Release  : 1
  Date     : 2018-07-12
 
  Description : dispatch module for python
 
  Notes :
  ===================
  History
  ===================
  2018/07/12  created by Kim, Seongrae
'''
import re
import os
import sys    
import time
import termios
import fcntl
import copy
from abc import *
from time import sleep
from singleton import *
from log import *
import timeit

H2_STAT_TYPE_SEND_REQUEST   = 0
H2_STAT_TYPE_RECV_REQUEST   = 1
H2_STAT_TYPE_SEND_ANSWER    = 2
H2_STAT_TYPE_RECV_ANSWER    = 3
H2_STAT_TYPE_HTTP2_BASE     = 4

H2_FRAME_DATA               = 0
H2_FRAME_HEADERS            = 1
H2_FRAME_PRIORITY           = 2
H2_FRAME_RST_STREAM         = 3
H2_FRAME_SETTINGS           = 4
H2_FRAME_PUSH_PROMISE       = 5
H2_FRAME_PING               = 6
H2_FRAME_GOAWAY             = 7
H2_FRAME_WINDOW_UPDATE      = 8
H2_FRAME_CONTINUATION       = 9
H2_FRAME_MAGIC              = 10
H2_FRAME_SETTINGS_ACK       = 14
H2_FRAME_PING_ACK           = 16


def frame_type_to_string(n_type):
     if n_type   == H2_FRAME_DATA          :
         return "DATA"
     elif n_type == H2_FRAME_HEADERS       :
         return "HEADERS"
     elif n_type == H2_FRAME_PRIORITY      :
         return "PRIORITY"
     elif n_type == H2_FRAME_RST_STREAM    :
         return "RST_STREAM"
     elif n_type == H2_FRAME_SETTINGS      :
         return "SETTINGS"
     elif n_type == H2_FRAME_PUSH_PROMISE  :
         return "PUSH_PROMISE"
     elif n_type == H2_FRAME_PING          :
         return "PING"
     elif n_type == H2_FRAME_GOAWAY        :
         return "GOAWAY"
     elif n_type == H2_FRAME_WINDOW_UPDATE :
         return "WINDOW_UPDATE"
     elif n_type == H2_FRAME_CONTINUATION  :  
         return "CONTINUATION"
     elif n_type == H2_FRAME_SETTINGS_ACK  :  
         return "SETTINGS_ACK"
     elif n_type == H2_FRAME_PING_ACK  :  
         return "PING_ACK"
     elif n_type == H2_FRAME_MAGIC  :  
         return "MAGIC"
     else:
         return None


def get_xy():
    command = "#!/bin/bash\n" + "exec < /dev/tty\n" + "oldstty=$(stty -g)\n" + "stty raw -echo min 0\n" + 'echo -en "\033[6n" > /dev/tty\n' + "IFS=';' read -r -d R -a pos\n" + "stty $oldstty\n" + "row=$((${pos[0]:2} - 1))    # strip off the esc-[\n" + "col=$((${pos[1]} - 1))\n" + "echo $row $col\n"
    result = os.popen(command)

    pair = result.read().split(' ')

    return int(pair[1]), int(pair[0])


#class dispatch(metaclass=ABCMeta):
#    @abstractmethod
class dispatch():
    def run(uri_list, param_list, data):
        pass

class dispatch_util(singleton_instance):
    h2_stat  = [{},{},{},{},{}]
    h2_tps   = {}
    lock     = threading.Semaphore(1)

    def __init__(self, dispatch):
        self.tot_tps    = 0
        self.__dispatch = dispatch
        self.old_timeit = timeit.default_timer()
        self.old_tps    = copy.deepcopy(self.h2_stat[H2_STAT_TYPE_HTTP2_BASE])

    def reset_api_stat(self):
        self.h2_stat = [{},{},{},{},{}]
        return True

    def show_stat(self):
        result_list = []
        result_list.append("%s" % (LINE110) )
        result_list.append("%s" % ("  HTTP/2 Simulator Statistic"))
        result_list.append("%s" % (LINE110))
        for item in result_list:
            PRINT("%s" % (item))

        self.show_api_stat()
        self.show_base_stat()
        self.show_tps_stat()

    def show_base_stat(self):
        idx_newline = 5
        frame_dict  = {}
        result_list = []
        h2_stat = self.h2_stat[H2_STAT_TYPE_HTTP2_BASE]
        result_list.append(" ")
        oper_str = "  %-20s   " % ("[HTTP/2 Frames]")
        result_list.append(oper_str)


        result_list.append("%s" % (line110))

        tmp_txt = []
        n_space = [0,] * (H2_FRAME_PING_ACK + 1)
        for idx in range(len(h2_stat.keys())):
            tmp_txt.append([None, ] * (H2_FRAME_PING_ACK + 1))
        for idx, item in enumerate(h2_stat.keys()):
            tmp_txt[idx][0] = "  %s  : " % (item)
            n_space[0]      = n_space[0] if len(tmp_txt[idx][0]) < n_space[0] else len(tmp_txt[idx][0])
            for idx2, key in enumerate(sorted(h2_stat[item].keys())):
                tmp_str                = "%s=%d, " % (key, h2_stat[item][key])
                tmp_txt[idx][idx2 + 1] = "%s" % (tmp_str)
                idx3 = idx2 + 1#(idx2 + 1 % idx_newline)
                if idx3 == 0:
                    idx3 += 1
                n_space[idx3]          = n_space[idx3] if len(tmp_str) < n_space[idx3] else len(tmp_str)

        for line in tmp_txt:
            oper_str = ""
            for idx, line_at in enumerate(line):
                if line_at == None:
                    break
                idx3 = idx2 + 1#(idx2 + 1 % idx_newline)
                if idx3 == 0:
                     idx3 += 1
                #formet = "%-" + str(n_space[idx3]) + "s"
                formet = "%-" + "s"
                oper_str += formet % (line_at)
            result_list.append(oper_str)

        result_list.append("%s" % (LINE110))
 
        for item in result_list:
            PRINT("%s" % (item))

    def show_api_stat(self, ln_sleep=1.0):
        tot_tps = 0

        result_list = []

        for idx, h2_stat in enumerate(self.h2_stat):
            if len(h2_stat.keys()) == 0:
                continue

            r_code_dict = []
            if idx == 0:
                #result_list.append("[Request-Send]")
                oper_str = "  %-32s   " % ("[Request-Send]")
            elif idx == 2:
                #result_list.append("[Request-Recv]")
                oper_str = "  %-32s   " % ("[Answer-Send]")
            elif idx == 1:
                #result_list.append("[Answer-Send]")
                oper_str = "  %-32s   " % ("[Request-Recv]")
            elif idx == 3:
                #result_list.append("[Answer-Recv]")
                oper_str = "  %-32s   " % ("[Answer-Recv]")
            else:
                continue
                #oper_str = "  %-32s   " % ("[?????]")
            result_list.append(" ")

            for item in h2_stat.keys():
                pos = h2_stat[item] 
                for oper in pos.keys():
                    if not r_code_dict.count(oper):
                        r_code_dict.append(oper)

            for item in r_code_dict:
                oper_str += "%-10s " % (item)

            #if oper_str == "":
            #    PRINT("There is no operation statistic")
            #    return

            result_list.append("%s" % (oper_str))
            result_list.append("%s" % (line110))
            for item in h2_stat.keys():
                pos = h2_stat[item] 
                oper_str = ""
                for idx2 in r_code_dict:
                    if idx2 not in pos:
                        oper_str += "%-10s " % ("0")
                        continue
                    oper_str += "%-10s " % (pos[idx2])
                    if idx == 3 or idx == 2:
                        tot_tps  += int(pos[idx2])
                result_list.append("  %-32s : %s" % (item, oper_str))
            result_list.append("%s" % (LINE110))

        '''
        result_list.append(" ")
        result_list.append("  [Performance]")
        result_list.append("%s" % (line110))
        #if tot_tps != 0:
        time_delta = timeit.default_timer() - self.old_timeit
        result_list.append("  TPS   : %d" % ((tot_tps - self.tot_tps) / time_delta) )

        self.tot_tps = tot_tps
        result_list.append("  TOTAL : %s" % (tot_tps) )
        result_list.append("%s" % (LINE110) )
        '''

        #x, y = get_xy()
        #PRINT("\033[%dd\033[%dG" % (y - len(result_list), 0));
        #
        #for i in range(len(result_list)):
        #    print("%-90s" % (' '))
        #
        #PRINT("\033[%dd\033[%dG" % (y - len(result_list), 0));

        for item in result_list:
            PRINT("%s" % (item))


    def show_tps_stat(self):
        idx_newline = 5
        frame_dict  = {}
        result_list = []
        result_list.append(" ")
        oper_str = "  %-20s   " % ("[Performance]")
        result_list.append(oper_str)
        result_list.append("%s" % (line110))

        time_delta = timeit.default_timer() - self.old_timeit
        self.old_timeit = timeit.default_timer()

        for key in self.h2_tps.keys():
            a_item = self.h2_tps[key]
            if "OUT" in a_item.keys() and "IN" in a_item.keys():
                in_val    = a_item["IN"]
                out_val   = a_item["OUT"]
                total_val = in_val + out_val
                if key in self.old_tps.keys():
                    in_tps    = int((a_item["IN"] - self.old_tps[key]["IN"]) / time_delta)
                    out_tps   = int((a_item["OUT"] -  self.old_tps[key]["OUT"]) / time_delta)
                else:
                    in_tps    = 0
                    out_tps   = 0
                total_tps = in_tps + out_tps

                if key == "TRAFFIC":
                    in_val  = "%0.2fMB" % (float(in_val)  / (1024.0 * 1024.0))
                    out_val = "%0.2fMB" % (float(out_val) / (1024.0 * 1024.0))
                    total_val = "%0.2fMB" % (float(total_val) / (1024.0 * 1024.0))
                    in_tps  = "%0.2fMB" % (float(in_tps)  / (1024.0 * 1024.0))
                    out_tps = "%0.2fMB" % (float(out_tps) / (1024.0 * 1024.0))
                    total_tps = "%0.2fMB" % (float(total_tps) / (1024.0 * 1024.0))
                in_val     = "%s (%s/s)" % (in_val, in_tps)
                out_val    = "%s (%s/s)" % (out_val, out_tps)
                total_val  = "%s (%s/s)" % (total_val, total_tps)
                oper_str   = "  %-10s: IN=%-24s OUT=%-24s TOTAL=%-24s" % (key, in_val, out_val, total_val)
            else:
                pass

            result_list.append(oper_str)
            
        result_list.append("%s" % (LINE110))

        for item in result_list:
            PRINT("%s" % (item))

        self.old_tps    = copy.deepcopy(self.h2_tps)


    def set_tps_stat(self, item, direction="OUT", value=1, obj=None, stat_rule="SUM"):
        if stat_rule != "SUM" and obj == None:
            return

        if direction != "IN" and direction != "OUT":
            return

        self.lock.acquire()
        if item not in self.h2_tps.keys():
            self.h2_tps[item] = {"IN" : 0, "OUT" : 0} if stat_rule == "SUM" else {obj:0}
        
        if stat_rule == "SUM":
            self.h2_tps[item][direction] += value
        else:
            self.h2_tps[item][obj] = value
        self.lock.release()

    def set_base_stat(self, n_dir, n_frame_type):
        h2_stat = self.h2_stat[H2_STAT_TYPE_HTTP2_BASE]

        if n_frame_type < H2_FRAME_DATA or n_frame_type > H2_FRAME_PING_ACK:
            return False

        '''
        {
            "RECV" : { 0: 10, 1: 13 2: 110, ...  },
            "SEND" : { 0: 10, 1: 13 2: 110, ...  }
        }
        '''

        s_frame_type = frame_type_to_string(n_frame_type)

        self.lock.acquire()

        if n_dir not in h2_stat.keys():
            h2_stat[n_dir] = {}
        in_stat = h2_stat[n_dir]
        if s_frame_type not in in_stat.keys():
            in_stat[s_frame_type] = 0
        in_stat[s_frame_type] += 1

        self.lock.release()

        return True

    def set_api_stat(self, method, uri, rCode, stat_type):

        if stat_type < 0 or stat_type > 3:
            LOG(LOG_CRT, "Error: Invalid stat type=%s" % (stat_type))
            return None

        if method == None:
            method = "None"
        if uri == None:
            uri = "/None"

        plist=uri.split('?')

        uri_list    = []
        value_list  = {}

        uri_list    = plist[0].split('/')
        if "" in uri_list:
            uri_list.remove("")
        uri_count = len(uri_list)
        selectd_item = "Unknown-API"

        for item in self.__dispatch:
            if item[1] != method:
                continue
            __uri_list    = item[2].split('/')
            __uri_list.remove("")

            i         = 0
            for utem2 in __uri_list:
                if i >= uri_count:
                    break
                if utem2 == uri_list[i]:
                    i+=1
                elif  utem2[0] == '{' and utem2[-1] == '}':
                    i+=1
                else:
                    break
            
                #print ("%s:%s %d, %d" % (uri, item[2], uri_count, i))
                if uri_count == i:
                    selectd_item = item[0]
                    break

        self.lock.acquire()
        stat_id = "%-6s: %s" % (method, selectd_item)
        h2_stat = self.h2_stat[stat_type]
        if stat_id not in h2_stat:
            h2_stat[stat_id] = {}

        pos = h2_stat[stat_id]

        if rCode == None:
            rCode = "ALL"
        if rCode not in pos:
            pos[rCode] = 0

        pos[rCode] += 1
        self.lock.release()

    def do_request_dispatch(self, req_method, req_path, req_data):

        plist=req_path.split('?')

        uri_list    = []
        value_list  = {}
        pram_list   = {}

        uri_list    = plist[0].split('/')
        if "" in uri_list:
            uri_list.remove("")
        uri_count = len(uri_list)
        if len (plist) > 1:
            tmp_list  = plist[1].split('&')
            for item2 in tmp_list:
                #value_list.append(item2.split('='))
                tmptmp = item2.split('=')
                if len(tmptmp) == 2:
                    value_list[tmptmp[0]] = tmptmp[1]

        #print("%s , %s" % (uri_list, value_list))

        for item in self.__dispatch:
            if item[1] != req_method:
                continue
            __uri_list    = item[2].split('/')
            __uri_list.remove("")
            #print("%s" % (__uri_list ))

            i         = 0
            pram_list = {}
            for utem2 in __uri_list:
                if i >= uri_count:
                    break
                if utem2 == uri_list[i]:
                    i+=1
                elif  utem2[0] == '{' and utem2[-1] == '}':
                    pram_list[utem2[1:-1]] = uri_list[i]
                    i+=1
                else:
                    break
            
            if len(__uri_list) == i and uri_count == i:
                rCode, rData =  item[3].run(pram_list, value_list, req_data)
                #self.set_api_stat(req_method, req_path, rCode)

                return rCode, rData

        return 400, None

if  __name__ == '__main__':
    sa_initlog("TEST")

    dispatch_util.instance(__dispatch)
    e = dispatch_util.getinstance()

    e.do_request_dispatch("GET"   , "/nudr-dr/v1/subscription-data/450081060000000/authentication-data", None)
    e.do_request_dispatch("PATCH" , "/nudr-dr/v1/subscription-data/450081060000000/authentication-data/eps-auth-data", None)
    e.do_request_dispatch("PATCH" , "/nudr-dr/v1/subscription-data/450081060000000/authentication-data/ims-auth-data", None)
    e.do_request_dispatch("PATCH" , "/nudr-dr/v1/subscription-data/450081060000000/authentication-data/wifi-auth-data", None)

