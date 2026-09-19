---
name: study-deck
description: Monta materiais de estudo visuais — deck de aula, resumo visual de um tema, flashcards em imagem, e deck de defesa/apresentação acadêmica. Fornece a estrutura pedagógica; delega geração/montagem ao keyless-deck/keyless-image. Use pra transformar matéria, artigo ou notas em material de estudo.
---

# keyless-study:study-deck — materiais de estudo

Especialização de estudo sobre o `keyless-deck`. Transforma matéria/artigo/notas em material que ensina, não só que "mostra".

## Requisito
`keyless-deck` + `keyless-image`. Sem eles, entregue a estrutura pro usuário montar.

## Templates

**Deck de aula** — abertura com objetivo de aprendizagem → 1 conceito por slide → exemplo concreto → checagem ("responda pra você") → resumo final. Ritmo: não mais de 1 ideia nova por slide.

**Resumo visual** (1 tema em N slides) — mapa do tema → pilares → cada pilar 1 slide com a essência → conexões → "o que levar". Bom pra revisão.

**Flashcards em imagem** — pares pergunta/resposta como imagens (frente 1 slide, verso o próximo), ou um card com pergunta destacada e resposta escondida embaixo. Texto curto, `EXACT TEXT`.

**Defesa / apresentação acadêmica** — 1 Capa (título, autor, orientador) · 2 Problema/pergunta de pesquisa · 3 Objetivos · 4 Método · 5-7 Resultados (inserir figuras reais do trabalho!) · 8 Discussão · 9 Conclusão · 10 Referências-chave. Estilo `científico`/`limpo-profissional`.

## Fluxo

1. Formato + material de origem (PDF, notas, artigo). Para defesa, peça as **figuras reais** (gráficos/tabelas do trabalho) — insira-as em vez de gerar.
2. Estruture pedagogicamente (objetivo → conteúdo → checagem). Fidelidade ao conteúdo acima de estética.
3. Passe pro `keyless-deck:deck`. Estilo sugerido: `quadro-branco-desenhado` (didático) ou `e-ink-revista`/`limpo-profissional` (acadêmico).

## Nunca
- Distorcer o conteúdo da matéria por causa do visual.
- Gerar figura científica "parecida" — figura de resultado é a real do trabalho, sempre.
- Inventar citação/referência.
