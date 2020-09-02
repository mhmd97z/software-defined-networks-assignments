#!/usr/bin/env python
# Importing ...
import sys
from time import sleep
import random
from scapy.all import sniff, sendp, send, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, IPOption
from scapy.all import Ether, TCP, IP, UDP, Raw
from scapy.fields import *
from scapy.layers.inet import _IPOption_HDR
import time, threading 

# Definitio of GLobal variables 
src_ip = "10.0.1.1"
dst_ip = "10.0.2.2"

# Definition of Thread
ThreadEvent = threading.Event()

# Definition of class
class DedicatedBearerTunnel(Packet):
    name = "DedicatedBearerTunnel"
    fields_desc = [ShortField("uid", 0),ShortField("qos", 0)]

bind_layers(Ether, IP,type=0x4567)
bind_layers(IP,DedicatedBearerTunnel,proto=42) 
bind_layers(DedicatedBearerTunnel,TCP)

# Definition of functions 
def sendAnswer(mymsg, msgType, Id, dst_ip, src_ip):
    # This functio is for sending messages 
    print("I gonna send " + mymsg)
    # dst_ip = "10.0.2.2"
    # src_ip = "10.0.1.1"
    
    iface = get_if()

    if(msgType == "TCP"):
         pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
         pkt = pkt/ IP(src = src_ip, dst = dst_ip) / TCP(dport=1234,sport=random.randint(49152,65535))/mymsg
	 pkt.show2()
         sendp(pkt, iface=iface, verbose=False)
         print("msg sent ...")

    elif(msgType == "DedicatedBearer"):
	  pkt = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)
	  pkt = pkt / IP(dst=dst_ip, src=src_ip)/DedicatedBearerTunnel(uid=Id,qos=10)/TCP(dport=1234, sport=random.randint(49152,65535)) / ''  
	  pkt.show2()
          sendp(pkt, iface=iface, verbose=False)
	  print("msg sent ...")

    else:
	  print("Message type is wrong")


def handle_pkt(pkt):
    global src_ip
    global dst_ip
    # This function is for receiving messages 
    print "I got a packet, packet is:\n"
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
	        print("I've received answer message\n")
		sleep(5)
	        print("Now , I will send packet via dedicated bearer\n")
		print("received hash is :" + str(rcv_arr1))

		Id = int(rcv_arr1[-4:])
		myMsg = "Tunnel Created"
        	sendAnswer(myMsg, "DedicatedBearer", Id, dst_ip, src_ip)

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
    # This function is for sniffing 
    sniff(iface = iface, prn = lambda x: handle_pkt(x))

def main():
    global src_ip
    global dst_ip

    Id = int(input("please enter uid(1 for user h1 and 2 for user h2):"))

    Id2 = 3 - Id
    src_ip = "10.0." + str(Id) + "." + str(Id)
    dst_ip = "10.0." + str(Id2) + "." + str(Id2) 

    mymsg = "hello," + src_ip
    
    iface = get_if()

    sendAnswer(mymsg, "TCP", 0, dst_ip, src_ip)

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
    	print("Warning: An exception Occured")
    	sys.exit("An error occured")

