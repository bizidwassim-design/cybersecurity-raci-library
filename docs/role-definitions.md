# Role definitions

Every matrix in this library uses the same ten roles, in the same column order. They are **functions**, not
people or job titles: one person may hold several of them in a small organisation, and one function may be a
department of forty in a large one. Rename them to match your organisation chart (see
[how-to-adapt.md](how-to-adapt.md)) but keep the meaning, otherwise the A/R split stops making sense.

## The letters

| Letter | Meaning | Rule in this library |
|--------|---------|----------------------|
| **R** — Responsible | Does the work, or directs the team that does it | At least one per activity. Several R are fine when the work is genuinely shared. |
| **A** — Accountable | Owns the outcome, answers for it, signs it off | Exactly one per activity. Never shared, never empty. |
| **C** — Consulted | Gives input **before** the decision or the work; two-way | Use sparingly. Every C is a meeting. |
| **I** — Informed | Told **after** the decision or the work; one-way | Use when the role needs to act on the outcome, not out of politeness. |
| *(empty)* | Not involved | Perfectly acceptable. A matrix with no empty cells is a matrix nobody will read. |

## The roles

### Top management
*Typical titles:* CEO, managing director, executive committee, board risk or audit committee.

Accountable for approving policies, plans and budgets, for accepting residual risk above the CISO's threshold,
and for independent review (internal audit reports to it). Almost never R: when you find yourself writing an R
in this column, ask whether an executive really performs the task or merely approves it.

### CISO
*Typical titles:* CISO, head of information security, information security manager, ISMS lead.

Accountable for security **outcomes**: policies are current, vulnerabilities are fixed within SLA, logs reach
the SIEM, suppliers are assessed. The CISO is the A on most operational rows of this library even when another
team does the work — that is the design, not an oversight. R where the security function itself produces
something (a policy draft, a report to management).

### IT operations
*Typical titles:* IT director, head of infrastructure, platform or cloud engineering, service desk.

Responsible for running and changing infrastructure, endpoints, identity platforms, backups and the CMDB.
Accountable for change management, device lifecycle, the infrastructure inventory and service restoration —
the places where IT, not security, owns the outcome.

### Security operations
*Typical titles:* SOC, detection engineering, vulnerability management, security engineering, MSSP (through a contract owner).

Responsible for scanning, detecting, triaging, responding and operating security tooling. Rarely A: it executes
on behalf of the CISO. If your SOC manager is a peer of the CISO rather than a report, move some A from the CISO column.

### Application owners
*Typical titles:* business owner, product owner, system owner, data owner — including the owner of an AI system.

Accountable for decisions about **their** system: who gets access, which changes are acceptable, what the
recovery objectives are, whether an AI model may go live. Responsible for certifying access and remediating
application-level findings. This is the role most often missing from real organisations; if you cannot name an
owner for a system, that is finding number one.

### HR
*Typical titles:* human resources, people operations.

Accountable for the joiner/mover/leaver source of truth, acknowledgements, and the disciplinary process.
Responsible for delivering training and communications to staff. Consulted on anything touching employee data or conduct.

### Legal & compliance
*Typical titles:* general counsel, legal, data protection officer, compliance officer, privacy office.

Accountable for legal and regulatory requirements, contract clauses, retention and legal holds, and for
deciding what must be notified to whom. Consulted on incidents, supplier contracts, policies and AI impact assessments.

### Procurement
*Typical titles:* purchasing, vendor management, sourcing.

Accountable for the supplier inventory. Responsible for running contract and assessment logistics, for
contractor lists, and for offboarding suppliers. A role security teams frequently forget and then re-create as a shadow process.

### Internal audit
*Typical titles:* internal audit, second- or third-line assurance, audit committee secretariat.

Responsible **only** for independent reviews and audits, with Top management accountable for them. Consulted
on reports it will later audit, informed of most other things. Never R on operational activities — the build
script prints a warning if it finds one, because an auditor who runs the process cannot audit it.

### Data & AI teams
*Typical titles:* data engineering, data science, ML engineering, analytics platform, AI product team.

Responsible for data pipelines, models, training data, AI monitoring and the data side of backups, logging and
access. Shares R with application owners for AI systems; the application owner keeps the A for business
decisions and the CISO for security ones. Introduced for ISO/IEC 42001 but relevant to every process that
touches a data platform.

## Standards cited

References in the `reference` column are **identifiers only** — ISO/IEC 27001:2022 Annex A control IDs
(`A.5.x`–`A.8.x`), ISO/IEC 42001:2023 Annex A control IDs and clauses, and NIST CSF 2.0 subcategory IDs
(`GV`, `ID`, `PR`, `DE`, `RS`, `RC`). They tell an auditor where the activity sits; they do not reproduce
the standards, whose text must be obtained from ISO or NIST.
