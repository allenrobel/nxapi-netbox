#!/usr/bin/env python
'''
Name: test_vault.py
Summary: Verify that HashiCorp Vault is working and contains the keys required by scripts in this repo

This script will not work without completing the following:

1. Environment variables

    Set the following env variables

    VAULT_ADDR=<vault url>
    VAULT_TOKEN=<vault token>

    Bash example:
    
    export VAULT_ADDR=http://127.0.0.1:8200
    export VAULT_TOKEN=hvs.SiVa7BDO92FfETBLdQuMxSCq

    Verify the above are present with:

    % env | grep VAULT_ADDR
    VAULT_ADDR=http://127.0.0.1:8200
    % env | grep VAULT_TOKEN
    VAULT_TOKEN=hvs.SiVa7BDO92FfETBLdQuMxSCq

2. Vault endpoint

By default, the scripts in this repo look for data in the vault at endpoint '/v1/kv/nxapi'

If your endpoint is different, you can set it below using 'endpoint' property of the VaultHashiCorp instance.

For example:

vault = VaultHashiCorp()
vault.endpoint = '/v2/kv/myendpoint'
vault.fetch_data()

'''
from vault.vault import get_vault

vault = get_vault('hashicorp')
# vault.endpoint = '/v1/kv/myendpoint'
vault.fetch_data()
print('nxos_username: {}'.format(vault.nxos_username))
print('nxos_password: {}'.format(vault.nxos_password))
print('netbox_token: {}'.format(vault.netbox_token))
print('netbox_url: {}'.format(vault.netbox_url))
