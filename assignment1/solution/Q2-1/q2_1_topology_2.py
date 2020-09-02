from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info



net = Mininet()




info( '*** Add hosts ***\n' )
green2 = net.addHost('green2', ip='10.0.0.2')
blue2 = net.addHost('blue2', ip='10.0.0.2')

info( '*** Add switch ***\n' )
s2 = net.addSwitch('s2')

info ( '*** Create links ***\n' )
net.addLink( green2, s2 )
net.addLink( blue2, s2 )

info ( '*** Start network ***\n' )
net.build()
net.start()

s2.cmd('ovs-vsctl add-port s2 vtep -- set interface vtep type=vxlan option:remote_ip=100.0.0.3 option:key=flow ofport_request=3')
s2.cmd('ovs-ofctl add-flows s2 flows2.txt')

info ( '*** Run CLI ***\n' )

CLI(net)

info( '*** Stop network ***' )
net.stop()


