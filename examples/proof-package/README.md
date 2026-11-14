<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Test-only proof package fixture

All files in this directory are synthetic test fixtures.

- `manifest.json` is a demonstration manifest.
- `signature.bin` contains a Base64-armored RSA/SHA-256 detached signature. The verifier decodes the `BASE64:` prefix before passing the raw signature bytes to OpenSSL. This textual encoding is used because the GitHub Contents API accepts UTF-8 text files.
- `certificate.pem` is a self-signed test certificate. Its SHA-256 fingerprint is pinned in the CI workflow only for this fixture.
- `manifest.json.ots` is deliberately invalid placeholder text. It is **not** an OpenTimestamps proof and must fail OTS verification.

The fixture tests signature verification and fail-closed rejection of a fake timestamp. It does not demonstrate a real Bitcoin timestamp or a production ASTON identity. Never use this certificate, key, or fixture as a production trust anchor.
