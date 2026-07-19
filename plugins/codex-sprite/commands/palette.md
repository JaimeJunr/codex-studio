---
description: Lista as paletas nomeadas de pixel art ou mostra as cores de uma delas.
argument-hint: [list | show <nome>]
allowed-tools: Bash
---

Paletas nomeadas do codex-sprite (usadas no `pixelate`/quantize).

Argumento: "$ARGUMENTS"
- vazio ou `list` → `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spritekit.py" palettes`
- `show <nome>` → `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spritekit.py" palettes --show <nome>`

Disponíveis: `db16`, `db32`, `pico8`, `nes`, `gameboy`, `gameboy-gray`, `c64`, `cga`, `snes`, `sweetie16`, `gray4`, `gray8`, `gray16`. Mostre o resultado do comando.
