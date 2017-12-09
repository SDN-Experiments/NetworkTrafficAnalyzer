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
        #Clients
        h1 = self.addHost( 'h1' )
        h2 = self.addHost( 'h2' )
        h3 = self.addHost( 'h3' )
        s1 = self.addSwitch( 's1', protocols=["OpenFlow13"] )
        s2 = self.addSwitch( 's2', protocols=["OpenFlow13"] )
        #server
        h4 = self.addHost( 'h4')
        #LAN1
        self.addLink( h1, s1 ,bw=15)
        self.addLink( h2, s1 ,bw=15)
        self.addLink( h3, s1 )
        #LAN2
        self.addLink( h4, s2 )
        self.addLink( s1, s2 )


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

def startDnsServer( host ):
    "Start Fake DNS server"
    info( '* Starting fake DNS server', host, 'at', host.IP(), '\n' )
    host.cmd( 'dnsmasq -k -A /#/%s 1>/tmp/dns.log 2>&1 &' %  host.IP() )

def stopDnsServer( host ):
    "Stop Fake DNS server"
    info( '* Stopping fake DNS server', host, 'at', host.IP(), '\n' )
    host.cmd( 'kill %dnsmasq' )

def startFTPServer( host ):
    "Start ftp server"
    info( '* Starting FTP server', host, 'at', host.IP(), '\n' ) 
    #host.cmd('kill %ftpd') 
    host.cmd('inetd &')

def stopFTPServer( host ):
    "Stop ftp server"
    info( '* Exiting ftp server', '\n' )




def readline():
    "Read a line from stdin"
    return stdin.readline()


def prompt( s=None ):
    "Print a prompt and read a line from stdin"
    if s is None:
        s = "Press return to continue: "
    print s,
    return readline()


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
    h1,h2,h3,h4,s1,ryu = net.get( 'h1', 'h2', 'h3','h4', 's1', 'c0')
    #info( "***Testing bandwidth between client and server Before...\n")



    net.start()

    # print ('*** Testing bandwidth Web... \n')
    # h4.cmd('iperf -s -p 80 &')
    # print h1.cmd('iperf -c ' +  h4.IP() + ' -p 80')
    # print net.iperf( (h1, h4) )
    # print ('*** Testing bandwidth DNS... \n')
    # print net.iperf( (h2, h4) )

    print('------------------------------------------------------------')
    print ryu.cmd('cd qos-command')
    print ryu.cmd('sudo ./ovs-qos-run')

    # print ('*** Testing bandwidth... \n')
    # print net.iperf( (h2, h4) )

    print('------------------------------------------------------------')
    print ('*** Testing Flow Web... \n')
    startWebServer(h4)
    clientRequestToServerWEB(h1, h4)
    #
    stopWebServer( h4 )
    #
    #h4.cmd('iperf -s -p 5000 &')
    #print h1.cmd('iperf -c ' +  h4.IP() + ' -p 5000')

    # #info( "***Testing bandwidth between client and server After...\n")
    # #print net.iperf( (h1, web) )
    # print ('*** Testing bandwidth... \n')
    # print net.iperf( (h1, h4) )
    # # h4.cmd('iperf -s -p 4000 &')
    # # print h1.cmd('iperf -c ' +  h4.IP() + ' -p 4000')
    #
    #
    #
    # stopWebServer( h4 )
    print('------------------------------------------------------------')
    print ('*** Testing Flow DNS... \n')
    startDnsServer( h4 )


    clientRequestToServerDNS(h2,h4)

    stopDnsServer( h4 )

    print ('*** Testing bandwidth... \n')
    #h4.cmd('iperf -s -p 4000 &')
    #print h2.cmd('iperf -c ' +  h4.IP() + ' -p 5000')
    print('------------------------------------------------------------')
    # print net.iperf( (h2, h4) )

    print('------------------------------------------------------------')
    print ('*** Testing Flow FTP... \n')
    startFTPServer( h4 )


    clientRequestToServerFTP(h3,h4)

    stopFTPServer( h4 )

    print ('*** Testing bandwidth... \n')
    #h4.cmd('iperf -s -p 4000 &')
    #print h2.cmd('iperf -c ' +  h4.IP() + ' -p 5000')
    print('------------------------------------------------------------')
    # print net.iperf( (h2, h4) )	
    net.stop()

def clientRequestToServerDNS(h1, h4):
    info( '*** Request NsLookup google.com...\n' )

    print h1.cmd( 'nslookup 10.0.0.4 ' )

def clientRequestToServerWEB(h1, h4):
    # Make sure we can fetch get request
    info( '* Fetching file web server:\n' )
    h1.cmd( 'cd Downloads')
    # print h1.cmd( 'pwd')
    # qt = 1

    # while  qt <= 1:

        # print h1.cmd( 'curl http://' + h4.IP() + '/index.html' )
        # qt= qt + 1
    print h1.cmd( 'curl http://' + h4.IP() + '/index.html' )
    info( '*** End Fetching Web Page!:\n' )

def clientRequestToServerFTP(client, server):
    info( '* Requesting to FTP server', client, 'at', client.IP(), '\n' )
    print client.cmd('lftp -u ubuntu,ubuntu -e ',  '"cd ftp;get temp.ftp;quit" ', server.IP())


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
