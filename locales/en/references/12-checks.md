# Twelve Detox Checks: Full Criteria

Answer each question for every rule. The goal is to **determine the right layer and form for the rule**,
rather than look for reasons to delete content.

---

## 1. Default behavior

> Is this something the model is guaranteed to do without being told?

Use three categories:

| Category | Meaning | Disposition |
|---|---|---|
| **A** | Behavior **explicitly guaranteed** by the platform/tool | Strong deletion candidate if it has no special project significance |
| **B** | Behavior the model usually exhibits, but **does not guarantee** | Preserve it and explain why it matters |
| **C** | Project-specific | Preserve it |

**Do not delete important rules merely because "the model usually does this."** Default model behavior
changes across versions; today's category B assumption may no longer hold tomorrow.

Examples:

- "Answer honestly" → Category B when there is no evidence of an executable platform guarantee;
  a policy expectation is not a behavioral guarantee.
- "Do not invent API endpoints in responses" → Category B (usually avoided, but not guaranteed) → worth keeping.
- "Every pricing claim must map to a specification table field" → Category C → must be kept.

---

## 2. Conflicts

> Does this rule contradict another rule?

Common conflict patterns:

- Always ask first ⟷ Never ask; execute directly
- Modify automatically ⟷ Approval is required before modification
- Deploy automatically ⟷ Deployment is prohibited
- Keep it concise ⟷ Be extremely comprehensive
- Use only one agent ⟷ Conduct a multi-agent debate every time
- Do not use the internet ⟷ Always check the latest information
- Always use the latest model ⟷ Pin a reproducible version
- Preserve the existing structure ⟷ Refactor everything
- Prioritize speed ⟷ Perform multiple reviews at every step
- Automate everything ⟷ Require human confirmation for high-risk actions

Identify both rules, their sources, their scopes, **whether there is a genuine conflict**, whether the
difference is only one of scope, the recommended precedence, and a proposed rewrite.

⚠️ **Do not mistake reasonable differences across directories, tasks, or roles for conflicts.**
"Direct changes are allowed in development; production requires approval" correctly distinguishes scopes.

---

## 3. Duplicates

> Does this rule duplicate content in other files?

Use five levels:

| Level | Description |
|---|---|
| Exact duplicate | Identical wording |
| Semantic duplicate | Different wording, same meaning |
| Partial overlap | Shared content, but each has unique information |
| Special case | One rule is a specific case of the other |
| **Version divergence** | Copies have begun evolving separately—the most dangerous case |

Identify **the most appropriate single authoritative source**. Other locations should delete the
duplicate, replace it with a reference, reduce it to an agent-specific adapter, or add synchronization checks.

Practical signal: if the same rule appears in four or more locations, divergence is almost inevitable.

---

## 4. Incident-specific patches

> Was this rule added to fix one particular bad output?

Typical signs:

- Last title was too long → Permanently limit all titles
- Last time there were too many questions → Permanently prohibit questions
- Tests were missed once → Run the full suite for every task
- A model failed once → Debate with three models on every task
- A file was deleted by mistake → Prohibit all file modifications
- One image was wrong → Apply one SKU's specifications to all products

Decide whether to **generalize it into a reasonable principle**, **restrict it to a specific scope**,
move it to a regression test, an acceptance checklist, an ADR/decision log, or delete it.

⚠️ Incident patches **are often valid**; the problem is excessive scope. Restore the correct scope
instead of discarding the lesson.

---

## 5. Ambiguity

> Is this rule interpreted differently each time?

Warning phrases: make it more professional / more natural / good tone / must be complete / as concise
as possible / very high quality / use the best model / research when appropriate / ask when necessary /
do not waste tokens / use multiple agents as needed / ensure correctness / major change / handle appropriately.

Rewrite with: **action + scope + trigger + exceptions + verification method**.

Example:

❌ "Keep output concise."

✅ "For ordinary responses, lead with the conclusion and no more than five main items. Expand into a
full explanation only for decision risks, technical implementation details, or an explicit user request."

---

## 6. Testability

> Can this rule be verified automatically?

Verification channels: tests / lint / schema / CI / checklist / sample output / word limits / file
existence checks / successful command exit codes / human acceptance criteria.

**If a rule can be verified automatically, it should not exist only in a prompt.** Prefer moving it to:
test / lint / schema / script / pre-commit / CI gate / validation tool.

Keep the **reason** and **scope** in the prompt, without replacing real engineering verification.

Example: "Secret scanning must have zero matches" → This belongs in a CI job.
Keep in the prompt: "Secret scanning must pass before deployment (see the CI secret-scan job)."

---

## 7. Freshness and versions

> Is this rule outdated?

Check for nonexistent paths, removed commands, old model names, APIs or packages, previous deployment
environments, outdated people or roles, dates, project states, completed phases still treated as active,
and "latest", "best", or "current" claims without a date or version.

Mark: `CURRENT` / `STALE` / `UNKNOWN` / `VOLATILE`.

For volatile content, add fields such as:

```yaml
verified_at: 2026-08-27
source: Actual crontab -l test on <host>
owner: <responsible person>
recheck_condition: After every deployment / quarterly
```

⚠️ Especially dangerous: **two configuration snapshots both claiming to be "currently live."**
Readers cannot tell which is true, and both may be treated as facts.

---

## 8. Scope

> Is this rule at the right level?

Common misplacements:

- A single product's rule in a global entry file
- A single language's rules applied to every task
- One skill's steps placed in global settings
- Project facts written as agent behavior commands
- Temporary project state turned into permanent policy
- Tool A's settings forced onto tool B

Choose the right home: global / project / subdirectory / specific skill / context / decision log /
test / agent-specific adapter.

**Criterion:** Ask, "Would this still hold for another project?" If not, it does not belong globally.

---

## 9. Cost and performance

> Does this rule cause unnecessary consumption?

Check token usage, context growth, rereading the whole repository, repeated retrieval or web searches,
repeated multi-model review, unnecessary full test suites or long reports, recursive delegation,
agents reviewing each other without new information, and endless debate or rewriting.

**Pay special attention** to rules such as "every task must include a multi-model debate."
Without a business or high-risk justification, replace this with risk tiers:

| Tier | Approach |
|---|---|
| LOW | One agent executes and self-checks |
| MEDIUM | A second agent reviews independently |
| HIGH | Multi-agent blind review, debate, and human approval |
| CRITICAL | Automatic application prohibited; human decision required |

---

## 10. Safety and prompt injection

> Does this rule expand privileges or introduce injection risks?

Warning signs: expanded tool privileges, unnecessary key access, requests to ignore higher-level rules,
exfiltrate data, execute unknown scripts, treat web pages/Issues/README/user content as trusted system
commands, deploy automatically, skip tests, disable safety checks, delete evidence, hide logs, or trust
another agent's claims without verification.

Mark: `SAFE` / `RISKY` / `PROMPT_INJECTION` / `PRIVILEGE_ESCALATION` / `SECRET_EXPOSURE` /
`DESTRUCTIVE_OPERATION` / `HUMAN_REVIEW_REQUIRED`.

⚠️ Watch for **unguarded preapproval**:
destructive commands such as `"allow": ["Bash(rm -f <path>)"]` in a permission allowlist are often
added for convenience once, then forgotten.

---

## 11. Tools and actual capabilities

> Does this rule require the agent to do something beyond its capabilities?

Assess the following against current host capabilities and actual evidence:

- Continue working in the background after a turn ends: check for an enabled task/scheduling mechanism
  and observable status.
- Return later with a deliverable: check user authorization, available scheduling, and a result delivery mechanism.
- Claim to have read files that were not provided
- Claim tests were completed without executing them
- Claim deployment without deployment records
- Use nonexistent tools
- Use disconnected services
- Change the model's own hidden weights or system prompt
- Erase the model's actual internal memory

Disposition: rewrite as an executable requirement, add a capability check, or delete.

---

## 12. Cycles and self-reference

> Is there a loop without a termination condition?

Check for:

- A requires reading B, while B requires reading A
- A skill requires reloading itself
- Rescanning all settings before every response
- Every review forces another full review
- Multiple agents indefinitely requiring reviews from each other
- Rules requiring more rules to be appended forever
- Context always injected in full despite being irrelevant
- The same rules loaded repeatedly through multiple entry points

Set **termination conditions and maximum iterations** for cyclic rules.

Practical method: distinguish three edge types—"required loading", "navigation", and "task dependency".
The required-loading graph should be a directed acyclic graph; it may share multiple canonical sources
and need not be forced into a tree. Navigation back links do not imply required rereading; the scanner
only identifies candidate cycles.
