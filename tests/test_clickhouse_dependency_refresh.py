"""Verify the refreshed dependencies in each actual release payload."""

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "clickhouse_native_security", ROOT / "scripts/native_security.py"
)
SECURITY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SECURITY)
BASELINE = json.loads((ROOT / "scripts/native-security-baseline.json").read_text())
REFRESHED = {
    "github.com/ClickHouse/ch-go": ("v0.76.0", "v0.75.0"),
    "github.com/grpc-ecosystem/grpc-gateway/v2": ("v2.34.0", "v2.33.0"),
}


@pytest.mark.packaged
@pytest.mark.parametrize("target", ["linux-amd64", "linux-arm64"])
def test_actual_payload_links_refreshed_clickhouse_dependencies(target):
    actual = SECURITY.inspect_binary(ROOT / "bin" / target / "toolbox")
    SECURITY.check_floors(actual, BASELINE)
    for module, (expected, _) in REFRESHED.items():
        assert actual["modules"][module] == expected


@pytest.mark.parametrize("module", REFRESHED)
def test_prior_clickhouse_dependency_is_rejected(module):
    _, previous = REFRESHED[module]
    with pytest.raises(ValueError, match="module below security floor"):
        SECURITY.check_floors(
            {"go_version": "go1.27.4", "modules": {module: previous}, "module_gaps": []},
            BASELINE,
        )
