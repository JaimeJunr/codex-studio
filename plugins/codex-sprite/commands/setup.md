---
description: Configura o Aseprite (backend de qualidade do pixel art) — detecta automaticamente ou fixa o caminho do binário.
argument-hint: [--detect | /caminho/do/aseprite]
allowed-tools: Bash
---

Configure o backend **Aseprite** do codex-sprite. O `spritekit.py` usa o Aseprite quando disponível (quantize indexed + dithering + paleta `.gpl` de qualidade) e cai pro Pillow quando não há.

Argumento recebido: "$ARGUMENTS"

- **Sem argumento** ou `--detect` → tenta achar sozinho (PATH + instalações Steam via `libraryfolders.vdf`):
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spritekit.py" setup --detect`
- **Caminho explícito** (Steam em disco custom costuma NÃO ser catalogado no `.vdf` — ex.: `.../SteamLibrary/steamapps/common/Aseprite/aseprite`):
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spritekit.py" setup --path "$ARGUMENTS"`
- **Só ver o estado atual** (sem flag): `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/spritekit.py" setup`

O caminho fica salvo em `~/.config/codex-sprite/config.json`. Reporte a versão e o caminho resolvido. Se `--detect` falhar, peça o caminho do binário e rode `setup --path`.
