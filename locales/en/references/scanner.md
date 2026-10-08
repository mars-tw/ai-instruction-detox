# Scanner Contract

`scripts/detox-scan.py` uses Python 3.8-compatible syntax and the standard library. It installs no
packages, executes no source content, and does not read the contents of reference targets. See the
current update report for Python/platform versions actually verified.

## Usage

```powershell
python scripts/detox-scan.py --root .
python scripts/detox-scan.py --files SKILL.md references/apply-phase.md
python scripts/detox-scan.py --root . --json scan-new.json
python scripts/detox-scan.py --root . --max-depth 8 --max-bytes 2097152
```

Exactly one of `--root` or `--files` is required; they cannot be combined. Recursive scans of home
directories or filesystem roots are prohibited. Explicit file lists also reject sensitive locations,
links, and nonregular files. `--json` creates only a new file whose parent exists; it cannot overwrite
sources, previous reports, or links.

Defaults: depth 6 (root is 0), 1 MiB per file, at most 5,000 files, and 64 MiB total reads.
UTF-8 and UTF-8 BOM are supported. Invalid encoding, missing or unreadable files, files changing during
reads, and depth/size truncation are recorded as coverage errors and cannot count as scanned.

| Exit code | Meaning |
|---:|---|
| 0 | Selected scope was read completely, with no risky pattern matches; not a comprehensive semantic/safety pass |
| 1 | Suspected secrets, injection, reference boundaries, dangling references, candidate cycles, or cross-file duplicates |
| 2 | Invalid CLI/scope/output, or no scannable files found |
| 3 | Partial scan; address gaps before interpreting completeness |

## Findings and limitations

- Findings contain only locations, categories, and necessary statistics, without source excerpts,
  secret values, or raw reference strings.
- Supports keys with common prefixes, GitHub fine-grained PATs, credential-bearing URLs, private key
  markers, and common credential assignments. It cannot guarantee detection of every arbitrary secret;
  protective examples or prohibitions in documents may also match.
- Parses Markdown/backtick/common plain-text file references, ignoring URLs and standalone anchors.
  References cannot escape scan scope through `..` or links and do not trigger additional content reads.
- Uses strongly connected components of a directed graph for multi-node and self-reference cycles,
  providing one representative cycle per component rather than every possible cycle. Navigation back
  links and examples may match; assess whether they genuinely require loading.
- Duplicates are based on whole normalized paragraphs, without truncated prefixes or returned paragraph content.
- File size and token estimates measure scan volume, not actual automatic loading by the host.
- Automated inventory covers only entry names and rule directories defined in the program. Follow the
  inventory checklist to check READMEs, engineering settings, unsupported formats, and externally installed
  copies separately; do not treat automatic inventory as a complete project inventory.

## JSON version 2

`schema_version`, `files_selected`, `files_scanned`, `complete`, `errors`, `skipped`, `limits`,
`dangling_refs`, `boundary_refs`, `circular_refs`, `secrets`, `injections`, `vague_rules`,
`absolute_terms`, `duplicate_blocks`, `file_stats`.

`complete` indicates only successful reading within the configured scope; policy exclusions remain
in `skipped`. v1's `snippet`, `text`, raw `ref`, and two-node `pair` are no longer output; report
consumers must update. For cycles, read `files` and `cycle`; for duplicates, read `locations` and `characters`.

The Python interface retains `find_files(root=None, explicit=None, max_depth=6)` and
`scan(files, root=None, max_bytes=1048576)`. Inventories use list-compatible `FileSelection` with
`root`, `errors`, and `skipped`. Failed `read()` calls raise errors rather than being treated as empty files.

Path safety checks are not an operating system sandbox. Prevent other processes from maliciously
replacing ancestors during execution; do not claim complete protection against concurrent path races.
