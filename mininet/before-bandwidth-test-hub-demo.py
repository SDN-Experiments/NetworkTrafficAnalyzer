#!/usr/bin/python
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import quietRun
from mininet.log import setLogLevel, info
from mininet.term import makeTerms
import mininet.util as util
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch

#from mininet.examples.nat import connectToInternet, stopNAT

from sys import exit, stdin, argv
from re import findall
from time import sleep
import os
import threading
import time
from random import randint
	
class BeforeBandwidthTestHubDemo( Topo ):
    """Topology for Web Demo:
       client - switch - link - Web server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        switches = [];
	for s in range(2):
	     s = self.addSwitch( 's%s' % (s + 1), protocols=["OpenFlow13"] )
	     switches.append(s)


        #Server
        h4 = self.addHost( 'h4', ip="10.0.0.4")

	for h in range(3):
	    if h+1 != 4:
            	host = self.addHost('h%s' % (h + 1))
	        self.addLink(host ,switches[0])
        
	self.addLink( h4, switches[-1] )
	for i in range(1):
		self.addLink( switches[i], switches[-1])


def demo( ):
    "Rogue Webdd server demonstration"
    #checkRequired()
    topo = BeforeBandwidthTestHubDemo()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)
    
    
    popens = {}
    server = net.get('h4')
     
    net.start()
    # (Bandidth before Apply Traffic Priorization)
    popens[server] = server.popen('iperf -s -p 5002 &')
    for client in net.hosts:

	if client.name != server.name: 
		print client.name
		popens[client] = client.popen('iperf -c ' +  server.IP() + ' -p 5002')
    
    try:
        for host, line in util.pmonitor(popens):
            if host:
                print(host.name, line)
	
    finally:
        # Don't leave things running if this script crashes.
        for process in popens.values():
            if not process.poll():
                process.kill()
    

    net.stop()

def usage():
    "Print usage message"
    print "%s [ -h | -text ]"
    print "-h: print this message"

if __name__ == '__main__':
    setLogLevel( 'info' )
    if '-h' in argv:
        usage()
        exit( 1 )
    #firefox = '-t' not in argv
    demo()
