# KERI Infrastructure: Modes, OOBIs, and Witnesses

<div class="alert alert-primary">
  <b>🎯 OBJECTIVE</b><hr>
Explain KERI's Direct and Indirect modes and the key components enabling Indirect Mode: Out-of-Band Introductions (OOBIs) for discovery, Mailboxes for asynchronous communication, Witnesses for availability and consistency, and the Threshold of Accountable Duplicity (TOAD) for defining signing thresholds.
</div>

## Operational Modes: Direct and Indirect
KERI provides a secure way to manage identifiers and track control using verifiable logs of key events (KEL). How these logs are shared and verified between the controller and someone verifying that identifier depends on one of the two operational modes: Direct and Indirect.


### Direct Mode

Direct Mode is a controller-to-controller communication approach, similar to a direct conversation, or like making an HTTP request from a client to a server.

In this mode the source controller shares their Key Event Log directly with a destination controller through an HTTP or TCP request. The destination controller acts as a validator by verifying the KEL events and their signatures to ensure integrity. 

The destination controller can choose to establish trust based solely on verifying the signatures of the source controller on its KEL. This is a lower security posture than relying on a watcher network, yet may be an appropriate choice for a use case. It is also a simple way to start using KERI and allows quick bootstrapping of nodes in a system because validators directly receive and verifies the KEL.

This mode is an option for interactions where both parties can connect directly, even if only occasionally, and need to be online to exchange new events or updates. 

<div class="alert alert-info">
    <b>🧩 DID YOU KNOW?</b><hr>
    <h4>Future Note: Watcher Networks for Direct Mode Verification Thresholds</h4>
    While watchers are not yet widely used in the KERI ecosystem landscape, using a watcher network
    to set a verification threshold is one way to increase the security of a direct mode installation. 
    A watcher or watcher network may be used by the validating controller to compare the KEL being
    received from the source controller with the view of the KEL that the watcher network has. 
    This is similar to how verifier nodes in distributed consensus systems, like a blockchain, 
    will verify block history with multiple nodes prior to accepting a new block.
</div>

#### Example of Direct Mode

The vLEI Reporting API component called [sally](https://github.com/GLEIF-IT/sally) is a direct mode validator component that receives credential presentations in the vLEI ecosystem. It receives KELs, ACDCs (credentials) directly from a presenter, verifies them, and validates them.

#### Direct Mode Wrap up

Although we haven't done any interaction so far, all the things we have done until this point fit within the direct mode approach.

### Indirect Mode

Indirect Mode is the asyncronous approach leveraging mailboxes for communication and witnesses for highly-available KELs, similar to using a public bulletin board instead of direct messaging.

It’s for scenarios where the controller may be sometimes offline or needs to serve many validators at once. Rather than relying on direct communication, it introduces infrastructure to both allow a controller to receive messages while offline, the mailbox, and to make the KEL reliably accessible from witnesses.

Verifiability extends beyond the controller’s signature to signed event receipts produced by witnesses, called witness receipts. This additional verification capability relies on a network of Witnesses, chosen by the controller, that verify, return signed receipts of, and store key events. When combined with the two factor authentication (2FA) capability then witnesses increase the security of an AID.

This mode is ideal for public identifiers used from mobile devices and web browsers, one-to-many interactions, or any situation where the controller can’t be constantly online. 

#### Indirect Mode Wrap Up

Most elements of the KERI ecosystem use indirect mode. Unless you know you need direct mode then you should be using indirect mode as your default.

## OOBIs: Discovery Mechanism

When an AID controller is operating in either mode, you need a way to tell others where they can find information about it, like its Key Event Log (KEL) or the schema of an ACDC. This is where Out-of-Band Introductions (OOBIs) come in. They function as an address of the way to communicate with a controller or to retrieve a resource.

**What is an OOBI?**

An OOBI is a **discovery mechanism** used in KERI used to discover controllers or resources. Its primary uses are to link a specific KERI AID to a network location (a URL or URI) where information about that identifier can potentially be found and also to declare the location a resource is hosted such as a JSON Schema document for an ACDC or a CESR stream for a well-known credential.

### Example OOBI

The simplest form of an OOBI pairs a SAID, either an AID or the SAID of a document, with a URL. For example:

`("http://8.8.5.6:8080/oobi", "EaU6JR2nmwyZ-i0d8JZAoTNZH3ULvYAfSVPzhzS6b5CM", "controller")`

This OOBI suggests that controller information related to the AID `EaU6JR2nmwyZ-i0d8JZAoTNZH3ULvYAfSVPzhzS6b5CM` might be available at the service endpoint `http://8.8.5.6:8080/oobi`.

The URL representation may be one of any of the following:

Blind OOBI (no AID at the end) interpreted as a controller OOBI: 
- `http://8.8.5.6:8080/oobi`

Controller OOBI with no role:
- `http://8.8.5.6:8080/oobi/EaU6JR2nmwyZ-i0d8JZAoTNZH3ULvYAfSVPzhzS6b5CM`

Controller OOBI with the specific role at the end:
- (`http://8.8.5.6:8080/oobi/EaU6JR2nmwyZ-i0d8JZAoTNZH3ULvYAfSVPzhzS6b5CM/controller`

### Kinds of OOBIs

There are four similar kinds of OOBIs: controller OOBIs, witness OOBIs, agent OOBIs, and data OOBIs. For controller OOBIs there are three variants: the blind OOBI, the no-role OOBI, and the full OOBI.

#### Controller OOBI

A controller OOBI is a service endpoint that a controller uses to advertise where its KEL may be retrieved from and where it may receive data. This is typically used by a witness or a direct mode agent. When witnesses are declared in an inception event they will typically have had their controller OOBI resolved.

Examples:
- Blind OOBI: `http://8.8.5.6:8080/oobi`
- AID and no role: `http://8.8.5.6:8080/oobi/EaU6JR2nmwyZ-i0d8JZAoTNZH3ULvYAfSVPzhzS6b5CM`
- AID and role: `http://10.0.0.1:9823/oobi/ECLwKe5b33BaV20x7HZWYi_KUXgY91S41fRL2uCaf4WQ/controller`

#### Witness OOBI

A witness OOBI is a service endpoint authorized and used by a controller to designate a witness as a mailbox for a given controller. It means that the witness runs a mailbox that receives messages on behalf of a controller so that the controller may poll for and receive messages when it comes back online.

They look like this: 
- `http://10.0.0.1:5645/oobi/EA69Z5sR2kr-05QmZ7v3VuMq8MdhVupve3caHXbhom0D/witness/BM35JN8XeJSEfpxopjn5jr7tAHCE5749f0OobhMLCorE`

This OOBI means that the controller with AID `EA69Z5sR2kr-05QmZ7v3VuMq8MdhVupve3caHXbhom0D` is using the witness with AID `BM35JN8XeJSEfpxopjn5jr7tAHCE5749f0OobhMLCorE` as its mailbox.

#### Agent OOBIs

An Agent OOBI, used in the KERIA multitenant agent server, is similar to a witness OOBI in that it is a service endpoint authorized and used by a controller to designate an agent as a mailbox for a controller. Where an Agent OOBI differs from a witness OOBI is that an agent OOBI also indicates which specific agent was authorized to act as an agent for a given Signify Controller.

It looks like this:
- `http://keria2:3902/oobi/ECls3BaUOAtZNO3Ejb4zCv-fybh_hk3iNQMZJVdItr5W/agent/EAueTIcNo9FYqBvtT2QSH-zKFW3TMJGrxEETuIyW2CLF`

#### Data OOBIs

A data OOBI shows a location to resolve what is typically either a JSON file or a CESR stream, though may be any resource identified by a self-addressing identifier (SAID). Data OOBIs are usually used for ACDC credential schemas, which are JSON files, or CESR streams for well-known ACDC credentials in order to speed up credential verification by hosting common parts of a verification chain in well-known locations.

For example, the QVI JSON schema identified with the SAID `EBfdlu8R27Fbx-ehrqwImnK-8Cm79sqbAQ4MmvEAYqao` is made available at the following URL on the `10.0.0.1` host.

- `http://10.0.0.1:7723/oobi/EBfdlu8R27Fbx-ehrqwImnK-8Cm79sqbAQ4MmvEAYqao`

### Role of the Service at an OOBI Endpoint

What an OOBI means is that a controller has designated and cryptographically authorized a particular service endpoint (web URL) as the location that controller will receive requests at whether for OOBI resolution, key state requests, or for direct CESR stream transmissions.

**Key Points**

- OOBIs Facilitate Discovery (Out-of-Band): They may use existing internet infrastructure (web servers, QR codes, etc.) to share potential (url, aid) links. This happens outside of KERI's core trust guarantees.
- OOBIs Themselves Are NOT Trusted: Receiving an OOBI does not guarantee the URL-AID link is valid or that the data at the URL is legitimate.
- Trust Requires KERI Verification (In-Band): After using an OOBI URL to retrieve data (like a Key Event Log), you must use KERI's standard cryptographic verification methods (checking signatures, verifying event history) to establish trust.

In short, OOBIs help you find potential information; verification ensures you can trust it.

## Mailboxes

Mailboxes are a simple store and forward mechanism where one controller receives messages on behalf of another. As the primary enabler of indirect mode, mailboxes are the always online presence that continues to receive messages for a controller while that controller is offline or unavailable.

<div class="alert alert-info">
    <b>ℹ️ NOTE</b><hr>
    Currently, the KERIpy implementation of witnesses also provides mailboxes. 
    When a transferable identifier <em>declares a witness</em> in the inception event, that <b><u>witness
    will also be used as a mailbox</u></b> for the controller to receive messages from other controllers.
    <br/>
    Similarly, KERIA agents also serve as mailboxes for Signify Controllers.
</div>

To receive messages from mailboxes a controller polls all of its witness mailboxes. Polling all of the mailboxes is currently necessary because when messages are sent from a source controller to a destination controller then one witness is selected at random from the list of witnesses that the source controller has for the destination controller. The message is not sent to every mailbox for the destination. Thus, every mailbox must be polled in order to discover new messages.

<div class="alert alert-info">
    <b>ℹ️ NOTE</b><hr>
    When the work to support separate mailboxes is completed and supported in the KERIpy reference implementation, then a controller may declare and use only one mailbox. 
    This will simplify mailbox management for controllers that use more than one witness since there will be then only one mailbox, and it will be deployed separately from the witness.
</div>


## Role of Witnesses

Witnesses are entities designated by the controller within their AID key event log, acting much like trusted notaries. Their role is to receive key events directly from the controller, verify the controller’s signature, and check that each event aligns with the event history they have recorded for that AID.

Once a witness confirms an event is valid and encounters it for the first time, it generates a **receipt** by signing the event (Witnesses also have their own AID). The witness then stores both the original event and its receipt, alongside receipts from other witnesses, in a local copy of the KEL known as the **Key Event Receipt Log (KERL)**.

Witnesses play a critical role in ensuring the system’s reliability and integrity. They provide availability by forming a distributed service that validators can query to access the KEL of a given prefix, even if the controller itself is unavailable. Additionally, they help ensure consistency: since honest witnesses only sign the first valid version of an event at a given sequence number they observe, it becomes significantly harder for a controller to present conflicting log versions (**duplicity**).

It's important to note that witnesses are software components. For the system to improve security and availability, the witness should be deployed independently, ideally operated by different entities, on different infrastructure, from both the controller and each other.

## TOAD: Ensuring Accountability

A key challenge in maintaining the integrity of an identifier's history is preventing the controller from presenting conflicting versions of events. This situation, known as **duplicity**, occurs if a controller improperly signs two or more different key events purporting to be at the same sequence number in their Key Event Log (KEL) – for example, signing two different rotation events both claiming to be sequence number 3. Such conflicting statements undermine trust in the identifier's true state and control. 

Reasons for duplicity may be due to malicious intent or operational errors. KERI addresses this partly through the behavior of witnesses, which only sign the first valid event they see per sequence number, and partially through watchers which keep a duplicate copy of a KEL for a given controller so they may detect when a malicious controller tries to change history by changing a key event at a given sequence number that has already occurred.

KERI assigns *accountability* for an event, and thus any potential duplicity (change of history), based on a signing threshold of witnesses for a given event, called the **Threshold of Accountable Duplicity (TOAD)**. This signing threshold quantifies the level of agreement needed to assign accountability to a controller for a given event, and thus any potential duplicity. The TOAD is specified in the inception event for an AID and can be changed in each rotation event.

We have seen this parameter before when calling `kli incept`. The `toad` value represents the minimum number of unique witness receipts the controller considers sufficient to accept accountability for a key event.

By gathering receipts that meet or exceed this controller-defined threshold (`toad`), validators gain assurance that the event history they are watching is the one the controller stands behind and is broadly agreed upon by the witness network. Crucially, while the `toad` defines the controller's threshold for their accountability, a validator may independently establish its own, often higher, threshold watchers that must agree on the history of a KEL to accept an event as fully validated according to its trust policy. These two threshold mechanisms, the TOAD for a signing threshold and a watcher threshold, allowing for distinct controller accountability and validator trust levels, are key to KERI's robust security model and fault tolerance, helping distinguish between minor issues and significant, actionable inconsistencies.

<div class="alert alert-prymary">
<b>📝 SUMMARY</b><hr>
KERI provides two operational modes for sharing Key Event Logs (KELs).
<ul>
<li><strong>Direct Mode:</strong> The synchronous, controller-to-controller connection approach for sharing KELs, suitable for when both parties are online.</li>
<li><strong>Indirect Mode:</strong> An asynchronous approach using key infrastructure, designed for high availability and for controllers that may be offline.</li>
</ul>
</li>

Key Infrastructure for Indirect Mode:
<ul>
<li><strong>Witnesses:</strong> Designated AIDs that enhance reliability and help prevent duplicity by receiving, receipting, and storing a controller's key events in a Key Event Receipt Log (KERL).</li>
<li><strong>Mailboxes:</strong> A store-and-forward service, often coupled with a witness, that accepts messages on behalf of an offline controller.</li>
<li><strong>OOBIs (Out-of-Band Introductions):</strong> An untrusted discovery mechanism that links an AID to a network URL. OOBIs help locate KELs and other resources, which must then be cryptographically verified.</li>
</ul>
</li>

Accountability and Trust:
<ul>
<li><strong>TOAD (Threshold of Accountable Duplicity):</strong> A controller-set threshold defining the minimum number of witness receipts required to hold the controller accountable for an event.</li>
<li><strong>Validator Trust Policy:</strong> A validator can enforce its own, separate trust policy, potentially requiring a higher threshold of verification (e.g., from watchers) than the controller's TOAD.</li>
</ul>
</li>
</ul>
</div>

[<- Prev (Key Rotation)](101_30_Key_Rotation.ipynb) | [Next (Witnesses) ->](101_40_Witnesses.ipynb)
