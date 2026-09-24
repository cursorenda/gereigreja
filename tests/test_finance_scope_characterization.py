"""Caracteriza o escopo legado do helper financeiro sem alterar sua semântica."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from contas.constants import PROFESSOR_EBD, SECRETARIO_LOCAL
from configuracao.models import Igreja, Ministerio, PerfilUsuario
from financeiro.models import TransferenciaCaixa
from financeiro.utils import get_allowed_churches_for_user, has_finance_view_permission
from secretaria.models import Membro, StatusPessoa, TipoPessoa


User = get_user_model()


class FinanceScopeCharacterizationTests(TestCase):
    """Registra fallback organizacional e bloqueios financeiros atualmente vigentes."""

    def setUp(self):
        self.ministerio_admin = User.objects.create_user(
            username='admin_finance_scope_characterization',
            password='senha123',
        )
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Characterization Finance Scope',
            administrador_principal=self.ministerio_admin,
            ativo=True,
        )
        self.igreja_a = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja A Characterization',
            tipo_igreja='congregacao',
        )
        self.tipo_membro = TipoPessoa.objects.create(nome='Membro Characterization')
        self.status_ativo = StatusPessoa.objects.create(nome='Ativo Characterization')

    def _criar_usuario_com_membro(self, username, grupo=None):
        user = User.objects.create_user(username=username, password='senha123')
        PerfilUsuario.objects.create(user=user, ministerio=self.ministerio)
        Membro.objects.create(
            nome=f'Membro {username}',
            igreja=self.igreja_a,
            usuario=user,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        if grupo:
            user.groups.add(Group.objects.get_or_create(name=grupo)[0])
        return user

    def test_helper_retorna_exclusivamente_igreja_do_membro_para_usuario_sem_papel_financeiro(self):
        user = self._criar_usuario_com_membro('nao_financeiro_member_fallback')

        igrejas = get_allowed_churches_for_user(user)

        self.assertEqual(list(igrejas), [self.igreja_a])
        self.assertFalse(has_finance_view_permission(user))

    def test_helper_retorna_exclusivamente_igreja_do_membro_para_professor_ebd(self):
        user = self._criar_usuario_com_membro(
            'professor_ebd_member_fallback',
            PROFESSOR_EBD,
        )

        igrejas = get_allowed_churches_for_user(user)

        self.assertEqual(list(igrejas), [self.igreja_a])
        self.assertFalse(has_finance_view_permission(user))

    def test_fallback_do_membro_nao_concede_acesso_as_rotas_financeiras(self):
        user = self._criar_usuario_com_membro('nao_financeiro_http_member_fallback')
        self.client.force_login(user)

        rotas = (
            reverse('financeiro:lista_receitas'),
            reverse('financeiro:lista_despesas'),
            reverse('financeiro:painel_financeiro'),
            reverse('financeiro:lista_fechamentos_caixa'),
            reverse('financeiro:api_caixas_por_igreja', args=[self.igreja_a.pk]),
            reverse('financeiro:nova_transferencia_caixa'),
        )

        with patch('financeiro.views.get_allowed_churches_for_user') as helper_da_view:
            for rota in rotas:
                with self.subTest(rota=rota):
                    response = self.client.get(rota)
                    self.assertIn(response.status_code, (302, 403))
                    self.assertNotIn('receitas', response.context or {})
                    self.assertNotIn('despesas', response.context or {})
                    self.assertNotIn('fechamentos', response.context or {})

        helper_da_view.assert_not_called()
        self.assertFalse(TransferenciaCaixa.objects.exists())

    def test_secretario_local_tem_match_hierarquico_e_escopo_mas_entrada_financeira_e_negada(self):
        user = self._criar_usuario_com_membro(
            'secretario_local_finance_scope_characterization',
            SECRETARIO_LOCAL,
        )
        user.perfil.igrejas_permitidas.add(self.igreja_a)
        self.client.force_login(user)

        self.assertTrue(has_finance_view_permission(user))
        self.assertEqual(list(get_allowed_churches_for_user(user)), [self.igreja_a])

        response = self.client.get(reverse('financeiro:lista_receitas'))

        self.assertEqual(response.status_code, 403)
        self.assertNotIn('receitas', response.context or {})