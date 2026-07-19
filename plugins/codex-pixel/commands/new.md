---
description: Inicia um novo sprite de pixel art com resolução e paleta definidas.
argument-hint: [tamanho] [paleta]  — ex.: 32 gameboy
---

Inicie a skill **codex-pixel:pixelate** para um novo sprite de pixel art.

Argumentos: "$ARGUMENTS" — interprete como `[grid] [paleta]` (ex.: `32 gameboy`, `64 db32`, `16 pico8`). Se faltar algo, resolva no briefing.

Fluxo: briefing (assunto · vista · silhueta) → **âncora** → derivar → pós **obrigatório** (`keyout` + `pixelate --grid <n> --palette <paleta>` via o script do `codex-sprite`; usa Aseprite se configurado com `/codex-sprite:setup`, senão Pillow). Paletas: `db16`, `db32`, `pico8`, `nes`, `gameboy`, `gameboy-gray`, `c64`, `cga`, `snes`, `sweetie16`, `gray4/8/16`. Opcional `--dither ordered` (Aseprite faz dither de verdade).
