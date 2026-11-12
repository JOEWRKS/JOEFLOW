#!/usr/bin/env python3
"""The JOEFLOW version a project uses, and the approval provenance log, in `joeflow-project.json`.

`state.json` follows the frozen 0.2.0 schema, which has no place for the
program version or for the user's approval words. Both live in a sidecar file
next to it:

    {
      "format": "joeflow-project/1",
      "joeflow_version": "1.7.0",
      "approvals": [
        {"revision": 43, "manifest_digest": "...", "definition_digest": "...",
         "approved_at": "...", "approved_at_source": "user_message",
         "quote": "이대로 승인", "relayed_from": null, "recorded_with": "1.7.0"}
      ]
    }

The sidecar is never Product Definition authority; the validators do not read it.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

PROJECT_FILE = "joeflow-project.json"
FORMAT = "joeflow-project/1"
_SKILL_DIR = Path(__file__).resolve().parents[1]


def running_version() -> str | None:
    """Version of the JOEFLOW skill these scripts belong to (skill VERSION file)."""
    for candidate in (_SKILL_DIR / "VERSION", _SKILL_DIR.parents[1] / "VERSION"):
        try:
            text = candidate.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if text:
            return text
    return None


def project_file(state_path: str | os.PathLike[str]) -> Path:
    return Path(state_path).resolve().with_name(PROJECT_FILE)


def read_project(state_path: str | os.PathLike[str]) -> dict[str, object] | None:
    path = project_file(state_path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"error": f"{PROJECT_FILE} is unreadable: {exc}"}
    return data if isinstance(data, dict) else {"error": f"{PROJECT_FILE} must be a JSON object"}


def write_project(state_path: str | os.PathLike[str], data: dict[str, object]) -> Path:
    path = project_file(state_path)
    data = {"format": FORMAT, **{k: v for k, v in data.items() if k != "format"}}
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)
    return path


def version_report(state_path: str | os.PathLike[str], state: dict[str, object] | None = None) -> dict[str, object]:
    """Running version, pinned version and a notice when they differ or no pin exists."""
    running = running_version()
    project = read_project(state_path)
    pinned = project.get("joeflow_version") if isinstance(project, dict) else None
    schema = state.get("schema_version") if isinstance(state, dict) else None
    notice = None
    if isinstance(project, dict) and "error" in project:
        notice = project["error"]
    elif pinned is None:
        notice = (
            f"this project does not record which JOEFLOW version it uses; running {running}. "
            f"Record it once with joeflow_version.py STATE_JSON --pin (writes {PROJECT_FILE} next to state.json) "
            "and use the scripts of that version"
        )
    elif pinned != running:
        notice = (
            f"this project pins JOEFLOW {pinned} but these scripts are {running}. "
            "Both read state schema 0.2.0, but a newer version may accept or build records the older one does not. "
            "Use the pinned version's scripts, or, if the project adopts this one, update the pin with "
            "joeflow_version.py STATE_JSON --pin and say so in the project notes"
        )
    return {
        "running_version": running,
        "pinned_version": pinned,
        "project_file": str(project_file(state_path)),
        "state_schema_version": schema,
        "notice": notice,
    }


def append_approval(state_path: str | os.PathLike[str], entry: dict[str, object]) -> Path:
    project = read_project(state_path)
    if project is None:
        project = {"joeflow_version": None}
    elif "error" in project:
        raise ValueError(project["error"])
    approvals = list(project.get("approvals", [])) if isinstance(project.get("approvals"), list) else []
    approvals.append(entry)
    project["approvals"] = approvals
    project.setdefault("joeflow_version", None)
    return write_project(state_path, project)


def schema_message(script: str, state: object) -> str:
    """Why a script refuses a state whose schema_version it does not support."""
    found = state.get("schema_version") if isinstance(state, dict) else None
    if found == "0.1.2.1":
        hint = ("this is a legacy 0.1.2.1 state: validate it with validate_state.py; "
                "migrate with migrate_state.py --apply only when the user asks to adopt V2")
    elif found is None:
        hint = "the file has no schema_version; is it a JOEFLOW state.json?"
    else:
        hint = f"no JOEFLOW {running_version()} script reads schema {found!r}; check which JOEFLOW version wrote it"
    return f"{script} supports schema_version 0.2.0 only; found {found!r}. {hint}"
