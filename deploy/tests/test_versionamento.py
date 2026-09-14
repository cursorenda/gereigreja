"""Testes focados do versionamento do modulo deploy (D1).

Comprovam que obter_versao_atual() reconhece o formato canonico do
CHANGELOG.md ("# vX.Y.Z — DD/MM/AAAA") e tambem variantes historicas.
"""

import os
import tempfile
from unittest import mock

from django.test import SimpleTestCase

from deploy.views import obter_versao_atual


def _ler_versao_de(conteudo):
    """Executa obter_versao_atual() contra um CHANGELOG temporario."""
    with tempfile.TemporaryDirectory() as tmpdir:
        caminho = os.path.join(tmpdir, 'CHANGELOG.md')
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            arquivo.write(conteudo)

        with mock.patch('deploy.views.settings') as settings_mock:
            settings_mock.BASE_DIR = tmpdir
            return obter_versao_atual()


class ObterVersaoAtualTests(SimpleTestCase):
    """Parser de versao do CHANGELOG.md."""

    def test_formato_canonico_atual_um_cardinal(self):
        """Formato canonico vigente: '# v1.14.26 — 25/08/2026' -> '1.14.26'."""
        conteudo = (
            '# v1.14.26 — 25/08/2026\n'
            '\n'
            'Alguma descricao da release.\n'
            '\n'
            '# v1.14.25 — 12/08/2026\n'
        )
        self.assertEqual(_ler_versao_de(conteudo), '1.14.26')

    def test_formato_historico_dois_cardinais(self):
        """Variante historica: '## v1.0.9' -> '1.0.9'."""
        conteudo = '## v1.0.9 — 05/02/2026\n\n## v1.0.8 — 01/02/2026\n'
        self.assertEqual(_ler_versao_de(conteudo), '1.0.9')

    def test_retorna_primeira_versao_do_arquivo(self):
        """Deve retornar a versao mais recente (primeira ocorrencia)."""
        conteudo = (
            '# v2.0.0 — 01/01/2027\n'
            '# v1.99.99 — 31/12/2026\n'
        )
        self.assertEqual(_ler_versao_de(conteudo), '2.0.0')

    def test_ignora_titulo_sem_versao(self):
        """Linhas de titulo sem versao nao devem interromper a leitura."""
        conteudo = (
            '# Changelog do GereIgreja\n'
            '\n'
            'Este arquivo registra as versoes publicadas.\n'
            '\n'
            '# v1.14.26 — 25/08/2026\n'
        )
        self.assertEqual(_ler_versao_de(conteudo), '1.14.26')

    def test_ignora_mencoes_de_versao_no_corpo(self):
        """Mencoes de versao no corpo do texto nao devem ser capturadas."""
        conteudo = (
            '# v1.14.26 — 25/08/2026\n'
            '\n'
            'Corrige regressao introduzida na v1.14.20.\n'
            '## v1.14.25 — 12/08/2026\n'
        )
        self.assertEqual(_ler_versao_de(conteudo), '1.14.26')

    def test_arquivo_sem_versao_retorna_fallback(self):
        """Sem versao reconhecivel, mantem o fallback historico '1.0.0'."""
        conteudo = '# Changelog\n\nSem versoes registradas.\n'
        self.assertEqual(_ler_versao_de(conteudo), '1.0.0')

    def test_arquivo_inexistente_retorna_fallback(self):
        """Erro de leitura nao deve propagar excecao."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch('deploy.views.settings') as settings_mock:
                settings_mock.BASE_DIR = tmpdir
                self.assertEqual(obter_versao_atual(), '1.0.0')

    def test_changelog_real_do_projeto(self):
        """O CHANGELOG.md real do projeto deve ser reconhecido."""
        versao = obter_versao_atual()
        self.assertRegex(versao, r'^\d+\.\d+\.\d+$')
        self.assertNotEqual(versao, '1.0.0')