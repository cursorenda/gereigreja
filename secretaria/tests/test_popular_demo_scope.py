"""Testes de isolamento de tenant do provisionamento Demo."""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from configuracao.models import Igreja, Ministerio
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


User = get_user_model()


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
        pessoa_demo = Pessoa.objects.get(usuario__username="demo_membro")
        self.assertEqual(pessoa_demo.igreja.ministerio.nome_fantasia, "DEMONSTRAÇÃO")
        self.assertNotEqual(pessoa_demo.pk, pessoa_outro_tenant.pk)
