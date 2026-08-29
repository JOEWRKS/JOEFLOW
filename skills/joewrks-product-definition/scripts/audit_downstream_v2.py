"""Installed entry point for dependency-scoped downstream V2 audit."""

import sys
from pathlib import Path


_SKILL_ROOT = Path(__file__).resolve().parents[1]
_SCRIPTS_ROOT = _SKILL_ROOT / "scripts"
for _root in (_SKILL_ROOT, _SCRIPTS_ROOT):
    if str(_root) not in sys.path:
        sys.path.insert(0, str(_root))

from downstream_v2.audit import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
