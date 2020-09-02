import requests
import json



#Because we have three kinds of flows (based on number of match and output action items) I've made three flow templates that I'll use to make flows.
table_0_flow = '''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<flow xmlns="urn:opendaylight:flow:inventory">
<table_id>0</table_id>
<id>{flow_id}</id>
<priority>100</priority>

<instructions>
    <instruction>
        <order>0</order>
        <apply-actions>
            <action>
                <order>0</order>
                <set-field>
                    <tunnel>
                        <tunnel-id>{tun_id}</tunnel-id>
                    </tunnel>
                </set-field>
            </action>
        </apply-actions>
    </instruction>
    <instruction>
        <order>1</order>
        <go-to-table>
            <table_id>1</table_id>
        </go-to-table>
    </instruction>
</instructions>

<match>
    <in-port>{in_port}</in-port>
</match>
</flow>
'''

table_0_flow_3 = '''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<flow xmlns="urn:opendaylight:flow:inventory">
<table_id>0</table_id>
<id>3</id>
<priority>10</priority>
<instructions>
    <instruction>
        <order>0</order>
        <go-to-table>
            <table_id>1</table_id>
        </go-to-table>
    </instruction>
</instructions>
<match>
</match>
</flow>
'''

table_1_flow = '''
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<flow xmlns="urn:opendaylight:flow:inventory">
<table_id>1</table_id>
<id>{flow_id}</id>
<instructions>
    <instruction>
        <order>0</order>
        <apply-actions>
            <action>
                <order>0</order>
                <output-action>
                    <output-node-connector>{output_port}</output-node-connector>
                </output-action>
            </action>
        </apply-actions>
    </instruction>
</instructions>

<match>
    <ethernet-match>
        <ethernet-type>
            <type>{eth_type}</type>
        </ethernet-type>
    </ethernet-match>
    <{prot}>{nw_dst}/32</{prot}>
    <tunnel>
        <tunnel-id>{tun_id}</tunnel-id>
    </tunnel>
</match>
</flow>
'''

#The base url that we use to send flows
b_url = "http://100.0.0.2:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:{s_id}/table/{table_id}/flow/{flow_id}"
#The base url of tables that I'll use to delete tables.
url = "http://100.0.0.2:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:{s_id}/table/{table_id}"

#First, I'll 
print(requests.delete(url.format(s_id=1,table_id=0), auth=("admin","admin")))
print(requests.delete(url.format(s_id=1,table_id=1), auth=("admin","admin")))
print(requests.delete(url.format(s_id=2,table_id=0), auth=("admin","admin")))
print(requests.delete(url.format(s_id=2,table_id=1), auth=("admin","admin")))



#table=0,in_port=1,actions=set_field:100->tun_id,resubmit(,1)
url = b_url.format(s_id=1, table_id=0, flow_id=1)
data = table_0_flow.format(flow_id=1, tun_id=100, in_port=1).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=0, flow_id=1)
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=0,in_port=2,actions=set_field:200->tun_id,resubmit(,1)
url = b_url.format(s_id=1, table_id=0, flow_id=2)
data = table_0_flow.format(flow_id=2, tun_id=200, in_port=2).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=0, flow_id=2)
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=0,actions=resubmit(,1)
url = b_url.format(s_id=1, table_id=0, flow_id=3)
data = table_0_flow_3.replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=0, flow_id=3)
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=1,tun_id=100,arp,nw_dst=10.0.0.1,actions=output:1
url = b_url.format(s_id=1, table_id=1, flow_id=1)
data = table_1_flow.format(flow_id=1, output_port=1, eth_type=2054, prot='arp-target-transport-address', nw_dst='10.0.0.1', tun_id=100).replace('\n','')

print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=1, flow_id=1)
data = table_1_flow.format(flow_id=1, output_port=1, eth_type=2054, prot='arp-target-transport-address', nw_dst='10.0.0.2', tun_id=100).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=1,tun_id=200,arp,nw_dst=10.0.0.1,actions=output:2
url = b_url.format(s_id=1, table_id=1, flow_id=2)
data = table_1_flow.format(flow_id=2, output_port=2, eth_type=2054, prot='arp-target-transport-address', nw_dst='10.0.0.1', tun_id=200).replace('\n','')

print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=1, flow_id=2)
data = table_1_flow.format(flow_id=2, output_port=2, eth_type=2054, prot='arp-target-transport-address', nw_dst='10.0.0.2', tun_id=200).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=1,tun_id=100,arp,nw_dst=10.0.0.2,actions=output:3
url = b_url.format(s_id=1, table_id=1, flow_id=3)
data = table_1_flow.format(flow_id=3, output_port=3, eth_type=2054, prot='arp-target-transport-address', nw_dst='10.0.0.2', tun_id=100).replace('\n','')

print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=1, flow_id=3)
data = table_1_flow.format(flow_id=3, output_port=3, eth_type=2054, prot='arp-target-transport-address', nw_dst='10.0.0.1', tun_id=100).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=1,tun_id=200,arp,nw_dst=10.0.0.2,actions=output:3
url = b_url.format(s_id=1, table_id=1, flow_id=4)
data = table_1_flow.format(flow_id=4, output_port=3, eth_type=2054, prot='arp-target-transport-address', nw_dst='10.0.0.2', tun_id=200).replace('\n','')

print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=1, flow_id=4)
data = table_1_flow.format(flow_id=4, output_port=3, eth_type=2054, prot='arp-target-transport-address', nw_dst='10.0.0.1', tun_id=200).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=1,tun_id=100,ip,nw_dst=10.0.0.1,actions=output:1
url = b_url.format(s_id=1, table_id=1, flow_id=5)
data = table_1_flow.format(flow_id=5, output_port=1, eth_type=2048, prot='ipv4-destination', nw_dst='10.0.0.1', tun_id=100).replace('\n','')

print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=1, flow_id=5)
data = table_1_flow.format(flow_id=5, output_port=1, eth_type=2048, prot='ipv4-destination', nw_dst='10.0.0.2', tun_id=100).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=1,tun_id=200,ip,nw_dst=10.0.0.1,actions=output:2
url = b_url.format(s_id=1, table_id=1, flow_id=6)
data = table_1_flow.format(flow_id=6, output_port=2, eth_type=2048, prot='ipv4-destination', nw_dst='10.0.0.1', tun_id=200).replace('\n','')

print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=1, flow_id=6)
data = table_1_flow.format(flow_id=6, output_port=2, eth_type=2048, prot='ipv4-destination', nw_dst='10.0.0.2', tun_id=200).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=1,tun_id=100,ip,nw_dst=10.0.0.2,actions=output:3
url = b_url.format(s_id=1, table_id=1, flow_id=7)
data = table_1_flow.format(flow_id=7, output_port=3, eth_type=2048, prot='ipv4-destination', nw_dst='10.0.0.2', tun_id=100).replace('\n','')

print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=1, flow_id=7)
data = table_1_flow.format(flow_id=7, output_port=3, eth_type=2048, prot='ipv4-destination', nw_dst='10.0.0.1', tun_id=100).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))

#table=1,tun_id=200,ip,nw_dst=10.0.0.2,actions=output:3
url = b_url.format(s_id=1, table_id=1, flow_id=7)
data = table_1_flow.format(flow_id=7, output_port=3, eth_type=2048, prot='ipv4-destination', nw_dst='10.0.0.2', tun_id=200).replace('\n','')

print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))
url = b_url.format(s_id=2, table_id=1, flow_id=7)
data = table_1_flow.format(flow_id=7, output_port=3, eth_type=2048, prot='ipv4-destination', nw_dst='10.0.0.1', tun_id=200).replace('\n','')
print(requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin')))



#Now it's time for making the tunnel


#Delete any previous ovsdb
print(requests.delete(url='http://100.0.0.2:8181/restconf/config/network-topology:network-topology/topology/ovsdb:1/', auth=('admin','admin')))

#Make two nodes for the two switches that are listening on port 6640
cm1 = {'network-topology:node': [{'node-id': 'ovsdb://DC1', 'ovsdb:connection-info': {'ovsdb:remote-port': '6640', 'ovsdb:remote-ip': '100.0.0.3'}}]}

cm2 = {'network-topology:node': [{'node-id': 'ovsdb://DC2', 'ovsdb:connection-info': {'ovsdb:remote-port': '6640', 'ovsdb:remote-ip': '100.0.0.4'}}]}

print(requests.put(url='http://100.0.0.2:8181/restconf/config/network-topology:network-topology/topology/ovsdb:1/node/ovsdb:%2F%2FDC1', data = json.dumps(cm1), headers={'content-type': 'application/json'}, auth=('admin','admin')))


print(requests.put(url='http://100.0.0.2:8181/restconf/config/network-topology:network-topology/topology/ovsdb:1/node/ovsdb:%2F%2FDC2', data = json.dumps(cm2), headers={'content-type': 'application/json'}, auth=('admin','admin')))

#Make the two switches make vxlan ports into each other
cm3 = {'termination-point': [{'ovsdb:interface-type': 'ovsdb:interface-type-vxlan', 'ovsdb:name': 'vtep', 'ovsdb:options': [{'option': 'remote_ip', 'value': '100.0.0.4'}, {'option': 'key', 'value': 'flow'}], 'ovsdb:ofport_request': '3', 'tp-id': 'vtep'}]}

cm4 = {'termination-point': [{'ovsdb:interface-type': 'ovsdb:interface-type-vxlan', 'ovsdb:name': 'vtep', 'ovsdb:options': [{'option': 'remote_ip', 'value': '100.0.0.3'}, {'option': 'key', 'value': 'flow'}], 'ovsdb:ofport_request': '3', 'tp-id': 'vtep'}]}


print(requests.put(url='http://100.0.0.2:8181/restconf/config/network-topology:network-topology/topology/ovsdb:1/node/ovsdb:%2F%2FDC1%2Fbridge%2Fs1/termination-point/vtep', data=json.dumps(cm3), headers={'content-type': 'application/json'}, auth=('admin','admin')))

print(requests.put(url='http://100.0.0.2:8181/restconf/config/network-topology:network-topology/topology/ovsdb:1/node/ovsdb:%2F%2FDC2%2Fbridge%2Fs2/termination-point/vtep', data=json.dumps(cm4), headers={'content-type': 'application/json'}, auth=('admin','admin')))








