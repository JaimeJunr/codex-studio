from pathlib import Path
import re
from typing import Iterator

import pytest


LEGACY_BRIDGE_PATTERN: re.Pattern[str] = re.compile(
    r"cursor-?(mcp-)?bridge|CURSOR_(MCP_)?BRIDGE"
)
EXCLUDED_DIRECTORY_NAMES: frozenset[str] = frozenset(
    {".git", ".ralph", ".depth-loop", "node_modules", "__pycache__"}
)
EXCLUDED_FILE_NAMES: frozenset[str] = frozenset(
    {
        "CHANGELOG.md",  # Histórico legítimo em qualquer nível do repositório.
    }
)

# AGENTS.md da raiz: fora do escopo da US-007, alinhamento pendente.
EXCLUDED_RELATIVE_PATHS: frozenset[str] = frozenset({"AGENTS.md"})


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _is_excluded(path: Path, root: Path, test_path: Path) -> bool:
    relative_path = path.relative_to(root)
    if any(part in EXCLUDED_DIRECTORY_NAMES for part in relative_path.parts):
        return True
    if path == test_path:
        return True
    if relative_path.as_posix() in EXCLUDED_RELATIVE_PATHS:
        return True
    return relative_path.name in EXCLUDED_FILE_NAMES


def _iter_repository_files(root: Path, test_path: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if path.is_file() and not _is_excluded(path, root, test_path):
            yield path


def _read_text(path: Path) -> str | None:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    if "\x00" in content:
        return None
    return content


def _find_occurrences(root: Path) -> list[tuple[str, int, str]]:
    occurrences: list[tuple[str, int, str]] = []
    test_path = Path(__file__).resolve()
    for path in _iter_repository_files(root, test_path):
        content = _read_text(path)
        if content is None:
            continue
        relative_path = path.relative_to(root).as_posix()
        for line_number, line in enumerate(content.splitlines(), start=1):
            for _ in LEGACY_BRIDGE_PATTERN.finditer(line):
                occurrences.append((relative_path, line_number, line.strip()))
    return sorted(occurrences)


def _format_occurrences(occurrences: list[tuple[str, int, str]]) -> str:
    return "\n".join(
        f"{path}:{line_number}: {line}"
        for path, line_number, line in occurrences
    )


def test_no_legacy_bridge_references() -> None:
    occurrences = _find_occurrences(_repo_root())
    if occurrences:
        pytest.fail(
            f"Found {len(occurrences)} legacy bridge references:\n"
            f"{_format_occurrences(occurrences)}"
        )
