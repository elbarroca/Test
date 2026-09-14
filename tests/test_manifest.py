from io import StringIO
import unittest
from unittest.mock import patch

from src.manifest import load_manifest, validate_manifest


class ValidateManifestTests(unittest.TestCase):
    def test_accepts_complete_unique_cases(self) -> None:
        manifest = {
            "cases": [
                {"name": "addition", "input": [2, 3], "expected": 5},
                {"name": "empty", "input": [], "expected": 0},
            ]
        }

        self.assertEqual(validate_manifest(manifest), [])

    def test_reports_invalid_case_shape(self) -> None:
        manifest = {
            "cases": [
                {"name": "same", "input": 1},
                {"name": " same ", "expected": 2},
                "not an object",
            ]
        }

        self.assertEqual(
            validate_manifest(manifest),
            [
                "cases[0] is missing expected",
                "cases[1].name is duplicated: same",
                "cases[1] is missing input",
                "cases[2] must be an object",
            ],
        )

    def test_requires_cases(self) -> None:
        self.assertEqual(validate_manifest({}), ["cases must be a non-empty list"])

    def test_loads_manifest_from_standard_input(self) -> None:
        content = '{"cases": [{"name": "piped", "input": 1, "expected": 1}]}'

        with patch("src.manifest.sys.stdin", StringIO(content)):
            self.assertEqual(
                load_manifest("-"),
                {"cases": [{"name": "piped", "input": 1, "expected": 1}]},
            )


if __name__ == "__main__":
    unittest.main()
