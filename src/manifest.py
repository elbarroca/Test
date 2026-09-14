"""Validate the small JSON format used by this repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping


def validate_manifest(data: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a manifest, or an empty list."""
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        return ["cases must be a non-empty list"]

    errors: list[str] = []
    names: set[str] = set()
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            errors.append(f"cases[{index}] must be an object")
            continue

        name = case.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"cases[{index}].name must be a non-empty string")
        elif name.strip() in names:
            errors.append(f"cases[{index}].name is duplicated: {name.strip()}")
        else:
            names.add(name.strip())

        for field in ("input", "expected"):
            if field not in case:
                errors.append(f"cases[{index}] is missing {field}")

    return errors


def load_manifest(path: str | Path) -> dict[str, Any]:
    """Load one JSON manifest from disk."""
    if str(path) == "-":
        data = json.load(sys.stdin)
    else:
        with Path(path).open(encoding="utf-8") as handle:
            data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("manifest root must be an object")
    return data


def result_payload(data: Mapping[str, Any], errors: list[str]) -> dict[str, Any]:
    """Build the stable payload emitted by the JSON output mode."""
    cases = data.get("cases")
    return {
        "valid": not errors,
        "errors": errors,
        "case_count": len(cases) if isinstance(cases, list) else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="JSON manifest to validate")
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="emit JSON output"
    )
    args = parser.parse_args()

    try:
        data = load_manifest(args.path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        if args.json_output:
            print(json.dumps({"valid": False, "errors": [str(error)], "case_count": 0}))
            return 1
        print(f"invalid manifest: {error}")
        return 1

    errors = validate_manifest(data)
    if args.json_output:
        print(json.dumps(result_payload(data, errors)))
        return 0 if not errors else 1

    if errors:
        for error in errors:
            print(f"error: {error}")
        return 1

    cases = data["cases"]
    print(f"valid manifest: {len(cases)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
