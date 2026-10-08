"""Source-only translation and release-scope checks; not shipped in skill ZIPs."""
from collections import Counter
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("locale_builder", ROOT / "scripts" / "build-locales.py")
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


def machine_structure(value):
    if isinstance(value, dict):
        return {key: machine_structure(item) for key, item in value.items() if key not in ("name", "purpose")}
    if isinstance(value, list):
        return [machine_structure(item) for item in value]
    return value


class SourceLocaleTests(unittest.TestCase):
    def test_complete_editions_have_matching_version_and_machine_contracts(self):
        public = BUILD.documentation_paths()
        for code in ("en", "de", "ja"):
            base = ROOT / "locales" / code
            files = sorted(p.relative_to(base).as_posix() for p in base.rglob("*") if p.is_file())
            self.assertEqual(files, public, code)
            header = (base / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[1]
            self.assertIn('version: "' + BUILD.version() + '"', header)
            self.assertIn("locale: " + code, header)
            for relative in public:
                source = (ROOT / relative).read_text(encoding="utf-8")
                translated = (base / relative).read_text(encoding="utf-8")
                with self.subTest(code=code, file=relative):
                    self.assertEqual(Counter(re.findall(r"\{\{[^{}]+\}\}", source)),
                                     Counter(re.findall(r"\{\{[^{}]+\}\}", translated)))
                    command = r"^\s*(?:python|git|crontab)\s+.*$"
                    self.assertEqual(re.findall(command, source, re.M), re.findall(command, translated, re.M))
                    if relative.endswith(".csv"):
                        self.assertEqual((ROOT / relative).read_bytes(), (base / relative).read_bytes())
                    if relative.endswith(".json"):
                        self.assertEqual(machine_structure(json.loads(source)), machine_structure(json.loads(translated)))

    def test_all_localized_markdown_resource_links_exist(self):
        for code in ("en", "de", "ja"):
            base = ROOT / "locales" / code
            sources = [base / name for name in BUILD.DOCS] + sorted((base / "references").glob("*.md"))
            for source in sources:
                text = re.sub(r"^```.*?^```[^\n]*", "", source.read_text(encoding="utf-8"), flags=re.M | re.S)
                for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                    if "://" in target or target.startswith("#"):
                        continue
                    target = unquote(target.split("#", 1)[0])
                    with self.subTest(code=code, file=source.name, target=target):
                        self.assertTrue((source.parent / target).is_file())

    def copy_public_fixture(self, root):
        root.mkdir()
        paths = BUILD.documentation_paths() + ["LICENSE"]
        paths += ["scripts/" + name for name in BUILD.RUNTIME]
        paths += ["tests/" + name for name in BUILD.TESTS]
        for name in paths:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)

    def test_builder_accepts_crlf_and_never_packages_nearby_private_files(self):
        with tempfile.TemporaryDirectory(prefix="detox-build-") as temporary:
            root = Path(temporary) / "source"
            self.copy_public_fixture(root)
            for path in root.rglob("*.md"):
                path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
            (root / "templates/credentials.json").write_text('{"password":"SYNTHETIC_ONLY"}', encoding="utf-8")
            (root / "references/private-draft.md").write_text("SYNTHETIC_ONLY", encoding="utf-8")
            with mock.patch.object(BUILD, "ROOT", root):
                self.assertEqual(BUILD.version(), "1.2.0")
                content = BUILD.payload("zh-TW", "1.2.0")
                self.assertNotIn("templates/credentials.json", content)
                self.assertNotIn("references/private-draft.md", content)
                self.assertFalse(any(b"SYNTHETIC_ONLY" in item for item in content.values()))

    def test_builder_refuses_existing_linked_and_sensitive_outputs(self):
        with tempfile.TemporaryDirectory(prefix="detox-output-") as temporary:
            root = Path(temporary) / "source"
            self.copy_public_fixture(root)
            (root / "existing").mkdir()
            (root / "existing/keep.txt").write_text("preserve", encoding="utf-8")
            with mock.patch.object(BUILD, "ROOT", root):
                for destination in ("existing", "../escape", "/absolute", "C:/escape", ".envrc/x", "credentials.txt/x"):
                    with self.subTest(destination=destination):
                        with self.assertRaises(BUILD.BuildError):
                            BUILD.output_path(destination)
                self.assertEqual((root / "existing/keep.txt").read_text(encoding="utf-8"), "preserve")
                real_lstat = Path.lstat
                def linked_lstat(path, *args, **kwargs):
                    if path == root:
                        from types import SimpleNamespace
                        return SimpleNamespace(st_mode=0o040755, st_file_attributes=0x400)
                    return real_lstat(path, *args, **kwargs)
                with mock.patch.object(Path, "lstat", linked_lstat):
                    with self.assertRaises(BUILD.BuildError):
                        BUILD.output_path("new")


if __name__ == "__main__":
    unittest.main()
