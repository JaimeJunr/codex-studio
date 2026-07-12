---
name: deck
description: Cria um deck/PowerPoint a partir de artigo, notas, outline ou ideia — gera cada slide como imagem full-bleed on-brand via Codex e monta um .pptx. Use pra apresentação, relatório, documento visual, aula, deck de trabalho. Fluxo estágio-a-estágio (outline → estilo → amostra → gera tudo). Depende do codex-image e de python-pptx.
---

# codex-deck:deck — deck/PPT como slides-imagem

Transforma conteúdo em um `.pptx` onde **cada slide é uma imagem inteira** gerada via Codex (keyless). Genérico: trabalho, relatório, documento, aula. Especializações (pitch, vendas, aula acadêmica) vêm dos plugins `codex-biz`/`codex-study`, que reutilizam esta skill.

## Pré-requisitos

- Skill `codex-image` (motor keyless via Codex). Sem Codex → gera os **prompts** dos slides pro usuário rodar no chatgpt.com/images e depois montar; não trava.
- `python-pptx` pra montar o arquivo: `pip install python-pptx`.

## Fluxo estágio-a-estágio (não gere tudo de cara)

Gerar 15 slides antes de alinhar estilo = retrabalho caro. Confirme em etapas:

### 1. Outline
A partir do material (artigo/notas/PDF/ideia), proponha `outline.md`: título, nº de slides, e por slide um título + 2-4 bullets. **Confirme com o usuário** antes de seguir.

### 2. Estilo
Ofereça um estilo da biblioteca (`references/estilos.md`) ou o guia de marca do projeto (`DESIGN.md`/`identidade/`). Traduza pra paleta (HEX→cores reais) + tipografia + tom visual. Se o usuário tem imagem/PPT de referência, analise e replique o estilo.

### 3. Amostra (1 slide) — trava de qualidade
Gere **só 1 slide** (ex: a capa) via `codex-image:generate`, no aspect ratio do deck (16:9 padrão; 9:16 pra mobile). Mostre. Só avance quando o usuário aprovar estilo + legibilidade do texto.

### 4. Gerar todos os slides
Uma chamada de imagem **por slide** (`slide_01.png`, `slide_02.png`, …) salvos em `<projeto>/origin_image/`. Regras:
- **generate-then-move**: mover cada PNG do cache do Codex pra `origin_image/`.
- **Texto**: use `EXACT TEXT: "..."` pros títulos/bullets curtos. Texto de parágrafo longo tende a tremular — prefira bullets curtos por slide.
- **Consistência**: repita o bloco de estilo em todo prompt; mantenha grid/margens/tipografia entre slides.
- Se um slide precisa de imagem real do usuário (gráfico, foto, print), insira essa imagem em vez de gerar.

### 5. Fala (opcional)
Gere `speech.md` com marcadores `## Slide N` — vira as **notas** de cada slide no PPTX.

### 6. Montar o .pptx
Rode o script empacotado:
```
python "${CLAUDE_PLUGIN_ROOT}/scripts/build_pptx.py" <projeto> --size 16:9
```
Ele lê `origin_image/*.png` (ordem natural) + `speech.md` e gera `<projeto>/<nome>.pptx`.

## Estrutura de saída (por deck)

```
<base>/<nome-do-deck>/
├── outline.md          # outline confirmado
├── origin_image/       # slide_01.png, slide_02.png, ... (só os finais)
├── speech.md           # notas por slide (opcional)
└── <nome-do-deck>.pptx # arquivo final montado
```

## Biblioteca de estilos

Estilos prontos em `references/estilos.md` (limpo-profissional, e-ink, McKinsey, quadro-branco desenhado, etc.). Ao acertar um estilo novo, salve ali pra reusar — a biblioteca cresce com o uso.

## Nunca

- Gerar todos os slides antes de aprovar a amostra (estágio 3).
- Deixar PNG só no cache do Codex (sempre mover pra `origin_image/`).
- Inventar dado/número — se veio do material, cite; se não, `[PENDENTE]`.
- Afirmar que o deck está pronto pra apresentar sem o usuário revisar legibilidade e conteúdo.
