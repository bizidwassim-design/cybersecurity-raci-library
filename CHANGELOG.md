# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-10-31

### Added
- Twelve RACI matrices as CSV (156 activities, 10 roles): vulnerability management, incident management, access review,
  change management, backup and recovery, third-party risk, security awareness, logging and monitoring, asset management,
  policy lifecycle, AI system lifecycle (ISO/IEC 42001), cloud security posture.
- Every activity referenced to ISO/IEC 27001:2022 Annex A, ISO/IEC 42001:2023 or NIST CSF 2.0 identifiers.
- `scripts/build_library.py`: validation (one A, at least one R, known roles and values, manifest consistency, independence
  warnings), generated `docs/<process>.md`, `docs/index.md` with accountability and responsibility heat maps, and
  `RACI-Library.xlsx` with dropdowns, "one A" check column and conditional formatting (openpyxl, no macros, pinned timestamps).
- `docs/role-definitions.md` and `docs/how-to-adapt.md`.
- CI that validates, rebuilds and diffs the generated docs; `SECURITY.md`; Dependabot for GitHub Actions; this changelog.
