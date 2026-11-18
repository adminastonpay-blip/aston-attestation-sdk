# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
import unittest

from aston_attestation.revocation import VerifiedRevocationSnapshot

from aston_attestation.containment import (
    ContainmentAction,
    ContainmentCommand,
    ContainmentTarget,
    RevocationSnapshot,
    canonical_command_bytes,
    evaluate_containment_command,
)


class ReplayStore:
    def __init__(self):
        self.seen = set()

    def claim(self, command_id, expires_at):
        if command_id in self.seen:
            return False
        self.seen.add(command_id)
        return True


def command(**changes):
    values = {
        "command_id": "cmd-001",
        "issuer_id": "authority-1",
        "target_type": ContainmentTarget.IDENTITY,
        "target_id": "agent-17",
        "action": ContainmentAction.SUSPEND,
        "reason": "Confirmed credential compromise",
        "issued_at": 1000,
        "expires_at": 1120,
        "tenant_id": "tenant-a",
        "signature": "test-signature",
    }
    values.update(changes)
    return ContainmentCommand(**values)


def evaluate(cmd=None, **overrides):
    args = {
        "now": 1050,
        "revocations": VerifiedRevocationSnapshot(\n            "snapshot-001", 1, "revocation-authority", 990, 1100, (), ()\n        ),
        "signature_verifier": lambda payload, signature, issuer_id: signature == "test-signature" and issuer_id == "authority-1",
        "issuer_authorizer": lambda issuer, item: issuer == "authority-1",
        "replay_guard": ReplayStore(),
    }
    args.update(overrides)
    return evaluate_containment_command(cmd or command(), **args)


class ContainmentPolicyTests(unittest.TestCase):
    def test_accepts_valid_scoped_command(self):
        self.assertEqual(evaluate().code, "authorized")

    def test_canonical_bytes_are_deterministic_and_exclude_signature(self):
        first = command(signature="one")
        second = command(signature="two")
        self.assertEqual(canonical_command_bytes(first), canonical_command_bytes(second))
        self.assertIn(b"aston-containment-command-v1", canonical_command_bytes(first))

    def test_rejects_invalid_signature(self):
        self.assertEqual(evaluate(signature_verifier=lambda payload, sig, issuer_id: False).code, "invalid_signature")

    def test_signature_verifier_exception_fails_closed(self):
        def broken(payload, signature, issuer_id):
            raise RuntimeError("verifier offline")
        self.assertEqual(evaluate(signature_verifier=broken).code, "signature_verification_error")

    def test_rejects_unauthorized_issuer(self):
        self.assertEqual(evaluate(issuer_authorizer=lambda issuer, item: False).code, "issuer_not_authorized")

    def test_rejects_expired_command(self):
        self.assertEqual(evaluate(command(expires_at=1049)).code, "expired")

    def test_rejects_future_issued_command(self):
        self.assertEqual(evaluate(command(issued_at=1081, expires_at=1120)).code, "issued_in_future")

    def test_rejects_excessive_validity_window(self):
        self.assertEqual(evaluate(command(expires_at=1400)).code, "validity_window_exceeded")

    def test_rejects_legacy_unsigned_revocation_snapshot(self):
        self.assertEqual(
            evaluate(revocations=RevocationSnapshot(990, 1100)).code,
            "revocation_snapshot_unverified",
        )

    def test_rejects_stale_revocation_snapshot(self):
        self.assertEqual(evaluate(revocations=VerifiedRevocationSnapshot(\n            "snapshot-old", 4, "revocation-authority", 900, 1049, (), ()\n        )).code, "revocation_snapshot_stale")

    def test_rejects_revoked_issuer(self):
        snapshot = VerifiedRevocationSnapshot(\n            "snapshot-002", 2, "revocation-authority", 990, 1100, ("authority-1",), ()\n        )
        self.assertEqual(evaluate(revocations=snapshot).code, "issuer_revoked")

    def test_rejects_revoked_exact_target(self):
        snapshot = RevocationSnapshot(
            990, 1100, revoked_targets=(("identity", "agent-17", "tenant-a"),)
        )
        self.assertEqual(evaluate(revocations=snapshot).code, "target_revoked")

    def test_tenant_scope_is_required(self):
        self.assertEqual(evaluate(command(tenant_id=None)).code, "tenant_scope_required")

    def test_platform_scope_requires_wildcard_and_no_tenant(self):
        broad = command(target_type=ContainmentTarget.PLATFORM, target_id="*", tenant_id=None)
        self.assertEqual(evaluate(broad).code, "independent_approval_required")
        malformed = command(target_type=ContainmentTarget.PLATFORM, target_id="agent-17", tenant_id=None)
        self.assertEqual(evaluate(malformed).code, "invalid_platform_scope")

    def test_broad_action_requires_independent_approval(self):
        broad = command(target_type=ContainmentTarget.TENANT, target_id="tenant-a")
        self.assertEqual(evaluate(broad).code, "independent_approval_required")

    def test_broad_action_requires_approval_verifier(self):
        broad = command(target_type=ContainmentTarget.TENANT, target_id="tenant-a")
        self.assertEqual(
            evaluate(broad, approval_token="approval-1").code,
            "approval_verifier_unavailable",
        )

    def test_broad_action_rejects_invalid_approval(self):
        broad = command(target_type=ContainmentTarget.TENANT, target_id="tenant-a")
        self.assertEqual(
            evaluate(
                broad,
                approval_token="approval-1",
                approval_verifier=lambda item, token: False,
            ).code,
            "independent_approval_invalid",
        )

    def test_broad_action_accepts_verified_approval(self):
        broad = command(target_type=ContainmentTarget.TENANT, target_id="tenant-a")
        decision = evaluate(
            broad,
            approval_token="approval-1",
            approval_verifier=lambda item, token: token == "approval-1",
        )
        self.assertEqual(decision.code, "authorized")

    def test_replay_is_rejected(self):
        store = ReplayStore()
        kwargs = {
            "now": 1050,
            "revocations": VerifiedRevocationSnapshot(\n                "snapshot-replay", 5, "revocation-authority", 990, 1100, (), ()\n            ),
            "signature_verifier": lambda payload, signature, issuer_id: True,
            "issuer_authorizer": lambda issuer, item: True,
            "replay_guard": store,
        }
        self.assertEqual(evaluate_containment_command(command(), **kwargs).code, "authorized")
        self.assertEqual(evaluate_containment_command(command(), **kwargs).code, "replay_detected")

    def test_replay_store_failure_fails_closed(self):
        class BrokenStore:
            def claim(self, command_id, expires_at):
                raise RuntimeError("store offline")
        self.assertEqual(evaluate(replay_guard=BrokenStore()).code, "replay_store_unavailable")

    def test_invalid_reason_is_rejected(self):
        self.assertEqual(evaluate(command(reason=" ")).code, "invalid_reason")


if __name__ == "__main__":
    unittest.main()
