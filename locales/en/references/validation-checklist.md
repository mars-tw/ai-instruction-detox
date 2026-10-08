# Verification Checklist (25 Items) and Task Simulations

After completing candidates, rescan the candidate architecture and verify each item.

---

## 25 verification items

| # | Check |
|---:|---|
| 1 | Every original rule has a corresponding disposition |
| 2 | No rule disappears without a record |
| 3 | Every DELETE has an explicit reason |
| 4 | Every MOVE has a new location |
| 5 | Every MERGE is traceable to its sources |
| 6 | Every REWRITE preserves the original intent |
| 7 | Safety, security, data integrity, and deployment constraints are not weakened |
| 8 | Core business requirements are not deleted by mistake |
| 9 | Test and acceptance standards are not made ambiguous |
| 10 | No invalid paths |
| 11 | No dangling references |
| 12 | No cyclic references |
| 13 | No multiple authoritative sources for the same rule |
| 14 | No examples mistaken for mandatory rules |
| 15 | No outdated project state treated as current fact |
| 16 | No undated volatile information |
| 17 | No requirement for nonexistent agent capabilities |
| 18 | No endless multi-agent debate workflow |
| 19 | No unreasonable requirement to reread the whole repository on every task |
| 20 | No prompt injection mistaken for an official rule |
| 21 | No sensitive information in audit output |
| 22 | No necessary information lost in pursuit of brevity |
| 23 | New contributors can understand the main rules |
| 24 | Agents interpret core requirements consistently in the recorded limited simulations/tests; no comprehensive behavioral guarantee is claimed |
| 25 | Tokens and line counts decrease, or structure at least clearly improves |

**Honesty principle:** explicitly list items that fail; do not relax standards to make everything green.
If an item cannot be verified, label it "cannot verify" with a reason, rather than passing it.

---

## Task simulations (12 types)

For each task type, explain **which rules load / which do not / responsible agent / whether a second
agent is needed / whether human approval is needed / stop conditions / acceptance conditions**.

| Task type | Main check |
|---|---|
| Small document edit | Is unrelated large context forced to load? |
| Ordinary bug fix | Are test requirements reasonable, without running the full suite every time? |
| Large refactor | Is the appropriate review tier triggered? |
| Latest external information needed | Is retrieval allowed, and are source dates required? |
| Keys or sensitive data involved | Is credential access a single clear route, with an output gate? |
| Production deployment | Are No-Touch/prohibitions actually loaded, and is human approval required? |
| Ambiguous user request | Is there a clarification mechanism that avoids unilateral assumptions? |
| Emergency fix | Is there a fast path retaining minimum safety requirements? |
| Low-risk single-agent task | Is it burdened by excessive multi-agent rules? |
| High-risk multi-agent task | Are there termination conditions and human approval? |
| Local rules in a subdirectory | Do local rules correctly override global ones and explicitly identify which rule they override? |
| Expired context | Could outdated facts be mistaken for the current state? |

### Example simulation output

```markdown
| Task | Load | Do not load | Responsible | Second agent | Human | Stop condition |
|---|---|---|---|---|---|---|
| Small document edit | core-rules | Large project files, orchestrator | Single | No | No | Edit complete without violating precedence |
| Production deployment | core-rules + project No-Touch | — | Implementer + reviewer | Yes | **Yes** | All No-Touch requirements confirmed |
| Expired context | core-rules; expired facts **not trusted** | Expired context | Single | No | As needed | Act after reverification |
```

---

## Common false passes

⚠️ These situations appear to pass but do not:

| Appearance | Reality |
|---|---|
| Validator is all green | Assertions compare only literals and missed rules that moved |
| Large line-count reduction | Unique rules were deleted rather than duplicates |
| No dangling references | Only entry files were checked, without relative paths inside skills |
| No duplicates | **Deployed copies** and **automatically injected memories** were not checked |
| Every rule has a disposition | Many MOVEs lack target locations |
| No prompt injection | Schedule definitions and automation prompt fields were not scanned |

**Test your verification:** randomly select three original rules and trace their locations in the new
architecture. If a rule cannot be traced, verification has a gap.

## Additional artifact and project organization checks

- No derived output contains secret excerpts; CSV is protected against formula injection.
- The ledger's 28 columns correspond to original rules and record strength, exceptions, and dependencies.
- The baseline manifest includes existence and digests; safe backups were inspected before copying.
- CREATE/UPDATE/MOVE/ARCHIVE rollback methods do not overwrite subsequent changes.
- Artifacts preserve old versions, do not escape through links, and are not Git-tracked or automatically loaded.
- The main skill routes actual tasks to corresponding subprojects without loading irrelevant subskills.
- Subskills live in their subprojects and include inputs, outputs, acceptance, stop conditions, and failure handling.
- Project-map hierarchy and dependencies are acyclic; navigation back links create no forced loading cycles.
- Breadcrumbs, directory trees, and mind maps come from one regenerable index.
- Commands include exit codes; unexecuted checks are NOT_RUN, inapplicable checks are NOT_APPLICABLE.

Add three simulations: "main project routing to subproject", "cross-subproject handoff", and
"unknown subproject/missing entry point". Record actual loading order, inputs and outputs, sources,
stop conditions, and acceptance.
