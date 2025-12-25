# --- Transferência entre Caixas ---
from .models import TransferenciaCaixa
from .forms import TransferenciaCaixaForm
from django.contrib.auth.decorators import login_required

@login_required
def transferencia_caixa_create(request):
    if request.method == 'POST':
        form = TransferenciaCaixaForm(request.POST)
        if form.is_valid():
            transferencia = form.save(commit=False)
            transferencia.usuario = request.user
            transferencia.save()
            messages.success(request, 'Transferência realizada com sucesso.')
            return redirect('financeiro:nova_transferencia_caixa')
    else:
        form = TransferenciaCaixaForm()

    # Histórico de transferências (todas)
    transferencias = TransferenciaCaixa.objects.select_related('caixa_origem', 'caixa_destino', 'usuario').order_by('-data')[:50]

    # Auditoria (ações principais)
    # Exemplo: logs fictícios, substitua por integração real se necessário
    auditoria = [
        {'acao': 'Transferência criada', 'usuario': t.usuario.get_full_name() if t.usuario else 'N/A', 'data': t.data, 'detalhes': f'{t.valor} de {t.caixa_origem} para {t.caixa_destino}'}
        for t in transferencias
    ]

    return render(request, 'financeiro/transferencia_caixa_form.html', {
        'form': form,
        'transferencias': transferencias,
        'auditoria': auditoria,
    })
from django.contrib.auth import get_user_model
from .models import PermissaoCaixa
from django.contrib.admin.views.decorators import staff_member_required
# --- Gestão de Permissões de Caixa ---
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from configuracao.models import PerfilUsuario, Ministerio, Igreja
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from .models import Receitas, Despesas, ContaBancaria, FechamentoCaixa, ContaPagar, CategoriaDespesa, Fornecedor
from .forms import (
    ReceitaForm, DespesaForm, CategoriaDespesaForm, FechamentoCaixaForm, ContaBancariaForm,
    FornecedorForm, ContaPagarForm, RegistrarPagamentoContaPagarForm
)
from .utils import has_finance_view_permission, has_finance_edit_permission, get_allowed_churches_for_user, is_finance_leader, is_admin_org
from core.utils import get_ministerio_or_error
from core.decorators import check_permission
from decimal import Decimal
import locale
import logging, traceback, calendar
from datetime import date, datetime, timedelta
from num2words import num2words
from django.db import transaction
import json
from django.urls import reverse
from core.decorators import verificar_assinatura_valida

# --- Painel Liderança Financeiro ---
@check_permission(is_finance_leader)
def painel_lideranca_financeiro(request):
    ministerio_usuario = get_ministerio_or_error(request)
    allowed_churches_base_financeiro = get_allowed_churches_for_user(request.user)
    if not allowed_churches_base_financeiro.exists() and not is_admin_org(request.user):
        messages.warning(request, "Nenhuma igreja encontrada para visualização no painel de liderança financeira.")
        return render(request, 'financeiro/painel_lideranca_financeiro.html', {
            'nenhuma_igreja_permissao': True,
            'ministerio_usuario': ministerio_usuario,
            'titulo_dashboard': f"Liderança Financeira - {ministerio_usuario.nome_fantasia}"
        })
    try:
        churches_for_queries = None
        igreja_em_foco_obj = None
        ver_apenas_entidade_foco = False
        titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
        opcoes_filtro_pagina = allowed_churches_base_financeiro.order_by('nome_igreja')
        id_selecionado_filtro_pagina = request.GET.get('igreja_filtro', '')
        if request.igreja_ativa and request.igreja_ativa in allowed_churches_base_financeiro:
            igreja_em_foco_obj = request.igreja_ativa
            temp_pks_dropdown = {request.igreja_ativa.pk}
            if hasattr(request.igreja_ativa, 'get_descendants'):
                desc_dropdown_qs = request.igreja_ativa.get_descendants(include_self=False).filter(
                    pk__in=allowed_churches_base_financeiro.values_list('pk', flat=True)
                )
                if desc_dropdown_qs.exists():
                    temp_pks_dropdown.update(desc_dropdown_qs.values_list('pk', flat=True))
            opcoes_filtro_pagina = Igreja.objects.filter(pk__in=list(temp_pks_dropdown)).order_by('nome_igreja')
            if not id_selecionado_filtro_pagina or id_selecionado_filtro_pagina == str(request.igreja_ativa.pk):
                id_selecionado_filtro_pagina = str(request.igreja_ativa.pk)
                igreja_em_foco_obj = request.igreja_ativa
                if request.GET.get('igreja_filtro') == str(request.igreja_ativa.pk) and \
                   hasattr(request.igreja_ativa, 'get_descendants') and \
                   request.igreja_ativa.get_descendants(include_self=False).filter(pk__in=allowed_churches_base_financeiro.values_list('pk', flat=True)).exists():
                    ver_apenas_entidade_foco = True
                    titulo_escopo_igreja = f"Apenas: {request.igreja_ativa.nome_igreja}"
                else:
                    ver_apenas_entidade_foco = False
                    titulo_escopo_igreja = f"Rede: {request.igreja_ativa.nome_igreja}" if len(temp_pks_dropdown) > 1 else f"Igreja: {request.igreja_ativa.nome_igreja}"
            else:
                try:
                    igreja_descendente_selecionada = opcoes_filtro_pagina.get(pk=id_selecionado_filtro_pagina)
                    igreja_em_foco_obj = igreja_descendente_selecionada
                    ver_apenas_entidade_foco = True
                    titulo_escopo_igreja = f"Igreja: {igreja_descendente_selecionada.nome_igreja}"
                    id_selecionado_filtro_pagina = str(igreja_descendente_selecionada.pk)
                except Igreja.DoesNotExist:
                    id_selecionado_filtro_pagina = str(request.igreja_ativa.pk)
                    igreja_em_foco_obj = request.igreja_ativa
                    ver_apenas_entidade_foco = False
                    titulo_escopo_igreja = f"Rede: {request.igreja_ativa.nome_igreja}" if len(temp_pks_dropdown) > 1 else f"Igreja: {request.igreja_ativa.nome_igreja}"
        else:
            opcoes_filtro_pagina = allowed_churches_base_financeiro.order_by('nome_igreja')
            if id_selecionado_filtro_pagina:
                try:
                    igreja_em_foco_obj = allowed_churches_base_financeiro.get(pk=id_selecionado_filtro_pagina)
                    ver_apenas_entidade_foco = False
                except Igreja.DoesNotExist:
                    messages.warning(request, "Igreja selecionada no filtro inválida. Mostrando consolidado.")
                    id_selecionado_filtro_pagina = ''
                    igreja_em_foco_obj = None
                    titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
            else:
                igreja_em_foco_obj = None
                id_selecionado_filtro_pagina = ''
                titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
        if igreja_em_foco_obj:
            if ver_apenas_entidade_foco:
                churches_for_queries = Igreja.objects.filter(pk=igreja_em_foco_obj.pk)
            else:
                pks_to_include = {igreja_em_foco_obj.pk}
                if hasattr(igreja_em_foco_obj, 'get_descendants'):
                    desc_qs = igreja_em_foco_obj.get_descendants(include_self=False).filter(
                        pk__in=allowed_churches_base_financeiro.values_list('pk', flat=True)
                    )
                    if desc_qs.exists():
                        pks_to_include.update(desc_qs.values_list('pk', flat=True))
                churches_for_queries = Igreja.objects.filter(pk__in=list(pks_to_include), ministerio=ministerio_usuario)
                if len(pks_to_include) > 1:
                    if not ver_apenas_entidade_foco:
                        titulo_escopo_igreja = f"Rede: {igreja_em_foco_obj.nome_igreja}"
                else:
                    if not ver_apenas_entidade_foco:
                        titulo_escopo_igreja = f"Igreja: {igreja_em_foco_obj.nome_igreja}"
        else:
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
        else:
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
from django.contrib.auth import get_user_model
from .models import PermissaoCaixa
from django.contrib.admin.views.decorators import staff_member_required
# --- Gestão de Permissões de Caixa ---
from django.contrib.auth.decorators import login_required

@login_required
@staff_member_required
def gerenciar_permissoes_caixa(request, caixa_id):
    caixa = get_object_or_404(ContaBancaria, pk=caixa_id)
    User = get_user_model()
    usuarios = User.objects.filter(is_active=True, perfil__ministerio=caixa.igreja.ministerio)
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
    permissoes_dict = {p.usuario_id: p for p in permissoes}
    return render(request, 'financeiro/gerenciar_permissoes_caixa.html', {
        'caixa': caixa,
        'usuarios': usuarios,
        'permissoes_dict': permissoes_dict,
    })
from django.db.models import Q
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from .models import Receitas, Despesas, ContaBancaria, FechamentoCaixa, ContaPagar, CategoriaDespesa, Fornecedor
from .forms import (
    ReceitaForm, DespesaForm, CategoriaDespesaForm, FechamentoCaixaForm, ContaBancariaForm,
    FornecedorForm, ContaPagarForm, RegistrarPagamentoContaPagarForm
)
from configuracao.models import PerfilUsuario, Ministerio, Igreja
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import Http404
from django.db.models import Sum, Q, Count
from .utils import has_finance_view_permission, has_finance_edit_permission, get_allowed_churches_for_user, is_finance_leader, is_admin_org
from core.utils import get_ministerio_or_error
from core.decorators import check_permission
from decimal import Decimal
import locale
import logging, traceback, calendar
from datetime import date, datetime, timedelta
from num2words import num2words
from django.db import transaction
import json
from django.urls import reverse
from core.decorators import verificar_assinatura_valida

logger = logging.getLogger(__name__)

# Tenta configurar o locale para pt_BR, com fallbacks.
locales_to_try = ['pt_BR.UTF-8', 'Portuguese_Brazil.1252']
locale_set = False
for loc in locales_to_try:
    try:
        locale.setlocale(locale.LC_ALL, loc)
        locale_set = True
        break
    except locale.Error:
        continue
if not locale_set:
    logger.warning(f"Nenhum dos locales {locales_to_try} foi suportado. Usando o locale padrão do sistema.")

@check_permission(has_finance_view_permission)
def painel_financeiro(request):
    """ Painel/Dashboard Financeiro da Ministério ou de uma Igreja específica. """
    ministerio = get_ministerio_or_error(request)
    try:
        allowed_churches = get_allowed_churches_for_user(request.user)
        igreja_id_filtro_get = request.GET.get('igreja_filtro', '')
        igreja_selecionada_para_dados = None
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_selecionada_para_dados = request.igreja_ativa
            titulo_dashboard = f"Igreja: {igreja_selecionada_para_dados.nome_igreja}"
            igrejas_para_filtro_template = Igreja.objects.filter(pk=request.igreja_ativa.pk)
            igreja_id_filtro_selecionado_template = str(request.igreja_ativa.pk)
        else:
            if igreja_id_filtro_get:
                try:
                    igreja_selecionada_para_dados = allowed_churches.get(pk=igreja_id_filtro_get)
                    titulo_dashboard = f"Igreja: {igreja_selecionada_para_dados.nome_igreja}"
                except Igreja.DoesNotExist:
                    messages.warning(request, "Igreja selecionada inválida ou não permitida. Mostrando dados consolidados.")
                    igreja_id_filtro_get = ''
            if not igreja_selecionada_para_dados:
                titulo_dashboard = f"Ministério: {ministerio.nome_fantasia} (Igrejas Permitidas)"
            igrejas_para_filtro_template = allowed_churches.order_by('nome_igreja')
            igreja_id_filtro_selecionado_template = igreja_id_filtro_get
        periodo_filtro = request.GET.get('periodo_filtro', 'aberto')
        ano_atual = date.today().year
        data_hoje = date.today()
        data_inicio_mes = data_hoje.replace(day=1)
        if igreja_selecionada_para_dados:
            receitas_base = Receitas.objects.filter(igreja=igreja_selecionada_para_dados)
            despesas_base = Despesas.objects.filter(igreja=igreja_selecionada_para_dados)
        else:
            receitas_base = Receitas.objects.filter(igreja__in=allowed_churches)
            despesas_base = Despesas.objects.filter(igreja__in=allowed_churches)
        if igreja_selecionada_para_dados:
            contas_pagar_base = ContaPagar.objects.filter(igreja=igreja_selecionada_para_dados)
        else:
            contas_pagar_base = ContaPagar.objects.filter(igreja__in=allowed_churches)
        total_contas_pendentes = contas_pagar_base.filter(status='PEN').aggregate(total=Sum('valor'))['total'] or Decimal(0)
        total_contas_vencidas = contas_pagar_base.filter(status='VEN').aggregate(total=Sum('valor'))['total'] or Decimal(0)
        if periodo_filtro == 'aberto':
            receitas_filtradas = receitas_base.filter(fechado=False)
            despesas_filtradas = despesas_base.filter(fechado=False)
            titulo_filtro_periodo = "Em Aberto"
        elif periodo_filtro == 'ano_atual':
            receitas_filtradas = receitas_base.filter(data__year=ano_atual)
            despesas_filtradas = despesas_base.filter(data__year=ano_atual)
            titulo_filtro_periodo = f"Ano {ano_atual}"
        else:
            receitas_filtradas = receitas_base
            despesas_filtradas = despesas_base
            titulo_filtro_periodo = "Geral"
        categorias_receita_data_qs = receitas_filtradas.values('categoria').annotate(total=Sum('valor')).filter(total__gt=0).order_by('-total')
        mapa_cat_receita_display = {codigo: nome for codigo, nome in Receitas.CATEGORIA_CHOICES}
        grafico_cat_rec_labels = [mapa_cat_receita_display.get(item['categoria'], item['categoria']) for item in categorias_receita_data_qs]
        grafico_cat_rec_valores = [float(item['total']) for item in categorias_receita_data_qs]
        categorias_despesa_data = despesas_filtradas.values('categoria__nome').annotate(total=Sum('valor')).filter(total__gt=0).order_by('-total')
        grafico_cat_desp_labels = [item['categoria__nome'] if item['categoria__nome'] else "Sem Categoria" for item in categorias_despesa_data]
        grafico_cat_desp_valores = [float(item['total']) for item in categorias_despesa_data]
        total_receitas = receitas_filtradas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        total_despesas = despesas_filtradas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        saldo_geral = total_receitas - total_despesas
        receitas_mes = receitas_base.filter(data__gte=data_inicio_mes).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        despesas_mes = despesas_base.filter(data__gte=data_inicio_mes).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        saldo_mes = receitas_mes - despesas_mes
        ultimas_receitas = receitas_filtradas.select_related('igreja', 'membro').order_by('-data')[:5]
        ultimas_despesas = despesas_filtradas.select_related('igreja', 'categoria').order_by('-data')[:5]
        can_edit = has_finance_edit_permission(request.user)
        hoje_grafico = date.today()
        meses_labels_grafico = []
        receitas_mensais_grafico_data = []
        despesas_mensais_grafico_data = []
        saldos_mensais_grafico_data = []
        dizimistas_unicos_mensais_grafico_data = []
        dizimistas_por_fechamento_labels = []
        dizimistas_por_fechamento_valores = []
        ultimos_fechamentos_qs = FechamentoCaixa.objects.filter(
            igreja__in=(allowed_churches if not igreja_selecionada_para_dados else [igreja_selecionada_para_dados])
        ).order_by('-data_fim')[:6]
        ultimos_fechamentos = sorted(list(ultimos_fechamentos_qs), key=lambda fc: fc.data_fim)
        grafico_fech_labels = []
        grafico_fech_receitas_data = []
        grafico_fech_despesas_data = []
        grafico_fech_saldos_data = []
        for fc in ultimos_fechamentos:
            label = f"{fc.data_inicio.strftime('%d/%m')} a {fc.data_fim.strftime('%d/%m/%y') }"
            grafico_fech_labels.append(label)
            grafico_fech_receitas_data.append(float(fc.total_entradas))
            grafico_fech_despesas_data.append(float(fc.total_saidas))
            grafico_fech_saldos_data.append(float(fc.saldo_final))
            dizimistas_no_fechamento_count = receitas_base.filter(
                data__gte=fc.data_inicio,
                data__lte=fc.data_fim,
                categoria='dizimo',
                membro__isnull=False
            ).values('membro').distinct().count()
            dizimistas_por_fechamento_labels.append(f"Fech. {fc.data_fim.strftime('%b/%y')}")
            dizimistas_por_fechamento_valores.append(dizimistas_no_fechamento_count)
        meses_para_iterar = []
        for i in range(11, -1, -1):
            ano_alvo = hoje_grafico.year
            mes_alvo_num = hoje_grafico.month - i
            while mes_alvo_num <= 0:
                mes_alvo_num += 12
                ano_alvo -= 1
            meses_para_iterar.append(date(ano_alvo, mes_alvo_num, 1))
        for data_mes_loop in meses_para_iterar:
            ano = data_mes_loop.year
            mes = data_mes_loop.month
            mes_label = data_mes_loop.strftime("%b/%y").capitalize()
            meses_labels_grafico.append(mes_label)
            receitas_do_mes_val = receitas_base.filter(
                data__year=ano, data__month=mes
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
            receitas_mensais_grafico_data.append(float(receitas_do_mes_val))
            despesas_do_mes_val = despesas_base.filter(
                data__year=ano, data__month=mes
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
            despesas_mensais_grafico_data.append(float(despesas_do_mes_val))
            saldos_mensais_grafico_data.append(float(receitas_do_mes_val - despesas_do_mes_val))
            dizimistas_count = receitas_base.filter(
                data__year=ano, data__month=mes, 
                categoria='dizimo', 
                membro__isnull=False
            ).values('membro').distinct().count()
            dizimistas_unicos_mensais_grafico_data.append(dizimistas_count)
        dizimos_no_periodo_filtrado = receitas_filtradas.filter(categoria='dizimo', membro__isnull=False)
        perfil_dizimistas_data_qs = dizimos_no_periodo_filtrado.values(
            'membro__tipo_pessoa__nome'
        ).annotate(
            quantidade_dizimistas=Count('membro', distinct=True),
            valor_total_dizimado=Sum('valor')
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
            qtd_perc = (item['quantidade_dizimistas'] / total_geral_dizimistas_no_periodo * 100) if total_geral_dizimistas_no_periodo > 0 else 0
            perfil_dizimistas_qtd_percentuais.append(round(qtd_perc, 2))
            valor_perc = (item['valor_total_dizimado'] / total_geral_valor_dizimado_no_periodo * 100) if total_geral_valor_dizimado_no_periodo > 0 else 0
            perfil_dizimistas_valor_percentuais.append(round(float(valor_perc), 2))
        caixa_id_filtro = request.GET.get('caixa_filtro')
        if igreja_selecionada_para_dados:
            contas_bancarias_dropdown = ContaBancaria.objects.filter(igreja=igreja_selecionada_para_dados).order_by('nome_identificacao')
        else:
            contas_bancarias_dropdown = ContaBancaria.objects.filter(igreja__in=allowed_churches).order_by('igreja__nome_igreja', 'nome_identificacao')
        if igreja_selecionada_para_dados:
            if caixa_id_filtro:
                contas_bancarias_painel = ContaBancaria.objects.filter(igreja=igreja_selecionada_para_dados, pk=caixa_id_filtro).order_by('nome_identificacao')
            else:
                contas_bancarias_painel = contas_bancarias_dropdown
        else:
            if caixa_id_filtro:
                contas_bancarias_painel = ContaBancaria.objects.filter(igreja__in=allowed_churches, pk=caixa_id_filtro).order_by('igreja__nome_igreja', 'nome_identificacao')
            else:
                contas_bancarias_painel = contas_bancarias_dropdown
        context = {
            'contas_bancarias_dropdown': contas_bancarias_dropdown,
            'ministerio': ministerio,
            'igrejas_org': igrejas_para_filtro_template,
            'igreja_selecionada': igreja_selecionada_para_dados,
            'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template,
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
            'grafico_mensal_labels_json': json.dumps(meses_labels_grafico),
            'grafico_receitas_data_json': json.dumps(receitas_mensais_grafico_data),
            'grafico_despesas_data_json': json.dumps(despesas_mensais_grafico_data),
            'grafico_saldos_data_json': json.dumps(saldos_mensais_grafico_data),
            'grafico_dizimistas_data_json': json.dumps(dizimistas_unicos_mensais_grafico_data),
            'grafico_dizimistas_fechamento_labels_json': json.dumps(dizimistas_por_fechamento_labels),
            'grafico_dizimistas_fechamento_valores_json': json.dumps(dizimistas_por_fechamento_valores),
            'grafico_cat_desp_labels_json': json.dumps(grafico_cat_desp_labels),
            'grafico_cat_desp_valores_json': json.dumps(grafico_cat_desp_valores),
            'grafico_fech_labels_json': json.dumps(grafico_fech_labels),
            'grafico_fech_receitas_data_json': json.dumps(grafico_fech_receitas_data),
            'grafico_fech_despesas_data_json': json.dumps(grafico_fech_despesas_data),
            'grafico_fech_saldos_data_json': json.dumps(grafico_fech_saldos_data),
            'total_contas_pendentes': total_contas_pendentes,
            'total_contas_vencidas': total_contas_vencidas,
            'grafico_cat_rec_labels_json': json.dumps(grafico_cat_rec_labels),
            'grafico_cat_rec_valores_json': json.dumps(grafico_cat_rec_valores),
            'contas_bancarias_painel': contas_bancarias_painel,
            'perfil_dizimistas_labels_json': json.dumps(perfil_dizimistas_labels),
            'perfil_dizimistas_qtd_valores_json': json.dumps(perfil_dizimistas_qtd_valores),
            'perfil_dizimistas_total_valores_json': json.dumps(perfil_dizimistas_total_valores),
            'perfil_dizimistas_qtd_percentuais_json': json.dumps(perfil_dizimistas_qtd_percentuais),
            'perfil_dizimistas_valor_percentuais_json': json.dumps(perfil_dizimistas_valor_percentuais),
        }
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
        min_id = ministerio.id if 'ministerio' in locals() else 'N/A'
        logger.exception(f"Erro no painel financeiro para ministério {min_id}")
        messages.error(request, f"Ocorreu um erro ao carregar o painel financeiro: {e}")
        return redirect('secretaria:dashboard')
