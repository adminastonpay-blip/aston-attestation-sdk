# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
import os
import sqlite3
import tempfile
import unittest

from Cryptodome.PublicKey import ECC
from Cryptodome.Signature import eddsa

from aston_attestation.containment_adapters import Ed25519IssuerKeyring
from aston_attestation.revocation import (
    SignedRevocationSnapshot,
    SQLiteSnapshotRollbackGuard,
    canonical_revocation_snapshot_bytes,
    verify_revocation_snapshot,
)


class SignedRevocationSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.private = ECC.generate(curve="Ed25519")
        self.keyring = Ed25519IssuerKeyring({
            "revocation-authority": self.private.public_key().export_key(format="PEM")
        })
        self.temp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.temp.name, "revocations.sqlite3")
        self.connection = sqlite3.connect(self.path, timeout=5)
        self.guard = SQLiteSnapshotRollbackGuard(self.connection)

    def tearDown(self):
        self.connection.close()
        self.temp.cleanup()

    def snapshot(self, **changes):
        values = {
            "snapshot_id": "snapshot-001",
            "sequence": 1,
            "issuer_id": "revocation-authority",
            "issued_at": 1000,
            "fresh_until": 1500,
            "revoked_issuers": ("issuer-old",),
            "revoked_targets": (("identity", "agent-7", "tenant-a"),),
            "signature": "placeholder",
        }
        values.update(changes)
        unsigned = SignedRevocationSnapshot(**values)
        signature = eddsa.new(self.private, "rfc8032").sign(canonical_revocation_snapshot_bytes(unsigned))
        import base64
        values["signature"] = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
        return SignedRevocationSnapshot(**values)

    def verify(self, snapshot, **overrides):
        args = {
            "now": 1100,
            "signature_verifier": self.keyring.verify,
            "issuer_authorizer": lambda issuer: issuer == "revocation-authority",
            "rollback_guard": self.guard,
        }
        args.update(overrides)
        return verify_revocation_snapshot(snapshot, **args)

    def test_accepts_valid_signed_snapshot(self):
        result = self.verify(self.snapshot())
        self.assertEqual(result.sequence, 1)
        self.assertEqual(result.revoked_issuers, ("issuer-old",))

    def test_rejects_tampered_payload(self):
        original = self.snapshot()
        changed = SignedRevocationSnapshot(
            original.snapshot_id, original.sequence, original.issuer_id,
            original.issued_at, original.fresh_until, ("issuer-new",),
            original.revoked_targets, original.signature,
        )
        with self.assertRaisesRegex(ValueError, "invalid_snapshot_signature"):
            self.verify(changed)

    def test_rejects_unknown_or_unauthorized_authority(self):
        with self.assertRaisesRegex(ValueError, "invalid_snapshot_signature"):
            self.verify(self.snapshot(issuer_id="unknown"))
        with self.assertRaisesRegex(ValueError, "snapshot_issuer_unauthorized"):
            self.verify(self.snapshot(), issuer_authorizer=lambda issuer: False)

    def test_rejects_stale_and_future_snapshots(self):
        with self.assertRaisesRegex(ValueError, "snapshot_stale"):
            self.verify(self.snapshot(fresh_until=1099))
        with self.assertRaisesRegex(ValueError, "snapshot_issued_in_future"):
            self.verify(self.snapshot(issued_at=1200, fresh_until=1500))

    def test_rejects_duplicate_and_invalid_scope(self):
        with self.assertRaisesRegex(ValueError, "duplicate_revoked_issuer"):
            self.verify(self.snapshot(revoked_issuers=("issuer-old", "issuer-old")))
        with self.assertRaisesRegex(ValueError, "invalid_platform_scope"):
            self.verify(self.snapshot(revoked_targets=(("platform", "tenant-a", None),)))

    def test_rejects_rollback_and_replay(self):
        self.verify(self.snapshot(sequence=2, snapshot_id="snapshot-002"))
        with self.assertRaisesRegex(ValueError, "snapshot_rollback_or_replay"):
            self.verify(self.snapshot(sequence=1, snapshot_id="snapshot-001"))
        with self.assertRaisesRegex(ValueError, "snapshot_rollback_or_replay"):
            self.verify(self.snapshot(sequence=2, snapshot_id="snapshot-002"))

    def test_rollback_head_survives_reopen(self):
        self.assertTrue(self.guard.accept("authority", 5, "snap-5"))
        self.connection.close()
        reopened = sqlite3.connect(self.path, timeout=5)
        try:
            guard = SQLiteSnapshotRollbackGuard(reopened)
            self.assertFalse(guard.accept("authority", 4, "snap-4"))
            self.assertTrue(guard.accept("authority", 6, "snap-6"))
        finally:
            reopened.close()

    def test_rollback_store_failure_fails_closed(self):
        class Broken:
            def accept(self, issuer, sequence, snapshot_id):
                raise RuntimeError("offline")
        with self.assertRaisesRegex(ValueError, "snapshot_rollback_store_unavailable"):
            self.verify(self.snapshot(), rollback_guard=Broken())


if __name__ == "__main__":
    unittest.main()
