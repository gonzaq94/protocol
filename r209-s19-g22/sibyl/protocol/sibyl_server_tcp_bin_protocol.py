# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import time
import struct

class SibylServerTcpBinProtocol(Protocol):
    """The class implementing the Sibyl TCP binary server protocol.

        .. note::
            You must not instantiate this class.  This is done by the code
            called by the main function.

        .. note::

            You have to implement this class.  You may add any attribute and
            method that you see fit to this class.  You must implement the
            following method (called by Twisted whenever it receives data):
            :py:meth:`~sibyl.main.protocol.sibyl_server_tcp_bin_protocol.dataReceived`
            See the corresponding documentation below.

    This class has the following attribute:

    .. attribute:: SibylServerProxy

        The reference to the SibylServerProxy (instance of the
        :py:class:`~sibyl.main.sibyl_server_proxy.SibylServerProxy` class).

            .. warning::

                All interactions between the client protocol and the server
                *must* go through the SibylServerProxy.

    """

    def __init__(self, sibylServerProxy):
        """The implementation of the UDP server text protocol.

        Args:
            sibylServerProxy: the instance of the server proxy.
        """
        self.sibylServerProxy = sibylServerProxy
        self.header_length = 6
        self.packet_length = 0
        self.tcp_msg = bytearray()
        self.b1 = bytearray()
        self.b2 = bytearray()
        self.timestamp = 0
        self.processed_header = False
    def dataReceived(self, line):
        """Called by Twisted whenever a data is received

        Twisted calls this method whenever it has received at least one byte
        from the corresponding TCP connection.

        Args:
            line (bytes): the data received (can be of any length greater than
            one);

        .. warning::
            You must implement this method.  You must not change the parameters,
            as Twisted calls it.

        """
        self.tcp_msg += line
        if len(self.tcp_msg) >= self.header_length and not self.processed_header :
            (self.timestamp, self.b1, self.b2) = struct.unpack_from("ibb", self.tcp_msg, offset=0)
            self.packet_length = int(self.b1+self.b2)
            self.processed_header = True
        if len(self.tcp_msg) >= self.packet_length and self.processed_header :
            (_,_,_,client_msg) = struct.unpack_from("ibb"+str(self.packet_length-self.header_length)+"s", self.tcp_msg, offset=0)
            
            question = client_msg.decode('ascii')
            response = self.sibylServerProxy.generateResponse(question)
            encoded_response = response.encode('ascii', 'replace')
            package_len = self.header_length + len(encoded_response)
            package_bin = struct.pack("ibb"+str(len(encoded_response))+"s", self.timestamp, self.b1, self.b2, encoded_response)
            
            self.processed_header = False
            self.packet_length = 0
            self.timestamp = 0
            self.tcp_msg = self.tcp_msg[self.packet_length:]
            self.b1 = bytearray()
            self.b2 = bytearray()

            self.transport.write(package_bin)

        pass
    
