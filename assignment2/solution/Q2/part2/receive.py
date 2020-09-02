#!/usr/bin/env python
# Importing 
import sys
import struct
import os
import time, threading 
import random 
from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, send, bind_layers
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, TCP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
from time import sleep

# Global variables definition
src_ip = "10.0.2.2"
dst_ip = "10.0.1.1"

# Thread's definition
ThreadEvent = threading.Event()

# class definition
class DedicatedBearerTunnel(Packet):
    name = "DedicatedBearerTunnel"
    fields_desc = [ShortField("uid", 0),ShortField("qos", 0)]

# functions' definition 
def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

# binding layers 
bind_layers(Ether, IP,type=0x4567)
bind_layers(IP,DedicatedBearerTunnel,proto=42) #proto=42 is our defined tunneling protocol after IP
bind_layers(DedicatedBearerTunnel,TCP) 

def handle_pkt(pkt):
    global src_ip
    global dst_ip 

    print "I got a packet"
    pkt.show2()
    try: 
	    rcv_msg = str(pkt[Raw])
	
	    rcv_arr = rcv_msg.split(",")
	    
	    rcv_arr0 = rcv_arr[0]
	
	    if(len(rcv_arr) > 1):
	    	rcv_arr1 = rcv_arr[1]
	    else:
		print("I've received a message which doesn't have IP address")
	    
	    if(rcv_arr0 == "hello"):
	        print("I've received hello message")
	
	        sleep(5)
	
	        print("I wanna send answer message")
		print(str(rcv_arr1))
	        myMsg = "Hi," + str(hash(str(rcv_arr1)))
	        sendAnswer(myMsg, "TCP", 0, dst_ip, src_ip)
	
	    if(rcv_msg == "answer"):
        	print("I've received answer message")
    except IndexError:
	print("Tunnel Message received")

    sys.stdout.flush()

def sendAnswer(mymsg, msgType, Id, dst_ip, src_ip):
    print("I gonna send " + mymsg)
    #src_ip = "10.0.2.2"
    #dst_ip = "10.0.1.1"
    
    iface = get_if()

    sleep(5)

    if(msgType == "TCP"):
         pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
         pkt = pkt/ IP(src = src_ip, dst = dst_ip) / TCP(dport=1234,sport=random.randint(49152,65535))/mymsg
	 pkt.show2()
         sendp(pkt, iface=iface, verbose=False)

    elif(msgType == "dBearer"):
	  pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)
	  pkt = pkt / IP(dst=dst_ip, src=src_ip,proto=42)/DedicatedBearerTunnel(uid=Id,qos=10)
	  pkt.show2()
          sendp(pkt, iface=iface, verbose=False)

    else:
	  print("Message type is wrong")



def mySniff(iface,prn):
    sniff(iface = iface, prn = lambda x: handle_pkt(x))
    
def main():
    global src_ip
    global dst_ip

    Id = int(input("please enter uid(1 for user h1 and 2 for user h2):"))

    Id2 = 3 - Id
    src_ip = "10.0." + str(Id) + "." + str(Id)
    dst_ip = "10.0." + str(Id2) + "." + str(Id2) 

    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    # sys.stdout.flush()

    t = threading.Thread(target=mySniff, args=(iface,lambda x: handle_pkt(x),))
    t.start()
    ThreadEvent.set()
    t.join(2)
    

    print("after sniff")

    return 0

if __name__ == '__main__':
    try:
    	main()
    except: 
	sys.exit("An error Occured")


