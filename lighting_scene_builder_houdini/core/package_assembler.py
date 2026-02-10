from __future__ import annotations

from datetime import datetime, timezone

from lighting_scene_builder_houdini.core.models import Compound, LightingPackage, ShotContext


def assemble_package(context: ShotContext, compounds: list[Compound]) -> LightingPackage:
    metadata = {
        "created_at_utc": datetime.now(tz=timezone.utc).isoformat(),
        "compound_count": len(compounds),
    }
    return LightingPackage(context=context, compounds=compounds, metadata=metadata)
