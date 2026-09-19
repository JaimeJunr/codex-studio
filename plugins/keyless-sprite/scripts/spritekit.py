#!/usr/bin/env python3
"""Post-processamento de sprites 2D (pixelate, chroma-key, sprite sheet, gif).

Uso:
    python spritekit.py pixelate IN OUT [--grid N] [--scale N] [--palette NAME|.gpl]
                                     [--dither none|ordered] [--no-upscale]
                                     [--downscale nearest|box]
                                     [--remove-aa [THRESH]] [--outline [HEX]]
    python spritekit.py extract-palette IN OUT.gpl [--colors N]
    python spritekit.py outline IN OUT [--color HEX] [--alpha-thresh N]
    python spritekit.py keyout   IN OUT (--key RRGGBB | --corners) [--tol N]
                                     [--defringe [N]] [--defringe-tol N] [--shrink N]
    python spritekit.py sheet    DIR OUT [--cols N] [--padding N] [--json]
                                     [--engine NAME] [--format json-hash|json-array]
                                     [--durations CSV] [--tag SPEC]
    python spritekit.py gif      DIR OUT [--fps N | --duration MS] [--durations CSV]
    python spritekit.py walkgen  SPRITE OUTDIR [--frames N] [--leg-split FRAC]
                                     [--amp N] [--lift N] [--bob N] [--scale N]
    python spritekit.py palettes [--show NAME]
    python spritekit.py setup [--path P | --detect]

Pillow-only (Aseprite e backend opcional de quantize). `setup` le/escreve
config via envkit.py (modulo compartilhado do plugin keyless-image) e exige-o
instalado, falhando cedo se faltar. `pixelate` tambem passa por config/envkit
ao resolver o Aseprite (etapas env var/PATH da cadeia nao dependem disso), mas
degrada sozinho pro Pillow se o keyless-image nao estiver instalado — nunca
falha por causa disso. Os demais subcomandos nunca tocam config/envkit. Parte
do plugin keyless-sprite (Claude Code).

walkgen: ciclo de caminhada top-down PROCEDURAL a partir de um sprite estatico
(desloca pernas/corpo por codigo — ritmo deterministico, sem IA). Fisica de
marcha por fase (stance + swing em arco + bob do corpo); banda inferior
(--leg-split) + metade esq/dir.

Requer: Pillow  ->  pip install Pillow
"""
import argparse
import importlib.util
import json

import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    sys.exit("Falta Pillow. Rode: pip install Pillow")

# Nomes de app usados na resolucao de config (ver envkit.migrate_legacy_config).
APP_NAME = "keyless-sprite"
LEGACY_APP_NAMES = ["codex-sprite"]


class EnvkitUnavailableError(RuntimeError):
    """Levantada quando envkit.py (modulo compartilhado do keyless-image) nao
    e localizavel. Nunca sys.exit aqui: isso mataria qualquer import ou
    coleta de teste que passe por _discover_envkit; quem decide encerrar o
    processo com mensagem amigavel e main()."""


def _discover_envkit():
    """Localiza envkit.py (modulo compartilhado do keyless-image) subindo a
    arvore de diretorios a partir deste arquivo ate a raiz do repo; fallback
    para plugins instalados (~/.claude/plugins/**/keyless-image/scripts/
    envkit.py, maior versao). Nao achou -> levanta EnvkitUnavailableError
    (main() converte em mensagem clara em vez de stack trace cru)."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "plugins" / "keyless-image" / "scripts" / "envkit.py"
        if candidate.is_file():
            return candidate
        if (parent / ".claude-plugin" / "marketplace.json").is_file():
            break  # raiz do repo atingida, nao adianta subir mais

    installed_root = Path.home() / ".claude" / "plugins"
    candidates = sorted(
        installed_root.glob("**/keyless-image/scripts/envkit.py"),
        key=_envkit_plugin_version,
    )
    if candidates:
        return candidates[-1]

    raise EnvkitUnavailableError(
        "envkit.py nao encontrado: o plugin keyless-image precisa estar "
        "instalado (ele fornece o modulo compartilhado de resolucao de "
        "ambiente entre Linux/macOS/Windows). Instale keyless-image e "
        "tente novamente."
    )


def _envkit_plugin_version(envkit_path):
    """Le a versao do plugin.json ao lado do envkit.py candidato (pra
    escolher a maior versao entre plugins instalados); 0.0.0 se ausente ou
    invalido."""
    plugin_json = envkit_path.parent.parent / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(plugin_json.read_text(encoding="utf-8"))
        version = str(data.get("version", "0.0.0"))
    except (OSError, ValueError, json.JSONDecodeError):
        version = "0.0.0"
    return _version_sort_key(version)


def _version_sort_key(version):
    """Chave de ordenacao para string de versao tipo semver ("v1.2.3" ou
    "1.2.3"). Cada segmento vira uma tupla (0, int) ou (1, str) — nunca int
    puro nem str pura — pra sorted() nunca comparar int com str quando
    formatos coexistem entre plugins instalados (ex.: "1.0.0" vs
    "1.0.beta"), o que levantaria TypeError."""
    version = version[1:] if version[:1] in ("v", "V") else version
    return tuple(
        (0, int(seg)) if seg.isdigit() else (1, seg)
        for seg in version.split(".")
    )


def _load_envkit():
    """Carrega o modulo envkit via importlib a partir do path descoberto."""
    module_path = _discover_envkit()
    spec = importlib.util.spec_from_file_location("envkit", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Catalogo de paletas fixas (hex RGB, sem #).
PALETTES = {
    "db16": [
        "140c1c", "442434", "30346d", "4e4a4e",
        "854c30", "346524", "d04648", "757161",
        "597dce", "d27d2c", "8595a1", "6daa2c",
        "d2aa99", "6dc2ca", "dad45e", "deeed6",
    ],
    "db32": [
        "000000", "222034", "45283c", "663931", "8f563b", "df7126",
        "d9a066", "eec39a", "fbf236", "99e550", "6abe30", "37946e",
        "4b692f", "524b24", "323c39", "3f3f74", "306082", "5b6ee1",
        "639bff", "5fcde4", "cbdbfc", "ffffff", "9badb7", "847e87",
        "696a6a", "595652", "76428a", "ac3232", "d95763", "d77bba",
        "8f974a", "8a6f30",
    ],
    "pico8": [
        "000000", "1D2B53", "7E2553", "008751",
        "AB5236", "5F574F", "C2C3C7", "FFF1E8",
        "FF004D", "FFA300", "FFEC27", "00E436",
        "29ADFF", "83769C", "FF77A8", "FFCCAA",
    ],
    "nes": [
        "000000", "3c3c3c", "545454", "982220", "ec6a64", "540400", "ecb4b0",
        "3c1800", "783c00", "d48820", "e4c490", "a0aa00", "ccd278", "545a00",
        "202a00", "74c400", "b4de78", "287200", "a8e290", "4cd020", "083a00",
        "087c00", "a0a2a0", "eceeec", "003c00", "004000", "007628", "38cc6c",
        "98e2b4", "006678", "38b4cc", "00323c", "a0d6e4", "a8ccec", "4c9aec",
        "084cc4", "001e74", "081090", "787cec", "3032ec", "bcbcec", "5c1ee4",
        "300088", "b062ec", "d4b2ec", "440064", "8814b0", "e454ec", "989698",
        "ecaeec", "ec58b4", "ecaed4", "a01464", "5c0030",
    ],
    "gameboy": [
        "0f380f", "306230", "8bac0f", "9bbc0f",
    ],
    "gameboy-gray": [
        "000000", "676767", "b6b6b6", "ffffff",
    ],
    "c64": [
        "000000", "626262", "898989", "adadad", "ffffff", "9f4e44",
        "cb7e75", "6d5412", "a1683c", "c9d487", "9ae29b", "5cab5e",
        "6abfc6", "887ecb", "50459b", "a057a3",
    ],
    "cga": [
        "000000", "0000aa", "00aa00", "00aaaa", "aa0000", "aa00aa",
        "aa5500", "aaaaaa", "555555", "5555ff", "55ff55", "55ffff",
        "ff5555", "ff55ff", "ffff55", "ffffff",
    ],
    "snes": [
        "902068", "f81868", "ffa880", "ff7000", "a80010", "ffa800",
        "ffffa8", "a8e038", "5800a8", "6828ff", "ffffff", "e0d0ff",
        "a070c8", "683090", "481868", "000000",
    ],
    "sweetie16": [
        "1a1c2c", "5d275d", "b13e53", "ef7d57", "ffcd75", "a7f070",
        "38b764", "257179", "29366f", "3b5dc9", "41a6f6", "73eff7",
        "f4f4f4", "94b0c2", "566c86", "333c57",
    ],
    "gray4": [
        "000000", "676767", "b6b6b6", "ffffff",
    ],
    "gray8": [
        "000000", "242424", "494949", "6d6d6d",
        "929292", "b6b6b6", "dbdbdb", "ffffff",
    ],
    "gray16": [
        "000000", "181818", "282828", "383838", "474747", "565656",
        "646464", "717171", "7e7e7e", "8c8c8c", "9b9b9b", "ababab",
        "bdbdbd", "d1d1d1", "e7e7e7", "ffffff",
    ],
}


def natural_key(p: Path):
    """Ordena frame_2 antes de frame_10."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.name)]


def palette_from_hex(hex_list):
    """Constroi imagem modo P com paleta a partir de lista de hex RGB."""
    flat = []
    for h in hex_list:
        h = h.lstrip("#")
        flat.extend(int(h[i : i + 2], 16) for i in (0, 2, 4))
    # Pillow exige paleta de 256*3 bytes.
    flat.extend([0] * (256 * 3 - len(flat)))
    pal = Image.new("P", (1, 1))
    pal.putpalette(flat)
    return pal


def parse_hex_color(s: str):
    """Converte RRGGBB (com ou sem #) em tupla (R, G, B)."""
    s = s.lstrip("#").strip()
    if len(s) != 6:
        sys.exit(f"Cor hex invalida: {s!r} (espere RRGGBB)")
    try:
        return tuple(int(s[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        sys.exit(f"Cor hex invalida: {s!r}")


# Modulo compartilhado (config dir + resolucao de binario portateis entre
# SOs), carregado sob demanda por _ensure_env() — nunca no import (efeito
# colateral de disco pertence a main(), ver EnvkitUnavailableError acima).
envkit = None


def _ensure_env():
    """Carrega envkit (uma vez, memoizado) e migra config de nomes legados.
    Chamada no comeco de main(); tambem chamada de forma preguicosa pelas
    funcoes de config/aseprite abaixo, pra continuar funcionando em quem as
    chame direto (testes, outros scripts) sem passar por main()."""
    global envkit
    if envkit is None:
        loaded = _load_envkit()
        loaded.migrate_legacy_config(APP_NAME, LEGACY_APP_NAMES)
        envkit = loaded  # so publica o global depois da migracao ter sucesso
    return envkit


def config_path():
    """Retorna path do arquivo de config do keyless-sprite."""
    return _ensure_env().config_path(APP_NAME)


def load_config():
    """Carrega config JSON; tolera arquivo ausente ou corrompido."""
    return _ensure_env().load_config(APP_NAME)


def save_config(data):
    """Mescla e persiste chaves no config JSON."""
    _ensure_env().save_config(APP_NAME, data)


_ASEPRITE_REL_PATHS = (
    "steamapps/common/Aseprite/aseprite",
    "steamapps/common/Aseprite/Aseprite.app/Contents/MacOS/aseprite",
    "steamapps/common/Aseprite/Aseprite.exe",
)


def _steam_aseprite_candidates():
    """Candidatos a binario Aseprite dentro de instalacoes Steam conhecidas
    (raizes resolvidas pelo envkit, incluindo libraryfolders.vdf).

    Generator, nao lista: o scan de Steam (~10 raizes candidatas, resolve()
    em cada, parse de libraryfolders.vdf) e o passo mais caro da cadeia de
    resolve_binary e so deve rodar se env/config/PATH falharem antes dele —
    resolve_binary consome isto com `for candidate in known_locations`, que
    aceita iteravel preguicoso sem mudanca do lado dele."""
    try:
        roots = _ensure_env().steam_roots()
    except EnvkitUnavailableError:
        return
    for root in roots:
        for rel in _ASEPRITE_REL_PATHS:
            yield root / rel


def _is_executable(path):
    """True se path e um arquivo executavel. Copia local e deliberada do
    mesmo teste em envkit.py: usada pelas etapas env/PATH de resolve_aseprite,
    que nao podem depender do envkit (ver docstring de resolve_aseprite)."""
    try:
        p = Path(path).expanduser()
        return p.is_file() and os.access(p, os.X_OK)
    except OSError:
        return False


def _config_aseprite_path():
    """Le aseprite_path do config do usuario via envkit; None se o envkit
    nao estiver instalado. Etapa isolada pra que a ausencia do keyless-image
    derrube so o passo 'config' da cadeia, nunca env/PATH (ver
    resolve_aseprite)."""
    try:
        return load_config().get("aseprite_path")
    except EnvkitUnavailableError:
        return None


def resolve_aseprite(
    *,
    include_env_config=True,
    include_path=True,
    include_steam=True,
):
    """Retorna (path, fonte) ou (None, None). Fonte: env|config|PATH|steam.

    Cadeia env var -> config -> PATH -> locais conhecidos (steam). As etapas
    env var e PATH usam so os.environ/shutil.which (nunca o envkit) e por
    isso continuam funcionando sem o plugin keyless-image instalado; so config
    e steam precisam do envkit (config dir e steam roots sao portateis entre
    SOs) e degradam sozinhas, sem interromper a cadeia, quando ele falta."""
    if include_env_config:
        env_path = os.environ.get("ASEPRITE_PATH")
        if env_path and _is_executable(env_path):
            return env_path, "env"

        config_path_value = _config_aseprite_path()
        if config_path_value and _is_executable(config_path_value):
            return config_path_value, "config"

    if include_path:
        which_path = shutil.which("aseprite")
        if which_path and _is_executable(which_path):
            return which_path, "PATH"

    if include_steam:
        for candidate in _steam_aseprite_candidates():
            if _is_executable(candidate):
                return str(candidate), "steam"

    return None, None


def aseprite_bin():
    """Retorna path do Aseprite se disponivel, senao None."""
    path, _ = resolve_aseprite()
    return path


def _validate_aseprite(path):
    """Executa --version; retorna (ok, texto)."""
    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return True, (result.stdout or result.stderr or "").strip()
        return False, (result.stderr or result.stdout or "").strip()
    except OSError as exc:
        return False, str(exc)


def _setup_hint():
    return (
        "Passe --path /caminho/aseprite ou exporte ASEPRITE_PATH=/caminho/aseprite"
    )


def cmd_setup(args):
    """Configura ou mostra resolucao do binario Aseprite.

    Unico subcomando que exige envkit de forma dura: le/escreve config, entao
    falha cedo com mensagem amigavel (nao traceback) se o keyless-image nao
    estiver instalado. `pixelate` tambem le config (via resolve_aseprite),
    mas so pra tentar o backend Aseprite — degrada pro Pillow sem falhar se
    o envkit faltar. Os demais subcomandos nunca leem config."""
    try:
        _ensure_env()
    except EnvkitUnavailableError as exc:
        sys.exit(str(exc))

    if args.path:
        ok, output = _validate_aseprite(args.path)
        if not ok:
            print(output, file=sys.stderr)
            sys.exit(1)
        save_config({"aseprite_path": args.path})
        print(output)
        print(f"Salvo em {config_path()}: aseprite_path={args.path}")
        return

    if args.detect:
        path, _ = resolve_aseprite(
            include_env_config=False,
            include_path=True,
            include_steam=True,
        )
        if not path:
            print(
                "Aseprite nao encontrado via PATH ou Steam.",
                file=sys.stderr,
            )
            print(_setup_hint(), file=sys.stderr)
            sys.exit(1)
        ok, version = _validate_aseprite(path)
        if not ok:
            print(version, file=sys.stderr)
            sys.exit(1)
        save_config({"aseprite_path": path})
        print(path)
        print(version)
        return

    path, source = resolve_aseprite()
    if path:
        print(f"{path} (via {source})")
        return

    print("Aseprite não encontrado")
    print(_setup_hint())
    sys.exit(1)


def write_gpl(hex_list, path):
    """Escreve paleta no formato GIMP .gpl (canais decimais)."""
    lines = ["GIMP Palette", "Name: keyless-sprite", "#"]
    for i, h in enumerate(hex_list):
        h = h.lstrip("#")
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        lines.append(f"{r} {g} {b}\t{i}")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_gpl(path):
    """Le paleta GIMP .gpl; retorna lista de hex rgb (sem #)."""
    colors = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if (
            not line
            or line.startswith("#")
            or line == "GIMP Palette"
            or line.startswith("Name:")
        ):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        try:
            r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        except ValueError:
            continue
        colors.append(f"{r:02x}{g:02x}{b:02x}")
    if not colors:
        sys.exit(f"Paleta .gpl vazia ou invalida: {path}")
    return colors


def resolve_palette(name: str):
    """Valida nome de paleta ou arquivo .gpl; retorna lista de hex ou None se 'none'."""
    if name == "none":
        return None
    p = Path(name)
    if name.endswith(".gpl") or p.is_file():
        return read_gpl(p.expanduser().resolve())
    if name not in PALETTES:
        valid = ", ".join(["none"] + sorted(PALETTES))
        sys.exit(f"Paleta desconhecida: {name!r}. Validas: {valid}")
    return PALETTES[name]


def remove_aa(img, thresh):
    """Binariza alpha: >= thresh -> 255, senao 0 (remove halo semi-transparente)."""
    img = img.convert("RGBA")
    r, g, b, a = img.split()
    a = a.point(lambda x: 255 if x >= thresh else 0)
    return Image.merge("RGBA", (r, g, b, a))


def add_outline(img, hex_color, alpha_thresh):
    """Contorno 1px ao redor da regiao opaca (dilate - mask)."""
    img = img.convert("RGBA").copy()
    alpha = img.getchannel("A")
    mask = alpha.point(lambda x: 255 if x >= alpha_thresh else 0)
    dilated = mask.filter(ImageFilter.MaxFilter(3))
    mask_data = list(mask.getdata())
    dilated_data = list(dilated.getdata())
    ring_data = [
        255 if d >= 128 and m < 128 else 0
        for d, m in zip(dilated_data, mask_data)
    ]
    ring = Image.new("L", img.size)
    ring.putdata(ring_data)
    color = (*parse_hex_color(hex_color), 255)
    px = img.load()
    ring_px = ring.load()
    for y in range(img.height):
        for x in range(img.width):
            if ring_px[x, y] >= 128:
                px[x, y] = color
    return img


def parse_durations_csv(csv_str, n_frames, context=""):
    """Normaliza CSV de duracoes (ms): pad/truncate com aviso."""
    try:
        parts = [int(x.strip()) for x in csv_str.split(",") if x.strip()]
    except ValueError:
        sys.exit(f"Duracoes invalidas{context}: {csv_str!r}")
    if not parts:
        sys.exit(f"Duracoes vazias{context}")
    if len(parts) < n_frames:
        print(
            f"AVISO: duracoes ({len(parts)}) < frames ({n_frames}); "
            f"preenchendo com ultimo valor",
            file=sys.stderr,
        )
        parts.extend([parts[-1]] * (n_frames - len(parts)))
    elif len(parts) > n_frames:
        print(
            f"AVISO: duracoes ({len(parts)}) > frames ({n_frames}); truncando",
            file=sys.stderr,
        )
        parts = parts[:n_frames]
    return parts


def parse_tag_spec(spec):
    """Parse name:from-to[:dir] (frames 1-based inclusive) -> dict 0-based."""
    m = re.match(
        r"^([^:]+):(\d+)-(\d+)(?::(forward|reverse|pingpong))?$",
        spec,
    )
    if not m:
        sys.exit(
            f"Tag malformada: {spec!r}. "
            "Esperado name:from-to[:forward|reverse|pingpong]"
        )
    name = m.group(1)
    from1 = int(m.group(2))
    to1 = int(m.group(3))
    direction = m.group(4) or "forward"
    if from1 < 1 or to1 < from1:
        sys.exit(f"Tag malformada: intervalo invalido em {spec!r}")
    return {
        "name": name,
        "from": from1 - 1,
        "to": to1 - 1,
        "direction": direction,
    }


def quantize_pillow(rgb, hex_list, dither: str):
    """Quantize com paleta fixa via Pillow (fallback)."""
    pal_img = palette_from_hex(hex_list)
    # Pillow nao tem ordered dither real em quantize com paleta custom;
    # FLOYDSTEINBERG e a aproximacao mais proxima.
    dither_mode = (
        Image.Dither.FLOYDSTEINBERG if dither == "ordered" else Image.Dither.NONE
    )
    return rgb.quantize(palette=pal_img, dither=dither_mode).convert("RGB")


def quantize_aseprite(rgb, hex_list, dither: str, bin_path: str):
    """Quantize via Aseprite CLI (indexed + paleta .gpl)."""
    with tempfile.TemporaryDirectory(prefix="spritekit-") as td:
        td = Path(td)
        rgb_tmp = td / "in.png"
        gpl_tmp = td / "pal.gpl"
        out_tmp = td / "out.png"
        rgb.save(rgb_tmp, format="PNG")
        write_gpl(hex_list, gpl_tmp)
        dither_alg = "ordered" if dither == "ordered" else "none"
        subprocess.run(
            [
                bin_path,
                "-b",
                str(rgb_tmp),
                "--palette",
                str(gpl_tmp),
                "--dithering-algorithm",
                dither_alg,
                "--color-mode",
                "indexed",
                "--save-as",
                str(out_tmp),
            ],
            check=True,
            capture_output=True,
        )
        # .copy() para sobreviver a limpeza do TemporaryDirectory.
        return Image.open(out_tmp).convert("RGB").copy()


def corner_bg_ref(img):
    """Media RGB dos 4 cantos da imagem original (referencia de fundo)."""
    w, h = img.size
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    pixels = img.load()
    rs, gs, bs = [], [], []
    for x, y in seeds:
        r, g, b, _a = pixels[x, y]
        rs.append(r)
        gs.append(g)
        bs.append(b)
    return (sum(rs) // 4, sum(gs) // 4, sum(bs) // 4)


def bg_chroma_fringe(r, g, b, ref_rgb, margin=15):
    """Detecta pixel puxado para a hue do fundo (ex.: magenta claro ou roxo escuro)."""
    ref_r, ref_g, ref_b = ref_rgb
    refs = [ref_r, ref_g, ref_b]
    pix = [r, g, b]
    spread = max(refs) - min(refs)
    if spread < 20:
        return False
    band = spread * 0.25
    high = [i for i, v in enumerate(refs) if v >= max(refs) - band]
    low = [i for i, v in enumerate(refs) if v <= min(refs) + band]
    if not high or not low or set(high) == set(low):
        return False
    hi_min = min(pix[i] for i in high)
    lo_max = max(pix[i] for i in low)
    return hi_min > lo_max + margin


def is_defringe_pixel(r, g, b, ref_rgb, tol):
    """Pixel de borda contaminado pelo fundo: match por tolerancia ou assinatura cromatica."""
    ref_r, ref_g, ref_b = ref_rgb
    if (
        abs(r - ref_r) <= tol
        and abs(g - ref_g) <= tol
        and abs(b - ref_b) <= tol
    ):
        return True
    return bg_chroma_fringe(r, g, b, ref_rgb)


def defringe_rgba(img, ref_rgb, iterations, tol):
    """Remove halo de chroma-key na borda alpha (N camadas, snapshot por iteracao)."""
    if iterations <= 0:
        return img
    img = img.convert("RGBA").copy()
    w, h = img.size
    for _ in range(iterations):
        alpha_data = list(img.getchannel("A").getdata())
        pixels = img.load()
        to_clear = []
        for y in range(h):
            for x in range(w):
                if alpha_data[y * w + x] == 0:
                    continue
                adjacent_transparent = (
                    (x > 0 and alpha_data[y * w + (x - 1)] == 0)
                    or (x < w - 1 and alpha_data[y * w + (x + 1)] == 0)
                    or (y > 0 and alpha_data[(y - 1) * w + x] == 0)
                    or (y < h - 1 and alpha_data[(y + 1) * w + x] == 0)
                )
                if not adjacent_transparent:
                    continue
                r, g, b, _a = pixels[x, y]
                if is_defringe_pixel(r, g, b, ref_rgb, tol):
                    to_clear.append((x, y))
        for x, y in to_clear:
            pixels[x, y] = (0, 0, 0, 0)
    return img


def shrink_alpha_rgba(img, iterations):
    """Erode a mascara alpha: borda opaca adjacente a transparente vira transparente."""
    if iterations <= 0:
        return img
    img = img.convert("RGBA").copy()
    w, h = img.size
    for _ in range(iterations):
        alpha_data = list(img.getchannel("A").getdata())
        pixels = img.load()
        to_clear = []
        for y in range(h):
            for x in range(w):
                if alpha_data[y * w + x] == 0:
                    continue
                adjacent_transparent = (
                    (x > 0 and alpha_data[y * w + (x - 1)] == 0)
                    or (x < w - 1 and alpha_data[y * w + (x + 1)] == 0)
                    or (y > 0 and alpha_data[(y - 1) * w + x] == 0)
                    or (y < h - 1 and alpha_data[(y + 1) * w + x] == 0)
                )
                if adjacent_transparent:
                    to_clear.append((x, y))
        for x, y in to_clear:
            pixels[x, y] = (0, 0, 0, 0)
    return img


def cmd_pixelate(args):
    """Downscale -> quantize opcional (preserva alpha) -> upscale."""
    src = Path(args.inp).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    grid = args.grid
    scale = args.scale
    hex_list = resolve_palette(args.palette)
    backend = "Pillow"

    img = Image.open(src).convert("RGBA")
    # 1) Downscale para resolucao logica de pixel.
    if args.downscale == "box":
        # BOX (media de area) reduz ruido ao encolher arte hi-res para grid pequeno.
        down_resample = Image.Resampling.BOX
    else:
        down_resample = Image.Resampling.NEAREST
    small = img.resize((grid, grid), down_resample)

    # 2) Quantize em paleta fixa, preservando alpha.
    if hex_list is not None:
        alpha = small.getchannel("A")
        rgb = small.convert("RGB")
        bin_path = aseprite_bin()
        if bin_path:
            q = quantize_aseprite(rgb, hex_list, args.dither, bin_path)
            backend = "aseprite"
        else:
            q = quantize_pillow(rgb, hex_list, args.dither)
            backend = "Pillow"
        small = Image.merge("RGBA", (*q.split(), alpha))

    if args.remove_aa is not None:
        small = remove_aa(small, args.remove_aa)
    if args.outline is not None:
        small = add_outline(small, args.outline, args.outline_thresh)

    # 3) Upscale de exibicao (vizinho mais proximo).
    if not args.no_upscale and scale > 1:
        small = small.resize((grid * scale, grid * scale), Image.Resampling.NEAREST)

    out.parent.mkdir(parents=True, exist_ok=True)
    small.save(out, format="PNG")
    print(
        f"OK: pixelate {src.name} -> {out} "
        f"({small.size[0]}x{small.size[1]}) [via {backend}]"
    )


def cmd_keyout(args):
    """Remove fundo por chroma-key ou flood-fill a partir dos 4 cantos."""
    if bool(args.key) == bool(args.corners):
        sys.exit("Informe exatamente um de: --key RRGGBB ou --corners")

    src = Path(args.inp).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    tol = args.tol

    img = Image.open(src).convert("RGBA")
    original = img.copy()

    if args.corners:
        ref_bg = corner_bg_ref(original)
        # Flood-fill a partir dos quatro cantos com transparencia.
        w, h = img.size
        seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        for seed in seeds:
            ImageDraw.floodfill(img, seed, (0, 0, 0, 0), thresh=tol)
    else:
        key = parse_hex_color(args.key)
        ref_bg = key
        pixels = img.load()
        w, h = img.size
        for y in range(h):
            for x in range(w):
                r, g, b, a = pixels[x, y]
                if (
                    abs(r - key[0]) <= tol
                    and abs(g - key[1]) <= tol
                    and abs(b - key[2]) <= tol
                ):
                    pixels[x, y] = (0, 0, 0, 0)

    if args.defringe:
        img = defringe_rgba(img, ref_bg, args.defringe, args.defringe_tol)
    if args.shrink:
        img = shrink_alpha_rgba(img, args.shrink)
        if args.defringe:
            img = defringe_rgba(img, ref_bg, args.defringe, args.defringe_tol)

    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, format="PNG")
    mode = "corners" if args.corners else f"key={args.key}"
    print(f"OK: keyout ({mode}) {src.name} -> {out}")


def cmd_extract_palette(args):
    """Extrai paleta de referencia via median-cut RGB (Pillow-only)."""
    src = Path(args.inp).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    img = Image.open(src)
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        rgb = bg
    else:
        rgb = img.convert("RGB")
    # Median-cut em RGB (sem deps extras), nao em espaco LAB.
    q = rgb.quantize(colors=args.colors, method=Image.Quantize.MEDIANCUT)
    pal = (q.getpalette() or [])[: args.colors * 3]
    hex_list = []
    for i in range(0, len(pal), 3):
        r, g, b = pal[i], pal[i + 1], pal[i + 2]
        hex_list.append(f"{r:02x}{g:02x}{b:02x}")
    out.parent.mkdir(parents=True, exist_ok=True)
    write_gpl(hex_list, out)
    for h in hex_list:
        print(f"#{h.lower()}")
    print(f"OK: extract-palette {src.name} -> {out} ({len(hex_list)} cores)")


def cmd_outline(args):
    """Aplica contorno 1px em PNG arbitrario."""
    src = Path(args.inp).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    img = Image.open(src).convert("RGBA")
    result = add_outline(img, args.color, args.alpha_thresh)
    out.parent.mkdir(parents=True, exist_ok=True)
    result.save(out, format="PNG")
    print(f"OK: outline {src.name} -> {out}")


def cmd_sheet(args):
    """Empacota frames de um diretorio em uma sprite sheet (+ JSON opcional)."""
    src_dir = Path(args.dir).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()

    if not src_dir.is_dir():
        sys.exit(f"Nao encontrei diretorio: {src_dir}")

    frames = sorted(
        [p for p in src_dir.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")],
        key=natural_key,
    )
    if not frames:
        sys.exit(f"Nenhuma imagem em {src_dir}.")

    # Abre todos e descobre tamanho da celula (max w x max h).
    images = []
    for p in frames:
        images.append((p, Image.open(p).convert("RGBA")))

    cw = max(im.width for _, im in images)
    ch = max(im.height for _, im in images)
    n = len(images)
    cols = args.cols if args.cols is not None else max(1, math.ceil(math.sqrt(n)))
    rows = math.ceil(n / cols)
    pad = args.padding

    durations = None
    if args.durations:
        durations = parse_durations_csv(args.durations, n, " (sheet)")

    frame_tags = None
    if args.tag:
        frame_tags = [parse_tag_spec(spec) for spec in args.tag]

    sheet_w = cols * (cw + pad) + pad
    sheet_h = rows * (ch + pad) + pad
    canvas = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))

    # Lista ordenada de (filename, frame dict) — base para hash ou array.
    frame_entries = []
    for i, (path, im) in enumerate(images):
        col = i % cols
        row = i // cols
        x = pad + col * (cw + pad)
        y = pad + row * (ch + pad)
        # Ancora top-left na celula.
        canvas.paste(im, (x, y), im)
        frame_data = {
            "frame": {"x": x, "y": y, "w": im.width, "h": im.height},
            "sourceSize": {"w": im.width, "h": im.height},
            "spriteSourceSize": {
                "x": 0,
                "y": 0,
                "w": im.width,
                "h": im.height,
            },
        }
        if durations is not None:
            frame_data["duration"] = durations[i]
        frame_entries.append((path.name, frame_data))

    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, format="PNG")
    print(f"OK: sheet {n} frames -> {out} ({sheet_w}x{sheet_h}, {cols}x{rows})")

    if args.json:
        # Mesmo stem, extensao .json (OUT.png -> OUT.json).
        json_path = out.with_suffix(".json")
        if args.format == "json-array":
            frames_payload = [
                {"filename": name, **data} for name, data in frame_entries
            ]
        else:
            # json-hash (default / estilo Aseprite).
            frames_payload = {name: data for name, data in frame_entries}

        meta = {
            "image": out.name,
            "size": {"w": sheet_w, "h": sheet_h},
            "scale": "1",
            "app": "keyless-sprite/spritekit",
            "engine": args.engine,
        }
        # Presets de engine: hints uteis, nao importadores completos.
        if args.engine in ("unity", "godot"):
            meta["filterMode"] = "Point"
            meta["pixelsPerUnit"] = ch
            meta["compression"] = "none"
        elif args.engine == "texturepacker":
            meta["format"] = "RGBA8888"

        if frame_tags:
            meta["frameTags"] = frame_tags

        payload = {"frames": frames_payload, "meta": meta}
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"OK: json -> {json_path}")


def rgba_to_gif_frame(im):
    """RGBA -> modo P com 1 indice reservado para transparencia."""
    im = im.convert("RGBA")
    alpha = im.getchannel("A")
    # 255 cores adaptativas; indice 255 fica para transparencia.
    q = im.convert("RGB").quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    pal = list(q.getpalette() or [])
    pal = pal[: 255 * 3]
    pal.extend([0, 0, 0])  # indice 255
    while len(pal) < 768:
        pal.append(0)

    transparent_idx = 255
    q_data = list(q.getdata())
    a_data = list(alpha.getdata())
    new_data = [
        transparent_idx if a < 128 else p for p, a in zip(q_data, a_data)
    ]
    out = Image.new("P", im.size)
    out.putpalette(pal)
    out.putdata(new_data)
    return out, transparent_idx


def cmd_gif(args):
    """Monta GIF animado a partir de PNGs no diretorio (preserva alpha)."""
    src_dir = Path(args.dir).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()

    if not src_dir.is_dir():
        sys.exit(f"Nao encontrei diretorio: {src_dir}")

    paths = sorted(
        [p for p in src_dir.iterdir() if p.suffix.lower() == ".png"],
        key=natural_key,
    )
    if not paths:
        sys.exit(f"Nenhuma PNG em {src_dir}.")

    n = len(paths)
    if args.durations:
        durations = parse_durations_csv(args.durations, n, " (gif)")
        ms = durations
    elif args.duration is not None:
        ms = args.duration
        durations = None
    else:
        ms = max(1, int(round(1000 / args.fps)))
        durations = None

    prepared = []
    transparent_idx = 0
    for p in paths:
        frame, transparent_idx = rgba_to_gif_frame(Image.open(p))
        prepared.append(frame)

    out.parent.mkdir(parents=True, exist_ok=True)
    save_kw = dict(
        save_all=True,
        append_images=prepared[1:],
        duration=ms,
        loop=0,
        disposal=2,
        transparency=transparent_idx,
    )
    prepared[0].save(out, **save_kw)
    if durations:
        print(
            f"OK: gif {len(prepared)} frames -> {out} "
            f"(durations={','.join(str(d) for d in durations)}ms)"
        )
    else:
        print(f"OK: gif {len(prepared)} frames -> {out} (duration={ms}ms)")


# ---------------------------------------------------------------------------
# walkgen — fisica de marcha top-down in-place (fase continua)
#
# Cada pe percorre um ciclo [0,1) com offset 0.5 (contrafase):
#   STANCE (p < 0.5): pe plantado, desliza para tras (simula chao movendo);
#                     lift=0, fwd vai de +amp → -amp.
#   SWING  (p >= 0.5): pe livre retorna a frente em ARCO; lift = lift_amp *
#                     sin(pi*s) (sobe no meio do swing, zero nas pontas);
#                     fwd vai de -amp → +amp.
# No sprite top-down, +Y = baixo = "frente"; lift sobe (subtrai de fwd).
# Corpo: bob vertical — sobe no passing (sin 2πt), desce no contact.
# Aproximacao procedural/mecanica, mas com plantio, arco e bob de peso.
# ---------------------------------------------------------------------------


def foot_dy_for_phase(p, amp, lift_amp):
    """Offset vertical de um pe para fase p em [0, 1). +Y = frente (baixo)."""
    if p < 0.5:
        # STANCE: pe plantado, desliza para tras; sem lift.
        s = p / 0.5
        fwd = amp * (1.0 - 2.0 * s)
        lift = 0.0
    else:
        # SWING: pe retorna a frente em arco (lift max no meio).
        s = (p - 0.5) / 0.5
        fwd = amp * (2.0 * s - 1.0)
        lift = lift_amp * math.sin(math.pi * s)
    return round(fwd - lift)


def walk_frame_offsets(t, amp, lift_amp, bob):
    """Offsets (body_dy, left_dy, right_dy) para t em [0, 1) do ciclo."""
    left_p = t % 1.0
    right_p = (t + 0.5) % 1.0
    left_dy = foot_dy_for_phase(left_p, amp, lift_amp)
    right_dy = foot_dy_for_phase(right_p, amp, lift_amp)
    # body sobe (dy negativo) no passing; mais baixo no contact.
    body_dy = round(-bob * abs(math.sin(2.0 * math.pi * t)))
    return body_dy, left_dy, right_dy


def paste_offset_rgba(canvas, part, x, y):
    """Cola part em (x, y) com alpha_composite; deslocamentos fora da borda clipam."""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(part, (x, y), part)
    return Image.alpha_composite(canvas, layer)


def cmd_walkgen(args):
    """Gera ciclo de caminhada top-down procedural (fisica stance/swing/bob)."""
    src = Path(args.sprite).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()

    if not src.is_file():
        sys.exit(f"Nao encontrei sprite: {src}")

    n_frames = args.frames
    if n_frames < 1:
        sys.exit("--frames deve ser >= 1")
    frac = args.leg_split
    if not (0.0 < frac < 1.0):
        sys.exit("--leg-split deve estar entre 0 e 1 (exclusivo)")
    amp = args.amp
    lift_amp = args.lift
    bob = args.bob
    scale = args.scale
    if scale < 1:
        sys.exit("--scale deve ser >= 1")

    img = Image.open(src).convert("RGBA")
    w, h = img.size
    leg_y = int(frac * h)
    if leg_y <= 0 or leg_y >= h:
        sys.exit(f"legY={leg_y} invalido para H={h} e --leg-split {frac}")

    body = img.crop((0, 0, w, leg_y))
    legs = img.crop((0, leg_y, w, h))
    mid = w // 2
    left_leg = legs.crop((0, 0, mid, legs.height))
    right_leg = legs.crop((mid, 0, w, legs.height))

    outdir.mkdir(parents=True, exist_ok=True)
    saved = []
    for i in range(n_frames):
        t = i / n_frames
        body_dy, left_dy, right_dy = walk_frame_offsets(t, amp, lift_amp, bob)

        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas = paste_offset_rgba(canvas, body, 0, body_dy)
        canvas = paste_offset_rgba(canvas, left_leg, 0, leg_y + left_dy)
        canvas = paste_offset_rgba(canvas, right_leg, mid, leg_y + right_dy)

        if scale > 1:
            canvas = canvas.resize(
                (w * scale, h * scale), Image.Resampling.NEAREST
            )

        out_path = outdir / f"frame_{i + 1:02d}.png"
        canvas.save(out_path, format="PNG")
        print(out_path)
        saved.append(out_path)

    print(
        f"OK: walkgen {len(saved)} frames (procedural/mecanico, arco+plantio+bob) "
        f"-> {outdir} — aproximacao por banda+split L/R com gait por fase; "
        f"melhor em sprites simetricos com pernas na faixa inferior."
    )


def cmd_palettes(args):
    """Lista o catalogo de paletas ou mostra as cores de uma."""
    if args.show:
        name = args.show
        if name not in PALETTES:
            valid = ", ".join(sorted(PALETTES))
            sys.exit(f"Paleta desconhecida: {name!r}. Validas: {valid}")
        for h in PALETTES[name]:
            print(f"#{h.lower()}")
        return

    for name in sorted(PALETTES):
        print(f"{name} {len(PALETTES[name])}")


def main():
    ap = argparse.ArgumentParser(description="Post-processamento de sprites 2D")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # pixelate
    p_pix = sub.add_parser("pixelate", help="Downscale + palette + upscale pixel-art")
    p_pix.add_argument("inp", metavar="IN", help="Imagem de entrada")
    p_pix.add_argument("out", metavar="OUT", help="PNG de saida")
    p_pix.add_argument("--grid", type=int, default=64, help="Resolucao logica (quadrado)")
    p_pix.add_argument("--scale", type=int, default=8, help="Upscale de exibicao")
    p_pix.add_argument(
        "--palette",
        default="none",
        help="Paleta fixa (none|db16|pico8|...) ou caminho .gpl",
    )
    p_pix.add_argument(
        "--dither",
        default="none",
        choices=["none", "ordered"],
        help="Dither na quantize (none|ordered; default none)",
    )
    p_pix.add_argument(
        "--remove-aa",
        nargs="?",
        const=128,
        default=None,
        type=int,
        metavar="THRESH",
        help="Binariza alpha (default thresh 128 se flag sozinha)",
    )
    p_pix.add_argument(
        "--outline",
        nargs="?",
        const="140c1c",
        default=None,
        metavar="HEX",
        help="Contorno 1px (default cor 140c1c se flag sozinha)",
    )
    p_pix.add_argument(
        "--outline-thresh",
        type=int,
        default=128,
        help="Limiar alpha para contorno (default 128)",
    )
    p_pix.add_argument(
        "--no-upscale",
        action="store_true",
        help="Manter saida no tamanho do grid",
    )
    p_pix.add_argument(
        "--downscale",
        default="nearest",
        choices=["nearest", "box"],
        help="Filtro no downscale para grid (default nearest; box suaviza hi-res)",
    )
    p_pix.set_defaults(func=cmd_pixelate)

    # extract-palette
    p_ext = sub.add_parser(
        "extract-palette",
        help="Extrai paleta .gpl de imagem de referencia",
    )
    p_ext.add_argument("inp", metavar="IN", help="Imagem de referencia")
    p_ext.add_argument("out", metavar="OUT.gpl", help="Paleta GIMP de saida")
    p_ext.add_argument(
        "--colors",
        type=int,
        default=16,
        help="Numero de cores (default 16)",
    )
    p_ext.set_defaults(func=cmd_extract_palette)

    # outline
    p_out = sub.add_parser("outline", help="Contorno 1px em PNG")
    p_out.add_argument("inp", metavar="IN", help="Imagem de entrada")
    p_out.add_argument("out", metavar="OUT", help="PNG de saida")
    p_out.add_argument(
        "--color",
        default="140c1c",
        help="Cor do contorno RRGGBB (default 140c1c)",
    )
    p_out.add_argument(
        "--alpha-thresh",
        type=int,
        default=128,
        help="Limiar alpha para mascara (default 128)",
    )
    p_out.set_defaults(func=cmd_outline)

    # keyout
    p_key = sub.add_parser("keyout", help="Chroma-key ou flood-fill dos cantos")
    p_key.add_argument("inp", metavar="IN", help="Imagem de entrada")
    p_key.add_argument("out", metavar="OUT", help="PNG de saida")
    p_key.add_argument("--key", default=None, help="Cor chroma RRGGBB")
    p_key.add_argument(
        "--corners",
        action="store_true",
        help="Flood-fill a partir dos 4 cantos",
    )
    p_key.add_argument("--tol", type=int, default=40, help="Tolerancia por canal")
    p_key.add_argument(
        "--defringe",
        nargs="?",
        const=1,
        default=0,
        type=int,
        metavar="N",
        help="Remove halo na borda alpha (N iteracoes; default 1 se flag sozinha)",
    )
    p_key.add_argument(
        "--defringe-tol",
        type=int,
        default=100,
        help="Tolerancia por canal no defringe (default 100)",
    )
    p_key.add_argument(
        "--shrink",
        type=int,
        default=0,
        metavar="N",
        help="Erode alpha N px apos defringe (default 0)",
    )
    p_key.set_defaults(func=cmd_keyout)

    # sheet
    p_sheet = sub.add_parser("sheet", help="Monta sprite sheet a partir de pasta")
    p_sheet.add_argument("dir", metavar="DIR", help="Pasta com frames")
    p_sheet.add_argument("out", metavar="OUT", help="PNG da sheet")
    p_sheet.add_argument(
        "--cols",
        type=int,
        default=None,
        help="Colunas (default: ceil(sqrt(n)))",
    )
    p_sheet.add_argument(
        "--padding",
        type=int,
        default=1,
        help="Gutter transparente entre frames (px)",
    )
    p_sheet.add_argument(
        "--json",
        action="store_true",
        help="Tambem grava JSON estilo Aseprite (hash)",
    )
    p_sheet.add_argument(
        "--engine",
        default="aseprite",
        choices=["aseprite", "unity", "godot", "texturepacker"],
        help="Preset de meta no JSON (default: aseprite)",
    )
    p_sheet.add_argument(
        "--format",
        default="json-hash",
        choices=["json-hash", "json-array"],
        help="Formato do campo frames no JSON (default: json-hash)",
    )
    p_sheet.add_argument(
        "--durations",
        default=None,
        metavar="CSV",
        help="Duracao por frame em ms (ex: 100,100,80,100)",
    )
    p_sheet.add_argument(
        "--tag",
        action="append",
        default=None,
        metavar="SPEC",
        help="Tag de animacao name:from-to[:forward|reverse|pingpong] (1-based)",
    )
    p_sheet.set_defaults(func=cmd_sheet)

    # gif
    p_gif = sub.add_parser("gif", help="Monta GIF animado a partir de PNGs")
    p_gif.add_argument("dir", metavar="DIR", help="Pasta com frames PNG")
    p_gif.add_argument("out", metavar="OUT", help="GIF de saida")
    p_gif.add_argument("--fps", type=float, default=8, help="Frames por segundo")
    p_gif.add_argument(
        "--duration",
        type=int,
        default=None,
        help="Duracao por frame em ms (sobrescreve --fps)",
    )
    p_gif.add_argument(
        "--durations",
        default=None,
        metavar="CSV",
        help="Duracao por frame em ms (sobrescreve --fps/--duration)",
    )
    p_gif.set_defaults(func=cmd_gif)

    # walkgen
    p_walk = sub.add_parser(
        "walkgen",
        help="Ciclo de caminhada top-down procedural a partir de 1 sprite",
    )
    p_walk.add_argument("sprite", metavar="SPRITE", help="PNG estatico (RGBA)")
    p_walk.add_argument("outdir", metavar="OUTDIR", help="Pasta de saida dos frames")
    p_walk.add_argument(
        "--frames",
        type=int,
        default=4,
        help="Numero de frames do ciclo (default 4; loop seamless)",
    )
    p_walk.add_argument(
        "--leg-split",
        type=float,
        default=0.74,
        metavar="FRAC",
        help="Fracao da altura onde comecam as pernas (default 0.74)",
    )
    p_walk.add_argument(
        "--amp",
        type=int,
        default=3,
        help="Amplitude fwd/back do pe em px (default 3)",
    )
    p_walk.add_argument(
        "--lift",
        type=int,
        default=2,
        help="Amplitude de lift do pe no arco de swing em px (default 2)",
    )
    p_walk.add_argument(
        "--bob",
        type=int,
        default=1,
        help="Pixels de bob vertical do corpo (default 1)",
    )
    p_walk.add_argument(
        "--scale",
        type=int,
        default=1,
        help="Upscale nearest de preview (default 1)",
    )
    p_walk.set_defaults(func=cmd_walkgen)

    # palettes
    p_pal = sub.add_parser("palettes", help="Lista paletas do catalogo")
    p_pal.add_argument(
        "--show",
        default=None,
        metavar="NAME",
        help="Mostra cores hex de uma paleta",
    )
    p_pal.set_defaults(func=cmd_palettes)

    # setup
    p_setup = sub.add_parser(
        "setup",
        help="Detecta ou configura o binario Aseprite",
    )
    p_setup.add_argument(
        "--path",
        default=None,
        metavar="P",
        help="Valida e salva caminho do Aseprite",
    )
    p_setup.add_argument(
        "--detect",
        action="store_true",
        help="Auto-detecta via PATH/Steam e salva no config",
    )
    p_setup.set_defaults(func=cmd_setup)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
