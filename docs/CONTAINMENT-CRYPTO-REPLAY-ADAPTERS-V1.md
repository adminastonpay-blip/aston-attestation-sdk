<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ASTON Containment Cryptographic and Replay Adapters v1

Status: implementation candidate in review. This change adds concrete SDK adapters; it does not connect them to a production enforcement point.

## Ed25519 issuer keyring

- Uses the already hash-pinned `pycryptodomex==3.24.2` dependency, now declared directly in `requirements.txt`.
- Accepts an explicit mapping of issuer IDs to PEM-encoded Ed25519 public keys.
- Rejects empty keyrings, private keys, non-Ed25519 keys, unknown issuers, malformed signatures and altered payloads.
- Verifies the signature over the exact canonical command bytes.
- Does not fetch keys, trust new issuers automatically, or decide how keys are provisioned, rotated or revoked.
- Public keys must be provisioned through a separate authenticated trust-management process.

The policy evaluator now passes the command's issuer ID to the signature verifier, preventing a caller from accidentally using an unrelated issuer's key without an explicit mapping.

## SQLite replay guard

- Uses a primary-key constraint on command ID and `BEGIN IMMEDIATE` to serialize claims.
- Duplicate IDs are rejected, including when two separate SQLite connections attempt the same claim.
- Claims remain in the database after command expiry. This prevents reuse of old identifiers; retention/compaction requires a separately reviewed policy.
- The caller supplies the database connection. A persistent file on durable storage is required for deployment; `:memory:` or ephemeral container storage is test-only.
- The adapter does not provide distributed replay protection across independent database files or hosts. A shared, correctly operated database is required for multi-instance deployments.

## What remains outside this change

- No production key registry, HSM/KMS integration, automated key rotation or independent key-revocation distribution.
- No cryptographic authentication of revocation snapshots or independent approval tokens.
- No distributed database service, process isolation, credential-provider revocation, kill switch, runtime enforcement, recovery workflow or Cloudflare integration.
- The SQLite adapter is a concrete local persistence implementation, not evidence that production storage has been provisioned or hardened.

## Status vocabulary

- IMPLEMENTED: concrete Ed25519 verification and SQLite replay adapter code exists in this branch.
- TESTED: only after CI passes the signature, tampering, unknown-issuer, persistence and concurrency tests.
- VALIDATED: not claimed; independent key-management review, production storage durability review, multi-process/multi-host tests and integration assessment remain.
- PRODUCTION: not claimed; nothing is deployed or connected to a live enforcement point.
