#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import sys


class host2host(Object):

    bigger_packet_size = -sys.maxsize
    smaller_packet_size = sys.maxsize

    median_packet_size = 0
    std_dev_packet_size = 0
    var_packet_size = 0

    sum_size_packet = 0
    qt_packets = 0
    values_size_packet = []

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
		updateStateHostToHost(self):

    def updateStateHostToHost(self):
        self.qt_packets += 1
        self.values_size_packet.add(self.size_packet)
        self.sum_size_packet += self.size_packet
        self.checkGreaterBytesPacket(self.size_packet)
        self.checkSmallerBytesPacket(self.size_packet)
        self.computeAverage()
        self.computeStandardDeviation()
        self.computeVariance()

    def checkSmallerBytesPacket(self, bytesPacket):
        if bytesPacket < self.smaller_packet_size:
            self.smaller_packet_size = bytesPacket

    def checkGreaterBytesPacket(self, bytesPacket):
        if bytesPacket > self.bigger_packet_size:
            self.bigger_packet_size = bytesPacket

    def computeAverage(self):
        self.median_packet_size = self.sum_size_packet / self.qt_packets

    def computeStandardDeviation(self):
        self.std_dev_packet_size = math.sqrt(self.median_packet_size)

    def computeVariance(self):
        sum_variance = 0
        for value_size_packet in self.values_size_packet:
            sum_variance += math.pow(value_size_packet
                    - self.median_packet_size, 2)

        self.var_packet_size = sum_variance / self.qt_packets

    def equals(self, o):
        if self.src_port == o.src_port and self.srt_port == o.dst_port:
            return True
        return False
