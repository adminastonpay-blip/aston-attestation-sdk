<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Threat Model

## Scope and assumptions
This threat model covers the published attestation schema, example proof-package workflow and repository supply-chain configuration. It does not claim to cover every future runtime, integration, tenant environment or production verifier. The repository is currently a schema/specification project; deployment-specific threats require a separate assessment.

## Assets
- Integrity and availability of source, schema, release artifacts and evidence.
- Authenticity of release provenance and cryptographic proof material.
- Trust-policy configuration, public-key identity bindings and revocation data in future verifiers.
- Confidentiality of private keys, access tokens, prompts, customer data and vulnerability reports.
- Accuracy of verification outcomes and audit records.
- Maintainer accounts, repository permissions, CI identities and release controls.

## Adversaries
- Malicious contributor or compromised maintainer account.
- Compromised GitHub Action, package dependency, runner or release workflow.
- Attacker submitting malformed or oversized JSON/proof packages.
- Attacker controlling a URI, registry, evidence endpoint or DNS response consumed by a verifier.
- Issuer attempting key confusion, replay, false identity or misleading claims.
- Insider or external actor attempting to replace release assets or provenance.
- Opportunistic attacker exploiting exposed secrets, permissive permissions or weak recovery procedures.

## Attack scenarios and required mitigations
| Scenario | Potential impact | Required controls / validation |
|---|---|---|
| Forged or self-asserted `verified` status | False trust decision | Verifier-generated result; signed result record; producer status ignored for trust decisions |
| Algorithm/key confusion or downgrade | Invalid signature accepted | Algorithm allowlist; key-type binding; reject unknown/weak algorithms; negative tests |
| Signature over ambiguous serialization | Signature bypass or inconsistent interpretation | Defined canonicalization and exact signed payload; cross-implementation test vectors |
| Key compromise or stale trust root | Attacker impersonates issuer | Key rotation, revocation, short-lived identity, trust-root governance and incident drills |
| Replay of old valid attestation | Stale execution accepted | Nonces/challenges where needed, audience, freshness policy, unique IDs and replay cache |
| Digest substitution / TOCTOU | Wrong artifact accepted | Recompute digest over exact bytes; immutable content-addressed storage; bind subject to provenance |
| Malicious URI / SSRF | Internal service access or data exfiltration | No automatic dereference; allowlists, DNS/IP validation, egress controls, redirect limits |
| Parser/resource exhaustion | DoS | Byte, nesting, array, string and CPU limits; timeouts; fuzzing |
| Extension abuse | Parser differential / hidden payload | Namespaced allowlist; critical-extension rules; strict validation |
| Timestamp or transparency proof spoofing | False chronology | Verify native proof format and trusted log roots; distinguish pending from verified |
| CI workflow compromise | Malicious release or forged provenance | Full-SHA action pins, least privilege, protected environments, independent provenance verification |
| Dependency compromise | Supply-chain compromise | Lockfiles/hashes, Dependabot, dependency review, SBOM, vulnerability triage |
| Secret leakage | Account or signing compromise | Secret scanning/push protection, short-lived credentials, rotation and audit |
| Maintainer unavailability | Security response/release paralysis | Two-person continuity, documented recovery and delegated authority |
| Misleading badge or marketing claim | Investor/customer trust damage | Evidence register, dated snapshots, claim approval and explicit status labels |

## Security invariants
1. No failed, skipped or indeterminate mandatory check may produce a trusted `verified` result.
2. No document is trusted solely because it validates against JSON Schema.
3. No key is trusted solely because its identifier appears in the document.
4. No artifact is trusted solely because its digest is stated in the document.
5. No provenance is trusted solely because a badge or workflow file exists.
6. No optional network evidence is fetched without an explicit safe retrieval policy.

## Residual risk
The schema cannot enforce runtime behavior, key custody, identity proofing, replay prevention, revocation, secure storage or availability. These remain obligations of each verifier/product implementation and its operator.
