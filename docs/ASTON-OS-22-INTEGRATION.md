# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
# ASTON OS 22 — Attestation SDK Integration

## Role
The SDK defines portable agent-attestation structures and verification tooling. A schema-valid package is structurally valid; it is not automatically authentic, authorized, fresh, or externally anchored.

## Verification layers
1. Parse and validate the versioned schema.
2. Verify canonical payload digest and signature against a trusted key set.
3. Check issuer, subject, tenant, audience, timestamps, nonce/replay state, and revocation policy.
4. Verify optional external timestamp proofs independently.
5. Return structured results per layer; never collapse partial success into an overall verified result.

## Compatibility
- Preserve released schema identifiers and fixtures.
- Introduce breaking semantics only through a new schema version.
- Keep verification deterministic and fail closed for unknown critical versions.
- Do not publish a release, rotate signing keys, or alter SLSA provenance from this branch.
