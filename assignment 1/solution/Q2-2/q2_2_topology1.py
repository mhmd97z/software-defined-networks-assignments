from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def netTAR():
        net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)
        c1 = net.addController('c1', controller=RemoteController,
ip="100.0.0.2", port=6653)

        info( '*** Add hosts ***\n' )
        green1 = net.addHost('green1', ip='10.0.0.1')
        blue1 = net.addHost('blue1', ip='10.0.0.1')

        info( '*** Add switch ***\n' )
        s1 = net.addSwitch('s1', protocols="OpenFlow13")

        info ( '*** Create links ***\n' )
        net.addLink( green1, s1 )
        net.addLink( blue1, s1 )

        info ( '*** Start network ***\n' )
        net.build()
        c1.start()

        s1.start( [c1] )
        net.start()

        #Making the switch listen for ovsdb controller
        s1.cmd('sh ovs-vsctl set-manager ptcp:6640')

        info ( '*** Run CLI ***\n' )

        CLI(net)

        info( '*** Stop network ***' )
        net.stop()

if __name__=='__main__':
        setLogLevel( 'info' )
        netTAR()

