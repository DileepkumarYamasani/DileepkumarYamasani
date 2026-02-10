from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ShotContext:
    project: str
    sequence: str
    shot: str
    step_code: str


@dataclass(slots=True)
class AssetTask:
    asset_name: str
    task_name: str
    step: str


@dataclass(slots=True)
class PublishRecord:
    asset_name: str
    step: str
    publish_type: str
    variant: str
    version: int
    file_path: Path


@dataclass(slots=True)
class Compound:
    asset_name: str
    variant: str
    components: list[PublishRecord]


@dataclass(slots=True)
class LightingPackage:
    context: ShotContext
    compounds: list[Compound] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
