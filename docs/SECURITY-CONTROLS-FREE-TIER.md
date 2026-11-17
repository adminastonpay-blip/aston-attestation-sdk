# SPDX-FileCopyrightText: 2026 Aston OS
# SPDX-License-Identifier: Apache-2.0

# Free-tier security controls

## Purpose

This repository is private and is maintained without GitHub Advanced Security.
The CI security checks in this document use community or open-source tooling and
do not depend on GitHub Code Security or Dependency Review entitlements.

## Automated checks

The `.github/workflows/free-security.yml` workflow runs on pull requests to
`main`, pushes to `main`, and manual dispatch:

| Control | Tool | Scope |
| --- | --- | --- |
| Secret detection | Gitleaks | Git history checked out by the workflow |
| Static analysis | Semgrep Community rules (`p/python`) | Python source in the repository |
| Python-specific security lint | Bandit | Python source in the repository |
| Dependency vulnerability audit | pip-audit | Dependencies listed in `requirements.txt` |
| License and SPDX compliance | REUSE workflow | Existing separate `reuse.yml` workflow |

Dependabot configuration and GitHub's available dependency graph/Dependabot
features remain separate from these CI checks.

## GitHub Advanced Security workflows

The CodeQL and Dependency Review workflows are removed from this private
repository's CI configuration because their private-repository execution
requires GitHub security entitlements that are not included in the current
plan. Their absence is an availability limitation, not a passing scan.

## Interpretation and limitations

- A passing workflow means only that the listed tools completed successfully
  against the checked-out revision and their configured scope.
- A passing scan is not proof that the repository is vulnerability-free.
- `pip-audit` audits the dependencies declared in `requirements.txt`; it
  does not discover every runtime, operating-system, or transitive dependency
  outside that manifest.
- Semgrep's selected community rules and Bandit's checks are not equivalent
  to GitHub CodeQL or a full security audit.
- Gitleaks detects patterns and may produce false positives or miss secrets.
  Findings require human triage.
- No result in this workflow establishes SLSA conformance, provenance validity,
  production readiness, certification, or independent verification.
- The existing SLSA/provenance workflows and published release artifacts are
  not modified by this adaptation.

## Review policy

Treat scanner output as evidence for the exact commit tested. Review alerts,
confirm remediation, and retain the workflow run URL and commit SHA when
recording a result. Do not describe an unavailable control as passed.
