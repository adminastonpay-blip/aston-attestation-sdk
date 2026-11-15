<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Security Incident Response Plan

Status: proposed operational plan. Named responders and contact channels must be completed before production use.

## Severity
- **SEV-1 Critical:** suspected signing-key compromise, forged trusted verification, malicious release/provenance, confirmed sensitive-data exposure, or widespread verifier bypass.
- **SEV-2 High:** exploitable vulnerability affecting supported verification or release paths; compromised maintainer account; material integrity failure.
- **SEV-3 Moderate:** limited-scope vulnerability with mitigations; dependency issue without known exploitation.
- **SEV-4 Low:** documentation, hardening or non-security defect.

## Immediate actions
1. Open a private security advisory; do not publish exploit details.
2. Assign an incident commander and a separate technical investigator where staffing permits.
3. Preserve evidence: commit IDs, workflow run IDs, artifact digests, audit logs, timestamps and relevant access records.
4. Stop affected releases and distribution; do not delete evidence.
5. Revoke or rotate suspected credentials, tokens, certificates and keys using the relevant provider's documented process.
6. Identify affected versions, tenants, artifacts, attestations and downstream consumers.
7. Set the system to fail closed for the affected verification path; if safe operation cannot be established, disable the affected feature.
8. Notify affected customers/partners and legal/privacy contacts according to contractual and legal duties.

## Investigation
- Establish timeline and initial access vector.
- Determine whether source, build, signing identity, artifact, trust store or verifier was affected.
- Reproduce in an isolated environment using synthetic data.
- Determine whether any `verified` decisions were incorrect.
- Identify all impacted digests and release tags.
- Record confidence and unknowns separately from confirmed facts.

## Recovery
- Fix the root cause in a reviewed branch and PR.
- Add regression tests for the exploit and adjacent failure modes.
- Rebuild from a known-good commit in a trusted workflow.
- Publish corrected artifacts with new immutable version identifiers; never silently replace a compromised artifact.
- Revoke compromised keys and publish trust-policy updates.
- Verify provenance and artifact digests independently before re-enabling distribution.
- Monitor for recurrence and downstream reports.

## Communications
- One designated spokesperson.
- State what is known, unknown, affected, contained and being done.
- Do not speculate, minimize impact or claim resolution before verification.
- Preserve legal privilege where counsel directs; coordinate regulatory/customer notices with counsel.
- Publish a post-incident report after containment, subject to privacy and security constraints.

## Targets (internal objectives, not contractual SLAs)
- SEV-1 triage: immediately during staffed coverage; escalation route must be tested.
- Initial acknowledgement: target within 24 hours for critical reports; the public SECURITY.md currently sets a 14-calendar-day acknowledgement target for general reports.
- Containment: prioritize immediately; report actual timestamps.
- Root-cause and corrective action review: within 10 business days after containment where feasible.

## Required contacts and prerequisites
Before production, record: primary and backup incident commanders, security contact, legal/privacy contact, cloud provider escalation, key custodian, customer communications owner, and emergency access procedure. No personal contact details or secrets belong in this public document.
