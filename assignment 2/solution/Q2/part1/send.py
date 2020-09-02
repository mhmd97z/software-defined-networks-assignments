#!/usr/bin/env python
# Importing
import sys
from time import sleep
import random
from scapy.all import sendp, send, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from scapy.fields import *

# Definition of class
class DedicatedBearerTunnel(Packet):
    name = "DedicatedBearerTunnel"
    fields_desc = [ShortField("uid", 0),ShortField("qos", 0)]

bind_layers(Ether, IP,type=0x4567)
bind_layers(IP,DedicatedBearerTunnel,proto=42) 

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
    Id = int(input("please choose between 1 and 2 as this host's Id"))
 
    Id2 = 3 - Id 
 
    src_ip = "10.0." + str(Id) + "." + str(Id) 
    dst_ip = "10.0." + str(Id2) + "." + str(Id2)
    iface = get_if()

    while True: 
	myMsg = raw_input("Please enter your message\n")
        
        pkt1 = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)

	pkt1 = pkt1 / IP(dst=dst_ip, src=src_ip,proto=42)/DedicatedBearerTunnel(uid=Id,qos=10)/TCP(dport=1234, sport=random.randint(49152,65535)) /myMsg  #uid is 2 when source is h2

        sendp(pkt1, iface=iface, verbose=True)

	print("msg sent")
        sleep(2)


if __name__ == '__main__':
    try:
    	main()

    except KeyboardInterrupt:
	sys.exit("An error occured")


