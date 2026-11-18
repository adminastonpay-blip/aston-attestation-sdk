<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ADR: ASTON Compromise Containment and Recovery v1

Status: Proposed — architecture and acceptance criteria only. This ADR does not implement an isolation controller, kill switch, backup service, key-management system, or production recovery workflow.

## 1. Objective

Define how an ASTON-integrated system limits the blast radius of a compromised identity, agent, signing key, supplier, workload, control-plane component, or administrator account, and how it returns to a demonstrably known-good state.

The security objective is not to promise that ASTON cannot be compromised. It is to ensure that one compromised component does not automatically confer control over unrelated tenants, identities, keys, policies, evidence, or recovery authority.

## 2. Scope and relationship to existing controls

This ADR complements:
- the Issuer Trust Registry design: issuer and key trust are explicit relying-party decisions;
- the Supply Chain Defense design and artifact policy: exact artifact bytes require independent approval;
- the Incident Response Plan: incident severity, investigation, communications and response;
- the Business Continuity and Disaster Recovery plan: backup and restoration objectives;
- runtime authorization and durable human approval controls: actions require explicit policy and approval.

It does not replace those controls. A policy decision, audit record, signature, backup, or kill-switch command is useful only when its own trust boundary is independently protected and tested.

## 3. Threat model

In scope:
- a workload or AI agent is compromised and attempts lateral movement;
- a tenant identity, service credential, API token, or signing key is stolen;
- a trusted supplier or software artifact becomes malicious;
- an administrator or CI identity is compromised;
- a policy, trust store, revocation feed, or authorization service is altered;
- an attacker attempts to disable monitoring, erase evidence, block revocation, or prevent recovery;
- an attacker abuses emergency shutdown or recovery controls to cause denial of service;
- a backup or restore source contains attacker-controlled state.

Assumptions:
- prevention can fail;
- detection may be delayed or incomplete;
- control-plane and data-plane components can fail independently;
- external providers may be unavailable or compromised;
- clocks, logs, and status signals are not automatically trustworthy;
- recovery must not trust the same credentials or mutable state suspected in the incident.

Out of scope for this v1 design:
- guaranteed detection of every intrusion;
- proof that arbitrary AI behavior is benign;
- universal endpoint or browser protection;
- automatic safe recovery without an operator or independently authorized policy;
- claims of immunity to nation-state attackers or zero-day vulnerabilities.

## 4. Core architecture principles

### 4.1 Separate security domains

At minimum, implementations MUST distinguish:
1. **Workload/data plane:** agents, tools, application requests and tenant data.
2. **Policy/control plane:** identity resolution, policy evaluation, approvals and authorization.
3. **Evidence plane:** security events, decisions, integrity checkpoints and incident records.
4. **Recovery plane:** recovery identities, trusted snapshots, key rotation and restoration authority.

A workload credential MUST NOT administer the policy plane, erase evidence, or authorize its own recovery. The evidence plane MUST NOT accept write authority from the workload being monitored. Recovery authority MUST NOT depend solely on credentials or infrastructure that may be compromised in the incident.

### 4.2 Least privilege and bounded authority

- Every identity is scoped to a tenant, workload, action, resource and environment.
- No wildcard tenant, implicit default tenant, or fallback identity is permitted for privileged operations.
- Credentials are short-lived where supported, purpose-bound and revocable.
- Administrative, release, signing and recovery roles are separated.
- Privileged changes require attributable approval and produce evidence.
- A successful authentication is not equivalent to authorization.

### 4.3 Fail-closed with explicit safe modes

If a required trust, authorization, revocation or integrity check is unavailable, the affected high-risk action is denied. Implementations MAY define a narrowly scoped read-only or degraded mode only when its allowed operations, data exposure and expiry are explicit and tested. There MUST be no silent fallback to a weaker policy.

A global shutdown is not the default response to every anomaly. Containment should be scoped to the affected tenant, identity, key, artifact, workload or capability unless evidence justifies a wider stop. This reduces attacker-triggered denial-of-service risk.

## 5. Containment model

### 5.1 Containment targets

The policy model SHOULD support independent suspension or revocation of:
- one agent/workload identity;
- one service credential or session;
- one issuer or signing key;
- one artifact digest or release;
- one tenant;
- one tool/action capability;
- one integration or supplier;
- one policy version or trust snapshot.

Revocation of one target MUST NOT silently revoke unrelated tenants or identities. Wider containment requires a separately recorded reason and authorization.

### 5.2 Kill switch / emergency interlock

An emergency interlock MUST:
- be outside the workload's administrative control;
- accept authenticated, authorized, replay-resistant commands;
- bind the command to target, scope, reason, issuer, issue time, expiry and unique command ID;
- enforce a short, bounded validity window;
- support idempotent execution and explicit status reporting;
- preserve evidence of request, approval, execution and failure;
- require stronger authorization for broad tenant or platform-wide actions;
- have a tested recovery path that does not reuse the suspected compromised credential.

A single static bearer token, environment variable, shared secret, or agent-controlled flag is not an adequate emergency authority.

For high-impact platform-wide actions, the implementation SHOULD use two-person approval or a threshold/quorum design with independently administered credentials. A quorum must not be reducible to two credentials stored in the same account or control plane.

The interlock MUST fail safely if command authenticity or authority cannot be established. Its availability failure must not be represented as successful containment.

### 5.3 Blast-radius boundaries

- Tenant data and authorization caches are tenant-scoped.
- Agent-to-agent communication is denied by default and explicitly granted.
- Tool credentials are separate per workload and purpose.
- One tenant's policy administrator cannot administer another tenant.
- A workload cannot mint or extend its own permissions.
- Shared services expose narrow APIs and enforce tenant identity at each boundary, not only at the gateway.
- High-risk actions re-check current authorization at the point of execution.

### 5.4 Detection and trigger quality

An anomaly is a signal, not proof of compromise. Automated containment rules MUST document:
- the observable signal and its source;
- confidence and known false-positive modes;
- affected scope;
- action and duration;
- whether a human approval is required;
- rollback and appeal path;
- evidence retained.

A low-confidence signal may trigger additional verification or a limited safe mode, but MUST NOT silently trigger irreversible platform-wide actions.

## 6. Evidence integrity during compromise

Security events SHOULD be exported to an independently administered evidence destination with:
- event ID and monotonic sequence or equivalent ordering metadata;
- event time plus ingestion time and clock-quality indicator;
- tenant/workload/identity scope;
- policy, artifact, trust-store and revocation snapshot identifiers;
- requested action, decision, reason code and enforcement result;
- actor identity and approval references;
- content digest and integrity linkage where applicable.

Do not log credentials, private keys, session tokens, passwords, payment data, raw prompts or unnecessary customer payloads.

The evidence destination SHOULD use append-only or tamper-evident retention and separate administrative authority. A local hash chain alone does not prevent an attacker with control of the entire store from rewriting the chain. Periodic independent checkpoints or externally retained digests are required for stronger tamper evidence.

If evidence export is unavailable, the implementation must record the gap and apply a documented policy. High-risk operations may need to stop when evidence persistence is a mandatory control.

## 7. Recovery model

Recovery MUST be treated as a new trust-establishment process, not simply restarting a stopped process.

1. **Declare scope:** identify affected tenants, identities, keys, artifacts, policies, systems and time window. Mark unknowns explicitly.
2. **Preserve evidence:** snapshot relevant logs, commits, workflow runs, artifact digests, configuration and provider audit records before destructive cleanup where feasible.
3. **Contain:** revoke affected sessions, credentials, keys, artifacts and permissions; isolate affected workloads; stop affected releases.
4. **Establish a clean root:** use separately controlled recovery identities and known-good source/configuration. Do not rely on the suspected compromised control plane as the sole source of truth.
5. **Rebuild:** create clean artifacts from a reviewed known-good commit in a trusted build process; pin dependencies and verify artifact digests and provenance independently.
6. **Restore minimally:** restore only required data and configuration from a verified snapshot. Scan and reconcile restored state; do not blindly restore compromised credentials, policies or sessions.
7. **Rotate and re-issue:** rotate affected secrets and keys using documented custody and approval procedures. Publish revocations before trusting replacements.
8. **Validate:** run security, tenant-isolation, authorization, replay, integrity, recovery and adversarial regression tests.
9. **Re-enable gradually:** restore one tenant/capability at a time with explicit approval, monitoring and rollback criteria.
10. **Close with evidence:** publish an incident record and corrective actions; do not claim full recovery while material unknowns remain.

## 8. Recovery trust anchors and backups

- Keep recovery credentials separate from daily developer and workload credentials.
- Maintain at least one independently administered, read-only source mirror and protected backup of required release/evidence metadata.
- Encrypt backups and separate backup-write, backup-delete and restore permissions.
- Use immutable retention where supported and appropriate.
- Verify backup integrity by digest and perform actual restore exercises.
- Keep trusted recovery configuration versioned and attributable.
- Require dual control for destructive backup deletion and platform-wide trust-root changes.
- Treat a backup as untrusted until its integrity and provenance are checked.

Recovery objectives in the existing continuity plan remain proposed targets until measured by exercises.

## 9. Adversarial validation plan

A future implementation MUST include deterministic tests for at least:

| Test | Attack/failure | Expected result |
|---|---|---|
| CT-01 | Compromised agent requests another tenant's data | Deny; no cross-tenant read or side effect |
| CT-02 | Workload attempts to change its own policy or trust store | Deny; evidence written outside workload authority |
| CT-03 | Revoked credential is replayed | Deny; no fallback to cached authorization |
| CT-04 | Kill-switch command has invalid signature/authority | Reject; report containment as not executed |
| CT-05 | Kill-switch command is replayed or expired | Reject idempotently; preserve evidence |
| CT-06 | One tenant is contained | Other tenants remain isolated and unaffected |
| CT-07 | Broad shutdown requested by one compromised administrator | Require independent quorum; reject if absent |
| CT-08 | Evidence sink is unavailable | Apply documented fail-closed/degraded policy; expose evidence gap |
| CT-09 | Local evidence store is rewritten | Independent checkpoint detects inconsistency |
| CT-10 | Backup contains revoked key or compromised policy | Restore process rejects unsafe state |
| CT-11 | Recovery credential is unavailable | No silent use of workload credential; recovery failure is explicit |
| CT-12 | Restored service starts with stale revocation snapshot | High-risk operations remain denied |
| CT-13 | Clean rebuild uses substituted dependency | Digest/provenance policy rejects artifact |
| CT-14 | Recovery is attempted from compromised source commit | Known-good commit verification fails |
| CT-15 | False-positive anomaly targets one tenant | Scoped, reversible response; no unjustified global shutdown |

Tests MUST verify both the security decision and the actual enforcement side effect. Unit tests of a policy function alone do not prove isolation in a deployed system.

## 10. Implementation sequence and gates

**Stage A — architecture and contracts (this ADR):**
- define trust domains, scope, command semantics, recovery invariants and adversarial tests;
- review against existing incident response and continuity documents.

**Stage B — pure policy primitives:**
- typed containment targets and commands;
- strict canonical representation and cryptographic command verification;
- injected clock, nonce/replay state and explicit revocation snapshot;
- deterministic policy decisions and reason codes;
- unit and property-based tests where tooling permits.

**Stage C — enforcement adapter:**
- integrate with a non-production test harness;
- prove tenant/workload isolation and point-of-action authorization;
- demonstrate scoped suspension and revocation;
- test failure behavior when control plane or evidence sink is unavailable.

**Stage D — recovery harness:**
- restore from verified fixture snapshots;
- reject compromised/stale trust state;
- rotate fixture keys and re-enable a single isolated test tenant;
- retain reproducible recovery evidence.

**Stage E — independent assessment:**
- threat-model review, code review, adversarial testing and scoped penetration test;
- remediate findings before any production claim.

Each stage requires a separate reviewed PR and explicit approval before merge or deployment. No stage automatically authorizes Cloudflare, D1, production worker, customer-data or live-key changes.

## 11. Acceptance criteria

The design is ready for implementation only when reviewers confirm:
- trust domains and administrative authorities are distinct and explicit;
- containment is scoped, reversible where possible and resistant to replay;
- emergency authority cannot be exercised by the workload it contains;
- high-impact global actions require independent approval;
- evidence and recovery sources do not share the compromised workload's write authority;
- restore procedures re-establish trust instead of restoring it blindly;
- each automated action has defined false-positive handling and expiry;
- adversarial tests cover both decisions and enforcement;
- operational owners, escalation contacts and recovery custodians are assigned before production use.

## 12. Explicit limitations

This ADR is design-only. It does not implement or validate isolation, a kill switch, quorum authorization, tamper-evident external logging, key custody, backup immutability, disaster recovery, or production enforcement. It does not establish that ASTON is secure against all attackers. Those claims require implementation evidence, integration tests, independent assessment and operational exercises.
