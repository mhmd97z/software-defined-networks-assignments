import xml.etree.ElementTree as ET
import requests


#Here I defined a function that makes and puts a flow, by getting the switch id, flow_id, ..., action and match properties.

def flow_put(switch_id, flow_id, table_id, priority, out_action, out_action_value, match_eth_type, match_prot, match_value):

	#The request url is made concatenating this base url with switch_id, flow_id and table_id
	base_url = 'http://100.0.0.2:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:'

	url = base_url + str(switch_id) + '/table/' + str(table_id) + '/flow/' + str(flow_id)

	#The body xml is made using flow_maker function that is explained later.
	data = flow_maker(str(flow_id), str(table_id), priority, out_action, out_action_value, match_eth_type, match_prot, match_value)

	return requests.put(url, data = data, headers={'content-type':'application/xml'}, auth=('admin','admin'))


def flow_maker(id, table_id, priority, out_action, out_action_value, match_eth_type, match_prot, match_value):
	flow = ET.Element('flow')
	flow.set('xmlns', "urn:opendaylight:flow:inventory")
	#Implementing id, table_id and priority in the xml
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
	#Here, the out_action is the action specified in the arguments and out_action_value is the value for it, for example out_action could be output-node-connector and value be 1 or NORMAL
	ET.SubElement(output_action, out_action).text = str(out_action_value)
	
	if (match_eth_type != ''):
		match = ET.SubElement(flow, 'match')
		ethernet_match = ET.SubElement(match, 'ethernet-match')
		ethernet_type = ET.SubElement(ethernet_match, 'ethernet-type')
		#Implementing ethernet_type, which can be 2048, 2054, ...
		ET.SubElement(ethernet_type, 'type').text = str(match_eth_type)
		if (match_prot != ''):
			#Set matching protocol, like ipv4 or arp, and value
			ET.SubElement(match, str(match_prot)).text = str(match_value)

	return ET.tostring(flow)



#===============================

#These flows are just like the ones in question 1_2
flow_put(1, 1, 0, 100, 'output-node-connector', 'NORMAL', '', '', '')
flow_put(2, 1, 0, 100, 'output-node-connector', 'NORMAL', '', '', '')
flow_put(3, 1, 0, 100, 'output-node-connector', 2, '2054', 'arp-target-transport-address', '10.0.2.1/24')
flow_put(3, 2, 0, 100, 'output-node-connector', 1, '2054', 'arp-target-transport-address', '10.0.1.1/24')
flow_put(3, 3, 0, 100, 'output-node-connector', 2, '2048', 'ipv4-destination', '10.0.2.1/24')
flow_put(3, 4, 0, 100, 'output-node-connector', 1, '2048', 'ipv4-destination', '10.0.1.1/24')


