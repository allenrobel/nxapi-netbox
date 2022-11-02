'''
netbox_config.py

Description:

Load YAML file pointed to by the config_file variable, and return the contents as a python dict()

Usage:

from netbox_tools.netbox_config import LoadConfig

c = LoadConfig()
print('c.vault {}'.format(c.config['vault']))

Author:

Allen Robel (arobel@cisco.com)
'''
import yaml

config_file = '/home/your_account/repos/nxapi-netbox/lib/nxapi_netbox/netbox/config.yml'
class LoadConfig(object):
    def __init__(self):
        self.properties = dict()
        self.load_config()

    def load_config(self):
        with open(config_file, 'r') as fp:
            self.properties['config'] = yaml.safe_load(fp)

    @property
    def config(self):
        return self.properties['config']
