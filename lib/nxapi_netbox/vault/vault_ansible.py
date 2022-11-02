import os
from ansible import constants as C
from ansible.cli import CLI
from ansible.parsing.dataloader import DataLoader
from nxapi_netbox.vault.vault import Vault

class VaultAnsible(Vault):
    def __init__(self):
        super().__init__()
        self.properties['vault_path'] = os.environ.get('ANSIBLE_VAULT_PATH', None)
        if self.properties['vault_path'] == None:
            self.vault_path_help()

    @property
    def vault_path(self):
        return self.properties['vault_path']

    def fetch_data(self):
        try:
            loader = DataLoader()
            vault_secrets = CLI.setup_vault_secrets(loader=loader,
                        vault_ids=C.DEFAULT_VAULT_IDENTITY_LIST)
            loader.set_vault_secrets(vault_secrets)
            data = loader.load_from_file(self.vault_path)
        except Exception as e:
            print('VaultAnsible.fetch_data: unable to load data in {}.'.format(self.vault_path))
            print('VaultAnsible.fetch_data: Exception was: {}'.format(e))
            exit(1)

        for key in self.mandatory_keys:
            if key not in data:
                print('VaultAnsible.fetch_data: exiting. Vault is missing mandatory key {}'.format(key))
                exit(1)
            self.properties[key] = str(data[key])

    def vault_path_help(self):
        print('VaultAnsible.init: exiting.')
        print('Reason: Environment variable ANSIBLE_VAULT_PATH not set.')
        print('To fix: export ANSIBLE_VAULT_PATH=</path/to/ansible/vault>')
        print('Example: export ANSIBLE_VAULT_PATH=/home/myaccount/ansible/vault')
        exit(1)
