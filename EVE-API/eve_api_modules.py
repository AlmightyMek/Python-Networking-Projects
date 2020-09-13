import signal
import requests
from requests import Request, Session
import argparse
import json
import getpass
import netmiko
from netmiko import ConnectHandler
import concurrent.futures
import sys
import urllib3
from urllib.parse import urlparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import re
import pprint

class EveClient():
    """Parent Object to interact with the EVE-NG API."""

    def __init__(self, username={},password={},server_ip=None,login_dict ={}, lab=None,nodes={}):
        self.username = username
        self.password = password
        self.server_ip = server_ip #Example https://{your-server-ip/name}
        self.login_dict = login_dict
        self.lab = lab
        self.session = Session()
        self.nodes = nodes

    def get_args(self):
        """Parse the args from the command line
        """
        parser = argparse.ArgumentParser(description='''Script to connect
        to a remote Eve-NG lab, save the lab devices' config, and then shut the lab down''')

        parser.add_argument('username', action='store',
        help = 'Username of user that is running the lab')

        parser.add_argument('Server', action='store',
        help = 'IP Address of the Eve-NG server ex: http://[ip address]')

        parser.add_argument('lab', action='store',
        help = 'Name of the lab without the .unl extension')

        args = parser.parse_args()

        self.username["username"] = args.username
        self.server_ip = args.Server
        self.lab = args.lab

        return self.username , self.server_ip, self.lab

    def exception_catch(self):
        #Catching Netmiko netmiko_exceptions as well as Python Exceptions
        signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C

        netmiko_exceptions = (netmiko.ssh_exception.NetMikoTimeoutException,
                          netmiko.ssh_exception.NetMikoAuthenticationException)

        return netmiko_exceptions

    def get_password(self):
        """Use getpass to get the password from the user
        """
        self.password = {}
        self.password["password"] = getpass.getpass("Enter the Admin user's password: ")

        return self.password


    def admin_login(self):
        """This function handles the login to the
            server
        """
        self.login_dict.update(self.get_args()[0])
        self.login_dict.update(self.get_password())
        console_dict = {"html5": "-1"}  #This will let us login with the Native console
        self.login_dict.update(console_dict)

        try:                                #Here we are passing in the Server ip
            req = Request('POST',F"https://{self.get_args()[1]}/api/auth/login" , data = (json.dumps(self.login_dict)))
            #self.cookies.update(req.cookies.get_dict())

            prepped = self.session.prepare_request(req)
            respone = self.session.send(prepped, verify=False)
            respone.raise_for_status()
            #print(self.cookies)

        except requests.exceptions.HTTPError as e:
            raise SystemExit(e)
            sys.exit(1)

        return respone

    def admin_logout(self):
        """This will log the user out of the Eve server"""
        try:
            req  = requests.post(F"https://{self.get_args()[1]}/api/auth/logout" , data = (json.dumps(self.login_dict)), verify=False)

        except self.exception_catch() as e:
            print(e)
            sys.exit(1)
        return req

    def get_lab_nodes(self):
        """We'll check the shared folder first, then the user's folder for the lab; If both fail exit out of the script"""
        try:
            req = Request('GET',f"https://{self.get_args()[1]}/api/labs/Shared/{self.get_args()[2]}.unl/nodes")
                                    #https://[public-ip]/api/labs/Shared/OSPF-LSAs.unl
            prepped = self.session.prepare_request(req)
            respone = self.session.send(prepped, verify=False)

        except self.exception_catch() as e:
            print("Lab not found in the shared folder " + e)

        else:
            try:
                req = self.session.get(f"https://{self.get_args()[1]}/api/labs/{self.username}/{self.get_args()[2]}/nodes", verify=False)

            except self.exception_catch() as e:
                print("Lab not found in the user's folder " + e)
                sys.exit(1)

        return respone.json()

    def get_node_inventory(self):
        self.nodes = self.get_lab_nodes()
        node_inventory = []
        temp_dict = {}
        devices = {}
        #Here we are looping over each node in the json we get back from the server
        #We then are going into each dict and pulling nodes name and port #s

        for node in self.nodes["data"]:
            for port in self.nodes["data"][node]:
                device_dict = {
                "name" : self.nodes['data']['name'],
                "host": self.server_ip, #All of the nodes should be at the same IP address
                "port": self.nodes["data"][node]['url']
                #Well set the url to this http://[server_ip]:port and then parse it below
                }
                #Here we use urlpase to spilt up the
                #ip portion of the url and the port portion
                # Doc https://bip.weizmann.ac.il/course/python/PyMOTW/PyMOTW/docs/urlparse/index.html
                url_port = urlparse(device_dict["port"])
                device_dict["port"] = url_port.port

            node_inventory.append(device_dict)
            json_node_inventory = json.dumps(node_inventory)

        return node_inventory

    def netmiko_connect(self,devices):
        try:
            print(f'Connecting to the device on port {devices["port"]}')
            net_connect = netmiko.base_connection.TelnetConnection(**devices,verbose=True)
            host_name = net_connect.set_base_prompt()
            print(f"Running commands on {host_name}")
            wr_config = 'wr'
            #net_connect.enable()
            enable = 'enable'
            #print(net_connect.send_command(enable))
            print(net_connect.send_command('show ip interface br'))

        except self.netmiko_exception_catch() as e:
            print('Failed to connect to; error ', e)
        #return output

    def save_configs(self):
        #We'll thread the connections the devices
        #then connect to them and run the command

        self.netmiko_exception_catch() #catch any exceptions

        #open the threads to the devices
        with concurrent.futures.ThreadPoolExecutor() as executor:
            login = self.admin_login()
            nodes = self.get_node_inventory()

            results = executor.map(self.netmiko_connect, nodes)
            self.admin_logout()
        #output = self.netmiko_connect(self.get_node_inventory()[0])

        # for results in concurrent.futures.as_completed(results):
        #     print(results.result())

        return results
