# Introducing KERIA and Signify: Architecture and Concepts

<div class="alert alert-primary">
  <b>🎯 OBJECTIVE</b><hr>
  Introduces the foundational concepts of KERIA and Signify TS, focusing on:
    <ul>
        <li>The KERIA/Signify client-agent architecture.</li>
        <li>Key KERIA endpoint interfaces.</li>
        <li>The concept of Endpoint Role records (End Roles).</li>
        <li>The relationship between Client AIDs and Agent AIDs.</li>
        <li>What SignifyTS and SignifyPy are.</li>
    </ul>
</div>

## Edge Signing Client - Agent Architecture

KERI is a protocol for secure, self-certifying identifiers. **KERIA** is an implementation of the multi-tenant server portion of the Signify agent protocol for KERI agents and is designed to run as a service (e.g., in the cloud or self-hosted) that manages AIDs on behalf of a controller. **Signify TS** is a TypeScript library implementing the edge signing client protocol. It acts as an edge signing client, enabling applications to interact with a KERIA agent. **Signify Py** is a Python library implementing the edge client protocol of the Signify and KERIA protocol. 

What does edge signing mean? It means that all of the cryptographic keypairs only ever exist at the edge, in memory, within the application that uses a Signify library. Keys existing at the edge provides security and confidence that only the person possessing the passcode, or cryptographic seed, is the one performing signing. The phrase "edge" is used to indicate that the Signify libraries are used in person-facing applications.

The idea behind this client-agent architecture is to enable "signing at the edge". Your sensitive private keys, used for signing key events and other data, remain on the client-side (managed by a Signify client library). The KERIA agent, running remotely, handles tasks like:
* Storing key indexes (retrieved by the Signify Client on boot up)
* Creating KERI AIDs delegated from the edge AID
* Managing Key Event Logs (KELs) for edge AIDs
* Creating, storing, issuing, revoking, presenting, and receiving ACDCs
* Acting as a cloud mailbox to send and receive KERI and ACDC messages from
  * Interacting with witnesses
  * Exchanging messages with other KERI agents

The KERIA agent itself never has access to your private keys. All critical signing operations happen on the client, and the signed events are then sent to the KERIA agent for processing and dissemination.

This architecture separates key management and signing authority (client-side) from the operational aspects of maintaining AIDs' KELs and ACDCs and their availability (agent-side).

### KERIA Deployment and Configuration

In a typical deployment, KERIA starts up and loads its configuration, including a list of default witnesses (or OOBI URLs) and ACDC schemas, from a JSON configuration file (e.g., **[keria configuration file](config/keria/keria-docker.json)**). This allows the agent to be pre-configured with a set of witnesses and connections to any other KERI AID that any AIDs created on that KERIA server are preconfigured to see.

## Agent Service Endpoints

A KERIA service instance exposes distinct HTTP endpoints to handle different types of interactions:

1.  **Boot Interface** (`boot port`, e.g., 3903 by default):
    * **Purpose**: Used for the initial setup and provisioning of a KERIA agent worker for a Signify client. This is where the client and agent establish their initial secure relationship.
    * **Interaction**: The Signify client sends its client AID's inception event to this endpoint to request the creation of a delegated agent AID.
    * **Accessibility**: Often restricted to internal infrastructure or disabled if agents are pre-configured (static worker mode).

2.  **Admin Interface** (`admin port`, e.g., 3901 by default):
    * **Purpose**: This is the primary REST API for the Signify client to command and control its KERIA agent.
    * **Interaction**: Used for operations like creating new AIDs, rotating keys, issuing credentials, resolving OOBIs, etc. All requests to this interface must be authenticated (e.g., signed by the Client AID).
    * **Accessibility**: Typically exposed externally to allow the client to manage its AIDs.

3.  **KERI Protocol Interface** (`http port`, e.g., 3902 by default):
    * **Purpose**: Handles standard KERI protocol messages (e.g., KELs, receipts, challenges) exchanged with other KERI agents and witnesses in the wider KERI network.
    * **Interaction**: Facilitates multi-sig coordination, credential revocation, KEL exchange, etc., using CESR (Composable Event Streaming Representation) over HTTP.
    * **Accessibility**: Exposed externally to enable interaction with the global KERI ecosystem.

This separation of interfaces enhances security and deployment flexibility.

## Understanding Endpoint Role Records

An **endpoint role record**, or "end role" for short, in KERI is an authorization that one AID grants to itself or another AID to act in a particular role representing a specific capacity to act on its behalf. Think of it as assigning a specific job to itself or another identifier.

For instance, when a Signify client connects to a KERIA agent, the **Client AID** (controlled by the user or application) delegates authority to an **Agent AID** (managed by the KERIA service). The Client AID essentially authorizes its Agent AID to perform certain KERI operations in its name, like anchoring its KEL with witnesses or responding to discovery requests.

Declaring an end role typically involves creating a KERI event, often an interaction event (`ixn`) or an establishment event (`icp` or `rot`) with specific configuration (`c` field) or an `end` role event, that specifies:
* The AID granting the authorization (the delegator or authorizer).
* The AID receiving the authorization (the delegate or authorized party).
* The specific role being granted (e.g., `agent`, `witness`, `watcher`, `controller`, `mailbox`).

This signed authorization will either be recorded in the KEL of the authorizing AID to make the role assignment verifiable by anyone who can access and validate that KEL or it will be stored locally for transmission when the key event log is requested through OOBI exchange or when it is sent directly from a given AID.

### Example of endpoint role in action

The end role records are necessary to enable specific permissions within the internal KERI communication system. For example, an agent AID having been assigned the role of `agent` for a given delegator, the Signify controller AID, allows messages for the controlling AID to be sent through the authorized agent AID.

## Client and Agent AIDs Explained

When you use Signify TS to connect to a KERIA agent, two primary AIDs are involved:

1.  **Client AID**:
    * This is an AID that *you* (or your application) control directly via the Signify TS client.
    * It is a single signature AID.
    * You hold its private keys.
    * It's typically a transferable AID, allowing for key rotation.
    * It acts as the **delegator** to the Agent AID.
    * The rotation key index for this client AID is stored encrypted in the KERIA agent that the client pairs with.

2.  **Agent AID**:
    * This AID is created and managed by the KERIA service *on your behalf* when the request to the `/boot` endpoint is made with the Client AID's inception event.
    * Its inception event specifies the Client AID as its delegator (`di` field in the inception event). This means the Agent AID's authority to act is derived from, and anchored to, your Client AID.
    * It's also typically a transferable AID.
    * The KERIA service uses this Agent AID to perform actions for your Client AID, such as acting as a communication proxy to interact with witnesses or other agents, without needing direct access to your Client AID's private keys.

The Signify client generates the Client AID and sends its inception event to the KERIA agent's Boot Interface (on `/boot`). The KERIA service then creates the delegated Agent AID and returns its inception event to the client. Finally, the Signify client approves this delegation by sending an interaction event back to the KERIA agent's Admin Interface.

This delegation model is fundamental to KERIA's security: your primary controlling keys (for the Client AID) remain "at the edge," while the KERIA agent operates with a delegated authority (via the Agent AID) that is always traceable back to your Client AID.

## SignifyTS and SignifyPy - Signify Client Libraries

There are currently two Signify protocol client library implementations, one in Typescript and one in Python. [SignifyTS](https://github.com/WebOfTrust/signify-ts) is the Typescript implementation whereas [SignifyPy](https://github.com/WebOfTrust/signifypy) is the Python implementation. The most up-to-date implementation is SignifyTS and is recommended to be used. SignifyPy would be usable with a modest amount of upgrade effort. A Rust client, [scir](https://github.com/WebOfTrust/scir) was started yet is currently mostly unfinished and should not be used.

### SignifyTS, or Signify TS

SignifyTS, also referred to as "signify-ts", is the Typescript implementation of the Signify client protocol and may be found at https://github.com/WebOfTrust/signify-ts.

### SignifyPy, or Signify Py

SignifyPy, also known as "sigpy", is the Python implementation of the Signify client protocol and was the original implementation of Signify and was used to drive initial creation of the KERIA server side of the Signify protocol. It may be found at https://github.com/WebOfTrust/signifypy.

<div class="alert alert-primary">
  <b>📝 SUMMARY</b><hr>
  <p>
    The KERIA/Signify architecture enables "signing at the edge," where a Signify client (like Signify TS) manages private keys and signing operations locally, while a remote KERIA agent handles ACDC storage, witness interactions, and KERI protocol communications. KERIA exposes three main HTTP endpoints:
    <ul>
        <li><b>Boot Interface:</b> For initial client-agent provisioning and creation of a delegated Agent AID.</li>
        <li><b>Admin Interface:</b> A REST API for the client to command and control its agent (e.g., create AIDs, rotate keys).</li>
        <li><b>KERI Protocol Interface:</b> For standard KERI message exchange with other agents and witnesses.</li>
    </ul>
    Endpoint role records, end roles, in KERI define verifiable authorizations for one AID to act in a specific capacity for another (e.g., an Agent AID acting in the 'agent' role for a Client AID).
  </p>
  <p>
    The connection process involves a <b>Client AID</b> (controlled by the user via Signify) delegating authority to an <b>Agent AID</b> (managed by KERIA).
  </p>
    <p>SignifyTS and SignifyPy comprise the two implementations of the Signify client protocol that are usable with the recommendation being to use SignifyTS.</p>
</div>

[<- Prev (ACDC Chained Credentials NI2I)](101_85_ACDC_Chained_Credentials_NI2I.ipynb) | [Next (KERIA Signify Basic Operations) ->](102_10_KERIA_Signify_Basic_Operations.ipynb)
