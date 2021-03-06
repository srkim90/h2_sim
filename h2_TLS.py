# -*- coding: utf-8 -*-

'''
  Author   : Kim, Seongrae
  Filename : h2_TLS.py
  Release  : 1
  Date     : 2018-07-02
 
  Description : HTTP/2 tls protocol module
 
  Notes :
  ===================
  History
  ===================
  2018/07/02  created by Kim, Seongrae
'''
import socket
import ssl

class h2_TLS:
    ctx = None
    tls_conn = None
    def __init__(self, server_cert, server_key, client_certs, client_key, client_side ):
        self.server_cert    = server_cert
        self.server_key     = server_key
        self.client_certs   = client_certs
        self.client_key     = client_key
        self.client_side    = client_side

        #self.ctx = self.__get_http2_ssl_context()


        self.__get_http2_ssl_context()

    def __get_http2_ssl_context(self):
        """
        This function creates an SSLContext object that is suitably configured for
        HTTP/2. If you're working with Python TLS directly, you'll want to do the
        exact same setup as this function does.
        """
        # Get the basic context from the standard library.
        if self.client_side == False:
            #self.ctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            self.ctx = ssl._create_unverified_context()
        else:
            #self.ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=self.server_cert)
            #self.ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH)
            self.ctx = ssl._create_unverified_context()

        # RFC 7540 Section 9.2: Implementations of HTTP/2 MUST use TLS version 1.2
        # or higher. Disable TLS 1.1 and lower.
        self.ctx.options |= (
            ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
        )

        # RFC 7540 Section 9.2.1: A deployment of HTTP/2 over TLS 1.2 MUST disable
        # compression.
        self.ctx.options |= ssl.OP_NO_COMPRESSION

        # RFC 7540 Section 9.2.2: "deployments of HTTP/2 that use TLS 1.2 MUST
        # support TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256". In practice, the
        # blacklist defined in this section allows only the AES GCM and ChaCha20
        # cipher suites with ephemeral key negotiation.


        if self.client_side == False:
            self.ctx.load_cert_chain(certfile=self.server_cert, keyfile=self.server_key)
            self.ctx.load_verify_locations(cafile=self.client_certs)                
        else:
            self.ctx.load_cert_chain(certfile=self.client_certs, keyfile=self.client_key)
            self.ctx.load_verify_locations(cafile=self.client_certs)                
            pass



        # We want to negotiate using NPN and ALPN. ALPN is mandatory, but NPN may
        # be absent, so allow that. This setup allows for negotiation of HTTP/1.1.
        self.ctx.set_alpn_protocols(["h2", "http/1.1"])

        try:
            self.ctx.set_npn_protocols(["h2", "http/1.1"])
        except NotImplementedError as e:
            print("TLS Error: NotImplementedError=%s" % (e))
            pass

        #self.ctx = ctx

        return True

    def getTlsConn(self, ):
        return self.tls_conn 

    def negotiate_tls(self, tcp_sock, peer_ipaddr):
        """
        Given an established TCP connection and a HTTP/2-appropriate TLS context,
        this function:

        1. wraps TLS around the TCP connection.
        2. confirms that HTTP/2 was negotiated and, if it was not, throws an error.
        """
        try:
            # Note that SNI is mandatory for HTTP/2, so you *must* pass the
            # server_hostname argument.
            if self.client_side == False:
                self.tls_conn = self.ctx.wrap_socket(tcp_sock, server_side=True)
            else:
                self.tls_conn = self.ctx.wrap_socket(tcp_sock, server_hostname=peer_ipaddr)
        except Exception as e:
            #print("Fail to create tls connection1!! : client_side=%s, Err=%s" % (self.client_side, e))
            return None
	
            # Always prefer the result from ALPN to that from NPN.
            # You can only check what protocol was negotiated once the handshake is
            # complete.
        try:
            negotiated_protocol = self.tls_conn.selected_alpn_protocol()
            if negotiated_protocol is None:
                negotiated_protocol = self.tls_conn.selected_npn_protocol()

            if negotiated_protocol != "h2":
                print("Err. negotiated_protocol=%s" % (negotiated_protocol))
                raise RuntimeError("Didn't negotiate HTTP/2!")
        except Exception as e:
            print("Fail to create tls connection2!! : %s" % (e))
            return None
        
        #print("%s" % self.ctx.client_random())
        #print("%s" % ssl.Connection.client_random())
        #print(self.tls_conn._sslobj.SSL_get_client_random())
        #print(self.ctx.SSL_get_client_random())

        return self.tls_conn
            
    def getHost(self, ip):
        """
        This method returns the 'True Host' name for a
        given IP address
        """
        try:
            data = socket.gethostbyaddr(ip)
            host = repr(data[0])
            return host
        except Exception:
            # fail gracefully
            return ip








