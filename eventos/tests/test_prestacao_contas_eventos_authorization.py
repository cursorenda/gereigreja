from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from contas.constants import ADMIN_MINISTERIO, EQUIPE_EVENTOS, PASTOR_LOCAL, SECRETARIO_LOCAL, TESOUREIRO
from configuracao.models import Igreja, Ministerio, PerfilUsuario
from eventos.models import Evento
from financeiro.models import CategoriaDespesa, ContaBancaria, Despesas, FechamentoCaixa, Receitas
from secretaria.models import Membro, StatusPessoa, TipoPessoa


User = get_user_model()


class PrestacaoContasEventosAuthorizationTests(TestCase):
    periodo_query = '?periodo_filtro=custom&data_inicio=2026-08-01&data_fim=2026-08-31'

    def setUp(self):
        self.admin_ministerio = User.objects.create_user(username='admin-eventos-raiz', password='senha123')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Eventos Autorizacao',
            administrador_principal=self.admin_ministerio,
            ativo=True,
        )
        self.outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Eventos Autorizacao',
            administrador_principal=User.objects.create_user(username='admin-outro-eventos', password='senha123'),
            ativo=True,
        )
        self.igreja_sede = self._criar_igreja('Sede Eventos', 'sede')
        self.igreja_independente = self._criar_igreja('Independente Eventos', 'independente')
        self.igreja_regional = self._criar_igreja('Regional Eventos', 'regional')
        self.igreja_congregacao = self._criar_igreja('Congregacao Eventos', 'congregacao')
        self.igreja_externa = Igreja.objects.create(
            ministerio=self.outro_ministerio,
            nome_igreja='Sede Externa Eventos',
            tipo_igreja='sede',
        )
        self.tipo_membro = TipoPessoa.objects.create(nome='Membro Eventos Autorizacao')
        self.status_ativo = StatusPessoa.objects.create(nome='Ativo Eventos Autorizacao')
        self._fixture_sequence = 0

    def _criar_igreja(self, nome, tipo):
        return Igreja.objects.create(ministerio=self.ministerio, nome_igreja=nome, tipo_igreja=tipo)

    def _criar_usuario(self, username, grupos=(), igrejas_permitidas=(), membro_em=None, ministerio=None):
        user = User.objects.create_user(username=username, password='senha123')
        perfil = PerfilUsuario.objects.create(user=user, ministerio=ministerio or self.ministerio)
        perfil.igrejas_permitidas.set(igrejas_permitidas)
        for grupo in grupos:
            user.groups.add(Group.objects.get_or_create(name=grupo)[0])
        if membro_em:
            Membro.objects.create(
                nome=f'Membro {username}', igreja=membro_em, usuario=user,
                tipo_pessoa=self.tipo_membro, status_pessoa=self.status_ativo,
            )
        return user

    def _criar_lancamentos(self, igreja):
        self._fixture_sequence += 1
        sequence = self._fixture_sequence
        conta = ContaBancaria.objects.create(igreja=igreja, nome_identificacao=f'Caixa {igreja.pk}-{sequence}', tipo='caixa_fisico')
        categoria = CategoriaDespesa.objects.create(ministerio=igreja.ministerio, nome=f'Categoria {igreja.pk}-{sequence}')
        evento = Evento.objects.create(
            titulo=f'Evento {igreja.pk}-{sequence}',
            igreja=igreja,
            data_inicio=timezone.make_aware(datetime(2026, 8, 10, 19, 0)),
            data_fim=timezone.make_aware(datetime(2026, 8, 10, 21, 0)),
        )
        receita = Receitas.objects.create(igreja=igreja, evento=evento, categoria='doacao', data=date(2026, 8, 10), valor=Decimal('100.00'), conta_bancaria=conta, fechado=False)
        despesa = Despesas.objects.create(igreja=igreja, evento=evento, categoria=categoria, data=date(2026, 8, 10), descricao='Despesa de evento', valor=Decimal('25.00'), conta_bancaria=conta, fechado=False)
        return receita, despesa

    def _definir_igreja_ativa(self, igreja):
        session = self.client.session
        session['igreja_ativa_id'] = igreja.pk
        session.save()

    def _post_fechamento(self, user, igreja):
        self.client.force_login(user)
        self._definir_igreja_ativa(igreja)
        return self.client.post(reverse('eventos:prestacao_contas_eventos') + self.periodo_query, {'acao': 'fechar_periodo_eventos'}, follow=True)

    def _assert_estado_nao_alterado(self, receita, despesa, igreja):
        receita.refresh_from_db()
        despesa.refresh_from_db()
        self.assertFalse(receita.fechado)
        self.assertFalse(despesa.fechado)
        self.assertFalse(FechamentoCaixa.objects.filter(igreja=igreja, data_inicio=date(2026, 8, 1), data_fim=date(2026, 8, 31)).exists())

    def test_equipe_eventos_pode_ler_mas_nao_fechar(self):
        user = self._criar_usuario('equipe-eventos', [EQUIPE_EVENTOS], membro_em=self.igreja_sede)
        receita, despesa = self._criar_lancamentos(self.igreja_sede)
        self.client.force_login(user)
        self._definir_igreja_ativa(self.igreja_sede)
        get_response = self.client.get(reverse('eventos:prestacao_contas_eventos') + self.periodo_query)
        self.assertEqual(get_response.status_code, 200)
        self.assertFalse(get_response.context['pode_fechar_periodo_eventos'])
        response = self.client.post(reverse('eventos:prestacao_contas_eventos') + self.periodo_query, {'acao': 'fechar_periodo_eventos'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self._assert_estado_nao_alterado(receita, despesa, self.igreja_sede)

    def test_membro_secretaria_nao_autoriza_equipe_eventos(self):
        user = self._criar_usuario('equipe-eventos-membro', [EQUIPE_EVENTOS], membro_em=self.igreja_sede)
        receita, despesa = self._criar_lancamentos(self.igreja_sede)
        self._post_fechamento(user, self.igreja_sede)
        self._assert_estado_nao_alterado(receita, despesa, self.igreja_sede)

    def test_pastor_local_fecha_somente_igreja_explicitamente_permitida(self):
        user = self._criar_usuario('pastor-local-eventos', [PASTOR_LOCAL], [self.igreja_sede, self.igreja_independente])
        receita, despesa = self._criar_lancamentos(self.igreja_sede)
        response = self._post_fechamento(user, self.igreja_sede)
        self.assertEqual(response.status_code, 200)
        receita.refresh_from_db(); despesa.refresh_from_db()
        self.assertTrue(receita.fechado); self.assertTrue(despesa.fechado)
        receita_b, despesa_b = self._criar_lancamentos(self.igreja_regional)
        self._post_fechamento(user, self.igreja_regional)
        self._assert_estado_nao_alterado(receita_b, despesa_b, self.igreja_regional)

    def test_admin_ministerio_so_fecha_sede_ou_independente(self):
        user = self._criar_usuario('admin-eventos', [ADMIN_MINISTERIO])
        for igreja, permitido in ((self.igreja_sede, True), (self.igreja_independente, True), (self.igreja_regional, False), (self.igreja_congregacao, False)):
            with self.subTest(tipo=igreja.tipo_igreja):
                receita, despesa = self._criar_lancamentos(igreja)
                self._post_fechamento(user, igreja)
                receita.refresh_from_db(); despesa.refresh_from_db()
                self.assertEqual(receita.fechado, permitido)
                self.assertEqual(despesa.fechado, permitido)

    def test_tesoureiro_secretario_e_cross_tenant_nao_fecham(self):
        for username, grupos, igreja, ministerio in (
            ('tesoureiro-eventos', [TESOUREIRO], self.igreja_sede, self.ministerio),
            ('secretario-eventos', [SECRETARIO_LOCAL], self.igreja_sede, self.ministerio),
            ('admin-cross-tenant-eventos', [ADMIN_MINISTERIO], self.igreja_externa, self.ministerio),
        ):
            with self.subTest(username=username):
                user = self._criar_usuario(username, grupos, [igreja], ministerio=ministerio)
                receita, despesa = self._criar_lancamentos(igreja)
                self._post_fechamento(user, igreja)
                self._assert_estado_nao_alterado(receita, despesa, igreja)

    def test_igreja_ativa_forjada_nao_produz_escrita(self):
        user = self._criar_usuario('pastor-forjado-eventos', [PASTOR_LOCAL], [self.igreja_sede])
        receita, despesa = self._criar_lancamentos(self.igreja_externa)
        self.client.force_login(user)
        self._definir_igreja_ativa(self.igreja_externa)
        self.client.post(reverse('eventos:prestacao_contas_eventos') + self.periodo_query, {'acao': 'fechar_periodo_eventos'}, follow=True)
        self._assert_estado_nao_alterado(receita, despesa, self.igreja_externa)