"""Shared failure reporting for the small offline delivery automations."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import argparse
import traceback
import sys


class AutomationError(RuntimeError):
    """A user-visible automation failure that must be recorded."""


def protected_name(path: Path) -> bool:
    name = path.name.lower()
    return (name.endswith(".tfvars") or name == ".env" or name.startswith(".env.")
            or name.endswith(".key") or name.endswith(".pem"))


def default_error_log(*candidates: Path | str | None) -> Path:
    """Return the stable sidecar error log for the first concrete artifact."""
    for candidate in candidates:
        if candidate is not None:
            path = Path(candidate).absolute()
            return path.with_name(path.name + ".errors.log")
    return Path.cwd() / "automation.errors.log"


def option_value(argv: list[str], option: str) -> str | None:
    """Read a simple option value before argparse can report a parse error."""
    value = None
    for index, token in enumerate(argv):
        if token == option and index + 1 < len(argv):
            value = argv[index + 1]
        elif token.startswith(option + "="):
            value = token.split("=", 1)[1]
    return value


class ErrorLoggingArgumentParser(argparse.ArgumentParser):
    """Keep argparse's normal visible usage while recording its failures."""

    def __init__(self, *args, error_log: Path, context: str, **kwargs):
        super().__init__(*args, **kwargs)
        self._error_log = error_log
        self._error_context = context

    def error(self, message: str) -> None:
        report_error(AutomationError("argument error: " + message), self._error_log,
                     context=self._error_context)
        super().error(message)


def report_error(exc: BaseException, error_log: Path | str | None, *, context: str) -> bool:
    """Immediately print and append a detailed error record.

    The caller must treat ``False`` as an additional failure.  Reporting never
    hides a failed write: a second stderr diagnostic is emitted if the durable
    error log cannot be appended.
    """
    destination = Path(error_log) if error_log is not None else default_error_log()
    detail = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    record = (
        "[" + datetime.now(timezone.utc).isoformat().replace("+00:00", "Z") + "] "
        + context + ": " + str(exc) + "\n" + detail
    )
    print(record, file=sys.stderr, end="" if record.endswith("\n") else "\n")
    try:
        if protected_name(destination):
            raise OSError("refusing protected error log: " + str(destination))
        if destination.exists() and destination.is_symlink():
            raise OSError("refusing symbolic-link error log: " + str(destination))
        with destination.open("a", encoding="utf-8") as stream:
            stream.write(record)
        return True
    except Exception as log_exc:
        logging_detail = "".join(traceback.format_exception(type(log_exc), log_exc, log_exc.__traceback__))
        print("AUTOMATION ERROR LOGGING FAILED:\n" + logging_detail, file=sys.stderr, end="")
        return False
