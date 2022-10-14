#!/usr/bin/env python
'''
Name: test_vault_ansible.py
Summary: Verify that Ansible Vault is working and contains the keys required by scripts in this repo

This script will not work without completing the following:

1. Environment variables

    Set the following env variables

    ANSIBLE_VAULT_PATH=<absolute path to ansible vault file>

    Bash example:
    
    export ANSIBLE_VAULT_PATH=/Users/me/repos/nxapi-netbox-prod/secrets

    Verify the above are present with:

    (py310) nxapi_netbox % env | grep ANSIBLE_VAULT_PATH
    ANSIBLE_VAULT_PATH=/Users/me/repos/nxapi-netbox-prod/secrets

'''
from vault.vault import get_vault
vault = get_vault('ansible')
vault.fetch_data()
print('nxos_username: {}'.format(vault.nxos_username))
print('nxos_password: {}'.format(vault.nxos_password))
print('netbox_token: {}'.format(vault.netbox_token))
print('netbox_url: {}'.format(vault.netbox_url))
