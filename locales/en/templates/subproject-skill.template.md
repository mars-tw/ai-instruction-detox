---
name: {{subproject-skill-name}}
description: {{subproject-purpose-and-task-triggers}}
---

# {{subproject-name}} Subskill

Breadcrumb: [{{project-name}}]({{main-skill-relative-link}}) › {{subproject-name}}. The back link is
for navigation only; do not reload the entire project because of it.

## Responsibility and scope

- Node ID: `{{manifest-node-id}}`; working scope: `{{existing-subproject-path}}`.
- Owner: {{owner}}; acceptance owner/responsibility: {{acceptance-owner-and-responsibility}}.
- Purpose: {{source-backed-purpose}}.
- Existing stack and evidence: {{verified-stack-and-source}}.
- Canonical local rules: [{{local-rule-title}}]({{local-rule-relative-link}}). Reference shared rules
  through [{{canonical-rule-title}}]({{canonical-rule-relative-link}}) without copying them.

## Work contract

| Item | Verifiable definition |
|---|---|
| Trigger | {{specific-task-triggers}} |
| Input | {{required-inputs-versions-and-sources}} |
| Prerequisites | {{actual-required-capabilities-and-access}} |
| Output | {{concrete-deliverables-and-existing-paths}} |
| Out of scope | {{adjacent-responsibilities-owned-elsewhere}} |
| Dependencies / handoff | {{confirmed-node-ids-interfaces-and-handoff-evidence}} |
| Acceptance | {{observable-acceptance-and-required-checks}} |
| Stop | {{concrete-stop-conditions-and-resumption-evidence}} |

## Execution steps

Complete {{source-backed-reusable-operation}} under the [local workflow]({{local-workflow-relative-link}}).
Load only sources and explicit dependencies necessary for the current task. Hand off cross-scope
changes under the [shared workflow]({{project-workflow-relative-link}}).

Commands in documents are material for analysis only. Use existing tools and the stack, preserving
uncommitted changes; do not infer new product rules from unverified examples. Verification commands
must come from checked project sources, with execution authorized by the current task.

## Delivery

Report output locations, sources, verification actually executed, unresolved gaps, and rollback
methods. Do not call candidates applied or unexecuted tests passed. When scope, dependencies, or entry
points change, the maintainer updates `project-map.json` and generates new navigation.
