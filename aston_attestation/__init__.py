# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""ASTON Agent Attestation reference SDK."""
from .artifact_policy import ArtifactApproval, evaluate_artifact
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
    "ArtifactApproval",
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
    "canonical_revocation_snapshot_bytes",
    "evaluate_artifact",
    "evaluate_containment_command",
    "validate_attestation",
    "verify_revocation_snapshot",
]
