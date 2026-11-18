<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ADR: ASTON Supply Chain Defense v1

Status: Proposed — design only. This document defines boundaries and acceptance criteria; it does not implement a scanner, browser control, policy engine, or production protection.

## Context

A website can execute third-party JavaScript because its owner trusts a vendor, tag manager, CDN, analytics provider, experimentation platform, payment integration, or other supplier. If that supplier account, publishing workflow, signing key, or delivery infrastructure is compromised, a legitimate website may distribute malicious code without changing its own application code.

A valid HTTPS connection, a familiar domain, a vendor's signature, or a previously approved supplier identity is not sufficient proof that the exact script bytes are safe. The design must account for a malicious or compromised trusted supplier as well as an unknown supplier.

The existing Issuer Trust Registry ADR defines how a relying party recognizes an issuer/key pair. It does not establish that a particular software artifact is approved for execution. Supply-chain artifact authorization is a separate decision and MUST NOT be inferred from issuer trust alone.

## Security objective

Provide a verifiable, fail-closed decision about whether an exact third-party software artifact is authorized under a relying party's policy, and produce evidence explaining that decision.

The objective is risk reduction and containment. ASTON MUST NOT claim to prevent all cyberattacks, prove that arbitrary JavaScript is benign, or protect a website unless the website's build, deployment, delivery, or runtime controls actually enforce ASTON's decision.

## Threat model

In scope:

- A supplier account or tenant is compromised and publishes a changed script.
- A trusted vendor intentionally or accidentally ships malicious code.
- A CDN, tag manager, package registry, build pipeline, or release channel is compromised.
- An artifact is replaced while retaining the same URL, package name, or version label.
- A signing key is stolen, misused, expired, or revoked.
- A dependency is mutable, unpinned, substituted, or downloaded from an unexpected origin.
- A policy, approval, or revocation snapshot is missing, stale, ambiguous, or tampered with.
- A previously approved artifact changes after approval.

Out of scope for v1:

- Proving the absence of malicious behavior in source or minified JavaScript.
- Complete browser sandboxing or endpoint protection.
- Universal detection of DOM manipulation, form skimming, wallet substitution, credential theft, or data exfiltration.
- Automatic remediation on websites that have not integrated an enforcement point.
- Full PKI path validation, a public global vendor registry, or a universal transparency network.

## Decision

Design v1 as an artifact authorization and evidence layer with four distinct stages:

1. **Inventory** — identify each external script/component and its exact origin, immutable version reference where available, owning supplier, load context, and consuming application.
2. **Integrity** — calculate and compare a cryptographic digest of the exact artifact bytes against an independently approved digest. A URL, package name, version string, or vendor assertion alone is not an integrity pin.
3. **Authorization** — evaluate the artifact against a relying-party-controlled policy and approval record, including issuer/key trust, artifact digest, allowed origin/context, validity window, revocation state, and policy version.
4. **Enforcement and evidence** — return a deterministic allow/deny decision and an evidence record. The integrating build/deployment/browser/gateway control is responsible for blocking execution when the decision is deny or indeterminate.

No stage may imply success of a later stage. A trusted issuer does not automatically authorize every artifact it signs. A valid signature does not make an unapproved digest acceptable. A matching digest proves byte equality to the approved reference, not benign behavior.

## Artifact authorization record

An approved artifact record SHOULD bind:

- Canonical supplier/issuer identifier and exact signing key identifier, resolved through the separate issuer trust policy.
- Artifact identity and media/type classification.
- Cryptographic digest algorithm and digest of the exact bytes (SHA-256 minimum for v1).
- Immutable source/release reference and expected origin; mutable URLs must never be treated as immutable identities.
- Application, environment, and execution context in which the artifact is allowed.
- Version/release identifier, approval record identifier, approver identity, and approval timestamp.
- Validity interval, policy version, and revocation/freshness metadata.
- Provenance reference where available, independently verified under a separately specified provenance policy.

Records MUST reject duplicate or conflicting identities, unsupported digest algorithms, malformed fields, missing approval evidence, expired approvals, revoked signers/artifacts, and stale revocation state. Wildcard origins, wildcard artifact digests, and implicit trust-on-first-use are prohibited.

## Supplier compromise and independent approval

A supplier signature proves only that the corresponding signing key signed the bytes. It does not prove that the supplier account, release pipeline, or signing key was uncompromised.

For high-impact scripts (payment, authentication, wallet/financial flows, customer data, or privileged page contexts), relying-party policy SHOULD require an independent approval of the exact digest, with separation between the person or system proposing an update and the approver. Emergency changes must be explicit, time-bounded, attributable, and auditable; no silent auto-approval based solely on a vendor signature.

A changed digest is a new artifact and MUST trigger a new authorization decision even when the URL, filename, package name, or vendor version label is unchanged.

## Enforcement integration boundaries

The SDK can calculate digests, validate records, resolve trust, evaluate policy, and emit evidence. It cannot by itself stop a browser from executing code.

Integrators must choose and validate an enforcement point:

- **Build/CI:** fail the build when a required artifact is unapproved, mutable, mismatched, or lacks required provenance.
- **Deployment/CDN:** publish only approved immutable artifacts and prevent unreviewed replacement.
- **Browser delivery:** use restrictive Content Security Policy (CSP) and Subresource Integrity (SRI) where technically applicable. SRI checks the fetched resource against an integrity value; it is not a universal control for dynamically generated scripts, arbitrary inline code, or every tag-manager loading pattern.
- **Runtime monitoring:** detect inventory drift and policy violations, then block or isolate through a separately deployed enforcement mechanism.

CSP and SRI are complementary integration controls, not substitutes for independent artifact authorization. CSP must avoid broad source wildcards and unsafe allowances. Any use of nonces, hashes, `strict-dynamic`, dynamic script loaders, or tag managers requires an explicit threat analysis and browser compatibility tests.

If the integration cannot enforce a deny decision before execution, ASTON MUST report the control as monitoring-only, not blocking protection.

## Fail-closed decision model

Machine-readable outcomes SHOULD include:

- `authorized`
- `unknown_artifact`
- `digest_mismatch`
- `untrusted_issuer`
- `untrusted_signing_key`
- `revoked_signing_key`
- `revoked_artifact`
- `missing_approval`
- `expired_approval`
- `stale_revocation_state`
- `mutable_or_unpinned_source`
- `provenance_required_but_missing`
- `policy_mismatch`
- `invalid_or_ambiguous_record`

Only the exact `authorized` result may permit an artifact, and only within the recorded application, environment, origin, and execution context. Unknown, unavailable, stale, malformed, or indeterminate states deny execution at an enforcing integration. No fallback to a prior approval is allowed after a digest change or revocation.

## Monitoring and incident response

A later implementation MAY provide privacy-conscious drift signals for:

- New or changed script inventory.
- Unexpected origins, redirects, or dynamic script loaders.
- Artifact digest changes.
- CSP/SRI violations and repeated authorization denials.
- Unexpected changes to sensitive page elements or form destinations, where the integrator can observe these safely.

Signals are detections, not proof of maliciousness. Monitoring MUST minimize collected data. Do not collect card numbers, passwords, authentication cookies, session tokens, raw form contents, or full customer payloads. Evidence should record hashes, identifiers, policy versions, timestamps, decision codes, and minimal contextual metadata.

Revocation and response design SHOULD support: revoke the artifact or key, deny future loads, stop publication/deployment, roll back to a separately verified known-good artifact, preserve evidence, and notify the relying party. A kill switch must itself be authenticated, authorized, auditable, and resistant to replay.

## Evidence model

An authorization evidence record SHOULD include:

- Artifact digest and digest algorithm.
- Artifact/supplier identifiers and signing key identifier.
- Approval and provenance references, if present.
- Policy version and trust-store/revocation snapshot identifiers.
- Evaluation timestamp and freshness deadline.
- Decision code and stable reason codes.
- Integrator/enforcement point identity and whether the result was enforced or only observed.

Evidence MUST NOT imply that code is safe, that a browser executed the expected bytes, or that a deny decision was enforced unless the relevant integration supplies verifiable evidence for that fact. Avoid storing secrets or customer data.

## Implementation sequence

1. Define a typed artifact manifest and deterministic canonicalization rules.
2. Define digest calculation and exact-byte acquisition boundaries; do not fetch arbitrary remote URLs implicitly in the SDK.
3. Define artifact approval records and the relationship to the caller-controlled issuer trust store.
4. Implement a pure policy evaluator with an injected clock and explicit revocation freshness.
5. Add adversarial tests for changed bytes at the same URL, malicious-but-validly-signed unapproved artifact, unknown/revoked key, stale revocation, duplicate records, mutable source, missing approval, policy-context mismatch, and attempted fallback.
6. Define separate integration profiles for CI/build enforcement, deployment enforcement, and browser CSP/SRI generation. Each profile needs its own tests and evidence.
7. Add monitoring and response integrations only after their enforcement boundary and privacy model are reviewed.

## Acceptance criteria for the first implementation PR

- Artifact digest and issuer/key trust are separate mandatory checks.
- A valid supplier signature cannot authorize an unapproved digest.
- A changed artifact at the same URL is denied.
- Unknown, revoked, expired, stale, malformed, ambiguous, or context-mismatched state fails closed.
- No implicit network fetches occur during policy evaluation.
- Clock, trust store, revocation snapshot, and policy are explicit inputs for deterministic tests.
- No sensitive customer data or secrets are recorded.
- Tests distinguish a policy decision from actual browser/build/deployment enforcement.
- Free GitHub Actions checks cover tests, secret scanning, static analysis, dependency audit, and REUSE.
- Documentation states exactly which integration enforces a denial and which only reports it.

## Explicit non-goals and limitations

This ADR does not implement runtime protection, browser isolation, CSP/SRI deployment, a vendor reputation service, a global artifact registry, automated malware classification, or production enforcement. It does not modify Cloudflare, D1, production workers, release artifacts, or existing provenance. It does not claim that hashes, signatures, CSP, SRI, or ASTON alone can guarantee software is non-malicious or stop every supply-chain attack.
