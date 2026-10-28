# producao.spec.md — Spec de produção: rodar o site 24/7 no servidor

> **Escopo deste arquivo:** como o site da Residência Universitária fica **rodando no servidor `servidor_residencia`**, de forma confiável, segura e 24/7.
>
> **Status (28/10/2026):** o ambiente está **preparado** — Python, Django, banco e dependências instalados e validados. A **publicação em si ainda não foi feita**: este spec é o roteiro para fazê-la.
>
> **Contexto geral** (stack, regras, RBAC, rotas) está em **`contexto.md`** — leia antes. **Organização de arquivos:** `organizacao.spec.md`. **Roadmap:** `update_spec/andamento.spec.md`.
>
> **Última atualização:** 28/10/2026

---

## 1. Objetivo e escopo

O site precisa:

- responder **24/7**, sem depender de alguém logado;
- **sobreviver a reinício** do servidor (falta de energia, update de kernel);
- **reiniciar sozinho** se o processo morrer;
- não expor o Django de desenvolvimento (`runserver`) na internet;
- servir **HTTPS** com cookies e HSTS de produção;
- ter **log** para diagnosticar problema;
- ter **backup** do banco.

**Fora do escopo:** o conteúdo do site (módulos, páginas) — cada um tem spec em `specs/`. Aqui só a **operação**.

---

## 2. Decisões (por quê)

| # | Decisão | Por quê |
|---|---|---|
| 1 | **systemd** (não supervisor, não Docker) | O servidor já é systemd (Fedora 44, systemd 259). Integration nativa: restart automático, boot, logs no `journalctl`, `Restart=always` sem gambiarra. |
| 2 | **gunicorn** (não `runserver`) | `runserver` é **para desenvolvimento**: não gerencia concorrência, não é seguro, avisa no startup. `gunicorn` é o servidor WSGI de produção, maduro e leve. |
| 3 | **systemd em vez do container** | Sem dependência de Docker/Podman no servidor; menos uma camada para manter. O site é Django puro — não precisa de isolamento de container. |
| 4 | **usuário `residencia`** (não root) | O serviço **não deve** rodar como root. `residencia` (uid 1000) é o dono do projeto. |
| 5 | **Nginx como proxy reverso** | TLS, HTTP/2, cache estático e `client_max_body_size` (upload de PDF) ficam fora do Python. `gunicorn` fica em `127.0.0.1:8000`, **sem porta pública**. |
| 6 | **certbot** para o certificado | Let's Encrypt automatiza a emissão e a renovação. O `contexto.md` §4 lista "HTTPS/domínio do servidor" como pendência. |
| 7 | **SQLite em produção** | Decisão de 28/10/2026 — ver `contexto.md` §2.1. Sem servidor de banco para manter. |
| 8 | **`.env` lido pelo serviço, não versionado** | O `SECRET_KEY` nunca entra no git (`organizacao.spec.md` §4.9). O systemd lê o `.env` na inicialização. |

> ⚠️ **Dependências novas desta publicação** (regra do `contexto.md` §6.1 — instalar só com o programador decidindo): `gunicorn` (lib Python), `nginx` e `certbot` (pacotes do sistema). **Ver §11 — a lista de aprovação.**

---

## 3. Arquitetura

```
                    Internet
                       │
                  :443 (HTTPS)
                       │
        ┌──────────────▼──────────────┐
        │   nginx                     │  ← TLS (certbot), HTTP/2,
        │   (systemd: nginx)          │    arquivos estáticos, upload
        └──────────────┬──────────────┘
                       │ 127.0.0.1:8000
        ┌──────────────▼──────────────┐
        │   gunicorn                  │  ← Django (WSGI)
        │   (systemd: residencia-site)│    3 workers
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼──────────────┐
        │   SQLite (WAL)              │  ← db.sqlite3
        │   db.sqlite3                │
        └─────────────────────────────┘
```

**Serviços systemd:**

| Unidade | Usuário | Porta | Função |
|---|---|---|---|
| `residencia-site.service` | `residencia` | `127.0.0.1:8000` | Django via gunicorn |
| `nginx.service` | root | `:443`, `:80` | TLS + proxy + estáticos |

**Fluxo de uma requisição:** nginx → gunicorn → Django → SQLite → resposta.

---

## 4. Pré-requisitos (todos verificados em 28/10/2026)

| Item | Estado | Verificação |
|---|---|---|
| Python no servidor | ✅ 3.14.3 | `/usr/bin/python3` |
| `venv` do projeto | ✅ funcional | `/home/residencia/PROJETO_SITE/venv/` |
| Django | ✅ 6.0.5 | `venv/bin/python -c "import django"` |
| `pypdf` | ✅ 6.21.4 | `venv/bin/python -c "import pypdf"` |
| `requirements.txt` | ✅ versionado | `pip install -r requirements.txt` |
| Banco (SQLite + WAL) | ✅ criado | `manage.py migrate` |
| `SECRET_KEY` | ✅ no `.env` | `manage.py check --deploy` sem avisos |
| `manage.py check --deploy` | ✅ 0 avisos | com `DJANGO_DEBUG=False` |
| `manage.py test` | ✅ 3 testes OK | |
| systemd | ✅ 259 | Fedora 44 |
| firewalld | ✅ ativo | padrão `FedoraServer` |
| SELinux | ⚠️ `Enforcing` | ver §8.2 |
| Usuário `residencia` | ✅ uid 1000 | dono do projeto |
| `gunicorn` | ❌ **falta instalar** | §5.1 |
| `nginx` | ❌ **falta instalar** | §5.2 |
| `certbot` | ❌ **falta instalar** | §5.4 |
| `git` | ✅ 2.56.0 | instalado em 28/10/2026 |

---

## 5. Instalação das dependências

### 5.1 `gunicorn` (lib Python — dentro do `venv`)

```bash
/home/residencia/PROJETO_SITE/venv/bin/pip install gunicorn
```

Depois, **atualizar o `requirements.txt`** (o `gunicorn` passa a ser dependência do projeto):

```bash
cd /home/residencia/PROJETO_SITE
venv/bin/pip freeze > /tmp/freeze.txt
```

E acrescentar ao `requirements.txt`:

```
gunicorn==<versão instalada>
```

> O `requirements.txt` é a fonte da verdade (`organizacao.spec.md` §4.8). Não versionar o `gunicorn` lá deixa o servidor irreprodutível.

### 5.2 `nginx` (pacote do sistema)

```bash
dnf install -y nginx
systemctl enable --now nginx
```

### 5.3 `gunicorn` — testar antes de serviço

```bash
cd /home/residencia/PROJETO_SITE
set -a; . ./.env; set +a
venv/bin/gunicorn core.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -
```

Testar em outra aba: `curl -I http://127.0.0.1:8000/`.

> ⚠️ **`--timeout 60`**: o upload de PDF para a impressora pode demorar. O padrão do gunicorn (30 s) mataria a requisição no meio.

### 5.4 `certbot` (pacote do sistema)

```bash
dnf install -y certbot python3-certbot-nginx
```

O certificado **só pode ser emitido com o domínio apontando para o servidor** (§6.4).

---

## 6. Configuração do nginx

### 6.1 Arquivo de site

`/etc/nginx/conf.d/residencia.conf`:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name residencia.ufrn.edu.br;   # AJUSTAR ao domínio real

    # Antes de ter certificado, este é o único caminho para o site.
    # Depois de emitir o certificado, o certbot reescreve este bloco.
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Upload de PDF (impressora): sem isso, o nginx barra acima de 1 MB.
        client_max_body_size 20M;

        # Upload lento não pode ser cortado pelo proxy.
        proxy_read_timeout 120s;
        proxy_send_timeout 120s;
    }

    # Estáticos servidos direto pelo nginx (não passa pelo Django).
    # `staticfiles/` é o que o `collectstatic` gera (ver §7.4).
    location /static/ {
        alias /home/residencia/PROJETO_SITE/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /home/residencia/PROJETO_SITE/media/;
        expires 7d;
    }
}
```

> ⚠️ **Os `location /static/` e `/media/` só funcionam depois de `collectstatic`** (§7.3). Sem isso, o Django serve os arquivos — funciona, mas mais devagar.

### 6.2 Desligar o site default

O `nginx` do Fedora traz um `default.conf` que ocupa a porta 80 e **mascaria** o site:

```bash
rm -f /etc/nginx/conf.d/default.conf
nginx -t && systemctl reload nginx
```

### 6.3 Testar

```bash
nginx -t                 # sintaxe
curl -I http://127.0.0.1/   # deve responder o Django
```

### 6.4 HTTPS com `certbot`

**Pré-requisito:** o domínio tem que apontar para o IP do servidor (`10.2.184.170`) e a porta 80 tem que estar acessível de fora.

```bash
# 1. Liberar a porta 80 no firewalld
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

# 2. Emitir o certificado
certbot --nginx -d residencia.ufrn.edu.br

# 3. Testar a renovação automática
certbot renew --dry-run
```

O `certbot` instala um **timer systemd** (`certbot-renew.timer`) que renova o certificado sozinho. Verificar:

```bash
systemctl list-timers | grep certbot
systemctl status certbot-renew.timer
```

> ⚠️ **Sem domínio público**, não há como emitir certificado. Nesse caso, o site roda **só em HTTP** ou por **IP com certificado self-signed** (§6.5) — e `check --deploy` vai reclamar do SSL. Decidir o domínio é **próximo passo do programador** (`update_spec/andamento.spec.md` §4).

### 6.5 Alternativa: certificado self-signed (sem domínio)

```bash
openssl req -x509 -newkey rsa:4096 -nodes -days 3650 \
  -keyout /etc/nginx/ssl/residencia.key \
  -out /etc/nginx/ssl/residencia.crt \
  -subj "/CN=10.2.184.170"
```

No `server` do nginx, dentro do `server { listen 443 ssl; ... }`:

```nginx
    ssl_certificate     /etc/nginx/ssl/residencia.crt;
    ssl_certificate_key /etc/nginx/ssl/residencia.key;
```

> O navegador vai avisar que o certificado não é confiável. Serve para uso interno; **não** é o ideal para o site real.

---

## 7. A unidade systemd do site

### 7.1 Arquivo

`/etc/systemd/system/residencia-site.service`:

```ini
[Unit]
Description=Site da Residência Universitária UFRN (Django + gunicorn)
After=network-online.target
Wants=network-online.target

[Service]
Type=notify
User=residencia
Group=residencia
WorkingDirectory=/home/residencia/PROJETO_SITE

# Carrega o .env (SECRET_KEY, DEBUG, ALLOWED_HOSTS...)
EnvironmentFile=/home/residencia/PROJETO_SITE/.env

# Segurança: DJANGO_SETTINGS_MODULE e o caminho do Python do venv.
Environment=DJANGO_SETTINGS_MODULE=core.settings
Environment=PATH=/home/residencia/PROJETO_SITE/venv/bin:/usr/local/bin:/usr/bin:/bin

ExecStart=/home/residencia/PROJETO_SITE/venv/bin/gunicorn core.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 3 \
    --timeout 60 \
    --access-logfile /home/residencia/PROJETO_SITE/logs/access.log \
    --error-logfile /home/residencia/PROJETO_SITE/logs/error.log \
    --capture-output

Restart=always
RestartSec=5

# --- Segurança (o serviço não precisa de nada disso) ---
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only
ReadWritePaths=/home/residencia/PROJETO_SITE/logs /home/residencia/PROJETO_SITE/media

[Install]
WantedBy=multi-user.target
```

### 7.2 Detalhes que importam

| Opção | Por quê |
|---|---|
| `EnvironmentFile=` | Carrega o `.env` **sem o shell interpretá-lo**. É o jeito systemd de ler o arquivo — o `SECRET_KEY` tem que chegar íntegro. |
| `User=residencia` | O serviço não roda como root. |
| `Type=notify` | O systemd sabe quando o gunicorn está pronto (e não quando só iniciou). |
| `Restart=always` | Volta sozinho se morrer. Junto com `RestartSec=5`, evita loop de reinício. |
| `WantedBy=multi-user.target` | Sobe sozinho no boot do servidor. |
| `ProtectSystem=full` | O processo não escreve fora de `logs/` e `media/`. |
| `NoNewPrivileges` | Não consegue ganhar privilégio. |
| `--capture-output` | Manda o stdout/stderr do gunicorn para os arquivos de log. |
| `logs/` no `ReadWritePaths` | Sem isso, o `ProtectSystem` bloqueia a escrita do log. |

> ⚠️ **`ProtectHome=read-only` + `ReadWritePaths`**: o `ProtectHome=read-only` deixa o `/home` legível, mas não gravável. Os `ReadWritePaths` reabrem **só** `logs/` e `media/`. Se o SQLite precisar escrever, ele está na raiz do projeto —ver §8.3.

### 7.3 Criar a pasta de log

```bash
mkdir -p /home/residencia/PROJETO_SITE/logs
chown residencia:residencia /home/residencia/PROJETO_SITE/logs
```

### 7.4 `collectstatic`

```bash
cd /home/residencia/PROJETO_SITE
set -a; . ./.env; set +a
venv/bin/python manage.py collectstatic --noinput
```

Isso cria `staticfiles/` (já no `.gitignore` — `organizacao.spec.md` §8).

### 7.5 Ativar

```bash
systemctl daemon-reload
systemctl enable --now residencia-site.service
systemctl status residencia-site.service
```

### 7.6 Verificar

```bash
curl -I http://127.0.0.1:8000/        # gunicorn direto
curl -I http://127.0.0.1/             # via nginx
ss -tlnp | grep 8000                  # escutando em 127.0.0.1 (não público)
```

---

## 8. Segurança

### 8.1 O que já está resolvido

| Item | Como |
|---|---|
| `SECRET_KEY` fora do código | `core/segredos.py` + `.env` (`contexto.md` §9) |
| `DEBUG=False` | `.env` → `DJANGO_DEBUG=False` |
| `ALLOWED_HOSTS` | `.env` → `DJANGO_ALLOWED_HOSTS=...` |
| HTTPS/cookies/HSTS | Ligados sozinhos quando `DEBUG=False` (`core/settings.py`) |
| `X-Frame-Options`, `nosniff` | Ligados no settings |
| `gunicorn` fora da internet | Escuta em `127.0.0.1:8000`; só o nginx escuta em `:443` |
| Serviço sem root | `User=residencia` |

### 8.2 SELinux (está em `Enforcing`)

O nginx em modo `Enforcing` precisa de uma permissão para **conectar** ao gunicorn:

```bash
# O nginx precisa poder se conectar a um socket unix/tcp do outro usuario.
setsebool -P httpd_can_network_connect 1
```

Verificar:

```bash
getsebool httpd_can_network_connect
```

> ⚠️ **Sem isso**, o nginx responde **502 Bad Gateway** mesmo com o gunicorn funcionando — o erro aparece no `journalctl -u nginx`, não no navegador.

### 8.3 O SQLite precisa ser gravável pelo serviço

O `ProtectSystem=full` bloqueia escrita fora das pastas liberadas. Se o banco ficar na raiz do projeto, acrescentar:

```ini
ReadWritePaths=/home/residencia/PROJETO_SITE/logs /home/residencia/PROJETO_SITE/media /home/residencia/PROJETO_SITE/db.sqlite3
```

> Em SQLite (WAL), também são criados `db.sqlite3-wal` e `db.sqlite3-shm` — **no mesmo diretório**. O `ReadWritePaths` do arquivo pode não cobrir arquivos novos; se der erro de permissão, colocar o banco numa subpasta dedicada (`var/`) e liberar a pasta.

### 8.4 Permissões do `.env`

```bash
chmod 600 /home/residencia/PROJETO_SITE/.env
chown residencia:residencia /home/residencia/PROJETO_SITE/.env
```

### 8.5 Firewall

```bash
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
firewall-cmd --list-all
```

**Só 80 e 443.** A porta 8000 **não** se abre — o gunicorn não é público.

### 8.6 Conta do superuser

```bash
cd /home/residencia/PROJETO_SITE
set -a; . ./.env; set +a
venv/bin/python manage.py createsuperuser
```

> ⚠️ O `db.sqlite3` que estava no histórico do git tinha um superuser `SUPERUSER-OMITIDO` com senha fraca. **Não repita esse erro**: senha forte, e não use e-mail real.

---

## 9. Operação diária

### 9.1 Comandos

```bash
# Estado
systemctl status residencia-site.service
systemctl status nginx

# Logs
journalctl -u residencia-site.service -f          # acompanha
journalctl -u residencia-site.service -n 100     # últimas 100 linhas
tail -f /home/residencia/PROJETO_SITE/logs/error.log

# Reiniciar
systemctl restart residencia-site.service

# Recarregar o nginx (após editar a config)
nginx -t && systemctl reload nginx
```

### 9.2 Publicar uma mudança

```bash
# 1. No computador do programador
cd /home/guizo/servidor_residencia/residencia/PROJETO_SITE
./push.sh "mensagem"

# 2. No servidor
cd /home/residencia/PROJETO_SITE
git pull origin main
set -a; . ./.env; set +a
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput
systemctl restart residencia-site.service
```

> ⚠️ **`git pull` no servidor** — o servidor **não tem credencial** do GitHub (28/10/2026). O `git pull` só funciona se a chave SSH do servidor for autorizada no GitHub, **ou** se o programador copiar os arquivos. Decidir o fluxo é **próximo passo** (`update_spec/andamento.spec.md` §4).

### 9.3 Backup do banco

O banco é **um arquivo** (`organizacao.spec.md` §4.8). O backup é copiar — mas copiar enquanto o site grava pode capturar um arquivo pela metade. Use o backup do SQLite, que é seguro com o site no ar:

```bash
# Backup consistente, mesmo com o site rodando
/home/residencia/PROJETO_SITE/venv/bin/python - <<'EOF'
import sqlite3
src = sqlite3.connect('/home/residencia/PROJETO_SITE/db.sqlite3')
dst = sqlite3.connect('/root/backup-db/residencia-$(date +%Y%m%d-%H%M%S).sqlite3')
src.backup(dst)
dst.close(); src.close()
print('backup ok')
EOF
```

Agendar (cron diário, às 3h):

```bash
cat > /etc/cron.d/backup-residencia <<'EOF'
0 3 * * * root /usr/local/bin/backup-residencia.sh
EOF
```

> O `backup` do SQLite **não** trava o site. **Não** use `cp` direto no `db.sqlite3` enquanto o site grava — pode sair um banco corrompido.

### 9.4 O que fazer se der problema

| Sintoma | Provável causa | O que fazer |
|---|---|---|
| **502 Bad Gateway** | nginx não conecta no gunicorn | `systemctl status residencia-site.service`; se o gunicorn está up, é SELinux (§8.2) |
| **Site não abre** | nginx parado | `systemctl status nginx`; `journalctl -u nginx -n 50` |
| **Site abre mas sem CSS** | `collectstatic` não rodou | `manage.py collectstatic --noinput` (§7.4) |
| **Erro 500 no admin** | `SECRET_KEY` ausente/errado | conferir o `.env`; `journalctl -u residencia-site.service` |
| **Erro de banco (readonly)** | permissão do SQLite | §8.3 |
| **Certificado expirado** | renovação falhou | `certbot renew --dry-run`; ver timer (§6.4) |
| **Serviço reiniciando em loop** | erro no `ExecStart` | `journalctl -u residencia-site.service -n 50` |

### 9.5 Atualizar o servidor

```bash
dnf update -y
systemctl daemon-reload
systemctl restart residencia-site.service
```

> Um `dnf update` pode trocar a versão do Python. O `venv` é do sistema — se o Python mudar de versão, o `venv` precisa ser refeito (§12).

---

## 10. Checklist de publicação

```bash
# 1. Dependências
/home/residencia/PROJETO_SITE/venv/bin/pip install gunicorn
# (e atualizar o requirements.txt no computador)

# 2. Pastas e permissões
mkdir -p /home/residencia/PROJETO_SITE/logs
chown -R residencia:residencia /home/residencia/PROJETO_SITE/logs

# 3. .env de produção
#    DJANGO_SECRET_KEY=<valor real>
#    DJANGO_DEBUG=False
#    DJANGO_ALLOWED_HOSTS=<dominio>,<ip>
#    DJANGO_MASTER_KEY=<frase-semente, se usar o arquivo encriptado>
chmod 600 /home/residencia/PROJETO_SITE/.env

# 4. Validação do Django
cd /home/residencia/PROJETO_SITE
set -a; . ./.env; set +a
venv/bin/python manage.py check --deploy     # tem que dar 0 avisos
venv/bin/python manage.py migrate
venv/bin/python manage.py collectstatic --noinput
venv/bin/python manage.py createsuperuser

# 5. nginx
dnf install -y nginx certbot python3-certbot-nginx
rm -f /etc/nginx/conf.d/default.conf
# (criar /etc/nginx/conf.d/residencia.conf — §6.1)
nginx -t && systemctl enable --now nginx

# 6. systemd
# (criar /etc/systemd/system/residencia-site.service — §7.1)
systemctl daemon-reload
systemctl enable --now residencia-site.service

# 7. SELinux
setsebool -P httpd_can_network_connect 1

# 8. Firewall
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload

# 9. Certificado
certbot --nginx -d <dominio>
certbot renew --dry-run

# 10. Teste final
curl -I http://127.0.0.1:8000/
curl -I http://127.0.0.1/
curl -I https://<dominio>/
ss -tlnp | grep -E ':8000|:443'    # 8000 só em 127.0.0.1
systemctl is-enabled residencia-site.service   # enabled
```

---

## 11. Dependências que precisam de aprovação

Regra do `contexto.md` §6.1: **dependência nova se decide antes, não depois.**

| Item | Tipo | Para quê | Aprovado? |
|---|---|---|---|
| `gunicorn` | lib Python (venv) | servidor WSGI de produção | ⬜ |
| `nginx` | pacote do sistema | proxy reverso + TLS | ⬜ |
| `certbot` + `python3-certbot-nginx` | pacote do sistema | certificado TLS | ⬜ |
| `python3-certbot-nginx` | pacote do sistema | plugin do certbot | ⬜ |

**Antes de instalar**, confirmar com o programador. A alternativa sem nenhuma dependência nova seria rodar o `runserver` do Django direto na porta 80 — **não recomendado** (é servidor de desenvolvimento).

---

## 12. Decisões em aberto (o programador precisa decidir)

| # | Questão | Por que precisa de decisão |
|---|---|---|
| 1 | **Domínio** — vai ser `residencia.ufrn.edu.br`? | Sem domínio não há certificado TLS. `update_spec/andamento.spec.md` §4 lista "HTTPS/domínio do servidor" como pendência. |
| 2 | **Fluxo do `git pull`** — chave SSH no servidor ou cópia manual? | O servidor não tem credencial do GitHub. |
| 3 | **IP público vs. rede interna** — o site é acessível de fora da rede da residência? | Muda o firewall, o certificado e a exposição de dados (LGPD). |
| 4 | **Log em arquivo ou só no journal?** | Arquivo ocupa espaço; precisa de rotação (`logrotate`). |
| 5 | **Frequência do backup** e **onde fica a cópia?** | O backup do §9.3 fica no mesmo servidor — não protege contra perda do disco. |
| 6 | **`gunicorn` com `--workers 3`?** | Quantidade de CPU do servidor — ainda não medido. |

---

## 13. Referências

| Documento | O que diz |
|---|---|
| `contexto.md` §2.1 | Banco SQLite em produção (decisão e limites) |
| `contexto.md` §8 | Ambiente e comandos |
| `contexto.md` §9 | `SECRET_KEY`, `segredos.py` e o `.env` |
| `contexto.md` §6.1 | Regra de libs extras (perguntar antes) |
| `organizacao.spec.md` §4.8 | `venv/`, `requirements.txt` e banco |
| `organizacao.spec.md` §4.9 | `secrets/` e o script de segredos |
| `update_spec/andamento.spec.md` §4 | Itens transversais (o que falta) |

---

## 14. Quando atualizar este spec

Atualize quando:

- o site for **publicado** de fato (mudar o status do topo);
- uma dependência da §11 for **aprovada ou recusada**;
- uma decisão da §12 for **fechada**;
- a **infraestrutura mudar** (trocar nginx, mudar de porta, o HTTPS ficar diferente);
- um problema recorrente aparecer e entrar na tabela §9.4.

> Mudança de **larga escala** neste spec também entra no log `update_spec/mod_spec.md` (ver `update_spec/regras_atualizacao.md` §3).
