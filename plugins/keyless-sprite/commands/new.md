---
description: Inicia um novo asset 2D de jogo (personagem, sheet, tileset, item, UI) pelo fluxo keyless-sprite.
argument-hint: [tipo] [descrição]
---

Inicie o fluxo da skill **keyless-sprite:sprite** para um novo asset de jogo.

Pedido: "$ARGUMENTS"

Conduza o briefing (tipo · vista · estilo · tamanho · engine-alvo), gere a **pose-âncora primeiro** (trava de qualidade — não gere tudo de cara), e só depois derive o restante por edição referenciada. Se o estilo for pixel art / cartoon / realista, aplique a especialização correspondente (`keyless-pixel` / `keyless-cartoon` / `keyless-realistic`).
