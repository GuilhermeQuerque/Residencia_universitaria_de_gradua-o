# mod_spec.md — Log de modificações de larga escala nos specs

> Registro **centralizado** de mudanças grandes feitas nos specs do projeto.
> Existe para que os arquivos de spec continuem limpos (só o conteúdo atual) e para que o histórico do *porquê* fique em um lugar só, consultável.
>
> **Última atualização:** 27/10/2026

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

### 28/10/2026 — Configuração por variável de ambiente (SECRET_KEY fora do código)

| | |
|---|---|
| **Motivo** | *Ant.:* o `SECRET_KEY` estava fixo no `core/settings.py` e publicado em todos os commits do GitHub; `DEBUG` e `ALLOWED_HOSTS` também fixos, sem forma de ligar o projeto em produção sem editar código. *Defeito:* segredo conhecido permite forjar sessões e cookies assinados; e o `check --deploy` do Django acusava 4 falhas de HTTPS (HSTS, redirect SSL, cookie de sessão e cookie CSRF). *Novo:* `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` e HSTS vêm do ambiente (`DJANGO_*`); o valor fixo virou fallback de desenvolvimento e o Django **recusa a subir** com `DEBUG=False` se ele ainda estiver em uso; HTTPS/cookies seguros ligam sozinhos fora de `DEBUG`; `.env.example` documenta as variáveis sem nenhum segredo. |
| **Local** | `core/settings.py` §"Configuração por variável de ambiente" (linhas 20–50) e §"HTTPS / cookies seguros" (linhas 150–163); `contexto.md` §9 (linhas 108–128); `organizacao.spec.md` §3 árvore-alvo (linha 41), §4.1 (linha 95) e §8 (linhas 229–240); `.env.example` (criação) |
| **Arquivos** | `core/settings.py`, `contexto.md`, `organizacao.spec.md`, `.env.example` |

### 27/10/2026 — Banco de desenvolvimento apagado

| | |
|---|---|
| **Motivo** | *Ant.:* o `db.sqlite3` estava **versionado no git** (commits `96e3509` em diante) e o repositório é público: o blob antigo continuava baixível, expondo 5 contas (incluindo o superuser `[SUPERUSER-OMITIDO]`), um email real da UFRN, um **CPF em texto puro** (`[CPF-OMITIDO]`) e hashes de senha. *Defeito:* dado pessoal e credenciais de teste publicados num repositório acessível a qualquer um. *Novo:* arquivo `db.sqlite3` **apagado do disco** (reconstruído com `python manage.py migrate`), `.gitignore` cobrindo `db.sqlite3`/`.env`/`*.pyc`/`media/`/`venv/`, e remoção dos blobs do índice. **Pendente:** o histórico do git ainda contém o banco — reescrever o histórico e rotacionar `SECRET_KEY`/senhas. |
| **Local** | `organizacao.spec.md` §4.8 (linhas 158–168); remoção de `db.sqlite3` (raiz); `.gitignore` (raiz) |
| **Arquivos** | `organizacao.spec.md`, `.gitignore` |

### 27/10/2026 — Spec de organização e reestruturação de pastas

| | |
|---|---|
| **Motivo** | *Ant.:* os specs de página viviam na raiz (`noticias.spec.md`), as fontes históricas (`especificacoes.md`, `Site_Residencia_spec.md`) também, e as imagens do site estavam em `imagens/` — fora de `static/`, que o `STATICFILES_DIRS` já referenciava mas **não existia** (o `{% static %}` do header apontava para arquivo morto). Não havia regra escrita de "onde cada arquivo mora" nem de nomenclatura. *Defeito:* raiz do repositório virava depósito de documento; inconsistência de caminhos quebrava o banner e não havia regra de nomenclatura nem de versionamento. *Novo:* spec transversal `organizacao.spec.md` (na raiz, por valer para o site inteiro); pasta `specs/` concentrando um spec por página; `arquivados/` para as fontes históricas congeladas; `imagens/` → `static/impressoras/imagens/`; `MEDIA_URL`/`MEDIA_ROOT`/`STATIC_ROOT` no settings e serviço de `media/` em desenvolvimento. |
| **Local** | Criação de `organizacao.spec.md` (1–268); `noticias.spec.md` → `specs/noticias.spec.md`; `especificacoes.md` → `arquivados/especificacoes.md`; `Site_Residencia_spec.md` → `arquivados/Site_Residencia_spec.md`; `imagens/cabecalho_residencia.jpg` → `static/impressoras/imagens/cabecalho_residencia.jpg`; `imagens/teste.pdf` → `static/impressoras/imagens/teste.pdf`; `core/settings.py` §"Static files" (linhas 118–130) com `STATIC_ROOT`, `MEDIA_URL` e `MEDIA_ROOT`; `core/urls.py` (linhas 17–30) servindo `static/` e `media/` em `DEBUG`; `contexto.md` §10–§12 (linhas 115–141); `AGENTS.md` (linhas 5–45); `update_spec/regras_atualizacao.md` §1, §2.2, §6, §7 (linhas 11–125); `update_spec/andamento.spec.md` §1, §2, §4 (linhas 15–79); `update_spec/README.md` (linhas 5–19); `specs/noticias.spec.md` cabeçalho e §13 (linhas 1–6, 234) |
| **Arquivos** | `organizacao.spec.md`, `specs/noticias.spec.md`, `arquivados/*`, `static/*`, `core/settings.py`, `core/urls.py`, `contexto.md`, `AGENTS.md`, `update_spec/*` |

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