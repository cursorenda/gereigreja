import os
import tempfile
from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from openpyxl import Workbook
from secretaria.models import Pessoa, Igreja, StatusPessoa, TipoPessoa

class ImportacaoPessoasTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='1234', is_staff=True)
        perm = Permission.objects.get(codename='add_pessoa')
        self.user.user_permissions.add(perm)
        self.client = Client()
        self.client.login(username='admin', password='1234')
        from configuracao.models import Ministerio
        self.ministerio = Ministerio.objects.create(nome_fantasia='Ministério Teste', administrador_principal=self.user)
        self.igreja = Igreja.objects.create(nome_igreja='Central', ministerio=self.ministerio)
        self.status = StatusPessoa.objects.create(nome='Ativo')
        self.tipo = TipoPessoa.objects.create(nome='Membro')

    def gerar_excel(self, linhas):
        wb = Workbook()
        ws = wb.active
        ws.title = "Pessoas"
        ws.append([
            "CPF", "Nome", "Nome do Pai", "Nome da Mãe", "Data de Nascimento", "Gênero", "Igreja", "Status", "Tipo",
            "Rua", "Número", "Bairro", "Cidade", "Estado", "Telefone", "E-mail"
        ])
        for linha in linhas:
            ws.append(linha)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        wb.save(tmp.name)
        tmp.seek(0)
        return tmp

    def test_importacao_sucesso(self):
        dados = [
            ["123.456.789-09", "João Teste", "Pai", "Mãe", "01/01/1990", "M", "Central", "Ativo", "Membro",
             "Rua A", "100", "Centro", "CidadeX", "SP", "(11) 99999-9999", "joao@teste.com"]
        ]
        tmp = self.gerar_excel(dados)
        with open(tmp.name, 'rb') as f:
            resp = self.client.post(reverse('secretaria:importar_pessoas'), {'arquivo': f})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Pessoa.objects.filter(nome="João Teste").exists())
        os.unlink(tmp.name)

    def test_importacao_erro_cpf(self):
        dados = [
            ["111.111.111-11", "Erro CPF", "Pai", "Mãe", "01/01/1990", "M", "Central", "Ativo", "Membro",
             "Rua A", "100", "Centro", "CidadeX", "SP", "(11) 99999-9999", "erro@teste.com"]
        ]
        tmp = self.gerar_excel(dados)
        with open(tmp.name, 'rb') as f:
            resp = self.client.post(reverse('secretaria:importar_pessoas'), {'arquivo': f})
        self.assertContains(resp, 'CPF inválido', status_code=200)
        os.unlink(tmp.name)

    def test_importacao_atualiza_existente(self):
        Pessoa.objects.create(
            cpf="123.456.789-09", nome="Antigo", igreja=self.igreja, status_pessoa=self.status, tipo_pessoa=self.tipo
        )
        dados = [
            ["123.456.789-09", "Novo Nome", "Pai", "Mãe", "01/01/1990", "M", "Central", "Ativo", "Membro",
             "Rua B", "200", "BairroY", "CidadeY", "SP", "(11) 98888-8888", "novo@teste.com"]
        ]
        tmp = self.gerar_excel(dados)
        with open(tmp.name, 'rb') as f:
            resp = self.client.post(reverse('secretaria:importar_pessoas'), {'arquivo': f})
        self.assertEqual(resp.status_code, 302)
        pessoa = Pessoa.objects.get(cpf="123.456.789-09")
        self.assertEqual(pessoa.nome, "Novo Nome")
        self.assertEqual(pessoa.rua, "Rua B")
        os.unlink(tmp.name)

    def test_importacao_erro_data(self):
        dados = [
            ["123.456.789-09", "Data Errada", "Pai", "Mãe", "1990-01-01", "M", "Central", "Ativo", "Membro",
             "Rua A", "100", "Centro", "CidadeX", "SP", "(11) 99999-9999", "data@teste.com"]
        ]
        tmp = self.gerar_excel(dados)
        with open(tmp.name, 'rb') as f:
            resp = self.client.post(reverse('secretaria:importar_pessoas'), {'arquivo': f})
        self.assertContains(resp, 'Data de nascimento deve estar no formato dd/mm/aaaa', status_code=200)
        os.unlink(tmp.name)
