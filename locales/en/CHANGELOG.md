# Changelog

## 1.2.0 (2026-10-08)

- Added complete English, German, and Japanese skills, reference documents, templates, and usage instructions.
- All four languages share tool code, machine fields, and safety contracts, with matching versions.
- Scanner and navigation tools support --language; release packages default to their respective languages.
- Added generation, integrity checks, and language consistency verification for each language release package.

## 1.1.0 (2026-10-08)

- Added project-wide standardization: main skill, shared workflow, subproject skills, a single index,
  breadcrumbs, directory trees, and mind maps.
- Added project-map.py route and dependency validation, without overwriting sources or executing manifest content.
- Fixed secret leakage in scan excerpts, detection limited to two-node cycles, false duplicate matches
  from truncated prefixes, swallowed read failures, and JSON overwrites.
- Added sensitive location/symlink/junction isolation, coverage gaps, and resource limits to scanning;
  upgraded JSON to v2.
- Completed audit templates and version baseline/rollback contracts; appended strength, exceptions,
  and dependencies to the ledger, expanding it from 25 to 28 columns.
- Added secret checks before backups, restricted untrusted script execution, and distinguished real
  tests, unexecuted checks, and simulations.
- Moved main skill metadata into the standard metadata field; corrected complete-package usage and
  read-only explanations.
- Added standard library tests and a single package verification entry point.

## 1.0.0 (2026-08-27)

Initial release. The methodology came from a real machine-wide AI instruction governance audit:
461 atomic rules, 88 conflicts, and 6 reorganized entry files.

- Twelve detox checks with full criteria
- Ten disposition categories, without silent deletion
- Separate audit and application phases: auditing preserves source files and permits isolated artifacts
- Read-only `detox-scan.py` scanner, with no external dependencies and secret locations reported without values
- 25 verification checks + 12 task simulations
- Six references: check criteria, inventory checklist, target architecture, multi-agent review, verification, and application
- Six practical lessons: false validator failures, memory overriding policy, deployed copies reversing
  changes, junction misclassification, conversation history cleanup, and state files being written back
