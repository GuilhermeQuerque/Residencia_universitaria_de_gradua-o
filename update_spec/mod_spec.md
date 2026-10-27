# mod_spec.md — Log de modificações de larga escala nos specs

> Registro **centralizado** de mudanças grandes feitas nos specs do projeto.
> Existe para que os arquivos de spec continuem limpos (só o conteúdo atual) e para que o histórico do *porquê* fique em um lugar só, consultável.
>
> **Última atualização:** 23/10/2026

---

## 1. O que precisa ser registrado aqui

**Só mudança de larga escala.** Exemplos do que conta:

- remover ou reescrever uma seção inteira;
- reestruturar o documento (mover conteúdo entre arquivos, renumerar seções);
- alterar a arquitetura, o modelo de dados, as rotas ou uma regra que valha para o site inteiro;
- inverter uma decisão anterior (trocar "proibido" por "permitido", por exemplo).

**O que NÃO precisa ser registrado aqui:**

- ajuste de texto, correção de typo, acerto de link quebrado;
- acrescentar um item pequeno a uma seção existente;
- mudança de status/próximo passo no roadmap — isso já é campo próprio em `andamento.spec.md`;
- qualquer alteração de código (o histórico disso é o git).

> Na dúvida: **a seção inteira mudou? entra aqui.** Uma linha a mais numa tabela que já existe? Não entra.

## 2. Formato da entrada

Cada linha é uma modificação, com:

| Campo | O que é |
|---|---|
| **Data** | `DD/MM/AAAA` |
| **Nome da modificação** | rótulo curto e simples (2–4 palavras), em pt-br |
| **Motivo** | resumido, cobrindo a **ideia antiga**, o **defeito** e a **ideia nova** |
| **Local** | arquivo + seção **e** intervalo de linhas (`linha X até linha Y`) |
| **Arquivo** | nome do arquivo `.md` alterado |

Exemplo do formato:

```
| 23/10/2026 | Regra de JS ampliada | Ant.: JS proibido fora do PIX. Defeito: travava casos que o nativo não resolvia. Novo: JS permitido, mínimo possível. | contexto.md §6, linhas 56–56 | contexto.md |
```

**Ao escrever a entrada:** pegue os números de linha **depois** de editar o arquivo, senão o intervalo aponta para o lugar errado.

## 3. Registro atual

### 23/10/2026 — Separação entre contexto geral e spec por página

| | |
|---|---|
| **Motivo** | *Ant.:* tudo num spec só — `noticias.spec.md` carregava stack, RBAC, rotas gerais e o roadmap junto com o layout da Página 1. *Defeito:* o spec de uma página ficava poluído com o geral do site, e a visão de módulos (que muda sempre) ficava presa num arquivo de módulo. *Novo:* `contexto.md` (geral, lido 1x), `noticias.spec.md` só com a Página 1, e `update_spec/` com o roadmap e as regras. |
| **Local** | `noticias.spec.md` reescrito por inteiro (linhas 1–261): seções de contexto geral removidas e conteúdo realocado; criação de `contexto.md` (1–126); criação de `update_spec/andamento.spec.md` (1–75), `update_spec/regras_atualizacao.md` (1–121), `update_spec/README.md` (1–18); `AGENTS.md` reescrito como índice (1–40) |
| **Arquivos** | `noticias.spec.md`, `contexto.md`, `AGENTS.md`, `update_spec/*` |

### 23/10/2026 — Regra de JS ampliada

| | |
|---|---|
| **Motivo** | *Ant.:* "JS permitido apenas para o widget do PIX; todo o resto é HTML/CSS puro". *Defeito:* a regra era categórica e obrigava gambiarras CSS (truque do checkbox) para casos com boa solução nativa em JS simples. *Novo:* JS permitido, mas no mínimo possível — usa o nativo (`<details>`, `<dialog>`, `:checked`) antes de JS; o JS só *melhora*, nunca é o que faz a página funcionar. |
| **Local** | `contexto.md` §6, item 3 (linha 56); `noticias.spec.md` §9 "Menu lateral sem JavaScript" → "Menu lateral (JS mínimo)" (linhas 162–187); `noticias.spec.md` §12 critério de aceite do menu (linha 214); `AGENTS.md` §Regras de ouro (linha 36); `update_spec/andamento.spec.md` §4, item do menu lateral (linha 68) |
| **Arquivos** | `contexto.md`, `noticias.spec.md`, `AGENTS.md`, `update_spec/andamento.spec.md` |