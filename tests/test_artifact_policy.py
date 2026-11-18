# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
import hashlib
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone

from aston_attestation.artifact_policy import ArtifactApproval, evaluate_artifact

NOW = datetime(2026, 11, 18, 12, 0, tzinfo=timezone.utc)
PAYLOAD = b"console.log('approved');"
KEY = ("vendor:example", "release-key-1")


def approval_for(payload=PAYLOAD):
    return ArtifactApproval(
        record_id="approval-001",
        artifact_id="script:checkout-v1",
        issuer_id=KEY[0],
        key_id=KEY[1],
        sha256=hashlib.sha256(payload).hexdigest(),
        source_ref="release:checkout/1.0.0",
        immutable_source=True,
        application="shop:storefront",
        environment="production",
        execution_context="checkout",
        approved_at=NOW - timedelta(hours=1),
        expires_at=NOW + timedelta(hours=1),
    )


def arguments(**overrides):
    values = dict(
        trusted_signing_keys=frozenset({KEY}),
        revoked_signing_keys=frozenset(),
        revoked_artifact_ids=frozenset(),
        now=NOW,
        revocation_issued_at=NOW - timedelta(minutes=5),
        revocation_fresh_until=NOW + timedelta(minutes=5),
        application="shop:storefront",
        environment="production",
        execution_context="checkout",
    )
    values.update(overrides)
    return values


class ArtifactPolicyTests(unittest.TestCase):
    def test_authorizes_exact_approved_bytes(self):
        result = evaluate_artifact(PAYLOAD, approval_for(), **arguments())
        self.assertEqual(result.code, "authorized")
        self.assertTrue(result.allowed)

    def test_rejects_changed_bytes_at_same_reference(self):
        result = evaluate_artifact(b"console.log('tampered');", approval_for(), **arguments())
        self.assertEqual(result.code, "digest_mismatch")
        self.assertFalse(result.allowed)

    def test_rejects_untrusted_signing_key(self):
        result = evaluate_artifact(PAYLOAD, approval_for(), **arguments(trusted_signing_keys=frozenset()))
        self.assertEqual(result.code, "untrusted_signing_key")

    def test_revoked_signing_key_takes_precedence(self):
        result = evaluate_artifact(PAYLOAD, approval_for(), **arguments(revoked_signing_keys=frozenset({KEY})))
        self.assertEqual(result.code, "revoked_signing_key")

    def test_rejects_revoked_artifact(self):
        result = evaluate_artifact(PAYLOAD, approval_for(), **arguments(revoked_artifact_ids=frozenset({"script:checkout-v1"})))
        self.assertEqual(result.code, "revoked_artifact")

    def test_rejects_stale_revocation_snapshot(self):
        result = evaluate_artifact(PAYLOAD, approval_for(), **arguments(revocation_fresh_until=NOW))
        self.assertEqual(result.code, "stale_revocation_state")

    def test_rejects_future_revocation_snapshot(self):
        result = evaluate_artifact(PAYLOAD, approval_for(), **arguments(revocation_issued_at=NOW + timedelta(seconds=1)))
        self.assertEqual(result.code, "stale_revocation_state")

    def test_rejects_expired_approval(self):
        item = replace(approval_for(), expires_at=NOW)
        result = evaluate_artifact(PAYLOAD, item, **arguments())
        self.assertEqual(result.code, "expired_approval")

    def test_rejects_mutable_source(self):
        item = replace(approval_for(), immutable_source=False)
        result = evaluate_artifact(PAYLOAD, item, **arguments())
        self.assertEqual(result.code, "mutable_or_unpinned_source")

    def test_rejects_wrong_execution_context(self):
        result = evaluate_artifact(PAYLOAD, approval_for(), **arguments(execution_context="homepage"))
        self.assertEqual(result.code, "policy_mismatch")

    def test_rejects_malformed_digest(self):
        item = replace(approval_for(), sha256="not-a-digest")
        result = evaluate_artifact(PAYLOAD, item, **arguments())
        self.assertEqual(result.code, "invalid_or_ambiguous_record")

    def test_rejects_naive_clock(self):
        result = evaluate_artifact(PAYLOAD, approval_for(), **arguments(now=datetime(2026, 11, 18, 12, 0)))
        self.assertEqual(result.code, "invalid_or_ambiguous_record")

    def test_rejects_non_bytes_input(self):
        result = evaluate_artifact("not bytes", approval_for(), **arguments())
        self.assertEqual(result.code, "invalid_or_ambiguous_record")


if __name__ == "__main__":
    unittest.main()
