# Gerenciador de Impressões

Sistema web para gerenciamento de impressões em residência universitária. Usuários autenticados fazem upload de arquivos, que são enviados para uma impressora CUPS com cobrança automática por página.

## Stack

- **Python 3.14** · **Django 6.0** · **SQLite**
- **pypdf** — leitura de páginas de PDF
- **CUPS** (`lp`) — envio para impressora (Linux/macOS); suporte a Windows via `print`

## Começando

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Criar banco
python manage.py migrate

# Criar admin
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/`.

## Configuração da impressora

| Variável           | Padrão             | Descrição                          |
|--------------------|--------------------|--------------------------------------|
| `IMPRESSORA_NOME`  | `impresora_padrão` | Fila CUPS para impressão            |
| `IMPRESSORA_IP`    | `10.1.168.164`     | Referência (não usado em runtime)   |

```bash
export IMPRESSORA_NOME=nome_da_fila
lpstat -p           # listar filas disponíveis
```

**Atenção**: filas `Samsung_M408x_*` apontam para `/dev/null` — não usar.

## Rotas

| Rota                          | Função              | Requer login |
|-------------------------------|----------------------|:------------:|
| `/`                           | Dashboard            | Sim          |
| `/login/`                     | Login                | Não          |
| `/logout/`                    | Logout               | Não          |
| `/registrar/`                 | Cadastro             | Não          |
| `/impressao/solicitar/`       | Solicitar impressão  | Sim          |
| `/recuperar/`                 | Recuperar senha (1)  | Não          |
| `/recuperar/confirmar/`       | Redefinir senha (2)  | Não          |
| `/admin/`                     | Administração Django | Staff        |

## Fluxo de impressão

1. Upload de arquivos (PDF, TXT, PS, PNG, JPG)
2. Contagem automática de páginas (`pypdf` para PDF; 1 para demais)
3. Envio via `lp -d <IMPRESSORA_NOME> <arquivo>` (timeout 120s)
4. Sucesso → `LogImpressao(status='ok')` + `Pagamento(R$ 0,50 × páginas)`
5. Falha → `LogImpressao(status='erro')`, sem cobrança

## Testes

```bash
python manage.py test controle
```

Usam `SimpleTestCase` + mocks — sem necessidade de banco ou impressora.

## Modelos

- **Perfil** — CPF e inscrição vinculados ao User (armazenados como hash PBKDF2)
- **Pagamento** — cobrança por impressão (`valor`, `data_pagamento`, `observacao`)
- **LogImpressao** — registro de cada job (`paginas`, `status`, `criado_em`, `descricao`)

## Notas

- `SECRET_KEY` e `DEBUG=True` são valores *dev* — alterar antes de publicar
- `ALLOWED_HOSTS` vazio — configurar para produção
- `EMAIL_BACKEND` usa console — sem envio real de email
- Arquivos de upload são temporários (não persistem em disco)
- Interface em português (pt-br), fuso `America/Sao_Paulo`
