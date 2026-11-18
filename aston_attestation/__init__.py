# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
"""ASTON Agent Attestation reference SDK."""
from .validation import ValidationError, validate_attestation
__all__ = ["ValidationError", "validate_attestation"]
