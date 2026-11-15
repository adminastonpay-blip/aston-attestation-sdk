<!--
SPDX-FileCopyrightText: 2026 Aston OS
SPDX-License-Identifier: Apache-2.0
-->
# Security Risk Register

Status: initial desk-based assessment; risks are not independently tested.  
Scoring: Critical / High / Medium / Low reflects potential impact and exposure, not a measured exploitability score.

| ID | Risk / weakness | Initial rating | Evidence or gap | Required action / exit evidence |
|---|---|---:|---|---|
| R-01 | SLSA Level 3 badge implies achieved status without a verifiable release | High | No published release/provenance established in this review | Badge removed in proposed change; publish only after independent verification |
| R-02 | Product name suggests a complete SDK although repo is schema/specification-led | Medium | README says no certified SDK/verifier | Rename or qualify product description; publish scope and roadmap |
| R-03 | `verified` can be producer-asserted in JSON | Critical for verifier consumers | Schema enum accepts the value; no trusted verifier is supplied here | Verifier must generate trusted result; tests prove self-assertion is ignored |
| R-04 | Signature semantics/canonicalization are unspecified | High | Schema stores algorithm/key/value but no suite semantics | Define versioned crypto profile and interoperable test vectors |
| R-05 | Digest algorithm/value length not bound | Medium | Algorithm free-form; value regex only | Profile-specific allowlist, encoding and exact lengths |
| R-06 | Arbitrary URI references may trigger SSRF or leak data | High for networked verifier | URI fields are allowed; schema does not define safe retrieval | Disable auto-fetch by default; SSRF-safe resolver and egress tests |
| R-07 | No schema-level resource limits for deeply nested/large documents | Medium | JSON Schema alone does not impose runtime resource budgets | Parser limits, fuzzing and resource-exhaustion tests |
| R-08 | Cross-field temporal consistency not enforced | Medium | Several timestamps can coexist | Semantic validation and clock-skew/replay tests |
| R-09 | Proof workflow's fixture checks are not equivalent to a complete verifier | High | CI workflow validates a fixture and tampering cases; README scope is foundational | Publish test coverage and limits; independent verifier review |
| R-10 | SLSA workflow only triggers on release creation | Medium | Workflow configuration | Validate release event, artifact subject, provenance identity and verifier output |
| R-11 | SBOM workflow success/artifact retention not proven for current main | Medium | Workflow configured; artifact evidence not collected in this assessment | Archive dated SBOM and validate completeness |
| R-12 | Governance, contribution and conduct docs absent at inspected ref | Medium | Files not found in repository snapshot | Add proposed docs; assign real owners and review |
| R-13 | Bus factor / key recovery / incident authority unknown | High | No independently confirmed alternate maintainers or recovery exercise | Name two authorized maintainers; conduct recovery drill |
| R-14 | No external penetration test / crypto review evidence | High | No report supplied | Commission independent scoped review; publish remediation summary |
| R-15 | Scorecard and REUSE badges may be mistaken for certification | Medium | Dynamic service outputs, not certifications | Date-stamp evidence; explain scope and limits |
| R-16 | Open issue / low community adoption may challenge maturity claims | Medium | Public repository metrics can change | Do not market adoption or maturity without dated metrics and support plan |
| R-17 | Apache 2.0 license does not prove contributor IP ownership or trademark rights | Medium | License file alone cannot establish chain of title | DCO/CLA decision, contributor records, trademark and entity counsel review |
| R-18 | Privacy, retention, residency and processor obligations for future production data undefined | High for production deployments | Repo policy explicitly does not create a product privacy notice | Product-specific data map, DPA, privacy notice and retention controls before launch |

## Prioritization
**P0 before any production verifier claim:** R-03, R-04, R-06, R-09, R-14.  
**P1 before investor/security due diligence:** R-01, R-02, R-10, R-11, R-12, R-13, R-17.  
**P2 before broad adoption:** R-05, R-07, R-08, R-15, R-16, R-18.

## Acceptance rule
A risk is not closed because a document describes a control. Closure requires an owner, implemented control, reproducible test, evidence link, date and reviewer. Until then, retain the risk as open or accepted by an explicitly authorized risk owner.
