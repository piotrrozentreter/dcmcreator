"""Exercise Windows batch packaging without rebuilding the application."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(
    os.name == "nt" and shutil.which("powershell"),
    "Windows cmd and PowerShell are required",
)
class TestBuildBatch(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="build packaging ")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        script = (PROJECT_ROOT / "build.bat").read_text()
        packaging = script[script.index("REM Create ZIP using PowerShell"):]
        self.script = self.root / "package.bat"
        self.script.write_text(
            "@echo off\nsetlocal enabledelayedexpansion\n" + packaging
        )
        self.archive = self.root / "DICOM Creator.zip"

    def create_distribution(self):
        distribution = self.root / "dist" / "DICOM Creator"
        distribution.mkdir(parents=True)
        (distribution / "DICOM Creator.exe").write_bytes(b"new executable")
        internal = distribution / "_internal"
        internal.mkdir()
        (internal / "resource.txt").write_text("resource")

    def run_packaging(self):
        return subprocess.run(
            [os.environ.get("COMSPEC", "cmd.exe"), "/d", "/c", str(self.script)],
            cwd=self.root,
            input="\n\n",
            capture_output=True,
            text=True,
            timeout=60,
        )

    def assert_packaged(self, result):
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 0, output)
        self.assertIn("Build completed successfully", output)
        self.assertIn("ZIP file size:", output)
        self.assertNotIn("unexpected at this time", output)
        with zipfile.ZipFile(self.archive) as archive:
            self.assertEqual(
                archive.read("DICOM Creator.exe"), b"new executable"
            )
            self.assertEqual(archive.read("_internal/resource.txt"), b"resource")

    def test_creates_new_archive(self):
        self.create_distribution()
        self.assert_packaged(self.run_packaging())

    def test_replaces_existing_archive(self):
        self.create_distribution()
        self.archive.write_bytes(b"old archive")
        self.assert_packaged(self.run_packaging())

    def test_failed_packaging_preserves_existing_archive(self):
        self.archive.write_bytes(b"old archive")
        result = self.run_packaging()
        self.assert_packaging_failed(result)

    def test_locked_archive_reports_failure_and_cleans_temporary_zip(self):
        self.create_distribution()
        self.archive.write_bytes(b"old archive")
        with self.archive.open("rb"):
            result = self.run_packaging()
        self.assert_packaging_failed(result, has_distribution=True)

    def assert_packaging_failed(self, result, has_distribution=False):
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("ZIP creation failed", output)
        self.assertNotIn("Build completed successfully", output)
        self.assertNotIn("unexpected at this time", output)
        self.assertEqual(self.archive.read_bytes(), b"old archive")
        expected = {"package.bat", "DICOM Creator.zip"}
        if has_distribution:
            expected.add("dist")
        self.assertEqual({path.name for path in self.root.iterdir()}, expected)


if __name__ == "__main__":
    unittest.main()
