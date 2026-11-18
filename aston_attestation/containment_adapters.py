# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""Concrete Ed25519 verification and SQLite replay adapters for ASTON commands."""
from __future__ import annotations

import base64
import binascii
import sqlite3
import threading
from collections.abc import Mapping

from Cryptodome.PublicKey import ECC
from Cryptodome.Signature import eddsa


class Ed25519IssuerKeyring:
    """Explicit issuer-to-public-key map; no key discovery or trust-on-first-use.

    Keys are PEM-encoded Ed25519 public keys. Callers must obtain and rotate
    these keys through an independently authenticated trust-management process.
    """

    def __init__(self, issuer_public_keys_pem: Mapping[str, bytes | str]):
        if not issuer_public_keys_pem:
            raise ValueError("issuer keyring must not be empty")
        self._keys = {}
        for issuer_id, encoded_key in issuer_public_keys_pem.items():
            if not isinstance(issuer_id, str) or not issuer_id:
                raise ValueError("issuer IDs must be non-empty strings")
            if not isinstance(encoded_key, (bytes, str)):
                raise TypeError("public keys must be PEM bytes or strings")
            key = ECC.import_key(encoded_key)
            if key.curve != "Ed25519" or key.has_private():
                raise ValueError("issuer key must be a public Ed25519 key")
            self._keys[issuer_id] = key

    def verify(self, payload: bytes, signature: str, issuer_id: str) -> bool:
        """Verify canonical command bytes against the exact issuer's pinned key."""
        key = self._keys.get(issuer_id)
        if key is None or not isinstance(payload, bytes) or not isinstance(signature, str):
            return False
        try:
            encoded = signature.encode("ascii")
            raw = base64.b64decode(
                encoded + b"=" * (-len(encoded) % 4),
                altchars=b"-_",
                validate=True,
            )
            if len(raw) != 64:
                return False
            canonical = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
            if canonical != signature:
                return False
            eddsa.new(key, "rfc8032").verify(payload, raw)
            return True
        except (ValueError, TypeError, UnicodeError, binascii.Error):
            return False


class SQLiteReplayGuard:
    """Atomic replay claims using a caller-owned, persistent SQLite database.

    Use a file on durable storage in deployments. ':memory:' and ephemeral
    container filesystems are for tests only and do not provide durable replay
    protection across process restarts or hosts.
    """

    _TABLE = "aston_containment_replay"

    def __init__(self, connection: sqlite3.Connection):
        if not isinstance(connection, sqlite3.Connection):
            raise TypeError("a sqlite3.Connection is required")
        self._connection = connection
        self._lock = threading.RLock()
        self._connection.execute(
            f"CREATE TABLE IF NOT EXISTS {self._TABLE} ("
            "command_id TEXT PRIMARY KEY NOT NULL, "
            "expires_at INTEGER NOT NULL, "
            "claimed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        self._connection.commit()

    def claim(self, command_id: str, expires_at: int) -> bool:
        """Atomically claim an ID once; claims are retained to prevent reuse."""
        if not isinstance(command_id, str) or not command_id:
            raise ValueError("command_id must be non-empty")
        if not isinstance(expires_at, int) or isinstance(expires_at, bool):
            raise ValueError("expires_at must be an integer")
        with self._lock:
            try:
                self._connection.execute("BEGIN IMMEDIATE")
                cursor = self._connection.execute(
                    f"INSERT OR IGNORE INTO {self._TABLE} (command_id, expires_at) VALUES (?, ?)",
                    (command_id, expires_at),
                )
                claimed = cursor.rowcount == 1
                self._connection.commit()
                return claimed
            except Exception:
                self._connection.rollback()
                raise
