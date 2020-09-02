from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def netTAR():

    #Here we run mininet using remote controller, that in my case is 
    #at 100.0.0.2:6653
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)
    c1 = net.addController('c1', controller=RemoteController,
ip="100.0.0.2", port=6653)

    h1 = net.addHost( 'h1', ip='10.0.1.1' )
    h2 = net.addHost( 'h2', ip='10.0.2.1' )


    #For better compatiblity with ODL, we use OpenFlow13 protocol for switches
    s1 = net.addSwitch( 's1' , protocols="OpenFlow13")
    s2 = net.addSwitch( 's2' , protocols="OpenFlow13")
    s3 = net.addSwitch( 's3' , protocols="OpenFlow13")

    s1.linkTo( h1 )
    s1.linkTo( s3 )
    s3.linkTo( s2 )
    s2.linkTo( h2 )



    net.build()
    c1.start()

    s1.cmd('ifconfig s1-eth1 10.0.1.2 netmask 255.255.255.0')
    s1.cmd('ifconfig s1-eth2 10.0.1.3 netmask 255.255.255.0')
    s2.cmd('ifconfig s2-eth1 10.0.2.2 netmask 255.255.255.0')
    s2.cmd('ifconfig s2-eth2 10.0.2.3 netmask 255.255.255.0')
    s3.cmd('ifconfig s3-eth1 10.0.1.4 netmask 255.255.255.0')
    s3.cmd('ifconfig s3-eth2 10.0.2.4 netmask 255.255.255.0')

    #Deleting the default flows.
    s1.cmd('ovs-ofctl -O Openflow13 del-flows s1')
    s2.cmd('ovs-ofctl -O Openflow13 del-flows s2')
    s3.cmd('ovs-ofctl -O Openflow13 del-flows s3')


    s1.start( [c1] )
    s3.start( [c1] )
    s2.start( [c1] )
    net.start()


    CLI( net )
    net.stop()

if __name__ == '__main__':
     setLogLevel( 'info' )
     netTAR()


