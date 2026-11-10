from io import StringIO
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings

from core.templatetags.versao import get_versao_gereigreja


class FooterVersionTests(SimpleTestCase):
    @override_settings(DEBUG=False)
    def test_uses_first_release_heading_before_legacy_heading(self):
        changelog = '# v1.14.26 — 25/08/2026\n## v1.14.1 — 08/07/2026\n'
        with (
            patch('core.templatetags.versao._versao_cache', None),
            patch('core.templatetags.versao._data_cache', None),
            patch('core.templatetags.versao.open', return_value=StringIO(changelog)),
        ):
            self.assertEqual(get_versao_gereigreja(), 'v1.14.26 — 25/08/2026')
