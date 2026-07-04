"""Validate all conformance fixtures against protocol schemas.

Exits 0 on success, 1 on failure. Used by the Taskfile `schema:validate` target
and imported by the pytest conformance test.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema
from jsonschema import ValidationError

REPO_ROOT = Path(__file__).parent.parent
SCHEMA_DIR = REPO_ROOT / "protocol" / "schema"
CONFORMANCE_DIR = REPO_ROOT / "tests" / "conformance"

TREESPEC_SCHEMA_PATH = SCHEMA_DIR / "treespec.schema.json"
RPC_SCHEMA_PATH = SCHEMA_DIR / "rpc.schema.json"


def _load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _make_validator(schema: dict) -> jsonschema.Validator:
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    return validator_cls(schema)


def validate_treespec_fixtures(
    conformance_dir: Path = CONFORMANCE_DIR,
    schema_path: Path = TREESPEC_SCHEMA_PATH,
) -> list[str]:
    """Validate every .json file in conformance_dir against the treespec schema.

    Returns a list of error strings. Empty means all passed.
    """
    schema = _load_json(schema_path)
    validator = _make_validator(schema)

    fixtures = sorted(conformance_dir.glob("*.json"))
    if not fixtures:
        return [f"No conformance fixtures found in {conformance_dir}"]

    errors: list[str] = []
    for fixture_path in fixtures:
        instance = _load_json(fixture_path)
        try:
            validator.validate(instance)
        except ValidationError as exc:
            errors.append(f"{fixture_path.name}: {exc.message} (path: {list(exc.absolute_path)})")

    return errors


def validate_rpc_schema(schema_path: Path = RPC_SCHEMA_PATH) -> list[str]:
    """Check that rpc.schema.json is itself a valid schema.

    Returns a list of error strings. Empty means valid.
    """
    schema = _load_json(schema_path)
    errors: list[str] = []
    try:
        _make_validator(schema)
    except jsonschema.exceptions.SchemaError as exc:
        errors.append(f"rpc.schema.json is invalid: {exc.message}")
    return errors


def main() -> int:
    passed = 0
    failed = 0

    print(f"Treespec schema: {TREESPEC_SCHEMA_PATH.relative_to(REPO_ROOT)}")
    print(f"RPC schema:      {RPC_SCHEMA_PATH.relative_to(REPO_ROOT)}")
    print(f"Fixtures:        {CONFORMANCE_DIR.relative_to(REPO_ROOT)}/")
    print()

    rpc_errors = validate_rpc_schema()
    if rpc_errors:
        for msg in rpc_errors:
            print(f"  FAIL  {msg}")
            failed += 1
    else:
        print("  PASS  rpc.schema.json (meta-valid)")
        passed += 1

    fixtures = sorted(CONFORMANCE_DIR.glob("*.json"))
    treespec_schema = _load_json(TREESPEC_SCHEMA_PATH)
    validator = _make_validator(treespec_schema)

    for fixture_path in fixtures:
        instance = _load_json(fixture_path)
        try:
            validator.validate(instance)
            print(f"  PASS  {fixture_path.name}")
            passed += 1
        except ValidationError as exc:
            print(f"  FAIL  {fixture_path.name}: {exc.message} (path: {list(exc.absolute_path)})")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
