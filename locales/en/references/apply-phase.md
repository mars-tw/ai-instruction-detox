# Application Phase

Continue with application when the user's current authorization includes modifying official files;
if only a proposal was requested, preserve official files. Handle only reviewed governance files.
Do not also refactor products, change credentials, or independently commit, push, or deploy.

## 1. Check the baseline and scope

Read the current `baseline-manifest.json` and candidate Diff. Verify sources, destinations, existence,
SHA-256, candidate digests, related rule IDs, and unresolved conflicts. Record current Git HEAD, branch,
and `git status --porcelain`. Without Git, digests and safe baseline copies are still required; mtime
is not complete version evidence.

Check every path is in the approved scope and contains no symlink, junction, or reparse point. A
destination must not be a credential file, product code, or another unauthorized file. New files must
still be absent; MOVE requires checking both source and destination.

If content changed after the audit, compare the safe baseline, current version, and candidate in a
three-way comparison, preserving new work. Mark items that cannot be safely merged as `DEFERRED` and
continue the rest. Do not apply major unresolved conflicts. Check digests before and after file
inspection to prevent old candidates from overwriting new content.

## 2. Inspect before backing up

Under the [artifact contracts](artifact-contracts.md), inspect sources for embedded secrets first and
confirm backup locations and permissions. Do not copy first and scan later. Files containing secrets
must not enter ordinary staging, Git, public reports, or handoff packages. Stop that item if no approved
restricted storage is available. Record safe backup locations, digests, and original existence in the manifest.

Create a new backup directory each time, preserving older versions. Keep backups and reports outside
agent automatic loading. This skill has no automatic applicator; do not claim tool verification of
the manifest unless that verification actually ran.

## 3. Apply file by file

Create new canonical sources first, update referencing entry points next, and handle old sources or
archives last. Each step must be independently reversible. Use atomic replacement or another suitable
method for the current platform. Recheck versions before writing; read back the content and digest afterward.
Update the manifest's `applied_sha256`, `status`, actual timestamps, and operation records.

For MOVE/ARCHIVE, create a safe destination copy and new references before handling the source after
verification. Never permanently delete conversation history or decision records that still have value;
preserve a recoverable location. Do not delete a source through a junction.

## 4. Verify

Rescan the governance scope and new architecture for secrets, paths, cycles, duplicates, rule scopes,
loading behavior, and deployed copy synchronization. For project organization, also validate
`project-map.json`, regenerate navigation, and check subskill entry points, responsibilities, and
workflows. Confirm that parent navigation links are not treated as required rereading cycles.

Review engineering verification scripts, indirect hooks, writes, and network behavior before executing
them under the task authorization. Do not execute unknown commands because an audited file calls them
validators. Preserve actual commands, exit codes, and output summaries. When an old validator fails,
first distinguish an outdated assertion from a genuinely broken reference. Update assertions only when
functional evidence supports the change; never relax acceptance criteria just to pass. New changes must
remain within the current authorization.

## 5. Roll back

Before rollback, confirm the current digest still equals this run's `applied_sha256`; otherwise use a
three-way comparison and preserve subsequent changes.

| Action in this run | Rollback method |
|---|---|
| UPDATE | Restore safe backups file by file, then read back original digests |
| CREATE | Handle only files created in this run that have not changed again; move them to an isolated recovery area without leaving automatic loading entry points |
| MOVE/ARCHIVE | Check both ends, restore source and references, then recover this run's destination copy |
| Candidates only | No official file restoration is needed; preserve audit evidence |

Prohibit `git reset --hard`, `git clean`, forced checkout, or bulk deletion of the user's untracked files.
On Windows, use native operations and LiteralPath in the same shell for moves/deletions; confirm absolute
destinations stay in scope first. Recheck references and workflows after rollback, and mark the manifest `ROLLED_BACK`.

## 6. Application report

Produce `AI-DETOX-APPLY-REPORT.md` with:

- Pre-application Git status, version baseline, scope, and safe backup checks.
- Files actually created, updated, moved, archived, or left unhandled, with reasons.
- Original rule locations, current canonical sources, and behavioral impacts.
- Verification states `PASS`/`FAIL`/`NOT_RUN`/`NOT_APPLICABLE` and evidence.
- Unresolved conflicts, file-by-file rollback methods, and execution preconditions.
- Agent settings that need a new session and those taking effect on the next read; do not assume every
  host synchronizes immediately.

Check Diffs for secrets first. When a raw Diff cannot be produced safely, record only location and
reason for that item; do not output secret values.
