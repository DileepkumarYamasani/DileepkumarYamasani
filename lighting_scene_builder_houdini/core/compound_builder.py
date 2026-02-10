from __future__ import annotations

from collections import defaultdict

from lighting_scene_builder_houdini.core.models import Compound, PublishRecord


def build_compounds(resolved_publishes: list[PublishRecord]) -> list[Compound]:
    grouped: dict[tuple[str, str], list[PublishRecord]] = defaultdict(list)
    for publish in resolved_publishes:
        grouped[(publish.asset_name, publish.variant)].append(publish)

    compounds: list[Compound] = []
    for (asset_name, variant), components in sorted(grouped.items(), key=lambda item: item[0]):
        compounds.append(Compound(asset_name=asset_name, variant=variant, components=components))
    return compounds
