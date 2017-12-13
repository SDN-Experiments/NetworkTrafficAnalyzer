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
	
class MultiThreadHubDemo( Topo ):
    """Topology for Web Demo:
       client - switch - link - Web server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        #Clients
        #h1 = self.addHost( 'h1' )
        #h2 = self.addHost( 'h2' )
        #h3 = self.addHost( 'h3' )
        s1 = self.addSwitch( 's1', protocols=["OpenFlow13"] )
        s2 = self.addSwitch( 's2', protocols=["OpenFlow13"] )
	s3 = self.addSwitch( 's3', protocols=["OpenFlow13"] )
        s4 = self.addSwitch( 's4', protocols=["OpenFlow13"] )
	s5 = self.addSwitch( 's5', protocols=["OpenFlow13"] )
	s6 = self.addSwitch( 's6', protocols=["OpenFlow13"] )

        #server
        h4 = self.addHost( 'h4')
        #LAN1
	for h in range(120):
	    if h+1 != 4:
            	host = self.addHost('h%s' % (h + 1))
		if h+1 >=  1 and h+1 <= 24:
	        	self.addLink(host ,s1 , bw=15)
		if h+1 >  24 and h+1 <= 48:
	        	self.addLink(host ,s2 , bw=15)
		if h+1 >  48 and h+1 <= 72:
	        	self.addLink(host ,s3 , bw=15)
		if h+1 >  72 and h+1 <= 96:
	        	self.addLink(host ,s4 , bw=15)
		if h+1 >  96 and h+1 <= 120:
	        	self.addLink(host ,s5, bw=15)
        #self.addLink( h1, s1 ,bw=15)
        #self.addLink( h2, s1 ,bw=15)
        #self.addLink( h3, s1 ,bw=15)
        #LAN2
        self.addLink( h4, s2 )
        self.addLink( s1, s6 )
	self.addLink( s2, s6 )
	self.addLink( s3, s6 )
	self.addLink( s4, s6 )
	self.addLink( s5, s6 )


# web server

def startWebServer( host ):
    "Start evil web server"
    info( '* Starting web server', host, 'at', host.IP(), '\n' )
    webdir = '/tmp/webserver'
    host.cmd( 'rm -rf', webdir )
    host.cmd( 'mkdir -p', webdir )
    with open( webdir + '/index.html', 'w' ) as f:
        # If we wanted to be truly evil, we could add this
        # to make it hard to retype URLs in firefox
        # f.write( '<meta http-equiv="refresh" content="1"> \n' )
        f.write( '<html><p>SDN is already a reality!<p>\n'
                 '<body></body></html>' )
    host.cmd( 'cd', webdir )
    host.cmd( 'python -m SimpleHTTPServer 80 >& /tmp/http.log &' )

def stopWebServer( host ):
    "Stop evil web server"
    info( '* Stopping web server', host, 'at', host.IP(), '\n' )
    host.cmd( 'kill %python' )


def webdemo2( ):
    "Rogue Web server demonstration"
    #checkRequired()
    topo = MultiThreadHubDemo()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)


    popens = {}
    server = net.get('h4')
    startWebServer(server)
    net.start()

    webdir = '/tmp/webserver'
   
    popens[server] = server.popen( "cd ", webdir, " &"  )
    popens[server] = server.popen("python -u-m SimpleHTTPServer 80 >& /tmp/http.log &")
    sleep(1)  # Wait for the server to start up.
    popens[server] = server.popen('dnsmasq -k -A /#/%s 1>/tmp/dns.log 2>&1 &' %  server.IP())
    sleep(1)  # Wait for the server to start up.
    popens[server] = server.popen("inetd &")
    sleep(1)  # Wait for the server to start up.

    #SO ONLY ONE HOST 0.1K TEST
    """h1 = net.get('h1')
    for client in range(1,100):
	popens[h1] = h1.popen("wget -O - {}".format(server.IP())) """
    for client in net.hosts:
	num = randint(1,3)
	if num ==1:
		popens[client] = client.popen("wget -O - {}".format(server.IP() + " &"))
	if num ==2:
		popens[client] = client.popen("nslookup 10.0.0.4 &")
	if num ==3:
		popens[client] = client.popen('lftp -u ubuntu,ubuntu -e ',  '"cd ftp;get temp.ftp;quit" ', server.IP() , ' &')
		popens[client] = client.popen('rm temp.ftp &')
    
    popens[server] = server.popen('kill %dnsmasq &')
    popens[server] = server.popen('kill %python &')
    


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
    webdemo2()
