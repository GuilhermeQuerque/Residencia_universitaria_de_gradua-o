from pathlib import Path
from unittest.mock import patch

from django.test import SimpleTestCase

from controle.impressao import ErroImpressao, imprimir_arquivo


class ImpressaoServiceTests(SimpleTestCase):
    @patch('controle.impressao.obter_impressora_nome', return_value='')
    def test_sem_impressora_configurada(self, _mock_obter):
        with self.assertRaises(ErroImpressao):
            imprimir_arquivo(Path('/tmp/teste.pdf'))

    @patch('controle.impressao.obter_impressora_nome', return_value='MinhaImpressora')
    @patch('controle.impressao.shutil.which', return_value='/usr/bin/lp')
    @patch('controle.impressao.subprocess.run')
    def test_cups_sucesso(self, mock_run, _mock_which, _mock_obter):
        mock_run.return_value.returncode = 0
        imprimir_arquivo(Path('/tmp/teste.pdf'))
        mock_run.assert_called_once_with(
            ['lp', '-d', 'MinhaImpressora', '/tmp/teste.pdf'],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

    @patch('controle.impressao.obter_impressora_nome', return_value='MinhaImpressora')
    @patch('controle.impressao.shutil.which', return_value='/usr/bin/lp')
    @patch('controle.impressao.subprocess.run')
    def test_cups_falha(self, mock_run, _mock_which, _mock_obter):
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = 'impressora offline'
        with self.assertRaises(ErroImpressao) as ctx:
            imprimir_arquivo(Path('/tmp/teste.pdf'))
        self.assertIn('offline', str(ctx.exception))
