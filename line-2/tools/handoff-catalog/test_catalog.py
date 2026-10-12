#!/usr/bin/env python3
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("catalog_under_test", ROOT / "line-2/tools/handoff-catalog/catalog.py")
catalog = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(catalog)


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.cwd = Path.cwd()
        scratch = ROOT / "test" / "scratch"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = Path(tempfile.mkdtemp(dir=scratch))
        self.addCleanup(shutil.rmtree, self.temp)
        self.a = self.temp / "a.zip"
        self.b = self.temp / "b.zip"
        producer = catalog.importlib.util.spec_from_file_location(
            "catalog_test_producer", ROOT / "line-2/tools/handoff/handoff.py")
        module = catalog.importlib.util.module_from_spec(producer)
        producer.loader.exec_module(module)
        self.a.write_bytes(module.build({"one.txt": b"one\n"}))
        self.b.write_bytes(module.build({"two.txt": b"two\n"}))

    def rel(self, path):
        return path.relative_to(self.cwd).as_posix()

    def test_build_is_sorted_and_replayable(self):
        value = catalog.build([self.rel(self.b), self.rel(self.a)])
        self.assertEqual([x["path"] for x in value["archives"]], [self.rel(self.a), self.rel(self.b)])
        self.assertTrue(catalog.verify(catalog.canonical(value))["verified"])

    def test_same_inputs_are_deterministic(self):
        self.assertEqual(catalog.canonical(catalog.build([self.rel(self.a)])),
                         catalog.canonical(catalog.build([self.rel(self.a)])))

    def test_duplicate_archive_is_refused(self):
        with self.assertRaisesRegex(ValueError, "distinct"):
            catalog.build([self.rel(self.a), self.rel(self.a)])

    def test_changed_archive_is_refused(self):
        data = catalog.canonical(catalog.build([self.rel(self.a)]))
        self.a.write_bytes(b"not a handoff")
        with self.assertRaises(ValueError):
            catalog.verify(data)

    def test_noncanonical_catalog_is_refused(self):
        value = catalog.build([self.rel(self.a)])
        data = json.dumps(value, indent=2).encode() + b"\n"
        with self.assertRaisesRegex(ValueError, "canonical"):
            catalog.verify(data)

    def test_duplicate_json_key_is_refused(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            catalog.parse_catalog(b'{"format":"handoff-catalog-v1","format":"x","archives":[]}\n')

    def test_outside_path_is_refused(self):
        with self.assertRaisesRegex(ValueError, "relative"):
            catalog.workspace_file("../outside.zip")

    def test_empty_archive_list_is_refused(self):
        with self.assertRaisesRegex(ValueError, "at least"):
            catalog.build([])

    def test_canonical_requires_lowercase_digest(self):
        value = catalog.build([self.rel(self.a)])
        value["archives"][0]["sha256"] = value["archives"][0]["sha256"].upper()
        with self.assertRaises(ValueError):
            catalog.parse_catalog(catalog.canonical(value))


if __name__ == "__main__":
    unittest.main()
