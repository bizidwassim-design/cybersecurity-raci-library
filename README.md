# Cybersecurity RACI Matrices Library

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![CI](https://github.com/bizidwassim-design/cybersecurity-raci-library/actions/workflows/ci.yml/badge.svg)](https://github.com/bizidwassim-design/cybersecurity-raci-library/actions/workflows/ci.yml) [![Fictional data](https://img.shields.io/badge/sample%20data-fictional-informational)](SECURITY.md)

Twelve ready-to-adapt **RACI matrices** for the security processes every organisation runs — vulnerability
management, incident management, access review, change, backup, third-party risk, awareness, logging, asset
management, policy lifecycle, cloud posture and the **AI system lifecycle (ISO/IEC 42001)** — as plain CSV,
generated Markdown and one validated Excel workbook. Ten roles, 156 activities, every row mapped to ISO/IEC
27001:2022 Annex A, ISO/IEC 42001:2023 or NIST CSF 2.0 identifiers, and exactly one **A** per row, enforced by script.

> 🇫🇷 Résumé en français en bas de page.

## Layout

```
data/processes.csv          Catalogue: slug, title, summary — one line per process
data/<process>.csv          The source of truth: activity, reference, then R/A/C/I per role (12 files)
docs/<process>.md           Generated Markdown table per process
docs/index.md               Generated catalogue + accountability and responsibility heat maps
docs/role-definitions.md    What each of the ten roles means and owns
docs/how-to-adapt.md        Renaming and merging roles, splitting the A across business units, adding a process, common mistakes
RACI-Library.xlsx           Generated workbook: Index · one sheet per process · Roles (dropdowns, "one A" check, colours)
scripts/build_library.py    Validates every CSV and regenerates docs/ and the workbook (openpyxl only)
```

## Quick start

```bash
pip install openpyxl
python scripts/build_library.py --check     # validate only: one A, at least one R, known roles, known values
python scripts/build_library.py             # validate + regenerate docs/ and RACI-Library.xlsx
```

```
validated 12 processes, 156 activities: one A and at least one R per row
wrote docs/index.md and 12 process pages
wrote RACI-Library.xlsx (14 sheets)
```

Then start with [`docs/index.md`](docs/index.md), open the process you are about to run a workshop on, and
read [`docs/how-to-adapt.md`](docs/how-to-adapt.md) before you change a column.

## What's inside

| Process | Activities | Covers | Main references |
|---------|-----------:|--------|-----------------|
| [Vulnerability management](docs/vulnerability-management.md) | 12 | Policy and SLAs, scope, scanning, advisories, triage, infrastructure and application remediation, exceptions, rescans, emergency patching, reporting, review | ISO 27001 A.8.8 · NIST CSF ID.RA, PR.PS-02 |
| [Incident management](docs/incident-management.md) | 14 | Plan, reporting, triage, containment, evidence, legal duties, notifications, management briefing, HR cases, recovery, lessons learned, tabletop, AI incidents | A.5.24–A.5.28, A.6.8 · RS, RC |
| [Access review](docs/access-review.md) | 12 | Policy, scope, extraction, JML source, certification, privileged and third-party review, revocation, evidence, AI-system access, reporting, audit | A.5.15, A.5.18, A.8.2 · PR.AA-05 |
| [Change management](docs/change-management.md) | 13 | Policy and CAB, requests, security impact, standard/emergency/security-control approvals, testing, scheduling, implementation, rollback, CMDB, unauthorised changes, AI model changes | A.8.32, A.8.9 · PR.PS-01 |
| [Backup and recovery](docs/backup-and-recovery.md) | 12 | Policy, RTO/RPO, running and monitoring, protected copies, restore tests, DR exercise, SaaS coverage, incident restores, AI artefacts, retention, reporting | A.8.13, A.5.30 · PR.DS-11, RC.RP |
| [Third-party risk](docs/third-party-risk.md) | 13 | Policy and tiering, inventory, pre-contract assessment, clauses, approval, onboarding, monitoring, yearly review, supplier incidents, AI providers, offboarding, reporting, audit | A.5.19–A.5.22 · GV.SC |
| [Security awareness](docs/security-awareness.md) | 12 | Programme, approval, onboarding and refresher training, phishing simulations, role-based and AI-use training, board briefing, communications, violations, measurement, review | A.6.3 · PR.AT |
| [Logging and monitoring](docs/logging-and-monitoring.md) | 13 | Standard, sources, generation, forwarding, SIEM, alert triage, escalation, privileged-activity review, retention and legal holds, personal data in logs, AI events, metrics, review | A.8.15, A.8.16 · DE.CM, DE.AE |
| [Asset management](docs/asset-management.md) | 13 | Policy, hardware/software/information/AI inventories, ownership, classification, acceptable use, device lifecycle, discovery, disposal, reconciliation, reporting | A.5.9–A.5.13 · ID.AM |
| [Policy lifecycle](docs/policy-lifecycle.md) | 13 | Framework, requirements, drafting, legal/HR review, approval, publication, acknowledgement, standards, exceptions, periodic review, AI policy, compliance, audit | A.5.1, A.5.36 · GV.PO |
| [AI system lifecycle](docs/ai-system-lifecycle.md) | 16 | Objectives, registration, impact assessment, go/no-go, requirements, training data, secure development, validation, deployment approval, user information, monitoring, incidents, third-party AI, retirement, management review, audit | ISO 42001 A.2–A.10, cl. 9 · GV, ID.RA |
| [Cloud security posture](docs/cloud-security-posture.md) | 13 | Standards, service approval, account inventory, landing zones, guardrails, posture scanning, remediation, privileged identities, public exposure, spend anomalies, attestations, exit planning, reporting | A.5.23, A.8.9 · PR.PS, GV.SC |

**Roles (columns, same order everywhere):** Top management · CISO · IT operations · Security operations ·
Application owners · HR · Legal & compliance · Procurement · Internal audit · Data & AI teams.
Definitions in [`docs/role-definitions.md`](docs/role-definitions.md).

**Workbook:** `RACI-Library.xlsx` has an `Index` sheet linking to one sheet per process. Each role cell has an
R/A/C/I dropdown and a colour; the `A count`, `R count` and `Check` columns turn red the moment a row breaks the
rules. No macros. The build pins the file's timestamps, so it only changes when the content does.

## Design choices

* **CSV is the source, everything else is generated.** Review a RACI change like code: one line in a diff, a
  reason in the commit message. The Markdown and the workbook are rebuilt by CI and must match the CSV.
* **Exactly one A, at least one R, no A/R on the same function.** The accountable role owns the outcome; the
  responsible role does the work. The CISO is therefore A on most operational rows while IT, the SOC or the
  application owner is R. The convention is explained and easy to relax in [`docs/how-to-adapt.md`](docs/how-to-adapt.md).
* **Empty cells are a feature.** A matrix where every function is at least "informed" of everything tells nobody anything.
* **Internal audit stays independent.** The script warns when audit holds R or A on an operational activity.
* **AI is not a separate world.** Every process has at least one AI row (AI incidents, AI model changes, AI
  artefact backups, AI event logging, AI providers…) and the ISO/IEC 42001 lifecycle has its own full matrix.
* **Identifiers only.** Standards are cited by control ID; no text from ISO or NIST is reproduced.

## Related repositories

| Repository | Relationship |
|------------|--------------|
| [iso27001-iso42001-toolkit](https://github.com/bizidwassim-design/iso27001-iso42001-toolkit) | Holds the single ISMS/AIMS-level RACI (20 governance activities); this library is the process-level layer beneath it |
| [grc-control-crosswalk](https://github.com/bizidwassim-design/grc-control-crosswalk) | Map each `reference` ID to NIST CSF 2.0, CIS v8 and SOC 2 |
| [application-risk-assessment-template](https://github.com/bizidwassim-design/application-risk-assessment-template) | The "Application owners" column assumes every system has an owner — that template is where you record it |
| [soc-detection-playbooks](https://github.com/bizidwassim-design/soc-detection-playbooks) | Fills in the "Security operations" R cells of logging/monitoring and incident management |
| [ciso-executive-dashboard](https://github.com/bizidwassim-design/ciso-executive-dashboard) | The "report to management" rows of every process feed it |
| [public-scripts](https://github.com/bizidwassim-design/public-scripts) | Automation behind several R cells (access reviews, Conditional Access, posture checks) |

## Contributing

New processes (secure development, physical security, business continuity), sector variants and translations
are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).
Run `python scripts/build_library.py` before opening a pull request and commit the regenerated files.

## Disclaimer

A model of responsibilities, not a statement about any real organisation. Adapt the roles to your own
structure and have the result approved by the people in the A column; a RACI nobody signed is a drawing.

## License

[MIT](LICENSE) — free to use, copy, modify and redistribute.

---

## 🇫🇷 Résumé

Bibliothèque **open source** de douze matrices **RACI** pour les processus de cybersécurité : gestion des
vulnérabilités, des incidents, revues d'accès, changements, sauvegardes, risques fournisseurs, sensibilisation,
journalisation, actifs, cycle de vie des politiques, posture cloud et cycle de vie des systèmes d'IA (ISO/IEC 42001).
Dix rôles, 156 activités, chacune référencée aux identifiants ISO/IEC 27001:2022, ISO/IEC 42001:2023 et NIST CSF 2.0.
Les CSV font foi ; un script Python valide chaque ligne (un seul A, au moins un R) et génère les pages Markdown et un
classeur Excel avec listes déroulantes et contrôle « un seul A », sans macro. Guide d'adaptation et définitions des
rôles inclus. Licence MIT.
