#!/usr/bin/env python
# Importing
import sys
from time import sleep
import random
import json
from scapy.all import sniff, sendp, send, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, IPOption
from scapy.all import Ether, TCP, IP, UDP, Raw
from scapy.fields import *
from scapy.layers.inet import _IPOption_HDR
import time, threading 

# Definition of thread
ThreadEvent = threading.Event()

# Global variables' definition
src_ip = ""
dst_ip = "10.0.7.7"

Tunnel_Id = 1

IDisSet = 0

host_id = 0

# class definition 
class DedicatedBearerTunnel(Packet):
    name = "DedicatedBearerTunnel"
    fields_desc = [ShortField("uid", 0),ShortField("qos", 0)]

# binding layers
bind_layers(Ether, IP,type=0x4567)
bind_layers(IP,DedicatedBearerTunnel,proto=42)
bind_layers(DedicatedBearerTunnel,TCP)

# functions' definition
def sendAnswer(mymsg, msgType, Id):
    global src_ip
    global dst_ip

    print("I gonna send " + mymsg)
    
    iface = get_if()

    print("going to send msg")

    if(msgType == "TCP"):
         pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff',type=0x4567)
         pkt = pkt/ IP(src = src_ip, dst = dst_ip) / TCP(dport=1234,sport=random.randint(49152,65535))/mymsg
	 pkt.show2()
         sendp(pkt, iface=iface, verbose=False)
         print("msg sent ...")

    elif(msgType == "DedicatedBearer"):
	  with open('idvalues.txt') as json_file:
    	  	data = json.load(json_file)
	
	  
	  print("data read is : " + str(data))
	  
	  pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff',type=0x4567)
	  pkt = pkt / IP(dst=dst_ip, src=src_ip)/DedicatedBearerTunnel(uid=Id,qos=(int)(host_id-1))/TCP(dport=1234, sport=random.randint(49152,65535)) /mymsg
	  pkt.show2()
          sendp(pkt, iface=iface, verbose=False)
	  print("msg sent ...")

    else:
	  print("Message type is wrong")


def handle_pkt(pkt):
    global Tunnel_Id
    global IDisSet

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
	
	    if(rcv_arr0 == "Hi"):
	        print("I've received answer message")
		sleep(5)

		Id = int(rcv_arr1[-4:])
		Tunnel_Id = Id
		
		print("Entering message send status\n")
		IDisSet = 1
		while True:
			myMsg = raw_input("If you've run Conroller code, Please give me message\n to send it using Tunnel\n")
			print("message is " + myMsg)
        		sendAnswer(myMsg, "DedicatedBearer", Id)

    except IndexError:
	print("got a message")

    sys.stdout.flush()


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

def mySniff(iface,prn):
    sniff(iface = iface, prn = lambda x: handle_pkt(x))

def main():
    global src_ip
    global IDisSet
    global host_id

    host_id = str(int(input("Hi, Please give me host id (1-4):\n")))
    
    src_ip = "10.0." + host_id + "." + host_id 

    mymsg = "hello," + src_ip
    iface = get_if()


    sendAnswer(mymsg, "TCP", 0)

    sleep(2)

    print("Going to receive msg")
	 
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    # sys.stdout.flush()

    t = threading.Thread(target=mySniff, args=(iface,lambda x: handle_pkt(x),))
    t.start()
    ThreadEvent.set()
    t.join(2)

    sys.stdout.flush()

if __name__ == '__main__':
    try:
    	main()

    except KeyboardInterrupt:
	sys.exit("An error occured")


