"""Schema conformance tests.

Each conformance fixture in tests/conformance/ must validate against
protocol/schema/treespec.schema.json. These tests are the executable proof
of INV-2/INV-5: a tree authored in Python must produce a structurally valid
spec that the Swift shim can materialize.
"""

import json
from pathlib import Path

import jsonschema
import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
SCHEMA_DIR = REPO_ROOT / "protocol" / "schema"
CONFORMANCE_DIR = REPO_ROOT / "tests" / "conformance"


def _load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _fixture_ids() -> list[str]:
    return [p.name for p in sorted(CONFORMANCE_DIR.glob("*.json"))]


@pytest.fixture(scope="module")
def treespec_validator() -> jsonschema.Validator:
    schema_path = SCHEMA_DIR / "treespec.schema.json"
    schema = _load_json(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)
    return validator_cls(schema)


@pytest.mark.unit
@pytest.mark.parametrize("fixture_name", _fixture_ids())
def test_fixture_validates(treespec_validator: jsonschema.Validator, fixture_name: str) -> None:
    """Each conformance fixture must satisfy the treespec schema."""
    fixture_path = CONFORMANCE_DIR / fixture_name
    instance = _load_json(fixture_path)
    treespec_validator.validate(instance)


@pytest.mark.unit
def test_treespec_schema_is_meta_valid() -> None:
    """The treespec schema must itself be a valid JSON Schema."""
    schema_path = SCHEMA_DIR / "treespec.schema.json"
    schema = _load_json(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)


@pytest.mark.unit
def test_rpc_schema_is_meta_valid() -> None:
    """The rpc schema must itself be a valid JSON Schema."""
    schema_path = SCHEMA_DIR / "rpc.schema.json"
    schema = _load_json(schema_path)
    validator_cls = jsonschema.validators.validator_for(schema)
    validator_cls.check_schema(schema)


@pytest.mark.unit
def test_conformance_dir_is_nonempty() -> None:
    """At least one conformance fixture must exist."""
    fixtures = list(CONFORMANCE_DIR.glob("*.json"))
    assert fixtures, f"No conformance fixtures found in {CONFORMANCE_DIR}"


@pytest.mark.unit
def test_all_node_types_covered() -> None:
    """Every node type defined in the architecture must appear in at least one fixture."""
    required_types = {
        "brew",
        "pkg",
        "sys",
        "jamf",
        "launch_daemon",
        "launch_agent",
        "customized",
        "anchor",
        "group",
    }
    found: set[str] = set()

    def _collect_types(node: object) -> None:
        if not isinstance(node, dict):
            return
        t = node.get("type")
        if isinstance(t, str):
            found.add(t)
        payload = node.get("payload", {})
        if isinstance(payload, dict):
            for child in payload.get("children", []):
                _collect_types(child)

    for fixture_path in CONFORMANCE_DIR.glob("*.json"):
        doc = _load_json(fixture_path)
        if isinstance(doc, dict):
            _collect_types(doc.get("root"))

    missing = required_types - found
    assert not missing, f"Node types with no fixture coverage: {sorted(missing)}"
