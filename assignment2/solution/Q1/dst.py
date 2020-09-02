#!/usr/bin/env python
# Importing 
import sys
from time import sleep

from scapy.all import sendp, send, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet
from scapy.all import Ether, IP, UDP
from scapy.fields import *

# Definition of class
class Dash(Packet):
    name = "Dash"
    fields_desc = [ShortField("weight", 0)]


class SourceRoute(Packet):
    fields_desc = [BitField("bos", 0, 1),
                   BitField("port", 0, 15)]


# Binding layers
bind_layers(Ether, Dash, type=0x4567)
bind_layers(Dash, SourceRoute)
bind_layers(SourceRoute, SourceRoute, bos=0)
bind_layers(SourceRoute, IP, bos=1)

# Definition of functions 
def get_if():
    iface = None
    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface


def main():

    iface = get_if()
    src_ip = "10.0.1.2"
    dst_ip = "10.0.1.1"

    RoundsList = [
        [[30, [1, 1, 5]], [0, [2, 1, 5]], [0, [3, 1, 5]], [0, [4, 1, 5]]],
        [[0, [1, 1, 5]], [30, [2, 1, 5]], [0, [3, 1, 5]], [0, [4, 1, 5]]],
        [[0, [1, 1, 5]], [0, [2, 1, 5]], [30, [3, 1, 5]], [0, [4, 1, 5]]],
        [[0, [1, 1, 5]], [0, [2, 1, 5]], [0, [3, 1, 5]], [30, [4, 1, 5]]]
        ]

    for InfoCounter in RoundsList:
        first_packet_data = InfoCounter[0]
        pkt1 = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)
        pkt1 = pkt1 / Dash(weight=first_packet_data[0])
        pkt1 = pkt1 / SourceRoute(bos=0, port=first_packet_data[1][0])
        pkt1 = pkt1 / SourceRoute(bos=0, port=first_packet_data[1][1])
        pkt1 = pkt1 / SourceRoute(bos=1, port=first_packet_data[1][2])
        pkt1 = pkt1 / IP(dst=dst_ip, src=src_ip) / UDP(dport=4321, sport=1234) / ''
        sendp(pkt1, iface=iface, verbose=False)
        time.sleep(0.1)

        second_packet_data = InfoCounter[1]
        pkt2 = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)
        pkt2 = pkt2 / Dash(weight=second_packet_data[0])
        pkt2 = pkt2 / SourceRoute(bos=0, port=second_packet_data[1][0])
        pkt2 = pkt2 / SourceRoute(bos=0, port=second_packet_data[1][1])
        pkt2 = pkt2 / SourceRoute(bos=1, port=second_packet_data[1][2])
        pkt2 = pkt2 / IP(dst=dst_ip, src=src_ip) / UDP(dport=4321, sport=1234) / ''
        sendp(pkt2, iface=iface, verbose=False)
        time.sleep(0.1)

        third_packet_data = InfoCounter[2]
        pkt3 = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)
        pkt3 = pkt3 / Dash(weight=third_packet_data[0])
        pkt3 = pkt3 / SourceRoute(bos=0, port=third_packet_data[1][0])
        pkt3 = pkt3 / SourceRoute(bos=0, port=third_packet_data[1][1])
        pkt3 = pkt3 / SourceRoute(bos=1, port=third_packet_data[1][2])
        pkt3 = pkt3 / IP(dst=dst_ip, src=src_ip) / UDP(dport=4321, sport=1234) / ''
        sendp(pkt3, iface=iface, verbose=False)
        time.sleep(0.1)

        forth_packet_data = InfoCounter[3]
        pkt4 = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)
        pkt4 = pkt4 / Dash(weight=forth_packet_data[0])
        pkt4 = pkt4 / SourceRoute(bos=0, port=forth_packet_data[1][0])
        pkt4 = pkt4 / SourceRoute(bos=0, port=forth_packet_data[1][1])
        pkt4 = pkt4 / SourceRoute(bos=1, port=forth_packet_data[1][2])
        pkt4 = pkt4 / IP(dst=dst_ip, src=src_ip) / UDP(dport=4321, sport=1234) / ''
        sendp(pkt4, iface=iface, verbose=False)
        sleep(12)


if __name__ == '__main__':
    main()
