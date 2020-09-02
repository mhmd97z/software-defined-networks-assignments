from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def netTAR():
    net = Mininet(controller=RemoteController, switch=OVSKernelSwitch)
    c1 = net.addController('c1', controller=RemoteController,
ip="100.0.0.2", port=6653)

    h1 = net.addHost( 'h1', ip='10.0.1.1' )
    h2 = net.addHost( 'h2', ip='10.0.2.1' )

    #===============================
    #Input parameters, to change, set them here.
    n=4 #number of switches 
    s=1 #number of the switch connected to h1
    d=4 #number of the swtich connected to h2
    #===============================

    switches = []
    for i in range(1, n+1):
        #Here we create n switches and store them in switches for further use
        switches.append(net.addSwitch( 's'+str(i) , protocols="OpenFlow13"))

    #Here, we connect all the switches together, in fact, here all the switches are interconnected, and connection weights, that also could be 0s, are implemented in the flow_adder file.
    for i in range(len(switches)):
        for j in range(i, len(switches)):
            if (i != j):
                #Please note that the ports are adjusted in a way that considering any switch, port i is connected to switch i.
                net.addLink( switches[i], switches[j], j+1, i+1 )

    #Here we connect h1 to switch s and h2 to switch d
    #Note that for source and destination switches, their s and d ports are connected to their corresponding hosts.
    net.addLink(h1, switches[s-1], 0, s)
    net.addLink(h2, switches[d-1], 0, d)

    net.build()
    c1.start()

    for switch in switches:
        switch.start( [c1] )

    net.start()


    CLI( net )
    net.stop()

if __name__ == '__main__':
     setLogLevel( 'info' )
     netTAR()

