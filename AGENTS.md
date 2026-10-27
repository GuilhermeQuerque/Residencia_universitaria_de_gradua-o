# AGENTS.md — Índice de leitura e regras de trabalho (Residência Universitária UFRN)

Este arquivo é um **ponto de entrada curto**. Ele diz **o que ler, em que ordem**. O contexto geral do projeto (stack, regras, RBAC, rotas, ambiente, gotchas) está todo em **`contexto.md`** — leia uma vez e trabalhe com ele.

## Ordem de leitura (obrigatória)

1. **`contexto.md`** — leitura inicial 1x por sessão: o que é o projeto, stack, regras técnicas, RBAC, rotas, ambiente, gotchas.
2. **O spec da página/módulo em que você vai trabalhar** — ex.: `noticias.spec.md` (Página 1 / Notícias). Se a tarefa não é de uma página específica, o passo 1 basta.
3. **`update_spec/andamento.spec.md`** — só se a tarefa mexer em escopo, status, rotas previstas ou próximos passos (é o roadmap vivo).
4. **`update_spec/regras_atualizacao.md`** — antes de editar qualquer spec.

## Documentos do projeto

| Documento | Tipo | Quando usar |
|---|---|---|
| `contexto.md` | Geral (read-once) | sempre, no início |
| `noticias.spec.md` | Spec do módulo/página Notícias (Página 1) | ao trabalhar em notícias/home |
| `update_spec/andamento.spec.md` | Roadmap **vivo** | mudanças de escopo/status/rota |
| `update_spec/regras_atualizacao.md` | Regras de update dos specs | antes de editar specs |
| `update_spec/mod_spec.md` | Log de mudanças de larga escala nos specs | para consultar o histórico do porquê |
| `especificacoes.md`, `Site_Residencia_spec.md`, `claude.md` | **Arquivados** (origem) | só para consultar a fonte |

## Comandos rápidos

```bash
cd /home/guizo/servidor_residencia/residencia/PROJETO_SITE
python manage.py runserver 0.0.0.0:8000
python manage.py migrate
python manage.py test
./push.sh "mensagem"      # commit + push para o GitHub
```

> O `venv/` do repositório **não funciona** pela montagem SSHFS (root-owned, só tem pip, binários com EPERM). Detalhes em `contexto.md` §8.

## Regras de ouro (resumo — o porquê está em `contexto.md`)

- **Não** adicionar libs extras nem frameworks frontend. **JS é permitido, mas no mínimo possível** (nativo antes de JS) — consulte o spec da página.
- Strings sempre em **pt-br**.
- Módulos/páginas com specs separados: um spec por página, seguindo o padrão de `noticias.spec.md`.
- Mudou escopo/status/rota/próximo passo? Atualize `update_spec/andamento.spec.md` (tabela **e** registro) na mesma sessão.

> O restante do contexto (stack, não-funcionais, design, RBAC, rotas gerais, ambiente, estrutura de apps, gotchas) está em **`contexto.md`**.