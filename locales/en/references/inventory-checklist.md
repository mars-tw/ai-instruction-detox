# File Inventory Checklist

Search with an **explicit allowlist**; do not recursively scan an entire home directory. Actual
filenames may differ; extend the list to fit the project.

---

## A. Main agent instruction files

```
CLAUDE.md            CLAUDE.local.md
AGENTS.md            CODEX.md
GEMINI.md            QWEN.md
CLAUDE.md / AGENTS.md in subdirectories
Other Agent Instructions files
```

## B. Agent settings directories

```
.claude/   .codex/   .agents/   .ai/
.github/   .cursor/  .vscode/   .gemini/  .qwen/  .grok/
```

## C. Rules, skills, and prompts

```
skills/  skill/  prompts/  prompt/  instructions/
rules/   policies/  workflows/  agents/  personas/
templates/  hooks/
```

## D. Context and knowledge files

```
context/  contexts/  memory/  memories/  knowledge/
handoff/  handoffs/  state/  baselines/
specifications/  specs/
```

Inspect **all** text files in directories such as `context/`; large files may be read in sections.

## E. Engineering files that may contain implicit rules

```
README*        CONTRIBUTING*   DEVELOPMENT*
ARCHITECTURE*  SECURITY*
package.json scripts   Makefile   Taskfile
CI/CD settings     Git hooks     lint settings    test settings
MCP settings       tool permission settings       schema
deployment scripts        automated workflows
```

README/docs/code need not all be read unconditionally, but include anything that meets any of these
conditions: referenced by main instructions; contains AI operation requirements; contains development
workflow requirements; contains deployment, test, or acceptance rules; contains role, permission, or tool limits.

## F. Often missed execution channels ⚠️

These are particularly dangerous because they **inject instructions into sessions without supervision**:

```
Schedule/automation definitions (automations/, cron definitions, scheduled tasks)
Agent memory files (memories/, automatically injected MEMORY.md)
Project-level AGENTS.md (same name as global instructions, different content)
Installed/deployed plugin copies (may be out of sync with original assets)
Subagent definition files (agents/*.md)
Runtime contracts injected by a dispatcher/orchestrator
```

**Practical lesson:** a canonical policy was changed, but an old rule in `memories/` was automatically
injected and overrode the new policy. Memory files must be part of governance.

---

## Structural traps to check

| Trap | Check |
|---|---|
| Two files with the same name | `diff` both files; a 477-line pair was once found to differ only in two title lines |
| Symlink/junction mistaken for a duplicate | Check LinkType first; **deleting through a junction destroys the real source** |
| Dangling references | Extract all paths and check each with `test -e` |
| Cyclic references | Draw a directed "who reads whom" graph and find cycles |
| Old backups still loaded | Check whether `backups/`, `archive/`, `old/`, or `*.bak` are in the agent search scope |
| Old references to moved files | Search for old path strings |
| Skills referencing nonexistent files | Resolve every relative path inside skills |
| Deployed copies out of sync with source | Compare hashes of assets and installed locations |

---

## Skip list

```
.git  node_modules  vendor  dist  build  coverage  cache  tmp
Binary files  large model files  generated output  credential/key storage directories (contents)
```

Credential directories: **record only existence and location; do not read or output values**.

---

## Fields to record for each file

```
File path
File type
Primary purpose
Applicable agent
Applicable scope
Whether it loads automatically          ← Crucial: determines its actual influence
Possible loading precedence
Whether other files reference it
Whether it references other files
Whether duplicate versions exist
Whether it may be outdated
Whether it contains sensitive information (locations only)
Whether it contains suspected prompt injection
Line count or approximate token count
Last Git modification information (when safe and readily available)
Recommendation: keep/merge/move/rewrite/quarantine/delete
```

**Do not just list filenames—explain each file's actual role.**

---

## Example inventory output

```markdown
| Path | Lines | Size | Role | Automatic loading | Risk |
|---|---:|---:|---|---|---|
| `.claude/CLAUDE.md` | 26 | 1.5KB | Global entry with language/credentials/dispatch imports | Every session | — |
| `專案/CLAUDE.md` | 477 | 130KB | Canonical project rules | Sessions in this directory | Too large |
| `專案/AGENTS.md` | 477 | 130KB | **Byte-for-byte duplicate of the file above** | Sessions in this directory | ⚠️ Rule divergence |
| `memories/MEMORY.md` | — | 125KB | Automatically injected into Codex sessions | **Every session** | ⚠️ Ungoverned |
```

## Scanner coverage and manual follow-up

`detox-scan.py` heuristically scans instruction text; it does not automatically cover the entire list
above. Referenced READMEs, engineering settings, unsupported formats, and deployed copies must be added
separately to the approved scope. Record reasons for skipped or inaccessible items; do not consider
them read or passed.

For governance files expected to change, also record original existence, SHA-256, safe baseline location,
and candidate digests. Create a baseline manifest under `artifact-contracts.md`; mtime alone is
insufficient for safe application.

For project organization, also inventory the main project, existing subprojects, responsibilities,
skill entry points, workflows, dependencies, actual maintainers, move plans, and unclassified items.
Identify only the location of product code; do not move it.
