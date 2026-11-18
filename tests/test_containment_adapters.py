# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
import base64
import os
import sqlite3
import tempfile
import unittest

from Cryptodome.PublicKey import ECC
from Cryptodome.Signature import eddsa

from aston_attestation.containment_adapters import (
    Ed25519IssuerKeyring,
    SQLiteReplayGuard,
)


class Ed25519IssuerKeyringTests(unittest.TestCase):
    def setUp(self):
        self.private_key = ECC.generate(curve="Ed25519")
        self.public_pem = self.private_key.public_key().export_key(format="PEM")
        self.keyring = Ed25519IssuerKeyring({"authority-1": self.public_pem})
        self.payload = b"ASTON containment command test vector"
        raw_signature = eddsa.new(self.private_key, "rfc8032").sign(self.payload)
        self.signature = base64.urlsafe_b64encode(raw_signature).rstrip(b"=").decode("ascii")

    def test_verifies_signature_for_exact_issuer(self):
        self.assertTrue(self.keyring.verify(self.payload, self.signature, "authority-1"))

    def test_rejects_unknown_issuer(self):
        self.assertFalse(self.keyring.verify(self.payload, self.signature, "authority-2"))

    def test_rejects_tampered_payload(self):
        self.assertFalse(self.keyring.verify(self.payload + b"!", self.signature, "authority-1"))

    def test_rejects_malformed_signature(self):
        self.assertFalse(self.keyring.verify(self.payload, "not-a-signature", "authority-1"))

    def test_rejects_private_key_material_in_trust_store(self):
        private_pem = self.private_key.export_key(format="PEM")
        with self.assertRaises(ValueError):
            Ed25519IssuerKeyring({"authority-1": private_pem})

    def test_rejects_empty_keyring(self):
        with self.assertRaises(ValueError):
            Ed25519IssuerKeyring({})


class SQLiteReplayGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "replay.sqlite3")
        self.connection = sqlite3.connect(self.db_path, timeout=5)
        self.guard = SQLiteReplayGuard(self.connection)

    def tearDown(self):
        self.connection.close()
        self.temp_dir.cleanup()

    def test_claims_command_once(self):
        self.assertTrue(self.guard.claim("cmd-1", 2000))
        self.assertFalse(self.guard.claim("cmd-1", 2000))

    def test_claim_survives_database_reopen(self):
        self.assertTrue(self.guard.claim("cmd-persistent", 2000))
        self.connection.close()
        reopened = sqlite3.connect(self.db_path, timeout=5)
        try:
            second_guard = SQLiteReplayGuard(reopened)
            self.assertFalse(second_guard.claim("cmd-persistent", 2000))
        finally:
            reopened.close()
        self.connection = sqlite3.connect(self.db_path, timeout=5)
        self.guard = SQLiteReplayGuard(self.connection)

    def test_two_connections_cannot_claim_same_id(self):
        second_connection = sqlite3.connect(self.db_path, timeout=5)
        try:
            second_guard = SQLiteReplayGuard(second_connection)
            self.assertTrue(self.guard.claim("cmd-race", 2000))
            self.assertFalse(second_guard.claim("cmd-race", 2000))
        finally:
            second_connection.close()

    def test_invalid_claim_input_is_rejected(self):
        with self.assertRaises(ValueError):
            self.guard.claim("", 2000)
        with self.assertRaises(ValueError):
            self.guard.claim("cmd-bad-time", True)


if __name__ == "__main__":
    unittest.main()
