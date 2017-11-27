#!/usr/bin/python
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.util import quietRun
from mininet.log import setLogLevel, info
from mininet.term import makeTerms
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch

#from mininet.examples.nat import connectToInternet, stopNAT

from sys import exit, stdin, argv
from re import findall
from time import sleep
import os

class QosDemo2( Topo ):
    """Topology for Web Demo:
       client - switch - link - Web server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        h3 = self.addHost( 'h3' )
        s1 = self.addSwitch( 's1', protocols=["OpenFlow13"] )
        s2 = self.addSwitch( 's2', protocols=["OpenFlow13"] )
        h4 = self.addHost( 'h4')
        #c0 = self.addController( 'c0', controller=RemoteController, ip='192.168.56.104', port=6633 )
        self.addLink( h1, s1 )
        self.addLink( h2, s1 )
        self.addLink( h3, s1 )
        #LAN2
        self.addLink( h4, s2 )
        self.addLink( s1, s2 )


def readline():
    "Read a line from stdin"
    return stdin.readline()


def prompt( s=None ):
    "Print a prompt and read a line from stdin"
    if s is None:
        s = "Press return to continue: "
    print s,
    return readline()


def clientRequestToServer(h1):
    # Make sure we can fetch get request
    info( '* Fetching file web server 100 times:\n' )
    h1.cmd( 'cd Downloads')
    print h1.cmd( 'pwd')
    qt = 1
    while  qt <= 1:
        #print h1.cmd( 'wget http://10.0.0.56/index.html >& /tmp/index.html &' )
        #print h1.cmd( 'curl http://10.0.0.50' )
        print h1.cmd( 'curl http://10.0.0.50/index.html' )
        qt= qt + 1

    info( '*** End Fetching Web Page!:\n' )

def qosdemo( ):
    "Rogue Web server demonstration"
    #checkRequired()
    topo = QosDemo2()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)

    #h1, web, sw = net.get( 'h1', 'web' , 's1')
    h1, h2,h3,h4, s1, ryu = net.get( 'h1', 'h2' , 'h3','h4', 's1', 'c0')


    net.start()
    #OVSB CONFIG
    #sw.cmd('cd qos-command')
    #sw.cmd('./ovs-qos-run')

    #IPERF TEST
    h4.cmd('iperf -s -p 4000 &')
    print h1.cmd('iperf -c 10.0.0.4 -p 4000')
    #
    h4.cmd('iperf -s -p 5000 &')
    print h2.cmd('iperf -c 10.0.0.4 -p 5000')

    h4.cmd('iperf -s -p 6000 &')
    print h3.cmd('iperf -c 10.0.0.4 -p 6000')


    prompt( "*** Execute script to enable QOS and press enter: " )

    h4.cmd('iperf -s -p 4000 &')
    print h1.cmd('iperf -c 10.0.0.4 -p 4000')
    #
    h4.cmd('iperf -s -p 5000 &')
    print h2.cmd('iperf -c 10.0.0.4 -p 5000')

    h4.cmd('iperf -s -p 6000 &')
    print h3.cmd('iperf -c 10.0.0.4 -p 6000')

    # startWebServer( h2 )
    #
    # clientRequestToServer(h1)
    #
    #
    #
    # stopWebServer( h2 )

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
    qosdemo()
