# keyless-image

Motor de imagem **keyless** do keyless-studio. Gera e edita imagem dentro do Claude Code via **polyagent-mcp** (tool `generate_image`) → `codex exec` + `image_gen` / gpt-image-2 — usando sua assinatura ChatGPT/Codex, **sem API key**.

## Skills

- **`keyless-image:generate`** — cria imagem nova (foto, ilustração, mockup, capa, slide-imagem).
- **`keyless-image:edit`** — altera imagem existente (fundo, objeto, cor/estilo, logo/texto, variação por referência).

## Requisito

1. Servidor MCP **`polyagent`** configurado globalmente no Claude Code, usando o projeto **[polyagent-mcp](https://github.com/JaimeJunr/polyagent-mcp)**.
2. **Codex CLI** instalado e logado (`codex` no PATH) — o bridge chama `codex exec`.

Instalar o plugin **não instala nem registra o MCP**. Configure o servidor MCP `polyagent` globalmente uma vez, fora deste repo. No terminal, escolha uma pasta permanente para o clone e execute:

```sh
git clone https://github.com/JaimeJunr/polyagent-mcp.git
cd polyagent-mcp
npm install
npm run build
claude mcp add --scope user --transport stdio polyagent -- node "$(pwd)/dist/index.js"
```

O comando registra o servidor na configuração MCP do Claude Code no escopo `user`, disponível em todos os projetos. Mantenha o clone nesse caminho. Reinicie o Claude Code e confira o servidor `polyagent` em `/mcp`; a tool de imagem resolve como `mcp__polyagent__generate_image`. O Codex CLI deve estar instalado e logado para a geração keyless.

Sem o bridge/Codex, as skills degradam pro fluxo copia-e-cola (prompt pronto pro chatgpt.com/images).

## Princípios

- **Keyless primeiro** (built-in do Codex via bridge, sem chave).
- **generate-then-move** — a tool salva direto no `out_path` do projeto (cwd).
- **Texto na imagem** com marcador `EXACT TEXT: "..."`; rótulo curto sai ótimo, parágrafo longo melhor sobrepor depois.
- **Iterar 1 mudança por vez.**

É a base dos outros plugins (`keyless-deck`, `keyless-social`, etc.) — instale primeiro.
