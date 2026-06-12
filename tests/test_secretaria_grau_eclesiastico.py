from django.contrib.auth.models import User
from django.test import TestCase

from configuracao.models import Igreja, Ministerio
from secretaria.forms import MembroForm
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


class SecretariaGrauEclesiasticoTests(TestCase):
    def setUp(self):
        self.admin_ministerio = User.objects.create_user(
            username="admin_ministerio_grau",
            email="admin.ministerio.grau@example.com",
            password="123",
        )
        self.ministerio = Ministerio.objects.create(
            nome_fantasia="Ministerio Teste",
            razao_social="Ministerio Teste LTDA",
            administrador_principal=self.admin_ministerio,
            cnpj="11.111.111/0001-11",
            email="ministerio.teste@example.com",
            telefone="11999999999",
            rua="Rua A",
            numero="100",
            bairro="Centro",
            cidade="Sao Paulo",
            estado="SP",
            cep="01000-000",
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja="Igreja Teste",
            cnpj="22.222.222/0001-22",
            pastor_local="Pastor Teste",
            telefone="11988888888",
            email="igreja.teste@example.com",
            rua="Rua B",
            numero_casa="50",
            bairro_distrito="Centro",
            cidade="Sao Paulo",
            estado="SP",
            cep="02000-000",
        )
        self.tipo_membro = TipoPessoa.objects.create(nome="Membro")
        self.tipo_visitante = TipoPessoa.objects.create(nome="Visitante")
        self.status_ativo = StatusPessoa.objects.create(nome="Ativo")

    def _base_form_data(self, tipo_pessoa_id):
        return {
            "igreja": str(self.igreja.pk),
            "nome": "Pessoa Teste",
            "genero": "M",
            "tipo_pessoa": str(tipo_pessoa_id),
            "status_pessoa": str(self.status_ativo.pk),
        }

    def test_form_define_null_para_nao_membro(self):
        data = self._base_form_data(self.tipo_visitante.pk)
        data.update(
            {
                "grau_eclesiastico": "pastor",
                "tipo_entrada": "BATISMO",
            }
        )

        form = MembroForm(data, ministerio=self.ministerio)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertIsNone(form.cleaned_data["grau_eclesiastico"])
        self.assertIsNone(form.cleaned_data["tipo_entrada"])

        pessoa = form.save()
        self.assertIsNone(pessoa.grau_eclesiastico)

    def test_form_membro_sem_grau_assume_membro_comum(self):
        data = self._base_form_data(self.tipo_membro.pk)
        data.update(
            {
                "tipo_entrada": "BATISMO",
                "grau_eclesiastico": "",
            }
        )

        form = MembroForm(data, ministerio=self.ministerio)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["grau_eclesiastico"], "membro_comum")

        pessoa = form.save()
        self.assertEqual(pessoa.grau_eclesiastico, "membro_comum")

    def test_model_forca_null_quando_tipo_nao_e_membro(self):
        pessoa = Pessoa.objects.create(
            nome="Visitante Persistencia",
            genero="M",
            igreja=self.igreja,
            tipo_pessoa=self.tipo_visitante,
            status_pessoa=self.status_ativo,
            grau_eclesiastico="presbitero",
        )

        pessoa.refresh_from_db()
        self.assertIsNone(pessoa.grau_eclesiastico)
