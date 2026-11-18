<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ASTON Containment Policy Primitives v1

Status: implementation candidate in review. These primitives evaluate an emergency containment command. They do not isolate a process, disable a credential, revoke a key at an external provider, or operate a production kill switch.

## Implemented in this change

- Immutable typed commands with explicit target and action enums.
- Deterministic UTF-8 command encoding with a version marker. The encoding is intentionally limited to strings, enum values, integer timestamps and null; it is not advertised as RFC 8785/JCS.
- Required tenant scope for tenant-bound targets; platform-wide scope must be explicit.
- Bounded command lifetime, expiry and limited future-clock tolerance using an injected integer clock.
- Fail-closed revocation snapshot freshness, issuer revocation and exact target revocation checks.
- Required signature-verification and issuer-authorization adapters. Missing or failing trust adapters deny the command.
- Independent approval adapter required for tenant-wide and platform-wide containment.
- Atomic replay-claim interface; duplicate commands and replay-store failures deny the command.
- Deterministic reason codes suitable for audit evidence.

## Security adapter contract

The caller MUST supply:
1. A signature verifier that cryptographically verifies the signature over `canonical_command_bytes(command)` against a key resolved from an independently maintained trust policy.
2. An issuer authorizer that confirms the issuer is allowed to issue this action for this exact target and tenant.
3. A durable, atomic, shared replay store implementing `ReplayGuard.claim`. The storage must prevent two concurrent workers from claiming the same command ID.
4. For tenant/platform-wide commands, an independent approval verifier whose trust domain and credentials are separate from the command issuer and affected workload.

The SDK does not ship a permissive default for any adapter. A boolean callback is an integration seam, not cryptographic proof by itself. Adapter correctness and key custody require separate implementation and review.

## Explicit limitations

- No Ed25519/RSA/ECDSA implementation or key registry is added in this stage.
- No durable replay database is included; an in-memory set is not suitable for production.
- No kill switch, process isolation, credential-provider revocation, tenant suspension, evidence export, backup/restore, or runtime enforcement is wired.
- The policy evaluator does not itself prove that a revocation snapshot was signed. The caller must authenticate the snapshot source before constructing it.
- The deterministic encoding is a versioned ASTON format, not an RFC 8785 implementation. Cross-language interoperability requires a separately specified and tested canonicalization standard before external adoption.

## Validation plan

The accompanying unit tests cover valid scoped commands, deterministic encoding, invalid signatures, issuer denial, expiry, future timestamps, excessive validity, stale/revoked trust snapshots, tenant/platform scope, independent approval, replay, and unavailable adapters. CI results must be reviewed before this change is considered tested.

## Status vocabulary

- IMPLEMENTED: the pure Python policy evaluator and adapter interfaces exist in this branch.
- TESTED: only after the relevant CI test job completes successfully.
- VALIDATED: not claimed; independent cryptographic adapter review, persistent replay-store concurrency tests, and integration tests are still required.
- PRODUCTION: not claimed; no runtime enforcement or deployment is included.
