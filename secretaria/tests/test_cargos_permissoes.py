from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase

from core.group_sync import recalcular_grupos_efetivos_usuario
from configuracao.models import Igreja, Ministerio
from secretaria.models import Cargo, Membro, MembroCargo, StatusPessoa, TipoPessoa


class CargoPermissaoSignalsTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(username='admin_cargos', password='pass')
        self.usuario = user_model.objects.create_user(username='usuario_cargo', password='pass')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Teste Cargos',
            administrador_principal=self.admin,
        )
        self.igreja = Igreja.objects.create(
            nome_igreja='Igreja Teste Cargos',
            ministerio=self.ministerio,
        )
        self.tipo = TipoPessoa.objects.create(nome='Membro')
        self.status = StatusPessoa.objects.create(nome='Ativo')
        self.grupo = Group.objects.create(name='Grupo Cargo Teste')
        self.membro = Membro.objects.create(
            nome='Membro Teste',
            igreja=self.igreja,
            tipo_pessoa=self.tipo,
            status_pessoa=self.status,
            usuario=self.usuario,
        )

    def test_adiciona_grupo_quando_cargo_ativo_e_criado(self):
        cargo = Cargo.objects.create(nome='Cargo Ativo', grupo_permissao=self.grupo)

        MembroCargo.objects.create(
            membro=self.membro,
            cargo=cargo,
            data_inicio=date.today(),
        )

        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.groups.filter(pk=self.grupo.pk).exists())

    def test_remove_grupo_quando_cargo_e_inativado(self):
        cargo = Cargo.objects.create(nome='Cargo Inativavel', grupo_permissao=self.grupo)
        vinculo = MembroCargo.objects.create(
            membro=self.membro,
            cargo=cargo,
            data_inicio=date.today(),
        )

        vinculo.data_fim = date.today()
        vinculo.save()

        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.groups.filter(pk=self.grupo.pk).exists())

    def test_mantem_grupo_se_existe_outro_cargo_ativo_com_mesmo_grupo(self):
        cargo_1 = Cargo.objects.create(nome='Cargo Multiplo 1', grupo_permissao=self.grupo)
        cargo_2 = Cargo.objects.create(nome='Cargo Multiplo 2', grupo_permissao=self.grupo)
        vinculo_1 = MembroCargo.objects.create(
            membro=self.membro,
            cargo=cargo_1,
            data_inicio=date.today(),
        )
        MembroCargo.objects.create(
            membro=self.membro,
            cargo=cargo_2,
            data_inicio=date.today(),
        )

        vinculo_1.data_fim = date.today()
        vinculo_1.save()

        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.groups.filter(pk=self.grupo.pk).exists())

    def test_preserva_grupo_manual_quando_cargo_e_inativado(self):
        grupo_manual = Group.objects.create(name='Grupo Manual Teste')
        cargo = Cargo.objects.create(nome='Cargo Manual + Cargo', grupo_permissao=self.grupo)
        vinculo = MembroCargo.objects.create(
            membro=self.membro,
            cargo=cargo,
            data_inicio=date.today(),
        )
        self.usuario.groups.add(grupo_manual)

        vinculo.data_fim = date.today()
        vinculo.save()

        self.usuario.refresh_from_db()
        self.assertFalse(self.usuario.groups.filter(pk=self.grupo.pk).exists())
        self.assertTrue(self.usuario.groups.filter(pk=grupo_manual.pk).exists())

    def test_recalculo_manual_nao_remove_grupo_vindo_de_cargo(self):
        grupo_manual = Group.objects.create(name='Grupo Manual Recalculo')
        cargo = Cargo.objects.create(nome='Cargo Recalculo', grupo_permissao=self.grupo)
        MembroCargo.objects.create(
            membro=self.membro,
            cargo=cargo,
            data_inicio=date.today(),
        )

        recalcular_grupos_efetivos_usuario(
            self.usuario,
            grupos_manuais=[grupo_manual],
            grupos_editaveis=Group.objects.all(),
        )

        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.groups.filter(pk=self.grupo.pk).exists())
        self.assertTrue(self.usuario.groups.filter(pk=grupo_manual.pk).exists())
