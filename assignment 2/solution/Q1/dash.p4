/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>


/* Value Definitions */
#define NUM_STAGES 4        // number of stages
#define STAGE_CAPACITY 16   // size of the table
#define WEIGHT_WIDTH 16     // size of weight feild in DASH probe packet
#define PORT_WIDTH 15       // size of port field in source routing packet
#define MAX_HOPS 5          // maximum number of 
/*------- ToDo: here you can write your value definitions -------*/


/* Constant values */
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_DASH = 0x4567;    // our convention for dash packets

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

/* Type Definition */
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<9>  egressSpec_t;
typedef bit<WEIGHT_WIDTH> weight_t;
typedef bit<WEIGHT_WIDTH> boundary_t;
typedef bit<PORT_WIDTH> port_t;
/*------- ToDo: here you can write your type definitions -------*/


/* Headers */
header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
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

header udp_t {
    bit<16> srcPort;
    bit<16> dstPort;
    bit<16> length_;
    bit<16> checksum;
}

header dash_t {
    weight_t weight;
}

header srcRoute_t {
    bit<1>    bos;
    port_t   port;
}

struct metadata {
    /*------- ToDo: here you can define your metadata -------*/
    
    bit<16>  hash; /* not sure about bit length*/
    bit<4>   flag; /* to show that packet isn't in switch 1 */
}

struct headers {
    ethernet_t              ethernet;
    srcRoute_t[MAX_HOPS]    srcRoutes;
    ipv4_t                  ipv4;
    udp_t                   udp;
    dash_t                  dash;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

/* Keep this unchanged */

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_DASH : parse_dash;
            TYPE_IPV4 : parse_ipv4;
            default   : accept;
        }
    }

    state parse_dash {
        packet.extract(hdr.dash);
        transition parse_srcRouting;
    }

    state parse_srcRouting {
        packet.extract(hdr.srcRoutes.next);
        transition select(hdr.srcRoutes.last.bos) {
            1       : parse_ipv4;
            default : parse_srcRouting;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w17: parse_udp;
            default: accept;
        }
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }

}

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

/* Keep this unchanged */

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {

    /* Registers */ /*to write final metric of paths on them  */
    register<boundary_t>(STAGE_CAPACITY) boundary_stage1_reg;
    register<boundary_t>(STAGE_CAPACITY) boundary_stage2_reg;
    register<boundary_t>(STAGE_CAPACITY) boundary_stage3_reg;
    register<boundary_t>(STAGE_CAPACITY) boundary_stage4_reg;
    /*------- ToDo: here you can define your registers -------*/
  
    /* This action will drop packets */
    action drop() {
        mark_to_drop(standard_metadata);
    }
    /*------- ToDo: here you can define your actions and tables -------*/
    action relay_forward(egressSpec_t port) {
       standard_metadata.egress_spec = port;


    }

    action srcRoute_nhop() {
        standard_metadata.egress_spec = (bit<9>)hdr.srcRoutes[0].port;
        hdr.srcRoutes.pop_front(1);
    }

    action update_ttl(){
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    } 
    
    action srcRoute_finish() {
        hdr.ethernet.etherType = TYPE_IPV4;
    }
    action write_data() {
        boundary_t w1;
        boundary_t w2;
        boundary_t w3;
        boundary_t w4;

        boundary_stage1_reg.read(w1,0);
        boundary_stage2_reg.read(w2,0);
        boundary_stage3_reg.read(w3,0);
        boundary_stage4_reg.read(w4,0);


        if (standard_metadata.ingress_port == 1) {
            
            w1 = hdr.dash.weight;

         }       
        else if (standard_metadata.ingress_port == 2) {
            
            w2 = hdr.dash.weight;

          }       
        else if (standard_metadata.ingress_port == 3) {
          
            w3= hdr.dash.weight;

          } 
        else if (standard_metadata.ingress_port == 4) {
           
            w4 =  hdr.dash.weight;
          } 
        
        boundary_stage1_reg.write(0,w1);
        boundary_stage2_reg.write(0,w2);
        boundary_stage3_reg.write(0,w3);
        boundary_stage4_reg.write(0,w4);

    }
    
   action make_decision() {
            hash(
                meta.hash,
                HashAlgorithm.crc16,
                (bit<16>)0,
                {hdr.ipv4.srcAddr, hdr.ipv4.dstAddr},
                (bit<16>)30);
                boundary_t stg1;
                boundary_t stg2;
                boundary_t stg3;
                boundary_t stg4;
                boundary_stage1_reg.read(stg1,0);
                boundary_stage2_reg.read(stg2,0); 
                boundary_stage3_reg.read(stg3,0);
                boundary_stage4_reg.read(stg4,0);
                if (meta.hash <= ( stg1 +1)) { 
                    standard_metadata.egress_spec = 1;
                     
                
                } 
                else if ( meta.hash <= ( stg2 +1 ) ) {
                   standard_metadata.egress_spec = 2;
                   
                   
                } 
                else if ( meta.hash <= (stg3 + 1)) {
                   standard_metadata.egress_spec = 3;
                  
                   
                }
                else if ( meta.hash <= (stg4+1)) {
                   standard_metadata.egress_spec = 4;
                   
                   
                }  

     }
    
    table take_hash {

       key = {
            standard_metadata.ingress_port: exact;
        }
       actions = {

           make_decision;
           NoAction;

      }
      
      size = 1024;
      default_action = NoAction();

    } 
      
    
    
    table know_path {
       key = {
            standard_metadata.ingress_port: exact;
        }
       actions = {

           write_data;
           NoAction;

      }
      
      size = 1024;
      default_action = NoAction();

    } 

    table relay {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            
            relay_forward;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    } 

    /*------- ToDo: here you can define your control flow -------*/
    apply {

        if (hdr.dash.isValid()){            // check whether this is DASH packet
            /*------- ToDo: here you can define your control flow for DASH probe packets -------*/
            know_path.apply();
            if (hdr.srcRoutes[0].isValid()){
                if (hdr.srcRoutes[0].bos == 1){
                     srcRoute_finish();
                }
            srcRoute_nhop();
            if (hdr.ipv4.isValid()){
                update_ttl();
                }
        }else{
            drop();
         } 

        }else if (hdr.ipv4.isValid()){      // check whether this is data packet
            /*------- ToDo: here you can define your control flow for ordinary Data probe packets -------*/
            
                /*use this Hash function:*/
                take_hash.apply();
                relay.apply();
            
    }
} /* end apply*/
}
/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

/* Keep this unchanged */

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply { }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

/* Keep this unchanged */

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
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

/* Keep this unchanged */

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.dash);
        packet.emit(hdr.srcRoutes);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.udp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

/* Keep this unchanged */

//switch architecture
V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
