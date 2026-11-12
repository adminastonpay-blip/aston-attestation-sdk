# ASTON PROOF PACKAGE — Independent Verification Guide

This guide describes how an independent auditor can verify the integrity of a proof package without calling ASTON OS. It uses OpenSSL and the official OpenTimestamps client.

## 1. Package layout

A minimal package has these files:

```text
proof-package/
├── manifest.json
├── signature.bin
├── certificate.pem
└── manifest.json.ots
```

- `manifest.json`: exact byte sequence whose integrity is protected.
- `signature.bin`: detached signature over the exact bytes of `manifest.json`.
- `certificate.pem`: X.509 certificate containing the public key used to verify the signature.
- `manifest.json.ots`: OpenTimestamps proof for the exact `manifest.json` file.

The issuer should distribute the package together with a trust method for the certificate (for example, a certificate chain rooted in a CA the auditor already trusts, or a certificate SHA-256 fingerprint obtained through an independently authenticated channel).

**Do not reserialize, pretty-print, normalize line endings, or otherwise edit `manifest.json` after signing or timestamping it.** Both checks operate on exact file bytes.

## 2. Requirements

- OpenSSL 3.x (or a compatible OpenSSL release supporting the commands below).
- Python 3.9+ for the reference verifier.
- The official OpenTimestamps client: `python3 -m pip install opentimestamps-client`.
- For fully local Bitcoin-chain verification, a synchronized Bitcoin Core node and its RPC access. Protect RPC credentials; do not put them in public logs or shared command history.

Check installations:

```bash
openssl version
python3 --version
ots --help
```

## 3. Establish trust in the issuer certificate

A mathematically valid signature proves control of the private key corresponding to the public key used. It does **not**, by itself, prove that the key belongs to ASTON or to any particular legal entity.

Choose one trust procedure and document it in the audit record.

### Option A — Validate a certificate chain against an independently trusted CA

Obtain the trust root from the auditor's trusted source, not merely from the same untrusted package. If required, obtain intermediate certificates independently.

```bash
openssl verify -CAfile trust-roots.pem certificate.pem
```

If intermediates are needed:

```bash
openssl verify -CAfile trust-roots.pem -untrusted intermediates.pem certificate.pem
```

A successful chain check means the certificate chains to the supplied trust store under OpenSSL's validation rules. The auditor must still decide whether that CA and certificate identity are authorized for the asserted ASTON role. Production policies should also define certificate purpose, name/identity matching, validity period, revocation checking, and key-usage requirements.

### Option B — Pin an independently authenticated certificate fingerprint

If no CA chain is used, obtain the expected SHA-256 certificate fingerprint from a channel independent of the proof package (for example, a previously published and authenticated key directory).

Display the certificate fingerprint:

```bash
openssl x509 -in certificate.pem -noout -fingerprint -sha256
```

Compare it character-for-character with the independently trusted fingerprint. A fingerprint copied from the same untrusted package does not establish identity.

## 4. Verify the detached signature

Extract the public key:

```bash
openssl x509 -in certificate.pem -pubkey -noout > pubkey.pem
```

Verify the signature:

```bash
openssl dgst -sha256 -verify pubkey.pem -signature signature.bin manifest.json
```

Expected success output:

```text
Verified OK
```

This confirms that the signature verifies over the exact bytes of `manifest.json` using the public key extracted from the supplied certificate. It does not establish issuer identity unless Step 3 succeeded, and it does not establish that the manifest's claims are true.

**Algorithm profile:** this example is specifically RSA/ECDSA-compatible OpenSSL `dgst -sha256` verification with the signature encoding expected by the selected key type. It is not a universal signature format. The producer and verifier must agree on the signature algorithm, encoding, signed byte sequence, and any canonicalization rules. Do not silently substitute algorithms.

## 5. Verify the OpenTimestamps proof

Run:

```bash
ots verify manifest.json.ots
```

The OpenTimestamps client infers the target file name by removing the `.ots` suffix, so `manifest.json` must be present in the same directory.

A successful, fully confirmed proof reports a Bitcoin block attesting the file's existence no later than the time represented by that block. If the proof is still pending, the client may report pending calendar attestations; that is **not** a completed Bitcoin timestamp verification.

For verification against a locally operated Bitcoin Core node, configure the official client to use that node:

```bash
ots --bitcoin-node http://USER:PASS@127.0.0.1:8332/ verify manifest.json.ots
```

Use secure local credential handling in real deployments; do not paste RPC credentials into tickets, public logs, or shell history. The local node must have the relevant block data available. OpenTimestamps' proof format and client determine which attestations can be verified locally; a pending proof may require a later upgrade or additional calendar data before it contains a Bitcoin attestation.

## 6. Reference automation

The repository includes `scripts/verify_proof_package.py`. It runs the same checks in order:

1. certificate trust (CA trust store or independently pinned SHA-256 fingerprint);
2. detached OpenSSL signature verification;
3. OpenTimestamps proof verification.

Example using a CA trust store:

```bash
python3 scripts/verify_proof_package.py ./proof-package --ca-file ./trust-roots.pem
```

Example using a pinned certificate fingerprint:

```bash
python3 scripts/verify_proof_package.py ./proof-package \
  --cert-sha256 'AA:BB:CC:...'
```

The script exits non-zero if a required check fails. It does not contact ASTON OS. The OpenTimestamps client may contact calendar servers when a proof is incomplete unless the verifier uses a local Bitcoin node and a sufficiently complete proof.

## 7. What the package proves — and what it does not

| Check | What a successful result supports | What it does not prove |
|---|---|---|
| Certificate trust | The certificate is trusted under the auditor's selected trust policy | That every claim made by the issuer is true |
| Signature | The exact manifest bytes verify under the certificate's public key | That the signer is authorized unless the trust policy says so |
| OpenTimestamps | The committed file existed no later than the attested Bitcoin block time | Who created it, whether its contents are true, or when it was first created |
| JSON Schema | The document has the required structural shape | Cryptographic authenticity or semantic correctness |

A Bitcoin timestamp establishes an upper bound on existence time (the file existed **no later than** the attested block time), not an exact creation time. A signature proves key control over signed bytes, not runtime integrity, model identity, correctness, safety, or truthfulness.

## 8. W3C Verifiable Credentials relationship

The ASTON Agent Attestation JSON Schema is **conceptually aligned** with the issuer / subject / verifier model used by W3C Verifiable Credentials. It is not, by itself, a conforming W3C Verifiable Credential Data Model 2.0 document. W3C VC conformance requires the VC data model's required structure and a recognized securing mechanism. A future VC profile or mapping must specify those details and pass independent conformance tests.

Reference: [W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model-2.0/).

## 9. Audit record

For reproducibility, record at least:

- package file names and SHA-256 digests;
- OpenSSL and OpenTimestamps client versions;
- certificate identity, fingerprint, chain result, and trust source;
- signature algorithm and verification result;
- OpenTimestamps result, Bitcoin block height/hash/time when available;
- whether a local Bitcoin node or remote calendar data was used;
- verifier identity, date, and verification policy version.

Never record private keys, API tokens, passwords, private prompts, or raw sensitive agent inputs in the proof package.

## 10. Security boundary

This guide is a reference procedure, not a certification. Auditors remain responsible for their trust roots, issuer authorization policy, revocation policy, node integrity, software supply chain, and interpretation of evidence. A package that passes these checks should be described as **cryptographically verified under the stated policy**, not as universally trusted or factually correct.
