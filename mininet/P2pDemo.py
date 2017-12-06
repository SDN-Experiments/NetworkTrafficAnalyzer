#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.link import Intf
from mininet.log import setLogLevel, info

def P2pDemo():

    net = Mininet( topo=None,
                   build=False)

    info( '*** Adding controller\n' )
    c0 = net.addController( 'c0', controller=RemoteController, ip='192.168.0.108', port=6633 )

    info( '*** Add switches\n')
    s1 = net.addSwitch('s1')
    Intf( 'eth0', node=s1 )

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', ip='0.0.0.0')

    info( '*** Add links\n')
    net.addLink(h1, s1)

    info( '*** Starting network\n')
    net.start()
    h1.cmdPrint('dhclient '+h1.defaultIntf().name)
    #h1.cmd(sudo deluge-gtk 'magnet:?xt=urn:btih:c1aa77dea674d71fbd85559034b6082b8434d36e&dn=lubuntu-16.04.3-desktop-amd64.iso')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    P2pDemo()
