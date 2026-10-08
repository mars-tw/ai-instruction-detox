# Target Architecture: After Cleanup

---

## Four firm principles

### 1. One authoritative source

Every rule has **one** primary authoritative source. Other files may only reference it, adapt it for
an agent, or add genuinely different scopes.

**Do not** copy the same rule into entry files, skills, and context.

### 2. Entry files contain only long-term global rules

Include:

- Project mission and scope
- Core constraints that must not be broken
- Important architecture principles
- Safety and data protection
- Main development commands
- Minimum test and acceptance requirements
- Change and deployment boundaries
- Instruction precedence
- How to load relevant skills/context
- Definition of done

**Do not** include large histories, one-off incidents, entire task-specific procedures, extensive
examples, details of completed phases, background unnecessary for every task, or frequently changing
people/version information.

Soft target: **80–200 lines**. Explain exceeding it; **do not forcibly delete important content to meet it**.

### 3. Skills contain reusable workflows

Each skill should include name, purpose, triggers, exclusions, required inputs, available tools,
execution steps, risks and limitations, output format, acceptance criteria, stop conditions, failure
handling, and relationships to other skills.

**Do not automatically load every skill on every task.** Load only skills directly relevant to the current task.

### 4. Context contains facts and state

Keep verified facts, architecture state, project baselines, current versions, completed and outstanding
items, glossaries, roles and resources, decision evidence, sources, and dates.

**Do not** fill context with large amounts of permanent behavior rules.

Volatile information requires:

```yaml
verified_at: 2026-08-27
source: <test method or source>
owner: <responsible person>
expires_at / recheck_condition: <reverification condition>
```

---

## Shared architecture across agents

**Problem:** Different agents use different entry files and may not support the same reference syntax.

**Approach** (without assuming any particular reference syntax is supported):

```
<共用目錄>/core-rules.md          ← Plain text any agent can read
├── Rule precedence
├── Language
├── Credentials
├── External communication policy
├── Cross-CLI delegation
└── Never claim actions that did not occur

Agent entry files (only actual agent-specific differences)
├── Claude:  Use import syntax supported by the tool and verified to work
├── Codex:   Explicit-path loading instruction ("Load and follow <path>")
├── Qwen:    Same as above
└── Grok:    Same as above
```

**Key points:**

1. First **check the current environment and actual project usage**; do not assume syntax works.
2. If references are unsupported, repeat only the **unavoidable minimum**.
3. **Add synchronization verification** for repeated content (below).
4. Add `VERSION` markers to entry files to detect divergence.

---

## Where one-off incidents belong

| Nature | Destination |
|---|---|
| Automatically verifiable behavior | Regression test |
| Required pre-delivery check | Acceptance checklist |
| Architecture decision | ADR (Architecture Decision Record) |
| Incident sequence and root cause | Incident report |
| Reason for a decision | Decision log |
| Pure history | Archive (no longer loaded) |
| Valid only in a particular directory | That directory's rules file |

**Do not permanently accumulate every incident in global agent instructions.**

---

## Writing rules

Include, where possible: **action / scope / trigger / exceptions / verification method / failure handling**.

Avoid words without assessment criteria: best / perfect / high quality / natural / appropriate / as
needed / latest / prioritize / complete.

**Scrutinize** `MUST`/`NEVER`/`ALWAYS`: reserve absolutes for genuinely inviolable safety, data integrity,
regulatory, or core acceptance requirements.

---

## Prevent rules from accumulating again

1. Write the **single authoritative source principle** into the entry file itself.
2. Set **soft entry file line limits** (user level ≤ 40 lines; project level ≤ 200 lines).
3. **Automate synchronization checks** with a script verifying that:
   - Every entry file points to the shared canonical source
   - `VERSION` markers match
   - Key rule strings appear only in the canonical source, without duplicates
   - Referenced paths exist, without dangling references
4. **Ask three questions before adding a rule:**
   - Where is the canonical source? Has someone already written it?
   - Can it be automatically verified? If so, write a test.
   - Is it a general principle or a one-off incident? Restrict scope for the latter.
5. **Include memories and schedules in quarterly reviews.** Both inject automatically and readily
   accumulate stale rules.

---

## What synchronization scripts should check

```
[ ] Shared canonical source exists and is nonempty
[ ] Shared canonical source includes every necessary section
[ ] Every entry file points to the shared canonical source
[ ] Entry files do not repeat canonical content (no duplicated key strings)
[ ] All referenced paths exist (no dangling references)
[ ] No cyclic references
[ ] Skill links/junctions point to correct targets
[ ] Deployed copies match source assets (hash comparison)
```

⚠️ **Verification scripts become outdated too.** Literal entry-file comparisons can report false
failures after rules move. Before fixing one, establish **whether the assertion is stale or the rule's
reference is actually broken**. Prefer **functional** assertions (does it point to the canonical source?)
over **literal** ones (does it contain a certain sentence?).

## Main project skills and subskills

When asked to standardize an entire project, follow the [project organization procedure](project-organization.md)
to create a main skill and workflow, placing each subskill in its subproject. Use project-map.json as
the single hierarchy/path index and generate navigation, breadcrumbs, and mind maps from it. Shared
canonical rules govern constraints across tasks; the main skill governs task routing and handoffs.
Do not duplicate shared rules or require loading every subskill.
