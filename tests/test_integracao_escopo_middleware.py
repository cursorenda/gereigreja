from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import SECRETARIO_LOCAL
from eventos.models import Evento
from secretaria.models import Membro, StatusPessoa, TipoPessoa


class EscopoMiddlewareIntegracaoTest(TestCase):
    def setUp(self):
        User = get_user_model()

        self.admin = User.objects.create_user(
            username="admin_ministerio_teste",
            email="admin_teste@example.com",
            password="senha123",
        )

        self.ministerio = Ministerio.objects.create(
            nome_fantasia="Ministerio Integracao",
            administrador_principal=self.admin,
            ativo=True,
            cnpj="12345678000199",
        )

        self.igreja_a = Igreja.objects.create(
            nome_igreja="Igreja A",
            ministerio=self.ministerio,
            tipo_igreja="sede",
        )
        self.igreja_b = Igreja.objects.create(
            nome_igreja="Igreja B",
            ministerio=self.ministerio,
            tipo_igreja="congregacao",
        )

        self.grupo_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)

        self.usuario_escopo_a = User.objects.create_user(
            username="usuario_escopo_a",
            email="escopo_a@example.com",
            password="senha123",
        )
        self.usuario_escopo_a.groups.add(self.grupo_secretario)

        self.perfil_escopo_a = PerfilUsuario.objects.create(
            user=self.usuario_escopo_a,
            ministerio=self.ministerio,
        )
        self.perfil_escopo_a.igrejas_permitidas.set([self.igreja_a])

        self.tipo_membro = TipoPessoa.objects.create(nome="Membro")
        self.tipo_visitante = TipoPessoa.objects.create(nome="Visitante")
        self.status_ativo = StatusPessoa.objects.create(nome="Ativo")

        self.membro_a = Membro.objects.create(
            nome="Membro Igreja A",
            igreja=self.igreja_a,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        self.membro_b = Membro.objects.create(
            nome="Membro Igreja B",
            igreja=self.igreja_b,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )

        self.usuario_responsavel_a = User.objects.create_user(
            username="responsavel_a",
            email="responsavel_a@example.com",
            password="senha123",
        )
        PerfilUsuario.objects.create(
            user=self.usuario_responsavel_a,
            ministerio=self.ministerio,
        )
        Membro.objects.create(
            nome="Responsavel Igreja A",
            igreja=self.igreja_a,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            usuario=self.usuario_responsavel_a,
        )

        agora = timezone.now()
        self.evento_a = Evento.objects.create(
            igreja=self.igreja_a,
            titulo="Evento Igreja A",
            tipo="culto",
            data_inicio=agora,
            criado_por=self.usuario_escopo_a,
        )
        self.evento_b = Evento.objects.create(
            igreja=self.igreja_b,
            titulo="Evento Igreja B",
            tipo="culto",
            data_inicio=agora,
            criado_por=self.usuario_escopo_a,
        )

        self.client.force_login(self.usuario_escopo_a)

    def test_middleware_define_igreja_ativa_automaticamente_quando_ha_uma_permitida(self):
        session = self.client.session
        session.pop("igreja_ativa_id", None)
        session.save()

        response = self.client.get(
            reverse("eventos:autocomplete_convidados"),
            {"filtro": "todos"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("igreja_ativa_id"), self.igreja_a.pk)

    def test_autocomplete_convidados_retorna_apenas_escopo_permitido(self):
        response = self.client.get(
            reverse("eventos:autocomplete_convidados"),
            {"filtro": "todos"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        nomes = {p["nome"] for p in payload.get("pessoas", [])}
        self.assertIn("Membro Igreja A", nomes)
        self.assertNotIn("Membro Igreja B", nomes)

    def test_autocomplete_convidados_bloqueia_igreja_fora_do_escopo(self):
        response = self.client.get(
            reverse("eventos:autocomplete_convidados"),
            {"filtro": "todos", "igreja": self.igreja_b.pk},
        )

        self.assertEqual(response.status_code, 403)

    def test_autocomplete_responsaveis_retorna_usuarios_da_igreja_permitida(self):
        response = self.client.get(
            reverse("eventos:autocomplete_responsaveis"),
            {"igreja_id": self.igreja_a.pk},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        ids = {item["id"] for item in payload.get("responsaveis", [])}
        self.assertIn(self.usuario_responsavel_a.pk, ids)

    def test_autocomplete_responsaveis_bloqueia_igreja_fora_do_escopo(self):
        response = self.client.get(
            reverse("eventos:autocomplete_responsaveis"),
            {"igreja_id": self.igreja_b.pk},
        )

        self.assertEqual(response.status_code, 403)

    def test_detalhe_evento_bloqueia_objeto_de_igreja_fora_do_escopo(self):
        response = self.client.get(reverse("eventos:detalhe_evento", args=[self.evento_b.pk]))
        self.assertEqual(response.status_code, 404)

    def test_exportar_participantes_bloqueia_evento_fora_do_escopo(self):
        response = self.client.get(reverse("eventos:exportar_participantes_excel", args=[self.evento_b.pk]))
        self.assertEqual(response.status_code, 404)

    def test_exportar_participantes_permitido_no_escopo(self):
        response = self.client.get(reverse("eventos:exportar_participantes_excel", args=[self.evento_a.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
