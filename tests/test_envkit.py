"""Testes do modulo compartilhado envkit (resolucao portatil de ambiente).

envkit vive em plugins/keyless-image/scripts/envkit.py (camada base). O
carregamento aqui usa importlib direto do arquivo — nao depende de
sys.path/instalacao do plugin, mesmo mecanismo que spritekit.py usara
para descobrir o modulo em runtime.
"""
import importlib.util
import json
import os
import stat
from pathlib import Path

import pytest


def _load_envkit():
    module_path = (
        Path(__file__).resolve().parent.parent
        / "plugins"
        / "keyless-image"
        / "scripts"
        / "envkit.py"
    )
    spec = importlib.util.spec_from_file_location("envkit", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


envkit = _load_envkit()


def _make_executable(path: Path) -> Path:
    """Cria arquivo com bit de execucao setado, pra simular um binario real."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("#!/bin/sh\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


def _pin_home(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(envkit.Path, "home", classmethod(lambda cls: tmp_path))


# --- config_dir ---------------------------------------------------------


def test_config_dir_linux_uses_xdg_config_home_when_set(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))

    result = envkit.config_dir("myapp")

    assert result == tmp_path / "xdg" / "myapp"


def test_config_dir_linux_defaults_to_dot_config_when_xdg_unset(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    _pin_home(monkeypatch, tmp_path)

    result = envkit.config_dir("myapp")

    assert result == tmp_path / ".config" / "myapp"


def test_config_dir_linux_treats_empty_xdg_config_home_as_unset(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", "")
    _pin_home(monkeypatch, tmp_path)

    result = envkit.config_dir("myapp")

    assert result == tmp_path / ".config" / "myapp"


def test_config_dir_macos_uses_application_support(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "darwin")
    _pin_home(monkeypatch, tmp_path)

    result = envkit.config_dir("myapp")

    assert result == tmp_path / "Library" / "Application Support" / "myapp"


def test_config_dir_windows_uses_appdata_when_set(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))

    result = envkit.config_dir("myapp")

    assert result == tmp_path / "Roaming" / "myapp"


def test_config_dir_windows_falls_back_when_appdata_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "win32")
    monkeypatch.delenv("APPDATA", raising=False)
    _pin_home(monkeypatch, tmp_path)

    result = envkit.config_dir("myapp")

    assert result == tmp_path / "AppData" / "Roaming" / "myapp"


# --- migrate_legacy_config ----------------------------------------------


def test_migrate_legacy_config_copies_when_new_absent_and_legacy_present(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(envkit.sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    _pin_home(monkeypatch, tmp_path)

    legacy_dir = tmp_path / ".config" / "old-app"
    legacy_dir.mkdir(parents=True)
    legacy_config = legacy_dir / "config.json"
    legacy_config.write_text(json.dumps({"aseprite_path": "/x"}), encoding="utf-8")

    envkit.migrate_legacy_config("new-app", ["old-app"])

    new_config = tmp_path / ".config" / "new-app" / "config.json"
    assert new_config.is_file()
    assert json.loads(new_config.read_text(encoding="utf-8")) == {
        "aseprite_path": "/x"
    }
    # copia, nao move: o legado precisa continuar intacto.
    assert legacy_config.is_file()


def test_migrate_legacy_config_new_wins_when_both_present(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    _pin_home(monkeypatch, tmp_path)

    new_dir = tmp_path / ".config" / "new-app"
    new_dir.mkdir(parents=True)
    (new_dir / "config.json").write_text(json.dumps({"a": 1}), encoding="utf-8")

    legacy_dir = tmp_path / ".config" / "old-app"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "config.json").write_text(json.dumps({"a": 2}), encoding="utf-8")

    envkit.migrate_legacy_config("new-app", ["old-app"])

    result = json.loads((new_dir / "config.json").read_text(encoding="utf-8"))
    assert result == {"a": 1}


def test_migrate_legacy_config_is_noop_when_neither_present(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    _pin_home(monkeypatch, tmp_path)

    envkit.migrate_legacy_config("new-app", ["old-app"])

    assert not (tmp_path / ".config" / "new-app" / "config.json").exists()


def test_migrate_legacy_config_is_idempotent(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    _pin_home(monkeypatch, tmp_path)

    legacy_dir = tmp_path / ".config" / "old-app"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "config.json").write_text(json.dumps({"a": 1}), encoding="utf-8")

    envkit.migrate_legacy_config("new-app", ["old-app"])
    envkit.migrate_legacy_config("new-app", ["old-app"])

    new_config = tmp_path / ".config" / "new-app" / "config.json"
    assert json.loads(new_config.read_text(encoding="utf-8")) == {"a": 1}


def test_migrate_legacy_config_macos_migrates_xdg_literal_legacy(
    monkeypatch, tmp_path
):
    """CRITICAL/AC2: versoes antigas cravavam XDG (~/.config) em qualquer
    SO. Um usuario de macOS que rodou 'setup --path' antes desta mudanca
    tem o config em ~/.config/keyless-sprite, nao em Application Support —
    a migracao precisa achar isso sem exigir acao do usuario."""
    monkeypatch.setattr(envkit.sys, "platform", "darwin")
    _pin_home(monkeypatch, tmp_path)

    legacy_dir = tmp_path / ".config" / "keyless-sprite"
    legacy_dir.mkdir(parents=True)
    legacy_config = legacy_dir / "config.json"
    legacy_config.write_text(
        json.dumps({"aseprite_path": "/Applications/Aseprite.app"}),
        encoding="utf-8",
    )

    envkit.migrate_legacy_config("keyless-sprite", ["keyless-sprite"])

    new_config = (
        tmp_path / "Library" / "Application Support" / "keyless-sprite" / "config.json"
    )
    assert new_config.is_file()
    assert json.loads(new_config.read_text(encoding="utf-8")) == {
        "aseprite_path": "/Applications/Aseprite.app"
    }
    # copia, nao move.
    assert legacy_config.is_file()


def test_migrate_legacy_config_windows_migrates_xdg_literal_legacy(
    monkeypatch, tmp_path
):
    """CRITICAL/AC2: mesmo cenario da probe do revisor, mas Windows."""
    monkeypatch.setattr(envkit.sys, "platform", "win32")
    monkeypatch.setenv("APPDATA", str(tmp_path / "Roaming"))
    _pin_home(monkeypatch, tmp_path)

    legacy_dir = tmp_path / ".config" / "keyless-sprite"
    legacy_dir.mkdir(parents=True)
    legacy_config = legacy_dir / "config.json"
    legacy_config.write_text(
        json.dumps({"aseprite_path": "C:/Games/Aseprite.exe"}), encoding="utf-8"
    )

    envkit.migrate_legacy_config("keyless-sprite", ["keyless-sprite"])

    new_config = tmp_path / "Roaming" / "keyless-sprite" / "config.json"
    assert new_config.is_file()
    assert json.loads(new_config.read_text(encoding="utf-8")) == {
        "aseprite_path": "C:/Games/Aseprite.exe"
    }
    assert legacy_config.is_file()


def test_migrate_legacy_config_tolerates_unreadable_legacy_config(
    monkeypatch, tmp_path
):
    """LOW (finding 1): legado com permissao de leitura negada (ou encoding
    ilegivel) nao pode derrubar a migracao com traceback — mesma tolerancia
    que load_config ja aplica ao ler config (OSError, ValueError). Um legado
    ilegivel simplesmente nao e migrado; a execucao segue."""
    monkeypatch.setattr(envkit.sys, "platform", "linux")
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    _pin_home(monkeypatch, tmp_path)

    legacy_dir = tmp_path / ".config" / "old-app"
    legacy_dir.mkdir(parents=True)
    legacy_config = legacy_dir / "config.json"
    legacy_config.write_text(json.dumps({"a": 1}), encoding="utf-8")
    legacy_config.chmod(0o000)

    try:
        if os.access(legacy_config, os.R_OK):
            pytest.skip("processo roda como root: permissao 000 nao bloqueia leitura")

        envkit.migrate_legacy_config("new-app", ["old-app"])
    finally:
        legacy_config.chmod(0o600)

    assert not (tmp_path / ".config" / "new-app" / "config.json").exists()


def test_migrate_legacy_config_new_wins_over_xdg_literal_legacy(monkeypatch, tmp_path):
    """Invariante preservada na dimensao layout: se o novo local ja tem
    config, ele vence mesmo com um legado XDG-literal presente."""
    monkeypatch.setattr(envkit.sys, "platform", "darwin")
    _pin_home(monkeypatch, tmp_path)

    new_dir = tmp_path / "Library" / "Application Support" / "keyless-sprite"
    new_dir.mkdir(parents=True)
    (new_dir / "config.json").write_text(json.dumps({"a": "novo"}), encoding="utf-8")

    legacy_dir = tmp_path / ".config" / "keyless-sprite"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "config.json").write_text(
        json.dumps({"a": "legado"}), encoding="utf-8"
    )

    envkit.migrate_legacy_config("keyless-sprite", ["keyless-sprite"])

    result = json.loads((new_dir / "config.json").read_text(encoding="utf-8"))
    assert result == {"a": "novo"}


# --- resolve_binary -------------------------------------------------------


def test_resolve_binary_finds_via_env_var(monkeypatch, tmp_path):
    fake = _make_executable(tmp_path / "mytool")
    monkeypatch.setenv("MYTOOL_PATH", str(fake))

    path, source = envkit.resolve_binary(
        "mytool", env_var="MYTOOL_PATH", config_key="mytool_path", known_locations=[]
    )

    assert path == str(fake)
    assert source == "env"


def test_resolve_binary_finds_via_config_when_env_missing(monkeypatch, tmp_path):
    monkeypatch.delenv("MYTOOL_PATH", raising=False)
    fake = _make_executable(tmp_path / "mytool")

    path, source = envkit.resolve_binary(
        "mytool",
        env_var="MYTOOL_PATH",
        config_key="mytool_path",
        known_locations=[],
        config={"mytool_path": str(fake)},
    )

    assert path == str(fake)
    assert source == "config"


def test_resolve_binary_finds_via_path(monkeypatch, tmp_path):
    monkeypatch.delenv("MYTOOL_PATH", raising=False)
    fake = _make_executable(tmp_path / "mytool")
    monkeypatch.setenv("PATH", str(tmp_path))

    path, source = envkit.resolve_binary(
        "mytool", env_var="MYTOOL_PATH", config_key="mytool_path", known_locations=[]
    )

    assert path == str(fake)
    assert source == "PATH"


def test_resolve_binary_finds_via_known_location_when_absent_from_path(
    monkeypatch, tmp_path
):
    monkeypatch.delenv("MYTOOL_PATH", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path / "empty-dir"))
    fake = _make_executable(tmp_path / "nested" / "mytool")

    path, source = envkit.resolve_binary(
        "mytool",
        env_var="MYTOOL_PATH",
        config_key="mytool_path",
        known_locations=[fake],
    )

    assert path == str(fake)
    assert source == "known_location"


def test_resolve_binary_returns_none_when_not_found(monkeypatch, tmp_path):
    monkeypatch.delenv("MYTOOL_PATH", raising=False)
    monkeypatch.setenv("PATH", str(tmp_path / "empty-dir"))

    path, source = envkit.resolve_binary(
        "mytool", env_var="MYTOOL_PATH", config_key="mytool_path", known_locations=[]
    )

    assert (path, source) == (None, None)


def test_resolve_binary_ignores_env_var_pointing_to_nonexistent_path(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("MYTOOL_PATH", str(tmp_path / "does-not-exist"))
    monkeypatch.setenv("PATH", str(tmp_path / "empty-dir"))

    path, source = envkit.resolve_binary(
        "mytool", env_var="MYTOOL_PATH", config_key="mytool_path", known_locations=[]
    )

    assert (path, source) == (None, None)


def test_resolve_binary_ignores_env_var_pointing_to_non_executable_file(
    monkeypatch, tmp_path
):
    non_executable = tmp_path / "mytool"
    non_executable.write_text("nao executavel", encoding="utf-8")
    non_executable.chmod(stat.S_IREAD)
    monkeypatch.setenv("MYTOOL_PATH", str(non_executable))
    monkeypatch.setenv("PATH", str(tmp_path / "empty-dir"))

    path, source = envkit.resolve_binary(
        "mytool", env_var="MYTOOL_PATH", config_key="mytool_path", known_locations=[]
    )

    assert (path, source) == (None, None)


def test_resolve_binary_precedence_is_a_descending_staircase(monkeypatch, tmp_path):
    """MEDIUM: os testes anteriores isolam cada fonte; nenhum prova ORDEM.
    Aqui as quatro fontes apontam pra binarios distintos e validos ao mesmo
    tempo, e cada uma e removida em sequencia — uma troca na ordem interna
    do bloco env/config ou uma inversao PATH<->known_location quebraria
    algum dos quatro asserts."""
    env_bin = _make_executable(tmp_path / "env_tool")
    config_bin = _make_executable(tmp_path / "config_dir" / "mytool")
    path_dir = tmp_path / "pathdir"
    path_bin = _make_executable(path_dir / "mytool")
    known_bin = _make_executable(tmp_path / "known" / "mytool")

    monkeypatch.setenv("MYTOOL_PATH", str(env_bin))
    monkeypatch.setenv("PATH", str(path_dir))
    config = {"mytool_path": str(config_bin)}

    def resolve():
        return envkit.resolve_binary(
            "mytool",
            env_var="MYTOOL_PATH",
            config_key="mytool_path",
            known_locations=[known_bin],
            config=config,
        )

    assert resolve() == (str(env_bin), "env")

    monkeypatch.delenv("MYTOOL_PATH", raising=False)
    assert resolve() == (str(config_bin), "config")

    config.pop("mytool_path")
    assert resolve() == (str(path_bin), "PATH")

    monkeypatch.setenv("PATH", str(tmp_path / "empty-dir"))
    assert resolve() == (str(known_bin), "known_location")


# --- steam_roots (Windows) -------------------------------------------------


def test_steam_roots_windows_respects_program_files_x86_env_var(monkeypatch, tmp_path):
    monkeypatch.setattr(envkit.sys, "platform", "win32")
    _pin_home(monkeypatch, tmp_path / "home")
    custom_root = tmp_path / "CustomProgramFilesX86" / "Steam"
    custom_root.mkdir(parents=True)
    monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "CustomProgramFilesX86"))
    monkeypatch.delenv("ProgramFiles", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    roots = envkit.steam_roots()

    assert custom_root.resolve() in roots


def test_steam_roots_propagates_non_os_error_instead_of_swallowing(monkeypatch):
    """LOW (finding 2): steam_roots e' best-effort e so deve tolerar OSError
    (esperado ao percorrer filesystem); um bug de programacao (ex.: TypeError)
    nao pode ser engolido pelo except cego — precisa propagar."""

    def boom():
        raise TypeError("bug de programacao, nao falha de filesystem")

    monkeypatch.setattr(envkit, "_steam_root_candidates", boom)

    with pytest.raises(TypeError):
        envkit.steam_roots()


def test_steam_roots_windows_without_env_vars_ignores_missing_literal_fallback(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(envkit.sys, "platform", "win32")
    _pin_home(monkeypatch, tmp_path / "home")
    monkeypatch.delenv("ProgramFiles(x86)", raising=False)
    monkeypatch.delenv("ProgramFiles", raising=False)
    monkeypatch.delenv("LOCALAPPDATA", raising=False)

    roots = envkit.steam_roots()

    # nenhum candidato existe no disco de teste; nao deve quebrar.
    assert roots == []
