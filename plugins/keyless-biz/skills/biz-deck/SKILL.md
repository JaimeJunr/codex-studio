---
name: biz-deck
description: Monta decks de negócio prontos — pitch deck, deck de vendas, proposta comercial, QBR/relatório executivo. Fornece a sequência de slides e o ângulo de cada um; delega a geração/montagem ao keyless-deck. Use quando o usuário quer um desses formatos específicos de negócio.
---

# keyless-biz:biz-deck — decks de negócio

Especialização de negócio sobre o `keyless-deck`. Aqui mora o **quê vai em cada slide** dos formatos clássicos; a geração de imagem e a montagem do `.pptx` são do `keyless-deck`/`keyless-image`.

## Requisito
`keyless-deck` + `keyless-image` instalados. Sem eles, entregue o outline dos slides pro usuário montar noutro lugar.

## Templates (sequência de slides sugerida)

**Pitch deck (investidor)** — 10-12 slides: 1 Capa/one-liner · 2 Problema · 3 Solução · 4 Por que agora · 5 Produto (demo) · 6 Mercado (TAM/SAM/SOM) · 7 Modelo de negócio · 8 Tração · 9 Concorrência/diferencial · 10 Time · 11 Projeções · 12 Ask + uso do recurso.

**Deck de vendas (prospect)** — 8-10 slides: 1 Capa · 2 A dor do cliente (espelho) · 3 Custo de não resolver · 4 Sua solução (resultado, não features) · 5 Como funciona (3 passos) · 6 Prova (case/depoimento/número) · 7 Oferta/pacotes · 8 Objeções comuns · 9 Próximo passo/CTA.

**Proposta comercial** — 7-9 slides: 1 Capa (cliente + data) · 2 O que entendemos do seu negócio · 3 Diagnóstico (top problemas c/ evidência) · 4 O que propomos (escopo) · 5 O que muda pra você (resultado) · 6 Investimento (à vista + parcelado) · 7 Cronograma · 8 Garantias · 9 Próximos passos.

**QBR / relatório executivo** — 6-8 slides: 1 Capa (período) · 2 Resumo executivo (3 bullets) · 3 Métricas-chave vs meta · 4 O que funcionou · 5 O que não funcionou · 6 Aprendizados · 7 Plano do próximo ciclo · 8 Pedidos/decisões.

## Fluxo

1. Pergunte o formato e colete o material (dados, contexto do cliente/empresa).
2. Adapte o template ao caso — **corte slide que não tem conteúdo real** (não encha por encher).
3. Passe o `outline.md` resultante pro `keyless-deck:deck` (estágio-a-estágio: outline → estilo → amostra → gera → `.pptx`).
4. Estilo padrão de negócio: `limpo-profissional` ou `mckinsey` (ver `references/estilos.md` do keyless-deck); título de ação no topo em QBR/proposta.

## Nunca
- Inventar tração, número ou depoimento — só o que o usuário forneceu; senão `[PENDENTE]`.
- Prometer resultado que o material não sustenta.
- Slide vazio "de enfeite".
