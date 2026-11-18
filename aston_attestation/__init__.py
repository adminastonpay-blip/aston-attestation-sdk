# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""ASTON Agent Attestation reference SDK."""
from .artifact_policy import ArtifactApproval, PolicyDecision, evaluate_artifact
from .validation import ValidationError, validate_attestation

__all__ = [
    "ArtifactApproval",
    "PolicyDecision",
    "ValidationError",
    "evaluate_artifact",
    "validate_attestation",
]
