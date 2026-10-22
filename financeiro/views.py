from django.contrib.auth import get_user_model
from .models import PermissaoCaixa
# --- Gestão de Permissões de Caixa ---
from django.contrib.auth.decorators import login_required
from core.decorators import page_access_required
from financeiro.authorization import get_finance_read_scope, get_finance_write_scope


@login_required
@page_access_required('financeiro')

def gerenciar_permissoes_caixa(request, caixa_id):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    caixa = get_object_or_404(ContaBancaria, pk=caixa_id, igreja__in=allowed_churches)
    User = get_user_model()
    usuarios = User.objects.filter(
        is_active=True,
        perfil__ministerio=ministerio,
        perfil__igrejas_permitidas=caixa.igreja,
    ).distinct()
    permissoes = PermissaoCaixa.objects.filter(caixa=caixa).select_related('usuario')

    if request.method == 'POST':
        for usuario in usuarios:
            prefix = f'user_{usuario.id}_'
            pode_visualizar = bool(request.POST.get(prefix + 'visualizar'))
            pode_transferir = bool(request.POST.get(prefix + 'transferir'))
            pode_editar = bool(request.POST.get(prefix + 'editar'))
            perm, created = PermissaoCaixa.objects.get_or_create(usuario=usuario, caixa=caixa)
            perm.pode_visualizar = pode_visualizar
            perm.pode_transferir = pode_transferir
            perm.pode_editar = pode_editar
            perm.save()
        messages.success(request, 'Permissões atualizadas com sucesso!')
        return redirect('financeiro:gerenciar_permissoes_caixa', caixa_id=caixa.id)

    # Monta dicionário de permissões atuais
    permissoes_dict = {p.usuario_id: p for p in permissoes}
    return render(request, 'financeiro/gerenciar_permissoes_caixa.html', {
        'caixa': caixa,
        'usuarios': usuarios,
        'permissoes_dict': permissoes_dict,
    })
from django.db.models import Q
# c:\Gereigreja\financeiro\views.py
# financeiro/views.py
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test # Importar user_passes_test
from django.utils.timezone import now # Importar now

# Importar modelos corretos
from .models import (
    Receitas,
    Despesas,
    FundoDepartamental,
    ContaBancaria,
    FechamentoCaixa,
    ContaPagar,
    RecorrenciaContaPagar,
    CategoriaDespesa,
    DepartamentoFinanceiro,
    DepartamentoCaixa,
    Fornecedor,
    TransferenciaCaixa,
    ImportacaoExtratoOFX,
)
# Importar forms corretos
from .forms import (
    ReceitaForm, DespesaForm, CategoriaDespesaForm, FechamentoCaixaForm, ContaBancariaForm,
    FornecedorForm, ContaPagarForm, RegistrarPagamentoContaPagarForm, TransferenciaCaixaForm,
    RecorrenciaContaPagarForm,
)
# from django.contrib.auth.decorators import login_required # Removido, já importado acima
from configuracao.models import PerfilUsuario, Ministerio, Igreja
from eventos.models import Evento
from django.core.exceptions import PermissionDenied, ValidationError # Adicionar ValidationError
from django.http import Http404, HttpResponse
from django.db.models import Sum, Q, Count # Adicionado Count
# --- IMPORTAR UTILS DE PERMISSÃO ---

from .utils import has_finance_view_permission, has_finance_edit_permission, get_allowed_churches_for_user, is_finance_leader, is_admin_org # Importar is_admin_org
from core.utils import get_ministerio_or_error # Importar de core.utils # noqa: E402
# --- FIM IMPORT ---
from decimal import Decimal # Import Decimal
import csv
import locale
import logging, traceback, calendar 
from datetime import date, datetime, timedelta 
from urllib.parse import urlencode
from uuid import uuid4
from num2words import num2words
from openpyxl import Workbook
from django.db import transaction, connection # Adicionar import para transações atômicas
import json # Adicionar esta linha # noqa: E402
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from core.decorators import verificar_assinatura_valida # Ou o caminho correto
from .services import (
    DepartamentoFinanceiroService,
    OFXImportService,
    RecorrenciaContaPagarService,
    ReceitaFluxoService,
    _materialize_payable_edit_authorization_events,
    _resolve_locked_payable_policy,
    _validate_payable_domain_integrity,
    _validate_payable_historical_decision_evidence_before_edit,
    apply_payable_authorization_edit_plan,
    build_payable_authorization_edit_snapshot,
    build_payable_material_snapshot_v1,
    compute_payable_material_fingerprint_v1,
    create_payable,
    plan_payable_authorization_after_edit,
    refresh_payable_material_fingerprint,
)
from contas.constants import PASTOR_LOCAL, user_has_permission_level_or_higher

@login_required
@verificar_assinatura_valida # Nosso novo decorator
def minha_view_protegida(request):
    ministerio = get_ministerio_or_error(request) # Ainda chama para obter o ministério e verificar ministerio.ativo
    # ...
    # ... resto da view ...




# Configurar locale e logger
# from dateutil.relativedelta import relativedelta # Descomente se for usar relativedelta

logger = logging.getLogger(__name__)


def _get_safe_next_url(request, fallback_url_name):
    """Return a safe local redirect target from request next param."""
    next_url = (request.POST.get('next') or request.GET.get('next') or '').strip()
    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return reverse(fallback_url_name)


def _fundos_departamentais_disponivel():
    """Retorna True quando a tabela de fundos departamentais existe no banco atual."""
    try:
        return 'financeiro_fundodepartamental' in connection.introspection.table_names()
    except Exception:
        return False


def _obter_ids_contas_eventos_para_igreja(igreja):
    """Retorna IDs de contas/caixas tratadas como contexto de eventos na igreja."""
    if not igreja:
        return []

    contas_eventos_ids = set(
        DepartamentoCaixa.objects.filter(
            departamento__igreja=igreja,
            departamento__codigo_interno=DepartamentoFinanceiro.CODIGO_EVENTOS,
            departamento__ativo=True,
            ativo=True,
            is_padrao=True,
        ).values_list('conta_bancaria_id', flat=True)
    )

    conta_padrao_eventos_id = getattr(igreja, 'conta_padrao_eventos_id', None)
    if conta_padrao_eventos_id:
        contas_eventos_ids.add(conta_padrao_eventos_id)

    return sorted(contas_eventos_ids)


def _batch_session_key(tipo, igreja_id):
    return f'financeiro_batch_{tipo}_{igreja_id}'


def _batch_get(request, tipo, igreja_id):
    return request.session.get(_batch_session_key(tipo, igreja_id), [])


def _batch_set(request, tipo, igreja_id, itens):
    request.session[_batch_session_key(tipo, igreja_id)] = itens
    request.session.modified = True


def _batch_clear(request, tipo, igreja_id):
    request.session.pop(_batch_session_key(tipo, igreja_id), None)
    request.session.modified = True


def _batch_defaults_session_key(tipo, igreja_id):
    return f'financeiro_batch_defaults_{tipo}_{igreja_id}'


def _batch_defaults_get(request, tipo, igreja_id):
    return request.session.get(_batch_defaults_session_key(tipo, igreja_id), {})


def _batch_defaults_set(request, tipo, igreja_id, valores):
    request.session[_batch_defaults_session_key(tipo, igreja_id)] = valores
    request.session.modified = True


def _resolver_fundo_para_politica_saida(despesa):
    if despesa.fundo_departamental_id:
        return despesa.fundo_departamental

    if despesa.evento_id and despesa.igreja_id:
        return FundoDepartamental.objects.filter(
            igreja=despesa.igreja,
            codigo=FundoDepartamental.CODIGO_EVENTOS,
        ).first()

    if despesa.igreja_id:
        return FundoDepartamental.objects.filter(
            igreja=despesa.igreja,
            codigo=FundoDepartamental.CODIGO_LOCAL,
        ).first()

    return None


def _user_pode_aprovar_saida(user):
    return is_admin_org(user) or user_has_permission_level_or_higher(user, PASTOR_LOCAL)


def _aplicar_politica_aprovacao_saida(request, despesa):
    fundo = _resolver_fundo_para_politica_saida(despesa)
    if not fundo and not despesa.igreja_id:
        despesa.aprovacao_status = Despesas.APROVACAO_APROVADA
        despesa.aprovado_por = request.user
        despesa.aprovado_em = now()
        return None

    departamento_financeiro = None
    if despesa.igreja_id:
        codigo_departamento = None
        if fundo and fundo.codigo:
            codigo_departamento = (fundo.codigo or '').strip().upper()
        elif despesa.evento_id:
            codigo_departamento = FundoDepartamental.CODIGO_EVENTOS
        else:
            codigo_departamento = FundoDepartamental.CODIGO_LOCAL

        if codigo_departamento:
            departamento_financeiro = DepartamentoFinanceiro.objects.filter(
                igreja=despesa.igreja,
                codigo_interno=codigo_departamento,
            ).first()

    if not departamento_financeiro and fundo is not None:
        departamento_financeiro = getattr(fundo, 'departamento_financeiro', None)

    if not departamento_financeiro or not departamento_financeiro.ativo:
        despesa.aprovacao_status = Despesas.APROVACAO_APROVADA
        despesa.aprovado_por = request.user
        despesa.aprovado_em = now()
        return None

    politica = getattr(departamento_financeiro, 'politica', None)
    if not politica or not politica.exige_aprovacao_para_saida:
        despesa.aprovacao_status = Despesas.APROVACAO_APROVADA
        despesa.aprovado_por = request.user
        despesa.aprovado_em = now()
        return None

    valor_despesa = despesa.valor or Decimal('0')
    limite_aprovacao = politica.valor_minimo_para_aprovacao
    if limite_aprovacao is not None and valor_despesa < limite_aprovacao:
        despesa.aprovacao_status = Despesas.APROVACAO_APROVADA
        despesa.aprovado_por = request.user
        despesa.aprovado_em = now()
        return None

    if (
        _user_pode_aprovar_saida(request.user)
        and despesa.criado_por_id != request.user.id
    ):
        despesa.aprovacao_status = Despesas.APROVACAO_APROVADA
        despesa.aprovado_por = request.user
        despesa.aprovado_em = now()
        if not despesa.observacao_aprovacao:
            despesa.observacao_aprovacao = 'Aprovacao automatica por perfil autorizado.'
        return None

    despesa.aprovacao_status = Despesas.APROVACAO_PENDENTE
    despesa.aprovado_por = None
    despesa.aprovado_em = None
    descricao_limite = f" acima de R$ {limite_aprovacao}" if limite_aprovacao is not None else ''
    return (
        f"A politica do departamento '{departamento_financeiro.nome_exibicao}' exige aprovacao para saidas"
        f"{descricao_limite}. Lancamento salvo como pendente para aprovacao de um Pastor Local ou superior."
    )

# Tenta configurar o locale para pt_BR, com fallbacks.
locales_to_try = ['pt_BR.UTF-8', 'Portuguese_Brazil.1252']
locale_set = False
for loc in locales_to_try:
    try:
        locale.setlocale(locale.LC_ALL, loc)
        locale_set = True
        break # Sucesso, para o loop
    except locale.Error:
        continue # Tenta o próximo
if not locale_set:
    logger.warning(f"Nenhum dos locales {locales_to_try} foi suportado. Usando o locale padrão do sistema.")


## A função get_ministerio_or_error foi movida para core.utils.py ##


@page_access_required('financeiro')
def painel_financeiro(request):
    """ Painel/Dashboard Financeiro da Ministério ou de uma Igreja específica. """
    ministerio = get_ministerio_or_error(request)
    try:
        allowed_churches = get_allowed_churches_for_user(request.user) # Igrejas permitidas
        # --- FILTRO DE IGREJA ---
        igreja_id_filtro_get = request.GET.get('igreja_filtro', '') # Pega o ID da igreja do GET, default ''
        igreja_selecionada_para_dados = None # Igreja usada para filtrar os DADOS do painel

        
        
        
        
        # --- Lógica para usar request.igreja_ativa para filtrar o painel ---
        # Se uma igreja ativa está selecionada E é permitida para o usuário, use-a como filtro principal
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_selecionada_para_dados = request.igreja_ativa
            titulo_dashboard = f"Igreja: {igreja_selecionada_para_dados.nome_igreja}"
            # Se uma igreja ativa está definida, o filtro de igreja_id_filtro do GET é ignorado para a filtragem principal
            # e o dropdown de filtro da página deve mostrar apenas a igreja ativa.
            igrejas_para_filtro_template = Igreja.objects.filter(pk=request.igreja_ativa.pk)
            igreja_id_filtro_selecionado_template = str(request.igreja_ativa.pk)
        else:
            # Se nenhuma igreja ativa, ou a ativa não é permitida, use o filtro do GET (se houver e for permitido)
            if igreja_id_filtro_get:
                try:
                    igreja_selecionada_para_dados = allowed_churches.get(pk=igreja_id_filtro_get) # Garante que a igreja do GET é permitida
                    titulo_dashboard = f"Igreja: {igreja_selecionada_para_dados.nome_igreja}"
                except Igreja.DoesNotExist:
                    messages.warning(request, "Igreja selecionada inválida ou não permitida. Mostrando dados consolidados.")
                    igreja_id_filtro_get = '' # Reseta o filtro
            # Se nenhum filtro do GET e nenhuma igreja ativa, mostra dados de todas as igrejas permitidas
            if not igreja_selecionada_para_dados:
                titulo_dashboard = f"Ministério: {ministerio.nome_fantasia} (Igrejas Permitidas)"

        
             # Para o dropdown de filtro na página, mostrar todas as permitidas se nenhuma global estiver ativa
            igrejas_para_filtro_template = allowed_churches.order_by('nome_igreja')
            igreja_id_filtro_selecionado_template = igreja_id_filtro_get
        
        
        
        # --- FIM FILTRO DE IGREJA ---

        # --- LÓGICA DO FILTRO DE PERÍODO ---
        periodo_filtro = request.GET.get('periodo_filtro', 'aberto') # Pega o valor do GET, default 'aberto'
        ano_atual = date.today().year
        data_hoje = date.today()
        data_inicio_mes = data_hoje.replace(day=1)

        # --- Filtro de data livre ---
        data_inicio_filtro_str = request.GET.get('data_inicio', '')
        data_fim_filtro_str    = request.GET.get('data_fim', '')
        data_inicio_filtro = None
        data_fim_filtro    = None
        if data_inicio_filtro_str and data_fim_filtro_str:
            try:
                from datetime import datetime as dt
                data_inicio_filtro = dt.strptime(data_inicio_filtro_str, '%Y-%m-%d').date()
                data_fim_filtro    = dt.strptime(data_fim_filtro_str,    '%Y-%m-%d').date()
                periodo_filtro = 'custom'
            except ValueError:
                data_inicio_filtro = None
                data_fim_filtro    = None

        # --- FILTRO DE DEPARTAMENTO ---
        departamento_filtro = (request.GET.get('dept_filtro') or '').strip()
        departamento_contexto_obj = None
        departamento_contexto_label = None

        if igreja_selecionada_para_dados:
            igrejas_escopo_departamento = Igreja.objects.filter(pk=igreja_selecionada_para_dados.pk)
        else:
            igrejas_escopo_departamento = allowed_churches

        if departamento_filtro:
            departamento_contexto_obj = DepartamentoFinanceiro.objects.filter(
                igreja__in=igrejas_escopo_departamento,
                pk=departamento_filtro,
                ativo=True,
            ).select_related('departamento', 'fundo_departamental').first()
            if departamento_contexto_obj:
                departamento_contexto_label = departamento_contexto_obj.nome_exibicao
                if departamento_contexto_obj.fundo_departamental_id and not fundo_id_filtro:
                    fundo_id_filtro = str(departamento_contexto_obj.fundo_departamental_id)
            else:
                messages.warning(request, 'Departamento selecionado inválido ou fora do seu escopo. Mostrando visão consolidada.')
                departamento_filtro = ''

        # --- FILTRO DE CAIXA ---
        caixa_id_filtro = (request.GET.get('caixa_filtro') or '').strip()
        fundo_id_filtro = (request.GET.get('fundo_filtro') or '').strip()
        fundos_disponivel = _fundos_departamentais_disponivel()
        if igreja_selecionada_para_dados:
            contas_bancarias_dropdown = ContaBancaria.objects.filter(
                igreja=igreja_selecionada_para_dados
            ).order_by('nome_identificacao')
            if fundos_disponivel:
                fundos_departamentais_dropdown = DepartamentoFinanceiroService.fundos_visiveis_para_igrejas(
                    [igreja_selecionada_para_dados]
                )
            else:
                fundos_departamentais_dropdown = FundoDepartamental.objects.none()
        else:
            contas_bancarias_dropdown = ContaBancaria.objects.filter(
                igreja__in=allowed_churches
            ).order_by('igreja__nome_igreja', 'nome_identificacao')
            if fundos_disponivel:
                fundos_departamentais_dropdown = DepartamentoFinanceiroService.fundos_visiveis_para_igrejas(
                    allowed_churches
                )
            else:
                fundos_departamentais_dropdown = FundoDepartamental.objects.none()

        if caixa_id_filtro and not contas_bancarias_dropdown.filter(pk=caixa_id_filtro).exists():
            messages.warning(request, 'Caixa selecionado inválido para o seu escopo. Exibindo dados consolidados por caixa.')
            caixa_id_filtro = ''
        if fundos_disponivel:
            if fundo_id_filtro and not fundos_departamentais_dropdown.filter(pk=fundo_id_filtro).exists():
                messages.warning(request, 'Fundo selecionado inválido para o seu escopo. Exibindo dados consolidados por fundo.')
                fundo_id_filtro = ''
        else:
            fundo_id_filtro = ''

        if departamento_contexto_obj and departamento_contexto_obj.fundo_departamental_id:
            fundo_id_filtro = str(departamento_contexto_obj.fundo_departamental_id)

        # Base Querysets - AGORA FILTRADOS PELAS IGREJAS PERMITIDAS ou pela igreja selecionada (se permitida)
        # Se igreja_selecionada (do seletor global ou do filtro GET) está definida, filtra por ela


        if igreja_selecionada_para_dados:
            receitas_base = Receitas.objects.filter(igreja=igreja_selecionada_para_dados)
            despesas_base = Despesas.objects.filter(igreja=igreja_selecionada_para_dados)
        else: # Todas as igrejas permitidas para o usuário
            receitas_base = Receitas.objects.filter(igreja__in=allowed_churches) # Já filtrado por allowed_churches
            despesas_base = Despesas.objects.filter(igreja__in=allowed_churches) # Já filtrado por allowed_churches

        if caixa_id_filtro:
            receitas_base = receitas_base.filter(conta_bancaria_id=caixa_id_filtro)
            despesas_base = despesas_base.filter(conta_bancaria_id=caixa_id_filtro)
        if fundos_disponivel and fundo_id_filtro:
            receitas_base = receitas_base.filter(fundo_departamental_id=fundo_id_filtro)
            despesas_base = despesas_base.filter(fundo_departamental_id=fundo_id_filtro)


         # --- Base para Contas a Pagar (filtrado por igreja/allowed_churches) ---
        if igreja_selecionada_para_dados:
            contas_pagar_base = ContaPagar.objects.filter(igreja=igreja_selecionada_para_dados)
        else:
            contas_pagar_base = ContaPagar.objects.filter(igreja__in=allowed_churches) 

        if caixa_id_filtro:
            contas_pagar_base = contas_pagar_base.filter(conta_debito_id=caixa_id_filtro)
        
        # --- Indicadores de Contas a Pagar ---
        total_contas_pendentes = contas_pagar_base.filter(
            status='PEN'
        ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
        total_contas_vencidas = contas_pagar_base.filter(
            status='VEN' # Ou usar a propriedade is_vencida se preferir, mas status='VEN' é mais direto
        ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
        qtd_contas_pendentes = contas_pagar_base.filter(status='PEN').count()
        qtd_contas_vencidas = contas_pagar_base.filter(status='VEN').count()
        # --- FIM Indicadores de Contas a Pagar ---

        # --- Indicadores de Contas Fixas no mês atual ---
        contas_fixas_mes_base = contas_pagar_base.filter(
            Q(recorrencia_origem__isnull=False) | Q(criado_automaticamente=True),
            data_vencimento__year=ano_atual,
            data_vencimento__month=data_hoje.month,
        )
        total_contas_fixas_previstas = contas_fixas_mes_base.aggregate(total=Sum('valor'))['total'] or Decimal(0)
        total_contas_fixas_pagas = contas_fixas_mes_base.filter(status='PAG').aggregate(total=Sum('valor'))['total'] or Decimal(0)
        total_contas_fixas_atrasadas = contas_fixas_mes_base.filter(
            status__in=['PEN', 'VEN'],
            data_vencimento__lt=data_hoje,
        ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
        qtd_contas_fixas_previstas = contas_fixas_mes_base.count()
        qtd_contas_fixas_pagas = contas_fixas_mes_base.filter(status='PAG').count()
        qtd_contas_fixas_atrasadas = contas_fixas_mes_base.filter(
            status__in=['PEN', 'VEN'],
            data_vencimento__lt=data_hoje,
        ).count()
        # --- FIM Indicadores de Contas Fixas ---

       


        # Aplicar filtro de período aos querysets base (já filtrados por igreja, se aplicável)
        if periodo_filtro == 'aberto':
            receitas_filtradas = receitas_base.filter(fechado=False)
            despesas_filtradas = despesas_base.filter(fechado=False)
            titulo_filtro_periodo = "Em Aberto"
        elif periodo_filtro == 'ano_atual':
            receitas_filtradas = receitas_base.filter(data__year=ano_atual)
            despesas_filtradas = despesas_base.filter(data__year=ano_atual)
            titulo_filtro_periodo = f"Ano {ano_atual}"
        elif periodo_filtro == 'custom' and data_inicio_filtro and data_fim_filtro:
            receitas_filtradas = receitas_base.filter(data__range=(data_inicio_filtro, data_fim_filtro))
            despesas_filtradas = despesas_base.filter(data__range=(data_inicio_filtro, data_fim_filtro))
            titulo_filtro_periodo = f"{data_inicio_filtro.strftime('%d/%m/%Y')} – {data_fim_filtro.strftime('%d/%m/%Y')}"
        else: # 'geral' ou default
            receitas_filtradas = receitas_base
            despesas_filtradas = despesas_base
            titulo_filtro_periodo = "Geral"
        # --- FIM DA LÓGICA DO FILTRO DE PERÍODO ---


        # --- DADOS PARA GRÁFICO DE CATEGORIAS DE RECEITA (MOVIDO PARA DEPOIS DA DEFINIÇÃO DE receitas_filtradas) ---
        categorias_receita_data_qs = receitas_filtradas.values(
            'categoria'  # Agrupa pelo código da categoria
        ).annotate(
            total=Sum('valor')  # Soma os valores
        ).filter(total__gt=0).order_by('-total')

        # Mapear os códigos para os nomes display
        mapa_cat_receita_display = {codigo: nome for codigo, nome in Receitas.CATEGORIA_CHOICES}

        grafico_cat_rec_labels = [mapa_cat_receita_display.get(item['categoria'], item['categoria']) for item in categorias_receita_data_qs]
        grafico_cat_rec_valores = [float(item['total']) for item in categorias_receita_data_qs]
        # --- FIM DADOS PARA GRÁFICO DE CATEGORIAS DE RECEITA ---

        # --- DADOS PARA GRÁFICO DE CATEGORIAS DE DESPESA (MOVIDO PARA DEPOIS DA DEFINIÇÃO DE despesas_filtradas) ---
        categorias_despesa_data = despesas_filtradas.values(
            'categoria__nome' # Agrupa pelo nome da categoria
        ).annotate(
            total=Sum('valor') # Soma os valores
        ).filter(total__gt=0).order_by('-total') # Filtra categorias com total > 0 e ordena
        
        grafico_cat_desp_labels = [item['categoria__nome'] if item['categoria__nome'] else "Sem Categoria" for item in categorias_despesa_data]
        grafico_cat_desp_valores = [float(item['total']) for item in categorias_despesa_data]
        # --- FIM DADOS PARA GRÁFICO DE CATEGORIAS DE DESPESA ---


        # Calcular totais USANDO os querysets duplamente filtrados (igreja E período)
        total_receitas = receitas_filtradas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        total_despesas = despesas_filtradas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        saldo_geral = total_receitas - total_despesas

        # KPIs por fundo no escopo/periodo corrente
        if fundos_disponivel:
            receitas_local = receitas_filtradas.filter(fundo_departamental__codigo='LOCAL').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            receitas_eventos = receitas_filtradas.filter(fundo_departamental__codigo='EVENTOS').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            receitas_missoes = receitas_filtradas.filter(fundo_departamental__codigo='MISSOES').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            receitas_assistencia = receitas_filtradas.filter(fundo_departamental__codigo='ASSISTENCIA').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            despesas_local = despesas_filtradas.filter(fundo_departamental__codigo='LOCAL').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            despesas_eventos = despesas_filtradas.filter(fundo_departamental__codigo='EVENTOS').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            despesas_missoes = despesas_filtradas.filter(fundo_departamental__codigo='MISSOES').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            despesas_assistencia = despesas_filtradas.filter(fundo_departamental__codigo='ASSISTENCIA').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        else:
            receitas_local = Decimal(0)
            receitas_eventos = Decimal(0)
            receitas_missoes = Decimal(0)
            receitas_assistencia = Decimal(0)
            despesas_local = Decimal(0)
            despesas_eventos = Decimal(0)
            despesas_missoes = Decimal(0)
            despesas_assistencia = Decimal(0)

        # Saldo do mês atual (também filtrado por igreja, se aplicável)
        receitas_mes = receitas_base.filter(data__gte=data_inicio_mes).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        despesas_mes = despesas_base.filter(data__gte=data_inicio_mes).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        saldo_mes = receitas_mes - despesas_mes

        # --- TENDÊNCIA: mês calendário anterior ---
        primeiro_dia_mes_ant = (data_inicio_mes - timedelta(days=1)).replace(day=1)
        ultimo_dia_mes_ant   = data_inicio_mes - timedelta(days=1)
        receitas_mes_anterior  = receitas_base.filter(data__range=(primeiro_dia_mes_ant, ultimo_dia_mes_ant)).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        despesas_mes_anterior  = despesas_base.filter(data__range=(primeiro_dia_mes_ant, ultimo_dia_mes_ant)).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)

        def calc_variacao_pct(atual, anterior):
            if anterior == 0:
                return None  # sem referência
            return round(float((atual - anterior) / anterior * 100), 1)

        variacao_receitas_pct  = calc_variacao_pct(receitas_mes, receitas_mes_anterior)
        variacao_despesas_pct  = calc_variacao_pct(despesas_mes, despesas_mes_anterior)
        diferenca_receitas = receitas_mes - receitas_mes_anterior
        diferenca_despesas = despesas_mes - despesas_mes_anterior
        saldo_mes_anterior = receitas_mes_anterior - despesas_mes_anterior
        diferenca_saldo = saldo_mes - saldo_mes_anterior
        variacao_saldo_pct = calc_variacao_pct(saldo_mes, saldo_mes_anterior)
        # --- FIM TENDÊNCIA ---

        # Últimas receitas/despesas (filtradas por igreja, se aplicável)
        ultimas_receitas = receitas_filtradas.select_related('igreja', 'membro').order_by('-data')[:5]
        ultimas_despesas = despesas_filtradas.select_related('igreja', 'categoria').order_by('-data')[:5]

        # Permissão de edição para o template
        can_edit = has_finance_edit_permission(request.user)

        # --- DADOS PARA GRÁFICOS MENSAIS (ÚLTIMOS 12 MESES) ---
        hoje_grafico = date.today()
        meses_labels_grafico = []
        receitas_mensais_grafico_data = []
        despesas_mensais_grafico_data = []
        saldos_mensais_grafico_data = []
        # Dizimistas únicos mensais (será populado abaixo)

        dizimistas_unicos_mensais_grafico_data = []

        # Base para filtros de igreja para os gráficos
        # Usaremos as mesmas 'receitas_base' e 'despesas_base' já filtradas por igreja/allowed_churches
        # Se 'receitas_base' e 'despesas_base' não estiverem definidas se não houver filtro de igreja,
        # precisamos redefini-las aqui com base em allowed_churches.
        # No seu código atual, elas já são definidas com base em allowed_churches se igreja_selecionada for None.
        
         # --- DADOS PARA GRÁFICO DE DIZIMISTAS POR FECHAMENTO DE CAIXA ---
        dizimistas_por_fechamento_labels = []
        dizimistas_por_fechamento_valores = []
        # Usaremos os 'ultimos_fechamentos' já buscados para o gráfico de movimentação

        # --- DADOS PARA GRÁFICO DE MOVIMENTAÇÃO POR FECHAMENTOS DE CAIXA (ÚLTIMOS 6) ---
        ultimos_fechamentos_qs = FechamentoCaixa.objects.filter(
            igreja__in=(allowed_churches if not igreja_selecionada_para_dados else [igreja_selecionada_para_dados])
        ).order_by('-data_fim')[:6] # Pega os últimos 6 fechamentos

        # Inverter a ordem para o gráfico (do mais antigo para o mais recente)
        ultimos_fechamentos = sorted(list(ultimos_fechamentos_qs), key=lambda fc: fc.data_fim)

        grafico_fech_labels = []
        grafico_fech_receitas_data = []
        grafico_fech_despesas_data = []
        grafico_fech_saldos_data = []

        for fc in ultimos_fechamentos:
            label = f"{fc.data_inicio.strftime('%d/%m')} a {fc.data_fim.strftime('%d/%m/%y')}"
            grafico_fech_labels.append(label)

            if caixa_id_filtro:
                receitas_no_fechamento = receitas_base.filter(
                    data__gte=fc.data_inicio,
                    data__lte=fc.data_fim,
                ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
                despesas_no_fechamento = despesas_base.filter(
                    data__gte=fc.data_inicio,
                    data__lte=fc.data_fim,
                ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
                grafico_fech_receitas_data.append(float(receitas_no_fechamento))
                grafico_fech_despesas_data.append(float(despesas_no_fechamento))
                grafico_fech_saldos_data.append(float(receitas_no_fechamento - despesas_no_fechamento))
            else:
                grafico_fech_receitas_data.append(float(fc.total_entradas))
                grafico_fech_despesas_data.append(float(fc.total_saidas))
                grafico_fech_saldos_data.append(float(fc.saldo_final))

            # Contar dizimistas únicos para este fechamento
            dizimistas_no_fechamento_count = receitas_base.filter(
                data__gte=fc.data_inicio,
                data__lte=fc.data_fim,
                categoria='dizimo',
                membro__isnull=False
            ).values('membro').distinct().count()
            dizimistas_por_fechamento_labels.append(f"Fech. {fc.data_fim.strftime('%b/%y')}")
            dizimistas_por_fechamento_valores.append(dizimistas_no_fechamento_count)

        # --- FIM DADOS PARA GRÁFICO DE MOVIMENTAÇÃO POR FECHAMENTOS ---

        
        
        meses_para_iterar = []
        for i in range(11, -1, -1): # Gera datas para os últimos 12 meses (do mais antigo para o mais recente)
            ano_alvo = hoje_grafico.year
            mes_alvo_num = hoje_grafico.month - i
            while mes_alvo_num <= 0:
                mes_alvo_num += 12
                ano_alvo -= 1
            meses_para_iterar.append(date(ano_alvo, mes_alvo_num, 1))

        for data_mes_loop in meses_para_iterar:
            ano = data_mes_loop.year
            mes = data_mes_loop.month

            # Formatar label do mês (Ex: Mai/25)
            # O locale já deve estar configurado para pt_BR no início da view
            mes_label = data_mes_loop.strftime("%b/%y").capitalize()
            meses_labels_grafico.append(mes_label)

            # Receitas do mês (alinhadas ao período selecionado no painel)
            receitas_do_mes_val = receitas_filtradas.filter(
                data__year=ano, data__month=mes
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
            receitas_mensais_grafico_data.append(float(receitas_do_mes_val))

            # Despesas do mês (alinhadas ao período selecionado no painel)
            despesas_do_mes_val = despesas_filtradas.filter(
                data__year=ano, data__month=mes
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
            despesas_mensais_grafico_data.append(float(despesas_do_mes_val))

            # Saldo do mês
            saldos_mensais_grafico_data.append(float(receitas_do_mes_val - despesas_do_mes_val))

            # Dizimistas únicos do mês (alinhados ao período selecionado)
            dizimistas_count = receitas_filtradas.filter(
                data__year=ano, data__month=mes, 
                categoria='dizimo', 
                membro__isnull=False # Apenas garante que há um membro associado
            ).values('membro').distinct().count()
            dizimistas_unicos_mensais_grafico_data.append(dizimistas_count)
        # --- FIM DADOS PARA GRÁFICOS MENSAIS ---

          # --- NOVO: DADOS PARA GRÁFICO DE PERFIL DOS DIZIMISTAS (POR TIPO DE PESSOA) ---
        # Usaremos 'receitas_filtradas' que já considera o filtro de período do painel
        dizimos_no_periodo_filtrado = receitas_filtradas.filter(categoria='dizimo', membro__isnull=False)

        perfil_dizimistas_data_qs = dizimos_no_periodo_filtrado.values(
            'membro__tipo_pessoa__nome' # Agrupa pelo nome do TipoPessoa do membro
        ).annotate(
            quantidade_dizimistas=Count('membro', distinct=True), # Conta membros distintos
            valor_total_dizimado=Sum('valor') # Soma o valor dos dízimos
        ).order_by('membro__tipo_pessoa__nome')

        perfil_dizimistas_labels = []
        perfil_dizimistas_qtd_valores = []
        perfil_dizimistas_total_valores = []

        total_geral_dizimistas_no_periodo = dizimos_no_periodo_filtrado.values('membro').distinct().count()
        total_geral_valor_dizimado_no_periodo = dizimos_no_periodo_filtrado.aggregate(total=Sum('valor'))['total'] or Decimal(0)

        perfil_dizimistas_qtd_percentuais = []
        perfil_dizimistas_valor_percentuais = []

        for item in perfil_dizimistas_data_qs:
            tipo_nome = item['membro__tipo_pessoa__nome'] if item['membro__tipo_pessoa__nome'] else "Sem Tipo"
            perfil_dizimistas_labels.append(tipo_nome)
            perfil_dizimistas_qtd_valores.append(item['quantidade_dizimistas'])
            perfil_dizimistas_total_valores.append(float(item['valor_total_dizimado']))

            # Calcular percentuais
            qtd_perc = (item['quantidade_dizimistas'] / total_geral_dizimistas_no_periodo * 100) if total_geral_dizimistas_no_periodo > 0 else 0
            perfil_dizimistas_qtd_percentuais.append(round(qtd_perc, 2))

            valor_perc = (item['valor_total_dizimado'] / total_geral_valor_dizimado_no_periodo * 100) if total_geral_valor_dizimado_no_periodo > 0 else 0
            perfil_dizimistas_valor_percentuais.append(round(float(valor_perc), 2))

        # --- FIM NOVO GRÁFICO DE PERFIL ---


        # --- DADOS PARA LISTAGEM DE SALDOS DE CONTAS BANCÁRIAS/CAIXAS ---
        # Queryset para o painel: aplica filtro de caixa se houver
        if caixa_id_filtro:
            contas_bancarias_painel = contas_bancarias_dropdown.filter(pk=caixa_id_filtro)
        else:
            contas_bancarias_painel = contas_bancarias_dropdown

        caixa_selecionada_obj = contas_bancarias_dropdown.filter(pk=caixa_id_filtro).first() if caixa_id_filtro else None

        query_receitas_despesas_parts = []
        if igreja_id_filtro_selecionado_template:
            query_receitas_despesas_parts.append(f"igreja={igreja_id_filtro_selecionado_template}")
        if caixa_id_filtro:
            query_receitas_despesas_parts.append(f"caixa_filtro={caixa_id_filtro}")
        if fundo_id_filtro:
            query_receitas_despesas_parts.append(f"fundo_filtro={fundo_id_filtro}")
        if periodo_filtro == 'custom' and data_inicio_filtro_str and data_fim_filtro_str:
            query_receitas_despesas_parts.append(f"data_inicio={data_inicio_filtro_str}")
            query_receitas_despesas_parts.append(f"data_fim={data_fim_filtro_str}")
        elif periodo_filtro == 'aberto':
            query_receitas_despesas_parts.append("fechado=false")
        elif periodo_filtro == 'ano_atual':
            query_receitas_despesas_parts.append(f"data_inicio={ano_atual}-01-01")
            query_receitas_despesas_parts.append(f"data_fim={data_hoje.strftime('%Y-%m-%d')}")
        query_receitas_despesas = f"?{'&'.join(query_receitas_despesas_parts)}" if query_receitas_despesas_parts else ''

        query_contas_pagar_params = {}
        if igreja_id_filtro_selecionado_template:
            query_contas_pagar_params['igreja'] = igreja_id_filtro_selecionado_template
        if caixa_id_filtro:
            query_contas_pagar_params['caixa_filtro'] = caixa_id_filtro
        query_contas_pagar_suffix = f"?{urlencode(query_contas_pagar_params)}" if query_contas_pagar_params else ''
        query_contas_pagar_extra = f"&{urlencode(query_contas_pagar_params)}" if query_contas_pagar_params else ''

        limpar_params = {}
        if igreja_id_filtro_selecionado_template and not request.igreja_ativa:
            limpar_params['igreja_filtro'] = igreja_id_filtro_selecionado_template
        url_limpar_filtros = reverse('financeiro:painel_financeiro')
        if limpar_params:
            url_limpar_filtros = f"{url_limpar_filtros}?{urlencode(limpar_params)}"

        voltar_geral_params = dict(limpar_params)
        voltar_geral_params['periodo_filtro'] = 'geral'
        url_voltar_geral = f"{reverse('financeiro:painel_financeiro')}?{urlencode(voltar_geral_params)}"

        dashboard_tem_dados = receitas_filtradas.exists() or despesas_filtradas.exists() or contas_pagar_base.exists()

        escopo_igreja_label = igreja_selecionada_para_dados.nome_igreja if igreja_selecionada_para_dados else 'Todas as igrejas permitidas'
        escopo_caixa_label = caixa_selecionada_obj.nome_identificacao if caixa_selecionada_obj else 'Todos os caixas'
        fundo_selecionado_obj = fundos_departamentais_dropdown.filter(pk=fundo_id_filtro).first() if fundo_id_filtro else None
        escopo_fundo_label = fundo_selecionado_obj.nome_exibicao if fundo_selecionado_obj else 'Todos os fundos'

        context = {
            'contas_bancarias_dropdown': contas_bancarias_dropdown,
            'fundos_departamentais_dropdown': fundos_departamentais_dropdown,
            'fundos_departamentais_disponivel': fundos_disponivel,
            'ministerio': ministerio,
            'igrejas_org': igrejas_para_filtro_template,
            'igreja_selecionada': igreja_selecionada_para_dados,
            'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template,
            'caixa_id_filtro_selecionado': caixa_id_filtro,
            'fundo_id_filtro_selecionado': fundo_id_filtro,
            'departamento_filtro_selecionado': departamento_filtro,
            'departamento_contexto_label': departamento_contexto_label,
            'departamento_contexto_id': departamento_contexto_obj.id if departamento_contexto_obj else None,
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo_geral': saldo_geral,
            'saldo_mes': saldo_mes,
            'ultimas_receitas': ultimas_receitas,
            'ultimas_despesas': ultimas_despesas,
            'periodo_filtro_selecionado': periodo_filtro,
            'titulo_filtro_periodo': titulo_filtro_periodo,
            'titulo_dashboard': titulo_dashboard,
            'can_edit_finance': can_edit,
            # Tendência mês anterior
            'variacao_receitas_pct': variacao_receitas_pct,
            'variacao_despesas_pct': variacao_despesas_pct,
            'saldo_mes_anterior': saldo_mes_anterior,
            'variacao_saldo_pct': variacao_saldo_pct,
            'receitas_mes': receitas_mes,
            'despesas_mes': despesas_mes,
            'receitas_mes_anterior': receitas_mes_anterior,
            'despesas_mes_anterior': despesas_mes_anterior,
            'diferenca_receitas': diferenca_receitas,
            'diferenca_despesas': diferenca_despesas,
            'diferenca_saldo': diferenca_saldo,
            'periodo_tendencia_label': f"{primeiro_dia_mes_ant.strftime('%d/%m/%Y')} a {ultimo_dia_mes_ant.strftime('%d/%m/%Y')}",
            # Filtro de data livre
            'data_inicio_filtro': data_inicio_filtro_str,
            'data_fim_filtro': data_fim_filtro_str,
            'data_hoje': data_hoje,
            # Dados para os novos gráficos
            'grafico_mensal_labels_json': json.dumps(meses_labels_grafico),
            'grafico_receitas_data_json': json.dumps(receitas_mensais_grafico_data),
            'grafico_despesas_data_json': json.dumps(despesas_mensais_grafico_data),
            'grafico_saldos_data_json': json.dumps(saldos_mensais_grafico_data),
            # Gráfico de Dizimistas (mensal e por fechamento)
            'grafico_dizimistas_data_json': json.dumps(dizimistas_unicos_mensais_grafico_data),
            'grafico_dizimistas_fechamento_labels_json': json.dumps(dizimistas_por_fechamento_labels),
            'grafico_dizimistas_fechamento_valores_json': json.dumps(dizimistas_por_fechamento_valores),

             # Dados para o novo gráfico de categorias de despesa
            'grafico_cat_desp_labels_json': json.dumps(grafico_cat_desp_labels),
            'grafico_cat_desp_valores_json': json.dumps(grafico_cat_desp_valores),
            # Dados para o gráfico de movimentação por fechamentos
            'grafico_fech_labels_json': json.dumps(grafico_fech_labels),
            'grafico_fech_receitas_data_json': json.dumps(grafico_fech_receitas_data),
            'grafico_fech_despesas_data_json': json.dumps(grafico_fech_despesas_data),
            'grafico_fech_saldos_data_json': json.dumps(grafico_fech_saldos_data),
             # Indicadores de Contas a Pagar
            'total_contas_pendentes': total_contas_pendentes,
            'total_contas_vencidas': total_contas_vencidas,
            'qtd_contas_pendentes': qtd_contas_pendentes,
            'qtd_contas_vencidas': qtd_contas_vencidas,
            'total_contas_fixas_previstas': total_contas_fixas_previstas,
            'total_contas_fixas_pagas': total_contas_fixas_pagas,
            'total_contas_fixas_atrasadas': total_contas_fixas_atrasadas,
            'qtd_contas_fixas_previstas': qtd_contas_fixas_previstas,
            'qtd_contas_fixas_pagas': qtd_contas_fixas_pagas,
            'qtd_contas_fixas_atrasadas': qtd_contas_fixas_atrasadas,
             # Dados para o novo gráfico de categorias de receita
            'grafico_cat_rec_labels_json': json.dumps(grafico_cat_rec_labels),
            'grafico_cat_rec_valores_json': json.dumps(grafico_cat_rec_valores),
             # Contas bancárias para o painel
            'contas_bancarias_painel': contas_bancarias_painel,
             # Dados para o novo gráfico de Perfil dos Dizimistas
            'perfil_dizimistas_labels_json': json.dumps(perfil_dizimistas_labels),
            'perfil_dizimistas_qtd_valores_json': json.dumps(perfil_dizimistas_qtd_valores),
            'perfil_dizimistas_total_valores_json': json.dumps(perfil_dizimistas_total_valores),
            'perfil_dizimistas_qtd_percentuais_json': json.dumps(perfil_dizimistas_qtd_percentuais),
            'perfil_dizimistas_valor_percentuais_json': json.dumps(perfil_dizimistas_valor_percentuais),
            'query_receitas_despesas': query_receitas_despesas,
            'query_contas_pagar_suffix': query_contas_pagar_suffix,
            'query_contas_pagar_extra': query_contas_pagar_extra,
            'escopo_igreja_label': escopo_igreja_label,
            'escopo_caixa_label': escopo_caixa_label,
            'escopo_fundo_label': escopo_fundo_label,
            'escopo_periodo_label': titulo_filtro_periodo,
            'url_limpar_filtros': url_limpar_filtros,
            'url_voltar_geral': url_voltar_geral,
            'dashboard_tem_dados': dashboard_tem_dados,
            'receitas_local': receitas_local,
            'receitas_eventos': receitas_eventos,
            'receitas_missoes': receitas_missoes,
            'receitas_assistencia': receitas_assistencia,
            'despesas_local': despesas_local,
            'despesas_eventos': despesas_eventos,
            'despesas_missoes': despesas_missoes,
            'despesas_assistencia': despesas_assistencia,

            # 'allowed_churches_count' não é usado diretamente neste painel da mesma forma que no de liderança
            # 'igrejas_permitidas_filtro' e 'igreja_id_filtro_selecionado' já são tratados por 'igrejas_org' e 'igreja_id_filtro'
        
        }
        
        # Adiciona resumo do último fechamento de caixa
        last_fechamento_qs = FechamentoCaixa.objects.filter(
            igreja__in=(allowed_churches if not igreja_selecionada_para_dados else [igreja_selecionada_para_dados])
        ).order_by('-data_fim')
        last_fechamento = last_fechamento_qs.first()
        if last_fechamento:
            context['last_fechamento_caixa_info'] = {
                'data_fim': last_fechamento.data_fim,
                'saldo_final': last_fechamento.saldo_final,
                'status': last_fechamento.get_status_display(),
            }
        else:
            context['last_fechamento_caixa_info'] = None
        return render(request, 'financeiro/painel_financeiro.html', context)
    except Exception as e:
        # Logar erro com mais detalhes se possível
        min_id = ministerio.id if 'ministerio' in locals() else 'N/A'
        logger.exception(f"Erro no painel financeiro para ministério {min_id}") # Corrigido o nome da função no log
        messages.error(request, f"Ocorreu um erro ao carregar o painel financeiro: {e}")
        return redirect('secretaria:dashboard') # Redireciona para o dashboard da secretaria ou outra página de fallback

# ... (restante das views) ...

# --- Receitas ---
@page_access_required('financeiro')
def lista_receitas(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    try:
        allowed_churches = get_finance_read_scope(request.user, ministerio)
        igrejas_base = allowed_churches
        # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
        if request.igreja_ativa:
            # Se uma igreja ativa está selecionada, filtra por ela (garantindo que ela está entre as permitidas)
            if request.igreja_ativa in igrejas_base:
                receitas_qs = Receitas.objects.filter(igreja=request.igreja_ativa).select_related('igreja', 'membro', 'evento').order_by('-data')
            else:
                receitas_qs = Receitas.objects.none()
        else:
            # Se nenhuma igreja ativa, mostra de todas as igrejas permitidas
            receitas_qs = Receitas.objects.filter(igreja__in=igrejas_base).select_related('igreja', 'membro', 'evento').order_by('-data')
        # --- Fim Lógica de Filtragem Inicial ---


        # Filtros adicionais do GET
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        categoria = request.GET.get('categoria')
        igreja_id_get = request.GET.get('igreja') # Renomeado
        caixa_id_filtro = request.GET.get('caixa_filtro')
        evento_id_filtro = request.GET.get('evento')
        fundo_id_filtro = request.GET.get('fundo_filtro')
        fundos_disponivel = _fundos_departamentais_disponivel()

        if fundos_disponivel:
            if request.igreja_ativa and igrejas_base.filter(pk=request.igreja_ativa.pk).exists():
                fundos_dropdown = DepartamentoFinanceiroService.fundos_visiveis_para_igrejas([request.igreja_ativa])
            elif request.igreja_ativa:
                fundos_dropdown = FundoDepartamental.objects.none()
            else:
                fundos_dropdown = DepartamentoFinanceiroService.fundos_visiveis_para_igrejas(igrejas_base)

            if fundo_id_filtro and not fundos_dropdown.filter(pk=fundo_id_filtro).exists():
                messages.warning(request, 'Fundo selecionado inválido para o seu escopo. Exibindo dados sem filtro de fundo.')
                fundo_id_filtro = ''
        else:
            fundos_dropdown = FundoDepartamental.objects.none()
            fundo_id_filtro = ''
        # --- LÓGICA DO FILTRO 'fechado' ---
        # Pega o valor do parâmetro, default para 'false' (aberto) se não vier na URL
        fechado_filter = request.GET.get('fechado', 'false')

        if data_inicio: receitas_qs = receitas_qs.filter(data__gte=data_inicio)
        if data_fim: receitas_qs = receitas_qs.filter(data__lte=data_fim)
        if categoria: receitas_qs = receitas_qs.filter(categoria=categoria)
        if caixa_id_filtro:
            receitas_qs = receitas_qs.filter(conta_bancaria_id=caixa_id_filtro)
        if evento_id_filtro:
            receitas_qs = receitas_qs.filter(evento_id=evento_id_filtro)
        if fundos_disponivel and fundo_id_filtro:
            receitas_qs = receitas_qs.filter(fundo_departamental_id=fundo_id_filtro)
        # --- Lógica para o filtro de igreja na página (se request.igreja_ativa NÃO estiver definida) ---

        if igreja_id_get:
            # Este filtro só deve ser aplicado se request.igreja_ativa NÃO estiver definida
            if not request.igreja_ativa:
                if allowed_churches.filter(pk=igreja_id_get).exists():
                    receitas_qs = receitas_qs.filter(igreja_id=igreja_id_get)


        # Base para indicadores antes do filtro final de status (aberto/fechado/todos)
        receitas_base_periodo = receitas_qs

        # --- LÓGICA DO FILTRO 'fechado' ---
        fechado_filter = request.GET.get('fechado', 'false')

        # Aplica o filtro 'fechado' baseado no valor (seja o da URL ou o default 'false')
        if fechado_filter == 'true':
            receitas_qs = receitas_qs.filter(fechado=True)
        elif fechado_filter == 'false': # Inclui o default
            receitas_qs = receitas_qs.filter(fechado=False)

        # Cards de dizimos/ofertas fazem sentido apenas no contexto Tesouraria Local.
        exibir_cards_dizimos_ofertas = False
        if fundos_disponivel and fundo_id_filtro:
            fundo_contexto = fundos_dropdown.filter(pk=fundo_id_filtro).only('codigo').first()
            exibir_cards_dizimos_ofertas = bool(
                fundo_contexto and fundo_contexto.codigo == FundoDepartamental.CODIGO_LOCAL
            )
        elif caixa_id_filtro:
            exibir_cards_dizimos_ofertas = DepartamentoCaixa.objects.filter(
                conta_bancaria_id=caixa_id_filtro,
                ativo=True,
                departamento__ativo=True,
                departamento__codigo_interno=DepartamentoFinanceiro.CODIGO_LOCAL,
                departamento__igreja__in=igrejas_base,
            ).exists()

        # --- RESUMOS DE DÍZIMOS E OFERTAS (DINHEIRO, PIX, TOTAL) ---
        from decimal import Decimal
        # Dízimos
        dizimos_dinheiro = receitas_qs.filter(categoria='dizimo', forma_pgto__in=['DIN', 'Dinheiro']).aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        dizimos_pix = receitas_qs.filter(categoria='dizimo', forma_pgto__in=['PIX', 'Pix', 'pix']).aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        dizimos_total = receitas_qs.filter(categoria='dizimo').aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        # Ofertas
        ofertas_dinheiro = receitas_qs.filter(categoria='oferta', forma_pgto__in=['DIN', 'Dinheiro']).aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        ofertas_pix = receitas_qs.filter(categoria='oferta', forma_pgto__in=['PIX', 'Pix', 'pix']).aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        ofertas_total = receitas_qs.filter(categoria='oferta').aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        # Se você adicionar uma opção 'todos' com value='', pode adicionar um 'elif fechado_filter == "":' aqui
        # --- FIM DA LÓGICA DO FILTRO 'fechado' ---

        resumo_total_periodo = receitas_base_periodo.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        resumo_total_aberto = receitas_base_periodo.filter(fechado=False).aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        resumo_quantidade_periodo = receitas_base_periodo.count()
        resumo_ticket_medio = (resumo_total_periodo / resumo_quantidade_periodo) if resumo_quantidade_periodo else Decimal('0.00')

        sort_map = {
            'data': 'data',
            '-data': '-data',
            'igreja': 'igreja__nome_igreja',
            '-igreja': '-igreja__nome_igreja',
            'membro': 'membro__nome',
            '-membro': '-membro__nome',
            'categoria': 'categoria',
            '-categoria': '-categoria',
            'evento': 'evento__titulo',
            '-evento': '-evento__titulo',
            'valor': 'valor',
            '-valor': '-valor',
        }
        sort = request.GET.get('sort', '-data')
        order_by = sort_map.get(sort, '-data')
        receitas_qs = receitas_qs.order_by(order_by, '-id')

        categorias_choices = Receitas.CATEGORIA_CHOICES
        # --- Lógica para o dropdown de filtro de igreja no template ---
        igrejas_para_filtro_template = igrejas_base
        igreja_id_selecionada_template = igreja_id_get # Para o select do filtro da página

        if request.igreja_ativa:
            igrejas_para_filtro_template = Igreja.objects.filter(pk=request.igreja_ativa.pk) # Ou desabilitar o filtro
            igreja_id_selecionada_template = str(request.igreja_ativa.pk) # Para o select do filtro da página

        # Permissão de edição para o template
        can_edit = has_finance_edit_permission(request.user)
        query_params = request.GET.copy()
        query_params.pop('sort', None)

        # --- FILTRO DE CONTAS BANCÁRIAS (respeitando a igreja ativa) ---
        if request.igreja_ativa and request.igreja_ativa in igrejas_base:
            contas_bancarias_dropdown = ContaBancaria.objects.filter(igreja=request.igreja_ativa).order_by('nome_identificacao')
            eventos_dropdown = Evento.objects.filter(igreja=request.igreja_ativa).order_by('-data_inicio', 'titulo')
        else:
            contas_bancarias_dropdown = ContaBancaria.objects.filter(igreja__in=igrejas_base).order_by('igreja__nome_igreja', 'nome_identificacao')
            eventos_dropdown = Evento.objects.filter(igreja__in=igrejas_base).order_by('-data_inicio', 'titulo')

        context = {
            'receitas': receitas_qs,
            'ministerio': ministerio,
            'categorias_choices': categorias_choices,
            'igrejas_org': igrejas_para_filtro_template, # Usar a lista ajustada
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'categoria_selecionada': categoria,
            'igreja_selecionada': igreja_id_selecionada_template, # ID para o select do filtro da página
            'evento_selecionado': evento_id_filtro,
            # Passa o valor que FOI USADO no filtro para o template selecionar a opção correta no filtro da página
            'fechado_selecionado': fechado_filter,
            'can_edit_finance': can_edit, # Flag para o template
            'contas_bancarias_painel': contas_bancarias_dropdown,
            'fundos_departamentais_dropdown': fundos_dropdown,
            'fundos_departamentais_disponivel': fundos_disponivel,
            'eventos_filtro': eventos_dropdown,
            'fundo_id_filtro_selecionado': fundo_id_filtro,
            'sort_atual': sort if sort in sort_map else '-data',
            'querystring_without_sort': query_params.urlencode(),
            'resumo_total_periodo': resumo_total_periodo,
            'resumo_total_aberto': resumo_total_aberto,
            'resumo_ticket_medio': resumo_ticket_medio,
            'resumo_quantidade_periodo': resumo_quantidade_periodo,
            # Novos cards de resumo
            'dizimos_dinheiro': dizimos_dinheiro,
            'dizimos_pix': dizimos_pix,
            'dizimos_total': dizimos_total,
            'ofertas_dinheiro': ofertas_dinheiro,
            'ofertas_pix': ofertas_pix,
            'ofertas_total': ofertas_total,
            'exibir_cards_dizimos_ofertas': exibir_cards_dizimos_ofertas,
        }
        return render(request, 'financeiro/receitas/lista_receitas.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar receitas para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao listar as receitas: {e}")
        return redirect('financeiro:painel_financeiro')


@page_access_required('financeiro')
def conciliacao_ofx(request):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    score_minimo_atual = 90

    importacoes = ImportacaoExtratoOFX.objects.select_related('igreja', 'conta_bancaria', 'usuario')
    if allowed_churches.exists():
        importacoes = importacoes.filter(igreja__in=allowed_churches)
    else:
        importacoes = importacoes.filter(igreja__ministerio=ministerio)
    importacoes = importacoes.order_by('-importado_em')

    importacao_id = request.GET.get('importacao')
    importacao = None
    sugestoes = []
    conciliados = []
    receitas_manuais = []
    despesas_manuais = []
    previsao_lote = None
    can_edit = has_finance_edit_permission(request.user)

    if request.method == 'POST':
        if not can_edit:
            messages.error(request, 'Você não tem permissão para confirmar conciliações.')
            return redirect('financeiro:conciliacao_ofx')

        lancamento_id = request.POST.get('lancamento_id')
        acao = request.POST.get('acao', 'confirmar')
        tipo = request.POST.get('tipo')
        referencia_id = request.POST.get('referencia_id')
        importacao_id_post = request.POST.get('importacao_id')
        score_minimo_post = request.POST.get('score_minimo', '90')
        try:
            score_minimo_atual = int(score_minimo_post)
        except (TypeError, ValueError):
            score_minimo_atual = 90
        score_minimo_atual = max(0, min(score_minimo_atual, 200))
        redirect_url = reverse('financeiro:conciliacao_ofx')
        if importacao_id_post:
            redirect_url = f"{redirect_url}?importacao={importacao_id_post}"

        try:
            service = OFXImportService()
            importacao_alvo = None
            if acao in {'conciliar_melhores', 'previsualizar_melhores', 'exportar_previsao_csv', 'exportar_previsao_xlsx'}:
                importacoes_para_lote = ImportacaoExtratoOFX.objects.filter(pk=importacao_id_post)
                if allowed_churches.exists():
                    importacoes_para_lote = importacoes_para_lote.filter(igreja__in=allowed_churches)
                else:
                    importacoes_para_lote = importacoes_para_lote.filter(igreja__ministerio=ministerio)
                importacao_alvo = get_object_or_404(importacoes_para_lote)

            if acao == 'desfazer':
                service.desfazer_conciliacao(lancamento_id=lancamento_id)
                messages.success(request, 'Conciliação desfeita com sucesso.')
                return redirect(redirect_url)
            elif acao == 'conciliar_melhores':
                resumo = service.conciliar_melhores_sugestoes(
                    importacao=importacao_alvo,
                    usuario=request.user,
                    score_minimo=score_minimo_atual,
                )
                messages.success(
                    request,
                    (
                        f"Conciliação em lote (score >= {score_minimo_atual}) concluída: {resumo['total_conciliados']} conciliado(s), "
                        f"{resumo['total_ignorados_score']} ignorado(s) por score e "
                        f"{resumo['total_erros']} com erro."
                    )
                )
                return redirect(redirect_url)
            elif acao == 'previsualizar_melhores':
                previsao_lote = service.conciliar_melhores_sugestoes(
                    importacao=importacao_alvo,
                    usuario=request.user,
                    score_minimo=score_minimo_atual,
                    dry_run=True,
                )
                importacao_id = str(importacao_alvo.id)
                messages.info(
                    request,
                    (
                        f"Pré-visualização pronta: {previsao_lote['total_conciliados']} item(ns) elegível(is) para lote "
                        f"com score >= {score_minimo_atual}."
                    )
                )
            elif acao == 'exportar_previsao_csv':
                previsao_csv = service.conciliar_melhores_sugestoes(
                    importacao=importacao_alvo,
                    usuario=request.user,
                    score_minimo=score_minimo_atual,
                    dry_run=True,
                )

                response = HttpResponse(content_type='text/csv; charset=utf-8')
                nome_arquivo = f"previsao_conciliacao_ofx_{importacao_alvo.id}_score_{score_minimo_atual}.csv"
                response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'

                writer = csv.writer(response)
                writer.writerow([
                    'lancamento_id_ofx',
                    'fit_id',
                    'tipo_ofx',
                    'data_ofx',
                    'valor_ofx',
                    'memo',
                    'tipo_referencia',
                    'referencia_id',
                    'data_referencia',
                    'valor_referencia',
                    'score',
                ])

                for item_csv in previsao_csv.get('itens_selecionados', []):
                    data_ofx = item_csv.get('data_ofx')
                    data_ref = item_csv.get('data_referencia')
                    writer.writerow([
                        item_csv.get('lancamento_id'),
                        item_csv.get('fit_id') or '',
                        item_csv.get('tipo_ofx') or '',
                        data_ofx.strftime('%d/%m/%Y %H:%M') if data_ofx else '',
                        f"{abs(Decimal(item_csv.get('valor_ofx') or 0)):.2f}",
                        item_csv.get('memo') or '',
                        item_csv.get('tipo_referencia') or '',
                        item_csv.get('referencia_id') or '',
                        data_ref.strftime('%d/%m/%Y') if data_ref else '',
                        f"{abs(Decimal(item_csv.get('valor_referencia') or 0)):.2f}",
                        item_csv.get('score') or 0,
                    ])

                resumo = previsao_csv.get('resumo_impacto', {})
                writer.writerow([])
                writer.writerow(['resumo'])
                writer.writerow(['score_minimo', score_minimo_atual])
                writer.writerow(['elegiveis', previsao_csv.get('total_conciliados', 0)])
                writer.writerow(['ignorados_score', previsao_csv.get('total_ignorados_score', 0)])
                writer.writerow(['erros_estimados', previsao_csv.get('total_erros', 0)])
                writer.writerow(['quantidade_entradas', resumo.get('quantidade_entradas', 0)])
                writer.writerow(['quantidade_saidas', resumo.get('quantidade_saidas', 0)])
                writer.writerow(['total_entradas', f"{Decimal(resumo.get('total_entradas', 0)):.2f}"])
                writer.writerow(['total_saidas', f"{Decimal(resumo.get('total_saidas', 0)):.2f}"])
                writer.writerow(['total_movimentado', f"{Decimal(resumo.get('total_movimentado', 0)):.2f}"])
                writer.writerow(['saldo_previsto', f"{Decimal(resumo.get('saldo_previsto', 0)):.2f}"])

                return response
            elif acao == 'exportar_previsao_xlsx':
                previsao_xlsx = service.conciliar_melhores_sugestoes(
                    importacao=importacao_alvo,
                    usuario=request.user,
                    score_minimo=score_minimo_atual,
                    dry_run=True,
                )

                wb = Workbook()
                ws = wb.active
                ws.title = 'Previsao OFX'

                headers = [
                    'lancamento_id_ofx',
                    'fit_id',
                    'tipo_ofx',
                    'data_ofx',
                    'valor_ofx',
                    'memo',
                    'tipo_referencia',
                    'referencia_id',
                    'data_referencia',
                    'valor_referencia',
                    'score',
                ]
                ws.append(headers)

                for item_xlsx in previsao_xlsx.get('itens_selecionados', []):
                    data_ofx = item_xlsx.get('data_ofx')
                    data_ref = item_xlsx.get('data_referencia')
                    ws.append([
                        item_xlsx.get('lancamento_id'),
                        item_xlsx.get('fit_id') or '',
                        item_xlsx.get('tipo_ofx') or '',
                        data_ofx.strftime('%d/%m/%Y %H:%M') if data_ofx else '',
                        float(abs(Decimal(item_xlsx.get('valor_ofx') or 0))),
                        item_xlsx.get('memo') or '',
                        item_xlsx.get('tipo_referencia') or '',
                        item_xlsx.get('referencia_id') or '',
                        data_ref.strftime('%d/%m/%Y') if data_ref else '',
                        float(abs(Decimal(item_xlsx.get('valor_referencia') or 0))),
                        item_xlsx.get('score') or 0,
                    ])

                ws.append([])
                ws.append(['resumo'])
                resumo = previsao_xlsx.get('resumo_impacto', {})
                ws.append(['score_minimo', score_minimo_atual])
                ws.append(['elegiveis', previsao_xlsx.get('total_conciliados', 0)])
                ws.append(['ignorados_score', previsao_xlsx.get('total_ignorados_score', 0)])
                ws.append(['erros_estimados', previsao_xlsx.get('total_erros', 0)])
                ws.append(['quantidade_entradas', resumo.get('quantidade_entradas', 0)])
                ws.append(['quantidade_saidas', resumo.get('quantidade_saidas', 0)])
                ws.append(['total_entradas', float(Decimal(resumo.get('total_entradas', 0)))])
                ws.append(['total_saidas', float(Decimal(resumo.get('total_saidas', 0)))])
                ws.append(['total_movimentado', float(Decimal(resumo.get('total_movimentado', 0)))])
                ws.append(['saldo_previsto', float(Decimal(resumo.get('saldo_previsto', 0)))])

                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                nome_arquivo = f"previsao_conciliacao_ofx_{importacao_alvo.id}_score_{score_minimo_atual}.xlsx"
                response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
                wb.save(response)
                return response
            else:
                service.confirmar_conciliacao(
                    lancamento_id=lancamento_id,
                    tipo=tipo,
                    referencia_id=referencia_id,
                    usuario=request.user,
                )
                messages.success(request, 'Conciliação confirmada com sucesso.')
                return redirect(redirect_url)
        except Exception as exc:
            messages.error(request, f'Não foi possível processar a conciliação: {exc}')
            if acao != 'previsualizar_melhores':
                return redirect(redirect_url)

    if importacao_id:
        importacao = get_object_or_404(importacoes, pk=importacao_id)
        sugestoes = OFXImportService().gerar_sugestoes_conciliacao(importacao)
        conciliados = (
            importacao.lancamentos
            .filter(conciliado=True)
            .order_by('-conciliado_em', '-id')
        )
        receitas_manuais = (
            Receitas.objects
            .filter(igreja=importacao.igreja)
            .order_by('-data', '-id')[:200]
        )
        despesas_manuais = (
            Despesas.objects
            .filter(igreja=importacao.igreja)
            .order_by('-data', '-id')[:200]
        )

    context = {
        'ministerio': ministerio,
        'importacoes': importacoes,
        'importacao': importacao,
        'sugestoes': sugestoes,
        'conciliados': conciliados,
        'receitas_manuais': receitas_manuais,
        'despesas_manuais': despesas_manuais,
        'previsao_lote': previsao_lote,
        'score_minimo_atual': score_minimo_atual,
        'can_edit_finance': can_edit,
    }
    return render(request, 'financeiro/ofx/conciliacao_ofx.html', context)



@page_access_required('financeiro')
def cadastrar_receita(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    igreja_padrao_para_form = None # Inicializa
    next_url = _get_safe_next_url(request, 'financeiro:lista_receitas')

    if request.method == 'GET' and next_url == reverse('eventos:lista_eventos'):
        return redirect('financeiro:cadastrar_receita_caixa_eventos')

    if not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar receitas ou não está associado a nenhuma igreja específica.")
        return redirect(next_url)

    # A igreja do lançamento deve vir do seletor global (igreja ativa).
    if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
        igreja_padrao_para_form = request.igreja_ativa
    elif allowed_churches.count() == 1:
        igreja_padrao_para_form = allowed_churches.first()

    if igreja_padrao_para_form is None:
        messages.error(request, "Selecione uma igreja no seletor global antes de cadastrar a receita.")
        return redirect(next_url)

    batch_itens = _batch_get(request, 'receitas', igreja_padrao_para_form.pk)
    batch_defaults = _batch_defaults_get(request, 'receitas', igreja_padrao_para_form.pk)

    if request.method == 'POST':
        action = (request.POST.get('action') or 'save_single').strip()

        if action == 'batch_remove':
            item_id = (request.POST.get('batch_item_id') or '').strip()
            batch_itens = [item for item in batch_itens if item.get('id') != item_id]
            _batch_set(request, 'receitas', igreja_padrao_para_form.pk, batch_itens)
            messages.success(request, 'Item removido da lista temporária.')
            return redirect(request.path)

        if action == 'batch_edit':
            item_id = (request.POST.get('batch_item_id') or '').strip()
            item = next((it for it in batch_itens if it.get('id') == item_id), None)
            if item:
                initial_edicao = {
                    'igreja': igreja_padrao_para_form,
                    'data': item.get('data') or '',
                    'categoria': item.get('categoria') or '',
                    'valor': item.get('valor') or '',
                    'forma_pgto': item.get('forma_pgto') or '',
                    'membro': item.get('membro') or '',
                    'evento': item.get('evento') or '',
                    'conta_bancaria': item.get('conta_bancaria') or '',
                    'observacao': item.get('observacao') or '',
                }
                form = ReceitaForm(
                    initial=initial_edicao,
                    ministerio=ministerio,
                    user=request.user, allowed_churches=allowed_churches,
                    igreja_selecionada_inicial=igreja_padrao_para_form,
                )
                context = {
                    'form': form,
                    'ministerio': ministerio,
                    'titulo_pagina': 'Cadastrar Receita',
                    'ocultar_campo_igreja': True,
                    'url_cancelar': next_url,
                    'next_url': next_url,
                    'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(igreja_padrao_para_form),
                    'mostrar_evento_por_conta': True,
                    'batch_itens': batch_itens,
                    'batch_tipo': 'receitas',
                    'batch_edit_item_id': item_id,
                }
                return render(request, 'financeiro/receitas/form_receita.html', context)
            messages.warning(request, 'Item não encontrado para edição.')
            return redirect(request.path)

        if action == 'batch_duplicate':
            item_id = (request.POST.get('batch_item_id') or '').strip()
            item = next((it for it in batch_itens if it.get('id') == item_id), None)
            if item:
                novo_item = item.copy()
                novo_item['id'] = str(uuid4())
                batch_itens.append(novo_item)
                _batch_set(request, 'receitas', igreja_padrao_para_form.pk, batch_itens)
                messages.success(request, 'Item duplicado na lista temporária.')
            else:
                messages.warning(request, 'Item não encontrado para duplicar.')
            return redirect(request.path)

        if action == 'batch_clear':
            _batch_clear(request, 'receitas', igreja_padrao_para_form.pk)
            messages.success(request, 'Lista temporária de receitas limpa.')
            return redirect(request.path)

        if action == 'batch_save':
            if not batch_itens:
                messages.warning(request, 'Não há itens na lista temporária para salvar.')
                return redirect(request.path)

            salvos = 0
            with transaction.atomic():
                for item in batch_itens:
                    payload = {
                        'igreja': str(igreja_padrao_para_form.pk),
                        'evento': item.get('evento') or '',
                        'membro': item.get('membro') or '',
                        'data': item.get('data') or '',
                        'categoria': item.get('categoria') or '',
                        'valor': item.get('valor') or '',
                        'forma_pgto': item.get('forma_pgto') or '',
                        'conta_bancaria': item.get('conta_bancaria') or '',
                        'observacao': item.get('observacao') or '',
                    }
                    item_form = ReceitaForm(
                        payload,
                        ministerio=ministerio,
                        user=request.user, allowed_churches=allowed_churches,
                        igreja_selecionada_inicial=igreja_padrao_para_form,
                    )
                    if not item_form.is_valid():
                        raise ValidationError(f"Item inválido no lote de receitas: {item_form.errors.as_text()}")

                    nova_receita = item_form.save(commit=False)
                    nova_receita.igreja = igreja_padrao_para_form
                    nova_receita.save()
                    salvos += 1

            _batch_clear(request, 'receitas', igreja_padrao_para_form.pk)
            messages.success(request, f'{salvos} receita(s) salvas com sucesso em lote!')
            return redirect(next_url)

        post_data = request.POST.copy()
        post_data['igreja'] = str(igreja_padrao_para_form.pk)
        # Passa ministério para o form filtrar igrejas e membros (se necessário)
        # Passa allowed_churches para o form filtrar o campo igreja
        form = ReceitaForm(post_data, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_selecionada_inicial=igreja_padrao_para_form)
        if form.is_valid():
            try:
                nova_receita = form.save(commit=False)
                nova_receita.igreja = igreja_padrao_para_form
                # Validação extra (form já deve ter validado, mas é bom garantir)
                if not allowed_churches.filter(pk=nova_receita.igreja_id).exists():
                    messages.error(request, "Erro: Igreja selecionada inválida.")
                # Validar membro (se selecionado) - form já deve filtrar
                elif nova_receita.membro and nova_receita.membro.igreja.ministerio != ministerio:
                    messages.error(request, "Erro: Membro selecionado não pertence à seu ministério.")
                else:
                    if action == 'batch_add':
                        novo_item = {
                            'id': str(uuid4()),
                            'data': str(form.cleaned_data['data']),
                            'categoria': form.cleaned_data['categoria'],
                            'categoria_label': form.fields['categoria'].choices and dict(form.fields['categoria'].choices).get(form.cleaned_data['categoria'], form.cleaned_data['categoria']),
                            'valor': str(form.cleaned_data['valor']),
                            'forma_pgto': form.cleaned_data.get('forma_pgto') or '',
                            'forma_pgto_label': dict(form.fields['forma_pgto'].choices).get(form.cleaned_data.get('forma_pgto'), form.cleaned_data.get('forma_pgto') or '-'),
                            'membro': str(form.cleaned_data['membro'].pk) if form.cleaned_data.get('membro') else '',
                            'membro_label': form.cleaned_data['membro'].nome if form.cleaned_data.get('membro') else '-',
                            'evento': str(form.cleaned_data['evento'].pk) if form.cleaned_data.get('evento') else '',
                            'evento_label': form.cleaned_data['evento'].titulo if form.cleaned_data.get('evento') else '-',
                            'conta_bancaria': str(form.cleaned_data['conta_bancaria'].pk) if form.cleaned_data.get('conta_bancaria') else '',
                            'conta_bancaria_label': form.cleaned_data['conta_bancaria'].nome_identificacao if form.cleaned_data.get('conta_bancaria') else '-',
                            'observacao': form.cleaned_data.get('observacao') or '',
                        }
                        edit_item_id = (request.POST.get('batch_edit_item_id') or '').strip()
                        if edit_item_id:
                            atualizado = False
                            for idx, item_existente in enumerate(batch_itens):
                                if item_existente.get('id') == edit_item_id:
                                    novo_item['id'] = edit_item_id
                                    batch_itens[idx] = novo_item
                                    atualizado = True
                                    break
                            if not atualizado:
                                batch_itens.append(novo_item)
                        else:
                            batch_itens.append(novo_item)

                        _batch_set(request, 'receitas', igreja_padrao_para_form.pk, batch_itens)
                        _batch_defaults_set(
                            request,
                            'receitas',
                            igreja_padrao_para_form.pk,
                            {
                                'categoria': novo_item.get('categoria') or '',
                                'forma_pgto': novo_item.get('forma_pgto') or '',
                                'conta_bancaria': novo_item.get('conta_bancaria') or '',
                                'membro': novo_item.get('membro') or '',
                                'evento': novo_item.get('evento') or '',
                            }
                        )
                        messages.success(request, 'Receita adicionada à lista temporária.')
                        return redirect(request.path)

                    # O método save da Receita agora atualiza o saldo
                    nova_receita.save()
                    messages.success(request, 'Receita cadastrada com sucesso!')
                    return redirect(next_url)
            except Exception as e:
                logger.exception(f"Erro ao salvar receita para ministério {ministerio.id}")
                messages.error(request, f'Erro ao salvar receita: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
        context = {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': 'Cadastrar Receita',
            'ocultar_campo_igreja': True,
            'url_cancelar': next_url,
            'next_url': next_url,
            'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(igreja_padrao_para_form),
            'mostrar_evento_por_conta': True,
            'batch_itens': batch_itens,
            'batch_tipo': 'receitas',
        }
        return render(request, 'financeiro/receitas/form_receita.html', context)
    else:
        initial_form_data = {'igreja': igreja_padrao_para_form}
        initial_form_data.update({
            'categoria': batch_defaults.get('categoria') or '',
            'forma_pgto': batch_defaults.get('forma_pgto') or '',
            'conta_bancaria': batch_defaults.get('conta_bancaria') or '',
            'membro': batch_defaults.get('membro') or '',
            'evento': batch_defaults.get('evento') or '',
        })
        form = ReceitaForm(initial=initial_form_data, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_selecionada_inicial=igreja_padrao_para_form)
        context = {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': 'Cadastrar Receita',
            'ocultar_campo_igreja': True,
            'url_cancelar': next_url,
            'next_url': next_url,
            'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(igreja_padrao_para_form),
            'mostrar_evento_por_conta': True,
            'batch_itens': batch_itens,
            'batch_tipo': 'receitas',
        }
        # Usar um template genérico ou específico
        return render(request, 'financeiro/receitas/form_receita.html', context)


@page_access_required('financeiro')
def cadastrar_receita_evento(request, evento_id):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    evento = get_object_or_404(Evento, pk=evento_id, igreja__in=allowed_churches)
    _, conta_evento_efetiva_id = ReceitaFluxoService.construir_initial_receita_evento(evento)

    if request.method == 'POST':
        post_data, conta_evento_efetiva_id = ReceitaFluxoService.construir_post_data_receita_evento(request.POST, evento)

        form = ReceitaForm(
            post_data,
            ministerio=ministerio,
            user=request.user, allowed_churches=allowed_churches,
            igreja_selecionada_inicial=evento.igreja,
            evento_contexto=evento,
            travar_evento=True,
            travar_conta_evento=bool(conta_evento_efetiva_id),
        )
        if form.is_valid():
            try:
                receita = form.save(commit=False)
                receita.igreja = evento.igreja
                receita.evento = evento
                ReceitaFluxoService.aplicar_defaults_receita_fluxo_evento(receita)
                receita.save()
                messages.success(request, 'Entrada do evento cadastrada com sucesso!')
                return redirect('eventos:detalhe_evento', pk=evento.pk)
            except Exception as e:
                logger.exception(f"Erro ao salvar receita do evento {evento.pk} para ministério {ministerio.id}")
                messages.error(request, f'Erro ao salvar entrada do evento: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        initial, conta_evento_efetiva_id = ReceitaFluxoService.construir_initial_receita_evento(evento)

        form = ReceitaForm(
            initial=initial,
            ministerio=ministerio,
            user=request.user, allowed_churches=allowed_churches,
            igreja_selecionada_inicial=evento.igreja,
            evento_contexto=evento,
            travar_evento=True,
            travar_conta_evento=bool(conta_evento_efetiva_id),
        )

    context = ReceitaFluxoService.construir_contexto_receita_evento(
        form=form,
        ministerio=ministerio,
        evento=evento,
        conta_evento_efetiva_id=conta_evento_efetiva_id,
    )
    context['contas_eventos_ids'] = _obter_ids_contas_eventos_para_igreja(evento.igreja)
    context['mostrar_evento_por_conta'] = False
    return render(request, 'financeiro/receitas/form_receita.html', context)


@page_access_required('financeiro')
def cadastrar_receita_caixa_eventos(request):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    igreja_padrao_para_form = ReceitaFluxoService.resolver_igreja_padrao_receita_caixa_eventos(
        request=request,
        allowed_churches=allowed_churches,
        is_admin=False,
    )

    if not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar entradas de eventos.")
        return redirect('eventos:lista_eventos')

    if igreja_padrao_para_form is None:
        messages.error(request, "Selecione uma igreja no seletor global antes de lançar entrada de eventos.")
        return redirect('eventos:lista_eventos')

    if request.method == 'POST':
        post_data, _evento, _conta_evento_efetiva_id = ReceitaFluxoService.construir_post_data_receita_caixa_eventos(
            raw_post_data=request.POST,
            igreja_padrao_para_form=igreja_padrao_para_form,
            allowed_churches=allowed_churches,
        )

        form = ReceitaForm(
            post_data,
            ministerio=ministerio,
            user=request.user, allowed_churches=allowed_churches,
            igreja_selecionada_inicial=igreja_padrao_para_form,
            codigo_fundo_contexto=FundoDepartamental.CODIGO_EVENTOS,
        )
        if form.is_valid():
            try:
                receita = form.save(commit=False)
                receita.igreja = igreja_padrao_para_form
                ReceitaFluxoService.aplicar_defaults_receita_caixa_eventos(receita)
                receita.full_clean()
                receita.save()
                messages.success(request, 'Entrada do caixa de eventos cadastrada com sucesso!')
                return redirect('eventos:lista_eventos')
            except Exception as e:
                logger.exception(f"Erro ao salvar entrada do caixa de eventos para ministério {ministerio.id}")
                messages.error(request, f'Erro ao salvar entrada do caixa de eventos: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        initial = ReceitaFluxoService.construir_initial_receita_caixa_eventos(igreja_padrao_para_form)
        form = ReceitaForm(
            initial=initial,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_selecionada_inicial=igreja_padrao_para_form,
            codigo_fundo_contexto=FundoDepartamental.CODIGO_EVENTOS,
        )

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Lançar Entrada - Caixa de Eventos',
        'ocultar_campo_igreja': True,
        'ocultar_campo_categoria': False,
        'ocultar_campo_conta_bancaria': bool(getattr(igreja_padrao_para_form, 'conta_padrao_eventos_id', None)),
        'url_cancelar': reverse('eventos:lista_eventos'),
        'form_action_url': reverse('financeiro:cadastrar_receita_caixa_eventos'),
        'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(igreja_padrao_para_form),
        'mostrar_evento_por_conta': False,
    }
    return render(request, 'financeiro/receitas/form_receita.html', context)


@page_access_required('financeiro')
def editar_receita(request, pk): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    # Garante que a receita pertence às igrejas permitidas
    receita = get_object_or_404(Receitas, pk=pk, igreja__in=allowed_churches)

    if receita.fechado:
        messages.error(request, "Não é possível editar uma receita fechada.")
        return redirect('financeiro:lista_receitas')

    if request.method == 'POST':
        form = ReceitaForm(request.POST, instance=receita, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)
        if form.is_valid():
            try:
                receita_editada = form.save(commit=False)
                # Validações extras
                if receita_editada.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida.")
                elif receita_editada.membro and receita_editada.membro.igreja.ministerio != ministerio:
                    messages.error(request, "Erro: Membro selecionado não pertence à seu ministério.")
                else:
                    receita_editada.save()
                    messages.success(request, 'Receita atualizada com sucesso!')
                    return redirect('financeiro:lista_receitas')
            except Exception as e:
                logger.exception(f"Erro ao salvar edição da receita {pk} para ministério {ministerio.id}")
                messages.error(request, f'Erro ao salvar receita: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = ReceitaForm(instance=receita, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Editar Receita',
        'receita': receita,
        'url_cancelar': reverse('financeiro:lista_receitas'),
        'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(receita.igreja),
        'mostrar_evento_por_conta': True,
    }
    return render(request, 'financeiro/receitas/form_receita.html', context)


@page_access_required('financeiro')
def excluir_receita(request, pk): # noqa: E302
    # Apenas quem pode editar pode excluir
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    receita = get_object_or_404(Receitas, pk=pk, igreja__in=allowed_churches)

    if receita.fechado:
        messages.error(request, "Não é possível excluir uma receita fechada.")
        return redirect('financeiro:lista_receitas')

    if request.method == 'POST': # Exclusão deve ser POST
        try:
             # Formata o nome da receita para a mensagem de sucesso
            if receita.membro:
                nome_receita_formatado = f"Receita de {receita.membro.nome} ({receita.get_categoria_display()})"
            elif receita.observacao:
                nome_receita_formatado = f"Receita ({receita.get_categoria_display()}): {receita.observacao[:30]}..."
            else:
                nome_receita_formatado = f"Receita ({receita.get_categoria_display()}) de R$ {receita.valor}"
            
            receita.delete() # O método delete da Receita agora reverte o saldo

            messages.success(request, f'Receita "{nome_receita_formatado}" excluída com sucesso!')
        except Exception as e:

            logger.exception(f"Erro ao excluir receita {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao excluir receita: {e}')
        return redirect('financeiro:lista_receitas')
    else:
        # GET não deve excluir, mostrar confirmação ou erro
        # context = {'receita': receita, 'ministerio': ministerio}
        # return render(request, 'financeiro/receitas/confirmar_excluir_receita.html', context)
        messages.error(request, 'Método inválido para exclusão.')
        return redirect('financeiro:lista_receitas')


# --- Despesas (Estrutura similar às Receitas) ---
@page_access_required('financeiro')
def lista_despesas(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    try:
        allowed_churches = get_finance_read_scope(request.user, ministerio)
        despesas_qs = Despesas.objects.filter(igreja__in=allowed_churches).select_related('igreja', 'categoria', 'evento').order_by('-data')

        # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
        if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
            despesas_qs = despesas_qs.filter(igreja=request.igreja_ativa)
        elif request.igreja_ativa:
            despesas_qs = Despesas.objects.none()
        # Se nenhuma igreja ativa, o filtro já é por igreja__in=allowed_churches (definido acima)
        # --- Fim Lógica de Filtragem Inicial ---
        
        # Filtros adicionais


        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        categoria_id = request.GET.get('categoria')
        igreja_id_get = request.GET.get('igreja') # Renomeado para evitar conflito com variável de contexto
        caixa_id_filtro = request.GET.get('caixa_filtro')
        evento_id_filtro = request.GET.get('evento')
        fundo_id_filtro = request.GET.get('fundo_filtro')
        aprovacao_status_filtro = (request.GET.get('aprovacao_status') or '').strip().upper()
        fundos_disponivel = _fundos_departamentais_disponivel()

        if fundos_disponivel:
            if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
                fundos_dropdown = DepartamentoFinanceiroService.fundos_visiveis_para_igrejas([request.igreja_ativa])
            elif request.igreja_ativa:
                fundos_dropdown = FundoDepartamental.objects.none()
            else:
                fundos_dropdown = DepartamentoFinanceiroService.fundos_visiveis_para_igrejas(allowed_churches)

            if fundo_id_filtro and not fundos_dropdown.filter(pk=fundo_id_filtro).exists():
                messages.warning(request, 'Fundo selecionado inválido para o seu escopo. Exibindo dados sem filtro de fundo.')
                fundo_id_filtro = ''
        else:
            fundos_dropdown = FundoDepartamental.objects.none()
            fundo_id_filtro = ''
        # --- LÓGICA DO FILTRO 'fechado' ---
        # Pega o valor do parâmetro, default para 'false' (aberto) se não vier na URL
        fechado_filter = request.GET.get('fechado', 'false')

        if data_inicio: despesas_qs = despesas_qs.filter(data__gte=data_inicio)
        if data_fim: despesas_qs = despesas_qs.filter(data__lte=data_fim)
        if categoria_id: despesas_qs = despesas_qs.filter(categoria_id=categoria_id)
        if caixa_id_filtro:
            despesas_qs = despesas_qs.filter(conta_bancaria_id=caixa_id_filtro)
        if evento_id_filtro:
            despesas_qs = despesas_qs.filter(evento_id=evento_id_filtro)
        if fundos_disponivel and fundo_id_filtro:
            despesas_qs = despesas_qs.filter(fundo_departamental_id=fundo_id_filtro)
        if aprovacao_status_filtro in {
            Despesas.APROVACAO_PENDENTE,
            Despesas.APROVACAO_APROVADA,
            Despesas.APROVACAO_REJEITADA,
        }:
            despesas_qs = despesas_qs.filter(aprovacao_status=aprovacao_status_filtro)
        if igreja_id_get:
            # Este filtro só deve ser aplicado se request.igreja_ativa NÃO estiver definida
            if not request.igreja_ativa and allowed_churches.filter(pk=igreja_id_get).exists():
                despesas_qs = despesas_qs.filter(igreja_id=igreja_id_get)

        # Aplica o filtro 'fechado' baseado no valor (seja o da URL ou o default 'false')
        if fechado_filter == 'true':
            despesas_qs = despesas_qs.filter(fechado=True)
        elif fechado_filter == 'false': # Inclui o default
            despesas_qs = despesas_qs.filter(fechado=False)
        # --- FIM DA LÓGICA DO FILTRO 'fechado' ---

        sort_map = {
            'data': 'data',
            '-data': '-data',
            'igreja': 'igreja__nome_igreja',
            '-igreja': '-igreja__nome_igreja',
            'descricao': 'descricao',
            '-descricao': '-descricao',
            'categoria': 'categoria__nome',
            '-categoria': '-categoria__nome',
            'evento': 'evento__titulo',
            '-evento': '-evento__titulo',
            'valor': 'valor',
            '-valor': '-valor',
        }
        sort = request.GET.get('sort', '-data')
        order_by = sort_map.get(sort, '-data')
        despesas_qs = despesas_qs.order_by(order_by, '-id')

        categorias_org = CategoriaDespesa.objects.filter(ministerio=ministerio)
        # --- RESUMOS GERAIS DE DESPESAS ---
        from decimal import Decimal
        despesas_base_filtradas = despesas_qs
        resumo_total_periodo = despesas_base_filtradas.aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        resumo_total_aberto = despesas_base_filtradas.filter(fechado=False).aggregate(total=Sum('valor')).get('total') or Decimal('0.00')
        resumo_quantidade_periodo = despesas_base_filtradas.count()
        resumo_ticket_medio = (resumo_total_periodo / resumo_quantidade_periodo) if resumo_quantidade_periodo else Decimal('0.00')

        # --- RESUMOS POR CATEGORIA DE DESPESA ---
        despesas_por_categoria = despesas_qs.values('categoria__nome').annotate(total=Sum('valor')).order_by('-total')
        resumos_categoria = {}
        for item in despesas_por_categoria:
            categoria_nome = item['categoria__nome'] if item['categoria__nome'] else 'Sem Categoria'
            resumos_categoria[categoria_nome] = item['total'] or Decimal('0.00')

        # --- Lógica para o dropdown de filtro de igreja no template ---        
        igrejas_para_filtro_template = allowed_churches
        igreja_id_selecionada_template = igreja_id_get # Para o select do filtro da página
        if request.igreja_ativa: igrejas_para_filtro_template = Igreja.objects.filter(pk=request.igreja_ativa.pk) # Ou desabilitar o filtro
        if request.igreja_ativa: igreja_id_selecionada_template = str(request.igreja_ativa.pk)

        # --- FILTRO DE CONTAS BANCÁRIAS (respeitando a igreja ativa) ---
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            contas_bancarias_dropdown = ContaBancaria.objects.filter(igreja=request.igreja_ativa).order_by('nome_identificacao')
            eventos_dropdown = Evento.objects.filter(igreja=request.igreja_ativa).order_by('-data_inicio', 'titulo')
        else:
            contas_bancarias_dropdown = ContaBancaria.objects.filter(igreja__in=allowed_churches).order_by('igreja__nome_igreja', 'nome_identificacao')
            eventos_dropdown = Evento.objects.filter(igreja__in=allowed_churches).order_by('-data_inicio', 'titulo')

        # Permissão de edição para o template
        can_edit = has_finance_edit_permission(request.user)
        can_approve = _user_pode_aprovar_saida(request.user)
        query_params = request.GET.copy()
        query_params.pop('sort', None)

        context = {
            'despesas': despesas_qs,
            'ministerio': ministerio,
            'categorias_org': categorias_org, # Continua mostrando todas as categorias da org
            'igrejas_org': igrejas_para_filtro_template, 
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'categoria_selecionada': categoria_id,
            'igreja_selecionada': igreja_id_selecionada_template, # ID para o select do filtro da página
            'evento_selecionado': evento_id_filtro,
            # Passa o valor que FOI USADO no filtro para o template selecionar a opção correta
            'fechado_selecionado': fechado_filter,
            'can_edit_finance': can_edit, # Flag para o template
            'contas_bancarias_painel': contas_bancarias_dropdown,
            'fundos_departamentais_dropdown': fundos_dropdown,
            'fundos_departamentais_disponivel': fundos_disponivel,
            'eventos_filtro': eventos_dropdown,
            'fundo_id_filtro_selecionado': fundo_id_filtro,
            'aprovacao_status_filtro': aprovacao_status_filtro,
            'sort_atual': sort if sort in sort_map else '-data',
            'querystring_without_sort': query_params.urlencode(),
            # Novos resumos
            'resumo_total_periodo': resumo_total_periodo,
            'resumo_total_aberto': resumo_total_aberto,
            'resumo_ticket_medio': resumo_ticket_medio,
            'resumo_quantidade_periodo': resumo_quantidade_periodo,
            'resumos_categoria': resumos_categoria,
            'can_approve_despesa': can_approve,
        }
        return render(request, 'financeiro/despesas/lista_despesas.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar despesas para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao listar as despesas: {e}")
        return redirect('financeiro:painel_financeiro')


@page_access_required('financeiro')
def cadastrar_despesa(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    igreja_padrao_para_form = None # Inicializa
    next_url = _get_safe_next_url(request, 'financeiro:lista_despesas')

    if request.method == 'GET' and next_url == reverse('eventos:lista_eventos'):
        return redirect('financeiro:cadastrar_despesa_caixa_eventos')

    if not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar despesas ou não está associado a nenhuma igreja específica.")
        return redirect(next_url)

    if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
        igreja_padrao_para_form = request.igreja_ativa
    elif allowed_churches.count() == 1:
        igreja_padrao_para_form = allowed_churches.first()

    if igreja_padrao_para_form is None:
        messages.error(request, "Selecione uma igreja no seletor global antes de cadastrar a despesa.")
        return redirect(next_url)

    batch_itens = _batch_get(request, 'despesas', igreja_padrao_para_form.pk)
    batch_defaults = _batch_defaults_get(request, 'despesas', igreja_padrao_para_form.pk)

    if request.method == 'POST':
        action = (request.POST.get('action') or 'save_single').strip()

        if action == 'batch_remove':
            item_id = (request.POST.get('batch_item_id') or '').strip()
            batch_itens = [item for item in batch_itens if item.get('id') != item_id]
            _batch_set(request, 'despesas', igreja_padrao_para_form.pk, batch_itens)
            messages.success(request, 'Item removido da lista temporária.')
            return redirect(request.path)

        if action == 'batch_edit':
            item_id = (request.POST.get('batch_item_id') or '').strip()
            item = next((it for it in batch_itens if it.get('id') == item_id), None)
            if item:
                initial_edicao = {
                    'igreja': igreja_padrao_para_form,
                    'data': item.get('data') or '',
                    'categoria': item.get('categoria') or '',
                    'valor': item.get('valor') or '',
                    'descricao': item.get('descricao') or '',
                    'evento': item.get('evento') or '',
                    'conta_bancaria': item.get('conta_bancaria') or '',
                    'observacao': item.get('observacao') or '',
                }
                form = DespesaForm(
                    initial=initial_edicao,
                    ministerio=ministerio,
                    user=request.user, allowed_churches=allowed_churches,
                    igreja_selecionada_inicial=igreja_padrao_para_form,
                )
                context = {
                    'form': form,
                    'ministerio': ministerio,
                    'titulo_pagina': 'Cadastrar Despesa',
                    'ocultar_campo_igreja': True,
                    'url_cancelar': next_url,
                    'next_url': next_url,
                    'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(igreja_padrao_para_form),
                    'mostrar_evento_por_conta': True,
                    'batch_itens': batch_itens,
                    'batch_tipo': 'despesas',
                    'batch_edit_item_id': item_id,
                }
                return render(request, 'financeiro/despesas/form_despesa.html', context)
            messages.warning(request, 'Item não encontrado para edição.')
            return redirect(request.path)

        if action == 'batch_duplicate':
            item_id = (request.POST.get('batch_item_id') or '').strip()
            item = next((it for it in batch_itens if it.get('id') == item_id), None)
            if item:
                novo_item = item.copy()
                novo_item['id'] = str(uuid4())
                batch_itens.append(novo_item)
                _batch_set(request, 'despesas', igreja_padrao_para_form.pk, batch_itens)
                messages.success(request, 'Item duplicado na lista temporária.')
            else:
                messages.warning(request, 'Item não encontrado para duplicar.')
            return redirect(request.path)

        if action == 'batch_clear':
            _batch_clear(request, 'despesas', igreja_padrao_para_form.pk)
            messages.success(request, 'Lista temporária de despesas limpa.')
            return redirect(request.path)

        if action == 'batch_save':
            if not batch_itens:
                messages.warning(request, 'Não há itens na lista temporária para salvar.')
                return redirect(request.path)

            salvos = 0
            with transaction.atomic():
                for item in batch_itens:
                    payload = {
                        'igreja': str(igreja_padrao_para_form.pk),
                        'evento': item.get('evento') or '',
                        'categoria': item.get('categoria') or '',
                        'data': item.get('data') or '',
                        'valor': item.get('valor') or '',
                        'descricao': item.get('descricao') or '',
                        'conta_bancaria': item.get('conta_bancaria') or '',
                        'observacao': item.get('observacao') or '',
                    }
                    item_form = DespesaForm(
                        payload,
                        ministerio=ministerio,
                        user=request.user, allowed_churches=allowed_churches,
                        igreja_selecionada_inicial=igreja_padrao_para_form,
                    )
                    if not item_form.is_valid():
                        raise ValidationError(f"Item inválido no lote de despesas: {item_form.errors.as_text()}")

                    nova_despesa = item_form.save(commit=False)
                    nova_despesa.igreja = igreja_padrao_para_form
                    nova_despesa.criado_por = request.user
                    _aplicar_politica_aprovacao_saida(request, nova_despesa)
                    nova_despesa.save()
                    salvos += 1

            _batch_clear(request, 'despesas', igreja_padrao_para_form.pk)
            messages.success(request, f'{salvos} despesa(s) salvas com sucesso em lote!')
            return redirect(next_url)

        post_data = request.POST.copy()
        post_data['igreja'] = str(igreja_padrao_para_form.pk)
        form = DespesaForm(post_data, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_selecionada_inicial=igreja_padrao_para_form)
        if form.is_valid():
            try:
                nova_despesa = form.save(commit=False)
                nova_despesa.igreja = igreja_padrao_para_form
                nova_despesa.criado_por = request.user
                if not allowed_churches.filter(pk=nova_despesa.igreja_id).exists(): messages.error(request, "Erro: Igreja inválida.")
                elif nova_despesa.categoria.ministerio != ministerio: messages.error(request, "Erro: Categoria inválida.")
                # Adicionar validação de conta bancária se usar
                else:
                        if action == 'batch_add':
                            novo_item = {
                                'id': str(uuid4()),
                                'data': str(form.cleaned_data['data']),
                                'categoria': str(form.cleaned_data['categoria'].pk),
                                'categoria_label': form.cleaned_data['categoria'].nome,
                                'valor': str(form.cleaned_data['valor']),
                                'descricao': form.cleaned_data.get('descricao') or '',
                                'evento': str(form.cleaned_data['evento'].pk) if form.cleaned_data.get('evento') else '',
                                'evento_label': form.cleaned_data['evento'].titulo if form.cleaned_data.get('evento') else '-',
                                'conta_bancaria': str(form.cleaned_data['conta_bancaria'].pk) if form.cleaned_data.get('conta_bancaria') else '',
                                'conta_bancaria_label': form.cleaned_data['conta_bancaria'].nome_identificacao if form.cleaned_data.get('conta_bancaria') else '-',
                                'observacao': form.cleaned_data.get('observacao') or '',
                            }
                            edit_item_id = (request.POST.get('batch_edit_item_id') or '').strip()
                            if edit_item_id:
                                atualizado = False
                                for idx, item_existente in enumerate(batch_itens):
                                    if item_existente.get('id') == edit_item_id:
                                        novo_item['id'] = edit_item_id
                                        batch_itens[idx] = novo_item
                                        atualizado = True
                                        break
                                if not atualizado:
                                    batch_itens.append(novo_item)
                            else:
                                batch_itens.append(novo_item)

                            _batch_set(request, 'despesas', igreja_padrao_para_form.pk, batch_itens)
                            _batch_defaults_set(
                                request,
                                'despesas',
                                igreja_padrao_para_form.pk,
                                {
                                    'categoria': novo_item.get('categoria') or '',
                                    'conta_bancaria': novo_item.get('conta_bancaria') or '',
                                    'evento': novo_item.get('evento') or '',
                                }
                            )
                            messages.success(request, 'Despesa adicionada à lista temporária.')
                            return redirect(request.path)

                        mensagem_aprovacao = _aplicar_politica_aprovacao_saida(request, nova_despesa)
                        # O método save da Despesa agora atualiza o saldo
                        nova_despesa.save()
                        if mensagem_aprovacao:
                            messages.warning(request, mensagem_aprovacao)
                        else:
                            messages.success(request, 'Despesa cadastrada com sucesso!')
                        return redirect(next_url)
   
            except Exception as e:
                 logger.exception(f"Erro ao salvar despesa para ministério {ministerio.id}")
                 messages.error(request, f'Erro ao salvar despesa: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
      
        initial_form_data = {'igreja': igreja_padrao_para_form}
        initial_form_data.update({
            'categoria': batch_defaults.get('categoria') or '',
            'conta_bancaria': batch_defaults.get('conta_bancaria') or '',
            'evento': batch_defaults.get('evento') or '',
        })
        form = DespesaForm(initial=initial_form_data, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_selecionada_inicial=igreja_padrao_para_form)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Cadastrar Despesa',
        'ocultar_campo_igreja': True,
        'url_cancelar': next_url,
        'next_url': next_url,
        'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(igreja_padrao_para_form),
        'mostrar_evento_por_conta': True,
        'batch_itens': batch_itens,
        'batch_tipo': 'despesas',
    }
    return render(request, 'financeiro/despesas/form_despesa.html', context)


@page_access_required('financeiro')
def cadastrar_despesa_evento(request, evento_id):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    evento = get_object_or_404(Evento, pk=evento_id, igreja__in=allowed_churches)
    conta_evento_efetiva_id = evento.conta_bancaria_evento_id or getattr(evento.igreja, 'conta_padrao_eventos_id', None)

    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['igreja'] = str(evento.igreja_id)
        post_data['evento'] = str(evento.pk)
        if conta_evento_efetiva_id:
            post_data['conta_bancaria'] = str(conta_evento_efetiva_id)

        form = DespesaForm(
            post_data,
            ministerio=ministerio,
            user=request.user, allowed_churches=allowed_churches,
            igreja_selecionada_inicial=evento.igreja,
            evento_contexto=evento,
            codigo_fundo_contexto=FundoDepartamental.CODIGO_EVENTOS,
            travar_evento=True,
            travar_conta_evento=bool(conta_evento_efetiva_id),
        )
        if form.is_valid():
            try:
                despesa = form.save(commit=False)
                despesa.igreja = evento.igreja
                despesa.evento = evento
                despesa.criado_por = request.user
                if conta_evento_efetiva_id:
                    despesa.conta_bancaria_id = conta_evento_efetiva_id
                mensagem_aprovacao = _aplicar_politica_aprovacao_saida(request, despesa)
                despesa.save()
                if mensagem_aprovacao:
                    messages.warning(request, mensagem_aprovacao)
                else:
                    messages.success(request, 'Saída do evento cadastrada com sucesso!')
                return redirect('eventos:detalhe_evento', pk=evento.pk)
            except Exception as e:
                logger.exception(f"Erro ao salvar despesa do evento {evento.pk} para ministério {ministerio.id}")
                messages.error(request, f'Erro ao salvar saída do evento: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        initial = {
            'igreja': evento.igreja,
            'evento': evento,
            'data': now().date(),
        }
        if conta_evento_efetiva_id:
            initial['conta_bancaria'] = conta_evento_efetiva_id

        form = DespesaForm(
            initial=initial,
            ministerio=ministerio,
            user=request.user, allowed_churches=allowed_churches,
            igreja_selecionada_inicial=evento.igreja,
            evento_contexto=evento,
            codigo_fundo_contexto=FundoDepartamental.CODIGO_EVENTOS,
            travar_evento=True,
            travar_conta_evento=bool(conta_evento_efetiva_id),
        )

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': f'Adicionar Saída - {evento.titulo}',
        'ocultar_campo_igreja': True,
        'ocultar_campo_evento': True,
        'ocultar_campo_conta_bancaria': bool(conta_evento_efetiva_id),
        'modo_evento': True,
        'evento_contexto': evento,
        'url_cancelar': reverse('eventos:detalhe_evento', kwargs={'pk': evento.pk}),
        'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(evento.igreja),
        'mostrar_evento_por_conta': False,
    }
    return render(request, 'financeiro/despesas/form_despesa.html', context)


@page_access_required('financeiro')
def cadastrar_despesa_caixa_eventos(request):
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    igreja_padrao_para_form = None

    if not allowed_churches.exists():
        return redirect('eventos:lista_eventos')

    if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
        igreja_padrao_para_form = request.igreja_ativa
    elif allowed_churches.count() == 1:
        igreja_padrao_para_form = allowed_churches.first()

    if igreja_padrao_para_form is None:
        messages.error(request, "Selecione uma igreja no seletor global antes de lançar saída de eventos.")
        return redirect('eventos:lista_eventos')

    conta_padrao_eventos_id = getattr(igreja_padrao_para_form, 'conta_padrao_eventos_id', None)

    if request.method == 'POST':
        post_data = request.POST.copy()
        post_data['igreja'] = str(igreja_padrao_para_form.pk)
        if conta_padrao_eventos_id and not post_data.get('conta_bancaria'):
            post_data['conta_bancaria'] = str(conta_padrao_eventos_id)

        evento_id = post_data.get('evento')
        evento = None
        conta_evento_efetiva_id = None
        if evento_id:
            evento = Evento.objects.filter(pk=evento_id, igreja__in=allowed_churches).first()
            if evento:
                conta_evento_efetiva_id = evento.conta_bancaria_evento_id or getattr(evento.igreja, 'conta_padrao_eventos_id', None)
                if conta_evento_efetiva_id:
                    post_data['conta_bancaria'] = str(conta_evento_efetiva_id)

        form = DespesaForm(
            post_data,
            ministerio=ministerio,
            user=request.user, allowed_churches=allowed_churches,
            igreja_selecionada_inicial=igreja_padrao_para_form,
            codigo_fundo_contexto=FundoDepartamental.CODIGO_EVENTOS,
        )
        if form.is_valid():
            try:
                despesa = form.save(commit=False)
                despesa.igreja = igreja_padrao_para_form
                despesa.criado_por = request.user
                if not despesa.evento_id and _fundos_departamentais_disponivel():
                    fundo_eventos, _created = FundoDepartamental.objects.get_or_create(
                        igreja=igreja_padrao_para_form,
                        codigo=FundoDepartamental.CODIGO_EVENTOS,
                        defaults={'nome_exibicao': 'Eventos'},
                    )
                    despesa.fundo_departamental = fundo_eventos
                if despesa.evento_id:
                    conta_evento_efetiva_id = despesa.evento.conta_bancaria_evento_id or getattr(despesa.evento.igreja, 'conta_padrao_eventos_id', None)
                    if conta_evento_efetiva_id:
                        despesa.conta_bancaria_id = conta_evento_efetiva_id
                mensagem_aprovacao = _aplicar_politica_aprovacao_saida(request, despesa)
                despesa.save()
                if mensagem_aprovacao:
                    messages.warning(request, mensagem_aprovacao)
                else:
                    messages.success(request, 'Saída do caixa de eventos cadastrada com sucesso!')
                return redirect('eventos:lista_eventos')
            except Exception as e:
                logger.exception(f"Erro ao salvar saída do caixa de eventos para ministério {ministerio.id}")
                messages.error(request, f'Erro ao salvar saída do caixa de eventos: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        initial = {
            'igreja': igreja_padrao_para_form,
            'data': now().date(),
        }
        if conta_padrao_eventos_id:
            initial['conta_bancaria'] = conta_padrao_eventos_id
        form = DespesaForm(
            initial=initial,
            ministerio=ministerio,
            user=request.user, allowed_churches=allowed_churches,
            igreja_selecionada_inicial=igreja_padrao_para_form,
            codigo_fundo_contexto=FundoDepartamental.CODIGO_EVENTOS,
        )

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Lançar Saída - Caixa de Eventos',
        'ocultar_campo_igreja': True,
        'ocultar_campo_categoria': False,
        'ocultar_campo_conta_bancaria': bool(conta_padrao_eventos_id),
        'url_cancelar': reverse('eventos:lista_eventos'),
        'form_action_url': reverse('financeiro:cadastrar_despesa_caixa_eventos'),
        'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(igreja_padrao_para_form),
        'mostrar_evento_por_conta': False,
    }
    return render(request, 'financeiro/despesas/form_despesa.html', context)


@page_access_required('financeiro')
def editar_despesa(request, pk): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    despesa = get_object_or_404(Despesas, pk=pk, igreja__in=allowed_churches)

    if despesa.fechado:
        messages.error(request, "Não é possível editar uma despesa fechada.")
        return redirect('financeiro:lista_despesas')

    if request.method == 'POST':
        form = DespesaForm(request.POST, instance=despesa, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)
        if form.is_valid():
            try:
                despesa_editada = form.save(commit=False)
                if despesa_editada.igreja not in allowed_churches: messages.error(request, "Erro: Igreja inválida.")
                elif despesa_editada.categoria.ministerio != ministerio: messages.error(request, "Erro: Categoria inválida.")
                # Adicionar validação de conta bancária se usar
                else:
                    mensagem_aprovacao = _aplicar_politica_aprovacao_saida(request, despesa_editada)
                    despesa_editada.save()
                    if mensagem_aprovacao:
                        messages.warning(request, mensagem_aprovacao)
                    else:
                        messages.success(request, 'Despesa atualizada com sucesso!')
                    return redirect('financeiro:lista_despesas')
            except Exception as e:
                 logger.exception(f"Erro ao salvar edição da despesa {pk} para ministério {ministerio.id}")
                 messages.error(request, f'Erro ao salvar despesa: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = DespesaForm(instance=despesa, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Editar Despesa',
        'despesa': despesa,
        'url_cancelar': reverse('financeiro:lista_despesas'),
        'contas_eventos_ids': _obter_ids_contas_eventos_para_igreja(despesa.igreja),
        'mostrar_evento_por_conta': True,
    }
    return render(request, 'financeiro/despesas/form_despesa.html', context)


@page_access_required('financeiro')
def excluir_despesa(request, pk): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    despesa = get_object_or_404(Despesas, pk=pk, igreja__in=allowed_churches)

    if despesa.fechado:
        messages.error(request, "Não é possível excluir uma despesa fechada.")
        return redirect('financeiro:lista_despesas')

    if request.method == 'POST':
        try:
            nome_despesa = despesa.descricao or f"Despesa ID {despesa.pk}"
            despesa.delete()  # O método delete da Despesa reverte o saldo
            messages.success(request, f'Despesa "{nome_despesa}" excluída com sucesso!')
        except Exception as e:
            logger.exception(f"Erro ao excluir despesa {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao excluir despesa: {e}')
        return redirect('financeiro:lista_despesas')

    messages.error(request, 'Método inválido para exclusão.')
    return redirect('financeiro:lista_despesas')


@page_access_required('financeiro')
def aprovar_despesa(request, pk):
    ministerio = get_ministerio_or_error(request)
    if request.method != 'POST':
        messages.error(request, 'Método inválido para aprovação.')
        return redirect('financeiro:lista_despesas')

    if not _user_pode_aprovar_saida(request.user):
        raise PermissionDenied('Você não tem permissão para aprovar despesas.')

    allowed_churches = get_finance_write_scope(request.user, ministerio)
    despesa = get_object_or_404(Despesas, pk=pk, igreja__in=allowed_churches)

    if despesa.criado_por_id == request.user.id:
        raise PermissionDenied('Você não pode aprovar uma despesa criada por você.')

    if despesa.fechado:
        messages.error(request, 'Não é possível aprovar uma despesa já fechada.')
        return redirect('financeiro:lista_despesas')

    if despesa.aprovacao_status == Despesas.APROVACAO_APROVADA:
        messages.info(request, 'Esta despesa já está aprovada.')
        return redirect('financeiro:lista_despesas')

    try:
        despesa.aprovacao_status = Despesas.APROVACAO_APROVADA
        despesa.aprovado_por = request.user
        despesa.aprovado_em = now()
        despesa.observacao_aprovacao = (request.POST.get('observacao_aprovacao') or '').strip() or despesa.observacao_aprovacao
        despesa.save(update_fields=['aprovacao_status', 'aprovado_por', 'aprovado_em', 'observacao_aprovacao'])
        messages.success(request, 'Despesa aprovada com sucesso.')
    except Exception:
        logger.exception(f"Erro ao aprovar despesa {pk} para ministério {ministerio.id}")
        messages.error(request, 'Erro ao aprovar despesa.')

    return redirect('financeiro:lista_despesas')


@page_access_required('financeiro')
def reprovar_despesa(request, pk):
    ministerio = get_ministerio_or_error(request)
    if request.method != 'POST':
        messages.error(request, 'Método inválido para reprovação.')
        return redirect('financeiro:lista_despesas')

    if not _user_pode_aprovar_saida(request.user):
        raise PermissionDenied('Você não tem permissão para reprovar despesas.')

    allowed_churches = get_finance_write_scope(request.user, ministerio)
    despesa = get_object_or_404(Despesas, pk=pk, igreja__in=allowed_churches)

    if despesa.criado_por_id == request.user.id:
        raise PermissionDenied('Você não pode reprovar uma despesa criada por você.')

    if despesa.fechado:
        messages.error(request, 'Não é possível reprovar uma despesa já fechada.')
        return redirect('financeiro:lista_despesas')

    if despesa.aprovacao_status == Despesas.APROVACAO_REJEITADA:
        messages.info(request, 'Esta despesa já está reprovada.')
        return redirect('financeiro:lista_despesas')

    observacao = (request.POST.get('observacao_aprovacao') or '').strip()
    if not observacao:
        messages.error(request, 'Informe o motivo da reprovação antes de continuar.')
        return redirect('financeiro:lista_despesas')

    try:
        despesa.aprovacao_status = Despesas.APROVACAO_REJEITADA
        despesa.aprovado_por = request.user
        despesa.aprovado_em = now()
        despesa.observacao_aprovacao = observacao
        despesa.save(update_fields=['aprovacao_status', 'aprovado_por', 'aprovado_em', 'observacao_aprovacao'])
        messages.success(request, 'Despesa reprovada com sucesso.')
    except Exception:
        logger.exception(f"Erro ao reprovar despesa {pk} para ministério {ministerio.id}")
        messages.error(request, 'Erro ao reprovar despesa.')

    return redirect('financeiro:lista_despesas')



# --- Categorias de Despesa ---
@page_access_required('financeiro')
def lista_categorias_despesa(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    categorias = CategoriaDespesa.objects.filter(ministerio=ministerio).order_by('nome')
    can_edit = has_finance_edit_permission(request.user) # Para botão de adicionar
    context = {
        'categorias': categorias,
        'ministerio': ministerio,
        'can_edit_finance': can_edit,
    }
    return render(request, 'financeiro/categorias/lista_categorias.html', context)

@page_access_required('financeiro')
def cadastrar_categoria_despesa(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    if request.method == 'POST':
        form = CategoriaDespesaForm(request.POST)
        if form.is_valid():
            try:
                nova_categoria = form.save(commit=False)
                nova_categoria.ministerio = ministerio # Associa à ministério
                nova_categoria.save()
                messages.success(request, 'Categoria de despesa cadastrada com sucesso!')
                return redirect('financeiro:lista_categorias_despesa')
            except Exception as e:
                 logger.exception(f"Erro ao salvar categoria de despesa para ministério {ministerio.id}")
                 messages.error(request, f'Erro ao salvar categoria: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = CategoriaDespesaForm()
    context = {'form': form, 'ministerio': ministerio, 'titulo_pagina': 'Cadastrar Categoria de Despesa'}
    return render(request, 'financeiro/categorias/form_categoria.html', context)




# ====================================================
# ========= INÍCIO: VIEWS PARA CONTAS BANCÁRIAS =========
# ====================================================

@page_access_required('financeiro')
def lista_contas_bancarias(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    try:
        allowed_churches = get_finance_read_scope(request.user, ministerio)
        query = request.GET.get('q', '').strip()
        tipo_selecionado = request.GET.get('tipo', 'todos')

        contas_base = ContaBancaria.objects.select_related('igreja').filter(igreja__in=allowed_churches)

        # --- Lógica para filtrar pela igreja ativa quando disponível ---
        if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
            contas_base = contas_base.filter(igreja=request.igreja_ativa)
        # --- Fim Lógica de Filtragem Inicial ---

        if query:
            contas_base = contas_base.filter(
                Q(nome_identificacao__icontains=query)
                | Q(igreja__nome_igreja__icontains=query)
                | Q(instituicao_bancaria__icontains=query)
                | Q(agencia__icontains=query)
                | Q(conta__icontains=query)
            )

        if tipo_selecionado in {'bancaria', 'caixa_fisico'}:
            contas_base = contas_base.filter(tipo=tipo_selecionado)
        else:
            tipo_selecionado = 'todos'

        contas_bancarias = contas_base.order_by('igreja__nome_igreja', 'nome_identificacao')

        can_edit = has_finance_edit_permission(request.user)

        resumo = contas_base.aggregate(
            total_saldo_inicial=Sum('saldo_inicial'),
            total_saldo_atual=Sum('saldo_atual'),
            quantidade=Count('id'),
        )
        resumo_tipos = contas_base.values('tipo').annotate(total=Count('id'))
        total_bancarias = next((item['total'] for item in resumo_tipos if item['tipo'] == 'bancaria'), 0)
        total_caixas = next((item['total'] for item in resumo_tipos if item['tipo'] == 'caixa_fisico'), 0)

        context = {
            'contas_bancarias': contas_bancarias,
            'ministerio': ministerio,
            'can_edit_finance': can_edit,
            'titulo_pagina': 'Contas Bancárias/Caixas',
            'current_q': query,
            'current_tipo': tipo_selecionado,
            'resumo_quantidade': resumo.get('quantidade') or 0,
            'resumo_total_bancarias': total_bancarias,
            'resumo_total_caixas': total_caixas,
            'resumo_saldo_inicial': resumo.get('total_saldo_inicial') or Decimal('0.00'),
            'resumo_saldo_atual': resumo.get('total_saldo_atual') or Decimal('0.00'),
        }
        return render(request, 'financeiro/contas_bancarias/lista_contas_bancarias.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar contas bancárias para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao listar as contas bancárias: {e}")
        return redirect('financeiro:painel_financeiro')


@page_access_required('financeiro')
def criar_conta_bancaria(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    igreja_inicial_para_form = None 


    if not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar contas ou não está associado a nenhuma igreja específica.")
        return redirect('financeiro:lista_contas_bancarias')

    if request.method == 'POST':
        # Ao submeter, o form pega a igreja do request.POST se o campo estiver habilitado,
        # ou usa a instance.igreja se estiver desabilitado (o que não é o caso aqui para criação)
        # Passamos igreja_selecionada_inicial=request.igreja_ativa para o form __init__
        # para que ele possa desabilitar o campo e torná-lo não obrigatório se necessário.
        form = ContaBancariaForm(request.POST, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_selecionada_inicial=request.igreja_ativa)
        if form.is_valid():
            try:
                nova_conta = form.save(commit=False)
                
                # Se request.igreja_ativa foi usada para desabilitar o campo 'igreja' no form,
                # form.cleaned_data['igreja'] será None (porque required=False).
                # Precisamos definir a igreja explicitamente.
                if request.igreja_ativa and request.igreja_ativa in allowed_churches:
                    nova_conta.igreja = request.igreja_ativa
                elif not nova_conta.igreja: # Se a igreja não foi definida (nem pelo form, nem pelo global)
                    messages.error(request, "A igreja para a nova conta não foi definida. Por favor, selecione uma igreja.")
                    raise ValueError("Igreja não definida para a nova conta.")

                # Validação de segurança adicional

                if nova_conta.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                    # Não levanta exceção aqui, deixa o form ser re-renderizado com a mensagem
                else:
                    nova_conta.save()
                    messages.success(request, f'Conta/Caixa "{nova_conta.nome_identificacao}" para a igreja "{nova_conta.igreja.nome_igreja}" cadastrada com sucesso!')
                    return redirect('financeiro:lista_contas_bancarias')
            except ValueError as ve: # Captura o ValueError que levantamos
                pass # A mensagem já foi adicionada, o formulário será re-renderizado

            except Exception as e:
                 logger.exception(f"Erro ao salvar conta bancária para ministério {ministerio.id}")
                 messages.error(request, f'Erro ao salvar conta/caixa: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
  
        # --- Lógica para pré-selecionar a igreja no formulário GET ---
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_inicial_para_form = request.igreja_ativa
        elif allowed_churches.count() == 1:

            igreja_unica_permitida = allowed_churches.first()
            igreja_inicial_para_form = igreja_unica_permitida
        form = ContaBancariaForm(
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_selecionada_inicial=igreja_inicial_para_form,
        )

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Adicionar Nova Conta Bancária/Caixa'
    }
    return render(request, 'financeiro/contas_bancarias/form_conta_bancaria.html', context)

@page_access_required('financeiro')
def editar_conta_bancaria(request, pk): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    conta_bancaria = get_object_or_404(ContaBancaria, pk=pk, igreja__in=allowed_churches)

    if request.method == 'POST':
        form = ContaBancariaForm(request.POST, instance=conta_bancaria, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)
        if form.is_valid():
            try:
                conta_editada = form.save(commit=False)
                if conta_editada.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida.")
                else:
                    conta_editada.save()
                    messages.success(request, 'Conta Bancária/Caixa atualizada com sucesso!')
                    return redirect('financeiro:lista_contas_bancarias')
            except Exception as e:
                 logger.exception(f"Erro ao editar conta bancária {pk} para ministério {ministerio.id}")
                 messages.error(request, f'Erro ao salvar conta/caixa: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = ContaBancariaForm(instance=conta_bancaria, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)

    context = {
        'form': form,
        'ministerio': ministerio,
        'conta_bancaria': conta_bancaria,
        'titulo_pagina': f'Editar Conta/Caixa: {conta_bancaria.nome_identificacao}'
    }
    return render(request, 'financeiro/contas_bancarias/form_conta_bancaria.html', context)

@page_access_required('financeiro')
def excluir_conta_bancaria(request, pk): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)
    conta_bancaria = get_object_or_404(ContaBancaria, pk=pk, igreja__in=allowed_churches)

    # Verificar se a conta está em uso antes de excluir
    if ContaPagar.objects.filter(conta_debito=conta_bancaria).exists(): # Adicionar outras verificações se Receitas/Despesas usarem
        messages.error(request, f'Não é possível excluir a conta/caixa "{conta_bancaria.nome_identificacao}", pois ela já foi utilizada em lançamentos de Contas a Pagar.')
        return redirect('financeiro:lista_contas_bancarias')
    # Adicionar verificações para Receitas e Despesas se elas passarem a usar conta_bancaria
    # if Receitas.objects.filter(conta_bancaria=conta_bancaria).exists() or \
    #    Despesas.objects.filter(conta_bancaria=conta_bancaria).exists():
    #     messages.error(request, f'Não é possível excluir a conta/caixa "{conta_bancaria.nome_identificacao}", pois ela já foi utilizada em Receitas ou Despesas.')
    #     return redirect('financeiro:lista_contas_bancarias')

    if request.method == 'POST':
        try:
            nome_conta = conta_bancaria.nome_identificacao
            conta_bancaria.delete()
            messages.success(request, f'Conta Bancária/Caixa "{nome_conta}" excluída com sucesso!')
        except Exception as e:
            logger.exception(f"Erro ao excluir conta bancária {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao excluir conta/caixa: {e}')
        return redirect('financeiro:lista_contas_bancarias')
    else:
        context = {
            'conta_bancaria': conta_bancaria,
            'ministerio': ministerio,
            'titulo_pagina': 'Confirmar Exclusão de Conta/Caixa'
            }
        return render(request, 'financeiro/contas_bancarias/confirmar_excluir_conta.html', context)

# ==================================================
# ========= FIM: VIEWS PARA CONTAS BANCÁRIAS =========
# ==================================================






# --- Fechamento de Caixa (Refatorado) ---
@page_access_required('financeiro')
def lista_fechamentos_caixa(request): # noqa: E302
    """ Lista os fechamentos de caixa do ministério. """
    ministerio = get_ministerio_or_error(request)
    
    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    try:
        allowed_churches = get_allowed_churches_for_user(request.user)
        dept_filtro = (request.GET.get('dept_filtro') or '').strip()
        if request.igreja_ativa and allowed_churches.filter(pk=request.igreja_ativa.pk).exists():
            igrejas_escopo = Igreja.objects.filter(pk=request.igreja_ativa.pk)
            fechamentos = FechamentoCaixa.objects.filter(
                igreja=request.igreja_ativa
            ).select_related('igreja', 'fundo_departamental').order_by('-data_fim')
        else:        
            igrejas_escopo = allowed_churches
            # Filtra pelos fechamentos das igrejas permitidas
            fechamentos = FechamentoCaixa.objects.filter(
                igreja__in=igrejas_escopo
            ).select_related('igreja', 'fundo_departamental').order_by('-data_fim')

        departamentos_financeiros_dropdown = DepartamentoFinanceiro.objects.filter(
            igreja__in=igrejas_escopo,
            ativo=True,
            fundo_departamental__isnull=False,
        ).select_related('igreja', 'fundo_departamental').order_by('igreja__nome_igreja', 'nome_exibicao')
        departamento_filtro_obj = None
        if dept_filtro:
            departamento_filtro_obj = departamentos_financeiros_dropdown.filter(pk=dept_filtro).first()
            if departamento_filtro_obj:
                fechamentos = fechamentos.filter(fundo_departamental=departamento_filtro_obj.fundo_departamental)
            else:
                messages.warning(request, 'Departamento selecionado inválido para o seu escopo. Exibindo todos os fechamentos permitidos.')
                dept_filtro = ''
        # Permissão para criar novo fechamento
        can_edit = has_finance_edit_permission(request.user)
        context = {
            'fechamentos': fechamentos,
            'ministerio': ministerio,
            'can_edit_finance': can_edit, # Passa para o template
            'departamentos_financeiros_dropdown': departamentos_financeiros_dropdown,
            'departamento_filtro_selecionado': dept_filtro,
            'departamento_filtro_obj': departamento_filtro_obj,
        }
        return render(request, 'financeiro/fechamentos/lista_fechamentos_caixa.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar fechamentos para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao listar os fechamentos: {e}")
        return redirect('financeiro:painel_financeiro')

# financeiro/views.py
# ... (imports e outras views como estão) ...

@page_access_required('financeiro')
def criar_fechamento_caixa(request): # noqa: E302
    """
    ETAPA 1: Exibe o formulário para selecionar igreja/período (GET)
    ou valida a seleção e mostra a pré-visualização (POST inicial).
    """
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)

    igreja_inicial_para_form = None
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        igreja_inicial_para_form = request.igreja_ativa
    elif allowed_churches.count() == 1 and not is_admin_org(request.user):
        igreja_inicial_para_form = allowed_churches.first()

    form = FechamentoCaixaForm(request.POST or None, 
                               ministerio=ministerio, 
                               user=request.user, # Adicionado user para consistência
                               allowed_churches=allowed_churches, 
                               igreja_selecionada_inicial=igreja_inicial_para_form)

    

    if request.method == 'POST' and form.is_valid():
        # Formulário inicial é válido, vamos buscar dados para pré-visualização
        try:
            # Se a igreja foi desabilitada no form, cleaned_data['igreja'] pode ser None
            if igreja_inicial_para_form and form.fields['igreja'].disabled:
                igreja_selecionada = igreja_inicial_para_form
            else:
                igreja_selecionada = form.cleaned_data.get('igreja')
            data_inicio = form.cleaned_data['data_inicio']
            data_fim = form.cleaned_data['data_fim']
            fundo_selecionado = form.cleaned_data.get('fundo_departamental')
            observacoes = form.cleaned_data.get('observacoes', '') # Pega observações para passar adiante

            # 1. Verificar se a igreja pertence às permitidas (redundante se o form filtrou, mas seguro)
            if not is_admin_org(request.user) and igreja_selecionada not in allowed_churches:
                messages.error(request, "Erro: Igreja selecionada inválida.")
                # Re-renderiza o form inicial com o erro, passando o form já instanciado
                context = {'form': form, 'ministerio': ministerio, 'titulo_pagina': 'Criar Fechamento de Caixa'}
                return render(request, 'financeiro/fechamentos/criar_fechamento_caixa.html', context)

            # 2. Verificar sobreposição (mantido aqui)
            sobreposicao_qs = FechamentoCaixa.objects.filter(
                Q(igreja=igreja_selecionada),
                Q(data_inicio__lte=data_fim) & Q(data_fim__gte=data_inicio)
            )
            if fundo_selecionado:
                sobreposicao_qs = sobreposicao_qs.filter(
                    Q(fundo_departamental=fundo_selecionado) | Q(fundo_departamental__isnull=True)
                )
            sobreposicao = sobreposicao_qs.exists()
            if sobreposicao:
                messages.error(request, f"Já existe um fechamento de caixa para a igreja '{igreja_selecionada.nome_igreja}' que se sobrepõe ao período selecionado.")
                # Re-renderiza o form inicial com o erro, passando o form já instanciado
                context = {'form': form, 'ministerio': ministerio, 'titulo_pagina': 'Criar Fechamento de Caixa'}
                return render(request, 'financeiro/fechamentos/criar_fechamento_caixa.html', context)

            # 3. Buscar receitas e despesas ABERTAS para a pré-visualização
            receitas = Receitas.objects.filter(igreja=igreja_selecionada, data__range=(data_inicio, data_fim), fechado=False)
            despesas = Despesas.objects.filter(
                igreja=igreja_selecionada,
                data__range=(data_inicio, data_fim),
                fechado=False,
                aprovacao_status=Despesas.APROVACAO_APROVADA,
            )
            if fundo_selecionado:
                receitas = receitas.filter(fundo_departamental=fundo_selecionado)
                despesas = despesas.filter(fundo_departamental=fundo_selecionado)
            receitas = receitas.select_related('membro')
            despesas = despesas.select_related('categoria')

            despesas_nao_aprovadas = Despesas.objects.filter(
                igreja=igreja_selecionada,
                data__range=(data_inicio, data_fim),
                fechado=False,
            ).exclude(aprovacao_status=Despesas.APROVACAO_APROVADA)
            if fundo_selecionado:
                despesas_nao_aprovadas = despesas_nao_aprovadas.filter(fundo_departamental=fundo_selecionado)
            despesas_pendentes_count = despesas_nao_aprovadas.filter(aprovacao_status=Despesas.APROVACAO_PENDENTE).count()
            despesas_rejeitadas_count = despesas_nao_aprovadas.filter(aprovacao_status=Despesas.APROVACAO_REJEITADA).count()
            despesas_nao_aprovadas_total = despesas_nao_aprovadas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)

            # 4. Calcular totais provisórios
            total_entradas = receitas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            total_saidas = despesas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            saldo_final = total_entradas - total_saidas

            # Resumo de dízimos e ofertas por forma de pagamento (DIN/PIX)
            dizimos_dinheiro = receitas.filter(categoria='dizimo', forma_pgto='DIN').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            dizimos_pix = receitas.filter(categoria='dizimo', forma_pgto='PIX').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            dizimos_total = dizimos_dinheiro + dizimos_pix

            ofertas_dinheiro = receitas.filter(categoria='oferta', forma_pgto='DIN').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            ofertas_pix = receitas.filter(categoria='oferta', forma_pgto='PIX').aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            ofertas_total = ofertas_dinheiro + ofertas_pix

            exibir_cards_dizimos_ofertas = bool(
                fundo_selecionado and fundo_selecionado.codigo == FundoDepartamental.CODIGO_LOCAL
            )

            # 5. Preparar contexto para o template de CONFIRMAÇÃO
            context_confirmacao = {
                'ministerio': ministerio,
                'igreja_selecionada': igreja_selecionada,
                'fundo_selecionado': fundo_selecionado,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'observacoes': observacoes, # Passa as observações
                'receitas': receitas,
                'despesas': despesas,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_final': saldo_final,
                'dizimos_dinheiro': dizimos_dinheiro,
                'dizimos_pix': dizimos_pix,
                'dizimos_total': dizimos_total,
                'ofertas_dinheiro': ofertas_dinheiro,
                'ofertas_pix': ofertas_pix,
                'ofertas_total': ofertas_total,
                'exibir_cards_dizimos_ofertas': exibir_cards_dizimos_ofertas,
                'despesas_pendentes_count': despesas_pendentes_count,
                'despesas_rejeitadas_count': despesas_rejeitadas_count,
                'despesas_nao_aprovadas_total': despesas_nao_aprovadas_total,
                'can_edit_finance': has_finance_edit_permission(request.user), # Adicionar esta linha
                'titulo_pagina': 'Confirmar Fechamento de Caixa'
            }
            # Renderiza o template de CONFIRMAÇÃO
            return render(request, 'financeiro/fechamentos/confirmar_fechamento_caixa.html', context_confirmacao)

        except Exception as e:
            logger.exception(f"Erro ao preparar pré-visualização do fechamento para ministério {ministerio.id}")
            messages.error(request, f'Erro ao preparar pré-visualização: {e}')
            # Volta para o form inicial em caso de erro inesperado, passando o form já instanciado
            context = {'form': form, 'ministerio': ministerio, 'titulo_pagina': 'Criar Fechamento de Caixa'}
            return render(request, 'financeiro/fechamentos/criar_fechamento_caixa.html', context)
        
        
        else: # Se o form NÃO for válido no POST
            # A mensagem de erro já deve ter sido adicionada pelo form.errors
            # Apenas re-renderiza o template com o form contendo os erros.
            pass # O código abaixo do if/else já lida com isso

    # Se GET ou form inválido no POST, renderiza o form inicial
    context = {'form': form, 'ministerio': ministerio, 'titulo_pagina': 'Criar Fechamento de Caixa'}
    return render(request, 'financeiro/fechamentos/criar_fechamento_caixa.html', context)

# --- FIM DA VIEW criar_fechamento_caixa MODIFICADA ---

# --- NOVA VIEW para finalizar o fechamento ---
@page_access_required('financeiro')
def finalizar_fechamento_caixa(request): # noqa: E302
    """
    ETAPA 2: Recebe o POST da página de confirmação e efetivamente
    cria o FechamentoCaixa e marca as transações como fechadas.
    """
    ministerio = get_ministerio_or_error(request)

    if request.method != 'POST':
        messages.error(request, "Ação inválida.")
        return redirect('financeiro:criar_fechamento_caixa') # Volta para o início

    try:
        # Pegar dados dos campos hidden do POST
        igreja_id = request.POST.get('igreja_id')
        fundo_id = (request.POST.get('fundo_id') or '').strip()
        data_inicio_str = request.POST.get('data_inicio')
        data_fim_str = request.POST.get('data_fim')
        observacoes = request.POST.get('observacoes', '') # Pega observações

        # Validar e converter dados recebidos
        if not all([igreja_id, data_inicio_str, data_fim_str]):
            messages.error(request, "Dados inválidos recebidos para confirmação.")
            return redirect('financeiro:criar_fechamento_caixa')

        # Garante que a igreja pertence às permitidas
        allowed_churches = get_allowed_churches_for_user(request.user)
        # Usar filter().first() ou get() com verificação
        igreja_selecionada = allowed_churches.filter(pk=igreja_id).first()
        if not igreja_selecionada:
             # Se não encontrou nas permitidas (ou ID inválido), negar permissão
             raise PermissionDenied("Igreja selecionada inválida ou não permitida.")

        fundo_selecionado = None
        if fundo_id:
            fundo_selecionado = FundoDepartamental.objects.filter(
                pk=fundo_id,
                igreja=igreja_selecionada,
                ativo=True,
            ).first()
            if not fundo_selecionado:
                raise PermissionDenied("Fundo departamental inválido para a igreja selecionada.")

        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date() # Converte string para date
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        # --- REFAZER AS VERIFICAÇÕES E CÁLCULOS (IMPORTANTE!) ---
        # Não confiar nos totais passados, recalcular com base nas transações ABERTAS atuais.

        # 1. Verificar sobreposição novamente (segurança extra)
        sobreposicao_qs = FechamentoCaixa.objects.filter(
            Q(igreja=igreja_selecionada),
            Q(data_inicio__lte=data_fim) & Q(data_fim__gte=data_inicio)
        )
        if fundo_selecionado:
            sobreposicao_qs = sobreposicao_qs.filter(
                Q(fundo_departamental=fundo_selecionado) | Q(fundo_departamental__isnull=True)
            )
        sobreposicao = sobreposicao_qs.exists()
        if sobreposicao:
            messages.error(request, f"Erro: Um fechamento sobreposto foi criado enquanto você confirmava. Tente novamente.")
            return redirect('financeiro:criar_fechamento_caixa')

        # 2. Buscar receitas e despesas ABERTAS no período para a igreja
        receitas = Receitas.objects.filter(igreja=igreja_selecionada, data__range=(data_inicio, data_fim), fechado=False)
        despesas = Despesas.objects.filter(
            igreja=igreja_selecionada,
            data__range=(data_inicio, data_fim),
            fechado=False,
            aprovacao_status=Despesas.APROVACAO_APROVADA,
        )
        if fundo_selecionado:
            receitas = receitas.filter(fundo_departamental=fundo_selecionado)
            despesas = despesas.filter(fundo_departamental=fundo_selecionado)

        # 3. Calcular totais
        total_entradas = receitas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        total_saidas = despesas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        saldo_final = total_entradas - total_saidas

        # 4. Criar o registro de Fechamento
        novo_fechamento = FechamentoCaixa.objects.create(
            igreja=igreja_selecionada,
            fundo_departamental=fundo_selecionado,
            data_inicio=data_inicio,
            data_fim=data_fim,
            total_entradas=total_entradas,
            total_saidas=total_saidas,
            saldo_final=saldo_final,
            status='fechado',
            observacoes=observacoes
        )

        # 5. Marcar receitas e despesas como fechadas
        receitas.update(fechado=True)
        despesas.update(fechado=True)

        from comunicacao.services import agendar_agradecimentos_dizimo_fechamento

        resumo_dizimos = agendar_agradecimentos_dizimo_fechamento(fechamento=novo_fechamento)

        mensagem_sucesso = (
            f'Caixa da igreja "{igreja_selecionada.nome_igreja}" fechado com sucesso para o período '
            f'{data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}!'
        )
        if fundo_selecionado:
            mensagem_sucesso = (
                f'Caixa da igreja "{igreja_selecionada.nome_igreja}" no fundo "{fundo_selecionado.nome_exibicao}" '
                f'fechado com sucesso para o período {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}!'
            )
        if resumo_dizimos.get('agendados'):
            mensagem_sucesso += f' {resumo_dizimos["agendados"]} agradecimento(s) de dízimo foram agendados.'
        messages.success(request, mensagem_sucesso)
        return redirect('financeiro:lista_fechamentos_caixa')

    except PermissionDenied as pd:
        messages.error(request, str(pd))
        return redirect('financeiro:criar_fechamento_caixa')
    except Exception as e:
        logger.exception(f"Erro ao finalizar fechamento de caixa para ministério {ministerio.id}")
        messages.error(request, f'Erro ao finalizar fechamento de caixa: {e}')
        # Volta para o início do processo em caso de erro
        return redirect('financeiro:criar_fechamento_caixa')

# --- FIM DA NOVA VIEW ---

# ... (restante das views: detalhe_fechamento_caixa, reabrir_fechamento_caixa, etc.) ...


@page_access_required('financeiro')
def detalhe_fechamento_caixa(request, pk): # noqa: E302
    """ Mostra os detalhes de um fechamento específico. """
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    # Garante que o fechamento pertence às igrejas permitidas
    fechamento = get_object_or_404(FechamentoCaixa, pk=pk, igreja__in=allowed_churches)
    try:
        # Busca as receitas e despesas que FORAM incluídas neste fechamento (fechado=True)
        # Não precisa filtrar por allowed_churches aqui, pois o fechamento já foi validado
        receitas = Receitas.objects.filter(igreja=fechamento.igreja, data__range=(fechamento.data_inicio, fechamento.data_fim), fechado=True)
        despesas = Despesas.objects.filter(igreja=fechamento.igreja, data__range=(fechamento.data_inicio, fechamento.data_fim), fechado=True)
        if fechamento.fundo_departamental_id:
            receitas = receitas.filter(fundo_departamental=fechamento.fundo_departamental)
            despesas = despesas.filter(fundo_departamental=fechamento.fundo_departamental)
        receitas = receitas.select_related('membro')
        despesas = despesas.select_related('categoria')

        # Recalcula totais para garantir consistência (ou usa os valores salvos no fechamento)
        # total_entradas = receitas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        # total_saidas = despesas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        # saldo_final = total_entradas - total_saidas

        # Permissão para reabrir
        can_edit = has_finance_edit_permission(request.user)

        context = {
            'fechamento': fechamento,
            'receitas': receitas,
            'despesas': despesas,
            # Usar os totais salvos no objeto fechamento é mais direto
            'total_entradas': fechamento.total_entradas,
            'total_saidas': fechamento.total_saidas,
            'saldo_final': fechamento.saldo_final,
            'ministerio': ministerio,
            'can_edit_finance': can_edit, # Para o botão Reabrir
        }
        return render(request, 'financeiro/fechamentos/detalhe_fechamento_caixa.html', context)
    except Exception as e:
        logger.exception(f"Erro ao detalhar fechamento {pk} para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao carregar os detalhes do fechamento: {e}")
        return redirect('financeiro:lista_fechamentos_caixa')


@page_access_required('financeiro')
def reabrir_fechamento_caixa(request, pk): # noqa: E302
    """ Reabre um caixa fechado, marcando as receitas/despesas como abertas novamente. """
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    # Garante que o fechamento pertence às igrejas permitidas
    fechamento = get_object_or_404(FechamentoCaixa, pk=pk, igreja__in=allowed_churches)

    if fechamento.status != 'fechado':
        messages.warning(request, "Este caixa não está fechado e não pode ser reaberto.")
        return redirect('financeiro:lista_fechamentos_caixa')

    if request.method == 'POST': # Ação de reabrir deve ser POST
        try:
            # Marcar receitas e despesas como abertas novamente
            Receitas.objects.filter(igreja=fechamento.igreja, data__range=(fechamento.data_inicio, fechamento.data_fim), fechado=True).update(fechado=False)
            Despesas.objects.filter(igreja=fechamento.igreja, data__range=(fechamento.data_inicio, fechamento.data_fim), fechado=True).update(fechado=False)

            # Excluir o registro de fechamento
            data_inicio_str = fechamento.data_inicio.strftime("%d/%m/%Y")
            data_fim_str = fechamento.data_fim.strftime("%d/%m/%Y")
            igreja_nome = fechamento.igreja.nome_igreja
            fechamento.delete()

            messages.success(request, f'Caixa da igreja "{igreja_nome}" ({data_inicio_str} a {data_fim_str}) foi reaberto com sucesso! As transações estão disponíveis para edição.')
            return redirect('financeiro:lista_fechamentos_caixa')
        except Exception as e:
            logger.exception(f"Erro ao reabrir fechamento {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao reabrir o caixa: {e}')
            return redirect('financeiro:detalhe_fechamento_caixa', pk=pk) # Volta para o detalhe em caso de erro
    else:
        # Se GET, mostrar página de confirmação para reabrir
        context = {'fechamento': fechamento, 'ministerio': ministerio}
        return render(request, 'financeiro/fechamentos/confirmar_reabrir_caixa.html', context)


# --- Relatórios ---
@page_access_required('financeiro')
def relatorio_mensal_detalhe(request, pk): # noqa: E302
    """ Gera o relatório formatado de um fechamento de caixa específico. """
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    # Garante que o fechamento pertence às igrejas permitidas
    fechamento = get_object_or_404(FechamentoCaixa, pk=pk, igreja__in=allowed_churches)
    try:
        receitas = Receitas.objects.filter(igreja=fechamento.igreja, data__range=(fechamento.data_inicio, fechamento.data_fim), fechado=True)
        despesas = Despesas.objects.filter(igreja=fechamento.igreja, data__range=(fechamento.data_inicio, fechamento.data_fim), fechado=True).select_related('categoria')

        # Calcular totais de receitas por categoria (mantido como dict, ordem não crítica aqui?)
        totais_receitas_cat = {}
        for choice_val, choice_disp in Receitas.CATEGORIA_CHOICES:
            totais_receitas_cat[choice_disp] = receitas.filter(categoria=choice_val).aggregate(total=Sum('valor'))['total'] or Decimal(0)

        # --- MODIFICAÇÃO PARA DESPESAS ---
        # 1. Buscar categorias ordenadas por ID (pk)
        categorias_despesa_org = CategoriaDespesa.objects.filter(ministerio=ministerio).order_by('pk')

        # 2. Criar uma LISTA de tuplas (nome, total) para preservar a ordem
        totais_despesas_cat_list = [] # Mudar para lista
        for cat_desp in categorias_despesa_org: # Agora itera na ordem de ID
            valor_total = despesas.filter(categoria=cat_desp).aggregate(total=Sum('valor'))['total'] or Decimal(0)
            totais_despesas_cat_list.append((cat_desp.nome, valor_total)) # Adiciona tupla à lista
        # --- FIM DA MODIFICAÇÃO ---

        total_entradas = fechamento.total_entradas
        total_saidas = fechamento.total_saidas
        valor_liquido = fechamento.saldo_final
        valor_liquido_extenso = num2words(valor_liquido, to='currency', lang='pt_BR')

        igreja = fechamento.igreja
        mes_nome = fechamento.data_inicio.strftime("%B").capitalize()
        ano = fechamento.data_inicio.year

        context = {
            'fechamento': fechamento,
            'igreja': igreja,
            'ministerio': ministerio,
            'totais_receitas_cat': totais_receitas_cat,
            # 'totais_despesas_cat': totais_despesas_cat, # Remover o dict antigo
            'totais_despesas_cat_list': totais_despesas_cat_list, # Passar a LISTA nova
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'valor_liquido': valor_liquido,
            'valor_liquido_extenso': valor_liquido_extenso,
            'data_atual': date.today().strftime('%d de %B de %Y'),
            'mes_nome': mes_nome,
            'ano': ano,
        }
        return render(request, 'financeiro/relatorio_mensal.html', context)
    except Exception as e:
        logger.exception(f"Erro ao gerar relatório para fechamento {pk}, ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao gerar o relatório: {e}")
        return redirect('financeiro:lista_fechamentos_caixa')


# ====================================================
# ========= INÍCIO: VIEWS PARA FORNECEDORES =========
# ====================================================

@page_access_required('financeiro')
def lista_fornecedores(request):
    """ Lista os fornecedores do ministério, com filtros. """
    ministerio = get_ministerio_or_error(request)
    try:
        # Fornecedores são ligados diretamente à ministério, não precisam de filtro de igreja
        fornecedores_qs = Fornecedor.objects.filter(ministerio=ministerio).order_by('nome')
        can_edit = has_finance_edit_permission(request.user) # Para botões

        # Filtros GET
        query = request.GET.get('q', '')
        status_ativo = request.GET.get('ativo', 'true') # Default para mostrar ativos

        if query:
            fornecedores_qs = fornecedores_qs.filter(
                Q(nome__icontains=query) |
                Q(cnpj_cpf__icontains=query) |
                Q(email__icontains=query)
            )

        if status_ativo == 'true':
            fornecedores_qs = fornecedores_qs.filter(ativo=True)
            status_selecionado = 'true'
        elif status_ativo == 'false':
            fornecedores_qs = fornecedores_qs.filter(ativo=False)
            status_selecionado = 'false'
        else: # 'todos' ou qualquer outro valor
            status_selecionado = 'todos'
            # Não aplica filtro de ativo

        context = {
            'fornecedores': fornecedores_qs,
            'ministerio': ministerio,
            'current_q': query,
            'current_status_ativo': status_selecionado,
            'can_edit_finance': can_edit,
        }
        return render(request, 'financeiro/fornecedores/lista_fornecedores.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar fornecedores para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao listar os fornecedores: {e}")
        return redirect('financeiro:painel_financeiro') # Redireciona para painel em caso de erro

@page_access_required('financeiro')
def criar_fornecedor(request): # noqa: E302
    """ Cria um novo fornecedor para a ministério. """
    ministerio = get_ministerio_or_error(request)
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            try:
                fornecedor = form.save(commit=False)
                fornecedor.ministerio = ministerio
                fornecedor.ativo = True # Novos fornecedores começam ativos
                fornecedor.save()
                messages.success(request, f'Fornecedor "{fornecedor.nome}" criado com sucesso!')
                return redirect('financeiro:lista_fornecedores')
            except Exception as e:
                # Verifica erro de unicidade (nome duplicado na ministério)
                if 'UNIQUE constraint' in str(e) and 'ministerio_id, nome' in str(e):
                     messages.error(request, f'Erro: Já existe um fornecedor com o nome "{form.cleaned_data.get("nome")}" nesta ministério.')
                else:
                    logger.exception(f"Erro ao salvar novo fornecedor para ministério {ministerio.id}")
                    messages.error(request, f'Erro ao salvar fornecedor: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = FornecedorForm()

    context = {'form': form, 'ministerio': ministerio, 'titulo_pagina': 'Criar Novo Fornecedor'}
    return render(request, 'financeiro/fornecedores/form_fornecedor.html', context)

@page_access_required('financeiro')
def editar_fornecedor(request, pk): # noqa: E302
    """ Edita um fornecedor existente do ministério. """
    ministerio = get_ministerio_or_error(request)
    # Validação de ministério já feita no get_object_or_404
    fornecedor = get_object_or_404(Fornecedor, pk=pk, ministerio=ministerio)

    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Fornecedor "{fornecedor.nome}" atualizado com sucesso!')
                return redirect('financeiro:lista_fornecedores')
            except Exception as e:
                 if 'UNIQUE constraint' in str(e) and 'ministerio_id, nome' in str(e):
                     messages.error(request, f'Erro: Já existe outro fornecedor com o nome "{form.cleaned_data.get("nome")}" nesta ministério.')
                 else:
                    logger.exception(f"Erro ao editar fornecedor {pk} para ministério {ministerio.id}")
                    messages.error(request, f'Erro ao salvar fornecedor: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = FornecedorForm(instance=fornecedor)

    context = {'form': form, 'ministerio': ministerio, 'titulo_pagina': f'Editar Fornecedor: {fornecedor.nome}', 'fornecedor': fornecedor}
    return render(request, 'financeiro/fornecedores/form_fornecedor.html', context)

@page_access_required('financeiro')
def alternar_status_fornecedor(request, pk): # noqa: E302
    """ Ativa ou desativa um fornecedor (requer método POST). """
    ministerio = get_ministerio_or_error(request)
    # Validação de ministério já feita no get_object_or_404
    fornecedor = get_object_or_404(Fornecedor, pk=pk, ministerio=ministerio)

    if request.method == 'POST':
        try:
            fornecedor.ativo = not fornecedor.ativo
            fornecedor.save()
            status_msg = "ativado" if fornecedor.ativo else "desativado"
            messages.success(request, f'Fornecedor "{fornecedor.nome}" foi {status_msg} com sucesso.')
        except Exception as e:
            logger.exception(f"Erro ao alternar status do fornecedor {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao alterar status do fornecedor: {e}')
    else:
        messages.error(request, "Ação inválida (requer POST).")

    # Redireciona de volta para a lista, preservando filtros se possível
    redirect_url = request.META.get('HTTP_REFERER', reverse('financeiro:lista_fornecedores'))
    return redirect(redirect_url)


# ==================================================
# ========= FIM: VIEWS PARA FORNECEDORES =========
# ==================================================

@page_access_required('financeiro')
def editar_categoria_despesa(request, pk): # noqa: E302
    """ Edita uma categoria de despesa existente. """
    ministerio = get_ministerio_or_error(request)
    # Validação de ministério já feita no get_object_or_404
    categoria = get_object_or_404(CategoriaDespesa, pk=pk, ministerio=ministerio)

    if request.method == 'POST':
        # Passa instance=categoria para editar o objeto existente
        form = CategoriaDespesaForm(request.POST, instance=categoria)
        if form.is_valid():
            try:
                form.save() # Salva as alterações
                messages.success(request, f'Categoria "{categoria.nome}" atualizada com sucesso!')
                return redirect('financeiro:lista_categorias_despesa')
            except Exception as e:
                 # Tratar erro de unicidade se o nome for alterado para um já existente
                 if 'UNIQUE constraint' in str(e) and 'ministerio_id, nome' in str(e):
                     messages.error(request, f'Erro: Já existe uma categoria com o nome "{form.cleaned_data.get("nome")}" nesta ministério.')
                 else:
                    logger.exception(f"Erro ao editar categoria {pk} para ministério {ministerio.id}")
                    messages.error(request, f'Erro ao salvar categoria: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        # GET: Exibe o formulário preenchido com os dados da categoria
        form = CategoriaDespesaForm(instance=categoria)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': f'Editar Categoria: {categoria.nome}',
        'categoria': categoria # Passa o objeto para o template, se necessário
    }
    # Reutilizar o template do formulário de cadastro
    return render(request, 'financeiro/categorias/form_categoria.html', context)

@page_access_required('financeiro')
def excluir_categoria_despesa(request, pk): # noqa: E302
    """ Exclui uma categoria de despesa (requer POST e confirmação). """
    ministerio = get_ministerio_or_error(request)
    # Validação de ministério já feita no get_object_or_404
    categoria = get_object_or_404(CategoriaDespesa, pk=pk, ministerio=ministerio)

    # Verificar se a categoria está em uso antes de excluir? (Boa prática)
    # despesas_associadas = Despesas.objects.filter(categoria=categoria).exists()
    # contas_pagar_associadas = ContaPagar.objects.filter(categoria=categoria).exists()
    # if despesas_associadas or contas_pagar_associadas:
    #     messages.error(request, f'Não é possível excluir a categoria "{categoria.nome}", pois ela já está sendo utilizada em lançamentos.')
    #     return redirect('financeiro:lista_categorias_despesa')

    if request.method == 'POST':
        try:
            nome_categoria = categoria.nome
            categoria.delete()
            messages.success(request, f'Categoria "{nome_categoria}" excluída com sucesso!')
        except Exception as e:
            logger.exception(f"Erro ao excluir categoria {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao excluir categoria: {e}')
        return redirect('financeiro:lista_categorias_despesa')
    else:
        # GET: Mostrar página de confirmação
        context = {'categoria': categoria, 'ministerio': ministerio}
        return render(request, 'financeiro/categorias/confirmar_excluir_categoria.html', context)


# ====================================================
# ========= INÍCIO: VIEWS PARA CONTAS A PAGAR =========
# ====================================================

@page_access_required('financeiro')
def lista_contas_pagar(request): # noqa: E302
    """ Lista as contas a pagar do ministério, com filtros. """
    ministerio = get_ministerio_or_error(request)
    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    
    try:
        allowed_churches = get_allowed_churches_for_user(request.user) # Base de igrejas permitidas
        igreja_contexto_filtro_dados = None # Igreja que efetivamente filtrará os dados principais
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_contexto_filtro_dados = request.igreja_ativa
            contas_qs = ContaPagar.objects.filter(ministerio=ministerio, igreja=request.igreja_ativa).select_related(
                'igreja', 'fornecedor', 'categoria', 'conta_debito').order_by('data_vencimento', 'status')
        else:        
             # Se nenhuma igreja ativa globalmente, começa com todas as permitidas
            contas_qs = ContaPagar.objects.filter(ministerio=ministerio, igreja__in=allowed_churches).select_related(
                'igreja', 'fornecedor', 'categoria', 'conta_debito'
            ).order_by('data_vencimento', 'status')

        # --- Filtros GET ---
        query = request.GET.get('q', '')
        status_filtro = request.GET.get('status', 'PEN') # Default para Pendente
        venc_inicio = request.GET.get('venc_inicio', '')
        venc_fim = request.GET.get('venc_fim', '')
        igreja_id = request.GET.get('igreja', '')
        fornecedor_id_get = request.GET.get('fornecedor', '')
        tipo_filtro = request.GET.get('tipo', 'TODOS')
        competencia_filtro = request.GET.get('competencia', '')
        gerada_auto_filtro = request.GET.get('gerada_auto', 'TODOS')
        caixa_id_filtro = request.GET.get('caixa_filtro', '')

        if query:
            contas_qs = contas_qs.filter(
                Q(descricao__icontains=query) |
                Q(numero_documento__icontains=query) |
                Q(fornecedor__nome__icontains=query) # Filtrar pelo nome do fornecedor
            )
        if status_filtro and status_filtro != 'TODOS': # Adicionado 'TODOS'
            contas_qs = contas_qs.filter(status=status_filtro)
        if venc_inicio:
            contas_qs = contas_qs.filter(data_vencimento__gte=venc_inicio)
        if venc_fim:
            contas_qs = contas_qs.filter(data_vencimento__lte=venc_fim)
        if igreja_id:

            # Este filtro só deve ser aplicado se request.igreja_ativa NÃO estiver definida
            if not request.igreja_ativa and (is_admin_org(request.user) or allowed_churches.filter(pk=igreja_id).exists()):
                contas_qs = contas_qs.filter(igreja_id=igreja_id)
                try: # Tenta definir o contexto de dados se um filtro GET de igreja foi aplicado
                    igreja_contexto_filtro_dados = allowed_churches.get(pk=igreja_id)
                except Igreja.DoesNotExist:
                    pass # Mantém igreja_contexto_filtro_dados como None ou o valor de request.igreja_ativa

        if fornecedor_id_get:
            contas_qs = contas_qs.filter(fornecedor_id=fornecedor_id_get)

        if caixa_id_filtro:
            contas_qs = contas_qs.filter(conta_debito_id=caixa_id_filtro)

        if tipo_filtro == 'FIXA':
            contas_qs = contas_qs.filter(recorrencia_origem__isnull=False)
        elif tipo_filtro == 'AVULSA':
            contas_qs = contas_qs.filter(recorrencia_origem__isnull=True)

        if competencia_filtro:
            contas_qs = contas_qs.filter(competencia=competencia_filtro)

        if gerada_auto_filtro == 'SIM':
            contas_qs = contas_qs.filter(criado_automaticamente=True)
        elif gerada_auto_filtro == 'NAO':
            contas_qs = contas_qs.filter(criado_automaticamente=False)

        # Opcional: Atualizar status para VENCIDA (pode impactar performance)
        # hoje = timezone.now().date()
        # ContaPagar.objects.filter(
        #     ministerio=ministerio, status='PEN', data_vencimento__lt=hoje
        # ).update(status='VEN')

        # Para os filtros no template
        # --- Lógica para o dropdown de filtro de igreja no template ---
        

        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igrejas_para_filtro_template = Igreja.objects.filter(pk=request.igreja_ativa.pk)
            igreja_id_selecionada_template = str(request.igreja_ativa.pk)
        else:
            igrejas_para_filtro_template = allowed_churches
            igreja_id_selecionada_template = igreja_id # O que foi passado no GET
        
        
        
        fornecedores_org = Fornecedor.objects.filter(ministerio=ministerio, ativo=True)

        # Permissão para criar/pagar
        can_edit = has_finance_edit_permission(request.user)
        can_pay_batch = bool(can_edit and request.igreja_ativa and request.igreja_ativa in allowed_churches)
        contas_bancarias_lote = ContaBancaria.objects.none()
        if can_pay_batch:
            contas_bancarias_lote = ContaBancaria.objects.filter(
                igreja=request.igreja_ativa
            ).order_by('nome_identificacao')

        context = {
            'contas': contas_qs,
            'ministerio': ministerio,
            'status_choices': ContaPagar.STATUS_CHOICES,
            'igrejas_org': igrejas_para_filtro_template, # Usar a lista ajustada
            'fornecedores_org': fornecedores_org,
            # Passar filtros atuais de volta
            'current_q': query,
            'current_status': status_filtro,
            'current_venc_inicio': venc_inicio,
            'current_venc_fim': venc_fim,
            'current_igreja': igreja_id_selecionada_template, # ID para o select do filtro da página
            'current_fornecedor': fornecedor_id_get,
            'current_tipo': tipo_filtro,
            'current_competencia': competencia_filtro,
            'current_gerada_auto': gerada_auto_filtro,
            'current_caixa_filtro': caixa_id_filtro,
            'can_edit_finance': can_edit,
            'can_pay_batch': can_pay_batch,
            'contas_bancarias_lote': contas_bancarias_lote,
            'forma_pagamento_choices': ContaPagar.FORMA_PAGAMENTO_CHOICES,
            'data_pagamento_lote_padrao': now().date().isoformat(),
        }
        return render(request, 'financeiro/contas_pagar/lista_contas_pagar.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar contas a pagar para ministério {ministerio.id}")
        messages.error(request, f"Ocorreu um erro ao listar as contas a pagar: {e}")
        return redirect('financeiro:painel_financeiro')


@page_access_required('financeiro')
def gerar_despesas_fixas_mes(request):
    """Executa manualmente a geração de contas fixas para a competência atual."""
    if request.method != 'POST':
        messages.error(request, 'Ação inválida (requer POST).')
        return redirect('financeiro:lista_contas_pagar')

    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para gerar despesas fixas manualmente.')

    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)

    igreja_id = None
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        igreja_id = request.igreja_ativa.id
    elif allowed_churches.count() == 1:
        igreja_id = allowed_churches.first().id
    else:
        messages.warning(
            request,
            'Selecione uma igreja ativa antes de gerar despesas fixas manualmente.',
        )
        return redirect('financeiro:lista_contas_pagar')

    service = RecorrenciaContaPagarService()
    resultado = service.gerar_competencia(
        ministerio_id=ministerio.id,
        igreja_id=igreja_id,
        dry_run=False,
    )

    if resultado.get('total_erros', 0):
        messages.warning(
            request,
            (
                f"Geração concluída com alertas. Competência {resultado['competencia']}: "
                f"geradas={resultado['total_geradas']}, existentes={resultado['total_existentes']}, "
                f"ignoradas={resultado['total_ignoradas']}, erros={resultado['total_erros']}."
            ),
        )
    else:
        messages.success(
            request,
            (
                f"Geração concluída. Competência {resultado['competencia']}: "
                f"geradas={resultado['total_geradas']}, existentes={resultado['total_existentes']}, "
                f"ignoradas={resultado['total_ignoradas']}."
            ),
        )

    return redirect('financeiro:lista_contas_pagar')


@page_access_required('financeiro')
def lista_recorrencias_contas_pagar(request):
    """Lista templates de despesas fixas com filtros básicos."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    igreja_id = request.GET.get('igreja', '')
    ativo = request.GET.get('ativo', 'SIM')

    recorrencias = RecorrenciaContaPagar.objects.filter(
        ministerio=ministerio,
        igreja__in=allowed_churches,
    ).select_related('igreja', 'fornecedor', 'categoria', 'conta_debito_padrao').order_by(
        'igreja__nome_igreja', 'descricao'
    )

    if igreja_id:
        recorrencias = recorrencias.filter(igreja_id=igreja_id)
    if ativo == 'SIM':
        recorrencias = recorrencias.filter(ativo=True)
    elif ativo == 'NAO':
        recorrencias = recorrencias.filter(ativo=False)

    context = {
        'ministerio': ministerio,
        'recorrencias': recorrencias,
        'igrejas_org': allowed_churches,
        'current_igreja': igreja_id,
        'current_ativo': ativo,
        'can_edit_finance': has_finance_edit_permission(request.user),
    }
    return render(request, 'financeiro/recorrencias_contas_pagar/lista_recorrencias.html', context)


@page_access_required('financeiro')
def criar_recorrencia_conta_pagar(request):
    """Cria um template de despesa fixa recorrente."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)

    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para criar recorrências.')

    if not request.igreja_ativa or request.igreja_ativa not in allowed_churches:
        messages.warning(request, 'Selecione uma igreja ativa para cadastrar despesa fixa.')
        return redirect('financeiro:lista_recorrencias_contas_pagar')

    if request.method == 'POST':
        form = RecorrenciaContaPagarForm(
            request.POST,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_selecionada_inicial=request.igreja_ativa,
        )
        if form.is_valid():
            recorrencia = form.save(commit=False)
            recorrencia.ministerio = ministerio
            recorrencia.usuario_criacao = request.user
            recorrencia.igreja = request.igreja_ativa
            recorrencia.save()
            messages.success(request, 'Recorrência de conta a pagar criada com sucesso!')
            return redirect('financeiro:lista_recorrencias_contas_pagar')
        messages.error(request, 'Formulário inválido. Verifique os campos.')
    else:
        form = RecorrenciaContaPagarForm(
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_selecionada_inicial=request.igreja_ativa,
        )

    return render(
        request,
        'financeiro/recorrencias_contas_pagar/form_recorrencia.html',
        {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': 'Nova Recorrência de Despesa Fixa',
            'ocultar_campo_igreja': True,
        },
    )


@page_access_required('financeiro')
def editar_recorrencia_conta_pagar(request, pk):
    """Edita um template de despesa fixa recorrente."""
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)

    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para editar recorrências.')
    if not request.igreja_ativa or request.igreja_ativa not in allowed_churches:
        messages.warning(request, 'Selecione uma igreja ativa para editar despesa fixa.')
        return redirect('financeiro:lista_recorrencias_contas_pagar')

    recorrencia = get_object_or_404(
        RecorrenciaContaPagar,
        pk=pk,
        ministerio=ministerio,
        igreja=request.igreja_ativa,
    )

    if request.method == 'POST':
        form = RecorrenciaContaPagarForm(
            request.POST,
            instance=recorrencia,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_selecionada_inicial=request.igreja_ativa,
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Recorrência atualizada com sucesso!')
            return redirect('financeiro:lista_recorrencias_contas_pagar')
        messages.error(request, 'Formulário inválido. Verifique os campos.')
    else:
        form = RecorrenciaContaPagarForm(
            instance=recorrencia,
            ministerio=ministerio,
            user=request.user,
            allowed_churches=allowed_churches,
            igreja_selecionada_inicial=request.igreja_ativa,
        )

    return render(
        request,
        'financeiro/recorrencias_contas_pagar/form_recorrencia.html',
        {
            'form': form,
            'ministerio': ministerio,
            'recorrencia': recorrencia,
            'titulo_pagina': f'Editar Recorrência: {recorrencia.descricao}',
            'ocultar_campo_igreja': True,
        },
    )


@page_access_required('financeiro')
def alternar_status_recorrencia_conta_pagar(request, pk):
    """Alterna status ativo/inativo da recorrência (POST)."""
    if request.method != 'POST':
        messages.error(request, 'Ação inválida (requer POST).')
        return redirect('financeiro:lista_recorrencias_contas_pagar')

    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para alterar status de recorrências.')

    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    recorrencia = get_object_or_404(
        RecorrenciaContaPagar,
        pk=pk,
        ministerio=ministerio,
        igreja__in=allowed_churches,
    )

    recorrencia.ativo = not recorrencia.ativo
    recorrencia.save(update_fields=['ativo', 'data_atualizacao'])
    messages.success(request, f'Recorrência "{recorrencia.descricao}" atualizada com sucesso.')
    return redirect('financeiro:lista_recorrencias_contas_pagar')

@page_access_required('financeiro')
def criar_conta_pagar(request): # noqa: E302
    """ Cria uma nova conta a pagar (ou uma parcela). """
    ministerio = get_ministerio_or_error(request)
    igreja_padrao_para_form = None # Inicializa

    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para criar contas a pagar.')

    allowed_churches = get_finance_write_scope(request.user, ministerio)

    if not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar contas a pagar ou não está associado a nenhuma igreja específica.")
        return redirect('financeiro:lista_contas_pagar')

    if request.method == 'POST': # O form já valida se a igreja selecionada é permitida
        form = ContaPagarForm(request.POST,
                              ministerio=ministerio,
                              allowed_churches=allowed_churches,
                              user=request.user, # Passar o usuário
                              igreja_selecionada_inicial=request.igreja_ativa) # Passar igreja ativa
        if form.is_valid():
            try:
                conta = form.save(commit=False)
                conta.ministerio = ministerio
                conta.usuario_criacao = request.user
                # Se o campo igreja foi desabilitado e uma igreja ativa foi passada, usar a igreja ativa
                if form.fields['igreja'].disabled and request.igreja_ativa:
                    conta.igreja = request.igreja_ativa

                
                conta.status = 'PEN' # Garante que começa como Pendente

                # Validações extras
                if conta.igreja not in allowed_churches: raise ValidationError("Igreja inválida")
                if conta.fornecedor.ministerio != ministerio: raise ValidationError("Fornecedor inválido")
                if conta.categoria and conta.categoria.ministerio != ministerio: raise ValidationError("Categoria inválida")

                create_payable(
                    ministerio=conta.ministerio,
                    igreja=conta.igreja,
                    fornecedor=conta.fornecedor,
                    categoria=conta.categoria,
                    descricao=conta.descricao,
                    numero_documento=conta.numero_documento,
                    valor=conta.valor,
                    data_emissao=conta.data_emissao,
                    data_vencimento=conta.data_vencimento,
                    conta_debito=conta.conta_debito,
                    forma_pagamento=conta.forma_pagamento,
                    observacoes=conta.observacoes,
                    usuario_criacao=conta.usuario_criacao,
                    actor=request.user,
                )
                messages.success(request, "Conta a pagar criada com sucesso!")
                # Redirecionar para lista ou para adicionar outra? Por enquanto, lista.
                return redirect('financeiro:lista_contas_pagar')
            except ValidationError as ve: # Captura erros de validação específicos
                 messages.error(request, f"Erro de validação: {ve}")
            except Exception as e:
                logger.exception(f"Erro ao salvar nova conta a pagar para ministério {ministerio.id}")
                messages.error(request, f"Erro ao salvar conta a pagar: {e}")
        else:
            messages.error(request, "Formulário inválido. Verifique os campos.")
    else:
        initial_form_data = {} # Dicionário para passar valores iniciais
        igreja_para_form_get = None # Variável para a igreja que será usada no form
        # --- Lógica para pré-selecionar a igreja no formulário GET ---
        # A pré-seleção agora é feita no __init__ do form ao passar igreja_selecionada_inicial
        # Mas podemos manter a lógica de initial_form_data para outros campos se necessário.
        # O importante é passar igreja_selecionada_inicial para o form.
        if request.igreja_ativa and request.igreja_ativa in allowed_churches: # Mantido para clareza, mas o form usa igreja_selecionada_inicial
            initial_form_data['igreja'] = request.igreja_ativa
            igreja_para_form_get = request.igreja_ativa
        elif allowed_churches.count() == 1:
            igreja_unica_permitida = allowed_churches.first()
            initial_form_data['igreja'] = igreja_unica_permitida
            igreja_para_form_get = igreja_unica_permitida # Adicionar esta linha

        form = ContaPagarForm(initial=initial_form_data, 
                              ministerio=ministerio,
                              allowed_churches=allowed_churches,
                              user=request.user, # Adicionar user
                              igreja_selecionada_inicial=igreja_para_form_get) # Usar igreja_para_form_get

    context = {        
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Criar Nova Conta a Pagar / Parcela'
    }
    return render(request, 'financeiro/contas_pagar/form_conta_pagar.html', context)

@page_access_required('financeiro')
def registrar_pagamento_conta_pagar(request, pk): # noqa: E302
    """ Registra o pagamento de uma conta a pagar específica. """
    ministerio = get_ministerio_or_error(request)
    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para registrar pagamentos.')

    allowed_churches = get_finance_write_scope(request.user, ministerio)
    # Permite pagar apenas contas Pendentes ou Vencidas E que pertençam às igrejas permitidas
    conta = get_object_or_404(ContaPagar, pk=pk, ministerio=ministerio, status__in=['PEN', 'VEN'], igreja__in=allowed_churches)

    # Envolver em uma transação atômica para garantir consistência
    if request.method == 'POST':
        # Passa instance=conta para o form saber qual conta está sendo paga
        # O form já filtra a conta_debito pela ministério
        form = RegistrarPagamentoContaPagarForm(request.POST, request.FILES, instance=conta, ministerio=ministerio) # Passa ministerio
        if form.is_valid():
            try:
                with transaction.atomic(): # Garante que ou tudo funciona ou nada é salvo
                    conta_paga = get_object_or_404(
                        ContaPagar.objects.select_for_update(),
                        pk=pk,
                        ministerio=ministerio,
                        status__in=['PEN', 'VEN'],
                        igreja__in=allowed_churches,
                    )
                    conta_paga.data_pagamento = form.cleaned_data['data_pagamento']
                    conta_paga.valor_pago = form.cleaned_data['valor_pago']
                    conta_paga.juros_multa = form.cleaned_data['juros_multa']
                    conta_paga.desconto = form.cleaned_data['desconto']
                    conta_paga.conta_debito = form.cleaned_data['conta_debito']
                    conta_paga.forma_pagamento = form.cleaned_data['forma_pagamento']
                    conta_paga.comprovante = form.cleaned_data['comprovante']
                    conta_paga.status = 'PAG'

                    # Validação extra da conta de débito (form já deve ter filtrado)
                    if conta_paga.conta_debito and conta_paga.conta_debito.igreja.ministerio != ministerio:
                        raise ValidationError("Conta de débito selecionada inválida.")

                    # Salva a ContaPagar com status 'PAG' e dados do pagamento
                    conta_paga.save()

                    _criar_despesa_por_conta_paga(conta_paga, request.user)
    

                    messages.success(request, f"Pagamento da conta '{conta.descricao}' registrado com sucesso!")
                    return redirect('financeiro:lista_contas_pagar')

            except Http404:
                 raise
            except ValidationError as ve:
                 messages.error(request, f"Erro de validação: {ve}")
            except Exception as e:
                 logger.exception(f"Erro ao registrar pagamento da conta {pk} para ministério {ministerio.id}")
                 logger.error(f"Erro ao registrar pagamento da conta {pk} para ministério {ministerio.id}: {e}\n{traceback.format_exc()}")
                 messages.error(request, f"Erro ao registrar pagamento: {e}")
        else:
            messages.error(request, "Formulário de pagamento inválido. Verifique os campos.")
    else:
        # GET: Exibe o formulário preenchido com sugestões
        # Passa a ministério para filtrar conta_debito
        form = RegistrarPagamentoContaPagarForm(instance=conta, ministerio=ministerio)
    # Verifica se o campo conta_debito tem opções disponíveis
    # Se o queryset estiver vazio, significa que não há contas bancárias cadastradas para a ministério
    if not form.fields['conta_debito'].queryset.exists():
        messages.warning(request, "Não há contas bancárias/caixas cadastradas para a seu ministério. Cadastre uma conta para registrar pagamentos.")
        # Opcional: Redirecionar para a página de cadastro de contas bancárias se ela existir
    context = {
        'form': form,
        'conta': conta, # Passa a conta para exibir detalhes no template
        'ministerio': ministerio,
        'titulo_pagina': f"Registrar Pagamento: {conta.descricao}"
    }
    return render(request, 'financeiro/contas_pagar/form_registrar_pagamento.html', context)


def _criar_despesa_por_conta_paga(conta_paga, user):
    """Cria a despesa espelho para uma conta já marcada como paga."""
    if conta_paga.status != 'PAG' or conta_paga.valor_pago is None:
        return

    valor_efetivo_despesa = conta_paga.valor_pago
    if conta_paga.juros_multa:
        valor_efetivo_despesa += conta_paga.juros_multa
    if conta_paga.desconto:
        valor_efetivo_despesa -= conta_paga.desconto

    Despesas.objects.create(
        igreja=conta_paga.igreja,
        data=conta_paga.data_pagamento,
        descricao=f"Pagamento: {conta_paga.descricao}",
        valor=valor_efetivo_despesa,
        categoria=conta_paga.categoria,
        observacao=f"Pagamento referente à conta a pagar ID {conta_paga.pk}. {conta_paga.observacoes or ''}".strip(),
        fechado=False,
        conta_bancaria=conta_paga.conta_debito,
        origem_conta_pagar=conta_paga,
        usuario_registro_pagamento=user,
        criado_por=user,
    )
    logger.info(f"Despesa criada automaticamente para a ContaPagar ID {conta_paga.pk}.")


@page_access_required('financeiro')
def registrar_pagamento_lote_contas_pagar(request):
    """Registra o pagamento em lote de contas pendentes/vencidas da igreja ativa."""
    if request.method != 'POST':
        messages.error(request, 'Ação inválida (requer POST).')
        return redirect('financeiro:lista_contas_pagar')

    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para registrar pagamentos em lote.')

    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_finance_write_scope(request.user, ministerio)

    if not request.igreja_ativa or request.igreja_ativa not in allowed_churches:
        messages.warning(request, 'Selecione uma igreja ativa para realizar pagamento em lote.')
        return redirect('financeiro:lista_contas_pagar')

    contas_ids_raw = request.POST.getlist('conta_ids')
    if not contas_ids_raw:
        messages.warning(request, 'Selecione ao menos uma conta para pagamento em lote.')
        return redirect('financeiro:lista_contas_pagar')

    try:
        contas_ids = list({int(conta_id) for conta_id in contas_ids_raw})
    except (TypeError, ValueError):
        messages.error(request, 'Lista de contas inválida para pagamento em lote.')
        return redirect('financeiro:lista_contas_pagar')

    data_pagamento_raw = request.POST.get('data_pagamento_lote')
    conta_debito_id = request.POST.get('conta_debito_lote')
    forma_pagamento = request.POST.get('forma_pagamento_lote')

    if not data_pagamento_raw or not conta_debito_id or not forma_pagamento:
        messages.error(request, 'Preencha data, conta/caixa de débito e forma de pagamento para o lote.')
        return redirect('financeiro:lista_contas_pagar')

    try:
        data_pagamento = datetime.strptime(data_pagamento_raw, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Data de pagamento inválida para o lote.')
        return redirect('financeiro:lista_contas_pagar')

    if forma_pagamento not in dict(ContaPagar.FORMA_PAGAMENTO_CHOICES):
        messages.error(request, 'Forma de pagamento inválida para o lote.')
        return redirect('financeiro:lista_contas_pagar')

    conta_debito = get_object_or_404(
        ContaBancaria,
        pk=conta_debito_id,
        igreja=request.igreja_ativa,
    )

    contas = ContaPagar.objects.filter(
        pk__in=contas_ids,
        ministerio=ministerio,
        igreja=request.igreja_ativa,
        status__in=['PEN', 'VEN'],
    ).select_related('categoria', 'igreja')

    if not contas.exists():
        messages.warning(request, 'Nenhuma conta elegível para pagamento em lote foi encontrada.')
        return redirect('financeiro:lista_contas_pagar')

    total_pagamentos = 0
    total_erros = 0

    for conta in contas:
        try:
            with transaction.atomic():
                conta_paga = ContaPagar.objects.select_for_update().get(
                    pk=conta.pk,
                    ministerio=ministerio,
                    igreja=request.igreja_ativa,
                    status__in=['PEN', 'VEN'],
                )
                conta_paga.data_pagamento = data_pagamento
                conta_paga.valor_pago = conta_paga.valor
                conta_paga.juros_multa = Decimal('0.00')
                conta_paga.desconto = Decimal('0.00')
                conta_paga.conta_debito = conta_debito
                conta_paga.forma_pagamento = forma_pagamento
                conta_paga.status = 'PAG'
                conta_paga.save()

                _criar_despesa_por_conta_paga(conta_paga, request.user)
                total_pagamentos += 1
        except Exception:
            total_erros += 1
            logger.exception(
                f"Erro ao registrar pagamento em lote da conta {conta.pk} para ministério {ministerio.id}"
            )

    if total_pagamentos:
        messages.success(
            request,
            f'Pagamento em lote concluído: {total_pagamentos} conta(s) paga(s).',
        )

    if total_erros:
        messages.warning(
            request,
            f'Pagamento em lote finalizado com {total_erros} erro(s). Verifique os logs.',
        )

    return redirect('financeiro:lista_contas_pagar')

# ==================================================
# ========= FIM: VIEWS PARA CONTAS A PAGAR =========
# ==================================================


# financeiro/views.py
# ... (imports e views existentes) ...

# ====================================================
# ========= CONTINUAÇÃO: VIEWS PARA CONTAS A PAGAR =========
# ====================================================

@page_access_required('financeiro')
def editar_conta_pagar(request, pk): # noqa: E302
    """ Edita uma conta a pagar existente (se ainda não estiver paga ou cancelada). """
    ministerio = get_ministerio_or_error(request)
    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para editar contas a pagar.')

    allowed_churches = get_finance_write_scope(request.user, ministerio)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                locked_payable = get_object_or_404(
                    ContaPagar.objects.select_for_update(),
                    pk=pk,
                    ministerio=ministerio,
                    status__in=['PEN', 'VEN'],
                )
                conta = locked_payable
                allowed_churches = get_finance_write_scope(request.user, ministerio)
                get_object_or_404(allowed_churches, pk=locked_payable.igreja_id)
                before = build_payable_authorization_edit_snapshot(locked_payable)
                financial_status_before = locked_payable.status
                form = ContaPagarForm(
                    request.POST,
                    instance=locked_payable,
                    ministerio=ministerio,
                    user=request.user,
                    allowed_churches=allowed_churches,
                )
                if form.is_valid():
                    payable = form.save(commit=False)
                    if not allowed_churches.filter(pk=payable.igreja_id).exists():
                        raise ValidationError('Igreja inválida')
                    _validate_payable_domain_integrity(payable)

                    after_material_fingerprint = compute_payable_material_fingerprint_v1(
                        build_payable_material_snapshot_v1(payable),
                    )
                    material_changed = before.material_fingerprint != after_material_fingerprint

                    if material_changed:
                        policy = _resolve_locked_payable_policy(payable.igreja)
                        plan = plan_payable_authorization_after_edit(
                            payable=payable,
                            before=before,
                            policy=policy,
                        )
                        _validate_payable_historical_decision_evidence_before_edit(
                            payable=payable,
                            before=before,
                            plan=plan,
                        )
                        apply_payable_authorization_edit_plan(payable, plan)
                    else:
                        policy = None
                        plan = plan_payable_authorization_after_edit(
                            payable=payable,
                            before=before,
                            policy=None,
                        )
                        refresh_payable_material_fingerprint(payable)

                    payable.full_clean()
                    payable.save()
                    if plan.material_changed:
                        _materialize_payable_edit_authorization_events(
                            payable=payable,
                            before=before,
                            plan=plan,
                            policy=policy,
                            actor=request.user,
                            financial_status_before=financial_status_before,
                            financial_status_after=payable.status,
                        )
                    conta = payable
                    messages.success(request, f'Conta a pagar \"{conta.descricao}\" atualizada com sucesso!')
                    return redirect('financeiro:lista_contas_pagar')
                messages.error(request, 'Por favor, corrija os erros no formulário.')
        except Http404:
            raise
        except ValidationError as ve:
            messages.error(request, f"Erro de validação: {ve}")
        except Exception as e:
            logger.exception(f"Erro ao editar conta a pagar {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao salvar conta a pagar: {e}')
    else:
        # GET: Exibe o formulário preenchido
        conta = get_object_or_404(
            ContaPagar,
            pk=pk,
            ministerio=ministerio,
            status__in=['PEN', 'VEN'],
            igreja__in=allowed_churches,
        )
        form = ContaPagarForm(instance=conta, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': f'Editar Conta: {conta.descricao}',
        'conta': conta # Passa o objeto para o template
    }
    # Reutiliza o mesmo template do formulário de criação
    return render(request, 'financeiro/contas_pagar/form_conta_pagar.html', context)

@page_access_required('financeiro')
def detalhe_conta_pagar(request, pk): # noqa: E302
    """ Exibe os detalhes completos de uma conta a pagar. """
    ministerio = get_ministerio_or_error(request)
    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    allowed_churches = get_allowed_churches_for_user(request.user)
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        # Se uma igreja ativa está selecionada, garante que a conta pertence a ela
        conta = get_object_or_404(ContaPagar, pk=pk, ministerio=ministerio, igreja=request.igreja_ativa)
    else:    
        # Garante que a conta pertence às igrejas permitidas
        conta = get_object_or_404(ContaPagar, pk=pk, ministerio=ministerio, igreja__in=allowed_churches)
    # Usar select_related para otimizar

    conta = ContaPagar.objects.select_related(
        # Re-busca com select_related após garantir a permissão
        'igreja', 'fornecedor', 'categoria', 'conta_debito', 'usuario_criacao'
    ).get(pk=pk, ministerio=ministerio) # A permissão já foi verificada acima

    # Permissão para editar/pagar/cancelar
    can_edit = has_finance_edit_permission(request.user)

    context = {
        'conta': conta,
        'ministerio': ministerio,
        'can_edit_finance': can_edit, # Passa para o template
    }
    return render(request, 'financeiro/contas_pagar/detalhe_conta_pagar.html', context)

@page_access_required('financeiro')
def cancelar_conta_pagar(request, pk): # noqa: E302
    """ Marca uma conta a pagar como Cancelada (requer POST). """
    ministerio = get_ministerio_or_error(request)
    if not has_finance_edit_permission(request.user):
        raise PermissionDenied('Você não tem permissão para cancelar contas a pagar.')

    allowed_churches = get_finance_write_scope(request.user, ministerio)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                conta = get_object_or_404(
                    ContaPagar.objects.select_for_update(),
                    pk=pk,
                    ministerio=ministerio,
                    status__in=['PEN', 'VEN'],
                )
                allowed_churches = get_finance_write_scope(request.user, ministerio)
                get_object_or_404(allowed_churches, pk=conta.igreja_id)
                conta.status = 'CAN'
                conta.save(update_fields=['status', 'data_atualizacao']) # Atualiza só os campos necessários
            messages.success(request, f'Conta a pagar "{conta.descricao}" cancelada com sucesso.')
        except Http404:
            raise
        except Exception as e:
            logger.exception(f"Erro ao cancelar conta a pagar {pk} para ministério {ministerio.id}")
            messages.error(request, f'Erro ao cancelar a conta: {e}')
        return redirect('financeiro:lista_contas_pagar')
    else:
        # GET não deve cancelar, pode mostrar confirmação ou redirecionar
        messages.error(request, "Ação inválida (requer POST).")
        return redirect('financeiro:lista_contas_pagar')

# ==================================================
# ========= FIM: VIEWS PARA CONTAS A PAGAR =========
# ==================================================
@page_access_required('lideranca_financeira')
def painel_lideranca_financeiro(request):
    ministerio_usuario = get_ministerio_or_error(request)
    allowed_churches_base_financeiro = get_allowed_churches_for_user(request.user)

    # print(f"DEBUG (Financeiro): Usuário: {request.user.username}, É Líder Financeiro: {is_finance_leader(request.user)}") # Removido para produção
    # print(f"DEBUG (Financeiro): allowed_churches_base_financeiro: {list(allowed_churches_base_financeiro)}") # Removido para produção

    if not allowed_churches_base_financeiro.exists() and not is_admin_org(request.user):
        messages.warning(request, "Nenhuma igreja encontrada para visualização no painel de liderança financeira.")
        return render(request, 'financeiro/painel_lideranca_financeiro.html', {
            'nenhuma_igreja_permissao': True,
            'ministerio_usuario': ministerio_usuario,
            'titulo_dashboard': f"Liderança Financeira - {ministerio_usuario.nome_fantasia}"
        })

    try:
        churches_for_queries = None
        igreja_em_foco_obj = None # Objeto da igreja que está em foco (pode ser do global ou do filtro da página)
        ver_apenas_entidade_foco = False # True se formos ver SÓ a igreja_em_foco_obj, sem descendentes
        
        # Título do escopo da igreja (será definido abaixo)
        titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}" 
        # Opções para o dropdown de filtro na página
        opcoes_filtro_pagina = allowed_churches_base_financeiro.order_by('nome_igreja')
        # ID selecionado no filtro da página (vem do GET, ou será definido)
        id_selecionado_filtro_pagina = request.GET.get('igreja_filtro', '')

        # --- Lógica principal de determinação do escopo ---
        if request.igreja_ativa and request.igreja_ativa in allowed_churches_base_financeiro:
            # 1. Igreja global está ativa e permitida
            igreja_em_foco_obj = request.igreja_ativa
            # Dropdown da página mostra a igreja_ativa e suas descendentes permitidas
            temp_pks_dropdown = {request.igreja_ativa.pk}
            if hasattr(request.igreja_ativa, 'get_descendants'):
                desc_dropdown_qs = request.igreja_ativa.get_descendants(include_self=False).filter(
                    pk__in=allowed_churches_base_financeiro.values_list('pk', flat=True)
                )
                if desc_dropdown_qs.exists():
                    temp_pks_dropdown.update(desc_dropdown_qs.values_list('pk', flat=True))
            opcoes_filtro_pagina = Igreja.objects.filter(pk__in=list(temp_pks_dropdown)).order_by('nome_igreja')

            # Se o filtro da página não foi usado (value=''), ou se é igual à igreja global
            if not id_selecionado_filtro_pagina or id_selecionado_filtro_pagina == str(request.igreja_ativa.pk):
                id_selecionado_filtro_pagina = str(request.igreja_ativa.pk)

                igreja_em_foco_obj = request.igreja_ativa # Confirma o foco
                # Se o filtro da página é explicitamente a igreja global (e não "Toda Rede DENTRO dela")
                # E essa igreja global tem descendentes, então o usuário quer ver SÓ a entidade global.
                if request.GET.get('igreja_filtro') == str(request.igreja_ativa.pk) and \
                   hasattr(request.igreja_ativa, 'get_descendants') and \
                   request.igreja_ativa.get_descendants(include_self=False).filter(pk__in=allowed_churches_base_financeiro.values_list('pk', flat=True)).exists():
                    ver_apenas_entidade_foco = True # Ver apenas a Regional/Sede
                    titulo_escopo_igreja = f"Apenas: {request.igreja_ativa.nome_igreja}" 
                else: # É uma folha ou não tem descendentes permitidas, ou o usuário quer a rede
                    ver_apenas_entidade_foco = False # Mostra a rede (que será só ela se for folha)
                    titulo_escopo_igreja = f"Rede: {request.igreja_ativa.nome_igreja}" if len(temp_pks_dropdown) > 1 else f"Igreja: {request.igreja_ativa.nome_igreja}"

            else: # Filtro da página selecionou uma descendente específica da igreja global
                try:
                    igreja_descendente_selecionada = opcoes_filtro_pagina.get(pk=id_selecionado_filtro_pagina)
                    igreja_em_foco_obj = igreja_descendente_selecionada
                    # Se a descendente selecionada tem sub-igrejas dentro das permitidas, mostrar rede
                    desc_da_selecionada = igreja_descendente_selecionada.get_descendants(include_self=False).filter(
                        pk__in=allowed_churches_base_financeiro.values_list('pk', flat=True)
                    )
                    if desc_da_selecionada.exists():
                        ver_apenas_entidade_foco = False
                        titulo_escopo_igreja = f"Rede: {igreja_descendente_selecionada.nome_igreja}"
                    else:
                        ver_apenas_entidade_foco = True # Folha: ver apenas ela
                        titulo_escopo_igreja = f"Igreja: {igreja_descendente_selecionada.nome_igreja}"
                    id_selecionado_filtro_pagina = str(igreja_descendente_selecionada.pk) # Garante que o ID correto está selecionado
                except Igreja.DoesNotExist: # Fallback: ID do filtro da página inválido
                    id_selecionado_filtro_pagina = str(request.igreja_ativa.pk) # Volta para a igreja_ativa
                    igreja_em_foco_obj = request.igreja_ativa
                    ver_apenas_entidade_foco = False # Visão de rede da igreja_ativa
                    titulo_escopo_igreja = f"Rede: {request.igreja_ativa.nome_igreja}" if len(temp_pks_dropdown) > 1 else f"Igreja: {request.igreja_ativa.nome_igreja}"
        
        else: # 2. Nenhuma igreja_ativa global, o filtro da página é o principal
            opcoes_filtro_pagina = allowed_churches_base_financeiro.order_by('nome_igreja') # Todas permitidas
            if id_selecionado_filtro_pagina: # Se um filtro de página foi usado
                try:
                    igreja_em_foco_obj = allowed_churches_base_financeiro.get(pk=id_selecionado_filtro_pagina)
                    # Quando não há igreja_ativa global, selecionar uma Regional/Sede no filtro da página
                    # implica ver a rede dessa Regional/Sede (ver_apenas_entidade_foco = False).
                    ver_apenas_entidade_foco = False 
                    # O título será definido na próxima seção ao construir pks_to_include
                except Igreja.DoesNotExist:
                    messages.warning(request, "Igreja selecionada no filtro inválida. Mostrando consolidado.")
                    id_selecionado_filtro_pagina = ''
                    igreja_em_foco_obj = None
                    titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
            else: # Nenhum filtro na página e nenhuma igreja_ativa global (value='')
                igreja_em_foco_obj = None
                id_selecionado_filtro_pagina = '' # Garante que "todas" esteja selecionado
                titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"

        # --- Construir churches_for_queries e título final com base no foco e flag ---
        if igreja_em_foco_obj:
            if ver_apenas_entidade_foco:
                churches_for_queries = Igreja.objects.filter(pk=igreja_em_foco_obj.pk)
                # O título já foi definido como "Apenas: ..." ou "Igreja: ..."
            else: # Visão de rede da igreja_em_foco_obj
                pks_to_include = {igreja_em_foco_obj.pk}
                if hasattr(igreja_em_foco_obj, 'get_descendants'):
                    desc_qs = igreja_em_foco_obj.get_descendants(include_self=False).filter(
                        pk__in=allowed_churches_base_financeiro.values_list('pk', flat=True)
                    )
                    if desc_qs.exists():
                        pks_to_include.update(desc_qs.values_list('pk', flat=True))
                churches_for_queries = Igreja.objects.filter(pk__in=list(pks_to_include), ministerio=ministerio_usuario)
                
                if len(pks_to_include) > 1: # Se incluiu descendentes
                    if not ver_apenas_entidade_foco: # Só define como rede se não for visão exclusiva
                        titulo_escopo_igreja = f"Rede: {igreja_em_foco_obj.nome_igreja}"
                else: # Apenas a igreja em foco (não tem descendentes ou é visão exclusiva implícita)
                    if not ver_apenas_entidade_foco: # Só define como igreja se não for visão exclusiva
                        titulo_escopo_igreja = f"Igreja: {igreja_em_foco_obj.nome_igreja}"
        else: # Visão consolidada de todas as igrejas permitidas ao líder
            churches_for_queries = allowed_churches_base_financeiro

        if not churches_for_queries or not churches_for_queries.exists():
            messages.warning(request, "Nenhuma igreja corresponde aos filtros aplicados.")
            return render(request, 'financeiro/painel_lideranca_financeiro.html', {
                'nenhuma_igreja_filtro': True, 
                'ministerio_usuario': ministerio_usuario,
                'titulo_dashboard': f"Liderança Financeira - {ministerio_usuario.nome_fantasia}",
                'igrejas_permitidas_filtro': allowed_churches_base_financeiro.order_by('nome_igreja'),
                'igreja_id_filtro_selecionado': id_selecionado_filtro_pagina,
            })

        # Filtros de período
        periodo_filtro = request.GET.get('periodo_filtro', 'mes_atual')
        ano_atual = now().year
        mes_atual = now().month

        receitas_base = Receitas.objects.filter(igreja__in=churches_for_queries)
        despesas_base = Despesas.objects.filter(igreja__in=churches_for_queries)

        titulo_filtro_periodo = "" 
        if periodo_filtro == 'ano_atual':
            receitas_filtradas = receitas_base.filter(data__year=ano_atual)
            despesas_filtradas = despesas_base.filter(data__year=ano_atual)
            titulo_filtro_periodo = f"Ano {ano_atual}"
        elif periodo_filtro == 'mes_atual':
            receitas_filtradas = receitas_base.filter(data__year=ano_atual, data__month=mes_atual)
            despesas_filtradas = despesas_base.filter(data__year=ano_atual, data__month=mes_atual)
            titulo_filtro_periodo = f"{calendar.month_name[mes_atual].capitalize()}/{ano_atual}"
        elif periodo_filtro == 'mes_anterior':
            hoje = now().date()
            primeiro_dia_mes_atual = hoje.replace(day=1)
            ultimo_dia_mes_anterior = primeiro_dia_mes_atual - timedelta(days=1)
            primeiro_dia_mes_anterior = ultimo_dia_mes_anterior.replace(day=1)
            receitas_filtradas = receitas_base.filter(data__gte=primeiro_dia_mes_anterior, data__lte=ultimo_dia_mes_anterior)
            despesas_filtradas = despesas_base.filter(data__gte=primeiro_dia_mes_anterior, data__lte=ultimo_dia_mes_anterior)
            titulo_filtro_periodo = f"{calendar.month_name[primeiro_dia_mes_anterior.month].capitalize()}/{primeiro_dia_mes_anterior.year}"
        else: # 'geral'
            receitas_filtradas = receitas_base
            despesas_filtradas = despesas_base
            titulo_filtro_periodo = "Geral"
        
        titulo_dashboard_final = f"Liderança Financeira - {titulo_escopo_igreja} ({titulo_filtro_periodo})"

        total_receitas_lideranca = receitas_filtradas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        total_despesas_lideranca = despesas_filtradas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        saldo_geral_lideranca = total_receitas_lideranca - total_despesas_lideranca
        
        grafico_comparativo_labels = []
        grafico_comparativo_receitas_data = []
        grafico_comparativo_despesas_data = []
        grafico_comparativo_saldos_data = []

        churches_to_compare_qs = churches_for_queries.order_by('nome_igreja')

        for igreja_obj_loop in churches_to_compare_qs:
            receitas_igreja_loop = receitas_filtradas.filter(igreja=igreja_obj_loop)
            despesas_igreja_loop = despesas_filtradas.filter(igreja=igreja_obj_loop)
            total_rec_igreja_loop = receitas_igreja_loop.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            total_desp_igreja_loop = despesas_igreja_loop.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            saldo_igreja_loop = total_rec_igreja_loop - total_desp_igreja_loop
            grafico_comparativo_labels.append(igreja_obj_loop.nome_igreja)
            grafico_comparativo_receitas_data.append(float(total_rec_igreja_loop))
            grafico_comparativo_despesas_data.append(float(total_desp_igreja_loop))
            grafico_comparativo_saldos_data.append(float(saldo_igreja_loop))

        igrejas_com_totais = []
        for i, igreja_obj_rank_loop in enumerate(churches_to_compare_qs):
            igrejas_com_totais.append({
                'igreja': igreja_obj_rank_loop,
                'total_receitas': Decimal(grafico_comparativo_receitas_data[i]),
                'total_despesas': Decimal(grafico_comparativo_despesas_data[i]),
                'saldo': Decimal(grafico_comparativo_saldos_data[i]),
            })
        ranking_top_receitas = sorted(igrejas_com_totais, key=lambda x: x['total_receitas'], reverse=True)[:5]
        ranking_top_saldo_positivo = sorted(
            [item for item in igrejas_com_totais if item['saldo'] >= 0],
            key=lambda x: x['saldo'],
            reverse=True
        )[:5]
        ranking_saldo_negativo = sorted(
            [item for item in igrejas_com_totais if item['saldo'] < 0],
            key=lambda x: x['saldo']
        )
        
        grafico_gastos_cat_labels = []
        grafico_gastos_cat_valores = []
        grafico_gastos_cat_percentuais = []
        if total_despesas_lideranca > 0:
            categorias_despesa_lideranca_qs = despesas_filtradas.values(
                'categoria__nome'
            ).annotate(
                total_categoria=Sum('valor')
            ).filter(total_categoria__gt=0).order_by('-total_categoria')
            for item_cat_gasto_loop in categorias_despesa_lideranca_qs:
                categoria_nome_gasto = item_cat_gasto_loop['categoria__nome'] if item_cat_gasto_loop['categoria__nome'] else "Sem Categoria"
                total_cat_gasto = item_cat_gasto_loop['total_categoria']
                percentual_gasto = (total_cat_gasto / total_despesas_lideranca) * 100
                grafico_gastos_cat_labels.append(categoria_nome_gasto)
                grafico_gastos_cat_valores.append(float(total_cat_gasto))
                grafico_gastos_cat_percentuais.append(round(float(percentual_gasto), 2))

        context = {
            'titulo_dashboard': titulo_dashboard_final,
            'total_receitas_lideranca': total_receitas_lideranca,
            'total_despesas_lideranca': total_despesas_lideranca,
            'saldo_geral_lideranca': saldo_geral_lideranca,
            'titulo_filtro_periodo': titulo_filtro_periodo,
            'periodo_filtro_selecionado': periodo_filtro,            
            'allowed_churches_count': churches_for_queries.count(),
            'grafico_comparativo_labels_json': json.dumps(grafico_comparativo_labels),
            'grafico_comparativo_receitas_data_json': json.dumps(grafico_comparativo_receitas_data),
            'grafico_comparativo_despesas_data_json': json.dumps(grafico_comparativo_despesas_data),
            'grafico_comparativo_saldos_data_json': json.dumps(grafico_comparativo_saldos_data),
            'ranking_top_receitas': ranking_top_receitas,
            'ranking_top_saldo_positivo': ranking_top_saldo_positivo,
            'ranking_saldo_negativo': ranking_saldo_negativo,
            'grafico_gastos_cat_labels_json': json.dumps(grafico_gastos_cat_labels),
            'grafico_gastos_cat_valores_json': json.dumps(grafico_gastos_cat_valores),
            'grafico_gastos_cat_percentuais_json': json.dumps(grafico_gastos_cat_percentuais),
            'igrejas_permitidas_filtro': opcoes_filtro_pagina,
            'igreja_id_filtro_selecionado': id_selecionado_filtro_pagina,
            'ministerio_usuario': ministerio_usuario, 
        }
        return render(request, 'financeiro/painel_lideranca_financeiro.html', context)
    except Exception as e:
        logger.exception(f"Erro ao carregar painel de liderança financeira para ministério {ministerio_usuario.id if ministerio_usuario else 'N/A'}: {e}")
        messages.error(request, f"Ocorreu um erro ao carregar o painel de liderança financeira: {e}")
        return render(request, 'financeiro/painel_lideranca_financeiro.html', {
            'erro_painel': True, 
            'ministerio_usuario': ministerio_usuario
        })


# --- Transferência entre Caixas ---
from .models import TransferenciaCaixa
from .forms import TransferenciaCaixaForm

@login_required
@page_access_required('financeiro')
def transferencia_caixa_create(request):
    if request.method == 'POST':
        form = TransferenciaCaixaForm(request.POST, request=request)
        if form.is_valid():
            transferencia = form.save(commit=False)
            transferencia.usuario = request.user
            transferencia.save()
            messages.success(request, 'Transferência realizada com sucesso.')
            return redirect('financeiro:nova_transferencia_caixa')
    else:
        form = TransferenciaCaixaForm(request=request)

    # Historico de transferencias apenas da igreja ativa ja validada pelo middleware.
    igreja_ativa = getattr(request, 'igreja_ativa', None)

    if igreja_ativa:
        transferencias = TransferenciaCaixa.objects.filter(
            caixa_origem__igreja=igreja_ativa,
            caixa_destino__igreja=igreja_ativa
        ).select_related('caixa_origem', 'caixa_destino', 'usuario').order_by('-data')[:50]
    else:
        transferencias = TransferenciaCaixa.objects.none()

    # Auditoria (ações principais)
    auditoria = [
        {'acao': 'Transferência criada', 'usuario': t.usuario.get_full_name() if t.usuario else 'N/A', 'data': t.data, 'detalhes': f'{t.valor} de {t.caixa_origem} para {t.caixa_destino}'}
        for t in transferencias
    ]

    return render(request, 'financeiro/transferencia_caixa_form.html', {
        'form': form,
        'transferencias': transferencias,
        'auditoria': auditoria,
    })


@login_required
@page_access_required('financeiro')
def api_caixas_por_igreja(request, igreja_id):
    """API endpoint para retornar caixas de uma Igreja (para filtro dinâmico no JavaScript)"""
    from django.http import JsonResponse
    
    igreja = get_object_or_404(
        get_allowed_churches_for_user(request.user),
        pk=igreja_id,
    )
    
    # Retornar caixas da Igreja, ordenadas por nome
    caixas = ContaBancaria.objects.filter(
        igreja=igreja
    ).values('id', 'nome_identificacao').order_by('nome_identificacao')
    
    caixas_json = [
        {'id': c['id'], 'nome': c['nome_identificacao']}
        for c in caixas
    ]
    
    return JsonResponse(caixas_json, safe=False)
