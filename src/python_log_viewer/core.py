"""
Framework-agnostic core logic for reading and managing log files.

No external dependencies – only the Python standard library.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class LogFileInfo:
    """Metadata for a single log file."""

    name: str  # relative path from the log directory
    size: int
    modified: float


class LogDirectory:
    """Represents a directory tree of log files.

    Parameters
    ----------
    path:
        Absolute or relative path to the root log directory.
    """

    def __init__(self, path: str) -> None:
        self.path = os.path.abspath(path)

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_files(self) -> List[LogFileInfo]:
        """Walk *self.path* and return metadata for every regular file."""
        if not os.path.isdir(self.path):
            return []

        files: list[LogFileInfo] = []
        for root, _dirs, filenames in os.walk(self.path):
            for entry in sorted(filenames):
                filepath = os.path.join(root, entry)
                if os.path.isfile(filepath):
                    rel = os.path.relpath(filepath, self.path)
                    stat = os.stat(filepath)
                    files.append(
                        LogFileInfo(name=rel, size=stat.st_size, modified=stat.st_mtime)
                    )
        files.sort(key=lambda f: f.name)
        return files

    # ------------------------------------------------------------------
    # Safe path resolution
    # ------------------------------------------------------------------

    def _safe_resolve(self, relative: str) -> Optional[str]:
        """Return the absolute path if *relative* stays inside *self.path*.

        Returns ``None`` when the path escapes the log directory.
        """
        safe = os.path.normpath(relative)
        if safe.startswith("..") or os.path.isabs(safe):
            return None
        full = os.path.realpath(os.path.join(self.path, safe))
        if not full.startswith(os.path.realpath(self.path)):
            return None
        if not os.path.isfile(full):
            return None
        return full

    # ------------------------------------------------------------------
    # File mutations
    # ------------------------------------------------------------------

    def delete_file(self, relative: str) -> bool:
        """Permanently remove a log file. Returns *True* on success."""
        resolved = self._safe_resolve(relative)
        if resolved is None:
            return False
        os.remove(resolved)
        return True

    def clear_file(self, relative: str) -> bool:
        """Truncate a log file to zero bytes. Returns *True* on success."""
        resolved = self._safe_resolve(relative)
        if resolved is None:
            return False
        open(resolved, "w", encoding="utf-8").close()
        return True


class LogReader:
    """Read and filter log entries from a file inside a :class:`LogDirectory`.

    Parameters
    ----------
    log_dir:
        A :class:`LogDirectory` instance.
    """

    _LEVEL_KEYWORDS = frozenset({"INFO", "WARNING", "ERROR", "DEBUG", "CRITICAL"})
    _MAX_READ_BYTES = 5 * 1024 * 1024  # 5 MB

    def __init__(self, log_dir: LogDirectory) -> None:
        self.log_dir = log_dir

    # ------------------------------------------------------------------
    # Efficient file reading
    # ------------------------------------------------------------------

    @staticmethod
    def _read_tail(filepath: str, max_bytes: int) -> list:
        """Read the tail of a file, optimised for large files.

        If the file is larger than *max_bytes*, only the last *max_bytes*
        are read and the first (potentially partial) line is discarded.
        """
        file_size = os.path.getsize(filepath)
        with open(filepath, "r", encoding="utf-8") as fh:
            if max_bytes > 0 and file_size > max_bytes:
                fh.seek(file_size - max_bytes)
                fh.readline()  # discard partial line at boundary
            return fh.readlines()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def read(
        self,
        file: str,
        *,
        lines: int = 500,
        level: str = "",
        search: str = "",
        page: int = 1,
    ) -> dict:
        """Return filtered, paginated log entries as a dict.

        Returns
        -------
        dict
            ``{"lines": [...], "total": int, "page": int, "total_pages": int}``
            on success, or the same shape with ``"error"`` on failure.
        """
        _err = {"lines": [], "total": 0, "page": 1, "total_pages": 1}

        resolved = self.log_dir._safe_resolve(file)
        if resolved is None:
            return {**_err, "error": "Invalid or missing file"}

        try:
            if lines > 0:
                # Read enough bytes from the tail for the requested pages
                read_bytes = max(page * lines * 500, self._MAX_READ_BYTES)
                raw_lines = self._read_tail(resolved, read_bytes)
            else:
                with open(resolved, "r", encoding="utf-8") as fh:
                    raw_lines = fh.readlines()
        except Exception as exc:
            return {**_err, "lines": [f"Error reading log file: {exc}"]}

        # Group multi-line entries
        entries: list[str] = []
        for line in raw_lines:
            stripped = line.rstrip()
            if stripped and (
                stripped[0].isdigit()
                or stripped.split()[0] in self._LEVEL_KEYWORDS
            ):
                entries.append(stripped)
            elif entries:
                entries[-1] += "\n" + stripped
            else:
                entries.append(stripped)

        # Level filter
        if level:
            upper = level.upper()
            entries = [e for e in entries if upper in e]

        # Text search
        if search:
            lower = search.lower()
            entries = [e for e in entries if lower in e.lower()]

        total = len(entries)

        if lines > 0:
            total_pages = max(1, -(-total // lines))  # ceiling division
            page = max(1, min(page, total_pages))
            # Page 1 = most recent entries, higher pages = older
            end_idx = total - (page - 1) * lines
            start_idx = max(0, end_idx - lines)
            entries = entries[start_idx:end_idx]
        else:
            total_pages = 1
            page = 1

        return {
            "lines": entries,
            "total": total,
            "page": page,
            "total_pages": total_pages,
        }
