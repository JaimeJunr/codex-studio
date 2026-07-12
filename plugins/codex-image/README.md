# codex-image

Motor de imagem **keyless** do codex-studio. Gera e edita imagem dentro do Claude Code via o MCP do **Codex** (`image_gen` / gpt-image-2) — usando sua assinatura ChatGPT/Codex, **sem API key**.

## Skills

- **`codex-image:generate`** — cria imagem nova (foto, ilustração, mockup, capa, slide-imagem).
- **`codex-image:edit`** — altera imagem existente (fundo, objeto, cor/estilo, logo/texto, variação por referência).

## Requisito

Codex CLI instalado e logado (`codex` no PATH). O plugin declara o MCP `codex` em `.mcp.json`. Sem o Codex, as skills degradam pro fluxo copia-e-cola (prompt pronto pro chatgpt.com/images).

## Princípios

- **Keyless primeiro** (built-in do Codex, sem chave).
- **generate-then-move** — asset do projeto nunca fica só em `~/.codex/generated_images/`.
- **Texto na imagem** com marcador `EXACT TEXT: "..."`; rótulo curto sai ótimo, parágrafo longo melhor sobrepor depois.
- **Iterar 1 mudança por vez.**

É a base dos outros plugins (`codex-deck`, `codex-social`, etc.) — instale primeiro.
