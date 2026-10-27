# noticias.spec.md — Spec da Página 1: Inicial / Notícias

> **Escopo deste arquivo:** a **primeira página do site** (`/`) — a home de notícias, com destaques, grid de 3, lista de notícias passadas, menu lateral e a página de leitura de uma notícia.
> **Contexto geral** (stack, regras técnicas, RBAC, rotas gerais, design, ambiente) está em **`contexto.md`** — leia antes.
> **Organização de diretórios e arquivos** está em **`organizacao.spec.md`**.
> **Status do módulo / roadmap do site:** `update_spec/andamento.spec.md`.
> **Última atualização:** 27/10/2026

---

## 1. Objetivo e público

Primeira página do site, **pública** (visitante não autenticado precisa ver as notícias sem logar). Concentra o que está acontecendo na residência e dá entrada para os demais módulos pelo menu lateral.

Referência de **estrutura** (não de identidade visual): https://g1.globo.com/

## 2. Rotas desta página

| Rota | `url_name` | Acesso | Descrição |
|---|---|---|---|
| `/` | `inicial` | público | **Home = Notícias** (destaques + grid + lista) |
| `/noticias/` | `noticias` | público | Listagem completa, filtro por categoria e paginação |
| `/noticia/<int:pk>/` | `noticia_detalhe` | público | Leitura de uma notícia |
| `/news/` | — | público | Alias → redirect 301 para `/noticias/` |

> O `dashboard` logado hoje ocupa `/`; ele migra para `/painel/` (ver `contexto.md` §7).

## 3. Categorias de notícia (definidas pelo jornalista)

| Valor | Rótulo | Exemplos de conteúdo |
|---|---|---|
| `destaque` | Destaques | Desligamento de energia, detetização, aviso urgente |
| `evento` | Eventos da residência | Festas, manifestações, atividades, assembleias |
| `dia_a_dia` | Dia a dia | Notícias comuns do cotidiano da residência |
| `ru` | Informes do RU | Cardápio de café, almoço e janta |
| `bolsa` | Bolsas e auxílios | Datas de recebimento de bolsas, auxílio 4ª refeição |
| `regras` | Regras, costumes e lazer | Normas de convivência, regras do bloco, lazer |

> A categoria é **sempre escolhida pelo jornalista** na publicação. A home destaca a categoria em foco; as demais viram sub-páginas no menu lateral (filtro).

## 4. Layout por zonas (desktop ≥ 1024px)

```
┌───────────────────────────────────────────────────────────────┐
│ BANNER SUPERIOR                                               │
│ [☰]  Logo UFRN · Residência Universitária de Graduação  [Entrar]│
├──────────┬────────────────────────────────────────────────────┤
│ MENU     │  ZONA DESTAQUES                                   │
│ LATERAL  │  ┌──────────────────────┬──────────────────────┐   │
│ (slide)  │  │  SLOT A              │  SLOT B              │   │
│ Notícias │  │  (destaque /         │  (prioridade 1,      │   │
│  ▾ sub-  │  │   "importante")      │   mais recente)     │   │
│   páginas│  │                      ├──────────────────────┤   │
│ Álbum    │  │  imagem grande       │  SLOT C              │   │
│ Lojinha  │  │  + título + resumo   │  (prioridade 2)      │   │
│ Impress. │  └──────────────────────┴──────────────────────┘   │
|
│          │  ZONA NOTÍCIAS PASSADAS (lista, paginada)          │
└──────────┴────────────────────────────────────────────────────┘
```

- **Banner superior:** logo/nome da residência, botão que abre o menu lateral e links de autenticação (Entrar/Sair) — nunca linkado ao admin.
- **Menu lateral:** botão com `ON_CLICK` abre a gaveta. 
- No menu, a opção da página atual abre um **dropdown** com os pontos especiais da página ou sub-páginas (páginas filhas).
- **Zona de destaques:** grid de **3 quadrados** (1 grande + 2 retângulos), preenchidos conforme §5.
- **Zona de notícias passadas:** lista das demais notícias, ordenada por prioridade e data, com paginação (25 por página) e link "ver todas".

## 5. Regras de seleção dos destaques

| Slot | Regra | Fallback (se não houver) |
|---|---|---|
| **A — maior quadrado** | Notícia marcada como **importante** (`importante=True`) | Notícia de prioridade 1 mais recente; se nenhuma, a mais recente da categoria em foco |
| **B — topo à direita** | **Prioridade 1**, mais recente primeiro | Notícia mais recente (qualquer prioridade) |
| **C — abaixo do quadrado grande** | **Prioridade 2** | Próxima disponível na ordenação geral, excluindo A e B |

- **Existe no máximo uma notícia "importante" ativa.** Ao publicar uma nova com `importante=True`, a anterior é **desmarcada automaticamente** (na mesma transação).
- A **categoria em foco** é a escolhida pelo jornalista para a home (padrão: `destaque`); o slot A respeita essa categoria.

## 6. Ordenação e consultas

**Regra de ordenação canônica:**

```sql
ORDER BY prioridade ASC, data_publicacao DESC, id DESC
```

- `prioridade`: inteiro onde **1 = maior prioridade** (nível 1) e valores maiores = menor prioridade (`Pmin` é o piso).
- O **default de inserção é `prioridade = 1` com `data_publicacao = now()`** — a notícia nasce no topo do slot B sem ajuste manual, porque a ordenação é por prioridade e, dentro do nível, por data mais recente.
- **Nota de interpretação:** o texto-fonte em `../arquivados/Site_Residencia_spec.md` diz "ordem decrescente da maior prioridade 1 para a menor Pmin" e ao mesmo tempo "por padrão é adicionada como nível 1… adicionada como último". A ambiguidade foi resolvida assim: **1 = maior prioridade** (ordem crescente do número) e a ordenação interna do nível é por **data mais recente primeiro**; "adicionada como último" = a notícia é a mais recente do banco e, por isso, fica no topo. Qualquer mudança nesse critério precisa atualizar este trecho.

**Consultas da home (Django ORM):**

```python
qs = (Noticia.objects
      .filter(ativo=True)
      .select_related('autor')
      .order_by('prioridade', '-data_publicacao', '-id'))

destaque = qs.filter(importante=True, categoria=categoria_em_foco).first()
usados = [destaque.pk] if destaque else []

nivel1 = qs.exclude(pk__in=usados).filter(prioridade=1).first() \
         or qs.exclude(pk__in=usados).first()
usados.append(nivel1.pk)

nivel2 = qs.exclude(pk__in=usados).filter(prioridade=2).first() \
         or qs.exclude(pk__in=usados).first()

passadas = qs.exclude(pk__in=usados)[:25]
```

## 7. Modelo de dados — `Noticia`

```python
class Noticia(models.Model):
    CATEGORIAS = [
        ('destaque', 'Destaques'),
        ('evento',   'Eventos da residência'),
        ('dia_a_dia','Dia a dia'),
        ('ru',       'Informes do RU'),
        ('bolsa',    'Bolsas e auxílios'),
        ('regras',   'Regras, costumes e lazer'),
    ]

    titulo      = models.CharField('Título', max_length=200)
    resumo      = models.CharField('Resumo', max_length=300, blank=True)
    conteudo    = models.TextField('Conteúdo')
    categoria   = models.CharField(max_length=20, choices=CATEGORIAS, default='destaque')
    prioridade  = models.PositiveSmallIntegerField('Prioridade', default=1)  # 1 = maior
    importante  = models.BooleanField('Importante (destaque)', default=False)
    imagem      = models.ImageField(upload_to='noticias/', blank=True, null=True)
    autor       = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='noticias')
    data_publicacao = models.DateTimeField('Publicação', default=timezone.now)
    ativo       = models.BooleanField('Publicada', default=True)

    class Meta:
        ordering = ['prioridade', '-data_publicacao', '-id']
        constraints = [
            # Salvaguarda no banco: no máximo uma notícia "importante" ativa.
            models.UniqueConstraint(fields=['importante'], condition=models.Q(importante=True),
                                    name='unica_noticia_importante'),
        ]
```

**Regras de escrita (no `ModelForm`/admin, dentro de `transaction.atomic`):**

1. Se `importante=True` → `Noticia.objects.filter(importante=True).exclude(pk=instancia.pk).update(importante=False)` **antes** de salvar (a constraint do banco é a rede de segurança).
2. `data_publicacao` pode ser ajustada pelo jornalista para reposicionar a notícia na ordenação.
3. `ativo=False` oculta a notícia da home e da listagem (não apaga — mantém histórico).
4. `resumo` é o texto da linha fina nos cards; se vazio, gerar dos primeiros ~160 caracteres do `conteudo`.

**Autor:** o morador é o `Perfil` já existente (OneToOne → `User`) — **não criar uma tabela `moradores` paralela** (ver `contexto.md` §10 e §12).

## 8. Publicação pelo jornalista (Django Admin)

- Criar o **grupo Django `jornalistas`** com as permissões `add/change/delete/view` de `Noticia`. Usuários do grupo entram em `/admin/` e **só** veem o modelo `Noticia` (limitar com `has_module_permission`/`get_queryset` no `NoticiaAdmin`).
- Formulário de edição: título, resumo, conteúdo, categoria, prioridade, **importante** (checkbox), imagem, data de publicação, publicado (ativo).
- Listagem do admin ordenada por `prioridade, -data_publicacao`, com `list_editable` para prioridade/importante (ajuste rápido de lineup).
- Toda publicação/edição fica registrada no `LogEntry` do admin (auditoria).
- Enquanto o módulo de páginas-filhas não existir, **categorias = sub-páginas** do menu lateral.

## 9. Menu lateral (JS mínimo)

Regra geral em `contexto.md` §6: **JS é permitido, mas no mínimo possível.** O menu lateral (abrir/fechar) e o dropdown da página atual têm solução **sem JS**, então essa é a implementação padrão:

```html
<input type="checkbox" id="menu-toggle" class="sr-only" hidden>
<label for="menu-toggle" class="menu-btn" aria-label="Abrir menu">☰</label>
<nav class="menu-lateral" id="menu"> … </nav>
```

```css
#menu-toggle:checked ~ .menu-lateral { transform: translateX(0); }
```

- No mobile, a gaveta entra por cima do conteúdo (overlay) e o `label` serve de botão fechar.
- O dropdown da página atual: `<details>/<summary>` (HTML nativo) ou o mesmo truque do checkbox.

**Quando o CSS puro não bastar**, pode-se adicionar JS **mínimo e sem dependência** — apenas vanilla JS inline ou em um `static/js/` pequeno, para:

- fechar o menu ao clicar fora ou ao pressionar `Esc` (o truque do checkbox não faz isso);
- marcar o item de menu da página atual com estado "aberto";
- trap de foco (`focus`) dentro da gaveta, para acessibilidade de teclado.

Requisitos de qualquer JS adicionado aqui: **sem jQuery, sem framework, sem build**; o HTML deve continuar funcionando (menu e dropdown utilizáveis) **se o JS falhar ou for desativado** — o JS só *melhora*, nunca é o que faz a página funcionar.

> Antes de escrever JS, confirme se `<details>`, `<dialog>` ou CSS `:checked`/`:target` já resolvem. Se resolverem, não use JS.

## 10. Página de leitura — `/noticia/<int:pk>/`

- Título, imagem, categoria (com link para o filtro), data de publicação, autor (jornalista) e corpo do texto.
- Bloco "outras notícias" da mesma categoria (até 4, mesma ordenação canônica).
- Botões: "Voltar para as notícias" e "Compartilhar" (compartilhar = exibir o link; copiar para a área de transferência é opcional e seria JS mínimo).
- Notícia inativa ou inexistente → 404.

## 11. Responsividade (mobile-first)

| Breakpoint | Comportamento |
|---|---|
| < 768px | Banner compacto; menu lateral em overlay; **grid empilha** na ordem: destaque (A) → B → C → lista de passadas; imagens com `aspect-ratio` para não pular o layout |
| 768–1023px | Grid 2 colunas (A ocupa a largura toda) |
| ≥ 1024px | Grid 3 quadrados conforme §4 |

Regras: sem rolagem horizontal; alvos de toque ≥ 44px; imagens com `width`/`height` ou `aspect-ratio`; texto ≥ 16px.

## 12. Critérios de aceitação (v1)

- [ ] `/` abre **sem autenticação** e mostra banner, menu lateral, 3 destaques e a lista de notícias passadas.
- [ ] O slot A exibe a notícia marcada como importante; publicar outra importante **desmarca a anterior** (nunca duas ativas).
- [ ] O slot B é a de prioridade 1 mais recente; o slot C é a de prioridade 2; com menos de 2 notícias, os slots de fallback preenchem sem erro.
- [ ] A ordenação da lista respeita `prioridade` e, no mesmo nível, a data mais recente primeiro.
- [ ] `/noticia/<id>/` exibe a notícia completa; notícias inativas não aparecem nem abrem.
- [ ] Somente usuários do grupo `jornalistas` publicam/editam; ações ficam no `LogEntry` do admin.
- [ ] O menu lateral e o dropdown funcionam **sem JavaScript** (HTML/CSS puro), e qualquer JS opcional é apenas melhoria (a página funciona se o JS falhar).
- [ ] Layout sem rolagem horizontal no mobile; imagens com `alt` e `aspect-ratio`.
- [ ] Todas as strings em pt-br; nenhum texto em inglês visível ao usuário.
- [ ] `python manage.py test` passa e há testes cobrindo a seleção dos slots (A/B/C) e a exclusão mútua do "importante".

## 13. Mapa de arquivos (v1)

```
core/settings.py          → + MEDIA_URL, MEDIA_ROOT, (opcional) static/
core/urls.py              → include('noticias.urls') + static() para dev
noticias/__init__.py
noticias/apps.py
noticias/models.py        → Noticia (+ constraint conforme §7)
noticias/admin.py         → NoticiaAdmin, acesso restrito ao grupo 'jornalistas'
noticias/views.py         → inicial(), noticias(), noticia_detalhe()
noticias/urls.py
noticias/templates/noticias/inicial.html     → estende o base do site
noticias/templates/noticias/lista.html
noticias/templates/noticias/detalhe.html
noticias/migrations/0001_initial.py
static/impressoras/imagens/cabecalho_residencia.jpg   → já no lugar (a imagem saiu de imagens/ em 27/10/2026)
```

**Duas decisões de estrutura (ver `update_spec/andamento.spec.md`):** app novo `noticias` (recomendado) e `base.html` refatorado para base **do site** (não mais "do gerenciador de impressões"). Se a equipe preferir app único, tudo acima aplica com `controle/` no lugar de `noticias/`.

## 14. Integrações com os demais módulos

O escopo/status de cada módulo vive em `update_spec/andamento.spec.md`. Aqui só os **pontos de contato com esta página**:

| Módulo | Ponto de contato |
|---|---|
| **Impressora** | O **status** (funcionando / em manutenção) pode aparecer como aviso em destaque na home; o link fica no menu lateral. |
| **Transparência** (atas, avisos PROAE, regimento, documentos) | Nasce como **categoria de notícia** (`destaque`, `evento`, `dia_a_dia`, `ru`, `bolsa`, `regras`) e evolui para página filha própria no menu lateral. |
| **Lojinha / Álbum** | Entradas no menu lateral (§9); o álbum de fotos de um evento pode virar notícia com imagem. |
| **Visitantes / Espaços / Votações** | Sem integração no v1; apenas entradas futuras no menu lateral. |

## 15. Quando atualizar este spec

Este é o spec do **módulo/página de Notícias**; muda quando o módulo muda:

- entra/sai uma regra funcional ou técnica **desta página**;
- muda o modelo `Noticia`, as rotas **desta página** ou o layout;
- uma decisão pendente desta página é fechada.

**Não** atualize aqui mudanças de escopo global (módulos, prioridades, status do projeto) — elas são de `update_spec/andamento.spec.md`.

> ⚠️ **Obrigatório:** ao concluir (ou descartar) uma parte deste módulo, atualize `update_spec/andamento.spec.md` — status, próximo passo e registro de alterações.
> As regras completas estão em `update_spec/regras_atualizacao.md`.
