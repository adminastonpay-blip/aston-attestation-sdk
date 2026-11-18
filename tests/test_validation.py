# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0
import unittest
from aston_attestation import ValidationError, validate_attestation

def valid_document():
    return {
        "schema_version": "1.0.0",
        "attestation_id": "att-001",
        "created_at": "2026-11-17T12:00:00Z",
        "agent": {"id": "agent:demo"},
        "issuer": {"id": "org:demo"},
        "execution": {"run_id": "run-001", "started_at": "2026-11-17T11:59:00Z"},
        "verification": {"status": "unverified"},
    }

class AttestationValidationTests(unittest.TestCase):
    def test_accepts_minimal_valid_unverified_attestation(self):
        self.assertIsNone(validate_attestation(valid_document()))
    def test_rejects_missing_required_field(self):
        doc = valid_document(); del doc["issuer"]
        with self.assertRaisesRegex(ValidationError, "issuer"): validate_attestation(doc)
    def test_rejects_unknown_top_level_property(self):
        doc = valid_document(); doc["trusted"] = True
        with self.assertRaisesRegex(ValidationError, "unexpected property"): validate_attestation(doc)
    def test_rejects_unsupported_schema_version(self):
        doc = valid_document(); doc["schema_version"] = "9.9.9"
        with self.assertRaises(ValidationError): validate_attestation(doc)
    def test_rejects_invalid_verification_state(self):
        doc = valid_document(); doc["verification"]["status"] = "trusted"
        with self.assertRaises(ValidationError): validate_attestation(doc)
    def test_rejects_invalid_datetime(self):
        doc = valid_document(); doc["created_at"] = "yesterday"
        with self.assertRaises(ValidationError): validate_attestation(doc)
    def test_rejects_party_without_identifier(self):
        doc = valid_document(); doc["issuer"] = {}
        with self.assertRaises(ValidationError): validate_attestation(doc)
    def test_rejects_boolean_as_string(self):
        doc = valid_document(); doc["attestation_id"] = True
        with self.assertRaises(ValidationError): validate_attestation(doc)

if __name__ == "__main__":
    unittest.main()
