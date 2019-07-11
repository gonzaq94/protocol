# -*- coding: utf-8 -*-
from twisted.internet.protocol import Protocol
import time
import struct

class SibylClientTcpBinProtocol(Protocol):
    """
    The class implementing the Sibyl TCP binary client protocol.  It has
    the following attribute:

    .. attribute:: proxy

        The reference to the SibylCientProxy (instance of the
        :py:class:`~sibyl.main.sibyl_client_proxy.SibylClientProxy` class).

        .. warning::
            All interactions between the client protocol and the user
            interface *must* go through the SibylClientProxy.  In other
            words you must call one of the methods of
            :py:class:`~sibyl.main.sibyl_client_proxy.SibylClientProxy`
            whenever you would like the user interface to do something.

    .. note::
        You must not instantiate this class.  This is done by the code
        called by the main function.

    .. note::
        You have to implement this class.  You may add any attribute and
        method that you see fit to this class.  You must implement two
        methods:
        :py:meth:`~sibyl.main.protocol.sibyl_cliend_udp_text_protocol.sendRequest`
        and
        :py:meth:`~sibyl.main.protocol.sibyl_cliend_udp_text_protocol.dataReceived`.
        See the corresponding documentation below.
    """

    def __init__(self, sibylProxy):
        """The implementation of the UDP Text Protocol.

        Args:
            sibylClientProxy: the instance of the client proxy,
                        this is the only way to interact with the user
                        interface;
        """
        self.clientProxy = sibylProxy
        self.packet_length = 0
        self.tcp_msg = bytearray()
        self.timestamp = 0
        self.processed_header = False
        self.header_length = 6
        self.b1 = bytearray()
        self.b2 = bytearray()

    def connectionMade(self):
        """
        The Graphical User Interface (GUI) needs this function to know
        when to display the request window.

        DO NOT MODIFY IT.
        """
        self.clientProxy.connectionSuccess()
        pass

    def sendRequest(self, line):
        """Called by the controller to send the request

        The :py:class:`~sibyl.main.sibyl_client_proxy.SibylClientProxy` calls
        this method when the user clicks on the "Send Question" button.

        Args:
            line (string): the text of the question

        .. warning::
            You must implement this method.  You must not change the parameters,
            as the controller calls it.

        """
        timestamp_bin = (int(time.time())).to_bytes(4,'big')
        timestamp_bin = timestamp_bin[::-1]
        package_len = self.header_length + len(line)
        encoded_msg = line.encode('ascii', 'replace')
        [b1, b2] = package_len.to_bytes(2,'big')       
        package_bin = struct.pack("BBBBbb"+str(len(line))+"s", timestamp_bin[3],timestamp_bin[2],timestamp_bin[1],timestamp_bin[0], b1, b2, encoded_msg)        
        self.transport.write(package_bin)
        pass

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
            (b1, b2, b3, b4, self.b1, self.b2) = struct.unpack_from("BBBBbb", self.tcp_msg, offset=0)
            self.timestamp = int(b1 + b2 + b3 + b4)
            self.packet_length = int(self.b1+self.b2)
            self.processed_header = True
        if len(self.tcp_msg) >= self.packet_length and self.processed_header :
            (_,_,_,_,_,_,server_msg) = struct.unpack_from("BBBBbb"+str(self.packet_length-self.header_length)+"s", self.tcp_msg, offset=0)
            response = server_msg.decode('ascii')
            
            self.processed_header = False
            self.packet_length = 0
            self.timestamp = 0
            self.tcp_msg = self.tcp_msg[self.packet_length:]
            self.b1 = bytearray()
            self.b2 = bytearray()

            self.clientProxy.responseReceived(response)     
        pass
    
