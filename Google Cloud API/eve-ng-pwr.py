#!/usr/bin/env python3

from gcp_api_client import *
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Script to power on/off the Eve-NG lab hosted in GCP')
    groups = parser.add_mutually_exclusive_group(required=False)

    groups.add_argument('-start', action='store_true',
    help="Starts the VM instance")
    groups.add_argument('-stop', action='store_true',
    help="Stops the VM instance")

    args = parser.parse_args()
    start_vm = args.start
    stop_vm = args.stop

    return start_vm, stop_vm

def main():
    get_args()
    client = GCPClient('eve-ng-272521','us-central1-a','4431324615673734442')

    if get_args()[0] == True: #This will start the VM
        instance_control = client.start_instance()
        pprint.pprint(instance_control)

    else: #Otherwise we'll try to stop the VM
        instance_control = client.stop_instance()
        pprint.pprint(instance_control)

if __name__ == '__main__':
    main()
