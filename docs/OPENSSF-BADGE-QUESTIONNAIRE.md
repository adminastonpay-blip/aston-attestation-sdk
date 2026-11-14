<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# OpenSSF Best Practices Badge — Questionnaire Answer Guide

**Repository:** https://github.com/adminastonpay-blip/aston-attestation-sdk  
**Assessment snapshot:** 2026-11-14  
**Default branch reviewed:** main  
**HEAD reviewed:** 05f75e1d2728cbd4e1019c60f5b2117146b0a1c9  
**Badge level covered:** Passing  
**Scope:** Change Control, Reporting, Quality, Security, Analysis. The Basics/General section is intentionally excluded because the maintainers report that it has already been completed.

> **Important — repository scope:** The reviewed main branch currently presents a foundational JSON Schema and specification overview, not a functioning Python SDK or cryptographic verifier. The README explicitly says the schema does not generate or verify signatures, prove issuer identity, validate timestamps or external anchors, and does not claim a certified SDK or conformance suite. The only primary machine-readable artifact confirmed in this review is agent-attestation.schema.json. No Python source file, test suite, packaging manifest, or workflow was confirmed on main. Therefore, do not infer implementation from the repository name or from code in other ASTON repositories.
>
> The user-selected General language value “Python/JSON” should be checked against the current repository contents before submission: Python source was not found in the inspected main-branch files. If Python code exists in another branch or has been added since this snapshot, reassess the Python-specific answers.

## How to use this guide

- Select exactly the status shown for each criterion: **Met**, **Unmet**, or **N/A**.
- Copy the English text under **Justification to paste** into the OpenSSF form.
- Where a criterion is marked **Unmet**, keep it Unmet even if a related workflow or implementation exists only in an unmerged pull request.
- N/A is used only where the current schema-only scope makes a criterion genuinely inapplicable. An SDK is still software; do not mark a criterion N/A merely because implementation work is unfinished.
- The justifications describe the evidence reviewed, not a promise that work has been completed.
- Some Passing criteria are MUST. An Unmet answer on a MUST criterion prevents a Passing badge until corrected. SHOULD and SUGGESTED criteria may be left Unmet subject to the badge rules and any required justification.

## Evidence reviewed

- README: https://github.com/adminastonpay-blip/aston-attestation-sdk/blob/05f75e1d2728cbd4e1019c60f5b2117146b0a1c9/README.md
- License: https://github.com/adminastonpay-blip/aston-attestation-sdk/blob/05f75e1d2728cbd4e1019c60f5b2117146b0a1c9/LICENSE
- Security policy: https://github.com/adminastonpay-blip/aston-attestation-sdk/blob/05f75e1d2728cbd4e1019c60f5b2117146b0a1c9/SECURITY.md
- JSON Schema: https://github.com/adminastonpay-blip/aston-attestation-sdk/blob/05f75e1d2728cbd4e1019c60f5b2117146b0a1c9/agent-attestation.schema.json
- Public issues: https://github.com/adminastonpay-blip/aston-attestation-sdk/issues
- Pull requests: https://github.com/adminastonpay-blip/aston-attestation-sdk/pulls
- Official Passing criteria: https://www.bestpractices.dev/en/criteria

**Branch/PR caution:** PR #1, “chore(security): ASTON security standardization baseline”, was visible but unmerged during this review. Its proposed secret-scanning, dependency-review, Scorecard and SLSA workflow files, and requirements.txt, are not evidence of controls already present on main. Do not mark those controls Met until the changes are merged and their operation is verified.

---

# 1. Change Control

### CC-01 — repo_public

**Question (English):** The project MUST have a version-controlled source repository that is publicly readable and has a URL.

**Answer:** **Met**

**Justification to paste:**
> The project source repository is public and version-controlled. The repository is available at https://github.com/adminastonpay-blip/aston-attestation-sdk.

### CC-02 — repo_track

**Question (English):** The project's source repository MUST track what changes were made, who made the changes, and when the changes were made.

**Answer:** **Met**

**Justification to paste:**
> The public Git repository records changes as commits with commit authorship and timestamps. The commit history is available at https://github.com/adminastonpay-blip/aston-attestation-sdk/commits/main.

### CC-03 — repo_interim

**Question (English):** To enable collaborative review, the project's source repository MUST include interim versions for review between releases; it MUST NOT include only final releases.

**Answer:** **Met**

**Justification to paste:**
> The repository exposes the ongoing main-branch history and pull requests, rather than distributing only final release snapshots. Reviewable changes are available at https://github.com/adminastonpay-blip/aston-attestation-sdk/pulls.

### CC-04 — repo_distributed

**Question (English):** It is SUGGESTED that common distributed version control software be used (e.g., git) for the project's source repository.

**Answer:** **Met**

**Justification to paste:**
> The project uses Git, a widely used distributed version control system, hosted publicly on GitHub.

### CC-05 — version_unique

**Question (English):** The project results MUST have a unique version identifier for each release intended to be used by users.

**Answer:** **Unmet**

**Justification to paste:**
> The reviewed default branch documents schema version 1.0.0, but I could not verify published project releases with unique release identifiers. The schema version alone is not evidence that a corresponding SDK release has been published. This criterion will be reassessed when versioned releases are published.

### CC-06 — version_semver

**Question (English):** It is SUGGESTED that the Semantic Versioning (SemVer) or Calendar Versioning (CalVer) version numbering format be used for releases. It is SUGGESTED that those who use CalVer include a micro level value.

**Answer:** **Unmet**

**Justification to paste:**
> The schema declares version 1.0.0, but no published release sequence using SemVer or CalVer was verified on the reviewed default branch. A schema version declaration is not, by itself, evidence of a release numbering policy.

### CC-07 — version_tags

**Question (English):** It is SUGGESTED that projects identify each release within their version control system. For example, it is SUGGESTED that those using git identify each release using git tags.

**Answer:** **Unmet**

**Justification to paste:**
> I could not verify Git tags corresponding to published project releases in the evidence reviewed. Release tags should be created and documented when versioned releases are published.

### CC-08 — release_notes

**Question (English):** The project MUST provide, in each release, release notes that are a human-readable summary of major changes in that release to help users determine if they should upgrade and what the upgrade impact will be. The release notes MUST NOT be the raw output of a version control log (e.g., the "git log" command results are not release notes). Projects whose results are not intended for reuse in multiple locations (such as the software for a single website or service) AND employ continuous delivery MAY select "N/A".

**Answer:** **Unmet**

**Justification to paste:**
> No published release notes were verified for this repository. The README describes the schema and its limitations, but it is not a per-release human-readable change summary. Release notes must be provided with each future release.

### CC-09 — release_notes_vulns

**Question (English):** The release notes MUST identify every publicly known run-time vulnerability fixed in this release that already had a CVE assignment or similar when the release was created. This criterion may be marked as not applicable (N/A) if users typically cannot practically update the software themselves (e.g., as is often true for kernel updates). If there are no release notes or there have been no publicly known vulnerabilities, choose N/A.

**Answer:** **N/A**

**Justification to paste:**
> No project release notes or published release artifacts were identified in the reviewed repository snapshot. There is therefore no release-specific vulnerability-fix information to report for this criterion at this time. This answer must be revisited when releases are published.

---

# 2. Reporting

### RP-01 — report_process

**Question (English):** The project MUST provide a process for users to submit bug reports (e.g., using an issue tracker or a mailing list).

**Answer:** **Met**

**Justification to paste:**
> The README invites users to report issues and submit pull requests through the public GitHub repository. The issue submission process is available at https://github.com/adminastonpay-blip/aston-attestation-sdk/issues.

### RP-02 — report_tracker

**Question (English):** The project SHOULD use an issue tracker for tracking individual issues.

**Answer:** **Met**

**Justification to paste:**
> The project uses GitHub Issues as its public issue-tracking mechanism: https://github.com/adminastonpay-blip/aston-attestation-sdk/issues.

### RP-03 — report_responses

**Question (English):** The project MUST acknowledge a majority of bug reports submitted in the last 2-12 months (inclusive); the response need not include a fix.

**Answer:** **Unmet**

**Justification to paste:**
> I could not establish an auditable response rate for bug reports submitted during the required 2-to-12-month period. The public issue tracker is available, but the reviewed evidence does not establish that a majority of applicable reports received an acknowledgement. The maintainers must review the complete issue history before changing this answer.

### RP-04 — enhancement_responses

**Question (English):** The project SHOULD respond to a majority (>50%) of enhancement requests in the last 2-12 months (inclusive).

**Answer:** **Unmet**

**Justification to paste:**
> I could not establish from the available public evidence that more than 50% of enhancement requests submitted during the required 2-to-12-month period received a response. The maintainers should review and count the applicable requests before marking this criterion Met.

### RP-05 — report_archive

**Question (English):** The project MUST have a publicly available archive for reports and responses for later searching.

**Answer:** **Met**

**Justification to paste:**
> GitHub Issues provides a public, URL-addressable and searchable archive for project reports and maintainer responses: https://github.com/adminastonpay-blip/aston-attestation-sdk/issues.

### RP-06 — vulnerability_report_process

**Question (English):** The project MUST publish the process for reporting vulnerabilities on the project site.

**Answer:** **Met**

**Justification to paste:**
> The repository publishes a security policy describing how to report suspected vulnerabilities, the information to include, the expected coordination approach, and the project's security scope. See https://github.com/adminastonpay-blip/aston-attestation-sdk/blob/main/SECURITY.md.

### RP-07 — vulnerability_report_private

**Question (English):** If private vulnerability reports are supported, the project MUST include how to send the information in a way that is kept private.

**Answer:** **Met**

**Justification to paste:**
> SECURITY.md instructs reporters not to disclose vulnerabilities in public issues, discussions or pull requests and documents the GitHub private vulnerability reporting route, with a private maintainer contact fallback. See https://github.com/adminastonpay-blip/aston-attestation-sdk/blob/main/SECURITY.md. The maintainers should confirm that private vulnerability reporting is enabled in the repository settings.

### RP-08 — vulnerability_report_response

**Question (English):** The project's initial response time for any vulnerability report received in the last 6 months MUST be less than or equal to 14 days.

**Answer:** **Unmet**

**Justification to paste:**
> The published security policy does not guarantee an initial response within 14 days; it states that response and remediation times are not guaranteed. I could not inspect private vulnerability reports to establish the actual response time for the last six months. The criterion is therefore not verified and is marked Unmet pending maintainer review of private report records.

---

# 3. Quality

### QL-01 — build

**Question (English):** If the software produced by the project requires building for use, the project MUST provide a working build system that can automatically rebuild the software from source code.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository currently publishes a JSON Schema and documentation. These artifacts are consumed directly and do not require compilation or a software build step to be used. This answer must be revisited if executable SDK packages or generated build artifacts are added.

### QL-02 — build_common_tools

**Question (English):** It is SUGGESTED that common tools be used for building the software.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository contains a directly consumable JSON Schema and documentation and has no verified build system. Common build-tool selection is not applicable to these current artifacts.

### QL-03 — build_floss_tools

**Question (English):** The project SHOULD be buildable using only FLOSS tools.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository contains a JSON Schema and documentation that do not require a build step. There is currently no build toolchain to assess.

### QL-04 — test

**Question (English):** The project MUST use at least one automated test suite that is publicly released as FLOSS (this test suite may be maintained as a separate FLOSS project). The project MUST clearly show or document how to run the test suite(s) (e.g., via a continuous integration (CI) script or via documentation in files such as BUILD.md, README.md, or CONTRIBUTING.md).

**Answer:** **Unmet**

**Justification to paste:**
> I could not verify a publicly available automated test suite or documented test execution instructions on the reviewed main branch. The JSON Schema is present, but its presence alone does not demonstrate automated tests. A public schema-validation and regression test suite is required.

### QL-05 — test_invocation

**Question (English):** A test suite SHOULD be invocable in a standard way for that language.

**Answer:** **Unmet**

**Justification to paste:**
> No test suite or standard test command was verified on the reviewed main branch. A documented standard invocation, such as a conventional Python test command if Python implementation code is added, is not currently evidenced.

### QL-06 — test_most

**Question (English):** It is SUGGESTED that the test suite cover most (or ideally all) the code branches, input fields, and functionality.

**Answer:** **Unmet**

**Justification to paste:**
> No automated test suite or coverage report was verified. Coverage of schema fields, valid and invalid documents, boundary conditions and compatibility cases therefore cannot currently be demonstrated.

### QL-07 — test_continuous_integration

**Question (English):** It is SUGGESTED that the project implement continuous integration (where new or changed code is frequently integrated into a central code repository and automated tests are run on the result).

**Answer:** **Unmet**

**Justification to paste:**
> I could not verify an active CI workflow on the reviewed main branch that runs automated project tests on changes. A workflow proposed only in an unmerged pull request is not evidence of an implemented CI control.

### QL-08 — test_policy

**Question (English):** The project MUST have a general policy (formal or not) that as major new functionality is added to the software produced by the project, tests of that functionality should be added to an automated test suite.

**Answer:** **Unmet**

**Justification to paste:**
> The README describes contribution expectations and requests examples and security-impact information, but it does not establish a policy requiring automated tests for major new functionality. No separate contribution policy documenting this requirement was verified.

### QL-09 — tests_are_added

**Question (English):** The project MUST have evidence that the test_policy for adding tests has been adhered to in the most recent major changes to the software produced by the project.

**Answer:** **Unmet**

**Justification to paste:**
> No test-addition policy or corresponding automated regression tests for the most recent major changes were verified on the reviewed main branch. There is insufficient evidence to demonstrate adherence to this criterion.

### QL-10 — tests_documented_added

**Question (English):** It is SUGGESTED that this policy on adding tests (see test_policy) be documented in the instructions for change proposals.

**Answer:** **Unmet**

**Justification to paste:**
> The repository does not currently provide verified contribution instructions that explicitly require tests for major new functionality. This should be added to the documented pull-request or contribution process.

### QL-11 — warnings

**Question (English):** The project MUST enable one or more compiler warning flags, a "safe" language mode, or use a separate "linter" tool to look for code quality errors or common simple mistakes, if there is at least one FLOSS tool that can implement this criterion in the selected language.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed main branch contains a JSON Schema and Markdown documentation, not executable Python source code or compiled code. No compiler warning or Python linter configuration applies to these current artifacts. Reassess this answer if executable Python modules are added.

### QL-12 — warnings_fixed

**Question (English):** The project MUST address warnings.

**Answer:** **N/A**

**Justification to paste:**
> No executable source code, compiler configuration or linter workflow was verified on the reviewed main branch. There are therefore no applicable compiler or linter warnings to assess for the current schema-and-documentation-only repository.

### QL-13 — warnings_strict

**Question (English):** It is SUGGESTED that projects be maximally strict with warnings in the software produced by the project, where practical.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository currently publishes a JSON Schema and documentation without executable source code or a compiler/linter configuration. Strict compiler or linter warning settings are not applicable to these current artifacts.

---

# 4. Security

### SE-01 — know_secure_design

**Question (English):** The project MUST have at least one primary developer who knows how to design secure software. (See ‘details’ for the exact requirements.)

**Answer:** **Unmet — maintainer confirmation required**

**Justification to paste:**
> This criterion is a statement about the knowledge of a primary human developer and cannot be established from repository files alone. The project has not yet provided auditable maintainer confirmation or supporting evidence of the required secure-software design knowledge. A primary developer must review the criterion details and attest truthfully before this answer is changed.

### SE-02 — know_common_errors

**Question (English):** At least one of the project's primary developers MUST know of common kinds of errors that lead to vulnerabilities in this kind of software, as well as at least one method to counter or mitigate each of them.

**Answer:** **Unmet — maintainer confirmation required**

**Justification to paste:**
> This criterion requires confirmation of a primary developer's knowledge of relevant vulnerability classes and mitigations. Repository documentation alone does not establish an individual's knowledge. A primary developer must review the criterion details and provide a truthful attestation before this answer is changed.

### SE-03 — crypto_published

**Question (English):** The software produced by the project MUST use, by default, only cryptographic protocols and algorithms that are publicly published and reviewed by experts (if cryptographic protocols and algorithms are used).

**Answer:** **N/A**

**Justification to paste:**
> The reviewed project publishes a descriptive JSON Schema and does not implement cryptographic protocols or algorithms. The README explicitly states that the schema does not generate or verify cryptographic signatures. Cryptographic verification is delegated to independent implementations.

### SE-04 — crypto_call

**Question (English):** If the software produced by the project is an application or library, and its primary purpose is not to implement cryptography, then it SHOULD only call on software specifically designed to implement cryptographic functions; it SHOULD NOT re-implement its own.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository contains a JSON Schema and documentation, not an executable application or library that calls cryptographic functions. It does not implement or re-implement cryptography.

### SE-05 — crypto_floss

**Question (English):** All functionality in the software produced by the project that depends on cryptography MUST be implementable using FLOSS.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed schema does not perform cryptographic operations or depend on a cryptographic implementation. Any future verifier implementation must reassess this criterion and document its cryptographic dependencies.

### SE-06 — crypto_keylength

**Question (English):** The security mechanisms within the software produced by the project MUST use default keylengths that at least meet the NIST minimum requirements through the year 2030 (as stated in 2012). It MUST be possible to configure the software so that smaller keylengths are completely disabled.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository does not implement key generation, key exchange, signing or other cryptographic security mechanisms. Key-length policy belongs to a future cryptographic implementation or verifier, not to this JSON Schema.

### SE-07 — crypto_working

**Question (English):** The default security mechanisms within the software produced by the project MUST NOT depend on broken cryptographic algorithms (e.g., MD4, MD5, single DES, RC4, Dual_EC_DRBG), or use cipher modes that are inappropriate to the context, unless they are necessary to implement an interoperable protocol (where the protocol implemented is the most recent version of that standard broadly supported by the network ecosystem, that ecosystem requires the use of such an algorithm or mode, and that ecosystem does not offer any more secure alternative). The documentation MUST describe any relevant security risks and any known mitigations if these broken algorithms or modes are necessary for an interoperable protocol.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository does not implement cryptographic security mechanisms or cipher modes. The schema allows algorithm-labelled metadata but does not execute or select cryptographic algorithms.

### SE-08 — crypto_weaknesses

**Question (English):** The default security mechanisms within the software produced by the project SHOULD NOT depend on cryptographic algorithms or modes with known serious weaknesses (e.g., the SHA-1 cryptographic hash algorithm or the CBC mode in SSH).

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository does not implement cryptographic mechanisms or select digest algorithms for execution. It only defines a data format in which implementations identify algorithms explicitly.

### SE-09 — crypto_pfs

**Question (English):** The security mechanisms within the software produced by the project SHOULD implement perfect forward secrecy for key agreement protocols so a session key derived from a set of long-term keys cannot be compromised if one of the long-term keys is compromised in the future.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository does not implement network sessions, key agreement or cryptographic security mechanisms. Perfect forward secrecy is therefore outside the current schema-only scope.

### SE-10 — crypto_password_storage

**Question (English):** If the software produced by the project causes the storing of passwords for authentication of external users, the passwords MUST be stored as iterated hashes with a per-user salt by using a key stretching (iterated) algorithm (e.g., Argon2id, Bcrypt, Scrypt, or PBKDF2).

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository does not authenticate external users or store passwords. It publishes a JSON Schema and documentation only.

### SE-11 — crypto_random

**Question (English):** The security mechanisms within the software produced by the project MUST generate all cryptographic keys and nonces using a cryptographically secure random number generator, and MUST NOT do so using generators that are cryptographically insecure.

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository does not generate cryptographic keys or nonces. The schema describes attestation fields but does not implement cryptographic operations or random-number generation.

### SE-12 — delivery_mitm

**Question (English):** The project MUST use a delivery mechanism that counters MITM attacks. Using https or ssh+scp is acceptable.

**Answer:** **Met**

**Justification to paste:**
> The source repository is hosted and accessed through GitHub HTTPS. The public repository URL uses HTTPS: https://github.com/adminastonpay-blip/aston-attestation-sdk.

### SE-13 — delivery_unsigned

**Question (English):** A cryptographic hash (e.g., a sha1sum) MUST NOT be retrieved over http and used without checking for a cryptographic signature.

**Answer:** **Met**

**Justification to paste:**
> The reviewed README and repository references use HTTPS. I found no documented workflow that retrieves a cryptographic hash over plain HTTP and uses it without signature verification. This answer should be revisited if external download or checksum-verification scripts are introduced.

### SE-14 — vulnerabilities_fixed_60_days

**Question (English):** There MUST be no unpatched vulnerabilities of medium or higher severity that have been publicly known for more than 60 days.

**Answer:** **Unmet**

**Justification to paste:**
> I could not verify a completed dependency or vulnerability scan for the reviewed main-branch snapshot, nor establish from repository evidence that no medium-or-higher severity vulnerability has remained unpatched for more than 60 days. The maintainers must review GitHub Security Advisories, dependency alerts and relevant vulnerability databases before marking this criterion Met.

### SE-15 — vulnerabilities_critical_fixed

**Question (English):** Projects SHOULD fix all critical vulnerabilities rapidly after they are reported.

**Answer:** **Unmet**

**Justification to paste:**
> SECURITY.md describes coordinated vulnerability reporting but does not define a target remediation period for critical vulnerabilities. No auditable remediation history was available to demonstrate that critical vulnerabilities are fixed rapidly after reporting.

### SE-16 — no_leaked_credentials

**Question (English):** The public repositories MUST NOT leak a valid private credential (e.g., a working password or private key) that is intended to limit public access.

**Answer:** **Unmet**

**Justification to paste:**
> I could not verify an active secret-scanning result or equivalent credential audit for the reviewed main-branch snapshot. Absence of an obvious credential in a limited file review is not proof that the repository contains no valid leaked credentials. The maintainers must run and review secret scanning across the repository history before marking this criterion Met.

---

# 5. Analysis

### AN-01 — static_analysis

**Question (English):** At least one static code analysis tool (beyond compiler warnings and "safe" language modes) MUST be applied to any proposed major production release of the software before its release, if there is at least one FLOSS tool that implements this criterion in the selected language.

**Answer:** **Unmet**

**Justification to paste:**
> No static source-code analysis tool applied to proposed releases was verified on the reviewed main branch. JSON Schema validation is not, by itself, evidence that a static code analysis tool is applied to each proposed major production release. The security-analysis workflows visible only in an unmerged pull request do not count as implemented controls.

### AN-02 — static_analysis_common_vulnerabilities

**Question (English):** It is SUGGESTED that at least one of the static analysis tools used for the static_analysis criterion include rules or approaches to look for common vulnerabilities in the analyzed language or environment.

**Answer:** **Unmet**

**Justification to paste:**
> No static-analysis tool or vulnerability-focused rule set was verified on the reviewed main branch. This cannot be claimed until a tool and its results are available for review.

### AN-03 — static_analysis_fixed

**Question (English):** All medium and higher severity exploitable vulnerabilities discovered with static code analysis MUST be fixed in a timely way after they are confirmed.

**Answer:** **Unmet**

**Justification to paste:**
> No static-analysis workflow or auditable process linking confirmed findings to remediation was verified on the reviewed main branch. The project cannot demonstrate timely remediation of findings from a static-analysis tool that is not yet evidenced.

### AN-04 — static_analysis_often

**Question (English):** It is SUGGESTED that static source code analysis occur on every commit or at least daily.

**Answer:** **Unmet**

**Justification to paste:**
> No active static source-code analysis workflow running on every commit or daily was verified on the reviewed main branch.

### AN-05 — dynamic_analysis

**Question (English):** It is SUGGESTED that at least one dynamic analysis tool be applied to any proposed major production release of the software before its release.

**Answer:** **Unmet**

**Justification to paste:**
> No dynamic-analysis tool or pre-release dynamic-analysis results were verified for this repository. The current main branch provides a JSON Schema and does not document a dynamic testing process for proposed releases.

### AN-06 — dynamic_analysis_unsafe

**Question (English):** It is SUGGESTED that if the software produced by the project includes software written using a memory-unsafe language (e.g., C or C++), then at least one dynamic tool (e.g., a fuzzer or web application scanner) be routinely used in combination with a mechanism to detect memory safety problems such as buffer overwrites. If the project does not produce software written using a memory-unsafe language, choose "not applicable" (N/A).

**Answer:** **N/A**

**Justification to paste:**
> The reviewed repository contains a JSON Schema and documentation and does not include software written in a memory-unsafe language such as C or C++.

### AN-07 — dynamic_analysis_enable_assertions

**Question (English):** It is SUGGESTED that the project use a configuration for at least some dynamic analysis (such as testing or fuzzing) which enables many assertions. In many cases these assertions should not be enabled in production builds.

**Answer:** **Unmet**

**Justification to paste:**
> No dynamic-analysis or fuzz-testing configuration with assertions was verified on the reviewed main branch. The repository currently does not document such a test configuration.

### AN-08 — dynamic_analysis_fixed

**Question (English):** All medium and higher severity exploitable vulnerabilities discovered with dynamic code analysis MUST be fixed in a timely way after they are confirmed.

**Answer:** **Unmet**

**Justification to paste:**
> No dynamic-analysis workflow or auditable remediation process for confirmed dynamic-analysis findings was verified on the reviewed main branch. The project cannot demonstrate timely remediation of findings from a dynamic-analysis process that is not yet evidenced.

---

## Items requiring a human check before submitting

1. **Private vulnerability reporting:** confirm in GitHub repository Settings → Security that private vulnerability reporting is enabled. The SECURITY.md instructions are present, but repository settings were not independently inspected.
2. **Vulnerability response window:** review private reports/advisories from the last six months. Only the maintainers can establish whether every initial response was within 14 days or whether N/A is allowed because no report was received.
3. **Bug/enhancement response rates:** inspect the full issue history for the relevant 2-to-12-month period. Do not infer a response rate from an empty or partial issue search.
4. **Secret scanning and dependency review:** the proposed controls in PR #1 are not active evidence until merged and successfully executed on the default branch. Review the results, not merely the workflow filenames.
5. **Developer knowledge:** the primary developer must personally confirm the OpenSSF secure-design and common-vulnerability knowledge criteria.
6. **General language selection:** the current reviewed main branch did not expose Python source code. Confirm that “Python/JSON” accurately describes the repository being assessed.

## Important note about the Passing badge

OpenSSF's rules do not allow a project to pass with arbitrary Unmet answers. All MUST criteria must be Met or validly N/A; SHOULD criteria may be Unmet with an acceptable justification; SUGGESTED criteria must be considered. The current guide deliberately leaves unsupported MUST criteria as Unmet rather than inventing evidence. In particular, the test suite, test policy, response-time evidence, vulnerability posture and static-analysis controls are material gaps.

The Passing questionnaire contains no standalone requirement for an **external penetration test**. Do not claim one was performed. The relevant criteria here concern automated testing, static analysis and suggested dynamic analysis.

## Official references

- OpenSSF Passing criteria and all criterion wording: https://www.bestpractices.dev/en/criteria
- OpenSSF explanation of Met, Unmet, N/A and badge-level rules: https://www.bestpractices.dev/en/criteria_discussion
- Repository README and scope limitations: https://github.com/adminastonpay-blip/aston-attestation-sdk/blob/main/README.md
- Repository security policy: https://github.com/adminastonpay-blip/aston-attestation-sdk/blob/main/SECURITY.md

---
**Prepared as an evidence-based draft, not as an OpenSSF submission or certification. Reassess against the live default branch and current private repository settings immediately before submitting the answers.**
