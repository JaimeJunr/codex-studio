# Roadmap — keyless-studio

Ideias aprovadas para depois. Não são compromissos de versão; são direções que já validamos que fazem sentido.

## Família game dev / pixel art

### MCP de edição procedural de pixel art (planejado)
Hoje o motor é **gerar via Codex + pós-processar** (`spritekit.py`: keyout, pixelate, quantize, outline, sheet, gif). Isso não deixa o agente **editar a arte pixel a pixel** depois de gerada.

Adicionar um **servidor MCP de edição** (inspiração: [willibrandon/pixel-mcp](https://github.com/willibrandon/pixel-mcp), que dirige o Aseprite headless via Lua) daria ao agente ferramentas para **desenhar e refinar diretamente**, complementando — não substituindo — o fluxo generate+pós:

- **Canvas/layers**: `create_canvas`, `add_layer`, `flatten`.
- **Desenho**: `draw_pixels`, `draw_line`, `draw_rectangle`, `draw_circle`, `fill_area`, `draw_contour`.
- **Seleção/clipboard**: select rect/ellipse, cut/copy/paste, move.
- **Pro**: `apply_outline`, `apply_shading`, `draw_with_dither` (Bayer/checker/materiais), `suggest_antialiasing`, `quantize_palette`.
- **Animação**: frames, `set_frame_duration`, tags, `link_cel`.

Racional: gerar dá o rascunho; a edição procedural dá o **controle fino** (corrigir um cluster, reforçar silhueta, ajustar um frame) sem sair pro Aseprite manual. O `spritekit.py` já cobre o pós em lote; o MCP cobriria a edição interativa.

Notas de implementação quando chegar a hora:
- Provavelmente um servidor dedicado dirigindo o **Aseprite CLI + Lua** (o binário já é detectado por `spritekit.py setup`). Reusar essa detecção de caminho.
- Auditar o approach do pixel-mcp: as ferramentas de **desenho/shading** dele fazem snap de cor em **RGB euclidiano** (apesar do README dizer "LAB"); só o pipeline de **quantização/extração** usa CIELAB. Ao portar, decidir conscientemente a métrica por ferramenta.

### extract-palette em LAB (refinamento)
O `spritekit.py extract-palette` atual usa median-cut em RGB (dep-free, só Pillow). Um modo LAB (k-means em CIELAB, como o `analyze_reference` do pixel-mcp) daria paletas perceptualmente melhores — exige `numpy` (opcional) ou o próprio Aseprite. Manter o RGB como fallback dep-free.

### Craft library
Continuar expandindo `references/` (hue-shifting, timing de animação, dither por material, recipes de material) conforme surgirem novos estilos e materiais.
