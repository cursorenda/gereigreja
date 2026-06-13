from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import SECRETARIO_LOCAL
from secretaria.models import Membro, StatusPessoa, TipoPessoa


class SecretariaEdicaoConcorrenciaTests(TestCase):
    def setUp(self):
        user_model = get_user_model()

        self.usuario = user_model.objects.create_user(
            username="secretario_concorrencia",
            email="secretario.concorrencia@example.com",
            password="senha123",
        )
        grupo_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.usuario.groups.add(grupo_secretario)

        # Nome de demonstracao libera validacoes de plano/modulo em ambiente de teste.
        self.ministerio = Ministerio.objects.create(
            nome_fantasia="demonstracao",
            administrador_principal=self.usuario,
            ativo=True,
            cnpj="11.111.111/0001-11",
        )

        self.igreja = Igreja.objects.create(
            nome_igreja="Igreja Concorrencia",
            ministerio=self.ministerio,
            tipo_igreja="sede",
        )

        perfil = PerfilUsuario.objects.create(user=self.usuario, ministerio=self.ministerio)
        perfil.igrejas_permitidas.set([self.igreja])

        self.tipo_membro = TipoPessoa.objects.create(nome="Membro")
        self.status_ativo = StatusPessoa.objects.create(nome="Ativo")

        self.membro = Membro.objects.create(
            nome="Membro Original",
            genero="M",
            igreja=self.igreja,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
            tipo_entrada="BATISMO",
            grau_eclesiastico="membro_comum",
        )

    def test_editar_membro_bloqueia_quando_token_de_atualizacao_esta_desatualizado(self):
        self.client.force_login(self.usuario)

        token_desatualizado = str(int(self.membro.atualizado_em.timestamp()))

        # Simula outro usuario/sessao salvando o cadastro antes do POST atual.
        self.membro.nome = "Atualizado por outra sessao"
        self.membro.save()

        url = reverse("secretaria:editar_membro", args=[self.membro.pk])
        payload = {
            "submit_membro_form": "_save",
            "_last_updated_epoch": token_desatualizado,
            "igreja": str(self.igreja.pk),
            "nome": "Tentativa com token stale",
            "genero": "M",
            "tipo_pessoa": str(self.tipo_membro.pk),
            "status_pessoa": str(self.status_ativo.pk),
            "tipo_entrada": "BATISMO",
            "grau_eclesiastico": "membro_comum",
        }

        response = self.client.post(url, data=payload, follow=True)

        self.assertEqual(response.status_code, 200)
        self.membro.refresh_from_db()
        self.assertEqual(self.membro.nome, "Atualizado por outra sessao")

        mensagens = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertTrue(
            any("atualizado por outro usuario" in msg.lower() for msg in mensagens),
            mensagens,
        )