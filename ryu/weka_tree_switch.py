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
import sys


TCP_SYN = 0x002

TCP_ACK = 0x010


class WekaTreeSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(WekaTreeSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}



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

        #Tamanho Janela TCP
        if eth.ethertype == ether_types.ETH_TYPE_IP:
            ipv4_temp = pkt.get_protocol(ipv4.ipv4)
            tcp_temp = pkt.get_protocol(tcp.tcp)
            #Clinte-To-Server
            self.logger.debug("* Desencaplusando... ")
            self.logger.debug("(PKT):  %s ", pkt)
            self.logger.debug("(TCP):  %s ", tcp_temp)
            self.logger.debug("(IP):  %s ", ipv4_temp)
            self.logger.debug("============== /// ==============")

            if len(tcp_temp) > 0 and self.hasFlagsClientToServerTCP(tcp_temp.bits,[TCP_SYN,TCP_ACK]):
                self.logger.debug("* Info  Extracting Attributes Choosen... ")
                self.logger.debug("(TCP) porta Origem:  %s ", tcp_temp.src_port)
                self.logger.debug("(TCP) Porta Destino :  %s ", tcp_temp.dst_port)

                self.logger.debug("(TCP) Tamanho Janela :  %s ", tcp_temp.window_size)

                # Tamanho Payloada
                payload = sys.getsizeof(pkt.data)
                self.logger.debug("(PKT) Tamanho Payload Pacote :  %s ", payload)
                #comprimento Pacote Ip
                self.logger.debug("(IP) Comprimento :  %s ", ipv4_temp.total_length)
                #Comprimento comp_cabecalho TCP


                self.logger.debug("(IP) Comprimento Cabecalho :  %s ",ipv4_temp.header_length )
                self.logger.debug("============== /// ==============")
                #Classificador J48 Tree
                fluxo_classe = self.weka_decision_tree(tcp_temp.window_size, payload,ipv4_temp.total_length, ipv4_temp.header_length)
                self.logger.debug("(Class):  %s", fluxo_classe)


        dst = eth.dst
        src = eth.src

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

    #!/usr/bin/python
# -*- coding: utf-8 -*-
    def weka_decision_tree(self,TamanhoPayload, TamanhoJanela, CompPacoteIp, comp_cabecalhotcp ):
        if TamanhoPayload <= 136:
            if CompPacoteIp <= 430:
                if TamanhoPayload <= 67:
                    return 'ftp'
                elif TamanhoPayload > 67:
                    return 'p2p'
            elif CompPacoteIp > 430:
                return 'p2p'
        elif TamanhoPayload > 136:
            if TamanhoJanela <= 170584:
                if TamanhoJanela <= 39479:
                    if TamanhoPayload <= 3467:
                        if TamanhoJanela <= 23770:
                            if TamanhoJanela <= 15210:
                                return 'web'
                            elif TamanhoJanela > 15210:
                                return 'p2p'
                        elif TamanhoJanela > 23770:
                            if comp_cabecalhotcp <= 1136:
                                if comp_cabecalhotcp <= 688:
                                    return 'web'
                                elif comp_cabecalhotcp > 688:
                                    if TamanhoJanela <= 26193:
                                        return 'web'
                                    elif TamanhoJanela > 26193:
                                        if TamanhoJanela <= 36266:
                                            if TamanhoJanela <= 28778:
                                                if CompPacoteIp <= 2160:
                                                    return 'p2p'
                                                elif CompPacoteIp > 2160:
                                                    return 'web'
                                            elif TamanhoJanela > 28778:
                                                return 'p2p'
                                        elif TamanhoJanela > 36266:
                                            return 'web'
                            elif comp_cabecalhotcp > 1136:
                                if comp_cabecalhotcp <= 2310:
                                    return 'p2p'
                                elif comp_cabecalhotcp > 2310:
                                    if CompPacoteIp <= 4415:
                                        return 'ftp'
                                    elif CompPacoteIp > 4415:
                                        return 'p2p'
                    elif TamanhoPayload > 3467:
                        if comp_cabecalhotcp <= 2608:
                            return 'web'
                        elif comp_cabecalhotcp > 2608:
                            if TamanhoPayload <= 35386:
                                return 'p2p'
                            elif TamanhoPayload > 35386:
                                if TamanhoJanela <= 36418:
                                    return 'web'
                                elif TamanhoJanela > 36418:
                                    if comp_cabecalhotcp <= 5004:
                                        return 'p2p'
                                    elif comp_cabecalhotcp > 5004:
                                        if CompPacoteIp <= 171812:
                                            return 'web'
                                        elif CompPacoteIp > 171812:
                                            return 'p2p'
                elif TamanhoJanela > 39479:
                    if TamanhoPayload <= 82566:
                        if TamanhoJanela <= 47517:
                            if comp_cabecalhotcp <= 1294:
                                return 'web'
                            elif comp_cabecalhotcp > 1294:
                                if CompPacoteIp <= 3271:
                                    return 'ftp'
                                elif CompPacoteIp > 3271:
                                    if CompPacoteIp <= 17321:
                                        return 'p2p'
                                    elif CompPacoteIp > 17321:
                                        if CompPacoteIp <= 39769:
                                            return 'web'
                                        elif CompPacoteIp > 39769:
                                            return 'p2p'
                        elif TamanhoJanela > 47517:
                            if comp_cabecalhotcp <= 4668:
                                return 'web'
                            elif comp_cabecalhotcp > 4668:
                                if CompPacoteIp <= 46843:
                                    return 'p2p'
                                elif CompPacoteIp > 46843:
                                    return 'web'
                    elif TamanhoPayload > 82566:
                        if TamanhoJanela <= 108317:
                            if CompPacoteIp <= 355937:
                                return 'p2p'
                            elif CompPacoteIp > 355937:
                                return 'web'
                        elif TamanhoJanela > 108317:
                            if CompPacoteIp <= 278656:
                                return 'web'
                            elif CompPacoteIp > 278656:
                                return 'p2p'
            elif TamanhoJanela > 170584:
                if TamanhoJanela <= 12945544:
                    if CompPacoteIp <= 600:
                        return 'web'
                    elif CompPacoteIp > 600:
                        if comp_cabecalhotcp <= 568:
                            if TamanhoJanela <= 273558:
                                return 'ftp'
                            elif TamanhoJanela > 273558:
                                if TamanhoJanela <= 328217:
                                    return 'web'
                                elif TamanhoJanela > 328217:
                                    if comp_cabecalhotcp <= 474:
                                        return 'ftp'
                                    elif comp_cabecalhotcp > 474:
                                        if CompPacoteIp <= 1857:
                                            return 'p2p'
                                        elif CompPacoteIp > 1857:
                                            return 'ftp'
                        elif comp_cabecalhotcp > 568:
                            if TamanhoPayload <= 4922:
                                if TamanhoJanela <= 630655:
                                    if TamanhoPayload <= 225:
                                        return 'p2p'
                                    elif TamanhoPayload > 225:
                                        if comp_cabecalhotcp <= 1014:
                                            if TamanhoPayload <= 1115:
                                                if TamanhoJanela <= 486442:
                                                    if TamanhoJanela \
        <= 409674:
                                                        return 'web'
                                                    elif TamanhoJanela \
        > 409674:
                                                        if comp_cabecalhotcp \
        <= 738:
                                                            return 'p2p'
                                                        elif comp_cabecalhotcp \
        > 738:
                                                            return 'web'
                                                elif TamanhoJanela > 486442:
                                                    return 'p2p'
                                            elif TamanhoPayload > 1115:
                                                return 'web'
                                        elif comp_cabecalhotcp > 1014:
                                            if TamanhoPayload <= 3117:
                                                if TamanhoJanela <= 206079:
                                                    return 'p2p'
                                                elif TamanhoJanela > 206079:
                                                    if comp_cabecalhotcp \
        <= 1398:
                                                        return 'web'
                                                    elif comp_cabecalhotcp \
        > 1398:
                                                        if TamanhoJanela \
        <= 236704:
                                                            return 'web'
                                                        elif TamanhoJanela \
        > 236704:
                                                            return 'p2p'
                                            elif TamanhoPayload > 3117:
                                                return 'web'
                                elif TamanhoJanela > 630655:
                                    if TamanhoJanela <= 2691633:
                                        return 'p2p'
                                    elif TamanhoJanela > 2691633:
                                        return 'ftp'
                            elif TamanhoPayload > 4922:
                                if comp_cabecalhotcp <= 1770:
                                    if TamanhoJanela <= 236704:
                                        return 'web'
                                    elif TamanhoJanela > 236704:
                                        if TamanhoJanela <= 375881:
                                            if comp_cabecalhotcp <= 1398:
                                                return 'ftp'
                                            elif comp_cabecalhotcp > 1398:
                                                return 'web'
                                        elif TamanhoJanela > 375881:
                                            if TamanhoPayload <= 10712:
                                                if comp_cabecalhotcp <= 846:
                                                    if TamanhoJanela \
        <= 517729:
                                                        return 'web'
                                                    elif TamanhoJanela \
        > 517729:
                                                        return 'ftp'
                                                elif comp_cabecalhotcp \
        > 846:
                                                    return 'web'
                                            elif TamanhoPayload > 10712:
                                                if TamanhoJanela <= 639512:
                                                    return 'ftp'
                                                elif TamanhoJanela > 639512:
                                                    if comp_cabecalhotcp \
        <= 1444:
                                                        return 'ftp'
                                                    elif comp_cabecalhotcp \
        > 1444:
                                                        return 'web'
                                elif comp_cabecalhotcp > 1770:
                                    if TamanhoJanela <= 560387:
                                        if TamanhoPayload <= 621997:
                                            return 'web'
                                        elif TamanhoPayload > 621997:
                                            return 'p2p'
                                    elif TamanhoJanela > 560387:
                                        if comp_cabecalhotcp <= 16008:
                                            if TamanhoPayload <= 151772:
                                                if TamanhoJanela <= 3509958:
                                                    if TamanhoPayload \
        <= 21990:
                                                        if TamanhoJanela \
        <= 2037460:
                                                            return 'web'
                                                        elif TamanhoJanela \
        > 2037460:
                                                            return 'p2p'
                                                    elif TamanhoPayload \
        > 21990:
                                                        if comp_cabecalhotcp \
        <= 3592:
                                                            if TamanhoJanela \
        <= 1250272:
                                                                if TamanhoPayload \
        <= 32275:
                                                                    if TamanhoJanela \
        <= 827803:
                                                                        return 'ftp'
                                                                    elif TamanhoJanela \
        > 827803:
                                                                        return 'web'
                                                                elif TamanhoPayload \
        > 32275:
                                                                    return 'ftp'
                                                            elif TamanhoJanela \
        > 1250272:
                                                                if TamanhoJanela \
        <= 2648452:
                                                                    return 'web'
                                                                elif TamanhoJanela \
        > 2648452:
                                                                    return 'p2p'
                                                        elif comp_cabecalhotcp \
        > 3592:
                                                            if TamanhoJanela \
        <= 1457064:
                                                                if comp_cabecalhotcp \
        <= 3884:
                                                                    return 'web'
                                                                elif comp_cabecalhotcp \
        > 3884:
                                                                    if TamanhoPayload \
        <= 40301:
                                                                        return 'p2p'
                                                                    elif TamanhoPayload \
        > 40301:
                                                                        if comp_cabecalhotcp \
        <= 9520:
                                                                            return 'web'
                                                                        elif comp_cabecalhotcp \
        > 9520:
                                                                            if comp_cabecalhotcp \
        <= 11916:
                                                                                return 'p2p'
                                                                            elif comp_cabecalhotcp \
        > 11916:
                                                                                return 'web'
                                                            elif TamanhoJanela \
        > 1457064:
                                                                if CompPacoteIp \
        <= 63801:
                                                                    return 'web'
                                                                elif CompPacoteIp \
        > 63801:
                                                                    return 'ftp'
                                                elif TamanhoJanela \
        > 3509958:
                                                    if CompPacoteIp \
        <= 69032:
                                                        return 'p2p'
                                                    elif CompPacoteIp \
        > 69032:
                                                        if TamanhoJanela \
        <= 7299764:
                                                            return 'web'
                                                        elif TamanhoJanela \
        > 7299764:
                                                            return 'p2p'
                                            elif TamanhoPayload > 151772:
                                                if TamanhoJanela <= 1773867:
                                                    return 'web'
                                                elif TamanhoJanela \
        > 1773867:
                                                    if comp_cabecalhotcp \
        <= 11830:
                                                        return 'ftp'
                                                    elif comp_cabecalhotcp \
        > 11830:
                                                        if TamanhoPayload \
        <= 215927:
                                                            return 'web'
                                                        elif TamanhoPayload \
        > 215927:
                                                            return 'ftp'
                                        elif comp_cabecalhotcp > 16008:
                                            if TamanhoJanela <= 11615977:
                                                if TamanhoJanela <= 1549788:
                                                    return 'p2p'
                                                elif TamanhoJanela \
        > 1549788:
                                                    if CompPacoteIp \
        <= 3678517:
                                                        return 'web'
                                                    elif CompPacoteIp \
        > 3678517:
                                                        return 'p2p'
                                            elif TamanhoJanela > 11615977:
                                                return 'ftp'
                elif TamanhoJanela > 12945544:
                    if TamanhoPayload <= 1179951:
                        if CompPacoteIp <= 1094127:
                            if TamanhoJanela <= 22425083:
                                if TamanhoJanela <= 19075583:
                                    return 'p2p'
                                elif TamanhoJanela > 19075583:
                                    return 'web'
                            elif TamanhoJanela > 22425083:
                                return 'p2p'
                        elif CompPacoteIp > 1094127:
                            return 'ftp'
                    elif TamanhoPayload > 1179951:
                        return 'ftp'
