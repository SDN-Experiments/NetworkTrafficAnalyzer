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
#from ryu.custom.host2host import host2host
import sys

import math


TCP_SYN = 0x002

TCP_ACK = 0x010
TCP_CODE = 6
UDP_CODE = 17
BROADCAST_STR = 'ff:ff:ff:ff:ff:ff:ff'
MULTICAST_IP_1 = '224.0.0.22'
MULTICAST_IP_2 = '224.0.0.251'
BROADCAST_IP = '255.255.255.255'



class WekaTreeSwitch1_5(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(WekaTreeSwitch1_5, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.host2host_instance = {}
	self.label_flow={'web':0,'dns':0,'ftp':0,'p2p':0, 'ssl' : 0}

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
            priority=priority, match=match,instructions=inst)
                                # instructions=inst, table_id=1 )
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
            match=match, instructions=inst)
                                    # match=match, instructions=inst,table_id=1 )
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

        fluxo_classe_temp = None
        #Tamanho Janela TCP
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ipv4_temp = pkt.get_protocol(ipv4.ipv4)
            tcp_temp = pkt.get_protocol(tcp.tcp)

            udp_temp = pkt.get_protocol(udp.udp)
            #Clinte-To-Server
            self.logger.debug("*** Desencaplusando... ")
            #self.logger.debug("(PKT):  %s ", pkt)
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

            fluxo_classe_temp = None
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ipv4_temp = pkt.get_protocol(ipv4.ipv4)
            tcp_temp = pkt.get_protocol(tcp.tcp)

            udp_temp = pkt.get_protocol(udp.udp)
            #Clinte-To-Server
            self.logger.debug("------------------------------------------------------------")
	    self.logger.debug("---------------------- *** Packet Attributes *** ----------------------")
            #self.logger.debug("(PKT):  %s ", pkt)
            # Tamanho Payloada
            payload = sys.getsizeof(pkt.data)
	    #self.logger.debug("(IP):  %s ", ipv4_temp)
            self.logger.debug("(PKT) Packet Size :  %s ", payload)
            self.logger.debug("(IP) Code Protocol:   %s ", ipv4_temp.proto)
            #comprimento Pacote Ip
            self.logger.debug("(IP) Comprimento :  %s ", ipv4_temp.total_length)
	    header_length_bytes = (ipv4_temp.header_length * 32)/8
            #Comprimento comp_cabecalho TCP
            self.logger.debug("(IP) Comprimento Cabecalho :  %s ",header_length_bytes )

                    
	    if ipv4_temp.dst != MULTICAST_IP_1 and ipv4_temp.dst != MULTICAST_IP_2 and ipv4_temp.dst != BROADCAST_IP:
	        temp_port_src = None    
	        temp_port_dst = None
   	        
	        if tcp_temp != None and ipv4_temp.proto == 6:
		    
		    temp_port_src = tcp_temp.src_port
		    temp_port_dst = tcp_temp.dst_port		
	
	    	elif udp_temp != None and ipv4_temp.proto == UDP_CODE:

		    
		    temp_port_src = udp_temp.src_port
		    temp_port_dst = udp_temp.dst_port
	    		    

	        self.logger.debug("Porta Origem:  %s ", temp_port_src)
	        self.logger.debug("Porta Destino :  %s ", temp_port_dst)

                h2h = host2host(temp_port_src, temp_port_dst,ipv4_temp.total_length,header_length_bytes,ipv4_temp.proto)
	        fluxo_classe = self.weka_decision_tree(h2h.median_packet_size, h2h.std_dev_packet_size, h2h.var_packet_size, h2h.bigger_packet_size, h2h.smaller_packet_size,h2h.length_header_average, h2h.protocol_code, h2h.src_port, h2h.dst_port)

	        self.logger.debug("------------------------------------------------------------")
	        self.logger.debug("----------------------- *** Definition Class *** ----------------------")
	        self.logger.debug("(Class)=  %s", fluxo_classe)
	        self.logger.debug("------------------------------------------------------------")	    	
	    	self.logger.debug("----------------------- *** Aggreation Class *** ----------------------")
		self.label_flow[fluxo_classe] =  self.label_flow[fluxo_classe] + 1
		for flow in self.label_flow:
		      print flow + " = " +  str(self.label_flow[flow])
		    

	
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        #actions = [parser.OFPActionOutput(out_port)]


        # install a flow to avoid packet_in next time
        """if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)"""
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
        #match =None
        actions = [parser.OFPActionOutput(out_port)]

        



        if out_port != ofproto.OFPP_FLOOD:
            #print fluxo_classe
            #self.logger.debug("***Selecting QoS..")
            # match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            match = None
            # if fluxo_classe_temp == "web" and ipv4_temp.proto == TCP_CODE:
            #     match = parser.OFPMatch(in_port=in_port, eth_dst=dst, ip_proto= ipv4_temp.proto, tcp_dst =  tcp_temp.dst_port )
            #     #actions= parser.OFPActionSetQueue(queue_id=1)
            # elif  fluxo_classe_temp == "dns" and ipv4_temp.proto == UDP_CODE:
            #     match = parser.OFPMatch(in_port=in_port, eth_dst=dst,ip_proto= ipv4_temp.proto, tcp_dst =  udp_temp.dst_port  )


            if match == None:
                match = parser.OFPMatch(in_port=in_port, eth_dst=dst)    # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            #self.logger.debug("(Match):  %s", match)

            if msg.buffer_id != ofproto.OFP_NO_BUFFER:#fi there is buffer

                self.add_flow(datapath, 1, match, actions, msg.buffer_id)

                return
            else:
                self.add_flow(datapath, 1, match, actions)


        data = None

        #self.logger.debug("(Match):  %s", match)
        #self.logger.debug("(Action):  %s", actions)


        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    def weka_decision_tree(self, tamtotal_med_pacote, desv_padrao_tamtotal, variancia_tamtotal, tamtotal_pacote_maior, tamtotal_pacote_menor, com_med_cabecalhoIP, codigo_protocolo, srcporta, dstporta):
        if codigo_protocolo <= 6:
            if dstporta <= 80:
                if com_med_cabecalhoIP <= 54.53933:
                    if dstporta <= 21: return 'ftp' 
                    elif dstporta > 21: return 'web' 
                elif com_med_cabecalhoIP > 54.53933:
                    if tamtotal_pacote_maior <= 181:
                        if tamtotal_pacote_maior <= 130: return 'ftp' 
                        elif tamtotal_pacote_maior > 130: return 'web' 
                    elif tamtotal_pacote_maior > 181: return 'web' 
            elif dstporta > 80:
                if srcporta <= 4410:
                    if srcporta <= 80:
                        if tamtotal_med_pacote <= 82.5:
                            if srcporta <= 21: return 'ftp' 
                            elif srcporta > 21: return 'web' 
                        elif tamtotal_med_pacote > 82.5: return 'web' 
                    elif srcporta > 80:
                        if com_med_cabecalhoIP <= 55.125:
                            if dstporta <= 57704: return 'ssl' 
                            elif dstporta > 57704: return 'web' 
                        elif com_med_cabecalhoIP > 55.125: return 'ssl' 
                elif srcporta > 4410:
                    if dstporta <= 443: return 'ssl' 
                    elif dstporta > 443:
                        if tamtotal_pacote_maior <= 1492:
                            if tamtotal_pacote_maior <= 201:
                                if desv_padrao_tamtotal <= 17.6225:
                                    if tamtotal_pacote_maior <= 88: return 'ftp' 
                                    elif tamtotal_pacote_maior > 88: return 'p2p' 
                                elif desv_padrao_tamtotal > 17.6225: return 'p2p' 
                            elif tamtotal_pacote_maior > 201:
                                if tamtotal_pacote_maior <= 253: return 'ftp' 
                                elif tamtotal_pacote_maior > 253:
                                    if com_med_cabecalhoIP <= 56.95652: return 'p2p' 
                                    elif com_med_cabecalhoIP > 56.95652:
                                        if com_med_cabecalhoIP <= 57:
                                            if srcporta <= 50956: return 'ftp' 
                                            elif srcporta > 50956: return 'p2p' 
                                        elif com_med_cabecalhoIP > 57:
                                            if tamtotal_pacote_maior <= 458: return 'ftp' 
                                            elif tamtotal_pacote_maior > 458: return 'p2p' 
                        elif tamtotal_pacote_maior > 1492:
                            if srcporta <= 46800:
                                if desv_padrao_tamtotal <= 723.68256: return 'p2p' 
                                elif desv_padrao_tamtotal > 723.68256: return 'ftp' 
                            elif srcporta > 46800:
                                if tamtotal_med_pacote <= 904.12108:
                                    if desv_padrao_tamtotal <= 717.06683:
                                        if com_med_cabecalhoIP <= 54.90909: return 'p2p' 
                                        elif com_med_cabecalhoIP > 54.90909:
                                            if tamtotal_med_pacote <= 727.05882: return 'ftp' 
                                            elif tamtotal_med_pacote > 727.05882: return 'p2p' 
                                    elif desv_padrao_tamtotal > 717.06683: return 'ftp' 
                                elif tamtotal_med_pacote > 904.12108: return 'ftp' 
        elif codigo_protocolo > 6: return 'dns' 

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
            self.logger.debug("(history_packet_size ) : %s",self.host2host_instance[key].values_size_packet )
            self.logger.debug("============== /// ==============")

"""@set_ev_cls(ofp_event.EventOFPQueueStatsReply, MAIN_DISPATCHER)
def queue_stats_reply_handler(self, ev):
    queues = []
    for stat in ev.msg.body:
        queues.append('port_no=%d queue_id=%d '
                      'tx_bytes=%d tx_packets=%d tx_errors=%d '
                      'duration_sec=%d duration_nsec=%d' %
                      (stat.port_no, stat.queue_id,
                       stat.tx_bytes, stat.tx_packets, stat.tx_errors,
                       stat.duration_sec, stat.duration_nsec))
    self.logger.debug('QueueStats: %s', queues)"""


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
        
        self.protocol_code = protocol_code
	self.qt_packets += 1
        self.values_size_packet.append(self.size_packet)
        self.sum_size_packet += self.size_packet
	self.sum_length_header+= length_header_IP
        self.checkGreaterBytesPacket(self.size_packet)
        self.checkSmallerBytesPacket(self.size_packet)
        self.computeAverage()
        self.computeVariance()
        self.computeStandardDeviation()
	self.computeAverageHeaderLength()
#        self.updateStateHostToHost()

    def updateStateHostToHost(self):
        self.qt_packets += 1
        self.values_size_packet.append(self.size_packet)
        self.sum_size_packet += self.size_packet
        self.checkGreaterBytesPacket(self.size_packet)
        self.checkSmallerBytesPacket(self.size_packet)
        self.computeAverage()
        self.computeVariance()
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
        self.computeStandardDeviation()

    def checkSmallerBytesPacket(self, bytesPacket):
        if bytesPacket < self.smaller_packet_size:
            self.smaller_packet_size = bytesPacket

    def checkGreaterBytesPacket(self, bytesPacket):
        if bytesPacket > self.bigger_packet_size:
            self.bigger_packet_size = bytesPacket


    def computeAverageHeaderLength(self):
	self.length_header_average = self.sum_length_header / self.qt_packets
	

    def computeAverage(self):
        self.median_packet_size = self.sum_size_packet / self.qt_packets

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
            self.updateStateHostToHostByPacket(o.size_packet)
            return True
        return False
