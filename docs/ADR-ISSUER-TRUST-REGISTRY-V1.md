<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ADR: Issuer Trust Registry v1

Status: Proposed — design only; no runtime trust decision is implemented by this document.

## Context

The SDK now validates the structure of an ASTON Agent Attestation document. Structural validity is not issuer authentication. The next security boundary is deciding whether the issuer and the signing key are trusted by the relying party.

The attestation's own `issuer`, `key_id`, `verification.status`, certificate URI, or other self-asserted fields MUST NOT establish trust. In particular, an input document that says `verification.status = "verified"` is still untrusted input until an independent verifier reaches that decision.

## Decision

Implement the first trust-registry slice as a **caller-controlled, explicit trust store** in the SDK. Do not introduce a hosted/global registry, automatic key discovery, or trust-on-first-use in v1.

A relying party supplies the trust anchors and revocation state through an explicit interface. ASTON does not become the authority that declares arbitrary issuers trusted.

### Trust record

Each record must bind, at minimum:

- A canonical issuer identifier.
- An exact key identifier scoped to that issuer.
- A supported public-key algorithm identifier and encoded public key.
- A validity interval (`not_before`, `not_after`).
- A lifecycle state (active or revoked).
- A stable record/version identifier and provenance for how the relying party installed the record.

The lookup key is the pair (issuer identifier, key identifier), never key identifier alone. Ambiguous matches, duplicate records, malformed records, unknown algorithms, and missing trust-store inputs fail closed.

### Resolution rules

1. Resolve the issuer/key pair only against the caller-supplied trust store.
2. Unknown issuer or key: reject as untrusted.
3. Revoked key: reject regardless of its nominal validity interval.
4. Before `not_before` or after `not_after`: reject.
5. Missing, malformed, or stale revocation state: reject; do not silently fall back to cached trust.
6. Never fetch a key from an attestation-provided URL and automatically trust it.
7. Never treat schema validation, a certificate pin fixture, or a self-declared verification status as issuer trust.
8. Key rotation requires an explicit new trust record; revocation of an old key takes precedence.

### Separation of responsibilities

Keep these stages distinct and expose separate outcomes:

- Structural validation: document matches the ASTON schema.
- Issuer/key resolution: caller's trust policy recognizes this exact issuer/key pair and its lifecycle state.
- Cryptographic verification: signature bytes verify over a precisely specified canonical payload and algorithm profile.
- Evidence verification: referenced digests, timestamps, transparency proofs, and runtime claims are independently checked where supported.
- Final policy decision: the relying party decides whether the verified evidence is sufficient for a particular action.

No earlier stage may imply success of a later stage. The SDK must not set or upgrade `verification.status` merely because issuer resolution succeeds.

### Fail-closed result model

Return explicit, machine-readable outcomes such as `trusted_key`, `unknown_issuer`, `unknown_key`, `revoked_key`, `not_yet_valid`, `expired_key`, `stale_revocation_state`, and `invalid_trust_record`. Errors must not disclose private key material or sensitive trust-store contents.

### Time and revocation

All comparisons use timezone-aware UTC instants. The caller supplies a trustworthy current-time source; tests inject a fixed clock. Revocation data must carry an issuance time and an explicit freshness deadline. If it is absent or past its freshness deadline, resolution fails closed. A future extension may define signed, portable registry snapshots and witnessed updates; that is out of scope for this first slice.

## Security and privacy constraints

- No private keys, credentials, raw prompts, or customer payloads in the registry.
- No implicit network requests during trust resolution.
- No trust-on-first-use, issuer self-registration, or issuer-controlled revocation override.
- No wildcard issuer/key trust.
- Algorithm allowlists are explicit; unknown or deprecated algorithms fail closed.
- Do not claim resistance to all cyberattacks or production certification from unit tests.

## Planned implementation sequence

1. Define typed trust-record and trust-store interfaces plus deterministic validation.
2. Add tests for unknown issuer/key, duplicate bindings, revoked, expired, not-yet-valid, stale revocation state, malformed records, and key rotation.
3. Add signature verification only after a separate ADR fixes canonical payload bytes, encoding, algorithm profile, and dependency policy.
4. Add end-to-end fixtures with test-only keys; never use test keys as production trust anchors.
5. Document limitations and independent relying-party responsibilities.

## Acceptance criteria

- No trust is inferred from attestation content alone.
- No network access or automatic key retrieval occurs.
- Every unknown, ambiguous, revoked, expired, malformed, or stale state is rejected.
- Clock behavior is deterministic in tests.
- Trust resolution does not claim that a signature, timestamp, transparency proof, or runtime claim has been verified.
- Free GitHub Actions checks cover unit tests, secret scanning, static analysis, dependency audit, and REUSE.

## Explicit non-goals

This ADR does not implement a public registry service, PKI certificate path validation, OCSP/CRL interoperability, transparency-log verification, runtime attestation, or a universal security guarantee. It does not modify production systems, Cloudflare, D1, releases, or the v1.0.0 provenance.
