'''
Name: args_nxapi_tools.py
Summary: Common command line arguments for nxapi-tools scripts.
Description:

Contains common arguments for scripts in the nxapi-tools repo
      --devices  : Comma-separated (no spaces) list of device names to query.
      --vault    : Which vault to use. Valid values: ansible, hashicorp
      --vrf      : The vrf in which to retrieve information.

'''
# standard libraries
import argparse
help_devices = 'Comma-separated (no spaces) list of device names to query.'
help_vault = 'The vault to use. Valid values: ansible, hashicorp.'
help_vrf = 'The vrf in which to retrieve information.'

ex_prefix = ' Example: '
ex_vrf = '{} --vrf TENANT1'.format(ex_prefix)
ex_devices = '{} --devices leaf_1,spine_3,pathway'.format(ex_prefix)
ex_vault = '{} --vault hashicorp'.format(ex_prefix)

ArgsNxapiTools = argparse.ArgumentParser(add_help=False, description='placeholder')
optional = ArgsNxapiTools.add_argument_group(title='OPTIONAL SCRIPT ARGS')
mandatory = ArgsNxapiTools.add_argument_group(title='MANDATORY SCRIPT ARGS')

mandatory.add_argument('--devices',
                     dest='devices',
                     required=True,
                     help='{} {}'.format(help_devices, ex_devices))

optional.add_argument('--vault',
                     dest='vault',
                     choices=['ansible', 'hashicorp'],
                     required=False,
                     default='hashicorp',
                     help='(default: {}) {} {}'.format('%(default)s', help_vault, ex_vault))

optional.add_argument('--vrf',
                     dest='vrf',
                     required=False,
                     default='default',
                     help='(default: {}) {} {}'.format('%(default)s', help_vrf, ex_vrf))
