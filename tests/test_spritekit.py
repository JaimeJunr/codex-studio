"""Testes do spritekit.py focados em efeitos colaterais de import time e na
resiliencia de _discover_envkit (rework do HIGH da US-006: efeito colateral
de filesystem em import time, com gatilho ja agendado pela US-012).

Carrega o modulo via importlib direto do arquivo, sob um nome de modulo
proprio (spritekit_under_test) pra nunca colidir com um spritekit ja
importado por outro teste na mesma sessao do pytest.
"""
import importlib.util
import sys
import types
from pathlib import Path

import pytest


SPRITEKIT_PATH = (
    Path(__file__).resolve().parent.parent
    / "plugins"
    / "codex-sprite"
    / "scripts"
    / "spritekit.py"
)


def _spec_and_module():
    spec = importlib.util.spec_from_file_location(
        "spritekit_under_test", SPRITEKIT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    return module, spec


def test_import_does_not_touch_filesystem(monkeypatch, tmp_path):
    """HIGH: migrate_legacy_config rodava no nivel do modulo (gatilho ja
    agendado pela US-012, rename de APP_NAME). Planta um config legado
    divergente em HOME e confirma que importar spritekit nao cria nem
    altera nada no disco — o efeito colateral pertence a main(), nao ao
    import. Fixa platform em darwin pra que o local novo (Application
    Support) difira do XDG legado plantado — no linux de dev os dois
    coincidem e mascarariam uma regressao real."""
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    legacy_dir = tmp_path / ".config" / "codex-sprite"
    legacy_dir.mkdir(parents=True)
    (legacy_dir / "config.json").write_text(
        '{"aseprite_path": "/legacy"}', encoding="utf-8"
    )

    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))

    module, spec = _spec_and_module()
    spec.loader.exec_module(module)

    after = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    assert after == before
    # prova estrutural (nao so comportamental): o modulo compartilhado nao
    # pode ter sido carregado/migrado so por causa do import.
    assert module.envkit is None


def test_discover_envkit_raises_instead_of_killing_process(monkeypatch, tmp_path):
    """HIGH: quando envkit.py nao e encontrado (nenhum codex-image instalado
    nem no repo nem em ~/.claude/plugins), _discover_envkit precisa levantar
    excecao — nunca sys.exit, que mataria qualquer import/coleta de teste
    que passe por esse caminho.

    LOW (rework rodada 3): o teste nao pode depender de onde TMPDIR aponta.
    Se TMPDIR cair dentro do proprio repo, o walk de parents de fake_file
    alcancaria o plugins/codex-image/scripts/envkit.py real e o teste
    passaria por acidente (ou falharia por motivo errado). Por isso
    is_file() e restrito a paths dentro de tmp_path: qualquer candidato
    fora dai (repo real, instalacoes reais) e' tratado como inexistente."""
    module, spec = _spec_and_module()
    spec.loader.exec_module(module)

    fake_file = tmp_path / "isolated" / "scripts" / "spritekit.py"
    fake_file.parent.mkdir(parents=True)
    monkeypatch.setattr(module, "__file__", str(fake_file))
    monkeypatch.setattr(module.Path, "home", classmethod(lambda cls: tmp_path))

    real_is_file = Path.is_file

    def isolated_is_file(self):
        if self != tmp_path and tmp_path not in self.parents:
            return False
        return real_is_file(self)

    monkeypatch.setattr(module.Path, "is_file", isolated_is_file)

    with pytest.raises(module.EnvkitUnavailableError):
        module._discover_envkit()


def test_ensure_env_is_idempotent_and_migrates_once(monkeypatch, tmp_path):
    """_ensure_env so deve carregar/migrar uma vez; chamadas subsequentes
    reaproveitam o modulo ja carregado.

    LOW (rework rodada 3): `first is second` sozinho so prova que o global
    foi reusado, nao que migrate_legacy_config rodou uma unica vez — que e'
    exatamente o que "idempotente" promete. Um spy fecha essa lacuna."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

    module, spec = _spec_and_module()
    spec.loader.exec_module(module)

    migrate_calls = []
    fake_envkit = types.SimpleNamespace(
        migrate_legacy_config=lambda *a, **k: migrate_calls.append((a, k))
    )
    monkeypatch.setattr(module, "_load_envkit", lambda: fake_envkit)

    first = module._ensure_env()
    second = module._ensure_env()

    assert first is second
    assert len(migrate_calls) == 1


def test_config_free_subcommand_works_without_codex_image(
    monkeypatch, tmp_path, capsys
):
    """HIGH (rework rodada 3): main() passou a chamar _ensure_env() de forma
    incondicional, o que derrubava TODOS os subcomandos (inclusive os que
    nunca leem config) quando o codex-image nao esta instalado — violando a
    degradacao graciosa exigida pelo CLAUDE.md. `palettes` nunca toca em
    envkit/config; precisa funcionar de ponta a ponta (exit 0, saida com as
    paletas) com a descoberta do envkit quebrada."""
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

    module, spec = _spec_and_module()
    spec.loader.exec_module(module)

    def discovery_unavailable():
        raise module.EnvkitUnavailableError("envkit.py nao encontrado")

    monkeypatch.setattr(module, "_discover_envkit", discovery_unavailable)
    monkeypatch.setattr(sys, "argv", ["spritekit.py", "palettes"])

    module.main()  # nao deve levantar/sys.exit — comando nao le config

    out = capsys.readouterr().out
    assert "db16" in out
    assert "pico8" in out


def _envkit_unavailable(module):
    def discovery_unavailable():
        raise module.EnvkitUnavailableError("envkit.py nao encontrado")

    return discovery_unavailable


def _executable(tmp_path, name):
    p = tmp_path / name
    p.write_text("#!/bin/sh\n")
    p.chmod(0o755)
    return p


def test_resolve_aseprite_env_var_without_envkit(monkeypatch, tmp_path):
    """HIGH (rework rodada 4): env var e' os.environ puro, nao pode depender
    do envkit. Com o envkit indescobrivel e ASEPRITE_PATH valido, a etapa
    'env' tem que continuar resolvendo — igual ao HEAD antes do acoplamento."""
    module, spec = _spec_and_module()
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_discover_envkit", _envkit_unavailable(module))

    env_bin = _executable(tmp_path, "aseprite")
    monkeypatch.setenv("ASEPRITE_PATH", str(env_bin))

    assert module.resolve_aseprite() == (str(env_bin), "env")


def test_resolve_aseprite_path_without_envkit(monkeypatch, tmp_path):
    """HIGH (rework rodada 4): PATH e' shutil.which puro, nao pode depender
    do envkit. Sem ASEPRITE_PATH e com o envkit indescobrivel, a etapa PATH
    tem que continuar resolvendo o binario."""
    module, spec = _spec_and_module()
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_discover_envkit", _envkit_unavailable(module))
    monkeypatch.delenv("ASEPRITE_PATH", raising=False)

    path_bin = _executable(tmp_path, "aseprite")
    monkeypatch.setattr(
        module.shutil,
        "which",
        lambda name: str(path_bin) if name == "aseprite" else None,
    )

    assert module.resolve_aseprite() == (str(path_bin), "PATH")


def test_resolve_aseprite_none_without_envkit_and_no_binary(monkeypatch, tmp_path):
    """HIGH (rework rodada 4): sem env, sem PATH e com o envkit indescobrivel
    (config/steam pulados), resolve_aseprite tem que devolver (None, None)
    sem deixar EnvkitUnavailableError vazar — quem chama nao trata excecao."""
    module, spec = _spec_and_module()
    spec.loader.exec_module(module)
    monkeypatch.setattr(module, "_discover_envkit", _envkit_unavailable(module))
    monkeypatch.delenv("ASEPRITE_PATH", raising=False)
    monkeypatch.setattr(module.shutil, "which", lambda name: None)

    assert module.resolve_aseprite() == (None, None)


def test_resolve_aseprite_precedence_with_envkit_available(monkeypatch, tmp_path):
    """Com o envkit disponivel, a cadeia continua env -> config -> PATH ->
    known_location (steam), cada etapa vencendo a seguinte quando presente."""
    module, spec = _spec_and_module()
    spec.loader.exec_module(module)

    env_bin = _executable(tmp_path, "env-aseprite")
    config_bin = _executable(tmp_path, "config-aseprite")
    path_bin = _executable(tmp_path, "path-aseprite")
    known_bin = _executable(tmp_path, "known-aseprite")

    fake_config = {"aseprite_path": str(config_bin)}
    fake_envkit = types.SimpleNamespace(
        migrate_legacy_config=lambda *a, **k: None,
        load_config=lambda app: fake_config,
        steam_roots=lambda: [],
    )
    monkeypatch.setattr(module, "_load_envkit", lambda: fake_envkit)
    monkeypatch.setattr(module, "_steam_aseprite_candidates", lambda: iter([known_bin]))
    monkeypatch.setattr(module.shutil, "which", lambda name: str(path_bin))

    monkeypatch.setenv("ASEPRITE_PATH", str(env_bin))
    assert module.resolve_aseprite() == (str(env_bin), "env")

    monkeypatch.delenv("ASEPRITE_PATH", raising=False)
    assert module.resolve_aseprite() == (str(config_bin), "config")

    fake_config.clear()
    assert module.resolve_aseprite() == (str(path_bin), "PATH")

    monkeypatch.setattr(module.shutil, "which", lambda name: None)
    assert module.resolve_aseprite() == (str(known_bin), "steam")


def test_config_aseprite_path_propagates_errors_other_than_envkit_unavailable(
    monkeypatch, tmp_path
):
    """LOW (finding 3): _config_aseprite_path so pode engolir
    EnvkitUnavailableError (envkit nao instalado); qualquer outra excecao
    vinda de load_config() precisa propagar, nao virar None silencioso.
    RuntimeError e' usada de proposito por nao estar na lista tolerada por
    migrate_legacy_config (OSError, ValueError) apos a correcao do finding 1
    — garante que este teste continua provando a propagacao na etapa
    'config', nao um efeito colateral da migracao."""
    module, spec = _spec_and_module()
    spec.loader.exec_module(module)

    def load_config_raises(app):
        raise RuntimeError("config corrompida de um jeito inesperado")

    fake_envkit = types.SimpleNamespace(
        migrate_legacy_config=lambda *a, **k: None,
        load_config=load_config_raises,
    )
    monkeypatch.setattr(module, "_load_envkit", lambda: fake_envkit)

    with pytest.raises(RuntimeError):
        module._config_aseprite_path()
