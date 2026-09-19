# Referência: pixel art autêntico

Fundamentos pra pixel art *de verdade* (grid inteiro + placement intencional), não o "look blocado" borrado que a IA cospe por padrão. Complementa `keyless-sprite/references/sprites.md` (convenções de sheet/engine).

## Por que a IA erra pixel art

Modelos de difusão operam em **espaço contínuo** → gradientes suaves, blending subpixel, milhares de cores quase-iguais. Aprendem pixel art como **textura**, não como **grid discreto**. Falhas típicas: células de tamanho não-inteiro (6.38px), *subpixel bleeding*, bordas anti-aliased (halos cinza), output 1024×1024 escondendo o grid implícito.

**Conclusão:** o prompt sozinho quase nunca dá pixel art game-ready. O pós-processamento (`spritekit.py pixelate`) é **obrigatório**, não opcional.

## Resoluções canônicas

| Tamanho | Papel | Cores típicas |
|---|---|---|
| **16×16** | Ícones, pickups, sprites NES-style | 4–8 |
| **32×32** | Padrão indie: sprites, props, faces | 8–16 |
| **64×64** | Mascotes, retratos, objetos ricos | 16–32 |

16×16 = símbolo, 32×32 = sprite legível, 64×64 = personalidade. Display sempre em **upscale inteiro** (2×/4×/8×), nunca fracionário.

## Paletas limitadas (catálogo embutido no `spritekit.py`)

| Paleta | Cores | Uso |
|---|---|---|
| **db16** (DawnBringer 16) | 16 | Propósito geral, bons ramps |
| **db32** (DawnBringer 32) | 32 | Geral com mais nuance; preserva bem cores originais |
| **pico8** | 16 | Coesão retro fantasy-console |
| **nes** | 54 | Hardware NES; sprites = 3 cores + alpha por tile |
| **snes** (Super16) | 16 | Vibe 16-bit saturada |
| **gameboy** | 4 | Verde-oliva DMG clássico |
| **gameboy-gray** | 4 | 4 tons de cinza (DMG mono) |
| **c64** | 16 | Commodore 64 |
| **cga** | 16 | IBM CGA RGBI |
| **sweetie16** | 16 | GrafxKid, moderna e versátil |
| **gray4 / gray8 / gray16** | 4/8/16 | Rampas de cinza (shading, mockup) |

Lista/mostra pela CLI: `spritekit.py palettes` e `palettes --show <nome>` (ou `/keyless-sprite:palette`). **Contraste de valor > contagem de matiz** — cores de brilho parecido borram no tamanho pequeno.

## Backend Aseprite (opcional, caminho de qualidade)

Quando o Aseprite está configurado (`/keyless-sprite:setup` → grava o caminho, detecta Steam via `libraryfolders.vdf`), o `pixelate` roteia a **quantização + dithering** pro Aseprite headless (`aseprite -b … --color-mode indexed`), que é superior ao Pillow: dithering ordered/Bayer real (`--dither ordered`), quantize indexed fiel. Sem Aseprite, cai pro Pillow (nearest + quantize, sem dither de verdade) — o resultado ainda é pixel art válido, só sem o refino. O downscale ao grid é sempre Pillow (idêntico nos dois caminhos).

## Técnicas core

- **Dithering** — alternância de 2 cores fingindo uma terceira (xadrez, Bayer). Necessidade retro, hoje estético. Ruidoso abaixo de ~32×32.
- **Anti-aliasing manual** — 1px de meio-tom só em **diagonais/curvas**, proporcional ao segmento; pule retas e 45°. AA demais = borrão no pequeno e dificulta animação. Na saída da IA, geralmente **remova** o AA (snap ao vizinho).
- **Clusters vs banding** — agrupe cores sólidas; evite ruído de 1px órfão. *Banding* (linhas de sombra paralelas colando no contorno) achata → varie largura ou rotacione o ramp.
- **Pillow shading** (sombrear da borda pra dentro) achata — evite; sombreie pela fonte de luz.
- **Sub-pixel animation** — movimento < 1px deslocando cor/AA interno, não o grid.
- **Outlines** — *hard outline* (máxima leitura, NES/SNES) vs *sel-out* (linha escura no lado sombra, clara no lado luz) vs *sem outline* (exige contraste forte; ok em tiles, arriscado em personagem).
- **Leitura no pequeno** — silhueta primeiro (teste do squint), ≤8 cores a 16×16, teste a 100% zoom, remova pixels antes de adicionar detalhe.

## Bloco de estilo (prompt)

```
8-bit / 16-bit pixel art sprite, [assunto], [vista],
NN×NN pixel grid, limited palette, flat cel shading,
clean color clusters, 1-pixel dark outline,
hard pixel edges, no anti-aliasing, no smooth gradients, no blur
```

Tokens úteis: `NES palette`, `SNES-era`, `dithering shading`, `strong silhouette`, `consistent baseline`. Negativos (prompt + filtro no pós): `anti-aliased, blurred edges, soft gradients, painterly, photorealistic, mixed pixel sizes`.

## Pipeline obrigatório

```
gerar (prompt travado, fundo chroma)
  → keyout       (remove fundo → alpha)     spritekit.py keyout --key 00ff00
  → pixelate     (downscale NEAREST + quantize paleta [+ dither])
                    spritekit.py pixelate --grid 32 --palette db16 [--dither ordered]
                    (usa Aseprite se configurado, senão Pillow)
  → sheet/gif    (empacota o ciclo)         spritekit.py sheet … --json  /  gif … --fps 8
  → cleanup manual (clusters, órfãos, outline) no Aseprite/LibreSprite se precisar
```

Nunca use bilinear/bicubic/lanczos no passo do grid — só **nearest-neighbor**. True pixel art = uma cor por célula, grid alinhado, hard edges, paleta limitada.
