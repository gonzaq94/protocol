# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
import struct

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_client_protocol')


class c2wUdpChatClientProtocol(DatagramProtocol):

    def __init__(self, serverAddress, serverPort, clientProxy, lossPr):
        """
        :param serverAddress: The IP address (or the name) of the c2w server,
            given by the user.
        :param serverPort: The port number used by the c2w server,
            given by the user.
        :param clientProxy: The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attributes:

        .. attribute:: serverAddress

            The IP address of the c2w server.

        .. attribute:: serverPort

            The port number of the c2w server.

        .. attribute:: clientProxy

            The clientProxy, which the protocol must use
            to interact with the Graphical User Interface.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """

        #: The IP address of the c2w server.
        self.serverAddress = serverAddress
        #: The port number of the c2w server.
        self.serverPort = serverPort
        #: The clientProxy, which the protocol must use
        #: to interact with the Graphical User Interface.
        self.clientProxy = clientProxy
        self.lossPr = lossPr
        self.HEADER_LENGTH = 4

    def startProtocol(self):
        """
        DO NOT MODIFY THE FIRST TWO LINES OF THIS METHOD!!

        If in doubt, do not add anything to this method.  Just ignore it.
        It is used to randomly drop outgoing packets if the -l
        command line option is used.
        """
        self.transport = LossyTransport(self.transport, self.lossPr)
        DatagramProtocol.transport = self.transport

    def sendLoginRequestOIE(self, userName):
        """
        :param string userName: The user name that the user has typed.

        The client proxy calls this function when the user clicks on
        the login button.
        """
        packet_length = self.HEADER_LENGTH + len(userName)
        seq_num = 0 #always begins connection with a 0
        packet_type = 1
        seq_num_and_packet_type = seq_num + packet_type
        encoded_userName = userName.encode('ascii', 'replace')
        packet_bin = struct.pack("hh"+str(len(userName))+"s", packet_length, seq_num_and_packet_type, encoded_userName)
        self.transport.write(packet_bin, (self.serverAddress, self.serverPort))        
        moduleLogger.debug('loginRequest called with username=%s', userName)

    def sendChatMessageOIE(self, message):
        """
        :param message: The text of the chat message.
        :type message: string

        Called by the client proxy  when the user has decided to send
        a chat message

        .. note::
           This is the only function handling chat messages, irrespective
           of the room where the user is.  Therefore it is up to the
           c2wChatClientProctocol or to the server to make sure that this
           message is handled properly, i.e., it is shown only by the
           client(s) who are in the same room.
        """
        pass

    def sendJoinRoomRequestOIE(self, roomName):
        """
        :param roomName: The room name (or movie title.)

        Called by the client proxy  when the user
        has clicked on the watch button or the leave button,
        indicating that she/he wants to change room.

        .. warning:
            The controller sets roomName to
            c2w.main.constants.ROOM_IDS.MAIN_ROOM when the user
            wants to go back to the main room.
        """
        pass

    def sendLeaveSystemRequestOIE(self):
        """
        Called by the client proxy  when the user
        has clicked on the leave button in the main room.
        """
        pass

    def datagramReceived(self, datagram, host_port):
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.

        Called **by Twisted** when the client has received a UDP
        packet.
        """
        (packet_length, seq_num_and_type) = struct.unpack_from("hh", datagram, offset=0)
        packet_type = seq_num_and_type % 16 #We take the last 4 bits
        seq_num = int(seq_num_and_type / 16) #We cut the last 4 bits 
        
        print(packet_length)
        print(packet_type)
        print(seq_num)



        # (self.msg,) = struct.unpack_from(str(self.packet_length-self.HEADER_LENGTH)+"s", datagram, offset=self.HEADER_LENGTH)

        # (timestamp, package_length) = struct.unpack_from("hh", datagram, offset=0)
        # (msg,) = struct.unpack_from(str(package_length-self.header_length)+"s", datagram, offset=self.header_length)
        # response = msg.decode('ascii')
        # self.clientProxy.responseReceived(response)

        pass
