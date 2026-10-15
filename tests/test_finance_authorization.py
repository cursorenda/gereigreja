from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from contas.constants import (
    ADMIN_MINISTERIO,
    LIDERANCA_FINANCEIRA,
    PASTOR_LOCAL,
    PASTOR_REGIONAL,
    TESOUREIRO,
)
from configuracao.models import Igreja, Ministerio, PerfilUsuario
from financeiro.authorization import get_finance_read_scope, get_finance_write_scope
from secretaria.models import Membro, StatusPessoa, TipoPessoa


class FinanceAuthorizationScopeTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_m1 = User.objects.create_user(username='admin-m1-finance-auth')
        self.admin_m2 = User.objects.create_user(username='admin-m2-finance-auth')
        self.ministerio_m1 = Ministerio.objects.create(
            nome_fantasia='Ministerio M1 Finance Authorization',
            administrador_principal=self.admin_m1,
            ativo=True,
        )
        self.ministerio_m2 = Ministerio.objects.create(
            nome_fantasia='Ministerio M2 Finance Authorization',
            administrador_principal=self.admin_m2,
            ativo=True,
        )
        self.sede_a = Igreja.objects.create(
            ministerio=self.ministerio_m1,
            nome_igreja='Sede A Finance Authorization',
            tipo_igreja='sede',
        )
        self.regional_b = Igreja.objects.create(
            ministerio=self.ministerio_m1,
            nome_igreja='Regional B Finance Authorization',
            tipo_igreja='regional',
            igreja_superior=self.sede_a,
        )
        self.congregacao_c = Igreja.objects.create(
            ministerio=self.ministerio_m1,
            nome_igreja='Congregacao C Finance Authorization',
            tipo_igreja='congregacao',
            igreja_superior=self.regional_b,
        )
        self.congregacao_d = Igreja.objects.create(
            ministerio=self.ministerio_m1,
            nome_igreja='Congregacao D Finance Authorization',
            tipo_igreja='congregacao',
            igreja_superior=self.regional_b,
        )
        self.igreja_x = Igreja.objects.create(
            ministerio=self.ministerio_m2,
            nome_igreja='Igreja X Finance Authorization',
            tipo_igreja='independente',
        )

    def _create_user_with_profile(self, username, churches=(), group_name=None):
        user = get_user_model().objects.create_user(username=username)
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
        perfil = PerfilUsuario.objects.create(user=user, ministerio=self.ministerio_m1)
        perfil.igrejas_permitidas.set(churches)
        return user

    def _assert_read_and_write_scope(self, user, ministerio, expected_churches):
        expected_ids = {church.pk for church in expected_churches}
        self.assertEqual(
            set(get_finance_read_scope(user, ministerio).values_list('pk', flat=True)),
            expected_ids,
        )
        self.assertEqual(
            set(get_finance_write_scope(user, ministerio).values_list('pk', flat=True)),
            expected_ids,
        )

    def test_admin_ministerio_uses_only_explicit_churches(self):
        user = self._create_user_with_profile(
            'admin-explicit-finance-auth',
            churches=[self.sede_a],
            group_name=ADMIN_MINISTERIO,
        )

        self._assert_read_and_write_scope(user, self.ministerio_m1, [self.sede_a])

    def test_admin_ministerio_with_empty_explicit_scope_fails_closed(self):
        user = self._create_user_with_profile(
            'admin-empty-finance-auth',
            group_name=ADMIN_MINISTERIO,
        )

        self._assert_read_and_write_scope(user, self.ministerio_m1, [])

    def test_pastor_regional_does_not_expand_to_subordinate_churches(self):
        user = self._create_user_with_profile(
            'regional-explicit-finance-auth',
            churches=[self.regional_b],
            group_name=PASTOR_REGIONAL,
        )

        self._assert_read_and_write_scope(user, self.ministerio_m1, [self.regional_b])

    def test_lideranca_financeira_does_not_expand_to_subordinate_churches(self):
        user = self._create_user_with_profile(
            'lideranca-explicit-finance-auth',
            churches=[self.sede_a],
            group_name=LIDERANCA_FINANCEIRA,
        )

        self._assert_read_and_write_scope(user, self.ministerio_m1, [self.sede_a])

    def test_pastor_local_uses_only_explicit_churches(self):
        user = self._create_user_with_profile(
            'pastor-local-explicit-finance-auth',
            churches=[self.congregacao_c],
            group_name=PASTOR_LOCAL,
        )

        self._assert_read_and_write_scope(user, self.ministerio_m1, [self.congregacao_c])

    def test_tesoureiro_uses_only_explicit_churches(self):
        user = self._create_user_with_profile(
            'tesoureiro-explicit-finance-auth',
            churches=[self.congregacao_d],
            group_name=TESOUREIRO,
        )

        self._assert_read_and_write_scope(user, self.ministerio_m1, [self.congregacao_d])

    def test_user_without_profile_has_empty_scopes(self):
        user = get_user_model().objects.create_user(username='without-profile-finance-auth')

        self._assert_read_and_write_scope(user, self.ministerio_m1, [])

    def test_profile_for_another_ministry_has_empty_scopes(self):
        user = self._create_user_with_profile(
            'wrong-ministry-finance-auth',
            churches=[self.sede_a],
        )

        self._assert_read_and_write_scope(user, self.ministerio_m2, [])

    def test_member_without_explicit_churches_has_empty_scopes(self):
        user = self._create_user_with_profile('member-without-scope-finance-auth')
        tipo_pessoa = TipoPessoa.objects.create(nome='Membro Finance Authorization')
        status_pessoa = StatusPessoa.objects.create(nome='Ativo Finance Authorization')
        Membro.objects.create(
            nome='Membro sem escopo financeiro',
            usuario=user,
            igreja=self.sede_a,
            tipo_pessoa=tipo_pessoa,
            status_pessoa=status_pessoa,
        )

        self._assert_read_and_write_scope(user, self.ministerio_m1, [])

    def test_superuser_without_explicit_churches_has_empty_scopes(self):
        user = get_user_model().objects.create_user(
            username='superuser-without-scope-finance-auth',
            is_superuser=True,
        )
        PerfilUsuario.objects.create(user=user, ministerio=self.ministerio_m1)

        self._assert_read_and_write_scope(user, self.ministerio_m1, [])
