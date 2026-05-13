# ACDC Issuance with KLI: Issuer-To-Issuee

<div class="alert alert-primary">
<b>🎯 OBJECTIVE</b><hr>
<p>Demonstrate how to issue chained Authentic Chained Data Containers (ACDCs) using an Issuer-To-Issuee (<code>I2I</code>) edge relationship with the KERI Command Line Interface (KLI).
    
<p>It also illustrates how to embed a simple rule within an ACDC. We will implement the "Endorsement for Building Access" scenario.</p>
</div>

## Scenario Recap: Endorsement for Building Access

Remember, the I2I operator enforces successive parent-child relationships across a chain of credential holders where the parent issuer of the current credential must be the child of the prior credential, if it has a parent. This is a strict constraint. Who enforces this strict constraint? Verifiers do, and usually within a set of rules for a credential ecosystem similar to how the vLEI Ecosystem Governance Framework (EGF) specifies the kind of credentials and their relationships to one another.

This notebook focuses on the practical KLI commands for implementing an `I2I` chained credential scenario. For a detailed theoretical explanation of ACDC Edges, Edge Operators, and Rules, please refer to the "[Advanced ACDC Features: Edges, Edge Operators, and Rules](101_75_ACDC_Edges_and_Rules.ipynb)" notebook. 

To summarize this scenario: 

- **ACME Corp** issues a "Role Credential" to an Employee.
- The **Employee**, by virtue of their "Role Credential", issues an "Access Credential" to a **Sub-contractor**.
- The **Access Credential** contains an `I2I` edge linking back to the Employee's "Role Credential", signifying that the Employee's authority to grant access is derived from their managerial role.
- The **Access Credential** will also include a simple textual rule regarding its usage policy.


## Initial Setup: Keystores, AIDs, Registries, and OOBIs
As usual, it is necessary to set up our participants:

- Acme Corporation (`acme_aid`): The initial, or root, authority in this scenario, responsible for issuing the top level Role Credential.
- Employee (`employee_aid`): This participant will first receive the Role Credential from Acme and subsequently issue the Access Credential.
- Sub-contractor (`subcontractor_aid`): The recipient of the Access Credential.

For each participant:
- Initialize their respective keystores.
- Incept their Autonomic Identifiers (AIDs). These AIDs will be configured as transferable and will utilize the default witness setup from `keystore_init_config.json`.
- Establish OOBI connections. This involves generating OOBIs for each AID and resolving them to ensure all necessary participants (Acme-Employee, Employee-Sub-contractor) can securely discover each other.

For ACME and the Employee:
- Incept a credential registry


```python
# Imports and Utility functions
from scripts.utils import exec, clear_keri, pr_title, pr_message, pr_continue
from scripts.saidify import get_schema_said
import json, os

clear_keri()

# ACME Keystore and AID
acme_keystore_name = "acme_ks"
acme_salt = exec("kli salt")
acme_aid_alias = "acme"
acme_registry_name = "acme_mgr_registry"

# Employee Keystore and AID
employee_keystore_name = "employee_ks"
employee_salt = exec("kli salt")
employee_aid_alias = "employee"
employee_registry_name = "employee_access_registry"

# Sub-contractor Keystore and AID
subcontractor_keystore_name = "subcontractor_ks"
subcontractor_salt = exec("kli salt")
subcontractor_aid_alias = "subcontractor"

pr_title("Initializing keystores")

!kli init --name {acme_keystore_name} \
    --nopasscode \
    --salt {acme_salt} \
    --config-dir ./config \
    --config-file keystore_init_config.json

!kli init --name {employee_keystore_name} \
    --nopasscode \
    --salt {employee_salt} \
    --config-dir ./config \
    --config-file keystore_init_config.json

!kli init --name {subcontractor_keystore_name} \
    --nopasscode \
    --salt {subcontractor_salt} \
    --config-dir ./config \
    --config-file keystore_init_config.json

pr_title("Initializing AIDs")

!kli incept --name {acme_keystore_name} \
    --alias {acme_aid_alias} \
    --file ./config/aid_inception_config.json # Uses witnesses and transferable settings

!kli incept --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --file ./config/aid_inception_config.json

!kli incept --name {subcontractor_keystore_name} \
    --alias {subcontractor_aid_alias} \
    --file ./config/aid_inception_config.json

pr_title("Initializing Credential Registries")

!kli vc registry incept --name {acme_keystore_name} \
    --alias {acme_aid_alias} \
    --registry-name {acme_registry_name}

!kli vc registry incept --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --registry-name {employee_registry_name}


acme_aid_prefix = exec(f"kli aid --name {acme_keystore_name} --alias {acme_aid_alias}")
employee_aid_prefix = exec(f"kli aid --name {employee_keystore_name}  --alias {employee_aid_alias}")
subcontractor_aid_prefix = exec(f"kli aid --name {subcontractor_keystore_name}  --alias {subcontractor_aid_alias}")

pr_message(f"ACME AID: {acme_aid_prefix}")
pr_message(f"Employee AID: {employee_aid_prefix}")
pr_message(f"Sub-contractor AID: {subcontractor_aid_prefix}")

pr_title("Generating and resolving OOBIs")

# ACME and Employee OOBI Exchange
acme_oobi = exec(f"kli oobi generate --name {acme_keystore_name} --alias {acme_aid_alias} --role witness")
employee_oobi = exec(f"kli oobi generate --name {employee_keystore_name} --alias {employee_aid_alias} --role witness")

!kli oobi resolve --name {acme_keystore_name} \
    --oobi-alias {employee_aid_alias} \
    --oobi {employee_oobi}

!kli oobi resolve --name {employee_keystore_name} \
    --oobi-alias {acme_aid_alias} \
    --oobi {acme_oobi}

# Employee and Sub-contractor OOBI Exchange
subcontractor_oobi = exec(f"kli oobi generate --name {subcontractor_keystore_name}  --alias {subcontractor_aid_alias} --role witness")

!kli oobi resolve --name {employee_keystore_name} \
    --oobi-alias {subcontractor_aid_alias} \
    --oobi {subcontractor_oobi}

!kli oobi resolve --name {subcontractor_keystore_name} \
    --oobi-alias {employee_aid_alias} \
    --oobi {employee_oobi}

pr_message("OOBI connections established.")

pr_continue()
```

    Proceeding with deletion of '/usr/local/var/keri/' without confirmation.
    ✅ Successfully removed: /usr/local/var/keri/


    
      Initializing keystores  
    


    KERI Keystore created at: /usr/local/var/keri/ks/acme_ks
    KERI Database created at: /usr/local/var/keri/db/acme_ks
    KERI Credential Store created at: /usr/local/var/keri/reg/acme_ks
    
    Loading 3 OOBIs...


    http://witness-demo:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller?name=Wan&tag=witness succeeded
    http://witness-demo:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller?name=Wes&tag=witness succeeded
    http://witness-demo:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller?name=Wil&tag=witness succeeded


    KERI Keystore created at: /usr/local/var/keri/ks/employee_ks
    KERI Database created at: /usr/local/var/keri/db/employee_ks
    KERI Credential Store created at: /usr/local/var/keri/reg/employee_ks
    
    Loading 3 OOBIs...


    http://witness-demo:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller?name=Wan&tag=witness succeeded
    http://witness-demo:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller?name=Wes&tag=witness succeeded
    http://witness-demo:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller?name=Wil&tag=witness succeeded


    KERI Keystore created at: /usr/local/var/keri/ks/subcontractor_ks
    KERI Database created at: /usr/local/var/keri/db/subcontractor_ks
    KERI Credential Store created at: /usr/local/var/keri/reg/subcontractor_ks
    
    Loading 3 OOBIs...


    http://witness-demo:5642/oobi/BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha/controller?name=Wan&tag=witness succeeded
    http://witness-demo:5643/oobi/BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM/controller?name=Wes&tag=witness succeeded
    http://witness-demo:5644/oobi/BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX/controller?name=Wil&tag=witness succeeded


    
      Initializing AIDs  
    


    Waiting for witness receipts...


    Prefix  EPRQCgop2CyHCC8tabtl9iJOw1ryr2eXofO6IF7NQtQ-
    	Public key 1:  DH8BuO089xEDuARHaXAq4V9Uqv2w7Pz4wBnb4AM9ojSa
    


    Waiting for witness receipts...


    Prefix  EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB
    	Public key 1:  DC3EVHqOWepm_r3wN33_IOlrNKsAuza6o0HLjMJdpdYn
    


    Waiting for witness receipts...


    Prefix  ECfW_ag06odaG2HgGqggnP697j17ZU7nM3dRb4ixpc9B
    	Public key 1:  DA9-YlRY7pXgaaKlhkppFTAZ88r4v68ooNc8s-FuW5hc
    


    
      Initializing Credential Registries  
    


    Waiting for TEL event witness receipts


    Sending TEL events to witnesses


    Registry:  acme_mgr_registry(EONNB-EvoWMm7aXTQpFDsN7hGCk-ZvRQEzdd0AZxox2r) 
    	created for Identifier Prefix:  EPRQCgop2CyHCC8tabtl9iJOw1ryr2eXofO6IF7NQtQ-


    Waiting for TEL event witness receipts


    Sending TEL events to witnesses


    Registry:  employee_access_registry(ECBgjw1OO2ZVr4U0_513HpnyRNtXmCBQ-UIY-ttC0n1Y) 
    	created for Identifier Prefix:  EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB


    
    ACME AID: EPRQCgop2CyHCC8tabtl9iJOw1ryr2eXofO6IF7NQtQ-
    
    
    Employee AID: EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB
    
    
    Sub-contractor AID: ECfW_ag06odaG2HgGqggnP697j17ZU7nM3dRb4ixpc9B
    
    
      Generating and resolving OOBIs  
    


    http://witness-demo:5642/oobi/EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB/witness resolved


    http://witness-demo:5642/oobi/EPRQCgop2CyHCC8tabtl9iJOw1ryr2eXofO6IF7NQtQ-/witness resolved


    http://witness-demo:5642/oobi/ECfW_ag06odaG2HgGqggnP697j17ZU7nM3dRb4ixpc9B/witness resolved


    http://witness-demo:5642/oobi/EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB/witness resolved


    
    OOBI connections established.
    
    
      You can continue ✅  
    
    


## Schema Definitions

We need two ACDC schemas as shown below. The non-metadata attributes are also shown below:
- Role Schema (`role_schema.json`): For the credential ACME issues to the Employee.
  - Attributes
    - `roleTitle`
    - `department` 
- Access Schema (`access_schema.json`): For the credential the Employee issues to the Sub-contractor. This schema will include definitions for an `e` (edges) section to specify the I2I link and an `r` (rules) section.
  - Attributes
    - `buildingId`
    - `accessLevel`
  - Edges
    - `manager_endorsement` (points to Role Schema ACDC)

<div class="alert alert-info">
<b>ℹ️ NOTE</b><hr>
For this notebook,the schemas have been SAIDified and made available on a schema server (a simple webserver hosting schema files as JSON). The SAIDification process was covered in the "SAIDifying ACDC Schemas" notebook.

### Role Schema

This schema defines the structure of the "Role Credential." It has a structure that is rather similar to the other schemas presented so far during the training:

- Filename: `role_schema.json` (content shown SAIDified)


```python
role_schema_path = "config/schemas/role_schema.json" 
pr_title(f"Schema: {role_schema_path}")

role_schema_said = get_schema_said(role_schema_path)
pr_message(f"Schema SAID: {role_schema_said}")

pr_message(f"Retrieving Role Schema from Server:")
!curl -s http://vlei-server:7723/oobi/{role_schema_said} | jq

pr_continue()
```

    
      Schema: config/schemas/role_schema.json  
    
    
    Schema SAID: ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw
    
    
    Retrieving Role Schema from Server:
    


    {
      "$id": "ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw",
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "RoleCredential",
      "description": "Credential signifying a role within an organization.",
      "type": "object",
      "credentialType": "RoleCredential",
      "version": "1.0.0",
      "properties": {
        "v": {
          "description": "Credential Version String",
          "type": "string"
        },
        "d": {
          "description": "Credential SAID",
          "type": "string"
        },
        "u": {
          "description": "One time use nonce",
          "type": "string"
        },
        "i": {
          "description": "Issuer AID",
          "type": "string"
        },
        "ri": {
          "description": "Registry SAID",
          "type": "string"
        },
        "s": {
          "description": "Schema SAID",
          "type": "string"
        },
        "a": {
          "oneOf": [
            {
              "description": "Attributes block SAID",
              "type": "string"
            },
            {
              "$id": "EFmgKWjhXaH2MYUmlNy5-t8Y6SHZ0InHriOkyAnI4777",
              "description": "Attributes block",
              "type": "object",
              "properties": {
                "d": {
                  "description": "Attributes data SAID",
                  "type": "string"
                },
                "i": {
                  "description": "Issuee AID (Employee's AID)",
                  "type": "string"
                },
                "dt": {
                  "description": "Issuance date time",
                  "type": "string",
                  "format": "date-time"
                },
                "roleTitle": {
                  "description": "The title of the role.",
                  "type": "string"
                },
                "department": {
                  "description": "The department the employee belongs to.",
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "required": [
                "d",
                "i",
                "dt",
                "roleTitle",
                "department"
              ]
            }
          ]
        }
      },
      "additionalProperties": false,
      "required": [
        "v",
        "d",
        "i",
        "ri",
        "s",
        "a"
      ]
    }


    
      You can continue ✅  
    
    


### Access Schema
This schema defines the "Access Credential". It includes an `e` (edges) section for the `I2I` link to the Role Credential and an `r` (rules) section for a usage policy.

Filename: `access_schema.json` (content shown SAIDified)



```python
access_schema_path = "config/schemas/access_schema.json" 
pr_title(f"Schema: {access_schema_path}")

access_schema_said = get_schema_said(access_schema_path)
pr_message(f"Schema SAID: {access_schema_said}")

pr_message(f"Retrieving Access Schema from Server:")
!curl -s http://vlei-server:7723/oobi/{access_schema_said} | jq

pr_continue()
```

    
      Schema: config/schemas/access_schema.json  
    
    
    Schema SAID: EF2zX3g5YDyHMSjgsK4OayZMFmLRMxcAJfW363JhBOfD
    
    
    Retrieving Access Schema from Server:
    


    {
      "$id": "EF2zX3g5YDyHMSjgsK4OayZMFmLRMxcAJfW363JhBOfD",
      "$schema": "http://json-schema.org/draft-07/schema#",
      "title": "AccessCredential",
      "description": "Credential granting access to a specific building or area, endorsed by a manager.",
      "type": "object",
      "credentialType": "AccessCredential",
      "version": "1.0.0",
      "properties": {
        "v": {
          "description": "Credential Version String",
          "type": "string"
        },
        "d": {
          "description": "Credential SAID",
          "type": "string"
        },
        "u": {
          "description": "One time use nonce",
          "type": "string"
        },
        "i": {
          "description": "Issuer AID (Employee's AID)",
          "type": "string"
        },
        "ri": {
          "description": "Registry SAID",
          "type": "string"
        },
        "s": {
          "description": "Schema SAID",
          "type": "string"
        },
        "a": {
          "oneOf": [
            {
              "description": "Attributes block SAID",
              "type": "string"
            },
            {
              "$id": "EOxa7LAD2BoA9tk9n0CW4zH7nF91DP1g_Pjz1wC_FuNw",
              "description": "Attributes block",
              "type": "object",
              "properties": {
                "d": {
                  "description": "Attributes data SAID",
                  "type": "string"
                },
                "i": {
                  "description": "Issuee AID (Sub-contractor's AID)",
                  "type": "string"
                },
                "dt": {
                  "description": "Issuance date time",
                  "type": "string",
                  "format": "date-time"
                },
                "buildingId": {
                  "description": "Identifier for the building access is granted to.",
                  "type": "string"
                },
                "accessLevel": {
                  "description": "Level of access granted.",
                  "type": "string"
                }
              },
              "additionalProperties": false,
              "required": [
                "d",
                "i",
                "dt",
                "buildingId",
                "accessLevel"
              ]
            }
          ]
        },
        "e": {
          "oneOf": [
            {
              "description": "Edges block SAID",
              "type": "string"
            },
            {
              "$id": "EI8RvTM23u-pQDK-KpDUBWOKbiOW8fpnzktVVBCLy55N",
              "description": "Edges block",
              "type": "object",
              "properties": {
                "d": {
                  "description": "Edges block SAID",
                  "type": "string"
                },
                "manager_endorsement": {
                  "description": "Link to the Manager Credential that endorses this access",
                  "type": "object",
                  "properties": {
                    "n": {
                      "description": "Issuer credential SAID",
                      "type": "string"
                    },
                    "s": {
                      "description": "SAID of required schema of the credential pointed to by this node",
                      "type": "string",
                      "const": "ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw"
                    },
                    "o": {
                      "description": "Operator indicating this node is the issuer",
                      "type": "string",
                      "const": "I2I"
                    }
                  },
                  "additionalProperties": false,
                  "required": [
                    "n",
                    "s",
                    "o"
                  ]
                }
              },
              "additionalProperties": false,
              "required": [
                "d",
                "manager_endorsement"
              ]
            }
          ]
        },
        "r": {
          "oneOf": [
            {
              "description": "Rules block SAID",
              "type": "string"
            },
            {
              "$id": "EKDmqq14KgthMAV23sCbzgdFFjT-v9x01toUsyfyi2uU",
              "description": "Rules governing the use of this access credential.",
              "type": "object",
              "properties": {
                "d": {
                  "description": "Rules block SAID",
                  "type": "string"
                },
                "usageDisclaimer": {
                  "description": "Usage Disclaimer",
                  "type": "object",
                  "properties": {
                    "l": {
                      "description": "Associated legal language",
                      "type": "string",
                      "const": "This mock credential grants no actual access. For illustrative use only."
                    }
                  }
                }
              },
              "additionalProperties": false,
              "required": [
                "d",
                "usageDisclaimer"
              ]
            }
          ]
        }
      },
      "additionalProperties": false,
      "required": [
        "v",
        "d",
        "i",
        "ri",
        "s",
        "a",
        "e",
        "r"
      ]
    }


    
      You can continue ✅  
    
    


## Resolving Schema OOBIs
All parties need to resolve the OOBIs for these schemas from the schema server to be able to either issue, receive, present, or receive presentations of credentials using these schemas.


```python
pr_title("Resolving schema OOBIs")

role_schema_oobi = f"http://vlei-server:7723/oobi/{role_schema_said}"
access_schema_oobi = f"http://vlei-server:7723/oobi/{access_schema_said}"

# ACME Corp
!kli oobi resolve --name {acme_keystore_name} \
    --oobi-alias "role_schema" --oobi {role_schema_oobi}

!kli oobi resolve --name {acme_keystore_name} \
    --oobi-alias "access_schema" --oobi {access_schema_oobi}

# Employee
!kli oobi resolve --name {employee_keystore_name} \
    --oobi-alias "role_schema" --oobi {role_schema_oobi}

!kli oobi resolve --name {employee_keystore_name} \
    --oobi-alias "access_schema" --oobi {access_schema_oobi}

# Sub-contractor
!kli oobi resolve --name {subcontractor_keystore_name} \
    --oobi-alias "role_schema" --oobi {role_schema_oobi}

!kli oobi resolve --name {subcontractor_keystore_name} \
    --oobi-alias "access_schema" --oobi {access_schema_oobi}

pr_message("Schema OOBIs resolved.")
pr_continue()
```

    
      Resolving schema OOBIs  
    


    http://vlei-server:7723/oobi/ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw resolved


    http://vlei-server:7723/oobi/EF2zX3g5YDyHMSjgsK4OayZMFmLRMxcAJfW363JhBOfD resolved


    http://vlei-server:7723/oobi/ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw resolved


    http://vlei-server:7723/oobi/EF2zX3g5YDyHMSjgsK4OayZMFmLRMxcAJfW363JhBOfD resolved


    http://vlei-server:7723/oobi/ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw resolved


    http://vlei-server:7723/oobi/EF2zX3g5YDyHMSjgsK4OayZMFmLRMxcAJfW363JhBOfD resolved


    
    Schema OOBIs resolved.
    
    
      You can continue ✅  
    
    


## Issuing credentials

Now that the setup is complete and the schemas are available, its necessary to create the credential chain. 


### Step 1: Role Credential Issuance

The Keystores, AIDs, and Credential Registry for ACME Corporation were created during the initial setup. The next step is to create the credential that grants the "Engineering Manager" role to the employee.

**ACME Creates Role Credential Data**

Create a JSON file `role_cred_data.json` with the attributes for this specific credential


```python
pr_title("Creating role credential data")

!echo '{ \
    "roleTitle": "Engineering Manager", \
    "department": "Technology Innovations" \
}' > config/credential_data/role_cred_data.json

!cat config/credential_data/role_cred_data.json | jq

pr_continue()
```

    
      Creating role credential data  
    


    {
      "roleTitle": "Engineering Manager",
      "department": "Technology Innovations"
    }


    
      You can continue ✅  
    
    


**ACME Issues Role Credential to Employee**

Now that the credential data is in the file the next step is to create the credential with `!kli vc create`


```python
pr_title("Creating Role credential")

issue_time_acme = exec("kli time")
!kli vc create --name {acme_keystore_name} \
    --alias {acme_aid_alias} \
    --registry-name {acme_registry_name} \
    --schema {role_schema_said} \
    --recipient {employee_aid_prefix} \
    --data "@./config/credential_data/role_cred_data.json" \
    --time {issue_time_acme}

role_credential_said = exec(f"kli vc list --name {acme_keystore_name} --alias {acme_aid_alias} --issued --said --schema {role_schema_said}")
pr_message(f"Role Credential SAID: {role_credential_said}")

pr_continue()
```

    
      Creating Role credential  
    


    Waiting for TEL event witness receipts


    Sending TEL events to witnesses


    EEy7jb0V3U8MucFutlRulbQ9eIYWNDrm7Jsbuzg144aZ has been created.


    
    Role Credential SAID: EEy7jb0V3U8MucFutlRulbQ9eIYWNDrm7Jsbuzg144aZ
    
    
      You can continue ✅  
    
    


**IPEX Transfer: ACME Grants, Engineering Manager Employee Admits Role Credential**

Next, perform the IPEX transfer as done in previous ACDC issuance examples. Afterwards, the employee will have the role credential.


```python
pr_title("Transferring credential (ipex grant)")

time = exec("kli time")
!kli ipex grant --name {acme_keystore_name} \
    --alias {acme_aid_alias} \
    --said {role_credential_said} \
    --recipient {employee_aid_prefix} \
    --time {time}

pr_title("Admitting credential (ipex admit)")
# Employee polls for the grant and admits it
employee_grant_msg_said = exec(f"kli ipex list --name {employee_keystore_name} --alias {employee_aid_alias} --poll --said")
time = exec("kli time")
!kli ipex admit --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --said {employee_grant_msg_said} \
    --time {time}

# Employee lists the received credential
pr_message("\nEngineering Manager Employee received Role Credential:")
!kli vc list --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --verbose

pr_continue()
```

    
      Transferring credential (ipex grant)  
    


    Sending message ECQY9YW7oFmRqOi2AJ1Mw69xtuBLTQc4-W37jbvKStgQ to EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB


    ... grant message sent


    
      Admitting credential (ipex admit)  
    


    Sending admit message to EPRQCgop2CyHCC8tabtl9iJOw1ryr2eXofO6IF7NQtQ-


    ... admit message sent


    
    
    Engineering Manager Employee received Role Credential:
    


    Current received credentials for employee (EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB):
    
    Credential #1: EEy7jb0V3U8MucFutlRulbQ9eIYWNDrm7Jsbuzg144aZ
        Type: RoleCredential
        Status: Issued ✔
        Issued by EPRQCgop2CyHCC8tabtl9iJOw1ryr2eXofO6IF7NQtQ-
        Issued on 2025-09-12T04:10:33.313202+00:00
        Full Credential:
    	{
    	  "v": "ACDC10JSON0001c2_",
    	  "d": "EEy7jb0V3U8MucFutlRulbQ9eIYWNDrm7Jsbuzg144aZ",
    	  "i": "EPRQCgop2CyHCC8tabtl9iJOw1ryr2eXofO6IF7NQtQ-",
    	  "ri": "EONNB-EvoWMm7aXTQpFDsN7hGCk-ZvRQEzdd0AZxox2r",
    	  "s": "ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw",
    	  "a": {
    	    "d": "EJZ5Ab5kkrz-hGU7-e5K7mV_LCpEFn1e1t7aNttCZwWu",
    	    "i": "EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB",
    	    "dt": "2025-09-12T04:10:33.313202+00:00",
    	    "roleTitle": "Engineering Manager",
    	    "department": "Technology Innovations"
    	  }
    	}


    
      You can continue ✅  
    
    


### Step 2: Access Credential Data properties - edge, rules, and attributes

The Employee, now holding the "Role Credential", issues the "Access Credential" to the Sub-contractor. This new credential will link to the Role Credential via an `I2I` edge and include a "Usage Disclaimer" rule. For this it is necessary to create JSON files for the attributes (`access_cred_data.json`), the edge (`access_cred_edge.json`), and the rule (`access_cred_rule.json`). The attributes, edges, and rules properties are displayed below.

#### Attributes Data

The attributes of the Role Credential include generic mock data to represent an access claim such as `buildingId` and `accessLevel` with sample data provided below.


```python
pr_message("Acces Credential Attributes")

access_cred_data_file_path = "config/credential_data/access_cred_data.json"

access_data = {
    "buildingId": "HQ-EastWing", 
    "accessLevel": "Level 2 - Common Areas & Labs" 
}

with open(access_cred_data_file_path, 'w') as f:
    json.dump(access_data, f, indent=4)

!cat {access_cred_data_file_path} | jq

```

    
    Acces Credential Attributes
    


    {
      "buildingId": "HQ-EastWing",
      "accessLevel": "Level 2 - Common Areas & Labs"
    }


#### Edge Data and SAID Calculation

When creating the Edge Data, the `manager_endorsement` edge is defined to link to the Role Credential ACDC by using the SAID of the Role Credential said, stored in the `role_credential_said` variable. The schema SAID `s` for this edge is the schema identifier, or SAID, of the Role Credential schema and is set to `role_schema_said`. The operator `o` is set to `I2I`.

To make this edge block verifiable, the `!kli saidify --file` command is used. When this command is executed, KERI processes the JSON content of the specified file and calculates a Self-Addressing Identifier (SAID) for its entire content. Crucially, the command then modifies the input file in place:
- It adds (or updates, if already present) a top-level field named `d` within the JSON structure of the file.
- The value of this `d` field is set to the newly calculated SAID.


```python
pr_message("Access Credential Edges")

access_cred_edge_file_path = "config/credential_data/access_cred_edge.json"

access_edge = {
    "d": "",
    "manager_endorsement": {
        "n": role_credential_said,
        "s": role_schema_said,
        "o": "I2I"
    }
}

with open(access_cred_edge_file_path, 'w') as f:
    json.dump(access_edge, f, indent=4)

!kli saidify --file {access_cred_edge_file_path}

!cat {access_cred_edge_file_path} | jq

```

    
    Access Credential Edges
    


    {
      "d": "EKkr7dXYEw4HFBpppP36I4hNmR6F_0XOHwduQSMGYTRF",
      "manager_endorsement": {
        "n": "EEy7jb0V3U8MucFutlRulbQ9eIYWNDrm7Jsbuzg144aZ",
        "s": "ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw",
        "o": "I2I"
      }
    }


#### Rule Data

The rule section `usageDisclaimer` contains a simple legal disclaimer. Take notice that this data property is also SAIDified.


```python
pr_message("Access Credential Rules")

access_cred_rule_file_path = "config/credential_data/access_cred_rule.json"

access_rule = {
  "d": "",
  "usageDisclaimer": {
    "l": "This mock credential grants no actual access. For illustrative use only."
  }
}

with open(access_cred_rule_file_path, 'w') as f:
    json.dump(access_rule, f, indent=4)

!kli saidify --file {access_cred_rule_file_path}

!cat {access_cred_rule_file_path} | jq

```

    
    Access Credential Rules
    


    {
      "d": "EGVMk928-Fz4DK2NSvZgtG0JJrMlrpxvuxBKPvFxfPSQ",
      "usageDisclaimer": {
        "l": "This mock credential grants no actual access. For illustrative use only."
      }
    }


### Step 3: Employee Creates Access Credential for Sub-contractor

Now, the Employee uses `kli vc create` with the attributes, SAIDified edges, and SAIDified rules files to issue the Access Credential. Notice the additional parameters `--edges` and `rules` to supply the data properties to the command.


```python
time = exec("kli time")
!kli vc create --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --registry-name {employee_registry_name} \
    --schema {access_schema_said} \
    --recipient {subcontractor_aid_alias} \
    --data  "@./config/credential_data/access_cred_data.json" \
    --edges "@./config/credential_data/access_cred_edge.json" \
    --rules "@./config/credential_data/access_cred_rule.json" \
    --time {time}

access_credential_said = exec(f"kli vc list --name {employee_keystore_name} --alias {employee_aid_alias} --issued --said --schema {access_schema_said}")
pr_message(f"Access Credential SAID: {access_credential_said}")

pr_continue()

```

    Waiting for TEL event witness receipts


    Sending TEL events to witnesses


    EA0-zXenxtqAZa5rjjCmxjAqhOVqFo-8WgqBmkvHUWEk has been created.


    
    Access Credential SAID: EA0-zXenxtqAZa5rjjCmxjAqhOVqFo-8WgqBmkvHUWEk
    
    
      You can continue ✅  
    
    


### Step 4: Employee Grants, Sub-contractor Admits Access Credential

The commands below show using IPEX to both grant the Access Credential from the manager employee and to admit the Access Credential as the sub-contractor. Finally the sub-contractor's credentials are listed with `kli vc list` to show that the Access Credential has been received.


```python
pr_title("Transferring Access Credential from Employee to Sub-contractor")

time = exec("kli time")
!kli ipex grant --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --said {access_credential_said} \
    --recipient {subcontractor_aid_prefix} \
    --time {time}

pr_title("Sub-contractor admitting Access Credential")
# Sub-contractor polls for the grant and admits it
subcontractor_grant_msg_said = exec(f"kli ipex list --name {subcontractor_keystore_name} \
    --alias {subcontractor_aid_alias} --poll --said")
time = exec("kli time")
!kli ipex admit --name {subcontractor_keystore_name} \
    --alias {subcontractor_aid_alias} \
    --said {subcontractor_grant_msg_said} \
    --time {time}

# Sub-contractor lists the received credential
pr_message("\nSub-contractor's received Access Credential:")
!kli vc list --name {subcontractor_keystore_name} \
    --alias {subcontractor_aid_alias} \
    --verbose

pr_continue()
```

    
      Transferring Access Credential from Employee to Sub-contractor  
    


    Sending message EJ6irfCsL-VdfLeX2g2QlqfB8cljJJjAFiF65C0o7kin to ECfW_ag06odaG2HgGqggnP697j17ZU7nM3dRb4ixpc9B


    ... grant message sent


    
      Sub-contractor admitting Access Credential  
    


    Sending admit message to EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB


    ... admit message sent


    
    
    Sub-contractor's received Access Credential:
    


    Current received credentials for subcontractor (ECfW_ag06odaG2HgGqggnP697j17ZU7nM3dRb4ixpc9B):
    
    Credential #1: EA0-zXenxtqAZa5rjjCmxjAqhOVqFo-8WgqBmkvHUWEk
        Type: AccessCredential
        Status: Issued ✔
        Issued by EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB
        Issued on 2025-09-12T04:10:52.883270+00:00
        Full Credential:
    	{
    	  "v": "ACDC10JSON000320_",
    	  "d": "EA0-zXenxtqAZa5rjjCmxjAqhOVqFo-8WgqBmkvHUWEk",
    	  "i": "EGKtnumYK9aJ0aKtX6WS8TPcVt2W8tYrlTbFwvX9T-IB",
    	  "ri": "ECBgjw1OO2ZVr4U0_513HpnyRNtXmCBQ-UIY-ttC0n1Y",
    	  "s": "EF2zX3g5YDyHMSjgsK4OayZMFmLRMxcAJfW363JhBOfD",
    	  "a": {
    	    "d": "EEnD2_uJHltlMdRJ_XZYE9YtutyPIwdYWlErX9JUeMol",
    	    "i": "ECfW_ag06odaG2HgGqggnP697j17ZU7nM3dRb4ixpc9B",
    	    "dt": "2025-09-12T04:10:52.883270+00:00",
    	    "buildingId": "HQ-EastWing",
    	    "accessLevel": "Level 2 - Common Areas & Labs"
    	  },
    	  "e": {
    	    "d": "EKkr7dXYEw4HFBpppP36I4hNmR6F_0XOHwduQSMGYTRF",
    	    "manager_endorsement": {
    	      "n": "EEy7jb0V3U8MucFutlRulbQ9eIYWNDrm7Jsbuzg144aZ",
    	      "s": "ENWatfUaeryBqvGnG7VdILVcqk84_eoxmiaJYguJXaRw",
    	      "o": "I2I"
    	    }
    	  },
    	  "r": {
    	    "d": "EGVMk928-Fz4DK2NSvZgtG0JJrMlrpxvuxBKPvFxfPSQ",
    	    "usageDisclaimer": {
    	      "l": "This mock credential grants no actual access. For illustrative use only."
    	    }
    	  }
    	}


    
      You can continue ✅  
    
    


The output for the Sub-contractor's received AccessCredential clearly shows:
- The attributes (`a` section) for building access.
- The edge (`e` section) with manager_endorsement linking to the RoleCredential's SAID (`n`) and using the `I2I` operator (`o`).
- The rule (`r` section) with the `usageDisclaimer`.

<div class="alert alert-primary">
<b>📝 SUMMARY</b><hr>
This notebook demonstrated the creation of a chained ACDC relationship using an Issuer-To-Issuee (I2I) edge and the inclusion of a rule:
<ol>
<li><b>Initial Setup:</b> Keystores, AIDs (ACME, Employee, Sub-contractor), and credential registries (for ACME and Employee) were initialized. OOBI connections were established between relevant parties.</li>
<li><b>Schema Preparation:</b> Two schemas, role_schema.json (for ACME to Employee) and access_schema.json (for Employee to Sub-contractor), were defined. The access_schema.json included definitions for an e (edges) section and an r (rules) section. Both schemas were assumed to be SAIDified and resolvable via a schema server.</li>
<li><b>Role Credential Issuance (ACME to Employee):</b>
<ul>
<li>ACME created data for the Role Credential.</li>
<li>ACME issued the Role Credential to the Employee's AID using <code>kli vc create</code>.</li>
<li>The Role Credential was transferred to the Employee via IPEX (<code>kli ipex grant</code> from ACME, <code>kli ipex admit</code> by Employee).</li>
</ul>
</li>
<li><b>Access Credential Issuance (Employee to Sub-contractor):</b>
<ul>
<li>The Employee created data for the Access Credential attributes.</li>
<li>A separate JSON file for the <b>edge</b> was created. This edge (<code>manager_endorsement</code>) pointed to the SAID of the Role Credential received by the Employee (<code>role_credential_said</code>), specified the Role Credential's schema SAID, and used the <code>"o": "I2I"</code> operator. This edge file was SAIDified using <code>kli saidify --file</code>, which populates its <code>d</code> field.</li>
<li>A separate JSON file for the <b>rule</b> (<code>usageDisclaimer</code>) was created and SAIDified using <code>kli saidify --file</code>.</li>
<li>The Employee issued the Access Credential to the Sub-contractor's AID using <code>kli vc create</code>, referencing the attributes data file, the SAIDified edge file (<code>--edges</code>), and the SAIDified rule file (<code>--rules</code>).</li>
<li>The Access Credential was transferred to the Sub-contractor via IPEX.</li>
</ul>
</li>
<li><b>Verification:</b> The Sub-contractor's received Access Credential clearly displayed the attributes, the I2I edge linking to the Employee's Role Credential, and the embedded rule.</li>
</ol>
This process illustrates how KERI and ACDC can model real-world endorsement scenarios where the authority to issue a credential is derived from another verifiable credential held by the issuer and how additional conditions can be embedded using rules.
</div>

[<- Prev (ACDC Edges and Rules)](101_75_ACDC_Edges_and_Rules.ipynb) | [Next (ACDC Chained Credentials NI2I) ->](101_85_ACDC_Chained_Credentials_NI2I.ipynb)
