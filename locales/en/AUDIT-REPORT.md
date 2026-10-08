# AI Instruction Detox 1.1.0 Update Verification

Date: 2026-10-08 (Asia/Taipei). Original source:
[mars-tw/ai-instruction-detox](https://github.com/mars-tw/ai-instruction-detox).
Baseline commit: `0b4ce515f209f3fb5cf82522d904f15999b69a1d`.

The local skill package was updated: scanner and governance contracts were corrected, and project-wide
standardization was added. Complete checks and regression tests passed; heuristic scanning and limited
simulations are not comprehensive safety guarantees. No commit, push, or deployment occurred during
the 1.1.0 baseline audit; the subsequent 1.2.0 was published to GitHub under explicit user authorization.
The original author and MIT license are preserved.

## Corrected issues

Locations below refer to line numbers in the original baseline commit; updated files have been rearranged.

| ID / severity | Original evidence | Issue and impact | Fix |
|---|---|---|---|
| S01 / HIGH | `scripts/detox-scan.py:157–159,166,174,194` | Injection, vague rule, absolute term, and duplicate block findings included raw excerpts, potentially sending secrets on the same line to stdout/JSON | Findings now contain locations/categories; all fields and path metadata prevent detected secrets from escaping |
| S02 / HIGH | `scripts/detox-scan.py:86–97` | Symlinks, Windows junctions, and sensitive directories were not isolated; explicit inputs could also read through links | lstat/reparse checks for every ancestor; exclusions for sensitive directories, files, and source/output locations |
| S03 / MEDIUM | `scripts/detox-scan.py:100–105` | Read failures became empty text, allowing missing/truncated coverage to appear successful | Separate selected/scanned counts, retain errors/skipped, return 3 for partial scans, add resource limits |
| S04 / MEDIUM | `scripts/detox-scan.py:177–183` | Only mutual two-node references were found; long cycles and self-references were missed | Nonrecursive strongly connected components; a 1,200-node cycle was checked without call-stack overflow |
| S05 / MEDIUM | `scripts/detox-scan.py:74–78,134–144` | Common references paths, Markdown, and paths with spaces were missed; parsing and scope were unclear | Distinguish URLs, anchors, and local paths; check only selected scope without expanding content reads through references |
| S06 / MEDIUM | `scripts/detox-scan.py:191` | Duplicate identity used the first 200 characters, merging distinct rules with identical openings | Compare whole normalized paragraphs; report source locations without paragraph output |
| S07 / HIGH | `scripts/detox-scan.py:266–268` | JSON used w and could overwrite sources or existing reports | Exclusive create, destination/ancestor checks, rejection of overwrites and sensitive destination files; mutually exclusive CLI modes |
| G01 / HIGH | `SKILL.md:93` | The ledger required source text without protecting embedded secrets; CSV could execute formulas | Unified masking contract for derived output, CSV formula protection, and JSON exchange guidance |
| G02 / HIGH | `references/apply-phase.md:45–59,85` | Secret checks happened after backup, and audited project scripts could be blindly executed | Inspect before backup; defer items without safe storage; review scripts/hooks before execution under task authorization |
| G03 / HIGH | `references/apply-phase.md:26–30`, `templates/06-rollback.template.md:16` | No baseline snapshot contract; rollback could overwrite later changes and did not handle CREATE/MOVE | Add existence, SHA-256, candidate/applied digests, per-item three-way comparison, recovery of new files, and restoration of moves |
| G04 / MEDIUM | `SKILL.md:93–94,189–201` | Ledger lacked strength, exceptions, and dependencies; templates 02–05 were missing | Retain the original 25 columns and append three; complete 00–06 and baseline templates |
| G05 / MEDIUM | `README.md:38,99`, `SKILL.md` frontmatter | Providing only the main file lost dependencies; "zero writes" contradicted report writes; metadata was incompatible with the current validator | Explain complete package usage, separate read-only sources from artifact writes, move version/author under metadata |
| G06 / MEDIUM | `references/12-checks.md:23,215–218`, `references/multi-agent-review.md:85` | Honesty was treated as a platform guarantee, scheduling as universally impossible, and canonical divergence across sessions was missed | Assess capabilities through official/test evidence, separate navigation/loading, and check cross-agent copies for version divergence |

Safety work used [Python file traversal specifications](https://docs.python.org/3.8/library/os.html#os.walk),
[Windows reparse attributes](https://docs.python.org/3.12/library/stat.html#stat.FILE_ATTRIBUTE_REPARSE_POINT),
and [OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection) as technical references.
This project is a standard library CLI; unrelated Web framework checklists were not applied.

## Added: project-wide standardization

The main skill adds `ORGANIZE_PROJECT` routing. See [project-organization.md](references/project-organization.md)
for the detailed procedure.

1. Inventory main projects/subprojects from existing responsibilities, paths, working documents, and acceptance sources.
2. Create a main skill and shared workflow, with subskills and local workflows inside their subprojects.
3. Use one `project-map.json` for nodes, hierarchy, skills, workflows, owners, sources, and dependencies.
4. After validation, `project-map.py` produces breadcrumb Markdown, a directory tree, a Mermaid mind map,
   and a dependency graph.
5. Review candidates in an isolated run and strictly verify routes after official application, without
   moving product code.

The tool rejects invalid schemas/types, duplicate IDs/paths, unknown parents/dependencies, out-of-scope
paths, sensitive locations, links, and dependency cycles. All navigation comes from one index; back
links do not require repeated loading. Main/subskill and workflow templates include inputs, outputs,
responsibilities, acceptance, stopping, handoff, and rollback requirements.

## Actual verification

Environment: Windows, Python 3.12.10, Git 2.53.0.windows.3.

| Verification | Result | Evidence |
|---|---|---|
| `python -W error scripts/verify-package.py` | PASS | 80 tests, 0 failures, 0 skipped |
| Scanner | PASS | 38 tests, including secret output, real symlinks/Windows junctions, CLI, coverage errors, and long cycles |
| Project map | PASS | 39 tests, including a three-level fixture, strict routes, read-only behavior, no overwriting, escaping, and invalid input |
| Package contracts | PASS | 3 tests, including all main skill/reference resource links, template completeness, and 28-column migration |
| Python 3.8 grammar | PASS | ast.parse compatibility checks on scripts/tests; not an actual Python 3.8 runtime execution |
| Official local skill-creator quick_validate | PASS | `Skill is valid!`; compatible frontmatter and main entry |
| `git diff --check` | PASS | No whitespace errors; Git LF/CRLF notices do not affect this result |
| Independent forward verification | PASS (candidate governance) | Frontend/backend fixture produced complete main/subskills, workflows, 28-column ledger, 00–06, baseline, and patch |
| Forward verification source preservation | PASS | Digests and Git status unchanged for 11 source files; two existing uncommitted product changes preserved |
| Candidate routing and navigation | PASS | Isolated overlay passed strict validation; four navigation files rebuilt twice byte-identically; Markdown links resolved |
| Candidate patch | PASS | `git apply --check` passed in an isolated fixture; not actually applied |
| Real product tests / official application / rollback | NOT_RUN | This update changed the skill package; no other user product project was governed or modified |

Implementation, document review, and forward evaluation used independent agent contexts built into
the host, with bounded scopes. The supervisor then read back results and performed actual verification.
This is not different-model verification. No external model round trip was used as verification
evidence for this audit.

## Cross-review fixes in the new module

- Mermaid ID end collided with [official reserved syntax](https://mermaid.js.org/syntax/flowchart.html).
  A safe node_ prefix was added, preserving manifest IDs and navigation anchors.
- Added .envrc and credentials.* exclusions; source, manifest, root, and output paths use the same restrictions.
- Markdown navigation directly includes the same-source directory tree, mind map, and dependency graph;
  users need not locate separate .mmd files to view diagrams.

## Compatibility and limitations

- JSON schema v2 removes raw snippet/text/ref; cycle and duplicate fields also become location structures.
  Consumers must update.
- Ledger expands from 25 to 28 columns. Existing files can add `strength`, `exceptions`, and `dependencies`;
  do not invent exceptions.
- Secret/injection detection and path parsing are heuristic and cannot cover every format; interpret matches in context.
- `complete` means reading finished within the selected scope, not a complete project inventory or proof of safety.
- The navigation tool does not create skill bodies or verify actual owners, business completeness, or unknown secrets in manifests.
- Other Python versions/operating systems, real novice use, governance application, and rollback have not
  been executed; they are not marked passed.
- Path checks are not an operating system sandbox and cannot guarantee protection against malicious
  processes concurrently replacing ancestor directories.

## Traditional Chinese wording change record

| Original sentence / practice | Reason | Replacement |
|---|---|---|
| Zero writes during auditing | Contradicts creation of reports/candidates | Auditing preserves sources; only specified modes write new isolated artifacts |
| Give SKILL.md to an AI agent | Omits referenced criteria and scripts | Preserve the complete skill package and relative paths |
| Answer honestly → platform already guarantees it → deletable | Treats a policy expectation as an executable behavior guarantee | Keep category B when guarantee evidence is absent |
| Duplicate only if loaded together in one session | Misses canonical rule divergence across agents | Assess scope and canonical sources; check cross-session copies too |

Other principal changes are technical contracts and new capabilities. The original author, dates,
license, and English identifiers are preserved.
