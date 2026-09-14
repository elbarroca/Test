import json
from contextlib import redirect_stdout
from io import StringIO
import unittest
from unittest.mock import patch

from src.manifest import load_manifest, main, validate_manifest


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

    def test_json_output_reports_valid_manifest(self) -> None:
        output = StringIO()
        with patch("sys.argv", ["manifest", "--json", "-"]), patch(
            "src.manifest.sys.stdin",
            StringIO('{"cases": [{"name": "piped", "input": 1, "expected": 1}]}'),
        ), redirect_stdout(output):
            exit_code = main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(
            json.loads(output.getvalue()),
            {"valid": True, "errors": [], "case_count": 1},
        )

    def test_json_output_reports_errors(self) -> None:
        output = StringIO()
        with patch("sys.argv", ["manifest", "--json", "-"]), patch(
            "src.manifest.sys.stdin",
            StringIO('{"cases": [{"name": "missing-input", "expected": 1}]}'),
        ), redirect_stdout(output):
            exit_code = main()

        self.assertEqual(exit_code, 1)
        self.assertEqual(
            json.loads(output.getvalue()),
            {
                "valid": False,
                "errors": ["cases[0] is missing input"],
                "case_count": 1,
            },
        )


if __name__ == "__main__":
    unittest.main()
