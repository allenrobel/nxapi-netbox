import json
import os
import requests
from nxapi_netbox.vault.vault import Vault

class VaultHashiCorp(Vault):
    def __init__(self):
        super().__init__()
        self.properties['endpoint'] = '/v1/kv/nxapi'
        self.properties['vault_token'] = os.environ.get('VAULT_TOKEN', None)
        if self.properties['vault_token'] == None:
            self.vault_token_help()
        self.properties['vault_address'] = os.environ.get('VAULT_ADDR', None)
        if self.properties['vault_address'] == None:
            self.vault_address_help()

    @property
    def endpoint(self):
        return self.properties['endpoint']
    @endpoint.setter
    def endpoint(self, x):
        self.properties['endpoint'] = x

    @property
    def vault_address(self):
        return self.properties['vault_address']

    @property
    def vault_token(self):
        return self.properties['vault_token']

    @property
    def vault_url(self):
        return '{}{}'.format(self.vault_address, self.endpoint)


    def fetch_data(self):
        headers = {'Authorization' : 'Bearer {}'.format(self.vault_token)}
        response = requests.get(self.vault_url, headers=headers)
        data = response.json()['data']
        for key in self.mandatory_keys:
            if key not in data:
                print('VaultHashiCorp.fetch_data: exiting. Mandatory key {} not found at endpoint {}'.format(key, self.vault_url))
                exit(1)
            self.properties[key] = data[key]

    def vault_token_help(self):
        print('VaultHashiCorp.init: exiting.')
        print('Reason: Environment variable VAULT_TOKEN not set.')
        print('To fix: export VAULT_TOKEN=<your token>')
        print('Example: export VAULT_TOKEN=hvs.SlZx4JZP63RfETBHkSuAxBEq')
        exit(1)
    def vault_address_help(self):
        print('VaultHashiCorp.init: exiting.')
        print('Reason: Environment variable VAULT_ADDR not set.')
        print('To fix: export VAULT_ADDR=<url for vault>')
        print('Example: export VAULT_ADDR=http://127.0.0.1:8200')
        exit(1)
