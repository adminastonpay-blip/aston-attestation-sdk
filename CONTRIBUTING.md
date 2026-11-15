<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Contributing

## Scope
This repository currently contains an attestation JSON Schema and specification material. Do not describe a schema change as implementation of a production verifier.

## Before opening a pull request
- Open or reference an issue for nontrivial changes.
- Explain the use case, threat model, trust assumptions and compatibility impact.
- Add or update positive and negative test fixtures for schema/semantic changes.
- Never include credentials, private keys, customer data, real prompts or confidential payloads.
- Update documentation and examples with the same change.
- Preserve SPDX notices and Apache-2.0 licensing unless a reviewed licensing decision says otherwise.

## Review requirements
- CI must pass.
- At least one independent review is required; two are required for cryptographic, trust-policy, release or security-control changes.
- Changes that affect verification semantics require explicit test vectors and compatibility notes.
- Do not weaken a failing security test merely to make CI green.

## Reporting vulnerabilities
Do not open a public issue for a suspected vulnerability. Follow [SECURITY.md](SECURITY.md).

## Developer Certificate of Origin
A DCO or CLA policy has not yet been adopted. Until governance approves one, contributors must submit only work they are legally authorized to contribute. The project should obtain legal review before selecting and enforcing a contribution-rights mechanism.
