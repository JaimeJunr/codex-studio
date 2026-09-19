---
name: social
description: Gera criativos on-brand pra redes sociais via Codex — capa/slides de carrossel, capa de story/reel, quote card, criativo de anúncio. Use quando o usuário quer a IMAGEM do post pronta (não só o texto). Depende do keyless-image.
---

# keyless-social:social — criativos on-brand pra redes

Gera a **imagem** do post via `keyless-image` (Codex, keyless), on-brand. Não escreve a estratégia (isso é do fluxo de conteúdo do projeto) — aqui é a arte.

## Tipos e aspect ratio

| Tipo | Aspect | Notas |
|---|---|---|
| Capa de carrossel | 4:5 | Título forte, gancho; slides seguintes com 1 ideia cada |
| Slide de carrossel | 4:5 | Consistência de grid/tipografia entre slides |
| Story / Reel cover | 9:16 | Texto na metade superior (safe zone), CTA embaixo |
| Quote card | 1:1 ou 4:5 | Frase verbatim em destaque + crédito |
| Criativo de anúncio | 1:1 / 4:5 / 9:16 | Benefício claro + CTA; evitar excesso de texto |

## Fluxo

1. **Marca:** leia o guia do projeto (`identidade/design-guide.md`, `DESIGN.md` ou `references/`): paleta HEX, tipografia, estilo, "o que NÃO fazer". Sem guia, pergunte 2-3 refs rápidas.
2. **Texto na arte:** títulos/frases via `EXACT TEXT: "..."` (curto). Frase de cliente = verbatim, não reescreva. Parágrafo longo → sobrepor depois, não pedir pro modelo.
3. **Gerar via `keyless-image:generate`** no aspect ratio certo, salvando no projeto (generate-then-move) — ex: `marketing/imagens/` ou `assets/social/`.
4. **Carrossel multi-slide:** uma chamada por slide, mesmo bloco de estilo em todas pra consistência.
5. **Revisar:** legibilidade do texto, contraste, safe zone. Ofereça 1 ajuste. Nada publicado sem aprovação de quem decide.

## Nunca

- Reescrever frase verbatim do cliente.
- Encher de texto (rede penaliza; e texto longo tremula no modelo).
- Deixar asset só no cache do Codex.
