<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Artifact policy v1 — implementation boundary

The first artifact-policy implementation evaluates exact bytes supplied by the caller against a caller-managed approval and explicit policy inputs.

## What it does

- Computes SHA-256 over the exact bytes supplied to the evaluator.
- Requires an explicit issuer/key pair in the caller's trusted-key set.
- Rejects revoked keys/artifacts, expired approvals, stale revocation snapshots, mutable-source declarations, and application/environment/context mismatches.
- Returns a deterministic machine-readable decision. Only the exact authorized result has allowed=true.

## Integration boundary

The module does not verify vendor signatures or provenance. The trusted-key set must be populated only after independent issuer/key verification. It does not fetch URLs, inspect source semantics, detect malware, or prove that an artifact is benign.

The immutable-source flag is a caller assertion; the integration must establish that the referenced release is immutable. This module does not block a browser. A build/deployment/browser integration must enforce a denial before execution.

## Minimal integration sequence

1. Obtain exact artifact bytes from a controlled build or delivery pipeline.
2. Load the approval record and trust/revocation inputs from an independently administered policy source.
3. Evaluate the artifact before publishing or executing it.
4. Stop the build/deployment/load unless the decision is authorized.
5. Preserve the decision evidence without recording customer data or secrets.

Passing unit tests does not establish production protection.
