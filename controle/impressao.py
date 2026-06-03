import platform
import shutil
import subprocess
from pathlib import Path

from django.conf import settings

EXTENSOES_IMPRESSAO = {'.pdf', '.txt', '.ps', '.png', '.jpg', '.jpeg'}


def listar_impressoras():
    try:
        resultado = subprocess.run(
            ['lpstat', '-p'],
            capture_output=True, text=True, timeout=10, check=False,
        )
        if resultado.returncode != 0:
            return []
        linhas = resultado.stdout.strip().splitlines()
        impressoras = []
        for linha in linhas:
            if linha.startswith('printer ') or linha.startswith('impressora '):
                partes = linha.split()
                if len(partes) >= 2:
                    nome = partes[1]
                    if nome not in impressoras:
                        impressoras.append(nome)
        return impressoras
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def obter_impressora_nome():
    from .models import ImpressoraConfig
    config = ImpressoraConfig.objects.first()
    if config and config.nome:
        return config.nome
    return settings.IMPRESSORA_NOME


def contar_paginas(caminho: Path) -> int:
    ext = caminho.suffix.lower()
    if ext == '.pdf':
        try:
            from pypdf import PdfReader
            reader = PdfReader(caminho)
            return len(reader.pages)
        except Exception as exc:
            raise ErroImpressao(
                f'Nao foi possivel ler o numero de paginas do PDF. Detalhe: {exc}'
            )
    return 1


class ErroImpressao(Exception):
    """Falha ao enviar arquivo para a impressora configurada."""


def imprimir_arquivo(caminho: Path) -> None:
    nome_impressora = obter_impressora_nome()
    if not nome_impressora:
        raise ErroImpressao(
            'Impressora nao configurada. Um administrador deve selecionar uma '
            'impressora em Administracao > Impressoras.'
        )

    if platform.system() == 'Windows':
        _imprimir_windows(caminho, nome_impressora)
    else:
        _imprimir_cups(caminho, nome_impressora)


def _imprimir_cups(caminho: Path, nome_impressora: str) -> None:
    if not shutil.which('lp'):
        raise ErroImpressao('Comando lp (CUPS) nao encontrado neste sistema.')

    resultado = subprocess.run(
        ['lp', '-d', nome_impressora, str(caminho)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if resultado.returncode != 0:
        detalhe = (resultado.stderr or resultado.stdout or '').strip()
        raise ErroImpressao(
            f'CUPS nao aceitou o job na impressora "{nome_impressora}": '
            f'{detalhe or "erro desconhecido"}'
        )


def _imprimir_windows(caminho: Path, nome_impressora: str) -> None:
    # Comando nativo; funciona melhor com texto. PDF pode exigir driver/app extra.
    resultado = subprocess.run(
        ['print', f'/D:{nome_impressora}', str(caminho)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        shell=True,
    )
    if resultado.returncode != 0:
        detalhe = (resultado.stderr or resultado.stdout or '').strip()
        raise ErroImpressao(
            f'Windows nao enviou o job para "{nome_impressora}": '
            f'{detalhe or "erro desconhecido"}'
        )
