from __future__ import annotations

import sqlite3
from pathlib import Path

from lighting_scene_builder_houdini.core.models import AssetTask, PublishRecord, ShotContext


class DataLoader:
    def __init__(self, data_dir: Path, project: str) -> None:
        self.tasks_db = data_dir / f"{project}_tasks.db"
        self.publishes_db = data_dir / f"{project}_published_files.db"

    def _connect(self, db_path: Path) -> sqlite3.Connection:
        if not db_path.exists():
            raise FileNotFoundError(f"Missing database: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def load_shot_assets(self, context: ShotContext) -> list[AssetTask]:
        query = """
        SELECT asset_name, task_name, step
        FROM tasks
        WHERE project = ? AND sequence = ? AND shot = ?
        ORDER BY asset_name ASC
        """
        with self._connect(self.tasks_db) as conn:
            rows = conn.execute(query, (context.project, context.sequence, context.shot)).fetchall()
        return [AssetTask(asset_name=r["asset_name"], task_name=r["task_name"], step=r["step"]) for r in rows]

    def load_publishes_for_assets(self, context: ShotContext, assets: list[str], max_versions: int = 3) -> list[PublishRecord]:
        if not assets:
            return []
        placeholders = ",".join("?" for _ in assets)
        query = f"""
        SELECT asset_name, step, publish_type, variant, version, file_path
        FROM publishes
        WHERE project = ? AND sequence = ? AND shot = ?
          AND asset_name IN ({placeholders})
        ORDER BY asset_name, step, publish_type, variant, version DESC
        """
        params: list[str] = [context.project, context.sequence, context.shot, *assets]
        with self._connect(self.publishes_db) as conn:
            rows = conn.execute(query, params).fetchall()

        grouped: dict[tuple[str, str, str, str], list[PublishRecord]] = {}
        for row in rows:
            key = (row["asset_name"], row["step"], row["publish_type"], row["variant"])
            grouped.setdefault(key, []).append(
                PublishRecord(
                    asset_name=row["asset_name"],
                    step=row["step"],
                    publish_type=row["publish_type"],
                    variant=row["variant"],
                    version=row["version"],
                    file_path=Path(row["file_path"]),
                )
            )

        filtered: list[PublishRecord] = []
        for records in grouped.values():
            filtered.extend(records[:max_versions])
        return filtered
