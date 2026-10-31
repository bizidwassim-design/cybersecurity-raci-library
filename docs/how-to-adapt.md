# How to adapt the library

The matrices are a starting point calibrated for a mid-sized organisation with a security function that
reports to the executive, an IT department, named application owners and a data/AI team. Nobody's
organisation looks exactly like that. Here is how to bend the library without breaking it.

## 1. Renaming roles

Role names live in two places: the header row of **every** `data/*.csv` and the `ROLES` tuple at the top of
`scripts/build_library.py`. Change both, keep the order, rebuild. The script refuses a header that does not
match `ROLES` exactly, so a half-done rename cannot slip through.

Typical renames:

| Library role | You might call it |
|--------------|-------------------|
| CISO | Information Security Manager, Head of Cyber, ISMS lead |
| Security operations | SOC, Cyber Defence, MSSP (name the *contract owner* inside your organisation, not the supplier) |
| Application owners | System owners, Product owners, Business owners |
| Data & AI teams | Data platform, Analytics, Machine learning |
| Legal & compliance | Legal, DPO, Risk & compliance |

To **remove** a role, delete its column from every CSV and from `ROLES`. Before you do, open `docs/index.md`:
the accountability heat map shows how many A the role holds. Every one of those rows needs a new A.

To **add** a role, append a column (empty cells are valid) and add it to `ROLES`. Then go through the
matrices and decide where it is R, C or I — adding a column full of blanks is worse than not adding it.

## 2. Merging roles in a small organisation

When one person is CISO *and* IT director *and* runs the SOC, you have two options:

* **Keep the columns, same person in several.** The matrix still documents what *should* be separated when
  the organisation grows, and auditors understand "the IT manager holds all three today". Add a note in the
  README of your copy.
* **Merge the columns.** Combine `CISO` + `Security operations` into `Security`, for instance. Where the two
  columns held A and R on the same row, keep the A: the library never puts A and R on the same function,
  but a merged function is both, and a row with one A and no R is invalid. Put the R on whoever actually
  executes — often `IT operations` or `Application owners` — or accept the merged role as A and mark the
  executing team R.

## 3. Splitting the A across business units

"Application owners" is one column, but you have twelve business units with their own systems. Three
patterns work:

1. **One matrix per business unit.** Copy `data/access-review.csv` to `data/access-review-finance.csv`,
   add a row to `data/processes.csv`, change what differs. Best when the units genuinely run the process
   differently. Cost: duplication.
2. **One column per business unit** for the processes where it matters (access review, change management),
   leaving the generic column for the others. The one-A rule still applies per row, so write one row per
   unit for activities such as "Certify user access — Finance", "Certify user access — Logistics".
3. **Keep the single column and resolve it in a mapping table** outside the RACI: a `system → owner` list
   (your asset inventory). The RACI says "the application owner is A"; the inventory says who that is for
   each system. This is the lightest option and the one the library assumes.

What does not work: two A in one row "because both units own part of it". Split the row instead.

## 4. The A/R convention in this library

The library **never** gives a function both A and R on the same row. The A sits with the function that owns
the *outcome* (usually CISO, Top management, Application owners, IT operations or Legal), the R with the team
that does the *work*. That is why the CISO is accountable for "remediate findings on infrastructure" while
IT operations is responsible: the CISO answers for the SLA, IT does the patching.

If your organisation holds the IT director accountable for patching outcomes, move the A. The build script
only cares that there is exactly one. If you want to allow `A/R` as a value, add it to `VALUES` in the script
and count it as both in the `COUNTIF` formulas of the workbook — a ten-line change.

## 5. Adding a process

1. Create `data/<slug>.csv` with the exact header of the other files.
2. Add a line to `data/processes.csv`: `slug,title,summary`. Keep the title under 32 characters (Excel sheet-name limit).
3. Write the activities as verbs ("Approve…", "Review…", "Run…"), one decision or deliverable per row.
   Ten to sixteen rows is the sweet spot; above twenty you are writing a procedure, not a RACI.
4. Cite the standard identifiers in `reference`.
5. `python scripts/build_library.py --check` until it is clean, then without `--check`, then commit the CSV,
   the generated Markdown and the workbook together.

## 6. Common RACI mistakes (and how the library avoids them)

| Mistake | Why it hurts | Guard |
|---------|-------------|-------|
| No A, or two A, on a row | Nobody answers for it, or two people argue | Validator fails the build; workbook `Check` column turns red |
| A without an R | An outcome everyone owns and nobody delivers | Validator requires at least one R |
| Same function A and R everywhere | The matrix just restates the org chart | Convention in section 4; heat maps in `docs/index.md` make it visible |
| Top management as R | Executives do not run scans | Warning from the build script |
| Internal audit as R on operations | An auditor cannot audit a process it runs | Warning from the build script |
| C on every row | Every activity becomes a committee | Role definitions: "every C is a meeting" |
| I as the default filler | The matrix stops saying anything | Empty cells are valid and encouraged |
| Names instead of roles | Breaks at the first resignation | Columns are functions; map people elsewhere |
| Activities that are nouns | "Vulnerability scanning" is a topic, not a decision | Rows start with a verb and name a deliverable |
| Written once, never reviewed | Drifts from reality within a year | CSV in Git: review it like code, diff it at each management review |
| AI left out | ISO/IEC 42001 asks who owns impact assessment, data and monitoring | Every process has at least one AI row; one full AI lifecycle matrix |

## 7. Using the outputs

* **Workshops.** Print the Markdown table of one process, give every function a highlighter, ask them to mark
  what they *actually* do today. The gaps against the library are your action list.
* **Audits.** Hand the auditor `docs/<process>.md` and the evidence that the A signed off (minutes, tickets).
* **Job descriptions and the ISMS roles clause.** The accountability heat map in `docs/index.md` is a
  ready-made answer to ISO/IEC 27001 clause 5.3 and ISO/IEC 42001 clause 5.3.
* **The workbook.** `RACI-Library.xlsx` is for people who will edit; the `Check` column tells them when they
  broke a rule. Re-import changes into the CSV (or just edit the CSV — it is the source of truth).
