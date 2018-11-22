# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : h2_base.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : HTTP/2 basic protocol module
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import os
import ssl
import sys
import ssl
import socket
import pickle
import random 
#import cPickle as pickle
import pytz
import json
import h2.events
import h2.config
import h2.settings
import h2.connection
import threading
import zlib
import select
from log import *
from sim_util import *
from enum import Enum
from time import sleep
from h2_TLS import *
from multiprocessing import Process
from h2_trace import *
from hpack.struct import HeaderTuple, NeverIndexedHeaderTuple
from proc_pool import *
from concurrent.futures import ProcessPoolExecutor 
#from perf import h2_perf
from dispatch_parse import *
from hyperframe.exceptions import InvalidPaddingError
from hyperframe.frame import (
    GoAwayFrame, WindowUpdateFrame, HeadersFrame, DataFrame, PingFrame,
    PushPromiseFrame, SettingsFrame, RstStreamFrame, PriorityFrame,
    ContinuationFrame, AltSvcFrame, ExtensionFrame
)

from h2.exceptions import (                                                  
    ProtocolError, NoSuchStreamError, FlowControlError, FrameTooLargeError,
    TooManyStreamsError, StreamClosedError, StreamIDTooLowError,           
    NoAvailableStreamIDError, RFC1122Error, DenialOfServiceError           
)                                                                          

def enum(**enums):
    return type('Enum', (), enums)

h2_service_type = enum(SERVICE_PROVIDER=0, SERVICE_CONSUMER=1)
h2_conn_type = enum(CONNTYPE_SERVER=0, CONNTYPE_CLIENT_NOTIFY=1, CONNTYPE_CLIENT_REQUEST=2)
h2_setting_dict = {}

enable_ping     = True
ping_interval   = 5.0
ping_timeout    = 3.0
stack_name      = "PY_HTTP/2_Stack"
perf_mode       = False
enable_response = True
request_timeout = 4.0
responce_delay  = 0.00

header_indexing_rule_table = {
    "server"          : HeaderTuple             ,
    "content-type"    : HeaderTuple             ,
    "content-length"  : NeverIndexedHeaderTuple ,
    ":method"         : HeaderTuple             ,
    ":scheme"         : HeaderTuple             ,
    ":authority"      : HeaderTuple             ,
    ":path"           : NeverIndexedHeaderTuple ,
    "accept"          : HeaderTuple             ,
    "accept-encoding" : HeaderTuple             ,
    "user-agent"      : HeaderTuple             ,
    ":status"         : NeverIndexedHeaderTuple ,
    "__default__"     : HeaderTuple             ,
}

def _null_fn():
    i=0
    return False

def my_print(s):
    print(s)

class neoH2Connection(h2.connection.H2Connection):
    n_inbound_setting = 0
    def __init__(self, connection_id, config=None):
        self.connection_id = connection_id
        self.trace         = h2_trace.getinstance()
        super(neoH2Connection, self).__init__(config)

    def _receive_frame(self, frame):
        is_magic   = False
        is_preface = False
        if frame.type == FRAME_TYPE_SETTINGS:
            if self.n_inbound_setting == 0 and self.config.client_side == False:
                is_magic = True
                is_preface = True
            self.n_inbound_setting += 1

        self.trace.h2_frame_trace(TRACE_DIR_RECV, frame, is_preface=is_preface, is_magic=is_magic)
        return super(neoH2Connection, self)._receive_frame(frame)

    def initiate_connection(self):
        """
        Provides any data that needs to be sent at the start of the connection.
        Must be called for both clients and servers.
        """
        is_magic = False
        self.config.logger.debug("Initializing connection")
        self.state_machine.process_input(h2.connection.ConnectionInputs.SEND_SETTINGS)
        if self.config.client_side:
            is_magic = True
            preamble = b'PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n'
        else:
            preamble = b''

        f = SettingsFrame(0)
        for setting, value in self.local_settings.items():
            f.settings[setting] = value
        self.config.logger.debug(
            "Send Settings frame: %s", self.local_settings
        )
        self.trace.h2_frame_trace(TRACE_DIR_SEND, f, is_preface=True, is_magic=is_magic)

        self._data_to_send += preamble + f.serialize()

    def _prepare_for_sending(self, frames):
        for frame in frames:
            n_frame_type = frame.type
            self.trace.h2_frame_trace(TRACE_DIR_SEND, frame)
            #PRINT("Send : frame=%d" % n_frame_type)
            for flag_at in frame.flags:
                if flag_at == "ACK":
                    n_frame_type += 10
            dispatch = dispatch_util.getinstance()
            dispatch.set_tps_stat("FRAME", "OUT")
            dispatch.set_base_stat("SEND", n_frame_type)
        return super(neoH2Connection, self)._prepare_for_sending(frames)

    def data_to_send(self, amt=None):
        datas = super(neoH2Connection, self).data_to_send(amt)
        dispatch_util.getinstance().set_tps_stat("TRAFFIC", "OUT", len(datas))
        return datas

    def show_hpack_index_table(self):
        hpack_encoder = self.encoder.header_table.dynamic_entries
        hpack_decoder = self.decoder.header_table.dynamic_entries

        encoder_obj = self.encoder.header_table
        decoder_obj = self.decoder.header_table

        if len(hpack_encoder) + len(hpack_decoder) == 0: 
            return

        PRINT("%s" % (" "))
        PRINT("%s" % (LINE80))
        PRINT("HPACK Table for connection: %s" % (self.connection_id))
        PRINT("%s" % (" "))
        PRINT("1. Table of HPACK encoder: maxsize=%s, current_size=%s" % (encoder_obj._maxsize, encoder_obj._current_size))
        PRINT("%s" % (line80))
        PRINT("  %-8s %-24s   %s" % ("[Index]", "[field]", "[value]"))
        for idx, item in enumerate(hpack_encoder):
            PRINT("   %-8d %-24s   %s" % (idx + 62, item[0].decode('utf-8'), item[1].decode('utf-8')))
        PRINT("%s" % (line80))

        PRINT("%s" % (" "))
        PRINT("2. Table of HPACK decoder: maxsize=%s, current_size=%s" % (decoder_obj._maxsize, decoder_obj._current_size))
        #PRINT("%s" % ("2. Table of HPACK decoder"))
        PRINT("%s" % (line80))
        PRINT("  %-8s %-24s   %s" % ("[Index]", "[field]", "[value]"))
        for idx, item in enumerate(hpack_decoder):
            PRINT("   %-8d %-24s   %s" % (idx + 62, item[0].decode('utf-8'), item[1].decode('utf-8')))
        PRINT("%s" % (LINE80))

        PRINT("%s" % (" "))

    def receive_data(self, data):
        """
        Pass some received HTTP/2 data to the connection for handling.

        :param data: The data received from the remote peer on the network.
        :type data: ``bytes``
        :returns: A list of events that the remote peer triggered by sending
            this data.
        """
        self.config.logger.debug(
            "Process received data on connection. Received data: %r", data
        )

        events = []
        self.incoming_buffer.add_data(data)
        self.incoming_buffer.max_frame_size = self.max_inbound_frame_size

        try:
            for frame in self.incoming_buffer:
                n_frame_type = frame.type
                for flag_at in frame.flags:
                    if flag_at == "ACK":
                        n_frame_type += 10
                dispatch = dispatch_util.getinstance()
                dispatch.set_tps_stat("FRAME", "IN")
                dispatch.set_base_stat("RECV", n_frame_type)
                events.extend(self._receive_frame(frame))
        except InvalidPaddingError:
            self._terminate_connection(ErrorCodes.PROTOCOL_ERROR)
            raise ProtocolError("Received frame with invalid padding.")
        except ProtocolError as e:
            # For whatever reason, receiving the frame caused a protocol error.
            # We should prepare to emit a GoAway frame before throwing the
            # exception up further. No need for an event: the exception will
            # do fine.
            self._terminate_connection(e.error_code)
            raise

        return events


class h2_base:
    printFn                 = my_print
    traceFn                 = _null_fn
    rrIndex                 = 0
    conn_list               = []
    isClose                 = False
    serverDefaultCallback   = None
    clientDefaultCallback   = None
    lock = threading.Semaphore(1)
    conn_notify_max         = 0
    conn_request_max        = 0

    #connection count
    count_server            = 0
    count_notify_client     = 0
    count_request_client    = 0

    def __init__( self, LocalIP, PeerIP, LocalServicePort ,LocalNotifyPort, PeerServicePort ,PeerNotifyPort, LocalConnType, isTls, server_cert, server_key, client_certs, client_key , max_stream_id=2147383648):

        if is_valid_ip(LocalIP) == False:
            LocalIP = "0.0.0.0"

        self.LocalIP             = LocalIP
        self.PeerIP              = PeerIP
        self.LocalServicePort    = LocalServicePort
        self.LocalNotifyPort     = LocalNotifyPort
        self.PeerServicePort     = PeerServicePort
        self.PeerNotifyPort      = PeerNotifyPort
        self.LocalConnType       = LocalConnType # ConnType  ( 0 : Service-provider   , 1 : Service-Consumer )
        self.isTls               = isTls
        self.max_stream_id       = max_stream_id
        if isTls==True:
            self.server_cert    = server_cert
            self.server_key     = server_key
            self.client_certs   = client_certs
            self.client_key     = client_key
        self.set_tps_stat      = dispatch_util.getinstance().set_tps_stat
        self.set_base_stat      = dispatch_util.getinstance().set_base_stat
        
    def h2_set_print_method(self, fn):
        self.printFn = fn

    def h2_set_trace_method(self, fn):
        self.traceFn = fn

    def h2OpenServer(self, serverInvorkCallback):
        if serverInvorkCallback == None:
            serverInvorkCallback = self.serverDefaultCallback

        hThread = threading.Thread(target=self.h2WaitForAcceptTh, args=(self.LocalNotifyPort, serverInvorkCallback))
        hThread.daemon = True
        hThread.start()
       
        if self.LocalConnType == h2_service_type.SERVICE_PROVIDER and self.LocalNotifyPort != self.LocalServicePort:
            hThread = threading.Thread(target=self.h2WaitForAcceptTh, args=(self.LocalServicePort, serverInvorkCallback))
            hThread.daemon = True
            hThread.start()

 
    def h2OpenClient(self, clientResumeCallback, nConnection=3):
        nNotiConnection          = 2
        self.conn_notify_max     = nNotiConnection
        self.conn_request_max    = nConnection

        if clientResumeCallback == None:
            clientResumeCallback = self.clientDefaultCallback
        #self.printFn("self.LocalConnType : %d, %s" % (self.LocalConnType, h2_service_type.SERVICE_CONSUMER) )
        if self.LocalConnType == h2_service_type.SERVICE_CONSUMER:
            for i in range(nConnection):
                hThread = threading.Thread(target=self.h2ClientRecvTh, args=(clientResumeCallback, self.PeerIP, self.PeerServicePort, h2_conn_type.CONNTYPE_CLIENT_REQUEST, i, self.LocalIP ))
                hThread.daemon = True
                hThread.start()

        for i in range(nNotiConnection):
            hThread = threading.Thread(target=self.h2ClientRecvTh, args=(clientResumeCallback, self.PeerIP, self.PeerNotifyPort, h2_conn_type.CONNTYPE_CLIENT_NOTIFY, i, self.LocalIP ))
            hThread.daemon = True
            hThread.start()
        

    def h2SetClientCount(self, clientResumeCallback, conn_type, count):
        if conn_type == h2_conn_type.CONNTYPE_CLIENT_REQUEST:
            old_cnt = self.conn_request_max
            self.conn_request_max = count
            #self.printFn("old_cnt:%d, count:%d" % (old_cnt, count))
            if old_cnt < count:
                for i in range (old_cnt, count):
                    hThread = threading.Thread(target=self.h2ClientRecvTh, args=(clientResumeCallback, self.PeerIP, self.PeerServicePort, h2_conn_type.CONNTYPE_CLIENT_REQUEST, i, self.LocalIP ))
                    hThread.daemon = True
                    hThread.start()
        if conn_type == h2_conn_type.CONNTYPE_CLIENT_NOTIFY:
            old_cnt = self.conn_notify_max
            self.conn_notify_max = count
            if old_cnt < count:
                for i in range (old_cnt, count):
                    hThread = threading.Thread(target=self.h2ClientRecvTh, args=(clientResumeCallback, self.PeerIP, self.PeerServicePort, h2_conn_type.CONNTYPE_CLIENT_NOTIFY, i , self.LocalIP))
                    hThread.daemon = True
                    hThread.start()


    def h2_recv_enswer(self, conn, stream_id, fHeaders, fData, resumeCallback):
        fFail            = False
        fGzip            = False
        fDeflate         = False
        json_obj         = None
        json_str         = ""
        contentLength    = -1
        byte_data        = None
        rCode            = -1
        

        ctx = None
        if stream_id in self.h2_find_connection_from_list(conn)[4]:
            ctx = self.h2_find_connection_from_list(conn)[4][stream_id]
            del  self.h2_find_connection_from_list(conn)[4][stream_id] 

        for hPara in fHeaders:
            tag   = hPara[0].decode(encoding="utf-8")
            value = hPara[1].decode(encoding="utf-8")
            if tag == "content-encoding":
                if value == "gzip":
                    fGzip = True
                elif value == "deflate":
                    fDeflate = True
                else:
                    self.printFn("Err. unsupported compression method : %s" % value)
                    fFail = True
            elif tag == ":status":
                rCode = int(value)

        try:
            if fGzip == True:
                self.printFn ("TODO: Add Decompress code for gzip")
            elif fDeflate == True:
                fData = zlib.decompress(fData)
        except Exception as e:
            self.printFn("Err. Invalid Data Decompress: fGzip=%s, fDeflate=%s" % (fGzip, fDeflate))
            return None

        if fData != None:
            try:
                strData = fData.decode(encoding="utf-8")
                json_obj = json.loads(strData)
            except:
                #self.printFn("Fail to Decode Json")
                #self.printFn("input: %s" % (fData))
                fData = None
                #return None
            #try:
            #    strData = fData.decode(encoding="utf-8")
            #    json_obj = json.loads(strData)
            #    self.printFn (strData)
            #except:
            #    self.printFn ("JSON Decodeing Error")
            #    self.printFn ("%s" % strData)
            #    fFail = True
            #    pass
        
        if rCode == -1:
            fFail = True

        if fFail == False :
            if ctx != None:
                return resumeCallback(ctx[0], ctx[1], ctx[2], rCode, json_obj)
            else :
                return resumeCallback(None, None, None, rCode, json_obj)
        else:
            self.printFn("Err. Invalid Peer Answer")
            return None

    def h2_send_response(self, conn, stream_id, fHeaders, fData, invorkCallback):
        fFail            = False
        fGzip            = False
        fDeflate         = False
        acceptGzip       = False
        acceptDeflate    = False
        selectedTrEncode = None
        method           = None
        path             = None
        json_obj         = None
        json_str         = ""
        contentLength    = -1
        byte_data        = None
        for hPara in fHeaders:
            tag   = hPara[0].decode(encoding="utf-8")
            value = hPara[1].decode(encoding="utf-8")

            #self.printFn ("%s : %s" % (tag, value))
            if tag == ":method":
                method = value
            elif tag == ":path":
                path = value
            elif tag == "content-encoding":
                if value == "gzip":
                    fGzip = True
                elif value == "deflate":
                    fDeflate = True
                else:
                    self.printFn("Err. unsupported compression method : %s" % value)
                    fFail = Tru
            elif tag == "accept-encoding":
                if value == "gzip, deflate":
                    acceptGzip = True
                    acceptDeflate = True
                elif value == "gzip":
                    acceptGzip = True
                elif value == "deflate":
                    acceptDeflate = True


        if fGzip == True:
            self.printFn ("TODO: Add Decompress code for gzip")
        elif fDeflate == True:
            fData = zlib.decompress(fData)

        if fData != None:
            strData = fData.decode(encoding="utf-8")
            #json_obj = json.loads(strData)
            try:
                strData = fData.decode(encoding="utf-8")
                json_obj = json.loads(strData)
                #self.printFn (strData)
            except:
                #self.printFn ("JSON Decodeing Error")
                #self.printFn ("%s" % strData)
                #fFail = True
                json_obj = None
                pass
        
        if method == None or path == None:
            fFail = True

        ls_content_type = 'application/json'
        if fFail != True:
            ErrCode, json_obj = invorkCallback(method, path, json_obj)

            if json_obj != None:
                compressed_data = None
                if type(json_obj) == dict:
                    byte_data = str.encode(json.dumps(json_obj))

                elif type(json_obj) == str:
                    #ls_content_type = 'application/xml'
                    pass
                else:
                    ls_content_type = 'application/xml'
                    byte_data = str.encode(json_obj)
                if acceptDeflate == True:
                    compressed_data = zlib.compress(byte_data, 2)       
                    selectedTrEncode = "deflate"
                elif acceptGzip == True:
                    #TODO: Add GZip Compress Code
                    #selectedTrEncode = "gzip"
                    selectedTrEncode = None
                if compressed_data != None:
                    byte_data = compressed_data
        else:
            ErrCode = 400 # Bad Request

        header=[ ]       
        header.append(h2_base.get_head_tuple_by_name(':status', str(ErrCode)))
        header.append(h2_base.get_head_tuple_by_name('server', stack_name))

        if byte_data != None:
            header.append(h2_base.get_head_tuple_by_name('content-length', str(len(byte_data))))
            header.append(h2_base.get_head_tuple_by_name('content-type'  , ls_content_type))
            if selectedTrEncode != None:
                header.append(h2_base.get_head_tuple_by_name('content-encoding'  , selectedTrEncode))

            hdr_end_stream = False
        else:
            hdr_end_stream = True
    
        global perf_mode
        if perf_mode != True:
            self.traceFn(stream_id=stream_id, headers=header, end_stream=hdr_end_stream)
            self.traceFn(stream_id=stream_id, data=byte_data, end_stream=True)

        try:
            conn.send_headers(
                stream_id=stream_id,
                headers=header,
                end_stream=hdr_end_stream
            )
        except Exception as e:
            PRINT("Error: Fail to encode header frame, error=%s" % (e))
            return True

        if byte_data != None:
            conn.send_data(
                stream_id=stream_id,
                data=byte_data,
                end_stream=True
            )

    def __h2_check_client_exit(self, conn_type, th_index):
        if conn_type == h2_conn_type.CONNTYPE_CLIENT_REQUEST and self.conn_request_max <= th_index:
           return True;
        elif conn_type == h2_conn_type.CONNTYPE_CLIENT_NOTIFY and self.conn_notify_max <= th_index:
           return True;
        return False;


    def h2ServerRecvTh(self, __sock, invorkCallback ):
        self._h2_set_stat(h2_conn_type.CONNTYPE_SERVER,  1)
        self.h2RecvProc(__sock, invorkCallback, False, h2_conn_type.CONNTYPE_SERVER, -1, None)
        self._h2_set_stat(h2_conn_type.CONNTYPE_SERVER, -1)

    def h2ClientRecvTh(self, invorkCallback, IpAddr, Port, conn_type, th_index, src_ipaddr ):
        while self.isClose == False and self.__h2_check_client_exit(conn_type, th_index) == False:
            try:
                if is_valid_ip(src_ipaddr):
                    sock = socket.create_connection((IpAddr, Port), source_address=(src_ipaddr, 0))
                    #print ("IpAddr:%s, Port=%d, src_ipaddr=%s" % (IpAddr, Port, src_ipaddr))
                else:
                    sock = socket.create_connection((IpAddr, Port))
                if self.isClose == True:
                    sock.close()
                    return
            except:# (socket.error, ssl.error):
                for i in range(25):
                    sleep (0.1)
                    if self.isClose == True:
                        return
                continue
            self._h2_set_stat(conn_type,   1)
            self.h2RecvProc(sock, invorkCallback, True, conn_type, th_index, IpAddr)
            self._h2_set_stat(conn_type,  -1)

    def h2RecvProc(self, __sock, callback, client_side, conn_type, th_index, IpAddr):
        global enable_ping
        n_wait_select       = 0.0
        select_timer        = 0.1
        frame_Headers       = None
        frame_Data          = None
        frame_ctx           = {}
        scheme              = None
        conn_lock           = threading.Semaphore(1)
        opaque_data         = 10000000
        sent_opaque_data    = -1
        
        try:
            peer_port       = __sock.getpeername()[1]
            peer_ipaddr     = __sock.getpeername()[0]
        except:
            __sock.close()
            return


        if(self.isTls == True):
            sslObj = h2_TLS(self.server_cert, self.server_key, self.client_certs, self.client_key, client_side)
            sock = sslObj.negotiate_tls(__sock, IpAddr)
            if sock == None:
                #print("Error!! Fail to Open TLS Session")
                sleep(1.0)
                return
            scheme  = "HTTPS"
            _scheme = "https"
        else:
            sock = __sock
            scheme  = "HTTP"
            _scheme = "http"

        if client_side == True:
            conn_side="CLIENT"
            _conn_side="client"
        else:
            conn_side="SERVER"
            _conn_side="server"

        connection_id = "%s://%s:%d" % (_scheme, peer_ipaddr, peer_port)

        try:
            sock.setblocking(0)

            config  = h2.config.H2Configuration(client_side=client_side)
            http2_connection = neoH2Connection(connection_id, config=config)
            n_sz_hdr_table   = 4096     if "HEADER_TABLE_SIZE" not in h2_setting_dict.keys() else h2_setting_dict["HEADER_TABLE_SIZE"]
            http2_connection.local_settings  = h2.settings.Settings(client=client_side, initial_values={
                  h2.settings.SettingCodes.MAX_CONCURRENT_STREAMS   : 30000    if "MAX_STREAMS"       not in h2_setting_dict.keys() else h2_setting_dict["MAX_STREAMS"], 
                  h2.settings.SettingCodes.INITIAL_WINDOW_SIZE      : 65535000 if "INIT_WINDOW_SIZE"  not in h2_setting_dict.keys() else h2_setting_dict["INIT_WINDOW_SIZE"],
                  h2.settings.SettingCodes.ENABLE_PUSH              : 0        if "EN_PUSH"           not in h2_setting_dict.keys() else h2_setting_dict["EN_PUSH"],
                  h2.settings.SettingCodes.MAX_FRAME_SIZE           : 16384    if "MAX_FRAME_SIZE"    not in h2_setting_dict.keys() else h2_setting_dict["MAX_FRAME_SIZE"],
                  h2.settings.SettingCodes.MAX_HEADER_LIST_SIZE     : 65536    if "HEADER_LIST_SIZE"  not in h2_setting_dict.keys() else h2_setting_dict["HEADER_LIST_SIZE"],
                  h2.settings.SettingCodes.HEADER_TABLE_SIZE        : 4096     if "HEADER_TABLE_SIZE" not in h2_setting_dict.keys() else h2_setting_dict["HEADER_TABLE_SIZE"]
                })
            #http2_connection.encoder.header_table_size = n_sz_hdr_table

            http2_connection.initiate_connection()
            sock.sendall(http2_connection.data_to_send())
        except Exception as e:
            self.printFn("Error!! Fail to initiate_connection : %s\n" % (e))
            sock.close()
            if self.isTls == True:
                __sock.close()
            return
        
        self.set_base_stat("SEND", H2_FRAME_SETTINGS)
        if client_side == True:
            self.set_base_stat("SEND", H2_FRAME_MAGIC)

        p_conn_block = self.h2_append_connection_to_list(conn_type, sock, http2_connection, conn_lock)
        #p_conn_block = None

        #print( p_conn_block[2])

        self.printFn (" -- %s %s (%s) Connection idx:%-3d %sUP%s" % (scheme, conn_side, connection_id, th_index, C_YELLOW, C_END))

        input_list = [sock]
    
        last_timeout_check = 0
        detect_stream_id_max_time = None
        while self.isClose == False and self.__h2_check_client_exit(conn_type, th_index) == False:
            input_ready, write_ready, except_ready = select.select(input_list, [], input_list, select_timer)

            conn_lock.acquire()

    
            if p_conn_block != None:

                #1. check Timeout
                context_list = p_conn_block[4]
                now_time = timeit.default_timer()
                del_list = []
                if now_time - last_timeout_check > 1.0:
                    for stream_id in context_list.keys():
                        send_time = context_list[stream_id][3]
                        if now_time - send_time > 4.0:
                            #PRINT("Timeout: In Connection=%s, streamId=%d" % (connection_id, stream_id) )
                            #http2_connection.reset_stream(stream_id)
                            del_list.append(stream_id)

                    if len(del_list) != 0:
                        for stream_id in del_list:
                            http2_connection.reset_stream(stream_id)
                            del context_list[stream_id]
                        #data_to_send = http2_connection.data_to_send()
                        #굳이 지금 안보내도 나중에 나가겠지 뭐..

                # Handle stream Id reched MAX
                highest_outbound_stream_id = p_conn_block[3]["highest_outbound_stream_id"]
                if detect_stream_id_max_time == None and self.max_stream_id <= highest_outbound_stream_id:
                    detect_stream_id_max_time = timeit.default_timer()
                elif detect_stream_id_max_time != None:
                    n_sec_after = timeit.default_timer() - detect_stream_id_max_time
                    if n_sec_after > 2.25:
                        error_code = 0x00 # NO_ERROR
                        error_str  = ("http/2 stream reached Max : Max=%d, Highest_outbound_stream_id=%d" % (self.max_stream_id, highest_outbound_stream_id))
                        p_conn_block[3]["highest_outbound_stream_id"] = 1
                        self._h2_connection_close(conn_type, scheme, conn_side, peer_ipaddr, peer_port, __sock, sock, http2_connection, error_code, error_str, th_index)
                        conn_lock.release()
                        return

            if len(input_ready) <= 0:
                if enable_ping == True:
                    n_wait_select += select_timer
                    if n_wait_select > ping_interval and sent_opaque_data == -1:
                        n_wait_select = 0.0
                        opaque_data += 1
                        if opaque_data > 99999998:
                            opaque_data = 10000000
                        sent_opaque_data = opaque_data
                        self.h2_send_ping(sent_opaque_data, sock, http2_connection)
                    elif n_wait_select > ping_timeout and sent_opaque_data != -1:
                        error_str = ("Err. Ping Timeout")
                        self._h2_connection_close(conn_type, scheme, conn_side, peer_ipaddr, peer_port, __sock, sock, http2_connection, 1, error_str, th_index)
                        conn_lock.release()
                        return
                conn_lock.release()
                continue
           
            #conn_lock.acquire()
            try:
                data = sock.recv(65535)
                self.set_tps_stat("TRAFFIC", "IN", len(data))
                if not data:
                    conn_lock.release()
                    break
            except:# (socket.error, ssl.error):
                self._h2_connection_close(conn_type, scheme, conn_side, peer_ipaddr, peer_port, __sock, sock, None, 0, None, th_index)
                conn_lock.release()
                return


            try:
                events = http2_connection.receive_data(data)
            #except h2.exceptions.ProtocolError, e:
            except Exception as e:
                error_str = ("Err. Invalid Protocol : %s" % str(e))
                self._h2_connection_close(conn_type, scheme, conn_side, peer_ipaddr, peer_port, __sock, sock, http2_connection, 1, error_str, th_index)
                return


            #self.set_base_stat("RECV", )


            for event in events:
                #print("%s" % (event.frame))
                #print(dir(event))

                global perf_mode
                if perf_mode != True:
                    try:
                        self.traceFn(event=event)
                    except:
                        pass
                if isinstance(event, h2.events.RequestReceived) or isinstance(event, h2.events.ResponseReceived) :
                    frame_ctx["headers_%d" % (event.stream_id)] = event.headers
                if isinstance(event, h2.events.PingAcknowledged):
                    if enable_ping == False:
                        continue
                    __opaque_data = int("%s" % (event.ping_data.decode("utf-8")))
                    if sent_opaque_data == __opaque_data:
                        sent_opaque_data = -1
                        continue

                    error_str = "Err. Recv invalid ping ack : sent_opaque_data=%d, recv_opaque_data=%d" %(sent_opaque_data, __opaque_data)
                    self._h2_connection_close(conn_type, scheme, conn_side, peer_ipaddr, peer_port, __sock, sock, http2_connection, 1, error_str, th_index)
                    conn_lock.release()
                    return

                if isinstance(event, h2.events.DataReceived):
                    key_name = "data_%d"    % (event.stream_id)

                    if key_name in frame_ctx:
                        tmp = frame_ctx[key_name] + event.data
                        del frame_ctx[key_name]
                        frame_ctx[key_name] = tmp
                    else:
                        frame_ctx[key_name] = event.data

                    #if client_side==False:
                    #    http2_connection.increment_flow_control_window(len(event.data), event.stream_id)

                    n_remain_window = http2_connection.outbound_flow_control_window
                    n_sizeof_window = http2_connection.remote_settings.initial_window_size
                    if n_remain_window < int(n_sizeof_window/2.0):
                        http2_connection.increment_flow_control_window(int(n_sizeof_window/3.0), None)
                        #http2_connection.increment_flow_control_window(100, None)
                        #print("Send increment_flow_control_window!!")
                    
                    #print("n_remain_window:%d , n_sizeof_window:%d" % (n_remain_window, n_sizeof_window))
                    if len(event.data) > 0:
                        http2_connection.increment_flow_control_window(len(event.data), None)

                    data_to_send = http2_connection.data_to_send()
                    if data_to_send:
                        try:
                            sock.sendall(data_to_send)
                        except:# (socket.error, ssl.error):
                            self._h2_connection_close(conn_type, scheme, conn_side, peer_ipaddr, peer_port, __sock, sock, None, 0, None, th_index)
                            conn_lock.release()
                            return
                if isinstance(event, h2.events.RemoteSettingsChanged):
                    #http2_connection.remote_settings =
                    new_setting = {}
                    for key in event.changed_settings.keys():
                        #print ("%s:%s" % (key, event.changed_settings[key].new_value))
                        new_setting[key]=event.changed_settings[key].new_value

                    http2_connection.remote_settings               = h2.settings.Settings(client=client_side, initial_values=new_setting)
                    http2_connection.outbound_flow_control_window  = http2_connection.remote_settings.initial_window_size
                    http2_connection.max_outbound_frame_size       = http2_connection.remote_settings.max_frame_size
                    #p_conn_block = self.h2_append_connection_to_list(conn_type, sock, http2_connection, conn_lock)

                if isinstance(event, h2.events.StreamEnded):
                    frame_Headers = frame_ctx["headers_%d" % (event.stream_id)]
                    key_name = "data_%d" % (event.stream_id)
                    if key_name in frame_ctx:
                        frame_Data    = frame_ctx[key_name]
                    else:
                        frame_Data    = None

                    if client_side==True:
                        self.set_tps_stat("CALL", "OUT")
                        self.h2_recv_enswer(http2_connection, event.stream_id, frame_Headers, frame_Data, callback)
                    else:
                        if enable_response != False:
                            self.set_tps_stat("CALL", "IN")
                            if responce_delay > 0.0001:
                                sleep(responce_delay)
                            self.h2_send_response(http2_connection, event.stream_id, frame_Headers, frame_Data, callback)

                    del frame_ctx["headers_%d" % (event.stream_id)]
                    if frame_Data != None:
                        del frame_ctx["data_%d"    % (event.stream_id)]

            data_to_send = http2_connection.data_to_send()
            if data_to_send:
                try:
                    sock.sendall(data_to_send)
                except:# (socket.error, ssl.error):
                    self._h2_connection_close(conn_type, scheme, conn_side, peer_ipaddr, peer_port, __sock, sock, None, 0, None, th_index)
                    conn_lock.release()
                    return
            conn_lock.release()

        self._h2_connection_close(conn_type, scheme, conn_side, peer_ipaddr, peer_port, __sock, sock, http2_connection, 0, None, th_index)

        return
        
    def h2_send_ping(self, opaque_data, sock, http2_connection):
        http2_connection.ping(str(opaque_data).encode('utf-8'))
        try:
            sock.sendall(http2_connection.data_to_send())
        except:# (socket.error, ssl.error):
            self.printFn("Err. Fail to send PING")
            return False
        return True

    def h2WaitForAcceptTh(self, Port, invorkCallback):
        """
        This function establishes a server-side TCP connection. How it works isn't
        very important to this example.
        """
        bind_socket = socket.socket()
        bind_socket.setblocking(0)

        try:
            socket.SO_REUSEPORT
        except AttributeError:
            err_str="Err. Not defined <socket.SO_REUSEPORT, PORT:%d>" % (Port)
            self.printFn (err_str)
        else:
            bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        bind_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        bind_socket.bind((self.LocalIP, Port))
        bind_socket.listen(5)
        #self.printFn ("Thread: h2WaitForAcceptTh")
        input_list = [bind_socket]

        while self.isClose == False :
            input_ready, write_ready, except_ready = select.select(input_list, [], [], 0.1)
            for ir in input_ready:
                if ir == bind_socket:
                    try:
                        aSock   = bind_socket.accept()[0]
                        if self.isClose == True :
                            aSock.close()
                            return
                        hThread = threading.Thread(target=self.h2ServerRecvTh, args=(aSock, invorkCallback ))
                        hThread.daemon = True
                        hThread.start()
                        '''
                        hProcess = Process(target=self.h2ServerRecvTh, args=(aSock, invorkCallback ))
                        hProcess.start()
                        '''
                    except:# (socket.error, ssl.error):
                        #self.printFn("Err, h2WaitForAcceptTh except")
                        print("Err, h2WaitForAcceptTh except")
                        break
                sleep(0.1)

        #self.printFn ("Thread: h2WaitForAcceptTh end")

    def h2SetDefaultCallback(self, func):
        self.serverDefaultCallback = func

    def h2_append_connection_to_list(self, conn_type, sock, h2_conn, lock):
        #p_conn_block = [conn_type, sock, h2_conn, 1, {}, lock]
          
        p_conn_block = [conn_type, sock, h2_conn, {"highest_outbound_stream_id": 1, "time" : timeit.default_timer()}, {}, lock]
        self.lock.acquire()
        self.conn_list.append(p_conn_block)
        self.lock.release()

        return p_conn_block
        
    def h2_delete_connection_to_list(self, conn_type, sock):
        i = 0
        for item in self.conn_list:
            if item[0] == conn_type and item[1] == sock:
                self.conn_list.remove(item)
                break
            i += 1

    def _h2_set_stat(self, conn_type, value):
        self.lock.acquire()
        if conn_type == h2_conn_type.CONNTYPE_SERVER            :
            self.count_server           += value
        elif conn_type == h2_conn_type.CONNTYPE_CLIENT_NOTIFY   :
            self.count_notify_client    += value
        elif conn_type == h2_conn_type.CONNTYPE_CLIENT_REQUEST  :
            self.count_request_client   += value
        self.lock.release()

    def h2_get_conn_cnt(self, conn_type=None):
        if conn_type == h2_conn_type.CONNTYPE_SERVER            :
            return self.count_server
        elif conn_type == h2_conn_type.CONNTYPE_CLIENT_NOTIFY   :
            return self.count_notify_client
        elif conn_type == h2_conn_type.CONNTYPE_CLIENT_REQUEST  :
            return self.count_request_client
        elif conn_type == None                                  :
            return self.count_server + self.count_notify_client + self.count_request_client 
        else:
            return 0

    def h2_find_connection_from_list(self, sock):
        i = 0
        for item in self.conn_list:
            if item[2] == sock:
                return item
        return None

    def h2_get_connection(self, conn_type):
        tmpList = []
        for idx, item in enumerate(self.conn_list):
            if item[0] == conn_type:
                tmpList.append(idx)

        connCnt = len(tmpList)

        if connCnt == 0:
            return None
        
        '''############################## NOT-RANDUN
        self.rrIndex += 1
        seleted_idx = tmpList[ (self.rrIndex - 1) % connCnt]
        '''##############################

        ############################## RANDUN
        MAX_RANGE = 25
        #print("h2_peer_cnt:%d" % h2_peer_cnt)
        while True:
            self.rrIndex += 1
            seleted_idx      = tmpList[(self.rrIndex - 1) % connCnt]
            neo_seleted_idx  = seleted_idx if seleted_idx < MAX_RANGE/2 else MAX_RANGE/2

            n_rand = random.randrange(1,MAX_RANGE)

            if n_rand < neo_seleted_idx:
                continue
            else:
                break
        ##############################


        #hdr_info     = self.conn_list[seleted_idx][3]
        #hdr_info["highest_outbound_stream_id"] += 2
        return self.conn_list[seleted_idx]

    def h2_send_request(self, conn_type, method, path, payload):
        byte_data     = None
        end_stream    = True

        #l_timeit=SET_TIMEIT()
        connLiet      = self.h2_get_connection(conn_type)

        if connLiet == None:
            return False

        conn_lock    = connLiet[5]
        conn_lock.acquire()

        hdr_info     = connLiet[3]
        if timeit.default_timer() - hdr_info["time"] < 2.25:
            conn_lock.release()
            return False

        peerIp       = ""
        peerPort     = ""
        sock         = connLiet[1]
        h2_conn      = connLiet[2]
        stream_id    = hdr_info["highest_outbound_stream_id"]
        context_list = connLiet[4]


        hdr_info["highest_outbound_stream_id"] = stream_id + 2
        #del hdr_info

        #stream_id    = h2_conn.get_next_outbound_stream_id()
        #stream_id = copy.deepcopy(self.g_stream_id)
        #self.g_stream_id += 2
        #del self.g_stream_id

        if stream_id > self.max_stream_id:
            conn_lock.release()
            return False

        if self.isTls == True:
            scheme = 'https'
        else:
            scheme = 'http'

        try:
            peerIp   = sock.getpeername()[0]
            peerPort = sock.getpeername()[1]
        except:
            self.printFn("Error. getpeername fail")
            conn_lock.release()
            return False

        #t1 = HeaderTuple('name', 'value')
        #t2 = NeverIndexedHeaderTuple('name', 'value')
        hd_auth = '%s:%d' % (peerIp, peerPort)
        '''
        header=[
            (':method', method),
            (':scheme', scheme),
            (':authority', hd_auth),
            ('accept', '*/*'),
            ('accept-encoding', 'gzip, deflate'),
            ('user-agent', 'nghttp2/1.29.0-DEV'),
        ]

        #header.append(NeverIndexedHeaderTuple(b':path', path.encode("ascii")))
        header.append(':path', path)

        if payload != None:
            request_data = json.dumps(payload)
            byte_data = str.encode(request_data)
            header.append(NeverIndexedHeaderTuple('content-length', str(len(byte_data))))
            header.append(('content-type'  , 'application/json'))
            end_stream = False



        '''
        hd_auth = '%s:%d' % (peerIp, peerPort)
        header=[
            h2_base.get_head_tuple_by_name(':method', method),
            h2_base.get_head_tuple_by_name(':scheme', scheme),
            h2_base.get_head_tuple_by_name(':authority', hd_auth),
        ]

        header.append(h2_base.get_head_tuple_by_name(':path', path))
        header.append(h2_base.get_head_tuple_by_name('accept', '*/*'))
        #header.append(h2_base.get_head_tuple_by_name('accept-encoding', 'gzip, deflate'))
        header.append(h2_base.get_head_tuple_by_name('user-agent', stack_name))

        #SET_TIMEIT(l_timeit)
        if payload != None:

            if type(payload) != bytes:
                raw_json = payload if type(payload) == str else json.dumps(payload)
                request_data = json.dumps(payload)
                byte_data = str.encode(request_data)
            else:
                byte_data = payload

            header.append(h2_base.get_head_tuple_by_name('content-length', str(len(byte_data))))
            header.append(h2_base.get_head_tuple_by_name('content-type'  , 'application/json'))
            end_stream = False

        #SET_TIMEIT(l_timeit)
        try:
            h2_conn.send_headers(
                stream_id=stream_id,
                headers=header,
                end_stream=end_stream
            )   
        except h2.exceptions.TooManyStreamsError:
            conn_lock.release()
            self.printFn("Error, Ongoing outbound streams reached MAX (h2.exceptions.TooManyStreamsError)")
            return False
        except Exception as e:
            conn_lock.release()
            self.printFn("Error, stream_id:%d, error:%s" % (stream_id,e))
            return False

        #SET_TIMEIT(l_timeit)
        if byte_data != None:
            h2_conn.send_data(
                stream_id=stream_id,
                data=byte_data,
                end_stream=True
            )   

        #SET_TIMEIT(l_timeit)
        context_list[stream_id] = [ method, path, payload, timeit.default_timer() ]
        
        global perf_mode
        if perf_mode != True:
            self.traceFn(stream_id=stream_id, headers=header, end_stream=end_stream)
            self.traceFn(stream_id=stream_id, data=byte_data, end_stream=True)

        #nErr = pickle.dumps(h2_conn)
        #print(nErr)

        #SET_TIMEIT(l_timeit)
        data_to_send = h2_conn.data_to_send()
        #SET_TIMEIT(l_timeit)
        if data_to_send:
            try:
                sock.sendall(data_to_send)
            except:
                self.printFn("Error. sendall fail")
                conn_lock.release()
                return False

        #del connLiet
        conn_lock.release()
        #PRINT_TIMEIT(l_timeit)

        return True


    def h2_send_request_N(self, conn_type, method, path, payload, n_request=1):
        byte_data     = None
        end_stream    = True

        connLiet      = self.h2_get_connection(conn_type)

        if connLiet == None:
            return None

        peerIp       = ""
        peerPort     = ""
        sock         = connLiet[1]
        h2_conn      = connLiet[2]
        stream_id    = connLiet[3]
        context_list = connLiet[4]
        conn_lock    = connLiet[5]

        conn_lock.acquire()

        if self.isTls == True:
            scheme = 'https'
        else:
            scheme = 'http'

        try:
            peerIp   = sock.getpeername()[0]
            peerPort = sock.getpeername()[1]
        except:
            self.printFn("Error. getpeername fail")
            conn_lock.release()
            return -1

        hd_auth = '%s:%d' % (peerIp, peerPort)
        header=[
            h2_base.get_head_tuple_by_name(':method', method),
            h2_base.get_head_tuple_by_name(':scheme', scheme),
            h2_base.get_head_tuple_by_name(':authority', hd_auth),
        ]

        #header.append(NeverIndexedHeaderTuple(':path', ""))
        header.append(h2_base.get_head_tuple_by_name(':path', ""))
        header.append(h2_base.get_head_tuple_by_name('accept', '*/*'))
        header.append(h2_base.get_head_tuple_by_name('accept-encoding', 'gzip, deflate'))
        header.append(h2_base.get_head_tuple_by_name('user-agent', stack_name))

        if payload != None:
            request_data = json.dumps(payload)
            byte_data = str.encode(request_data)
            header.append(h2_base.get_head_tuple_by_name('content-length', str(len(byte_data))))
            header.append(h2_base.get_head_tuple_by_name('content-type'  , 'application/json'))
            end_stream = False

        path_head = None
        path_base = None
        path_tail = None
        if type(path) == list:
            path_head = path[0]
            path_base = path[1]
            path_tail = path[2]
        else:
            header[3]   = NeverIndexedHeaderTuple(':path', path )
    
        #do_async_work
        #'''
        data_pairs = []
        for i in range(n_request):
            data_pair  = {}

            stream_id   = connLiet[3]
            if path_head != None:
                header[3]   = NeverIndexedHeaderTuple(':path', "%s%06d%s" % (path_base, path_base + i, path_tail))

            data_pair["data"]      = byte_data
            data_pair["header"]    = header[0:]
            data_pair["stream_id"] = stream_id

            data_pairs.append(data_pair)

            connLiet[3]+=2 # Increase stream Id

        #####################################
        #h2_conn = do_async_work(h2_base.h2_request_worker, [pickle.dumps(h2_conn), data_pairs,])
        #connLiet[2] = h2_conn

        #h2_conn = h2_base.h2_request_worker(pickle.dumps(h2_conn), data_pairs)
        #connLiet[2] = h2_conn

        do_async_work(h2_base.h2_request_worker, [h2_conn, data_pairs,])
        #####################################

        data_to_send = h2_conn.data_to_send()
        if data_to_send:
            try:
                sock.sendall(data_to_send)
            except:
                self.printFn("Error. sendall fail")
                conn_lock.release()
                return -1
        #'''

        '''
        for i in range(n_request):

            stream_id   = connLiet[3]
            if path_head != None:
                header[3]   = NeverIndexedHeaderTuple(':path', "%s%06d%s" % (path_base, path_base + i, path_tail))
            try:
                h2_conn.send_headers(
                    stream_id=stream_id,
                    headers=header,
                    end_stream=end_stream
                )   
            except h2.exceptions.TooManyStreamsError:
                conn_lock.release()
                self.printFn("Error, Ongoing outbound streams reached MAX (h2.exceptions.TooManyStreamsError)")
                return 0

            if byte_data != None:
                h2_conn.send_data(
                    stream_id=stream_id,
                    data=byte_data,
                    end_stream=True
                )   

            #context_list[stream_id] = [ method, header[3], payload ]
            #
            #global perf_mode
            #if perf_mode != True:
                #self.traceFn(stream_id=stream_id, headers=header, end_stream=end_stream)
                #self.traceFn(stream_id=stream_id, data=byte_data, end_stream=True)

            data_to_send = h2_conn.data_to_send()
            if data_to_send:
                try:
                    sock.sendall(data_to_send)
                except:
                    self.printFn("Error. sendall fail")
                    conn_lock.release()
                    return -1

            connLiet[3]+=2 # Increase stream Id
        '''

        conn_lock.release()

        return 1

    @staticmethod
    def h2_request_worker(h2_conn, data_pairs):
        if type(h2_conn) == str:
            h2_conn    = pickle.loads(h2_conn)

        for idx, pair in enumerate(data_pairs):
            header     = pair["header"]
            #print(header)
            byte_data  = pair["data"]
            stream_id  = pair["stream_id"]
            end_stream = False if byte_data != None else True



            for idx, item in enumerate(header):
                #print ("idx:%d, %s" % (idx, item))
                if type(item) == tuple and len(item) == 2:
                    continue
                elif len(item) == 1 and type(item[0] == tuple):
                    header[idx] = NeverIndexedHeaderTuple(item[0][0], item[0][1] )
                else:
                    continue

            #print("stream_id:%d\nheader:%s"% (stream_id, header))
            try:
                h2_conn.send_headers(
                    stream_id=stream_id,
                    headers=header,
                    end_stream=end_stream
                )   
            except h2.exceptions.TooManyStreamsError:
                conn_lock.release()
                print("Error, Ongoing outbound streams reached MAX (h2.exceptions.TooManyStreamsError)")
                #return (False, h2_conn)
                return h2_conn

            if byte_data != None:
                h2_conn.send_data(
                    stream_id=stream_id,
                    data=byte_data,
                    end_stream=True
                )   

        #return (True, h2_conn)
        return h2_conn


    def _h2_connection_close(self, conn_type, scheme, conn_side, peer_ipaddr, peer_port,  org_sock, sock, h2_conn, error_code, error_reason, th_index):
        error_str       = ""
        __error_reason  = None

        self.printFn (" -- %s %s (%s:%d) Connection idx:%-3d %sDOWN%s" % (scheme, conn_side, peer_ipaddr, peer_port, th_index, C_RED, C_END ))
        if error_reason != None:
            error_str = "%s" % (error_reason)
            __error_reason = error_reason.encode('utf-8')
            self.printFn (" -- %s" % (error_str), tab=2)

        self.h2_delete_connection_to_list(conn_type, sock)
        try:
            if h2_conn != None:
                h2_conn.close_connection(error_code=error_code, additional_data=__error_reason)
                sock.sendall(h2_conn.data_to_send())
            sock.close()
            if self.isTls == True:
                org_sock.close()
        except:# (socket.error, ssl.error):
            return False       

        return True

    @staticmethod
    def get_head_tuple_by_name(field, value):
        #header_tuple = (field, value,)
        if field in header_indexing_rule_table.keys():
            return header_indexing_rule_table[field](field, value)
        else:
            return header_indexing_rule_table["__default__"](field, value)

    @staticmethod
    def set_head_tuple_by_name(field, is_indexed=True):

        if field == "__ALL__":
            for field in header_indexing_rule_table.keys():
                header_indexing_rule_table[field] = HeaderTuple if is_indexed == True else NeverIndexedHeaderTuple
            return 

        if field not in header_indexing_rule_table.keys():
            LOG(LOG_MIN, "Insert new item in Header indexing table : field=%s" % (field));
            header_indexing_rule_table[field] = None

        header_indexing_rule_table[field] = HeaderTuple if is_indexed == True else NeverIndexedHeaderTuple
 
    @staticmethod
    def show_head_indxing_rule():
        PRINT("%s" % (LINE80))
        PRINT("  %-24s   %s" % ("[FIELD]", "[INDEX_RULE]"))
        PRINT("%s" % (line80))
        for field in header_indexing_rule_table.keys():
            index_rule = "literal header field with incremental indexing" if header_indexing_rule_table[field] == HeaderTuple else "literal header field never indexed"
            PRINT("  %-24s : %s" % (field, index_rule))
        PRINT("%s" % (LINE80))


    @staticmethod
    def set_responce_delay(val):
        global responce_delay
        responce_delay = val

    @staticmethod
    def get_responce_delay():
        global responce_delay
        return responce_delay

    @staticmethod
    def set_request_timeout(val):
        global request_timeout
        request_timeout = val

    @staticmethod
    def get_request_timeout():
        global request_timeout
        return request_timeout

    @staticmethod
    def set_enable_response(val):
        global enable_response
        enable_response = val

    @staticmethod
    def set_enable_ping(val):
        global enable_ping
        enable_ping = val

    @staticmethod
    def set_ping_interval(val):
        global ping_interval
        ping_interval = val

    @staticmethod
    def set_ping_timeout(val):
        global ping_timeout
        ping_timeout = val

    @staticmethod
    def get_ping_interval():
        return ping_interval

    @staticmethod
    def get_ping_timeout():
        return ping_timeout

    @staticmethod
    def set_perf_mode(val):
        global perf_mode
        perf_mode = val

    @staticmethod
    def set_inital_setting_list(s_dict):
        global h2_setting_dict
        h2_setting_dict = s_dict
 
   
sem = threading.Semaphore(1) 
invoke_count = 0
resume_count = 0

def exam_Invoke_Callback(method, path, data):
    resultCode = 200
    resultData = data
    
    #self.printFn ("method : %s" % method)
    #self.printFn ("path   : %s" % path)
    #self.printFn ("data   : %s" % data)
    global invoke_count
    sem.acquire()
    invoke_count += 1
    sem.release()
    return resultCode, resultData


def exam_Resume_Callback(req_method, req_path, req_data, asw_code, asw_data):
    self.printFn ("req_method : %s" % req_method)
    self.printFn ("req_path   : %s" % req_path)
    self.printFn ("req_data   : %s" % req_data)
    self.printFn ("asw_code   : %d" % asw_code)
    self.printFn ("asw_data   : %s" % asw_data)

    global resume_count
    sem.acquire()
    resume_count += 1
    sem.release()
    return None


if __name__ == '__main__':
    e = h2_base(LocalIP = "0.0.0.0", PeerIP = "192.168.20.100", 
               #LocalServicePort = 8888, LocalNotifyPort = 8887, PeerServicePort = 18888, PeerNotifyPort = 18887, 
               #LocalConnType=h2_service_type.SERVICE_CONSUMER, 
               #isTls = True, 
               LocalServicePort = 9998, LocalNotifyPort = 9998, PeerServicePort = 18888, PeerNotifyPort = 18888, 
               LocalConnType=h2_service_type.SERVICE_CONSUMER, 
               isTls = False, 
               server_cert = "./certification/client.crt", server_key = "./certification/client.key", client_certs = "./certification/server.crt", client_key = "./certification/server.key", )

    #e.h2SetDefaultCallback(exam_Callback)
    e.h2OpenServer(exam_Invoke_Callback)
    e.h2OpenClient(exam_Resume_Callback)
    sleep(0.5)
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )
    e.h2_send_request(h2_conn_type.CONNTYPE_CLIENT_REQUEST, "GET", "/index.html", None )

    old_invoke  = 0
    old_resume  = 0
    while True:
        self.printFn ("TPS: invoke=%d, resume=%d TOTAL: invoke=%d, resume=%d" % (invoke_count - old_invoke, resume_count - old_resume, invoke_count, resume_count))
        old_invoke = invoke_count
        old_resume = resume_count
        sleep(1)







