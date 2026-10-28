# contexto.md — Leitura inicial obrigatória (contexto geral do projeto)

> **Este é o primeiro arquivo a ler em qualquer chat/sessão.**
> Ele reúne, em um só lugar, o que é **igual para o site inteiro** — stack, regras, permissões, rotas, ambiente — para que a IA já comece entendendo o projeto sem precisar deduzir de outros arquivos.
> Ele é **geral** (vale para todas as páginas/módulos). O que é específico de uma página vive no spec daquela página (ex.: `specs/noticias.spec.md`).
>
> **Última atualização:** 28/10/2026

---

## 1. O que é este projeto

Portal web da **Residência Universitária de Graduação da UFRN** (Campus III / Campus Central, PROAE, Natal/RN): complexo de assistência estudantil com alojamentos coletivos e áreas comuns (salas de estudo, cozinha, lavanderia, convivência).

O site atualiza os residentes, facilita comunicação entre vendedores e compradores, e concentra serviços que os moradores precisam (votação DCE/Reitor, requisição de autorização, entre outros).

## 2. Stack e infraestrutura

- **Backend:** Python 3.14 + **Django 6.0.5**
- **Banco:** **SQLite (nativo do Django) também em produção** — ver §2.1
- **Frontend:** HTML + CSS + templates do Django. **Com minimo de uso de JavaScript.**
- **Infraestrutura:** servidor local próprio da residência (`servidor_residencia`, via SSHFS em `residencia@10.2.184.170:/`), com rotinas de backup e logs de auditoria.
- **Idioma:** pt-br em todas as strings, labels, mensagens e nomes de rotas.

### 2.1 Banco de dados: SQLite em produção

**Decisão de 28/10/2026.** O projeto usa **SQLite nos dois ambientes** — em desenvolvimento e no servidor. Não há PostgreSQL.

**Por quê:**

| Motivo | Detalhe |
|---|---|
| **Volume** | O site atende dezenas de moradores de uma residência: poucos milhares de registros de impressão, pagamento e perfil. Isso é pequeno para qualquer banco. |
| **Zero servidor de banco** | Não há `postgres` instalado no servidor, nem serviço para manter, atualizar, fazer backup e proteger. |
| **Zero dependência extra** | PostgreSQL exigiria `psycopg` — uma lib a mais, contra a regra do §6.1. SQLite é nativo do Django. |
| **Backup trivial** | O banco é **um arquivo** (`db.sqlite3`): copiar o arquivo é o backup. Com PostgreSQL seria `pg_dump` + agendamento. |
| **Código neutro** | Nenhum model usa recurso específico de PostgreSQL. Trocar de banco depois é só mudar o `ENGINE` — o Django não exige reescrever os models. |

**Teste de concorrência feito (28/10/2026, no servidor):** 8 threads (4 escrevendo + 4 lendo), 240 operações — **zero erros**, 7 s. Com **modo WAL** ativado (`journal_mode=wal`), leitura e escrita acontecem ao mesmo tempo, que é o caso real do site.

**Limites conhecidos (quando revisitar):** o SQLite serializa as escritas. Para um site com muitos usuários gravando ao mesmo tempo, o PostgreSQL escala melhor. **Ponto de revisão:** se o site passar a ter tráfego pesado, ou se o "controle de visitantes" (v3, com log de auditoria próprio) gerar gravação constante, reavaliar para PostgreSQL.

**Como trocar, se um dia precisar:** `DATABASES` em `core/settings.py` muda o `ENGINE` para `django.db.backends.postgresql` e o `NAME` para o banco; os models não mudam. O `psycopg` precisaria ser instalado (é dependência nova — perguntar antes, §6.1).

## 3. Requisitos não-funcionais

- **Mobile-first:** a interface é usada principalmente no celular do morador e na portaria — layout pensado primeiro para telas pequenas.
- **LGPD:** proteção de dados sensíveis de moradores e visitantes (documentos, foto de perfil, entrada/saída). O módulo de notícias publica apenas conteúdo institucional; nunca dados de visitantes.
- **Arquitetura leve:** sem build step, sem npm, sem framework SPA; deploy por `git pull` + `migrate` + restart do serviço.
- **Auditoria:** ações administrativas sensíveis (publicar/editar/remover notícia, aceitar anúncio, liberar impressão) devem ficar rastreadas. O `LogEntry` do Django Admin já cobre o painel; o módulo de visitantes exigirá log próprio.
- **Acessibilidade:** HTML semântico (`header/nav/main/article/section/footer`), `alt` obrigatório nas imagens, contraste AA, foco visível, link "pular para o conteúdo".

## 4. Design e identidade visual

- **Protótipo aprovado:** https://classificadosdaresi.my.canva.site/
- **Referência de layout da página de notícias:** https://g1.globo.com/ (estrutura de portal de notícias, não identidade visual).
- **Cores:** oficiais da UFRN e da Residência, conforme o protótipo; logomarca pré-definida no protótipo.
- **Implementação:** não existe CSS externo no projeto — cada template carrega seu próprio `<style>` inline. Manter esse padrão (ou consolidar em um `static/css/` no v2, com aprovação no spec).

## 5. Atores e permissões (RBAC consolidado)

| Ator | Acesso | Pode |
|---|---|---|
| **Visitante (não autenticado)** | `/`, `/noticias/`, `/noticia/<id>/`, `/impressora/` (consulta de valores/status), `/lojinha/` (listar e pegar contato do vendedor) | Ler notícias, ver o mural, consultar valores da impressora |
| **Morador (autenticado)** | tudo do visitante + área logada | Usar a impressora (upload + pagamento), pedir/solicitar itens na lojinha, votar/comentar (futuro), requerer autorização (futuro) |
| **Jornalista (estudante de jornalismo com permissão)** | Django Admin, restrito ao modelo `Noticia` | Publicar, editar, remover, priorizar e marcar como **importante** as notícias; controlar destaques e o menu lateral |
| **Administrador / Conselho da Residência** | Django Admin completo | Aceitar/ativar anúncios, gerenciar posts (fotos, notícias), mudar status da impressora (funcionando / em manutenção), avisos de PROAE, atas |
| **Portaria / Segurança** | Área logada da portaria (v3) | Ler e validar rápido de entrada e saída de visitantes |

> **Regra de ouro:** o **mural de notícias é administrado somente por estudantes de jornalismo**. O painel administrativo é "oculto" (não é linkado no site público).

## 6. Regras técnicas globais

1. **Não adicionar bibliotecas extras por vontade própria.** A regra permite **perguntar** — e perguntar é o caminho certo quando a biblioteca faz sentido. O que **não** pode é adicionar a dependência sem o programador decidir. Na prática:
   - **Pode** usar só o que já está instalado (biblioteca padrão do Python, Django, o que o `requirements.txt` já trouxer).
   - **Pode** sugerir uma biblioteca e **perguntar** — mesmo que a solução pareça óbvia.
   - **Não pode** instalar, adicionar ao `requirements.txt` ou escrever código que dependa de uma lib nova sem a resposta do programador.
   - Antes de perguntar, ver se a biblioteca padrão resolve (o `contexto.md` §9 traz um exemplo: a encriptação do `SECRET_KEY` foi feita com `secrets` + `hashlib.scrypt` + `hmac`, sem `pip install`).
   - Se a resposta for "não", o caminho é resolver com o que já existe — não contornar a regra.

   > A pergunta é barato; a dependência é permanente (instalar no servidor, manter atualizada, auditing de segurança). Por isso ela se decide antes, não depois.

2. **Não usar frameworks de frontend** (React, Vue, Angular…).
3. **JavaScript é permitido, mas no mínimo possível.** Use JS apenas quando o HTML/CSS puro não resolve o caso (ex.: widget do PIX InfinitePay). Onde o nativo resolver, resolva no nativo: `<details>` para dropdown, `<dialog>` para modal, CSS `:checked`/`:target` para abrir/fechar. Sem jQuery, sem bundler, sem `node_modules`.
4. **SQLite em produção também** (decisão de 28/10/2026) — o ponto de revisão para PostgreSQL está em §2.1.
5. **Strings sempre em português** (pt-br), sem acento removido no código (apenas em strings de log antigas, legado).
6. **Fotos/arquivos de upload** via `MEDIA_ROOT`; estáticos via `STATICFILES_DIRS`.
7. Sem `Pillow`/processamento de imagem no v1: apenas upload do arquivo original com validação de extensão e tamanho.

## 7. Estrutura de rotas (geral do site)

| Rota | Nome (`url_name`) | Acesso | Descrição |
|---|---|---|---|
| `/` | `inicial` | público | **Página inicial = Notícias** (destaques + grid + lista) |
| `/noticias/` | `noticias` | público | Listagem completa, com filtro por categoria e paginação |
| `/noticia/<int:pk>/` | `noticia_detalhe` | público | Leitura de uma notícia |
| `/news/` | — | público | **Alias** que redireciona (301) para `/noticias/` |
| `/impressora/` | `impressora` | público | Consulta de valores e status da impressora |
| `/impressao/solicitar/` | `solicitar_impressao` | morador | Upload + pagamento + impressão (rota já existente) |
| `/impressoras/` | `selecionar_impressora` | staff | Seleção da fila CUPS (rota já existente) |
| `/album/` | `album` | público | Álbum de fotos |
| `/lojinha/` | `lojinha` | público | Anúncios |
| `/login/`, `/logout/`, `/registrar/` | — | — | Autenticação (rotas já existentes) |
| `/painel/` | `painel` | morador | **Antigo dashboard** (histórico de impressões), hoje em `/` |
| `/admin/` | — | staff | Django Admin (oculto) |

> **Atenção às colisões:** `/impressora/` (público) e `/impressoras/` (staff) são coisas diferentes — não unificar por engano.
> Rotas de módulos **ainda não implementados** (v2/v3) estão resumidas em `update_spec/andamento.spec.md` — é lá que elas mudam quando o escopo muda.

## 8. Ambiente e comandos (reproduzível)

```bash
# --- caminhos ---
# Local (via SSHFS montado de root@10.2.184.170:/home):
/home/guizo/servidor_residencia/residencia/PROJETO_SITE
# No servidor (caminho real):
/home/residencia/PROJETO_SITE

# --- no servidor (o venv do projeto) ---
cd /home/residencia/PROJETO_SITE
venv/bin/python manage.py runserver 0.0.0.0:8000
venv/bin/python manage.py migrate
venv/bin/python manage.py createsuperuser
venv/bin/python manage.py test
venv/bin/python manage.py check --deploy
```

> ⚠️ **O `venv/` quebra SÓ pela montagem SSHFS** (os symlinks dão `EPERM` — `readlink` em `venv/bin/python` falha). **No servidor ele funciona normalmente.** Não criar venv dentro da pasta montada: `python -m venv` falha ali com `Operation not permitted`. Use o `venv/` do servidor ou um venv em disco local (`/tmp`).
>
> O `venv/` do servidor tem **Python 3.14.3** e o Django **6.0.5** instalado (28/10/2026). As dependências estão fixadas em `requirements.txt`.

**Acesso ao servidor:** `ssh root@10.2.184.170` (chave já instalada em 28/10/2026 — sem senha no prompt). O `git` **não está instalado** no servidor: o deploy é manual.

**Carregar as variáveis de ambiente (serviço ou shell):**
```bash
set -a; . /home/residencia/PROJETO_SITE/.env; set +a
```

> ⚠️ **O `SECRET_KEY` no `.env` precisa ser seguro para shell.** Se tiver `$` ou `)`, o shell expande `$var` ou quebra a linha de sintaxe — e o Django lê um valor diferente (ou nenhum) **sem avisar**. O `segredos.py` já gera só com `A-Za-z0-9-_.~` por isso.

**Enviar para o GitHub:**

```bash
./push.sh                  # pede a mensagem, commita e envia
./push.sh "mensagem"       # commita com a mensagem dada
./push.sh --dry-run        # só mostra o que seria commitado
./push.sh --no-push        # commita local, não envia
```

O script **recusa** o commit se houver arquivo sensível rastreado (`db.sqlite3`, `.env`, `.pyc`, `media/`, `venv/`).

> ⚠️ O `venv/` do repositório foi criado no servidor remoto e é root-owned. Pela montagem SSHFS os binários retornam `EPERM` — **`source venv/bin/activate` não funciona** a partir da montagem. No servidor, porém, **funciona normalmente** (Python 3.14.3 + Django 6.0.5 instalados em 28/10/2026).

## 9. Variáveis de ambiente

### Django / segurança (ler primeiro)

| Variável | Padrão | Quando usar |
|---|---|---|
| `DJANGO_SECRET_KEY` | — (nenhuma) | **Obrigatória em produção.** Sem ela, o Django não sobe — não existe valor fixo no código |
| `DJANGO_MASTER_KEY` | — (nenhuma) | Frase-semente que **decripta** o segredo local. Só em desenvolvimento |
| `DJANGO_DEBUG` | `True` | `False` em produção (liga SSL, cookies seguros e HSTS) |
| `DJANGO_ALLOWED_HOSTS` | vazio | Lista separada por vírgula: `a.com,b.com` |
| `DJANGO_SECURE_HSTS_SECONDS` | `31536000` | Em produção, tempo do HSTS em segundos |

### O `SECRET_KEY`: script de geração e decriptação

> **Regra de ouro:** o `SECRET_KEY` **nunca** está escrito no código — nem em `core/settings.py`, nem em nenhum arquivo versionado.

O segredo é gerado e guardado **encriptado** pelo script `segredos.py` (raiz do repositório):

```bash
# 1. Gerar o segredo (pede a frase-semente; ela nunca é salva em arquivo).
./segredos.py gerar

# 2. Ver o valor em texto claro.
DJANGO_MASTER_KEY="sua frase" ./segredos.py decriptar

# 3. Gravar direto no .env local (permissões 600).
DJANGO_MASTER_KEY="sua frase" ./segredos.py decriptar --escrever-env

# 4. Conferir se o arquivo encriptado continua íntegro.
DJANGO_MASTER_KEY="sua frase" ./segredos.py verificar
```

**Onde o segredo é resolvido** (`core/settings.py`, via `core/segredos.py`), em ordem de preferência:

1. **`DJANGO_SECRET_KEY` do ambiente** — é o caminho de **produção**; o serviço do servidor define a variável.
2. **Arquivo `secrets/secret.key`, decriptado na hora** — caminho de **desenvolvimento**; precisa da frase-semente em `DJANGO_MASTER_KEY`.
3. **Nenhum dos dois** → o Django **recusa a subir** com `RuntimeError` explicando o que fazer.

> ⚠️ **Onde o decriptamento é necessário:** o `core/segredos.py` é o **único** lugar do projeto que decripta o segredo — ele é importado pelo `core/settings.py`, que é o **único** ponto onde o valor em texto claro é usado. Qualquer outro módulo que precisar do segredo (ex.: um script de backup, uma tarefa de deploy) deve **importar `core.segredos.obter_secret_key()`** e **nunca** reimplementar a decriptação, nem ler o arquivo encriptado por conta própria.

**Como a encriptação funciona** (implementada com a **biblioteca padrão do Python** — sem `pip install`, conforme a regra de libs extras do §6):

- `secrets` sorteia o *salt* e o *nonce* de cada encriptação;
- `hashlib.scrypt` deriva a chave a partir da frase-semente (lento de propósito, contra força bruta);
- `hmac`/`sha256` gera o fluxo de cifragem (modo CTR) e a **etiqueta de autenticação**;
- o arquivo encriptado tem o formato `v1.<salt>.<nonce>.<cifrado>.<etiqueta>` (Base64 url-safe);
- o decriptor **confere a etiqueta antes de devolver qualquer texto** — se a frase estiver errada ou o arquivo for adulterado, ele **falha** em vez de devolver lixo.

> ⚠️ **O `SECRET_KEY` antigo estava publicado no histórico do git** (27/10/2026) — quem o conhece consegue forjar sessões e cookies assinados. Ele foi removido do código e **não volta**: o valor novo só existe encriptado ou no ambiente. **Rotacionar** o valor antigo continua pendente no histórico (ver `update_spec/andamento.spec.md` §4).

> 📌 **O `segredos.py` (raiz) e a pasta `secrets/` estão no `.gitignore`** — junto com o `.env`. O módulo `core/segredos.py` **versiona normalmente**, porque é código, não segredo.

### Impressora

```bash
export IMPRESSORA_NOME="impresora_padrão"   # ou outra fila CUPS
export IMPRESSORA_IP="10.1.168.164"
```

## 10. Estrutura de apps

- `controle/` — App principal (models, views, forms, impressao) + Perfil (morador)
- `core/` — Configurações Django (settings, urls, wsgi)
- `noticias/` — **Planejado** (v1): app do módulo de notícias (detalhes em `specs/noticias.spec.md` §13)

> A **organização de diretórios e arquivos** (onde cada coisa mora, nomenclatura, o que não versionar) está em **`organizacao.spec.md`**.

## 11. Onde está cada tipo de documento

| Documento | Tipo | Quando ler |
|---|---|---|
| `contexto.md` (este) | **Geral** — leitura inicial | **Sempre, 1x por sessão** |
| `organizacao.spec.md` | **Spec de organização** | Ao criar/mover/renomear arquivos e pastas |
| `specs/noticias.spec.md` | Spec do **módulo/página** | Ao trabalhar na Página 1 / Notícias |
| `update_spec/andamento.spec.md` | **Vivo** — roadmap (módulos, status, rotas previstas) | Quando o escopo/status do projeto muda |
| `update_spec/regras_atualizacao.md` | **Vivo** — regras de manutenção dos specs | Antes de editar qualquer spec |
| `update_spec/mod_spec.md` | **Vivo** — log de mudanças de larga escala nos specs | Para consultar o histórico do *porquê* das mudanças |
| `arquivados/especificacoes.md`, `arquivados/Site_Residencia_spec.md` | **Arquivados** (fonte histórica) | Só para consultar a origem |

## 12. Gotchas do código atual

- `controle/models.py` **não tem** `moradores`: o morador é o `Perfil` (OneToOne → `User`). Evoluir esse modelo em vez de criar tabela paralela.
- O `dashboard` ainda ocupa `/` com `@login_required`; o plano é movê-lo para `/painel/` e deixar `/` para a home de notícias (público).
- Sem `Pillow` ainda — o upload de imagens das notícias exigirá configurar isso (ver `specs/noticias.spec.md` §13).
- `MEDIA_URL`/`MEDIA_ROOT` e a pasta `static/` **já estão configurados** (27/10/2026) e a imagem do header está em `static/impressoras/imagens/cabecalho_residencia.jpg`. O que falta é o `MEDIA_ROOT` com subpastas de `upload_to` em produção (ver `organizacao.spec.md` §4.6).

