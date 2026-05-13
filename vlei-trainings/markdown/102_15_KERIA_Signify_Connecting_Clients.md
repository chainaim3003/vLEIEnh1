# SignifyTS: Securely Connecting Controllers

<div class="alert alert-primary">
  <b>🎯 OBJECTIVE</b><hr>
  Explain how to establish a secure, mutually authenticated connection between two KERIA/SignifyTS controllers using Out-of-Band Introductions (OOBIs) and the challenge/response protocol to enhance trust.
</div>

## Controller and AID Setup

This notebook focuses on connecting two independent controllers using the KERIA/Signify architecture. This involves two `SignifyClient` instances, each managing its own AID, establishing contact (node discovery), and then mutually authenticating each to the other using the challenge signing and verification process. Conceptually, these steps mirror the `kli` process for connecting and verifying controllers yet are executed through the `signify-ts` library interacting with KERIA agents.

You will begin by setting up two distinct `SignifyClient` instances, which we'll call `clientA` (representing a controller Alfred) and `clientB` (representing a controller Betty). Each client will:
1.  Generate a unique `bran` (passcode).
2.  Instantiate `SignifyClient`.
3.  Boot and connect to its KERIA agent, establishing its Client AID and the delegated Agent AID.
4.  Create a primary AID (let's call them `aidA` for Alfred and `aidB` for Betty) with a set of predefined witnesses.

The specifics of client creation, booting, connecting, and basic AID inception using `signify-ts` were covered in the "KERIA-Signify Basic Operations" notebook. You will apply those principles below:



```typescript
import { randomPasscode, ready, SignifyClient, Tier } from 'npm:signify-ts';

const url = 'http://keria:3901';
const bootUrl = 'http://keria:3903';

// Inception request parameters
const inceptionArgs = {
    toad: 3,
    wits: [  
        'BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha',
        'BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM',
        'BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX'
    ]
};

await ready();
console.log("Signify library is ready.")

// ----- Client A (Alfred) -----

const aidAAlias = 'aidA'
const branA = randomPasscode();
const clientA = new SignifyClient(url, branA, Tier.low, bootUrl);

await clientA.boot();
await clientA.connect();
console.log("Agent delegated and ready")

const aInceptionResult = await clientA.identifiers().create(aidAAlias, inceptionArgs);

const aInceptionOperation = await aInceptionResult.op();

const { response: aidA }  = await clientA
    .operations()
    .wait(aInceptionOperation, AbortSignal.timeout(30000));

await clientA.operations().delete(aInceptionOperation.name);

// ----- Client B (Betty) -----

const aidBAlias = 'aidB'
const branB = randomPasscode();
const clientB = new SignifyClient(url, branB, Tier.low, bootUrl);

await clientB.boot();
await clientB.connect();

const bInceptionResult = await clientB.identifiers().create(aidBAlias, inceptionArgs);

const bInceptionOperation = await bInceptionResult.op();

const { response: aidB }  = await clientB
    .operations()
    .wait(bInceptionOperation, AbortSignal.timeout(30000));

await clientB.operations().delete(bInceptionOperation.name);

console.log(`Client A AID Pre: ${aidA.i}\nClient B AID Pre: ${aidB.i}`)
```

    Signify library is ready.


    Agent delegated and ready


    Client A AID Pre: EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU
    Client B AID Pre: EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN


<div class="alert alert-info">
    <b>ℹ️ Note</b><hr> For this demonstration, both clients will connect to the same KERIA instance (defined by <code>url</code> and <code>bootUrl</code>). In a real-world scenario, Alfred and Betty would likely each have their own Signify clients running on their respective devices and interacting with their own (or chosen) KERIA agent instances. The KERIA agent URLs might be different for each. However, the KERI protocol and Signify patterns for connection and authentication remain the same.
</div>

## 

## Assigning Agent End Roles

As discussed in "KERIA-Signify Basics", when a `SignifyClient` connects, it establishes a **Client AID** (which you directly control via the `bran`) and a delegated **Agent AID** (managed by the KERIA agent). For these Agent AIDs to act effectively on behalf of the AIDs we just created (`aidA` and `aidB`), we need to explicitly authorize the Agent AID to act in the `agent` role by assigning an `agent` end role to.

The `agent` role, in this context, signifies that the KERIA Agent AID associated with `clientA` is authorized to manage/interact on behalf of `aidA`, and similarly for `clientB` and `aidB`. This is a crucial step for enabling the KERIA agent to perform tasks like sending messages through the agent mailbox and responding to OOBI requests for these specific identifiers.

Use the `client.identifiers().addEndRole()` method to add the role. This method requires:
- The alias of the identifier granting the authorization (e.g., `aidAAlias`).
- The role to be assigned (e.g., `'agent'`).
- The prefix of the AID being authorized for that role. In this case, it's the prefix of the client's own KERIA Agent AID, accessible via `client.agent!.pre`.


```typescript
// ----- Client A: Assign 'agent' role for aidA to its KERIA Agent AID -----
const agentRole = 'agent';

// Authorize clientA's Agent AID to act as an agent for aidA
const aAddRoleResult = await clientA
    .identifiers()
    .addEndRole(aidAAlias, 
                agentRole, 
                clientA!.agent!.pre // clientA.agent.pre is the Agent AID prefix
               ); 

const aAddRoleOperation = await aAddRoleResult.op();

const { response: aAddRoleResponse } = await clientA
    .operations()
    .wait(aAddRoleOperation, AbortSignal.timeout(30000));

await clientA.operations().delete(aAddRoleOperation.name);

console.log(`Client A: Assigned '${agentRole}' role to KERIA Agent ${clientA.agent!.pre} for AID ${aidA.i}`);

// ----- Client B: Assign 'agent' role for aidB to its KERIA Agent AID -----

// Authorize clientB's Agent AID to act as an agent for aidB
const bAddRoleResult = await clientB
    .identifiers()
    .addEndRole(aidBAlias, 
                agentRole, 
                clientB!.agent!.pre // clientB.agent.pre is the Agent AID prefix
               ); 

const bAddRoleOperation = await bAddRoleResult.op();

const { response: bAddRoleResponse } = await clientB
    .operations()
    .wait(bAddRoleOperation, AbortSignal.timeout(30000));

await clientB.operations().delete(bAddRoleOperation.name);

console.log(`Client B: Assigned '${agentRole}' role to KERIA Agent ${clientB.agent!.pre} for AID ${aidB.i}`);

```

    Client A: Assigned 'agent' role to KERIA Agent EMMKkxBz_28NGq5mmDCzBG7qPVbfNkiO3G25Mh53LI8t for AID EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU


    Client B: Assigned 'agent' role to KERIA Agent EJMGsMkIMUzLZKLG2xMpfhu00H_vLEcKvqyc3uZJkBIa for AID EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN


## Discovery via OOBIs

With the AIDs created and their respective KERIA agents authorized, Alfred (`clientA`, `aidA`) and Betty (`clientB`, `aidB`) need a way to discover each other. This is where Out-of-Band Introductions (OOBIs) are used.

### Generating OOBI URLs

Each client needs to generate an OOBI for its AID (`aidA` and `aidB`). This OOBI is associated with the `agent` role, meaning the OOBI URL (**IURL** for short) will point to an endpoint on their KERIA agent that is authorized to serve information about the AID.

Proceed by generating the IURLs:
- `clientA` generates an OOBI for `aidA` with the role `agent`.
- `clientB` generates an OOBI for `aidB` with the role `agent`.



```typescript
// ----- Generate OOBIs -----

// Client A generates OOBI for aidA (role 'agent')
const oobiA_Result = await clientA.oobis().get(aidAAlias, agentRole);
const oobiA_url = oobiA_Result.oobis[0]; // Assuming at least one OOBI is returned
console.log(`Client A (Alfred) generated OOBI for aidA: ${oobiA_url}`);

// Client B generates OOBI for aidB (role 'agent')
const oobiB_Result = await clientB.oobis().get(aidBAlias, agentRole);
const oobiB_url = oobiB_Result.oobis[0]; // Assuming at least one OOBI is returned
console.log(`Client B (Betty) generated OOBI for aidB: ${oobiB_url}`);

```

    Client A (Alfred) generated OOBI for aidA: http://keria:3902/oobi/EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU/agent/EMMKkxBz_28NGq5mmDCzBG7qPVbfNkiO3G25Mh53LI8t


    Client B (Betty) generated OOBI for aidB: http://keria:3902/oobi/EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN/agent/EJMGsMkIMUzLZKLG2xMpfhu00H_vLEcKvqyc3uZJkBIa


### Resolving OOBI URLs

In a real scenario, Alfred would share `oobiA` with Betty, and Betty would share `oobiB` with Alfred through some non-KERI channel (e.g., email, QR code, messaging app). For this notebook, we'll just store them in variables.

Now perform the OOBI resolution. This means `clientA`'s KERIA agent uses the URL in `oobiB` to fetch `aidB`'s KEL from `clientB`'s KERIA agent. `clientA` then cryptographically verifies this KEL. `clientB` resolves `oobiA` similarly.




```typescript
// Client A resolves Client B's OOBI
const contactBAlias = 'Betty_Contact_for_Alfred'; // Alias for clientA to refer to aidB
console.log(`\nClient A (Alfred) attempting to resolve Betty's OOBI...`);
const AResolveOperation = await clientA.oobis().resolve(oobiB_url, contactBAlias);
const AResolveResponse = await clientA
    .operations()
    .wait(AResolveOperation, AbortSignal.timeout(30000));
await clientA.operations().delete(AResolveOperation.name);
console.log(`Client A resolved Betty's OOBI. Response:`, AResolveResponse.response ? "OK" : "Failed or no response data");

// Client B resolves Client A's OOBI
const contactAAlias = 'Alfred_Contact_for_Betty'; // Alias for clientB to refer to aidA
console.log(`\nClient B (Betty) attempting to resolve Alfred's OOBI...`);
const BResolveOperation = await clientB.oobis().resolve(oobiA_url, contactAAlias);
const BResolveResponse = await clientB
    .operations()
    .wait(BResolveOperation, AbortSignal.timeout(30000));
await clientB.operations().delete(BResolveOperation.name);
console.log(`Client B resolved Alfred's OOBI. Response:`, BResolveResponse.response ? "OK" : "Failed or no response data");

```

    
    Client A (Alfred) attempting to resolve Betty's OOBI...


    Client A resolved Betty's OOBI. Response: OK


    
    Client B (Betty) attempting to resolve Alfred's OOBI...


    Client B resolved Alfred's OOBI. Response: OK


### Verifying Resolved Contacts

Upon successful resolution, each client will have added the other's AID to their local contact list. Use `clientA.contacts().list()` to display the contacts:


```typescript
console.log(`\nVerifying contacts...`);
const AContacts = await clientA.contacts().list(undefined, 'alias', contactBAlias);
console.log(AContacts);

const BContacts = await clientB.contacts().list(undefined, 'alias', contactAAlias);
console.log(BContacts);

```

    
    Verifying contacts...


    [
      {
        alias: "Betty_Contact_for_Alfred",
        oobi: "http://keria:3902/oobi/EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN/agent/EJMGsMkIMUzLZKLG2xMpfhu00H_vLEcKvqyc3uZJkBIa",
        id: "EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN",
        ends: {
          agent: {
            EJMGsMkIMUzLZKLG2xMpfhu00H_vLEcKvqyc3uZJkBIa: { http: "http://keria:3902/" }
          },
          witness: {
            "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha": {
              http: "http://witness-demo:5642/",
              tcp: "tcp://witness-demo:5632/"
            },
            BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM: {
              http: "http://witness-demo:5643/",
              tcp: "tcp://witness-demo:5633/"
            },
            "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX": {
              http: "http://witness-demo:5644/",
              tcp: "tcp://witness-demo:5634/"
            }
          }
        },
        challenges: [],
        wellKnowns: []
      }
    ]


    [
      {
        alias: "Alfred_Contact_for_Betty",
        oobi: "http://keria:3902/oobi/EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU/agent/EMMKkxBz_28NGq5mmDCzBG7qPVbfNkiO3G25Mh53LI8t",
        id: "EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU",
        ends: {
          agent: {
            EMMKkxBz_28NGq5mmDCzBG7qPVbfNkiO3G25Mh53LI8t: { http: "http://keria:3902/" }
          },
          witness: {
            "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha": {
              http: "http://witness-demo:5642/",
              tcp: "tcp://witness-demo:5632/"
            },
            BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM: {
              http: "http://witness-demo:5643/",
              tcp: "tcp://witness-demo:5633/"
            },
            "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX": {
              http: "http://witness-demo:5644/",
              tcp: "tcp://witness-demo:5634/"
            }
          }
        },
        challenges: [],
        wellKnowns: []
      }
    ]


## Mutual Authentication with Challenge-Response

Successfully resolving an OOBI means you've retrieved and cryptographically verified the KEL of the target AID. This establishes the authenticity and integrity of the AID's key history.

However, it does not, by itself, prove conclusively that the entity you are currently communicating with over the network (the one that provided the OOBI or is responding via the OOBI's endpoint) is the legitimate controller of that AID's private keys. A liveness test is needed to prove that the controllers of each AID are actually in control of each respective AID.

This is why the **Challenge-Response** protocol is critical for establishing authenticated control. It serves as that liveness test.

The process, as described in the "Connecting Controllers" notebook for `kli`, is as follows for each pair (e.g., Alfred challenging Betty):

1.  **Generate Challenge**: Alfred (`clientA`) generates a set of unique challenge words.
2.  **Send Challenge (Simulated OOB)**: Alfred communicates these words to Betty through an out-of-band channel (e.g., verbally, secure message). This step is crucial to prevent a Man-in-the-Middle (MITM) on the main KERI connection from intercepting or altering the challenge. For this notebook, we'll print the words.
3.  **Respond to Challenge**: Betty (`clientB`), using `aidB`, signs the exact challenge words received from Alfred. The `respond()` method sends this signed response to Alfred's KERIA agent.
4.  **Verify Response**: Alfred (`clientA`) receives the signed response. His KERIA agent verifies that the signature corresponds to `aidB`'s current authoritative keys (from the KEL he resolved earlier) and that the signed message matches the original challenge words. This is an asynchronous operation.
5.  **Mark as Responded/Authenticated**: If verification is successful, Alfred (`clientA`) marks the challenge for `aidB` as successfully responded to and authenticated. This updates the contact information for Betty in Alfred's client.

This process is then repeated with Betty challenging Alfred.

### Generating Challenge Phrases

Generate a set of random words for each client. `signify-ts` uses `client.challenges().generate()` for this. The strength of the challenge can be specified by the bit length (e.g., 128 or 256 bits, which translates to a certain number of words).


```typescript
// ----- Generate Challenge Words -----

// Client A (Alfred) generates challenge words for Betty
const challengeWordsA = await clientA.challenges().generate(128); // 128-bit strength
console.log("Client A's challenge words for Betty:", challengeWordsA.words);

// Client B (Betty) generates challenge words for Alfred
const challengeWordsB = await clientB.challenges().generate(128); // 128-bit strength
console.log("Client B's challenge words for Alfred:", challengeWordsB.words);
```

    Client A's challenge words for Betty: [
      "ghost",   "color",
      "mandate", "nephew",
      "cook",    "small",
      "myth",    "door",
      "lake",    "turkey",
      "spare",   "what"
    ]


    Client B's challenge words for Alfred: [
      "stable",  "salt",
      "diesel",  "police",
      "cancel",  "sell",
      "portion", "twin",
      "enjoy",   "appear",
      "field",   "crystal"
    ]


### Performing the Challenge-Response Protocol

Perform the following sequence of steps to simulate the challenge/respond protocol.

Assume Alfred has securely (out-of-band) communicated `challengeWordsA.words` to Betty.
- Betty will now use `clientB.challenges().respond()` to sign these words with `aidB` and send the response to `aidA`.
- Alfred will then use `clientA.challenges().verify()` to verify Betty's response. This verification is an operation that needs to be polled.
- Finally, Alfred uses `clientA.challenges().responded()` to mark the contact as authenticated.



```typescript
// ----- Betty (Client B) responds to Alfred's (Client A) challenge -----
console.log(`\nBetty (aidB: ${aidB.i}) responding to Alfred's (aidA: ${aidA.i}) challenge...`);

// Betty uses aidBAlias to sign, targeting aidA.i with challengeWordsA.words
await clientB.challenges().respond(aidBAlias, aidA.i, challengeWordsA.words);
console.log("Betty's response sent.");

// ----- Alfred (Client A) verifies Betty's (Client B) response -----
console.log(`\nAlfred (aidA) verifying Betty's (aidB) response...`);

// Alfred verifies the response allegedly from aidB.i using challengeWordsA.words
const AVerifyBOperation = await clientA.challenges().verify(aidB.i, challengeWordsA.words);

const { response: AVerifyBResponseDetails } = await clientA
    .operations()
    .wait(AVerifyBOperation, AbortSignal.timeout(30000));

await clientA.operations().delete(AVerifyBOperation.name);

const exnSaidB = AVerifyBResponseDetails.exn.d;
console.log("Alfred: Betty's response verified. SAID of exn:", exnSaidB);

// Alfred marks the challenge for Betty (aidB.i) as successfully responded
await clientA.challenges().responded(aidB.i, exnSaidB);
console.log("Alfred: Marked Betty's contact as authenticated.");


// Check Alfred's contact list for Betty's authenticated status
const AContactsAfterAuth = await clientA.contacts().list(undefined, 'alias', contactBAlias);

console.log(AContactsAfterAuth)
```

    
    Betty (aidB: EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN) responding to Alfred's (aidA: EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU) challenge...


    Betty's response sent.


    
    Alfred (aidA) verifying Betty's (aidB) response...


    Alfred: Betty's response verified. SAID of exn: EGaovC5tH_MqxM8E8-lOnp6wD-bw1kO-zqJHxogUUzx7


    Alfred: Marked Betty's contact as authenticated.


    [
      {
        alias: "Betty_Contact_for_Alfred",
        oobi: "http://keria:3902/oobi/EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN/agent/EJMGsMkIMUzLZKLG2xMpfhu00H_vLEcKvqyc3uZJkBIa",
        id: "EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN",
        ends: {
          agent: {
            EJMGsMkIMUzLZKLG2xMpfhu00H_vLEcKvqyc3uZJkBIa: { http: "http://keria:3902/" }
          },
          witness: {
            "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha": {
              http: "http://witness-demo:5642/",
              tcp: "tcp://witness-demo:5632/"
            },
            BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM: {
              http: "http://witness-demo:5643/",
              tcp: "tcp://witness-demo:5633/"
            },
            "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX": {
              http: "http://witness-demo:5644/",
              tcp: "tcp://witness-demo:5634/"
            }
          }
        },
        challenges: [
          {
            dt: "2025-09-12T04:11:28.618000+00:00",
            words: [
              "ghost",   "color",
              "mandate", "nephew",
              "cook",    "small",
              "myth",    "door",
              "lake",    "turkey",
              "spare",   "what"
            ],
            said: "EGaovC5tH_MqxM8E8-lOnp6wD-bw1kO-zqJHxogUUzx7",
            authenticated: true
          }
        ],
        wellKnowns: []
      }
    ]


Now, the roles reverse. Assume Betty (Client B) has securely (out-of-band) communicated `challengeWordsB.words` to Alfred (Client A).
Alfred will use `clientA.challenges().respond()` to sign these words with `aidA` and send the response to `aidB`.
Betty will then use `clientB.challenges().verify()` to verify Alfred's response and `clientB.challenges().responded()` to mark the contact.


```typescript
// ----- Alfred (Client A) responds to Betty's (Client B) challenge -----
console.log(`\nAlfred (aidA: ${aidA.i}) responding to Betty's (aidB: ${aidB.i}) challenge...`);

// Alfred uses aidAAlias to sign, targeting aidB.i with challengeWordsB.words
await clientA.challenges().respond(aidAAlias, aidB.i, challengeWordsB.words);
console.log("Alfred's response sent.");

// ----- Betty (Client B) verifies Alfred's (Client A) response -----
console.log(`\nBetty (aidB) verifying Alfred's (aidA) response...`);

// Betty verifies the response allegedly from aidA.i using challengeWordsB.words
const BVerifyAOperation = await clientB.challenges().verify(aidA.i, challengeWordsB.words);

const { response: BVerifyAResponseDetails } = await clientB
    .operations()
    .wait(BVerifyAOperation, AbortSignal.timeout(30000));

await clientB.operations().delete(BVerifyAOperation.name);


const exnSaidA = BVerifyAResponseDetails.exn.d;
console.log("Betty: Alfred's response verified. SAID of exn:", exnSaidA);

// Betty marks the challenge for Alfred (aidA.i) as successfully responded
await clientB.challenges().responded(aidA.i, exnSaidA);

console.log("Betty: Marked Alfred's contact as authenticated.");


// Check Betty's contact list for Alfred's authenticated status
const BContactsAfterAuth = await clientB.contacts().list(undefined, 'alias', contactAAlias);

console.log(BContactsAfterAuth);
```

    
    Alfred (aidA: EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU) responding to Betty's (aidB: EFr4NDK3M7B28dMWZ0s8drzuuJ_dXg-W5SM1c2fnMXnN) challenge...


    Alfred's response sent.


    
    Betty (aidB) verifying Alfred's (aidA) response...


    Betty: Alfred's response verified. SAID of exn: EGuHjc2voHRKPHwKRFO4H8wygZNBCHEpv3lMT2QfsxKX


    Betty: Marked Alfred's contact as authenticated.


    [
      {
        alias: "Alfred_Contact_for_Betty",
        oobi: "http://keria:3902/oobi/EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU/agent/EMMKkxBz_28NGq5mmDCzBG7qPVbfNkiO3G25Mh53LI8t",
        id: "EEf12hYPxR7v5S9IMEMia1v_lzowPBpGUgMr8sRw5DJU",
        ends: {
          agent: {
            EMMKkxBz_28NGq5mmDCzBG7qPVbfNkiO3G25Mh53LI8t: { http: "http://keria:3902/" }
          },
          witness: {
            "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha": {
              http: "http://witness-demo:5642/",
              tcp: "tcp://witness-demo:5632/"
            },
            BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM: {
              http: "http://witness-demo:5643/",
              tcp: "tcp://witness-demo:5633/"
            },
            "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX": {
              http: "http://witness-demo:5644/",
              tcp: "tcp://witness-demo:5634/"
            }
          }
        },
        challenges: [
          {
            dt: "2025-09-12T04:11:29.215000+00:00",
            words: [
              "stable",  "salt",
              "diesel",  "police",
              "cancel",  "sell",
              "portion", "twin",
              "enjoy",   "appear",
              "field",   "crystal"
            ],
            said: "EGuHjc2voHRKPHwKRFO4H8wygZNBCHEpv3lMT2QfsxKX",
            authenticated: true
          }
        ],
        wellKnowns: []
      }
    ]


If both challenge-response cycles complete successfully, Alfred and Betty have now established a mutually authenticated connection. This provides a strong foundation of trust for subsequent interactions, such as exchanging verifiable credentials.


<div class="alert alert-primary">
<b>📝 SUMMARY</b><hr>
This notebook demonstrated the process of connecting two KERIA/Signify controllers, Alfred (<code>clientA</code>) and Betty (<code>clientB</code>):
<ol>
    <li><b>Initial Setup:</b> Each client was initialized, booted its KERIA agent, connected, and created an Autonomic Identifier(<code>aidA</code> for Alfred, <code>aidB</code> for Betty).</li>
    <li><b>End Role Assignment:</b> The KERIA Agent AID for each client was authorized with an <code>agent</code> end role for its respective AID (<code>aidA</code> and <code>aidB</code>). This allows the KERIA agent to manage these AIDs, such as serving their KELs via OOBIs. This was done using <code>client.identifiers().addEndRole()</code>.</li>
    <li><b>OOBI Generation & Resolution:</b>
        <ul>
            <li>Each client generated an OOBI URL for its AID, specifically for the <code>'agent'</code> role, using <code>client.oobis().get(alias, 'agent')</code>. This OOBI points to their KERIA agent's endpoint for that AID.</li>
            <li>The OOBIs were (simulated) exchanged out-of-band.</li>
            <li>Each client then resolved the other's OOBI using <code>client.oobis().resolve()</code>. This retrieved and cryptographically verified the other's KEL, adding them to their local contact list.</li>
        </ul>
    </li>
    <li><b>Challenge-Response Protocol for Mutual Authentication:</b>
        <ul>
            <li>Each client generated unique challenge words using <code>client.challenges().generate()</code>.</li>
            <li>These words were (conceptually) exchanged out-of-band.</li>
            <li><b>Cycle 1 (Betty responds to Alfred):</b>
                <ul>
                    <li>Betty signed Alfred's challenge words with <code>aidB</code> using <code>clientB.challenges().respond()</code>.</li>
                    <li>Alfred verified Betty's signed response against <code>aidB</code>'s known keys using <code>clientA.challenges().verify()</code>.</li>
                    <li>Upon successful verification, Alfred marked Betty's contact as authenticated using <code>clientA.challenges().responded()</code>.</li>
                </ul>
            </li>
            <li><b>Cycle 2 (Alfred responds to Betty):</b> The same process was repeated with Alfred responding to Betty's challenge.</li>
        </ul>
    </li>
</ol>
Successful completion of both OOBI resolution and the mutual challenge-response protocol establishes a high degree of trust. Both controllers have verified each other's identity (KEL) and cryptographically confirmed that the other party has active control of their private keys. The <code>challengesAuthenticated</code> flag in their contact lists for each other should now be true.
</div>

[<- Prev (KERIA Signify Basic Operations)](102_10_KERIA_Signify_Basic_Operations.ipynb) | [Next (KERIA Signify Key Rotation) ->](102_17_KERIA_Signify_Key_Rotation.ipynb)
