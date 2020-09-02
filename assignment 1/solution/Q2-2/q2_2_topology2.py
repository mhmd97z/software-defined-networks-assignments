from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info



def netTAR():
        net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)
        c1 = net.addController('c1', controller=RemoteController,
ip="100.0.0.2", port=6653)

        info( '*** Add hosts ***\n' )
        green2 = net.addHost('green2', ip='10.0.0.2')
        blue2 = net.addHost('blue2', ip='10.0.0.2')

        info( '*** Add switch ***\n' )
        s2 = net.addSwitch('s2', protocols="OpenFlow13")

        info ( '*** Create links ***\n' )
        net.addLink( green2, s2 )
        net.addLink( blue2, s2 )

        info ( '*** Start network ***\n' )
        net.build()
        c1.start()

        s2.start( [c1] )
        net.start()

        #Making the switch listen for ovsdb controller
        s2.cmd('sh ovs-vsctl set-manager ptcp:6640')


        info ( '*** Run CLI ***\n' )

        CLI(net)

        info( '*** Stop network ***' )
        net.stop()
if __name__=='__main__':
        setLogLevel( 'info' )
        netTAR()

