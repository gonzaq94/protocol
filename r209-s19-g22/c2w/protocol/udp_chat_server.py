# -*- coding: utf-8 -*-
from twisted.internet.protocol import DatagramProtocol
from c2w.main.lossy_transport import LossyTransport
import logging
import struct

logging.basicConfig()
moduleLogger = logging.getLogger('c2w.protocol.udp_chat_server_protocol')


class c2wUdpChatServerProtocol(DatagramProtocol):

    def __init__(self, serverProxy, lossPr):
        """
        :param serverProxy: The serverProxy, which the protocol must use
            to interact with the user and movie store (i.e., the list of users
            and movies) in the server.
        :param lossPr: The packet loss probability for outgoing packets.  Do
            not modify this value!

        Class implementing the UDP version of the client protocol.

        .. note::
            You must write the implementation of this class.

        Each instance must have at least the following attribute:

        .. attribute:: serverProxy

            The serverProxy, which the protocol must use
            to interact with the user and movie store in the server.

        .. attribute:: lossPr

            The packet loss probability for outgoing packets.  Do
            not modify this value!  (It is used by startProtocol.)

        .. note::
            You must add attributes and methods to this class in order
            to have a working and complete implementation of the c2w
            protocol.
        """
        #: The serverProxy, which the protocol must use
        #: to interact with the server (to access the movie list and to 
        #: access and modify the user list).
        self.serverProxy = serverProxy
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

    def f_0(self):
        pass

    def connection(self):
        user_name = self.msg.decode('ascii')
        print(user_name)
        packet_length = self.HEADER_LENGTH
        packet_type = 0
        if not self.serverProxy.userExists(user_name):
            print(user_name+" joined the MAIN_ROOM")
            self.serverProxy.addUser(user_name, "MAIN_ROOM")        
            packet_type = 7
        else:
            print(user_name+" could not join the MAIN_ROOM")
            packet_type = 8
            
        seq_num_and_packet_type = self.seq_num * 16 + packet_type
        packet_bin = struct.pack("hh", packet_length, seq_num_and_packet_type)
        self.transport.write(packet_bin, self.host_port)
        pass        

    def f_2(self):
        pass

    def f_3(self):
        pass

    def f_4(self):
        pass

    def f_5(self):
        pass

    def f_6(self):
        pass

    def f_7(self):
        pass

    def f_8(self):
        pass

    def f_9(self):
        pass

    def send_ack(self, seq_num, host_port):
        # encoded_response = response.encode('ascii', 'replace')
        # package_len = self.header_length + len(encoded_response)
        # package_bin = struct.pack("ih"+str(len(encoded_response))+"s", timestamp, package_len, encoded_response)        
 
        # self.transport.write(package_bin, host_port)
        packet_length = self.HEADER_LENGTH
        seq_num_and_packet_type = seq_num * 16
        packet_bin = struct.pack("hh", packet_length, seq_num_and_packet_type)
        print(packet_bin)
        self.transport.write(packet_bin, host_port)
        pass

    def datagramReceived(self, datagram, host_port):
        """
        :param string datagram: the payload of the UDP packet.
        :param host_port: a touple containing the source IP address and port.
        
        Twisted calls this method when the server has received a UDP
        packet.  You cannot change the signature of this method.
        """
        self.host_port = host_port
        (self.packet_length, seq_num_and_type) = struct.unpack_from("hh", datagram, offset=0)
        self.packet_type = seq_num_and_type % 16 #We take the last 4 bits
        self.seq_num = int(seq_num_and_type / 16) #We cut the last 4 bits 
        
        (self.msg,) = struct.unpack_from(str(self.packet_length-self.HEADER_LENGTH)+"s", datagram, offset=self.HEADER_LENGTH)

        self.send_ack(self.seq_num, self.host_port)

        types_selector = {
            0 : self.f_0,
            1 : self.connection,
            2 : self.f_2,
            3 : self.f_3,
            4 : self.f_4,
            5 : self.f_5,
            6 : self.f_6,
            7 : self.f_7,
            8 : self.f_8,
            9 : self.f_9
        }

        selector = types_selector.get(self.packet_type, lambda: "Invalid type")
        selector()

        pass
