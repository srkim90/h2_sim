# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : dispatch.py
  Release  : 1
  Date     : 2018-07-13
 
  Description : HTTP/2 dispatch module
 
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

from abc import *
from time import sleep

from dispatch_parse import *
from peer import h2_peer
from sim_exit import *
from h2_util import *
from h2_trace import *
from random import *


'''
    <examples>
        GET : {apiRoot}/nudr-dr/v1/subscription-data/{ueId}/authentication-data?    
        http://192.168.2.141:9990/nudr-dr/v1/subscription-data/450081060000000/authentication-data
        http://192.168.2.141:9990/nudr-dr/v1/subscription-data/450081060000000/authentication-data?request-domain=EPS
        http://192.168.2.141:9990/nudr-dr/v1/subscription-data/450081060000000/authentication-data?request-domain=IMS
        http://192.168.2.141:9990/nudr-dr/v1/subscription-data/450081060000000/authentication-data?request-domain=WIFI
        PATCH : {apiRoot}/nudr-dr/v1/subscription-data/{ueId}/authentication-data/xxx-auth-data
        http://192.168.2.141:9990/nudr-dr/v1/subscription-data/450081060000000/authentication-data/eps-auth-data
        http://192.168.2.141:9990/nudr-dr/v1/subscription-data/450081060000000/authentication-data/ims-auth-data
        http://192.168.2.141:9990/nudr-dr/v1/subscription-data/450081060000000/authentication-data/wifi-auth-data
'''

class __dispatch_GET_authentication_data(dispatch):
    @staticmethod
    def run(uri_list, param_list, data):
        ueId = uri_list["ueId"]

        if len(param_list) != 0:
            request_domain  = param_list["request-domain"]
        else:
            request_domain = None

        result_data = { "Session-Id"                        : "pcscf3a.ktlte.com;0;450072100000001", 
                        "Auth-Application-Id"               : 16777236,
                        "Origin-Host"                       : "pcscf3a.ktlte.com",
                        "Origin-Realm"                      : "ktlte.com",
                        "Destination-Realm"                 : "kt.com",
                        "Reservation-Priority"              : 1,
                        "Media-Component-Description"       :  
                         {  "Media-Component-Number"        : 1,
                            "Media-Sub-Component"           :
                             {  "Flow-Number"               : 1,
                                "Flow-Description"          : "permit out 6 from 118.235.253.106 10000 to 120.1.1.1 40000",
                                "Flow-Description"          : "permit in 6 from 120.1.1.1 40000 to 118.235.253.106 10000",
                                "Flow-Usage"                : 0 },
                            "AF-Application-Identifier"     : "75726e3a75726e2d373a336770702d736572766963652e696d732e696373692e6d6d74656c",
                            "Media-Type"                    : 0,
                            "Max-Requested-Bandwidth-UL"    : 20000,
                            "Max-Requested-Bandwidth-DL"    : 20000,
                            "Flow-Status"                   : 2 },
                        "Service-Info-Status"               : 0,
                        "AF-Charging-Identifier"            : "6368617267696e672d31",
                        "SIP-Forking-Indication"            : 0,
                        "Specific-Action"                   : 2,
                        "Specific-Action"                   : 4,
                        "Subscription-Id"                   : 
                         {  "Subscription-Id-Type"          : 1,
                            "Subscription-Id-Data"          : ueId },
                        "Framed-IP-Address"                 : "111.222.111.131",
                        "Origin-State-Id"                   : 0,
                        }
        jObject = result_data
        return 200, jObject

class __dispatch_PATCH_authentication_eps_data(dispatch):
    @staticmethod
    def run(uri_list, param_list, req_data):
        ueId            = uri_list["ueId"]
        #PRINT("__dispatch_PATCH_authentication_eps_data : ueId=%s" % (ueId))

        return 200, None

class __dispatch_PATCH_authentication_ims_data(dispatch):
    @staticmethod
    def run(uri_list, param_list, req_data):
        ueId            = uri_list["ueId"]
        #PRINT("__dispatch_PATCH_authentication_ims_data : ueId=%s" % (ueId))

        return 200, None

class __dispatch_PATCH_authentication_wifi_data(dispatch):
    @staticmethod
    def run(uri_list, param_list, req_data):
        ueId            = uri_list["ueId"]
        #PRINT("__dispatch_PATCH_authentication_wifi_data : ueId=%s" % (ueId))

        return 200, None


class __dispatch_PATCH_default(dispatch):
    @staticmethod
    def run(uri_list, param_list, req_data):
        ueId            = uri_list["ueId"]
        result_data     = None #{"Origin-State-Id" : 1}

        return 204, result_data

class __dispatch_GET_default(dispatch):
    @staticmethod
    def run(uri_list, param_list, req_data):
        ueId            = uri_list["ueId"]

        return 200, None

class __dispatch_DELETE_default(dispatch):
    @staticmethod
    def run(uri_list, param_list, req_data):
        ueId            = uri_list["ueId"]

        return 204, None

class __dispatch_PUT_default(dispatch):
    @staticmethod
    def run(uri_list, param_list, req_data):
        ueId            = uri_list["ueId"]

        return 204, None

class __dispatch_POST_default(dispatch):
    @staticmethod
    def run(uri_list, param_list, req_data):
        ueId            = uri_list["ueId"]

        return 201, None





__dispatch = ([
             # [ "auth-data"               , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/authentication-data"                                        , __dispatch_GET_authentication_data         ], 
             # [ "eps-auth-data"           , "PATCH"  , "/nudr-dr/v1/subscription-data/{ueId}/authentication-data/eps-auth-data"                          , __dispatch_PATCH_authentication_eps_data   ], 
             # [ "ims-auth-data"           , "PATCH"  , "/nudr-dr/v1/subscription-data/{ueId}/authentication-data/ims-auth-data"                          , __dispatch_PATCH_authentication_ims_data   ], 
             # [ "wifi-auth-data"          , "PATCH"  , "/nudr-dr/v1/subscription-data/{ueId}/authentication-data/wifi-auth-data"                         , __dispatch_PATCH_authentication_wifi_data  ], 
               [ "active-apn-data"         , "DELETE" , "/nudr-dr/v1/subscription-data/{ueId}/eps-am-data/active-apn-data/{apnContextId}"                 , __dispatch_DELETE_default                  ],
               [ "as-notify-data"          , "DELETE" , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data/as-notify-data/{asGroupId}/{dataReferenceId}"   , __dispatch_DELETE_default                  ],
               [ "cscf-restore-data"       , "DELETE" , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data/cscf-restore-data"                              , __dispatch_DELETE_default                  ],
               [ "authentication-data"     , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/authentication-data"                                        , __dispatch_GET_default                     ],
               [ "eps-am-data"             , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/eps-am-data"                                                , __dispatch_GET_default                     ],
               [ "active-apn-data"         , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/eps-am-data/active-apn-data"                                , __dispatch_GET_default                     ],
               [ "ims-am-data"             , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data"                                                , __dispatch_GET_default                     ],
               [ "as-notify-data"          , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data/as-notify-data"                                 , __dispatch_GET_default                     ],
               [ "cscf-restore-data"       , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data/cscf-restore-data"                              , __dispatch_GET_default                     ],
               [ "location-data"           , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/location-data"                                              , __dispatch_GET_default                     ],
               [ "supplement-service-data" , "GET"    , "/nudr-dr/v1/subscription-data/{ueId}/supplement-service-data"                                    , __dispatch_GET_default                     ],
               [ "eps-auth-data"           , "PATCH"  , "/nudr-dr/v1/subscription-data/{ueId}/authentication-data/eps-auth-data"                          , __dispatch_PATCH_default                   ],
               [ "ims-auth-data"           , "PATCH"  , "/nudr-dr/v1/subscription-data/{ueId}/authentication-data/ims-auth-data"                          , __dispatch_PATCH_default                   ],
               [ "wifi-auth-data"          , "PATCH"  , "/nudr-dr/v1/subscription-data/{ueId}/authentication-data/wifi-auth-data"                         , __dispatch_PATCH_default                   ],
               [ "location-data"           , "PATCH"  , "/nudr-dr/v1/subscription-data/{ueId}/location-data"                                              , __dispatch_PATCH_default                   ],
               [ "supplement-service-data" , "PATCH"  , "/nudr-dr/v1/subscription-data/{ueId}/supplement-service-data"                                    , __dispatch_PATCH_default                   ],
               [ "active-apn-data"         , "POST"   , "/nudr-dr/v1/subscription-data/{ueId}/eps-am-data/active-apn-data/{apnContextId}"                 , __dispatch_POST_default                    ],
               [ "as-notify-data"          , "POST"   , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data/as-notify-data/{asGroupId}/{dataReferenceId}"   , __dispatch_POST_default                    ],
               [ "cscf-restore-data"       , "POST"   , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data/cscf-restore-data/{imsPrivateUserId}"           , __dispatch_POST_default                    ],
               [ "active-apn-data"         , "PUT"    , "/nudr-dr/v1/subscription-data/{ueId}/eps-am-data/active-apn-data/{apnContextId}"                 , __dispatch_PUT_default                     ],
               [ "as-notify-data"          , "PUT"    , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data/as-notify-data/{asGroupId}/{dataReferenceId}"   , __dispatch_PUT_default                     ],
               [ "cscf-restore-data"       , "PUT"    , "/nudr-dr/v1/subscription-data/{ueId}/ims-am-data/cscf-restore-data/{imsPrivateUserId}"           , __dispatch_PUT_default                     ],
              ])

def init_dispatch():
    dispatch_util.instance(__dispatch)



