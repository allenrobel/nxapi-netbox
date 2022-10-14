def get_vault(vault_type):
    if vault_type == 'ansible':
        from vault.vault_ansible import VaultAnsible
        return VaultAnsible()
    elif vault_type == 'hashicorp':
        from vault.vault_hashicorp import VaultHashiCorp
        return VaultHashiCorp()

class Vault():
    def __init__(self):
        self.properties = dict()
        self.mandatory_keys = set()
        self.mandatory_keys.add('netbox_token')
        self.mandatory_keys.add('netbox_url')
        self.mandatory_keys.add('nxos_password')
        self.mandatory_keys.add('nxos_username')

    @property
    def netbox_token(self):
        return self.properties['netbox_token']

    @property
    def netbox_url(self):
        return self.properties['netbox_url']

    @property
    def nxos_password(self):
        return self.properties['nxos_password']

    @property
    def nxos_username(self):
        return self.properties['nxos_username']
