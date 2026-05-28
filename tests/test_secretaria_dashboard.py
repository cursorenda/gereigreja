from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL, TESOUREIRO
from secretaria.models import Membro, StatusPessoa, TipoPessoa


class SecretariaDashboardPendenciasTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.admin = user_model.objects.create_user(
            username='admin_dash_secretaria',
            password='senha123',
        )
        self.usuario_secretaria = user_model.objects.create_user(
            username='secretario_dash',
            password='senha123',
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Dashboard Secretaria',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            nome_igreja='Igreja Dashboard Secretaria',
            ministerio=self.ministerio,
        )

        grupo_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.usuario_secretaria.groups.add(grupo_secretario)

        perfil = PerfilUsuario.objects.create(
            user=self.usuario_secretaria,
            ministerio=self.ministerio,
        )
        perfil.igrejas_permitidas.set([self.igreja])

        self.tipo_membro = TipoPessoa.objects.create(nome='Membro')
        self.status_ativo = StatusPessoa.objects.create(nome='Ativo')

        hoje = timezone.localdate()

        Membro.objects.create(
            nome='Membro Antigo Com Pendencia',
            igreja=self.igreja,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            data_entrada=hoje - timedelta(days=120),
            email='',
        )
        Membro.objects.create(
            nome='Membro Recente Com Pendencia',
            igreja=self.igreja,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            data_entrada=hoje - timedelta(days=5),
            email='',
        )
        Membro.objects.create(
            nome='Membro Recente Completo',
            igreja=self.igreja,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            data_entrada=hoje - timedelta(days=3),
            email='completo@example.com',
            nascimento=hoje - timedelta(days=365 * 30),
        )

    def test_dashboard_separa_pendencias_da_base_e_do_periodo(self):
        self.client.force_login(self.usuario_secretaria)

        response = self.client.get(reverse('secretaria:dashboard'), {'periodo': '30d'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_pendencias_cadastro'], 2)
        self.assertEqual(response.context['total_pendencias_cadastro_periodo'], 1)
        self.assertContains(response, 'Pessoas da base ativa com dados essenciais pendentes')
        self.assertContains(response, '1 registro(s) com pendência no período filtrado.')

    def test_dashboard_presets_de_periodo(self):
        self.client.force_login(self.usuario_secretaria)

        for periodo in ['30d', '90d', '6m', '12m']:
            with self.subTest(periodo=periodo):
                response = self.client.get(reverse('secretaria:dashboard'), {'periodo': periodo})

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['periodo_filtro'], periodo)
                self.assertLessEqual(response.context['periodo_data_inicio'], response.context['periodo_data_fim'])

    def test_dashboard_periodo_custom_normaliza_intervalo_invertido(self):
        self.client.force_login(self.usuario_secretaria)

        response = self.client.get(
            reverse('secretaria:dashboard'),
            {
                'periodo': 'custom',
                'data_inicio': '2026-05-27',
                'data_fim': '2026-05-20',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['periodo_filtro'], 'custom')
        self.assertEqual(response.context['periodo_data_inicio'], '2026-05-20')
        self.assertEqual(response.context['periodo_data_fim'], '2026-05-27')

    def test_dashboard_periodo_custom_invalido_faz_fallback_para_12m(self):
        self.client.force_login(self.usuario_secretaria)

        response = self.client.get(
            reverse('secretaria:dashboard'),
            {
                'periodo': 'custom',
                'data_inicio': 'invalido',
                'data_fim': '2026-05-27',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['periodo_filtro'], '12m')


class SecretariaDashboardEstadoNeutroTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.admin = user_model.objects.create_user(
            username='admin_dash_neutro',
            password='senha123',
        )
        self.usuario_secretaria = user_model.objects.create_user(
            username='secretario_dash_neutro',
            password='senha123',
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Dashboard Neutro',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            nome_igreja='Igreja Dashboard Neutro',
            ministerio=self.ministerio,
        )

        grupo_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.usuario_secretaria.groups.add(grupo_secretario)

        perfil = PerfilUsuario.objects.create(
            user=self.usuario_secretaria,
            ministerio=self.ministerio,
        )
        perfil.igrejas_permitidas.set([self.igreja])

        tipo_membro = TipoPessoa.objects.create(nome='MembroNeutro')
        status_ativo = StatusPessoa.objects.create(nome='AtivoNeutro')
        Membro.objects.create(
            nome='Membro Antigo Estavel',
            igreja=self.igreja,
            tipo_pessoa=tipo_membro,
            status_pessoa=status_ativo,
            email='estavel@example.com',
            nascimento=timezone.localdate() - timedelta(days=365 * 35),
            data_entrada=timezone.localdate() - timedelta(days=800),
        )

    def test_dashboard_exibe_sinal_neutro_sem_alerta_critico(self):
        self.client.force_login(self.usuario_secretaria)

        response = self.client.get(reverse('secretaria:dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Painel estavel no periodo')
        self.assertContains(response, 'Sem alertas criticos no recorte atual. Mantenha o monitoramento semanal.')


class SecretariaDashboardAcessoPerfisTest(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.admin = user_model.objects.create_user(
            username='admin_dashboard_perfis',
            password='senha123',
        )
        self.usuario_secretario = user_model.objects.create_user(
            username='secretario_dashboard_perfis',
            password='senha123',
        )
        self.usuario_pastor = user_model.objects.create_user(
            username='pastor_dashboard_perfis',
            password='senha123',
        )
        self.usuario_tesoureiro = user_model.objects.create_user(
            username='tesoureiro_dashboard_perfis',
            password='senha123',
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Dashboard Perfis',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            nome_igreja='Igreja Dashboard Perfis',
            ministerio=self.ministerio,
        )

        grupo_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)
        grupo_admin_ministerio, _ = Group.objects.get_or_create(name=ADMIN_MINISTERIO)

        self.usuario_secretario.groups.add(grupo_secretario)
        self.usuario_pastor.groups.add(grupo_pastor)
        self.usuario_tesoureiro.groups.add(grupo_tesoureiro)
        self.admin.groups.add(grupo_admin_ministerio)

        for usuario in [self.usuario_secretario, self.usuario_pastor, self.usuario_tesoureiro, self.admin]:
            perfil = PerfilUsuario.objects.create(
                user=usuario,
                ministerio=self.ministerio,
            )
            perfil.igrejas_permitidas.set([self.igreja])

        tipo_membro = TipoPessoa.objects.create(nome='MembroAcesso')
        status_ativo = StatusPessoa.objects.create(nome='AtivoAcesso')
        Membro.objects.create(
            nome='Membro Base Acesso',
            igreja=self.igreja,
            tipo_pessoa=tipo_membro,
            status_pessoa=status_ativo,
            email='membro.acesso@example.com',
            data_entrada=timezone.localdate() - timedelta(days=10),
        )

        self.dashboard_url = reverse('secretaria:dashboard')

    def _assert_ctas_visiveis_sem_bloqueio(self, user):
        self.client.force_login(user)
        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Gestão indisponível')

        cta_names = [
            'secretaria:cadastrar_membro',
            'secretaria:cadastrar_visitante',
            'secretaria:escolher_pessoa_para_acompanhamento',
            'secretaria:lista_pessoas',
            'secretaria:lista_visitantes',
            'secretaria:lista_cargos',
            'secretaria:lista_grupos_casa',
            'secretaria:relatorio_reuniao_membros',
            'secretaria:acompanhamentos_visita',
            'secretaria:criar_tag',
        ]

        for url_name in cta_names:
            target = self.client.get(reverse(url_name))
            self.assertNotEqual(
                target.status_code,
                403,
                msg=f'CTA {url_name} retornou 403 para usuário permitido.',
            )

    def test_dashboard_permite_secretario_local(self):
        self._assert_ctas_visiveis_sem_bloqueio(self.usuario_secretario)

    def test_dashboard_permite_pastor_local(self):
        self._assert_ctas_visiveis_sem_bloqueio(self.usuario_pastor)

    def test_dashboard_bloqueia_admin_ministerio(self):
        self.client.force_login(self.admin)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 403)

    def test_dashboard_bloqueia_tesoureiro(self):
        self.client.force_login(self.usuario_tesoureiro)

        response = self.client.get(self.dashboard_url)

        self.assertEqual(response.status_code, 403)