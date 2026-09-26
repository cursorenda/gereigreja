"""
Testes para validar o context processor unificado de status do plano.
Executa: python manage.py test core.tests.test_context_status_plano
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch

from configuracao.models import Ministerio, Plano, AssinaturaMinisterio, PerfilUsuario
from core.context_status_plano import status_plano_unificado


class StatusPlanoUnificadoTestCase(TestCase):
    
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Igreja Teste',
            administrador_principal=self.user,
            ativo=True
        )
        self.perfil = PerfilUsuario.objects.create(
            user=self.user,
            ministerio=self.ministerio
        )
        
    def _make_request(self, path='/'):
        request = self.factory.get(path)
        request.user = self.user
        return request
    
    def test_unauthenticated_user_returns_none(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        result = status_plano_unificado(request)
        self.assertEqual(result, {'status_plano': None})
    
    def test_superuser_returns_none(self):
        self.user.is_superuser = True
        self.user.save()
        request = self._make_request()
        result = status_plano_unificado(request)
        self.assertEqual(result, {'status_plano': None})
    
    def test_sem_assinatura_returns_critico(self):
        """Ministério sem assinatura deve retornar estado crítico"""
        request = self._make_request()
        with patch('configuracao.services_assinatura.assinatura_esta_regular', return_value=False):
            result = status_plano_unificado(request)
        
        self.assertIsNotNone(result['status_plano'])
        self.assertEqual(result['status_plano']['nivel'], 'critico')
        self.assertEqual(result['status_plano']['tipo'], 'sem_assinatura')
        self.assertIn('não possui uma assinatura', result['status_plano']['mensagem'])

    def test_ministerio_demo_com_username_normal_suprime_status(self):
        self.ministerio.is_demo = True
        self.ministerio.save(update_fields=['is_demo'])

        result = status_plano_unificado(self._make_request())

        self.assertEqual(result, {'status_plano': None})

    def test_username_demo_nao_suprime_status_de_tenant_real(self):
        self.user.username = 'demo_usuario'
        self.user.save(update_fields=['username'])

        with patch('configuracao.services_assinatura.assinatura_esta_regular', return_value=False):
            result = status_plano_unificado(self._make_request())

        self.assertEqual(result['status_plano']['tipo'], 'sem_assinatura')

    def test_admin_demo_username_nao_suprime_status_de_tenant_real(self):
        self.user.username = 'admin_demo'
        self.user.save(update_fields=['username'])

        with patch('configuracao.services_assinatura.assinatura_esta_regular', return_value=False):
            result = status_plano_unificado(self._make_request())

        self.assertEqual(result['status_plano']['tipo'], 'sem_assinatura')
    
    def test_assinatura_vencida_returns_critico(self):
        """Assinatura vencida deve retornar estado crítico"""
        plano = Plano.objects.create(
            nome='crescimento',
            limite_membros=50,
            preco_mensal=99,
            preco_anual=990,
            stripe_product_id='prod_test'
        )
        assinatura = AssinaturaMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano,
            status='vencida',
            data_inicio=timezone.now() - timedelta(days=365),
            data_fim=timezone.now() - timedelta(days=30),
        )
        request = self._make_request()
        with patch('configuracao.services_assinatura.assinatura_esta_regular', return_value=False):
            result = status_plano_unificado(request)
        
        self.assertIsNotNone(result['status_plano'])
        self.assertEqual(result['status_plano']['nivel'], 'critico')
        self.assertEqual(result['status_plano']['tipo'], 'assinatura_vencida')
        self.assertIn('vencida', result['status_plano']['mensagem'].lower())
    
    def test_limite_atingido_returns_aviso(self):
        """Limite de 100% deve retornar estado aviso"""
        plano = Plano.objects.create(
            nome='crescimento',
            limite_membros=5,
            preco_mensal=99,
            preco_anual=990,
            stripe_product_id='prod_test'
        )
        AssinaturaMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano,
            status='ativa',
            data_inicio=timezone.now() - timedelta(days=30),
            data_fim=timezone.now() + timedelta(days=365),
        )

        request = self._make_request()
        with patch('configuracao.services_assinatura.assinatura_esta_regular', return_value=True), \
             patch('configuracao.services_assinatura.obter_limite_pessoas_ativas', return_value=5), \
             patch('configuracao.services_assinatura.contar_pessoas_ativas', return_value=5):
            result = status_plano_unificado(request)

        self.assertIsNotNone(result['status_plano'])
        self.assertEqual(result['status_plano']['nivel'], 'aviso')
        self.assertEqual(result['status_plano']['tipo'], 'limite_atingido')
    
    def test_ministerio_inativo_returns_none(self):
        """Ministério inativo não deve retornar alerta"""
        self.ministerio.ativo = False
        self.ministerio.save()
        request = self._make_request()
        result = status_plano_unificado(request)
        self.assertEqual(result, {'status_plano': None})
    
    def test_sem_ministerio_returns_none(self):
        """Usuário sem ministério associado deve retornar None"""
        self.perfil.delete()  # Remove a associação
        request = self._make_request()
        result = status_plano_unificado(request)
        self.assertEqual(result, {'status_plano': None})
