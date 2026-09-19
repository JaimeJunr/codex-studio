# Changelog

## Unreleased — rename `codex-*` → `keyless-*`

**BREAKING.** O marketplace e os 11 plugins deixam de se chamar `codex-*`. Os ids antigos **não existem mais** — não há alias de compatibilidade no marketplace, nas invocações `<plugin>:<skill>` nem nos slash commands.

O projeto passa a se chamar **keyless-studio**.

| Antes | Depois |
|---|---|
| `codex-studio` | `keyless-studio` |
| `codex-image` | `keyless-image` |
| `codex-deck` | `keyless-deck` |
| `codex-social` | `keyless-social` |
| `codex-infographic` | `keyless-infographic` |
| `codex-biz` | `keyless-biz` |
| `codex-study` | `keyless-study` |
| `codex-web` | `keyless-web` |
| `codex-sprite` | `keyless-sprite` |
| `codex-pixel` | `keyless-pixel` |
| `codex-cartoon` | `keyless-cartoon` |
| `codex-realistic` | `keyless-realistic` |

### Quem já tinha os plugins instalados

Reinstale com os nomes novos. O Claude Code não mapeia `codex-image@codex-studio` para `keyless-image@keyless-studio`.

```
/plugin uninstall codex-image@codex-studio
# …e os demais `codex-*` que estiver usando
/plugin marketplace add JaimeJunr/keyless-studio
/plugin install keyless-image@keyless-studio
# …e os demais `keyless-*`
```

Invocações e slash commands mudam no mesmo padrão: `codex-image:generate` → `keyless-image:generate`, `/codex-sprite:setup` → `/keyless-sprite:setup`.

### O que NÃO muda

- O enum `engine: "codex"` da tool `generate_image` (polyagent-mcp). Continua `z.enum(["codex","grok"])`.
- Codex CLI, `codex exec`, `~/.codex`, `~/.codex/auth.json` — produto e filesystem da OpenAI.
- `gpt-image-2`, `image_gen`, `polyagent`, `polyagent-mcp`.

### Config do Aseprite (`spritekit.py`)

`APP_NAME` passou a `keyless-sprite`. Config nova vai para `~/.config/keyless-sprite/` (ou o equivalente no macOS/Windows). Quem já rodou `/codex-sprite:setup` **não precisa refazer**: `LEGACY_APP_NAMES` ainda lista `codex-sprite`, e a migração copia o `config.json` antigo para o diretório novo na primeira execução.
