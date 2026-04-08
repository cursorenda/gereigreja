from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import SECRETARIO_LOCAL, TESOUREIRO
from financeiro.models import ContaBancaria, Receitas
from secretaria.models import Membro, StatusPessoa, TipoPessoa


class EscopoSecretariaFinanceiroIntegracaoTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_user(
            username="admin_integracao_sf",
            email="admin_sf@example.com",
            password="senha123",
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia="Ministerio Integracao SF",
            administrador_principal=self.admin,
            ativo=True,
            cnpj="12345678000188",
        )

        self.igreja_a = Igreja.objects.create(
            nome_igreja="Igreja A SF",
            ministerio=self.ministerio,
            tipo_igreja="sede",
        )
        self.igreja_b = Igreja.objects.create(
            nome_igreja="Igreja B SF",
            ministerio=self.ministerio,
            tipo_igreja="congregacao",
        )

        self.grupo_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.grupo_tesoureiro, _ = Group.objects.get_or_create(name=TESOUREIRO)

        self.usuario_secretaria = User.objects.create_user(
            username="usuario_secretaria_sf",
            email="secretaria_sf@example.com",
            password="senha123",
        )
        self.usuario_secretaria.groups.add(self.grupo_secretario)

        perfil_secretaria = PerfilUsuario.objects.create(
            user=self.usuario_secretaria,
            ministerio=self.ministerio,
        )
        perfil_secretaria.igrejas_permitidas.set([self.igreja_a])

        self.usuario_financeiro = User.objects.create_user(
            username="usuario_financeiro_sf",
            email="financeiro_sf@example.com",
            password="senha123",
        )
        self.usuario_financeiro.groups.add(self.grupo_tesoureiro)

        perfil_financeiro = PerfilUsuario.objects.create(
            user=self.usuario_financeiro,
            ministerio=self.ministerio,
        )
        perfil_financeiro.igrejas_permitidas.set([self.igreja_a])

        self.tipo_membro = TipoPessoa.objects.create(nome="Membro SF")
        self.status_ativo = StatusPessoa.objects.create(nome="Ativo SF")

        self.membro_a = Membro.objects.create(
            nome="Membro A SF",
            igreja=self.igreja_a,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        self.membro_b = Membro.objects.create(
            nome="Membro B SF",
            igreja=self.igreja_b,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )

        self.conta_a = ContaBancaria.objects.create(
            igreja=self.igreja_a,
            nome_identificacao="Conta A SF",
            tipo="caixa_fisico",
            saldo_inicial=0,
        )
        self.conta_b = ContaBancaria.objects.create(
            igreja=self.igreja_b,
            nome_identificacao="Conta B SF",
            tipo="caixa_fisico",
            saldo_inicial=0,
        )

        Receitas.objects.create(
            igreja=self.igreja_a,
            categoria="oferta",
            data="2026-04-01",
            valor=Decimal("100.00"),
            membro=self.membro_a,
            conta_bancaria=self.conta_a,
            fechado=False,
        )
        Receitas.objects.create(
            igreja=self.igreja_b,
            categoria="oferta",
            data="2026-04-01",
            valor=Decimal("200.00"),
            membro=self.membro_b,
            conta_bancaria=self.conta_b,
            fechado=False,
        )

    def test_secretaria_detalhe_membro_permitido_no_escopo(self):
        self.client.force_login(self.usuario_secretaria)

        response = self.client.get(reverse("secretaria:detalhe_membro", args=[self.membro_a.pk]))

        self.assertEqual(response.status_code, 200)

    def test_secretaria_detalhe_membro_fora_escopo_retorna_404(self):
        self.client.force_login(self.usuario_secretaria)

        response = self.client.get(reverse("secretaria:detalhe_membro", args=[self.membro_b.pk]))

        self.assertEqual(response.status_code, 404)

    def test_financeiro_lista_receitas_retorna_apenas_igreja_permitida(self):
        self.client.force_login(self.usuario_financeiro)

        response = self.client.get(reverse("financeiro:lista_receitas"))

        self.assertEqual(response.status_code, 200)
        receitas_ids_igreja = set(response.context["receitas"].values_list("igreja_id", flat=True))
        self.assertEqual(receitas_ids_igreja, {self.igreja_a.pk})

    def test_financeiro_lista_contas_bancarias_retorna_apenas_igreja_permitida(self):
        self.client.force_login(self.usuario_financeiro)

        response = self.client.get(reverse("financeiro:lista_contas_bancarias"))

        self.assertEqual(response.status_code, 200)
        contas_ids_igreja = set(response.context["contas_bancarias"].values_list("igreja_id", flat=True))
        self.assertEqual(contas_ids_igreja, {self.igreja_a.pk})
