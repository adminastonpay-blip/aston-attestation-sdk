# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed policy primitives for authenticated containment commands.

This module evaluates commands; it does not stop workloads or revoke credentials.
Cryptographic signature verification, issuer authorization, independent approval,
and durable replay storage are injected adapters and MUST be supplied by the caller.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Protocol


class ContainmentTarget(str, Enum):
    IDENTITY = "identity"
    CREDENTIAL = "credential"
    ISSUER_KEY = "issuer_key"
    ARTIFACT = "artifact"
    TENANT = "tenant"
    CAPABILITY = "capability"
    INTEGRATION = "integration"
    POLICY_SNAPSHOT = "policy_snapshot"
    PLATFORM = "platform"


class ContainmentAction(str, Enum):
    SUSPEND = "suspend"
    REVOKE = "revoke"
    QUARANTINE = "quarantine"


@dataclass(frozen=True)
class ContainmentCommand:
    command_id: str
    issuer_id: str
    target_type: ContainmentTarget
    target_id: str
    action: ContainmentAction
    reason: str
    issued_at: int
    expires_at: int
    tenant_id: str | None
    signature: str


@dataclass(frozen=True)
class RevocationSnapshot:
    issued_at: int
    fresh_until: int
    revoked_issuers: tuple[str, ...] = ()
    # Tuples are (target_type, target_id, tenant_id); tenant_id=None is platform scope.
    revoked_targets: tuple[tuple[str, str, str | None], ...] = ()


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    code: str


class ReplayGuard(Protocol):
    """Atomic, durable, shared replay store supplied by the deployment adapter."""

    def claim(self, command_id: str, expires_at: int) -> bool:
        """Atomically record a previously unseen command ID until expiry."""
        ...


SignatureVerifier = Callable[[bytes, str, str], bool]
IssuerAuthorizer = Callable[[str, ContainmentCommand], bool]
ApprovalVerifier = Callable[[ContainmentCommand, str], bool]


_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_MAX_REASON = 512
_BROAD_TARGETS = {ContainmentTarget.TENANT, ContainmentTarget.PLATFORM}


def canonical_command_bytes(command: ContainmentCommand) -> bytes:
    """Return deterministic UTF-8 bytes to be signed/verified by an adapter.

    The schema deliberately uses strings, enums and integer timestamps only.
    This is a versioned ASTON command encoding, not a claim of RFC 8785 support.
    """
    payload = {
        "action": command.action.value,
        "command_id": command.command_id,
        "expires_at": command.expires_at,
        "issued_at": command.issued_at,
        "issuer_id": command.issuer_id,
        "reason": command.reason,
        "target_id": command.target_id,
        "target_type": command.target_type.value,
        "tenant_id": command.tenant_id,
        "version": "aston-containment-command-v1",
    }
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def evaluate_containment_command(
    command: ContainmentCommand,
    *,
    now: int,
    revocations: object,
    signature_verifier: SignatureVerifier,
    issuer_authorizer: IssuerAuthorizer,
    replay_guard: ReplayGuard,
    approval_token: str | None = None,
    approval_verifier: ApprovalVerifier | None = None,
    max_validity_seconds: int = 300,
    clock_skew_seconds: int = 30,
) -> PolicyDecision:
    """Evaluate a signed, scoped command; every missing trust input denies it."""
    if not isinstance(now, int) or isinstance(now, bool):
        return PolicyDecision(False, "invalid_clock")
    if not isinstance(command, ContainmentCommand):
        return PolicyDecision(False, "invalid_command")
    if not isinstance(command.target_type, ContainmentTarget) or not isinstance(
        command.action, ContainmentAction
    ):
        return PolicyDecision(False, "unsupported_command")
    identifiers = (command.command_id, command.issuer_id)
    if not all(isinstance(value, str) and _ID.fullmatch(value) for value in identifiers):
        return PolicyDecision(False, "invalid_identifier")
    if command.target_type is ContainmentTarget.PLATFORM:
        if command.target_id != "*":
            return PolicyDecision(False, "invalid_platform_scope")
    elif not isinstance(command.target_id, str) or not _ID.fullmatch(command.target_id):
        return PolicyDecision(False, "invalid_identifier")
    if not isinstance(command.reason, str) or not command.reason.strip() or len(command.reason) > _MAX_REASON:
        return PolicyDecision(False, "invalid_reason")
    if not isinstance(command.signature, str) or not command.signature.strip():
        return PolicyDecision(False, "missing_signature")
    if command.target_type is ContainmentTarget.PLATFORM:
        if command.target_id != "*" or command.tenant_id is not None:
            return PolicyDecision(False, "invalid_platform_scope")
    elif not isinstance(command.tenant_id, str) or not _ID.fullmatch(command.tenant_id):
        return PolicyDecision(False, "tenant_scope_required")
    if (
        not isinstance(command.issued_at, int)
        or isinstance(command.issued_at, bool)
        or not isinstance(command.expires_at, int)
        or isinstance(command.expires_at, bool)
        or not isinstance(max_validity_seconds, int)
        or max_validity_seconds <= 0
        or not isinstance(clock_skew_seconds, int)
        or clock_skew_seconds < 0
    ):
        return PolicyDecision(False, "invalid_time")
    if command.issued_at > now + clock_skew_seconds:
        return PolicyDecision(False, "issued_in_future")
    if command.expires_at <= now:
        return PolicyDecision(False, "expired")
    if command.expires_at <= command.issued_at or command.expires_at - command.issued_at > max_validity_seconds:
        return PolicyDecision(False, "validity_window_exceeded")

    # Import locally to avoid a module cycle: revocation.py shares the
    # ContainmentTarget enum for snapshot scope validation.
    from .revocation import VerifiedRevocationSnapshot

    if not isinstance(revocations, VerifiedRevocationSnapshot):
        return PolicyDecision(False, "revocation_snapshot_unverified")
    if (
        not isinstance(revocations.issued_at, int)
        or isinstance(revocations.issued_at, bool)
        or not isinstance(revocations.fresh_until, int)
        or isinstance(revocations.fresh_until, bool)
        or revocations.issued_at > now + clock_skew_seconds
        or revocations.fresh_until <= now
        or revocations.fresh_until <= revocations.issued_at
    ):
        return PolicyDecision(False, "revocation_snapshot_stale")
    if command.issuer_id in revocations.revoked_issuers:
        return PolicyDecision(False, "issuer_revoked")
    target_key = (
        command.target_type.value,
        command.target_id,
        command.tenant_id,
    )
    if target_key in revocations.revoked_targets:
        return PolicyDecision(False, "target_revoked")

    try:
        if not signature_verifier(canonical_command_bytes(command), command.signature, command.issuer_id):
            return PolicyDecision(False, "invalid_signature")
    except Exception:
        return PolicyDecision(False, "signature_verification_error")

    try:
        if not issuer_authorizer(command.issuer_id, command):
            return PolicyDecision(False, "issuer_not_authorized")
    except Exception:
        return PolicyDecision(False, "issuer_authorization_error")

    if command.target_type in _BROAD_TARGETS:
        if not isinstance(approval_token, str) or not approval_token.strip():
            return PolicyDecision(False, "independent_approval_required")
        if approval_verifier is None:
            return PolicyDecision(False, "approval_verifier_unavailable")
        try:
            if not approval_verifier(command, approval_token):
                return PolicyDecision(False, "independent_approval_invalid")
        except Exception:
            return PolicyDecision(False, "approval_verification_error")

    try:
        if not replay_guard.claim(command.command_id, command.expires_at):
            return PolicyDecision(False, "replay_detected")
    except Exception:
        return PolicyDecision(False, "replay_store_unavailable")

    return PolicyDecision(True, "authorized")
