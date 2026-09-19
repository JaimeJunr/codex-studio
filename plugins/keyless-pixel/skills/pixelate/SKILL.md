---
name: pixelate
description: Especialista em pixel art autêntico pra jogos — sprites, sheets, tilesets e ícones com grid inteiro real, paleta limitada (DB16/PICO-8/NES), hard edges e sem anti-aliasing. Especialização de estilo sobre keyless-sprite: herda o fluxo game dev e adiciona o bloco de estilo pixel + o pós obrigatório (downscale nearest + quantize de paleta). Depende de keyless-sprite (fluxo + script) e keyless-image.
---

# keyless-pixel:pixelate — pixel art autêntico

Especialização de **estilo** sobre `keyless-sprite`. Não reescreve o fluxo: **herda** `keyless-sprite:sprite` (briefing → âncora → derivar → sheet) e injeta (a) o bloco de estilo pixel art e (b) o pós **obrigatório** que transforma a saída borrada da IA em pixel art de verdade. Fundamentos em `references/pixel-art.md`.

> **Herda as Regras de fluxo invioláveis** de `keyless-sprite:sprite`: entreviste ANTES de gerar; você dita a ordem de produção (não pergunte "em que ordem"); contorne moderação/IP antes (design original desde o 1º prompt); sprite pequeno pede prompt sprite-oriented (chibi/overhead/formas simples).

## Por que o pós é obrigatório

Modelos de difusão dão gradientes suaves e grid quebrado — "pixel art falso". O prompt sozinho não resolve. O passo `pixelate` (downscale nearest + quantize de paleta, sem dither) é o que torna o asset game-ready. Sem ele, **não é pixel art**.

## Bloco de estilo (injete em todo prompt)

```
8-bit / 16-bit pixel art sprite, [assunto], [vista],
NN×NN pixel grid, limited palette, flat cel shading,
clean color clusters, 1-pixel dark outline,
hard pixel edges, no anti-aliasing, no smooth gradients, no blur
```
Negativos: `anti-aliased, blurred edges, soft gradients, painterly, photorealistic, mixed pixel sizes`. Escolha a resolução (16/32/64) e a paleta (`db16`/`pico8`/`nes`) no briefing — ver `references/pixel-art.md`.

## Fluxo

Siga `keyless-sprite:sprite`, com estas diferenças:

1. **Briefing** — defina resolução alvo (`--grid`) e paleta. Silhueta primeiro.
2. **Âncora / derivar** — igual à base pai, com o bloco de estilo pixel + fundo chroma.
3. **Pós obrigatório** (script `spritekit.py` do keyless-sprite, dependência):
   ```
   # remover fundo → alpha SEM halo. shrink 1 (2 come o outline); defringe descasca a borda contaminada
   spritekit.py keyout frame.png frame.png --corners --tol 60 --defringe 2 --shrink 1
   # pixelizar: --outline reconstrói a borda preta; --downscale nearest (crisp) p/ sprite chapado
   spritekit.py pixelate frame.png frame.png --grid 32 --palette db16 --downscale nearest --remove-aa --outline --no-upscale
   ```
   `--no-upscale` gera o asset REAL no grid (ex: 32×32 / 48×48); `--scale N` só pra preview ampliado — entregue os dois. Ordem: `keyout` antes de `pixelate` (preserva o alpha). Fundo chroma deve ser uma cor que NÃO exista no personagem (magenta p/ herói esverdeado; verde p/ personagem sem verde) — senão o keyout come o personagem.
   - **Paletas** (`--palette`): `db16`, `db32`, `pico8`, `nes`, `snes`, `gameboy`, `gameboy-gray`, `c64`, `cga`, `sweetie16`, `gray4/8/16`. Ver `references/pixel-art.md`; listar com `/keyless-sprite:palette`.
   - **Backend Aseprite** (recomendado): se o usuário tem Aseprite, rode `/keyless-sprite:setup` uma vez — o `pixelate` passa a usar o Aseprite pra quantize+dither de qualidade (imprime `[via aseprite]`), com `--dither ordered` fazendo dithering Bayer real. Sem Aseprite, cai no Pillow automaticamente (`[via Pillow]`, sem dither real).
4. **Sheet / GIF** — `spritekit.py sheet ... --json [--engine unity|godot]` e/ou `gif ... --fps 8` pra prévia do ciclo (ou `/keyless-sprite:export`).
5. **Cleanup opcional** — clusters/órfãos/outline no Aseprite/LibreSprite.

## Atalhos

`/keyless-pixel:new [grid] [paleta]` (ex.: `32 gameboy`) inicia o fluxo; `/keyless-sprite:setup`, `/keyless-sprite:palette`, `/keyless-sprite:export` operam o script.

## Nunca

- Entregar como "pixel art" sem rodar o `pixelate` (senão é só imagem borrada).
- Usar bilinear/bicubic no passo do grid — só nearest-neighbor.
- Paleta incoerente entre assets do mesmo jogo — trave uma paleta e reuse.
- AA/gradiente no resultado final — remova no pós.
