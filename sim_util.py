# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : sim_util.py
  Release  : 1
  Date     : 2018-08-28
 
  Description : utility for python
 
  Notes :
  ===================
  History
  ===================
  2018/08/28  created by Kim, Seongrae
'''
import os
import pytz
import timeit
import datetime 

def get_old_time(n_day):
    now = datetime.datetime.now(tz=pytz.timezone("Asia/Seoul"))
    old = now - datetime.timedelta(n_day)
    #print("%s-%02d-%02d %02d:%02d:%02d" % (old.year, old.month, old.day, old.hour, old.minute, old.second ))
    str_day = "%s-%02d-%02d" % (old.year, old.month, old.day)
    return old#str_day, old.weekday()


def get_now_time(format_string="%Y-%m-%d"):
    now = datetime.datetime.now(tz=pytz.timezone("Asia/Seoul"))
    #old = now - datetime.timedelta(n_day)
    #print("%s-%02d-%02d %02d:%02d:%02d" % (old.year, old.month, old.day, old.hour, old.minute, old.second, old.milliseconds ))
    #yyyy:mm:dd:hh:MM:ss
    
    #  get_now_time("%Y-%m-%d %H:%M:%S %f")

    '''
    %Y  Year                        2013, 2014,     ... , 9999
    %y  Year                        17, 18,         ... , 99  
    %m  Month                       01, 02,         ... , 12
    %d  Day                         01, 02,         ... , 31
    %H  Hour (24-hour clock)        00, 01,         ... , 23
    %M  Minute                      00, 01,         ... , 59
    %S  Second                      00, 01,         ... , 59
    %f  Microsecond                 000000, 000001, ... , 999999
    '''

    #if format_string == "yyyy:mm:dd":
    #    str_day = "%s-%02d-%02d" % (old.year, old.month, old.day)
    return now.strftime(format_string)

#def get_old_time_list()


PYTHON_TYPE_CPYTHON = 0
PYTHON_TYPE_PYPY    = 1
g_python_type       =-1

def get_python_runtime():

    global g_python_type
    if g_python_type != -1:
        return g_python_type

    from subprocess import Popen, PIPE
    for line in Popen(['ps', 'aux'], shell=False, stdout=PIPE).stdout:
        if line.find("%s" % (os.getpid())) == -1:
            continue
        line = line.split(' ')
        for item in line:
            if item.find('pypy') != -1:
                g_python_type = PYTHON_TYPE_PYPY
                return g_python_type
            elif item.find('python') != -1:
                g_python_type = PYTHON_TYPE_CPYTHON
                return g_python_type
            else:
                continue

    return g_python_type

f_timeit = False
g_timeit = {}
def SET_TIMEIT(l_timeit=None, description=""):
    if f_timeit == False:
        return

    global g_timeit
    if l_timeit == None:
        l_timeit = {}
    
    now_idx    = len(l_timeit.keys())
    timeit_key = "%02d %s" % ( now_idx, get_now_time("%H:%M:%S_%f")) + description
    l_timeit[timeit_key] = timeit.default_timer()

    g_timeit = l_timeit

    return l_timeit

def PRINT_TIMEIT(l_timeit=None):
    if f_timeit == False:
        return

    global g_timeit
    if l_timeit == None:
        l_timeit = g_timeit

    item_list  = sorted(l_timeit.keys())
    old_timeit = None
    for idx, key in enumerate(item_list):
        prev_timeit = l_timeit[key]
        next_timeit = l_timeit[item_list[idx+1]] if idx+1 < len(item_list) else timeit.default_timer()
        print("%s : %.6f" % (key, next_timeit - prev_timeit))

    g_timeit = {}



