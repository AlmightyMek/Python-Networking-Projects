from genie_modules import GenieClient
from genie.testbed import load
from dynamic_testbed import create_device_inventory
from datetime import datetime
import pprint

def save_config():
    startTime = datetime.now()

    testbed = create_device_inventory() #from dynamic_testbed file
    #pprint.pprint(testbed)
    tb = load(testbed)
    client = GenieClient(tb,log=False).save_device_config() #saves the devices configuration

    total_time = (datetime.now() - startTime)
    print('Script took {} to complete'.format(total_time))

save_config()
