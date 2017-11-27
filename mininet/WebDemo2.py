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

def checkRequired():
    "Check for required executables"
    required = [ 'udhcpd', 'udhcpc', 'dnsmasq', 'curl', 'firefox' ]
    for r in required:
        if not quietRun( 'which ' + r ):
            print '* Installing', r
            print quietRun( 'apt-get install -y ' + r )
            if r == 'dnsmasq':
                # Don't run dnsmasq by default!
                print quietRun( 'update-rc.d dnsmasq disable' )

class WebTopo2( Topo ):
    """Topology for Web Demo:
       client - switch - link - Web server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        client = self.addHost( 'h1', ip='10.0.0.10/24' )
        switch = self.addSwitch( 's1', protocols=["OpenFlow13"] )
        web = self.addHost( 'web', ip='10.0.0.50/24')
        #c0 = self.addController( 'c0', controller=RemoteController, ip='192.168.56.104', port=6633 )
        self.addLink( client, switch )
        #self.addLink( web, switch, bw=10, delay='500ms' )
        self.addLink( web, switch )

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

def readline():
    "Read a line from stdin"
    return stdin.readline()


def prompt( s=None ):
    "Print a prompt and read a line from stdin"
    if s is None:
        s = "Press return to continue: "
    print s,
    return readline()

def verifyConnection(client, server):
    print client.cmd('ping -c 1 ' + server.IP())
    print server.cmd('ping -c 1 ' + client.IP())

def webdemo2( ):
    "Rogue Web server demonstration"
    #checkRequired()
    topo = WebTopo2()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)

    #h1, web, sw = net.get( 'h1', 'web' , 's1')
    h1, web, sw, ryu = net.get( 'h1', 'web' , 's1', 'c0')
    #info( "***Testing bandwidth between client and server Before...\n")

    # h1.cmd("ifconfig h1-eth0 0")
    # web.cmd("ifconfig web-eth0 0")
    #
    # sw.cmd("ifconfig s1-eth1 0")
    # sw.cmd("ifconfig s1-eth2 0")
    #
    # sw.cmd("brctl addbr mybr")
    # sw.cmd("brctl addif mybr s1-eth1")
    # sw.cmd("brctl addif mybr s1-eth2")
    #
    # sw.cmd("ifconfig mybr up")
    #
    # h1.cmd("ip address add 10.0.0.10/24 dev h1-eth0")
    # h1.cmd("route add default gw 10.0.0.1")
    # #h1.cmd("iperf -c ", web.IP(), " -p 5001 -u -b 1M &")
    #
    # web.cmd("ip address add 10.0.0.50/24 dev web-eth0")
    # web.cmd("route add default gw 10.0.0.1")
    #web.cmd("iperf -s -u -i 1 -p 5001 &")
    # sw.cmd('ovs-vsctl set Bridge s1 protocols=OpenFlow13')
    # sw.cmd('ovs-vsctl set-manager ptcp:6632')

    net.start()
    sw.cmd('ovs-vsctl set Bridge s1 protocols=OpenFlow13')
    sw.cmd('ovs-vsctl set-manager ptcp:6632')


    ryu.cmd('curl -X PUT -d '"tcp:127.0.0.1:6632"' http://localhost:8080/v1.0/conf/switches/0000000000000001/ovsdb_addr')
    #ryu.cmd('curl -X POST -d "{'"port_name"': '"s1-eth1"', '"type"': '"linux-htb"', '"max_rate"': '"1000000"', '"queues"': [{'"max_rate"': '"500000"'}, {'"min_rate"': '"800000"'}]}" http://localhost:8080/qos/queue/0000000000000001')
    print ryu.cmd(""" curl -X POST -d '{"port_name": "s1-eth1", "type": "linux-htb", "max_rate": "1000000", queues": [{"max_rate": "500000"}, {"min_rate": "800000"}]}' http://localhost:8080/qos/queue/0000000000000001""")
    print ryu.cmd(""" curl -X POST -d '{"match": {"nw_dst": "10.0.0.50", "nw_proto": "UDP", "tp_dst": "5002"} , "actions":{"queue": "1"}}' http://localhost:8080/qos/rules/0000000000000001""")
    #print ryu.cmd("curl http://localhost:8080/qos/queue/0000000000000001")

    #print net.iperf( (h1,web), l4Type='TCP') )

    #ryu.cmd('curl -X POST -d ''{"port_name": "s1-eth1", "type": "linux-htb", "max_rate": "5000000", "queues": [{"max_rate": "1000000"}, {"min_rate": "2000000", "max_rate": "3000000"}, {"min_rate": "4000000"}, ]}''')

    #ryu.cmd('curl -X POST -d ''{"port_name": "s1-eth2", "type": "linux-htb", "max_rate": "5000000", "queues": [{"max_rate": "1000000"}, {"min_rate": "2000000", "max_rate": "3000000"}, {"min_rate": "4000000"}, ]}''')
    #verifyConnection(h1, web)

    startWebServer( web )

    clientRequestToServer(h1)

    #info( "***Testing bandwidth between client and server After...\n")
    #print net.iperf( (h1, web) )

    stopWebServer( web )

    net.stop()

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
