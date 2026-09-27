from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from configuracao.models import Departamento, DepartamentoVinculo, Igreja, Ministerio
from configuracao.templatetags.departamento_tags import usuario_tem_departamento_ativo
from secretaria.models import Pessoa, StatusPessoa, TipoPessoa


class UsuarioTemDepartamentoAtivoTagTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='usuario-tag-departamento')
        self.outro_user = User.objects.create_user(username='outro-usuario-tag-departamento')
        self.sem_pessoa = User.objects.create_user(username='sem-pessoa-tag-departamento')
        self.admin = User.objects.create_user(username='admin-tag-departamento')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Tag Departamento',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Tag Departamento',
        )
        tipo = TipoPessoa.objects.create(nome='Membro Tag Departamento')
        status = StatusPessoa.objects.create(nome='Ativo Tag Departamento')
        self.pessoa = Pessoa.objects.create(
            usuario=self.user,
            igreja=self.igreja,
            nome='Pessoa Tag Departamento',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        self.outra_pessoa = Pessoa.objects.create(
            usuario=self.outro_user,
            igreja=self.igreja,
            nome='Outra Pessoa Tag Departamento',
            tipo_pessoa=tipo,
            status_pessoa=status,
        )
        self.departamento = Departamento.objects.get(igreja=self.igreja, codigo_interno='MISSOES')
        self.outro_departamento = Departamento.objects.get(igreja=self.igreja, codigo_interno='ASSISTENCIA')

    def _criar_vinculo(self, *, membro=None, departamento=None, data_fim=None):
        return DepartamentoVinculo.objects.create(
            membro=membro or self.pessoa,
            departamento=departamento or self.departamento,
            data_fim=data_fim,
        )

    def test_usuario_nao_autenticado_retorna_false(self):
        self.assertFalse(usuario_tem_departamento_ativo(None))

    def test_usuario_sem_pessoa_retorna_false(self):
        self.assertFalse(usuario_tem_departamento_ativo(self.sem_pessoa))

    def test_pessoa_sem_vinculo_retorna_false(self):
        self.assertFalse(usuario_tem_departamento_ativo(self.user))

    def test_somente_vinculo_encerrado_retorna_false(self):
        self._criar_vinculo(data_fim=date.today())
        self.assertFalse(usuario_tem_departamento_ativo(self.user))

    def test_vinculo_ativo_proprio_retorna_true(self):
        self._criar_vinculo()
        self.assertTrue(usuario_tem_departamento_ativo(self.user))

    def test_multiplos_vinculos_ativos_proprios_retornam_true(self):
        self._criar_vinculo()
        self._criar_vinculo(departamento=self.outro_departamento)
        self.assertTrue(usuario_tem_departamento_ativo(self.user))

    def test_vinculo_ativo_de_outro_usuario_nao_influencia(self):
        self._criar_vinculo(membro=self.outra_pessoa)
        self.assertFalse(usuario_tem_departamento_ativo(self.user))

    def test_grupo_sem_vinculo_ativo_retorna_false(self):
        grupo = Group.objects.create(name='Grupo Sem Vinculo Departamental')
        self.user.groups.add(grupo)
        self.assertFalse(usuario_tem_departamento_ativo(self.user))