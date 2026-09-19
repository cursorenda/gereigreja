"""
Testes de integracao para a regra de acesso ao Financeiro por Admin Ministerio.

Cobre o comportamento real atraves do decorator @page_access_required('financeiro'),
usando o cliente de teste Django e o ciclo completo de request (middleware, sessao, view).
"""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, TESOUREIRO
from configuracao.models import Igreja, Ministerio, PerfilUsuario


User = get_user_model()


class AdminMinisterioFinanceiroIntegracaoTest(TestCase):
    """Testa a regra de Financeiro via decorator @page_access_required real."""

    def setUp(self):
        self.grupo_admin, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)
        self.grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)

        self.admin_user = User.objects.create_user(username='admin_base', password='demo123')

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Integracao',
            cnpj='99.999.999/0001-99',
            cidade='Cidade Teste',
            estado='SP',
            administrador_principal=self.admin_user,
            ativo=True,
        )

        # Assinatura gratuita para que usuario_pode_usar_modulo retorne True
        from configuracao.models import AssinaturaMinisterio
        AssinaturaMinisterio.objects.get_or_create(
            ministerio=self.ministerio,
            defaults={
                'data_inicio': timezone.now(),
                'data_fim': timezone.now() + timedelta(days=3650),
                'status': 'gratuita',
            },
        )

        self.igreja_sede = Igreja.objects.create(
            nome_igreja='Sede Integracao',
            ministerio=self.ministerio,
            tipo_igreja='sede',
            cidade='Cidade Teste',
            estado='SP',
        )
        self.igreja_independente = Igreja.objects.create(
            nome_igreja='Independente Integracao',
            ministerio=self.ministerio,
            tipo_igreja='independente',
            cidade='Cidade Teste',
            estado='SP',
        )
        self.igreja_regional = Igreja.objects.create(
            nome_igreja='Regional Integracao',
            ministerio=self.ministerio,
            tipo_igreja='regional',
            cidade='Cidade Teste',
            estado='SP',
        )
        self.igreja_congregacao = Igreja.objects.create(
            nome_igreja='Congregacao Integracao',
            ministerio=self.ministerio,
            tipo_igreja='congregacao',
            cidade='Cidade Teste',
            estado='SP',
        )

        self.ministerio_b = Ministerio.objects.create(
            nome_fantasia='Ministerio B',
            cnpj='88.888.888/0001-88',
            cidade='Cidade Teste',
            estado='SP',
            administrador_principal=self.admin_user,
        )
        self.igreja_outro_ministerio = Igreja.objects.create(
            nome_igreja='Sede Ministerio B',
            ministerio=self.ministerio_b,
            tipo_igreja='sede',
            cidade='Cidade Teste',
            estado='SP',
        )

    def _criar_user_admin(self):
        user = User.objects.create_user(username='admin_integracao', password='demo123')
        user.groups.add(self.grupo_admin)
        PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={'ministerio': self.ministerio},
        )
        return user

    def _criar_user_pastor(self):
        user = User.objects.create_user(username='pastor_integracao', password='demo123')
        user.groups.add(self.grupo_pastor)
        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={'ministerio': self.ministerio},
        )
        perfil.igrejas_permitidas.set([self.igreja_sede])
        return user

    def _criar_user_tesoureiro(self):
        user = User.objects.create_user(username='tesoureiro_integracao', password='demo123')
        user.groups.add(self.grupo_tesoureiro)
        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={'ministerio': self.ministerio},
        )
        perfil.igrejas_permitidas.set([self.igreja_sede])
        return user

    def test_admin_sede_permite(self):
        """Admin Ministerio + Sede valida no escopo -> 200."""
        user = self._criar_user_admin()
        status = self._acessar_financeiro(user, self.igreja_sede)
        self.assertEqual(status, 200)

    def test_admin_independente_permite(self):
        """Admin Ministerio + Independente valida no escopo -> 200."""
        user = self._criar_user_admin()
        status = self._acessar_financeiro(user, self.igreja_independente)
        self.assertEqual(status, 200)

    def test_admin_regional_nega(self):
        """Admin Ministerio + Regional -> 403."""
        user = self._criar_user_admin()
        status = self._acessar_financeiro(user, self.igreja_regional)
        self.assertEqual(status, 403)

    def test_admin_congregacao_nega(self):
        """Admin Ministerio + Congregacao -> 403."""
        user = self._criar_user_admin()
        status = self._acessar_financeiro(user, self.igreja_congregacao)
        self.assertEqual(status, 403)

    def test_admin_sem_igreja_nega(self):
        """Admin Ministerio + sem igreja ativa -> 403."""
        user = self._criar_user_admin()
        status = self._acessar_financeiro(user, None)
        self.assertEqual(status, 403)

    def test_admin_igreja_fora_escopo_nega(self):
        """Admin Ministerio + igreja de outro ministerio -> 403."""
        user = self._criar_user_admin()
        status = self._acessar_financeiro(user, self.igreja_outro_ministerio)
        self.assertEqual(status, 403)

    def test_pastor_local_preservado(self):
        """Pastor Local com igreja permitida -> 200 (comportamento preservado)."""
        user = self._criar_user_pastor()
        status = self._acessar_financeiro(user, self.igreja_sede)
        self.assertEqual(status, 200)

    def test_tesoureiro_preservado(self):
        """Tesoureiro com igreja permitida -> 200 (comportamento preservado)."""
        user = self._criar_user_tesoureiro()
        status = self._acessar_financeiro(user, self.igreja_sede)
        self.assertEqual(status, 200)

    def test_superuser_sem_papel_funcional_e_negado(self):
        user = User.objects.create_user(
            username='superuser_sem_papel_integracao',
            password='demo123',
            is_superuser=True,
        )
        PerfilUsuario.objects.create(user=user, ministerio=self.ministerio)

        status = self._acessar_financeiro(user, self.igreja_sede)
        self.assertEqual(status, 403)

    def test_troca_de_contexto_recalcula_acesso_do_admin(self):
        user = self._criar_user_admin()

        self.assertEqual(self._acessar_financeiro(user, self.igreja_sede), 200)
        self.assertEqual(self._acessar_financeiro(user, self.igreja_congregacao), 403)
        self.assertEqual(self._acessar_financeiro(user, self.igreja_independente), 200)

    def _acessar_financeiro(self, user, igreja_ativa=None):
        """Helper: login + GET financeiro:painel_financeiro e retorna status_code."""
        self.client.force_login(user)
        session = self.client.session
        if igreja_ativa is not None:
            session['igreja_ativa_id'] = igreja_ativa.pk
        else:
            session.pop('igreja_ativa_id', None)
        session.save()
        response = self.client.get(reverse('financeiro:painel_financeiro'))
        return response.status_code
