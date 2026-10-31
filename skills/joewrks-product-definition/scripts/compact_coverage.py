#!/usr/bin/env python3
"""Rewrite coverage rows in the compact form where that loses nothing.

For each requirement, screen and action row the most reused COVERED binding set becomes
the row's default_authority and the cells it reproduces are dropped. Hand-written N/A
cells and action shapes are never changed: an inherited N/A has no basis or rationale,
so compacting one would change the record. The result must expand back to the original
byte for byte and keep the definition and Approval Manifest digests, or nothing is written.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from approval_v2 import approval_manifest_digest, compute_approval_manifest, definition_digest
from cli_output import use_utf8_stdio
from coverage_inheritance import compact_coverage, declared_rows, expand_coverage
from state_validation_v2 import validate_state_v2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("state", help="canonical state.json (schema 0.2.0)")
    parser.add_argument("--write", action="store_true", help="replace the file (default: report only)")
    args = parser.parse_args(argv)
    path = Path(args.state)
    try:
        original = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    compact, removed = compact_coverage(original)
    explicit = expand_coverage(original, strip=True)
    checks = {
        "expands_to_original": expand_coverage(compact, strip=True) == explicit,
        "definition_digest_equal": definition_digest(compact) == definition_digest(original),
        "manifest_digest_equal": approval_manifest_digest(compute_approval_manifest(compact))
        == approval_manifest_digest(compute_approval_manifest(original)),
        "validation_equal": validate_state_v2(compact) == validate_state_v2(original),
    }
    report = {"ok": all(checks.values()), "removed_cells": removed, "checks": checks,
              "declared_rows": sum(1 for _ in declared_rows(compact))}
    if args.write and report["ok"] and sum(removed.values()):
        path.write_text(json.dumps(compact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        report["written"] = True
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    use_utf8_stdio()
    raise SystemExit(main())
