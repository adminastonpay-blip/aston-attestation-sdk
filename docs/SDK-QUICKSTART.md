<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# ASTON Attestation SDK — initial validation API

This change introduces the first reusable Python validation surface for the
ASTON Agent Attestation 1.0.0 schema.

## Status boundary

- Structural validation: implemented in the reference module.
- Automated unit tests: included; CI must pass before calling this tested.
- Signature verification, issuer trust resolution, revocation, digest retrieval,
  transparency verification, runtime attestation, and production certification:
  not implemented by this module.

The validator implements the JSON Schema keywords used by the published ASTON
schema. It is not advertised as a general-purpose JSON Schema engine.

## Quick start

```python
from aston_attestation import ValidationError, validate_attestation

try:
    validate_attestation(attestation_document)
except ValidationError as exc:
    # Reject malformed input; never treat it as trusted.
    print(f"Invalid attestation: {exc}")
else:
    # Structural validity only. Keep the trust state unverified.
    print("Structure valid; attestation remains unverified.")
```

A caller must never promote a document to `verified` merely because schema
validation succeeded.

## Run tests

```bash
python -m unittest discover -s tests -v
```

Structural validity does not prove issuer identity, signature authenticity,
claim truth, runtime integrity, or safety.
