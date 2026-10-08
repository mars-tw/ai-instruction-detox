"""Check the deliverable's resource links and migration contract."""
import csv
from pathlib import Path
import re
import unittest
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]


class PackageContractTests(unittest.TestCase):
    def test_instruction_resource_links_exist(self):
        sources = [ROOT / "SKILL.md"] + sorted((ROOT / "references").glob("*.md"))
        for source in sources:
            # Code examples can intentionally contain hypothetical paths.
            text = re.sub(r"^```.*?^```[^\n]*", "", source.read_text(encoding="utf-8"),
                          flags=re.M | re.S)
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                target = unquote(target.split("#", 1)[0])
                with self.subTest(source=source.name, target=target):
                    self.assertTrue((source.parent / target).is_file(), "missing skill resource")

    def test_complete_output_template_set(self):
        for stem in ("00-scope-and-inventory", "02-conflicts-and-precedence",
                     "03-delete-merge-move", "04-target-architecture",
                     "05-validation", "06-rollback"):
            with self.subTest(stem=stem):
                self.assertTrue((ROOT / "templates" / (stem + ".template.md")).is_file())
        self.assertTrue((ROOT / "templates" / "baseline-manifest.template.json").is_file())

    def test_ledger_additive_schema_migration(self):
        with (ROOT / "templates" / "01-rule-ledger-header.csv").open(encoding="utf-8", newline="") as stream:
            header = next(csv.reader(stream))
        self.assertEqual(len(header), 28)
        self.assertEqual(len(set(header)), 28)
        self.assertEqual(header[-3:], ["strength", "exceptions", "dependencies"])
        self.assertEqual(header[0], "rule_id")
        self.assertEqual(header[24], "confidence")


if __name__ == "__main__":
    unittest.main()
