"""
Testes de equivalencia de escopo para o provisionamento demo.

Comprova que popular_demo provisiona identidades demo com a mesma
estrutura de vinculo de um usuario real equivalente:

- Ministerial: igrejas_permitidas vazia (escopo derivado do grupo)
- Regional: apenas 1 regional explicitamente gravada (expansao canonica)
- Local: apenas 1 igreja
- Idempotencia: segunda execucao nao reintroduz escopos antigos
"""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from configuracao.models import Igreja, PerfilUsuario, Ministerio
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa
from contas.constants import (
    ADMIN_MINISTERIO,
    LIDERANCA_FINANCEIRA,
    LIDERANCA_SECRETARIA,
    PASTOR_LOCAL,
    PASTOR_REGIONAL,
    SECRETARIO_LOCAL,
    TESOUREIRO,
)
from core.utils import get_igrejas_permitidas, get_igrejas_selecionaveis

User = get_user_model()


class PopularDemoScopeTests(TestCase):
    """Valida que popular_demo provisiona escopos equivalentes aos usuarios reais."""

    @classmethod
    def setUpTestData(cls):
        call_command("popular_demo")

    def _get_perfil(self, username):
        return PerfilUsuario.objects.get(user__username=username)

    def _get_igrejas_permitidas(self, username):
        perfil = self._get_perfil(username)
        return perfil.igrejas_permitidas.count()

    def _assert_perfil_local_na_sede_demo(self, username, grupo):
        ministerio = Ministerio.objects.get(nome_fantasia="DEMONSTRAÇÃO")
        sede = Igreja.objects.get(
            ministerio=ministerio,
            nome_igreja="Igreja Sede DEMO",
        )
        user = User.objects.get(username=username)
        perfil = self._get_perfil(username)

        self.assertTrue(user.groups.filter(name=grupo).exists())
        self.assertEqual(perfil.ministerio, ministerio)
        self.assertEqual(
            list(perfil.igrejas_permitidas.values_list("pk", flat=True)),
            [sede.pk],
        )

    def test_ministerio_demo_ativo_e_marcado_como_demo_apos_reexecucao(self):
        """O ministerio Demo deve permanecer ativo e marcado como demo."""
        ministerio = Ministerio.objects.get(nome_fantasia="DEMONSTRAÇÃO")
        self.assertTrue(ministerio.is_demo)
        self.assertTrue(ministerio.ativo)

        call_command("popular_demo")

        ministerio.refresh_from_db()
        self.assertTrue(ministerio.is_demo)
        self.assertTrue(ministerio.ativo)

    # === MINISTERIAL: igrejas_permitidas vazia ===

    def test_admin_ministerial_igrejas_permitidas_vazia(self):
        """Admin Ministerio demo deve ter igrejas_permitidas vazia."""
        count = self._get_igrejas_permitidas("demo_admin")
        self.assertEqual(count, 0, "Admin ministerial deve ter igrejas_permitidas vazia")

    def test_lideranca_secretaria_igrejas_permitidas_vazia(self):
        """Secretaria Ministerial demo deve ter igrejas_permitidas vazia."""
        count = self._get_igrejas_permitidas("demo_lideranca_secretaria")
        self.assertEqual(count, 0, "Lideranca Secretaria deve ter igrejas_permitidas vazia")

    def test_lideranca_financeira_igrejas_permitidas_vazia(self):
        """Tesouraria Ministerial demo deve ter igrejas_permitidas vazia."""
        count = self._get_igrejas_permitidas("demo_lideranca_financeira")
        self.assertEqual(count, 0, "Lideranca Financeira deve ter igrejas_permitidas vazia")

    def test_ministerial_escopo_derivado_do_grupo(self):
        """Escopo ministerial e derivado do grupo, nao de igrejas_permitidas."""
        user = User.objects.get(username="demo_admin")
        igrejas = get_igrejas_selecionaveis(user)
        total_igrejas = Igreja.objects.filter(ministerio__nome_fantasia="DEMONSTRAÇÃO").count()
        self.assertEqual(igrejas.count(), total_igrejas)

    # === REGIONAL: 1 regional + expansao canonica ===

    def test_pastor_regional_apenas_1_regional_explicita(self):
        """Pastor Regional demo deve ter apenas 1 regional em igrejas_permitidas."""
        perfil = self._get_perfil("demo_pastor_regional")
        igrejas = perfil.igrejas_permitidas.all()
        self.assertEqual(igrejas.count(), 1)
        self.assertEqual(igrejas.first().tipo_igreja, "regional")

    def test_pastor_regional_expansao_canonica(self):
        """Pastor Regional: expansao canonica retorna regional + subordinadas."""
        user = User.objects.get(username="demo_pastor_regional")
        igrejas = get_igrejas_permitidas(user)
        # 1 regional + 3 congregacoes subordinadas = 4
        self.assertEqual(igrejas.count(), 4)

    # === LOCAL: apenas 1 igreja ===

    def test_pastor_local_apenas_1_igreja(self):
        """Pastor Local demo deve ter apenas 1 igreja em igrejas_permitidas."""
        count = self._get_igrejas_permitidas("demo_pastor_local")
        self.assertEqual(count, 1)

    def test_tesoureiro_local_na_sede_demo(self):
        """O tesoureiro canonico demo_tesoureiro deve ter escopo local na sede."""
        self._assert_perfil_local_na_sede_demo("demo_tesoureiro", TESOUREIRO)

    def test_secretario_local_na_sede_demo_apos_reexecucao(self):
        """Secretario Local deve manter exatamente a Sede Demo apos reexecucao."""
        self._assert_perfil_local_na_sede_demo(
            "demo_secretario_local",
            SECRETARIO_LOCAL,
        )

        call_command("popular_demo")

        self._assert_perfil_local_na_sede_demo(
            "demo_secretario_local",
            SECRETARIO_LOCAL,
        )

    def test_alias_demo_pastor_na_sede_demo_apos_reexecucao(self):
        """Alias demo_pastor deve manter exatamente a Sede Demo apos reexecucao."""
        self._assert_perfil_local_na_sede_demo("demo_pastor", PASTOR_LOCAL)

        call_command("popular_demo")

        self._assert_perfil_local_na_sede_demo("demo_pastor", PASTOR_LOCAL)

    def test_membro_apenas_1_igreja(self):
        """Membro Comum demo deve ter apenas 1 igreja em igrejas_permitidas."""
        count = self._get_igrejas_permitidas("demo_membro")
        self.assertEqual(count, 1)

    # === IDEMPOTENCIA: segunda execucao nao reintroduz escopos antigos ===

    def test_idempotencia_ministerial(self):
        """Segunda execucao nao reintroduz igrejas em perfil ministerial."""
        # Executa popular_demo novamente
        call_command("popular_demo")

        # Ministerial continua com igrejas_permitidas vazia
        for username in ["demo_admin", "demo_lideranca_secretaria", "demo_lideranca_financeira"]:
            count = self._get_igrejas_permitidas(username)
            self.assertEqual(count, 0, f"{username} deve manter igrejas_permitidas vazia apos re-execucao")

    def test_idempotencia_regional(self):
        """Segunda execucao mantem apenas 1 regional."""
        call_command("popular_demo")
        perfil = self._get_perfil("demo_pastor_regional")
        self.assertEqual(perfil.igrejas_permitidas.count(), 1)

    def test_idempotencia_local(self):
        """Segunda execucao mantem apenas 1 igreja para perfis locais."""
        call_command("popular_demo")
        for username in [
            "demo_pastor_local",
            "demo_secretario_local",
            "demo_tesoureiro",
            "demo_membro",
            "demo_pastor",
        ]:
            count = self._get_igrejas_permitidas(username)
            self.assertEqual(count, 1, f"{username} deve manter 1 igreja apos re-execucao")

class PopularDemoTenantIsolationTests(TestCase):
    """Valida que o vinculo de demo_membro nao atravessa tenants."""

    def test_pessoa_demo_de_outro_tenant_nao_recebe_usuario_demo(self):
        """Uma Pessoa de outro ministerio nunca pode receber demo_membro."""
        administrador_real = User.objects.create_user(
            username="admin_ministerio_real",
            password="senha-segura",
        )
        ministerio_real = Ministerio.objects.create(
            nome_fantasia="Ministerio Real A",
            cnpj="11.111.111/0001-11",
            cidade="Cidade Real",
            estado="SP",
            administrador_principal=administrador_real,
        )
        igreja_real = Igreja.objects.create(
            ministerio=ministerio_real,
            nome_igreja="Igreja Real A",
            tipo_igreja="sede",
            cidade="Cidade Real",
            estado="SP",
        )
        tipo_membro, _ = TipoPessoa.objects.get_or_create(nome="Membro")
        status_ativo, _ = StatusPessoa.objects.get_or_create(nome="Ativo")
        pessoa_outro_tenant = Pessoa.objects.create(
            nome="Pessoa Real Com Email Demo",
            igreja=igreja_real,
            cpf="111.111.111-11",
            email="pessoa.real@demo.com",
            tipo_pessoa=tipo_membro,
            status_pessoa=status_ativo,
        )

        call_command("popular_demo")

        pessoa_outro_tenant.refresh_from_db()
        self.assertIsNone(pessoa_outro_tenant.usuario)
        pessoa_demo = Pessoa.objects.get(
            usuario__username="demo_membro",
        )
        self.assertEqual(pessoa_demo.igreja.ministerio.nome_fantasia, "DEMONSTRAÇÃO")
        self.assertNotEqual(pessoa_demo.pk, pessoa_outro_tenant.pk)
