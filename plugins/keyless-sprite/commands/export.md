---
description: Exporta assets já gerados — sprite sheet (+JSON de engine), GIF animado, ou pixeliza frames.
argument-hint: [sheet|gif|pixelate] <dir/arquivo> [opções]
allowed-tools: Bash
---

Empacote/exporte os frames de um projeto de sprite via `spritekit.py`. Escolha o subcomando pela intenção do pedido: "$ARGUMENTS"

- **Sprite sheet + JSON**: `sheet <dir_frames> <out.png> --cols N --padding 1 --json --engine unity|godot|aseprite|texturepacker --format json-hash|json-array`
- **GIF animado** (preview do ciclo): `gif <dir_frames> <out.gif> --fps 8`
- **Pixelizar** (grid + paleta): `pixelate <in.png> <out.png> --grid 32 --palette <nome> [--dither ordered]`

Rode `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spritekit.py" <subcomando> ...` com os caminhos do projeto atual e confirme os arquivos gerados. Se a paleta for pixel art e o Aseprite estiver configurado (`/keyless-sprite:setup`), o `pixelate` usa o motor Aseprite automaticamente.
