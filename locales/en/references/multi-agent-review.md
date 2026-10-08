# Multi-Agent Review Procedure

---

## When two or more **truly independent** models are available

### Round one: blind review

| Role | Work | Constraint |
|---|---|---|
| Auditor A | File inventory, rule atomization, conflict and duplicate analysis | **Do not read B's conclusions first** |
| Auditor B | Independently perform the same audit | **Do not read A's deletion recommendations first** |

### Round two: cross-review

Compare both results and identify:

- Rules A would delete and B would preserve
- Rules A sees as conflicts and B sees as scope differences
- **Rules both missed** (the most valuable findings)
- Differences in safety, deployment, and data integrity assessments
- Differences over "one-off patch versus general rule"

### Round three: governance decisions

An integrator produces the final proposal. **Preserve both sides' reasoning on major disagreements;
do not pretend a consensus was reached.**

---

## When only one agent is available (common)

Perform two reviews with different focuses:

| Round | Focus | Bias |
|---|---|---|
| First | Completeness and preservation | Keep more initially; ensure no rule is missed |
| Second | Simplification, conflicts, and cost | Actively seek duplicates, contradictions, stale content, and bloat |

**Label this explicitly:**

> These are two reviews by a single model with different focuses, **not blind reviews by two independent models**.

### Absolute prohibition

**Never describe two self-reviews by one agent as independent third-party verification.**

This is a baseline of honesty. Two self-reviews are useful—the second may catch omissions from the
first—but they share biases and do not constitute independent verification.

---

## Practical recommendation: parallel audit by area

With hundreds of rules, one agent's output may exceed limits. Divide the work:

```
Area A: User-level entry files + settings
Area B: Largest project instruction file (may need further segmentation)
Area C: Other project files + memory files
Area D: Cross-file conflicts and duplicates (specifically across A/B/C)
Area E: Safety, injection, capabilities, and cycles (specifically dangerous categories)
Area F: Completeness critic (specifically "locations everyone missed")
```

**Area F is the easiest to omit, yet often finds the most important issues.** For example, everyone
audits `CLAUDE.md` and misses an equally large `AGENTS.md` beside it.

### Handling output limits

If too many rules in an area cause output truncation:

1. **Do not pretend the work is complete.**
2. Switch to segments, for example three parts split by section.
3. State in the report that the area was incomplete and is being completed in segments.
4. Fill in the completed results and update verification items afterward.

---

## Decision principles during cross-review

When the two audits differ:

| Situation | Decision |
|---|---|
| One has actual test evidence; the other is speculation | Prefer **evidence** |
| One says "safe" and the other "risky" | Take the **stricter** position unless evidence establishes no risk |
| One says duplicate; the other says different scope | Examine scope and canonical sources. Simultaneous loading creates duplicate cost; copies of the same rule across sessions still require divergence checks. Preserve genuinely different scopes. |
| One would delete; the other would preserve | **Preserve** by default unless the deletion proposal identifies a replacement rule |

Record the conflicting content, which rule was adopted, why, how the superseded rule is handled,
and whether human confirmation is required.

## Independent contexts and different models

Independent contexts of the same model can review work, but are not different-model verification.
Delegate only necessary, masked data through mechanisms currently available and authorized. Do not
start unknown tools, delegate recursively, or review indefinitely. Reviewers read back files and test
evidence rather than trusting the implementer's completion claims directly.
