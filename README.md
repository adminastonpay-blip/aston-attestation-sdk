<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ASTON Agent Attestation

[![REUSE status](https://api.reuse.software/badge/github.com/adminastonpay-blip/aston-attestation-sdk)](https://api.reuse.software/info/github.com/adminastonpay-blip/aston-attestation-sdk)

[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/adminastonpay-blip/aston-attestation-sdk/badge)](https://scorecard.dev/viewer/?uri=github.com/adminastonpay-blip/aston-attestation-sdk)
**An open, implementation-neutral format for AI agent traceability and attestation.**

Repository: [adminastonpay-blip/aston-attestation-sdk](https://github.com/adminastonpay-blip/aston-attestation-sdk)  
Schema: [agent-attestation.schema.json](./agent-attestation.schema.json)  
License: Apache-2.0

## Purpose

ASTON Agent Attestation defines a portable, machine-readable structure for recording what an AI agent claims about its identity, execution context, artifacts, provenance, and supporting evidence.

It is designed as an **open standard that independent third parties can implement** in their own agent runtimes, platforms, audit pipelines, and verification services. It is not tied to ASTON infrastructure or any particular model provider.

## What it records

The JSON Schema describes fields for:

- **Agent and issuer identity** — identifiers and declared versions for the agent and the party issuing an attestation.
- **Execution context** — run identifiers, timestamps, and declared environment information.
- **Integrity references** — algorithm-labelled digests for inputs, outputs, and artifacts. Raw prompts, credentials, and private payloads should not be placed in attestations.
- **Provenance** — source references and links to preceding attestations.
- **Claims and evidence** — assertions and references to material that may support them.
- **Signatures and verification** — signature metadata, key references, and an explicit verification state.
- **Transparency and anchoring references** — optional external log or timestamp references.

The schema is intentionally descriptive. Implementations can adopt the fields relevant to their threat model and deployment.

## Important security distinction

**A syntactically valid attestation is not proof that its claims are true.**

The schema validates document structure and data constraints only. It does not:
- generate or verify cryptographic signatures;
- prove that a key belongs to the named issuer;
- establish that a model actually ran as declared;
- validate timestamps, transparency logs, or external anchors;
- guarantee the integrity of a runtime, host, model, or supply chain.

A verifier must independently validate signatures, key trust, digest values, timestamps, evidence availability, revocation, and any external anchoring mechanism. Treat unsigned or unchecked statements as claims, not verified facts. A `verified` status must only be emitted by a verifier after its defined checks succeed.

## Interoperability principles

1. **Portable JSON:** use standard JSON and JSON Schema Draft 2020-12.
2. **Algorithm agility:** identify digest and signature algorithms explicitly; do not infer them from digest length.
3. **Data minimization:** reference sensitive inputs and outputs by digest or protected URI rather than embedding them.
4. **Explicit uncertainty:** distinguish `unverified`, `verified`, `failed`, and `not_applicable`.
5. **Extensibility:** use namespaced extension fields for implementation-specific data.
6. **No vendor lock-in:** independent implementations should be able to produce and consume conforming documents.

## Quick start

A producer creates a JSON document conforming to `agent-attestation.schema.json`, populates the claims and evidence it can substantiate, and records verification as `unverified` until a separate verifier has completed its checks.

A consumer should:
1. validate the JSON document against the published schema;
2. reject malformed or unsupported critical fields;
3. resolve the issuer and key reference using its own trust policy;
4. verify signatures and all referenced digests;
5. independently evaluate timestamps, evidence, provenance, and transparency references;
6. record the verifier identity, policy, and result in its own audit trail.

## Versioning and compatibility

The initial schema identifies itself as `1.0.0`. The schema URI and `schema_version` field are versioned independently of any implementation SDK. Breaking changes should use a new major schema version. Producers and consumers should preserve unknown extension namespaces where safe.

This repository currently publishes the foundational schema and specification overview. It does not yet claim a certified SDK, production verifier, conformance suite, or third-party interoperability certification.

## Contributing

Issues and pull requests are welcome. Please include:
- the interoperability problem being addressed;
- example documents (with secrets and personal data removed);
- security and privacy implications;
- compatibility impact on existing producers and consumers.

Security vulnerabilities should be reported privately to the repository maintainers rather than disclosed in a public issue. Do not submit credentials, private prompts, personal data, or production secrets.

## License

This project is licensed under the [Apache License, Version 2.0](./LICENSE).
