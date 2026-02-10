from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def generate_dummy_data(out_dir: Path, project: str) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    tasks_db = out_dir / f"{project}_tasks.db"
    publishes_db = out_dir / f"{project}_published_files.db"

    _create_tasks_db(tasks_db)
    _create_publishes_db(publishes_db)

    return {"tasks_db": tasks_db, "publishes_db": publishes_db}


def _create_tasks_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS tasks")
        conn.execute(
            """
            CREATE TABLE tasks (
                project TEXT,
                sequence TEXT,
                shot TEXT,
                asset_name TEXT,
                task_name TEXT,
                step TEXT
            )
            """
        )
        rows = [
            ("PRJ", "SQ010", "SH010", "carA", "car_model", "geo"),
            ("PRJ", "SQ010", "SH010", "carA", "car_lookdev", "material"),
            ("PRJ", "SQ010", "SH010", "carA", "car_rig", "rig"),
            ("PRJ", "SQ010", "SH010", "treeA", "tree_model", "geo"),
            ("PRJ", "SQ010", "SH010", "treeA", "tree_lookdev", "material"),
            ("PRJ", "SQ010", "SH010", "treeA", "tree_rig", "rig"),
        ]
        conn.executemany("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?)", rows)


def _create_publishes_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS publishes")
        conn.execute(
            """
            CREATE TABLE publishes (
                project TEXT,
                sequence TEXT,
                shot TEXT,
                asset_name TEXT,
                step TEXT,
                publish_type TEXT,
                variant TEXT,
                version INTEGER,
                file_path TEXT
            )
            """
        )
        rows = []
        for asset in ("carA", "treeA"):
            rows.extend(
                [
                    ("PRJ", "SQ010", "SH010", asset, "geo", "usd", "high", 3, f"/show/PRJ/assets/{asset}/geo/high/v003/model.usd"),
                    ("PRJ", "SQ010", "SH010", asset, "geo", "usd", "medium", 2, f"/show/PRJ/assets/{asset}/geo/medium/v002/model.usd"),
                    ("PRJ", "SQ010", "SH010", asset, "material", "usd", "high", 5, f"/show/PRJ/assets/{asset}/look/high/v005/look.usd"),
                    ("PRJ", "SQ010", "SH010", asset, "material", "usd", "medium", 4, f"/show/PRJ/assets/{asset}/look/medium/v004/look.usd"),
                    ("PRJ", "SQ010", "SH010", asset, "rig", "abc", "high", 1, f"/show/PRJ/assets/{asset}/rig/high/v001/rig.abc"),
                ]
            )
        conn.executemany("INSERT INTO publishes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate local SQLite dummy data for scene builder")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--project", default="PRJ")
    args = parser.parse_args()

    result = generate_dummy_data(args.out_dir, args.project)
    print(f"Generated tasks DB: {result['tasks_db']}")
    print(f"Generated publishes DB: {result['publishes_db']}")


if __name__ == "__main__":
    main()
