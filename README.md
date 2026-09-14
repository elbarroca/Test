# Test

Test is a small, dependency-free validator for JSON test manifests. It keeps
test cases easy to review and catches missing, empty, or duplicate case names
before a test run starts.

## Run it

```sh
python -m unittest discover -s tests -v
python -m src.manifest examples/manifest.json
```

## Manifest format

```json
{
  "cases": [
    {"name": "addition", "input": [2, 3], "expected": 5}
  ]
}
```

Each case needs a non-empty unique `name`, plus `input` and `expected` fields.
