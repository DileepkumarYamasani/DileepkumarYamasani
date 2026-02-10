from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from lighting_scene_builder_houdini.core.models import PublishRecord


class ValidationError(ValueError):
    """Raised when selected assets/components are invalid for assembly."""


def validate_asset_selection(requested_assets: list[str], available_assets: list[str]) -> None:
    missing = sorted(set(requested_assets) - set(available_assets))
    if missing:
        raise ValidationError(f"Selected assets do not exist in shot context: {missing}")


def validate_publishes(publishes: list[PublishRecord], config: dict) -> None:
    required_components = config.get("required_components", [])
    allowed_publish_types = config.get("allowed_publish_types", {})
    allowed_extensions = config.get("allowed_extensions", {})

    by_asset_component: dict[str, set[str]] = defaultdict(set)
    for pub in publishes:
        by_asset_component[pub.asset_name].add(pub.step)
        _validate_single_publish(pub, allowed_publish_types, allowed_extensions)

    for asset, present_steps in by_asset_component.items():
        missing_components = [component for component in required_components if component not in present_steps]
        if missing_components:
            raise ValidationError(f"Asset {asset} missing required components: {missing_components}")


def _validate_single_publish(
    publish: PublishRecord,
    allowed_publish_types: dict[str, list[str]],
    allowed_extensions: dict[str, list[str]],
) -> None:
    component_publish_types = allowed_publish_types.get(publish.step, [])
    if publish.publish_type not in component_publish_types:
        raise ValidationError(
            f"Invalid publish type for {publish.asset_name}:{publish.step}. "
            f"Got {publish.publish_type}, allowed={component_publish_types}"
        )

    valid_extensions = allowed_extensions.get(publish.publish_type, [])
    if not _path_has_allowed_extension(publish.file_path, valid_extensions):
        raise ValidationError(
            f"Invalid file extension for publish {publish.file_path}. "
            f"Expected one of {valid_extensions}"
        )


def _path_has_allowed_extension(path: Path, valid_extensions: list[str]) -> bool:
    normalized = str(path).lower()
    return any(normalized.endswith(ext.lower()) for ext in valid_extensions)
