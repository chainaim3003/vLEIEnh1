# Signify TS Basics: Client Setup and AID Management

<div class="alert alert-primary">
  <b>🎯 OBJECTIVE</b><hr>
  Introduce basic operations using the typescript implementation of Signify, Signify TS: creating a client, initializing (booting) an agent, connecting to an agent, and creating an Autonomic Identifier (AID).</li>
    </ul>
    Familiarity with core KERI concepts (AIDs, KELs, digital signatures, witnesses, OOBIs) is assumed.
</div>

## Connecting to a KERIA Agent

Now that we understand the architecture, let's see how to use the [signify-ts](https://github.com/WebOfTrust/signify-ts) library to initialize a Signify controller and establish a connection with a KERIA agent. This process involves three main steps:
1.  Initializing the `signify-ts` library, necessary since the dependency libsodium must be initialized in order to be used.
2.  Creating a `SignifyClient` instance, creating your Client AID, which is where your cryptographic keypairs are stored in-memory, and contains your client's connection to a specific KERIA agent once bootstrapped.
3.  Bootstrapping and connecting the client to a KERIA agent, which establishes the relationship Client AID and the delegated Agent AID in a specific KERIA instance.

<div class="alert alert-info">
    <b>ℹ️ Note: KERIA should be available</b><hr>
    <p>This section assumes that a KERIA agent is running and its Boot and Admin interfaces are accessible at the specified URLs. In the context of these notebooks, KERIA is pre-configured and running as part of the Docker deployment.</p>
</div>

### Initializing the Signify TS Library

The `signify-ts` library contains components for cryptographic operations using libsodium. Before any of its functionalities can be used, these components must be initialized. This is achieved by calling and the `ready()` function. This function should be called at the initialization of your application before any functions or SignifyClient methods from `signify-ts` are used.


```typescript
import { randomPasscode, ready, SignifyClient, Tier } from 'npm:signify-ts';

await ready();

console.log("Signify-ts library initialized and ready.");
```

    Signify-ts library initialized and ready.


### Creating the Client Instance
Once the library is initialized, you can create an instance of `SignifyClient`. This object will be your primary interface for all interactions with the KERIA agent. It requires several parameters:

- **url**: The URL of the KERIA agent's Admin Interface. The client uses this for most command and control operations after the initial connection is established.
- **bran**: A 21-character, high-entropy string, often referred to as a "passcode." This bran serves as the root salt for deriving the Client AID's signing and rotation keys via a Hierarchical Deterministic (HD) key algorithm. It is critical to treat the bran as securely as a private key. Losing it means losing control of the Client AID and any identifiers or ACDCs created in the connected KERIA Agent, if any.
- **tier**: The security tier for the passcode hashing algorithm. Tier.low, Tier.med, and Tier.high represent different computational costs for deriving keys from the bran. Higher tiers are more resistant to brute-force attacks but require more processing power and time. The high tier is appropriate for any use. The low tier is primarily used for unit testing so that tests will complete quickly.
- **bootUrl**: The URL of the KERIA agent's Boot Interface. This is used for the initial setup and provisioning of the agent worker for this client.


```typescript
const adminUrl = 'http://keria:3901'; // KERIA agent's Admin Interface URL
const bootUrl = 'http://keria:3903';  // KERIA agent's Boot Interface URL

// Generate a new random 21-character bran (passcode/salt)
// In a real application, you would securely store and reuse this bran by having the user reenter it on opening the application.
const bran = randomPasscode();

// Create the SignifyClient instance
const client = new SignifyClient(
    adminUrl,
    bran,
    Tier.low, // Using Tier.low for faster execution
    bootUrl
);

console.log('SignifyClient instance created.');
console.log('Using Passcode (bran):', bran);
```

    SignifyClient instance created.


    Using Passcode (bran): DM4gMSUh1eELpAXSn7e7c


<div class="alert alert-info">
  <b>ℹ️ NOTE</b><hr>
  <p>In a production environment, the <code>bran</code> must be securely generated and stored and should NOT be displayed on screen or in any log messages. It is displayed above for illustrative and training purposes only.</p>
  <p>For a given Client AID, you must consistently use the same bran to reconnect and derive the correct private keys. Using <code>randomPasscode()</code> each time, as in this demo, will result in a new Client AID being created or an inability to connect to an existing one if the KERIA agent already has a state associated with a different bran for its controller.</p>
</div>

### Bootstrapping and Connecting to the Agent

With the `SignifyClient` instance created, the next step is to establish the initial connection and state with the KERIA agent. This involves two methods:

- **`client.boot()`**: Initiates the bootstrapping process with the KERIA agent's Boot Interface:
  - The client generates its Client AID using the provided bran.
  - It sends the Client AID's inception event to the KERIA agent's Boot Interface, along with the KEL of the Client AID (also known as `caid`).
  - The KERIA agent, upon successful verification of the client AID, creates a delegated Agent AID, that is delegated from the Client AID, and returns the delegated Agent AID inception event to the client.
    - This step essentially provisions the necessary resources and partially the delegated relationship on the KERIA agent for this specific client.
- **`client.connect()`**: After `boot()` (or if the agent has been previously booted with the same bran), connect() completes the delegation to the KERIA Agent AID via its Admin Interface on the first invocation of `.connect()`. All subsequent invocations reuse the existing Agent state and just read the existing key state from the already existing agent.


```typescript
// Bootstrap the connection with the KERIA agent
// This creates the Client AID and requests the Agent AID creation.
await client.boot(); // Triggers a request to the /boot endpoint on the Boot URL from the initial SignifyClient configuration
console.log('Client boot process initiated with KERIA agent.');

// Completes the delegation, if needed, between the Client AID and the Agent AID, and initializes the SignifyClient dependencies.
await client.connect();
console.log('Client connected to KERIA agent.');

// Retrieve and display the current state
const state = await client.state();
console.log('\nConnection State Details:');
console.log('-------------------------');
console.log('Client AID Prefix: ', state.controller.state.i);
console.log('Client AID Keys:   ', state.controller.state.k);
console.log('Client AID Next Keys Digest: ', state.controller.state.n);
console.log('')
console.log('Agent AID Prefix:   ', state.agent.i);
console.log('Agent AID Type:     ', state.agent.et); // Should be 'dip' for delegated inception
console.log('Agent AID Delegator:', state.agent.di); // Should be the Client AID's prefix

```

    Client boot process initiated with KERIA agent.


    Client connected to KERIA agent.


    
    Connection State Details:


    -------------------------


    Client AID Prefix:  EH8QJKt2VvEKXuG11MkjXcHpINk0NurX20CnU2s5KYFw


    Client AID Keys:    [ "DMh176ZFof98WEDQ3mTU4OUNls8jOIHxHssQB0QDtoYI" ]


    Client AID Next Keys Digest:  [ "EPWeorrNy2yJcl0Yf5gbmUwjlwdSzgHIUbMnuL4B7nPf" ]


    


    Agent AID Prefix:    ED-3z7JwTpmFSC87Z_LRlrvdT2hyQW9VsKVDIlFpF755


    Agent AID Type:      dip


    Agent AID Delegator: EH8QJKt2VvEKXuG11MkjXcHpINk0NurX20CnU2s5KYFw


**Output Explanation:**

- **Client AID Prefix:** The unique, self-certifying identifier for the controller AID of the SignifyClient instance, tied to the bran.
- **Client AID Keys:** The current public signing key(s) for the Client AID.
- **Client AID Next Keys Digest:** The digest (hash) of the public key(s) pre-rotated for the next key rotation of the Client AID.
- **Agent AID Prefix:** The unique KERI AID of the KERIA agent worker associated with your client.
- **Agent AID Type:** dip indicates a "delegated inception" event, signifying that this Agent AID's authority is delegated by another AID, in this case the Client AID of the SignifyClient instance.
- **Agent AID Delegator:** This crucial field shows the prefix of the Client AID, confirming that the Agent AID is indeed delegated by your Client AID.

### Reconnecting to an Existing Agent
If the KERIA agent has already been booted for a specific `bran` (Client AID), you don't need to call `client.boot()` again when using the same bran. You directly use `client.connect()`. SignifyTS will detect and reuse the existing agent state.


```typescript
// Create a new client instance with the SAME bran
const client2 = new SignifyClient(
    adminUrl,
    bran, // Using the same bran as the first client
    Tier.low,
    bootUrl
);
console.log('Second SignifyClient instance created with the same bran.');

// Connect without booting, as the agent state for this bran should already exist
await client2.connect();
console.log('Second client connected to the existing KERIA agent.');

const state2 = await client2.state();
console.log('\nReconnection State Details:');
console.log('---------------------------');
console.log('Client AID Prefix:  ', state2.controller.state.i); // Should be the same Client AID
console.log('Agent AID Prefix:   ', state2.agent.i);  // Should be the same Agent AID
console.log('Agent AID Delegator:', state2.agent.di); // Should be the same Client AID
```

    Second SignifyClient instance created with the same bran.


    Second client connected to the existing KERIA agent.


    
    Reconnection State Details:


    ---------------------------


    Client AID Prefix:   EH8QJKt2VvEKXuG11MkjXcHpINk0NurX20CnU2s5KYFw


    Agent AID Prefix:    ED-3z7JwTpmFSC87Z_LRlrvdT2hyQW9VsKVDIlFpF755


    Agent AID Delegator: EH8QJKt2VvEKXuG11MkjXcHpINk0NurX20CnU2s5KYFw


<div class="alert alert-primary">
<b>📝 SUMMARY</b><hr>
To connect to a KERIA agent using SignifyTS:
<ol>
<li>Initialize the library with <code>await ready()</code>.</li>
<li>Create a <code>SignifyClient</code> instance, providing the agent's Admin and Boot URLs, a unique 21-character <code>bran</code> (passcode/salt for key derivation), and a security <code>Tier</code>.</li>
<li>For the first-time connection with a new <code>bran</code>, call <code>await client.boot()</code> to provision the Client AID and request the creation of a delegated Agent AID from KERIA.</li>
<li>Call <code>await client.connect()</code> to and retrieve the state of the Client and Agent AIDs and, on first invocation, complete any delegation approvals. The Client AID delegates authority to the Agent AID, whose inception event (type <code>dip</code>) will list the Client AID as its delegator.</li>
<li>For subsequent connections using the same <code>bran</code>, skip <code>client.boot()</code> and directly use <code>client.connect()</code>.</li>
</ol>
The <code>bran</code> is critical for deriving the Client AID's keys and must be kept secure and reused consistently in order to have the same identity across time.
</div>

## Adding an Autonomic Identifier (AID)

Once your Signify client is initialized and connected to the KERIA agent you can create new AIDs and instruct the agent to store key events and key indexes for the new AIDs, called managed AIDs. These AIDs will be controlled by your Client AID (established during the `connect()` phase) through the delegation mechanism.

### Initiating AID Inception

Creating a new AID occurs locally yet storing its KEL and current key index are asynchronous operations. When you request the KERIA agent to store the inception event and key index of the new AID the agent starts the process and also obtains witness receipts from any witnesses stated in the inception event. The `signify-ts` library handles this asynchronous operation by returning an "operation" object in response to creating an AID which you can then use to poll for completion of the inception process.

The `client.identifiers().create()` method is used to start the inception of a new AID.

**Parameters Explained:**

- **aidAlias (string):** This is a human-readable alias that you assign to the AID within your Signify client's local storage. It is used to refer to this AID in subsequent client operations. It is not part of the KERI protocol itself but a convenience label for client-side management.
- **inceptionArgs (object):** This object contains the configuration for the new AID:
  - **toad (number):** The Threshold of Accountable Duplicity. This is the minimum number of witness receipts the controller (your Client AID via KERIA) requires for this new AID's events to be considered accountable.
  - **wits (array of strings):** A list of AID prefixes of the witnesses that this new AID should use. These witnesses must be discoverable by your KERIA agent (e.g., pre-loaded during KERIA's startup or resolved via OOBIs by the client/agent).
  - **Other parameters:** not shown for brevity but available, see **[CreateIdentifierArgs](https://weboftrust.github.io/signify-ts/interfaces/CreateIdentiferArgs.html)**


```typescript
// Define an alias for the new AID for easy reference within the client
const aidAlias = 'newAid';

// Inception request parameters
const identifierArgs = {
    toad: 2, // Threshold of Accountable Duplicity: minimum number of witness receipts required
    wits: [   // List of witness AID prefixes to use for this AID
        'BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha',
        'BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM',
        'BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX'
    ]
    // Other parameters can be specified. If not, defaults are used.
};

// Creates and sends the locally client-signed inception event to the KERIA agent, 
//  - initializing to zero (0) the agent-stored key index for this AID.
//  - causing the agent to obtain witness receipts for the event as needed
const inceptionResult = await client.identifiers().create(aidAlias, identifierArgs);
console.log(`AID inception initiated for alias: ${aidAlias}`);

// The result contains information about the long-running operation
const inceptionOperation = await inceptionResult.op();
console.log('Inception Operation Details:');
console.log(inceptionOperation);

```

    AID inception initiated for alias: newAid


    Inception Operation Details:


    {
      name: "witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
      metadata: { pre: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF", sn: 0 },
      done: false,
      error: null,
      response: null
    }


**Outout explained**

Calling `inceptionResult.op()` returns a promise that resolves to an operation object containing:
- **name:** A unique name for this long-running operation (e.g., `witness.AID_PREFIX`). KERIA uses this to track the task. The prefix in the name corresponds to the AID being created.
- **metadata:** Contains details like the prefix (pre) of the AID being incepted and the sequence number (`sn`, which is 0 for inception).
- **done:** A boolean indicating if the operation has completed. Initially, it's `false`.
- **error:** Will contain error details if the operation fails.
- **response:** Will contain the result of the operation (the signed inception event) once `done` is `true`.

### Waiting for Operation Completion
Since AID inception involves network communication (e.g., with witnesses to gather receipts), it doesn't complete instantly. You need to poll or wait for the operation to finish. The `client.operations().wait()` method handles this, periodically checking with the KERIA agent until the operation's `done` flag becomes `true` or a timeout occurs.


```typescript
// Poll the KERIA agent for the completion of the inception operation.
// AbortSignal.timeout(30000) sets a 30-second timeout for waiting.
console.log('Waiting for inception operation to complete...');
const operationResponse = await client
    .operations()
    .wait(inceptionOperation, AbortSignal.timeout(30000)); // Pass the operation name

console.log('\nInception Operation Completed:');
console.log(operationResponse);

// The actual inception event is in the 'response' field of the completed operation
const newAidInceptionEvent = operationResponse.response;
console.log(`\nSuccessfully created AID with prefix: ${newAidInceptionEvent.i}`);
console.log(`Witnesses specified: ${JSON.stringify(newAidInceptionEvent.b)}`);

console.log(`Icp op name: ${inceptionOperation.name}`);
const icpOp = await client.operations().get(inceptionOperation.name);
console.log("Inception operation");
console.dir(icpOp);

```

    Waiting for inception operation to complete...


    
    Inception Operation Completed:


    {
      name: "witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
      metadata: { pre: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF", sn: 0 },
      done: true,
      error: null,
      response: {
        v: "KERI10JSON0001b7_",
        t: "icp",
        d: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
        i: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
        s: "0",
        kt: "1",
        k: [ "DDIdUqYZKNw1tqQsqidDt_IOMQrxsCkjodATHT2-GRcT" ],
        nt: "1",
        n: [ "EFfw_k3SV0jNDfJaBx40OMw3mPzWqzhisVy9II3L1gU_" ],
        bt: "2",
        b: [
          "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
          "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
          "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"
        ],
        c: [],
        a: []
      }
    }


    
    Successfully created AID with prefix: ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF


    Witnesses specified: ["BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha","BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM","BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"]


    Icp op name: witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF


    Inception operation


    {
      name: "witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
      metadata: { pre: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF", sn: 0 },
      done: true,
      error: null,
      response: {
        v: "KERI10JSON0001b7_",
        t: "icp",
        d: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
        i: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
        s: "0",
        kt: "1",
        k: [ "DDIdUqYZKNw1tqQsqidDt_IOMQrxsCkjodATHT2-GRcT" ],
        nt: "1",
        n: [ "EFfw_k3SV0jNDfJaBx40OMw3mPzWqzhisVy9II3L1gU_" ],
        bt: "2",
        b: [
          "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
          "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
          "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"
        ],
        c: [],
        a: []
      }
    }


**Completed Operation Output Explained:**

- `done`: Now true, indicating the inception is received on the KERIA agent's side and has been witnessed (receipted and the agent received the receipts).
- `response`: This field now contains the actual signed inception event (`icp`) for the newly created AID (`newAid`) originally submitted by the Client AID.
- `i`: The prefix of the AID now receipted and stored locally in the KERIA agent's database.
- `k`: The list of current public signing keys.
- `n`: The list of digests of the next (pre-rotated) public keys.
- `b`: The list of witness AIDs that this AID is configured to use.
- `bt`: The Threshold of Accountable Duplicity (TOAD) specified during creation (matches toad: 2 from our request).

The KERIA agent has successfully received the AID from the Controller AID, has communicated with witnesses to have the event receipted, and has stored its KEL, starting with the s inception event, in the local agent database.

## Managing Agent Operations

SignifyTS also provides methods to list and delete operations tracked by the KERIA agent for your client. This is useful to show in user interfaces so that the user knows when there are any in-progress operations for one or more managed AIDs.

### Listing Operations

Listing operations is agent-wide meaning all operations for all AIDs on this agent will be returned.


```typescript
// List all current long-running operations for this client
const operationsList = await client.operations().list();
console.log('\nCurrent Operations List:');
console.log(JSON.stringify(operationsList, null, 2));
```

    
    Current Operations List:


    [
      {
        "name": "witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
        "metadata": {
          "pre": "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
          "sn": 0
        },
        "done": true,
        "error": null,
        "response": {
          "v": "KERI10JSON0001b7_",
          "t": "icp",
          "d": "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
          "i": "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
          "s": "0",
          "kt": "1",
          "k": [
            "DDIdUqYZKNw1tqQsqidDt_IOMQrxsCkjodATHT2-GRcT"
          ],
          "nt": "1",
          "n": [
            "EFfw_k3SV0jNDfJaBx40OMw3mPzWqzhisVy9II3L1gU_"
          ],
          "bt": "2",
          "b": [
            "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
            "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
            "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"
          ],
          "c": [],
          "a": []
        }
      }
    ]


### Get Single Operation

A single operation may be retrieved by name in order to view its state. The name of an operation is formatted as `<role>.<digest>` and the example `witness.EF03TKpT68zTvOeFJM4pU64XEonLsZ29rxYFKN8u8AFO` shows that this operation is waiting on a witnessfor the `EF03TKpT68zTvOeFJM4pU64XEonLsZ29rxYFKN8u8AFO` identifier.


```typescript
console.log(`Icp op name: ${inceptionOperation.name}`);
const icpOp = await client.operations().get(inceptionOperation.name);
console.log("Inception operation");
console.dir(icpOp);
```

    Icp op name: witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF


    Inception operation


    {
      name: "witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
      metadata: { pre: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF", sn: 0 },
      done: true,
      error: null,
      response: {
        v: "KERI10JSON0001b7_",
        t: "icp",
        d: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
        i: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
        s: "0",
        kt: "1",
        k: [ "DDIdUqYZKNw1tqQsqidDt_IOMQrxsCkjodATHT2-GRcT" ],
        nt: "1",
        n: [ "EFfw_k3SV0jNDfJaBx40OMw3mPzWqzhisVy9II3L1gU_" ],
        bt: "2",
        b: [
          "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
          "BLskRTInXnMxWaGqcpSyMgo0nYbalW99cGZESrz3zapM",
          "BIKKuvBwpmDVA4Ds-EpL5bt9OqPzWPja2LigFYZN2YfX"
        ],
        c: [],
        a: []
      }
    }


### Waiting on an Operation

An operation may be waited on to know when an operation completes. Internally the SignifyTS library uses the `setTimeout` built-in along with an `AbortSignal` to control the polling loop that checks with the Signify controller's KERIA agent to determine operation status.


```typescript
// this code sample focuses on operating waiting and is a simple version of what is shown above
const aidAlias = 'waitAidExample';

const icpArgs = {
    toad: 1, 
    wits: ['BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha']
};

const icpRes = await client.identifiers().create(aidAlias, icpArgs);
const icpOp = await icpRes.op();
console.log('Inception Operation Details:');
console.log(inceptionOperation);

// the wait command below
console.log('Waiting for inception operation to complete...');
const operationResponse = await client
    .operations()
    .wait(icpOp, AbortSignal.timeout(5000)); // Pass the operation name
console.log("Inception operation complete");
```

    Inception Operation Details:


    {
      name: "witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF",
      metadata: { pre: "ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF", sn: 0 },
      done: false,
      error: null,
      response: null
    }


    Waiting for inception operation to complete...


    Inception operation complete


### Deleting Operations

As you have seen above old operations stay in the operation list which may or may not be desirable. You may delete operations if you want to clean up the operations list using the Operation delete API as shown below. Run the code as many times as you need in order to clear out the list, running the `.list()` command to verify your operations are being removed from the long-running operations response list.


```typescript
// Delete the completed inception operation (optional cleanup)
const opNameToDelete = operationsList[0].name;
await client.operations().delete(opNameToDelete);
console.log(`\nDeleted operation: ${opNameToDelete}`);
```

    
    Deleted operation: witness.ECmTNMrQYlKin_gqj3kOtN0XwHO5TIYBz1-Gz2tnbixF


Now run the `client.operations().list()` function to see that the operations have been cleared out.


```typescript
// List all current long-running operations for this client
const operationsList = await client.operations().list();
console.log('\nCurrent Operations List:');
console.log(JSON.stringify(operationsList, null, 2));
```

    
    Current Operations List:


    [
      {
        "name": "witness.EGH7tjO0WgOge87vFoghxigky8N4_RLZ_ZC_k5FWAW-F",
        "metadata": {
          "pre": "EGH7tjO0WgOge87vFoghxigky8N4_RLZ_ZC_k5FWAW-F",
          "sn": 0
        },
        "done": true,
        "error": null,
        "response": {
          "v": "KERI10JSON000159_",
          "t": "icp",
          "d": "EGH7tjO0WgOge87vFoghxigky8N4_RLZ_ZC_k5FWAW-F",
          "i": "EGH7tjO0WgOge87vFoghxigky8N4_RLZ_ZC_k5FWAW-F",
          "s": "0",
          "kt": "1",
          "k": [
            "DEdcIv9efB03ts7Hah6tym0XbXaD9P2GwtNluo2DQZdr"
          ],
          "nt": "1",
          "n": [
            "ECSf4N55OPixAdmKBwEIoZyZwKebtcEPZjxafH7iKX2L"
          ],
          "bt": "1",
          "b": [
            "BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha"
          ],
          "c": [],
          "a": []
        }
      }
    ]


<div class="alert alert-primary">
<b>📝 SUMMARY</b><hr>
To create a new AID using Signify-ts and a KERIA agent:
<ol>
<li>Use <code>client.identifiers().create(alias, config)</code> to create an inception event locally for a new AID and then send it to the KERIA agent for getting witness receipts and for storing the event and receipts in the agent database. Provide a client-side <code>alias</code> as a human-readable label for the AID and a <code>config</code> object specifying parameters like <code>toad</code> (Threshold of Accountable Duplicity) and <code>wits</code> (list of witness AIDs).</li>
<li>The <code>create()</code> method returns an object from which you can get a long-running <code>operation</code> object using <code>.op()</code>. This operation is initially marked as not <code>done</code>.</li>
<li>Use <code>client.operations().wait(operationName)</code> to poll the KERIA agent until the operation completes. The resolved object will have
<code>done: true</code> and its <code>response</code> field will contain the signed inception event (<code>icp</code>) of the newly created AID.</li>
<li>Operations can be listed with <code>client.operations().list()</code> and deleted with <code>client.operations().delete(operationName)</code>.</li>
<li>Individual operations may be retrieved with <code>client.operations().get(name)</code>.</li>
</ol>
This process highlights the asynchronous nature of KERIA operations that involve agent-side processing and network interactions.
</div>

[<- Prev (KERIA Signify)](102_05_KERIA_Signify.ipynb) | [Next (KERIA Signify Connecting Clients) ->](102_15_KERIA_Signify_Connecting_Clients.ipynb)
