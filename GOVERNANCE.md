<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Project Governance

Status: proposed governance model; maintainer names and delegated roles require explicit acceptance.

## Decision principles
- Security, compatibility and evidence take precedence over release speed and marketing claims.
- Changes are proposed through issues or pull requests; direct changes to the default branch should be restricted.
- Security-sensitive changes require independent review by a second authorized maintainer before merge.
- Release, signing and trust-policy changes require documented approval and an evidence record.
- Material security exceptions require a named risk owner, rationale, expiry date and compensating controls.

## Roles
- **Project Lead:** roadmap, scope, prioritization and public project status.
- **Security Maintainer:** vulnerability triage, security review, incident coordination and disclosure.
- **Release Maintainer:** versioning, release checklist, SBOM and provenance evidence.
- **Backup Maintainer:** continuity coverage and independent approval.
These are role definitions, not claims that all roles are currently staffed. Publish named assignments only after consent and access validation.

## Change process
1. Open an issue describing purpose, threat impact and compatibility.
2. Submit a branch and pull request with tests and documentation.
3. Require passing CI and at least one independent review; security-critical changes require two-person review.
4. Record exceptions and unresolved risks.
5. Merge only after approval; preserve review and CI evidence.

## Release authority
A release requires a reviewed tag, release notes, clean CI, SBOM, provenance, provenance verification, artifact digest publication and a rollback/revocation plan. No person should be able to silently replace a published release artifact.

## Conflicts and escalation
Disclose conflicts of interest. Security maintainers may request a release freeze pending investigation. The project lead cannot waive a critical security control without documented risk acceptance and independent review.
