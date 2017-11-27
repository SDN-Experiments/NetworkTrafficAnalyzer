#!/usr/bin/python

"""
Rogue DHCP server demo for Stanford CS144.
We set up a network where the DHCP server is on a slow
link. Then we start up a rogue DHCP server on a fast
link which should beat it out (although we should look
at wireshark for the details.) This rogue DHCP server
redirects DNS to a rogue DNS server, which redirects
all DNS queries to the attacker. Hilarity ensues.
The demo supports two modes: the default interactive
mode (X11/firefox) or a non-interactive "text" mode
(text/curl).
We could also do the whole thing without any custom
code at all, simply by using ettercap.
Note you may want to arrange your windows so that
you can see everything well.
"""

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

class sslTopo( Topo ):
    """Topology for ssl Demo:
       client - switch - link - ssl server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        client = self.addHost( 'h2', ip='10.0.0.2/24' )
        switch = self.addSwitch( 's2', protocols=["OpenFlow13"] )
        ssl = self.addHost( 'ssl', ip='10.0.0.20/24')
        #c0 = self.addController( 'c0', controller=RemoteController, ip='192.168.0.113', port=6633 )
        self.addLink( client, switch )
        self.addLink( ssl, switch, bw=10, delay='500ms' )

# ssl server

def startsslServer( host ):
    "Start evil ssl server"
    info( '* Starting ssl server', host, 'at', host.IP(), '\n' )
    ssldir = '/tmp/sslserver'
    host.cmd( 'rm -rf', ssldir )
    host.cmd( 'mkdir -p', ssldir )
    with open( ssldir + '/index.html', 'w' ) as f:
        # If we wanted to be truly evil, we could add this
        # to make it hard to retype URLs in firefox
        # f.write( '<meta http-equiv="refresh" content="1"> \n' )
        f.write( '<html><p>SDN is already a reality!<p>\n'
                 '<body></body></html>' )
    host.cmd( 'cd', ssldir )
    host.cmd( 'python -m SimpleHTTPServer 4443 >& /tmp/http.log &' )

def stopsslServer( host ):
    "Stop evil ssl server"
    info( '* Stopping ssl server', host, 'at', host.IP(), '\n' )
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


def ssldemo( ):
    "Rogue ssl server demonstration"
    #checkRequired()
    topo = sslTopo()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.0.113' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)


    h2, ssl, sw = net.get( 'h2', 'ssl' , 's2')

    # h1.cmd("ifconfig h1-eth0 0")
    # ssl.cmd("ifconfig h2-eth0 0")
    #
    # sw.cmd("ifconfig sw-eth0 0")
    # sw.cmd("ifconfig sw-eth1 0")
    #
    # sw.cmd("brctl addbr mybr")
    # sw.cmd("brctl addif mybr sw-eth0")
    # sw.cmd("brctl addif mybr sw-eth1")
    #
    # sw.cmd("ifconfig mybr up")
    #
    # h1.cmd("ip address add 10.0.0.10/24 dev h1-eth0")
    # ssl.cmd("ip address add 10.0.0.50/24 dev h2-eth0")



    #verifyConnection(h1, ssl)
    # And an ssl server
    net.start()

    startsslServer( ssl )

    clientRequestToServer(h2)

    stopsslServer( ssl )




    net.stop()



def clientRequestToServer(h2):
    # Make sure we can fetch get request
    info( '* Fetching file ssl server 100 times:\n' )
    h2.cmd( 'cd Downloads')
    print h2.cmd( 'pwd')
    qt = 1
    while  qt <= 1:
        #print h1.cmd( 'wget http://10.0.0.56/index.html >& /tmp/index.html &' )
        #print h1.cmd( 'curl http://10.0.0.50' )
        print h2.cmd( 'curl https://10.0.0.20/index.html:4443' )
        qt= qt + 1

    info( '* End Fetching!:\n' )
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
    ssldemo()
