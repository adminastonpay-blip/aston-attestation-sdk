#!/usr/bin/env python3
"""Independent verifier for an ASTON PROOF PACKAGE.

Requires OpenSSL, the official OpenTimestamps CLI (ots), and Python 3.9+.
The verifier fails closed unless the caller supplies either a CA trust store
or an independently authenticated SHA-256 certificate fingerprint.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command: list[str], label: str) -> str:
    print(f"[RUN] {label}")
    try:
        result = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(f"Required executable not found: {command[0]}") from exc
    output = result.stdout.strip()
    if output:
        print(output)
    if result.returncode != 0:
        raise RuntimeError(f"{label} failed (exit {result.returncode})")
    print(f"[PASS] {label}")
    return output


def normalized_fingerprint(value: str) -> str:
    normalized = re.sub(r"[^0-9a-fA-F]", "", value).lower()
    if len(normalized) != 64:
        raise ValueError("Expected a SHA-256 certificate fingerprint (64 hex characters).")
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify certificate trust, detached signature, and OpenTimestamps proof."
    )
    parser.add_argument("package_dir", type=Path, help="Directory containing the four proof-package files")
    trust = parser.add_mutually_exclusive_group(required=True)
    trust.add_argument("--ca-file", type=Path, help="Independently trusted CA root bundle (PEM)")
    trust.add_argument("--cert-sha256", help="Independently authenticated SHA-256 fingerprint of certificate.pem")
    parser.add_argument("--intermediates", type=Path, help="Optional PEM bundle of intermediate certificates")
    parser.add_argument("--skip-ots", action="store_true", help="Skip timestamp verification for signature-only fixtures; never use as a full package verification.")
    parser.add_argument(
        "--bitcoin-node",
        help="Optional Bitcoin Core RPC URL passed to ots; protect credentials and avoid shell history.",
    )
    args = parser.parse_args()

    package = args.package_dir.resolve()
    manifest = package / "manifest.json"
    signature = package / "signature.bin"
    certificate = package / "certificate.pem"
    timestamp = package / "manifest.json.ots"

    required = [manifest, signature, certificate, timestamp]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        print("[FAIL] Missing package file(s): " + ", ".join(missing), file=sys.stderr)
        return 2

    if shutil.which("openssl") is None or (not args.skip_ots and shutil.which("ots") is None):
        needed = "openssl" if shutil.which("openssl") is None else "ots"
        print(f"[FAIL] Required executable '{needed}' is not installed or not on PATH.", file=sys.stderr)
        return 2

    try:
        if args.ca_file:
            ca_file = args.ca_file.resolve()
            if not ca_file.is_file():
                raise RuntimeError(f"CA trust file not found: {ca_file}")
            command = ["openssl", "verify", "-CAfile", str(ca_file)]
            if args.intermediates:
                intermediates = args.intermediates.resolve()
                if not intermediates.is_file():
                    raise RuntimeError(f"Intermediate certificate bundle not found: {intermediates}")
                command += ["-untrusted", str(intermediates)]
            command.append(str(certificate))
            run(command, "Certificate chain validation")
        else:
            expected = normalized_fingerprint(args.cert_sha256)
            output = run(
                ["openssl", "x509", "-in", str(certificate), "-noout", "-fingerprint", "-sha256"],
                "Read certificate SHA-256 fingerprint",
            )
            match = re.search(r"=([0-9A-Fa-f:]+)", output)
            if not match:
                raise RuntimeError("Could not parse certificate fingerprint from OpenSSL output.")
            actual = normalized_fingerprint(match.group(1))
            if actual != expected:
                raise RuntimeError("Certificate fingerprint does not match the independently trusted pin.")
            print("[PASS] Pinned certificate fingerprint matches")

        with tempfile.TemporaryDirectory(prefix="aston-proof-") as temp_dir:
            public_key = Path(temp_dir) / "public-key.pem"
            signature_file = signature
            signature_bytes = signature.read_bytes()
            if signature_bytes.startswith(b"BASE64:"):
                try:
                    decoded = base64.b64decode(signature_bytes.split(b":", 1)[1].strip(), validate=True)
                except Exception as exc:
                    raise RuntimeError("signature.bin contains invalid BASE64-armored signature data.") from exc
                signature_file = Path(temp_dir) / "signature.raw"
                signature_file.write_bytes(decoded)
            with public_key.open("wb") as output:
                result = subprocess.run(
                    ["openssl", "x509", "-in", str(certificate), "-pubkey", "-noout"],
                    check=False,
                    stdout=output,
                    stderr=subprocess.PIPE,
                )
            if result.returncode != 0:
                raise RuntimeError("Could not extract public key from certificate: " + result.stderr.decode(errors="replace"))
            run(
                [
                    "openssl", "dgst", "-sha256", "-verify", str(public_key),
                    "-signature", str(signature_file), str(manifest),
                ],
                "Detached SHA-256 signature verification",
            )

        if not args.skip_ots:
            ots_command = ["ots"]
            if args.bitcoin_node:
                ots_command += ["--bitcoin-node", args.bitcoin_node]
            ots_command += ["verify", str(timestamp)]
            run(ots_command, "OpenTimestamps proof verification")

        digest = hashlib.sha256(manifest.read_bytes()).hexdigest()
        print()
        if args.skip_ots:
            print("[PARTIAL SUCCESS] Certificate trust and detached signature passed; timestamp verification was explicitly skipped.")
        else:
            print("[SUCCESS] All configured proof-package checks passed.")
        print(f"Manifest SHA-256: {digest}")
        print("Interpretation: only the checks actually executed are verified. This does not prove that manifest claims are true or that the agent runtime was uncompromised.")
        print("This does not prove that the manifest's claims are true or that the agent runtime was uncompromised.")
        return 0
    except (RuntimeError, ValueError) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
