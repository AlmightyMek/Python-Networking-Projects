#from genie.libs.conf.base import device
#from genie.libs.conf.interface import Interface
from genie.libs.sdk.apis import *
from pyats.async_ import pcall
import pprint
import pyats

class GenieClient():
    """An Object to interact with pyATS's Genie parsers"""

    def __init__(self,testbed,log=False):
        """Init the Config Object and connect to Testbed"""

        self.testbed = testbed.connect(log_stdout=log,learn_os=True)
        self.devices = testbed.devices

    def push_config(self):
        user_input = input('Do you want to push this config to the device? Y/N ')
        if user_input == 'y' or 'Y':
            push_config = True

        else:
            push_config = False

        return push_config

    def get_info(self,command):
        """Generic method to get structured
        data back. Depends on if the genie parser is present for that command
        """
        for device in self.devices:
            print(f'Running commands on {device}...')
            command = self.devices[device].parse(command)

        return command

    def save_device_config(self):
        '''Saves the device's in the testbed
        running config to the start up config'''

        def write_mem(devices):
            print(f'Running commands on {devices}...')
            cmd = "write memory"
            output = devices.execute(cmd)
            print(f'\nOutput of {cmd} on {devices}\n' + output + '\n')

        #Using pcall to run the above function in Parallel

        write_config = pcall(write_mem,devices=self.devices.values())

    def get_running_config(self):
        """Grabs the running config from devices in the
        testbed file using genie"""

        device_configs = {}

        for device in self.devices:
            print(f'Running commands on {device}...')
            config = self.devices[device].parse('show running-config')
            device_configs[device] = config

        return device_configs


    def get_cdp(self,cdp_dict={}):
        """Gets CDP neighbors information and returns a dict
        with the key as the device name
        """
        for device in self.devices:
            print(f'Running commands on {device}...')
            cdp_dict[device] = self.devices[device].parse("show cdp neighbors")

        return cdp_dict

    def update_interface_desc(self):
        """Updates device interface desc with the cdp information from the get_cdp function
        """
        interface_dict = self.get_cdp()
        management_interface = ['GigabitEthernet0/0','MgmtEth0/RP0/CPU0/0','GigabitEthernet0']

        for device in self.devices:

            for index in interface_dict[device]["cdp"]["index"]: # For each cdp entry in each of the devices
                local_interface = interface_dict[device]["cdp"]["index"][index]["local_interface"]
                #pprint.pprint(local_interface)
                remote_device_hostname = interface_dict[device]["cdp"]["index"][index]["device_id"]
                remote_device_interface = interface_dict[device]["cdp"]["index"][index]["port_id"]
    #Make sure this works               
                if local_interface any in management_interface: #Check if the local interface is 
                    interface_desc=(f'Conneted to the backbone') # management interface, if so set this desc

                interface_desc=(f"connected to {remote_device_hostname} via its {remote_device_interface} interface")           

                iosxe_interface = Interface(device=self.devices[device], name=local_interface)
                iosxe_interface.description = interface_desc

                final_config = iosxe_interface.build_config(apply=True)
                print(f"Interface configuration for {self.devices[device]} \n {final_config}")
                #final_config = iosxe_interface.build_config(apply=True)

    def get_inventory(self):
        """Get inventory from testbed devices"""
        inventory_dict = {}

        for device in self.devices:
            inventory_dict[device] = self.devices[device].parse('show inventory')

        return inventory_dict
