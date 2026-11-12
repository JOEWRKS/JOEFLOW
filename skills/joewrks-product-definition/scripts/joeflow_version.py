#!/usr/bin/env python3
"""Show which JOEFLOW version this project uses and which one is running; --pin records it.

The pin lives in joeflow-project.json next to state.json (state schema 0.2.0 has no
place for it). Run this before opening a revision when more than one JOEFLOW copy
is installed, or when project notes and the installed copy disagree.
"""

from __future__ import annotations

import argparse
import json

from cli_output import use_utf8_stdio
from project_pin import read_project, running_version, version_report, write_project
from state_validation import load_state


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state", help="state.json of the project")
    parser.add_argument("--pin", nargs="?", const="", metavar="VERSION",
                        help="record VERSION (default: the running version) as the version this project uses")
    args = parser.parse_args(argv)
    try:
        state = load_state(args.state)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False))
        return 2
    if args.pin is not None:
        project = read_project(args.state)
        if isinstance(project, dict) and "error" in project:
            print(json.dumps({"pinned": False, "error": project["error"]}, ensure_ascii=False))
            return 1
        version = args.pin or running_version()
        if not version:
            print(json.dumps({"pinned": False, "error": "running version unknown; pass --pin VERSION"}, ensure_ascii=False))
            return 1
        project = dict(project or {})
        previous = project.get("joeflow_version")
        project["joeflow_version"] = version
        write_project(args.state, project)
        report = version_report(args.state, state)
        report["pinned"] = True
        report["previous_pin"] = previous
    else:
        report = version_report(args.state, state)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
