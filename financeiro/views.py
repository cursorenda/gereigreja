# c:\Gereigreja\financeiro\views.py
# financeiro/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test # Importar user_passes_test
from django.utils.timezone import now # Importar now

# Importar modelos corretos
from .models import Receitas, Despesas, ContaBancaria, FechamentoCaixa, ContaPagar, CategoriaDespesa, Fornecedor, Organizacao # Removed CATEGORIA_RECEITA_CHOICES import
# Importar forms corretos
from .forms import (
    ReceitaForm, DespesaForm, CategoriaDespesaForm, FechamentoCaixaForm, ContaBancariaForm,
    FornecedorForm, ContaPagarForm, RegistrarPagamentoContaPagarForm # Adicionar novos forms
)
# from django.contrib.auth.decorators import login_required # Removido, já importado acima
from configuracao.models import PerfilUsuario, Organizacao, Igreja
from django.core.exceptions import PermissionDenied, ValidationError # Adicionar ValidationError
from django.http import Http404
from django.db.models import Sum, Q, Count # Adicionado Count
# --- IMPORTAR UTILS DE PERMISSÃO ---

from .utils import has_finance_view_permission, has_finance_edit_permission, get_allowed_churches_for_user, is_finance_leader, is_admin_org # Importar is_admin_org
from core.utils import get_organizacao_or_error # Importar de core.utils # noqa: E402
from core.decorators import check_permission # <<< ADICIONE ESTA LINHA
# --- FIM IMPORT ---
from decimal import Decimal # Import Decimal
import locale
import logging, traceback, calendar 
from datetime import date, datetime, timedelta 
from num2words import num2words
from django.db import transaction # Adicionar import para transações atômicas
import json # Adicionar esta linha # noqa: E402
from django.urls import reverse
from core.decorators import verificar_assinatura_valida # Ou o caminho correto

@login_required
@verificar_assinatura_valida # Nosso novo decorator
def minha_view_protegida(request):
    organizacao = get_organizacao_or_error(request) # Ainda chama para obter a org e verificar org.ativo
    # ...
    # ... resto da view ...




# Configurar locale e logger
# from dateutil.relativedelta import relativedelta # Descomente se for usar relativedelta

try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8') # Usar LC_ALL
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252') # Fallback para Windows
logger = logging.getLogger(__name__)


## A função get_organizacao_or_error foi movida para core.utils.py ##


@check_permission(has_finance_view_permission) # MODIFICADO
def painel_financeiro(request):
    """ Painel/Dashboard Financeiro da Organização ou de uma Igreja específica. """
    organizacao = get_organizacao_or_error(request)
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
                titulo_dashboard = f"Organização: {organizacao.nome_fantasia} (Igrejas Permitidas)"

        
             # Para o dropdown de filtro na página, mostrar todas as permitidas se nenhuma global estiver ativa
            igrejas_para_filtro_template = allowed_churches.order_by('nome_igreja')
            igreja_id_filtro_selecionado_template = igreja_id_filtro_get
        
        
        
        # --- FIM FILTRO DE IGREJA ---

        # --- LÓGICA DO FILTRO DE PERÍODO ---
        periodo_filtro = request.GET.get('periodo_filtro', 'aberto') # Pega o valor do GET, default 'aberto'
        ano_atual = date.today().year
        data_hoje = date.today()
        data_inicio_mes = data_hoje.replace(day=1)

        # Base Querysets - AGORA FILTRADOS PELAS IGREJAS PERMITIDAS ou pela igreja selecionada (se permitida)
        # Se igreja_selecionada (do seletor global ou do filtro GET) está definida, filtra por ela

        if igreja_selecionada_para_dados:
            receitas_base = Receitas.objects.filter(igreja=igreja_selecionada_para_dados)
            despesas_base = Despesas.objects.filter(igreja=igreja_selecionada_para_dados)

        else: # Todas as igrejas permitidas para o usuário
            receitas_base = Receitas.objects.filter(igreja__in=allowed_churches) # Já filtrado por allowed_churches
            despesas_base = Despesas.objects.filter(igreja__in=allowed_churches) # Já filtrado por allowed_churches

         # --- Base para Contas a Pagar (filtrado por igreja/allowed_churches) ---
        if igreja_selecionada_para_dados:
            contas_pagar_base = ContaPagar.objects.filter(igreja=igreja_selecionada_para_dados)
        else:
            contas_pagar_base = ContaPagar.objects.filter(igreja__in=allowed_churches) 
        
        # --- Indicadores de Contas a Pagar ---
        total_contas_pendentes = contas_pagar_base.filter(
            status='PEN'
        ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
        total_contas_vencidas = contas_pagar_base.filter(
            status='VEN' # Ou usar a propriedade is_vencida se preferir, mas status='VEN' é mais direto
        ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
        # --- FIM Indicadores de Contas a Pagar ---

       


        # Aplicar filtro de período aos querysets base (já filtrados por igreja, se aplicável)
        if periodo_filtro == 'aberto':
            receitas_filtradas = receitas_base.filter(fechado=False)
            despesas_filtradas = despesas_base.filter(fechado=False)
            titulo_filtro_periodo = "Em Aberto"
        elif periodo_filtro == 'ano_atual':
            receitas_filtradas = receitas_base.filter(data__year=ano_atual)
            despesas_filtradas = despesas_base.filter(data__year=ano_atual)
            titulo_filtro_periodo = f"Ano {ano_atual}"
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

        # Saldo do mês atual (também filtrado por igreja, se aplicável)
        receitas_mes = receitas_base.filter(data__gte=data_inicio_mes).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        despesas_mes = despesas_base.filter(data__gte=data_inicio_mes).aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        saldo_mes = receitas_mes - despesas_mes

        # Últimas receitas/despesas (filtradas por igreja, se aplicável)
        ultimas_receitas = receitas_base.select_related('igreja', 'membro').order_by('-data')[:5]
        ultimas_despesas = despesas_base.select_related('igreja', 'categoria').order_by('-data')[:5]

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

            # Receitas do mês (usando receitas_base já filtrada por igreja/allowed_churches)
            receitas_do_mes_val = receitas_base.filter(
                data__year=ano, data__month=mes
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
            receitas_mensais_grafico_data.append(float(receitas_do_mes_val))

            # Despesas do mês (usando despesas_base já filtrada por igreja/allowed_churches)
            despesas_do_mes_val = despesas_base.filter(
                data__year=ano, data__month=mes
            ).aggregate(total=Sum('valor'))['total'] or Decimal(0)
            despesas_mensais_grafico_data.append(float(despesas_do_mes_val))

            # Saldo do mês
            saldos_mensais_grafico_data.append(float(receitas_do_mes_val - despesas_do_mes_val))

            # Dizimistas únicos do mês (usando receitas_base)
            dizimistas_count = receitas_base.filter(
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
        # Filtra contas pela(s) igreja(s) selecionada(s) ou todas as permitidas
        if igreja_selecionada_para_dados:
            # Se uma igreja está selecionada, mostra apenas as contas dela

            contas_bancarias_painel = ContaBancaria.objects.filter(igreja=igreja_selecionada_para_dados).order_by('nome_identificacao')
        else:
            # Se nenhuma igreja selecionada, mostra contas de todas as igrejas permitidas

            contas_bancarias_painel = ContaBancaria.objects.filter(igreja__in=allowed_churches).order_by('igreja__nome_igreja', 'nome_identificacao')

        context = {
            'organizacao': organizacao,
            'igrejas_org': igrejas_para_filtro_template, # Lista de igrejas para o dropdown de filtro da página
            'igreja_selecionada': igreja_selecionada_para_dados, # Objeto da igreja cujos dados estão sendo mostrados (ou None)
            'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template, # ID para manter o filtro da página selecionado
            'total_receitas': total_receitas,
            'total_despesas': total_despesas,
            'saldo_geral': saldo_geral,
            'saldo_mes': saldo_mes,
            'ultimas_receitas': ultimas_receitas,
            'ultimas_despesas': ultimas_despesas,
            'periodo_filtro_selecionado': periodo_filtro,
            'titulo_filtro_periodo': titulo_filtro_periodo, # Título do filtro de período
            'titulo_dashboard': titulo_dashboard, # Título principal (Org ou Igreja)
            'can_edit_finance': can_edit, # Flag para o template
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

            # 'allowed_churches_count' não é usado diretamente neste painel da mesma forma que no de liderança
            # 'igrejas_permitidas_filtro' e 'igreja_id_filtro_selecionado' já são tratados por 'igrejas_org' e 'igreja_id_filtro'
        
        }
        
        return render(request, 'financeiro/painel_financeiro.html', context)
    except Exception as e:
        # Logar erro com mais detalhes se possível
        org_id = organizacao.id if 'organizacao' in locals() else 'N/A'
        logger.exception(f"Erro no painel financeiro para organização {org_id}") # Corrigido o nome da função no log
        messages.error(request, f"Ocorreu um erro ao carregar o painel financeiro: {e}")
        return redirect('secretaria:dashboard') # Redireciona para o dashboard da secretaria ou outra página de fallback

# ... (restante das views) ...

# --- Receitas ---
@check_permission(has_finance_view_permission) # MODIFICADO
def lista_receitas(request): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    try:
        allowed_churches = get_allowed_churches_for_user(request.user)
        # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
        if request.igreja_ativa:
            # Se uma igreja ativa está selecionada, filtra por ela (garantindo que ela está entre as permitidas)
            if request.igreja_ativa in allowed_churches: 
                receitas_qs = Receitas.objects.filter(igreja=request.igreja_ativa).select_related('igreja', 'membro').order_by('-data')
            else: # Segurança: se a igreja ativa não for permitida, mostra vazio ou todas permitidas
                receitas_qs = Receitas.objects.filter(igreja__in=allowed_churches).select_related('igreja', 'membro').order_by('-data')
        else:
            # Se nenhuma igreja ativa, mostra de todas as igrejas permitidas
            receitas_qs = Receitas.objects.filter(igreja__in=allowed_churches).select_related('igreja', 'membro').order_by('-data')
        # --- Fim Lógica de Filtragem Inicial ---

        # Filtros adicionais do GET
        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        categoria = request.GET.get('categoria')
        igreja_id_get = request.GET.get('igreja') # Renomeado
        # --- LÓGICA DO FILTRO 'fechado' ---
        # Pega o valor do parâmetro, default para 'false' (aberto) se não vier na URL
        fechado_filter = request.GET.get('fechado', 'false')

        if data_inicio: receitas_qs = receitas_qs.filter(data__gte=data_inicio)
        if data_fim: receitas_qs = receitas_qs.filter(data__lte=data_fim)
        if categoria: receitas_qs = receitas_qs.filter(categoria=categoria)
        # --- Lógica para o filtro de igreja na página (se request.igreja_ativa NÃO estiver definida) ---

        if igreja_id_get:
            # Este filtro só deve ser aplicado se request.igreja_ativa NÃO estiver definida
            if not request.igreja_ativa:
                if is_admin_org(request.user) or allowed_churches.filter(pk=igreja_id_get).exists():
                    receitas_qs = receitas_qs.filter(igreja_id=igreja_id_get)
       
       
        # --- LÓGICA DO FILTRO 'fechado' ---
        fechado_filter = request.GET.get('fechado', 'false')

        # Aplica o filtro 'fechado' baseado no valor (seja o da URL ou o default 'false')
        if fechado_filter == 'true':
            receitas_qs = receitas_qs.filter(fechado=True)
        elif fechado_filter == 'false': # Inclui o default
            receitas_qs = receitas_qs.filter(fechado=False)
        # Se você adicionar uma opção 'todos' com value='', pode adicionar um 'elif fechado_filter == "":' aqui
        # --- FIM DA LÓGICA DO FILTRO 'fechado' ---

        categorias_choices = Receitas.CATEGORIA_CHOICES
        # --- Lógica para o dropdown de filtro de igreja no template ---
        igrejas_para_filtro_template = allowed_churches
        igreja_id_selecionada_template = igreja_id_get # Para o select do filtro da página

        if request.igreja_ativa:
            igrejas_para_filtro_template = Igreja.objects.filter(pk=request.igreja_ativa.pk) # Ou desabilitar o filtro
            igreja_id_selecionada_template = str(request.igreja_ativa.pk) # Para o select do filtro da página

        # Permissão de edição para o template
        can_edit = has_finance_edit_permission(request.user)

        context = {
            'receitas': receitas_qs,
            'organizacao': organizacao,
            'categorias_choices': categorias_choices,
            'igrejas_org': igrejas_para_filtro_template, # Usar a lista ajustada
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'categoria_selecionada': categoria,
            'igreja_selecionada': igreja_id_selecionada_template, # ID para o select do filtro da página
            # Passa o valor que FOI USADO no filtro para o template selecionar a opção correta no filtro da página
            'fechado_selecionado': fechado_filter,
            'can_edit_finance': can_edit, # Flag para o template
        }
        return render(request, 'financeiro/receitas/lista_receitas.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar receitas para organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao listar as receitas: {e}")
        return redirect('financeiro:painel_financeiro')



@check_permission(has_finance_edit_permission) # MODIFICADO
def cadastrar_receita(request): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    igreja_padrao_para_form = None # Inicializa

    # Se não for admin e não tiver igrejas permitidas, não pode criar
    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar receitas ou não está associado a nenhuma igreja específica.")
        return redirect('financeiro:lista_receitas')

    if request.method == 'POST':
        # Passa organização para o form filtrar igrejas e membros (se necessário)
        # Passa allowed_churches para o form filtrar o campo igreja
        form = ReceitaForm(request.POST, organizacao=organizacao, allowed_churches=allowed_churches, igreja_selecionada_inicial=request.igreja_ativa) # Passa request.igreja_ativa
        if form.is_valid():
            try:
                nova_receita = form.save(commit=False)
                # Validação extra (form já deve ter validado, mas é bom garantir)
                if not is_admin_org(request.user) and nova_receita.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida.")
                # Validar membro (se selecionado) - form já deve filtrar
                elif nova_receita.membro and nova_receita.membro.igreja.organizacao != organizacao:
                     messages.error(request, "Erro: Membro selecionado não pertence à sua organização.")
                else:
                     # O método save da Receita agora atualiza o saldo
                     nova_receita.save()

                     messages.success(request, 'Receita cadastrada com sucesso!')
                     return redirect('financeiro:lista_receitas')



            except Exception as e:
                 logger.exception(f"Erro ao salvar receita para organização {organizacao.id}")
                 messages.error(request, f'Erro ao salvar receita: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
 
        initial_form_data = {} # Dicionário para passar valores iniciais
        
        # --- Lógica para pré-selecionar a igreja no formulário GET ---
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            # Se uma igreja ativa está selecionada e é permitida, pré-seleciona ela
            initial_form_data['igreja'] = request.igreja_ativa
            igreja_padrao_para_form = request.igreja_ativa # Passa para o form usar a conta padrão
        elif allowed_churches.count() == 1:
            # Se nenhuma igreja ativa, mas o usuário só tem uma permitida, pré-seleciona essa
            igreja_unica_permitida = allowed_churches.first()
            initial_form_data['igreja'] = igreja_unica_permitida
            igreja_padrao_para_form = igreja_unica_permitida # Passa para o form usar a conta padrão
        # Se múltiplas igrejas permitidas e nenhuma ativa, o campo igreja ficará vazio (usuário seleciona)


        form = ReceitaForm(initial=initial_form_data, organizacao=organizacao, allowed_churches=allowed_churches, igreja_selecionada_inicial=igreja_padrao_para_form)

 
    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Cadastrar Receita'}
    # Usar um template genérico ou específico
    return render(request, 'financeiro/receitas/form_receita.html', context)


@check_permission(has_finance_edit_permission) # MODIFICADO
def editar_receita(request, pk): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    # Garante que a receita pertence às igrejas permitidas
    receita = get_object_or_404(Receitas, pk=pk, igreja__in=allowed_churches)

    # Não permitir editar receita já fechada? (Opcional)
    # if receita.fechado:
    #    messages.error(request, "Não é possível editar uma receita que pertence a um caixa fechado.")
    #    return redirect('financeiro:lista_receitas')

    if request.method == 'POST':
        form = ReceitaForm(request.POST, instance=receita, organizacao=organizacao, allowed_churches=allowed_churches)
        if form.is_valid():
            try:
                receita_editada = form.save(commit=False)
                # Validações extras
                if not is_admin_org(request.user) and receita_editada.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida.")
                elif receita_editada.membro and receita_editada.membro.igreja.organizacao != organizacao:
                     messages.error(request, "Erro: Membro selecionado não pertence à sua organização.")
                else:
                    receita_editada.save()
                    messages.success(request, 'Receita atualizada com sucesso!')
                    return redirect('financeiro:lista_receitas')
            except Exception as e:
                 logger.exception(f"Erro ao salvar edição da receita {pk} para organização {organizacao.id}")
                 messages.error(request, f'Erro ao salvar receita: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = ReceitaForm(instance=receita, organizacao=organizacao, allowed_churches=allowed_churches)

    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Editar Receita', 'receita': receita}
    return render(request, 'financeiro/receitas/form_receita.html', context)


# @login_required # Removido pois check_permission faria isso, mas aqui a lógica é interna
def excluir_receita(request, pk): # noqa: E302
    # Apenas quem pode editar pode excluir
    if not has_finance_edit_permission(request.user):
        raise PermissionDenied("Você não tem permissão para excluir receitas.")
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    receita = get_object_or_404(Receitas, pk=pk, igreja__in=allowed_churches)

    # Não permitir excluir receita já fechada?
    # if receita.fechado:
    #    messages.error(request, "Não é possível excluir uma receita que pertence a um caixa fechado.")
    #    return redirect('financeiro:lista_receitas')

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

            logger.exception(f"Erro ao excluir receita {pk} para organização {organizacao.id}")
            messages.error(request, f'Erro ao excluir receita: {e}')
        return redirect('financeiro:lista_receitas')
    else:
        # GET não deve excluir, mostrar confirmação ou erro
        # context = {'receita': receita, 'organizacao': organizacao}
        # return render(request, 'financeiro/receitas/confirmar_excluir_receita.html', context)
        messages.error(request, 'Método inválido para exclusão.')
        return redirect('financeiro:lista_receitas')


# --- Despesas (Estrutura similar às Receitas) ---
@check_permission(has_finance_view_permission) # MODIFICADO
def lista_despesas(request): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    try:
        allowed_churches = get_allowed_churches_for_user(request.user)
        despesas_qs = Despesas.objects.filter(igreja__in=allowed_churches).select_related('igreja', 'categoria').order_by('-data')

        # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            despesas_qs = despesas_qs.filter(igreja=request.igreja_ativa)
        # Se nenhuma igreja ativa, o filtro já é por igreja__in=allowed_churches (definido acima)
        # --- Fim Lógica de Filtragem Inicial ---
        
        # Filtros adicionais

        data_inicio = request.GET.get('data_inicio')
        data_fim = request.GET.get('data_fim')
        categoria_id = request.GET.get('categoria')
        igreja_id_get = request.GET.get('igreja') # Renomeado para evitar conflito com variável de contexto
        # --- LÓGICA DO FILTRO 'fechado' ---
        # Pega o valor do parâmetro, default para 'false' (aberto) se não vier na URL
        fechado_filter = request.GET.get('fechado', 'false')

        if data_inicio: despesas_qs = despesas_qs.filter(data__gte=data_inicio)
        if data_fim: despesas_qs = despesas_qs.filter(data__lte=data_fim)
        if categoria_id: despesas_qs = despesas_qs.filter(categoria_id=categoria_id)
        if igreja_id_get:
            # Este filtro só deve ser aplicado se request.igreja_ativa NÃO estiver definida
            if not request.igreja_ativa and (is_admin_org(request.user) or allowed_churches.filter(pk=igreja_id_get).exists()):
                despesas_qs = despesas_qs.filter(igreja_id=igreja_id_get)

        # Aplica o filtro 'fechado' baseado no valor (seja o da URL ou o default 'false')
        if fechado_filter == 'true':
            despesas_qs = despesas_qs.filter(fechado=True)
        elif fechado_filter == 'false': # Inclui o default
            despesas_qs = despesas_qs.filter(fechado=False)
        # --- FIM DA LÓGICA DO FILTRO 'fechado' ---

        categorias_org = CategoriaDespesa.objects.filter(organizacao=organizacao)
        # --- Lógica para o dropdown de filtro de igreja no template ---        
        igrejas_para_filtro_template = allowed_churches
        igreja_id_selecionada_template = igreja_id_get # Para o select do filtro da página
        if request.igreja_ativa: igrejas_para_filtro_template = Igreja.objects.filter(pk=request.igreja_ativa.pk) # Ou desabilitar o filtro
        if request.igreja_ativa: igreja_id_selecionada_template = str(request.igreja_ativa.pk)

        # Permissão de edição para o template
        can_edit = has_finance_edit_permission(request.user)

        context = {
            'despesas': despesas_qs,
            'organizacao': organizacao,
            'categorias_org': categorias_org, # Continua mostrando todas as categorias da org
            'igrejas_org': igrejas_para_filtro_template, 
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'categoria_selecionada': categoria_id,
            'igreja_selecionada': igreja_id_selecionada_template, # ID para o select do filtro da página
            # Passa o valor que FOI USADO no filtro para o template selecionar a opção correta
            'fechado_selecionado': fechado_filter,
            'can_edit_finance': can_edit, # Flag para o template
        }
        return render(request, 'financeiro/despesas/lista_despesas.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar despesas para organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao listar as despesas: {e}")
        return redirect('financeiro:painel_financeiro')


@check_permission(has_finance_edit_permission) # MODIFICADO
def cadastrar_despesa(request): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    igreja_padrao_para_form = None # Inicializa

    # Se não for admin e não tiver igrejas permitidas, não pode criar
    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar despesas ou não está associado a nenhuma igreja específica.")
        return redirect('financeiro:lista_despesas')

    if request.method == 'POST':
        form = DespesaForm(request.POST, organizacao=organizacao, allowed_churches=allowed_churches, igreja_selecionada_inicial=request.igreja_ativa) # Passa request.igreja_ativa
        if form.is_valid():
            try:
                nova_despesa = form.save(commit=False)
                if not is_admin_org(request.user) and nova_despesa.igreja not in allowed_churches: messages.error(request, "Erro: Igreja inválida.")
                elif nova_despesa.categoria.organizacao != organizacao: messages.error(request, "Erro: Categoria inválida.")
                # Adicionar validação de conta bancária se usar
                else:
                        # O método save da Despesa agora atualiza o saldo
                        nova_despesa.save() 
                        
                       
                   
                        messages.success(request, 'Despesa cadastrada com sucesso!')
                        return redirect('financeiro:lista_despesas')
   
            except Exception as e:
                 logger.exception(f"Erro ao salvar despesa para organização {organizacao.id}")
                 messages.error(request, f'Erro ao salvar despesa: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
      
        initial_form_data = {} # Dicionário para passar valores iniciais
        
        # --- Lógica para pré-selecionar a igreja no formulário GET ---
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            # Se uma igreja ativa está selecionada e é permitida, pré-seleciona ela
            initial_form_data['igreja'] = request.igreja_ativa
            igreja_padrao_para_form = request.igreja_ativa # Passa para o form usar a conta padrão
        elif allowed_churches.count() == 1:
            # Se nenhuma igreja ativa, mas o usuário só tem uma permitida, pré-seleciona essa
            igreja_unica_permitida = allowed_churches.first()
            initial_form_data['igreja'] = igreja_unica_permitida
            igreja_padrao_para_form = igreja_unica_permitida # Passa para o form usar a conta padrão
        # Se múltiplas igrejas permitidas e nenhuma ativa, o campo igreja ficará vazio (usuário seleciona)



        form = DespesaForm(initial=initial_form_data, organizacao=organizacao, allowed_churches=allowed_churches, igreja_selecionada_inicial=igreja_padrao_para_form)

    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Cadastrar Despesa'}
    return render(request, 'financeiro/despesas/form_despesa.html', context)


# @login_required # Removido
def editar_despesa(request, pk): # noqa: E302
    if not has_finance_edit_permission(request.user): raise PermissionDenied("Sem permissão para editar.")
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    despesa = get_object_or_404(Despesas, pk=pk, igreja__in=allowed_churches)

    # if despesa.fechado: ... (verificar se pode editar)

    if request.method == 'POST':
        form = DespesaForm(request.POST, instance=despesa, organizacao=organizacao, allowed_churches=allowed_churches)
        if form.is_valid():
            try:
                despesa_editada = form.save(commit=False)
                if not is_admin_org(request.user) and despesa_editada.igreja not in allowed_churches: messages.error(request, "Erro: Igreja inválida.")
                elif despesa_editada.categoria.organizacao != organizacao: messages.error(request, "Erro: Categoria inválida.")
                # Adicionar validação de conta bancária se usar
                else:
                    despesa_editada.save()
                    messages.success(request, 'Despesa atualizada com sucesso!')
                    return redirect('financeiro:lista_despesas')
            except Exception as e:
                 logger.exception(f"Erro ao salvar edição da despesa {pk} para organização {organizacao.id}")
                 messages.error(request, f'Erro ao salvar despesa: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = DespesaForm(instance=despesa, organizacao=organizacao, allowed_churches=allowed_churches)

    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Editar Despesa', 'despesa': despesa}
    return render(request, 'financeiro/despesas/form_despesa.html', context)


# @login_required # Removido
def excluir_despesa(request, pk): # noqa: E302
    if not has_finance_edit_permission(request.user): raise PermissionDenied("Sem permissão para excluir.")
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    despesa = get_object_or_404(Despesas, pk=pk, igreja__in=allowed_churches)

    # if despesa.fechado: ... (verificar se pode excluir)

    if request.method == 'POST':
        try:
            nome_despesa = despesa.descricao or f"Despesa ID {despesa.pk}"
            despesa.delete() # O método delete da Despesa agora reverte o saldo
            
            messages.success(request, f'Despesa "{nome_despesa}" excluída com sucesso!')
        except Exception as e:
            logger.exception(f"Erro ao excluir despesa {pk} para organização {organizacao.id}")



# --- Categorias de Despesa ---
@check_permission(has_finance_view_permission) # MODIFICADO
def lista_categorias_despesa(request): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    categorias = CategoriaDespesa.objects.filter(organizacao=organizacao).order_by('nome')
    can_edit = has_finance_edit_permission(request.user) # Para botão de adicionar
    context = {
        'categorias': categorias,
        'organizacao': organizacao,
        'can_edit_finance': can_edit,
    }
    return render(request, 'financeiro/categorias/lista_categorias.html', context)

@check_permission(has_finance_edit_permission) # MODIFICADO
def cadastrar_categoria_despesa(request): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    if request.method == 'POST':
        form = CategoriaDespesaForm(request.POST)
        if form.is_valid():
            try:
                nova_categoria = form.save(commit=False)
                nova_categoria.organizacao = organizacao # Associa à organização
                nova_categoria.save()
                messages.success(request, 'Categoria de despesa cadastrada com sucesso!')
                return redirect('financeiro:lista_categorias_despesa')
            except Exception as e:
                 logger.exception(f"Erro ao salvar categoria de despesa para organização {organizacao.id}")
                 messages.error(request, f'Erro ao salvar categoria: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = CategoriaDespesaForm()
    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Cadastrar Categoria de Despesa'}
    return render(request, 'financeiro/categorias/form_categoria.html', context)




# ====================================================
# ========= INÍCIO: VIEWS PARA CONTAS BANCÁRIAS =========
# ====================================================

@check_permission(has_finance_view_permission) # MODIFICADO
def lista_contas_bancarias(request): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    try:
        allowed_churches = get_allowed_churches_for_user(request.user)
        # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            contas_bancarias = ContaBancaria.objects.filter(igreja=request.igreja_ativa).select_related('igreja').order_by('nome_identificacao')
        else: # Se nenhuma igreja ativa, mostra de todas as permitidas
            contas_bancarias = ContaBancaria.objects.filter(igreja__in=allowed_churches).select_related('igreja').order_by('igreja__nome_igreja', 'nome_identificacao')
        # --- Fim Lógica de Filtragem Inicial ---

        can_edit = has_finance_edit_permission(request.user)

        context = {
            'contas_bancarias': contas_bancarias,
            'organizacao': organizacao,
            'can_edit_finance': can_edit,
            'titulo_pagina': 'Contas Bancárias/Caixas'
        }
        return render(request, 'financeiro/contas_bancarias/lista_contas_bancarias.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar contas bancárias para organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao listar as contas bancárias: {e}")
        return redirect('financeiro:painel_financeiro')


@check_permission(has_finance_edit_permission) # MODIFICADO
def criar_conta_bancaria(request): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    igreja_inicial_para_form = None 


    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar contas ou não está associado a nenhuma igreja específica.")
        return redirect('financeiro:lista_contas_bancarias')

    if request.method == 'POST':
        # Ao submeter, o form pega a igreja do request.POST se o campo estiver habilitado,
        # ou usa a instance.igreja se estiver desabilitado (o que não é o caso aqui para criação)
        # Passamos igreja_selecionada_inicial=request.igreja_ativa para o form __init__
        # para que ele possa desabilitar o campo e torná-lo não obrigatório se necessário.
        form = ContaBancariaForm(request.POST, organizacao=organizacao, user=request.user, allowed_churches=allowed_churches, igreja_selecionada_inicial=request.igreja_ativa)
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

                if not is_admin_org(request.user) and nova_conta.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                    # Não levanta exceção aqui, deixa o form ser re-renderizado com a mensagem
                else:
                    nova_conta.save()
                    messages.success(request, f'Conta/Caixa "{nova_conta.nome_identificacao}" para a igreja "{nova_conta.igreja.nome_igreja}" cadastrada com sucesso!')
                    return redirect('financeiro:lista_contas_bancarias')
            except ValueError as ve: # Captura o ValueError que levantamos
                pass # A mensagem já foi adicionada, o formulário será re-renderizado

            except Exception as e:
                 logger.exception(f"Erro ao salvar conta bancária para organização {organizacao.id}")
                 messages.error(request, f'Erro ao salvar conta/caixa: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
  
        # --- Lógica para pré-selecionar a igreja no formulário GET ---
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_inicial_para_form = request.igreja_ativa
        elif allowed_churches.count() == 1 and not is_admin_org(request.user): # Admin Org pode querer escolher

            igreja_unica_permitida = allowed_churches.first()
            igreja_inicial_para_form = igreja_unica_permitida
        form = ContaBancariaForm(organizacao=organizacao, user=request.user, allowed_churches=allowed_churches, igreja_selecionada_inicial=igreja_inicial_para_form)

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': 'Adicionar Nova Conta Bancária/Caixa'
    }
    return render(request, 'financeiro/contas_bancarias/form_conta_bancaria.html', context)

@check_permission(has_finance_edit_permission) # MODIFICADO
def editar_conta_bancaria(request, pk): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    conta_bancaria = get_object_or_404(ContaBancaria, pk=pk, igreja__in=allowed_churches)

    if request.method == 'POST':
        form = ContaBancariaForm(request.POST, instance=conta_bancaria, organizacao=organizacao, user=request.user, allowed_churches=allowed_churches)
        if form.is_valid():
            try:
                conta_editada = form.save(commit=False)
                if not is_admin_org(request.user) and conta_editada.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida.")
                else:
                    conta_editada.save()
                    messages.success(request, 'Conta Bancária/Caixa atualizada com sucesso!')
                    return redirect('financeiro:lista_contas_bancarias')
            except Exception as e:
                 logger.exception(f"Erro ao editar conta bancária {pk} para organização {organizacao.id}")
                 messages.error(request, f'Erro ao salvar conta/caixa: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = ContaBancariaForm(instance=conta_bancaria, organizacao=organizacao, user=request.user, allowed_churches=allowed_churches)

    context = {
        'form': form,
        'organizacao': organizacao,
        'conta_bancaria': conta_bancaria,
        'titulo_pagina': f'Editar Conta/Caixa: {conta_bancaria.nome_identificacao}'
    }
    return render(request, 'financeiro/contas_bancarias/form_conta_bancaria.html', context)

@check_permission(has_finance_edit_permission) # MODIFICADO
def excluir_conta_bancaria(request, pk): # noqa: E302
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
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
            logger.exception(f"Erro ao excluir conta bancária {pk} para organização {organizacao.id}")
            messages.error(request, f'Erro ao excluir conta/caixa: {e}')
        return redirect('financeiro:lista_contas_bancarias')
    else:
        context = {
            'conta_bancaria': conta_bancaria,
            'organizacao': organizacao,
            'titulo_pagina': 'Confirmar Exclusão de Conta/Caixa'
            }
        return render(request, 'financeiro/contas_bancarias/confirmar_excluir_conta.html', context)

# ==================================================
# ========= FIM: VIEWS PARA CONTAS BANCÁRIAS =========
# ==================================================






# --- Fechamento de Caixa (Refatorado) ---
@check_permission(has_finance_view_permission) # MODIFICADO
def lista_fechamentos_caixa(request): # noqa: E302
    """ Lista os fechamentos de caixa da organização. """
    organizacao = get_organizacao_or_error(request)
    
    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    try:
        allowed_churches = get_allowed_churches_for_user(request.user)
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
           fechamentos = FechamentoCaixa.objects.filter(igreja=request.igreja_ativa).select_related('igreja').order_by('-data_fim')
        else:        
        # allowed_churches já foi definida no início do try
        # Filtra pelos fechamentos das igrejas permitidas
            fechamentos = FechamentoCaixa.objects.filter(igreja__in=allowed_churches).select_related('igreja').order_by('-data_fim')
        # Permissão para criar novo fechamento
        can_edit = has_finance_edit_permission(request.user)
        context = {
            'fechamentos': fechamentos,
            'organizacao': organizacao,
            'can_edit_finance': can_edit, # Passa para o template
        }
        return render(request, 'financeiro/fechamentos/lista_fechamentos_caixa.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar fechamentos para organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao listar os fechamentos: {e}")
        return redirect('financeiro:painel_financeiro')

# financeiro/views.py
# ... (imports e outras views como estão) ...

@check_permission(has_finance_edit_permission) # MODIFICADO
def criar_fechamento_caixa(request): # noqa: E302
    """
    ETAPA 1: Exibe o formulário para selecionar igreja/período (GET)
    ou valida a seleção e mostra a pré-visualização (POST inicial).
    """
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)

    igreja_inicial_para_form = None
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        igreja_inicial_para_form = request.igreja_ativa
    elif allowed_churches.count() == 1 and not is_admin_org(request.user):
        igreja_inicial_para_form = allowed_churches.first()

    form = FechamentoCaixaForm(request.POST or None, 
                               organizacao=organizacao, 
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
            observacoes = form.cleaned_data.get('observacoes', '') # Pega observações para passar adiante

            # 1. Verificar se a igreja pertence às permitidas (redundante se o form filtrou, mas seguro)
            if not is_admin_org(request.user) and igreja_selecionada not in allowed_churches:
                messages.error(request, "Erro: Igreja selecionada inválida.")
                # Re-renderiza o form inicial com o erro, passando o form já instanciado
                context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Criar Fechamento de Caixa'}
                return render(request, 'financeiro/fechamentos/criar_fechamento_caixa.html', context)

            # 2. Verificar sobreposição (mantido aqui)
            sobreposicao = FechamentoCaixa.objects.filter(
                Q(igreja=igreja_selecionada),
                Q(data_inicio__lte=data_fim) & Q(data_fim__gte=data_inicio)
            ).exists()
            if sobreposicao:
                messages.error(request, f"Já existe um fechamento de caixa para a igreja '{igreja_selecionada.nome_igreja}' que se sobrepõe ao período selecionado.")
                # Re-renderiza o form inicial com o erro, passando o form já instanciado
                context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Criar Fechamento de Caixa'}
                return render(request, 'financeiro/fechamentos/criar_fechamento_caixa.html', context)

            # 3. Buscar receitas e despesas ABERTAS para a pré-visualização
            receitas = Receitas.objects.filter(igreja=igreja_selecionada, data__range=(data_inicio, data_fim), fechado=False).select_related('membro')
            despesas = Despesas.objects.filter(igreja=igreja_selecionada, data__range=(data_inicio, data_fim), fechado=False).select_related('categoria')

            # 4. Calcular totais provisórios
            total_entradas = receitas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            total_saidas = despesas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
            saldo_final = total_entradas - total_saidas

            # 5. Preparar contexto para o template de CONFIRMAÇÃO
            context_confirmacao = {
                'organizacao': organizacao,
                'igreja_selecionada': igreja_selecionada,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'observacoes': observacoes, # Passa as observações
                'receitas': receitas,
                'despesas': despesas,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo_final': saldo_final,
                'can_edit_finance': has_finance_edit_permission(request.user), # Adicionar esta linha
                'titulo_pagina': 'Confirmar Fechamento de Caixa'
            }
            # Renderiza o template de CONFIRMAÇÃO
            return render(request, 'financeiro/fechamentos/confirmar_fechamento_caixa.html', context_confirmacao)

        except Exception as e:
            logger.exception(f"Erro ao preparar pré-visualização do fechamento para organização {organizacao.id}")
            messages.error(request, f'Erro ao preparar pré-visualização: {e}')
            # Volta para o form inicial em caso de erro inesperado, passando o form já instanciado
            context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Criar Fechamento de Caixa'}
            return render(request, 'financeiro/fechamentos/criar_fechamento_caixa.html', context)
        
        
        else: # Se o form NÃO for válido no POST
            # A mensagem de erro já deve ter sido adicionada pelo form.errors
            # Apenas re-renderiza o template com o form contendo os erros.
            pass # O código abaixo do if/else já lida com isso

    # Se GET ou form inválido no POST, renderiza o form inicial
    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Criar Fechamento de Caixa'}
    return render(request, 'financeiro/fechamentos/criar_fechamento_caixa.html', context)

# --- FIM DA VIEW criar_fechamento_caixa MODIFICADA ---

# --- NOVA VIEW para finalizar o fechamento ---
@check_permission(has_finance_edit_permission) # MODIFICADO
def finalizar_fechamento_caixa(request): # noqa: E302
    """
    ETAPA 2: Recebe o POST da página de confirmação e efetivamente
    cria o FechamentoCaixa e marca as transações como fechadas.
    """
    organizacao = get_organizacao_or_error(request)

    if request.method != 'POST':
        messages.error(request, "Ação inválida.")
        return redirect('financeiro:criar_fechamento_caixa') # Volta para o início

    try:
        # Pegar dados dos campos hidden do POST
        igreja_id = request.POST.get('igreja_id')
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

        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date() # Converte string para date
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        # --- REFAZER AS VERIFICAÇÕES E CÁLCULOS (IMPORTANTE!) ---
        # Não confiar nos totais passados, recalcular com base nas transações ABERTAS atuais.

        # 1. Verificar sobreposição novamente (segurança extra)
        sobreposicao = FechamentoCaixa.objects.filter(
            Q(igreja=igreja_selecionada),
            Q(data_inicio__lte=data_fim) & Q(data_fim__gte=data_inicio)
        ).exists()
        if sobreposicao:
            messages.error(request, f"Erro: Um fechamento sobreposto foi criado enquanto você confirmava. Tente novamente.")
            return redirect('financeiro:criar_fechamento_caixa')

        # 2. Buscar receitas e despesas ABERTAS no período para a igreja
        receitas = Receitas.objects.filter(igreja=igreja_selecionada, data__range=(data_inicio, data_fim), fechado=False)
        despesas = Despesas.objects.filter(igreja=igreja_selecionada, data__range=(data_inicio, data_fim), fechado=False)

        # 3. Calcular totais
        total_entradas = receitas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        total_saidas = despesas.aggregate(Sum('valor'))['valor__sum'] or Decimal(0)
        saldo_final = total_entradas - total_saidas

        # 4. Criar o registro de Fechamento
        novo_fechamento = FechamentoCaixa.objects.create(
            igreja=igreja_selecionada,
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

        messages.success(request, f'Caixa da igreja "{igreja_selecionada.nome_igreja}" fechado com sucesso para o período {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}!')
        return redirect('financeiro:lista_fechamentos_caixa')

    except PermissionDenied as pd:
        messages.error(request, str(pd))
        return redirect('financeiro:criar_fechamento_caixa')
    except Exception as e:
        logger.exception(f"Erro ao finalizar fechamento de caixa para organização {organizacao.id}")
        messages.error(request, f'Erro ao finalizar fechamento de caixa: {e}')
        # Volta para o início do processo em caso de erro
        return redirect('financeiro:criar_fechamento_caixa')

# --- FIM DA NOVA VIEW ---

# ... (restante das views: detalhe_fechamento_caixa, reabrir_fechamento_caixa, etc.) ...


@check_permission(has_finance_view_permission) # MODIFICADO
def detalhe_fechamento_caixa(request, pk): # noqa: E302
    """ Mostra os detalhes de um fechamento específico. """
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    # Garante que o fechamento pertence às igrejas permitidas
    fechamento = get_object_or_404(FechamentoCaixa, pk=pk, igreja__in=allowed_churches)
    try:
        # Busca as receitas e despesas que FORAM incluídas neste fechamento (fechado=True)
        # Não precisa filtrar por allowed_churches aqui, pois o fechamento já foi validado
        receitas = Receitas.objects.filter(igreja=fechamento.igreja, data__range=(fechamento.data_inicio, fechamento.data_fim), fechado=True).select_related('membro') # noqa
        despesas = Despesas.objects.filter(igreja=fechamento.igreja, data__range=(fechamento.data_inicio, fechamento.data_fim), fechado=True).select_related('categoria')

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
            'organizacao': organizacao,
            'can_edit_finance': can_edit, # Para o botão Reabrir
        }
        return render(request, 'financeiro/fechamentos/detalhe_fechamento_caixa.html', context)
    except Exception as e:
        logger.exception(f"Erro ao detalhar fechamento {pk} para organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao carregar os detalhes do fechamento: {e}")
        return redirect('financeiro:lista_fechamentos_caixa')


@check_permission(has_finance_edit_permission) # MODIFICADO
def reabrir_fechamento_caixa(request, pk): # noqa: E302
    """ Reabre um caixa fechado, marcando as receitas/despesas como abertas novamente. """
    organizacao = get_organizacao_or_error(request)
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
            logger.exception(f"Erro ao reabrir fechamento {pk} para organização {organizacao.id}")
            messages.error(request, f'Erro ao reabrir o caixa: {e}')
            return redirect('financeiro:detalhe_fechamento_caixa', pk=pk) # Volta para o detalhe em caso de erro
    else:
        # Se GET, mostrar página de confirmação para reabrir
        context = {'fechamento': fechamento, 'organizacao': organizacao}
        return render(request, 'financeiro/fechamentos/confirmar_reabrir_caixa.html', context)


# --- Relatórios ---
@check_permission(has_finance_view_permission) # MODIFICADO
def relatorio_mensal_detalhe(request, pk): # noqa: E302
    """ Gera o relatório formatado de um fechamento de caixa específico. """
    organizacao = get_organizacao_or_error(request)
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
        categorias_despesa_org = CategoriaDespesa.objects.filter(organizacao=organizacao).order_by('pk')

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
            'organizacao': organizacao,
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
        logger.exception(f"Erro ao gerar relatório para fechamento {pk}, organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao gerar o relatório: {e}")
        return redirect('financeiro:lista_fechamentos_caixa')


# Remover a classe FechamentoCaixaService e as funções soltas buscar_dados_fechamento,
# calcular_totais_fechamento, fechar_caixa, pois a lógica foi incorporada na view criar_fechamento_caixa.
# Remover a definição duplicada de lista_fechamentos_caixa.
# Remover a view editar_fechamento_caixa antiga, pois a lógica de reabrir é diferente.



# ====================================================
# ========= INÍCIO: VIEWS PARA FORNECEDORES =========
# ====================================================

@check_permission(has_finance_view_permission) # MODIFICADO
def lista_fornecedores(request):
    """ Lista os fornecedores da organização, com filtros. """
    organizacao = get_organizacao_or_error(request)
    try:
        # Fornecedores são ligados diretamente à organização, não precisam de filtro de igreja
        fornecedores_qs = Fornecedor.objects.filter(organizacao=organizacao).order_by('nome')
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
            'organizacao': organizacao,
            'current_q': query,
            'current_status_ativo': status_selecionado,
            'can_edit_finance': can_edit,
        }
        return render(request, 'financeiro/fornecedores/lista_fornecedores.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar fornecedores para organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao listar os fornecedores: {e}")
        return redirect('financeiro:painel_financeiro') # Redireciona para painel em caso de erro

@check_permission(has_finance_edit_permission) # MODIFICADO
def criar_fornecedor(request): # noqa: E302
    """ Cria um novo fornecedor para a organização. """
    organizacao = get_organizacao_or_error(request)
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            try:
                fornecedor = form.save(commit=False)
                fornecedor.organizacao = organizacao
                fornecedor.ativo = True # Novos fornecedores começam ativos
                fornecedor.save()
                messages.success(request, f'Fornecedor "{fornecedor.nome}" criado com sucesso!')
                return redirect('financeiro:lista_fornecedores')
            except Exception as e:
                # Verifica erro de unicidade (nome duplicado na organização)
                if 'UNIQUE constraint' in str(e) and 'organizacao_id, nome' in str(e):
                     messages.error(request, f'Erro: Já existe um fornecedor com o nome "{form.cleaned_data.get("nome")}" nesta organização.')
                else:
                    logger.exception(f"Erro ao salvar novo fornecedor para organização {organizacao.id}")
                    messages.error(request, f'Erro ao salvar fornecedor: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = FornecedorForm()

    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': 'Criar Novo Fornecedor'}
    return render(request, 'financeiro/fornecedores/form_fornecedor.html', context)

@check_permission(has_finance_edit_permission) # MODIFICADO
def editar_fornecedor(request, pk): # noqa: E302
    """ Edita um fornecedor existente da organização. """
    organizacao = get_organizacao_or_error(request)
    # Validação de organização já feita no get_object_or_404
    fornecedor = get_object_or_404(Fornecedor, pk=pk, organizacao=organizacao)

    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=fornecedor)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Fornecedor "{fornecedor.nome}" atualizado com sucesso!')
                return redirect('financeiro:lista_fornecedores')
            except Exception as e:
                 if 'UNIQUE constraint' in str(e) and 'organizacao_id, nome' in str(e):
                     messages.error(request, f'Erro: Já existe outro fornecedor com o nome "{form.cleaned_data.get("nome")}" nesta organização.')
                 else:
                    logger.exception(f"Erro ao editar fornecedor {pk} para organização {organizacao.id}")
                    messages.error(request, f'Erro ao salvar fornecedor: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = FornecedorForm(instance=fornecedor)

    context = {'form': form, 'organizacao': organizacao, 'titulo_pagina': f'Editar Fornecedor: {fornecedor.nome}', 'fornecedor': fornecedor}
    return render(request, 'financeiro/fornecedores/form_fornecedor.html', context)

@check_permission(has_finance_edit_permission) # MODIFICADO
def alternar_status_fornecedor(request, pk): # noqa: E302
    """ Ativa ou desativa um fornecedor (requer método POST). """
    organizacao = get_organizacao_or_error(request)
    # Validação de organização já feita no get_object_or_404
    fornecedor = get_object_or_404(Fornecedor, pk=pk, organizacao=organizacao)

    if request.method == 'POST':
        try:
            fornecedor.ativo = not fornecedor.ativo
            fornecedor.save()
            status_msg = "ativado" if fornecedor.ativo else "desativado"
            messages.success(request, f'Fornecedor "{fornecedor.nome}" foi {status_msg} com sucesso.')
        except Exception as e:
            logger.exception(f"Erro ao alternar status do fornecedor {pk} para organização {organizacao.id}")
            messages.error(request, f'Erro ao alterar status do fornecedor: {e}')
    else:
        messages.error(request, "Ação inválida (requer POST).")

    # Redireciona de volta para a lista, preservando filtros se possível
    redirect_url = request.META.get('HTTP_REFERER', reverse('financeiro:lista_fornecedores'))
    return redirect(redirect_url)


# ==================================================
# ========= FIM: VIEWS PARA FORNECEDORES =========
# ==================================================

@check_permission(has_finance_edit_permission) # MODIFICADO
def editar_categoria_despesa(request, pk): # noqa: E302
    """ Edita uma categoria de despesa existente. """
    organizacao = get_organizacao_or_error(request)
    # Validação de organização já feita no get_object_or_404
    categoria = get_object_or_404(CategoriaDespesa, pk=pk, organizacao=organizacao)

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
                 if 'UNIQUE constraint' in str(e) and 'organizacao_id, nome' in str(e):
                     messages.error(request, f'Erro: Já existe uma categoria com o nome "{form.cleaned_data.get("nome")}" nesta organização.')
                 else:
                    logger.exception(f"Erro ao editar categoria {pk} para organização {organizacao.id}")
                    messages.error(request, f'Erro ao salvar categoria: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        # GET: Exibe o formulário preenchido com os dados da categoria
        form = CategoriaDespesaForm(instance=categoria)

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': f'Editar Categoria: {categoria.nome}',
        'categoria': categoria # Passa o objeto para o template, se necessário
    }
    # Reutilizar o template do formulário de cadastro
    return render(request, 'financeiro/categorias/form_categoria.html', context)

@check_permission(has_finance_edit_permission) # MODIFICADO
def excluir_categoria_despesa(request, pk): # noqa: E302
    """ Exclui uma categoria de despesa (requer POST e confirmação). """
    organizacao = get_organizacao_or_error(request)
    # Validação de organização já feita no get_object_or_404
    categoria = get_object_or_404(CategoriaDespesa, pk=pk, organizacao=organizacao)

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
            logger.exception(f"Erro ao excluir categoria {pk} para organização {organizacao.id}")
            messages.error(request, f'Erro ao excluir categoria: {e}')
        return redirect('financeiro:lista_categorias_despesa')
    else:
        # GET: Mostrar página de confirmação
        context = {'categoria': categoria, 'organizacao': organizacao}
        return render(request, 'financeiro/categorias/confirmar_excluir_categoria.html', context)


# ====================================================
# ========= INÍCIO: VIEWS PARA CONTAS A PAGAR =========
# ====================================================

@check_permission(has_finance_view_permission) # MODIFICADO
def lista_contas_pagar(request): # noqa: E302
    """ Lista as contas a pagar da organização, com filtros. """
    organizacao = get_organizacao_or_error(request)
    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    
    try:
        allowed_churches = get_allowed_churches_for_user(request.user) # Base de igrejas permitidas
        igreja_contexto_filtro_dados = None # Igreja que efetivamente filtrará os dados principais
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_contexto_filtro_dados = request.igreja_ativa
            contas_qs = ContaPagar.objects.filter(organizacao=organizacao, igreja=request.igreja_ativa).select_related(
                'igreja', 'fornecedor', 'categoria', 'conta_debito').order_by('data_vencimento', 'status')
        else:        
             # Se nenhuma igreja ativa globalmente, começa com todas as permitidas
            contas_qs = ContaPagar.objects.filter(organizacao=organizacao, igreja__in=allowed_churches).select_related(
                'igreja', 'fornecedor', 'categoria', 'conta_debito'
            ).order_by('data_vencimento', 'status')

        # --- Filtros GET ---
        query = request.GET.get('q', '')
        status_filtro = request.GET.get('status', 'PEN') # Default para Pendente
        venc_inicio = request.GET.get('venc_inicio', '')
        venc_fim = request.GET.get('venc_fim', '')
        igreja_id = request.GET.get('igreja', '')
        fornecedor_id_get = request.GET.get('fornecedor', '')

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

        # Opcional: Atualizar status para VENCIDA (pode impactar performance)
        # hoje = timezone.now().date()
        # ContaPagar.objects.filter(
        #     organizacao=organizacao, status='PEN', data_vencimento__lt=hoje
        # ).update(status='VEN')

        # Para os filtros no template
        # --- Lógica para o dropdown de filtro de igreja no template ---
        

        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igrejas_para_filtro_template = Igreja.objects.filter(pk=request.igreja_ativa.pk)
            igreja_id_selecionada_template = str(request.igreja_ativa.pk)
        else:
            igrejas_para_filtro_template = allowed_churches
            igreja_id_selecionada_template = igreja_id # O que foi passado no GET
        
        
        
        fornecedores_org = Fornecedor.objects.filter(organizacao=organizacao, ativo=True)

        # Permissão para criar/pagar
        can_edit = has_finance_edit_permission(request.user)

        context = {
            'contas': contas_qs,
            'organizacao': organizacao,
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
            'can_edit_finance': can_edit,
        }
        return render(request, 'financeiro/contas_pagar/lista_contas_pagar.html', context)
    except Exception as e:
        logger.exception(f"Erro ao listar contas a pagar para organização {organizacao.id}")
        messages.error(request, f"Ocorreu um erro ao listar as contas a pagar: {e}")
        return redirect('financeiro:painel_financeiro')

@check_permission(has_finance_edit_permission) # MODIFICADO
def criar_conta_pagar(request): # noqa: E302
    """ Cria uma nova conta a pagar (ou uma parcela). """
    organizacao = get_organizacao_or_error(request)
    igreja_padrao_para_form = None # Inicializa

    allowed_churches = get_allowed_churches_for_user(request.user)

    # Se não for admin e não tiver igrejas permitidas, não pode criar
    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar contas a pagar ou não está associado a nenhuma igreja específica.")
        return redirect('financeiro:lista_contas_pagar')

    if request.method == 'POST': # O form já valida se a igreja selecionada é permitida
        form = ContaPagarForm(request.POST,
                              organizacao=organizacao,
                              allowed_churches=allowed_churches,
                              user=request.user, # Passar o usuário
                              igreja_selecionada_inicial=request.igreja_ativa) # Passar igreja ativa
        if form.is_valid():
            try:
                conta = form.save(commit=False)
                conta.organizacao = organizacao
                conta.usuario_criacao = request.user
                # Se o campo igreja foi desabilitado e uma igreja ativa foi passada, usar a igreja ativa
                if form.fields['igreja'].disabled and request.igreja_ativa:
                    conta.igreja = request.igreja_ativa

                
                conta.status = 'PEN' # Garante que começa como Pendente

                # Validações extras
                if not is_admin_org(request.user) and conta.igreja not in allowed_churches: raise ValidationError("Igreja inválida")
                if conta.fornecedor.organizacao != organizacao: raise ValidationError("Fornecedor inválido")
                if conta.categoria and conta.categoria.organizacao != organizacao: raise ValidationError("Categoria inválida")

                conta.save()
                messages.success(request, "Conta a pagar criada com sucesso!")
                # Redirecionar para lista ou para adicionar outra? Por enquanto, lista.
                return redirect('financeiro:lista_contas_pagar')
            except ValidationError as ve: # Captura erros de validação específicos
                 messages.error(request, f"Erro de validação: {ve}")
            except Exception as e:
                logger.exception(f"Erro ao salvar nova conta a pagar para organização {organizacao.id}")
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
                              organizacao=organizacao,
                              allowed_churches=allowed_churches,
                              user=request.user, # Adicionar user
                              igreja_selecionada_inicial=igreja_para_form_get) # Usar igreja_para_form_get

    context = {        
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': 'Criar Nova Conta a Pagar / Parcela'
    }
    return render(request, 'financeiro/contas_pagar/form_conta_pagar.html', context)

@check_permission(has_finance_edit_permission) # MODIFICADO
def registrar_pagamento_conta_pagar(request, pk): # noqa: E302
    """ Registra o pagamento de uma conta a pagar específica. """
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    # Permite pagar apenas contas Pendentes ou Vencidas E que pertençam às igrejas permitidas
    conta = get_object_or_404(ContaPagar, pk=pk, organizacao=organizacao, status__in=['PEN', 'VEN'], igreja__in=allowed_churches)

    # Envolver em uma transação atômica para garantir consistência
    if request.method == 'POST':
        # Passa instance=conta para o form saber qual conta está sendo paga
        # O form já filtra a conta_debito pela organização
        form = RegistrarPagamentoContaPagarForm(request.POST, request.FILES, instance=conta, organizacao=organizacao) # Passa organizacao
        if form.is_valid():
            try:
                with transaction.atomic(): # Garante que ou tudo funciona ou nada é salvo
                    conta_paga = form.save(commit=False) # O save do form já define status='PAG'

                    # Validação extra da conta de débito (form já deve ter filtrado)
                    if conta_paga.conta_debito and conta_paga.conta_debito.igreja.organizacao != organizacao:
                        raise ValidationError("Conta de débito selecionada inválida.")

                    # Salva a ContaPagar com status 'PAG' e dados do pagamento
                    # O form já define o status para 'PAG' no seu método save
                    conta_paga.save()

                    # --- CRIAR A DESPESA CORRESPONDENTE ---
                    if conta_paga.status == 'PAG' and conta_paga.valor_pago is not None:
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
                            categoria=conta_paga.categoria, # Usa a mesma categoria da ContaPagar
                            observacao=f"Pagamento referente à conta a pagar ID {conta_paga.pk}. {conta_paga.observacoes or ''}".strip(),
                            fechado=False, # Despesa começa aberta
                            conta_bancaria=conta_paga.conta_debito,
                            origem_conta_pagar=conta_paga, # Vincula à ContaPagar
                            usuario_registro_pagamento=request.user # Usuário que registrou o pagamento
                        )
                        logger.info(f"Despesa criada automaticamente para a ContaPagar ID {conta_paga.pk}.")

                        # A ATUALIZAÇÃO DO SALDO DA CONTA BANCÁRIA É FEITA PELO MÉTODO SAVE DA DESPESA.
                     # --- FIM CRIAR DESPESA CORRESPONDENTE ---
    

                    messages.success(request, f"Pagamento da conta '{conta.descricao}' registrado com sucesso!")
                    return redirect('financeiro:lista_contas_pagar')

            except ValidationError as ve:
                 messages.error(request, f"Erro de validação: {ve}")
            except Exception as e:
                 logger.exception(f"Erro ao registrar pagamento da conta {pk} para organização {organizacao.id}")
                 logger.error(f"Erro ao registrar pagamento da conta {pk} para organização {organizacao.id}: {e}\n{traceback.format_exc()}")
                 messages.error(request, f"Erro ao registrar pagamento: {e}")
        else:
            messages.error(request, "Formulário de pagamento inválido. Verifique os campos.")
    else:
        # GET: Exibe o formulário preenchido com sugestões
        # Passa a organização para filtrar conta_debito
        form = RegistrarPagamentoContaPagarForm(instance=conta, organizacao=organizacao)
    # Verifica se o campo conta_debito tem opções disponíveis
    # Se o queryset estiver vazio, significa que não há contas bancárias cadastradas para a organização
    if not form.fields['conta_debito'].queryset.exists():
        messages.warning(request, "Não há contas bancárias/caixas cadastradas para a sua organização. Cadastre uma conta para registrar pagamentos.")
        # Opcional: Redirecionar para a página de cadastro de contas bancárias se ela existir
    context = {
        'form': form,
        'conta': conta, # Passa a conta para exibir detalhes no template
        'organizacao': organizacao,
        'titulo_pagina': f"Registrar Pagamento: {conta.descricao}"
    }
    return render(request, 'financeiro/contas_pagar/form_registrar_pagamento.html', context)

# ==================================================
# ========= FIM: VIEWS PARA CONTAS A PAGAR =========
# ==================================================


# financeiro/views.py
# ... (imports e views existentes) ...

# ====================================================
# ========= CONTINUAÇÃO: VIEWS PARA CONTAS A PAGAR =========
# ====================================================

@check_permission(has_finance_edit_permission) # MODIFICADO
def editar_conta_pagar(request, pk): # noqa: E302
    """ Edita uma conta a pagar existente (se ainda não estiver paga ou cancelada). """
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_user(request.user)
    # Permite editar apenas contas Pendentes ou Vencidas E das igrejas permitidas
    conta = get_object_or_404(ContaPagar, pk=pk, organizacao=organizacao, status__in=['PEN', 'VEN'], igreja__in=allowed_churches)

    if request.method == 'POST':
        form = ContaPagarForm(request.POST, instance=conta, organizacao=organizacao, allowed_churches=allowed_churches)
        if form.is_valid():
            try:
                conta_editada = form.save(commit=False)
                # Validações extras (redundantes se o form filtra, mas seguro)
                if not is_admin_org(request.user) and conta_editada.igreja not in allowed_churches: raise ValidationError("Igreja inválida")
                if conta_editada.fornecedor.organizacao != organizacao: raise ValidationError("Fornecedor inválido")
                if conta_editada.categoria and conta_editada.categoria.organizacao != organizacao: raise ValidationError("Categoria inválida")

                conta_editada.save()
                messages.success(request, f'Conta a pagar "{conta.descricao}" atualizada com sucesso!')
                return redirect('financeiro:lista_contas_pagar')
            except ValidationError as ve:
                 messages.error(request, f"Erro de validação: {ve}")
            except Exception as e:
                logger.exception(f"Erro ao editar conta a pagar {pk} para organização {organizacao.id}")
                messages.error(request, f'Erro ao salvar conta a pagar: {e}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        # GET: Exibe o formulário preenchido
        form = ContaPagarForm(instance=conta, organizacao=organizacao, allowed_churches=allowed_churches)

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': f'Editar Conta: {conta.descricao}',
        'conta': conta # Passa o objeto para o template
    }
    # Reutiliza o mesmo template do formulário de criação
    return render(request, 'financeiro/contas_pagar/form_conta_pagar.html', context)

@check_permission(has_finance_view_permission) # MODIFICADO
def detalhe_conta_pagar(request, pk): # noqa: E302
    """ Exibe os detalhes completos de uma conta a pagar. """
    organizacao = get_organizacao_or_error(request)
    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    allowed_churches = get_allowed_churches_for_user(request.user)
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        # Se uma igreja ativa está selecionada, garante que a conta pertence a ela
        conta = get_object_or_404(ContaPagar, pk=pk, organizacao=organizacao, igreja=request.igreja_ativa)
    else:    
        # Garante que a conta pertence às igrejas permitidas
        conta = get_object_or_404(ContaPagar, pk=pk, organizacao=organizacao, igreja__in=allowed_churches)
    # Usar select_related para otimizar

    conta = ContaPagar.objects.select_related(
        # Re-busca com select_related após garantir a permissão
        'igreja', 'fornecedor', 'categoria', 'conta_debito', 'usuario_criacao'
    ).get(pk=pk, organizacao=organizacao) # A permissão já foi verificada acima

    # Permissão para editar/pagar/cancelar
    can_edit = has_finance_edit_permission(request.user)

    context = {
        'conta': conta,
        'organizacao': organizacao,
        'can_edit_finance': can_edit, # Passa para o template
    }
    return render(request, 'financeiro/contas_pagar/detalhe_conta_pagar.html', context)

@check_permission(has_finance_edit_permission) # MODIFICADO
def cancelar_conta_pagar(request, pk): # noqa: E302
    """ Marca uma conta a pagar como Cancelada (requer POST). """
    organizacao = get_organizacao_or_error(request)
    
# --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    allowed_churches = get_allowed_churches_for_user(request.user)
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        # Se uma igreja ativa está selecionada, garante que a conta pertence a ela
        conta = get_object_or_404(ContaPagar, pk=pk, organizacao=organizacao, status__in=['PEN', 'VEN'], igreja=request.igreja_ativa)
    else:
        # Permite cancelar apenas contas Pendentes ou Vencidas E das igrejas permitidas
        conta = get_object_or_404(ContaPagar, pk=pk, organizacao=organizacao, status__in=['PEN', 'VEN'], igreja__in=allowed_churches)
        # conta = get_object_or_404(ContaPagar, pk=pk, organizacao=organizacao, status__in=['PEN', 'VEN']) # Linha duplicada removida

    if request.method == 'POST':
        try:
            conta.status = 'CAN'
            conta.save(update_fields=['status', 'data_atualizacao']) # Atualiza só os campos necessários
            messages.success(request, f'Conta a pagar "{conta.descricao}" cancelada com sucesso.')
        except Exception as e:
            logger.exception(f"Erro ao cancelar conta a pagar {pk} para organização {organizacao.id}")
            messages.error(request, f'Erro ao cancelar a conta: {e}')
        return redirect('financeiro:lista_contas_pagar')
    else:
        # GET não deve cancelar, pode mostrar confirmação ou redirecionar
        messages.error(request, "Ação inválida (requer POST).")
        return redirect('financeiro:lista_contas_pagar')

# ==================================================
# ========= FIM: VIEWS PARA CONTAS A PAGAR =========
# ==================================================
@check_permission(is_finance_leader) # MODIFICADO
def painel_lideranca_financeiro(request):
    organizacao_usuario = get_organizacao_or_error(request)
    allowed_churches_base_financeiro = get_allowed_churches_for_user(request.user)

    print(f"DEBUG (Financeiro): Usuário: {request.user.username}, É Líder Financeiro: {is_finance_leader(request.user)}")
    print(f"DEBUG (Financeiro): allowed_churches_base_financeiro: {list(allowed_churches_base_financeiro)}")

    if not allowed_churches_base_financeiro.exists() and not is_admin_org(request.user):
        messages.warning(request, "Nenhuma igreja encontrada para visualização no painel de liderança financeira.")
        return render(request, 'financeiro/painel_lideranca_financeiro.html', {
            'nenhuma_igreja_permissao': True,
            'organizacao_usuario': organizacao_usuario,
            'titulo_dashboard': f"Liderança Financeira - {organizacao_usuario.nome_fantasia}"
        })

    try:
        churches_for_queries = None
        igreja_em_foco_obj = None # Objeto da igreja que está em foco (pode ser do global ou do filtro da página)
        ver_apenas_entidade_foco = False # True se formos ver SÓ a igreja_em_foco_obj, sem descendentes
        
        # Título do escopo da igreja (será definido abaixo)
        titulo_escopo_igreja = f"Consolidado - {organizacao_usuario.nome_fantasia}" 
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
                    ver_apenas_entidade_foco = True # Ao selecionar uma congregação, vemos apenas ela
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
                    titulo_escopo_igreja = f"Consolidado - {organizacao_usuario.nome_fantasia}"
            else: # Nenhum filtro na página e nenhuma igreja_ativa global (value='')
                igreja_em_foco_obj = None
                id_selecionado_filtro_pagina = '' # Garante que "todas" esteja selecionado
                titulo_escopo_igreja = f"Consolidado - {organizacao_usuario.nome_fantasia}"

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
                churches_for_queries = Igreja.objects.filter(pk__in=list(pks_to_include), organizacao=organizacao_usuario)
                
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
                'organizacao_usuario': organizacao_usuario,
                'titulo_dashboard': f"Liderança Financeira - {organizacao_usuario.nome_fantasia}",
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
            'organizacao_usuario': organizacao_usuario, 
        }
        return render(request, 'financeiro/painel_lideranca_financeiro.html', context)
    except Exception as e:
        logger.exception(f"Erro ao carregar painel de liderança financeira para organização {organizacao_usuario.id if organizacao_usuario else 'N/A'}: {e}")
        messages.error(request, f"Ocorreu um erro ao carregar o painel de liderança financeira: {e}")
        return render(request, 'financeiro/painel_lideranca_financeiro.html', {
            'erro_painel': True, 
            'organizacao_usuario': organizacao_usuario
        })
