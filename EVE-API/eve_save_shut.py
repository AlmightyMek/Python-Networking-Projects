from genie_modules import GenieClient
from genie.testbed import load
from dynamic_testbed import create_device_inventory
from pyats.async_ import pcall
from datetime import datetime
import os
import errno
import pprint

def create_config_dir():
    cwd = os.getcwd()
    dirname = "deivce-configs"
    try:
        os.mkdir(dirname)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
        return os.path.join(cwd,dirname)
    return None

def save_config_to_file(device):

    save_device_config = device.copy(source='running-config',
               dest='startup-config')
    device_running_config = device.execute('show running-config')
   
    #move into the config dir and save the configs
    os.chdir(create_config_dir())

    with open (f'{device.name}.txt', 'w') as file:
            file.write(device_running_config)
    
    os.chdir("..")

    return None
       
def main():
    startTime = datetime.now()

    testbed = create_device_inventory() #from dynamic_testbed file
    #pprint.pprint(testbed)
    tb = load(testbed)
    client = GenieClient(tb,log=False) #saves the devices configuration
    devices = client.devices.values()
    
    device_config_dir = create_config_dir()

    pcall_task = pcall(save_config_to_file, device=devices, )

    total_time = (datetime.now() - startTime)
    print('Script took {} to complete'.format(total_time))

if __name__ == "__main__":
    main()
