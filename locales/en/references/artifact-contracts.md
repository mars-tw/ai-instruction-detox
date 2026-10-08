# Audit Artifact Contracts

Audited content may contain secrets or commands. These contracts govern derived output and do not
authorize access to additional credentials.

## Isolation and version baselines

Use a new `.ai-detox/run-識別碼/` directory for each run. Check the destination and ancestors for links
or junctions, confirm the approved scope, and preserve existing reports. Keep staging, backups, and
handoffs out of automatic agent loading. Check Git ignore rules and `git ls-files`; adding an ignore
rule does not automatically exclude a tracked file.

`baseline-manifest.json` uses `schema_version: 1`. Record each change as follows:

| Field | Contract |
|---|---|
| `source_path`/`target_path` | Relative paths within the approved root; out-of-scope paths, sensitive locations, and links are prohibited |
| `action` | `CREATE`/`UPDATE`/`MOVE`/`ARCHIVE`; deletion also requires a recovery plan |
| `source_exists`/`target_exists` | Existence at audit time; distinguish creation from update |
| `source_sha256`/`target_sha256` | Digests of existing files; null when originally absent |
| `proposed_path`/`proposed_sha256` | Candidate location and digest |
| `baseline_copy` | Baseline copy that passed sensitivity checks; null if it cannot be stored safely |
| `backup_path` | Safe backup location before application; null if not applied |
| `applied_sha256` | Actual digest after application; null if not applied |
| `rule_ids` | Corresponding ledger IDs |
| `status` | `PROPOSED`/`APPLIED`/`DEFERRED`/`ROLLED_BACK` |

Also record the root, Git HEAD if available, and audit/application timestamps. mtime is supplementary;
digests and existence are the preconditions for writes. MOVE checks both ends; CREATE confirms the file
is still absent. Never include raw secrets or hashes dedicated to secret values; whole-file digests
are only for version comparison. The manifest records operations; this skill has no automatic applicator,
so do not claim it has been programmatically verified or applied.

## Secrets and excerpts

1. Exclude credential directories and files before scanning.
2. If an allowed instruction file includes keys, tokens, passwords, or credential-bearing URLs, report
   only the file, line, and type. Replace secrets in fields such as `original_text` with `[REDACTED]`;
   do not quote the full original sentence again.
3. For excerpts that cannot be reliably masked, use the source location and "Contains sensitive
   information; excerpt omitted." If a Diff would reveal raw values, do not produce a raw patch;
   mark the item `HUMAN_REVIEW`.
4. Inspect before backing up. Do not copy secret-bearing files to ordinary staging. Store them only
   under the policy of approved restricted storage. If safe backup is impossible, stop that item
   without delaying the others.
5. Secret detection is heuristic; zero matches do not guarantee absence of secrets. Inspect every
   artifact intended for delivery.

## Ledger: 28 columns in a fixed order

Use the [header](../templates/01-rule-ledger-header.csv). The first 25 columns retain v1.0 names;
`strength`, `exceptions`, and `dependencies` are appended. New ledgers have 28 columns.

| Field group | Definition |
|---|---|
| `rule_id`, `source_file`, `source_location` | Unique ID, relative source path, line or section |
| `original_text`, `normalized_rule` | Masked source text and normalized rule; preserve valid intent |
| `category`, `scope`, `agent` | Type, applicable scope, actual agent or UNKNOWN |
| `severity` | `LOW`/`MEDIUM`/`HIGH`/`CRITICAL`; risk, not requirement strength |
| `default_behavior` | `A` (sourced tool guarantee)/`B` (not guaranteed)/`C` (project-specific)/`UNKNOWN` |
| `conflict`, `duplicate`, `incident_patch`, `ambiguity` | Conclusions, related IDs, and evidence; NONE if absent |
| `testability`, `stale_status`, `scope_problem`, `cost_problem` | Verification method, freshness, scope, and cost issues |
| `security_status`, `capability_mismatch`, `circularity` | Safety assessment, capability differences, loading cycle evidence |
| `recommendation`, `target_location`, `reason`, `confidence` | One of ten dispositions, destination, reason, confidence from 0 to 1 |
| `strength` | `REQUIRED`/`RECOMMENDED`/`OPTIONAL`/`INFORMATIONAL`/`UNKNOWN` |
| `exceptions`, `dependencies` | Explicit exceptions and dependency rule IDs/files/tools; NONE if absent |

Rule categories: security, legal, data-integrity, business-brand, architecture, test-acceptance,
workflow, tool-usage, multi-agent-dispatch, output-format, language-tone, persona, factual-context,
project-state, example, history, one-off-exception, incident-patch, temporary, possible-prompt-injection.

Each rule has exactly one ID and disposition; MERGE/MOVE remain traceable to new locations. Use a CSV
writer for commas, quotes, and newlines. In copies for Excel review, prefix a single quote when a cell's
first effective character is `=`, `+`, `-`, or `@`, or when it starts with tab/CR/LF. This does not guarantee
safety after reopening or saving again. Use masked JSON for verbatim preservation and structured
exchange, avoiding spreadsheet execution. See [OWASP CSV Injection](https://community.owasp.org/attacks/CSV_Injection).

## Verification states

`PASS` requires an actual command, successful result, or file evidence. `FAIL` records a counterexample;
`NOT_RUN` records why it was not executed; `NOT_APPLICABLE` explains non-applicability. Simulations are
design checks, not real tests. Navigation links do not force loading; the presence of a test script
does not establish that it ran.
