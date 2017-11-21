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
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from ftplib import FTP

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

class FtpTopo( Topo ):
    """Topology for Ftp Demo:
       client - switch - link - Ftp server
                  """
    def __init__( self, *args, **kwargs ):
        Topo.__init__( self, *args, **kwargs )
        client = self.addHost( 'h1', ip='10.0.0.10/24' )
        switch = self.addSwitch( 's1', protocols=["OpenFlow13"] )
        ftp = self.addHost( 'ftp', ip='10.0.0.50/24')
        #c0 = self.addController( 'c0', controller=RemoteController, ip='192.168.56.104', port=6633 )
        self.addLink( client, switch )
        self.addLink( ftp, switch, bw=10, delay='500ms' )

# ftp server

server = None
def startFTPServer( host ):
    "Start evil ftp server"
    info( '* Starting FTP server', host, 'at', host.IP(), '\n' )

    authorizer = DummyAuthorizer()
    authorizer.add_user("ubuntu", "ubuntu", "/home/ubuntu/ftp", perm="elradfmw")
    authorizer.add_anonymous("/home/ubuntu/ftp", perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = authorizer

    server = FTPServer((host.IP(), 21), handler)
    server.serve_forever()


def stopFTPServer( host ):
    "Stop ftp server"
    info( '* Stopping ftp server', host, 'at', host.IP(), '\n' )
    server.clo

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


def ftpdemo( ):
    "Rogue ftp server demonstration"
    #checkRequired()
    topo = FtpTopo()
    net = Mininet( topo=topo,
    controller=lambda name: RemoteController( name = 'c0', ip='192.168.56.104' ),
      link=TCLink,
      switch=OVSKernelSwitch)


    h1, ftp, sw = net.get( 'h1', 'ftp' , 's1')



    net.start()
    #verifyConnection(h1, ftp)
    # And an ftp server
    startFTPServer( ftp )

    clientRequestToServer(h1,ftp)

    stopFTPServer( ftp )
    net.stop()

def clientRequestToServer(client, server):
    # Make sure we can fetch get request
    info( '* Fetching file FTP server:\n' )
    # ftp = FTP('')
    # ftp.connect(server.IP(),21)
    # ftp.login()
    # ftp.cwd('directory_name') #replace with your directory
    # ftp.retrlines('LIST')
    # uploadFile()
    print client.cmd('wget ftp://ubuntu:ubuntu@SERVERNAME/ftp/temp.ftp')

def uploadFile():
     filename = 'testfile.txt' #replace with your file in your home folder
     ftp.storbinary('STOR '+filename, open(filename, 'rb'))
     ftp.quit()

def downloadFile():
     filename = 'testfile.txt' #replace with your file in the directory ('directory_name')
     localfile = open(filename, 'wb')
     ftp.retrbinary('RETR ' + filename, localfile.write, 21)
     ftp.quit()
     localfile.close()
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
    ftpdemo()
