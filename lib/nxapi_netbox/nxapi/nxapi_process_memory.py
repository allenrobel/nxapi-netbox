'''
Name: nxapi_vpc.py
Author: Allen Robel (arobel@cisco.com)
Description: methods which collect/return information about system processes memory
'''
import re
from nxapi_netbox.nxapi.nxapi_base import NxapiBase

our_version = 100

class NxapiProcessMemoryPhysical(NxapiBase):
    '''
        This class creates info_dict which contains the output of show processes memory physical

        We populate two dict():
            self.info - keyed on processname.  Since there can be more than one process with the 
                same name, we sum the memory used by all such processes and provide a comma-separated
                list of process IDs that comprise the summed process memory stats.
            self.info_by_processid - keyed on processid.  This can be used to retrieve memory stats
                for each of the processes above that had the same name.

        If info_dict is empty due to this library encountering an error, self.error_reason
        will be populated with the reason for the error and self.error dict will contain
        self.error['error'] = self.error_reason

        switch# show processes memory physical | json-pretty
        {
            "TABLE_process_physical_memory": {
                "ROW_process_physical_memory": [
                    {
                        "processid": "1",
                        "virtual": "2272",
                        "physical": "141",
                        "rss": "1680",
                        "processname": "init"
                    },
                    ...
                    {
                        "processid": "30354",
                        "virtual": "392536",
                        "physical": "5145",
                        "rss": "21528",
                        "processname": "dcos_sshd:"
                    }
                ]
            }
        }

    '''
    def __init__(self, username, password, mgmt_ip, _log):
        super().__init__(username, password, mgmt_ip, _log)
        self.info = dict() # keyed on processname
        self.info_by_processid = dict() # keyed on processid
        self.error = dict()
        self.properties = dict()
        self.properties['process_names'] = set()
        self.properties['process_ids'] = set()
        self.properties['error_reason'] = None
        self.properties['process'] = None
        self.lib_version = our_version
        self.class_name = 'NxapiProcessMemoryPhysical'
        self.refreshed = False

    def verify_refreshed(self):
        if self.refreshed != True:
            self.log.error('{}: exiting. call instance.refresh() before accessing getter properties.'.format(self.class_name))
            exit(1)
    def verify_process_is_set(self):
        if self.process == None:
            self.log.error('{}: exiting. call instance.process = <processname> before accessing getter properties.'.format(self.class_name))
            exit(1)
    def verify_ready(self):
        self.verify_refreshed()
        self.verify_process_is_set()

    @property
    def error_reason(self):
        return self.properties['error_reason']
    @error_reason.setter
    def error_reason(self, _x):
        self.properties['error_reason'] = _x

    @property
    def process(self):
        return self.properties['process']
    @process.setter
    def process(self, _x):
        self.properties['process'] = _x

    @property
    def physical(self):
        self.verify_ready()
        return self.info[self.process]['physical']

    @property
    def process_ids(self):
        self.verify_refreshed()
        return sorted(self.properties['process_ids'])

    @property
    def process_names(self):
        self.verify_refreshed()
        return sorted(self.properties['process_names'])

    @property
    def instances(self):
        self.verify_ready()
        return self.info[self.process]['instances']

    @property
    def processid(self):
        self.verify_ready()
        return self.info[self.process]['processid']

    @property
    def processname(self):
        self.verify_ready()
        return self.info[self.process]['processname']

    @property
    def rss(self):
        self.verify_ready()
        return self.info[self.process]['rss']

    @property
    def virtual(self):
        self.verify_ready()
        return self.info[self.process]['virtual']

    def make_info_dict_error(self):
        self.log.debug(self.error_reason)
        self.error = dict()
        self.error['error'] = self.error_reason
        self.info = [self.error]

    def make_info_dict(self):
        '''
        from self.body[0] populate self.info
        '''
        self.info = dict()
        self.error = dict()
        self.error_reason = None

        if self.body_length != 1:
            self.log.error('{} {} early return: unexpected body_length {}'.format(self.class_name, self.hostname, self.body_length))
            self.error_reason = '{} {} unexpected body_length {}'.format(self.class_name, self.hostname, self.body_length)
            self.make_info_dict_error()
            return
        try:
            _list = self._get_table_row('process_physical_memory', self.body[0])
            for item in _list:
                # There can be more than one instance of a process.
                # All instances of a process have the same name, so for these processes,
                # we sum the total memory used by all of them and provide a comma-separated list of
                # process IDs, which the user can use to query self.info_by_processid, if desired.

                # Intermittenty, we get one or more processes with blank ("") names. 
                # Provide a "best guess" name for these.
                if item['processname'] == "":
                    item['processname'] = 'unknown_likely_spurious'

                # 1. processname is not stripped in the NXAPI output.
                #    (it IS stripped in the CLI | json-pretty output, go figure)
                #    Here's an example of NXAPI output as of 10.2(3).
                #    Notice the trailing spaces in the processname value.
                #    {'processid': 8640, 'virtual': 3216, 'physical': 310, 'rss': 2392, 'processname': 'rpc.statd               '}
                process = item['processname'].strip()

                # 2. dcos_sshd process name contains a colon (:). We strip that so that users can
                #    retrieve the process stats using the bare name.
                #    Here's an example as of 10.2(3)
                #    {'processid': 30345, 'virtual': 392424, 'physical': 5436, 'rss': 52856, 'processname': 'dcos_sshd:              '}
                process = re.sub(':', '', process)
                processid = item['processid']

                self.properties['process_names'].add(process)
                self.properties['process_ids'].add(processid)
                item['processname'] = process
                self.info_by_processid[processid] = item
                if process not in self.info:
                    self.info[process] = dict()
                    self.info[process]['processname'] = process
                    self.info[process]['processid'] = ""
                    self.info[process]['physical'] = 0
                    self.info[process]['rss'] = 0
                    self.info[process]['virtual'] = 0
                    self.info[process]['instances'] = 0

                self.info[process]['instances'] += 1
                if self.info[process]['processid'] != "":
                    self.info[process]['processid'] = '{},{}'.format(self.info[process]['processid'], item['processid'])
                else:
                    self.info[process]['processid'] = item['processid']
                self.info[process]['physical'] += int(item['physical'])
                self.info[process]['rss'] += int(item['rss'])
                self.info[process]['virtual'] += int(item['virtual'])
        except:
            self.log.error('{} {} early return. self.info {}'.format(self.class_name, self.hostname, self.info))
            self.error_reason = '{} {} unable to process output of {}'.format(self.class_name, self.hostname, self.cli)
            self.make_info_dict_error()
            return

    def print_dict(self):
        '''
        print the contents of self.info
        '''
        for process in self.info:
            print('process {} -> {}'.format(process, self.info[process]))

    def refresh(self):
        self.cli = 'show processes memory physical'
        self.show()
        self.make_info_dict()
        self.refreshed = True
    
