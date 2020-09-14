from genie_modules import *
from genie.testbed import load
from dynamic_testbed import *
import pprint

def save_config():
    testbed = create_device_inventory() #from dynamic_testbed file
    #pprint.pprint(testbed)
    tb = load(testbed)
    client = GenieClient(tb,log=True).save_device_config()

def main():
    save_config()

main()
