from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from configuracao.models import Igreja, Ministerio, PerfilUsuario
from contas.constants import SECRETARIO_LOCAL
from secretaria.models import Membro, StatusHistorico, StatusPessoa, TimelineEvent, TipoPessoa


class SecretariaHistoricoTipoStatusTests(TestCase):
    def setUp(self):
        self.ministerio = Ministerio.objects.create(
            nome_fantasia="Ministerio Teste",
            razao_social="Ministerio Teste LTDA",
            cnpj="12.345.678/0001-90",
            email="ministerio@example.com",
            telefone="11999999999",
            rua="Rua A",
            numero="100",
            bairro="Centro",
            cidade="Sao Paulo",
            estado="SP",
            cep="01000-000",
            administrador_principal=User.objects.create_user(
                username="admin_min",
                email="admin_min@example.com",
                password="123",
            ),
            ativo=True,
        )

        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja="Igreja Central",
            cnpj="98.765.432/0001-10",
            pastor_local="Pastor Teste",
            telefone="11988888888",
            email="igreja@example.com",
            rua="Rua B",
            numero_casa="50",
            bairro_distrito="Centro",
            cidade="Sao Paulo",
            estado="SP",
            cep="02000-000",
        )

        self.group_secretario, _ = Group.objects.get_or_create(name=SECRETARIO_LOCAL)
        self.user = User.objects.create_user(
            username="secretario",
            email="secretario@example.com",
            password="123",
            first_name="Sec",
            last_name="Local",
        )
        self.user.groups.add(self.group_secretario)

        self.perfil = PerfilUsuario.objects.create(
            user=self.user,
            ministerio=self.ministerio,
        )
        self.perfil.igrejas_permitidas.add(self.igreja)

        self.tipo_membro = TipoPessoa.objects.create(nome="Membro")
        self.tipo_congregado = TipoPessoa.objects.create(nome="Congregado")

        self.status_ativo = StatusPessoa.objects.create(nome="Ativo")
        self.status_inativo = StatusPessoa.objects.create(nome="Inativo")

    def _criar_membro(self):
        return Membro.objects.create(
            nome="Joao da Silva",
            genero="M",
            estado_civil="Solteiro",
            igreja=self.igreja,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )

    def test_salvar_membro_com_novo_tipo_status_cria_historico_com_usuario(self):
        membro = self._criar_membro()
        historico_inicial = StatusHistorico.objects.filter(membro=membro).count()

        membro.tipo_pessoa = self.tipo_congregado
        membro.status_pessoa = self.status_inativo
        membro.save(user=self.user)

        historicos = StatusHistorico.objects.filter(membro=membro).order_by("id")
        self.assertEqual(historicos.count(), historico_inicial + 1)

        ultimo = historicos.last()
        self.assertEqual(ultimo.tipo_pessoa_anterior, self.tipo_membro)
        self.assertEqual(ultimo.tipo_pessoa_novo, self.tipo_congregado)
        self.assertEqual(ultimo.status_pessoa_anterior, self.status_ativo)
        self.assertEqual(ultimo.status_pessoa_novo, self.status_inativo)
        self.assertEqual(ultimo.registrado_por, self.user)

    def test_detalhe_membro_renderiza_historico_tipo_status(self):
        membro = self._criar_membro()
        membro.tipo_pessoa = self.tipo_congregado
        membro.status_pessoa = self.status_inativo
        membro.save(user=self.user)

        self.client.force_login(self.user)
        response = self.client.get(reverse("secretaria:detalhe_membro", args=[membro.pk]))
        html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Histórico de Alterações de Tipo e Status", html)
        self.assertIn("Membro", html)
        self.assertIn("Congregado", html)
        self.assertIn("Ativo", html)
        self.assertIn("Inativo", html)

    def test_statushistorico_sem_data_transicao_e_permitido_sem_timeline_temporal(self):
        membro = self._criar_membro()

        before = TimelineEvent.objects.filter(membro=membro).count()
        historico = StatusHistorico.objects.create(
            membro=membro,
            status_pessoa_anterior=self.status_ativo,
            status_pessoa_novo=self.status_inativo,
            data_transicao=None,
            registrado_por=self.user,
        )

        self.assertIsNone(historico.data_transicao)
        after = TimelineEvent.objects.filter(membro=membro).count()
        self.assertEqual(after, before)

    def test_historico_sem_data_nao_cria_timeline_de_mudanca_tipo(self):
        membro = self._criar_membro()

        TimelineEvent.objects.filter(membro=membro).delete()
        StatusHistorico.objects.create(
            membro=membro,
            tipo_pessoa_anterior=self.tipo_membro,
            tipo_pessoa_novo=self.tipo_congregado,
            data_transicao=None,
            registrado_por=self.user,
        )

        self.assertFalse(TimelineEvent.objects.filter(membro=membro, tipo_evento='mudanca_tipo').exists())

    def test_historico_com_data_cria_timeline_status_com_mesma_data(self):
        membro = self._criar_membro()
        TimelineEvent.objects.filter(membro=membro, tipo_evento='mudanca_status').delete()
        data_ref = timezone.now().replace(microsecond=0)

        StatusHistorico.objects.create(
            membro=membro,
            status_pessoa_anterior=self.status_ativo,
            status_pessoa_novo=self.status_inativo,
            data_transicao=data_ref,
            registrado_por=self.user,
        )

        evento = TimelineEvent.objects.get(membro=membro, tipo_evento='mudanca_status', data=data_ref)
        self.assertEqual(evento.data, data_ref)

    def test_historico_com_data_cria_timeline_tipo_com_mesma_data(self):
        membro = self._criar_membro()
        TimelineEvent.objects.filter(membro=membro, tipo_evento='mudanca_tipo').delete()
        data_ref = timezone.now().replace(microsecond=0)

        StatusHistorico.objects.create(
            membro=membro,
            tipo_pessoa_anterior=self.tipo_membro,
            tipo_pessoa_novo=self.tipo_congregado,
            data_transicao=data_ref,
            registrado_por=self.user,
        )

        evento = TimelineEvent.objects.get(membro=membro, tipo_evento='mudanca_tipo', data=data_ref)
        self.assertEqual(evento.data, data_ref)

    def test_criacao_de_membro_sem_data_historica_nao_quebra_timeline(self):
        membro = self._criar_membro()

        self.assertTrue(StatusHistorico.objects.filter(membro=membro).exists())
        self.assertFalse(
            TimelineEvent.objects.filter(
                membro=membro,
                tipo_evento__in=['mudanca_status', 'mudanca_tipo'],
            ).exists()
        )

    def test_linha_do_tempo_com_datas_nao_quebra_e_respeita_escopo(self):
        membro_escopo = self._criar_membro()
        membro_escopo.tipo_pessoa = self.tipo_congregado
        membro_escopo.status_pessoa = self.status_inativo
        membro_escopo.save(user=self.user)

        igreja_fora_escopo = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja="Igreja Fora Escopo",
            cnpj="11.222.333/0001-44",
            pastor_local="Pastor Fora",
            telefone="11977777777",
            email="fora@example.com",
            rua="Rua C",
            numero_casa="90",
            bairro_distrito="Centro",
            cidade="Sao Paulo",
            estado="SP",
            cep="03000-000",
        )
        membro_fora_escopo = Membro.objects.create(
            nome="Membro Fora Escopo",
            genero="M",
            estado_civil="Solteiro",
            igreja=igreja_fora_escopo,
            tipo_pessoa=self.tipo_membro,
            status_pessoa=self.status_ativo,
        )
        membro_fora_escopo.tipo_pessoa = self.tipo_congregado
        membro_fora_escopo.status_pessoa = self.status_inativo
        membro_fora_escopo.save(user=self.user)

        self.client.force_login(self.user)
        session = self.client.session
        session["igreja_ativa_id"] = self.igreja.pk
        session.save()

        ano = timezone.now().year
        response = self.client.get(
            reverse("secretaria:linha_do_tempo"),
            {
                "periodo_predefinido": "ano_atual",
                "data_inicio": f"{ano}-01-01",
                "data_fim": f"{ano}-12-31",
            },
        )
        html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Joao da Silva", html)
        self.assertNotIn("Membro Fora Escopo", html)
