from __future__ import annotations

from pathlib import Path

import pytest

from lighting_scene_builder_houdini.core.context import ContextError, resolve_shot_context
from lighting_scene_builder_houdini.core.pipeline import run_pipeline
from lighting_scene_builder_houdini.core.validation import ValidationError
from lighting_scene_builder_houdini.data.generate_dummy_data import generate_dummy_data


@pytest.fixture()
def dummy_data_dir(tmp_path: Path) -> Path:
    generate_dummy_data(tmp_path, "PRJ")
    return tmp_path


def test_context_rejects_non_lighting_step() -> None:
    with pytest.raises(ContextError):
        resolve_shot_context("PRJ", "SQ010", "SH010", "comp")


def test_pipeline_happy_path(dummy_data_dir: Path) -> None:
    result = run_pipeline(
        project="PRJ",
        sequence="SQ010",
        shot="SH010",
        step_code="light",
        data_dir=dummy_data_dir,
        selected_assets=["carA", "treeA"],
        variant_overrides={"quality": "high"},
    )

    assert result.package.context.shot == "SH010"
    assert len(result.package.compounds) == 2
    assert result.load_result["mode"] in {"dry_run", "houdini"}


def test_pipeline_rejects_unknown_asset(dummy_data_dir: Path) -> None:
    with pytest.raises(ValidationError):
        run_pipeline(
            project="PRJ",
            sequence="SQ010",
            shot="SH010",
            step_code="light",
            data_dir=dummy_data_dir,
            selected_assets=["ghostAsset"],
            variant_overrides={},
        )


def test_pipeline_rejects_invalid_variant(dummy_data_dir: Path) -> None:
    with pytest.raises(ValidationError):
        run_pipeline(
            project="PRJ",
            sequence="SQ010",
            shot="SH010",
            step_code="light",
            data_dir=dummy_data_dir,
            selected_assets=["carA"],
            variant_overrides={"quality": "ultra"},
        )
