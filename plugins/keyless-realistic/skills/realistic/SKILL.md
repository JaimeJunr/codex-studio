---
name: realistic
description: Especialista em arte realista/semi-realista (painterly) pra jogos — personagens, props, ícones e key art com volume, iluminação direcional, textura e detalhe. Especialização de estilo sobre keyless-sprite: herda o fluxo game dev e injeta o bloco de estilo realista; pós = remoção de fundo pra alpha (sem pixelate). Depende de keyless-sprite e keyless-image.
---

# keyless-realistic:realistic — arte realista/painterly

Especialização de **estilo** sobre `keyless-sprite`. Herda o fluxo `keyless-sprite:sprite`, troca o bloco de estilo + o pós. Alvo: 2D realista/semi-realista pintado — RPG/estratégia, ícones detalhados, key art e retratos.

## Bloco de estilo (injete em todo prompt)

```
semi-realistic game art, [assunto], [vista], painterly rendering,
volumetric form, directional lighting, detailed textures,
rich shading, subtle color grading, high detail, artstation quality,
solid bright green background
```
Negativos: `pixel art, flat cartoon, hard outline, low detail, sticker look`. Coeso = mesma direção/temperatura de luz + mesma densidade de detalhe entre assets.

## Fluxo

Siga `keyless-sprite:sprite`:

1. **Briefing / âncora / derivar** — igual à base pai, com o bloco de estilo realista e fundo chroma. Iluminação consistente é a trava de coesão; use edição referenciada (`keyless-image:edit`) pra variações.
2. **Pós** (script `spritekit.py` do keyless-sprite):
   ```
   # fundo → alpha (contornos suaves → prefira --corners ou key limpo)
   spritekit.py keyout frame.png frame.png --corners --tol 30
   # sheet + json (útil pra ícones/props; personagens realistas raramente animam por sheet)
   spritekit.py sheet <projeto>/frames <projeto>/sheet.png --json
   ```
   **Não** rode `pixelate`. Realista costuma ser **alta resolução** — não force grid pequeno.
3. **Reportar** — caminhos + nota de que é asset painterly (import sem filtro Point).

## Nunca

- Rodar `pixelate` ou impor paleta limitada (mata o realismo).
- Prometer consistência perfeita de rosto/anatomia entre frames — é o ponto mais frágil; ofereça ajuste.
- Misturar `flat cartoon`/`pixel art` no bloco de estilo.
- Entregar com fundo colado — sempre `keyout` (bordas suaves → `--corners` costuma limpar melhor).
