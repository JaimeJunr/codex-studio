---
name: web-visuals
description: Gera visuais pra produção de site via Codex — hero image, OG/social card, ilustração de seção, background/textura e favicon. Use ao construir/refatorar um site e precisar de imagens on-brand coerentes entre si. Depende do codex-image.
---

# codex-web:web-visuals — visuais pra site

Gera os assets visuais de um site via `codex-image` (Codex, keyless), mantendo **coerência visual entre os slots** (hero, cards, seções).

## Requisito
`codex-image` instalado. Ideal: um `DESIGN.md`/guia de marca no projeto (paleta, tipografia, estilo de ilustração) pra tudo sair coerente.

## Slots e specs

| Slot | Aspect/size | Notas |
|---|---|---|
| Hero | 16:9 (ou 21:9) | Espaço "limpo" pra headline/CTA por cima em HTML/CSS — não queime muito texto na imagem |
| OG / social card | 1200×630 (~1.91:1) | Título curto legível (`EXACT TEXT`), logo, alto contraste |
| Ilustração de seção | 1:1 ou 4:3 | Série coerente (mesmo traço/paleta) entre seções |
| Background / textura | conforme uso | Sutil, não competir com o conteúdo |
| Favicon | 1:1, símbolo simples | Gerar em alta e reduzir; formas simples leem melhor em 16px |

## Fluxo

1. **Coerência primeiro:** fixe o bloco de estilo (paleta HEX, traço, mood) do `DESIGN.md` e reuse em TODOS os slots — é o que faz o site parecer de uma marca só.
2. **Texto:** em hero, prefira **texto real em HTML/CSS** sobre a imagem (nítido, acessível, i18n) — gere a imagem com "espaço de respiro" pro texto. OG card pode ter título curto burnado via `EXACT TEXT`.
3. **Gerar via `codex-image:generate`**, salvando direto na árvore do site (`public/`, `assets/img/`) — generate-then-move.
4. **Peso:** lembre de otimizar (o modelo gera PNG grande); sugira converter pra WebP e dimensionar pro uso real.

## Nunca
- Queimar headline longa na imagem do hero (use HTML/CSS por cima).
- Assets do site inconsistentes entre si (sempre o mesmo bloco de estilo).
- Deixar asset só no cache do Codex.
