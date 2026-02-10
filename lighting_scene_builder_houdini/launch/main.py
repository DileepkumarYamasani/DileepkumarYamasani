from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from lighting_scene_builder_houdini.core.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Houdini Lighting Scene Builder launcher")
    parser.add_argument("--project", required=True)
    parser.add_argument("--sequence", required=True)
    parser.add_argument("--shot", required=True)
    parser.add_argument("--step", default="light")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--assets", nargs="+", required=True, help="Asset names to include")
    parser.add_argument("--variant-quality", default=None, choices=["low", "medium", "high"])
    parser.add_argument("--variant-lod", default=None, choices=["lodA", "lodB"])
    parser.add_argument("--config", type=Path, default=None)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    variant_overrides = {}
    if args.variant_quality:
        variant_overrides["quality"] = args.variant_quality
    if args.variant_lod:
        variant_overrides["lod"] = args.variant_lod

    result = run_pipeline(
        project=args.project,
        sequence=args.sequence,
        shot=args.shot,
        step_code=args.step,
        data_dir=args.data_dir,
        selected_assets=args.assets,
        variant_overrides=variant_overrides,
        config_path=args.config,
    )

    payload = {
        "context": asdict(result.package.context),
        "metadata": result.package.metadata,
        "compounds": [
            {
                "asset_name": compound.asset_name,
                "variant": compound.variant,
                "components": [
                    {
                        "step": component.step,
                        "publish_type": component.publish_type,
                        "version": component.version,
                        "file_path": str(component.file_path),
                    }
                    for component in compound.components
                ],
            }
            for compound in result.package.compounds
        ],
        "load_result": result.load_result,
    }

    print(json.dumps(payload, indent=2, default=str))


if __name__ == "__main__":
    main()
