import fs from "fs";
import {resolveEnvironment} from "../../client/resolve-env.js";
import {getOrCreateClient} from "../../client/identifiers.js";
import {createRegistry} from "../../client/credentials.js";

// process arguments
const args = process.argv.slice(2);
const env = args[0] as 'docker' | 'testnet';
const passcode = args[1];
const aidName = args[2];
const registryName = args[3];
const registryInfoPath = args[4];

// get client and create registry
const client = await getOrCreateClient(passcode, env);
const registryInfo: any = await createRegistry(client, aidName, registryName);
await fs.promises.writeFile(registryInfoPath, JSON.stringify(registryInfo));
console.log(`Registry info written to ${registryInfoPath}`)
