# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : mmc_api.py
  Release  : 1
  Date     : 2018-08-02
 
  Description : HTTP/2 mmc module
 
  Notes :
  ===================
  History
  ===================
  2018/08/02  created by Kim, Seongrae
'''
import re
import os
import sys    
import termios
import fcntl

sys.path.insert(0, './util')
sys.path.insert(0, './.core')
sys.path.insert(0, './core')

import h2_base
from abc import *
from perf import *
from h2_util import *
from sim_exit import *
from singleton import *
from h2_trace import *
from time import sleep
from mmc_parse import *
from dispatch_parse import *
from perf_scenario import *
from mmc_build_payload import *
from interwork import h2_interwork

__api_mmc = []

def mmc_append(e):
    global __api_mmc
    __api_mmc.append(e)

def get_api():
    return __api_mmc

def send_notify(command, path, method, data):
    #PRINT("Enter MMC in '%s'" % command)

    iwk = h2_interwork.getinstance()
    nErr = iwk.h2_send_notify(method, path, data)   

def builder():
    b = payload_builder.getinstance()
    return b

def reload_config():
    return
    #e    = cfg_data.getinstance()            
    #item = e.read_data_file()

def check_null(command):
    if command == 'NULL' or command == 'null' or command == 'Null' or command == 'None' or command == 'none' or command == 'NA' or command == 'na' or command == 'N/A' or command == 'n/a' or command == "" or command == None:
        return True
    return False

def ueId_check(ueId):
    #{root:udId}
    if ueId[0] == '{' and ueId[-1] == '}':
        __ueId = ueId
        ueId = ueId[1:-1]
        ueId = ueId.split(':')
        if len(ueId) != 2:
            PRINT("Error. Invalid config tocken : ueId = %s" % (__ueId))
            sleep(0.5)
            return __ueId
        e    = cfg_data.getinstance()            
        item = e.search_data_cfg(ueId[1], ueId[0])
        if item == None:
            PRINT("Error. Notfund config tocken : ueId = %s" % (__ueId))
            sleep(0.5)
            return __ueId
        return item
    return ueId

ROOT_API="/nudr-dr/v1/subscription-data"

''' 1. Operation : subscriber_id_data '''
class __mmc_api_GET_subscriber_id_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId   = ueId_check(command[3])
        __path   = "%s/%s/subscriber-id-data" % (ROOT_API, __ueId)
        send_notify(command, __path, "GET", None)
        return
mmc_append(["subscriber_id_data"      ,  2, "send-notify-subscriber_id_data"                                   , None                                      ])
mmc_append(["UeId"                    ,  3, "send-notify-subscriber_id_data-S"                                 , None                                      ])
mmc_append(["GET"                     ,  4, "send-notify-subscriber_id_data-S-GET"                             , __mmc_api_GET_subscriber_id_data          ])
''' end of API '''



''' 2. Operation : authentication-data '''
class __mmc_api_GET_authentication_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId   = ueId_check(command[3])
        __type   = command[5]
        __path   = "%s/%s/authentication-data" % (ROOT_API, __ueId)

        if __type == "ALL":
            pass
        elif __type == "eps":
            __path += "?fields=authEpsData"
        elif __type == "ims":
            __path += "?fields=authImsData"
        elif __type == "wifi":
            __path += "?fields=authWifiData"
        else:
            PRINT("Invalid input MMC : %s" % command)
            return

        send_notify(command, __path, "GET", None)
        return
mmc_append(["authentication_data"     ,  2, "send-notify-authentication_data"                                  , None                                      ])
mmc_append(["UeId"                    ,  3, "send-notify-authentication_data-S"                                , None                                      ])
mmc_append(["GET"                     ,  4, "send-notify-authentication_data-S-GET"                            , None                                      ])
mmc_append(["ALL"                     ,  5, "send-notify-authentication_data-S-GET-ALL"                        , __mmc_api_GET_authentication_data         ])
mmc_append(["eps"                     ,  5, "send-notify-authentication_data-S-GET-eps"                        , __mmc_api_GET_authentication_data         ])
mmc_append(["ims"                     ,  5, "send-notify-authentication_data-S-GET-ims"                        , __mmc_api_GET_authentication_data         ])
mmc_append(["wifi"                    ,  5, "send-notify-authentication_data-S-GET-wifi"                       , __mmc_api_GET_authentication_data         ])

class __mmc_api_PATCH_authentication_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId   = ueId_check(command[3])
        #__type   = command[5]
        __path   = "%s/%s/authentication-data" % (ROOT_API, __ueId)
        __data   = None
        __data, name = builder().build_AuthData(__ueId)
        send_notify(command, __path, "PATCH", __data)
        return
mmc_append(["PATCH"                   ,  4, "send-notify-authentication_data-S-PATCH"                          , __mmc_api_PATCH_authentication_data       ])
''' end of API '''



''' 3. Operation : eps_am_data '''
class __mmc_api_GET_eps_am_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId   = ueId_check(command[3])
        __type   = command[5]
        __path   = "%s/%s/eps-am-data" % (ROOT_API, __ueId)

        if __type == "ALL":
            pass
        elif __type == "active_apn_data":
            __path += "/active-apn-data"
        else:
            PRINT("Invalid input MMC : %s" % command)
            return

        send_notify(command, __path, "GET", None)
        return
mmc_append(["eps_am_data"             ,  2, "send-notify-eps_am_data"                                          , None                                      ])
mmc_append(["ueId"                    ,  3, "send-notify-eps_am_data-S"                                        , None                                      ])
mmc_append(["GET"                     ,  4, "send-notify-eps_am_data-S-GET"                                    , None                                      ])
mmc_append(["ALL"                     ,  5, "send-notify-eps_am_data-S-GET-ALL"                                , __mmc_api_GET_eps_am_data                 ])
mmc_append(["active_apn_data"         ,  5, "send-notify-eps_am_data-S-GET-active_apn_data"                    , __mmc_api_GET_eps_am_data                 ])

class __mmc_api_POST_eps_am_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId    = ueId_check(command[3])
        __apn_cid = command[6]
        __path    = "%s/%s/eps-am-data/active-apn-data/%s" % (ROOT_API, __ueId, __apn_cid)
        __data, name   = builder().build_ActiveApnData(__ueId)
        send_notify(command, __path, "POST", __data)
        return
mmc_append(["POST"                    ,  4, "send-notify-eps_am_data-S-POST"                                   , None                                      ])
mmc_append(["active_apn_data"         ,  5, "send-notify-eps_am_data-S-POST-active_apn_data"                   , None                                      ])
mmc_append(["apnContextId"            ,  6, "send-notify-eps_am_data-S-POST-active_apn_data-S"                 , __mmc_api_POST_eps_am_data                ])

class __mmc_api_PUT_eps_am_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId    = ueId_check(command[3])
        __apn_cid = command[6]
        __path    = "%s/%s/eps-am-data/active-apn-data/%s" % (ROOT_API, __ueId, __apn_cid)
        __data, name   = builder().build_ActiveApnData(__ueId)
        send_notify(command, __path, "PUT", __data)
        return
mmc_append(["PUT"                     ,  4, "send-notify-eps_am_data-S-PUT"                                    , None                                      ])
mmc_append(["active_apn_data"         ,  5, "send-notify-eps_am_data-S-PUT-active_apn_data"                    , None                                      ])
mmc_append(["apnContextId"            ,  6, "send-notify-eps_am_data-S-PUT-active_apn_data-S"                  , __mmc_api_PUT_eps_am_data                 ])

class __mmc_api_DELETE_eps_am_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId    = ueId_check(command[3])
        __type    = command[5]
        if __type == "ALL":
            __path    = "%s/%s/eps-am-data/active-apn-data" % (ROOT_API, __ueId)
        else:
            __path    = "%s/%s/eps-am-data/active-apn-data" % (ROOT_API, __ueId)
            __apn_cid = command[6]
            if check_null(__apn_cid) == False:
                __path += "/%s" % __apn_cid

        send_notify(command, __path, "DELETE", None)
        return
mmc_append(["DELETE"                  ,  4, "send-notify-eps_am_data-S-DELETE"                                 , None                                      ])
mmc_append(["active_apn_data"         ,  5, "send-notify-eps_am_data-S-DELETE-active_apn_data"                 , None                                      ])
mmc_append(["ALL"                     ,  5, "send-notify-eps_am_data-S-DELETE-ALL"                             , __mmc_api_DELETE_eps_am_data              ])
mmc_append(["apnContextId"            ,  6, "send-notify-eps_am_data-S-DELETE-active_apn_data-S"               , __mmc_api_DELETE_eps_am_data              ])
''' end of API '''




''' 4. Operation : ims_am_data '''
class __mmc_api_GET_ims_am_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId   = ueId_check(command[3])
        __type   = command[5]
        __path   = "%s/%s/ims-am-data" % (ROOT_API, __ueId)

        if __type == "ALL":
            pass
        elif __type == "cscf_restore_data":
            __path += "/cscf-restore-data"
        elif __type == "as_notify_data":
            __path += "/as-notify-data"
        else:
            PRINT("Invalid input MMC : %s" % command)
            return

        send_notify(command, __path, "GET", None)
        return
mmc_append(["ims_am_data"             ,  2, "send-notify-ims_am_data"                                          , None                                      ])
mmc_append(["ueId"                    ,  3, "send-notify-ims_am_data-S"                                        , None                                      ])
mmc_append(["GET"                     ,  4, "send-notify-ims_am_data-S-GET"                                    , None                                      ])
mmc_append(["ALL"                     ,  5, "send-notify-ims_am_data-S-GET-ALL"                                , __mmc_api_GET_ims_am_data                 ])
mmc_append(["cscf_restore_data"       ,  5, "send-notify-ims_am_data-S-GET-cscf_restore_data"                  , __mmc_api_GET_ims_am_data                 ])
mmc_append(["as_notify_data"          ,  5, "send-notify-ims_am_data-S-GET-as_notify_data"                     , __mmc_api_GET_ims_am_data                 ])

class __mmc_api_POST_ims_am_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId              = ueId_check(command[3])
        __type              = command[5]
        imsPrivateUserId    = None
        asGroupId           = None
        dataReferenceId     = None
        __data              = None
        __path    = "%s/%s/ims-am-data" % (ROOT_API, __ueId)

        if __type == "cscf_restore_data":
            imsPrivateUserId    = command[6]
            __path             += "/cscf-restore-data/%s" % (imsPrivateUserId)
            __data, name   = builder().build_CscfRestoreData(__ueId)
        elif __type == "as_notify_data":
            asGroupId           = command[6]
            dataReferenceId     = command[7]
            __path             += "/as-notify-data/%s/%s" % (asGroupId, dataReferenceId)
            __data, name   = builder().build_AsNotifyData(__ueId)
        
        send_notify(command, __path, "POST", __data)
        return
mmc_append(["POST"                    ,  4, "send-notify-ims_am_data-S-POST"                                   , None                                      ])
mmc_append(["cscf_restore_data"       ,  5, "send-notify-ims_am_data-S-POST-cscf_restore_data"                 , None                                      ])
mmc_append(["imsPrivateUserId"        ,  6, "send-notify-ims_am_data-S-POST-cscf_restore_data-S"               , __mmc_api_POST_ims_am_data                ])
mmc_append(["as_notify_data"          ,  5, "send-notify-ims_am_data-S-POST-as_notify_data"                    , None                                      ])
mmc_append(["asGroupId"               ,  6, "send-notify-ims_am_data-S-POST-as_notify_data-S"                  , None                                      ])
mmc_append(["dataReferenceId"         ,  7, "send-notify-ims_am_data-S-POST-as_notify_data-S-S"                , __mmc_api_POST_ims_am_data                ])

class __mmc_api_PUT_ims_am_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId              = ueId_check(command[3])
        __type              = command[5]
        imsPrivateUserId    = None
        asGroupId           = None
        dataReferenceId     = None
        __data              = None
        __path    = "%s/%s/ims-am-data" % (ROOT_API, __ueId)

        if __type == "cscf_restore_data":
            imsPrivateUserId    = command[6]
            __path             += "/cscf-restore-data/%s" % (imsPrivateUserId)
            __data, name   = builder().build_CscfRestoreData(__ueId)
        elif __type == "as_notify_data":
            asGroupId           = command[6]
            dataReferenceId     = command[7]
            __path             += "/as-notify-data/%s/%s" % (asGroupId, dataReferenceId)
            __data, name   = builder().build_AsNotifyData(__ueId)
        
        send_notify(command, __path, "PUT", __data)
        return
mmc_append(["PUT"                     ,  4, "send-notify-ims_am_data-S-PUT"                                    , None                                      ])
mmc_append(["cscf_restore_data"       ,  5, "send-notify-ims_am_data-S-PUT-cscf_restore_data"                  , None                                      ])
mmc_append(["imsPrivateUserId"        ,  6, "send-notify-ims_am_data-S-PUT-cscf_restore_data-S"                , __mmc_api_PUT_ims_am_data                 ])
mmc_append(["as_notify_data"          ,  5, "send-notify-ims_am_data-S-PUT-as_notify_data"                     , None                                      ])
mmc_append(["asGroupId"               ,  6, "send-notify-ims_am_data-S-PUT-as_notify_data-S"                   , None                                      ])
mmc_append(["dataReferenceId"         ,  7, "send-notify-ims_am_data-S-PUT-as_notify_data-S-S"                 , __mmc_api_PUT_ims_am_data                 ])

class __mmc_api_DELETE_ims_am_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId              = ueId_check(command[3])
        __type              = command[5]
        imsPrivateUserId    = None
        asGroupId           = None
        dataReferenceId     = None
        __data              = None
        __path    = "%s/%s/ims-am-data" % (ROOT_API, __ueId)

        if __type == "cscf_restore_data":
            __path             += "/cscf-restore-data"
        elif __type == "as_notify_data":
            __path             += "/as-notify-data"
            if command[6] != "ALL":
                asGroupId           = command[7]
                dataReferenceId     = command[8]
                if check_null(asGroupId) == False and check_null(dataReferenceId) == False:
                    __path             += "/%s/%s" % (asGroupId, dataReferenceId)
        
        send_notify(command, __path, "DELETE", __data)
        return
mmc_append(["DELETE"                  ,  4, "send-notify-ims_am_data-S-DELETE"                                 , None                                      ])
#mmc_append(["cscf_restore_data"       ,  5, "send-notify-ims_am_data-S-DELETE-cscf_restore_data"               , None                                      ])
#mmc_append(["imsPrivateUserId"        ,  6, "send-notify-ims_am_data-S-DELETE-cscf_restore_data-S"             , __mmc_api_DELETE_ims_am_data              ])
mmc_append(["as_notify_data"          ,  5, "send-notify-ims_am_data-S-DELETE-as_notify_data"                  , None                                      ])
mmc_append(["ALL"                     ,  6, "send-notify-ims_am_data-S-DELETE-as_notify_data-ALL"              , __mmc_api_DELETE_ims_am_data              ])
mmc_append(["SELECT"                  ,  6, "send-notify-ims_am_data-S-DELETE-as_notify_data-SELECT"           , None                                      ])
mmc_append(["asGroupId"               ,  7, "send-notify-ims_am_data-S-DELETE-as_notify_data-SELECT-S"         , None                                      ])
mmc_append(["dataReferenceId"         ,  8, "send-notify-ims_am_data-S-DELETE-as_notify_data-SELECT-S-S"       , __mmc_api_DELETE_ims_am_data              ])
mmc_append(["cscf_restore_data"       ,  5, "send-notify-ims_am_data-S-DELETE-cscf_restore_data"               , __mmc_api_DELETE_ims_am_data              ])
''' end of API '''




''' 5. Operation : location_data '''

#{CommLocationData} , {CsLocationData}, {PsLocationData}, {EpsLocationData}, {ImsLocationData}, {AsLocationData}
class __mmc_api_GET_location_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId    = ueId_check(command[3])
        __type    = command[5]
        __mask    = ""
        __path    = "%s/%s/location-data" % (ROOT_API, __ueId)

        if __type == "ALL":
            __mask = ""
        elif __type == "BITMASK":
            __mask = command[6]
        elif __type == "SELECT":
            item = command[6]
            if item == "CommLocationData":
                __mask += '0'
            if item == "CsLocationData":
                __mask += '1'
            if item == "PsLocationData":
                __mask += '2'
            if item == "EpsLocationData":
                __mask += '3'
            if item == "ImsLocationData":
                __mask += '4'
            if item == "AsLocationData":
                __mask += '5'

        if __mask != "":
            __path += "?fields="

        for i in __mask:
            if i == '1':
                __path += "/CsLocationData,"
            elif i == '2':
                __path += "/PsLocationData,"
            elif i == '3':
                __path += "/EpsLocationData,"
            elif i == '4':
                __path += "/ImsLocationData,"
            elif i == '5':
                __path += "/AsLocationData,"
 
        if __path[-1] == ',':
            __path = __path[0:-1]

        send_notify(command, __path, "GET", None)
        return
mmc_append(["location_data"   ,  2, "send-notify-location_data"                                 , None                         ])
mmc_append(["ueId"            ,  3, "send-notify-location_data-S"                               , None                         ])
mmc_append(["GET"             ,  4, "send-notify-location_data-S-GET"                           , None                         ])
mmc_append(["ALL"             ,  5, "send-notify-location_data-S-GET-ALL"                       , __mmc_api_GET_location_data  ])
mmc_append(["SELECT"          ,  5, "send-notify-location_data-S-GET-SELECT"                    , None                         ])
mmc_append(["BITMASK"         ,  5, "send-notify-location_data-S-GET-BITMASK"                   , None                         ])
mmc_append(["CsLocationData"  ,  6, "send-notify-location_data-S-GET-SELECT-CsLocationData"     , __mmc_api_GET_location_data  ])
mmc_append(["PsLocationData"  ,  6, "send-notify-location_data-S-GET-SELECT-PsLocationData"     , __mmc_api_GET_location_data  ])
mmc_append(["EpsLocationData" ,  6, "send-notify-location_data-S-GET-SELECT-EpsLocationData"    , __mmc_api_GET_location_data  ])
mmc_append(["ImsLocationData" ,  6, "send-notify-location_data-S-GET-SELECT-ImsLocationData"    , __mmc_api_GET_location_data  ])
mmc_append(["AsLocationData"  ,  6, "send-notify-location_data-S-GET-SELECT-AsLocationData"     , __mmc_api_GET_location_data  ])
mmc_append(["__bit_flags"     ,  6, "send-notify-location_data-S-GET-BITMASK-S"                 , __mmc_api_GET_location_data  ])

class __mmc_api_PATCH_location_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId    = ueId_check(command[3])
        __type    = command[5]
        __mask    = ""
        __path    = "%s/%s/location-data" % (ROOT_API, __ueId)
        __json    = {}

        if __type == "ALL":
            __mask = "012345"
        elif __type == "BITMASK":
            __mask = command[6]
        elif __type == "SELECT":
            item = command[6]
            if item == "CommLocationData":
                __mask += '0'
            if item == "CsLocationData":
                __mask += '1'
            if item == "PsLocationData":
                __mask += '2'
            if item == "EpsLocationData":
                __mask += '3'
            if item == "ImsLocationData":
                __mask += '4'
            if item == "AsLocationData":
                __mask += '5'

        for i in __mask:
            __data = None
            if i == '0':
                __data, name   = builder().build_CommLocationData(__ueId)
                __json[name]   = __data
            elif i == '1':
                __data, name   = builder().build_CsLocationData(__ueId)
                __json[name]   = __data
            elif i == '2':
                __data, name   = builder().build_PsLocationData(__ueId)
                __json[name]   = __data
            elif i == '3':
                __data, name   = builder().build_EpsLocationData(__ueId)
                __json[name]   = __data
            elif i == '4':
                __data, name   = builder().build_ImsLocationData(__ueId)
                __json[name]   = __data
            elif i == '5':
                __data, name   = builder().build_AsLocationData(__ueId)
                __json[name]   = __data
            #print("i=%s" % __data)
 
        #if len(__json) == 1:
        #    __json = __json[0]   

        send_notify(command, __path, "PATCH", __json)
        return
mmc_append(["PATCH"            ,  4, "send-notify-location_data-S-PATCH"                         , None                          ])
mmc_append(["ALL"              ,  5, "send-notify-location_data-S-PATCH-ALL"                     , __mmc_api_PATCH_location_data ])
mmc_append(["SELECT"           ,  5, "send-notify-location_data-S-PATCH-SELECT"                  , None                          ])
mmc_append(["BITMASK"          ,  5, "send-notify-location_data-S-PATCH-BITMASK"                 , None                          ])
mmc_append(["CommLocationData" ,  6, "send-notify-location_data-S-PATCH-SELECT-CommLocationData" , __mmc_api_PATCH_location_data ])
mmc_append(["CsLocationData"   ,  6, "send-notify-location_data-S-PATCH-SELECT-CsLocationData"   , __mmc_api_PATCH_location_data ])
mmc_append(["PsLocationData"   ,  6, "send-notify-location_data-S-PATCH-SELECT-PsLocationData"   , __mmc_api_PATCH_location_data ])
mmc_append(["EpsLocationData"  ,  6, "send-notify-location_data-S-PATCH-SELECT-EpsLocationData"  , __mmc_api_PATCH_location_data ])
mmc_append(["ImsLocationData"  ,  6, "send-notify-location_data-S-PATCH-SELECT-ImsLocationData"  , __mmc_api_PATCH_location_data ])
mmc_append(["AsLocationData"   ,  6, "send-notify-location_data-S-PATCH-SELECT-AsLocationData"   , __mmc_api_PATCH_location_data ])
mmc_append(["__bit_flags"      ,  6, "send-notify-location_data-S-PATCH-BITMASK-S"               , __mmc_api_PATCH_location_data ])
''' end of API '''



''' 6. Operation : supplement_service_data '''
class __mmc_api_GET_supplement_service_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId    = ueId_check(command[3])
        __type    = command[5]
        __mask    = ""
        __path    = "%s/%s/supplement-service-data" % (ROOT_API, __ueId)

        if __type == "ALL":
            __mask = ""
        elif __type == "BITMASK":
            __mask = command[6]
        elif __type == "SELECT":
            item = command[6]
            if item == "BasicServiceData":
                __mask += '0'
            if item == "CFServiceData":
                __mask += '1'
            if item == "SNDServiceData":
                __mask += '2'
            if item == "ImsServiceData":
                __mask += '3'
            if item == "InServiceData":
                __mask += '4'
            if item == "VirtualServiceData":
                __mask += '5'
            if item == "BSGServiceData":
                __mask += '6'

        if __mask != "":
            __path += "?fields="

        for i in __mask:
            if i == '0':
                __path += "/BasicServiceData,"
            elif i == '1':
                __path += "/CFServiceData,"
            elif i == '2':
                __path += "/SNDServiceData,"
            elif i == '3':
                __path += "/ImsServiceData,"
            elif i == '4':
                __path += "/InServiceData,"
            elif i == '5':
                __path += "/VirtualServiceData,"
            elif i == '6':
                __path += "/BSGServiceData,"

        if __path[-1] == ',':
            __path = __path[0:-1]

        send_notify(command, __path, "GET", None)

        return
mmc_append(["supplement_service_data" ,  2, "send-notify-supplement_service_data"                                  , None                                       ])
mmc_append(["ueId"                    ,  3, "send-notify-supplement_service_data-S"                                , None                                       ])
mmc_append(["GET"                     ,  4, "send-notify-supplement_service_data-S-GET"                            , None                                       ])
mmc_append(["ALL"                     ,  5, "send-notify-supplement_service_data-S-GET-ALL"                        , __mmc_api_GET_supplement_service_data      ])
mmc_append(["SELECT"                  ,  5, "send-notify-supplement_service_data-S-GET-SELECT"                     , None                                       ])
mmc_append(["BITMASK"                 ,  5, "send-notify-supplement_service_data-S-GET-BITMASK"                    , None                                       ])
mmc_append(["BasicServiceData"        ,  6, "send-notify-supplement_service_data-S-GET-SELECT-BasicServiceData"    , __mmc_api_GET_supplement_service_data      ])
mmc_append(["CFServiceData"           ,  6, "send-notify-supplement_service_data-S-GET-SELECT-CFServiceData"       , __mmc_api_GET_supplement_service_data      ])
mmc_append(["SNDServiceData"          ,  6, "send-notify-supplement_service_data-S-GET-SELECT-SNDServiceData"      , __mmc_api_GET_supplement_service_data      ])
mmc_append(["ImsServiceData"          ,  6, "send-notify-supplement_service_data-S-GET-SELECT-ImsServiceData"      , __mmc_api_GET_supplement_service_data      ])
mmc_append(["InServiceData"           ,  6, "send-notify-supplement_service_data-S-GET-SELECT-InServiceData"       , __mmc_api_GET_supplement_service_data      ])
mmc_append(["VirtualServiceData"      ,  6, "send-notify-supplement_service_data-S-GET-SELECT-VirtualServiceData"  , __mmc_api_GET_supplement_service_data      ])
mmc_append(["BSGServiceData"          ,  6, "send-notify-supplement_service_data-S-GET-SELECT-BSGServiceData    "  , __mmc_api_GET_supplement_service_data      ])
mmc_append(["__bit_flags"             ,  6, "send-notify-supplement_service_data-S-GET-BITMASK-S"                  , __mmc_api_GET_supplement_service_data      ])

class __mmc_api_PATCH_supplement_service_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId   = ueId_check(command[3])
        __type   = command[5]
        __path   = "%s/%s/supplement-service-data" % (ROOT_API, __ueId)
        __data   = None
        name     = None

        if __type == "BasicServiceData":
            #__path += "basic-service-data"
            __data, name   = builder().build_BasicServiceData(__ueId)
        elif __type == "CFServiceData":
            #__path += "cf_service-data"
            __data, name   = builder().build_CFServiceData(__ueId)
        elif __type == "SNDServiceData":
            #__path += "snd-service-data"
            __data, name   = builder().build_SNDServiceData(__ueId)
        elif __type == "ImsServiceData":
            #__path += "ims-service-data"
            __data, name   = builder().build_ImsServiceData(__ueId)
        elif __type == "InServiceData":
            #__path += "in-service-data"
            __data, name   = builder().build_InServiceData(__ueId)
        elif __type == "VirtualServiceData":
            #__path += "virtual-service-data"
            __data, name   = builder().build_VirtualServiceData(__ueId)
        else:
            PRINT("Invalid input MMC : %s" % command)
            return

        send_notify(command, __path, "PATCH", {name : __data})
        return
mmc_append(["PATCH"                 ,  4, "send-notify-supplement_service_data-S-PATCH"                          , None                                       ])
mmc_append(["BasicServiceData"      ,  5, "send-notify-supplement_service_data-S-PATCH-BasicServiceData"       , __mmc_api_PATCH_supplement_service_data    ])
mmc_append(["CFServiceData"         ,  5, "send-notify-supplement_service_data-S-PATCH-CFServiceData"          , __mmc_api_PATCH_supplement_service_data    ])
mmc_append(["SNDServiceData"        ,  5, "send-notify-supplement_service_data-S-PATCH-SNDServiceData"         , __mmc_api_PATCH_supplement_service_data    ])
mmc_append(["ImsServiceData"        ,  5, "send-notify-supplement_service_data-S-PATCH-ImsServiceData"         , __mmc_api_PATCH_supplement_service_data    ])
mmc_append(["InServiceData"         ,  5, "send-notify-supplement_service_data-S-PATCH-InServiceData"          , __mmc_api_PATCH_supplement_service_data    ])
mmc_append(["VirtualServiceData"    ,  5, "send-notify-supplement_service_data-S-PATCH-VirtualServiceData"     , __mmc_api_PATCH_supplement_service_data    ])


''' 7. Operation : TAS Service Data '''
class __mmc_api_GET_TAS_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId    = ueId_check(command[3])
        __type    = command[5]
        __mask    = ""
        __path    = "%s/%s/tas-sm-data" % (ROOT_API, __ueId)

        if __type == "fields":
            __sub_type    = command[6]
            if __sub_type == "TasContextData":
                __path += "?fields="
                __path += "/TasContextData"
            elif __sub_type == "TasNdubData":
                __path += "?fields="
                __path += "/TasNdubData"
            else:
                pass
                #__path += "?fields="
                #__path += "/TasContextData,/TasNdubData"
        elif __type == "tas_context_data":
            __path += "/tas-context-data"
        else:
            __path += "/tas-ndub-data"
            if command[6] != "ALL":
                __path += "/" + command[7]

        send_notify(command, __path, "GET", None)
        return
mmc_append(["tas_data"        ,  2, "send-notify-tas_data"                                      , None                         ])
mmc_append(["ueId"            ,  3, "send-notify-tas_data-S"                                    , None                         ])
mmc_append(["GET"             ,  4, "send-notify-tas_data-S-GET"                                , None                         ])
mmc_append(["fields"          ,  5, "send-notify-tas_data-S-GET-fields"                         , None                         ])
#mmc_append(["TasContextData"  ,  6, "send-notify-tas_data-S-GET-fields-TasContextData"          , __mmc_api_GET_TAS_data       ])
#mmc_append(["TasNdubData"     ,  6, "send-notify-tas_data-S-GET-fields-TasNdubData"             , __mmc_api_GET_TAS_data       ])
mmc_append(["ALL"             ,  6, "send-notify-tas_data-S-GET-fields-ALL"                     , __mmc_api_GET_TAS_data       ])
mmc_append(["tas_context_data",  5, "send-notify-tas_data-S-GET-tas_context_data"               , __mmc_api_GET_TAS_data       ])
mmc_append(["tas_ndub_data"   ,  5, "send-notify-tas_data-S-GET-tas_ndub_data"                  , None                         ])
mmc_append(["ALL"             ,  6, "send-notify-tas_data-S-GET-tas_ndub_data-ALL"              , __mmc_api_GET_TAS_data       ])
mmc_append(["targetId"        ,  6, "send-notify-tas_data-S-GET-tas_ndub_data-targetId"         , None                         ])
mmc_append(["targetId"        ,  7, "send-notify-tas_data-S-GET-tas_ndub_data-targetId-S"       , __mmc_api_GET_TAS_data       ])

class __mmc_api_POST_TAS_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId     = ueId_check(command[3])
        __targetId = command[7]
        __path     = "%s/%s/tas-sm-data/tas-ndub-data/%s" % (ROOT_API, __ueId, __targetId)

        __data, name   = builder().build_TasNdubData(__ueId)
        send_notify(command, __path, "POST", __data)
        return

mmc_append(["POST"            ,  4, "send-notify-tas_data-S-POST"                                , None                         ])
mmc_append(["tas_ndub_data"   ,  5, "send-notify-tas_data-S-POST-tas_ndub_data"                  , None                         ])
mmc_append(["targetId"        ,  6, "send-notify-tas_data-S-POST-tas_ndub_data-targetId"         , None                         ])
mmc_append(["targetId"        ,  7, "send-notify-tas_data-S-POST-tas_ndub_data-targetId-S"       , __mmc_api_POST_TAS_data      ])

class __mmc_api_PATCH_TAS_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId     = ueId_check(command[3])
        __type     = ueId_check(command[5])
    
        if __type == "tas_ndub_data":
            __targetId = command[7]
            __path     = "%s/%s/tas-sm-data/tas-ndub-data/%s" % (ROOT_API, __ueId, __targetId)
            __data, name   = builder().build_TasNdubData(__ueId)
        elif __type == "tas_context_data":
            __path     = "%s/%s/tas-sm-data/tas-context-data" % (ROOT_API, __ueId)
            __data, name   = builder().build_TasContextData(__ueId)

        send_notify(command, __path, "PATCH", __data)
        return

mmc_append(["PATCH"           ,  4, "send-notify-tas_data-S-PATCH"                                , None                         ])
mmc_append(["tas_context_data",  5, "send-notify-tas_data-S-PATCH-tas_context_data"               , __mmc_api_PATCH_TAS_data     ])
mmc_append(["tas_ndub_data"   ,  5, "send-notify-tas_data-S-PATCH-tas_ndub_data"                  , None                         ])
mmc_append(["targetId"        ,  6, "send-notify-tas_data-S-PATCH-tas_ndub_data-targetId"         , None                         ])
mmc_append(["targetId"        ,  7, "send-notify-tas_data-S-PATCH-tas_ndub_data-targetId-S"       , __mmc_api_PATCH_TAS_data     ])


class __mmc_api_DELETE_TAS_data(mmc):
    @staticmethod
    def run(command):
        reload_config()
        __ueId     = ueId_check(command[3])
        __type     = ueId_check(command[6])
        __path     = "%s/%s/tas-sm-data/tas-ndub-data" % (ROOT_API, __ueId)

        if __type == "targetId":
            __targetId = "/" + command[7]
            __path    += __targetId

        send_notify(command, __path, "DELETE", None)
        return

mmc_append(["DELETE"          ,  4, "send-notify-tas_data-S-DELETE"                                , None                         ])
mmc_append(["tas_ndub_data"   ,  5, "send-notify-tas_data-S-DELETE-tas_ndub_data"                  , None                         ])
mmc_append(["ALL"             ,  6, "send-notify-tas_data-S-DELETE-tas_ndub_data-ALL"              , __mmc_api_DELETE_TAS_data    ])
mmc_append(["targetId"        ,  6, "send-notify-tas_data-S-DELETE-tas_ndub_data-targetId"         , None                         ])
mmc_append(["targetId"        ,  7, "send-notify-tas_data-S-DELETE-tas_ndub_data-targetId-S"       , __mmc_api_DELETE_TAS_data    ])





''' end of API '''
