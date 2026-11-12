# Security Policy

## Supported versions

Security fixes are currently provided for the latest version of the project on the default branch. No older release line is currently designated as supported. If versioned releases are introduced, this policy will be updated to identify their support windows.

## Reporting a vulnerability

Please do **not** report suspected security vulnerabilities in a public GitHub issue, discussion, pull request, or social-media post.

Use GitHub's private vulnerability reporting for this repository:

1. Open the repository's **Security** tab.
2. Select **Report a vulnerability** (or **Advisories**, then **Report a vulnerability**, depending on the GitHub interface).
3. Submit the report privately to the maintainers.

If private vulnerability reporting is not enabled or the option is unavailable, contact the repository maintainers privately through the contact route listed on the maintainers' GitHub profile. Do not publish exploit details while arranging contact.

Please include, where possible:

- A concise description and the affected file, component, commit, or version.
- The security impact and realistic attack scenario.
- Reproduction steps or a minimal proof of concept.
- Required configuration, permissions, and environmental assumptions.
- Any suggested mitigation.
- Whether the issue is known to affect production deployments or only a local/test fixture.

Do not include real credentials, private keys, access tokens, personal information, customer data, private prompts, or confidential production artifacts. Use synthetic data in proof-of-concept material.

## What to expect

The maintainers will make a reasonable effort to acknowledge a private report, assess its reproducibility and impact, coordinate a fix, and communicate a disclosure plan. Response and remediation times are not guaranteed; they depend on severity, report quality, maintainer availability, and the complexity of a safe fix.

Please allow maintainers reasonable time to investigate and prepare a correction before public disclosure. Coordinated disclosure is preferred. If a report is out of scope or cannot be reproduced, the maintainers may explain that assessment.

## Scope and security boundaries

Reports are especially useful for issues involving:

- Incorrect signature, digest, certificate, or proof verification.
- Trust-policy bypasses, key-confusion, algorithm-confusion, or unsafe certificate handling.
- Incorrect acceptance of malformed, altered, or untrusted proof packages.
- Fail-open behavior where a required verification step fails, is skipped, or is indeterminate.
- Unsafe parsing, path handling, command execution, dependency use, or CI workflow permissions.
- Leakage of secrets or sensitive attestation data caused by project code or workflows.

The following are not, by themselves, security vulnerabilities in this repository:

- A claim in an attestation that has not been independently substantiated.
- A syntactically valid JSON document whose semantic claims are false.
- A timestamp that is pending, incomplete, or not yet anchored, when the verifier correctly reports that state.
- A limitation explicitly documented in the schema or verification guide.
- Issues in third-party services or infrastructure that are not caused by this project, although a concrete unsafe interaction in the SDK may be in scope.

The repository's schema and reference verifier do not, by themselves, prove model identity, runtime integrity, issuer identity, or the truth of an agent's claims. A valid signature proves only that the signed bytes verify under a public key; identity depends on an independently established trust policy. An OpenTimestamps proof, when fully verified, supports an existence-time bound; it does not prove authorship or truth.

## Safe testing

Only test systems and data you own or are explicitly authorized to assess. Avoid denial of service, destructive actions, persistence, exfiltration, privacy violations, and tests against third-party production systems without permission. Do not use production credentials or real personal data in a report.

## Disclosure and credit

The maintainers may acknowledge researchers in a release note or security advisory, subject to the reporter's preference and applicable legal or safety constraints. Please state whether you want public credit and the name or handle to use. No bounty or compensation program is currently promised.

## Policy changes

This policy may be updated as the project adds releases, maintainers, or formal security-response processes. The policy in the repository's default branch is the current version.
