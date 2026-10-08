#!/usr/bin/env python3
"""Validate this installed package with the standard library only."""
import ast
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def main():
    try:
        for source in sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "tests").glob("*.py")):
            ast.parse(source.read_text(encoding="utf-8"), filename=str(source), feature_version=(3, 8))
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        header = re.match(r"\A---\n(.*?)\n---(?:\n|\Z)", text, re.S)
        if not header:
            raise ValueError("SKILL.md frontmatter is missing")
        fields = set(re.findall(r"^([a-z][a-z-]*):", header.group(1), re.M))
        if not {"name", "description"} <= fields:
            raise ValueError("SKILL.md requires name and description")
        if fields - {"name", "description", "license", "metadata", "allowed-tools"}:
            raise ValueError("unsupported top-level skill metadata")
        if not re.search(r"^name: ai-instruction-detox$", header.group(1), re.M):
            raise ValueError("unexpected skill name")
    except (OSError, SyntaxError, ValueError) as exc:
        print("PACKAGE ERROR: {}".format(exc), file=sys.stderr)
        return 1
    print("Python 3.8 grammar and package entry metadata: PASS", flush=True)
    # Only the installed, reviewed test suite is executed; never load a target
    # audit project's hooks or commands here.
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                            cwd=str(ROOT), check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
