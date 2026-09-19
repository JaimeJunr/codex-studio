---
description: Inicia um novo asset 2D de jogo (personagem, sheet, tileset, item, UI) pelo fluxo codex-sprite.
argument-hint: [tipo] [descrição]
---

Inicie o fluxo da skill **codex-sprite:sprite** para um novo asset de jogo.

Pedido: "$ARGUMENTS"

Conduza o briefing (tipo · vista · estilo · tamanho · engine-alvo), gere a **pose-âncora primeiro** (trava de qualidade — não gere tudo de cara), e só depois derive o restante por edição referenciada. Se o estilo for pixel art / cartoon / realista, aplique a especialização correspondente (`codex-pixel` / `codex-cartoon` / `codex-realistic`).
