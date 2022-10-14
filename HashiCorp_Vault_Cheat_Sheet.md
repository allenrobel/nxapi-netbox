## HashiCorp Vault Cheat Sheet

### A vault installation guide from HashiCorp is here

[Install HashiCorp Vault](https://learn.hashicorp.com/tutorials/vault/getting-started-install)

Below is a summarized cheat-sheet based on the needs of this repo.

### 1. Create vault config file

```bash
vim vault.hcl
```

Should look like

```bash
storage "raft" {
  path    = "./vault/data"
  node_id = "node1"
}

listener "tcp" {
  address     = "127.0.0.1:8200"
  tls_disable = "true"
}

api_addr = "http://127.0.0.1:8200"
cluster_addr = "https://127.0.0.1:8201"
ui = true
```

### 2. Make directory for raft

```bash
mkdir -p ./vault/data
```

### 3. Start the vault server

```bash
vault server -config=vault.hcl
```

### 4. Export the vault address

```bash
export VAULT_ADDR='http://127.0.0.1:8200'
```

### 5. Create the unseal keys

```bash
vault operator init

Unseal Key 1: yzx8Vl2cjch5CDKj3lAY3/gqGr0kRU6bjf0ICH3AELnR
Unseal Key 2: GhMa/moIbXZotscaSFBb01OO6HI7kjIBVCNuIAXJrxP6
Unseal Key 3: 266JEInlg3b8N5Q72eanGPGoJgAgUWh6btjTB1x2XAWd
Unseal Key 4: m5SA/mzDNVvSac/4QU5a9GLo7iwa9Vqu1DEu02fOmuMj
Unseal Key 5: nPryLNFjMmHrWeLEC/7cDcQVdGux9aoz6s/Ujl9faGN7

Initial Root Token: hvs.SkZy4JXM51UdPWNLkSuAxSEq

Vault initialized with 5 key shares and a key threshold of 3. Please securely
distribute the key shares printed above. When the Vault is re-sealed,
restarted, or stopped, you must supply at least 3 of these keys to unseal it
before it can start servicing requests.

Vault does not store the generated root key. Without at least 3 keys to
reconstruct the root key, Vault will remain permanently sealed!

It is possible to generate new unseal keys, provided you have a quorum of
existing unseal keys shares. See "vault operator rekey" for more information.
```


### 6. Unseal the vault (below must be done 3 times, each with a different Unseal Key from above)

vault operator unseal


### 7. Create the vault endpoint

```bash
vault secrets enable kv
```

### 8. Verify the vault endpoint

```bash
vault secrets list
```

### 9. Populate data at this endpoint

vault kv put kv/nxapi nxos_username=admin nxos_password=mypassword netbox_token=21716fi7k4ac9a8a51d99c5fab025e207b741fe netbox_url=http://mynetbox.foo.com

### 10. Verify the expected key/values are present at this endpoint

```bash
% vault kv get -format="json" kv/nxapi
{
"request_id": "cc330dc0-b84b-e1b6-27bd-98bfc860344a",
"lease_id": "",
"lease_duration": 2764800,
"renewable": false,
"data": {
    "netbox_token": "21716fi7k4ac9a8a51d99c5fab025e207b741fe",
    "netbox_url": "http://mynetbox.foo.com",
    "nxos_password": "ax84fs00fs",
    "nxos_username": "admin"
},
"warnings": null
}
```

### 10. Environment variables

This repo requires the following environment variables to be set.

```bash
export VAULT_ADDR=http://127.0.0.1:8200
export VAULT_TOKEN=hvs.SkZx4JXP61RfETBLkSuAxSEq
```

You can test these using the following script in this repo: ``test_vault_hashicorp.py``

If things are working, you'll see something like:

```bash
% ./test_vault_hashicorp.py
nxos_username: admin
nxos_password: ax84fs00fs
netbox_token: 21716fi7k4ac9a8a51d99c5fab025e207b741fe
netbox_url: http://mynetbox.foo.com
% 
```