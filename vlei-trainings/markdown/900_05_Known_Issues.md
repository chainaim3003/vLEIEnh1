# Known Issues

This document outlines several known issues that users may encounter while working with the KERI ecosystem. Understanding these issues can help in troubleshooting and setting expectations during development and testing.

## Issue 1: kli vc create Hangs with NI2I Operator

When creating a chained credential that uses the Not-Issuer-To-Issuee (`NI2I`) operator, the kli vc create command may hang indefinitely.

**Expected Behavior**

The command `kli vc create` should complete successfully when issuing a credential with an `NI2I` edge.

**Actual Behavior**

The command execution stalls after displaying the following log messages, and never completes

**Workaround**  
There is currently no known workaround for this issue.

For more technical details and to track the status of this issue, please refer to:https://github.com/WebOfTrust/keripy/issues/1040 

## Issue 2: KERIA Multisig State Synchronization Lag
In a multisig group managed by KERIA, members who are not required to sign an event (based on the signing threshold) may not have their local state updated after the event is completed by other members.

**Expected Behavior**

All members of a multisig group should be able to stay synchronized with the group's KEL, regardless of whether their signature was required for a specific event.

**Actual Behavior**

The problem is that multisig members in KERIA are not being updated with the latest state when they join a transaction after the fact. For example, if the signing threshold for a three-participant multisig group is set to 2-of-3 (e.g., ['1/2','1/2','1/2']), the operation completes as soon as the first two members sign. The third member, who did not sign, is not notified of the completed event and their local KEL for the group AID becomes outdated. They are unable to "see" the new event, such as a credential registry creation, that was anchored by the interaction.

**Workaround**

There is currently no known workaround for this issue. A temporary mitigation is to set signing thresholds to require signatures from all participants (e.g., 3-of-3), which forces all members to be involved and thus remain synchronized. However, this negates the flexibility and resilience benefits of partial thresholds.

For more technical details and to track the status of this issue, please refer to: https://github.com/WebOfTrust/keria/issues/316
