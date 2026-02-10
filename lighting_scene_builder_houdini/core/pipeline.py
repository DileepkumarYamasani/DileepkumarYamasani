from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from lighting_scene_builder_houdini.config.filter_config import load_filter_config
from lighting_scene_builder_houdini.core.compound_builder import build_compounds
from lighting_scene_builder_houdini.core.context import resolve_shot_context
from lighting_scene_builder_houdini.core.db.data_loader import DataLoader
from lighting_scene_builder_houdini.core.models import LightingPackage
from lighting_scene_builder_houdini.core.package_assembler import assemble_package
from lighting_scene_builder_houdini.core.validation import validate_asset_selection, validate_publishes
from lighting_scene_builder_houdini.core.variant_resolver import resolve_variants
from lighting_scene_builder_houdini.integration.houdini.houdini_actions import load_lighting_scene


@dataclass(slots=True)
class PipelineResult:
    package: LightingPackage
    load_result: dict


def run_pipeline(
    *,
    project: str,
    sequence: str,
    shot: str,
    step_code: str,
    data_dir: Path,
    selected_assets: list[str],
    variant_overrides: dict[str, str],
    config_path: Path | None = None,
) -> PipelineResult:
    config = load_filter_config(config_path)

    context = resolve_shot_context(project=project, sequence=sequence, shot=shot, step_code=step_code)

    if context.step_code != config.get("allowed_step", "light"):
        raise ValueError(f"Configured allowed step is {config.get('allowed_step')}, got {context.step_code}")

    data_loader = DataLoader(data_dir=data_dir, project=project)
    available_tasks = data_loader.load_shot_assets(context)
    available_assets = sorted({task.asset_name for task in available_tasks})

    validate_asset_selection(selected_assets, available_assets)

    publishes = data_loader.load_publishes_for_assets(
        context,
        assets=selected_assets,
        max_versions=config.get("max_versions_per_component", 3),
    )

    validate_publishes(publishes, config)

    resolved = resolve_variants(publishes, variant_overrides=variant_overrides, config=config)
    compounds = build_compounds(resolved)
    package = assemble_package(context, compounds)

    load_result = load_lighting_scene(package)
    return PipelineResult(package=package, load_result=load_result)
