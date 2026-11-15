<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Business Continuity and Disaster Recovery

Status: proposed plan; recovery objectives are targets to validate, not measured guarantees.

## Critical capabilities
- Repository and source history.
- Release artifacts, SBOMs, provenance and verification records.
- Maintainer access and private vulnerability-report handling.
- Trust roots, key metadata, revocation and policy configuration for future verifier deployments.
- Documentation, issue tracker and customer communication channels.

## Failure scenarios
| Scenario | Immediate response | Recovery path |
|---|---|---|
| Primary maintainer unavailable | Activate named backup; freeze nonessential changes | Restore delegated repo/release authority; verify legal and access prerequisites |
| GitHub account/org compromise | Suspend releases; revoke sessions/tokens; contact GitHub | Restore from verified source mirror; rotate credentials; review audit logs |
| Signing key suspected compromised | Stop trust in affected key; publish revocation | Rotate key under approved ceremony; re-issue only after review |
| Malicious or broken release | Quarantine release; publish advisory | Rebuild from known-good commit; new version and verified provenance |
| Cloud/provider outage | Use local reproducible verification/demo path where supported | Resume only after health checks and reconciliation |
| Artifact store loss | Preserve known digests and metadata | Restore from independent immutable backup; verify digest after restore |
| Data exposure | Contain access and preserve evidence | Legal/privacy-led notification and remediation |
| Dependency compromise | Freeze affected dependency update | Pin known-good version, rebuild, scan and document exposure |

## Recovery objectives
Initial proposed objectives, requiring a tabletop exercise before adoption:
- Repository source recovery point objective (RPO): 24 hours.
- Documentation/evidence RPO: 24 hours.
- Critical security-response contact availability: two independent authorized people.
- Recovery time objective (RTO): 1 business day for repository access and emergency release governance; 3 business days for noncritical documentation services.
These are planning targets, not current service commitments.

## Backups and recovery controls
- Maintain a periodic read-only mirror of source and signed release metadata in a separately controlled account.
- Back up release artifacts, SBOMs, provenance, trust policies and audit records with immutable retention where legally appropriate.
- Encrypt backups; restrict restore authority; test restore integrity by digest.
- Keep recovery credentials offline or in an approved secrets manager with dual control.
- Document emergency access without placing credentials in this repository.
- Test recovery quarterly and after material architecture changes.

## Continuity governance
At least two people must be able to triage reports, approve emergency fixes, access release procedures and communicate with users. If this cannot be demonstrated, disclose the single-maintainer/key-person risk and do not claim resilient operations.
