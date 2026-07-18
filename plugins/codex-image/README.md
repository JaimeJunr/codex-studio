# codex-image

Motor de imagem **keyless** do codex-studio. Gera e edita imagem dentro do Claude Code via **cursor-mcp-bridge** (tool `generate_image`) → `codex exec` + `image_gen` / gpt-image-2 — usando sua assinatura ChatGPT/Codex, **sem API key**.

## Skills

- **`codex-image:generate`** — cria imagem nova (foto, ilustração, mockup, capa, slide-imagem).
- **`codex-image:edit`** — altera imagem existente (fundo, objeto, cor/estilo, logo/texto, variação por referência).

## Requisito

1. **cursor-mcp-bridge** clonado e buildado (`npm run build`); exporte `CURSOR_MCP_BRIDGE_DIST=/caminho/para/cursor-mcp-bridge/dist/index.js`.
2. **Codex CLI** instalado e logado (`codex` no PATH) — o bridge chama `codex exec`.

O plugin declara o MCP `cursor-bridge` em `.mcp.json`. Sem o bridge/Codex, as skills degradam pro fluxo copia-e-cola (prompt pronto pro chatgpt.com/images).

## Princípios

- **Keyless primeiro** (built-in do Codex via bridge, sem chave).
- **generate-then-move** — a tool salva direto no `out_path` do projeto (cwd).
- **Texto na imagem** com marcador `EXACT TEXT: "..."`; rótulo curto sai ótimo, parágrafo longo melhor sobrepor depois.
- **Iterar 1 mudança por vez.**

É a base dos outros plugins (`codex-deck`, `codex-social`, etc.) — instale primeiro.
