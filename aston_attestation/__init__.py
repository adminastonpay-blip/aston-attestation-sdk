# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""ASTON Agent Attestation reference SDK."""
from .containment import (
    ContainmentAction,
    ContainmentCommand,
    ContainmentTarget,
    PolicyDecision,
    RevocationSnapshot,
    canonical_command_bytes,
    evaluate_containment_command,
)
from .containment_adapters import Ed25519IssuerKeyring, SQLiteReplayGuard
from .revocation import (
    SignedRevocationSnapshot,
    SQLiteSnapshotRollbackGuard,
    VerifiedRevocationSnapshot,
    canonical_revocation_snapshot_bytes,
    verify_revocation_snapshot,
)
from .validation import ValidationError, validate_attestation

__all__ = [
    "ContainmentAction",
    "ContainmentCommand",
    "ContainmentTarget",
    "Ed25519IssuerKeyring",
    "PolicyDecision",
    "RevocationSnapshot",
    "SQLiteReplayGuard",
    "SignedRevocationSnapshot",
    "SQLiteSnapshotRollbackGuard",
    "VerifiedRevocationSnapshot",
    "ValidationError",
    "canonical_command_bytes",
    "evaluate_containment_command",
    "validate_attestation",
    "canonical_revocation_snapshot_bytes",
    "verify_revocation_snapshot",
]
