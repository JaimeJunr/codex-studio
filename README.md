# codex-studio

**Superpoder visual keyless para o Claude Code, via Codex.**

O Claude Code não gera pixel. O `codex-studio` resolve isso ligando o Claude Code ao **Codex** (`image_gen` / gpt-image-2) — que gera e edita imagem usando a **sua assinatura ChatGPT/Codex, sem API key**. Em cima disso, entrega skills para **decks/PowerPoint, criativos sociais, infográficos e visuais de site** — genéricos o suficiente pra qualquer coisa (trabalho, documento, aula, site) e com pacotes especialistas quando você quer resultado pronto de um domínio.

## Por que

- **Sem API key.** Imagem via Codex usa a auth que você já tem (ChatGPT free incluído). Sem `OPENAI_API_KEY`, sem chave de terceiro pra gerenciar.
- **Local e seu.** Decks viram `.pptx` de verdade montado localmente (python-pptx). Imagens ficam no seu projeto.
- **Genérico + especialista.** Os plugins-base servem pra tudo; os especialistas (negócio, estudo, web) dão templates curados por cima.
- **Degrada com elegância.** Sem Codex, cai pro fluxo copia-e-cola (prompt pronto pro chatgpt.com/images) ou outro provedor — nunca trava.

## Pré-requisitos

- **Claude Code** (com suporte a plugins/marketplace).
- **Codex CLI** instalado e logado (`codex` no PATH) — é o motor de imagem keyless.
- **Python 3** + `python-pptx` (só pro `codex-deck` montar `.pptx`): `pip install python-pptx`.

## Instalação

```
/plugin marketplace add JaimeJunr/codex-studio
/plugin install codex-image@codex-studio      # motor (instale primeiro)
/plugin install codex-deck@codex-studio        # decks/PPT
/plugin install codex-social@codex-studio      # criativos sociais
/plugin install codex-infographic@codex-studio
/plugin install codex-biz@codex-studio         # especialista: negócio
/plugin install codex-study@codex-studio       # especialista: estudo
/plugin install codex-web@codex-studio         # especialista: site
```

Um comando por linha (o Claude Code interpreta slash line-by-line).

## Plugins

| Plugin | Camada | O que faz |
|---|---|---|
| **codex-image** | motor | Gera/edita imagem via Codex (keyless). `generate-then-move`, texto PT-BR na imagem. Base dos demais. |
| **codex-deck** | genérico | Deck genérico → slides-imagem → `.pptx`. Trabalho, documento, relatório, aula. |
| **codex-social** | genérico | Capa de carrossel, story/reel, quote card, criativo de anúncio. |
| **codex-infographic** | genérico | Número/dado → slide infográfico. |
| **codex-biz** | especialista | Pitch, deck de vendas, proposta, QBR (templates sobre o `codex-deck`). |
| **codex-study** | especialista | Aula, resumo, flashcard, defesa acadêmica. |
| **codex-web** | especialista | Hero, OG card, ilustração de seção, favicon pra sites. |

## Como funciona (arquitetura)

```
Claude Code
   │  usa skill (ex: codex-deck:deck)
   ▼
codex-image  ──(MCP)──►  Codex CLI  ──►  image_gen (gpt-image-2, keyless)
   │                                         │ salva em ~/.codex/generated_images/
   │  generate-then-move                     ▼
   └────────────────────────────────►  seu projeto (marketing/, decks/, ...)
```

Princípios herdados do `image_gen` oficial do Codex e da comunidade: **built-in tool primeiro** (sem chave), **generate-then-move** (nunca deixar asset só no cache do Codex), **fluxo estágio-a-estágio** (confirma outline/estilo/amostra antes de gerar tudo), e **biblioteca de estilos** versionada em cada plugin (`references/`).

## Créditos e inspiração

- Codex `image_gen` / [imagegen SKILL oficial](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/imagegen/SKILL.md)
- [codex-ppt-skill](https://github.com/ningzimu/codex-ppt-skill) (fluxo de PPT como imagens-slide)
- [Claude Code Plugins reference](https://code.claude.com/docs/en/plugins-reference)

## Licença

MIT — veja [LICENSE](LICENSE).
