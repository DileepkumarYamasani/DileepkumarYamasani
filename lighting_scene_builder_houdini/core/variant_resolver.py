from __future__ import annotations

from collections import defaultdict

from lighting_scene_builder_houdini.core.models import PublishRecord
from lighting_scene_builder_houdini.core.validation import ValidationError


def resolve_variants(
    publishes: list[PublishRecord],
    variant_overrides: dict[str, str],
    config: dict,
) -> list[PublishRecord]:
    allowed_variants = config.get("variants", {})
    defaults = config.get("default_variant", {})

    final_variant_values = dict(defaults)
    final_variant_values.update(variant_overrides)

    for key, value in final_variant_values.items():
        allowed_values = allowed_variants.get(key)
        if allowed_values is None:
            raise ValidationError(f"Unknown variant key: {key}")
        if value not in allowed_values:
            raise ValidationError(f"Invalid variant value {value!r} for key={key}. Allowed={allowed_values}")

    # map generic "quality" variant choice to publish.variant directly
    desired_publish_variant = final_variant_values.get("quality")

    grouped: dict[tuple[str, str], list[PublishRecord]] = defaultdict(list)
    for pub in publishes:
        grouped[(pub.asset_name, pub.step)].append(pub)

    resolved: list[PublishRecord] = []
    for key, records in grouped.items():
        matching = [record for record in records if record.variant == desired_publish_variant]
        if matching:
            resolved.append(max(matching, key=lambda item: item.version))
        else:
            resolved.append(max(records, key=lambda item: item.version))

    return resolved
