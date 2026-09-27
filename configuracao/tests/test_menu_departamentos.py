from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.sessions.middleware import SessionMiddleware
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase
from django.urls import reverse

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL
from configuracao.models import Departamento, DepartamentoVinculo, Igreja, Ministerio, PerfilUsuario
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


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

    def _criar_pessoa(self, user, nome):
        tipo, _ = TipoPessoa.objects.get_or_create(nome='Membro Menu Departamentos')
        status, _ = StatusPessoa.objects.get_or_create(nome='Ativo Menu Departamentos')
        return Pessoa.objects.create(
            usuario=user,
            igreja=self.igreja,
            nome=nome,
            tipo_pessoa=tipo,
            status_pessoa=status,
        )

    def _renderizar_menu_para_usuario(self, user):
        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={'ministerio': self.ministerio},
        )
        perfil.igrejas_permitidas.add(self.igreja)
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

    def test_meus_departamentos_so_aparece_com_vinculo_ativo_proprio(self):
        User = get_user_model()
        user_sem_vinculo = User.objects.create_user(username='menu-sem-vinculo')
        user_vinculo_encerrado = User.objects.create_user(username='menu-vinculo-encerrado')
        user_vinculo_ativo = User.objects.create_user(username='menu-vinculo-ativo')
        outro_user = User.objects.create_user(username='menu-vinculo-outro')
        departamento = Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        departamento_encerrado = Departamento.objects.get(igreja=self.igreja, codigo_interno='ASSISTENCIA')
        pessoa_encerrada = self._criar_pessoa(user_vinculo_encerrado, 'Pessoa Encerrada')
        pessoa_ativa = self._criar_pessoa(user_vinculo_ativo, 'Pessoa Ativa')
        pessoa_outro = self._criar_pessoa(outro_user, 'Pessoa Outro Usuario')
        DepartamentoVinculo.objects.create(
            membro=pessoa_encerrada,
            departamento=departamento_encerrado,
            data_fim=date.today(),
        )
        DepartamentoVinculo.objects.create(membro=pessoa_ativa, departamento=departamento)
        DepartamentoVinculo.objects.create(membro=pessoa_outro, departamento=departamento_encerrado)
        DepartamentoVinculo.objects.create(membro=pessoa_ativa, departamento=departamento_encerrado)
        url = f'href="{reverse("configuracao:meus_departamentos")}"'

        self.assertNotIn(url, self._renderizar_menu_para_usuario(user_sem_vinculo))
        self.assertNotIn(url, self._renderizar_menu_para_usuario(user_vinculo_encerrado))
        self.assertNotIn(url, self._renderizar_menu_para_usuario(user_sem_vinculo))
        self.assertEqual(self._renderizar_menu_para_usuario(user_vinculo_ativo).count(url), 1)
