<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Security Architecture and Assurance Boundaries

## Document status
Version: 0.1 (proposed)  
Status: design baseline; not an independent security assessment  
Applies to: the ASTON Agent Attestation JSON Schema and repository workflows

## Product boundary
This repository currently publishes a JSON Schema and a specification overview. It is not, by itself, a production verifier, key-management service, trusted execution environment, identity provider, transparency log, or certified SDK. Any implementation that consumes this schema must define and enforce its own trust policy.

## Security objectives
1. Preserve integrity of attestation bytes and referenced artifacts.
2. Make issuer, agent, execution, and evidence claims explicit and attributable.
3. Prevent an unverified or indeterminate result from being represented as verified.
4. Minimize sensitive data in attestations and logs.
5. Make provenance and verification decisions reproducible and auditable.
6. Fail closed when a required cryptographic or policy check cannot be completed.

## Trust boundaries
- Producer/runtime: supplies claims and evidence; is not trusted merely because it created an attestation.
- Attestation document: untrusted input until parsed and independently validated.
- Verifier: responsible for parsing, cryptographic verification, trust policy, revocation, timestamps, and policy result.
- Key and identity infrastructure: establishes which public keys are trusted for which issuers and purposes.
- External evidence services: timestamps, transparency logs, registries and artifact stores; each has independent availability and trust assumptions.
- Build/release pipeline: creates repository artifacts and provenance; must be assessed separately from runtime attestation verification.
- Consumer: decides whether a verified result is sufficient for its own risk context.

## Required verifier behavior (implementation requirement, not supplied by this schema)
- Reject malformed, oversized, ambiguous, or unsupported critical input.
- Verify signatures over a precisely specified canonical byte representation; never sign an ambiguously serialized object.
- Enforce algorithm allowlists and algorithm/key-type compatibility.
- Bind trusted issuer identity to key material through an independently configured trust policy.
- Check key validity, rotation, revocation and purpose constraints.
- Recompute all artifact digests from retrieved bytes; never trust a digest string alone.
- Validate timestamp and transparency proofs against their actual formats and trusted roots.
- Distinguish passed, failed, skipped and indeterminate checks; never map skipped/indeterminate to verified.
- Apply strict timeouts, size limits and safe parsing; avoid network fetches from arbitrary URIs by default.
- Record verifier version, policy version, trust-store version, checked subjects and evidence digests.
- Fail closed for security-critical checks. Preserve an explicit indeterminate state for unavailable optional evidence.

## Data handling
Do not embed prompts, credentials, personal data, customer payloads, private keys or confidential source material. Prefer digests and access-controlled references. URI dereferencing must be opt-in, allowlisted, SSRF-resistant and isolated. Define retention, deletion, access logging and data residency in the consuming product's own privacy and security documentation.

## Schema-level observations requiring future engineering decisions
- Digest algorithm names are free-form strings while digest values are constrained to hexadecimal characters; an implementation profile must bind algorithm identifiers to exact digest lengths and encodings.
- Signature algorithm and signature encoding are descriptive strings; the schema does not define a cryptographic suite, canonicalization method or verification semantics.
- The `verification.status` field can contain `verified`, but the schema cannot enforce that a verifier performed any checks. Producers must not self-assert a trusted verification result.
- JSON Schema `format` behavior depends on validator configuration; implementations must explicitly enable and test format assertions where required.
- `extensions` permits arbitrary nested content; consumers need extension allowlists, size/depth limits and critical-extension handling.
- Timestamp ordering (created/started/ended/signed/verified) and cross-field consistency are not fully enforced by this schema.
- URI fields can create SSRF, privacy and availability risks if a verifier dereferences them without policy.
- A valid schema document is not proof of identity, runtime integrity, execution, truth or non-repudiation.

## Assurance status
This document is a proposed control baseline. No independent cryptographic review, formal verification, penetration test, certification or production-verifier assessment is claimed. Controls become implemented only when code, tests and operational evidence demonstrate them.
