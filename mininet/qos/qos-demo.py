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

class QosDemo( Topo ):
    """Topology for Web Demo:
       client - switch - link - Web server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        client = self.addHost( 'h1' )
        switch = self.addSwitch( 's1', protocols=["OpenFlow13"] )
        web = self.addHost( 'h2')
        #c0 = self.addController( 'c0', controller=RemoteController, ip='192.168.56.104', port=6633 )
        self.addLink( client, switch )
        #self.addLink( web, switch, bw=10, delay='500ms' )
        self.addLink( web, switch )

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
    topo = QosDemo()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)

    #h1, web, sw = net.get( 'h1', 'web' , 's1')
    h1, h2, sw, ryu = net.get( 'h1', 'h2' , 's1', 'c0')


    net.start()
    #OVSB CONFIG
    sw.cmd('ovs-vsctl set Bridge s1 protocols=OpenFlow13')
    sw.cmd('ovs-vsctl set-manager ptcp:6632')


    #QUEUE COONFIG
    print ryu.cmd("""curl -X PUT -d '"tcp:127.0.0.1:6632"' http://localhost:8080/v1.0/conf/switches/0000000000000001/ovsdb_addr""")
    print ryu.cmd("""curl -X POST -d '{"port_name": "s1-eth1", "type": "linux-htb", "max_rate": "1000000", "queues": [{"max_rate": "500000"}, {min_rate": "700000"}]}' http://localhost:8080/qos/queue/0000000000000001""")
    #print ryu.cmd("""curl -X PUT -d '"tcp:192.168.56.104:6632"' http://localhost:8080/v1.0/conf/switches/0000000000000001/ovsdb_addr""")


    #OOS CONFIG
    #print ryu.cmd(""" curl -X POST -d '{"match": {"nw_dst": "10.0.0.1", "nw_proto": "UDP", "tp_dst": "5001"} , "actions":{"queue": "0"}}' http://localhost:8080/qos/rules/0000000000000001""")
    print ryu.cmd(""" curl -X POST -d '{"match": {"nw_dst": "10.0.0.1", "nw_proto": "UDP", "tp_dst": "5002"} , "actions":{"queue": "1"}}' http://localhost:8080/qos/rules/0000000000000001""")
    print ryu.cmd(""" curl -X POST -d '{"match": {"nw_dst": "10.0.0.1", "nw_proto": "UDP", "tp_dst": "5003"} , "actions":{"queue": "0"}}' http://localhost:8080/qos/rules/0000000000000001""")

    # print ryu.cmd('curl -X GET http://localhost:8080/qos/rules/0000000000000001')

    #IPERF TEST
    h1.cmd('iperf -s -u -i 1 -p 5002 &')
    print h2.cmd('iperf -c 10.0.0.1 -p 5002 -u -b 1M')
    #
    h1.cmd('iperf -s -u -i 1 -p 5003 &')
    print h2.cmd('iperf -c 10.0.0.1 -p 5003 -u -b 1M')

    h1.cmd('iperf -s -u -i 1 -p 5004 &')
    print h2.cmd('iperf -c 10.0.0.1 -p 5004 -u -b 1M')


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
