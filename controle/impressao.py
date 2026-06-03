import platform
import shutil
import subprocess
from pathlib import Path

from django.conf import settings

EXTENSOES_IMPRESSAO = {'.pdf', '.txt', '.ps', '.png', '.jpg', '.jpeg'}


class ErroImpressao(Exception):
    """Falha ao enviar arquivo para a impressora configurada."""


def imprimir_arquivo(caminho: Path) -> None:
    nome_impressora = settings.IMPRESSORA_NOME
    if not nome_impressora:
        raise ErroImpressao(
            'Impressora nao configurada. Defina a variavel IMPRESSORA_NOME '
            '(nome exato do CUPS; use lpstat -p para listar).'
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
