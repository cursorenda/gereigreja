from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from configuracao.models import Ministerio, PerfilUsuario
from configuracao.templatetags.grupo_tags import resumo_atuacao_usuario
from contas.constants import ADMIN_MINISTERIO, MEMBRO_COMUM, PASTOR_LOCAL, TESOUREIRO


class ResumoAtuacaoUsuarioTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='usuario-atuacao')

    def _adicionar_grupos(self, *nomes):
        for nome in nomes:
            grupo, _ = Group.objects.get_or_create(name=nome)
            self.user.groups.add(grupo)

    def test_prioriza_atuacao_hierarquicamente_e_indica_adicionais(self):
        self._adicionar_grupos(PASTOR_LOCAL, TESOUREIRO, MEMBRO_COMUM)

        resumo = resumo_atuacao_usuario(self.user)

        self.assertEqual(resumo['principal'], 'Pastor Local')
        self.assertEqual(resumo['adicionais'], 1)
        self.assertEqual(resumo['titulo'], 'Atuações: Pastor Local, Tesoureiro Local')
        self.assertEqual(resumo['atuacoes'], ['Pastor Local', 'Tesoureiro Local'])

    def test_admin_sem_vinculo_de_presidencia_mantem_rotulo_administrativo(self):
        self._adicionar_grupos(ADMIN_MINISTERIO)

        resumo = resumo_atuacao_usuario(self.user)

        self.assertEqual(resumo['principal'], 'Administrador do Ministério')

    def test_admin_principal_recebe_rotulo_de_presidente(self):
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministério de Teste',
            administrador_principal=self.user,
        )
        PerfilUsuario.objects.create(user=self.user, ministerio=ministerio)
        self._adicionar_grupos(ADMIN_MINISTERIO)

        resumo = resumo_atuacao_usuario(self.user)

        self.assertEqual(resumo['principal'], 'Presidente do Ministério')
        self.assertEqual(resumo['atuacoes'], ['Presidente do Ministério'])
        self.assertNotIn('Pastor Local', resumo['atuacoes'])

    def test_usuario_sem_grupos_retorna_resumo_vazio(self):
        resumo = resumo_atuacao_usuario(self.user)

        self.assertEqual(
            resumo,
            {'principal': '', 'adicionais': 0, 'titulo': '', 'atuacoes': []},
        )
