---
name: edit
description: Edita uma imagem existente via polyagent-mcp → Codex (gpt-image-2), sem API key — trocar fundo, remover/adicionar objeto, mudar cor/estilo, inserir logo/texto, gerar variação a partir de referência. Use quando já existe uma imagem e o usuário quer ALTERÁ-la. Para criar do zero, use a skill generate.
---

# keyless-image:edit — editar imagem keyless via polyagent-mcp → Codex

Transforma uma imagem existente via a tool **`generate_image`** do MCP `polyagent`. **Sem API key.**

## Pré-requisito

Servidor MCP `polyagent` configurado globalmente no Claude Code e disponível, com Codex CLI logado. Se **não** estiver: monte o **prompt de edição** e diga "cole no chatgpt.com/images **junto com a imagem original**". Não trave.

## Fluxo

### 1. Entender o ponto de partida
Peça o caminho da imagem original (e referências, se houver: logo, foto de produto). O modelo precisa do arquivo de origem.

### 2. Prompt de edição — Keep / Change / Do not
Ordem que preserva o que importa:
```
Edit this image. Keep: <o que preservar — sujeito, enquadramento, identidade do produto, texto>.
Change: <a alteração única e específica>.
Style: <paleta em cores reais, iluminação, mood on-brand>.
Do not: <itens do "o que NÃO fazer" do guia de estilo>.
```
- **Uma alteração por vez.** Trocar fundo + remover objeto + mudar cor num prompt só sai impreciso — encadeie: edita, salva, edita de novo.
- Preserve invariantes agressivamente (rosto/texto/marca não mudam salvo se pedido).

### 3. Editar via `generate_image` ⚠️
Chame a tool **`generate_image`** com:
- **`input_images`**: array com os caminhos das imagens de origem.
- **`description`**: o prompt Keep/Change (§2).
- **`out_path`**: um **arquivo novo** (não sobrescreva o original) relativo ao cwd do projeto — versione (`-v2`, `-v3`). A tool salva **direto** nesse caminho e retorna só o path final.

### 4. Iterar
Se desviou do que devia ficar, **reforce o "Keep:"** e tente de novo, uma mudança por vez.

### 5. Reportar
Caminho final no projeto + prompt usado + provedor (polyagent-mcp → Codex built-in). Não afirme perfeição; ofereça 1 ajuste.

## Nunca

- Alteração destrutiva no original (sempre salve cópia nova).
- Usar `out_path` fora do cwd do projeto.
- Editar rosto/pessoa de forma enganosa; usar imagem de terceiro sem autorização (direito de imagem / LGPD).
