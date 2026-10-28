# `update_spec/` — Specs vivos do projeto

Documentos que **mudam a cada avanço** do site. São diferentes dos documentos da raiz:

| Documento | Onde | Papel |
|---|---|---|
| [`../contexto.md`](../contexto.md) | raiz | **Contexto geral** — leitura inicial 1x por sessão (stack, regras, RBAC, rotas, ambiente). |
| [`../organizacao.spec.md`](../organizacao.spec.md) | raiz | **Spec de organização** — onde cada arquivo mora, nomenclatura, o que versionar. |
| [`../specs/noticias.spec.md`](../specs/noticias.spec.md) | `specs/` | **Spec de página** — um arquivo por página do site (esta é a Página 1 / Notícias). |
| [`../specs/producao.spec.md`](../specs/producao.spec.md) | `specs/` | **Spec de produção** — como publicar o site 24/7 no servidor (systemd, gunicorn, nginx, HTTPS, backup). |
| [`andamento.spec.md`](andamento.spec.md) | aqui | **Roadmap do site** (vivo): módulos, versões, status, rotas previstas, próximos passos, registro de alterações. É o único lugar onde a visão geral dos módulos é mantida. |
| [`regras_atualizacao.md`](regras_atualizacao.md) | aqui | **Regras de manutenção dos specs** (vivo): quando atualizar cada documento, formato padrão, checklist e o que não fazer. |
| [`mod_spec.md`](mod_spec.md) | aqui | **Log de mudanças de larga escala** (vivo): o que mudou em cada spec, o motivo (ideia antiga / defeito / ideia nova) e onde. |

## Regras em uma linha

> Mudou módulo, status, rota ou próximo passo? → atualize `andamento.spec.md` (tabela **e** registro de alterações) na mesma hora.
> Mudou algo geral (stack, regras, RBAC, rotas, ambiente)? → atualize `contexto.md`.
> Mudou o escopo de uma página? → atualize o spec daquela página (`specs/`).
> Mudou a organização de diretórios/arquivos? → atualize `organizacao.spec.md`.

Antes de escrever em qualquer spec, leia [`regras_atualizacao.md`](regras_atualizacao.md) — ela define o formato e evita conteúdo duplicado entre documentos.