"""
segredos.py — Utilitário de leitura do SECRET_KEY encriptado do projeto.

Este módulo é a **ponte** entre o arquivo encriptado (`secrets/secret.key`)
e o Django. Ele é importado pelo `core/settings.py` e é o **único** lugar
do projeto que decripta o segredo.

A encriptação/decriptação em si vive em `segredos.py` (o script da raiz),
que é o gerador e a ferramenta de linha de comando. Este módulo é a versão
importável, sem efeitos colaterais de linha de comando.

Fluxo do `core/settings.py`:

    1. `DJANGO_SECRET_KEY` no ambiente        -> usa direto (produção).
    2. arquivo `secrets/secret.key` encriptado -> decripta aqui (dev).
    3. nenhum dos dois                        -> o Django não sobe.

> Regra: **nunca** há um segredo escrito no código. Se o passo 1 e o passo 2
> falharem, o projeto recusa a subir com um erro claro.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

# Caminho da raiz do projeto (a pasta que contém `manage.py`).
RAIZ = Path(__file__).resolve().parent.parent

# Caminho do script que sabe encriptar/decriptar.
CAMINHO_SCRIPT = RAIZ / 'segredos.py'

# Caminho do arquivo que guarda o segredo encriptado.
CAMINHO_ARQUIVO = RAIZ / 'secrets' / 'secret.key'


def _carregar_script():
    """Carrega o módulo `segredos.py` da raiz como `segredos`.

    O script é carregado por caminho (e não por `import segredos`) para não
    depender do `sys.path` nem conflitar com o pacote `secrets` da biblioteca
    padrão do Python.
    """
    if not CAMINHO_SCRIPT.exists():
        raise RuntimeError(
            f'O script de segredos não foi encontrado em "{CAMINHO_SCRIPT}".'
        )

    especificacao = importlib.util.spec_from_file_location(
        'segredos_ferramenta', CAMINHO_SCRIPT
    )
    if especificacao is None or especificacao.loader is None:
        raise RuntimeError(f'Não foi possível carregar "{CAMINHO_SCRIPT}".')

    modulo = importlib.util.module_from_spec(especificacao)
    sys.modules[especificacao.name] = modulo
    especificacao.loader.exec_module(modulo)
    return modulo


def decriptar_segredo() -> str | None:
    """Decripta o segredo guardado em `secrets/secret.key`.

    Devolve o texto claro, ou `None` se:
      - o arquivo não existir;
      - a frase-semente (`DJANGO_MASTER_KEY`) não estiver no ambiente;
      - a verificação de autenticação falhar (frase errada ou arquivo adulterado).

    Nunca levanta exceção por segredo ausente — quem chama decide o que
    fazer com a ausência (aqui: recusar subir o Django).
    """
    if not CAMINHO_ARQUIVO.exists():
        return None

    frase_semente = os.environ.get('DJANGO_MASTER_KEY')
    if not frase_semente:
        return None

    try:
        script = _carregar_script()
        token = CAMINHO_ARQUIVO.read_text(encoding='utf-8').strip()
        return script.decriptar(token, frase_semente)
    except (OSError, ValueError, RuntimeError):
        # Arquivo corrompido, frase errada, script quebrado: sem segredo.
        return None


def obter_secret_key() -> str | None:
    """Devolve o `SECRET_KEY` do projeto, ou `None` se não houver nenhum.

    Ordem de preferência:
      1. variável de ambiente `DJANGO_SECRET_KEY` (produção);
      2. arquivo encriptado `secrets/secret.key`, decriptado na hora
         (desenvolvimento).
    """
    do_ambiente = os.environ.get('DJANGO_SECRET_KEY')
    if do_ambiente:
        return do_ambiente
    return decriptar_segredo()
