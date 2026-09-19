# codex-pixel

**Especialista em pixel art autêntico** do codex-studio. Especialização de **estilo** sobre o `codex-sprite`: herda o fluxo game dev (briefing → âncora → derivar → sheet) e adiciona o bloco de estilo pixel + o pós **obrigatório** que transforma a saída borrada da IA em pixel art de verdade (grid inteiro, paleta limitada, hard edges).

## Skill & comandos

- **`codex-pixel:pixelate`** — pixel art game-ready com resolução (16/32/64) e paleta travadas.
- **`/codex-pixel:new [tamanho] [paleta]`** — atalho (ex.: `32 gameboy`).

Paletas: `db16`, `db32`, `pico8`, `nes`, `snes`, `gameboy`, `gameboy-gray`, `c64`, `cga`, `sweetie16`, `gray4/8/16`.

## Por que o pós é obrigatório

Modelos de difusão dão gradientes suaves e grid quebrado ("pixel art falso"). O prompt não resolve — o passo `spritekit.py pixelate` (downscale nearest + quantize) é o que torna o asset game-ready.

## Aseprite (recomendado)

Com Aseprite configurado (`/codex-sprite:setup`), a quantização + dithering roteia pro Aseprite headless (qualidade superior, `--dither ordered` = Bayer real). Sem ele, o Pillow faz o fallback. Ver [`references/pixel-art.md`](references/pixel-art.md).

## Requisitos

- `codex-sprite` instalado (fluxo base + script `spritekit.py`).
- `codex-image` (motor keyless).
- `pip install Pillow`; **Aseprite** opcional (qualidade).

## Referências

- [`references/pixel-art.md`](references/pixel-art.md) — resoluções, paletas, dithering, AA, clusters/banding, outlines, por que a IA erra pixel art, pipeline obrigatório.
