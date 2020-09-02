from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info



net = Mininet()




info( '*** Add hosts ***\n' )
green1 = net.addHost('green1', ip='10.0.0.1')
blue1 = net.addHost('blue1', ip='10.0.0.1')

info( '*** Add switch ***\n' )
s1 = net.addSwitch('s1')

info ( '*** Create links ***\n' )
net.addLink( green1, s1 )
net.addLink( blue1, s1 )

info ( '*** Start network ***\n' )
net.build()
net.start()

#Making the tunnel
s1.cmd('ovs-vsctl add-port s1 vtep -- set interface vtep type=vxlan option:remote_ip=100.0.0.4 option:key=flow ofport_request=3')
#Importing the flows from file
s1.cmd('ovs-ofctl add-flows s1 flows1.txt')
#The first two flows, put vxlan id 100 and 200 on any packet coming out of hosts 1 and 2 and resubmits it to table_1
#The third flow, just resubmits any other packet to be processed in table_2
#The next flows just route the packets based on their vxlan ids through vxlan tunnels 1 and 2

info ( '*** Run CLI ***\n' )
CLI(net)

info( '*** Stop network ***' )
net.stop()

