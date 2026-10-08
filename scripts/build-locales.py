#!/usr/bin/env python3
"""Build complete language editions from the reviewed source repository."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import zipfile

from locale_data import LANGUAGES


ROOT = Path(__file__).resolve().parents[1]
DOCS = ("SKILL.md", "README.md", "CHANGELOG.md", "AUDIT-REPORT.md")
REFERENCES = ("12-checks.md", "apply-phase.md", "artifact-contracts.md", "inventory-checklist.md",
              "localization.md", "multi-agent-review.md", "project-organization.md", "scanner.md",
              "target-architecture.md", "validation-checklist.md")
TEMPLATES = ("00-scope-and-inventory.template.md", "01-rule-ledger-header.csv",
             "02-conflicts-and-precedence.template.md", "03-delete-merge-move.template.md",
             "04-target-architecture.template.md", "05-validation.template.md", "06-rollback.template.md",
             "baseline-manifest.template.json", "project-main-skill.template.md", "project-map.example.json",
             "project-workflow.template.md", "subproject-skill.template.md")
RUNTIME = ("detox-scan.py", "project-map.py", "locale_data.py", "verify-package.py")
TESTS = ("test_detox_scan.py", "test_project_map.py", "test_package_contract.py", "test_runtime_locales.py")


class BuildError(ValueError):
    pass


def inspect_path(path, required=True):
    for part in list(reversed(path.parents)) + [path]:
        try:
            info = part.lstat()
        except FileNotFoundError:
            if required:
                raise BuildError("a required package path is missing")
            return False
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise BuildError("package and output paths must not use links or reparse points")
        if part != path and not stat.S_ISDIR(info.st_mode):
            raise BuildError("a package path has a non-directory ancestor")
    return True


def read_public(path):
    inspect_path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > 2 * 1024 * 1024:
        raise BuildError("package inputs must be bounded regular files")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    with os.fdopen(os.open(str(path), flags), "rb") as stream:
        opened = os.fstat(stream.fileno())
        if (info.st_dev, info.st_ino) != (opened.st_dev, opened.st_ino):
            raise BuildError("a package input changed during read")
        data = stream.read(2 * 1024 * 1024 + 1)
    if len(data) > 2 * 1024 * 1024:
        raise BuildError("a package input grew beyond its limit")
    return data


def version():
    source = read_public(ROOT / "SKILL.md").decode("utf-8").replace("\r\n", "\n")
    match = re.search(r'^  version: "(\d+\.\d+\.\d+)"$', source, re.M)
    if not match:
        raise BuildError("source skill has no supported release version")
    return match.group(1)


def documentation_paths():
    # A nearby credentials.json or newly added private draft must never become
    # public merely because it shares a documentation extension.
    return sorted(list(DOCS) + ["references/" + name for name in REFERENCES]
                  + ["templates/" + name for name in TEMPLATES])


def portable_readme(data, release_version):
    value = data.decode("utf-8")
    base = "https://github.com/mars-tw/ai-instruction-detox/blob/v" + release_version + "/"
    destinations = {"README.md": "README.md", "../../README.md": "README.md"}
    for code in LANGUAGES[1:]:
        remote = "locales/{}/README.md".format(code)
        destinations[remote] = remote
        destinations["../{}/README.md".format(code)] = remote
    for local, remote in destinations.items():
        value = value.replace("](" + local + ")", "](" + base + remote + ")")
    return value.encode("utf-8")


def payload(language, release_version):
    if language not in LANGUAGES:
        raise BuildError("unsupported package language")
    source = ROOT if language == "zh-TW" else ROOT / "locales" / language
    result = {}
    for relative in documentation_paths():
        data = read_public(source / relative)
        if relative == "README.md":
            data = portable_readme(data, release_version)
        result[relative] = data
    header = result["SKILL.md"].decode("utf-8").replace("\r\n", "\n").split("---", 2)[1]
    if ('version: "' + release_version + '"') not in header:
        raise BuildError("localized skill version differs from the source version")
    if not re.search(r"^  locale: " + re.escape(language) + r"$", header, re.M):
        raise BuildError("localized skill language metadata is inconsistent")
    for name in RUNTIME:
        result["scripts/" + name] = read_public(ROOT / "scripts" / name)
    for name in TESTS:
        result["tests/" + name] = read_public(ROOT / "tests" / name)
    result["LICENSE"] = read_public(ROOT / "LICENSE")
    result["package-language.json"] = (json.dumps({"schema_version": 1, "language": language,
                                                  "version": release_version, "source_locale": "zh-TW"},
                                                 ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return result


def output_path(relative):
    if (not relative or "\\" in relative or ":" in relative or relative.startswith("/")
            or any(part in ("", ".", "..") for part in relative.split("/"))):
        raise BuildError("output must be a new project-relative directory")
    for part in PurePosixPath(relative).parts:
        folded = part.casefold()
        if (folded in (".git", ".ssh", ".aws", ".azure", ".gnupg", ".secrets", "secrets", "credentials")
                or folded.startswith("credentials.") or folded == ".envrc"
                or folded == ".env" or folded.startswith(".env.")):
            raise BuildError("sensitive output locations are excluded")
        if (part.endswith((" ", ".")) or any(ord(c) < 32 for c in part)
                or re.match(r"(?i)(con|prn|aux|nul|com[0-9]|lpt[0-9])(?:\.|$)", part)):
            raise BuildError("ambiguous or device output names are excluded")
    target = ROOT / relative
    inspect_path(target.parent)
    if inspect_path(target, required=False):
        raise BuildError("output already exists; choose a new directory")
    return target


def build(relative, languages=LANGUAGES):
    release_version = version()
    target = output_path(relative)
    # Validate every selected edition before creating output.
    editions = {language: payload(language, release_version) for language in languages}
    os.mkdir(str(target), 0o755)
    artifacts = []
    for language, contents in editions.items():
        inspect_path(target)
        filename = "ai-instruction-detox-{}-{}.zip".format(release_version, language)
        with (target / filename).open("xb") as output:
            with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
                for relative_name, data in sorted(contents.items()):
                    info = zipfile.ZipInfo("ai-instruction-detox/" + relative_name, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, data)
        artifact = target / filename
        with zipfile.ZipFile(artifact) as archive:
            if archive.testzip() is not None:
                raise BuildError("a generated archive failed integrity validation")
            for name, data in contents.items():
                if archive.read("ai-instruction-detox/" + name) != data:
                    raise BuildError("archive payload verification failed")
        artifacts.append({"language": language, "file": filename,
                          "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                          "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(contents.items())}})
    manifest = {"schema_version": 1, "version": release_version, "source_reference": "v" + release_version,
                "artifacts": artifacts}
    manifest_data = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    inspect_path(target)
    with (target / "RELEASE-MANIFEST.json").open("xb") as output:
        output.write(manifest_data)
    checksums = [item["sha256"] + "  " + item["file"] for item in artifacts]
    checksums.append(hashlib.sha256(manifest_data).hexdigest() + "  RELEASE-MANIFEST.json")
    with (target / "SHA256SUMS.txt").open("x", encoding="utf-8", newline="\n") as output:
        output.write("\n".join(checksums) + "\n")
    return target, manifest


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, help="new directory relative to the source repository")
    parser.add_argument("--language", choices=("all",) + LANGUAGES, default="all")
    args = parser.parse_args(argv)
    try:
        target, manifest = build(args.output_dir, LANGUAGES if args.language == "all" else (args.language,))
        print("BUILT: {} verified language packages".format(len(manifest["artifacts"])))
        print(str(target))
        return 0
    except (BuildError, OSError, ValueError, IndexError):
        print("BUILD ERROR: incomplete or unsafe source/output; existing files were not overwritten.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
