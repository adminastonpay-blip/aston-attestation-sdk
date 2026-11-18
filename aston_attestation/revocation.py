# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""Authenticated, freshness-bounded revocation snapshots with rollback protection."""
from __future__ import annotations

import json
import re
import sqlite3
import threading
from dataclasses import dataclass, field as dataclass_field
from typing import Callable, Protocol

from .containment import ContainmentTarget

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_TARGET_TYPES = {item.value for item in ContainmentTarget}


@dataclass(frozen=True)
class SignedRevocationSnapshot:
    snapshot_id: str
    sequence: int
    issuer_id: str
    issued_at: int
    fresh_until: int
    revoked_issuers: tuple[str, ...]
    # Entries are (target_type, target_id, tenant_id).
    revoked_targets: tuple[tuple[str, str, str | None], ...]
    signature: str


@dataclass(frozen=True)
class VerifiedRevocationSnapshot:
    snapshot_id: str
    sequence: int
    issuer_id: str
    issued_at: int
    fresh_until: int
    revoked_issuers: tuple[str, ...]
    revoked_targets: tuple[tuple[str, str, str | None], ...]
    _verification_token: object = dataclass_field(default=None, repr=False, compare=False)


_VERIFICATION_TOKEN = object()


def is_verified_revocation_snapshot(value: object) -> bool:
    return (
        isinstance(value, VerifiedRevocationSnapshot)
        and value._verification_token is _VERIFICATION_TOKEN
    )


class SnapshotRollbackGuard(Protocol):
    def accept(self, issuer_id: str, sequence: int, snapshot_id: str) -> bool:
        """Atomically accept only a sequence newer than the issuer's last one."""
        ...


SnapshotSignatureVerifier = Callable[[bytes, str, str], bool]
SnapshotIssuerAuthorizer = Callable[[str], bool]


def canonical_revocation_snapshot_bytes(snapshot: SignedRevocationSnapshot) -> bytes:
    """Canonical versioned bytes. Arrays are sorted to remove caller ordering."""
    payload = {
        "fresh_until": snapshot.fresh_until,
        "issued_at": snapshot.issued_at,
        "issuer_id": snapshot.issuer_id,
        "revoked_issuers": sorted(snapshot.revoked_issuers),
        "revoked_targets": sorted(
            [list(item) for item in snapshot.revoked_targets],
            key=lambda item: (item[0], item[1], item[2] or ""),
        ),
        "sequence": snapshot.sequence,
        "snapshot_id": snapshot.snapshot_id,
        "version": "aston-revocation-snapshot-v1",
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_revocation_snapshot(
    snapshot: SignedRevocationSnapshot,
    *,
    now: int,
    signature_verifier: SnapshotSignatureVerifier,
    issuer_authorizer: SnapshotIssuerAuthorizer,
    rollback_guard: SnapshotRollbackGuard,
    max_validity_seconds: int = 3600,
    clock_skew_seconds: int = 30,
) -> VerifiedRevocationSnapshot:
    """Verify authenticity, authority, freshness and monotonic sequence; fail closed."""
    if not isinstance(snapshot, SignedRevocationSnapshot):
        raise ValueError("invalid_snapshot")
    if not isinstance(now, int) or isinstance(now, bool):
        raise ValueError("invalid_clock")
    if not isinstance(max_validity_seconds, int) or isinstance(max_validity_seconds, bool) or max_validity_seconds <= 0:
        raise ValueError("invalid_max_validity")
    if not isinstance(clock_skew_seconds, int) or isinstance(clock_skew_seconds, bool) or clock_skew_seconds < 0:
        raise ValueError("invalid_clock_skew")
    if not all(isinstance(value, str) and _ID.fullmatch(value) for value in (snapshot.snapshot_id, snapshot.issuer_id)):
        raise ValueError("invalid_identifier")
    if not isinstance(snapshot.sequence, int) or isinstance(snapshot.sequence, bool) or snapshot.sequence < 1:
        raise ValueError("invalid_sequence")
    if (
        not isinstance(snapshot.issued_at, int) or isinstance(snapshot.issued_at, bool)
        or not isinstance(snapshot.fresh_until, int) or isinstance(snapshot.fresh_until, bool)
    ):
        raise ValueError("invalid_time")
    if snapshot.issued_at > now + clock_skew_seconds:
        raise ValueError("snapshot_issued_in_future")
    if snapshot.fresh_until <= now:
        raise ValueError("snapshot_stale")
    if snapshot.fresh_until <= snapshot.issued_at or snapshot.fresh_until - snapshot.issued_at > max_validity_seconds:
        raise ValueError("snapshot_validity_exceeded")
    if not isinstance(snapshot.revoked_issuers, tuple) or not all(
        isinstance(item, str) and _ID.fullmatch(item) for item in snapshot.revoked_issuers
    ):
        raise ValueError("invalid_revoked_issuer")
    if len(set(snapshot.revoked_issuers)) != len(snapshot.revoked_issuers):
        raise ValueError("duplicate_revoked_issuer")
    if not isinstance(snapshot.revoked_targets, tuple):
        raise ValueError("invalid_revoked_targets")
    seen_targets = set()
    for item in snapshot.revoked_targets:
        if not isinstance(item, tuple) or len(item) != 3:
            raise ValueError("invalid_revoked_target")
        target_type, target_id, tenant_id = item
        if not isinstance(target_type, str) or target_type not in _TARGET_TYPES:
            raise ValueError("invalid_target_type")
        if target_type == ContainmentTarget.PLATFORM.value:
            if target_id != "*" or tenant_id is not None:
                raise ValueError("invalid_platform_scope")
        elif not isinstance(target_id, str) or not _ID.fullmatch(target_id):
            raise ValueError("invalid_target_id")
        if target_type != ContainmentTarget.PLATFORM.value and (
            not isinstance(tenant_id, str) or not _ID.fullmatch(tenant_id)
        ):
            raise ValueError("invalid_tenant_scope")
        if item in seen_targets:
            raise ValueError("duplicate_revoked_target")
        seen_targets.add(item)
    if not isinstance(snapshot.signature, str) or not snapshot.signature:
        raise ValueError("missing_signature")
    try:
        if not signature_verifier(
            canonical_revocation_snapshot_bytes(snapshot), snapshot.signature, snapshot.issuer_id
        ):
            raise ValueError("invalid_snapshot_signature")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("snapshot_signature_verification_error") from exc
    try:
        if not issuer_authorizer(snapshot.issuer_id):
            raise ValueError("snapshot_issuer_unauthorized")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("snapshot_issuer_authorization_error") from exc
    try:
        if not rollback_guard.accept(snapshot.issuer_id, snapshot.sequence, snapshot.snapshot_id):
            raise ValueError("snapshot_rollback_or_replay")
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("snapshot_rollback_store_unavailable") from exc
    verified = VerifiedRevocationSnapshot(
        snapshot.snapshot_id, snapshot.sequence, snapshot.issuer_id,
        snapshot.issued_at, snapshot.fresh_until,
        tuple(sorted(snapshot.revoked_issuers)),
        tuple(sorted(snapshot.revoked_targets, key=lambda item: (item[0], item[1], item[2] or ""))),
    )
    object.__setattr__(verified, "_verification_token", _VERIFICATION_TOKEN)
    return verified


class SQLiteSnapshotRollbackGuard:
    """Persistent per-issuer monotonic sequence guard; caller owns the connection."""

    _TABLE = "aston_revocation_snapshot_heads"

    def __init__(self, connection: sqlite3.Connection):
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError("a sqlite3.Connection is required")
        self._connection = connection
        self._lock = threading.RLock()
        self._connection.execute(
            f"CREATE TABLE IF NOT EXISTS {self._TABLE} ("
            "issuer_id TEXT PRIMARY KEY NOT NULL, "
            "sequence INTEGER NOT NULL, snapshot_id TEXT NOT NULL)"
        )
        self._connection.commit()

    def accept(self, issuer_id: str, sequence: int, snapshot_id: str) -> bool:
        if not isinstance(issuer_id, str) or not issuer_id or not isinstance(snapshot_id, str) or not snapshot_id:
            raise ValueError("issuer_id and snapshot_id must be non-empty strings")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            raise ValueError("sequence must be a positive integer")
        with self._lock:
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                cursor = self._connection.execute(
                    "INSERT INTO aston_revocation_snapshot_heads "
                    "(issuer_id, sequence, snapshot_id) VALUES (?, ?, ?) "
                    "ON CONFLICT(issuer_id) DO UPDATE SET "
                    "sequence=excluded.sequence, snapshot_id=excluded.snapshot_id "
                    "WHERE excluded.sequence > aston_revocation_snapshot_heads.sequence",
                    (issuer_id, sequence, snapshot_id),
                )
                accepted = cursor.rowcount == 1
                self._connection.commit()
                return accepted
            except Exception:
                self._connection.rollback()
                raise
