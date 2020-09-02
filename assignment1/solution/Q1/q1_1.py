from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info


#net = Mininet(controller=RemoteController)
net = Mininet()


info( '*** Add hosts ***\n' )
h1 = net.addHost('h1', ip='10.0.1.1')
h2 = net.addHost('h2', ip='10.0.1.6')

info( '*** Add switches ***\n' )
s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')

info ( '*** Create links ***\n' )
net.addLink( h1, s1 )
net.addLink( s1, s2 )
net.addLink( h2, s2 )

info ( '*** Start network ***\n' )
net.build()
net.start()

#Setting the interface ips as in the question, busing ifconfig
s1.cmd('ifconfig s1-eth1 10.0.1.2 netmask 255.255.255.0 up')
s1.cmd('ifconfig s1-eth2 10.0.1.3 netmask 255.255.255.0 up')
s2.cmd('ifconfig s2-eth2 10.0.1.4 netmask 255.255.255.0 up')
s2.cmd('ifconfig s2-eth1 10.0.1.5 netmask 255.255.255.0 up')

#Here we set flows using command line
#These two rules, match literally everything and the output-port is set to
#NORMAL meaning that these switches just do the regular switching, when 
#some packet is received from one port, it gets sent to other ports.
s1.cmd('ovs-ofctl add-flow s1 action=normal')
s2.cmd('ovs-ofctl add-flow s2 action=normal')

info ( '*** Run CLI ***\n' )

CLI(net)

info( '*** Stop network ***' )
net.stop()


