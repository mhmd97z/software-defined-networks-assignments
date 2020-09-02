import xml.etree.ElementTree as ET
import requests
import networkx as nx
import numpy as np


#==================================
def flow_put(switch_id, flow_id, table_id, priority, out_action, out_action_value, match_eth_type, match_prot, match_value):
	base_url = 'http://100.0.0.2:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:'

	url = base_url + str(switch_id) + '/table/' + str(table_id) + '/flow/' + str(flow_id)

	data = flow_maker(str(flow_id), str(table_id), priority, out_action, out_action_value, match_eth_type, match_prot, match_value)

	return requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin'))

def flow_maker(id, table_id, priority, out_action, out_action_value, match_eth_type, match_prot, match_value):
	flow = ET.Element('flow')
	flow.set('xmlns', "urn:opendaylight:flow:inventory")
	ET.SubElement(flow, 'id').text = str(id)
	ET.SubElement(flow, 'table_id').text = str(table_id)
	ET.SubElement(flow, 'priority').text = str(priority)
	instructions = ET.SubElement(flow, 'instructions')
	instruction = ET.SubElement(instructions, 'instruction')
	ET.SubElement(instruction, 'order').text = '0'
	apply_actions = ET.SubElement(instruction, 'apply-actions')
	action = ET.SubElement(apply_actions, 'action')
	ET.SubElement(action, 'order').text = '0'
	output_action = ET.SubElement(action, 'output-action')
	ET.SubElement(output_action, out_action).text = str(out_action_value)
	
	if (match_eth_type != ''):
		match = ET.SubElement(flow, 'match')
		ethernet_match = ET.SubElement(match, 'ethernet-match')
		ethernet_type = ET.SubElement(ethernet_match, 'ethernet-type')
		ET.SubElement(ethernet_type, 'type').text = str(match_eth_type)
		if (match_prot != ''):
			ET.SubElement(match, str(match_prot)).text = str(match_value)

	return ET.tostring(flow)
#==================================

#Here is the adjacency matrix, to change it just alter this matrix, it could be of any degree.
A_matrix = np.matrix([ [0, 2, 3, 4],
                       [2, 0, 0, 1],
                       [3, 0, 0, 0],
                       [1, 1, 0, 0] ])
s = 1 -1 # -1 :To get compatible with matrix indices
d = 4 -1

#Make the network graph from matrix using networkx
G = nx.from_numpy_matrix(A_matrix, create_using=nx.MultiDiGraph)

#Finding the shortest paths using networkx_dijkstra
#path_1 from s to d, path_2 from d to s
path_1 = nx.dijkstra_path(G, s, d)
path_2 = nx.dijkstra_path(G, d, s)

#Now that we have our paths, we walk through the paths and put flows so that packets of each path are routed through that path, here every switch in the path, sends its packets out to the next switch in the path.
for i in range(len(path_1)):
	if(i != len(path_1)-1):
		flow_put(path_1[i]+1, 1, 0, 100, 'output-node-connector', path_1[i+1]+1, '2054', 'arp-target-transport-address', '10.0.2.1/24')
		flow_put(path_1[i]+1, 2, 0, 100, 'output-node-connector', path_1[i+1]+1, '2048', 'ipv4-destination', '10.0.2.1/24')

	else:
		flow_put(path_1[i]+1, 1, 0, 100, 'output-node-connector', path_1[i]+1, '2054', 'arp-target-transport-address', '10.0.2.1/24')
		flow_put(path_1[i]+1, 2, 0, 100, 'output-node-connector', path_1[i]+1, '2048', 'ipv4-destination', '10.0.2.1/24')


for i in range(len(path_2)):
	if(i != len(path_2)-1):
		flow_put(path_2[i]+1, 3, 0, 100, 'output-node-connector', path_2[i+1]+1, '2054', 'arp-target-transport-address', '10.0.1.1/24')
		flow_put(path_2[i]+1, 4, 0, 100, 'output-node-connector', path_2[i+1]+1, '2048', 'ipv4-destination', '10.0.1.1/24')

	else:
		flow_put(path_2[i]+1, 3, 0, 100, 'output-node-connector', path_2[i]+1, '2054', 'arp-target-transport-address', '10.0.1.1/24')
		flow_put(path_2[i]+1, 4, 0, 100, 'output-node-connector', path_2[i]+1, '2048', 'ipv4-destination', '10.0.1.1/24')



