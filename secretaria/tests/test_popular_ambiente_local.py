from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from contas.constants import ADMIN_MINISTERIO, MEMBRO_COMUM, PASTOR_LOCAL, SECRETARIO_LOCAL, TESOUREIRO
from contas.page_permissions import pode_acessar_financeiro, pode_acessar_secretaria
from configuracao.services_assinatura import usuario_pode_usar_modulo
from configuracao.models import Departamento, DepartamentoVinculo, Igreja, Ministerio, PerfilUsuario
from core.utils import get_igrejas_selecionaveis
from secretaria.management.commands.popular_ambiente_local import (
    CONGREGACAO_NOME,
    DEPARTAMENTO_CODIGO,
    MINISTERIO_NOME,
    REGIONAL_NOME,
    SEDE_NOME,
    USUARIOS,
    preparar_ambiente_local,
    validar_ambiente_local,
)
from secretaria.models import Pessoa


class PopularAmbienteLocalTests(TestCase):
    password = 'senha-local-de-teste'

    def preparar(self):
        return preparar_ambiente_local(password=self.password, permitir_settings_test=True)

    def test_comando_operacional_bloqueia_settings_de_teste(self):
        with self.assertRaises(CommandError):
            validar_ambiente_local()

    @override_settings(DATABASES={'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': 'nao-usar'}})
    def test_guard_rejeita_engine_nao_sqlite(self):
        with self.assertRaises(CommandError):
            validar_ambiente_local(permitir_settings_test=True)

    def test_cenario_e_idempotente_sem_modificar_admin_local(self):
        User = get_user_model()
        admin_local = User.objects.create_superuser('admin_local', 'admin_local@example.test', 'tecnica')
        self.preparar()
        contagens_antes = {
            'ministerios': Ministerio.objects.filter(nome_fantasia=MINISTERIO_NOME).count(),
            'igrejas': Igreja.objects.filter(ministerio__nome_fantasia=MINISTERIO_NOME).count(),
            'usuarios': User.objects.filter(username__in=[item[0] for item in USUARIOS]).count(),
            'perfis': PerfilUsuario.objects.filter(user__username__in=[item[0] for item in USUARIOS]).count(),
            'pessoas': Pessoa.objects.filter(usuario__username__in=[item[0] for item in USUARIOS]).count(),
            'departamentos': Departamento.objects.filter(codigo_interno=DEPARTAMENTO_CODIGO).count(),
            'vinculos': DepartamentoVinculo.objects.filter(membro__usuario__username='multi_funcao_local').count(),
        }
        self.preparar()
        contagens_depois = {
            'ministerios': Ministerio.objects.filter(nome_fantasia=MINISTERIO_NOME).count(),
            'igrejas': Igreja.objects.filter(ministerio__nome_fantasia=MINISTERIO_NOME).count(),
            'usuarios': User.objects.filter(username__in=[item[0] for item in USUARIOS]).count(),
            'perfis': PerfilUsuario.objects.filter(user__username__in=[item[0] for item in USUARIOS]).count(),
            'pessoas': Pessoa.objects.filter(usuario__username__in=[item[0] for item in USUARIOS]).count(),
            'departamentos': Departamento.objects.filter(codigo_interno=DEPARTAMENTO_CODIGO).count(),
            'vinculos': DepartamentoVinculo.objects.filter(membro__usuario__username='multi_funcao_local').count(),
        }
        self.assertEqual(contagens_antes, contagens_depois)
        admin_local.refresh_from_db()
        self.assertTrue(admin_local.is_superuser)
        self.assertFalse(admin_local.groups.exists())
        self.assertFalse(PerfilUsuario.objects.filter(user=admin_local).exists())
        self.assertFalse(Pessoa.objects.filter(usuario=admin_local).exists())

    def test_tenant_usuarios_vinculos_e_escopos(self):
        self.preparar()
        ministerio = Ministerio.objects.get(nome_fantasia=MINISTERIO_NOME)
        sede = Igreja.objects.get(ministerio=ministerio, nome_igreja=SEDE_NOME)
        regional = Igreja.objects.get(ministerio=ministerio, nome_igreja=REGIONAL_NOME)
        congregacao = Igreja.objects.get(ministerio=ministerio, nome_igreja=CONGREGACAO_NOME)
        self.assertTrue(ministerio.ativo)
        self.assertFalse(ministerio.is_demo)
        self.assertEqual((sede.tipo_igreja, regional.igreja_superior, congregacao.igreja_superior), ('sede', sede, regional))

        expected = {
            'admin_ministerio_local': (ADMIN_MINISTERIO, sede),
            'pastor_local_teste': (PASTOR_LOCAL, congregacao),
            'secretario_local_teste': (SECRETARIO_LOCAL, sede),
            'tesoureiro_local_teste': (TESOUREIRO, sede),
            'membro_local_teste': (MEMBRO_COMUM, congregacao),
            'multi_funcao_local': (TESOUREIRO, congregacao),
        }
        User = get_user_model()
        for username, (group_name, igreja) in expected.items():
            user = User.objects.get(username=username)
            perfil = PerfilUsuario.objects.get(user=user)
            pessoa = Pessoa.objects.get(usuario=user)
            self.assertFalse(user.is_superuser)
            self.assertFalse(user.is_staff)
            self.assertTrue(user.groups.filter(name=group_name).exists())
            self.assertEqual(perfil.ministerio, ministerio)
            self.assertEqual(list(perfil.igrejas_permitidas.all()), [igreja])
            self.assertEqual(pessoa.igreja, igreja)

        self.assertEqual(ministerio.administrador_principal.username, 'admin_ministerio_local')
        self.assertTrue(DepartamentoVinculo.objects.filter(
            departamento__igreja=congregacao,
            departamento__codigo_interno=DEPARTAMENTO_CODIGO,
            membro__usuario__username='multi_funcao_local',
            data_fim__isnull=True,
        ).exists())

    def test_politicas_de_secretaria_preservam_escopo_operacional(self):
        self.preparar()
        ministerio = Ministerio.objects.get(nome_fantasia=MINISTERIO_NOME)
        sede = Igreja.objects.get(ministerio=ministerio, nome_igreja=SEDE_NOME)
        regional = Igreja.objects.get(ministerio=ministerio, nome_igreja=REGIONAL_NOME)
        congregacao = Igreja.objects.get(ministerio=ministerio, nome_igreja=CONGREGACAO_NOME)
        User = get_user_model()
        admin = User.objects.get(username='admin_ministerio_local')
        pastor = User.objects.get(username='pastor_local_teste')
        secretario = User.objects.get(username='secretario_local_teste')
        tesoureiro = User.objects.get(username='tesoureiro_local_teste')

        self.assertTrue(pode_acessar_secretaria(admin, igreja=sede))
        self.assertFalse(pode_acessar_secretaria(admin, igreja=regional))
        self.assertFalse(pode_acessar_secretaria(admin, igreja=congregacao))
        self.assertTrue(pode_acessar_secretaria(pastor, igreja=congregacao))
        self.assertFalse(pode_acessar_secretaria(pastor, igreja=sede))
        self.assertTrue(pode_acessar_secretaria(secretario, igreja=sede))
        self.assertFalse(pode_acessar_secretaria(secretario, igreja=congregacao))
        self.assertFalse(pode_acessar_secretaria(tesoureiro, igreja=sede))
        self.assertTrue(pode_acessar_financeiro(tesoureiro, igreja=sede))
        self.assertTrue(usuario_pode_usar_modulo(secretario, 'secretaria'))
        self.assertTrue(usuario_pode_usar_modulo(tesoureiro, 'financeiro'))
        self.assertSetEqual(
            {sede.pk, regional.pk, congregacao.pk},
            {sede.pk, regional.pk, congregacao.pk}.intersection(
                set(get_igrejas_selecionaveis(admin).values_list('pk', flat=True))
            ),
        )

    def test_seed_nao_realiza_chamada_externa(self):
        with patch('socket.socket') as socket_mock:
            self.preparar()
        socket_mock.assert_not_called()