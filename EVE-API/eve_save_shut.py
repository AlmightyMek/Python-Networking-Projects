from eve_api_modules import *
import pprint

def main():
    client = EveClient()
    #login = client.admin_login()
    #nodes = client.get_node_inventory()
    save_config = client.save_configs()
    #lab = client.get_lab_nodes()
    #logout = client.admin_logout()

    #pprint.pprint(login)
    print()
    print(save_config)

main()
