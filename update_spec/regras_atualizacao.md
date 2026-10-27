# regras_atualizacao.md — Regras de atualização dos specs do projeto

> Regras que valem para **todos** os documentos de spec do repositório.
> Objetivo: que um agente (ou o programador) saiba **quando** e **como** atualizar cada documento, sem deixar informação duplicada e defasada em dois lugares.
> **Última atualização:** 27/10/2026

---

## 1. Tipos de documento

| Tipo | Onde vive | Exemplo | Cadência |
|---|---|---|---|
| **Contexto geral** (read-once) | na raiz | `contexto.md` | Raramente — só quando muda stack, regra global, RBAC, rotas gerais ou ambiente |
| **Spec de página/módulo** (estável) | `specs/` | `specs/noticias.spec.md` | Muda quando o escopo/regra **daquela página** muda |
| **Spec de organização** (estável) | na raiz | `organizacao.spec.md` | Muda quando a organização de diretórios/arquivos muda |
| **Spec vivo** (mutável) | `update_spec/` | `update_spec/andamento.spec.md` | Muda a **cada** avanço do projeto |

**Um spec por página:** cada página/módulo do site tem seu próprio arquivo de spec em `specs/`, seguindo o padrão de `specs/noticias.spec.md` (ex.: `specs/impressora.spec.md`, `specs/album.spec.md`, `specs/lojinha.spec.md`). Nenhuma página precisa das regras gerais — elas estão em `contexto.md`. A **organização de diretórios e arquivos** é transversal e tem spec próprio na raiz: `organizacao.spec.md`.

**Regra de ouro:** a **visão de módulos, prioridades, status e rotas previstas** vive **apenas** em `update_spec/andamento.spec.md`. Nenhum outro documento pode copiar essa tabela. Se outro doc precisar falar de um módulo, ele **linka** para o `andamento.spec.md` em vez de repetir a informação.

## 2. Gatilhos — o que obriga a atualizar

### 2.1 `update_spec/andamento.spec.md` (obrigatório)

Atualize **sempre** que ocorrer um destes eventos:

- um módulo novo entrar no escopo do site;
- um módulo mudar de status (`planejado` → `em andamento` → `concluído` → `adiado`);
- uma versão (`v1`, `v2`, `v3`) ser repriorizada;
- uma rota prevista mudar de nome, sumir ou aparecer;
- um item transversal da seção 4 for entregue, bloqueado ou descartado;
- o próximo passo de um módulo mudar.

Nesses casos, atualize a tabela/seção correspondente. Status e próximos passos **não** entram no `mod_spec.md` — o campo de status já é o registro.

### 2.2 Spec de página/módulo (ex.: `specs/noticias.spec.md`)

Atualize quando a **página** muda:

- entra/sai uma regra funcional ou técnica **daquela página**;
- muda o modelo de dados, as rotas ou o layout **daquela página**;
- um conflito entre documentos é resolvido;
- uma decisão pendente **dessa página** é fechada.

### 2.3 `contexto.md`

Atualize quando muda algo que vale para **o site inteiro**:

- stack, banco de dados, infraestrutura, idioma;
- requisitos não-funcionais, design/identidade visual;
- atores, permissões (RBAC) ou regras técnicas globais;
- estrutura de apps, rotas gerais, ambiente/comandos, gotchas.

`contexto.md` é o **único** lugar para essas informações gerais — nenhum spec de página deve repetir stack, RBAC ou regras globais.

### 2.4 `AGENTS.md`

Atualize quando muda a **ordem de leitura** ou o índice de documentos:

- qual documento a IA deve ler primeiro (hoje: `contexto.md`);
- quais documentos existem e o que é arquivado;
- um comando rápido que mude.

O `AGENTS.md` é um **índice curto** — não guarda contexto, histórico nem detalhes de implementação (esses ficam em `contexto.md` e nos specs).

## 3. Formato padrão

- **Idioma:** pt-br em todo o conteúdo, inclusive títulos, tabelas e mensagens de log.
- **Data:** `DD/MM/AAAA`.
- **Tabelas:** Markdown, com uma coluna de status/versão quando o tema pedir.
- **Status possíveis (módulo):** `planejado` · `em andamento` · `concluído` · `adiado`.
- **Prioridade/versão:** `v1`, `v2`, `v3` — indica a ordem de implementação, não a versão do documento.
- **Log de mudanças:** mudança de larga escala vai para `update_spec/mod_spec.md` (formato em §2). Não leve tabela de histórico para dentro do spec.
- **Links internos:** referencie seções pelo número (`§9.4`) e arquivos pelo caminho relativo a partir da raiz do projeto.
- **Nada de "futuro distante" nos specs de módulo:** descreva o que o módulo faz agora; o que está por vir fica no `andamento.spec.md`.

## 4. Checklist de atualização

Ao mexer em qualquer spec, confirme:

- [ ] O conteúdo alterado **não** está duplicado em outro documento (se estiver, remova a duplicata e deixe o link).
- [ ] O status/versão/rota correspondente no `andamento.spec.md` foi atualizado no mesmo momento.
- [ ] Se a mudança foi de **larga escala**, a entrada foi acrescentada em `update_spec/mod_spec.md` (com intervalo de linhas).
- [ ] Se a mudança foi pequena, **nada** foi adicionado ao `mod_spec.md`.
- [ ] Datas no formato `DD/MM/AAAA`.
- [ ] "Última atualização" no topo do documento está com a data de hoje.
- [ ] As referências cruzadas (`§`, caminhos de arquivo) continuam apontando para o lugar certo.
- [ ] Se a mudança afeta as regras **globais** (stack, libs, JS, banco, permissão, rotas gerais, ambiente), o `contexto.md` foi conferido.
- [ ] Se a mudança afeta **onde um agente começa a ler**, o `AGENTS.md` foi conferido.

## 5. Fluxo de trabalho

1. **O rumo muda** (decisão do programador) → o módulo correspondente tem spec próprio, ou nasce um novo.
2. **O agente implementa** conforme o spec do módulo.
3. **Ao entregar** (ou ao descartar uma ideia), o agente atualiza `update_spec/andamento.spec.md` — status, próximo passo e registro de alterações.
4. **O programador revisa** o spec do módulo quando o escopo muda de verdade (não a cada bug).

> Em Agents: **após concluir uma tarefa que muda status, rota ou próximo passo, atualize `update_spec/andamento.spec.md` na mesma sessão.** É o passo que costuma ser esquecido.

## 6. O que não fazer

- ❌ Não copie a tabela de módulos para dentro de um spec de página.
- ❌ Não repita stack, RBAC, regras técnicas globais ou rotas gerais dentro de um spec de página — linke para `contexto.md`.
- ❌ Não repita as regras de organização de diretórios/arquivos dentro de um spec de página — linke para `organizacao.spec.md`.
- ❌ Não deixe duas versões da mesma rota em documentos diferentes sem apontar qual vale.
- ❌ Não coloque tabela de histórico dentro de um spec — o log fica só em `update_spec/mod_spec.md`.
- ❌ Não registre mudança pequena no `mod_spec.md` (typo, ajuste de texto, item acrescentado a uma seção).
- ❌ Não crie um spec novo por tarefa pequena: atualize o spec da página existente.
- ❌ Não use inglês nos títulos e tabelas dos specs (o código pode manter identificadores em inglês).
- ❌ Não altere `arquivados/especificacoes.md` e `arquivados/Site_Residencia_spec.md` (fontes históricas, arquivadas) — elas não são mais atualizadas.
- ❌ Não faça o `AGENTS.md` crescer: ele é índice, o contexto mora em `contexto.md`.

## 7. Índice dos documentos

| Arquivo | Tipo | Conteúdo | Atualizado por |
|---|---|---|---|
| `contexto.md` | geral (read-once) | Stack, não-funcionais, design, RBAC, regras técnicas, rotas gerais, ambiente, apps, gotchas | programador |
| `organizacao.spec.md` | spec de organização | Onde cada arquivo mora, nomenclatura, o que versionar, checklist de commit | programador + agente |
| `specs/noticias.spec.md` | spec de página | A Página 1 / Notícias (escopo, layout, modelo, admin, aceite) | programador + agente |
| `update_spec/andamento.spec.md` | vivo | Roadmap: módulos, versões, status, rotas previstas, itens transversais | programador + agente |
| `update_spec/mod_spec.md` | vivo | Log de mudanças de larga escala nos specs (nome, motivo, local, arquivo) | programador + agente |
| `update_spec/regras_atualizacao.md` | vivo | Este documento: regras de manutenção dos specs | programador |
| `AGENTS.md` | índice | Ordem de leitura e regras de ouro resumidas | programador |
