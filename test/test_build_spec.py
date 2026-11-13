"""Regression tests for dynamically imported modules in the frozen app."""

from pathlib import Path
from importlib.util import find_spec
import runpy
import tempfile
import unittest
from unittest.mock import MagicMock


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = PROJECT_ROOT / "dcmcreator.spec"


def load_analysis_options(project_root=PROJECT_ROOT):
    """Execute the spec with build operations mocked, without PyInstaller."""
    analysis = MagicMock()
    runpy.run_path(
        str(SPEC_PATH),
        init_globals={
            "SPECPATH": str(project_root),
            "Analysis": analysis,
            "PYZ": MagicMock(),
            "EXE": MagicMock(),
            "COLLECT": MagicMock(),
        },
    )
    return analysis.call_args.kwargs


class TestBuildSpec(unittest.TestCase):
    def test_third_party_hidden_imports_exist(self):
        options = load_analysis_options()
        for module in options["hiddenimports"]:
            if module.startswith(("pydicom.", "pynetdicom.", "PIL.", "numpy.")):
                with self.subTest(module=module):
                    self.assertIsNotNone(find_spec(module))

    def test_receiver_modules_are_hidden_imports(self):
        options = load_analysis_options()
        self.assertIn("dicom_receiver", options["hiddenimports"])
        self.assertIn("dicom_receiver_tab", options["hiddenimports"])

    def test_application_resources_and_documentation_are_bundled(self):
        options = load_analysis_options()
        resources = set(options["datas"])
        for resource in (("src", "src"), ("src/VR.xml", "src"),
                         ("README.md", "."), ("LICENSE", "."), ("doc", "doc")):
            with self.subTest(resource=resource):
                self.assertIn(resource, resources)
                self.assertTrue((PROJECT_ROOT / resource[0]).exists())
        self.assertTrue((PROJECT_ROOT / "doc" / "DICOM_RECEIVER.md").is_file())
        self.assertTrue((PROJECT_ROOT / "doc" / "CHANGELOG_v0.9.4.md").is_file())
        self.assertFalse(any("received_dicoms" in source for source, _ in resources))

    def test_storage_commitment_modules_are_hidden_imports(self):
        options = load_analysis_options()
        self.assertIn("storage_commitment_action", options["hiddenimports"])
        self.assertIn("storage_commitment", options["hiddenimports"])

    def test_all_application_modules_are_hidden_imports(self):
        options = load_analysis_options()
        modules = {
            path.stem
            for path in (PROJECT_ROOT / "src").glob("*.py")
            if path.stem != "__init__"
        }
        self.assertTrue(modules)
        self.assertFalse(modules - set(options["hiddenimports"]))

    def test_source_directory_is_on_analysis_path(self):
        options = load_analysis_options()
        self.assertIn(str(PROJECT_ROOT / "src"), options["pathex"])

    def test_new_modules_are_discovered_relative_to_spec(self):
        with tempfile.TemporaryDirectory() as directory:
            project_root = Path(directory)
            source = project_root / "src"
            source.mkdir()
            (source / "future_feature.py").touch()
            (source / "__init__.py").touch()
            options = load_analysis_options(project_root)

        self.assertIn("future_feature", options["hiddenimports"])
        self.assertNotIn("__init__", options["hiddenimports"])
        self.assertIn(str(source), options["pathex"])


if __name__ == "__main__":
    unittest.main()
