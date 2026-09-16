from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import reverse

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL
from configuracao.models import Igreja, Ministerio, PerfilUsuario


class MenuDepartamentosTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.administrador = get_user_model().objects.create_user(username='admin-menu-departamentos')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Menu Departamentos',
            administrador_principal=self.administrador,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Menu Departamentos',
        )

    def _renderizar_menu(self, grupo=None):
        user = get_user_model().objects.create_user(username=f'usuario-menu-{grupo or "sem-grupo"}')
        perfil = PerfilUsuario.objects.create(user=user, ministerio=self.ministerio)
        perfil.igrejas_permitidas.add(self.igreja)
        if grupo:
            grupo_obj, _ = Group.objects.get_or_create(name=grupo)
            user.groups.add(grupo_obj)

        request = self.factory.get('/')
        SessionMiddleware(lambda request: None).process_request(request)
        request.user = user
        return render_to_string('menu.html', request=request)

    def test_exibe_gestao_local_somente_para_grupos_autorizados(self):
        url_local = f'href="{reverse("configuracao:gestao_departamentos")}"'

        for grupo in (ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL):
            with self.subTest(grupo=grupo):
                self.assertIn(url_local, self._renderizar_menu(grupo))

        self.assertNotIn(url_local, self._renderizar_menu())

    def test_perfis_locais_nao_ganham_acesso_a_gestao_ministerial(self):
        url_centro_ministerial = f'href="{reverse("configuracao:centro_ministerial")}"'

        for grupo in (PASTOR_LOCAL, SECRETARIO_LOCAL):
            with self.subTest(grupo=grupo):
                self.assertNotIn(url_centro_ministerial, self._renderizar_menu(grupo))
