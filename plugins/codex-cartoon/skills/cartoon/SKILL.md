---
name: cartoon
description: Especialista em arte cartoon/toon pra jogos — sprites, personagens e assets com cores chapadas, contorno marcado (bold outline), formas exageradas e leitura limpa (estilo vetor/mobile game). Especialização de estilo sobre codex-sprite: herda o fluxo game dev e injeta o bloco de estilo cartoon; pós = remoção de fundo pra alpha (sem pixelate). Depende de codex-sprite e codex-image.
---

# codex-cartoon:cartoon — arte cartoon/toon

Especialização de **estilo** sobre `codex-sprite`. Herda o fluxo `codex-sprite:sprite` e troca só o bloco de estilo + o pós. Alvo: cartoon vetorial/mobile — cores chapadas, contorno grosso, apelo "cute/hero".

## Bloco de estilo (injete em todo prompt)

```
cartoon game art, [assunto], [vista], bold clean outline,
flat vibrant colors, cel shading, soft rounded shapes,
exaggerated proportions, high readability, vector illustration style,
smooth edges, solid bright green background
```
Negativos: `pixel art, photorealistic, gritty, noisy texture, dull colors, realistic lighting`. Coeso = contorno de espessura constante + paleta viva limitada + mesma linguagem de forma entre assets.

## Fluxo

Siga `codex-sprite:sprite`:

1. **Briefing / âncora / derivar** — igual à base pai, com o bloco de estilo cartoon e fundo chroma sólido. Consistência via edição referenciada (`codex-image:edit`).
2. **Pós** (script `spritekit.py` do codex-sprite):
   ```
   # fundo chroma → alpha (NÃO pixelize cartoon)
   spritekit.py keyout frame.png frame.png --key 00ff00
   # sheet + json
   spritekit.py sheet <projeto>/frames <projeto>/sheet.png --cols 6 --padding 1 --json
   ```
   Cartoon **mantém** as bordas suaves — **não** rode `pixelate`.
3. **Reportar** — caminhos + preset de import (aqui o filtro pode ser Bilinear, não Point).

## Nunca

- Rodar `pixelate` (destrói o traço cartoon).
- Contorno de espessura variável entre assets (quebra a coesão).
- Misturar realismo/textura suja no bloco de estilo.
- Entregar com fundo colado — sempre `keyout`.
