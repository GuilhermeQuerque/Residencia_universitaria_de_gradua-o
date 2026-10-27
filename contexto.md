# contexto.md — Leitura inicial obrigatória (contexto geral do projeto)

> **Este é o primeiro arquivo a ler em qualquer chat/sessão.**
> Ele reúne, em um só lugar, o que é **igual para o site inteiro** — stack, regras, permissões, rotas, ambiente — para que a IA já comece entendendo o projeto sem precisar deduzir de outros arquivos.
> Ele é **geral** (vale para todas as páginas/módulos). O que é específico de uma página vive no spec daquela página (ex.: `specs/noticias.spec.md`).
>
> **Última atualização:** 27/10/2026

---

## 1. O que é este projeto

Portal web da **Residência Universitária de Graduação da UFRN** (Campus III / Campus Central, PROAE, Natal/RN): complexo de assistência estudantil com alojamentos coletivos e áreas comuns (salas de estudo, cozinha, lavanderia, convivência).

O site atualiza os residentes, facilita comunicação entre vendedores e compradores, e concentra serviços que os moradores precisam (votação DCE/Reitor, requisição de autorização, entre outros).

## 2. Stack e infraestrutura

- **Backend:** Python 3.14 + **Django 6.0.5**
- **Banco:** SQLite em desenvolvimento → **PostgreSQL em produção** (migrar quando o módulo entrar em produção)
- **Frontend:** HTML + CSS + templates do Django. **Com minimo de uso de JavaScript.**
- **Infraestrutura:** servidor local próprio da residência (`servidor_residencia`, via SSHFS em `residencia@10.2.184.170:/`), com rotinas de backup e logs de auditoria.
- **Idioma:** pt-br em todas as strings, labels, mensagens e nomes de rotas.

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

1. **Não adicionar bibliotecas extras** sem consultar o spec da página em que você está trabalhando.
2. **Não usar frameworks de frontend** (React, Vue, Angular…).
3. **JavaScript é permitido, mas no mínimo possível.** Use JS apenas quando o HTML/CSS puro não resolve o caso (ex.: widget do PIX InfinitePay). Onde o nativo resolver, resolva no nativo: `<details>` para dropdown, `<dialog>` para modal, CSS `:checked`/`:target` para abrir/fechar. Sem jQuery, sem bundler, sem `node_modules`.
4. **Migrar para PostgreSQL** quando o módulo entrar em produção.
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
# caminho no servidor (via SSHFS montado localmente)
/home/guizo/servidor_residencia/residencia/PROJETO_SITE   # local
/residencia/PROJETO_SITE                                   # no servidor

python manage.py runserver 0.0.0.0:8000
python manage.py migrate
python manage.py createsuperuser
python manage.py test
```

**Enviar para o GitHub:**

```bash
./push.sh                  # pede a mensagem, commita e envia
./push.sh "mensagem"       # commita com a mensagem dada
./push.sh --dry-run        # só mostra o que seria commitado
./push.sh --no-push        # commita local, não envia
```

O script **recusa** o commit se houver arquivo sensível rastreado (`db.sqlite3`, `.env`, `.pyc`, `media/`, `venv/`).

> ⚠️ O `venv/` do repositório foi criado no servidor remoto, é root-owned, só contém o `pip` (sem Django) e seus binários retornam `EPERM` pela montagem SSHFS — **`source venv/bin/activate` não funciona** a partir da montagem. Crie um venv próprio ou instale as dependências no `python3` do sistema.

## 9. Variáveis de ambiente (impressora)

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

