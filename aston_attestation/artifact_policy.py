# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, fail-closed artifact authorization primitives.

No network access, vendor-signature verification, or browser enforcement occurs
here. Callers supply exact bytes and independently managed trust inputs.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import re
from typing import FrozenSet, Tuple

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_KEY = Tuple[str, str]


@dataclass(frozen=True)
class ArtifactApproval:
    record_id: str
    artifact_id: str
    issuer_id: str
    key_id: str
    sha256: str
    source_ref: str
    immutable_source: bool
    application: str
    environment: str
    execution_context: str
    approved_at: datetime
    expires_at: datetime
    revoked: bool = False


@dataclass(frozen=True)
class PolicyDecision:
    code: str
    allowed: bool
    actual_sha256: str | None = None

    @property
    def reason(self) -> str:
        return self.code


def _aware(value: object) -> bool:
    return isinstance(value, datetime) and value.tzinfo is not None and value.utcoffset() is not None


def evaluate_artifact(
    artifact_bytes: bytes,
    approval: ArtifactApproval,
    *,
    trusted_signing_keys: FrozenSet[_KEY],
    revoked_signing_keys: FrozenSet[_KEY],
    revoked_artifact_ids: FrozenSet[str],
    now: datetime,
    revocation_issued_at: datetime,
    revocation_fresh_until: datetime,
    application: str,
    environment: str,
    execution_context: str,
) -> PolicyDecision:
    """Evaluate exact bytes against explicit caller-owned policy inputs."""
    if not isinstance(artifact_bytes, bytes) or not isinstance(approval, ArtifactApproval):
        return PolicyDecision("invalid_or_ambiguous_record", False)

    fields = (
        approval.record_id, approval.artifact_id, approval.issuer_id, approval.key_id,
        approval.source_ref, approval.application, approval.environment,
        approval.execution_context, application, environment, execution_context,
    )
    if any(not isinstance(value, str) or not value.strip() for value in fields):
        return PolicyDecision("invalid_or_ambiguous_record", False)

    if (
        not isinstance(approval.immutable_source, bool)
        or not isinstance(approval.revoked, bool)
        or not isinstance(approval.sha256, str)
        or not _SHA256_RE.fullmatch(approval.sha256)
        or not all(_aware(value) for value in (
            now, approval.approved_at, approval.expires_at,
            revocation_issued_at, revocation_fresh_until,
        ))
    ):
        return PolicyDecision("invalid_or_ambiguous_record", False)

    key = (approval.issuer_id, approval.key_id)
    if key in revoked_signing_keys:
        return PolicyDecision("revoked_signing_key", False)
    if approval.revoked or approval.artifact_id in revoked_artifact_ids:
        return PolicyDecision("revoked_artifact", False)
    if key not in trusted_signing_keys:
        return PolicyDecision("untrusted_signing_key", False)

    current = now.astimezone(timezone.utc)
    issued = revocation_issued_at.astimezone(timezone.utc)
    fresh_until = revocation_fresh_until.astimezone(timezone.utc)
    approved = approval.approved_at.astimezone(timezone.utc)
    expires = approval.expires_at.astimezone(timezone.utc)

    if issued > current or fresh_until <= current or issued > fresh_until:
        return PolicyDecision("stale_revocation_state", False)
    if approved > current or expires <= current or approved >= expires:
        return PolicyDecision("expired_approval", False)
    if not approval.immutable_source:
        return PolicyDecision("mutable_or_unpinned_source", False)
    if (
        approval.application != application
        or approval.environment != environment
        or approval.execution_context != execution_context
    ):
        return PolicyDecision("policy_mismatch", False)

    actual = hashlib.sha256(artifact_bytes).hexdigest()
    if actual != approval.sha256:
        return PolicyDecision("digest_mismatch", False, actual)
    return PolicyDecision("authorized", True, actual)
