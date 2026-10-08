# Language Editions and Installation

Four languages are provided: `zh-TW`, `en`, `de`, and `ja`. The Chinese root documents are the
translation source; semantics and safety contracts are maintained at the same version. Translations
are editions for reading and execution, without additional privileges or competing canonical authority.
Do not let the host automatically load all four identically named skills together.

## Complete scope

Each language has README, SKILL, CHANGELOG, AUDIT-REPORT, all references, and all templates. Natural
language explanations and template labels are translated. Code, commands, filenames, JSON keys,
schema versions, the CSV header, status enums, rule IDs, template variables, and external URLs stay
the same. Source documents preserve historical test results; do not claim that limited tests verify
every language or platform.

In the source checkout, translated documents are in `locales/en`, `locales/de`, and `locales/ja`.
Tools and tests have one shared copy in the root `scripts/` and `tests/` directories. When reading a
locale's main skill directly, run commands from the repository root. Copying only a locale folder
does not provide a complete executable skill.

## Release packages

Run this build command only in the complete source repository. A release ZIP is a runnable skill in
the selected language, not a multilingual source/build checkout; it excludes the source-only builder
and unselected locale directories.

```powershell
python scripts/build-locales.py --output-dir release-packages-new
```

The output directory must be new. The build produces four ZIPs, SHA256SUMS.txt, and RELEASE-MANIFEST.json.
Each ZIP has `ai-instruction-detox/` at the top level, containing that language's documents and
templates, shared tools and tests, and `package-language.json`. Package only explicitly listed public
files, excluding Git, staging, backups, private paths, and credentials. Language switch links inside
the package point to the corresponding GitHub edition, avoiding reliance on uninstalled language files.

After downloading and confirming SHA-256, put the complete folder in the host's skill directory.
Use the host's own loading/refresh procedure; do not assume every product shares installation paths
or automatic loading syntax. Preserve existing skill modifications and recoverable copies before
updating. Do not install four main skills with the same name simultaneously. To switch language,
check the source version first and replace the complete package.

## Tool language

The scanner and navigation tool accept `--language zh-TW|en|de|ja`. Without that option, they use
`package-language.json` in their own skill package; the source checkout defaults to Traditional
Chinese. They do not read metadata from the audited directory or infer language from the operating
system environment. CLI text, summaries, and generated navigation labels change; machine fields,
filenames, and exit codes stay the same.

```powershell
python scripts/detox-scan.py --root . --language en
python scripts/project-map.py check --manifest project-map.json --language de
python scripts/project-map.py render --manifest project-map.json --output-dir map-preview-new --language ja
```

These flags do not change allowed paths, scan scope, write boundaries, or safety checks.

## Maintenance and verification

Whenever a source contract changes, synchronize relevant translations, templates, and versions.
Use tests to compare complete document inventories, relative links, template variables, machine
fields, code commands, and language options. Also conduct semantic review in an independent context;
file existence checks alone are insufficient. Run the CLI in every language with temporary fixtures;
extract release ZIPs and verify resources, tools, and metadata. Mark unexecuted language/platform
checks NOT_RUN; finished translations do not establish a passing result.
