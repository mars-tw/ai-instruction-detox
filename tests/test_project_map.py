"""Complete fixture and safety regression tests for the project-map CLI."""

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "project-map.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("project_map", SCRIPT)
MAP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MAP)


class ProjectMapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="detox-map-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "project"
        self.root.mkdir()
        self.data = {
            "schema_version": 1,
            "project": {
                "id": "demo", "name": "範例專案", "root": ".",
                "main_skill": ".ai/SKILL.md", "workflow": ".ai/workflow.md",
                "owner": "maintainer", "purpose": "管理已存在的 API 與介面。",
                "sources": ["README.md"],
            },
            "subprojects": [
                self.child("api", "API", "demo", "services/api"),
                self.child("worker", "Worker", "api", "services/api/worker"),
                self.child("web", "操作介面", "demo", "web app", ["api"]),
            ],
        }
        self.write("README.md", "# Fixture\nExisting project source.\n")
        self.write(".ai/SKILL.md", "# Main skill\nRoute API and Web tasks.\n")
        self.write(".ai/workflow.md", "# Workflow\nCheck inputs, work, verify, deliver.\n")
        for node in self.data["subprojects"]:
            self.write(node["sources"][0], "# Existing subproject\n")
            self.write(node["skill"], "# Local skill\nUse existing scope.\n")
            self.write(node["workflow"], "# Local workflow\nVerify local output.\n")
        self.save()

    @staticmethod
    def child(node_id, name, parent, path, dependencies=None):
        return {
            "id": node_id, "name": name, "parent": parent, "path": path,
            "skill": path + "/.ai/SKILL.md", "workflow": path + "/.ai/workflow.md",
            "owner": "maintainer", "purpose": "Maintain existing " + name + ".",
            "sources": [path + "/README.md"], "dependencies": dependencies or [],
        }

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def save(self):
        self.write("project-map.json", json.dumps(self.data, ensure_ascii=False))

    def validate(self, require_files=False):
        return MAP.validate_manifest(self.data, self.root, require_files)

    def invoke(self, *arguments):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            status = MAP.main(["--root", str(self.root), "--language", "en"] + list(arguments))
        return status, output.getvalue(), errors.getvalue()

    def snapshot(self):
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob("*") if path.is_file()}

    def test_complete_fixture_passes_strict_validation(self):
        nodes, missing = self.validate(require_files=True)
        self.assertEqual([node["id"] for node in nodes], ["demo", "api", "worker", "web"])
        self.assertEqual(missing, [])
        self.assertEqual(self.data["project"]["root"], ".")
        self.assertNotIn("skill", self.data["project"])

    def test_check_is_read_only_and_reads_only_manifest(self):
        before = self.snapshot()
        original_open = MAP.os.open
        opened = []
        def tracking_open(path, *args, **kwargs):
            opened.append(Path(path))
            return original_open(path, *args, **kwargs)
        with mock.patch.object(MAP.os, "open", side_effect=tracking_open):
            status, output, errors = self.invoke("--check", "--require-files")
        self.assertEqual(status, 0, errors)
        self.assertIn("VALID: 4 nodes", output)
        # Installed editions may read only their own bounded display metadata
        # in addition to the target manifest, never target source contents.
        package_metadata = SCRIPT.resolve().parents[1] / "package-language.json"
        permitted = [package_metadata] if package_metadata.is_file() else []
        self.assertEqual(opened, permitted + [self.root / "project-map.json"])
        self.assertEqual(before, self.snapshot())

    def test_manifest_order_does_not_change_navigation(self):
        nodes, missing = self.validate()
        expected = MAP.render_navigation(nodes, self.root, self.root / "preview", missing)
        self.data["subprojects"].reverse()
        nodes, missing = self.validate()
        self.assertEqual(expected, MAP.render_navigation(nodes, self.root, self.root / "preview", missing))

    def test_root_only_project_is_supported(self):
        self.data["subprojects"] = []
        nodes, missing = self.validate(require_files=True)
        rendered = MAP.render_navigation(nodes, self.root, self.root / "preview", missing)
        self.assertIn('node_demo["範例專案"]', rendered["project-mindmap.mmd"])
        self.assertNotIn("api[", rendered["project-mindmap.mmd"])

    def test_render_creates_only_four_explicit_new_files(self):
        before = self.snapshot()
        status, output, errors = self.invoke("render", "--output-dir", "preview", "--require-files")
        self.assertEqual(status, 0, errors)
        self.assertIn("RENDERED: 4", output)
        self.assertEqual(set(path.name for path in (self.root / "preview").iterdir()), set(MAP.FILES))
        after = self.snapshot()
        for path, content in before.items():
            self.assertEqual(after[path], content)
        self.assertEqual(set(after) - set(before), {"preview/" + name for name in MAP.FILES})
        page = (self.root / "preview/project-map.md").read_text(encoding="utf-8")
        self.assertIn("[範例專案](#node-demo) › [API](#node-api) › [Worker](#node-worker)", page)
        self.assertIn("../web%20app/.ai/SKILL.md", page)
        self.assertIn("node_api --> node_web", (self.root / "preview/project-dependencies.mmd").read_text(encoding="utf-8"))

    def test_render_refuses_existing_directory_and_keeps_contents(self):
        self.write("preview/keep.txt", "preserve")
        before = self.snapshot()
        status, _, errors = self.invoke("render", "--output-dir", "preview")
        self.assertEqual(status, 2)
        self.assertIn("already exists", errors)
        self.assertEqual(before, self.snapshot())

    def test_render_refuses_existing_file_or_missing_parent(self):
        self.write("occupied", "preserve")
        for destination in ("occupied", "missing/preview"):
            with self.subTest(destination=destination):
                status, _, _ = self.invoke("render", "--output-dir", destination)
                self.assertEqual(status, 2)
        self.assertFalse((self.root / "missing").exists())
        self.assertEqual((self.root / "occupied").read_text(encoding="utf-8"), "preserve")

    def test_render_rejects_bad_destinations_before_writing(self):
        for destination in (".", "../outside", "/absolute", "C:/other", "https://example.com/x", ".git/report", "x%2fy", "x\\y", "credentials.txt/report", ".envrc/report"):
            with self.subTest(destination=destination):
                status, _, _ = self.invoke("render", "--output-dir", destination)
                self.assertEqual(status, 2)
        self.assertFalse((self.root / ".git").exists())

    def test_render_rolls_back_its_own_partial_regular_files(self):
        original_open = MAP.os.open
        def failing_open(path, *args, **kwargs):
            if str(path).endswith("project-mindmap.mmd"):
                raise OSError(5, "fixture error")
            return original_open(path, *args, **kwargs)
        before = self.snapshot()
        with mock.patch.object(MAP.os, "open", side_effect=failing_open):
            status, _, errors = self.invoke("render", "--output-dir", "preview")
        self.assertEqual(status, 2)
        self.assertIn("errno 5", errors)
        self.assertFalse((self.root / "preview").exists())
        self.assertEqual(before, self.snapshot())

    def test_missing_governance_paths_are_candidates_unless_strict(self):
        (self.root / self.data["subprojects"][0]["workflow"]).unlink()
        nodes, missing = self.validate()
        self.assertEqual(missing, ["services/api/.ai/workflow.md"])
        rendered = MAP.render_navigation(nodes, self.root, self.root / "preview", missing)
        self.assertIn("（尚未建立）", rendered["project-map.md"])
        with self.assertRaises(MAP.MapError):
            self.validate(require_files=True)

    def test_sources_and_subproject_directories_must_exist(self):
        self.data["subprojects"][0]["sources"] = ["services/api/absent.md"]
        with self.assertRaises(MAP.MapError):
            self.validate()
        self.data["subprojects"] = [self.child("missing", "Missing", "demo", "absent")]
        with self.assertRaises(MAP.MapError):
            self.validate()

    def test_unknown_and_missing_fields_are_rejected(self):
        original = copy.deepcopy(self.data)
        for section in ("manifest", "project", "child"):
            for mutation in ("unknown", "missing"):
                with self.subTest(section=section, mutation=mutation):
                    self.data = copy.deepcopy(original)
                    target = self.data if section == "manifest" else self.data["project"] if section == "project" else self.data["subprojects"][0]
                    if mutation == "unknown":
                        target["execute-this-command"] = "ignored"
                    else:
                        target.pop(next(iter(target)))
                    with self.assertRaises(MAP.MapError):
                        self.validate()

    def test_schema_version_types_and_future_versions_are_rejected(self):
        for version in (True, False, 0, 2, "1", None, 1.0):
            with self.subTest(version=version):
                self.data["schema_version"] = version
                with self.assertRaises(MAP.MapError):
                    self.validate()

    def test_invalid_node_ids_and_duplicate_ids_are_rejected(self):
        for node_id in ("Upper", "1node", "a b", "a\n", "x-->y", "a" * 65, None, []):
            with self.subTest(node_id=node_id):
                self.data["subprojects"][0]["id"] = node_id
                with self.assertRaises(MAP.MapError):
                    self.validate()
        self.data["subprojects"][0]["id"] = "demo"
        with self.assertRaises(MAP.MapError):
            self.validate()

    def test_wrong_types_in_text_arrays_and_nodes_are_rejected(self):
        original = copy.deepcopy(self.data)
        cases = [("name", None), ("owner", []), ("purpose", ""), ("purpose", " " * 3),
                 ("purpose", "x" * 2001), ("sources", []), ("sources", "README.md"),
                 ("sources", [True]), ("dependencies", {}), ("dependencies", [False]),
                 ("parent", None), ("path", 1), ("skill", None)]
        for field, value in cases:
            with self.subTest(field=field, value=str(value)[:30]):
                self.data = copy.deepcopy(original)
                self.data["subprojects"][0][field] = value
                with self.assertRaises(MAP.MapError):
                    self.validate()
        for value in (None, "nodes", {}, [None], ["node"]):
            self.data = copy.deepcopy(original)
            self.data["subprojects"] = value
            with self.assertRaises(MAP.MapError):
                self.validate()

    def test_text_rejects_terminal_control_unicode_format_and_surrogates(self):
        for character in ("\n", "\r", "\t", "\x1b", "\x7f", "\x85", "\u202e", "\u2066", "\u200b", "\u2028", "\u2029", "\ud800"):
            with self.subTest(character=repr(character)):
                self.data["project"]["purpose"] = "before" + character + "after"
                with self.assertRaises(MAP.MapError):
                    self.validate()

    def test_unsafe_path_forms_are_rejected(self):
        for value in ("../outside", "./local", "x/../y", "/absolute", "C:/root", "C:relative",
                      "\\server\\share", "x\\file", "https://example.com/x", "x//y", "x/",
                      "x%2fy", "x/file:stream", "x/con.txt", "x/NUL", "x/COM1",
                      "x/LPT9.md", "x/name.", "x/name ", "x/?file", "x/*.md", "x/\ud800"):
            with self.subTest(value=repr(value)):
                with self.assertRaises(MAP.MapError):
                    MAP.route(value, "fixture")

    def test_sensitive_and_generated_paths_are_rejected(self):
        for value in (".secrets/a.md", ".ssh/config", ".aws/config", ".azure/config",
                      ".gnupg/config", "secrets/a.md", "credentials/a.md", ".env", ".env.local", ".envrc",
                      "x/credentials.md", "x/credentials.toml", "x/credentials.txt", "x/credentials.custom", "x/secrets.yaml", "x/.netrc",
                      "x/.npmrc", "x/.pypirc", "x/id_rsa", "x/key.PEM", "x/key.key",
                      "x/key.pfx", "x/key.p12", "x/key.p8", "x/key.keystore", ".git/config",
                      "node_modules/a.md", "vendor/a.md", "models/a.md", "dist/a.md",
                      "build/a.md", "cache/a.md", ".venv/a.md", "coverage/a.md"):
            with self.subTest(value=value):
                with self.assertRaises(MAP.MapError):
                    MAP.route(value, "fixture")

    def test_project_scope_refuses_home_filesystem_root_and_sensitive_ancestor(self):
        for root in (os.path.expanduser("~"), Path(self.root.anchor), self.root / ".aws", self.root / ".env"):
            with self.subTest(root=str(root)):
                with self.assertRaises(MAP.MapError):
                    MAP.project_root(str(root))

    def test_root_and_parent_containment_are_enforced(self):
        self.data["project"]["root"] = "nested"
        with self.assertRaises(MAP.MapError):
            self.validate()
        self.data["project"]["root"] = "."
        self.data["subprojects"][2]["parent"] = "api"
        with self.assertRaises(MAP.MapError):
            self.validate()

    def test_parent_path_case_must_match_exactly_for_portable_containment(self):
        self.assertFalse(MAP.beneath("services/API/worker", "services/api"))
        self.assertTrue(MAP.beneath("services/api/worker", "services/api"))
        self.assertFalse(MAP.beneath("services/apiworker", "services/api"))

    def test_network_root_is_rejected_before_filesystem_access(self):
        with mock.patch.object(MAP, "inspect_path", side_effect=AssertionError("must not inspect network")):
            for root in ("\\\\server\\share\\project", "//server/share/project"):
                with self.assertRaises(MAP.MapError):
                    MAP.project_root(root)

    def test_unknown_self_and_cyclic_parents_are_rejected(self):
        for parent in ("unknown", "api", "worker"):
            with self.subTest(parent=parent):
                self.data["subprojects"][0]["parent"] = parent
                with self.assertRaises(MAP.MapError):
                    self.validate()

    def test_skills_workflows_and_sources_stay_in_own_scope(self):
        original = copy.deepcopy(self.data)
        for field, value in (("skill", ".ai/SKILL.md"), ("workflow", "web app/.ai/workflow.md"),
                             ("sources", ["README.md"])):
            self.data = copy.deepcopy(original)
            self.data["subprojects"][0][field] = value
            with self.assertRaises(MAP.MapError):
                self.validate()

    def test_duplicate_paths_files_and_sources_are_rejected(self):
        original = copy.deepcopy(self.data)
        self.data["subprojects"][2]["path"] = "services/API"
        with self.assertRaises(MAP.MapError):
            self.validate()
        self.data = copy.deepcopy(original)
        self.data["project"]["workflow"] = ".ai/skill.MD"
        with self.assertRaises(MAP.MapError):
            self.validate()
        self.data = copy.deepcopy(original)
        self.data["project"]["sources"] = ["README.md", "readme.MD"]
        with self.assertRaises(MAP.MapError):
            self.validate()

    def test_dependencies_reject_unknown_self_duplicates_and_cycles(self):
        original = copy.deepcopy(self.data)
        for values in (["unknown"], ["api"], ["worker", "worker"]):
            self.data = copy.deepcopy(original)
            self.data["subprojects"][0]["dependencies"] = values
            with self.assertRaises(MAP.MapError):
                self.validate()
        self.data = copy.deepcopy(original)
        self.data["subprojects"][0]["dependencies"] = ["web"]
        with self.assertRaisesRegex(MAP.MapError, "cycle"):
            self.validate()

    def test_json_duplicate_keys_bad_encoding_and_excessive_size_are_rejected(self):
        for raw in (b'{"schema_version":1,"schema_version":1}', b"\xff", b"{not json}", b" " * (MAP.MAX_BYTES + 1)):
            with self.subTest(raw=raw[:40]):
                (self.root / "project-map.json").write_bytes(raw)
                with self.assertRaises(MAP.MapError):
                    MAP.load_manifest(self.root, "project-map.json")

    def test_utf8_bom_manifest_is_accepted(self):
        (self.root / "project-map.json").write_bytes(b"\xef\xbb\xbf" + json.dumps(self.data).encode("utf-8"))
        self.assertEqual(MAP.load_manifest(self.root, "project-map.json"), self.data)

    def test_bad_manifest_path_is_rejected_without_read(self):
        with mock.patch.object(MAP.os, "open", side_effect=AssertionError("must not open")):
            for path in ("../outside.json", "https://example.com/map.json", ".secrets/map.json", "credentials.txt", ".envrc"):
                with self.assertRaises(MAP.MapError):
                    MAP.load_manifest(self.root, path)

    def test_node_and_source_count_limits(self):
        self.data["subprojects"] *= MAP.MAX_NODES
        with self.assertRaises(MAP.MapError):
            self.validate()
        self.data["subprojects"] = []
        self.data["project"]["sources"] = ["README.md"] * 101
        with self.assertRaises(MAP.MapError):
            self.validate()

    def test_routes_cannot_be_directories_or_have_file_parents(self):
        self.data["project"]["main_skill"] = ".ai"
        with self.assertRaises(MAP.MapError):
            self.validate()
        self.data["project"]["main_skill"] = "README.md/SKILL.md"
        with self.assertRaises(MAP.MapError):
            self.validate()

    def test_sensitive_source_paths_are_rejected_before_their_contents_are_read(self):
        for source in ("credentials.txt", "credentials.custom", ".envrc"):
            self.write(source, "fixture, not a real secret\n")
            self.data["project"]["sources"] = [source]
            with mock.patch.object(MAP.os, "open", side_effect=AssertionError("must not open source")):
                with self.assertRaises(MAP.MapError):
                    self.validate()

    def test_windows_junction_and_reparse_attributes_are_rejected(self):
        self.assertTrue(MAP.is_link(SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)))
        self.assertTrue(MAP.is_link(SimpleNamespace(st_mode=stat.S_IFLNK, st_file_attributes=0)))
        self.assertFalse(MAP.is_link(SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0)))
        actual = Path.lstat
        def reparse_lstat(path, *args, **kwargs):
            if path == self.root / "services":
                return SimpleNamespace(st_mode=stat.S_IFDIR, st_file_attributes=0x400)
            return actual(path, *args, **kwargs)
        with mock.patch.object(Path, "lstat", reparse_lstat):
            with self.assertRaisesRegex(MAP.MapError, "reparse"):
                self.validate()

    def make_symlink(self, link, target, directory=False):
        try:
            os.symlink(str(target), str(link), target_is_directory=directory)
        except (OSError, NotImplementedError) as exc:
            self.skipTest("OS symlink creation unavailable: {}".format(type(exc).__name__))

    def test_actual_linked_source_manifest_and_root_are_rejected(self):
        self.make_symlink(self.root / "linked.md", self.root / "README.md")
        self.data["project"]["sources"] = ["linked.md"]
        with self.assertRaisesRegex(MAP.MapError, "symlink"):
            self.validate()
        self.make_symlink(self.root / "linked.json", self.root / "project-map.json")
        with self.assertRaisesRegex(MAP.MapError, "symlink"):
            MAP.load_manifest(self.root, "linked.json")
        alias = self.root.parent / "alias"
        self.make_symlink(alias, self.root, directory=True)
        with self.assertRaisesRegex(MAP.MapError, "symlink"):
            MAP.project_root(str(alias))

    def test_actual_linked_output_parent_is_rejected(self):
        outside = self.root.parent / "outside"
        outside.mkdir()
        self.make_symlink(self.root / "linked", outside, directory=True)
        status, _, errors = self.invoke("render", "--output-dir", "linked/preview")
        self.assertEqual(status, 2)
        self.assertIn("symlink", errors)
        self.assertEqual(list(outside.iterdir()), [])

    def test_markdown_and_mermaid_labels_are_escaped(self):
        self.data["project"]["name"] = '[label](javascript:alert(1)) <img src="x"> `code`'
        nodes, missing = self.validate()
        rendered = MAP.render_navigation(nodes, self.root, self.root / "preview", missing)
        self.assertNotIn('<img src="x">', rendered["project-map.md"])
        self.assertNotIn('[label](javascript:alert(1))', rendered["project-map.md"])
        self.assertIn("&#34;", rendered["project-mindmap.mmd"])
        self.assertNotIn('<img src="x">', rendered["project-mindmap.mmd"])

    def test_mermaid_reserved_words_are_encoded_as_safe_node_ids(self):
        original = copy.deepcopy(self.data)
        self.data["subprojects"] = []
        self.data["project"]["id"] = "end"
        nodes, missing = self.validate()
        rendered = MAP.render_navigation(nodes, self.root, self.root / "preview", missing)
        self.assertIn('node_end["', rendered["project-mindmap.mmd"])
        self.assertIn('node_end["', rendered["project-dependencies.mmd"])
        self.assertEqual(MAP.mermaid_id("a-b"), "node_a_b")
        self.data = original
        self.data["subprojects"][0]["id"] = "end"
        self.data["subprojects"][1]["parent"] = "end"
        self.data["subprojects"][2]["dependencies"] = ["end"]
        nodes, missing = self.validate()
        rendered = MAP.render_navigation(nodes, self.root, self.root / "preview", missing)
        self.assertIn('node_end["', rendered["project-mindmap.mmd"])
        self.assertIn("node_end --> node_web", rendered["project-dependencies.mmd"])

    def test_unknown_keys_and_os_errors_do_not_echo_untrusted_values(self):
        self.data["\x1b[31msecret-value"] = "sensitive"
        self.save()
        status, _, errors = self.invoke("check")
        self.assertEqual(status, 2)
        self.assertNotIn("secret-value", errors)
        self.assertNotIn("sensitive", errors)
        with mock.patch.object(MAP, "load_manifest", side_effect=OSError(13, "secret fixture path")):
            status, _, errors = self.invoke("check")
        self.assertEqual(status, 2)
        self.assertIn("errno 13", errors)
        self.assertNotIn("secret fixture", errors)


    def test_navigation_entry_contains_matching_renderable_diagrams(self):
        nodes, missing = self.validate()
        rendered = MAP.render_navigation(nodes, self.root, self.root / "preview", missing)
        entry = rendered["project-map.md"]
        for filename in ("project-mindmap.mmd", "project-dependencies.mmd"):
            self.assertIn("```mermaid\n" + rendered[filename] + "```", entry)
        self.assertIn("```text\n" + rendered["project-tree.txt"] + "```", entry)


if __name__ == "__main__":
    unittest.main()
