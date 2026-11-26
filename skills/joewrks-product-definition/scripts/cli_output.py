#!/usr/bin/env python3
"""Shared standard-stream encoding boundary for human-readable JOEFLOW CLIs."""

from __future__ import annotations

import atexit
import os
import sys


def use_utf8_stdio() -> None:
    """Write UTF-8 to redirected stdout/stderr unless PYTHONIOENCODING chooses otherwise.

    On Windows a piped stream inherits the ANSI code page (for example cp949),
    which cannot encode characters such as an em dash and corrupts Korean text
    for UTF-8 readers.
    """
    atexit.register(_flush_or_silence)
    previous_hook = sys.excepthook

    def _quiet_closed_pipe(kind, value, traceback):
        # the reader closed the pipe (head, Select-Object -First): the command already did its work
        if isinstance(value, OSError) and (isinstance(value, BrokenPipeError) or value.errno in {22, 32}):
            _silence_stdout()
            return
        previous_hook(kind, value, traceback)

    sys.excepthook = _quiet_closed_pipe
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


def _flush_or_silence() -> None:
    """Flush stdout at exit; when the reader has gone (a pipe cut by head, Select-Object -First),
    point the descriptor at devnull so interpreter shutdown does not raise OSError/BrokenPipeError."""
    try:
        sys.stdout.flush()
    except (OSError, ValueError):
        _silence_stdout()


def _silence_stdout() -> None:
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
    except (OSError, ValueError):
        pass
