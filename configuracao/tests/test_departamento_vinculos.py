from concurrent.futures import ThreadPoolExecutor
from datetime import date
from threading import Barrier

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError, OperationalError, close_old_connections, transaction
from django.test import TestCase, TransactionTestCase
from django.urls import reverse

from contas.constants import ADMIN_MINISTERIO, PASTOR_LOCAL, SECRETARIO_LOCAL
from configuracao.models import (
    Departamento,
    DepartamentoVinculo,
    Igreja,
    Ministerio,
    PerfilUsuario,
)
from configuracao.services_departamentos import DepartamentoVinculoService
from financeiro.models import DepartamentoFinanceiro
from secretaria.models import Cargo, MembroCargo, Pessoa, StatusPessoa, TipoPessoa


class DepartamentoVinculoBase:
    def criar_cenario(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin-equipes')
        self.pastor = User.objects.create_user(username='pastor-equipes')
        self.secretario = User.objects.create_user(username='secretario-equipes')
        self.ministerio = Ministerio.objects.create(
            nome_fantasia='Ministerio Equipes',
            administrador_principal=self.admin,
            ativo=True,
        )
        self.igreja_a = Igreja.objects.create(ministerio=self.ministerio, nome_igreja='Igreja A Equipes')
        self.igreja_b = Igreja.objects.create(ministerio=self.ministerio, nome_igreja='Igreja B Equipes')
        for usuario, grupo_nome in (
            (self.admin, ADMIN_MINISTERIO),
            (self.pastor, PASTOR_LOCAL),
            (self.secretario, SECRETARIO_LOCAL),
        ):
            perfil = PerfilUsuario.objects.create(user=usuario, ministerio=self.ministerio)
            perfil.igrejas_permitidas.add(self.igreja_a)
            grupo, _ = Group.objects.get_or_create(name=grupo_nome)
            usuario.groups.add(grupo)

        self.departamento_a = Departamento.objects.get(
            igreja=self.igreja_a,
            codigo_interno='MISSOES',
        )
        self.departamento_b = Departamento.objects.get(
            igreja=self.igreja_b,
            codigo_interno='MISSOES',
        )
        self.tipo = TipoPessoa.objects.create(nome='Membro')
        self.status = StatusPessoa.objects.create(nome='Ativo')
        self.membro_a, self.membro_b = Pessoa.objects.bulk_create(
            [
                Pessoa(
                igreja=self.igreja_a,
                nome='Membro A',
                tipo_pessoa=self.tipo,
                status_pessoa=self.status,
                ),
                Pessoa(
                    igreja=self.igreja_b,
                    nome='Membro B',
                    tipo_pessoa=self.tipo,
                    status_pessoa=self.status,
                ),
            ]
        )
        self.cargo = Cargo.objects.create(nome='Lider de Missoes')


class DepartamentoVinculoServiceTests(DepartamentoVinculoBase, TestCase):
    def setUp(self):
        self.criar_cenario()

    def test_cria_vinculo_valido_sem_efeitos_de_autorizacao(self):
        grupo = Group.objects.create(name='Grupo Inerte Departamento')
        self.cargo.grupo_permissao = grupo
        self.cargo.save(update_fields=['grupo_permissao'])
        grupos_antes = set(self.pastor.groups.values_list('pk', flat=True))
        financeiros_antes = DepartamentoFinanceiro.objects.count()

        vinculo = DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            cargo=self.cargo,
            usuario=self.pastor,
            data_inicio=date(2026, 8, 1),
        )

        self.assertIsNone(vinculo.data_fim)
        self.assertEqual(vinculo.criado_por, self.pastor)
        self.assertEqual(set(self.pastor.groups.values_list('pk', flat=True)), grupos_antes)
        self.assertFalse(self.pastor.groups.filter(pk=grupo.pk).exists())
        self.assertFalse(MembroCargo.objects.filter(membro=self.membro_a).exists())
        self.assertEqual(DepartamentoFinanceiro.objects.count(), financeiros_antes)

    def test_service_e_constraint_impedem_segundo_vinculo_ativo(self):
        DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            usuario=self.pastor,
        )
        with self.assertRaises(ValidationError):
            DepartamentoVinculoService.adicionar(
                departamento=self.departamento_a,
                membro=self.membro_a,
                usuario=self.pastor,
            )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DepartamentoVinculo.objects.create(
                    departamento=self.departamento_a,
                    membro=self.membro_a,
                    criado_por=self.pastor,
                )

    def test_encerrar_preserva_historico_e_retorno_cria_novo_registro(self):
        primeiro = DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            usuario=self.pastor,
            data_inicio=date(2026, 8, 1),
        )
        DepartamentoVinculoService.encerrar(
            vinculo=primeiro,
            usuario=self.secretario,
            data_fim=date(2026, 8, 10),
        )
        segundo = DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            usuario=self.pastor,
            data_inicio=date(2026, 8, 20),
        )

        primeiro.refresh_from_db()
        self.assertEqual(primeiro.data_fim, date(2026, 8, 10))
        self.assertEqual(primeiro.encerrado_por, self.secretario)
        self.assertNotEqual(primeiro.pk, segundo.pk)
        self.assertEqual(DepartamentoVinculo.objects.count(), 2)

    def test_troca_de_cargo_encerra_atual_e_cria_novo_historico(self):
        novo_cargo = Cargo.objects.create(nome='Auxiliar de Missoes')
        primeiro = DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            cargo=self.cargo,
            usuario=self.pastor,
            data_inicio=date(2026, 8, 1),
        )

        segundo = DepartamentoVinculoService.trocar_cargo(
            vinculo=primeiro,
            novo_cargo=novo_cargo,
            usuario=self.secretario,
            data_troca=date(2026, 8, 15),
        )

        primeiro.refresh_from_db()
        self.assertEqual(primeiro.data_fim, date(2026, 8, 15))
        self.assertEqual(primeiro.encerrado_por, self.secretario)
        self.assertEqual(segundo.cargo, novo_cargo)
        self.assertEqual(segundo.data_inicio, date(2026, 8, 15))
        self.assertNotEqual(primeiro.pk, segundo.pk)

    def test_membro_de_outra_igreja_e_bloqueado(self):
        with self.assertRaises(ValidationError):
            DepartamentoVinculoService.adicionar(
                departamento=self.departamento_a,
                membro=self.membro_b,
                usuario=self.pastor,
            )

    def test_adicionar_rejeita_admin_outro_tenant_e_operadores_sem_igreja_explicita(self):
        outro_usuario = get_user_model().objects.create_user(username='outro-tenant-equipes')
        outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministerio Equipes',
            administrador_principal=outro_usuario,
        )
        PerfilUsuario.objects.create(user=outro_usuario, ministerio=outro_ministerio)
        outro_grupo, _ = Group.objects.get_or_create(name=PASTOR_LOCAL)
        outro_usuario.groups.add(outro_grupo)

        self.pastor.perfil.igrejas_permitidas.clear()
        self.secretario.perfil.igrejas_permitidas.clear()
        for usuario in (self.admin, outro_usuario, self.pastor, self.secretario):
            with self.subTest(usuario=usuario.username):
                with self.assertRaises(ValidationError):
                    DepartamentoVinculoService.adicionar(
                        departamento=self.departamento_a,
                        membro=self.membro_a,
                        usuario=usuario,
                    )

        self.assertFalse(DepartamentoVinculo.objects.exists())

    def test_operador_local_com_igreja_explicita_pode_adicionar(self):
        vinculo = DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            usuario=self.secretario,
        )

        self.assertEqual(vinculo.criado_por, self.secretario)
        self.assertIsNone(vinculo.data_fim)

    def test_encerrar_nao_autorizado_preserva_vinculo_ativo(self):
        vinculo = DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            usuario=self.pastor,
        )

        with self.assertRaises(ValidationError):
            DepartamentoVinculoService.encerrar(vinculo=vinculo, usuario=self.admin)

        vinculo.refresh_from_db()
        self.assertIsNone(vinculo.data_fim)
        self.assertIsNone(vinculo.encerrado_por)

    def test_trocar_cargo_nao_autorizado_preserva_vinculo_e_historico(self):
        novo_cargo = Cargo.objects.create(nome='Novo Cargo Protegido')
        vinculo = DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            cargo=self.cargo,
            usuario=self.pastor,
        )

        with self.assertRaises(ValidationError):
            DepartamentoVinculoService.trocar_cargo(
                vinculo=vinculo,
                novo_cargo=novo_cargo,
                usuario=self.admin,
            )

        vinculo.refresh_from_db()
        self.assertIsNone(vinculo.data_fim)
        self.assertEqual(vinculo.cargo, self.cargo)
        self.assertEqual(DepartamentoVinculo.objects.filter(departamento=self.departamento_a).count(), 1)

    def test_constraint_de_datas_rejeita_fim_anterior(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                DepartamentoVinculo.objects.create(
                    departamento=self.departamento_a,
                    membro=self.membro_a,
                    data_inicio=date(2026, 8, 10),
                    data_fim=date(2026, 8, 9),
                )


class DepartamentoVinculoViewTests(DepartamentoVinculoBase, TestCase):
    def setUp(self):
        self.criar_cenario()
        self.url = reverse('configuracao:gestao_departamentos')

    def _post_adicionar(self, usuario, **dados):
        self.client.force_login(usuario)
        payload = {
            'action': 'adicionar_vinculo_departamento',
            'igreja_id': self.igreja_a.pk,
            'departamento_id': self.departamento_a.pk,
            'membro': self.membro_a.pk,
            'cargo': self.cargo.pk,
            'data_inicio': '2026-08-01',
        }
        payload.update(dados)
        return self.client.post(self.url, payload)

    def test_pastor_e_secretario_operam_somente_igreja_explicita(self):
        resposta_pastor = self._post_adicionar(self.pastor)
        vinculo = DepartamentoVinculo.objects.get(departamento=self.departamento_a, membro=self.membro_a)
        self.client.force_login(self.secretario)
        resposta_secretario = self.client.post(
            self.url,
            {
                'action': 'encerrar_vinculo_departamento',
                'igreja_id': self.igreja_a.pk,
                'vinculo_id': vinculo.pk,
            },
        )

        self.assertEqual(resposta_pastor.status_code, 302)
        self.assertEqual(resposta_secretario.status_code, 302)
        vinculo.refresh_from_db()
        self.assertIsNotNone(vinculo.data_fim)

    def test_idor_de_membro_de_outra_igreja_retorna_404(self):
        response = self._post_adicionar(self.pastor, membro=self.membro_b.pk)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(DepartamentoVinculo.objects.exists())

    def test_idor_de_departamento_de_outra_igreja_retorna_404(self):
        response = self._post_adicionar(self.pastor, departamento_id=self.departamento_b.pk)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(DepartamentoVinculo.objects.exists())

    def test_idor_de_cargo_inexistente_retorna_404(self):
        response = self._post_adicionar(self.pastor, cargo=999999)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(DepartamentoVinculo.objects.exists())

    def test_igreja_nao_explicita_retorna_404(self):
        response = self._post_adicionar(
            self.pastor,
            igreja_id=self.igreja_b.pk,
            departamento_id=self.departamento_b.pk,
            membro=self.membro_b.pk,
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(DepartamentoVinculo.objects.exists())

    def test_admin_ministerio_visualiza_readonly_e_post_e_bloqueado(self):
        DepartamentoVinculoService.adicionar(
            departamento=self.departamento_a,
            membro=self.membro_a,
            usuario=self.pastor,
        )
        self.client.force_login(self.admin)
        get_response = self.client.get(self.url, {'igreja_id': self.igreja_a.pk})
        post_response = self.client.post(
            self.url,
            {
                'action': 'adicionar_vinculo_departamento',
                'igreja_id': self.igreja_a.pk,
                'departamento_id': self.departamento_a.pk,
                'membro': self.membro_a.pk,
            },
        )

        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, 'Equipe do departamento')
        self.assertContains(get_response, 'Visao somente leitura')
        self.assertNotContains(get_response, 'name="action" value="adicionar_vinculo_departamento"')
        self.assertEqual(post_response.status_code, 403)
        self.assertEqual(DepartamentoVinculo.objects.count(), 1)

    def test_pastor_com_pessoa_em_igreja_nao_permitida_opera_apenas_igreja_do_perfil(self):
        self.membro_b.usuario = self.pastor
        self.membro_b.save(update_fields=['usuario'])
        self.secretario.perfil.igrejas_permitidas.add(self.igreja_b)
        DepartamentoVinculoService.adicionar(
            departamento=self.departamento_b,
            membro=self.membro_b,
            usuario=self.secretario,
        )

        self.client.force_login(self.pastor)

        response_permitida = self.client.get(self.url, {'igreja_id': self.igreja_a.pk})
        response_fora_escopo = self.client.get(self.url, {'igreja_id': self.igreja_b.pk})
        post_fora_escopo = self._post_adicionar(
            self.pastor,
            igreja_id=self.igreja_b.pk,
            departamento_id=self.departamento_b.pk,
            membro=self.membro_b.pk,
        )

        self.assertEqual(response_permitida.status_code, 200)
        self.assertEqual(response_fora_escopo.status_code, 404)
        self.assertEqual(post_fora_escopo.status_code, 404)
        self.assertEqual(DepartamentoVinculo.objects.filter(departamento=self.departamento_b).count(), 1)

    def test_secretario_sem_igreja_permitida_nao_opera_igreja_da_pessoa(self):
        self.secretario.perfil.igrejas_permitidas.clear()
        self.membro_b.usuario = self.secretario
        self.membro_b.save(update_fields=['usuario'])

        self.client.force_login(self.secretario)

        response = self.client.get(self.url, {'igreja_id': self.igreja_b.pk})

        self.assertEqual(response.status_code, 302)
        self.assertFalse(DepartamentoVinculo.objects.filter(departamento=self.departamento_b).exists())

    def test_igreja_da_pessoa_e_vinculo_nao_ampliam_escopo_quando_igreja_b_nao_e_permitida(self):
        self.membro_b.usuario = self.pastor
        self.membro_b.save(update_fields=['usuario'])
        self.secretario.perfil.igrejas_permitidas.add(self.igreja_b)
        DepartamentoVinculoService.adicionar(
            departamento=self.departamento_b,
            membro=self.membro_b,
            usuario=self.secretario,
        )

        self.client.force_login(self.pastor)

        response = self.client.get(self.url, {'igreja_id': self.igreja_b.pk})

        self.assertEqual(response.status_code, 404)

    def test_pastor_com_igreja_b_expressamente_permitida_pode_operar_nela(self):
        self.pastor.perfil.igrejas_permitidas.add(self.igreja_b)
        self.membro_b.usuario = self.pastor
        self.membro_b.save(update_fields=['usuario'])

        self.client.force_login(self.pastor)
        response = self.client.get(self.url, {'igreja_id': self.igreja_b.pk})

        self.assertEqual(response.status_code, 200)

    def test_admin_ministerio_mantem_escopo_do_proprio_tenant(self):
        outro_admin = get_user_model().objects.create_user(username='admin-outro-tenant-departamentos')
        outro_ministerio = Ministerio.objects.create(
            nome_fantasia='Outro Ministério Departamentos',
            administrador_principal=outro_admin,
        )
        igreja_outro_tenant = Igreja.objects.create(
            ministerio=outro_ministerio,
            nome_igreja='Igreja Outro Tenant Departamentos',
        )

        self.client.force_login(self.admin)
        response_proprio_tenant = self.client.get(self.url, {'igreja_id': self.igreja_b.pk})
        response_outro_tenant = self.client.get(self.url, {'igreja_id': igreja_outro_tenant.pk})

        self.assertEqual(response_proprio_tenant.status_code, 200)
        self.assertEqual(response_outro_tenant.status_code, 404)

class DepartamentoVinculoConcorrenciaTests(DepartamentoVinculoBase, TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        self.criar_cenario()

    def test_duas_criacoes_concorrentes_nao_produzem_dois_vinculos_ativos(self):
        barrier = Barrier(2)

        def criar():
            close_old_connections()
            try:
                departamento = Departamento.objects.get(pk=self.departamento_a.pk)
                membro = Pessoa.objects.get(pk=self.membro_a.pk)
                usuario = get_user_model().objects.get(pk=self.pastor.pk)
                barrier.wait()
                DepartamentoVinculoService.adicionar(
                    departamento=departamento,
                    membro=membro,
                    usuario=usuario,
                )
                return 'criado'
            except (ValidationError, IntegrityError, OperationalError):
                return 'bloqueado'
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(lambda _: criar(), range(2)))

        ativos = DepartamentoVinculo.objects.filter(data_fim__isnull=True).count()
        self.assertLessEqual(ativos, 1)
        self.assertNotEqual(resultados, ['criado', 'criado'])
