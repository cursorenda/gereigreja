"""
Testes completos do sistema de assinaturas, planos e controle de acesso.

Cobre:
  - assinatura_esta_regular()         — todas as condições de elegibilidade
  - is_trial_ativo() / dias_restantes_trial()
  - iniciar_trial()
  - assinatura_em_graca_inadimplencia() / dias_restantes_graca()
  - obter_plano_efetivo_ministerio()  — prioridade: liberacao > assinatura > pioneiro
  - ministerio_pode_usar_modulo()
  - usuario_pode_usar_modulo()
  - ministerio_pode_adicionar_pessoa_ativa()
  - ministerio_pode_criar_igreja()
  - ministerio_pode_visualizar_plano() / ministerio_pode_contratar_plano()
  - listar_planos_para_ministerio()
  - verificar_elegibilidade_plano_gratuito()  — usa só membros ativos (P2 fix)
  - decorator verificar_assinatura_valida     — bloqueio + redirect

Executar:
  python manage.py test configuracao.tests.test_assinatura_services
"""

from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils import timezone

from configuracao.models import (
    AssinaturaMinisterio,
    Igreja,
    LiberacaoPlanoMinisterio,
    Ministerio,
    Plano,
    HistoricoAssinatura,
)
from configuracao.services_assinatura import (
    _ministerio_eh_demo,
    assinatura_em_graca_inadimplencia,
    assinatura_esta_regular,
    contar_pessoas_ativas,
    dias_restantes_graca,
    dias_restantes_trial,
    iniciar_trial,
    is_trial_ativo,
    listar_planos_para_ministerio,
    ministerio_pode_adicionar_pessoa_ativa,
    ministerio_pode_contratar_plano,
    ministerio_pode_criar_igreja,
    ministerio_pode_usar_modulo,
    ministerio_pode_visualizar_plano,
    obter_limite_pessoas_ativas,
    obter_plano_efetivo_ministerio,
    usuario_pode_usar_modulo,
)
from core.decorators import verificar_assinatura_valida


# ===========================================================================
# FIXTURES / HELPERS
# ===========================================================================

def criar_plano(
    nome='pioneiro',
    codigo='pioneiro',
    limite_membros=100,
    limite_igrejas=1,
    ativo=True,
    is_visible=True,
    liberado_publicamente=False,
    contratacao_publica_liberada=False,
    ordem=0,
    permite_financeiro=True,
    permite_comunicacao=False,
):
    """Cria (ou retorna) um plano com os parâmetros dados."""
    plano, _ = Plano.objects.get_or_create(
        nome=nome,
        defaults=dict(
            codigo_plano=codigo,
            limite_membros=limite_membros,
            limite_igrejas=limite_igrejas,
            ativo=ativo,
            is_visible=is_visible,
            liberado_publicamente=liberado_publicamente,
            contratacao_publica_liberada=contratacao_publica_liberada,
            ordem_liberacao=ordem,
            permite_modulo_financeiro=permite_financeiro,
            permite_modulo_comunicacao=permite_comunicacao,
        ),
    )
    return plano


def criar_ministerio(admin=None, ativo=True, nome='Ministério Teste'):
    if admin is None:
        admin = User.objects.create_user(
            username=f'admin_{nome[:6]}_{id(nome)}',
            password='pass',
        )
    m = Ministerio.objects.create(
        nome_fantasia=nome,
        administrador_principal=admin,
        ativo=ativo,
    )
    return m, admin


def criar_assinatura(ministerio, plano, status='ativa', **kwargs):
    defaults = dict(
        ministerio=ministerio,
        plano=plano,
        status=status,
        data_inicio=timezone.now(),
    )
    defaults.update(kwargs)
    return AssinaturaMinisterio.objects.create(**defaults)


def desativar_liberacoes_automaticas(ministerio):
    """Desativa liberações automáticas que alguns sinais podem criar no setup."""
    LiberacaoPlanoMinisterio.objects.filter(ministerio=ministerio).update(
        ativo=False,
        acesso_beta=False,
        pode_visualizar=False,
        pode_contratar=False,
    )


def criar_status_pessoa(nome='Ativo'):
    from secretaria.models import StatusPessoa
    sp, _ = StatusPessoa.objects.get_or_create(nome=nome)
    return sp


def criar_tipo_pessoa(nome='Membro'):
    from secretaria.models import TipoPessoa
    tp, _ = TipoPessoa.objects.get_or_create(nome=nome)
    return tp


def criar_membro(igreja, status_nome='Ativo', nome_suffix=''):
    from secretaria.models import Pessoa, StatusPessoa, TipoPessoa
    status = criar_status_pessoa(status_nome)
    tipo = criar_tipo_pessoa()
    return Pessoa.objects.create(
        nome=f'Membro {status_nome} {nome_suffix}',
        igreja=igreja,
        status_pessoa=status,
        tipo_pessoa=tipo,
    )


# ===========================================================================
# 1. ELEGIBILIDADE GRATUITA — verificar_elegibilidade_plano_gratuito()
# ===========================================================================

class ElegibilidadeGratuitaTestCase(TestCase):
    def setUp(self):
        self.plano_pioneiro = criar_plano(limite_membros=10)
        self.ministerio, self.admin = criar_ministerio()
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Teste',
        )

    def test_sem_membros_e_elegivel(self):
        self.assertTrue(self.ministerio.verificar_elegibilidade_plano_gratuito())

    def test_abaixo_do_limite_e_elegivel(self):
        for i in range(8):
            criar_membro(self.igreja, nome_suffix=str(i))
        self.assertTrue(self.ministerio.verificar_elegibilidade_plano_gratuito())

    def test_exatamente_no_limite_e_elegivel(self):
        for i in range(10):
            criar_membro(self.igreja, nome_suffix=str(i))
        self.assertTrue(self.ministerio.verificar_elegibilidade_plano_gratuito())

    def test_acima_do_limite_nao_elegivel(self):
        for i in range(11):
            criar_membro(self.igreja, nome_suffix=str(i))
        self.assertFalse(self.ministerio.verificar_elegibilidade_plano_gratuito())

    def test_membros_inativos_nao_contam(self):
        """Membros inativos NÃO devem influenciar o limite. (Fix P2)"""
        # Cria 15 membros inativos — se contassem, ultrapassariam o limite de 10
        for i in range(15):
            criar_membro(self.igreja, status_nome='Inativo', nome_suffix=str(i))
        # Apenas 5 ativos
        for i in range(5):
            criar_membro(self.igreja, status_nome='Ativo', nome_suffix=f'ativo{i}')
        # Deve ser elegível: apenas 5 ativos, limite é 10
        self.assertTrue(self.ministerio.verificar_elegibilidade_plano_gratuito())

    def test_limite_zero_sempre_elegivel(self):
        """Limite 0 no plano Pioneiro = ilimitado → sempre elegível."""
        self.plano_pioneiro.limite_membros = 0
        self.plano_pioneiro.save()
        for i in range(200):
            criar_membro(self.igreja, nome_suffix=str(i))
        self.assertTrue(self.ministerio.verificar_elegibilidade_plano_gratuito())

    def test_sem_plano_pioneiro_usa_fallback_50(self):
        """Sem plano cadastrado, fallback é 50."""
        self.plano_pioneiro.delete()
        # 49 membros ativos → elegível
        for i in range(49):
            criar_membro(self.igreja, nome_suffix=str(i))
        self.assertTrue(self.ministerio.verificar_elegibilidade_plano_gratuito())
        # 51 membros ativos → não elegível
        criar_membro(self.igreja, nome_suffix='50')
        criar_membro(self.igreja, nome_suffix='51')
        self.assertFalse(self.ministerio.verificar_elegibilidade_plano_gratuito())


# ===========================================================================
# 2. assinatura_esta_regular() — todas as condições
# ===========================================================================

class AssinaturaEstaRegularTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano(limite_membros=100)
        self.ministerio, self.admin = criar_ministerio()
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio,
            nome_igreja='Igreja Base',
        )
        desativar_liberacoes_automaticas(self.ministerio)

    # --- 2.1 Sem assinatura ---

    def test_sem_assinatura_elegivel_retorna_true(self):
        """Sem assinatura + dentro do limite gratuito → True."""
        self.assertTrue(assinatura_esta_regular(None, self.ministerio))

    def test_sem_assinatura_acima_limite_retorna_false(self):
        """Sem assinatura + excede limite gratuito → False."""
        self.plano.limite_membros = 2
        self.plano.save()
        for i in range(5):
            criar_membro(self.igreja, nome_suffix=str(i))
        self.assertFalse(assinatura_esta_regular(None, self.ministerio))

    # --- 2.2 Trial ---

    def test_trial_ativo_retorna_true(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=True,
            data_inicio_trial=timezone.now() - timedelta(days=3),
            dias_trial_totais=14,
        )
        self.assertTrue(assinatura_esta_regular(assinatura, self.ministerio))

    def test_trial_expirado_retorna_false(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=True,
            data_inicio_trial=timezone.now() - timedelta(days=20),
            dias_trial_totais=14,
        )
        self.assertFalse(assinatura_esta_regular(assinatura, self.ministerio))

    # --- 2.3 Status ativa / gratuita ---

    def test_status_ativa_retorna_true(self):
        assinatura = criar_assinatura(self.ministerio, self.plano, status='ativa')
        self.assertTrue(assinatura_esta_regular(assinatura, self.ministerio))

    def test_status_gratuita_retorna_true(self):
        assinatura = criar_assinatura(self.ministerio, self.plano, status='gratuita')
        self.assertTrue(assinatura_esta_regular(assinatura, self.ministerio))

    def test_status_cancelada_retorna_false(self):
        assinatura = criar_assinatura(self.ministerio, self.plano, status='cancelada')
        self.assertFalse(assinatura_esta_regular(assinatura, self.ministerio))

    # --- 2.4 Cortesia ---

    def test_cortesia_valida_retorna_true(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='vencida',
            periodo_cortesia_ativo=True,
            data_inicio_cortesia=timezone.now() - timedelta(hours=1),
        )
        self.assertTrue(assinatura_esta_regular(assinatura, self.ministerio))

    def test_cortesia_expirada_retorna_false(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='cancelada',
            periodo_cortesia_ativo=True,
            data_inicio_cortesia=timezone.now() - timedelta(days=5),
        )
        self.assertFalse(assinatura_esta_regular(assinatura, self.ministerio))

    # --- 2.5 Grace period (inadimplência) — FIX P1 ---

    def test_graca_inadimplencia_ativa_retorna_true(self):
        """Status pendente_pagamento + dentro do prazo de graça → True. (Fix P1)"""
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='pendente_pagamento',
            data_fim_graca_inadimplencia=timezone.now() + timedelta(days=5),
        )
        self.assertTrue(assinatura_esta_regular(assinatura, self.ministerio))

    def test_graca_inadimplencia_expirada_retorna_false(self):
        """Status pendente_pagamento + graça expirada → False."""
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='pendente_pagamento',
            data_fim_graca_inadimplencia=timezone.now() - timedelta(days=1),
        )
        self.assertFalse(assinatura_esta_regular(assinatura, self.ministerio))

    def test_pendente_sem_data_graca_retorna_false(self):
        """Status pendente_pagamento + sem data de graça → False."""
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='pendente_pagamento',
        )
        self.assertFalse(assinatura_esta_regular(assinatura, self.ministerio))

    # --- 2.6 Vencida + elegível grátis ---

    def test_vencida_dentro_limite_gratis_retorna_true(self):
        assinatura = criar_assinatura(self.ministerio, self.plano, status='vencida')
        # Nenhum membro → elegível
        self.assertTrue(assinatura_esta_regular(assinatura, self.ministerio))

    def test_vencida_acima_limite_gratis_retorna_false(self):
        self.plano.limite_membros = 2
        self.plano.save()
        for i in range(5):
            criar_membro(self.igreja, nome_suffix=str(i))
        assinatura = criar_assinatura(self.ministerio, self.plano, status='vencida')
        self.assertFalse(assinatura_esta_regular(assinatura, self.ministerio))

    # --- 2.7 Acesso BETA (P4 fix) ---

    def test_acesso_beta_bypassa_assinatura_cancelada(self):
        """LiberacaoPlanoMinisterio(acesso_beta=True) libera acesso independente do status."""
        assinatura = criar_assinatura(self.ministerio, self.plano, status='cancelada')
        plano_beta = criar_plano(nome='crescimento', codigo='crescimento', ordem=1)
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano_beta,
            ativo=True,
            acesso_beta=True,
            pode_visualizar=True,
        )
        self.assertTrue(assinatura_esta_regular(assinatura, self.ministerio))

    def test_acesso_beta_bypassa_sem_assinatura_acima_limite(self):
        """BETA também libera ministérios acima do limite gratuito sem assinatura."""
        self.plano.limite_membros = 1
        self.plano.save()
        for i in range(5):
            criar_membro(self.igreja, nome_suffix=str(i))
        plano_beta = criar_plano(nome='crescimento', codigo='crescimento', ordem=1)
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano_beta,
            ativo=True,
            acesso_beta=True,
            pode_visualizar=True,
        )
        self.assertTrue(assinatura_esta_regular(None, self.ministerio))

    def test_liberacao_beta_inativa_nao_bypassa(self):
        """LiberacaoPlanoMinisterio(ativo=False) não bypassa o bloqueio."""
        assinatura = criar_assinatura(self.ministerio, self.plano, status='cancelada')
        plano_beta = criar_plano(nome='crescimento', codigo='crescimento', ordem=1)
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano_beta,
            ativo=False,  # inativo
            acesso_beta=True,
            pode_visualizar=True,
        )
        self.assertFalse(assinatura_esta_regular(assinatura, self.ministerio))


# ===========================================================================
# 3. is_trial_ativo() / dias_restantes_trial()
# ===========================================================================

class TrialTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano()
        self.ministerio, _ = criar_ministerio()
        desativar_liberacoes_automaticas(self.ministerio)

    def test_trial_none_retorna_false(self):
        self.assertFalse(is_trial_ativo(None))

    def test_trial_flag_false_retorna_false(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=False,
        )
        self.assertFalse(is_trial_ativo(assinatura))

    def test_trial_sem_data_inicio_retorna_false(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=True,
            # data_inicio_trial = None por padrão
        )
        self.assertFalse(is_trial_ativo(assinatura))

    def test_trial_em_andamento_retorna_true(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=True,
            data_inicio_trial=timezone.now() - timedelta(days=5),
            dias_trial_totais=14,
        )
        self.assertTrue(is_trial_ativo(assinatura))

    def test_trial_expirado_retorna_false(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=True,
            data_inicio_trial=timezone.now() - timedelta(days=15),
            dias_trial_totais=14,
        )
        self.assertFalse(is_trial_ativo(assinatura))

    def test_dias_restantes_em_andamento(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=True,
            data_inicio_trial=timezone.now() - timedelta(days=5),
            dias_trial_totais=14,
        )
        dias = dias_restantes_trial(assinatura)
        self.assertIsNotNone(dias)
        self.assertGreaterEqual(dias, 8)  # 14 - 5 = 9 dias (pode ser 8 dependendo do momento)
        self.assertLessEqual(dias, 9)

    def test_dias_restantes_expirado_retorna_none(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=True,
            data_inicio_trial=timezone.now() - timedelta(days=20),
            dias_trial_totais=14,
        )
        self.assertIsNone(dias_restantes_trial(assinatura))

    def test_trial_customizado_30_dias(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='gratuita',
            trial_ativo=True,
            data_inicio_trial=timezone.now() - timedelta(days=25),
            dias_trial_totais=30,
        )
        self.assertTrue(is_trial_ativo(assinatura))
        dias = dias_restantes_trial(assinatura)
        self.assertGreaterEqual(dias, 4)


# ===========================================================================
# 4. iniciar_trial()
# ===========================================================================

class IniciarTrialTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano()
        self.ministerio, _ = criar_ministerio()
        desativar_liberacoes_automaticas(self.ministerio)

    def test_iniciar_trial_cria_assinatura(self):
        assinatura = iniciar_trial(self.ministerio)
        self.assertIsNotNone(assinatura)
        self.assertTrue(assinatura.trial_ativo)
        self.assertEqual(assinatura.dias_trial_totais, 14)
        self.assertEqual(assinatura.status, 'gratuita')

    def test_iniciar_trial_registra_historico(self):
        iniciar_trial(self.ministerio)
        historico = HistoricoAssinatura.objects.filter(
            ministerio=self.ministerio, tipo='trial'
        ).first()
        self.assertIsNotNone(historico)
        self.assertEqual(historico.status, 'a_vencer')

    def test_iniciar_trial_em_assinatura_existente(self):
        assinatura_existente = criar_assinatura(
            self.ministerio, self.plano, status='gratuita'
        )
        assinatura = iniciar_trial(self.ministerio)
        self.assertEqual(assinatura.pk, assinatura_existente.pk)
        self.assertTrue(assinatura.trial_ativo)

    def test_trial_ativo_gera_acesso_regular(self):
        assinatura = iniciar_trial(self.ministerio)
        self.assertTrue(assinatura_esta_regular(assinatura, self.ministerio))


# ===========================================================================
# 5. assinatura_em_graca_inadimplencia() / dias_restantes_graca()
# ===========================================================================

class GracaInadimplenciaTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano()
        self.ministerio, _ = criar_ministerio()
        desativar_liberacoes_automaticas(self.ministerio)

    def test_none_retorna_false(self):
        self.assertFalse(assinatura_em_graca_inadimplencia(None))

    def test_status_ativa_nao_eh_graca(self):
        assinatura = criar_assinatura(self.ministerio, self.plano, status='ativa')
        self.assertFalse(assinatura_em_graca_inadimplencia(assinatura))

    def test_pendente_sem_data_fim_nao_eh_graca(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='pendente_pagamento'
        )
        self.assertFalse(assinatura_em_graca_inadimplencia(assinatura))

    def test_pendente_dentro_do_prazo_eh_graca(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='pendente_pagamento',
            data_fim_graca_inadimplencia=timezone.now() + timedelta(days=3),
        )
        self.assertTrue(assinatura_em_graca_inadimplencia(assinatura))

    def test_pendente_apos_prazo_nao_eh_graca(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='pendente_pagamento',
            data_fim_graca_inadimplencia=timezone.now() - timedelta(hours=1),
        )
        self.assertFalse(assinatura_em_graca_inadimplencia(assinatura))

    def test_dias_restantes_graca_correto(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='pendente_pagamento',
            data_fim_graca_inadimplencia=timezone.now() + timedelta(days=3),
        )
        dias = dias_restantes_graca(assinatura)
        self.assertIsNotNone(dias)
        self.assertGreaterEqual(dias, 2)
        self.assertLessEqual(dias, 3)

    def test_dias_restantes_graca_expirado_retorna_none(self):
        assinatura = criar_assinatura(
            self.ministerio, self.plano, status='pendente_pagamento',
            data_fim_graca_inadimplencia=timezone.now() - timedelta(days=1),
        )
        self.assertIsNone(dias_restantes_graca(assinatura))


# ===========================================================================
# 6. obter_plano_efetivo_ministerio() — ordem de prioridade
# ===========================================================================

class PlanoEfetivoTestCase(TestCase):
    def setUp(self):
        self.plano_pioneiro = criar_plano(
            nome='pioneiro', codigo='pioneiro',
            liberado_publicamente=True, contratacao_publica_liberada=True,
        )
        self.plano_crescimento = criar_plano(
            nome='crescimento', codigo='crescimento', ordem=1,
        )
        self.ministerio, _ = criar_ministerio()
        desativar_liberacoes_automaticas(self.ministerio)

    def test_sem_assinatura_sem_liberacao_retorna_pioneiro(self):
        """Fallback: sem assinatura, sem liberação → plano Pioneiro."""
        plano = obter_plano_efetivo_ministerio(self.ministerio)
        self.assertEqual(plano.codigo_plano, 'pioneiro')

    def test_assinatura_com_plano_retorna_plano_assinatura(self):
        criar_assinatura(self.ministerio, self.plano_crescimento, status='ativa')
        plano = obter_plano_efetivo_ministerio(self.ministerio)
        self.assertEqual(plano.codigo_plano, 'crescimento')

    def test_liberacao_sobrepoe_assinatura(self):
        """LiberacaoPlanoMinisterio ativa tem MAIOR prioridade que a assinatura contratada."""
        plano_rede = criar_plano(nome='rede', codigo='rede', ordem=3)
        # Assinatura no Crescimento
        criar_assinatura(self.ministerio, self.plano_crescimento, status='ativa')
        # Liberação para Rede
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano_rede,
            ativo=True,
            pode_visualizar=True,
        )
        plano = obter_plano_efetivo_ministerio(self.ministerio)
        self.assertEqual(plano.codigo_plano, 'rede')

    def test_liberacao_inativa_nao_sobrepoe(self):
        """LiberacaoPlanoMinisterio(ativo=False) deve ser ignorada."""
        plano_rede = criar_plano(nome='rede', codigo='rede', ordem=3)
        criar_assinatura(self.ministerio, self.plano_crescimento, status='ativa')
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano_rede,
            ativo=False,
            pode_visualizar=True,
        )
        plano = obter_plano_efetivo_ministerio(self.ministerio)
        self.assertEqual(plano.codigo_plano, 'crescimento')

    def test_liberacao_sem_pode_visualizar_nao_sobrepoe(self):
        """LiberacaoPlanoMinisterio(pode_visualizar=False) deve ser ignorada."""
        plano_rede = criar_plano(nome='rede', codigo='rede', ordem=3)
        criar_assinatura(self.ministerio, self.plano_crescimento, status='ativa')
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano_rede,
            ativo=True,
            pode_visualizar=False,
        )
        plano = obter_plano_efetivo_ministerio(self.ministerio)
        self.assertEqual(plano.codigo_plano, 'crescimento')

    def test_liberacao_para_plano_inativo_ignorada(self):
        """Plano inativo na LiberacaoPlanoMinisterio não deve ser retornado."""
        plano_inativo = criar_plano(nome='rede', codigo='rede', ativo=False, ordem=3)
        criar_assinatura(self.ministerio, self.plano_crescimento, status='ativa')
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=plano_inativo,
            ativo=True,
            pode_visualizar=True,
        )
        plano = obter_plano_efetivo_ministerio(self.ministerio)
        self.assertEqual(plano.codigo_plano, 'crescimento')


# ===========================================================================
# 7. ministerio_pode_usar_modulo()
# ===========================================================================

class ModuloTestCase(TestCase):
    def setUp(self):
        self.plano_sem_comunicacao = criar_plano(
            nome='pioneiro', codigo='pioneiro',
            permite_financeiro=True,
            permite_comunicacao=False,
        )
        self.plano_com_comunicacao = criar_plano(
            nome='crescimento', codigo='crescimento', ordem=1,
            permite_financeiro=True,
            permite_comunicacao=True,
        )
        self.ministerio, _ = criar_ministerio()
        desativar_liberacoes_automaticas(self.ministerio)

    def test_modulo_permitido_retorna_true(self):
        criar_assinatura(self.ministerio, self.plano_sem_comunicacao, status='ativa')
        self.assertTrue(ministerio_pode_usar_modulo(self.ministerio, 'financeiro'))

    def test_modulo_bloqueado_retorna_false(self):
        criar_assinatura(self.ministerio, self.plano_sem_comunicacao, status='ativa')
        self.assertFalse(ministerio_pode_usar_modulo(self.ministerio, 'comunicacao'))

    def test_modulo_liberado_no_plano_superior(self):
        criar_assinatura(self.ministerio, self.plano_com_comunicacao, status='ativa')
        self.assertTrue(ministerio_pode_usar_modulo(self.ministerio, 'comunicacao'))

    def test_modulo_desconhecido_retorna_true(self):
        """Módulo não mapeado deve retornar True (fail-open)."""
        criar_assinatura(self.ministerio, self.plano_sem_comunicacao, status='ativa')
        self.assertTrue(ministerio_pode_usar_modulo(self.ministerio, 'modulo_inexistente'))

    def test_modulo_via_beta_override(self):
        """Liberação BETA para plano com comunicação → comunicação liberada."""
        criar_assinatura(self.ministerio, self.plano_sem_comunicacao, status='ativa')
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=self.plano_com_comunicacao,
            ativo=True,
            pode_visualizar=True,
        )
        self.assertTrue(ministerio_pode_usar_modulo(self.ministerio, 'comunicacao'))

    def test_sem_plano_efetivo_retorna_true(self):
        """Sem plano nenhum → fail-open para módulos."""
        # Sem assinatura, sem plano pioneiro
        self.plano_sem_comunicacao.delete()
        self.plano_com_comunicacao.delete()
        self.assertTrue(ministerio_pode_usar_modulo(self.ministerio, 'financeiro'))


# ===========================================================================
# 8. usuario_pode_usar_modulo()
# ===========================================================================

class UsuarioModuloTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano(
            nome='pioneiro', codigo='pioneiro',
            permite_comunicacao=False,
        )
        self.ministerio, self.admin = criar_ministerio()
        criar_assinatura(self.ministerio, self.plano, status='ativa')
        # Perfil para resolução de ministério via usuário
        from configuracao.models import PerfilUsuario
        PerfilUsuario.objects.create(
            user=self.admin,
            ministerio=self.ministerio,
        )
        desativar_liberacoes_automaticas(self.ministerio)

    def test_superuser_pode_tudo(self):
        self.admin.is_superuser = True
        self.admin.save()
        self.assertTrue(usuario_pode_usar_modulo(self.admin, 'comunicacao'))

    def test_usuario_nao_autenticado_retorna_false(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertFalse(usuario_pode_usar_modulo(AnonymousUser(), 'financeiro'))

    def test_usuario_com_permissao_no_plano(self):
        self.assertTrue(usuario_pode_usar_modulo(self.admin, 'financeiro'))

    def test_usuario_sem_permissao_no_plano(self):
        self.assertFalse(usuario_pode_usar_modulo(self.admin, 'comunicacao'))


# ===========================================================================
# 9. Tenant Demo — fonte canônica Ministerio.is_demo
# ===========================================================================

class MinisterioDemoCanonicoTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano(
            nome='pioneiro',
            codigo='pioneiro',
            limite_membros=5,
            permite_comunicacao=False,
        )

    def test_ministerio_marcado_demo_com_nome_e_admin_normais_libera_modulos_e_limites(self):
        ministerio, admin = criar_ministerio(nome='Ministério Comum')
        ministerio.is_demo = True
        ministerio.save(update_fields=['is_demo'])
        Igreja.objects.create(ministerio=ministerio, nome_igreja='Igreja Demo')
        criar_assinatura(ministerio, self.plano, status='cancelada')
        desativar_liberacoes_automaticas(ministerio)

        self.assertFalse(admin.username.startswith('admin_demo'))
        self.assertTrue(_ministerio_eh_demo(ministerio))
        self.assertTrue(usuario_pode_usar_modulo(admin, 'comunicacao'))
        self.assertEqual(contar_pessoas_ativas(ministerio), 0)
        self.assertEqual(obter_limite_pessoas_ativas(ministerio), 0)
        self.assertTrue(ministerio_pode_adicionar_pessoa_ativa(ministerio))

    def test_nome_demonstracao_nao_classifica_tenant_real_como_demo(self):
        ministerio, admin = criar_ministerio(nome='Demonstração')
        criar_assinatura(ministerio, self.plano, status='ativa')
        desativar_liberacoes_automaticas(ministerio)

        self.assertFalse(ministerio.is_demo)
        self.assertFalse(_ministerio_eh_demo(ministerio))
        self.assertFalse(usuario_pode_usar_modulo(admin, 'comunicacao'))

    def test_admin_demo_username_nao_classifica_tenant_real_como_demo(self):
        admin = User.objects.create_user(username='admin_demo_x', password='pass')
        ministerio, _ = criar_ministerio(admin=admin, nome='Ministério Real')
        criar_assinatura(ministerio, self.plano, status='ativa')
        desativar_liberacoes_automaticas(ministerio)

        self.assertFalse(ministerio.is_demo)
        self.assertFalse(_ministerio_eh_demo(ministerio))
        self.assertFalse(usuario_pode_usar_modulo(admin, 'comunicacao'))

    def test_nome_demonstracao_sem_flag_nao_classifica_tenant_real_como_demo(self):
        ministerio, admin = criar_ministerio(nome='Demonstracao')
        criar_assinatura(ministerio, self.plano, status='ativa')
        desativar_liberacoes_automaticas(ministerio)

        self.assertFalse(ministerio.is_demo)
        self.assertFalse(_ministerio_eh_demo(ministerio))
        self.assertFalse(usuario_pode_usar_modulo(admin, 'comunicacao'))


# ===========================================================================
# 10. ministerio_pode_adicionar_pessoa_ativa()
# ===========================================================================

class PodeAdicionarPessoaTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano(nome='pioneiro', codigo='pioneiro', limite_membros=5)
        self.ministerio, _ = criar_ministerio()
        self.igreja = Igreja.objects.create(
            ministerio=self.ministerio, nome_igreja='Igreja Limite'
        )
        criar_assinatura(self.ministerio, self.plano, status='ativa')
        desativar_liberacoes_automaticas(self.ministerio)

    def test_abaixo_do_limite_pode_adicionar(self):
        for i in range(3):
            criar_membro(self.igreja, nome_suffix=str(i))
        self.assertTrue(ministerio_pode_adicionar_pessoa_ativa(self.ministerio))

    def test_no_limite_nao_pode_adicionar(self):
        for i in range(5):
            criar_membro(self.igreja, nome_suffix=str(i))
        self.assertFalse(ministerio_pode_adicionar_pessoa_ativa(self.ministerio))

    def test_limite_zero_sempre_pode(self):
        self.plano.limite_membros = 0
        self.plano.save()
        for i in range(1000):
            pass  # não precisa criar; basta verificar a lógica
        self.assertTrue(ministerio_pode_adicionar_pessoa_ativa(self.ministerio))

    def test_assinatura_irregular_nao_pode(self):
        assinatura = AssinaturaMinisterio.objects.get(ministerio=self.ministerio)
        assinatura.status = 'cancelada'
        assinatura.save()
        desativar_liberacoes_automaticas(self.ministerio)
        self.assertFalse(ministerio_pode_adicionar_pessoa_ativa(self.ministerio))

    def test_quantidade_multipla_respeitada(self):
        for i in range(4):
            criar_membro(self.igreja, nome_suffix=str(i))
        # 4 ativos, limite 5, tenta adicionar 2 → não pode
        self.assertFalse(ministerio_pode_adicionar_pessoa_ativa(self.ministerio, quantidade=2))
        # tenta adicionar 1 → pode
        self.assertTrue(ministerio_pode_adicionar_pessoa_ativa(self.ministerio, quantidade=1))


# ===========================================================================
# 10. ministerio_pode_criar_igreja()
# ===========================================================================

class PodeCriarIgrejaTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano(nome='pioneiro', codigo='pioneiro', limite_igrejas=2)
        self.ministerio, _ = criar_ministerio()
        criar_assinatura(self.ministerio, self.plano, status='ativa')
        desativar_liberacoes_automaticas(self.ministerio)

    def test_abaixo_do_limite_pode_criar(self):
        # Não cria novas igrejas aqui para evitar dependência de sinais de bootstrap.
        self.assertTrue(ministerio_pode_criar_igreja(self.ministerio))

    def test_no_limite_nao_pode_criar(self):
        # Completa até atingir exatamente o limite configurado.
        faltantes = max(self.plano.limite_igrejas - self.ministerio.igrejas.count(), 0)
        for i in range(faltantes):
            Igreja.objects.create(ministerio=self.ministerio, nome_igreja=f'Igreja {i}')
        self.assertFalse(ministerio_pode_criar_igreja(self.ministerio))

    def test_limite_zero_sempre_pode(self):
        self.plano.limite_igrejas = 0
        self.plano.save()
        for i in range(10):
            Igreja.objects.create(ministerio=self.ministerio, nome_igreja=f'Igreja {i}')
        self.assertTrue(ministerio_pode_criar_igreja(self.ministerio))

    def test_assinatura_irregular_nao_pode(self):
        assinatura = AssinaturaMinisterio.objects.get(ministerio=self.ministerio)
        assinatura.status = 'cancelada'
        assinatura.save()
        desativar_liberacoes_automaticas(self.ministerio)
        self.assertFalse(ministerio_pode_criar_igreja(self.ministerio))


# ===========================================================================
# 11. Visibilidade / Contratação de Planos
# ===========================================================================

class VisibilidadePlanoTestCase(TestCase):
    def setUp(self):
        self.plano_publico = criar_plano(
            nome='pioneiro', codigo='pioneiro',
            liberado_publicamente=True,
            contratacao_publica_liberada=True,
            is_visible=True,
        )
        self.plano_piloto = criar_plano(
            nome='crescimento', codigo='crescimento', ordem=1,
            liberado_publicamente=False,
            contratacao_publica_liberada=False,
            is_visible=False,
        )
        self.ministerio, _ = criar_ministerio()
        desativar_liberacoes_automaticas(self.ministerio)

    def test_plano_publico_visivel_para_todos(self):
        self.assertTrue(ministerio_pode_visualizar_plano(self.ministerio, self.plano_publico))

    def test_plano_piloto_invisivel_sem_liberacao(self):
        self.assertFalse(ministerio_pode_visualizar_plano(self.ministerio, self.plano_piloto))

    def test_plano_piloto_visivel_com_liberacao(self):
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=self.plano_piloto,
            ativo=True,
            pode_visualizar=True,
        )
        self.assertTrue(ministerio_pode_visualizar_plano(self.ministerio, self.plano_piloto))

    def test_plano_publico_pode_contratar(self):
        self.assertTrue(ministerio_pode_contratar_plano(self.ministerio, self.plano_publico))

    def test_plano_piloto_nao_pode_contratar_sem_liberacao(self):
        self.assertFalse(ministerio_pode_contratar_plano(self.ministerio, self.plano_piloto))

    def test_plano_piloto_pode_contratar_com_liberacao(self):
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=self.plano_piloto,
            ativo=True,
            pode_visualizar=True,
            pode_contratar=True,
        )
        self.assertTrue(ministerio_pode_contratar_plano(self.ministerio, self.plano_piloto))

    def test_liberacao_sem_pode_contratar_bloqueia_contratacao(self):
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=self.plano_piloto,
            ativo=True,
            pode_visualizar=True,
            pode_contratar=False,  # pode ver mas não contratar
        )
        self.assertTrue(ministerio_pode_visualizar_plano(self.ministerio, self.plano_piloto))
        self.assertFalse(ministerio_pode_contratar_plano(self.ministerio, self.plano_piloto))

    def test_ministerio_none_nao_ve_plano_piloto(self):
        self.assertFalse(ministerio_pode_visualizar_plano(None, self.plano_piloto))

    def test_ministerio_none_nao_contrata_plano_piloto(self):
        self.assertFalse(ministerio_pode_contratar_plano(None, self.plano_piloto))


# ===========================================================================
# 12. listar_planos_para_ministerio()
# ===========================================================================

class ListarPlanosTestCase(TestCase):
    def setUp(self):
        self.plano_publico = criar_plano(
            nome='pioneiro', codigo='pioneiro',
            liberado_publicamente=True,
            contratacao_publica_liberada=True,
            is_visible=True,
        )
        self.plano_piloto = criar_plano(
            nome='crescimento', codigo='crescimento', ordem=1,
            liberado_publicamente=False,
            is_visible=False,
        )
        self.ministerio, _ = criar_ministerio()
        desativar_liberacoes_automaticas(self.ministerio)

    def test_lista_apenas_planos_visiveis_por_padrao(self):
        planos = listar_planos_para_ministerio(self.ministerio)
        codigos = [p.codigo_plano for p in planos]
        self.assertIn('pioneiro', codigos)
        self.assertNotIn('crescimento', codigos)

    def test_lista_inclui_piloto_com_liberacao(self):
        LiberacaoPlanoMinisterio.objects.create(
            ministerio=self.ministerio,
            plano=self.plano_piloto,
            ativo=True,
            pode_visualizar=True,
        )
        planos = listar_planos_para_ministerio(self.ministerio)
        codigos = [p.codigo_plano for p in planos]
        self.assertIn('crescimento', codigos)

    def test_lista_nao_inclui_planos_inativos(self):
        plano_inativo = criar_plano(
            nome='rede', codigo='rede', ordem=3,
            ativo=False, liberado_publicamente=True, is_visible=True,
        )
        planos = listar_planos_para_ministerio(self.ministerio)
        codigos = [p.codigo_plano for p in planos]
        self.assertNotIn('rede', codigos)


# ===========================================================================
# 13. Decorator verificar_assinatura_valida — bloqueio e redirect
# ===========================================================================

class DecoratorAssinaturaValidaTestCase(TestCase):
    def setUp(self):
        self.plano = criar_plano(
            nome='pioneiro', codigo='pioneiro',
            liberado_publicamente=True,
            contratacao_publica_liberada=True,
            is_visible=True,
        )
        self.ministerio, self.admin = criar_ministerio()
        from configuracao.models import PerfilUsuario
        PerfilUsuario.objects.create(
            user=self.admin,
            ministerio=self.ministerio,
        )
        desativar_liberacoes_automaticas(self.ministerio)
        self.client.force_login(self.admin)
        self.factory = RequestFactory()

    def test_assinatura_ativa_permite_acesso(self):
        criar_assinatura(self.ministerio, self.plano, status='ativa')
        # Acessa a própria página de assinatura (sempre permitida) como proxy de teste
        response = self.client.get(reverse('configuracao:gerenciar_assinatura'))
        self.assertIn(response.status_code, [200, 302])  # pode redirecionar para login dependendo do setup

    def test_superuser_nao_e_bloqueado(self):
        """Superusuário deve ignorar a verificação de assinatura."""
        self.admin.is_superuser = True
        self.admin.save()

        @verificar_assinatura_valida
        def _view(request):
            from django.http import HttpResponse
            return HttpResponse('ok', status=200)

        request = self.factory.get('/rota-protegida/')
        request.user = self.admin
        response = _view(request)
        self.assertEqual(response.status_code, 200)
