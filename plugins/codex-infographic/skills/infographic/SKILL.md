---
name: infographic
description: Transforma número/dado/métrica numa imagem infográfica on-brand via Codex — big number, comparativo, timeline, funil, antes/depois. Use pra destacar um dado de forma visual (post, slide, relatório). Depende do codex-image.
---

# codex-infographic:infographic — dado vira visual

Gera uma imagem infográfica on-brand destacando um dado, via `codex-image` (Codex, keyless).

## ⚠️ Honestidade sobre dados

Modelo de imagem **não é ferramenta de gráfico exato** — barras/pizzas geradas são *aproximadas*. Portanto:
- **Bom pra:** big number ("+120 famílias"), comparativo simples, timeline, funil, antes/depois, destaque qualitativo — onde o **número exato é escrito como texto** (`EXACT TEXT`) e o visual é ilustrativo.
- **Ruim pra:** gráfico que precisa ser proporcionalmente exato (série temporal, distribuição). Nesse caso, **avise** e sugira gerar o gráfico real (matplotlib/lib de chart) e, se quiser, usar `codex-image:edit` só pra emoldurar on-brand.

## Fluxo

1. **Dado + mensagem:** qual número e o que ele significa (a conclusão, não só o valor). Sem dado real → `[PENDENTE]`, não invente.
2. **Metáfora visual:** escolha (big number / comparativo / timeline / funil / antes-depois) conforme a mensagem.
3. **Marca:** paleta HEX + estilo do guia do projeto.
4. **Gerar via `codex-image:generate`:** o número exato entra como `EXACT TEXT: "..."`; o resto é ilustração on-brand. Aspect conforme destino (1:1/4:5 post, 16:9 slide). generate-then-move.
5. **Revisar:** o número está legível e correto? Ofereça 1 ajuste.

## Nunca

- Passar gráfico aproximado como se fosse dado exato.
- Inventar número. Aprovação de quem decide antes de publicar.
