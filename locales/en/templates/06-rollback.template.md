# 06 — Rollback Methods

## Current mode

Record whether only candidates were produced or changes were applied. With candidates only, official
files need no restoration; preserve audit evidence. Do not assume everything under .ai-detox was
created in this run or delete existing reports in bulk.

## Preconditions for file-by-file operations

| Path | Action | Originally existed | Baseline SHA-256 | Applied SHA-256 | Safe backup | Rollback method |
|---|---|---|---|---|---|---|

Compare with baseline-manifest.json. Check current digests before rollback. If they differ from the
applied version, preserve subsequent changes and use a three-way comparison or mark pending confirmation.
Do not overwrite directly with an old backup.

## Rollback by action

- UPDATE: Safely restore backups and read back original digests.
- CREATE: Recover only files created in this run that have not changed again; ensure no automatic loading entry remains.
- MOVE/ARCHIVE: Check both ends, restore source and references, and recover this run's destination copy.
- Not applied: No official file rollback needed; record candidate locations only.

Fill each item with verified actual paths and commands for the applicable platform; do not provide
bulk reset/clean or recursive deletion. On Windows use LiteralPath, verifying absolute paths stay
inside the approved scope first; do not operate on sources through links.

## Rollback verification

Record verification commands, exit codes, and read-back results for references, main/subskill routing,
workflows, and the project index. Identify entry settings requiring a new session, and update the
manifest to ROLLED_BACK.
