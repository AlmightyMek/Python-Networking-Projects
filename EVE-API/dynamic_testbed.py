from eve_api_modules import EveClient
import pprint

def get_nodes_from_eve():
    
    client = EveClient()
    login = client.admin_login() #Login into the server and get the nodes
    nodes = client.create_node_inventory()

    return nodes

def create_device_inventory():
    ###define device template dict
    node_inventory = get_nodes_from_eve()
    mydict = {'devices': {}}

    #Here we loop through the list we get back and create a testbed device_type
    for entry in range(len(node_inventory)):
        hostname = node_inventory[entry]['name']
        ip_address = node_inventory[entry]['ip']
        port = node_inventory[entry]['port']
		#device_os = row['device_os']
		#device_platform = row['device_platform']
		#device_type = row['device_type']
		###define device template dict
        mydict_template = {f'{hostname}':
            {"ip": f'{ip_address}',
            "port": f'{port}',
            "protocol": "telnet",
            "username" : "",
            "password" : "",
            "os": "",
            "type": ""}}
        
        mydict['devices'].update(mydict_template)

    return mydict
