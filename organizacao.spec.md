# organizacao.spec.md — Spec de organização de diretórios e arquivos

> **Escopo deste arquivo:** as **regras de organização de diretórios e arquivos** do repositório do site da Residência Universitária de Graduação da UFRN.
> Serve para que qualquer programador (ou agente) saiba **onde cada arquivo mora**, **como nomear** e **o que não versionar** — sem precisar deduzir por leitura de código.
> **Contexto geral** (stack, regras técnicas, RBAC, rotas gerais, ambiente) está em **`contexto.md`** — leia antes.
> **Roadmap do site:** `update_spec/andamento.spec.md`.
> **Última atualização:** 28/10/2026

---

## 1. Objetivo

Duas metas:

1. **Organização do servidor** — o repositório tem uma estrutura previsível, o que reduz acerto em arquivos no lugar errado e deixa o deploy (`git pull` + `migrate` + restart) previsível.
2. **Visualização por programadores** — quem abre o repositório entende em segundos o que é cada pasta, sem ler código.

> **Escopo restrito ao repositório do site.** A organização do sistema operacional do servidor (partições, `/home`, `/var`, backups de sistema, permissões de usuário) **não** é regida por este spec — ver §12.

## 2. Princípios

| # | Princípio | O que significa na prática |
|---|---|---|
| 1 | **Uma pasta, uma responsabilidade** | `static/` é estático; `media/` é upload; `specs/` é spec; `arquivados/` é história morta. Nada "por acaso". |
| 2 | **Nome descritivo em pt-br, `snake_case`** | Pastas e arquivos de conteúdo usam `snake_case` (`cabecalho_residencia.jpg`). Código Python mantém PEP 8 (`snake_case`); nomes de classe Django usam `CamelCase`. |
| 3 | **Códigos do Django em inglês, conteúdo em português** | Identificadores (`models.py`, `Noticia`, `upload_to`) em inglês; rótulos, textos, nomes de arquivo visíveis ao usuário em pt-br. |
| 4 | **Documento em um lugar só** | Um spec por página, todos em `specs/`. Nada duplicado entre documentos. |
| 5 | **Nada gerado ou sensível versionado** | `db.sqlite3`, `media/`, `venv/`, `__pycache__/` nunca entram no git. |
| 6 | **Pasta vazia não versiona** | Git não guarda diretórios. Toda pasta precisa de um arquivo real (ou de um `.gitkeep`, se forplaceholder). |

## 3. Árvore-alvo do repositório

```
PROJETO_SITE/
├── AGENTS.md                  → índice de leitura (ponto de entrada para agentes)
├── contexto.md                → contexto geral do site (read-once)
├── organizacao.spec.md        → este spec (organização de diretórios e arquivos)
├── manage.py                  → entrypoint do Django
├── requirements.txt           → dependências do projeto (versionado)
├── push.sh                    → script de commit + push
├── segredos.py                → script que gera/decripta o SECRET_KEY (NÃO versionado)
├── .gitignore                 → lista do que NÃO versionar
├── .env.example               → modelo de variáveis de ambiente (sem segredos)
├── claude.md                  → nota original da ideia do portal (arquivada na prática)
│
├── specs/                     → um spec por página/módulo do site
│   ├── noticias.spec.md
│   └── producao.spec.md       → spec de produção (serviço 24/7, nginx, HTTPS)
│
├── update_spec/               → docs vivos (mudam a cada avanço)
│   ├── README.md
│   ├── andamento.spec.md      → roadmap (módulos, status, rotas)
│   ├── regras_atualizacao.md  → regras de manutenção dos specs
│   └── mod_spec.md            → log de mudanças de larga escala
│
├── arquivados/                → fontes históricas, NÃO são mais atualizadas
│   ├── Site_Residencia_spec.md
│   └── especificacoes.md
│
├── core/                      → app de configuração do Django
│   ├── settings.py
│   ├── segredos.py            → ponte que decripta o segredo (versionado)
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── controle/                  → app principal (impressora, auth, Perfil)
│   ├── models.py  views.py  forms.py  admin.py  urls.py  impressao.py
│   ├── migrations/
│   ├── templates/controle/
│   └── tests.py
│
├── noticias/                  → app do módulo de Notícias (planejado, v1)
│
├── static/                    → arquivos servidos pelo Django (versionado)
│   └── impressoras/imagens/
│
├── media/                     → uploads dos moradores (NÃO versionado)
│   └── .gitkeep               → mantém a pasta no git (o conteúdo é ignorado)
│
├── secrets/                   → segredo ENCRIPTADO do Django (NÃO versionado)
│   └── secret.key             → só o arquivo encriptado; a frase-semente é do operador
│
├── venv/                      → ambiente virtual (NÃO versionado)
└── db.sqlite3                 → banco local (NÃO versionado)
```

## 4. Regras por tipo de pasta

### 4.1 Raiz do repositório

Só entram na raiz: **configuração do projeto**, **ponto de entrada do Django** e **documentos de topo** (o índice, o contexto geral e este spec). Qualquer outro documento vai para `specs/` ou `update_spec/`.

| Item | Onde | Regra |
|---|---|---|
| `AGENTS.md` | raiz | Índice de leitura. Não cresce — aponta para os outros docs. |
| `contexto.md` | raiz | Contexto geral. Único lugar para stack, RBAC, rotas gerais, ambiente. |
| `organizacao.spec.md` | raiz | Este spec. Único spec fora de `specs/` (por ser regra transversal, não de página). |
| `manage.py` | raiz | Padrão do Django. |
| `requirements.txt` | raiz | Dependências do projeto, **versionado**. Fonte da verdade do que instalar — ver §6. |
| `push.sh` | raiz | Script operacional do repositório. |
| `segredos.py` | raiz | Script que **gera e decripta** o `SECRET_KEY`. **NÃO versionado** (§8). Vive na raiz porque é script operacional, junto do `push.sh`. |
| `.gitignore` | raiz | Lista de exclusão (§8). |
| `.env.example` | raiz | Modelo das variáveis de ambiente **sem segredo nenhum**. O `.env` real nunca é versionado. |

### 4.2 `specs/` — um spec por página/módulo

- **Um arquivo por página ou módulo**, no formato `<pagina>.spec.md` (`noticias.spec.md`, `album.spec.md`, `lojinha.spec.md`, `impressora.spec.md`).
- **Exceção: `producao.spec.md`** — não é uma página, é a operação do site no servidor (serviço systemd, nginx, HTTPS, backup). Fica em `specs/` mesmo assim, porque é o mesmo tipo de documento: escopo + regras + checklist de um recorte do projeto.
- O **conteúdo de cada spec** é o escopo, layout, modelo de dados, rotas e critérios de aceitação **daquela página**.
- Specs **nunca** repetem stack, RBAC, regras técnicas globais ou rotas gerais — isso está em `contexto.md`; o spec **linka**.
- O **roadmap** (módulos, versões, status, rotas previstas) **não** vive em `specs/` — vive em `update_spec/andamento.spec.md`.
- Ao criar um spec novo: siga o padrão de `specs/noticias.spec.md` (escopo no topo, seções numeradas, "Critérios de aceitação", "Quando atualizar este spec").

### 4.3 `update_spec/` — documentos vivos

- Documentos que mudam a cada avanço do site: roadmap, regras de manutenção e log de mudanças.
- **Não** comportam specs de página (isso é `specs/`).
- O `README.md` da pasta é o índice local do conjunto.

### 4.4 `arquivados/` — fontes históricas

- Documentos de origem que **não são mais atualizados** (`especificacoes.md`, `Site_Residencia_spec.md`).
- Servem só para consultar a origem de uma decisão.
- **Proibido** editar arquivos desta pasta. Se uma decisão antiga for superada, a mudança vai nos specs vivos, com registro em `update_spec/mod_spec.md`.

### 4.5 `static/` — estáticos versionados

- Tudo que o Django serve sem passar pelo app: CSS, JS, imagens de marca, ícones, fontes.
- **Versionado** no git (é código, não conteúdo gerado).
- Estrutura por módulo: `static/<modulo>/<tipo>/` — ex.: `static/impressoras/imagens/cabecalho_residencia.jpg`.
- O template referencia com `{% static "impressoras/imagens/cabecalho_residencia.jpg" %}` — o caminho **precisa** bater com o arquivo em disco.
- Hoje **cada template carrega seu próprio `<style>` inline** (ver `contexto.md` §4). Quando houver CSS consolidado, vai para `static/css/` — essa mudança precisa de aprovação no spec da página.

### 4.6 `media/` — uploads (NÃO versionado)

- Arquivos **enviados pelos moradores** (imagens de notícia, fotos do álbum, arquivos de impressão).
- **Nunca** entra no git. Já está no `.gitignore` (a pasta em si é mantida por um `.gitkeep`, para existir no repositório).
- Requer `MEDIA_URL` e `MEDIA_ROOT` no `core/settings.py` (definidos; ver `contexto.md` §12).
- Subpastas são criadas pelo `upload_to` do `FileField`/`ImageField` do model (ex.: `media/noticias/`, `media/arquivos_impressao/`).
- Em desenvolvimento, `core/urls.py` serve `media/` automaticamente quando `DEBUG=True`.
- Em produção, este diretório precisa de **backup** separado do código — ver `update_spec/andamento.spec.md` §4.

### 4.7 Apps Django (`core/`, `controle/`, `noticias/`)

Layout interno padrão de um app:

```
<app>/
├── __init__.py
├── apps.py            → AppConfig
├── models.py          → modelos e relacionamentos
├── views.py           → views
├── forms.py           → formulários
├── admin.py           → registro no Django Admin
├── urls.py            → rotas do app
├── tests.py           → testes
├── migrations/        → migrações (NUNCA editar à mão uma migration já aplicada)
└── templates/<app>/   → templates do app (namespace = nome do app)
```

**Regras:**

- **Um app por módulo do site** (`noticias/` para Notícias, `controle/` para Impressora + auth). Não criar um app por página se as páginas pertencem ao mesmo módulo.
- **Templates dentro do app**, em `templates/<nome_do_app>/` — nunca soltos na raiz do projeto.
- **Migrations**: geradas pelo Django (`makemigrations`). Editar à mão só em caso extremo, e nunca uma migration já aplicada no servidor.
- **`tests.py` dentro do app** que testa.
- Ao criar um app novo: registrar em `INSTALLED_APPS` (`core/settings.py`) e incluir as rotas em `core/urls.py`.

### 4.8 `venv/`, `requirements.txt` e banco de dados

- `venv/` e `db.sqlite3` são **artefatos locais**, ignorados pelo git.
- **O `venv/` do repositório NÃO funciona pela montagem SSHFS** (symlinks dão `EPERM`) — mas **funciona normalmente no servidor**, onde o sistema de arquivos é nativo. Ver `contexto.md` §8.
- **`requirements.txt` (raiz, versionado)** é a fonte da verdade das dependências:
  - Só entra no arquivo o que o código **realmente importa** (`Django`, `pypdf`) + as dependências transitivas fixadas.
  - **Não** gerar com `pip freeze` sem revisar: ele também gravaria pacotes de desenvolvimento e de sistema.
  - Instalar no servidor: `venv/bin/pip install -r requirements.txt`.
- **O banco é SQLite nos dois ambientes** (dev e servidor) — decisão de 28/10/2026, ver `contexto.md` §2.1. O `DATABASES` fica em `core/settings.py`, com **modo WAL** ativado.
- **O `db.sqlite3` foi apagado de propósito (27/10/2026):** era o banco de desenvolvimento, com contas de teste e um superuser, e tinha acabado versionado por engano. O arquivo é **reconstruído** a qualquer momento com `python manage.py migrate` — não há dado de produção nele.
  - O `.gitignore` garante que ele **nunca mais** entre no repositório.
  - **Atenção:** apagar o arquivo **não** remove o banco do **histórico do git**. As versões antigas continuam acessíveis no GitHub até que o histórico seja reescrito (ver `update_spec/mod_spec.md`).
  - **No servidor**, o `db.sqlite3` fica em `/home/residencia/PROJETO_SITE/` e é criado com `manage.py migrate`. É o banco real de produção — e precisa de **backup** (é um arquivo: copiar já é o backup).

### 4.9 `secrets/` e o script `segredos.py` — o segredo do Django

- **`segredos.py` (raiz)** — script que **gera** o `SECRET_KEY`, **encripta** e **decripta**. É o único lugar do projeto que conhece a criptografia. **Não versionado** (§8).
- **`secrets/secret.key` (raiz)** — o segredo **encriptado**, em texto local. Permissões `600`. **Não versionado** (§8).
- **`core/segredos.py`** — a **ponte importável**: carrega o script por caminho e expõe `obter_secret_key()`. **Este sim é versionado** — é código, não segredo. É importado por `core/settings.py`.
- A **frase-semente** (`DJANGO_MASTER_KEY`) **nunca** é salva em arquivo. Ela pertence ao operador (e ao ambiente do serviço). Sem ela, o arquivo encriptado é inútil — e está tudo bem: é só regerar o segredo.
- **Quem precisa do segredo em texto claro** importa `core.segredos.obter_secret_key()` e **não** reimplementa a decriptação nem lê o arquivo encriptado por conta própria. A regra completa está em `contexto.md` §9.
- O `push.sh` **recusa o commit** se `segredos.py` ou `secrets/` estiverem rastreados (§8).

## 5. Nomenclatura

| Tipo | Padrão | Exemplo |
|---|---|---|
| Pasta de conteúdo | `snake_case` pt-br | `static/impressoras/imagens/` |
| Arquivo de imagem | `snake_case` + extensão real | `cabecalho_residencia.jpg` |
| Spec de página | `<pagina>.spec.md` | `noticias.spec.md` |
| Documento vivo | `snake_case` + `.md` | `andamento.spec.md` |
| Módulo Python | `snake_case` (PEP 8) | `impressao.py` |
| Classe Django | `CamelCase` | `Noticia`, `ImpressoraConfig` |
| Variável / função | `snake_case` | `contar_paginas()` |
| Constante | `UPPER_CASE` | `EXTENSOES_IMPRESSAO` |
| Rota (`url_name`) | `snake_case` pt-br | `noticia_detalhe`, `solicitar_impressao` |

**Regras de nome:**

- Sem acentos, sem cedilha e sem espaço em **nomes de arquivo** (compatibilidade de shell e URL). Acentos só em **conteúdo** (textos de tela, comentários).
- Sem maiúsculas em nomes de arquivo (tudo minúsculo, `_` como separador).
- Extensão sempre em minúsculas (`.jpg`, `.py`, `.md`, `.pdf`).
- Zero à esquerda (`01_`, `02_`) só nas migrations do Django — é convenção do framework.
- Datas em nomes de arquivo: `AAAA-MM-DD` (ex.: `ata_assembleia_2026-10-27.md`).

## 6. Onde cada tipo de arquivo vai

| Tipo de arquivo | Pasta | Versionado? |
|---|---|---|
| Código Python (app) | `controle/`, `noticias/`, `core/` | sim |
| Dependências | `requirements.txt` (raiz) | sim |
| Template HTML | `<app>/templates/<app>/` | sim |
| Migration | `<app>/migrations/` | sim |
| CSS / JS / imagem de marca | `static/<modulo>/<tipo>/` | sim |
| Spec de página | `specs/<pagina>.spec.md` | sim |
| Documento vivo | `update_spec/<doc>.md` | sim |
| Fonte histórica | `arquivados/` | sim (congelado) |
| Ponte de segredos (código) | `core/segredos.py` | sim |
| Upload de morador | `media/<subpasta>/` | **não** |
| Banco local | `db.sqlite3` | **não** |
| Ambiente virtual | `venv/` | **não** |
| Cache Python | `__pycache__/` | **não** |
| Segredo em texto claro | `.env` | **não** |
| Segredo encriptado | `secrets/` | **não** |
| Script de segredos | `segredos.py` (raiz) | **não** |

## 7. Regras de nome na interface (visível ao usuário)

- **Strings sempre em pt-br** (`contexto.md` §6): rótulos, mensagens, `verbose_name` de campos, títulos de página.
- Nenhum texto em inglês visível ao usuário final.
- Identificadores de código permanecem em inglês (convenção Django/PEP 8).

## 8. O que **nunca** entra no git

```
db.sqlite3          → banco local
db.sqlite3-journal  → lock do banco
media/              → uploads dos moradores
venv/  .venv/       → ambiente virtual
__pycache__/        → cache Python
*.py[cod]           → bytecode
staticfiles/        → estáticos coletados (collectstatic)
.env  .env.*        → segredos e configuração local
*.pem  *.key        → chaves e certificados
*.log               → logs
secrets/            → segredo ENCRIPTADO do Django
/segredos.py        → script que gera/decripta o segredo
```

> ✅ **Sã o `.env.example`** — ele tem os *nomes* das variáveis e valores de exemplo, **nenhum segredo real**. É a única forma de documentar a configuração sem vazar nada.

O `push.sh` **recusa o commit** se algum desses já estiver rastreado — ver `contexto.md` §8.

> **Arquivo local de configuração:** se um valor variar entre máquinas (fila da impressora, chave de API), ele vem de **variável de ambiente** (`os.environ.get`) — ver `core/settings.py` §`IMPRESSORA_NOME`/`IMPRESSORA_IP` e `contexto.md` §9. Nunca hardcode e nunca comite.
>
> **`SECRET_KEY` em particular:** nunca no código — nem fixo, nem "fallback". O `core/settings.py` resolve o segredo por `core.segredos.obter_secret_key()`, que tenta (1) `DJANGO_SECRET_KEY` do ambiente e (2) o arquivo encriptado `secrets/secret.key`, decriptado com a frase-semente `DJANGO_MASTER_KEY`. Se nenhum dos dois existir, o Django **recusa a subir**. O `.env.example` documenta as variáveis; o `.env` real fica fora do git. Detalhes em `contexto.md` §9 e `organizacao.spec.md` §4.9.

## 9. Checklist antes de commitar

- [ ] O arquivo novo está na pasta certa (§4 e §6)?
- [ ] O nome segue `snake_case`, minúsculo, sem acento e sem espaço (§5)?
- [ ] Nada de `db.sqlite3`, `media/`, `venv/`, `__pycache__/`, `.env`, `secrets/` ou `segredos.py` rastreado?
- [ ] O `SECRET_KEY` não está escrito em nenhum arquivo versionado?
- [ ] Se criei um spec de página, ele está em `specs/` e segue o padrão de `specs/noticias.spec.md`?
- [ ] Se mudei escopo, status ou rota, `update_spec/andamento.spec.md` foi atualizado na mesma sessão?
- [ ] Se mudei algo geral (stack, RBAC, rotas, ambiente), `contexto.md` foi atualizado?
- [ ] As referências cruzadas (caminhos de arquivo, `§`) continuam apontando para o lugar certo?
- [ ] `./push.sh --dry-run` mostra só o que eu espero?

## 10. Onde esta spec é referenciada

| Documento | O que diz sobre organização |
|---|---|
| `AGENTS.md` | Ordem de leitura e índice de documentos (inclui este spec e `specs/`). |
| `contexto.md` §10, §11 | Estrutura de apps e onde está cada tipo de documento. |
| `update_spec/andamento.spec.md` §4 | Itens transversais (ex.: pasta `static/`, `MEDIA_URL`/`MEDIA_ROOT`). |
| `update_spec/regras_atualizacao.md` | Formato padrão dos specs e índice de documentos. |

> Este spec **não** duplica a tabela de módulos do roadmap (ver `update_spec/regras_atualizacao.md` §6).

## 11. Quando atualizar este spec

Atualize quando:

- entra/sai uma regra de organização (nova categoria de pasta, novo padrão de nome);
- muda a árvore-alvo (§3) — nova pasta relevante, pasta movida, pasta removida;
- uma decisão de organização é invertida (ex.: "specs na raiz" → "specs em `specs/`");
- uma inconsistência real é corrigida e o padrão precisa ficar registrado.

> Mudanças de **larga escala** na organização entram também no log `update_spec/mod_spec.md` (ver `update_spec/regras_atualizacao.md` §3).
> Mudança pequena (ajuste de texto, mover um arquivo sem mudar regra) **não** entra no `mod_spec.md`.

## 12. Fora do escopo

Este spec **não** regula:

- a organização do **sistema operacional** do servidor (`/home`, `/var`, `/opt`, partições, usuários, permissões, cron, backups de sistema);
- a estrutura interna do **banco de dados** (tabelas e models já são regidos pelos specs de página);
- a organização do **`venv/`** e do ambiente Python fora do repositório;
- ferramentas de **deploy** além do `push.sh` já descrito em `contexto.md` §8.

> Se o servidor precisar de um padrão de diretórios **de sistema**, isso vira um spec próprio — sugestão de nome: `servidor.spec.md` — e este spec linka para ele (sem duplicar o conteúdo).
