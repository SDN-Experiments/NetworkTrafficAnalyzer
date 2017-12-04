# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import ipv4
from ryu.lib.packet import tcp
from ryu.lib.packet import udp
from ryu.lib import pcaplib
#from ryu.custom.host2host import host2host
import sys

import math
import sys

TCP_SYN = 0x002

TCP_ACK = 0x010
TCP_CODE = 6
UDP_CODE = 17


class WekaTreeSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(WekaTreeSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.host2host_instance = {}
        #self.pcap_writer = pcaplib.Writer(open('my_pcap.pcap', 'wb'))



    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)


    def hasFlagsClientToServerTCP(self, bits, flags ):
        bits  = self.doOrBits(bits)
        mask = sum(flags)
        return (bits & mask) == mask

    def doOrBits(self, bits):
        if bits == 0x002 or bits == 0x010:
            if bits == 0x002:
                self.logger.debug("(TCP): SYN Flag")
                return bits | 0x010
            if bits == 0x010:
                self.logger.debug("(TCP): ACK Flag")
                return bits | 0x002





    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):

        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)

        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)

        eth = pkt.get_protocols(ethernet.ethernet)[0]

        dst = eth.dst
        src = eth.src
        #self.pcap_writer.write_pkt(ev.msg.data)
        #Tamanho Janela TCP
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ipv4_temp = pkt.get_protocol(ipv4.ipv4)
            tcp_temp = pkt.get_protocol(tcp.tcp)

            udp_temp = pkt.get_protocol(udp.udp)
            #Clinte-To-Server
            self.logger.debug("*** Desencaplusando... ")
            # Tamanho Payloada
            payload = sys.getsizeof(pkt.data)
            self.logger.debug("(PKT) Tamanho Payload Pacote :  %s ", payload)
            self.logger.debug("(IP):  %s ", ipv4_temp)
            self.logger.debug("(IP) Code Protocol:   %s ", ipv4_temp.proto)
            #comprimento Pacote Ip
            self.logger.debug("(IP) Comprimento :  %s ", ipv4_temp.total_length)
            #Comprimento comp_cabecalho TCP
            self.logger.debug("(IP) Comprimento Cabecalho :  %s ",ipv4_temp.header_length )
            self.logger.debug("============== /// ==============")
            self.logger.debug("(TCP):  %s ", tcp_temp)
            self.logger.debug("(UDP):  %s ", udp_temp)

            header_length_bytes = (ipv4_temp.header_length * 32)/8

            #Web
            if tcp_temp != None and self.hasFlagsClientToServerTCP(tcp_temp.bits,[TCP_SYN,TCP_ACK]) and ipv4_temp.proto == 6:
                self.logger.debug("*** Info  Extracting Attributes Choosen... ")
                self.logger.debug("(TCP) porta Origem:  %s ", tcp_temp.src_port)
                self.logger.debug("(TCP) Porta Destino :  %s ", tcp_temp.dst_port)

                self.logger.debug("(TCP) Tamanho Janela :  %s ", tcp_temp.window_size)



                #dpid = datapath.id
                #self.host2host_instance.setdefault(dpid, {})

                h2h = None
                key = src + dst
                if len(self.host2host_instance) > 0:
                    if  key in self.host2host_instance:
                        h2h = self.host2host_instance[key]
                        h2h.updateStateHostToHostByPacket(ipv4_temp.total_length,header_length_bytes)
                    else:
                        #self.host2host_instance.setdefault(src + dst, {})
                        h2h = host2host(tcp_temp.src_port, tcp_temp.dst_port,ipv4_temp.total_length,header_length_bytes,6 )
                        self.host2host_instance[key] = h2h
                else:
                    #self.host2host_instance.setdefault(src + dst, {})
                    h2h = host2host(tcp_temp.src_port, tcp_temp.dst_port,ipv4_temp.total_length,header_length_bytes,6 )
                    self.host2host_instance[key] = h2h


                self.printInstanceH2H()

                #Classificador J48 Tree
                #host2host = host2host(tcp_temp.src_port, tcp_temp.dst_port,payload,ipv4_temp.total_length,6 )
                #srcporta,dstporta, tamtotal_pacote_menor,tamtotal_pacote_maior,codigo_protocolo
                fluxo_classe = self.weka_decision_tree(h2h.src_port,
                h2h.dst_port,
                h2h.smaller_packet_size,
                h2h.bigger_packet_size,
                h2h.protocol_code
                )

                self.logger.debug("(Class):  %s", fluxo_classe)

            if udp_temp != None and ipv4_temp.proto == UDP_CODE:
                self.logger.debug("*** Info  Extracting Attributes (UDP) Choosen... ")
                self.logger.debug("(UDP) porta Origem:  %s ", udp_temp.src_port)
                self.logger.debug("(UDP) Porta Destino :  %s ", udp_temp.dst_port)

                self.logger.debug("============== /// ==============")

                #dpid = datapath.id
                #self.host2host_instance.setdefault(dpid, {})

                h2h = None
                key = src + dst
                if len(self.host2host_instance) > 0:
                    if  key in self.host2host_instance:
                        h2h = self.host2host_instance[key]
                        h2h.updateStateHostToHostByPacket(ipv4_temp.total_length,header_length_bytes)
                    else:
                        #self.host2host_instance.setdefault(src + dst, {})
                        h2h = host2host(udp_temp.src_port, udp_temp.dst_port,ipv4_temp.total_length,header_length_bytes,UDP_CODE )
                        self.host2host_instance[key] = h2h
                else:
                    #self.host2host_instance.setdefault(src + dst, {})
                    h2h = host2host(udp_temp.src_port, udp_temp.dst_port,ipv4_temp.total_length,header_length_bytes,UDP_CODE )
                    self.host2host_instance[key] = h2h


                self.printInstanceH2H()

                #Classificador J48 Tree
                #host2host = host2host(tcp_temp.src_port, tcp_temp.dst_port,payload,ipv4_temp.total_length,6 )
                #srcporta,dstporta, tamtotal_pacote_menor,tamtotal_pacote_maior,codigo_protocolo
                fluxo_classe = self.weka_decision_tree(h2h.src_port,
                h2h.dst_port,
                h2h.smaller_packet_size,
                h2h.bigger_packet_size,
                h2h.protocol_code
                )

                self.logger.debug("(Class):  %s", fluxo_classe)



        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def weka_decision_tree(self, srcporta,dstporta, tamtotal_pacote_menor,tamtotal_pacote_maior,codigo_protocolo):
        if codigo_protocolo <= 6:
            if tamtotal_pacote_menor <= 54:
                return 'ftp'
            elif tamtotal_pacote_menor > 54:
                if dstporta <= 80:
                    return 'web'
                elif dstporta > 80:
                    if srcporta <= 2632:
                        return 'web'
                    elif srcporta > 2632:
                        if tamtotal_pacote_menor <= 60:
                            if dstporta <= 7957:
                                if dstporta <= 443:
                                    return 'web'
                                elif dstporta > 443:
                                    return 'p2p'
                            elif dstporta > 7957:
                                return 'p2p'
                        elif tamtotal_pacote_menor > 60:
                            if tamtotal_pacote_maior <= 81:
                                return 'ftp'
                            elif tamtotal_pacote_maior > 81:
                                return 'p2p'
        elif codigo_protocolo > 6:
            return 'dns'


    def printInstanceH2H(self):
        for key in self.host2host_instance:
            self.logger.debug("*** Info  Accumalate h2h : (%s) ", key)
            self.logger.debug("(src_port) : %s",self.host2host_instance[key].src_port )
            self.logger.debug("(dst_port) : %s",self.host2host_instance[key].dst_port )
            self.logger.debug("(smaller packet) : %s",self.host2host_instance[key].smaller_packet_size )
            self.logger.debug("(bigger packet) : %s",self.host2host_instance[key].bigger_packet_size )
            self.logger.debug("(qt_packets ) : %s",self.host2host_instance[key].qt_packets )
            self.logger.debug("(sum_size_packet) : %s",self.host2host_instance[key].sum_size_packet )
            self.logger.debug("(median_packet_size ) : %s",self.host2host_instance[key].median_packet_size )
            self.logger.debug("(var_packet_size) : %s",self.host2host_instance[key].var_packet_size )
            self.logger.debug("(std_dev_packet_size ) : %s",self.host2host_instance[key].std_dev_packet_size )
            self.logger.debug("(std_dev_packet_size ) : %s",self.host2host_instance[key].values_size_packet )
            self.logger.debug("============== /// ==============")




class host2host(object):

    src_port = 0
    dst_port = 0

    bigger_packet_size = -sys.maxsize
    smaller_packet_size = sys.maxsize

    median_packet_size = 0
    std_dev_packet_size = 0
    var_packet_size = 0.0

    sum_length_header = 0
    length_header_average = 0.0

    sum_size_packet = 0
    qt_packets = 0
    values_size_packet = []

    length_header_IP = 0
    protocol_code = 0


    def __init__(
        self,
        src_port,
        dst_port,
        size_packet,
        length_header_IP,
        protocol_code,
        ):
        self.src_port = src_port
        self.dst_port = dst_port
        self.size_packet = size_packet
        self.length_header_IP = length_header_IP
        self.protocol_code = protocol_code
        self.updateStateHostToHost()

    def updateStateHostToHost(self):
        self.qt_packets += 1
        self.values_size_packet.append(self.size_packet)
        self.sum_size_packet += self.size_packet
        self.sum_length_header += self.length_header_IP
        self.checkGreaterBytesPacket(self.size_packet)
        self.checkSmallerBytesPacket(self.size_packet)
        self.computeAverage()
        self.computeVariance()
        self.computeAverageHeaderLength()
        self.computeStandardDeviation()


    def updateStateHostToHostByPacket(self, size_packet,length_header_IP):
        self.qt_packets += 1
        self.values_size_packet.append(size_packet)
        self.sum_size_packet += size_packet
        self.sum_length_header += length_header_IP
        self.checkGreaterBytesPacket(size_packet)
        self.checkSmallerBytesPacket(size_packet)
        self.computeAverage()
        self.computeVariance()
        self.computeAverageHeaderLength()
        self.computeStandardDeviation()

    def checkSmallerBytesPacket(self, bytesPacket):
        if bytesPacket < self.smaller_packet_size:
            self.smaller_packet_size = bytesPacket

    def checkGreaterBytesPacket(self, bytesPacket):
        if bytesPacket > self.bigger_packet_size:
            self.bigger_packet_size = bytesPacket

    def computeAverage(self):
        self.median_packet_size = self.sum_size_packet / self.qt_packets

    def computeAverageHeaderLength(self):
        self.length_header_average = self.sum_length_header / self.qt_packets

    def computeStandardDeviation(self):
        self.std_dev_packet_size = math.sqrt(self.var_packet_size)

    def computeVariance(self):
        sum_variance = 0.0
        for value_size_packet in self.values_size_packet:
            sum_variance += math.pow(value_size_packet
                    - self.median_packet_size, 2)

        self.var_packet_size = sum_variance / self.qt_packets

    def equals(self, o):
        if self.src_port == o.src_port and self.src_port == o.dst_port:
            self.updateStateHostToHostByPacket(o.size_packet,o.length_header_IP)
            return True
        return False
