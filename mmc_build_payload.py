# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : mmc_build_payload.py
  Release  : 1
  Date     : 2018-08-02
 
  Description :
 
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
sys.path.insert(0, './h2_core')

#from perf import *
from abc import *
from time import sleep
from log import *
from h2_base import *
from singleton import *
from config import *
import copy

class payload_builder(singleton_instance):
    def __init__(self):
        return

    def __get_config_data(self, __type, category, field):
        e    = cfg_data.getinstance()
        item = e.search_data_cfg(field, category)

        if item == None:
            return None
        if __type == int:
            int_val = -1
            try:
                int_val = int(item)
            except:
                PRINT("Error. invalid literal for int() : '%s' at <%s : %s>" % (item, category, field))
                sleep(0.5)
            return int_val
        return item

    def __remove_null_element(self, result_data):
        new_data = copy.deepcopy(result_data)
        for item in result_data.keys():
            if result_data[item] == None:
                del new_data[item]
        return new_data

    def build_CommSubsData(self, ueId):
        name        = "CommSubsData"
        result_data = {
            "imsi"                  : self.__get_config_data(str, name, "imsi"),                 # String  15~15
            "msisdn"                : self.__get_config_data(str, name, "msisdn"),               # String  11~15
            "imei"                  : self.__get_config_data(str, name, "imei"),                 # String  14 ~ 16
            "authStatus"            : self.__get_config_data(int, name, "authStatus"),           # Integer 1
            "serviceType"           : self.__get_config_data(str, name, "serviceType"),          # String  ~ 8
            "preferCarrierId"       : self.__get_config_data(str, name, "preferCarrierId"),      # String  ~ 6
            "userUsageType"         : self.__get_config_data(int, name, "userUsageType"),        # Integer ~ 4
            "privateLteId"          : self.__get_config_data(int, name, "privateLteId"),         # Integer 1 ~ 4
            "networkAccesMode"      : self.__get_config_data(str, name, "networkAccesMode"),     # String  ~ 4
            "accessRestrictData"    : self.__get_config_data(str, name, "accessRestrictData"),   # Bit String  16 ~ 16
            "charging"              : self.__get_config_data(str, name, "charging"),             # String  ~ 10
            "imsProfile"            : self.__get_config_data(str, name, "imsProfile"),           # String  ~ 3
            "imsDomain"             : self.__get_config_data(str, name, "imsDomain"),            # String  0 ~ 48
            "voltePolicy"           : self.__get_config_data(int, name, "voltePolicy"),          # Integer 1
            "psvtPolicy"            : self.__get_config_data(int, name, "psvtPolicy"),           # Integer 1
            "smsIpPolicy"           : self.__get_config_data(int, name, "smsIpPolicy"),          # Integer 1
            "password"              : self.__get_config_data(str, name, "password"),             # String  4
        }
        return self.__remove_null_element(result_data), name
    def build_CommOdbData(self, ueId):
        name        = "CommOdbData"
        result_data = {
            "odbOutCall"            : self.__get_config_data(str, name, "odbOutCall"      ),     # Bit String  6 ~ 6
            "odbInCall"             : self.__get_config_data(str, name, "odbInCall"       ),     # Bit String  3 ~ 3
            "odbRoaming"            : self.__get_config_data(str, name, "odbRoaming"      ),     # Bit String  2 ~ 2
            "odbPrRate"             : self.__get_config_data(str, name, "odbPrRate"       ),     # Bit String  2 ~ 2
            "odbSsMgmt"             : self.__get_config_data(str, name, "odbSsMgmt"       ),     # Bit String  2 ~ 2
            "odbCallFowrd"          : self.__get_config_data(str, name, "odbCallFowrd"    ),     # Bit String  5 ~ 5
            "odbCallTransfer"       : self.__get_config_data(str, name, "odbCallTransfer" ),     # Bit String  6 ~ 6
            "odbPLMNData"           : self.__get_config_data(str, name, "odbPLMNData"     ),     # Bit String  4 ~ 4
            "odbGprsOutCall"        : self.__get_config_data(str, name, "odbGprsOutCall"  ),     # Bit String  3 ~ 3
            "odbGprsRoaming"        : self.__get_config_data(str, name, "odbGprsRoaming"  ),     # Bit String  2 ~ 2
            "odbGprsPlmnData"       : self.__get_config_data(str, name, "odbGprsPlmnData" ),     # Bit String  4 ~ 4
            "odbEpsRoaming"         : self.__get_config_data(str, name, "odbEpsRoaming"   ),     # Bit String  2 ~ 4
        }
        return self.__remove_null_element(result_data), name
    def build_OperatorSubsData(self, ueId):
        name        = "OperatorSubsData"
        result_data = {
            "planType"              :  self.__get_config_data(int, name,  "planType"      ),   #   Interger    1  ~ 4
            "usimType"              :  self.__get_config_data(int, name,  "usimType"      ),   #   Interger    1  ~ 4
            "referenceImsi"         :  self.__get_config_data(str, name,  "referenceImsi" ),   #   Imsi        15 ~ 15
        }
        return self.__remove_null_element(result_data), name
    def build_UeInfoData(self, ueId):
        name        = "UeInfoData"
        result_data = {
            "modelName"             :  self.__get_config_data(str, name, "modelName"        ),      # string  ~12
            "apChip"                :  self.__get_config_data(str, name, "apChip"           ),      # string  ~12
            "suppVolte"             :  self.__get_config_data(str, name, "suppVolte"        ),      # string  ~ 4
            "suppPsvt"              :  self.__get_config_data(str, name, "suppPsvt"         ),      # string  ~ 4
            "suppVolteRoaming"      :  self.__get_config_data(str, name, "suppVolteRoaming" ),      # string  ~ 4
            "suppSmsOverIP"         :  self.__get_config_data(str, name, "suppSmsOverIP"    ),      # string  ~ 4
            "defaultPDN"            :  self.__get_config_data(str, name, "defaultPDN"       ),      # string  ~ 4
            "suppLtePreferred"      :  self.__get_config_data(str, name, "suppLtePreferred" ),      # string  ~ 4
            "suppOtaOverHttp"       :  self.__get_config_data(str, name, "suppOtaOverHttp"  ),      # string  ~ 4
            "supp3gNetwork"         :  self.__get_config_data(str, name, "supp3gNetwork"    ),      # string  ~ 4
            "supp4gNetwork"         :  self.__get_config_data(str, name, "supp4gNetwork"    ),      # string  ~ 4
            "supp5gNetwork"         :  self.__get_config_data(int, name, "supp5gNetwork"    ),      # interger~ 4
        }
        return self.__remove_null_element(result_data), name
    def build_PermanentKey(self, ueId):
        name        = "PermanentKey"
        result_data = {
            "authCipherIndex"       :   self.__get_config_data(int, name,  "authCipherIndex"     ),    # Integer 1~3
            "authenticationKey"     :   self.__get_config_data(str, name,  "authenticationKey"   ),    # Hex String  32 ~ 32
            "authenticationOpc"     :   self.__get_config_data(str, name,  "authenticationOpc"   ),    # Hex String  32 ~ 32
            "authenticationAmf"     :   self.__get_config_data(str, name,  "authenticationAmf"   ),    # Hex String  4 ~ 4
            "authenticationDigest"  :   self.__get_config_data(str, name,  "authenticationDigest"),    # String  0 ~ 16
        }
        return self.__remove_null_element(result_data), name
    def build_AuthEpsData(self, ueId):
        name        = "AuthEpsData"
        result_data = {
            "sequenceInd"           : self.__get_config_data(int, name, "sequenceInd"),     # Integer     4
            "sequenceNumber"        : self.__get_config_data(str, name, "sequenceNumber"),  # Hex String  12 ~ 12
            "accessNodeData"        : self.__get_config_data(str, name, "accessNodeData"),  # Hex String  0 ~ 64
            "accessTime"            : self.__get_config_data(str, name, "accessTime"),      # String      0 ~ 24
        }
        return self.__remove_null_element(result_data), name
    def build_AuthImsData(self, ueId):
        name        = "AuthImsData"
        result_data = {
            "sequenceInd"           : self.__get_config_data(int, name, "sequenceInd"      ), # Integer     4
            "sequenceNumber"        : self.__get_config_data(str, name, "sequenceNumber"   ), # Hex String  12 ~ 12
            "accessNodeData"        : self.__get_config_data(str, name, "accessNodeData"   ), # Hex String  0 ~ 64
            "accessTime"            : self.__get_config_data(str, name, "accessTime"       ), # String      0 ~ 24
        }
        return self.__remove_null_element(result_data), name
    def build_AuthWifiData(self, ueId):
        name        = "AuthWifiData"
        result_data = {
            "sequenceInd"           :  self.__get_config_data(int, name, "sequenceInd"      ),    # Integer     4
            "sequenceNumber"        :  self.__get_config_data(str, name, "sequenceNumber"   ),    # Hex String  12 ~ 12
            "accessNodeData"        :  self.__get_config_data(str, name, "accessNodeData"   ),    # Hex String  0 ~ 64
            "accessTime"            :  self.__get_config_data(str, name, "accessTime"       ),    # String      0 ~ 24
        }
        return self.__remove_null_element(result_data), name
    def build_EpsSubsData(self, ueId):
        name        = "EpsSubsData"
        result_data = {
            "icsInd"                : self.__get_config_data(int, name, "icsInd"                ), # Integer 1
            "hsivops"               : self.__get_config_data(int, name, "hsivops"               ), # Integer 1
            "epsAttachType"         : self.__get_config_data(int, name, "epsAttachType"         ), # Integer 1
            "defaultApnContextId"   : self.__get_config_data(int, name, "defaultApnContextId"   ), # Integer 1 ~ 4
            "ambrUl"                : self.__get_config_data(int, name, "ambrUl"                ), # Integer 1 ~ 12
            "ambrDl"                : self.__get_config_data(int, name, "ambrDl"                ), # Integer 1 ~12
            "rfspId"                : self.__get_config_data(int, name, "rfspId"                ), # Integer 1 ~ 4
            "apnOiReplacement"      : self.__get_config_data(str, name, "apnOiReplacement"      ), # String  0 ~ 64
            "stnSR"                 : self.__get_config_data(str, name, "stnSR"                 ), # String  0 ~ 16
            "imsiGroupId"           : self.__get_config_data(str, name, "imsiGroupId"           ), # String  0 ~ 20
        }
        return self.__remove_null_element(result_data), name
    def build_EpsApnList(self, ueId):
        name        = "EpsApnList"
        result_data = {
            "apnContextId"          : self.__get_config_data(int, name, "apnContextId"   ), # Integer     4
        }
        return self.__remove_null_element(result_data), name
    def build_PsPdpList(self, ueId):
        name        = "PsPdpList"
        result_data = {
            "pdpContexId"           : self.__get_config_data(int, name,  "pdpContexId"  ), # Integer     4
        }
        return self.__remove_null_element(result_data), name
    def build_ActiveApnData(self, ueId):
        name        = "ActiveApnData"
        result_data = {
            "apnContextId"          : self.__get_config_data(int, name,   "apnContextId"     ), # Integer 1 ~ 3
            "apnName"               : self.__get_config_data(str, name,   "apnName"          ), # String    ~ 32
            "mipHaAddr1"            : self.__get_config_data(str, name,   "mipHaAddr1"       ), # String  4 ~ 24
            "mipHaAddr2"            : self.__get_config_data(str, name,   "mipHaAddr2"       ), # String  4 ~ 24
            "mipDestHost"           : self.__get_config_data(str, name,   "mipDestHost"      ), # String  4 ~ 64
            "mipDestRealm"          : self.__get_config_data(str, name,   "mipDestRealm"     ), # String  4 ~ 64
            "visitedNetworkId"      : self.__get_config_data(str, name,   "visitedNetworkId" ), # String  4 ~ 32
        }                             
        return self.__remove_null_element(result_data), name
    def build_CscfRestoreData(self, ueId):
        name        = "CscfRestoreData"
        result_data = {
            "imsPrivateUserId"      : self.__get_config_data(str, name,  "imsPrivateUserId"   ), # String  ~ 64    64
            "restoreData"           : self.__get_config_data(str, name,  "restoreData"        ), # Binary  ~1500   1500
        }
        return self.__remove_null_element(result_data), name
    def build_AsNotifyData(self, ueId):
        name        = "AsNotifyData"
        result_data = {
            "asGroupId"             : self.__get_config_data(int, name,  "asGroupId"        ), # Integer 4
            "asDataReference"       : self.__get_config_data(int, name,  "asDataReference"  ), # Integer 1
            "asOntimeFlag"          : self.__get_config_data(int, name,  "asOntimeFlag"     ), # Integer 1
            "asUeIdType"            : self.__get_config_data(int, name,  "asUeIdType"       ), # Integer 4
            "asExpiryTime"          : self.__get_config_data(int, name,  "asExpiryTime"     ), # Integer 4
            "asFailFlag"            : self.__get_config_data(int, name,  "asFailFlag"       ), # Integer 1
        }
        return self.__remove_null_element(result_data), name
    def build_CommLocationData(self, ueId):
        name        = "CommLocationData"
        result_data = {
            "lastRegPlmn"           : self.__get_config_data(int, name,  "lastRegPlmn"   ), # Integer 1
            "mnrf"                  : self.__get_config_data(int, name,  "mnrf"          ), # Integer 1
            "mnrr"                  : self.__get_config_data(int, name,  "mnrr"          ), # Integer 1
            "mnrg"                  : self.__get_config_data(int, name,  "mnrg"          ), # Integer 1
            "gprsmnrr"              : self.__get_config_data(int, name,  "gprsmnrr"      ), # Integer 1
            "unri"                  : self.__get_config_data(int, name,  "unri"          ), # Integer 1
            "unrr"                  : self.__get_config_data(int, name,  "unrr"          ), # Integer 1
            "mcef"                  : self.__get_config_data(int, name,  "mcef"          ), # Integer 1
        }
        return self.__remove_null_element(result_data), name
    def build_CsLocationData(self, ueId):
        name        = "CsLocationData"
        result_data = {
            "csRegStatus"           : self.__get_config_data(int, name,  "csRegStatus"          ), # Integer ~ 1
            "vlrNumber"             : self.__get_config_data(str, name,  "vlrNumber"            ), # String  ~ 16
            "mscNumber"             : self.__get_config_data(str, name,  "mscNumber"            ), # String  ~ 16
            "vlrRegTime"            : self.__get_config_data(str, name,  "vlrRegTime"           ), # String  ~ 24
            "vlrCamelPhase"         : self.__get_config_data(int, name,  "vlrCamelPhase"        ), # Integer 1
            "vlrVisitedGmlcAddr"    : self.__get_config_data(str, name,  "vlrVisitedGmlcAddr"   ), # String  ~ 48
            "vlrLcsCapa"            : self.__get_config_data(int, name,  "vlrLcsCapa"           ), # Integer 1
            "lmsi"                  : self.__get_config_data(str, name,  "lmsi"                 ), # String  ~ 8
        }
        return self.__remove_null_element(result_data), name
    def build_EpsLocationData(self, ueId):
        name        = "EpsLocationData"
        result_data = {
            "mmeRegStatus"          : self.__get_config_data(int, name,  "mmeRegStatus"           ),  # Integer ~ 1
            "mmeHost"               : self.__get_config_data(str, name,  "mmeHost"                ),  # String  ~ 64
            "mmeRealm"              : self.__get_config_data(str, name,  "mmeRealm"               ),  # String  ~ 64
            "mmeRegTime"            : self.__get_config_data(str, name,  "mmeRegTime"             ),  # String  ~ 24
            "mmeVplmnId"            : self.__get_config_data(str, name,  "mmeVplmnId"             ),  # String  ~ 6
            "mmeImsVoiceOverPS"     : self.__get_config_data(int, name,  "mmeImsVoiceOverPS"      ),  # Integer 1
            "mmeRaType"             : self.__get_config_data(int, name,  "mmeRaType"              ),  # Integer 4
            "mmeUlrFlags"           : self.__get_config_data(str, name,  "mmeUlrFlags"            ),  # Bit  String 8
            "uePurgeMme"            : self.__get_config_data(int, name,  "uePurgeMme"             ),  # Integer ~ 1
            "mmeSuppFeature1"       : self.__get_config_data(str, name,  "mmeSuppFeature1"        ),  # Bit  String 32
            "mmeSuppFeature2"       : self.__get_config_data(str, name,  "mmeSuppFeature2"        ),  # Bit  String 32
            "mmeCancelFailCount"    : self.__get_config_data(int, name,  "mmeCancelFailCount"     ),  # Integer 1
            "urrpMme"               : self.__get_config_data(int, name,  "urrpMme"                ),  # Integer 1
            "imei"                  : self.__get_config_data(str, name,  "imei"                   ),  # String  14 ~ 16
            "softVersion"           : self.__get_config_data(str, name,  "softVersion"            ),  # String  ~ 4
            "nodeTypeInd"           : self.__get_config_data(int, name,  "nodeTypeInd"            ),  # Integer ~ 4
            "s4SgsnRegStatus"       : self.__get_config_data(int, name,  "s4SgsnRegStatus"        ),  # Integer ~ 1
            "s4SgsnHost"            : self.__get_config_data(str, name,  "s4SgsnHost"             ),  # String  ~ 64
            "s4SgsnRealm"           : self.__get_config_data(str, name,  "s4SgsnRealm"            ),  # String  ~ 64
            "s4SgsnRegTime"         : self.__get_config_data(str, name,  "s4SgsnRegTime"          ),  # String  ~ 24
            "s4SgsnVplmnId"         : self.__get_config_data(str, name,  "s4SgsnVplmnId"          ),  # String  ~ 6
            "s4SgsnImsVoiceOverPS"  : self.__get_config_data(int, name,  "s4SgsnImsVoiceOverPS"   ),  # Integer 1
            "s4SgsnRaType"          : self.__get_config_data(int, name,  "s4SgsnRaType"           ),  # Integer 4
            "s4SgsnUlrFlags"        : self.__get_config_data(str, name,  "s4SgsnUlrFlags"         ),  # Bit  String 8
            "uePurgeSgsn"           : self.__get_config_data(int, name,  "uePurgeSgsn"            ),  # Integer ~ 1
            "s4SgsnSuppFeature1"    : self.__get_config_data(str, name,  "s4SgsnSuppFeature1"     ),  # Bit  String 32
            "s4SgsnSuppFeature2"    : self.__get_config_data(str, name,  "s4SgsnSuppFeature2"     ),  # Bit  String 32
            "s4SgsnCancelFailCount" : self.__get_config_data(int, name,  "s4SgsnCancelFailCount"  ),  # Integer 1
            "urrpSgsn"              : self.__get_config_data(int, name,  "urrpSgsn"               ),  # Integer 1
        }
        return self.__remove_null_element(result_data), name
    def build_PsLocationData(self, ueId):
        name        = "PsLocationData"
        result_data = {
            "psRegStatus"           : self.__get_config_data(int, name,  "psRegStatus"         ),  # Integer ~ 1
            "sgsnNumber"            : self.__get_config_data(str, name,  "sgsnNumber"          ),  # String  ~ 16
            "sgsnRegTime"           : self.__get_config_data(str, name,  "sgsnRegTime"         ),  # String  ~ 24
            "sgsnCamelPhase"        : self.__get_config_data(int, name,  "sgsnCamelPhase"      ),  # Integer 1
            "sgsnLcsCapa"           : self.__get_config_data(int, name,  "sgsnLcsCapa"         ),  # Integer 1
            "sgsnEnhancement"       : self.__get_config_data(int, name,  "sgsnEnhancement"     ),  # Integer 1
            "sgsnLSA4PS"            : self.__get_config_data(int, name,  "sgsnLSA4PS"          ),  # Integer 1
            "sgsnSuperCharger"      : self.__get_config_data(int, name,  "sgsnSuperCharger"    ),  # Integer 1
            "psCancelFailCount"     : self.__get_config_data(int, name,  "psCancelFailCount"   ),  # Integer 1
        }
        return self.__remove_null_element(result_data), name
    def build_AsLocationData(self, ueId):
        name        = "AsLocationData"
        result_data = {
            "tasRegStatus"          : self.__get_config_data(int, name,  "tasRegStatus"      ), # Integer 1
            "tasRegTime"            : self.__get_config_data(str, name,  "tasRegTime"        ), # String  ~24
            "ipsmgwRegStatus"       : self.__get_config_data(int, name,  "ipsmgwRegStatus"   ), # Integer 1
            "ipsmgwRegTime"         : self.__get_config_data(str, name,  "ipsmgwRegTime"     ), # String  ~24
            "ipsmgwNumber"          : self.__get_config_data(str, name,  "ipsmgwNumber"      ), # String  ~ 16
        }
        return self.__remove_null_element(result_data), name
    def build_ImsLocationData(self, ueId):
        name        = "ImsLocationData"
        result_data = {
            "imsRegStatus"          : self.__get_config_data(int, name,  "imsRegStatus"       ),  # Integer ~ 1
            "imsRegTime"            : self.__get_config_data(str, name,  "imsRegTime"         ),  # String  ~24
            "imsDeregTime"          : self.__get_config_data(str, name,  "imsDeregTime"       ),  # String  ~24
            "implictRegSetId"       : self.__get_config_data(int, name,  "implictRegSetId"    ),  # Integer 1
            "lastSaType"            : self.__get_config_data(int, name,  "lastSaType"         ),  # Integer ~ 4
            "authPendingFlag"       : self.__get_config_data(int, name,  "authPendingFlag"    ),  # Integer 1
            "regPendingFlag"        : self.__get_config_data(int, name,  "regPendingFlag"     ),  # Integer 1
            "authFailCount"         : self.__get_config_data(int, name,  "authFailCount"      ),  # Integer 1 ~ 2
            "regPublidUserId"       : self.__get_config_data(str, name,  "regPublidUserId"    ),  # String  ~ 64
            "scscfName"             : self.__get_config_data(str, name,  "scscfName"          ),  # String  ~ 64
            "cxSuppFeature"         : self.__get_config_data(str, name,  "cxSuppFeature"      ),  # Bit String  4 ~ 4
        }                             
        return self.__remove_null_element(result_data), name

    def build_BasicServieGroupList(self, ueId):
        name        = "BasicServieGroupList"
        result_data = {
            "BSGName"               : self.__get_config_data(str, name,  "BSGName"  ),  # String 4 ~ 4
        }
        return self.__remove_null_element(result_data), name
    def build_BasicServiceData(self, ueId):
        name        = "BasicServiceData"
        result_data = {
            "ECTStatus"             : self.__get_config_data(int, name,  "ECTStatus"         ),   #   Integer 1
            "CDStatus"              : self.__get_config_data(int, name,  "CDStatus"          ),   #   Integer 1
            "CDNotiCall"            : self.__get_config_data(int, name,  "CDNotiCall"        ),   #   Integer 1
            "CDPresentation"        : self.__get_config_data(int, name,  "CDPresentation"    ),   #   Integer 1
            "HOLDStatus"            : self.__get_config_data(int, name,  "HOLDStatus"        ),   #   Integer 1
            "MPTYStatus"            : self.__get_config_data(int, name,  "MPTYStatus"        ),   #   Integer 1
            "CLIPStatus"            : self.__get_config_data(int, name,  "CLIPStatus"        ),   #   Integer 1
            "CLIPOverride"          : self.__get_config_data(int, name,  "CLIPOverride"      ),   #   Integer 1
            "CLIRStatus"            : self.__get_config_data(int, name,  "CLIRStatus"        ),   #   Integer 1
            "CLIRPresentation"      : self.__get_config_data(int, name,  "CLIRPresentation"  ),   #   Integer 1
            "COLPStatus"            : self.__get_config_data(int, name,  "COLPStatus"        ),   #   Integer 1
            "COLPOverride"          : self.__get_config_data(int, name,  "COLPOverride"      ),   #   Integer 1
            "COLRStatus"            : self.__get_config_data(int, name,  "COLRStatus"        ),   #   Integer 1
            "BICRoamStatus"         : self.__get_config_data(int, name,  "BICRoamStatus"     ),   #   Integer 1
            "BICRoamOperCtl"        : self.__get_config_data(int, name,  "BICRoamOperCtl"    ),   #   Integer 1
            "AoCIStatus"            : self.__get_config_data(int, name,  "AoCIStatus"        ),   #   Integer 1
            "AoCCStatus"            : self.__get_config_data(int, name,  "AoCCStatus"        ),   #   Integer 1
            "CCBSStatus"            : self.__get_config_data(int, name,  "CCBSStatus"        ),   #   Integer 1
            "CNAPStatus"            : self.__get_config_data(int, name,  "CNAPStatus"        ),   #   Integer 1
            "CNAPOverride"          : self.__get_config_data(int, name,  "CNAPOverride"      ),   #   Integer 1
            "CNARStatus"            : self.__get_config_data(int, name,  "CNARStatus"        ),   #   Integer 1
            "EMLPPStatus"           : self.__get_config_data(int, name,  "EMLPPStatus"       ),   #   Integer 1
            "EMLPPPriority"         : self.__get_config_data(int, name,  "EMLPPPriority"     ),   #   Integer 1
            "MCStatus"              : self.__get_config_data(int, name,  "MCStatus"          ),   #   Integer 1
            "MCSStatus"             : self.__get_config_data(int, name,  "MCSStatus"         ),   #   Integer 1
            "CISSStatus"            : self.__get_config_data(int, name,  "CISSStatus"        ),   #   Integer 1
            "RCCStatus"             : self.__get_config_data(int, name,  "RCCStatus"         ),   #   Integer 1
            "WOWStatus"             : self.__get_config_data(int, name,  "WOWStatus"         ),   #   Integer 1
            "RCCDStatus"            : self.__get_config_data(int, name,  "RCCDStatus"        ),   #   Integer 1
            "CNIRDStatus"           : self.__get_config_data(int, name,  "CNIRDStatus"       ),   #   Integer 1
            "OCSStatus"             : self.__get_config_data(int, name,  "OCSStatus"         ),   #   Integer 1
            "OCSNumber"             : self.__get_config_data(str, name,  "OCSNumber"         ),   #   String  10 ~ 11
            "SMAMRStatus"           : self.__get_config_data(int, name,  "SMAMRStatus"       ),   #   Integer 1
            "HDVoiceStatus"         : self.__get_config_data(int, name,  "HDVoiceStatus"     ),   #   Integer 1
            "VoLTERoamStatus"       : self.__get_config_data(int, name,  "VoLTERoamStatus"   ),   #   Integer 1
            "WHOStatus"             : self.__get_config_data(int, name,  "WHOStatus"         ),   #   Integer 1
            "ForkMStatus"           : self.__get_config_data(int, name,  "ForkMStatus"       ),   #   Integer 1
            "ForkMode"              : self.__get_config_data(int, name,  "ForkMode"          ),   #   Integer 1
            "ForkMNumber"           : self.__get_config_data(str, name,  "ForkMNumber"       ),   #   String  10 ~ 11
            "ForkSStatus"           : self.__get_config_data(int, name,  "ForkSStatus"       ),   #   Integer 1
            "ForkSNumber"           : self.__get_config_data(str, name,  "ForkSNumber"       ),   #   String  10 ~ 11
            "PlteStatus"            : self.__get_config_data(int, name,  "PlteStatus"        ),   #   integer 1
        }
        return self.__remove_null_element(result_data), name
    def build_CFServiceData(self, ueId):
        name        = "CFServiceData"
        result_data = {
            "CFUPresentation"       : self.__get_config_data(int, name,  "CFUPresentation"  ), #   Integer 1
            "CFUNotiCall"           : self.__get_config_data(int, name,  "CFUNotiCall"      ), #   Integer 1
            "CFDPresentation"       : self.__get_config_data(int, name,  "CFDPresentation"  ), #   Integer 1
            "CFDNotiCall"           : self.__get_config_data(int, name,  "CFDNotiCall"      ), #   Integer 1
            "CFDNotiFoward"         : self.__get_config_data(int, name,  "CFDNotiFoward"    ), #   Integer 1
            "SCFUStatus"            : self.__get_config_data(int, name,  "SCFUStatus"       ), #   Integer 1
            "SCFUNumber"            : self.__get_config_data(str, name,  "SCFUNumber"       ), #   String  10 ~ 11
        }                             
        return self.__remove_null_element(result_data), name
    def build_SNDServiceData(self, ueId):
        name        = "SNDServiceData"
        result_data = {
            "SNDStatus"             : self.__get_config_data(int, name,  "SNDStatus"     ),   #   Integer 1
            "SNBDStatus"            : self.__get_config_data(int, name,  "SNBDStatus"    ),   #   Integer 1
            "SNBDType"              : self.__get_config_data(int, name,  "SNBDType"      ),   #   Integer 1
            "SNBDNumber0"           : self.__get_config_data(str, name,  "SNBDNumber0"   ),   #   String  3~8
            "SNBDNumber1"           : self.__get_config_data(str, name,  "SNBDNumber1"   ),   #   String  3~8
            "SNBDNumber2"           : self.__get_config_data(str, name,  "SNBDNumber2"   ),   #   String  3~8
            "SNBDNumber3"           : self.__get_config_data(str, name,  "SNBDNumber3"   ),   #   String  3~8
            "SNBDNumber4"           : self.__get_config_data(str, name,  "SNBDNumber4"   ),   #   String  3~8
            "SNBDNumber5"           : self.__get_config_data(str, name,  "SNBDNumber5"   ),   #   String  3~8
            "SNBDNumber6"           : self.__get_config_data(str, name,  "SNBDNumber6"   ),   #   String  3~8
            "SNBDNumber7"           : self.__get_config_data(str, name,  "SNBDNumber7"   ),   #   String  3~8
            "SNBDNumber8"           : self.__get_config_data(str, name,  "SNBDNumber8"   ),   #   String  3~8
            "SNBDNumber9"           : self.__get_config_data(str, name,  "SNBDNumber9"   ),   #   String  3~8
            "SNBD2Status"           : self.__get_config_data(int, name,  "SNBD2Status"   ),   #   Integer 1
        }
        return self.__remove_null_element(result_data), name
    def build_ImsServiceData(self, ueId):
        name        = "ImsServiceData"
        result_data = {
            "VoLTEStatus"           : self.__get_config_data(int, name,  "VoLTEStatus"  ),  #   Integer 1
            "PSVTStatus"            : self.__get_config_data(int, name,  "PSVTStatus"   ),  #   Integer 1
            "SMSIPStatus"           : self.__get_config_data(int, name,  "SMSIPStatus"  ),  #   Integer 1
        }                             
        return self.__remove_null_element(result_data), name
    def build_InServiceData(self, ueId):
        name        = "InServiceData"
        result_data = {
            "ATS1Status"            : self.__get_config_data(int, name,  "ATS1Status"      ),   #   Integer 1
            "ATS1Act"               : self.__get_config_data(int, name,  "ATS1Act"         ),   #   Integer 1
            "TNSStatus"             : self.__get_config_data(int, name,  "TNSStatus"       ),   #   Integer 1
            "STNSStatus"            : self.__get_config_data(int, name,  "STNSStatus"      ),   #   Integer 1
            "STNSNumber"            : self.__get_config_data(str, name,  "STNSNumber"      ),   #   String  10 ~ 11
            "SFZStatus"             : self.__get_config_data(int, name,  "SFZStatus"       ),   #   Integer 1
            "SFZIndex"              : self.__get_config_data(int, name,  "SFZIndex"        ),   #   Integer 1
            "SpsCarStatus"          : self.__get_config_data(int, name,  "SpsCarStatus"    ),   #   Integer 1
            "SpsUserStatus"         : self.__get_config_data(int, name,  "SpsUserStatus"   ),   #   Integer 1
            "SpsIMSI"               : self.__get_config_data(str, name,  "SpsIMSI"         ),   #   String  15 ~ 15
            "SpsMSISDN"             : self.__get_config_data(str, name,  "SpsMSISDN"       ),   #   String  10 ~ 11
            "WINStatus"             : self.__get_config_data(int, name,  "WINStatus"       ),   #   Integer 1
            "WIN1Status"            : self.__get_config_data(int, name,  "WIN1Status"      ),   #   Integer 1
            "WIN2Status"            : self.__get_config_data(int, name,  "WIN2Status"      ),   #   Integer 1
            "WINId"                 : self.__get_config_data(int, name,  "WINId"           ),   #   Integer 1
            "ATS3Status"            : self.__get_config_data(int, name,  "ATS3Status"      ),   #   Integer 1
            "RTS1Status"            : self.__get_config_data(int, name,  "RTS1Status"      ),   #   Integer 1
            "RTS2Status"            : self.__get_config_data(int, name,  "RTS2Status"      ),   #   Integer 1
        }
        return self.__remove_null_element(result_data), name
    def build_VirtualServiceData(self, ueId):
        name        = "VirtualServiceData"
        result_data = {
            "DNFStatus"             : self.__get_config_data(int, name,  "DNFStatus"        ),  #   Integer 1
            "DNFNotification"       : self.__get_config_data(int, name,  "DNFNotification"  ),  #   Integer 1
            "DNFNumber"             : self.__get_config_data(str, name,  "DNFNumber"        ),  #   String  10 ~ 11
            "MNFStatus"             : self.__get_config_data(int, name,  "MNFStatus"        ),  #   Integer 1
            "MNFNumber"             : self.__get_config_data(str, name,  "MNFNumber"        ),  #   String  10 ~ 11
            "CNFStatus"             : self.__get_config_data(int, name,  "CNFStatus"        ),  #   Integer 1
            "CNFNumber"             : self.__get_config_data(str, name,  "CNFNumber"        ),  #   String  10 ~ 11
            "STNFStatus"            : self.__get_config_data(int, name,  "STNFStatus"       ),  #   Integer 1
        }
        return self.__remove_null_element(result_data), name

    def build_BSGServiceData(self, ueId):
        name        = "BSGServiceData"
        result_data = {
            "BAOCStatus"            : self.__get_config_data(str, name,   "BAOCStatus"       ),  #   Bitstring   6
            "BAOCOperCtl"           : self.__get_config_data(str, name,   "BAOCOperCtl"      ),  #   Bitstring   6
            "BOICStatus"            : self.__get_config_data(str, name,   "BOICStatus"       ),  #   Bitstring   6
            "BOICOperCtl"           : self.__get_config_data(str, name,   "BOICOperCtl"      ),  #   Bitstring   3
            "BOICExhcStatus"        : self.__get_config_data(str, name,   "BOICExhcStatus"   ),  #   Bitstring   6
            "BOICExhcOperCtl"       : self.__get_config_data(str, name,   "BOICExhcOperCtl"  ),  #   Bitstring   3
            "BAICStatus"            : self.__get_config_data(str, name,   "BAICStatus"       ),  #   Bitstring   6
            "BAICOperCtl"           : self.__get_config_data(str, name,   "BAICOperCtl"      ),  #   Bitstring   3
            "CWStatus"              : self.__get_config_data(str, name,   "CWStatus"         ),  #   Bitstring   6
            "CFUStatus"             : self.__get_config_data(str, name,   "CFUStatus"        ),  #   Bitstring   6
            "CFUNumber"             : self.__get_config_data(str, name,   "CFUNumber"        ),  #   String  10 ~ 11
            "CFDStatus"             : self.__get_config_data(str, name,   "CFDStatus"        ),  #   Bitstring   6
            "CFDNumber"             : self.__get_config_data(str, name,   "CFDNumber"        ),  #   String  10 ~ 11
            "VMUStatus"             : self.__get_config_data(str, name,   "VMUStatus"        ),  #   Bitstring   6
            "VMDStatus"             : self.__get_config_data(str, name,   "VMDStatus"        ),  #   Bitstring   6
            "XRSStatus"             : self.__get_config_data(str, name,   "XRSStatus"        ),  #   Bitstring   6
        }
        return self.__remove_null_element(result_data), name

    def build_ImsCommData(self, ueId):
        name        = "ImsCommData"
        result_data = {
            "imsSvcDomain"          : self.__get_config_data(int, name,   "imsSvcDomain" ),  #   Integer ~ 4
            "imsSvcPrefix"          : self.__get_config_data(str, name,   "imsSvcPrefix" ),  #   String  ~ 8
        }
        return self.__remove_null_element(result_data), name

    def build_ImsSubsData(self, ueId):
        name        = "ImsSubsData"
        result_data = {
            "imsPrivateUserId"      : self.__get_config_data(str, name,  "imsPrivateUserId"  ),   #   String  ~ 64
            "imsPublicUserId"       : self.__get_config_data(str, name,  "imsPublicUserId"   ),   #   String  ~ 64
            "imsPuidType"           : self.__get_config_data(int, name,  "imsPuidType"       ),   #   Integer 1
            "defaultPuidFlag"       : self.__get_config_data(int, name,  "defaultPuidFlag"   ),   #   Integer 1
            "barringIndicator"      : self.__get_config_data(int, name,  "barringIndicator"  ),   #   Integer 1
            "implictRegSetId"       : self.__get_config_data(int, name,  "implictRegSetId"   ),   #   Integer 1
            "disPlayName"           : self.__get_config_data(str, name,  "disPlayName"       ),   #   String  0 ~ 32
        }
        return self.__remove_null_element(result_data), name

payload_builder.instance()





