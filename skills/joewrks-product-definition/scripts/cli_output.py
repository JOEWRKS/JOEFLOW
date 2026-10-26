#!/usr/bin/env python3
"""Shared standard-stream encoding boundary for human-readable JOEFLOW CLIs."""

from __future__ import annotations

import os
import sys


def use_utf8_stdio() -> None:
    """Write UTF-8 to redirected stdout/stderr unless PYTHONIOENCODING chooses otherwise.

    On Windows a piped stream inherits the ANSI code page (for example cp949),
    which cannot encode characters such as an em dash and corrupts Korean text
    for UTF-8 readers.
    """
    if os.environ.get("PYTHONIOENCODING"):
        return
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except (OSError, ValueError):
            continue
