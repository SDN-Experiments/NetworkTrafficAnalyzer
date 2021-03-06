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
from sys import exit, stdin, argv
from re import findall
from time import sleep
import os
from ftplib import FTP


def checkRequired():
    "Check for required executables"
    required = [ 'ftpd',  'lftp' ]
    for r in required:
        if not quietRun( 'which ' + r ):
            print '* Installing', r
            print quietRun( 'apt-get install -y ' + r )

class FtpTopo( Topo ):
    """Topology for Ftp Demo:
       client - switch - link - Ftp server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        client = self.addHost( 'h1' )
        switch = self.addSwitch( 's1', protocols=["OpenFlow13"] )
        ftp = self.addHost( 'ftp')
        #c0 = self.addController( 'c0', controller=RemoteController, ip='192.168.56.104', port=6633 )
        self.addLink( client, switch )
        self.addLink( ftp, switch, bw=1000 )

# ftp server

def startFTPServer( host ):
    "Start ftp server"
    info( '* Starting FTP server', host, 'at', host.IP(), '\n' ) 
    #host.cmd('kill %ftpd') 
    host.cmd('inetd &')

def stopFTPServer( host ):
    "Stop ftp server"
    info( '* Exiting ftp server', '\n' )

def clientRequestToServer(client, server):
    #print client.cmd('pftp -u ubuntu,ubuntu -e "get myfile;quit" ' + server.IP())
    info( '* Requesting to FTP server', client, 'at', client.IP(), '\n' )
    #client.cmd( 'cd Downloads')
    #print client.cmd( 'pwd')
    #print client.cmd('cd Downloads')
    print client.cmd('lftp -u ubuntu,ubuntu -e ',  '"cd ftp;get temp.ftp;quit" ', server.IP())
    #print client.cmd('lftp -e ''cd ftp/; get temp.ftp'' -u ubuntu,ubuntu 10.0.0.2')
    #print client.cmd( 'curl ftp://10.0.0.1/myfile' )
   
         


def readline():
    "Read a line from stdin"
    return stdin.readline()


def prompt( s=None ):
    "Print a prompt and read a line from stdin"
    if s is None:
        s = "Press return to continue: "
    print s,
    return readline()

def ftpdemo( ):
    "Rogue ftp server demonstration"
    #checkRequired()
    topo = FtpTopo()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch,
      autoSetMacs=True)


    h1, ftp, sw = net.get( 'h1', 'ftp' , 's1')

    #checkRequire()


    net.start()
    #net.iperf((h1,ftp))
    startFTPServer( ftp )

    clientRequestToServer(h1,ftp)

    stopFTPServer( ftp )
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
    ftpdemo()
