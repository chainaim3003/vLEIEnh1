# ACDC Issuance with KLI: Not-Issuer-To-Issuee

<b>🎯 OBJECTIVE</b><hr>
Demonstrate how to issue an ACDC that utilizes a Not-Issuer-To-Issuee (NI2I) edge, illustrating how to reference another parent credential for context without implying the issuer of the child is the issuee of the linked parent ACDC. This notebook will also show how a rule can be embedded in the credential. We will implement the **"Linking to an External Training Course"** scenario.
</div>

<div class="alert alert-danger">
    <b>ℹ️⚠️ BUG ALERT</b><hr>
    <p>Currently the <code>NI2I</code> operator does not work due to a bug. For more details on this and other issues, please see the <a href="900_05_Known_Issues.ipynb">Known Issues Section</a>.

The material will be updated once the bug is resolved. For now you can skip this notebook.</p>
</div>

## Scenario Recap: Linking to an External Training Course

This notebook focuses on the practical KLI commands for implementing an `NI2I` chained credentials. For a detailed theoretical explanation of ACDC Edges, Edge Operators, and Rules, please refer to the **[Advanced ACDC Features: Edges, Edge Operators, and Rules](101_75_ACDC_Edges_and_Rules.ipynb)** notebook. To summarize the scenario:

- A Company issues a **"Skill Certified"** ACDC to an employee, after the employee completes an internal assessment.
- To add verifiable, supporting context to this certification, the "Skill Certified" ACDC can contain an `NI2I` (Not-Issuer-To-Issuee) edge. This edge would point to a "Course Completion" ACDC that the employee had previously received from an external, third-party Training Provider.
- This `NI2I` link signifies that while the external training is acknowledged as relevant evidence, the Company's authority to issue its own skill certification is independent and does not derive from the Training Provider's credential.
- The "Employee Skill Certified" ACDC will also include a simple rule in its `r` section.

## Initial Setup: Keystores, AIDs, Registries, and OOBIs

We begin by setting up the three participants in our scenario:

- Training Provider (`training_provider_aid`): The entity issuing the course credential.
- Company (`company_aid`): The entity issuing the skill credential that references the course credential.
- Employee (`employee_aid`): The entity who is the subject (issuee) of both credentials.

For each participant, we will:
- Initialize a KERI keystore.
- Incept an AID, using a default witness configuration.
- Establish OOBI connections between the necessary parties (Training Provider ➡️ Employee, and Company ➡️ Employee) to enable secure communication.
- For the two issuers (Training Provider and Company), we will also incept a credential registry to manage the lifecycle of the credentials they issue.


```python
# Imports and Utility functions
from scripts.utils import exec, clear_keri, pr_title, pr_message, pr_continue
from scripts.saidify import get_schema_said
import json, os

clear_keri()

# Training Provider Keystore and AID
training_provider_keystore_name = "training_provider_ks"
training_provider_salt = exec("kli salt")
training_provider_aid_alias = "training_provider"
training_provider_registry_name = "training_provider_reg"

# Company Keystore and AID
company_keystore_name = "company_ks"
company_salt = exec("kli salt")
company_aid_alias = "company"
company_registry_name = "company_skill_reg"

# Employee Keystore and AID
employee_keystore_name = "employee_ks"
employee_salt = exec("kli salt")
employee_aid_alias = "employee"

pr_title("Initializing keystores")

!kli init --name {training_provider_keystore_name} \
    --nopasscode \
    --salt {training_provider_salt} \
    --config-dir ./config \
    --config-file keystore_init_config.json

!kli init --name {company_keystore_name} \
    --nopasscode \
    --salt {company_salt} \
    --config-dir ./config \
    --config-file keystore_init_config.json

!kli init --name {employee_keystore_name} \
    --nopasscode \
    --salt {employee_salt} \
    --config-dir ./config \
    --config-file keystore_init_config.json

pr_title("Initializing AIDs")

!kli incept --name {training_provider_keystore_name} \
    --alias {training_provider_aid_alias} \
    --file ./config/aid_inception_config.json

!kli incept --name {company_keystore_name} \
    --alias {company_aid_alias} \
    --file ./config/aid_inception_config.json

!kli incept --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --file ./config/aid_inception_config.json

pr_title("Initializing Credential Registries")

!kli vc registry incept --name {training_provider_keystore_name} \
    --alias {training_provider_aid_alias} \
    --registry-name {training_provider_registry_name}

!kli vc registry incept --name {company_keystore_name} \
    --alias {company_aid_alias} \
    --registry-name {company_registry_name}

training_provider_aid_prefix = exec(f"kli aid --name {training_provider_keystore_name} --alias {training_provider_aid_alias}")
company_aid_prefix = exec(f"kli aid --name {company_keystore_name} --alias {company_aid_alias}")
employee_aid_prefix = exec(f"kli aid --name {employee_keystore_name} --alias {employee_aid_alias}")

pr_message(f"Training Provider AID: {training_provider_aid_prefix}")
pr_message(f"Company AID: {company_aid_prefix}")
pr_message(f"Employee AID: {employee_aid_prefix}")

pr_title("Generating and resolving OOBIs")

# Training Provider and Employee OOBI Exchange
training_provider_oobi = exec(f"kli oobi generate --name {training_provider_keystore_name} --alias {training_provider_aid_alias} --role witness")
employee_oobi = exec(f"kli oobi generate --name {employee_keystore_name} --alias {employee_aid_alias} --role witness")
company_oobi = exec(f"kli oobi generate --name {company_keystore_name} --alias {company_aid_alias} --role witness")

!kli oobi resolve --name {training_provider_keystore_name} \
    --oobi-alias {employee_aid_alias} \
    --oobi {employee_oobi}
           
!kli oobi resolve --name {employee_keystore_name} \
    --oobi-alias {training_provider_aid_alias} \
    --oobi {training_provider_oobi}

# Company and Employee OOBI Exchange

!kli oobi resolve --name {company_keystore_name} \
    --oobi-alias {employee_aid_alias} \
    --oobi {employee_oobi}

!kli oobi resolve --name {employee_keystore_name} \
    --oobi-alias {company_aid_alias} \
    --oobi {company_oobi}

# Company and Training Provider -----------------------------------
!kli oobi resolve --name {company_keystore_name} \
    --oobi-alias {training_provider_aid_alias} \
    --oobi {training_provider_oobi}

!kli oobi resolve --name {training_provider_keystore_name} \
    --oobi-alias {company_aid_alias} \
    --oobi {company_oobi}

pr_message("OOBI connections established.")
pr_continue()
```

## Schema Definitions

For this scenario, we require two distinct ACDC schemas:
- **Course Completion Schema** (' course_completion_schema.json' ): Defines the credential issued by the Training Provider.
- **Employee Skill Schema** (' employee_skill_schema.json'): Defines the credential issued by the Company, which will include the `NI2I` edge and a rule.

<div class="alert alert-info">
<b>ℹ️ NOTE</b><hr>
For this notebook, the schemas have been pre-SAIDified and are available on our mock schema server. The process of SAIDifying schemas was detailed in a previous notebook.
</div>

### Course Completion Schema

This schema defines a basic credential for certifying the completion of a training course. It's a standard, non-chained credential.

Filename: `course_completion_schema.json`


```python
course_schema_path = "config/schemas/course_completion_schema.json"
pr_title(f"Schema: {course_schema_path}")

course_schema_said = get_schema_said(course_schema_path)
pr_message(f"Schema SAID: {course_schema_said}")

pr_message(f"Retrieving Schema from Server:")
!curl -s http://vlei-server:7723/oobi/{course_schema_said} | jq

pr_continue()
```

### Employee Skill Schema
This schema defines the credential issued by the Company to the Employee. It includes an `e` (edges) section with an `NI2I` operator to reference the "Course Completion" credential and an `r` (rules) section for a verification policy.

Filename: `employee_skill_schema.json`


```python
skill_schema_path = "config/schemas/skill_certified_schema.json"
pr_title(f"Schema: {skill_schema_path}")

skill_schema_said = get_schema_said(skill_schema_path)
pr_message(f"Schema SAID: {skill_schema_said}")

pr_message(f"Retrieving Schema from Server:")
!curl -s http://vlei-server:7723/oobi/{skill_schema_said} | jq

pr_continue()
```

## Resolving Schema OOBIs

All three participants must resolve the OOBIs for both schemas to ensure they can understand and validate the credentials.


```python
pr_title("Resolving schema OOBIs")

course_schema_oobi = f"http://vlei-server:7723/oobi/{course_schema_said}"
skill_schema_oobi = f"http://vlei-server:7723/oobi/{skill_schema_said}"

# Participants resolving Course Completion Schema
!kli oobi resolve --name {training_provider_keystore_name} \
    --oobi-alias "course_schema" \
    --oobi {course_schema_oobi}

!kli oobi resolve --name {company_keystore_name} \
    --oobi-alias "course_schema" \
    --oobi {course_schema_oobi}

!kli oobi resolve --name {employee_keystore_name} \
    --oobi-alias "course_schema" \
    --oobi {course_schema_oobi}

# Participants resolving Employee Skill Schema
!kli oobi resolve --name {training_provider_keystore_name} \
    --oobi-alias "skill_schema" \
    --oobi {skill_schema_oobi}

!kli oobi resolve --name {company_keystore_name} \
    --oobi-alias "skill_schema" \
    --oobi {skill_schema_oobi}

!kli oobi resolve --name {employee_keystore_name} \
    --oobi-alias "skill_schema" \
    --oobi {skill_schema_oobi}

pr_message("Schema OOBIs resolved.")
pr_continue()
```

## Issuing credentials
Now that the setup is complete and the schemas are available, it's necessary to create the credential chain starting with the Course Completion credential and later the Employee Skill credential.

### Step 1: Course Completion Credential Issuance (Training Provider to Employee)
First, the Training Provider issues the "Course Completion" credential to the Employee. This establishes the base credential that will be referenced later.

**Create Course Completion Credential Data**  

Create a JSON file with the specific attributes for the course completion.


```python
pr_title("Creating Course Completion credential data")

!echo '{ \
    "courseName": "Advanced Cryptographic Systems", \
    "courseLevel": "Expert", \
    "completionDate": "2024-09-15" \
}' > config/credential_data/course_cred_data.json

!cat config/credential_data/course_cred_data.json | jq

pr_continue()
```

### Training Provider Issues Credential
The Training Provider uses `kli vc create` to issue the credential.


```python
pr_title("Creating Course Completion credential")

issue_time_training = exec("kli time")
!kli vc create --name {training_provider_keystore_name} \
    --alias {training_provider_aid_alias} \
    --registry-name {training_provider_registry_name} \
    --schema {course_schema_said} \
    --recipient {employee_aid_prefix} \
    --data "@./config/credential_data/course_cred_data.json" \
    --time {issue_time_training}

course_credential_said = exec(f"kli vc list --name {training_provider_keystore_name} --alias {training_provider_aid_alias} --issued --said --schema {course_schema_said}")
pr_message(f"Course Credential SAID: {course_credential_said}")

pr_continue()
```

**IPEX Transfer: Training Provider Grants, Employee Admits**  

The credential is then transferred to the Employee using the standard IPEX grant/admit flow.


```python
pr_title("Transferring Course Completion credential (IPEX)")

time = exec("kli time")
!kli ipex grant --name {training_provider_keystore_name} \
    --alias {training_provider_aid_alias} \
    --said {course_credential_said} \
    --recipient {employee_aid_prefix} \
    --time {time}

# Employee polls for the grant and admits it
print("Polling mailboxes for IPEX Grant messages to admit...")
employee_grant_msg_said = exec(f"kli ipex list --name {employee_keystore_name} --alias {employee_aid_alias} --poll --said")
time = exec("kli time")
!kli ipex admit --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --said {employee_grant_msg_said} \
    --time {time}

pr_message("\nEmployee's received Course Completion Credential:")
!kli vc list --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --verbose

pr_continue()
```

### Step 2: Employee Skill Credential Issuance (Company to Employee)
Now, the Company issues the "Employee Skill Certified" credential, which will link to the one the Employee just received.

Create Data Properties for Skill Credential
We need to create three separate JSON files for the attributes, the NI2I edge, and the rule.

**Attributes Data**   

Generic mock data to represent an access claim.


```python
pr_message("Employee Skill Credential Attributes")

skill_cred_data_file_path = "config/credential_data/skill_cred_data.json"

skill_data = {
    "skillName": "Secure System Design",
    "skillLevel": "Proficient",
    "assessmentDate": "2025-01-20"
}

with open(skill_cred_data_file_path, 'w') as f:
    json.dump(skill_data, f, indent=4)
    
!cat {skill_cred_data_file_path} | jq
```

**Edge Data (NI2I) and SAIDification**  

The edge data is created, linking to the `course_credential_said` obtained in the previous step. The operator `o` is explicitly set to `NI2I`. This file is then SAIDified using `kli saidify` to populate its `d` field.


```python
pr_message("Employee Skill Credential Edges (NI2I)")

skill_cred_edge_file_path = "config/credential_data/skill_cred_edge.json"

skill_edge = {
    "d": "",
    "supporting_evidence": {
        "n": course_credential_said,
        "s": course_schema_said,
        "o": "NI2I"
    }
}

with open(skill_cred_edge_file_path, 'w') as f:
    json.dump(skill_edge, f, indent=4)
    
!kli saidify --file {skill_cred_edge_file_path}

!cat {skill_cred_edge_file_path} | jq
```

**Rule Data and SAIDification**  

The rule data is created and SAIDified.


```python
pr_message("Employee Skill Credential Rules")

skill_cred_rule_file_path = "config/credential_data/skill_cred_rule.json"

skill_rule = {
  "d": "",
  "verification_policy": {
    "l": "Verification of this skill certification requires checking the validity of supporting evidence."
  }
}
with open(skill_cred_rule_file_path, 'w') as f:
    json.dump(skill_rule, f, indent=4)
    
!kli saidify --file {skill_cred_rule_file_path}
!cat {skill_cred_rule_file_path} | jq
```

#### Company Issues Skill Credential

The Company now creates the chained credential using kli vc create, supplying the attributes, edges, and rules files.


```python
time = exec("kli time")

!kli vc create --name {company_keystore_name} \
    --alias {company_aid_alias} \
    --registry-name {company_registry_name} \
    --schema {skill_schema_said} \
    --recipient {employee_aid_prefix} \
    --data  "@./config/credential_data/skill_cred_data.json" \
    --edges "@./config/credential_data/skill_cred_edge.json" \
    --rules "@./config/credential_data/skill_cred_rule.json" \
    --time {time}

skill_credential_said = exec(f"kli vc list --name {company_keystore_name} --alias {company_aid_alias} --issued --said --schema {skill_schema_said}")

pr_message(f"Employee Skill Credential SAID: {skill_credential_said}")

pr_continue()
```

### Step 3: Company Grants, Employee Admits Skill Credential

The final step is to transfer the newly created chained credential to the Employee.


```python
pr_title("Transferring Employee Skill Credential from Company to Employee")
time = exec("kli time")
!kli ipex grant --name {company_keystore_name} \
    --alias {company_aid_alias} \
    --said {skill_credential_said} \
    --recipient {employee_aid_prefix} \
    --time {time}

pr_title("Employee admitting Skill Credential")
# Employee polls for the grant and admits it
employee_skill_grant_msg_said = exec(f"kli ipex list --name {employee_keystore_name} --alias {employee_aid_alias} --poll --said")
time = exec("kli time")
!kli ipex admit --name {employee_keystore_name} \
    --alias {employee_aid_alias} \
    --said {employee_skill_grant_msg_said} \
    --time {time}

pr_message("\nEmployee's received Employee Skill Credential:")
!kli vc list --name {employee_keystore_name} --alias {employee_aid_alias} --said {skill_credential_said} --verbose

pr_continue()
```

When you view the final "Employee Skill Credential" held by the Employee, you will see:

- The attributes (`a` section) for the certified skill.
- The edge (`e` section) with `supporting_evidence` linking to the Course Completion ACDC's SAID (n) and using the `NI2I` operator (`o`).
- The rule (`r` section) with the `verification_policy`.

This confirms the successful creation and issuance of a chained credential using an NI2I edge to provide external, verifiable context.

<div class="alert alert-primary">
<b>📝 SUMMARY</b><hr>
This notebook demonstrated the creation of a chained ACDC relationship using a Not-Issuer-To-Issuee (NI2I) edge and the inclusion of a rule.
<ol>
<li><b>Setup:</b> Three participants (Training Provider, Company, Employee) were initialized with keystores, AIDs, and credential registries for the issuers. OOBI connections were established between them.</li>
<li><b>Schema Preparation:</b> Two schemas, one for "Course Completion" and another for "Skill Certified" (which included definitions for <code>e</code> and <code>r</code> sections), were resolved by all parties from a schema server.</li>
<li><b>Base Credential Issuance (Training Provider to Employee):</b>
<ul>
<li>The Training Provider issued a "Course Completion" ACDC to the Employee.</li>
<li>This credential was transferred via IPEX and admitted by the Employee. The SAID of this credential was saved for the next step.</li>
</ul>
</li>
<li><b>Chained Credential Issuance (Company to Employee):</b>
<ul>
<li>The Company prepared the data for the "Employee Skill" ACDC.</li>
<li>An <b>edge file</b> was created, linking to the previously issued "Course Completion" ACDC's SAID and explicitly using the <b><code>"o": "NI2I"</code></b> operator. This file was SAIDified.</li>
<li>A <b>rule file</b> was created with a custom policy and was also SAIDified.</li>
<li>The Company issued the "Employee Skill" ACDC using <code>kli vc create</code>, supplying the attributes, edges, and rules files.</li>
<li>This second credential was transferred to the Employee via IPEX.</li>
</ul>
</li>
<li><b>Verification:</b> The final ACDC held by the Employee contained the skill attributes, the NI2I edge pointing to the course certificate as supporting evidence, and the embedded verification policy rule, successfully demonstrating the NI2I use case.</li>
</ol>
</div>


```python
# from scripts.saidify import process_schema_file

# # Run the saidify script
# process_schema_file("./config/schemas/course_completion_schema.bak.json", "./config/schemas/course_completion_schema.json", True)
# process_schema_file("./config/schemas/skill_certified_schema.bak.json", "./config/schemas/skill_certified_schema.json", True)
```

[<- Prev (ACDC Chained Credentials I2I)](101_80_ACDC_Chained_Credentials_I2I.ipynb) | [Next (KERIA Signify) ->](102_05_KERIA_Signify.ipynb)
