from eve_api_modules import *
import pprint

def main():
    eve_api = SaveAndShut()
    login = eve_api.admin_login()
    lab_nodes = eve_api.get_lab_nodes()


    pprint.pprint(login)
    print()
    pprint.pprint(lab_nodes)

main()
