<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ASTON Signed Revocation and Independent Approval v1 — Design

Status: DESIGN ONLY. This document defines the next SDK implementation boundary. It does not add runtime enforcement, cryptographic verification, key custody, or production controls.

## 1. Objective

The containment evaluator currently accepts a `RevocationSnapshot` as an in-memory object and delegates broad-scope approval verification to an injected callback. A caller could therefore accidentally supply an unauthenticated snapshot or an approval verifier with weaker semantics.

The next implementation must authenticate both inputs before a containment command can be accepted:

- a signed, freshness-bounded revocation snapshot;
- a separately signed approval envelope for tenant-wide or platform-wide actions.

All missing, malformed, stale, mismatched, or unverifiable trust inputs must fail closed.

## 2. Signed revocation snapshot

### Required fields

A versioned snapshot payload must contain:

- `version`: fixed value `aston-revocation-snapshot-v1`;
- `snapshot_id`: unique identifier;
- `issuer_id`: exact authority whose pinned public key verifies the signature;
- `issued_at` and `fresh_until`: integer UTC epoch seconds;
- `revoked_issuers`: unique, sorted issuer identifiers;
- `revoked_targets`: unique, sorted tuples of target type, target ID, and tenant ID (null only for platform scope).

The signature is Ed25519 over deterministic canonical UTF-8 bytes of every field above except the signature itself. The signature must use the SDK's canonical base64url encoding (no padding). Unknown snapshot issuers are rejected; no key discovery or trust-on-first-use is permitted.

### Validation requirements

- Reject unsupported versions, duplicate entries, invalid identifiers, malformed scopes, non-integer timestamps, future-issued snapshots beyond configured clock skew, expired snapshots, and non-positive validity windows.
- Enforce a configured maximum snapshot lifetime.
- Bind verification to the exact `issuer_id` in the payload.
- Require an explicit trust policy that authorizes the snapshot issuer for revocation publication; possession of a valid key alone is not authorization.
- A command may be evaluated only against an authenticated snapshot whose `fresh_until` is later than the evaluator's current time.
- Snapshot rollback protection must be explicit: persist the highest accepted sequence or issued-at value per revocation authority in a durable shared store. If that store is unavailable, deny. A timestamp alone is not sufficient where clocks or issuance can be manipulated; prefer a monotonically increasing sequence plus unique snapshot ID.

## 3. Independent approval envelope

### Required fields

A broad-scope approval envelope must contain:

- `version`: fixed value `aston-containment-approval-v1`;
- `approval_id`: unique, single-use identifier;
- `approver_id`: independently authenticated human or approval authority;
- `issuer_id`: signing authority for the approval envelope;
- `command_digest`: SHA-256 digest of the exact canonical containment command bytes;
- `target_type`, `target_id`, and `tenant_id`: repeated scope fields that must exactly match the command;
- `action`: exact approved action;
- `issued_at` and `expires_at`: short bounded validity window;
- `signature`: Ed25519 signature over deterministic canonical bytes of all other fields.

The approval signer must be distinct from the command issuer for tenant-wide and platform-wide actions. The policy must explicitly authorize the approver and approval issuer. A valid signature from an unapproved key is not a valid approval.

### Validation requirements

- Bind approval to the exact command digest, scope, action, and validity interval.
- Reject self-approval by the command issuer for broad-scope actions.
- Reject expired, future-issued, malformed, mismatched, unknown, or unauthorized approvals.
- Consume `approval_id` atomically in the same durable replay domain as command IDs (or in a transactionally coordinated store). Reuse must be rejected.
- Approval consumption and command replay claim must be atomic with respect to the final authorization decision. If the backing store cannot guarantee the required transaction semantics, the adapter must document the weaker guarantee and the evaluator must not claim atomic cross-record consumption.
- Do not treat a text token, caller-supplied boolean, or callback returning true without cryptographic and policy checks as independent approval.

## 4. Key separation and rotation

- Command-signing, revocation-publication, and approval-signing authorities must be separately identified and authorized.
- The same public key may not silently acquire multiple authority roles.
- Key provisioning, rotation, revocation, and recovery must be authenticated out of band.
- No private key material belongs in the SDK repository, tests, fixtures, or CI secrets.
- HSM/KMS integration is a future deployment adapter; this SDK design does not claim hardware-backed custody.

## 5. Required adversarial tests before implementation can be called TESTED

1. Valid signed snapshot accepted; modified payload and modified signature rejected.
2. Unknown or unauthorized snapshot issuer rejected.
3. Expired, future-issued, overlong, duplicate-entry, malformed-scope, and unsupported-version snapshots rejected.
4. Older snapshot sequence rejected after a newer snapshot has been accepted.
5. Rollback-store outage fails closed.
6. Valid approval accepted only for the exact command digest, target, tenant, action, and validity window.
7. Approval for a different command, tenant, target, or action rejected.
8. Approval signed by command issuer rejected for broad-scope actions.
9. Unknown or unauthorized approver and approval issuer rejected.
10. Expired, future-issued, malformed, or altered approval rejected.
11. Approval replay and command replay rejected under concurrent attempts.
12. Failure between approval consumption and command claim cannot produce an accepted decision or silently permit replay.
13. No private keys or secret material appear in repository files, logs, or CI artifacts.

## 6. Explicit non-goals

This design does not implement or prove:

- a live kill switch, process isolation, workload quarantine, or provider-side credential revocation;
- production key custody, HSM/KMS, key rotation operations, or independent human identity verification;
- a distributed transactional replay/rollback service;
- runtime wiring, Cloudflare deployment, D1 migration, or production enforcement;
- resistance to compromise of every independent authority or the host executing the evaluator.

## 7. Status vocabulary

- DESIGN: this document specifies an implementation contract only.
- IMPLEMENTED: must wait until concrete canonicalization, signature, authorization, freshness, rollback, and replay adapters exist.
- TESTED: must wait until the adversarial tests above pass in CI.
- VALIDATED: must wait for independent security review and deployment-level storage/key-custody validation.
- PRODUCTION: must not be claimed until a real enforcement point is deployed and operationally tested.
