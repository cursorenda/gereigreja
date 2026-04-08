from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, PASTOR_REGIONAL
from secretaria.models import Cargo


class CargoAutorizacaoViewsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.user_admin_principal = user_model.objects.create_user(
            username='admin_principal_ministerio',
            password='pass123',
        )
        self.user_local = user_model.objects.create_user(
            username='pastor_local_user',
            password='pass123',
        )
        self.user_regional = user_model.objects.create_user(
            username='pastor_regional_user',
            password='pass123',
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste Escopo Cargos',
            administrador_principal=self.user_admin_principal,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            nome_igreja='Igreja Teste Escopo Cargos',
            ministerio=self.ministerio,
        )

        self.perfil_local = PerfilUsuario.objects.create(
            user=self.user_local,
            ministerio=self.ministerio,
        )
        self.perfil_local.igrejas_permitidas.add(self.igreja)

        self.perfil_regional = PerfilUsuario.objects.create(
            user=self.user_regional,
            ministerio=self.ministerio,
        )
        self.perfil_regional.igrejas_permitidas.add(self.igreja)

        self.grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.grupo_pastor_regional, _ = Group.objects.get_or_create(name=PASTOR_REGIONAL)
        self.grupo_pastor_local, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)

        self.user_local.groups.add(self.grupo_pastor_local)
        self.user_regional.groups.add(self.grupo_pastor_regional)

        self.cargo_superior = Cargo.objects.create(
            nome='Cargo Superior Admin',
            grupo_permissao=self.grupo_admin,
        )
        self.cargo_local = Cargo.objects.create(
            nome='Cargo Local Pastor',
            grupo_permissao=self.grupo_pastor_local,
        )
        self.cargo_sem_grupo = Cargo.objects.create(
            nome='Cargo Sem Grupo',
            grupo_permissao=None,
        )

    def test_pastor_local_lista_cargos_filtra_grupos_superiores(self):
        self.client.force_login(self.user_local)

        response = self.client.get(reverse('secretaria:lista_cargos'))

        self.assertEqual(response.status_code, 200)
        cargos_exibidos = {cargo.nome for cargo in response.context['cargos']}
        self.assertIn(self.cargo_local.nome, cargos_exibidos)
        self.assertIn(self.cargo_sem_grupo.nome, cargos_exibidos)
        self.assertNotIn(self.cargo_superior.nome, cargos_exibidos)

    def test_pastor_local_nao_pode_editar_cargo_superior_por_url_direta(self):
        self.client.force_login(self.user_local)

        response = self.client.get(
            reverse('secretaria:editar_cargo', kwargs={'cargo_id': self.cargo_superior.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_pastor_local_nao_pode_excluir_cargo_superior_por_url_direta(self):
        self.client.force_login(self.user_local)

        response = self.client.get(
            reverse('secretaria:excluir_cargo', kwargs={'cargo_id': self.cargo_superior.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_pastor_local_nao_pode_gerenciar_ocupantes_de_cargo_superior(self):
        self.client.force_login(self.user_local)

        response = self.client.get(
            reverse('secretaria:gerenciar_ocupantes', kwargs={'cargo_id': self.cargo_superior.id})
        )

        self.assertEqual(response.status_code, 403)

    def test_pastor_local_form_criar_cargo_limita_grupos_disponiveis(self):
        self.client.force_login(self.user_local)

        response = self.client.get(reverse('secretaria:criar_cargo'))

        self.assertEqual(response.status_code, 200)
        grupos_disponiveis = set(
            response.context['form'].fields['grupo_permissao'].queryset.values_list('name', flat=True)
        )
        self.assertIn(PASTOR_LOCAL, grupos_disponiveis)
        self.assertNotIn(ADMIN_MINISTERIO, grupos_disponiveis)

    def test_pastor_regional_lista_cargos_filtra_grupos_superiores(self):
        self.client.force_login(self.user_regional)

        response = self.client.get(reverse('secretaria:lista_cargos'))

        self.assertEqual(response.status_code, 200)
        cargos_exibidos = {cargo.nome for cargo in response.context['cargos']}
        self.assertIn(self.cargo_local.nome, cargos_exibidos)
        self.assertIn(self.cargo_sem_grupo.nome, cargos_exibidos)
        self.assertNotIn(self.cargo_superior.nome, cargos_exibidos)
