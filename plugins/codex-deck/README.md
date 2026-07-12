# codex-deck

Motor de **deck/PowerPoint** do codex-studio. Transforma artigo, notas, outline ou ideia em um `.pptx` onde **cada slide é uma imagem full-bleed** gerada via Codex (keyless), montado localmente com `python-pptx`.

Genérico de propósito: apresentação de trabalho, relatório, documento visual, aula. As especializações (pitch, vendas, proposta, aula acadêmica) ficam em `codex-biz` e `codex-study`, que reutilizam esta skill.

## Skill

- **`codex-deck:deck`** — fluxo estágio-a-estágio: outline → estilo → amostra (1 slide) → gera todos → monta `.pptx`.

## Requisitos

- `codex-image` instalado (motor keyless via Codex).
- `pip install python-pptx` (pra montar o arquivo).

## Montagem

```
python "${CLAUDE_PLUGIN_ROOT}/scripts/build_pptx.py" <projeto> --size 16:9
```
Lê `<projeto>/origin_image/slide_*.png` (+ `speech.md` opcional pras notas) e gera `<projeto>/<nome>.pptx`. Tamanhos: `16:9`, `4:3`, `9:16`.

## Estilos

Biblioteca em [`references/estilos.md`](references/estilos.md) — limpo-profissional, McKinsey, e-ink, quadro-branco, dashboard, e mais. Adicione os seus.
