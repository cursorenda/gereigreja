from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from configuracao.models import Ministerio
from contas.constants import (
    ADMIN_MINISTERIO,
    MEMBRO_COMUM,
    PASTOR_LOCAL,
    _is_admin_ministerio_principal,
    user_tem_grupo,
    user_tem_qualquer_grupo,
)


User = get_user_model()


class AuthorizationInstanceCacheTests(TestCase):
    def _create_user(self, username):
        return User.objects.create_user(username=username, password='senha123')

    def test_admin_principal_repetido_mantem_resultado_e_consulta_uma_vez(self):
        user = self._create_user('admin-principal-cache')
        Ministerio.objects.create(
            nome_fantasia='Ministerio Cache Admin Principal',
            administrador_principal=user,
        )

        with CaptureQueriesContext(connection) as queries:
            self.assertTrue(_is_admin_ministerio_principal(user))
            self.assertTrue(_is_admin_ministerio_principal(user))

        self.assertEqual(len(queries), 1)

    def test_verificacoes_de_grupos_carregam_nomes_uma_vez(self):
        user = self._create_user('grupos-cache')
        pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        membro_comum, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
        user.groups.add(pastor_local, membro_comum)

        with CaptureQueriesContext(connection) as queries:
            self.assertTrue(user_tem_grupo(user, PASTOR_LOCAL))
            self.assertTrue(user_tem_qualquer_grupo(user, [MEMBRO_COMUM]))
            self.assertTrue(user_tem_qualquer_grupo(user, [PASTOR_LOCAL, MEMBRO_COMUM]))

        self.assertEqual(len(queries), 1)

    def test_instancias_de_usuarios_nao_compartilham_cache_de_grupos(self):
        user_a = self._create_user('usuario-a-cache')
        user_b = self._create_user('usuario-b-cache')
        pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        user_a.groups.add(pastor_local)

        self.assertTrue(user_tem_grupo(user_a, PASTOR_LOCAL))
        self.assertFalse(user_tem_grupo(user_b, PASTOR_LOCAL))

        self.assertEqual(user_a._gereigreja_group_names_cache, {PASTOR_LOCAL})
        self.assertEqual(user_b._gereigreja_group_names_cache, set())

    def test_usuario_sem_grupo_permanece_sem_acesso(self):
        user = self._create_user('sem-grupo-cache')

        self.assertFalse(user_tem_grupo(user, PASTOR_LOCAL))
        self.assertFalse(user_tem_qualquer_grupo(user, [PASTOR_LOCAL, MEMBRO_COMUM]))

    def test_nova_instancia_reconhece_grupo_adicionado_apos_cache_anterior(self):
        user = self._create_user('nova-instancia-cache')
        pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)

        self.assertFalse(user_tem_grupo(user, PASTOR_LOCAL))
        user.groups.add(pastor_local)

        fresh_user = User.objects.get(pk=user.pk)

        self.assertTrue(user_tem_grupo(fresh_user, PASTOR_LOCAL))

    def test_administrador_principal_e_reconhecido_sem_grupo_django(self):
        user = self._create_user('admin-principal-sem-grupo')
        Ministerio.objects.create(
            nome_fantasia='Ministerio Admin Principal Sem Grupo',
            administrador_principal=user,
        )

        self.assertTrue(user_tem_grupo(user, ADMIN_MINISTERIO))
        self.assertTrue(user_tem_qualquer_grupo(user, [PASTOR_LOCAL, ADMIN_MINISTERIO]))

    def test_usuario_comum_nao_vira_admin_ministerio(self):
        user = self._create_user('membro-comum-cache')
        membro_comum, _ = Group.objects.get_or_create(name=MEMBRO_COMUM)
        user.groups.add(membro_comum)

        self.assertFalse(_is_admin_ministerio_principal(user))
        self.assertFalse(user_tem_grupo(user, ADMIN_MINISTERIO))
        self.assertFalse(user_tem_qualquer_grupo(user, [ADMIN_MINISTERIO]))