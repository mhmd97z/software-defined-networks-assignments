#!/usr/bin/env python
# Importing 
import sys
import struct
import os
import time, threading 
import random 
import json
from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr, send, bind_layers
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, TCP, UDP, Raw, Ether
from scapy.layers.inet import _IPOption_HDR
from time import sleep

# Definition of thread event
ThreadEvent = threading.Event()

# global varaibles' definition
src_ip = "10.0.7.7"

IDs_list = {}

hostCounter = 0

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
bind_layers(IP,DedicatedBearerTunnel,proto=42) 
bind_layers(DedicatedBearerTunnel,TCP)

def handle_pkt(pkt):
    global IDs_list
    global hostCounter

    print "I got a packet"
    pkt.show2()

    sender_ip = str(pkt[IP].src)
    print("I've received a packet from :"+ sender_ip)

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

		rcv_IPpart = str(pkt[IP].src)
		rcv_hostId = rcv_IPpart[-1]

		hashValue = str(hash(str(rcv_arr1)))

		rcvId = int(hashValue[-4:])

		IDs_list[rcv_hostId] = rcvId
		
		if(len(IDs_list) == 4):
			with open('idvalues.txt','w') as json_file:
				json.dump(IDs_list, json_file)
			
		print("Sending answer message")
	        myMsg = "Hi," + str(hashValue)
	        sendAnswer(myMsg, "TCP", 0, sender_ip)
	
	    if(len(rcv_msg) == 0):
		print("DedicatedBearerTunnel Message received inside try part")

    except:
	print("DedicatedBearerTunnel Message received")

    sys.stdout.flush()

def sendAnswer(mymsg, msgType, Id, dst_ip):
    print("I gonna send " + mymsg)
    
    iface = get_if()

    sleep(5)
    print("going to send msg")

    if(msgType == "TCP"):
         pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
         pkt = pkt/ IP(src = src_ip, dst = dst_ip) / TCP(dport=1234,sport=random.randint(49152,65535))/mymsg
	 pkt.show2()
         sendp(pkt, iface=iface, verbose=False)

    elif(msgType == "DedicatedBearer"):
	  pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)
	  pkt = pkt / IP(dst=dst_ip, src=src_ip)/DedicatedBearerTunnel(uid=Id,qos=10)/TCP(dport=1234, sport=random.randint(49152,65535)) / ''
	  pkt.show2()
          sendp(pkt, iface=iface, verbose=False)

    else:
	  print("Message type is wrong")



def mySniff(iface,prn):
    sniff(iface = iface, prn = lambda x: handle_pkt(x))
    
def main():
    print("Please wait, deleting json data remained from last execution\n")
    
    if os.path.exists("idvalues.txt"):
    	os.remove("idvalues.txt")
    else:
	print("the id values text file does not exist\n")

	
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    sys.stdout.flush()

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
	sys.exit("An error occured")

