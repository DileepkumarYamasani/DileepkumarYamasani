from __future__ import annotations

from lighting_scene_builder_houdini.core.models import ShotContext


class ContextError(ValueError):
    """Raised when shot/task context is invalid."""


def resolve_shot_context(project: str, sequence: str, shot: str, step_code: str) -> ShotContext:
    values = {
        "project": project,
        "sequence": sequence,
        "shot": shot,
        "step_code": step_code,
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise ContextError(f"Missing required context keys: {', '.join(missing)}")

    if step_code.lower() != "light":
        raise ContextError(f"Tool is restricted to lighting tasks. Received step_code={step_code!r}")

    return ShotContext(project=project, sequence=sequence, shot=shot, step_code=step_code.lower())
