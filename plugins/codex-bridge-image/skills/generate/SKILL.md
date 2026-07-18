---
name: generate
description: Gera ou edita imagem (bitmap) dentro do Claude Code via cursor-mcp-bridge → Codex (gpt-image-2), sem API key. Use para CRIAR imagem nova ou ALTERAR uma existente (fundo, objeto, cor, logo, variação). Salva no projeto via out_path. Para vetor/HTML/CSS, não use esta skill.
---

# codex-bridge-image:generate — gerar/editar imagem keyless via cursor-mcp-bridge

Cria ou edita imagem bitmap via o MCP `cursor-bridge`, tool **`mcp__cursor-bridge__generate_image`**. O bridge roda `codex exec` com `image_gen` / **gpt-image-2** — **sem API key**, usa a assinatura ChatGPT/Codex do usuário. A tool já faz generate-then-move e devolve **só o caminho do PNG salvo** (nunca bytes inline).

## Quando usar / não usar

- **Use** pra criar imagem nova: foto, ilustração, mockup, capa, textura, sprite, slide-imagem, cutout.
- **Use** pra editar imagem existente: trocar fundo, remover/adicionar objeto, mudar cor/estilo, inserir logo/texto, variação a partir de referência.
- **Não use** pra: editar SVG/vetor/ícone existente, montar UI em HTML/CSS/canvas, ou estender um sistema de logo — isso é código-nativo, não bitmap.

## Pré-requisito

MCP `cursor-bridge` disponível (`cursor-mcp-bridge` clonado, `npm run build`, `CURSOR_MCP_BRIDGE_DIST` apontando pro `dist/index.js`). Codex CLI instalado + logado (o bridge chama `codex exec`). Se **não** estiver:
- Não trave. Gere o **prompt pronto** e diga: "cole no chatgpt.com/images" (e, na edição, junto com a imagem original). Informe que instalar o bridge + Codex CLI destrava a geração automática.

## Fluxo

### 1. Contexto de marca (se houver)
Se o projeto tem um guia de estilo (`identidade/design-guide.md`, `DESIGN.md`, ou `references/`), leia: paleta (HEX), estilo de imagem, "o que NÃO fazer". Sem guia, gere neutro e diga que ficou genérico.

### 2. Montar o prompt (`description`)

**Geração do zero** — estrutura de 5 partes. Ordem: **sujeito+ação → cenário/ambiente → iluminação → paleta (cores reais, HEX→"warm terracotta") + estilo → composição/enquadramento**. Prosa natural, sem flags.

**Edição** — passe `input_images` com caminhos das imagens de origem e use Keep/Change no `description`:
```
Edit this image. Keep: <o que preservar — sujeito, enquadramento, identidade do produto, texto>.
Change: <a alteração única e específica>.
Style: <paleta em cores reais, iluminação, mood on-brand>.
Do not: <itens do "o que NÃO fazer" do guia de estilo>.
```
- **Uma alteração por vez.** Encadeie: edita, salva, edita de novo.
- Preserve invariantes agressivamente (rosto/texto/marca não mudam salvo se pedido).
- Salve **não-destrutivo** (não sobrescreva o original); versione (`-v2`, `-v3`).

**Texto dentro da imagem (geração ou edição):**
- Literal com marcador: `EXACT TEXT: "Movimento é liberdade"` (aspas duplas).
- Rótulo curto sai quase perfeito; **parágrafo longo tremula** — pra texto longo, gere sem o texto e sobreponha depois (HTML/CSS ou editor).
- Nome de marca difícil: soletre letra a letra.

Mostre o prompt ao usuário **antes** de gerar (pré-aprovação), salvo quando for só preview/brainstorm.

### 3. Chamar `mcp__cursor-bridge__generate_image` ⚠️

Parâmetros:
- **`description`** (obrigatório): prompt de geração ou edição (ver §2).
- **`out_path`** (obrigatório): caminho **relativo ao cwd** onde salvar o PNG. **Deve ficar dentro do cwd do projeto** — o sandbox do bridge só monta cwd; caminhos fora falham. Use ex.: `assets/hero.png`, `marketing/imagens/capa-v2.png`.
- **`input_images`** (opcional): array de caminhos das imagens de origem — **omitir** pra gerar do zero; **preencher** pra editar.
- **`cwd`** (opcional): cwd do projeto se o host não estiver já nele.

A tool executa generate-then-move internamente e retorna **apenas o caminho final salvo**. Não espere bytes de imagem na resposta.

**Não** troque de modelo silenciosamente (gpt-image-2 → gpt-image-1.5). Se algo forçar downgrade, pergunte antes.

### 4. Revisar e iterar (1 mudança por vez)
Inspecione: sujeito, estilo, composição, **precisão do texto**, itens a evitar. Ajuste com **uma** mudança alvo e re-cheque — não empilhe 5 mudanças num prompt.

### 5. Reportar
Sempre informe: **caminho final salvo no projeto** (`out_path` retornado), o **prompt final** (`description`), e que foi via **cursor-mcp-bridge → Codex built-in** (keyless). Lote = uma chamada por asset.

## Nunca

- Usar `out_path` fora do cwd do projeto.
- Sobrescrever o original na edição (sempre cópia nova).
- Afirmar que ficou perfeito — descreva o que foi pedido e ofereça 1 ajuste.
- Gerar imagem de pessoa real/depoimento sem material autorizado.
- Editar rosto/pessoa de forma enganosa; usar imagem de terceiro sem autorização (direito de imagem / LGPD).
- Publicar/entregar como final sem quem decide aprovar (quando houver esse fluxo no projeto).
