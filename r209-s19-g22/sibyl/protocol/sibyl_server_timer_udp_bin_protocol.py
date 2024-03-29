# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
import struct
from twisted.internet import reactor
import math

class SibylServerTimerUdpBinProtocol(DatagramProtocol):
    """The class implementing the Sibyl UDP binary server protocol.

        .. note::
            You must not instantiate this class.  This is done by the code
            called by the main function.

        .. note::

            You have to implement this class.  You may add any attribute and
            method that you see fit to this class.  You must implement the
            following method (called by Twisted whenever it receives a
            datagram):
            :py:meth:`~sibyl.main.protocol.sibyl_server_udp_bin_protocol.datagramReceived`
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

    def datagramReceived(self, datagram, host_port):
        """Called by Twisted whenever a datagram is received

        Twisted calls this method whenever a datagram is received.

        Args:
            datagram (bytes): the payload of the UPD packet;
            host_port (tuple): the source host and port number.

            .. warning::
                You must implement this method.  You must not change the
                parameters, as Twisted calls it.

        """
        
        (timestamp, package_length) = struct.unpack_from("ih", datagram, offset=0)
        (msg,) = struct.unpack_from(str(package_length-self.header_length)+"s", datagram, offset=self.header_length)
        
        question = msg.decode('ascii')
        response = self.sibylServerProxy.generateResponse(question)
        
        encoded_response = response.encode('ascii', 'replace')
        package_len = self.header_length + len(encoded_response)
        package_bin = struct.pack("ih"+str(len(encoded_response))+"s", timestamp, package_len, encoded_response)

        delta_time = int(math.log(len(question)))
        reactor.callLater(delta_time, self.transport.write, package_bin, host_port)
        #reactor.run()
        pass
    
