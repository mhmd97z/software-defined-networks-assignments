#!/usr/bin/env python
# Importing 
import sys
from time import sleep
import random
import json
from scapy.all import sniff, sendp, send, get_if_list, get_if_hwaddr, bind_layers
from scapy.all import Packet, IPOption
from scapy.all import Ether, IP, UDP,TCP,Raw
from scapy.fields import *
from scapy.layers.inet import _IPOption_HDR
import time, threading 

# Definition of Thread
ThreadEvent = threading.Event()

# global variables' definition 
rcv_ip = "10.0.7.7"

Tunnel_Id = 1

IDisSet = 0

host_id = 0

# Definition of class
class DedicatedBearerTunnel(Packet):
    name = "DedicatedBearerTunnel"
    fields_desc = [ShortField("uid", 0),ShortField("qos", 0)]

# Binding layers
bind_layers(Ether, IP,type=0x4567)
bind_layers(IP,DedicatedBearerTunnel,proto=42) #proto=42 is our defined tunneling protocol after IP
bind_layers(DedicatedBearerTunnel,TCP) #proto=42 is our defined tunneling protocol after IP

# Definition of functions 
def handle_pkt(pkt):
    global Tunnel_Id
    global IDisSet

    print "I got a packet"
    pkt.show2()
    
    try: 
	    rcv_msg = str(pkt[Raw])
	    print("received raw is(Fafy):{}".format(rcv_msg))
	
	    rcv_arr = rcv_msg.split(",")

	    rcv_arr0 = rcv_arr[0]
	
	    if(len(rcv_arr) > 1):
	    	rcv_arr1 = rcv_arr[1]

	    else:
		print("I've received a message which doesn't have IP address")
	
	    if(rcv_arr0 == "Hi"):
	        print("I've received answer message")
                src_ip = str(pkt[IP].dst)
		sleep(5)
	        print("I wanna send message with dedicated bearer ")
		print(str(rcv_arr1))

		Id = int(rcv_arr1[-4:])
		Tunnel_Id = Id
		IDisSet = 1
		
		print("Now please run mycontroller for Tunnel mode\n")

		print("After you ran it, please give me message to send it\n")
	
		while True:
			myMsg = raw_input("Give me message:\n")
        		sendAnswer("DedicatedBearer",src_ip,Id, myMsg)

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

def sendAnswer(msg_type,src_ip,Id,myMsg):
    global rcv_ip
    global host_id

    QoS=0;

    iface = get_if()

    if msg_type == "TCP":
       message = "hello," + str(src_ip) 
       pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff',type=0x4567)
       pkt = pkt / IP(src=src_ip,dst=rcv_ip) / TCP(dport=1234, sport=random.randint(49152,65535)) /message
       pkt.show2()
       sendp(pkt, iface=iface, verbose=False)

    elif msg_type == "DedicatedBearer":
       #read your qos value from file
       Qos = host_id - 1       
              
       pkt1 = Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff', type=0x4567)
       pkt1 = pkt1 / IP(dst=rcv_ip, src=src_ip)/DedicatedBearerTunnel(uid=Id,qos=QoS)/TCP(dport=1234, sport=random.randint(49152,65535)) / myMsg     
       pkt1.show2()
       sendp(pkt1, iface=iface, verbose=False)
       
    
def main():
    host_id = int(input("please give me host number ( 1 to 4)"))

    ip = "10.0." + str(host_id) + "." + str(host_id)

    sendAnswer("TCP",ip,0,'')
	 
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    
    t = threading.Thread(target=mySniff, args=(iface,lambda x: handle_pkt(x),))
    t.start()
    ThreadEvent.set()
    t.join(2)

    sys.stdout.flush()  

if __name__ == '__main__':
    try:
    	main()
    except KeyboardInterrupt:
    	sys.exit("An error occured\n")




