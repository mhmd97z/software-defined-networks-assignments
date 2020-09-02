/* Indlucding libraries */
#include <core.p4>
#include <v1model.p4>

/* const variables definition*/
const bit<8> TYPE_DedicatedBearerTunnel = 42;
const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/
/* typedefs definition*/
typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

/* headers' definition*/
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header DedicatedBearerTunnel_t {
    bit<16> uid;
    bit<16> qos;

}
header tcp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<32> seqNo;
    bit<32> ackNo;
    bit<4>  dataOffset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgentPtr;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

/* structs' definition*/
struct metadata {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
    DedicatedBearerTunnel_t   DedicatedBearerTunnel;
    ipv4_t       ipv4;
    tcp_t        tcp;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition parse_ipv4;
    }
    


    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_DedicatedBearerTunnel: parse_DedicatedBearerTunnel;
            default: accept;
       }
    }

    state parse_DedicatedBearerTunnel {
        packet.extract(hdr.DedicatedBearerTunnel);
        transition parse_tcp;
            
    }
   state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    counter(4, CounterType.packets_and_bytes) Idcounter;
    counter(8, CounterType.packets_and_bytes) QoScounter;


    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }
    action uid_forward(egressSpec_t port) {
           standard_metadata.egress_spec = port;

    }
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    table DedicatedBearerTunnel_exact {
        key = {
            hdr.DedicatedBearerTunnel.uid: exact;
        }
        actions = {
            uid_forward;
            drop;
        }
        size = 1024;
        default_action = drop();
    }

    apply {
        if (hdr.ipv4.isValid() && !hdr.DedicatedBearerTunnel.isValid()) {
            // Process only non-tunneled IPv4 packets
            ipv4_lpm.apply();
        } 

        if (hdr.DedicatedBearerTunnel.isValid()) {
            // process tunneled packets
            if (hdr.DedicatedBearerTunnel.uid == 7169) {
               Idcounter.count(0);
            }
			
            if (hdr.DedicatedBearerTunnel.uid == 7165) {
               Idcounter.count(1);
            }
			
            if (hdr.DedicatedBearerTunnel.uid == 7153) {
               Idcounter.count(2);
            }
			
            if (hdr.DedicatedBearerTunnel.uid == 7053) {
               Idcounter.count(3);
            }
			
            if (hdr.DedicatedBearerTunnel.qos == 0) {
            standard_metadata.priority=(bit<3>)0;
            QoScounter.count(0);
            }
			
            if (hdr.DedicatedBearerTunnel.qos == 1) {
            standard_metadata.priority=(bit<3>)1; 
            QoScounter.count(1);
            }
			
            if (hdr.DedicatedBearerTunnel.qos == 2) {
            standard_metadata.priority=(bit<3>)2;
            QoScounter.count(2);
            }
			
            if (hdr.DedicatedBearerTunnel.qos == 3) {
            standard_metadata.priority=(bit<3>)3;
            QoScounter.count(3);
            }
					
            DedicatedBearerTunnel_exact.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
	update_checksum(
	    hdr.ipv4.isValid(),
            { hdr.ipv4.version,
	      hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.DedicatedBearerTunnel);
        packet.emit(hdr.tcp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;