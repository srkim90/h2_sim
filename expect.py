# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : expect.py
  Release  : 1
  Date     : 2018-08-18
 
  Description : HTTP/2 test expect module
 
  Notes :
  ===================
  History
  ===================
  2018/08/18  created by Kim, Seongrae
'''

import re
import os
import sys    
import termios
import fcntl

sys.path.insert(0, './util')

import h2_base
from abc import *
from perf import *
from h2_util import *
from sim_exit import *
from h2_trace import *
from time import sleep
from mmc_parse import *
from interwork import *
from dispatch_parse import *

JSON_IGNORE                = 0
JSON_FIND_COINCIDE_ITEM    = 1
#JSON_COMPARE_ALL           = 2

def check_json_data(result_data, find_info):
    check_list = []
    total_list = []
    for key in find_info.keys():
        item = find_info[key]
        if type(item) == dict:
            for key2 in item.keys():
                item2 = item[key2]
                str_item = "%s:%s:%s" % (key, key2, item2)
                check_list.append(str_item)
        else:
            str_item = "%s:%s" % (key, item)
            check_list.append(str_item)
    
    for key in result_data.keys():
        item = result_data[key]
        if type(item) == dict:
            for key2 in item.keys():
                item2 = item[key2]
                str_item = "%s:%s:%s" % (key, key2, item2)
                total_list.append(str_item)
        else:
            str_item = "%s:%s" % (key, item)
            total_list.append(str_item)

    error_list = []
    for i in range(len(check_list)):
        item = check_list[i]
        is_find = 0
        for item2 in total_list:
            if item2.find(item) != -1:
                is_find = 1
                break
        if is_find == 1:
            check_list[i] = ""
            #del_list.append(i)
    
    for item in check_list:
        if item != "":
            error_list.append(item)

    #for i in range(len(del_list)):
    #    del check_list[i]

    if len(error_list) != 0:
        return (False, error_list)
    return (True, None)

class expect(singleton_instance):
    used                  = False
    expect_list           = []
    result_list           = []
    g_expect_result       = 0
    g_mode                = 0
    check_request_method  = ""
    check_answer_method   = ""
    def __init__(self):
        pass
    
    def init_expect(self):
        self.expect_list           = []
        self.result_list           = []
        self.g_expect_result       = 0
        self.g_mode                = 0
        self.check_request_method  = ""
        self.check_answer_method   = ""
        self.used                  = True
        return True

    def del_expect(self):
        self.expect_list           = []
        self.result_list           = []
        self.g_expect_result       = 0
        self.g_mode                = 0
        self.check_request_method  = ""
        self.check_answer_method   = ""
        self.used                  = False
        return True


    def reset_expect_result(self):
        self.expect_list           = []
        self.result_list           = []
        self.g_expect_result       = 0
        self.g_mode                = 0
        self.check_request_method  = ""
        self.check_answer_method   = ""
        return True


    def set_expect_result(self, expect_result, mode, check_request_method, check_answer_method):
        if self.used == False:
            return False
        self.g_mode                = mode
        self.g_expect_result       = expect_result
        self.check_request_method  = check_request_method
        self.check_answer_method   = check_answer_method
        return True

    def _peint_result_a_line(self, result, analyze):

        # 1                   2                      3                    4                    5
        # first_request_uri,  first_request_method,  first_request_json,  first_answer_rcode,  first_answer_json
        # second_request_uri, second_request_method, second_request_json, second_answer_rcode, second_answer_json
        result_count            = len(result)
        second_request_uri      = None
        second_request_method   = None
        second_request_json     = None
        second_answer_rcode     = 0
        second_answer_json      = None
        is_second_request_json  = 'X'
        is_second_answer_json   = 'X'

        first_request_uri       = result[0]
        first_request_method    = result[1]
        first_request_json      = result[2]
        first_answer_rcode      = result[3]
        first_answer_json       = result[4]
        is_first_request_json   = 'X' if first_request_json == None else "O"
        is_first_answer_json    = 'X' if first_answer_json  == None else "O"
        if result_count > 5:
            second_request_uri       = result[5]
            second_request_method    = result[6]
            second_request_json      = result[7]
            second_answer_rcode      = result[8]
            second_answer_json       = result[9]
            is_second_request_json   = 'X' if second_request_json == None else "O"
            is_second_answer_json    = 'X' if second_answer_json  == None else "O"

        color = C_RED if analyze[0] == "FAIL" else C_GREEN
        test_result = "%s%s%s%s" % (C_BOLD, color, analyze[0], C_END)
        PRINT("status=%s, analyze=%s" % (test_result, analyze[1]), tab=2)
        PRINT("  %-6s:%-100s Result:%s [data: req=%s, asw=%s]" % (first_request_method, first_request_uri, first_answer_rcode, is_first_request_json, is_first_answer_json), tab=2)
        if result_count > 5:
            PRINT("  %-6s:%-100s Result:%s [data: req=%s, asw=%s]" % (second_request_method, second_request_uri, second_answer_rcode, is_second_request_json, is_second_answer_json), tab=2)

        if len(analyze) >= 3:
            for i in range(2, len(analyze)):
                PRINT("%s" % (analyze[i]), tab=3)

    def on_send_request(self, request_uri, method, expect_json=None):
        if self.used == False:
            return False
        
        if method == self.check_request_method and len(self.expect_list) == 0:
            self.expect_list = [request_uri, method, expect_json]
        elif method == self.check_answer_method and len(self.expect_list) == 5:
            self.expect_list.append(request_uri)
            self.expect_list.append(method)
            self.expect_list.append(expect_json)
        else:
            return False
        return True

    def on_recv_answer(self, uri, method, r_code, json):
        if self.used == False:
            return False

        if  method == self.check_request_method and len(self.expect_list) == 3:
            self.expect_list.append(r_code)
            self.expect_list.append(json)
            if self.check_request_method != self.check_answer_method:
                return False
        elif method != self.check_answer_method:
            return False
        else:
            self.expect_list.append(r_code)
            self.expect_list.append(json)

        if len(self.expect_list) == 0:
            return False



        '''
        expect_result = self.g_expect_result
        expect_json   = self.expect_list[1]
        request_uri   = self.expect_list[0]
        request_rcode = self.expect_list[2]
        mode          = self.g_mode

        self.g_expect_result       = 0
        self.g_mode                = 0
        self.check_request_method  = ""
        self.check_answer_method   = ""
        i = 1
        for item in self.expect_list:
            print ("%02d:  %s" % (i, item))
            i += 1
        
        self.reset_expect_result()
        return
        '''
        # 1                   2                      3                    4                    5
        # first_request_uri,  first_request_method,  first_request_json,  first_answer_rcode,  first_answer_json
        # second_request_uri, second_request_method, second_request_json, second_answer_rcode, second_answer_json
        second_request_uri      = None
        second_request_method   = None
        second_request_json     = None
        second_answer_rcode     = 0
        second_answer_json      = None

        first_request_uri       = self.expect_list[0]
        first_request_method    = self.expect_list[1]
        first_request_json      = self.expect_list[2]
        first_answer_rcode      = self.expect_list[3]
        first_answer_json       = self.expect_list[4]
        #PRINT("%s, %s, %s, %s, %s" % (first_request_uri, first_request_method, first_request_json, first_answer_rcode, first_answer_json))
        expect_json             = first_answer_json
        if len(self.expect_list) > 5:
            second_request_uri       = self.expect_list[5]
            second_request_method    = self.expect_list[6]
            second_request_json      = self.expect_list[7]
            second_answer_rcode      = self.expect_list[8]
            second_answer_json       = self.expect_list[9]
            expect_json              = second_answer_json
            #PRINT("%s, %s, %s, %s, %s" % (second_request_uri, second_request_method, second_request_json, second_answer_rcode, second_answer_json))

        mode          = self.g_mode
        result        = self.expect_list
        analyze       = []
        expect_result = self.g_expect_result
        self.reset_expect_result()


        if first_answer_rcode != expect_result:
            analyze.append("FAIL")
            analyze.append("[RESULT CODE ERROR] : expected result codes=%s, but received=%s" % (expect_result, first_answer_rcode))
        elif second_answer_rcode > 299 and first_request_method != "DELETE" :
            analyze.append("FAIL")
            analyze.append("[RESULT CODE ERROR] : error! when doing %s operation, result code = %s" % (second_request_method, second_answer_rcode))
        elif mode == JSON_FIND_COINCIDE_ITEM :
            if second_answer_json != None and second_answer_json != [] and first_request_json != None and first_request_json != []:
                nErr, notfoud_list = check_json_data(second_answer_json, first_request_json)
                if nErr == False:
                    analyze.append("FAIL")
                    analyze.append("[JSON DATA ERROR] : do not match '%s json' and '%s json'" % (first_request_method, second_request_method))
                    for err_item in notfoud_list:
                        str_error = "error in : %s" % (err_item)
                        analyze.append(str_error)
            else:
                analyze.append("FAIL")
                analyze.append("[JSON DATA ERROR] : no json message")
        if len(analyze) == 0:
            analyze.append("OK")
            analyze.append("No Error")

        self._peint_result_a_line(result, analyze)
        return (True, result)

    def print_expect_result(self):
        if self.used == False:
            return False


        return True




