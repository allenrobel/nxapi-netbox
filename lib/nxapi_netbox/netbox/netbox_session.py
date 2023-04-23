def netbox(vault):
    """
    Return a configured netbox instance.  given an instance of either Ansible or Hashicorp Vault
    """
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    import pynetbox

    from nxapi_netbox.netbox.netbox_config import LoadConfig

    cfg = LoadConfig()
    nb = pynetbox.api(vault.netbox_url, token=vault.netbox_token)

    session = requests.Session()
    if "ssl_verify" in cfg.config:
        session.verify = cfg.config["ssl_verify"]
    if "disable_insecure_request_warnings" in cfg.config:
        if cfg.config["disable_insecure_request_warnings"] == True:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    nb.http_session = session
    return nb


def get_device_mgmt_ip(nb, device_name):
    device = nb.dcim.devices.get(name=device_name)
    if device == None:
        print(
            "netbox_session.get_device_mgmt_ip: exiting. Device {} does not exist in netbox.".format(
                device_name
            )
        )
        exit(1)
    return device.primary_ip4.address.split("/")[0]
