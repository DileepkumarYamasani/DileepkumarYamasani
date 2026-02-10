from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


DEFAULT_FILTER_PATH = Path(__file__).with_name("scene_builder_filters.yaml")


def load_filter_config(path: Path | None = None) -> dict[str, Any]:
    target = path or DEFAULT_FILTER_PATH
    if yaml is None:
        return _fallback_default_config()
    with target.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _fallback_default_config() -> dict[str, Any]:
    return {
        "allowed_step": "light",
        "required_components": ["geo", "material", "rig"],
        "allowed_publish_types": {
            "geo": ["bgeo", "usd"],
            "material": ["usd", "ass"],
            "rig": ["abc", "usd"],
        },
        "allowed_extensions": {
            "bgeo": [".bgeo.sc", ".bgeo"],
            "usd": [".usd", ".usda", ".usdc"],
            "ass": [".ass"],
            "abc": [".abc"],
        },
        "variants": {
            "quality": ["low", "medium", "high"],
            "lod": ["lodA", "lodB"],
        },
        "default_variant": {"quality": "high", "lod": "lodA"},
        "max_versions_per_component": 3,
    }
