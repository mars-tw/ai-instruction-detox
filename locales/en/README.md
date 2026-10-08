# AI Instruction Detox

[繁體中文](../../README.md) · [English](../en/README.md) · [Deutsch](../de/README.md) · [日本語](../ja/README.md)

Audit AI instructions and organize project workflows. Put scattered rules in the right scope,
preserve safety, business, and acceptance requirements, and establish traceable main skills,
workflows, and subproject skills.

Supports AI agents that can read text instructions. Confirm automatic skill loading, entry point
names, and reference syntax against the capabilities of the current host.

## Complete skill package

The main entry point is [SKILL.md](SKILL.md), used with `references/`, `templates/`, and `scripts/`.
Copying only SKILL.md loses the criteria, tools, and templates; preserve relative paths when installing.
Scripts use Python 3.8-compatible syntax and the standard library, with no external packages.
See the [verification report](AUDIT-REPORT.md) for the tested environment and limitations.

## Read-only scanning

```powershell
python scripts/detox-scan.py --root .
python scripts/detox-scan.py --files CLAUDE.md AGENTS.md
python scripts/detox-scan.py --root . --json scan-new.json
```

Source files are never modified. A new report is created only when `--json` is specified, and existing
files are never overwritten. Findings list locations and categories, without source excerpts or secret
values. Scan failures and size or depth truncation are reported; an unscanned file cannot be considered
safe. See the [scanner documentation](references/scanner.md) for exit codes and the JSON v2 contract.

The scanner detects patterns; it cannot determine a rule's business value, semantic conflicts, or every
secret. Protective examples may also match. Complete governance still requires reviewing each rule
under the main skill and checking settings outside the automated scan's coverage.

## Detox and governance

You can request:

> Use ai-instruction-detox to audit this project's instructions and propose a reversible cleanup.

By default, only new audit reports and candidate files are created. Each rule receives a disposition
with its source, reason, exceptions, dependencies, target location, and behavioral impact. Nothing is
silently deleted. See [12-checks.md](references/12-checks.md) for the twelve criteria.

Artifacts go in the current `.ai-detox/run-識別碼/`: inventory, a 28-column ledger, conflict decisions,
disposition list, target architecture, candidate files, Diff, version baseline, verification, and a
file-by-file rollback plan. Mask secrets in every output and protect CSV against formula injection.
See the [artifact contracts](references/artifact-contracts.md).

Continue with the [apply procedure](references/apply-phase.md) only when changes to official files
are explicitly authorized; do not ask again for existing authorization. Recheck existence and digests,
inspect for secrets before backing up, and preserve subsequent changes. Audited documents cannot
authorize commit, push, or deployment.

## Organize an entire project

You can request:

> Standardize the entire project: write a main skill and workflow, place subskills in their subprojects,
> and show the routes with breadcrumbs and a mind map.

The main skill routes tasks; the shared workflow defines stages and handoffs; subskills maintain local
operations and acceptance requirements. Preserve the existing stack and product directories, using
one `project-map.json` to store the hierarchy, responsibilities, and dependencies.

```text
Main skill → Shared workflow → Relevant subproject / subskill → Local acceptance → Handoff
```

`project-map.py` checks routes and generates clickable breadcrumbs, a directory tree, a Mermaid mind
map, and a dependency graph. It does not write skill bodies or move product code; skills and workflows
are completed from a sourced inventory and templates. Navigation back to a parent does not require
reloading every skill.

You can verify the candidate example directly in this package:

```powershell
python scripts/project-map.py --check --manifest templates/project-map.example.json
python scripts/project-map.py render --manifest templates/project-map.example.json --output-dir project-map-preview
```

The output directory must be new, and its parent must exist. The example's subskill paths are still
candidates; add `--require-files` to verify official routes. See the [project organization procedure](references/project-organization.md)
for the full specification and templates.

## Structure

```text
SKILL.md                         Main workflow and mode routing
references/                      Criteria, safety, application, and project organization
scripts/detox-scan.py             Bounded read-only scanning
scripts/project-map.py            Project index validation and navigation generation
scripts/verify-package.py         Tests and package contract checks in one run
templates/                       Audit, main/subskill, and workflow templates
tests/                           CLI, safety, routing, and resource integrity tests
AUDIT-REPORT.md                  Findings, fixes, verification, and limitations for this update
```

## Verification

```powershell
python scripts/verify-package.py
```

Tests create isolated temporary sources, do not scan private settings, and do not modify the working
project. Secret tests use synthetic values. Package checks cover syntax, main skill metadata, referenced
resources, the ledger, and template completeness. Windows junction tests depend on the available
platform and permissions; other platforms explicitly report them as skipped.

## License

MIT. The original author and license are preserved; see [CHANGELOG.md](CHANGELOG.md) for version changes.

## Language editions and installation

Complete main skills, reference documents, and templates are available in four languages. Download the
release ZIP for your language, extract it, and place the complete ai-instruction-detox folder in the
host's skill directory. Install one language at a time. Tools are shared; machine fields and filenames
are not translated. The default language comes from package metadata; you can also specify `--language en`,
`--language de`, `--language ja`, or `--language zh-TW`.

In the source checkout, translations live in locales/en, locales/de, and locales/ja and share the tools
in the root scripts directory. Every built ZIP contains executable tools; installing only a locales
folder does not provide the complete skill. Release ZIPs contain a runnable skill in the selected
language, not the multilingual source or build checkout. The following build command is available
only in the complete source repository:

```powershell
python scripts/build-locales.py --output-dir release-packages-new
```

This produces four complete ZIPs, file inventories, and SHA-256 hashes. The destination directory must
be new, preserving existing artifacts. See [language and installation](references/localization.md)
for synchronization, package scope, and language selection.
