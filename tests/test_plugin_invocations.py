from pathlib import Path
import json
import re
import pytest

# Exclusions similar to other tests
EXCLUDED_DIRS = {".git", ".ralph", ".depth-loop", "node_modules", "__pycache__"}
EXCLUDED_FILES = {"CHANGELOG.md"}
EXCLUDED_REL_PATHS = {"AGENTS.md"}

# Casa qualquer id kebab com >=2 segmentos (`keyless-image`, `codex-inexistente`)
# seguido de skill kebab. O lado esquerdo NÃO pode ser a lista de plugins
# existentes: se o padrão só reconhece ids que já existem, invocações órfãs
# nunca entram na varredura e o teste passa por tautologia.
INVOCATION_PATTERN = re.compile(
    r"\b([a-z][a-z0-9]*(?:-[a-z0-9]+)+):([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\b"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _is_excluded(path: Path, root: Path) -> bool:
    rel = path.relative_to(root)
    if any(part in EXCLUDED_DIRS for part in rel.parts):
        return True
    if path == Path(__file__).resolve():
        return True
    if rel.as_posix() in EXCLUDED_REL_PATHS:
        return True
    return rel.name in EXCLUDED_FILES


def _plugin_dirs() -> set[str]:
    plugins_path = _repo_root() / "plugins"
    return {p.name for p in plugins_path.iterdir() if p.is_dir()}


def _plugin_names() -> dict[str, str]:
    plugins_path = _repo_root() / "plugins"
    mapping: dict[str, str] = {}
    for plugin_dir in plugins_path.iterdir():
        if not plugin_dir.is_dir():
            continue
        json_path = plugin_dir / ".claude-plugin" / "plugin.json"
        if not json_path.is_file():
            continue
        try:
            data = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        mapping[plugin_dir.name] = data.get("name", "")
    return mapping


def _markdown_files() -> list[Path]:
    root = _repo_root()
    exts = {".md", ".py", ".json"}
    return [p for p in root.rglob("*") if p.is_file() and p.suffix in exts and not _is_excluded(p, root)]


def collect_invocations() -> list[tuple[str, int, str, str]]:
    """(rel_path, line_number, match_text, plugin_id) em todo markdown do repo."""
    root = _repo_root()
    found: list[tuple[str, int, str, str]] = []
    for md_path in _markdown_files():
        rel = md_path.relative_to(root).as_posix()
        for i, line in enumerate(md_path.read_text(encoding="utf-8").splitlines(), start=1):
            for match in INVOCATION_PATTERN.finditer(line):
                found.append((rel, i, match.group(0), match.group(1)))
    return found


def _orphan_reports(plugin_ids: set[str]) -> list[str]:
    reports: list[str] = []
    for rel, line_number, invocation, plugin_id in collect_invocations():
        if plugin_id not in plugin_ids:
            reports.append(
                f"{rel}:{line_number}: {invocation}  (plugin '{plugin_id}' nao existe)"
            )
    return reports


def test_every_plugin_invocation_resolves_to_an_existing_plugin() -> None:
    plugin_ids = _plugin_dirs()
    mismatches = [
        f"{dir_name}: name '{name}' differs from directory"
        for dir_name, name in _plugin_names().items()
        if name != dir_name
    ]
    if mismatches:
        pytest.fail("Plugin name mismatches:\n" + "\n".join(mismatches))
    orphan = _orphan_reports(plugin_ids)
    if orphan:
        pytest.fail(
            f"Found {len(orphan)} orphan plugin invocations:\n" + "\n".join(orphan)
        )


def test_every_plugin_is_registered_in_the_marketplace() -> None:
    plugin_ids = _plugin_dirs()
    marketplace_path = _repo_root() / ".claude-plugin" / "marketplace.json"
    try:
        data = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except Exception as e:
        pytest.fail(f"Unable to read marketplace.json: {e}")
    # Validate source dirs
    for entry in data.get("plugins", []):
        src = entry.get("source")
        if src:
            src_path = Path(_repo_root()) / src
            if not src_path.is_dir():
                pytest.fail(f"Marketplace entry '{entry.get('name')}' has invalid source path: {src_path}")
    marketplace_names = {entry.get("name") for entry in data.get("plugins", [])}
    missing_in_marketplace = plugin_ids - marketplace_names
    extra_in_marketplace = marketplace_names - plugin_ids
    messages = []
    if missing_in_marketplace:
        messages.append("Plugins not in marketplace: " + ", ".join(sorted(missing_in_marketplace)))
    if extra_in_marketplace:
        messages.append("Marketplace entries without plugin dir: " + ", ".join(sorted(extra_in_marketplace)))
    if messages:
        pytest.fail("\n".join(messages))
