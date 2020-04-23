from googleapiclient.discovery import build
from googleapiclient import discovery
from googleapiclient import errors
import json
import pprint


class GCPClient():
    '''
    Client to interface with the GCP API
    '''

    def __init__(self,project=None,zone=None,resourceId=None,service=None):

        self.project = project
        self.zone = zone
        self.resourceId = resourceId
        self.service = build('compute', 'v1')

    def start_instance(self):
        try:
            req = self.service.instances().start(project=self.project, zone=self.zone, instance=self.resourceId)
            respone = req.execute()

        except errors.HttpError as err:
            print(err._get_reason())

        return respone

    def stop_instance(self):
        try:
            req = self.service.instances().stop(project=self.project, zone=self.zone, instance=self.resourceId)
            respone = req.execute()

        except errors.HttpError as err:
            print(err._get_reason())

        return respone


def main():
    client = GCPClient('eve-ng-272521','us-central1-a','4587562327453364584')
    stop_instance = client.stop_instance()
    pprint.pprint(stop_instance)

if __name__ == '__main__':
    main()
