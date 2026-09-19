"""Resolucao portatil de ambiente (config dir, migracao, binarios) para
Linux/macOS/Windows.

Modulo compartilhado da camada base (keyless-image). Outros plugins descobrem
este arquivo em runtime subindo a arvore de diretorios a partir do proprio
script — ver spritekit.py (keyless-sprite) para o mecanismo de fallback e a
mensagem de degradacao quando keyless-image nao esta instalado.
"""
import json
import os
import re
import shutil
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path


def _os_family() -> str:
    """Ponto unico de decisao de SO — evita sys.platform espalhado pelo modulo."""
    if sys.platform == "darwin":
        return "darwin"
    if sys.platform.startswith("win"):
        return "windows"
    return "linux"


def config_dir(app_name: str) -> Path:
    """Diretorio de config por SO: XDG no Linux, Application Support no
    macOS, %APPDATA% no Windows (com fallback quando a env var falta)."""
    family = _os_family()
    if family == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif family == "windows":
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME")
        base = Path(xdg) if xdg else Path.home() / ".config"
    return base / app_name


def config_path(app_name: str) -> Path:
    """Path do arquivo config.json dentro do diretorio de config do app."""
    return config_dir(app_name) / "config.json"


def load_config(app_name: str) -> dict:
    """Carrega config JSON do app; tolera arquivo ausente ou corrompido."""
    try:
        cfg_file = config_path(app_name)
        if cfg_file.is_file():
            return json.loads(cfg_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        pass
    return {}


def save_config(app_name: str, data: dict) -> None:
    """Mescla e persiste chaves no config JSON do app."""
    cfg_file = config_path(app_name)
    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    merged = load_config(app_name)
    merged.update(data)
    cfg_file.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")


def _legacy_config_candidates(app_name: str) -> list[Path]:
    """Origens candidatas de config legado para um dado nome de app, nas
    duas dimensoes que uma migracao precisa cobrir: NOME (config_path
    resolvido pelo SO atual — cobre rename de app, ex.: US-012) e LOCAL
    (o path XDG literal ~/.config/<app>/config.json avaliado em QUALQUER
    SO — cobre portabilidade, ex.: US-006: versoes antigas do codigo
    cravavam XDG mesmo fora do Linux, entao um usuario de macOS/Windows
    pode ter o config exatamente ali)."""
    by_current_os = config_path(app_name)
    xdg_literal = Path.home() / ".config" / app_name / "config.json"
    if xdg_literal == by_current_os:
        return [by_current_os]
    return [by_current_os, xdg_literal]


def migrate_legacy_config(app_name: str, legacy_names: Sequence[str]) -> None:
    """Copia config de um nome/local legado pro novo app_name, se o novo
    ainda nao existir. Nunca move: o config legado precisa continuar intacto
    pra quem ainda dependa dele. Se o novo ja existe, ele vence e nada e
    feito (idempotente: rodar de novo nao substitui nem duplica).

    Para cada nome legado percorre ambas as origens candidatas (ver
    _legacy_config_candidates) — nome e local sao dimensoes independentes
    e precisam ser combinadas, nao tratadas como alternativas."""
    new_config = config_path(app_name)
    if new_config.is_file():
        return
    for legacy_name in legacy_names:
        for legacy_config in _legacy_config_candidates(legacy_name):
            if legacy_config.is_file():
                try:
                    content = legacy_config.read_text(encoding="utf-8")
                    new_config.parent.mkdir(parents=True, exist_ok=True)
                    new_config.write_text(content, encoding="utf-8")
                except (OSError, ValueError):
                    # legado ilegivel (encoding invalido, permissao negada):
                    # nao migra, mas nao derruba quem chamou — mesma
                    # tolerancia que load_config ja aplica ao ler config.
                    continue
                return


def _is_executable(path: str | Path) -> bool:
    """True se path e um arquivo executavel."""
    try:
        p = Path(path).expanduser()
        return p.is_file() and os.access(p, os.X_OK)
    except OSError:
        return False


def resolve_binary(
    name: str,
    *,
    env_var: str,
    config_key: str,
    known_locations: Iterable[str | Path],
    config: dict | None = None,
    include_env_config: bool = True,
    include_path: bool = True,
) -> tuple[str | None, str | None]:
    """Resolve um binario por env var -> config -> PATH -> locais conhecidos.

    Mesmo contrato do resolve_aseprite ja existente em spritekit.py: retorna
    (path, fonte) com fonte em {"env", "config", "PATH", "known_location"},
    ou (None, None) se nao encontrado. Motivado por caso real medido nesta
    maquina: binario resolvivel no shell interativo (~/.grok/bin/grok) mas
    ausente do PATH de um processo filho — daí a etapa de known_locations.

    include_env_config/include_path: toggles ja usados por resolve_aseprite
    (ex.: `setup --detect` ignora env/config de proposito); default True
    preserva a ordem completa.
    """
    if include_env_config:
        env_path = os.environ.get(env_var)
        if env_path and _is_executable(env_path):
            return env_path, "env"

        cfg_path = (config or {}).get(config_key)
        if cfg_path and _is_executable(cfg_path):
            return cfg_path, "config"

    if include_path:
        which_path = shutil.which(name)
        if which_path and _is_executable(which_path):
            return which_path, "PATH"

    for candidate in known_locations:
        if _is_executable(candidate):
            return str(candidate), "known_location"

    return None, None


_LIBRARYFOLDERS_VDF = (
    "steamapps/libraryfolders.vdf",
    "config/libraryfolders.vdf",
)


def _steam_root_candidates() -> tuple[Path, ...]:
    """Raizes Steam default por SO. Windows le variaveis de ambiente reais
    (ProgramFiles(x86)/ProgramFiles/LOCALAPPDATA) em vez de cravar o path;
    o literal C:/... fica como ultimo fallback quando nenhuma env var existe."""
    program_files_x86 = os.environ.get("ProgramFiles(x86)")
    program_files = os.environ.get("ProgramFiles")
    local_appdata = os.environ.get("LOCALAPPDATA")
    windows_candidates = []
    if program_files_x86:
        windows_candidates.append(Path(program_files_x86) / "Steam")
    if program_files:
        windows_candidates.append(Path(program_files) / "Steam")
    if local_appdata:
        windows_candidates.append(Path(local_appdata) / "Steam")
    windows_candidates.append(Path("C:/Program Files (x86)/Steam"))

    return (
        Path.home() / ".steam" / "steam",
        Path.home() / ".steam" / "root",
        Path.home() / ".local" / "share" / "Steam",
        Path.home()
        / ".var"
        / "app"
        / "com.valvesoftware.Steam"
        / ".local"
        / "share"
        / "Steam",
        Path.home() / "Library" / "Application Support" / "Steam",
        *windows_candidates,
    )


def _parse_steam_library_paths(vdf_text: str) -> list[str]:
    """Extrai paths de libraryfolders.vdf via regex."""
    paths = []
    for raw in re.findall(r'"path"\s*"([^"]+)"', vdf_text):
        p = raw.replace("\\\\", "\\").replace("//", "/")
        paths.append(p)
    return paths


def steam_roots() -> list[Path]:
    """Monta lista de raizes Steam (defaults por SO + libraryfolders.vdf,
    que cobre biblioteca em disco custom nao catalogada nos defaults)."""
    roots: list[Path] = []
    seen: set[str] = set()
    try:
        for candidate in _steam_root_candidates():
            try:
                resolved = candidate.expanduser().resolve()
            except OSError:
                continue
            key = str(resolved)
            if resolved.is_dir() and key not in seen:
                seen.add(key)
                roots.append(resolved)

        idx = 0
        while idx < len(roots):
            root = roots[idx]
            idx += 1
            for rel in _LIBRARYFOLDERS_VDF:
                vdf = root / rel
                try:
                    if not vdf.is_file():
                        continue
                    text = vdf.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for lib_path in _parse_steam_library_paths(text):
                    try:
                        lib_root = Path(lib_path).expanduser().resolve()
                    except OSError:
                        continue
                    key = str(lib_root)
                    if lib_root.is_dir() and key not in seen:
                        seen.add(key)
                        roots.append(lib_root)
    except OSError:
        # best-effort: is_dir() acima pode propagar OSError (ex.: EACCES)
        # que os try/except internos nao cobrem; um bug de programacao
        # (TypeError etc.) nao deve ser engolido aqui.
        pass
    return roots
