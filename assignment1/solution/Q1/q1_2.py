from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink


net = Mininet()

h1 = net.addHost('h1', ip='10.0.1.1')
h2 = net.addHost('h2', ip='10.0.2.1')

s1 = net.addSwitch('s1')
s2 = net.addSwitch('s2')

r1 = net.addSwitch('r1')

net.addLink(h1, s1)
net.addLink(h2, s2)
net.addLink(s1, r1)
net.addLink(s2, r1)

net.build()
net.start()

s1.cmd('ifconfig s1-eth1 10.0.1.2 netmask 255.255.255.0')
s1.cmd('ifconfig s1-eth2 10.0.1.3 netmask 255.255.255.0')
s2.cmd('ifconfig s2-eth1 10.0.2.2 netmask 255.255.255.0')
s2.cmd('ifconfig s2-eth2 10.0.2.3 netmask 255.255.255.0')
r1.cmd('ifconfig r1-eth1 10.0.1.4 netmask 255.255.255.0')
r1.cmd('ifconfig r1-eth2 10.0.2.4 netmask 255.255.255.0')


s1.cmd('ovs-ofctl add-flow s1 action=normal')
s2.cmd('ovs-ofctl add-flow s2 action=normal')

#Here we add l3 forwarding rules using command line
#The first rule says that when an arp(2054) packet is received with source
#of 1.1 it will be sent out of port 2, the second rule is for ip(2048) packets
#and the latter two send packets with source 2.1 out of port 1
r1.cmd('ovs-ofctl add-flow r1 arp,nw_src=10.0.1.1,action=2')
r1.cmd('ovs-ofctl add-flow r1 ip,nw_src=10.0.1.1,action=2')
r1.cmd('ovs-ofctl add-flow r1 arp,nw_src=10.0.2.1,action=1')
r1.cmd('ovs-ofctl add-flow r1 ip,nw_src=10.0.2.1,action=1')


CLI(net)

net.stop()



