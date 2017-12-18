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
	
class AfterBandwidthTestHubDemo( Topo ):
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
    topo = AfterBandwidthTestHubDemo()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)
    
    
    popens = {}
    server = net.get('h4')
    #c = net.get('c0')
    net.start()

    # (Banwidth Test After Apply Traffic Priorization Correlationed witn Classification by Application Class(HTTP, DNS, FTP)) on Controller RYU
    
    #net.get('s1').cmd('cd qos-command &')
    #net.get('s1').cmd('sudo ./ovs-qos-run s1-eth4' )
    # (Executing OVSDB Queue on Switches)   
    #switches =  net.switches
    for switch in net.switches:
	if net.switches[-1].name  != switch.name :
		print switch.intfList()[-1]
		#popens[switch] = switch.popen('cd qos-command &')
                #popens[switch] = switch.popen('sudo ./ovs-qos-run ' + str(switch.intfList()[-1]) + ' &' )
		popens[switch] = switch.popen( 'ovs-vsctl set port ' + str(switch.intfList()[-1]) + ' qos=@newqos -- --id=@newqos create QoS type=linux-htb other-config:max-rate=7000000 queues=0=@q0,1=@q1,2=@q2,3=@q3 -- --id=@q0 create Queue other-config:max-rate=1000000 -- --id=@q1 create Queue other-config:min-rate=1000000 other-config:max-rate=2000000 -- --id=@q2 create Queue other-config:min-rate=3000000 other-config:max-rate=4000000 -- --id=@q3 create Queue other-config:min-rate=5000000 other-config:max-rate=6000000' )
		
		
      

 
    # (Starting up HTTP Server)
    webdir = '/tmp/webserver'
    popens[server] = server.popen( "cd ", webdir, " &"  )
    popens[server] = server.popen("python -u-m SimpleHTTPServer 80 >& /tmp/http.log &")
    sleep(1)
    
    # (Starting up DNS Server)
    popens[server] = server.popen('dnsmasq -k -A /#/%s 1>/tmp/dns.log 2>&1 &' %  server.IP())
    sleep(1)
    
    # (Starting up FTP Server)
    """popens[server] = server.popen("inetd")
    #sleep(1)"""

    # (Generate Flow by Class(HTTP, DNS, FTP)
    for client in net.hosts:	
	if client.name == "h1":
		popens[client] = client.popen("wget -O - {}".format(server.IP()))		
	if client.name == "h2":
		popens[client] = client.popen("nslookup 10.0.0.4")
	if client.name == "h3":
		popens[client] = client.popen('curl ftp://' + server.IP()+ ' --user ubuntu:ubuntu')
    

    

    # (Stoping DNS Server)
    popens[server] = server.popen('kill %dnsmasq')
    # (Stoping HTTP Server)
    popens[server] = server.popen('kill %python &')
    #server.cmd('kill %python &')
  
    popens[server] = server.popen('iperf -s -p 5003 &')

    for client in net.hosts:
    	if client.name != server.name: 
		#print client
		popens[client] = client.popen('iperf -c ' +  server.IP() + ' -p 5003')
    
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
