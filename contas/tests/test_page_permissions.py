"""
Testes focados para a regra de acesso ao Financeiro (pode_acessar_financeiro).

Cobre a especificacao:
- Pastor Local e Tesoureiro: comportamento preservado
- Admin Ministerio: permitido apenas com igreja ativa Sede ou Independente valida
- Admin Ministerio: negado para Regional, Congregacao, None, ou igreja fora do escopo
"""
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase

from contas.constants import (
    ADMIN_MINISTERIO,
    MEMBRO_COMUM,
    PASTOR_LOCAL,
    TESOUREIRO,
)
from contas.page_permissions import PAGE_ACCESS_RULES, pode_acessar_financeiro, user_can_access_page


User = get_user_model()


class PodeAcessarFinanceiroTests(TestCase):
    """Testa a funcao pode_acessar_financeiro()."""

    def setUp(self):
        self.factory = RequestFactory()
        self._criar_grupos()

    def _criar_grupos(self):
        for nome in (ADMIN_MINISTERIO, PASTOR_LOCAL, TESOUREIRO, MEMBRO_COMUM):
            Group.objects.get_or_create(name=nome)

    def _criar_usuario(self, username, grupo):
        user = User.objects.create_user(username=username, password='demo123')
        user.groups.add(Group.objects.get(name=grupo))
        return user

    def _criar_request_com_igreja(self, user, igreja):
        request = self.factory.get('/')
        request.user = user
        request.igreja_ativa = igreja
        return request

    def _criar_cenario_local(self, username, grupo):
        from configuracao.models import Igreja, Ministerio, PerfilUsuario

        user = self._criar_usuario(username, grupo)
        administrador = User.objects.create_user(username=f'{username}-admin')
        ministerio = Ministerio.objects.create(
            nome_fantasia=f'Ministerio {username}',
            administrador_principal=administrador,
        )
        igreja_permitida = Igreja.objects.create(
            ministerio=ministerio,
            nome_igreja=f'Igreja Permitida {username}',
            tipo_igreja='congregacao',
        )
        igreja_fora = Igreja.objects.create(
            ministerio=ministerio,
            nome_igreja=f'Igreja Fora {username}',
            tipo_igreja='congregacao',
        )
        perfil = PerfilUsuario.objects.create(user=user, ministerio=ministerio)
        perfil.igrejas_permitidas.add(igreja_permitida)
        return user, igreja_permitida, igreja_fora

    def test_pastor_local_sem_modulo_retorna_false(self):
        """Pastor Local sem modulo habilitado nao acessa."""
        user = self._criar_usuario('pastor_test', PASTOR_LOCAL)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=False):
            resultado = pode_acessar_financeiro(user)

        self.assertFalse(resultado)

    def test_tesoureiro_sem_modulo_retorna_false(self):
        """Tesoureiro sem modulo habilitado nao acessa."""
        user = self._criar_usuario('tesoureiro_test', TESOUREIRO)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=False):
            resultado = pode_acessar_financeiro(user)

        self.assertFalse(resultado)

    def test_pastor_local_com_modulo_retorna_true(self):
        """Pastor Local com modulo habilitado acessa (comportamento preservado)."""
        user = self._criar_usuario('pastor_ok', PASTOR_LOCAL)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            resultado = pode_acessar_financeiro(user)

        self.assertTrue(resultado)

    def test_tesoureiro_com_modulo_retorna_true(self):
        """Tesoureiro com modulo habilitado acessa (comportamento preservado)."""
        user = self._criar_usuario('tesoureiro_ok', TESOUREIRO)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            resultado = pode_acessar_financeiro(user)

        self.assertTrue(resultado)

    def test_usuario_nao_autenticado_retorna_false(self):
        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            resultado = pode_acessar_financeiro(AnonymousUser())

        self.assertFalse(resultado)

    def test_pastor_local_com_igreja_explicita_permitida_retorna_true(self):
        user, igreja_permitida, _ = self._criar_cenario_local('pastor-contexto', PASTOR_LOCAL)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertTrue(pode_acessar_financeiro(user, igreja=igreja_permitida))

    def test_pastor_local_com_igreja_explicita_fora_do_escopo_retorna_false(self):
        user, _, igreja_fora = self._criar_cenario_local('pastor-fora', PASTOR_LOCAL)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertFalse(pode_acessar_financeiro(user, igreja=igreja_fora))

    def test_tesoureiro_com_igreja_explicita_permitida_retorna_true(self):
        user, igreja_permitida, _ = self._criar_cenario_local('tesoureiro-contexto', TESOUREIRO)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertTrue(pode_acessar_financeiro(user, igreja=igreja_permitida))

    def test_tesoureiro_com_igreja_explicita_fora_do_escopo_retorna_false(self):
        user, _, igreja_fora = self._criar_cenario_local('tesoureiro-fora', TESOUREIRO)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertFalse(pode_acessar_financeiro(user, igreja=igreja_fora))

    def test_request_igreja_ativa_permitida_retorna_true(self):
        user, igreja_permitida, _ = self._criar_cenario_local('pastor-request-ok', PASTOR_LOCAL)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertTrue(
                pode_acessar_financeiro(
                    user,
                    request=self._criar_request_com_igreja(user, igreja_permitida),
                )
            )

    def test_request_igreja_ativa_fora_do_escopo_retorna_false(self):
        user, _, igreja_fora = self._criar_cenario_local('pastor-request-fora', PASTOR_LOCAL)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertFalse(
                pode_acessar_financeiro(
                    user,
                    request=self._criar_request_com_igreja(user, igreja_fora),
                )
            )


    def test_igreja_explicita_tem_precedencia_sobre_request_igreja_ativa(self):
        user, igreja_permitida, igreja_fora = self._criar_cenario_local(
            'pastor-precedencia-contexto',
            PASTOR_LOCAL,
        )

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertTrue(
                pode_acessar_financeiro(
                    user,
                    request=self._criar_request_com_igreja(user, igreja_fora),
                    igreja=igreja_permitida,
                )
            )
            self.assertFalse(
                pode_acessar_financeiro(
                    user,
                    request=self._criar_request_com_igreja(user, igreja_permitida),
                    igreja=igreja_fora,
                )
            )
    def test_request_sem_igreja_ativa_preserva_elegibilidade_local_abstrata(self):
        user = self._criar_usuario('tesoureiro-request-sem-contexto', TESOUREIRO)
        request = self._criar_request_com_igreja(user, None)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertTrue(pode_acessar_financeiro(user, request=request))

    def test_membro_comum_mesmo_com_modulo_retorna_false(self):
        """Membro Comum nunca acessa o Financeiro."""
        user = self._criar_usuario('membro_test', MEMBRO_COMUM)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            resultado = pode_acessar_financeiro(user)

        self.assertFalse(resultado)

    def test_pessoa_igreja_nao_e_fallback_de_autorizacao_contextual(self):
        from configuracao.models import Igreja, Ministerio, PerfilUsuario
        from secretaria.models import Pessoa, StatusPessoa, TipoPessoa

        user = self._criar_usuario('pastor-pessoa-sem-perfil', PASTOR_LOCAL)
        administrador = User.objects.create_user(username='admin-pessoa-sem-perfil')
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Pessoa Sem Perfil',
            administrador_principal=administrador,
        )
        igreja = Igreja.objects.create(
            ministerio=ministerio,
            nome_igreja='Igreja da Pessoa Sem Perfil',
            tipo_igreja='congregacao',
        )
        tipo_pessoa = TipoPessoa.objects.create(nome='Tipo Pessoa Sem Perfil')
        status_pessoa = StatusPessoa.objects.create(nome='Status Pessoa Sem Perfil')
        Pessoa.objects.bulk_create([
            Pessoa(
                usuario=user,
                igreja=igreja,
                nome='Pessoa Vinculada Sem Perfil',
                tipo_pessoa=tipo_pessoa,
                status_pessoa=status_pessoa,
            )
        ])
        pessoa = Pessoa.objects.get(usuario=user)
        user.refresh_from_db()

        self.assertFalse(PerfilUsuario.objects.filter(user=user).exists())
        self.assertEqual(user.membro_secretaria.pk, pessoa.pk)
        self.assertEqual(pessoa.igreja_id, igreja.pk)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertTrue(pode_acessar_financeiro(user))
            self.assertFalse(pode_acessar_financeiro(user, igreja=pessoa.igreja))

    def test_admin_sem_igreja_concreta_retorna_false(self):
        user = self._criar_usuario('admin-sem-contexto', ADMIN_MINISTERIO)

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            self.assertFalse(pode_acessar_financeiro(user))

    def test_superuser_sem_papel_funcional_admin_retorna_false(self):
        user = User.objects.create_user(username='superuser-sem-papel', password='demo123', is_superuser=True)
        from configuracao.models import Igreja, Ministerio, PerfilUsuario

        administrador = User.objects.create_user(username='admin-do-ministerio-superuser')
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Superuser Sem Papel',
            administrador_principal=administrador,
        )
        igreja = Igreja.objects.create(
            ministerio=ministerio,
            nome_igreja='Sede Superuser Sem Papel',
            tipo_igreja='sede',
        )
        PerfilUsuario.objects.create(user=user, ministerio=ministerio)

        self.assertFalse(pode_acessar_financeiro(user, igreja=igreja))

    def _criar_perfil(self, user, ministerio):
        """Cria PerfilUsuario para o usuario no ministerio."""
        from configuracao.models import PerfilUsuario
        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={'ministerio': ministerio},
        )
        if perfil.ministerio != ministerio:
            perfil.ministerio = ministerio
            perfil.save()
        return perfil

    def test_admin_com_sede_permite_acesso(self):
        """Admin Ministerio com igreja ativa Sede permite acesso."""
        from configuracao.models import Igreja, Ministerio

        user = self._criar_usuario('admin_sede', ADMIN_MINISTERIO)
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste',
            cnpj='11.111.111/0001-11',
            cidade='Cidade Teste',
            estado='SP',
            administrador_principal=user,
        )
        self._criar_perfil(user, ministerio)
        igreja_sede = Igreja.objects.create(
            nome_igreja='Sede Teste',
            ministerio=ministerio,
            tipo_igreja='sede',
            cidade='Cidade Teste',
            estado='SP',
        )

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            request = self._criar_request_com_igreja(user, igreja_sede)
            resultado = pode_acessar_financeiro(user, request=request)

        self.assertTrue(resultado)

    def test_admin_com_independente_permite_acesso(self):
        """Admin Ministerio com igreja ativa Independente permite acesso."""
        from configuracao.models import Igreja, Ministerio

        user = self._criar_usuario('admin_ind', ADMIN_MINISTERIO)
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste Ind',
            cnpj='22.222.222/0001-22',
            cidade='Cidade Teste',
            estado='SP',
            administrador_principal=user,
        )
        self._criar_perfil(user, ministerio)
        igreja_ind = Igreja.objects.create(
            nome_igreja='Independente Teste',
            ministerio=ministerio,
            tipo_igreja='independente',
            cidade='Cidade Teste',
            estado='SP',
        )

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            request = self._criar_request_com_igreja(user, igreja_ind)
            resultado = pode_acessar_financeiro(user, request=request)

        self.assertTrue(resultado)

    def test_admin_com_regional_nega_acesso(self):
        """Admin Ministerio com igreja ativa Regional nega acesso."""
        from configuracao.models import Igreja, Ministerio

        user = self._criar_usuario('admin_reg', ADMIN_MINISTERIO)
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste Reg',
            cnpj='33.333.333/0001-33',
            cidade='Cidade Teste',
            estado='SP',
            administrador_principal=user,
        )
        self._criar_perfil(user, ministerio)
        igreja_reg = Igreja.objects.create(
            nome_igreja='Regional Teste',
            ministerio=ministerio,
            tipo_igreja='regional',
            cidade='Cidade Teste',
            estado='SP',
        )

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            request = self._criar_request_com_igreja(user, igreja_reg)
            resultado = pode_acessar_financeiro(user, request=request)

        self.assertFalse(resultado)

    def test_admin_com_congregacao_nega_acesso(self):
        """Admin Ministerio com igreja ativa Congregacao nega acesso."""
        from configuracao.models import Igreja, Ministerio

        user = self._criar_usuario('admin_cong', ADMIN_MINISTERIO)
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste Cong',
            cnpj='44.444.444/0001-44',
            cidade='Cidade Teste',
            estado='SP',
            administrador_principal=user,
        )
        self._criar_perfil(user, ministerio)
        igreja_cong = Igreja.objects.create(
            nome_igreja='Congregacao Teste',
            ministerio=ministerio,
            tipo_igreja='congregacao',
            cidade='Cidade Teste',
            estado='SP',
        )

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            request = self._criar_request_com_igreja(user, igreja_cong)
            resultado = pode_acessar_financeiro(user, request=request)

        self.assertFalse(resultado)

    def test_admin_com_igreja_fora_do_escopo_nega_acesso(self):
        """Admin Ministerio com igreja ativa fora do escopo canonico nega acesso."""
        from configuracao.models import Igreja, Ministerio

        user = self._criar_usuario('admin_fora', ADMIN_MINISTERIO)
        ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste Fora',
            cnpj='55.555.555/0001-55',
            cidade='Cidade Teste',
            estado='SP',
            administrador_principal=user,
        )
        self._criar_perfil(user, ministerio)
        outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio',
            cnpj='66.666.666/0001-66',
            cidade='Cidade Teste',
            estado='SP',
            administrador_principal=user,
        )
        igreja_fora = Igreja.objects.create(
            nome_igreja='Sede Fora',
            ministerio=outro_ministerio,
            tipo_igreja='sede',
            cidade='Cidade Teste',
            estado='SP',
        )

        with patch('contas.page_permissions.usuario_pode_usar_modulo', return_value=True):
            request = self._criar_request_com_igreja(user, igreja_fora)
            resultado = pode_acessar_financeiro(user, request=request)

        self.assertFalse(resultado)


class UserCanAccessPageDispatcherTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='dispatcher-user', password='demo123')
        self.request = RequestFactory().get('/')
        self.request.user = self.user
        self.igreja = object()

    def test_regra_comum_recebe_somente_usuario(self):
        chamadas = []

        def regra_comum(user):
            chamadas.append(user)
            return True

        with patch.dict(PAGE_ACCESS_RULES, {'regra_comum_teste': regra_comum}):
            resultado = user_can_access_page(
                self.user,
                'regra_comum_teste',
                request=self.request,
                igreja=self.igreja,
            )

        self.assertTrue(resultado)
        self.assertEqual(chamadas, [self.user])

    def test_regra_financeira_recebe_request_e_igreja(self):
        recebidos = {}

        def regra_financeira(user, request=None, igreja=None):
            recebidos.update(user=user, request=request, igreja=igreja)
            return True

        with patch.dict(PAGE_ACCESS_RULES, {'financeiro': regra_financeira}):
            resultado = user_can_access_page(
                self.user,
                'financeiro',
                request=self.request,
                igreja=self.igreja,
            )

        self.assertTrue(resultado)
        self.assertEqual(recebidos['user'], self.user)
        self.assertIs(recebidos['request'], self.request)
        self.assertIs(recebidos['igreja'], self.igreja)

    def test_chave_desconhecida_nega(self):
        self.assertFalse(user_can_access_page(self.user, 'chave_inexistente'))

    def test_typeerror_interno_de_regra_comum_e_propagado(self):
        def regra_com_bug(user):
            raise TypeError('erro interno da regra')

        with patch.dict(PAGE_ACCESS_RULES, {'regra_com_bug_teste': regra_com_bug}):
            with self.assertRaisesRegex(TypeError, 'erro interno da regra'):
                user_can_access_page(self.user, 'regra_com_bug_teste', request=self.request)

    def test_regras_contextuais_preexistentes_preservam_request_e_igreja(self):
        page_keys = (
            'dashboard_secretaria',
            'secretaria_pessoas',
            'secretaria_transferencias',
            'secretaria_cargos',
            'secretaria_grupos_casa',
            'secretaria_acompanhamentos',
            'secretaria_tags',
            'secretaria_relatorios',
            'recepcao_visitantes',
        )

        for page_key in page_keys:
            with self.subTest(page_key=page_key):
                recebidos = {}

                def regra_contextual(user, request=None, igreja=None):
                    recebidos.update(user=user, request=request, igreja=igreja)
                    return True

                with patch.dict(PAGE_ACCESS_RULES, {page_key: regra_contextual}):
                    resultado = user_can_access_page(
                        self.user,
                        page_key,
                        request=self.request,
                        igreja=self.igreja,
                    )

                self.assertTrue(resultado)
                self.assertEqual(recebidos['user'], self.user)
                self.assertIs(recebidos['request'], self.request)
                self.assertIs(recebidos['igreja'], self.igreja)
