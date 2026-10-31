#!/usr/bin/env python3
"""Validate the RACI matrices in data/ and generate docs/ and RACI-Library.xlsx.

    pip install openpyxl
    python scripts/build_library.py            # validate + generate
    python scripts/build_library.py --check    # validate only, no files written (no openpyxl needed)

Validation (errors stop the build, exit code 1):
  * every process in data/processes.csv has a data/<slug>.csv and vice versa;
  * the header is exactly: activity, reference, then the ten roles in ROLES order;
  * every cell is R, A, C, I or empty;
  * every row has exactly one A and at least one R;
  * activities are non-empty and unique within a process.

Advisory warnings (printed, never fatal):
  * Internal audit holds R or A on an activity that is not an audit or independent review;
  * Top management holds R (it usually approves, it rarely executes).

Generated files (do not edit them by hand; edit the CSV):
  docs/<slug>.md       one Markdown table per process
  docs/index.md        catalogue + accountability heat map
  RACI-Library.xlsx    one sheet per process with R/A/C/I dropdowns, "one A" check, colours
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"
XLSX = ROOT / "RACI-Library.xlsx"
MANIFEST = DATA / "processes.csv"

ROLES: tuple[str, ...] = (
    "Top management",
    "CISO",
    "IT operations",
    "Security operations",
    "Application owners",
    "HR",
    "Legal & compliance",
    "Procurement",
    "Internal audit",
    "Data & AI teams",
)
VALUES: frozenset[str] = frozenset({"R", "A", "C", "I", ""})
HEADER: tuple[str, ...] = ("activity", "reference", *ROLES)
AUDIT_WORDS = re.compile(r"\b(audit|independent)", re.IGNORECASE)

# Fixed timestamp so the workbook only changes when its content does.
STAMP = (2026, 1, 1, 0, 0, 0)


@dataclass
class Process:
    slug: str
    title: str
    summary: str
    rows: list[dict[str, str]] = field(default_factory=list)

    @property
    def sheet_name(self) -> str:
        return self.title[:31]

    def count(self, role: str, value: str) -> int:
        return sum(1 for r in self.rows if r[role] == value)


# --- Loading and validation ---------------------------------------------------


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.strip() for h in (reader.fieldnames or [])]
        rows = [{(k or "").strip(): (v or "").strip() for k, v in row.items()} for row in reader]
    return header, [r for r in rows if any(r.values())]


def load_manifest() -> list[Process]:
    header, rows = read_csv(MANIFEST)
    if header != ["slug", "title", "summary"]:
        raise SystemExit(f"error: {MANIFEST.name} must have columns slug,title,summary (got {header})")
    return [Process(slug=r["slug"], title=r["title"], summary=r["summary"]) for r in rows]


def validate(processes: list[Process]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    listed = {p.slug for p in processes}
    on_disk = {p.stem for p in DATA.glob("*.csv") if p.name != MANIFEST.name}
    for slug in sorted(on_disk - listed):
        errors.append(f"data/{slug}.csv exists but is not listed in {MANIFEST.name}")
    for slug in sorted(listed - on_disk):
        errors.append(f"{MANIFEST.name} lists '{slug}' but data/{slug}.csv does not exist")

    for proc in processes:
        path = DATA / f"{proc.slug}.csv"
        if not path.exists():
            continue
        header, rows = read_csv(path)
        if tuple(header) != HEADER:
            errors.append(f"{path.name}: header must be exactly {', '.join(HEADER)}")
            continue
        if not rows:
            errors.append(f"{path.name}: no activities")
            continue
        if len(proc.title) > 31:
            warnings.append(f"{proc.slug}: title longer than 31 characters will be truncated as a sheet name")
        seen: set[str] = set()
        for line, row in enumerate(rows, start=2):
            where = f"{path.name} line {line}"
            activity = row["activity"]
            if not activity:
                errors.append(f"{where}: empty activity")
            elif activity.lower() in seen:
                errors.append(f"{where}: duplicate activity '{activity}'")
            seen.add(activity.lower())
            if not row["reference"]:
                errors.append(f"{where}: empty reference")
            values = {role: row[role].upper() for role in ROLES}
            bad = [f"{role}={v!r}" for role, v in values.items() if v not in VALUES]
            if bad:
                errors.append(f"{where}: invalid value(s) {', '.join(bad)} (use R, A, C, I or leave empty)")
            n_a = sum(1 for v in values.values() if v == "A")
            n_r = sum(1 for v in values.values() if v == "R")
            if n_a != 1:
                errors.append(f"{where}: exactly one A required, found {n_a}")
            if n_r < 1:
                errors.append(f"{where}: at least one R required")
            if values["Internal audit"] in ("R", "A") and not AUDIT_WORDS.search(activity):
                warnings.append(f"{where}: Internal audit is {values['Internal audit']} on an operational activity — check independence")
            if values["Top management"] == "R":
                warnings.append(f"{where}: Top management is R — it usually approves rather than executes")
            for role in ROLES:
                row[role] = values[role]
        proc.rows = rows
    return errors, warnings


# --- Markdown -------------------------------------------------------------------


def md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def render_process_md(proc: Process) -> str:
    out = [f"# {proc.title} — RACI matrix", "", proc.summary, ""]
    out.append(
        "**R** responsible (does the work) · **A** accountable (one per activity, owns the outcome) · "
        "**C** consulted (two-way, before the decision) · **I** informed (one-way, after)."
    )
    out.append("")
    out.append("| # | Activity | Reference | " + " | ".join(ROLES) + " |")
    out.append("|---|----------|-----------|" + "|".join(":---:" for _ in ROLES) + "|")
    for n, row in enumerate(proc.rows, start=1):
        cells = " | ".join(row[r] or "" for r in ROLES)
        out.append(f"| {n} | {md_escape(row['activity'])} | {md_escape(row['reference'])} | {cells} |")
    out.append("")
    accountable = Counter(row[r] == "A" and r for row in proc.rows for r in ROLES)
    acc_lines = [f"{role} ({cnt})" for role, cnt in accountable.most_common() if role]
    out.append("**Accountable roles:** " + ", ".join(acc_lines) + ".")
    out.append("")
    out.append(
        f"_Generated by `scripts/build_library.py` from `data/{proc.slug}.csv` — edit the CSV, not this file. "
        "Standards are cited by identifier only; their text must be obtained from the issuing body._"
    )
    out.append("")
    return "\n".join(out)


def render_index_md(processes: list[Process]) -> str:
    out = ["# RACI library — index", ""]
    out.append(f"{len(processes)} processes, {sum(len(p.rows) for p in processes)} activities, {len(ROLES)} roles.")
    out.append("")
    out.append("| Process | Activities | Most accountable role | Data file |")
    out.append("|---------|-----------:|-----------------------|-----------|")
    for p in processes:
        top = Counter(r for row in p.rows for r in ROLES if row[r] == "A").most_common(1)
        top_role = f"{top[0][0]} ({top[0][1]})" if top else "—"
        out.append(f"| [{p.title}]({p.slug}.md) | {len(p.rows)} | {top_role} | `data/{p.slug}.csv` |")
    out.append("")
    out.append("## Accountability heat map")
    out.append("")
    out.append("Number of activities where each role holds the **A**. A column that is almost empty is a role you may not need; a row where the A sits with one role for everything is worth a second look.")
    out.append("")
    short = [r.replace(" & ", " and ") for r in ROLES]
    out.append("| Process | " + " | ".join(short) + " |")
    out.append("|---------|" + "|".join("---:" for _ in ROLES) + "|")
    totals = Counter()
    for p in processes:
        counts = [p.count(r, "A") for r in ROLES]
        for r, c in zip(ROLES, counts):
            totals[r] += c
        out.append(f"| {p.title} | " + " | ".join(str(c) if c else "·" for c in counts) + " |")
    out.append("| **Total** | " + " | ".join(f"**{totals[r]}**" for r in ROLES) + " |")
    out.append("")
    out.append("## Responsibility heat map")
    out.append("")
    out.append("Number of activities where each role holds an **R**. Use it to see which teams carry the operational load of a process.")
    out.append("")
    out.append("| Process | " + " | ".join(short) + " |")
    out.append("|---------|" + "|".join("---:" for _ in ROLES) + "|")
    for p in processes:
        counts = [p.count(r, "R") for r in ROLES]
        out.append(f"| {p.title} | " + " | ".join(str(c) if c else "·" for c in counts) + " |")
    out.append("")
    out.append("See [role-definitions.md](role-definitions.md) for what each role means and [how-to-adapt.md](how-to-adapt.md) before changing anything.")
    out.append("")
    out.append("_Generated by `scripts/build_library.py`._")
    out.append("")
    return "\n".join(out)


# --- Excel ------------------------------------------------------------------------


def build_xlsx(processes: list[Process], path: Path) -> None:
    from openpyxl import Workbook
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.worksheet.hyperlink import Hyperlink

    navy = "1F3864"
    font = "Arial"
    h_font = Font(name=font, bold=True, color="FFFFFF", size=10)
    h_fill = PatternFill("solid", fgColor=navy)
    body = Font(name=font, size=10)
    bold = Font(name=font, size=10, bold=True)
    title_font = Font(name=font, size=14, bold=True, color=navy)
    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    wrap = Alignment(wrap_text=True, vertical="top")
    center = Alignment(horizontal="center", vertical="top")
    fills = {
        "A": PatternFill("solid", fgColor="F8CBAD"),
        "R": PatternFill("solid", fgColor="BDD7EE"),
        "C": PatternFill("solid", fgColor="FFF2CC"),
        "I": PatternFill("solid", fgColor="EDEDED"),
    }
    ok_fill = PatternFill("solid", fgColor="C6EFCE")
    bad_fill = PatternFill("solid", fgColor="FFC7CE")

    def header(ws, row: int, labels: list[str]) -> None:
        for col, label in enumerate(labels, start=1):
            c = ws.cell(row=row, column=col, value=label)
            c.font, c.fill, c.border = h_font, h_fill, border
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.row_dimensions[row].height = 42

    wb = Workbook()
    wb.properties.creator = "build_library.py"
    wb.properties.lastModifiedBy = "build_library.py"
    wb.properties.created = datetime(*STAMP)
    wb.properties.modified = datetime(*STAMP)

    # Index sheet
    ws = wb.active
    ws.title = "Index"
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Cybersecurity RACI library"
    ws["A1"].font = title_font
    ws["A2"] = "R responsible · A accountable (exactly one per activity) · C consulted · I informed. Each sheet validates its own rows in the Check column."
    ws["A2"].font = Font(name=font, size=9, italic=True, color="595959")
    header(ws, 4, ["Process", "Activities", "Summary"] + list(ROLES))
    ws.cell(row=3, column=4, value="Activities where the role is accountable (A)").font = Font(name=font, size=9, italic=True, color="595959")
    for i, p in enumerate(processes, start=5):
        c = ws.cell(row=i, column=1, value=p.title)
        c.hyperlink = Hyperlink(ref=c.coordinate, location=f"'{p.sheet_name}'!A1", display=p.title)
        c.font = Font(name=font, size=10, color="0563C1", underline="single")
        c.border, c.alignment = border, wrap
        n = ws.cell(row=i, column=2, value=len(p.rows))
        n.font, n.border, n.alignment = body, border, center
        s = ws.cell(row=i, column=3, value=p.summary)
        s.font, s.border, s.alignment = body, border, wrap
        for j, role in enumerate(ROLES, start=4):
            v = ws.cell(row=i, column=j, value=p.count(role, "A") or None)
            v.font, v.border, v.alignment = body, border, center
    ws.column_dimensions["A"].width = 32
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 70
    for j in range(4, 4 + len(ROLES)):
        ws.column_dimensions[get_column_letter(j)].width = 11
    ws.freeze_panes = "B5"

    # One sheet per process
    first_role_col = 3
    last_role_col = first_role_col + len(ROLES) - 1
    a_col = last_role_col + 1
    r_col = a_col + 1
    check_col = r_col + 1
    for p in processes:
        ws = wb.create_sheet(p.sheet_name)
        ws.sheet_view.showGridLines = False
        ws["A1"] = f"{p.title} — RACI"
        ws["A1"].font = title_font
        ws["A2"] = p.summary
        ws["A2"].font = Font(name=font, size=9, italic=True, color="595959")
        header(ws, 4, ["Activity", "Reference", *ROLES, "A count", "R count", "Check"])
        first = 5
        last = first + len(p.rows) - 1
        for i, row in enumerate(p.rows, start=first):
            a = ws.cell(row=i, column=1, value=row["activity"])
            a.font, a.border, a.alignment = body, border, wrap
            r = ws.cell(row=i, column=2, value=row["reference"])
            r.font, r.border, r.alignment = Font(name=font, size=9, color="595959"), border, wrap
            for j, role in enumerate(ROLES, start=first_role_col):
                c = ws.cell(row=i, column=j, value=row[role] or None)
                c.font, c.border, c.alignment = bold, border, center
            rng = f"{get_column_letter(first_role_col)}{i}:{get_column_letter(last_role_col)}{i}"
            ca = ws.cell(row=i, column=a_col, value=f'=COUNTIF({rng},"A")')
            cr = ws.cell(row=i, column=r_col, value=f'=COUNTIF({rng},"R")')
            cc = ws.cell(
                row=i,
                column=check_col,
                value=f'=IF(AND({get_column_letter(a_col)}{i}=1,{get_column_letter(r_col)}{i}>=1),"OK","CHECK")',
            )
            for c in (ca, cr, cc):
                c.font, c.border, c.alignment = body, border, center
        ws.column_dimensions["A"].width = 58
        ws.column_dimensions["B"].width = 34
        for j in range(first_role_col, last_role_col + 1):
            ws.column_dimensions[get_column_letter(j)].width = 11
        for j in (a_col, r_col, check_col):
            ws.column_dimensions[get_column_letter(j)].width = 9
        ws.freeze_panes = ws.cell(row=first, column=first_role_col)
        ws.auto_filter.ref = f"A4:{get_column_letter(check_col)}{last}"

        role_rng = f"{get_column_letter(first_role_col)}{first}:{get_column_letter(last_role_col)}{last}"
        dv = DataValidation(type="list", formula1='"R,A,C,I"', allow_blank=True, showErrorMessage=True,
                            errorTitle="RACI value", error="Use R, A, C, I or leave the cell empty.")
        ws.add_data_validation(dv)
        dv.add(role_rng)
        for value, fill in fills.items():
            ws.conditional_formatting.add(role_rng, CellIsRule(operator="equal", formula=[f'"{value}"'], fill=fill))
        chk = f"{get_column_letter(check_col)}{first}:{get_column_letter(check_col)}{last}"
        ws.conditional_formatting.add(chk, CellIsRule(operator="equal", formula=['"OK"'], fill=ok_fill))
        ws.conditional_formatting.add(chk, CellIsRule(operator="equal", formula=['"CHECK"'], fill=bad_fill, font=Font(name=font, bold=True, color="9C0006")))
        acnt = f"{get_column_letter(a_col)}{first}:{get_column_letter(a_col)}{last}"
        ws.conditional_formatting.add(acnt, CellIsRule(operator="notEqual", formula=["1"], fill=bad_fill))

    # Roles sheet
    ws = wb.create_sheet("Roles")
    ws.sheet_view.showGridLines = False
    ws["A1"] = "Roles used in every matrix"
    ws["A1"].font = title_font
    header(ws, 3, ["Role", "Typical title(s)", "In this library the role is accountable for…"])
    for i, (role, titles, owns) in enumerate(ROLE_NOTES, start=4):
        for j, v in enumerate((role, titles, owns), start=1):
            c = ws.cell(row=i, column=j, value=v)
            c.font = bold if j == 1 else body
            c.border, c.alignment = border, wrap
    ws.column_dimensions["A"].width = 22
    ws.column_dimensions["B"].width = 40
    ws.column_dimensions["C"].width = 80

    buffer = io.BytesIO()
    wb.save(buffer)
    rezip_fixed(buffer.getvalue(), path)


ROLE_NOTES: tuple[tuple[str, str, str], ...] = (
    ("Top management", "CEO, executive committee, board risk or audit committee", "Approving policies, plans and budgets; accepting high residual risk; owning independent review"),
    ("CISO", "CISO, head of information security, ISMS lead", "Security outcomes: policies, programmes, risk decisions below the executive threshold, reporting to management"),
    ("IT operations", "IT director, infrastructure, service desk, platform and cloud engineering", "Running and changing infrastructure, endpoints, identity platforms, backups and the CMDB"),
    ("Security operations", "SOC, detection engineering, vulnerability management, security engineering", "Detecting, triaging, scanning, responding; operating security tooling"),
    ("Application owners", "Business or product owner of a system, including AI systems", "Decisions about their system: access, changes, requirements, recovery objectives, AI deployment"),
    ("HR", "Human resources, people operations", "Joiner/mover/leaver data, training delivery, disciplinary process, acknowledgements"),
    ("Legal & compliance", "Legal counsel, DPO, compliance officer", "Legal and regulatory requirements, contracts, notifications, retention and legal holds"),
    ("Procurement", "Purchasing, vendor management", "Supplier inventory, contract execution, supplier assessment logistics, offboarding"),
    ("Internal audit", "Internal audit, second-line assurance", "Independent review only; consulted or informed everywhere else to preserve independence"),
    ("Data & AI teams", "Data engineering, data science, ML engineering, AI product teams", "Data pipelines, models, training data, AI monitoring; shares R with application owners for AI systems"),
)


def rezip_fixed(blob: bytes, path: Path) -> None:
    """Rewrite the workbook zip with fixed entry timestamps and a pinned dcterms:modified."""
    src = zipfile.ZipFile(io.BytesIO(blob))
    iso = "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}Z".format(*STAMP).encode()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for info in sorted(src.infolist(), key=lambda i: i.filename):
            data = src.read(info.filename)
            if info.filename == "docProps/core.xml":
                data = re.sub(rb"(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)", lambda m: m.group(1) + iso + m.group(2), data)
            entry = zipfile.ZipInfo(info.filename, date_time=STAMP)
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = info.external_attr
            dst.writestr(entry, data)


# --- Main -------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the RACI CSVs and build docs/ and RACI-Library.xlsx")
    parser.add_argument("--check", action="store_true", help="validate only; write nothing")
    parser.add_argument("--no-xlsx", action="store_true", help="write the Markdown but skip the workbook")
    args = parser.parse_args(argv)

    processes = load_manifest()
    errors, warnings = validate(processes)
    for w in warnings:
        print(f"warning: {w}")
    if errors:
        print(f"error: {len(errors)} problem(s) found:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    n_rows = sum(len(p.rows) for p in processes)
    print(f"validated {len(processes)} processes, {n_rows} activities: one A and at least one R per row")
    if args.check:
        return 0

    DOCS.mkdir(exist_ok=True)
    for p in processes:
        (DOCS / f"{p.slug}.md").write_text(render_process_md(p), encoding="utf-8", newline="\n")
    (DOCS / "index.md").write_text(render_index_md(processes), encoding="utf-8", newline="\n")
    print(f"wrote docs/index.md and {len(processes)} process pages")
    if not args.no_xlsx:
        build_xlsx(processes, XLSX)
        print(f"wrote {XLSX.name} ({len(processes) + 2} sheets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
