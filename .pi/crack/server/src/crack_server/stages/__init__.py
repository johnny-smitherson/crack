"""Stage registry: auto-discovers sNN_*.py modules in this package.

Each module must define a module-level ``STAGE = <Stage subclass instance>()``.
The filename supplies the order (s01 → 1) and must agree with ``STAGE.slug``
(s02_plan.py → slug "plan"). Home page and task page iterate REGISTRY — nothing
hard-codes a specific stage.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

from crack_server.stages.base import Part, Stage

_STAGE_FILE_RE = re.compile(r"^s(\d\d)_([a-z0-9_]+)\.py$")


def _discover() -> list[Stage]:
    stages: list[Stage] = []
    for path in sorted(Path(__file__).resolve().parent.glob("s??_*.py")):
        match = _STAGE_FILE_RE.match(path.name)
        if not match:
            continue
        order, slug = int(match.group(1)), match.group(2)
        module = importlib.import_module(f"crack_server.stages.{path.stem}")
        stage = getattr(module, "STAGE", None)
        if not isinstance(stage, Stage):
            raise RuntimeError(f"{path.name}: missing module-level STAGE = <Stage>()")
        if stage.slug != slug:
            raise RuntimeError(
                f"{path.name}: filename slug {slug!r} != STAGE.slug {stage.slug!r}"
            )
        stage.order = order
        stages.append(stage)
    return sorted(stages, key=lambda s: s.order)


REGISTRY: list[Stage] = _discover()


def get(slug: str) -> Stage | None:
    for stage in REGISTRY:
        if stage.slug == slug:
            return stage
    return None


__all__ = ["Part", "Stage", "REGISTRY", "get"]
