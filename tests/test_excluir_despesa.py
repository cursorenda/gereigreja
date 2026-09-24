from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from contas.constants import PASTOR_LOCAL
from configuracao.models import Igreja, Ministerio, PerfilUsuario, Plano
from financeiro.models import CategoriaDespesa, ContaBancaria, Despesas


class ExcluirDespesaViewTest(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(username='admin-excluir-despesa')
        self.pastor = user_model.objects.create_user(username='pastor-excluir-despesa')
        self.sem_escopo = user_model.objects.create_user(username='sem-escopo-excluir-despesa')

        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Exclusao Despesa',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja_permitida = Igreja.objects.create(
            nome_igreja='Igreja Permitida Exclusao',
            ministerio=self.ministerio,
            tipo_igreja='sede',
        )
        self.igreja_mesmo_ministerio = Igreja.objects.create(
            nome_igreja='Igreja Fora do Escopo Exclusao',
            ministerio=self.ministerio,
            tipo_igreja='independente',
        )

        self.outro_admin = user_model.objects.create_user(username='admin-outro-excluir-despesa')
        self.outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Exclusao Despesa',
            administrador_principal=self.outro_admin,
            ativo=True,
        )
        self.igreja_outro_ministerio = Igreja.objects.create(
            nome_igreja='Igreja Outro Ministerio Exclusao',
            ministerio=self.outro_ministerio,
            tipo_igreja='sede',
        )

        self.perfil_pastor = PerfilUsuario.objects.create(
            user=self.pastor,
            ministerio=self.ministerio,
        )
        self.perfil_pastor.igrejas_permitidas.add(self.igreja_permitida)
        PerfilUsuario.objects.create(user=self.sem_escopo, ministerio=self.ministerio)

        grupo_pastor, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        self.pastor.groups.add(grupo_pastor)

        Plano.objects.get_or_create(
            nome='pioneiro',
            defaults={
                'codigo_plano': 'pioneiro',
                'permite_modulo_financeiro': True,
                'ativo': True,
            },
        )

        self.categoria = CategoriaDespesa.objects.create(
            ministerio=self.ministerio,
            nome='Categoria Exclusao Despesa',
        )
        self.categoria_outro_ministerio = CategoriaDespesa.objects.create(
            ministerio=self.outro_ministerio,
            nome='Categoria Outro Ministerio Exclusao',
        )
        self.conta_permitida = self._criar_conta(self.igreja_permitida, 'Caixa Permitido Exclusao')
        self.conta_mesmo_ministerio = self._criar_conta(
            self.igreja_mesmo_ministerio,
            'Caixa Mesmo Ministerio Exclusao',
        )
        self.conta_outro_ministerio = self._criar_conta(
            self.igreja_outro_ministerio,
            'Caixa Outro Ministerio Exclusao',
        )

    def _criar_conta(self, igreja, nome):
        return ContaBancaria.objects.create(
            igreja=igreja,
            nome_identificacao=nome,
            tipo='caixa_fisico',
            saldo_inicial=Decimal('100.00'),
        )

    def _criar_despesa(self, igreja, conta, *, fechado=False, descricao='Despesa para exclusao'):
        categoria = self.categoria if igreja.ministerio_id == self.ministerio.id else self.categoria_outro_ministerio
        return Despesas.objects.create(
            igreja=igreja,
            data=date(2026, 9, 24),
            descricao=descricao,
            valor=Decimal('10.00'),
            categoria=categoria,
            conta_bancaria=conta,
            fechado=fechado,
        )

    def _autenticar_com_igreja_ativa(self, usuario, igreja):
        self.client.force_login(usuario)
        session = self.client.session
        session['igreja_ativa_id'] = igreja.pk
        session.save()

    def test_post_permitido_exclui_despesa_aberta_retorna_redirect_e_reverte_saldo(self):
        despesa = self._criar_despesa(
            self.igreja_permitida,
            self.conta_permitida,
            descricao='Despesa permitida',
        )
        self._autenticar_com_igreja_ativa(self.pastor, self.igreja_permitida)

        response = self.client.post(reverse('financeiro:excluir_despesa', args=[despesa.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('financeiro:lista_despesas'))
        self.assertFalse(Despesas.objects.filter(pk=despesa.pk).exists())
        self.conta_permitida.refresh_from_db()
        self.assertEqual(self.conta_permitida.saldo_atual, Decimal('100.00'))

    def test_post_mesmo_ministerio_fora_do_escopo_nao_exclui(self):
        despesa = self._criar_despesa(
            self.igreja_mesmo_ministerio,
            self.conta_mesmo_ministerio,
            descricao='Despesa mesmo ministerio fora do escopo',
        )
        self._autenticar_com_igreja_ativa(self.pastor, self.igreja_permitida)

        response = self.client.post(reverse('financeiro:excluir_despesa', args=[despesa.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Despesas.objects.filter(pk=despesa.pk).exists())

    def test_post_outro_ministerio_nao_exclui(self):
        despesa = self._criar_despesa(
            self.igreja_outro_ministerio,
            self.conta_outro_ministerio,
            descricao='Despesa outro ministerio',
        )
        self._autenticar_com_igreja_ativa(self.pastor, self.igreja_permitida)

        response = self.client.post(reverse('financeiro:excluir_despesa', args=[despesa.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Despesas.objects.filter(pk=despesa.pk).exists())

    def test_post_despesa_fechada_nao_exclui_e_retorna_redirect(self):
        despesa = self._criar_despesa(
            self.igreja_permitida,
            self.conta_permitida,
            fechado=True,
            descricao='Despesa fechada',
        )
        self._autenticar_com_igreja_ativa(self.pastor, self.igreja_permitida)

        response = self.client.post(reverse('financeiro:excluir_despesa', args=[despesa.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('financeiro:lista_despesas'))
        self.assertTrue(Despesas.objects.filter(pk=despesa.pk).exists())

    def test_get_retorna_redirect_seguro_sem_none(self):
        despesa = self._criar_despesa(self.igreja_permitida, self.conta_permitida)
        self._autenticar_com_igreja_ativa(self.pastor, self.igreja_permitida)

        response = self.client.get(reverse('financeiro:excluir_despesa', args=[despesa.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('financeiro:lista_despesas'))
        self.assertTrue(Despesas.objects.filter(pk=despesa.pk).exists())

    def test_usuario_sem_escopo_financeiro_nao_exclui_despesa(self):
        despesa = self._criar_despesa(self.igreja_permitida, self.conta_permitida)
        self._autenticar_com_igreja_ativa(self.sem_escopo, self.igreja_permitida)

        response = self.client.post(reverse('financeiro:excluir_despesa', args=[despesa.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Despesas.objects.filter(pk=despesa.pk).exists())