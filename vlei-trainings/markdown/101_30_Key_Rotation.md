# Key Rotation and Pre-rotation

<div class="alert alert-primary">
  <b>🎯 OBJECTIVE</b><hr>
    Understand the importance of key rotation, learn about the pre-rotation mechanism, and see how to execute and verify a rotation using KLI commands.
</div>

## Importance of Key Rotation

Key rotation in a scalable identity system while the identifier remains stable is the hard problem from cryptography and distributed systems that KERI solves. The need to rotate keys guided the entire design of KERI and deeply impacted the vLEI system architecture. This is because securing identity and data involves more than just signing data; robust long-term security for an identity and any data it signs relies on key rotation. The ability to rotate keys is a fundamental security practice that involves changing over time the cryptographic keys associated with an identifier.

Rotating keys is not just about changing them arbitrarily; it's a crucial practice for several reasons:

- **Security Hygiene and Limiting Exposure:** Keys used frequently are more exposed to potential compromise (e.g., residing in memory). Regularly rotating to new keys limits the time window an attacker has if they manage to steal a current key
- **Cryptographic Agility:** Cryptographic algorithms evolve. Vulnerabilities are found in older ones, and stronger new ones emerge (like post-quantum algorithms). Key rotation allows an identifier to smoothly transition to updated cryptography without changing the identifier itself
- **Recovery and Delegation:** You might need to recover control of an identifier if the current keys are lost or compromised, or delegate authority to another entity. Both scenarios typically involve establishing new keys, which is achieved through rotation events


## Understanding Establishment Events

Before diving into key rotation, it's helpful to explain Establishment Events. Not all events recorded in a KEL are the same. Some events specifically define or change the set of cryptographic keys that are authorized to control an identifier (AID) at a particular point in time. These crucial events are called Establishment Events. The two primary types are:   
- **Inception Event (icp):** The very first event that creates the AID and establishes its initial controlling keys
- **Rotation Event (rot):** An event that changes the controlling keys from the set established by the previous Establishment Event to a new set

These Establishment Events form the backbone of an AID's security history, allowing anyone to verify which keys had control at what time. Other event types exist (like interaction events), but they rely on the authority defined by the latest Establishment Event. Interaction events rely on the signing authority of the keys referenced in the latest establishment event. 

## The Pre-Rotation Mechanism

KERI utilizes a strategy called pre-rotation, which decouples the act of key rotation from the preparation for it. With pre-rotation, the cryptographic commitment (a digest of the public keys) for the next key set is embedded within the current key establishment event. This means the next keys can be generated and secured in advance, separate from the currently active operational keys. This pre-commitment acts as a safeguard, as the active private key doesn't grant an attacker the ability to perform the next rotation, as they won't have the corresponding pre-committed private key.

<div class="alert alert-info">
  <b>ℹ️ NOTE</b><hr>
A potential question arises: "If the next keys are kept in the same place as the active operational keys, doesn't that defeat the purpose?" Pre-rotation enables stronger security by decoupling preparation from rotation, but realizing this benefit depends on sound operational practices. Specifically, the pre-committed keys must be stored more securely than the active ones. KERI provides the mechanism; effective key management brings it to life.
</div>

## Performing Key Rotation with KLI

Next, you will complete a key rotation example. Start by setting up a keystore and an identifier.


```python
# Imports and Utility functions
from scripts.utils import clear_keri
clear_keri()

keystore_name="rotation-keystore"
keystore_passcode="xSLg286d4iWiRg2mzGYca"
salt="0ABeuT2dErMrqFE5Dmrnc2Bq"

# Alias for non-transferable AID
aid_alias_non_transferable = "aid-non-transferable"

# Initialize the keystore
!kli init --name {keystore_name} --passcode {keystore_passcode} --salt {salt}

# Incept the AID
!kli incept --name {keystore_name} \
    --passcode {keystore_passcode} \
    --alias {aid_alias_non_transferable} \
    --icount 1 \
    --isith 1 \
    --ncount 1 \
    --nsith 1 \
    --toad 0
```

    Proceeding with deletion of '/usr/local/var/keri/' without confirmation.
    ✅ Successfully removed: /usr/local/var/keri/


    KERI Keystore created at: /usr/local/var/keri/ks/rotation-keystore
    KERI Database created at: /usr/local/var/keri/db/rotation-keystore
    KERI Credential Store created at: /usr/local/var/keri/reg/rotation-keystore
    	aeid: BD-1udeJaXFzKbSUFb6nhmndaLlMj-pdlNvNoN562h3z


    Prefix  BEG5uWt6xB94bIkdGUCjYcBf_ryDgPa7t1GUtVc7lerw
    	Public key 1:  BEG5uWt6xB94bIkdGUCjYcBf_ryDgPa7t1GUtVc7lerw
    


Now, attempt to rotate the keys for this AID, using the command `kli rotate`.
You will see an error message


```python
!kli rotate --name {keystore_name} --alias {aid_alias_non_transferable} --passcode {keystore_passcode}
```

    ERR: Attempt to rotate nontransferable pre=BEG5uWt6xB94bIkdGUCjYcBf_ryDgPa7t1GUtVc7lerw.


The error message says we tried to rotate a nontransferable prefix. What does this mean?

### Transferable vs. Non-Transferable AIDs  

Not all KERI identifiers are designed to have their keys rotated. By default, `kli incept` creates a non-transferable identifier. Here is the difference:

**Non-Transferable AID:**
- Key rotation is not possible. Think of it as a fixed set of keys for an identifier.
- Its control is permanently bound to the initial set of keys established at inception.
- The prefix is derived from these initial keys.
- As a special case, when only a single key pair was used to create a non-transferable AID the public key is directly derivable from the AID prefix itself.
  - This is useful for use cases where you want to avoid sending KELs of non-transferable AIDs and instead infer the one-event KEL and associated public key from the AID.

**Transferable AID:**
- Key rotation is possible. 
- Its control can be transferred (rotated) to new sets of keys over time.
- It uses the pre-rotation mechanism, committing to the next set of keys in each rotation event.
- The prefix is derived from the initial keys. Although authoritative keys will change upon each rotation the prefix will remain the same. This allows the identifier to remain stable even as its underlying controlling keys change.

How does KERI know the difference?

The difference lies in the parameters set during the AID's inception event. Let's look at the inception event data for the non-transferable AID we just created:


```python
!kli status --name {keystore_name} --alias {aid_alias_non_transferable} --passcode {keystore_passcode} --verbose
```

    Alias: 	aid-non-transferable
    Identifier: BEG5uWt6xB94bIkdGUCjYcBf_ryDgPa7t1GUtVc7lerw
    Seq No:	0
    
    Witnesses:
    Count:		0
    Receipts:	0
    Threshold:	0
    
    Public Keys:	
    	1. BEG5uWt6xB94bIkdGUCjYcBf_ryDgPa7t1GUtVc7lerw
    
    
    Witnesses:	
    
    {
     "v": "KERI10JSON0000fd_",
     "t": "icp",
     "d": "EC8pCWrNEdrLD64K1Z7qlYQp7mp6Dq7n30Ze6ElP49pO",
     "i": "BEG5uWt6xB94bIkdGUCjYcBf_ryDgPa7t1GUtVc7lerw",
     "s": "0",
     "kt": "1",
     "k": [
      "BEG5uWt6xB94bIkdGUCjYcBf_ryDgPa7t1GUtVc7lerw"
     ],
     "nt": "0",
     "n": [],
     "bt": "0",
     "b": [],
     "c": [],
     "a": []
    }
    


Look closely at the JSON output at the end (representing the inception event). You'll find these key fields:
- `"nt": "0"`: The threshold required to authorize the next key set is zero.
- `"n": []`: The list of digests for the next public keys is empty.

These two fields mark the AID as non-transferable. No commitment to future keys was made.

### Incepting and Rotating a Transferable Identifier

To enable key rotation, we need to explicitly create a transferable AID using the `--transferable` option during inception and using `--ncount` and `--nsith` equal to 1 (or greater). This tells KLI to:

- Generate not just the initial keys, but also the next set of keys (pre-rotated keys).
- Set the appropriate nt (Next Key Signing Threshold, defined by `nsith`) in the inception event.
- Include the digests of the next public keys in the n field of the inception event.
  
Now create a transferable AID:


```python
# Alias for our transferable AID
aid_alias_transferable = "aid-transferable"

# Create the identifier WITH the --transferable flag
!kli incept --name {keystore_name} \
    --passcode {keystore_passcode} \
    --alias {aid_alias_transferable} \
    --icount 1 \
    --isith 1 \
    --ncount 1 \
    --nsith 1 \
    --toad 0 \
    --transferable
```

    Prefix  EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM
    	Public key 1:  DOdymqdtGJzeoRRSL9C8Suni6ebPaSqQfuEUM_JFkPQx
    


Now, check its status and inception event:


```python
!kli status --name {keystore_name} \
    --passcode {keystore_passcode} \
    --alias {aid_alias_transferable} \
    --verbose
```

    Alias: 	aid-transferable
    Identifier: EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM
    Seq No:	0
    
    Witnesses:
    Count:		0
    Receipts:	0
    Threshold:	0
    
    Public Keys:	
    	1. DOdymqdtGJzeoRRSL9C8Suni6ebPaSqQfuEUM_JFkPQx
    
    
    Witnesses:	
    
    {
     "v": "KERI10JSON00012b_",
     "t": "icp",
     "d": "EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM",
     "i": "EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM",
     "s": "0",
     "kt": "1",
     "k": [
      "DOdymqdtGJzeoRRSL9C8Suni6ebPaSqQfuEUM_JFkPQx"
     ],
     "nt": "1",
     "n": [
      "EO95Pwm8WYG_dIS2-H6LGoXmzOEEnbRljeIjy-Hd7aVx"
     ],
     "bt": "0",
     "b": [],
     "c": [],
     "a": []
    }
    


Compare the JSON output for this transferable AID's inception event with the previous one. You'll notice key differences:
- `"nt": "1"` the next Key Signing Threshold is now 1
- `"n": ["EO95Pwm8WYG_dIS2-H6LGoXmzOEEnbRljeIjy-Hd7aVx"]` The presence of a key digest means that this AID is transferable and has pre-rotated keys ready.


### Performing the Rotation

With the commitment to the next keys in place, we can now successfully rotate the key of the transferable AID. 


```python
!kli rotate --name {keystore_name} \
    --passcode {keystore_passcode} \
    --alias {aid_alias_transferable} 
```

    Prefix  EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM
    New Sequence No.  1
    	Public key 1:  DOkM4enfZoc7w8oVdkXzRaVoCdz8f9aAm2u4kA5CHNcQ


### Examining the Rotation (rot) Event

The kli rotate command performed the key rotation by creating and signing a new establishment event of type `rot`. Let's examine the state of the AID after the rotation:


```python
!kli status --name {keystore_name} \
    --passcode {keystore_passcode} \
    --alias {aid_alias_transferable} \
    --verbose
```

    Alias: 	aid-transferable
    Identifier: EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM
    Seq No:	1
    
    Witnesses:
    Count:		0
    Receipts:	0
    Threshold:	0
    
    Public Keys:	
    	1. DOkM4enfZoc7w8oVdkXzRaVoCdz8f9aAm2u4kA5CHNcQ
    
    
    Witnesses:	
    
    {
     "v": "KERI10JSON00012b_",
     "t": "icp",
     "d": "EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM",
     "i": "EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM",
     "s": "0",
     "kt": "1",
     "k": [
      "DOdymqdtGJzeoRRSL9C8Suni6ebPaSqQfuEUM_JFkPQx"
     ],
     "nt": "1",
     "n": [
      "EO95Pwm8WYG_dIS2-H6LGoXmzOEEnbRljeIjy-Hd7aVx"
     ],
     "bt": "0",
     "b": [],
     "c": [],
     "a": []
    }
    
    {
     "v": "KERI10JSON000160_",
     "t": "rot",
     "d": "EMZIjwx8mBQpTbKa4q-daoxu0Rv5oX-KR0Q3JbQOJG3Z",
     "i": "EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM",
     "s": "1",
     "p": "EAv3ajpSbn807a-HSPuDZm0PFzr6jn58m306dibjrxwM",
     "kt": "1",
     "k": [
      "DOkM4enfZoc7w8oVdkXzRaVoCdz8f9aAm2u4kA5CHNcQ"
     ],
     "nt": "1",
     "n": [
      "EJ9DtlVWW6TKPU0AcXBhx3YYDR5FuF9zXqJQqmqJngU8"
     ],
     "bt": "0",
     "br": [],
     "ba": [],
     "a": []
    }
    


Observe the following changes in the output:

- **Event Type (t):** The latest event shows `"t": "rot"`, indicating it's a rotation event.
- **Digest said (d):** This is the digest of the event block.
- **Sequence Number (s):** The `s` value in the latest event has incremented (from "0" to "1"). Each rotation event increases the sequence number.
- **Current Keys (k):** The public key(s) listed in the `k` field of the latest event have changed. They are revealed as public keys instead of the digest previously listed in the `n` field of the inception event. The previously committed pre-rotated keys are now the active signing keys.
- **Next Keys Signing Threshold (nt):** Is 1, as defined by the `--nsith` parameter during inception
- **New Next Keys (n):** The `n` field in the rotation event contains a new key digest. The rotation process automatically generated the next set of keys for the next potential rotation and committed them.
- **Prefix (i):** has not changed. 

**Understanding the rot Event**

- A `rot` event is an Establishment Event. Like the inception (`icp`) event, it defines the authoritative key state of an AID at a specific point in its history (sequence number).
- Its primary function is to change the key state. It transitions control from the keys established in the previous establishment event to the keys that were pre-rotated (committed to via the n field) in that previous event.
- It simultaneously establishes the commitment (n field and nt threshold) for the next rotation cycle.
- This chaining of events (icp -> rot -> rot -> ...) forms the Key Event Log, and the ability to verify this log using receipts from witnesses is a fundamental concept within KERI.

You have now successfully rotated the keys for a transferable KERI identifier!

<div class="alert alert-primary">
  <b>📝 SUMMARY</b><hr>
<p>
Key rotation is essential for security hygiene, cryptographic agility, and enabling recovery or delegation. KERI uses a "pre-rotation" strategy where the commitment (digest) for the next set of keys is included in the current key establishment event (`icp` or `rot`). This secures the rotation process even if the currently active key is compromised. 
</p>
Performing a rotation (<code>kli rotate</code>) creates a rot event, increments the sequence number, activates the previously pre-rotated keys (revealing them in the k field), and commits to a new set of keys (digest in the n field), all while keeping the AID prefix unchanged. This chained process forms part of the Key Event Log (KEL).
</div>

[<- Prev (Signatures)](101_25_Signatures.ipynb) | [Next (Modes, OOBIs, and Witnesses) ->](101_35_Modes_oobis_and_witnesses.ipynb)
