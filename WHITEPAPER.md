<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ASTON Trust Fabric
## A verifiable evidence layer for AI agents and automated decisions

**Whitepaper draft — November 2026**  
**Project:** ASTON Agent Attestation / `aston-attestation-sdk`  
**Status:** Concept and reference implementation direction; not a certification or production-readiness claim.

---

## Abstract

AI agents increasingly make recommendations, transform data, call tools, and initiate consequential workflows. Yet an output that looks authoritative is not necessarily reproducible, attributable, or independently auditable. Application logs can be incomplete or mutable; model-provider records may be inaccessible to the party affected by a decision; and a signed statement can still contain false claims.

ASTON Trust Fabric is a proposed, implementation-neutral evidence layer for recording agent activity as structured attestations and allowing independent parties to verify selected integrity claims. Its foundation is deliberately narrower than “proving an AI is correct”: identify the claims, bind evidence to exact bytes with cryptographic digests and signatures, establish key trust independently, and optionally anchor commitments to a public timestamping system such as Bitcoin through OpenTimestamps.

The design pairs cryptographic verification with **Fail-Closed** decision rules. When a required check fails, is missing, or remains indeterminate, the system must not silently promote the package to verified or authorize a protected action. The result is not a guarantee of truth or safety. It is a disciplined way to distinguish evidence-backed facts, unverified assertions, and unavailable checks.

## 1. The problem: capable AI, weak audit trails

AI systems are moving from conversational interfaces into operational environments: finance, commerce, logistics, software delivery, customer service, research, and internal enterprise workflows. In these settings, it is no longer enough to retain only a final answer or a conventional application log.

An auditor may need to answer questions such as:

- Which agent, model, version, and runtime were declared for a particular execution?
- What inputs, outputs, and artifacts were involved, without exposing sensitive payloads?
- Has the recorded artifact changed since it was signed?
- Which party issued the record, and why should its signing key be trusted?
- Did the evidence exist by a particular point in time?
- Which checks were actually performed, by whom, under what policy, and with what result?

Traditional logs are useful operational records, but they may be mutable, fragmented across providers, or controlled by the same operator whose actions are being reviewed. A model-generated explanation is not independent evidence. A hash without a trusted reference does not establish who committed to the data. A signature without key governance does not establish the signer's real-world identity. And a timestamp without a verified proof should not be presented as a completed public anchor.

The core gap is therefore not simply a lack of more logs. It is the lack of a portable evidence package that an independent verifier can examine without trusting the agent's own user interface or calling its production runtime.

## 2. ASTON Trust Fabric: an evidence-first architecture

ASTON Trust Fabric is the architectural vision around the open ASTON Agent Attestation format. The repository currently publishes a JSON Schema (Draft 2020-12), a verification guide, and a reference proof-package verifier. The schema provides a common structure for declarations and evidence references; it does not itself perform cryptographic verification.

A typical attestation can describe:

1. **Agent and issuer:** identifiers, declared versions, provider, runtime, and issuer key references.
2. **Execution context:** run identifier, timestamps, environment metadata, and deployment references.
3. **Integrity commitments:** algorithm-labelled digests for inputs, outputs, configuration, and artifacts.
4. **Provenance:** source references and links to preceding attestations.
5. **Claims and evidence:** statements, evidence references, and explicit claim status.
6. **Verification record:** verifier identity, policy reference, checks performed, and outcomes.
7. **Transparency references:** external log or timestamp proof identifiers and anchor state.

Sensitive prompts, credentials, and private payloads should not be embedded by default. A deployment can retain protected evidence in its own controlled storage and place only a digest and access-controlled reference in the attestation. This supports data minimization while allowing an authorized auditor to retrieve and compare the underlying material when necessary.

The format is intended to be vendor-neutral. Independent agent platforms, auditors, enterprises, and tool providers should be able to produce or consume attestations without depending on ASTON's runtime. Interoperability requires published profiles for signature algorithms, canonical byte handling, key identifiers, trust policies, and timestamp interpretation; a schema alone cannot settle those operational choices.

## 3. Cryptographic integrity and Bitcoin anchoring

The proof-package model separates three questions that are often incorrectly conflated.

**Integrity:** A cryptographic digest commits to a particular byte sequence. A detached digital signature can then authenticate that commitment against a public key. A successful signature check establishes that the exact signed bytes verify under that key. It does not prove that the claims are true or that the key belongs to the named organization.

**Identity and authorization:** The verifier must establish trust in the signing key through an independently trusted certificate authority, an authenticated fingerprint, or another documented trust mechanism. The verifier must also decide whether that key is authorized for the asserted role, and account for validity, revocation, key rotation, and algorithm policy.

**Time evidence:** OpenTimestamps can aggregate a commitment to data and, once its proof is fully upgraded and verified, connect it to a Bitcoin block. This provides evidence that the committed data existed **no later than** the time represented by that block. It does not reveal the exact creation time, prove who created the data, or establish the truth of its contents.

Bitcoin is useful here as a widely replicated public timestamping substrate: an organization need not ask the AI provider or ASTON service to be the sole authority for the existence-time claim. The auditor can verify the proof independently using the OpenTimestamps client and, where appropriate, its own Bitcoin Core node.

The anchor is optional and asynchronous. A proof may be pending while calendar attestations are collected or upgraded. Pending is not anchored. A missing, invalid, or incomplete receipt must remain visibly unresolved; no system should manufacture a receipt or infer a successful anchor from a request having been submitted.

## 4. Fail-Closed: uncertainty must not become approval

Cryptography is only as useful as the policy that interprets its results. ASTON's Fail-Closed principle is that a protected workflow must not treat an unperformed or inconclusive check as a successful check.

A verifier should distinguish at least:

- **Verified:** all checks required by the applicable policy completed successfully.
- **Failed:** one or more required checks definitively failed.
- **Indeterminate / pending:** a required check could not yet reach a conclusive result.
- **Not applicable:** a check is explicitly outside the policy for this package, with that exception recorded.

For an action requiring a verified proof package, only the first state may satisfy the evidence gate. A signature mismatch, untrusted certificate, digest mismatch, malformed package, invalid timestamp, unavailable mandatory verifier, or policy violation should block the protected action or route it to an explicitly authorized review process. A skipped check must never be silently relabelled as passed.

Fail-Closed does not mean every outage must halt every business process. Each deployment defines which controls are mandatory for which actions, what fallback or human-review path is permitted, and how availability exceptions are recorded. The critical requirement is that an exception is explicit, attributable, and auditable—not an invisible downgrade.

## 5. Independent verification and the current proof of concept

The repository's reference verification guide describes a package containing a manifest, detached signature, certificate, and OpenTimestamps proof. An auditor can validate the certificate trust method, verify the signature over the exact manifest bytes, and run the OpenTimestamps client against the proof.

The current GitHub Actions workflow exercises a test fixture and includes both positive and negative checks: a test signature is accepted, a modified manifest is rejected, and a deliberately simulated invalid OTS receipt is rejected. The workflow's green result demonstrates that these specific automated checks passed. It does **not** demonstrate a completed Bitcoin timestamp, production issuer identity, runtime attestation, or end-to-end production deployment.

That distinction is central to the project. A test fixture is labelled as a fixture; an invalid timestamp is tested as invalid; and a pending external dependency is not represented as a successful proof. The next milestone is to obtain and independently verify an authentic OpenTimestamps proof for the intended final manifest, then document the resulting block evidence and verification environment. Until that happens, the Bitcoin anchor remains a planned verification step, not a completed result.

## 6. Threat model, limitations, and responsible claims

ASTON Trust Fabric is designed to make tampering and evidence gaps more detectable. It does not eliminate trust.

A compromised agent runtime may emit misleading claims before signing them. A compromised signing key can produce valid signatures. A dishonest issuer can sign false statements. A compromised verifier or trust store can accept the wrong key. A digest proves byte equality, not semantic correctness. A Bitcoin timestamp proves an existence-time bound for a commitment, not the quality, provenance, or legality of the underlying content.

Production deployments therefore need key protection and rotation, issuer authorization, certificate and revocation policy, secure verifier distribution, algorithm agility, dependency and workflow hardening, privacy controls, evidence retention, and independent review. They also need clear policies for what is signed: raw artifacts, canonicalized documents, or a precisely specified manifest byte sequence. Verifiers must reject ambiguous encodings and must not silently normalize signed content.

The current public repository is a foundational open specification and reference implementation direction. It is not a certified security product, a formal attestation of model behavior, a W3C Verifiable Credential conformance claim, or a guarantee that an AI system is safe, unbiased, or correct.

## 7. Vision and roadmap

The long-term vision is an ecosystem in which an AI-generated action can carry a portable evidence package that customers, auditors, regulators, and partner systems can verify under their own policies. The same basic model should work across providers and industries: structured declarations, exact-byte integrity, independently governed keys, optional public timestamping, and explicit verification outcomes.

A responsible path forward is incremental:

1. Stabilize the schema and publish test vectors for valid and invalid attestations.
2. Define interoperable signature, manifest, key-discovery, and trust-policy profiles.
3. Add authentic timestamp fixtures and independent verification instructions.
4. Expand negative tests for malformed packages, key mismatch, tampering, algorithm confusion, and fail-open regressions.
5. Invite independent implementations, security review, and documented interoperability testing.
6. Develop deployment profiles for privacy, retention, revocation, and high-assurance workflows.

**ASTON Trust Fabric's proposition is simple:** AI systems should not be asked to serve as the sole witnesses of their own actions. Their claims should be packaged as evidence, bound to exact data, independently verifiable, and denied protected authority when required proof is absent or fails.

---

*This document is a technical vision and draft, not legal advice, a security certification, or a claim that all described capabilities are already implemented. The repository's verification guide and test results define the current implementation evidence.*
