# SignifyTS: ACDC Presentation and Revocation with IPEX

<div class="alert alert-primary">
<b>🎯 OBJECTIVE</b><hr>
Demonstrate the process of presenting an ACDC (Authentic Chained Data Container) from a Holder to a Verifier using the IPEX protocol with the SignifyTS library and the process of credential revocation.
</div>

<div class="alert alert-info">
<b>ℹ️ NOTE</b><hr>
This section utilizes utility functions (from <code>./scripts_ts/utils.ts</code>) to quickly establish the necessary preconditions for credential presentation. Refer to the <a href="./101_65_ACDC_Issuance.ipynb">ACDC Issuance</a> notebook for a detailed explanation of the setup steps.
</div>

## Prerequisites: Client and Credential Setup 

The client setup process from the previous notebook is reused here.


```typescript
import { randomPasscode, Serder} from 'npm:signify-ts';
import { initializeSignify, 
         initializeAndConnectClient,
         createNewAID,
         addEndRoleForAID,
         generateOOBI,
         resolveOOBI,
         createTimestamp,
         createCredentialRegistry,
         getSchema,
         issueCredential,
         ipexGrantCredential,
         getCredentialState,
         waitForAndGetNotification,
         ipexAdmitGrant,
         markNotificationRead,
         DEFAULT_IDENTIFIER_ARGS,
         DEFAULT_TIMEOUT_MS,
         DEFAULT_DELAY_MS,
         DEFAULT_RETRIES,
         ROLE_AGENT,
         IPEX_GRANT_ROUTE,
         IPEX_ADMIT_ROUTE,
         IPEX_APPLY_ROUTE,
         IPEX_OFFER_ROUTE,
         SCHEMA_SERVER_HOST
       } from './scripts_ts/utils.ts';

// Clients setup
// Initialize Issuer, Holder and Verifier Clients, Create AIDs for each one, assign 'agent' role to the AIDs
// generate and resolve OOBIs 

// Issuer Client
console.log("Creating Issuer...")
const issuerBran = randomPasscode()
const issuerAidAlias = 'issuerAid'
const { client: issuerClient } = await initializeAndConnectClient(issuerBran)
const { aid: issuerAid} = await createNewAID(issuerClient, issuerAidAlias, DEFAULT_IDENTIFIER_ARGS);
await addEndRoleForAID(issuerClient, issuerAidAlias, ROLE_AGENT);
const issuerOOBI = await generateOOBI(issuerClient, issuerAidAlias, ROLE_AGENT);

// Holder Client
console.log("Creating Holder...");
const holderBran = randomPasscode()
const holderAidAlias = 'holderAid'
const { client: holderClient } = await initializeAndConnectClient(holderBran)
const { aid: holderAid} = await createNewAID(holderClient, holderAidAlias, DEFAULT_IDENTIFIER_ARGS);
await addEndRoleForAID(holderClient, holderAidAlias, ROLE_AGENT);
const holderOOBI = await generateOOBI(holderClient, holderAidAlias, ROLE_AGENT);

// Verifier Client
console.log("Creating Verifier...")
const verifierBran = randomPasscode()
const verifierAidAlias = 'verifierAid'
const { client: verifierClient } = await initializeAndConnectClient(verifierBran)
const { aid: verifierAid} = await createNewAID(verifierClient, verifierAidAlias, DEFAULT_IDENTIFIER_ARGS);
await addEndRoleForAID(verifierClient, verifierAidAlias, ROLE_AGENT);
const verifierOOBI = await generateOOBI(verifierClient, verifierAidAlias, ROLE_AGENT);

console.log("Created issuer, holder, and verifier AIDs");

// Clients OOBI Resolution
// Resolve OOBIs to establish connections Issuer-Holder, Holder-Verifier
const issuerContactAlias = 'issuerContact';
const holderContactAlias = 'holderContact';
const verifierContactAlias = 'verifierContact';

await resolveOOBI(issuerClient, holderOOBI, holderContactAlias);
await resolveOOBI(holderClient, issuerOOBI, issuerContactAlias);
await resolveOOBI(verifierClient, holderOOBI, holderContactAlias);
await resolveOOBI(holderClient, verifierOOBI, verifierContactAlias);
await resolveOOBI(issuerClient, verifierOOBI, holderContactAlias); // for sending revocation status

console.log("Resolved agent OOBIs to connect issuer, holder, and verifier");

// Schemas OOBI Resolution
// Resolve the Schemas from the Schema Server (VLEI-Server)
const schemaContactAlias = 'schemaContact';
const schemaSaid = 'EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK';
const schemaOOBI = `http://vlei-server:7723/oobi/${schemaSaid}`;

await resolveOOBI(issuerClient, schemaOOBI, schemaContactAlias);
await resolveOOBI(holderClient, schemaOOBI, schemaContactAlias);
await resolveOOBI(verifierClient, schemaOOBI, schemaContactAlias);

console.log("Resolved schema OOBIs to discover the ACDC schema as issuer, holder, and verifier");

console.log("\n\n✅ Client setup and OOBI resolutions complete.");
```

    Creating Issuer...


    Using Passcode (bran): DXqFqbhriflAbpfHtGhCb


    Client boot process initiated with KERIA agent.


      Client AID Prefix:  EJaE5qzycFObah5TRtXwjr_wJmNT1WX3iQ0XfNHRpcRa


      Agent AID Prefix:   EMzug2qMIcy5dOTmWVaWJFVxLfvFMNCY_sJf_RAFvW7v


    Initiating AID inception for alias: issuerAid


    Successfully created AID with prefix: EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY


    Assigning 'agent' role to KERIA Agent EMzug2qMIcy5dOTmWVaWJFVxLfvFMNCY_sJf_RAFvW7v for AID alias issuerAid


    Successfully assigned 'agent' role for AID alias issuerAid.


    Generating OOBI for AID alias issuerAid with role agent


    Generated OOBI URL: http://keria:3902/oobi/EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY/agent/EMzug2qMIcy5dOTmWVaWJFVxLfvFMNCY_sJf_RAFvW7v


    Creating Holder...


    Using Passcode (bran): BqEf1olUY7fLOJ5HD59lC


    Client boot process initiated with KERIA agent.


      Client AID Prefix:  EEtiYLdoIHKkbur161cbTRdzmKhaOB9ewDPunrZjU3o3


      Agent AID Prefix:   ENB5REtgeq_hge71JzF8jJvxwti169qPgWXTBWOCCtVm


    Initiating AID inception for alias: holderAid


    Successfully created AID with prefix: EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG


    Assigning 'agent' role to KERIA Agent ENB5REtgeq_hge71JzF8jJvxwti169qPgWXTBWOCCtVm for AID alias holderAid


    Successfully assigned 'agent' role for AID alias holderAid.


    Generating OOBI for AID alias holderAid with role agent


    Generated OOBI URL: http://keria:3902/oobi/EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG/agent/ENB5REtgeq_hge71JzF8jJvxwti169qPgWXTBWOCCtVm


    Creating Verifier...


    Using Passcode (bran): DrvtxpOKfaZAIKdMQs9Lr


    Client boot process initiated with KERIA agent.


      Client AID Prefix:  EGdjSZ5qK7aM7rNt90jg8ZlFrDdS6YG-MreHQh4oAKUj


      Agent AID Prefix:   EHWra_FnhyO5V00wTEnW0fhbGsU1mNAPVF2-WVsdI9mb


    Initiating AID inception for alias: verifierAid


    Successfully created AID with prefix: ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy


    Assigning 'agent' role to KERIA Agent EHWra_FnhyO5V00wTEnW0fhbGsU1mNAPVF2-WVsdI9mb for AID alias verifierAid


    Successfully assigned 'agent' role for AID alias verifierAid.


    Generating OOBI for AID alias verifierAid with role agent


    Generated OOBI URL: http://keria:3902/oobi/ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy/agent/EHWra_FnhyO5V00wTEnW0fhbGsU1mNAPVF2-WVsdI9mb


    Created issuer, holder, and verifier AIDs


    Resolving OOBI URL: http://keria:3902/oobi/EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG/agent/ENB5REtgeq_hge71JzF8jJvxwti169qPgWXTBWOCCtVm with alias holderContact


    Successfully resolved OOBI URL. Response: OK


    Contact "holderContact" added/updated.


    Resolving OOBI URL: http://keria:3902/oobi/EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY/agent/EMzug2qMIcy5dOTmWVaWJFVxLfvFMNCY_sJf_RAFvW7v with alias issuerContact


    Successfully resolved OOBI URL. Response: OK


    Contact "issuerContact" added/updated.


    Resolving OOBI URL: http://keria:3902/oobi/EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG/agent/ENB5REtgeq_hge71JzF8jJvxwti169qPgWXTBWOCCtVm with alias holderContact


    Successfully resolved OOBI URL. Response: OK


    Contact "holderContact" added/updated.


    Resolving OOBI URL: http://keria:3902/oobi/ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy/agent/EHWra_FnhyO5V00wTEnW0fhbGsU1mNAPVF2-WVsdI9mb with alias verifierContact


    Successfully resolved OOBI URL. Response: OK


    Contact "verifierContact" added/updated.


    Resolving OOBI URL: http://keria:3902/oobi/ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy/agent/EHWra_FnhyO5V00wTEnW0fhbGsU1mNAPVF2-WVsdI9mb with alias holderContact


    Successfully resolved OOBI URL. Response: OK


    Contact "holderContact" added/updated.


    Resolved agent OOBIs to connect issuer, holder, and verifier


    Resolving OOBI URL: http://vlei-server:7723/oobi/EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK with alias schemaContact


    Successfully resolved OOBI URL. Response: OK


    Contact "schemaContact" added/updated.


    Resolving OOBI URL: http://vlei-server:7723/oobi/EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK with alias schemaContact


    Successfully resolved OOBI URL. Response: OK


    Contact "schemaContact" added/updated.


    Resolving OOBI URL: http://vlei-server:7723/oobi/EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK with alias schemaContact


    Successfully resolved OOBI URL. Response: OK


    Contact "schemaContact" added/updated.


    Resolved schema OOBIs to discover the ACDC schema as issuer, holder, and verifier


    
    
    ✅ Client setup and OOBI resolutions complete.


As you will be conducting a credential presentation in this notebook, let's generate one for use in the presentation workflow. Again, this involves creating a credential registry for the issuer, creating the ACDC credential, and then using IPEX grant and admit actions to send the credential to the holder and finally to the verifier.


```typescript
// Create Issuer Credential Registry
const issuerRegistryName = 'issuerRegistry'
console.log("Creating issuer registry")
const { registrySaid: registrySaid } = await createCredentialRegistry(issuerClient, issuerAidAlias, issuerRegistryName)

// Define credential Claims
const credentialClaims = {
    "eventName":"GLEIF Summit",
    "accessLevel":"staff",
    "validDate":"2026-10-01"
}

// Issuer - Issue Credential
console.log("issuing credential to holder")
const { credentialSaid: credentialSaid} = await issueCredential(
    issuerClient, 
    issuerAidAlias, 
    registrySaid, 
    schemaSaid,
    holderAid.i,
    credentialClaims
)

// Issuer - get credential (with all its data)
const credential = await issuerClient.credentials().get(credentialSaid);

// Issuer - Ipex grant
console.log("granting credential to holder")
const grantResponse = await ipexGrantCredential(
    issuerClient,
    issuerAidAlias, 
    holderAid.i,
    credential
)
console.log("Issuer created and granted credential.")

// Holder - Wait for grant notification
console.log("Holder waiting for credential")
const grantNotifications = await waitForAndGetNotification(holderClient, IPEX_GRANT_ROUTE)
const grantNotification = grantNotifications[0]

// Holder - Admit Grant
const admitResponse = await ipexAdmitGrant(
    holderClient,
    holderAidAlias,
    issuerAid.i,
    grantNotification.a.d
)
console.log("Holder admitting credential")

// Holder - Mark notification
await markNotificationRead(holderClient, grantNotification.i)

// Issuer - Wait for admit notification
console.log("Issuer receiving admit...")
const admitNotifications = await waitForAndGetNotification(issuerClient, IPEX_ADMIT_ROUTE)
const admitNotification = admitNotifications[0]

// Issuer - Mark notification
await markNotificationRead(issuerClient, admitNotification.i)
console.log("\n\n✅ Issuer received admit. Issuance and reception complete.")
```

    Creating issuer registry


    Creating credential registry "issuerRegistry" for AID alias "issuerAid"...


    Successfully created credential registry: EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI


    issuing credential to holder


    Issuing credential from AID "issuerAid" to AID "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG"...


    {
      name: "credential.EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
      metadata: {
        ced: {
          v: "ACDC10JSON0001c4_",
          d: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
          i: "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY",
          ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
          s: "EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK",
          a: {
            d: "EHX-zIC6mi2bqDC7sq9dCu8OgfuFoToMX_iL5q4rtqV_",
            i: "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG",
            eventName: "GLEIF Summit",
            accessLevel: "staff",
            validDate: "2026-10-01",
            dt: "2025-09-12T04:12:11.639000+00:00"
          }
        },
        depends: {
          name: "witness.EP6gx17zzX_JfzCPzEnp4ZuRJffPCauz6CyaZHur60KJ",
          metadata: { pre: "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY", sn: 2 },
          done: false,
          error: null,
          response: null
        }
      },
      done: true,
      error: null,
      response: {
        ced: {
          v: "ACDC10JSON0001c4_",
          d: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
          i: "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY",
          ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
          s: "EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK",
          a: {
            d: "EHX-zIC6mi2bqDC7sq9dCu8OgfuFoToMX_iL5q4rtqV_",
            i: "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG",
            eventName: "GLEIF Summit",
            accessLevel: "staff",
            validDate: "2026-10-01",
            dt: "2025-09-12T04:12:11.639000+00:00"
          }
        }
      }
    }


    Successfully issued credential with SAID: EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG


    granting credential to holder


    AID "issuerAid" granting credential to AID "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG" via IPEX...


    Successfully submitted IPEX grant from "issuerAid" to "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG".


    Issuer created and granted credential.


    Holder waiting for credential


    Waiting for notification with route "/exn/ipex/grant"...


    [Retry] Grant notification not found on attempt #1 of 5


    [Retry] Waiting 5000ms before next attempt...


    AID "holderAid" admitting IPEX grant "ELOWFOpxTIMEle3DLOTlZWGQh3OXgePFXaKmwdHZla1R" from AID "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY"...


    Successfully submitted IPEX admit for grant "ELOWFOpxTIMEle3DLOTlZWGQh3OXgePFXaKmwdHZla1R".


    Holder admitting credential


    Marking notification "0ABrTf1ml6YO_Ch7wnf92WfD" as read...


    Notification "0ABrTf1ml6YO_Ch7wnf92WfD" marked as read.


    Issuer receiving admit...


    Waiting for notification with route "/exn/ipex/admit"...


    Marking notification "0ADeBsGFOHL6YOz-fKg14Twz" as read...


    Notification "0ADeBsGFOHL6YOz-fKg14Twz" marked as read.


    
    
    ✅ Issuer received admit. Issuance and reception complete.


<h2>Full Formal IPEX Credential Presentation Workflow: Apply through Admit</h2>
<p>Now that the Holder possesses the credential, they can present it to a KERI AID acting as sample verifier.</p>

<div class="alert alert-info">
    <b>NOTE: A more interesting verifier - vLEI Reporting API</b>
    <hr/>
    In this instance the verifier does not do anything special with the credential above and beyond receiving the credential presentation. To go beyond simple reception of the credential you may review the GLEIF <a href="https://github.com/GLEIF-IT/sally">vLEI Reporting API verifier sally</a>. This verifier receives IPEX Grant messages, performs cryptographic verification on the chain of credentials, and also performs business logic checks on the types and issuer root of the parent QVI credential.
</div>

<p>Getting back to this simplistic verifier, the workflow in this notebook also uses IPEX which may start with any of the following IPEX operations:
    <ol>
        <li>IPEX Grant: The issuer or holder using an IPEX Grant to share the credential with a verifier.</li>
        <li>IPEX Apply: This includes the whole IPEX chain (apply -> offer -> agree -> grant -> admit): This begins with the Verifier requesting a presentation using IPEX Apply, followed by the Holder's IPEX Offer, followed by the Verifier's IPEX Agree, then the Holder's IPEX Grant, ended by the Verifier's IPEX Admit.</li>
        <li>IPEX Offer: This begins with the holder sending a metadata ACDC, or an ACDC showing the schema (shape) of data to share, to the verifier. The verifier can then respond with an IPEX Agree and the rest of the disclosure workflow with grant and admit can continue, as needed.</li>
    </ol>
</p>

<p>Below we dive into the second option, the longer, whole IPEX chain and show the code snipets you need to follow to do the presentation. If you wanted to start with IPEX Grant in your process then you could skip to step 7 and begin with the IPEX Grant.</p>

### Step 1: Verifier Requests Presentation (Apply)

The Verifier initiates the presentation process by sending an IPEX apply message. This `apply` message is an `exn` message specifying the criteria for the credential they are requesting. This includes the `schemaSaid` and can include specific attributes the credential must have.


```typescript
// Verifier Ipex Apply (Presentation request)

// Prepare the IPEX apply message.
const [apply, sigsApply, _endApply] = await verifierClient.ipex().apply({ //_endApply is not used
    senderName: verifierAidAlias,     // Alias of the Verifier's AID
    schemaSaid: schemaSaid,           // SAID of the schema for the requested credential
    attributes: { eventName:'GLEIF Summit' }, // Specific attributes the credential should have
    recipient: holderAid.i,           // AID of the Holder being asked for the presentation
    datetime: createTimestamp(),      // Timestamp for the apply message
});

// Verifier submits the prepared apply message to the Holder.
const applyOperation = await verifierClient
    .ipex()
    .submitApply(verifierAidAlias, apply, sigsApply, [holderAid.i]);
console.log("Verifier sending IPEX Apply to holder...")

// Wait for the submission operation to complete.
const applyResponse = await verifierClient
    .operations()
    .wait(applyOperation, AbortSignal.timeout(DEFAULT_TIMEOUT_MS));
console.log("IPEX Apply succeeded")

// Clean up the operation.
await verifierClient.operations().delete(applyOperation.name);
console.log("✅ IPEX Apply complete")
```

    Verifier sending IPEX Apply to holder...


    IPEX Apply succeeded


    ✅ IPEX Apply complete


### Step 2: Holder Receives Apply Request

#### Holder Apply Notification and Exchange

The Holder receives a notification for the Verifier's `apply` request. They retrieve the details of this request from the exchange message. After processing, the Holder marks the notification as read.


```typescript
// Holder receives the IPEX apply notification from the Verifier.

let holderApplyNotifications;

// Retry loop for the Holder to receive the apply notification.
for (let attempt = 1; attempt <= DEFAULT_RETRIES ; attempt++) {
    try{
        // List notifications, filtering for unread IPEX_APPLY_ROUTE messages.
        let allNotifications = await holderClient.notifications().list()
        holderApplyNotifications = allNotifications.notes.filter(
            (n) => n.a.r === IPEX_APPLY_ROUTE && n.r === false // where "is read" (n.r) is false.
        )        
        if(holderApplyNotifications.length === 0){ 
            throw new Error("Apply notification not found"); // Throw error to trigger retry
        }
        break; // Exit loop if notification found
    }
    catch (error){    
         console.log(`[Retry] Apply notification not found for Holder on attempt #${attempt} of ${DEFAULT_RETRIES}`);
         if (attempt === DEFAULT_RETRIES) {
             console.error(`[Retry] Max retries (${DEFAULT_RETRIES}) reached for Holder's apply notification.`);
             throw error; 
         }
         console.log(`[Retry] Waiting ${DEFAULT_DELAY_MS}ms before next attempt...`);
         await new Promise(resolve => setTimeout(resolve, DEFAULT_DELAY_MS));
    }
}

const applyNotificationForHolder = holderApplyNotifications[0] // Assuming one notification

console.log("Holder received Apply Notification:");
console.log(applyNotificationForHolder);

// Retrieve the full IPEX apply exchange details.
const applyExchange = await holderClient.exchanges().get(applyNotificationForHolder.a.d);
console.log("\nDetails of Apply Exchange received by Holder:");
console.log(applyExchange);

// Extract the SAID of the apply 'exn' message for use in the offer.
const applyExchangeSaid = applyExchange.exn.d;

// Holder marks the apply notification as read.
await holderClient.notifications().mark(applyNotificationForHolder.i);
console.log("\nHolder's notifications after marking apply as read:");
console.log(await holderClient.notifications().list());

console.log("\n\n✅ Holder notification processing complete.")
```

    [Retry] Apply notification not found for Holder on attempt #1 of 5


    [Retry] Waiting 5000ms before next attempt...


    Holder received Apply Notification:


    {
      i: "0AA8PpMsjBVmBpmvkV_i9iXp",
      dt: "2025-09-12T04:12:19.041059+00:00",
      r: false,
      a: {
        r: "/exn/ipex/apply",
        d: "ECReKB0JTHwQ9eGlqYaK3lHlF5aBGKjsyek4iUkhkHE1",
        m: ""
      }
    }


    
    Details of Apply Exchange received by Holder:


    {
      exn: {
        v: "KERI10JSON0001a0_",
        t: "exn",
        d: "ECReKB0JTHwQ9eGlqYaK3lHlF5aBGKjsyek4iUkhkHE1",
        i: "ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy",
        rp: "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG",
        p: "",
        dt: "2025-09-12T04:12:18.659000+00:00",
        r: "/ipex/apply",
        q: {},
        a: {
          i: "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG",
          m: "",
          s: "EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK",
          a: { eventName: "GLEIF Summit" }
        },
        e: {}
      },
      pathed: {}
    }


    
    Holder's notifications after marking apply as read:


    {
      start: 0,
      end: 1,
      total: 2,
      notes: [
        {
          i: "0ABrTf1ml6YO_Ch7wnf92WfD",
          dt: "2025-09-12T04:12:13.012539+00:00",
          r: true,
          a: {
            r: "/exn/ipex/grant",
            d: "ELOWFOpxTIMEle3DLOTlZWGQh3OXgePFXaKmwdHZla1R",
            m: ""
          }
        },
        {
          i: "0AA8PpMsjBVmBpmvkV_i9iXp",
          dt: "2025-09-12T04:12:19.041059+00:00",
          r: true,
          a: {
            r: "/exn/ipex/apply",
            d: "ECReKB0JTHwQ9eGlqYaK3lHlF5aBGKjsyek4iUkhkHE1",
            m: ""
          }
        }
      ]
    }


    
    
    ✅ Holder notification processing complete.


### Step 3: Holder Finds Matching Credential

The Holder now needs to find a credential in their possession that satisfies the Verifier's `apply` request (matches the schema SAID and any specified attributes). The code below constructs a filter based on the `applyExchange` data and uses it to search the Holder's credentials.

The syntax of the `filter` attribute below sent to the `credentials().list(...)` call is intended to be similar to the MongoDB search syntax and is inspired by it.


```typescript
// The apply operation from the Verifier asks for a specific credential 
// (matching schema and attribute values).
// This code snippet creates a credential filter based on the criteria
// from the applyExchange message received by the Holder.

let filter: { [x: string]: any } = { '-s': applyExchange.exn.a.s }; // Filter by schema SAID
// Add attribute filters from the apply request
for (const key in applyExchange.exn.a.a) { // 'a.a' contains the requested attributes
    filter[`-a-${key}`] = applyExchange.exn.a.a[key];
}

console.log("Constructed filter for matching credentials:");
console.log(filter);

// Holder lists credentials matching the filter.
const matchingCredentials = await holderClient.credentials().list({ filter });

console.log("Matching credentials found by Holder:");
console.log(matchingCredentials); // Should list the EventPass credential issued earlier
console.log("\n\n✅ Matching credential complete.")
```

    Constructed filter for matching credentials:


    {
      "-s": "EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK",
      "-a-eventName": "GLEIF Summit"
    }


    Matching credentials found by Holder:


    [
      {
        sad: {
          v: "ACDC10JSON0001c4_",
          d: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
          i: "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY",
          ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
          s: "EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK",
          a: {
            d: "EHX-zIC6mi2bqDC7sq9dCu8OgfuFoToMX_iL5q4rtqV_",
            i: "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG",
            eventName: "GLEIF Summit",
            accessLevel: "staff",
            validDate: "2026-10-01",
            dt: "2025-09-12T04:12:11.639000+00:00"
          }
        },
        atc: "-IABEEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG0AAAAAAAAAAAAAAAAAAAAAAAEEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
        iss: {
          v: "KERI10JSON0000ed_",
          t: "iss",
          d: "EN-9Mt1MGzZmaTNwchPv-05uYd6LlR6oweGUNS5SGHHO",
          i: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
          s: "0",
          ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
          dt: "2025-09-12T04:12:11.639000+00:00"
        },
        issatc: "-VAS-GAB0AAAAAAAAAAAAAAAAAAAAAACEP6gx17zzX_JfzCPzEnp4ZuRJffPCauz6CyaZHur60KJ",
        pre: "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY",
        schema: {
          "$id": "EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK",
          "$schema": "http://json-schema.org/draft-07/schema#",
          title: "EventPass",
          description: "Event Pass Schema",
          type: "object",
          credentialType: "EventPassCred",
          version: "1.0.0",
          properties: {
            v: { description: "Credential Version String", type: "string" },
            d: { description: "Credential SAID", type: "string" },
            u: { description: "One time use nonce", type: "string" },
            i: { description: "Issuer AID", type: "string" },
            ri: { description: "Registry SAID", type: "string" },
            s: { description: "Schema SAID", type: "string" },
            a: { oneOf: [Array] }
          },
          additionalProperties: false,
          required: [ "v", "d", "i", "ri", "s", "a" ]
        },
        chains: [],
        status: {
          vn: [ 1, 0 ],
          i: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
          s: "0",
          d: "EN-9Mt1MGzZmaTNwchPv-05uYd6LlR6oweGUNS5SGHHO",
          ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
          ra: {},
          a: { s: 2, d: "EP6gx17zzX_JfzCPzEnp4ZuRJffPCauz6CyaZHur60KJ" },
          dt: "2025-09-12T04:12:11.639000+00:00",
          et: "iss"
        },
        anchor: {
          pre: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
          sn: 0,
          d: "EN-9Mt1MGzZmaTNwchPv-05uYd6LlR6oweGUNS5SGHHO"
        },
        anc: {
          v: "KERI10JSON00013a_",
          t: "ixn",
          d: "EP6gx17zzX_JfzCPzEnp4ZuRJffPCauz6CyaZHur60KJ",
          i: "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY",
          s: "2",
          p: "EIbPRr2Z-97Wfw9OfEhrQkzFg7eAkxpAlsSMaZIj1-m-",
          a: [
            {
              i: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
              s: "0",
              d: "EN-9Mt1MGzZmaTNwchPv-05uYd6LlR6oweGUNS5SGHHO"
            }
          ]
        },
        ancatc: [
          "-VBq-AABAACTVQvz7zIGDw8XmxFd89gA31ONU34uNMNr2A9Dhltb1ILjeEb7e1c4_VDHC8zgrhX0KTxtCuNWiJnrnJGnNGcE-BADAADSXCDh_JwLGdkBFhn48oFLRygSzsyh7NFizHc2dDkDVmPR2UiaMrh8frthMj2uVu3ERmuK1NNMj88_lUKpf7QAABD6mI-fDyrdfDCmZjTqjybDpTcCqHhArd9B4Lj4GsVjeI3vZCyUIVyYoXSLGsZJUEY5K8CTg8SDR5CGIS9FceoBACDUx8j9C8Dv0q-scIpnK5sNFJq1vCaXPE6rlR_sVbpmz9XNxPwp0uphkWyC8Q-5sIAci3m-9w_c01j7Eo5LU0QJ-EAB0AAAAAAAAAAAAAAAAAAAAAAA1AAG2025-09-12T04c12c13d153540p00c00"
        ]
      }
    ]


    
    
    ✅ Matching credential complete.


### Step 4: Holder Offers Credential

Assuming a matching credential is found, the Holder prepares an IPEX offer message. This `offer` is intended to include only the metadata ACDC showing only the schema of the eventual full ACDC that will be presented later with an IPEX grant. This offer is sent back to the Verifier.


```typescript
// Holder prepares and submits an IPEX offer message with the matching credential.

// Prepare the IPEX offer message.
const [offer, sigsOffer, endOffer] = await holderClient.ipex().offer({
    senderName: holderAidAlias,                   // Alias of the Holder's AID
    recipient: verifierAid.i,                     // AID of the Verifier
    acdc: new Serder(matchingCredentials[0].sad), // The ACDC being offered (first matching credential)
    applySaid: applyExchangeSaid,                 // SAID of the Verifier's apply 'exn' message this offer is responding to
    datetime: createTimestamp(),                  // Timestamp for the offer message
});

// Holder submits the prepared offer message to the Verifier.
const offerOperation = await holderClient
    .ipex()
    .submitOffer(holderAidAlias, offer, sigsOffer, endOffer, [
        verifierAid.i, // Recipient AID
    ]);
console.log("Submitting Offer from holder to Verifier.")

// Wait for the submission operation to complete.
const offerResponse = await holderClient
    .operations()
    .wait(offerOperation, AbortSignal.timeout(DEFAULT_TIMEOUT_MS));
console.log("Holder submitted IPEX Offer to Verifier.");

// Clean up the operation.
await holderClient.operations().delete(offerOperation.name);
console.log("Holder deleted Offer operation.");
console.log("\n\n✅ Holder IPEX Offer complete.")


```

    Submitting Offer from holder to Verifier.


    Holder submitted IPEX Offer to Verifier.


    Holder deleted Offer operation.


    
    
    ✅ Holder IPEX Offer complete.


### Step 5: Verifier Receives Offer

The Verifier receives a notification for the Holder's `offer`. The Verifier retrieves the exchange details and marks the notification.

An offer is one of the three possible initiating IPEX actions along with Apply and Grant. An IPEX exchange may begin with an Offer to which a receiver, or disclosee, of the Offer would respond with an IPEX Agree, followed by a Grant and an Admit.


```typescript
// Verifier receives the IPEX offer notification from the Holder.

let verifierOfferNotifications;

// Retry loop for the Verifier to receive the offer notification.
for (let attempt = 1; attempt <= DEFAULT_RETRIES ; attempt++) {
    try{
        // List notifications, filtering for unread IPEX_OFFER_ROUTE messages.
        verifierOfferNotifications = await verifierClient.notifications().list(
            (n) => n.a.r === IPEX_OFFER_ROUTE && n.r === false
        );
        if(verifierOfferNotifications.notes.length === 0){ 
            throw new Error("Offer notification not found"); // Throw error to trigger retry
        }
        break; // Exit loop if notification found
    }
    catch (error){    
         console.log(`[Retry] Offer notification not found for Verifier on attempt #${attempt} of ${DEFAULT_RETRIES}`);
         if (attempt === DEFAULT_RETRIES) {
             console.error(`[Retry] Max retries (${DEFAULT_RETRIES}) reached for Verifier's offer notification.`);
             throw error; 
         }
         console.log(`[Retry] Waiting ${DEFAULT_DELAY_MS}ms before next attempt...`);
         await new Promise(resolve => setTimeout(resolve, DEFAULT_DELAY_MS));
    }
}

const offerNotificationForVerifier = verifierOfferNotifications.notes[0]; // Assuming one notification

console.log("Verifier received Offer Notification:");
console.log(offerNotificationForVerifier);

// Retrieve the full IPEX offer exchange details.
const offerExchange = await verifierClient.exchanges().get(offerNotificationForVerifier.a.d);
console.log("\nDetails of Offer Exchange received by Verifier:");
console.log(offerExchange); // This will contain the ACDC presented by the Holder

// Extract the SAID of the offer 'exn' message for use in the agree.
let offerExchangeSaid = offerExchange.exn.d;

// Verifier marks the offer notification as read.
await verifierClient.notifications().mark(offerNotificationForVerifier.i);
console.log("\n\nVerifier's notifications after marking offer as read:");
console.log(await verifierClient.notifications().list());
console.log("\n\n✅ Verifier Offer notification handling complete.")
```

    [Retry] Offer notification not found for Verifier on attempt #1 of 5


    [Retry] Waiting 5000ms before next attempt...


    Verifier received Offer Notification:


    {
      i: "0ABXiV1JPTPLLBfKgoa4MktC",
      dt: "2025-09-12T04:12:24.663702+00:00",
      r: false,
      a: {
        r: "/exn/ipex/offer",
        d: "EBWG4vH1tKw7VZZU-sTF4ZU3TWdye-mQMUw2pn10dSwa",
        m: ""
      }
    }


    
    Details of Offer Exchange received by Verifier:


    {
      exn: {
        v: "KERI10JSON000376_",
        t: "exn",
        d: "EBWG4vH1tKw7VZZU-sTF4ZU3TWdye-mQMUw2pn10dSwa",
        i: "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG",
        rp: "ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy",
        p: "ECReKB0JTHwQ9eGlqYaK3lHlF5aBGKjsyek4iUkhkHE1",
        dt: "2025-09-12T04:12:24.231000+00:00",
        r: "/ipex/offer",
        q: {},
        a: { i: "ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy", m: "" },
        e: {
          acdc: {
            v: "ACDC10JSON0001c4_",
            d: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
            i: "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY",
            ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
            s: "EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK",
            a: {
              d: "EHX-zIC6mi2bqDC7sq9dCu8OgfuFoToMX_iL5q4rtqV_",
              i: "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG",
              eventName: "GLEIF Summit",
              accessLevel: "staff",
              validDate: "2026-10-01",
              dt: "2025-09-12T04:12:11.639000+00:00"
            }
          },
          d: "ECDNeO6oSRg9MRgC5eMchaxsC6l2a84DpRNnK-aQagSX"
        }
      },
      pathed: {}
    }


    
    
    Verifier's notifications after marking offer as read:


    {
      start: 0,
      end: 0,
      total: 1,
      notes: [
        {
          i: "0ABXiV1JPTPLLBfKgoa4MktC",
          dt: "2025-09-12T04:12:24.663702+00:00",
          r: true,
          a: {
            r: "/exn/ipex/offer",
            d: "EBWG4vH1tKw7VZZU-sTF4ZU3TWdye-mQMUw2pn10dSwa",
            m: ""
          }
        }
      ]
    }


    
    
    ✅ Verifier Offer notification handling complete.


### Step 6: Verifier Agrees and Validates

Next, the Verifier, after validating the offered metadata ACDC credential (which signify-ts does implicitly upon processing the offer and preparing the agree), will send an IPEX agree message back to the Holder. This confirms successful receipt and validation of the metadata ACDC credential presented. This means that the verifier has agreed that the schema of the data being sent back is acceptable to the verifier. The actual data is shared later in the IPEX Grant step.


```typescript
// Verifier prepares and submits an IPEX agree message.

// Prepare the IPEX agree message.
const [agree, sigsAgree, _endAgree] = await verifierClient.ipex().agree({
    senderName: verifierAidAlias, // Alias of the Verifier's AID
    recipient: holderAid.i,       // AID of the Holder
    offerSaid: offerExchangeSaid, // SAID of the Holder's offer 'exn' message this agree is responding to
    datetime: createTimestamp(),  // Timestamp for the agree message
});

// Verifier submits the prepared agree message to the Holder.
const agreeOperation = await verifierClient
    .ipex()
    .submitAgree(verifierAidAlias, agree, sigsAgree, [holderAid.i]);
console.log("Verifier submitted IPEX Agree to Holder")

// Wait for the submission operation to complete.
const agreeResponse = await verifierClient
    .operations()
    .wait(agreeOperation, AbortSignal.timeout(DEFAULT_TIMEOUT_MS));
console.log("Verifier IPEX Agree sent");

// Clean up the operation.
await verifierClient.operations().delete(agreeOperation.name);
console.log("Verifier deleted Agree operation");
console.log("\n\n✅ Verifier IPEX Agree complete.")

// At this point, the Verifier has successfully received and validated the metadata ACDC credential.
```

    Verifier submitted IPEX Agree to Holder


    Verifier IPEX Agree sent


    Verifier deleted Agree operation


    
    
    ✅ Verifier IPEX Agree complete.


### Step 7: Holder shares credential with IPEX Grant

The act of sharing a credential and its data with the verifier happens with an IPEX Grant as shown below. This can be the first operation in a chain of IPEX operations or it can be performed after an IPEX Agree. In this case the grant occurs after an agree so we will chain to the prior agreement.


```typescript
// Holder - get credential (with all its data)
const credential = await holderClient.credentials().get(credentialSaid);

// Holder - Ipex grant
console.log("Granting credential from holder to issuer")
const grantResponse = await ipexGrantCredential(
    holderClient,
    holderAidAlias, 
    verifierAid.i,
    credential
)
console.log("✅ Holder granted credential.")
```

    Granting credential from holder to issuer


    AID "holderAid" granting credential to AID "ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy" via IPEX...


    Successfully submitted IPEX grant from "holderAid" to "ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy".


    ✅ Holder granted credential.


After the holder sends the IPEX Grant then the verifier will receive two things:
- The notification of the IPEX Grant
- An IPEX Grant, which is an exchange message, abbreviated as `exn`.

The notification message contains a digest of the `exn` IPEX Grant message, which contains the presented ACDC as an embedded data property. So, to retrieve the ACDC the grant `exn` digest should be retrieved from the `a.d` property of the notification and used to load the 


```typescript
// Verifier - Wait for grant notification
console.log("Verifier waiting for credential")
const grantNotifications = await waitForAndGetNotification(verifierClient, IPEX_GRANT_ROUTE)
const grantNotification = grantNotifications[0]
console.log("Verifier received IPEX Grant notification", grantNotification)

// Retrieve the full IPEX offer exchange details.
const grantExn = await verifierClient.exchanges().get(grantNotification.a.d);
console.log("Details of ACDC embedded in the Grant Exchange received by Verifier:");
const embeddedACDC = grantExn.exn.e.acdc;
console.log(embeddedACDC); // This will contain the ACDC presented by the Holder

console.log("\n\n✅ Verifier IPEX Grant notification processing complete.")
```

    Verifier waiting for credential


    Waiting for notification with route "/exn/ipex/grant"...


    [Retry] Grant notification not found on attempt #1 of 5


    [Retry] Waiting 5000ms before next attempt...


    Verifier received IPEX Grant notification {
      i: "0ACTl0UOevpcP-X4ZLv8Poiu",
      dt: "2025-09-12T04:12:30.597778+00:00",
      r: false,
      a: {
        r: "/exn/ipex/grant",
        d: "ECDH8_eQ0jPpBEnn4IjSJxtSCGmT0jUSQh2qN1zlFwBo",
        m: ""
      }
    }


    Details of ACDC embedded in the Grant Exchange received by Verifier:


    {
      v: "ACDC10JSON0001c4_",
      d: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
      i: "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY",
      ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
      s: "EGUPiCVO73M9worPwR3PfThAtC0AJnH5ZgwsXf6TzbVK",
      a: {
        d: "EHX-zIC6mi2bqDC7sq9dCu8OgfuFoToMX_iL5q4rtqV_",
        i: "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG",
        eventName: "GLEIF Summit",
        accessLevel: "staff",
        validDate: "2026-10-01",
        dt: "2025-09-12T04:12:11.639000+00:00"
      }
    }


    
    
    ✅ Verifier IPEX Grant notification processing complete.


As you see the ACDC has already been received by the verifier. 

This means that the verifier could act on the ACDC directly after receiving the Exchange message for the IPEX Grant containing the ACDC. Sending back an IPEX Admit message is entirely optional and is left up to the architectural design preferences of the individual application implementor. The [vLEI Reporting API verifier (sally)](https://github.com/GLEIF-IT/sally/) used by GLEIF in production follows the model of extracting the ACDC from the IPEX Grant `exn` and does not send back an IPEX Admit message because sending the admit, in this use case, does not yet provide business value. That might change in the future.

This demonstration shows completing the entire formal IPEX workflow by using an IPEX Admit to respond to the IPEX Grant.

### Step 8: Verifier Sends IPEX Admit to the Holder

While a verifier does not have to explicitly admit a credential doing so may provide valuable information to the holder or issuer depending on the use case so that workflow is shown below.


```typescript
// Verifier - Admit Grant
const admitResponse = await ipexAdmitGrant(
    verifierClient,
    verifierAidAlias,
    holderAid.i,
    grantNotification.a.d
)
console.log("Verifier admitting credential")

// Verifier - Mark notification
await markNotificationRead(verifierClient, grantNotification.i)
console.log("\n✅ Verifier marked notification read")
```

    AID "verifierAid" admitting IPEX grant "ECDH8_eQ0jPpBEnn4IjSJxtSCGmT0jUSQh2qN1zlFwBo" from AID "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG"...


    Successfully submitted IPEX admit for grant "ECDH8_eQ0jPpBEnn4IjSJxtSCGmT0jUSQh2qN1zlFwBo".


    Verifier admitting credential


    Marking notification "0ACTl0UOevpcP-X4ZLv8Poiu" as read...


    Notification "0ACTl0UOevpcP-X4ZLv8Poiu" marked as read.


    
    ✅ Verifier marked notification read


You can now view the Verifier's list of notifications to see that the Grant notification has been marked as read.


```typescript
// Verifier shows Grant notification is now read
let notifications;
// Retry loop to fetch notifications.
for (let attempt = 1; attempt <= DEFAULT_RETRIES ; attempt++) {
    try{
        // List notifications, filtering for unread IPEX_GRANT_ROUTE messages.
        let allNotifications = await verifierClient.notifications().list( );
        notifications = allNotifications.notes.filter(
            (n) => n.a.r === IPEX_GRANT_ROUTE // get all notifications even if read
        )        
        if(notifications.length === 0){ 
            throw new Error("Grant notification not found"); // Throw error to trigger retry
        }
        console.log("Found a notification for an IPEX Grant");
        break;     
    }
    catch (error){    
         console.log(`[Retry] Grant notification not found on attempt #${attempt} of ${DEFAULT_RETRIES}`);
         if (attempt === DEFAULT_RETRIES) {
             console.error(`[Retry] Max retries (${DEFAULT_RETRIES}) reached for grant notification.`);
             throw error; 
         }
         console.log(`[Retry] Waiting ${DEFAULT_DELAY_MS}ms before next attempt...`);
         await new Promise(resolve => setTimeout(resolve, DEFAULT_DELAY_MS));
    }
}

const grantNote = notifications[0]  // Assuming only one grant notification for simplicity
console.log("✅ Existing grant notification for verifier now shows as read with 'r: true'");
console.log(grantNote);
```

    Found a notification for an IPEX Grant


    ✅ Existing grant notification for verifier now shows as read with 'r: true'


    {
      i: "0ACTl0UOevpcP-X4ZLv8Poiu",
      dt: "2025-09-12T04:12:30.597778+00:00",
      r: true,
      a: {
        r: "/exn/ipex/grant",
        d: "ECDH8_eQ0jPpBEnn4IjSJxtSCGmT0jUSQh2qN1zlFwBo",
        m: ""
      }
    }


Lastly the holder receives the admit which also means receiving a notification of the IPEX Admit. This notification can be marked as read to signify that the entire formal process is complete as shown below.


```typescript
// Holder - Wait for admit notification
console.log("Holder receiving admit...")
const admitNotifications = await waitForAndGetNotification(holderClient, IPEX_ADMIT_ROUTE)
const admitNotification = admitNotifications[0]

// Issuer - Mark notification
await markNotificationRead(holderClient, admitNotification.i)
console.log("\n\n✅ Holder received admit. Presentation exchange complete.")
```

    Holder receiving admit...


    Waiting for notification with route "/exn/ipex/admit"...


    Marking notification "0AAkUq24By8Kf_s2_TWQtWPh" as read...


    Notification "0AAkUq24By8Kf_s2_TWQtWPh" marked as read.


    
    
    ✅ Holder received admit. Presentation exchange complete.


## Credential Revocation by Issuer

Circumstances may require a credential to be invalidated before its intended expiry or if it has no expiry. This process is known as revocation. Only the original Issuer of a credential can revoke it. Revocation involves the Issuer recording a revocation event in the specific credential's Transaction Event Log (TEL), which is part of the Issuer's credential database. This event is, like all TEL events, anchored to the Issuer's KEL. The issuer may directly tell the holder of the revocation status, which the holder may, in turn, directly tell a verifier, using the IPEX Grant and Admit steps.

The Issuer uses the `issuerClient.credentials().revoke()` method, specifying the alias of their issuing AID and the SAID of the credential to be revoked. This action creates a new event in the TEL associated with the credential, marking its status as revoked.

First, check the credential status before revocation. The status object contains details about the latest event in the credential's TEL. The `et` field indicates the event type (e.g., `iss` for issuance).


```typescript

// Log the credential's status from the Issuer's perspective before revocation.
// The 'status' field shows the latest event in the credential's Transaction Event Log (TEL).
// 'et: "iss"' indicates it's currently in an issued state.
const statusBefore = (await issuerClient.credentials().get(credentialSaid)).status;
console.log("Credential status before revocation:", statusBefore);

// Issuer revokes the credential.
// This creates a revocation event in the credential's TEL within the Issuer's registry.
const revokeResult = await issuerClient.credentials().revoke(issuerAidAlias, credentialSaid); // Changed from revokeOperation to revokeResult to get .op
const revokeOperation = revokeResult.op; // Get the operation from the result

// Wait for the revocation operation to complete.
const revokeResponse = await issuerClient
    .operations()
    .wait(revokeOperation, AbortSignal.timeout(DEFAULT_TIMEOUT_MS)); // Used revokeOperation directly

// Log the credential status after revocation.
// Note the 'et: "rev"' indicating it's now revoked, and the sequence number 's' has incremented.
const statusAfter = (await issuerClient.credentials().get(credentialSaid)).status;
console.log("✅ Credential status after revocation:", statusAfter);
```

    Credential status before revocation: {
      vn: [ 1, 0 ],
      i: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
      s: "0",
      d: "EN-9Mt1MGzZmaTNwchPv-05uYd6LlR6oweGUNS5SGHHO",
      ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
      ra: {},
      a: { s: 2, d: "EP6gx17zzX_JfzCPzEnp4ZuRJffPCauz6CyaZHur60KJ" },
      dt: "2025-09-12T04:12:11.639000+00:00",
      et: "iss"
    }


    ✅ Credential status after revocation: {
      vn: [ 1, 0 ],
      i: "EEr2KjMDimM-NzHvqpBjz-ZBGctjGZDK3WH2lndNlwCG",
      s: "1",
      d: "ENWjDrT1_mqdEtpR5cohaSLwjXpPMAp3t94FV5AublLJ",
      ri: "EI1knJMnZANO17CvQPEQ5Hza0mWo4xE_JZ7guKtzyqfI",
      ra: {},
      a: { s: 3, d: "ECtamOP5KYCURrHyzNfeAdDIFTqhFCN5air7Y1y2vWuq" },
      dt: "2025-09-12T04:12:36.315000+00:00",
      et: "rev"
    }


The output shows the change in the credential's status object:

- Before revocation, `et` (event type) was `iss`.
- After revocation, `et` is `rev`.
- The sequence number `s` of the TEL event also increments, reflecting the new event.
- The digest d of the event changes, as it's a new event.

This demonstrates that the Issuer has successfully updated the credential's status in their registry. Anyone (like a Verifier) who subsequently checks this registry for the credential's status will see that it has been revoked.

### Propagating revocation state to Holders and Verifiers

Knowing issuance and revocation state for ACDC credentials comprises an essential part of some use cases and so propagating revocation state to verifiers, and possibly holders becomes an important workflow. Direct transmission of revocation state is one way of propagating this state between either an issue and a holder, between an issuer and a verifier, or between a holder and a verifier. This direct transmission may be accomplished with an IPEX Grant. Again, for the verifier the IPEX Admit in response to this Grant is optional, yet for the Holder to show the credential as revoked in their KERIA Agent database they must send an IPEX admit.

#### Directly Sending Revocation State from Issuer to Holder

Now that the credential has been shown to be revoked in the issuer's database you can re-grant it to the Holder to propagate the revocation state to the holder. This process may be used with the verifier as well to inform the verifier of credential revocation.


```typescript
// Issuer - get credential (with all its data)
const credential = await issuerClient.credentials().get(credentialSaid);
console.log(`Issuer credential state (iss = issued, rev = revoked): ${credential.status.et}`);

```

    Issuer credential state (iss = issued, rev = revoked): rev


The issuer then re-grants this credential to the holder.


```typescript
// Issuer - Ipex grant
console.log("granting credential to holder")
const grantResponse = await ipexGrantCredential(
    issuerClient,
    issuerAidAlias, 
    holderAid.i,
    credential
)
console.log("✅ Issuer created and granted credential.")


```

    granting credential to holder


    AID "issuerAid" granting credential to AID "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG" via IPEX...


    Successfully submitted IPEX grant from "issuerAid" to "EDTeQiSu_8hLVGyQ04C9-p5k3WPdfrmi1WT9XXyWXMJG".


    ✅ Issuer created and granted credential.


After being granted the credential the holder may take the grant notification and admit the credential which will cause the credential to show as revoked in the Holder's database.


```typescript
// Holder - Wait for grant notification
console.log("Holder waiting for credential")
const grantNotifications = await waitForAndGetNotification(holderClient, IPEX_GRANT_ROUTE)
const grantNotification = grantNotifications[0]

// Holder - Admit Grant
const admitResponse = await ipexAdmitGrant(
    holderClient,
    holderAidAlias,
    issuerAid.i,
    grantNotification.a.d
)
console.log("Holder admitting credential")

// Holder - Mark notification
await markNotificationRead(holderClient, grantNotification.i)

const credential = await holderClient.credentials().get(credentialSaid);
console.log(`✅ Holder credential state (iss = issued, rev = revoked): ${credential.status.et}`);
```

    Holder waiting for credential


    Waiting for notification with route "/exn/ipex/grant"...


    [Retry] Grant notification not found on attempt #1 of 5


    [Retry] Waiting 5000ms before next attempt...


    AID "holderAid" admitting IPEX grant "EMTj0CR8ErK2R5HxSFDfbXniC4Uf8BlCQku7ekjamDjA" from AID "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY"...


    Successfully submitted IPEX admit for grant "EMTj0CR8ErK2R5HxSFDfbXniC4Uf8BlCQku7ekjamDjA".


    Holder admitting credential


    Marking notification "0ADj6EemnDUGvDoxzMnGrGrH" as read...


    Notification "0ADj6EemnDUGvDoxzMnGrGrH" marked as read.


    ✅ Holder credential state (iss = issued, rev = revoked): rev


Now that the Holder has received the Grant and sent back an Admit then the issuer may mark as read the notification of the Admit.


```typescript
// Issuer - Wait for admit notification
console.log("Issuer receiving admit...")
const admitNotifications = await waitForAndGetNotification(issuerClient, IPEX_ADMIT_ROUTE)
const admitNotification = admitNotifications[0]

// Issuer - Mark notification
await markNotificationRead(issuerClient, admitNotification.i)
console.log("\n\n✅ Issuer received admit. Propagation of revocation state to holder complete.")
```

    Issuer receiving admit...


    Waiting for notification with route "/exn/ipex/admit"...


    Marking notification "0ADUsXMBGdNd_-hLL4cOaXos" as read...


    Notification "0ADUsXMBGdNd_-hLL4cOaXos" marked as read.


    
    
    ✅ Issuer received admit. Propagation of revocation state to holder complete.


#### Directly Sending Revocation State from Issuer to Verifier

The issuer may send revocation state directly to the verifier as shown below. There is an alternative flow using what are known as Observers that will be explained in an upcoming training.


```typescript
// Issuer - Ipex grant
console.log("granting credential to verifier")
const grantResponse = await ipexGrantCredential(
    issuerClient,
    issuerAidAlias, 
    verifierAid.i,
    credential
)
console.log("✅ Issuer created and granted credential.")
```

    granting credential to verifier


    AID "issuerAid" granting credential to AID "ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy" via IPEX...


    Successfully submitted IPEX grant from "issuerAid" to "ED-xfM6ATAg7mA3O94OQ_tN4Q7rbwl4v7N-WpEmzrfjy".


    ✅ Issuer created and granted credential.


Finally, the verifier may process the notification of the re-granted credential and send back an IPEX Admit to the Holder, yet, again, the necessity of sending the Admit depends on the use case. The verifier has received the revocation state by virtue of receiving and processing the IPEX Grant following the revocation of the credential and the holder learning about the revocation of the credential state. 

In use cases needing end-verifiability and signing of the reception of credentials then IPEX Admits must ALWAYS be sent since they represent the credential receiver cryptographically signing their acceptance of a credential presentation. This may be required for legal certainty on the terms of data sharing expressed in the rules section of an ACDC or other terms such as those in a privacy policy or terms of service for an application or service. An IPEX Admit is useful when the legal requirements of a use case include the need for a receiver of a credential (holder) or a credential presentation (verifier) to sign that they received it.


```typescript
// Verifier - Wait for grant notification
console.log("Verifier waiting for credential")
const grantNotifications = await waitForAndGetNotification(verifierClient, IPEX_GRANT_ROUTE)
const grantNotification = grantNotifications[0]

// Verifier - Admit Grant
const admitResponse = await ipexAdmitGrant(
    verifierClient,
    verifierAidAlias,
    issuerAid.i,
    grantNotification.a.d
)
console.log("Verifier admitting credential")

// Verifier - Mark notification
await markNotificationRead(verifierClient, grantNotification.i)
```

    Verifier waiting for credential


    Waiting for notification with route "/exn/ipex/grant"...


    [Retry] Grant notification not found on attempt #1 of 5


    [Retry] Waiting 5000ms before next attempt...


    AID "verifierAid" admitting IPEX grant "EPiaeSv6ix1gyVkACzKkC2MUZOp4CDFUf5wDcmCdmFzH" from AID "EGOrzLLCX0fN4XRHE_SQFBGu6sht8iO_l1VGCO7ag7AY"...


    Successfully submitted IPEX admit for grant "EPiaeSv6ix1gyVkACzKkC2MUZOp4CDFUf5wDcmCdmFzH".


    Verifier admitting credential


    Marking notification "0ADNeJ1Swux_flAxknJRASip" as read...


    Notification "0ADNeJ1Swux_flAxknJRASip" marked as read.


As noted above, the revocation state shows up prior to sending the IPEX Admit. You can run the below code snippet prior to sending the IPEX Admit and you will see that the credential state shows up as revoked even though the Admit has not yet been sent.


```typescript
// You can run this prior to sending the IPEX Admit to see that the credential state is already 
// revoked before sending the Admit.
// You can also run this after sending the Admit. The result is the same before or after.
const credential = await verifierClient.credentials().get(credentialSaid);
console.log(`✅ Verifier credential state (iss = issued, rev = revoked): ${credential.status.et}`);
```

    ✅ Verifier credential state (iss = issued, rev = revoked): rev


#### Discovering Revocation State

Typically the responsibility for discovering revocation state would be stay with the verifier rather than with the issuer. The verifier is usually a subscriber to revocation state of credentials it depends on. The best way to accomplish this is with the equivalent of a Watcher network yet for credentials which, in the case of ACDCs, are called Observers. A verifier would have Observers set up that watch any issuers of credentials it accepts, or any propagation networks such as a global DHT of issuers, KEL state, and ACDC state, so that the verifier can be automatically informed of credential state within seconds, or sub-seconds, once an issuer publishes a revocation event.

So, what is shown in this demonstration of the issuer sending revocation state to the verifier is not scalable and is not appropriate for production. It is only suitable for toy or proof of concept projects. A production implementation would use observers.

### Current state of Observers in the KERI ecosystem

A barebones implementation of Observers as a feature of a witness for an issuer exist in the KERI ecosystem in the [keripy](https://github.com/WebOfTrust/keripy) implementation of witnesses. Those witnesses expose a `/query` endpoint for polling the state of an ACDC. An upcoming training shows how to use this functionality and how to incorporate it into a verifier so that using ACDCs and monitoring revocation state is seamless and with as few steps for the user as possible.

Next we cover the final topic for this particular training, cleaning up the holder database by deleting revoked credentials.

## Deleting Revoked Credentials from the Holder Database

Once a Holder becomes aware that a credential they possess has been revoked (e.g., by checking its status in the Issuer's registry or being informed through other means), it may want to delete that credential from its database. This is a design choice left up to the developers and architects of a given system. Deletion of credentials after revocation is not required and may not be desirable from a recordkeeping standpoint, yet if needed it can be a useful way to clean up credential stores and is a simple way to prevent credential holders from accidentally presenting revoked credentials to verifiers.

The `holderClient.credentials().delete()` method removes the credential from the Holder's local client storage.


```typescript
// Holder deletes the (now revoked) credential from their local store.
await holderClient.credentials().delete(credentialSaid);

// Verify the credential is no longer in the Holder's list.
console.log("Holder's credential list after deleting the revoked credential:");
console.log(await holderClient.credentials().list()); // Should be an empty array or not contain the revoked credential

```

    Holder's credential list after deleting the revoked credential:


    []


<div class="alert alert-primary">
<b>📝 SUMMARY</b><hr>
This notebook demonstrated ACDC Presentation and Revocation steps using IPEX with KERIA and Signify TS:
<ul>
<li><b>Full Formal IPEX flow:</b> the entire IPEX set of verbs including apply, offer, agree, grant, and admit may be used to orchestrate the disclosure process</li>
<li><b>Partial flow for presentation:</b> an abbreviated IPEX flow with only grant and admit may be used to share credentials. This is the most common workflow.</li>
<li><b>Simple sharing:</b> only an IPEX Grant is needed to share credentials as a verifier does not need to reply with an IPEX Admit, which permits the simplest presentation flow from either an issuer or holder to a verifier.</li>
<li><b>Revocation:</b> After a successful credential creation the issuer may choose to revoke a credential. Propagating this state to a holder or a verifier may be directly performed with another IPEX Grant and Admit or may be discovered through observer infrastructure.</li>
</ul>
<p>The IPEX credential presentation and revocation flows are a critical part of the value add the whole vLEI protocol stack, KERI, ACDC, and CESR, stand to provide as the basis for data sharing with verifiable credentials. This training walked you through both the presentation and revocation workflows.</p>
</div>

[<- Prev (KERIA Signify Credential Issuance)](102_20_KERIA_Signify_Credential_Issuance.ipynb) | [Next (Third Party Tools) ->](102_30_Third_Party_Tools.ipynb)
