# 00 — Scan Scope and File Inventory

Generated at: <DATE>
Mode: `MODE = AUDIT_AND_DRAFT` / `ORIGINAL_FILES_WRITE = DENIED` / `DEPLOYMENT = DENIED` / `GIT_COMMIT = DENIED`

## 1. Identify the environment

| Item | Observed result |
|---|---|
| Executing agent | <Claude Code / Codex / …> |
| Working directory | <path> |
| Git repository | <yes/no; if no, describe the levels containing instruction files> |
| Other agent entry points | <list those that actually exist> |

## 2. Git status (do not touch uncommitted changes)

| Project | branch | Uncommitted changes |
|---|---|---:|

## 3. Scan scope

Use an explicit allowlist; no recursive scan of the entire home directory.
Skipped: `.git` / `node_modules` / `vendor` / `dist` / `build` / `cache` / binaries / model files /
credential directory contents (existence recorded only).

## 4. File inventory

### A. User-level agent entry files (automatically loaded)

| Path | Lines | Size | Role | Loading trigger |
|---|---:|---:|---|---|

### B. Project-level instruction files

| Path | Lines | Size | Role | Risk |
|---|---:|---:|---|---|

### C. Settings files
### D. Skills / Agents / Automations
### E. Memories / context

## 5. Inaccessible / out of scope

- Platform-level System/Developer prompts: **inaccessible, outside this audit, and not claimed to have been read**.
- <credential file>: record only existence; output no values.

## 6. Loading relationships and known structural risks

```
<draw a graph of who loads whom>
```

**Verified structural problems**:
1.

## 7. Version baselines and artifact isolation

| Governance path | Originally existed | SHA-256 | Safe baseline location | Destination / candidate digest | LinkType | Loading / tracking status |
|---|---|---|---|---|---|---|

Record every item in baseline-manifest.json. Check for secrets before backing up; do not excerpt
secrets into this table. Record the current new artifact directory, existing artifacts, and scan gaps
such as depth/size limits.

## 8. Project organization scope

| Module / subproject | Responsibility / sources | Existing path | Main / subskill | Workflow | Dependencies | Reason unclassified |
|---|---|---|---|---|---|---|
