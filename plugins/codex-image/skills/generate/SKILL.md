---
name: generate
description: Gera imagem (bitmap) dentro do Claude Code via Codex (gpt-image-2), sem API key. Use quando o usuário quer CRIAR uma imagem nova — foto, ilustração, mockup, capa, textura, slide-imagem. Salva no projeto (generate-then-move). Para EDITAR imagem existente, use a skill edit. Para vetor/HTML/CSS, não use esta skill.
---

# codex-image:generate — gerar imagem keyless via Codex

Cria imagem bitmap via o MCP `codex` (`image_gen` / gpt-image-2). **Sem API key** — usa a assinatura ChatGPT/Codex do usuário.

## Quando usar / não usar

- **Use** pra criar imagem nova: foto, ilustração, mockup, capa, textura, sprite, slide-imagem, cutout.
- **Não use** pra: editar SVG/vetor/ícone existente, montar UI em HTML/CSS/canvas, ou estender um sistema de logo — isso é código-nativo, não bitmap.

## Pré-requisito

MCP `codex` disponível (Codex CLI instalado + logado). Se **não** estiver:
- Não trave. Gere o **prompt pronto** e diga: "cole no chatgpt.com/images". Informe que instalar/logar o Codex CLI destrava a geração automática.

## Fluxo

### 1. Contexto de marca (se houver)
Se o projeto tem um guia de estilo (`identidade/design-guide.md`, `DESIGN.md`, ou `references/`), leia: paleta (HEX), estilo de imagem, "o que NÃO fazer". Sem guia, gere neutro e diga que ficou genérico.

### 2. Montar o prompt (estrutura de 5 partes)
Ordem: **sujeito+ação → cenário/ambiente → iluminação → paleta (cores reais, HEX→"warm terracotta") + estilo → composição/enquadramento**. Prosa natural, sem flags.

**Texto dentro da imagem:**
- Literal com marcador: `EXACT TEXT: "Movimento é liberdade"` (aspas duplas).
- Rótulo curto sai quase perfeito; **parágrafo longo tremula** — pra texto longo, gere sem o texto e sobreponha depois (HTML/CSS ou editor).
- Nome de marca difícil: soletre letra a letra.

Mostre o prompt ao usuário **antes** de gerar (pré-aprovação), salvo quando for só preview/brainstorm.

### 3. Gerar via Codex + generate-then-move ⚠️
Chame o MCP `codex` pedindo pra gerar a imagem **e mover o PNG** pro destino do projeto.

**Regra de ouro (generate-then-move):** o Codex salva por padrão em `~/.codex/generated_images/...` (ou `$CODEX_HOME/...`). **Nunca** deixe um asset do projeto só lá:
- Se o usuário deu um destino → mova/copie pra lá.
- Se é asset do projeto → mova pro workspace (ex: `assets/`, `marketing/imagens/`, `out/`).
- Se é só preview/brainstorm → pode deixar no caminho padrão e mostrar inline.

**Não** troque de modelo silenciosamente (gpt-image-2 → gpt-image-1.5). Se algo forçar downgrade, pergunte antes.

### 4. Revisar e iterar (1 mudança por vez)
Inspecione: sujeito, estilo, composição, **precisão do texto**, itens a evitar. Ajuste com **uma** mudança alvo e re-cheque — não empilhe 5 mudanças num prompt.

### 5. Reportar
Sempre informe: **caminho final salvo no projeto**, o **prompt final**, e que foi via **built-in do Codex** (keyless). Lote = uma chamada por asset.

## Nunca

- Deixar asset do projeto só em `~/.codex/generated_images/...`.
- Afirmar que ficou perfeito — descreva o que foi pedido e ofereça 1 ajuste.
- Gerar imagem de pessoa real/depoimento sem material autorizado.
- Publicar/entregar como final sem quem decide aprovar (quando houver esse fluxo no projeto).
