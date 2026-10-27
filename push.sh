#!/usr/bin/env bash
#
# push.sh — commit e envia as alterações do projeto para o GitHub.
#
# Uso:
#   ./push.sh              # pede a mensagem, commita e faz o push
#   ./push.sh "mensagem"   # usa a mensagem dada, sem perguntar
#   ./push.sh --dry-run    # mostra o que seria commitado, sem commitar/push
#   ./push.sh --no-push    # commita localmente, sem enviar
#
set -euo pipefail

cd "$(dirname "$0")"

# --- Configuração -----------------------------------------------------------
REMOTE="${PUSH_REMOTE:-origin}"
BRANCH="${PUSH_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
DRY_RUN=0
DO_PUSH=1
MESSAGE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --no-push) DO_PUSH=0; shift ;;
    -m|--message) MESSAGE="${2:-}"; shift 2 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    -*) echo "Opção desconhecida: $1" >&2; exit 1 ;;
    *) MESSAGE="$1"; shift ;;
  esac
done

say() { printf '\033[1;34m==>\033[0m %s\n' "$1"; }
warn() { printf '\033[1;33mAVISO:\033[0m %s\n' "$1" >&2; }
err() { printf '\033[1;31mERRO:\033[0m %s\n' "$1" >&2; exit 1; }

# --- Verificações -----------------------------------------------------------
command -v git >/dev/null 2>&1 || err "git não encontrado."

git rev-parse --git-dir >/dev/null 2>&1 || err "isto não é um repositório git."

if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  err "remote '$REMOTE' não existe. Configure com: git remote add $REMOTE <url>"
fi

# Impede que arquivos sensíveis entrem no commit (o .gitignore cobre o futuro,
# mas arquivos já versionados podem continuar rastreados).
# Obs.: media/.gitkeep é a única coisa permitida dentro de media/ (pasta vazia
# não versiona no git). Ver organizacao.spec.md §4.6.
LEAKED=$(git ls-files | grep -E '(^|/)(db\.sqlite3|\.env)$|\.pyc$|__pycache__/|^venv/|^\.venv/|^media/' | grep -v '^media/\.gitkeep$' || true)
if [[ -n "$LEAKED" ]]; then
  err "Arquivos sensíveis ainda rastreados pelo git — remova-os antes de commitar:
$LEAKED
Use: git rm -r --cached <arquivo>"
fi

# Aviso (não bloqueia): segredo de verdade no conteúdo do diff.
if git diff --cached --no-color 2>/dev/null | grep -nE '^\+.*(SECRET_KEY *= *["'"'"'][^"'"'"']{20,}|api[_-]?key *= *["'"'"'][^"'"'"']{15,}|password *= *["'"'"'][^"'"'"']{8,})' >/dev/null 2>&1; then
  warn "O diff staged parece conter chave/segredo. Revise antes de commitar."
fi

# --- Coleta o que será commitado --------------------------------------------
if git diff --quiet && git diff --cached --quiet && [[ -z "$(git ls-files --others --exclude-standard)" ]]; then
  say "Nada a commitar — working tree limpa."
  exit 0
fi

say "Arquivos que serão commitados:"
git status --short | sed 's/^/    /'

if [[ $DRY_RUN -eq 1 ]]; then
  say "--dry-run: nada foi commitado nem enviado."
  exit 0
fi

# --- Commit -----------------------------------------------------------------
if [[ -z "$MESSAGE" ]]; then
  if ! git diff --quiet || ! git diff --cached --quiet; then
    say "Diff a ser commitado:"
    git diff --stat | sed 's/^/    /'
    git diff --cached --stat | sed 's/^/    /'
  fi
  printf '\nMensagem do commit: '
  read -r MESSAGE || err "mensagem vazia."
fi
[[ -n "${MESSAGE// }" ]] || err "mensagem do commit não pode ser vazia."

git add -A
git commit -m "$MESSAGE"

# --- Push -------------------------------------------------------------------
if [[ $DO_PUSH -eq 0 ]]; then
  say "Commit feito localmente (--no-push). Envie com: git push $REMOTE $BRANCH"
  exit 0
fi

say "Enviando para $REMOTE/$BRANCH ..."
if git push "$REMOTE" "$BRANCH"; then
  say "Push concluído: $(git rev-parse --short HEAD) -> $REMOTE/$BRANCH"
else
  err "Falha no push. Verifique a autenticação (token/credencial) e a rede."
fi
