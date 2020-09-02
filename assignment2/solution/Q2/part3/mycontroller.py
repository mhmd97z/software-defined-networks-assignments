#!/usr/bin/env python2
# Importing 
import argparse
import grpc
import os
import sys
from time import sleep
import json

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 '../../utils/'))
import p4runtime_lib.bmv2
from p4runtime_lib.switch import ShutdownAllSwitchConnections
import p4runtime_lib.helper


# Functions' Definition
def writeTunnelRules(p4info_helper, ingress_sw, Host_ID, Port_value):

    # 1) Tunnel Ingress Rule
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.DedicatedBearerTunnel_exact",
        match_fields={
            "hdr.DedicatedBearerTunnel.uid": Host_ID
        },
        action_name="MyIngress.uid_forward",
        action_params={
            "port": Port_value
        })
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name


def writeIPRules(p4info_helper, ingress_sw,dst_eth_addr, dst_ip_addr, Port_value):
    
    
    # 1) add ip forwarding table
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": (dst_ip_addr, 32)
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            
            "dstAddr":dst_eth_addr,
            "port": Port_value
        })
    
    ingress_sw.WriteTableEntry(table_entry)
    print "Installed ingress tunnel rule on %s" % ingress_sw.name


def readTableRules(p4info_helper, sw):
    """
    Reads the table entries from all tables on the switch.

    :param p4info_helper: the P4Info helper
    :param sw: the switch connection
    """
    print '\n----- Reading tables rules for %s -----' % sw.name
    for response in sw.ReadTableEntries():
        for entity in response.entities:
            entry = entity.table_entry

            table_name = p4info_helper.get_tables_name(entry.table_id)
            print '%s: ' % table_name,
            for m in entry.match:
                print p4info_helper.get_match_field_name(table_name, m.field_id),
                print '%r' % (p4info_helper.get_match_field_value(m),),
            action = entry.action.action
            action_name = p4info_helper.get_actions_name(action.action_id)
            print '->', action_name,
            for p in action.params:
                print p4info_helper.get_action_param_name(action_name, p.param_id),
                print '%r' % p.value,
            print

def printCounter(p4info_helper, sw, counter_name, index):
    """
    Reads the specified counter at the specified index from the switch. In our
    program, the index is the tunnel ID. If the index is 0, it will return all
    values from the counter.

    :param p4info_helper: the P4Info helper
    :param sw:  the switch connection
    :param counter_name: the name of the counter from the P4 program
    :param index: the counter index (in our case, the tunnel ID)
    """
    for response in sw.ReadCounters(p4info_helper.get_counters_id(counter_name), index):
        for entity in response.entities:
            counter = entity.counter_entry
            print "%s %s %d: %d packets (%d bytes)" % (
                sw.name, counter_name, index,
                counter.data.packet_count, counter.data.byte_count
            )

def printGrpcError(e):
    print "gRPC Error:", e.details(),
    status_code = e.code()
    print "(%s)" % status_code.name,
    traceback = sys.exc_info()[2]
    print "[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno)

def main(p4info_file_path, bmv2_file_path):

    print("Hi, This is controller talking to you!\n")
    selId = (int)(raw_input("1. If you want to add Initialization flows (IP rules) please press '1' \n2. If you want to add Tunnel flows ( you should run codes before and idvalues.txt should be created automatically), press '2'\n"))

    if(selId == 1):
	WritingRulesType = "IPRules"
    elif(selId == 2):
	WritingRulesType = "TunnelRules"
    else:
	print("given number is invalid, please try again\n")
	return 0
    
    # Reading json file
    HostIDList = [] 
 
    with open('idvalues.txt') as json_file:
    	data = json.load(json_file)

    for p in range(4):
	HostIDList.append(data[str(p+1)])

    print("Loaded data is : " + str(HostIDList))

    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1 and s2;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')
        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s4-p4runtime-requests.txt')
        s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
            proto_dump_file='logs/s5-p4runtime-requests.txt')
        s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s6',
            address='127.0.0.1:50056',
            device_id=5,
            proto_dump_file='logs/s6-p4runtime-requests.txt')
        s7 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s7',
            address='127.0.0.1:50057',
            device_id=6,
            proto_dump_file='logs/s7-p4runtime-requests.txt')

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
	s3.MasterArbitrationUpdate()
	s4.MasterArbitrationUpdate()
	s5.MasterArbitrationUpdate()
	s6.MasterArbitrationUpdate()
	s7.MasterArbitrationUpdate()

        # Install the P4 program on the switches
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s1"
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s2"
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s3"
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s4"
        s5.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s5"
        s6.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s6"
        s7.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print "Installed P4 Program using SetForwardingPipelineConfig on s7" 


	if(WritingRulesType == "TunnelRules"):
		numOfHosts = 4
		for hostCounter in range(numOfHosts):
			Host_ID = (int)(HostIDList[hostCounter])
			if(hostCounter == 0):
				writeTunnelRules(p4info_helper, ingress_sw=s1, Host_ID=Host_ID, Port_value= 2)
				writeTunnelRules(p4info_helper, ingress_sw=s5, Host_ID=Host_ID, Port_value= 3)			

			if(hostCounter == 1):
				writeTunnelRules(p4info_helper, ingress_sw=s2, Host_ID=Host_ID, Port_value= 2)
				writeTunnelRules(p4info_helper, ingress_sw=s5, Host_ID=Host_ID, Port_value= 3)

			if(hostCounter == 2):
				writeTunnelRules(p4info_helper, ingress_sw=s3, Host_ID=Host_ID, Port_value= 2)
				writeTunnelRules(p4info_helper, ingress_sw=s6, Host_ID=Host_ID, Port_value= 3)

			if(hostCounter == 3):
				writeTunnelRules(p4info_helper, ingress_sw=s4, Host_ID=Host_ID, Port_value= 2)
				writeTunnelRules(p4info_helper, ingress_sw=s6, Host_ID=Host_ID, Port_value= 3)

			writeTunnelRules(p4info_helper, ingress_sw=s7, Host_ID=Host_ID, Port_value= 3)
			
			
			hostCounter = hostCounter + 1

	elif(WritingRulesType == "IPRules"):
	     writeIPRules(p4info_helper, ingress_sw=s5,dst_eth_addr="08:00:00:00:01:00", dst_ip_addr="10.0.1.1", Port_value=1)
	     writeIPRules(p4info_helper, ingress_sw=s1,dst_eth_addr="08:00:00:00:11:11", dst_ip_addr="10.0.1.1", Port_value=1)
 	     writeIPRules(p4info_helper, ingress_sw=s7,dst_eth_addr="08:00:00:00:05:00", dst_ip_addr="10.0.1.1", Port_value=1)

	     writeIPRules(p4info_helper, ingress_sw=s2,dst_eth_addr="08:00:00:00:22:22", dst_ip_addr="10.0.2.2", Port_value=1)
	     writeIPRules(p4info_helper, ingress_sw=s5,dst_eth_addr="08:00:00:00:02:00", dst_ip_addr="10.0.2.2", Port_value=2)
	     writeIPRules(p4info_helper, ingress_sw=s7,dst_eth_addr="08:00:00:00:05:00", dst_ip_addr="10.0.2.2", Port_value=1)

         writeIPRules(p4info_helper, ingress_sw=s3,dst_eth_addr="08:00:00:00:33:33", dst_ip_addr="10.0.3.3", Port_value=1)	
         writeIPRules(p4info_helper, ingress_sw=s7,dst_eth_addr="08:00:00:00:06:00", dst_ip_addr="10.0.3.3", Port_value=2)
         writeIPRules(p4info_helper, ingress_sw=s6,dst_eth_addr="08:00:00:00:03:00", dst_ip_addr="10.0.3.3", Port_value=1)

         writeIPRules(p4info_helper, ingress_sw=s4,dst_eth_addr="08:00:00:00:44:44", dst_ip_addr="10.0.4.4", Port_value=1)
         writeIPRules(p4info_helper, ingress_sw=s6,dst_eth_addr="08:00:00:00:04:00", dst_ip_addr="10.0.4.4", Port_value=2)
         writeIPRules(p4info_helper, ingress_sw=s7,dst_eth_addr="08:00:00:00:06:00", dst_ip_addr="10.0.4.4", Port_value=2)

         writeIPRules(p4info_helper, ingress_sw=s1,dst_eth_addr="08:00:00:00:07:00", dst_ip_addr="10.0.7.7", Port_value=2)         
         writeIPRules(p4info_helper, ingress_sw=s2,dst_eth_addr="08:00:00:00:07:00", dst_ip_addr="10.0.7.7", Port_value=2)
         writeIPRules(p4info_helper, ingress_sw=s3,dst_eth_addr="08:00:00:00:07:00", dst_ip_addr="10.0.7.7", Port_value=2)
         writeIPRules(p4info_helper, ingress_sw=s4,dst_eth_addr="08:00:00:00:07:00", dst_ip_addr="10.0.7.7", Port_value=2)
         writeIPRules(p4info_helper, ingress_sw=s5,dst_eth_addr="08:00:00:00:07:00", dst_ip_addr="10.0.7.7", Port_value=3)
         writeIPRules(p4info_helper, ingress_sw=s6,dst_eth_addr="08:00:00:00:07:00", dst_ip_addr="10.0.7.7", Port_value=3)         
         writeIPRules(p4info_helper, ingress_sw=s7,dst_eth_addr="08:00:00:00:77:77", dst_ip_addr="10.0.7.7", Port_value=3)


        readTableRules(p4info_helper, s1)
        readTableRules(p4info_helper, s2)


    except KeyboardInterrupt:
        print " Shutting down."
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/part3.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/part3.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print "\np4info file not found: %s\nHave you run 'make'?" % args.p4info
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print "\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json
        parser.exit(1)
    main(args.p4info, args.bmv2_json)



