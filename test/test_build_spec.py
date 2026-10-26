"""Regression tests for dynamically imported modules in the frozen app."""

from pathlib import Path
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
