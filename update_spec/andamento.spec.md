# andamento.spec.md — Roadmap vivo do Site da Residência Universitária de Graduação (UFRN)

> **Documento VIVO.** Este arquivo muda a cada avanço do projeto e é o **único** lugar onde a visão de módulos, prioridades e status do site é mantida.
> **Regra:** nenhum outro spec pode duplicar a tabela de módulos. Se um módulo nasce, muda de status ou ganha/perde rota, **este arquivo é atualizado na mesma hora** (ver `regras_atualizacao.md`).
> **Última atualização:** 27/10/2026

---

## 1. Metodologia

**Build as you go** (de `arquivados/Site_Residencia_spec.md`): o agente segue o spec e implementa; o programador define o rumo do site atualizando os specs.

Consequência prática: o escopo do site é amplo e nem tudo está definido. Documentos foram separados em dois tipos:

| Tipo | Onde vive | Quando muda |
|---|---|---|
| **Contexto geral** (read-once) | `contexto.md` na raiz | Só quando muda a stack, as regras globais, o RBAC ou o ambiente |
| **Spec de página** (estável) | `specs/` na raiz do repo | Quando o escopo/regra daquela página muda |
| **Spec de organização** (estável) | `organizacao.spec.md` na raiz | Quando a organização de diretórios/arquivos muda |
| **Spec vivo** (mutável) | `update_spec/` | A cada atualização do projeto |

## 2. Visão geral dos módulos

**Legenda de status:** `planejado` · `em andamento` · `concluído` · `adiado`

| Módulo | Descrição | Versão | Status | Rotas |
|---|---|---|---|---|
| **Notícias / Mural** | Página inicial com destaques, mural de avisos, atas, avisos PROAE, regimento, documentos | v1 | **planejado** (spec em `specs/noticias.spec.md`) | `/`, `/noticias/`, `/noticia/<id>/` |
| **Impressora compartilhada** | Upload de arquivos, cobrança via PIX, impressão automática em CUPS | v1 | **em andamento** | `/impressao/solicitar/`, `/impressoras/` |
| **Lojinha (anúncios)** | Moradores vendem itens/serviços; contato por WhatsApp; admin ativa/desativa | v2 | planejado | `/lojinha/` |
| **Álbum de fotos** | Álbuns de eventos da residência com fotos | v2 | planejado | `/album/` |
| **Controle de visitantes** | Solicitação e emissão de autorização de visita (portaria) | v3 | planejado | `/visitantes/` |
| **Espaços e infraestrutura** | Agendamento de equipamentos (lavanderia), escala de limpeza, chamados de manutenção | v3 | planejado | `/espacos/`, `/chamados/` |
| **Votação / Representações** | Votação DCE, Reitor, Griffiths etc. | v3 | planejado | `/votacoes/` |

## 3. Módulos por status — detalhe

### Notícias / Mural (v1) — planejado
- Spec completo em `specs/noticias.spec.md`.
- **Próximo passo:** criar o app `noticias` (model, admin, views, templates) e mover o dashboard logado de `/` para `/painel/`.
- Bloqueia: nada. É a primeira página do site.

### Impressora compartilhada (v1) — em andamento
- Funcional: upload multi-arquivo, contagem de páginas via `pypdf`, envio para CUPS (`lp`), cobrança automática de R$ 0,50/página registrada em `Pagamento`.
- **Falta:** fluxo de pagamento PIX (InfinitePay) com QR Code e expiração de 10 min; página pública `/impressora/` com valores e status (funcionando / em manutenção).
- Bloqueia: nada.

### Lojinha (v2) — planejado
- Modelos já decididos: `Anuncio` (tipo `servico`/`item`, valor, `esgotado`, `ativo`, `contato_whatsapp`).
- Admin ativa/desativa anúncios; visitante vê o contato por WhatsApp.

### Álbum de fotos (v2) — planejado
- Modelos já decididos: `Album` (nome, descrição do evento, criado_por) e `Foto` (album, nome_arquivo, url_imagem).

### Controle de visitantes (v3) — planejado
- Solicitação de autorização de visita pelo morador; validação na portaria.
- **Atenção LGPD:** dados sensíveis de visitantes — exige log de auditoria próprio.

### Espaços e infraestrutura (v3) — planejado
- Agendamento de equipamentos compartilhados (lavanderia), escala de limpeza, chamados de manutenção predial/rede.

### Votação / Representações (v3) — planejado
- Votação em DCE, Reitor, Griffiths etc.

## 4. Itens transversais (módulos × regras)

| Item | Estado | Onde |
|---|---|---|
| Menu lateral do site (HTML/CSS puro, JS só como melhoria) | pendente | `specs/noticias.spec.md` §9 |
| `base.html` refatorado de "gerenciador de impressões" para base do **site** | pendente | `specs/noticias.spec.md` §13 |
| `MEDIA_URL` / `MEDIA_ROOT` no settings | **concluído** (27/10/2026) | `organizacao.spec.md` §4.6 |
| Pasta `static/` + `impressoras/imagens/cabecalho_residencia.jpg` | **concluído** (27/10/2026) | `organizacao.spec.md` §4.5 |
| Especificação da organização de diretórios e arquivos | **concluído** (27/10/2026) | `organizacao.spec.md` |
| Migração SQLite → PostgreSQL | pendente (ao ir para produção) | `contexto.md` §2 e §6 |
| Backup do banco no `servidor_residencia` | pendente | `contexto.md` §3 |
| Backup do `media/` (uploads) no `servidor_residencia` | pendente | `organizacao.spec.md` §4.6 |
| Log de auditoria próprio (visitantes) | pendente | `contexto.md` §3 |
| HTTPS/domínio do servidor | pendente | `contexto.md` §2 |
| **Reescrever histórico do git** (tirar `db.sqlite3` dos commits antigos) + rotacionar `SECRET_KEY` e senhas | **urgente** | `update_spec/mod_spec.md` (27/10/2026) |
