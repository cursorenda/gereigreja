# c:\Gereigreja\secretaria\views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Membro, Tiposstatus
from .forms import MembroForm
from django.http import HttpResponse, Http404
from datetime import datetime
from django.conf import settings
import os
import shutil
import logging
import zipfile
from django.db.models import Count, Q
import json
from django.contrib.auth.decorators import login_required, user_passes_test
from configuracao.models import PerfilUsuario, Organizacao, Igreja # Adicionado Igreja
from django.core.exceptions import PermissionDenied
from datetime import datetime, date # Importe 'date' aqui também
from django.db.models import Count, Q, F, Value, Case, When, BooleanField # Adicione F, Value, Case, When, BooleanField
from django.urls import reverse_lazy # Para login_url

# --- IMPORTAR UTILS DE PERMISSÃO PARA secretaria (Consolidado) ---
from django.db.models.functions import Extract # Adicione esta linha para Extract
from .utils import has_membro_view_permission, has_membro_edit_permission, get_allowed_churches_for_membros, is_secretaria_leader, is_admin_org # Adicionar is_secretaria_leader
from django.urls import reverse



# Configura o logger (mantido como estava)



logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('backup_log.txt') # Considere um nome de arquivo mais específico ou um caminho absoluto
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# --- Função auxiliar para obter organização (evita repetição) ---
def get_organizacao_or_error(request):
    """
    Obtém a organização do usuário logado.
    Levanta PermissionDenied se não autenticado, superuser, ou erro de perfil.
    Levanta Http404 se o perfil não tem organização associada.
    Retorna o objeto Organizacao em caso de sucesso.
    """
    if not request.user.is_authenticated:
        # PermissionDenied é suficiente
        raise PermissionDenied("Usuário não autenticado.")
    
    if request.user.is_superuser:
        messages.info(request, "Superusuários devem usar o painel Admin para secretaria global.")
        raise PermissionDenied("Superusuário não acessa esta área.")
    
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Perfil de usuário não encontrado. Contate o suporte.")
        raise PermissionDenied("Perfil de usuário não encontrado.")
    
    organizacao = perfil.organizacao
    if not organizacao:
        messages.error(request, "Seu usuário não está associado a nenhuma organização.")
        raise Http404("Organização não encontrada para o usuário.")
    
    if not organizacao.ativo:
        messages.warning(request, f"A organização '{organizacao.nome_fantasia}' não está ativa. Contate o suporte do sistema.")
        raise PermissionDenied(f"Acesso negado: Organização '{organizacao.nome_fantasia}' inativa.")

    # --- VERIFICAÇÃO DO STATUS DA ASSINATURA ---
    try:
        assinatura = organizacao.assinatura # Acesso via related_name
        status_validos = ['ativa', 'gratuita']
        
        if assinatura.status not in status_validos:
            # Se o status não for válido, verifica se a organização é elegível para o gratuito
            # OU se um período de cortesia está ativo e válido.
            if not assinatura.is_periodo_cortesia_valido():
                # Se não há cortesia válida, e a assinatura não é 'ativa' ou 'gratuita'
                # E não é o caso de ser 'vencida' mas a organização ser elegível para o gratuito
                if not (assinatura.status == 'vencida' and organizacao.verificar_elegibilidade_plano_gratuito()):
                    # Adiciona mensagem de aviso, mas não bloqueia se estiver indo para a página de assinatura
                    if not request.user.is_superuser and request.path != reverse('configuracao:gerenciar_assinatura'):
                        messages.warning(request, f"Sua assinatura do plano {assinatura.plano.get_nome_display() if assinatura.plano else ''} está {assinatura.get_status_display()}. Por favor, regularize sua situação ou ative sua cortesia.")
                        # Aqui, em vez de raise PermissionDenied, a view chamadora decidirá se redireciona
                        # para 'configuracao:gerenciar_assinatura' se a assinatura não estiver OK.
                        # Por enquanto, apenas avisamos. O bloqueio efetivo (redirecionamento) será feito na view.

    except AssinaturaOrganizacao.DoesNotExist:
        # Se não tem assinatura E não é elegível para gratuita
        if not organizacao.verificar_elegibilidade_plano_gratuito():
            if not request.user.is_superuser and request.path != reverse('configuracao:gerenciar_assinatura'):
                    messages.warning(request, f"Sua assinatura do plano {assinatura.plano.get_nome_display() if assinatura.plano else ''} está {assinatura.get_status_display()}. Por favor, regularize sua situação.")
                    messages.warning(request, "Sua organização não possui uma assinatura ativa. Por favor, escolha um plano ou ative sua cortesia.")
# --- FIM VERIFICAÇÃO DA ASSINATURA ---
    
    return organizacao
    
    # --- Fim função auxiliar ---


@login_required
def index(request):
    if request.user.is_superuser:
        return redirect('admin:index')
    try:
        organizacao = get_organizacao_or_error(request)
        total_membros_ativos_count = 0
        novos_membros_ultimo_mes_count = 0

        titulo_contextual = f"Visão Geral - {organizacao.nome_fantasia}"

        allowed_churches_secretaria = get_allowed_churches_for_membros(request.user)
        membros_base_qs = Membro.objects.none()

        if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
            membros_base_qs = Membro.objects.filter(igreja=request.igreja_ativa)
            titulo_contextual = f"Visão Geral - Igreja: {request.igreja_ativa.nome_igreja}"
        elif allowed_churches_secretaria.exists():
            membros_base_qs = Membro.objects.filter(igreja__in=allowed_churches_secretaria)
            titulo_contextual += " (Consolidado)"
        # Se não houver igreja ativa nem igrejas permitidas (exceto para admin org que vê tudo),
        # os counts permanecerão zero, o que é correto.
        # Para Admin Org, get_allowed_churches_for_membros deve retornar todas da organização.
        
        if membros_base_qs.exists() or (is_admin_org(request.user) and not request.igreja_ativa): # Garante que Admin Org veja dados da organização se nenhuma igreja ativa
            if is_admin_org(request.user) and not request.igreja_ativa and not allowed_churches_secretaria.exists(): # Caso específico de Admin Org sem igrejas no perfil e sem igreja ativa
                membros_base_qs = Membro.objects.filter(igreja__organizacao=organizacao)

            total_membros_ativos_count = membros_base_qs.filter(
                status__considerar_ativo_relatorios=True
            ).count()

            from datetime import timedelta 
            um_mes_atras = date.today() - timedelta(days=30)
            novos_membros_ultimo_mes_count = membros_base_qs.filter(
                data_entrada__gte=um_mes_atras
            ).count() 
        
                
        # A variável 'can_view' não estava definida aqui. A permissão é passada ao contexto abaixo.
        # print(f"DEBUG VIEW: has_membro_view_permission = {has_membro_view_permission(request.user)}") # Exemplo de como poderia ser
        print(f"DEBUG VIEW: novos_membros_ultimo_mes_count = {novos_membros_ultimo_mes_count} (Tipo: {type(novos_membros_ultimo_mes_count)})")
        print(f"DEBUG VIEW: total_membros_ativos_count = {total_membros_ativos_count} (Tipo: {type(total_membros_ativos_count)})")
        
        context = {
            'organizacao': organizacao,
            'user': request.user,
            'titulo_pagina': titulo_contextual,
            'can_view_membros': has_membro_view_permission(request.user), # Permissão para o template
            'can_edit_membros': has_membro_edit_permission(request.user), # Permissão para o template

            'total_membros_ativos': total_membros_ativos_count,
            'novos_membros_ultimo_mes': novos_membros_ultimo_mes_count,
            'proximo_evento': "Nenhum evento próximo.", # Placeholder
            'igreja_ativa_atual': request.igreja_ativa # Passa a igreja ativa para o template

        }
        return render(request, 'secretaria/index.html', context)
    except (PermissionDenied, Http404):
         return redirect('login')


@login_required
def dashboard(request):
    organizacao = get_organizacao_or_error(request)
    allowed_churches_secretaria = get_allowed_churches_for_membros(request.user)
    titulo_contextual_dashboard = f"Dashboard - {organizacao.nome_fantasia}"
    membros_para_relatorios = Membro.objects.none()




    # Verificar permissão de visualização de membros antes de prosseguir
    if not has_membro_view_permission(request.user):
        messages.warning(request, "Você não tem permissão para visualizar os dados do dashboard.")
        context = {
            'organizacao': organizacao,
            'titulo_pagina': titulo_contextual_dashboard,
            'status_data_json': json.dumps([]),
            'genero_data_json': json.dumps([]),
            'faixa_etaria_data_json': json.dumps([]),
            'total_membros_dashboard': 0,
            'novos_membros_30_dias': 0,
            'aniversariantes_mes_atual_count': 0,
            'media_idade_membros': 0,

            'aniversariantes_proximos': [],
            'permissao_negada': True # Flag para o template, se necessário
        }
        return render(request, 'dashboard.html', context)

    allowed_churches = get_allowed_churches_for_membros(request.user)

    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
        membros_para_relatorios = Membro.objects.filter(
            igreja=request.igreja_ativa,
            status__considerar_ativo_relatorios=True
        )
        titulo_contextual_dashboard = f"Dashboard - Igreja: {request.igreja_ativa.nome_igreja}"
    elif allowed_churches_secretaria.exists():
        membros_para_relatorios = Membro.objects.filter(
            igreja__in=allowed_churches_secretaria,
            status__considerar_ativo_relatorios=True
        )
        titulo_contextual_dashboard += " (Visão Consolidada)"
    elif is_admin_org(request.user): # Admin da Org sem igrejas no perfil e sem igreja ativa
        membros_para_relatorios = Membro.objects.filter(
            igreja__organizacao=organizacao,
            status__considerar_ativo_relatorios=True
        )
        titulo_contextual_dashboard += " (Visão da Organização)"
    else:
        # Se não tem igreja ativa, nem igrejas permitidas (e não é admin org),
        # membros_para_relatorios continuará como queryset vazio.
        messages.info(request, "Nenhuma igreja selecionada ou permitida para visualização de dados no dashboard.")
        # Os cálculos abaixo resultarão em zero ou listas vazias, o que é o comportamento esperado.

    # --- Fim Lógica de Filtragem Inicial ---



    # 1. Contagem por Status
    status_data_qs = membros_para_relatorios.values( # Renomeado para evitar conflito
        'status__status'
    ).annotate(
        total=Count('chave')
    ).order_by('status__status')
    status_data_list = [{'status': item['status__status'], 'total': item['total']} for item in status_data_qs]
    logger.info(f"Dashboard - Status Data (Filtrado): {status_data_list}")

    # 2. Contagem por Gênero (para gráfico)
    genero_data_qs = membros_para_relatorios.values('genero').annotate( # Renomeado
        total=Count('chave')
    )
    genero_map = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
    aggregated_genero = {}
    for item in genero_data_qs:
        genero_display = genero_map.get(item['genero'], 'Não Informado')
        aggregated_genero[genero_display] = aggregated_genero.get(genero_display, 0) + item['total']
    genero_data_normalized = [{'genero': key, 'total': value} for key, value in aggregated_genero.items()]
    logger.info(f"Dashboard - Gênero Data Normalized (Filtrado e Agregado): {genero_data_normalized}")

    # 3. Contagem por Faixa Etária
    membros_com_nascimento = membros_para_relatorios.filter(
        nascimento__isnull=False
    ).values_list('nascimento', flat=True)
    idades = []
    hoje_data = date.today() # Renomeado para evitar conflito com datetime.date
    for nascimento in membros_com_nascimento:
        if nascimento:
            try:
                idade = hoje_data.year - nascimento.year - ((hoje_data.month, hoje_data.day) < (nascimento.month, nascimento.day))
                idades.append(idade)
            except AttributeError:
                logger.warning(f"Valor inesperado encontrado para data de nascimento ao calcular idade: {nascimento}")
        else:
            logger.warning("Valor None encontrado para nascimento mesmo após filtro isnull=False.")

    faixas = {
        '0-5 anos': 0,
        '6-10 anos': 0,
        '11-14 anos': 0,
        '15-17 anos': 0,
        '18-30 anos': 0, # Chave correta
        '31-50 anos': 0,
        '51-65 anos': 0,
        'Mais de 65 anos': 0,
        'Não Informado': membros_para_relatorios.filter(nascimento__isnull=True).count() # Contar quem não tem nascimento
    }
    for idade_val in idades:
        if 0 <= idade_val <= 5:
            faixas['0-5 anos'] += 1
        elif 6 <= idade_val <= 10:
            faixas['6-10 anos'] += 1
        elif 11 <= idade_val <= 14:
            faixas['11-14 anos'] += 1
        elif 15 <= idade_val <= 17:
            faixas['15-17 anos'] += 1
        elif 18 <= idade_val <= 30: # Acesso à chave correta
            faixas['18-30 anos'] += 1
        elif 31 <= idade_val <= 50:
            faixas['31-50 anos'] += 1
        elif 51 <= idade_val <= 65:
            faixas['51-65 anos'] += 1
        elif idade_val > 65:
            faixas['Mais de 65 anos'] += 1
        
        # Membros sem nascimento já foram contados na inicialização do dicionário 'faixas'

    faixa_etaria_data = [{'faixa_etaria': k, 'total': v} for k, v in faixas.items()]
    logger.info(f"Dashboard - Faixa Etária Data (Filtrado): {faixa_etaria_data}")

    # 4. Total de Membros para o Dashboard
    total_membros_dashboard = membros_para_relatorios.count()
    logger.info(f"Dashboard - Total de Membros (Filtrado): {total_membros_dashboard}")

    # 5. Próximos Aniversariantes
    mes_atual = hoje_data.month
    dia_atual = hoje_data.day
    aniversariantes_qs = membros_para_relatorios.filter(nascimento__isnull=False).annotate(
        nascimento_month=Extract('nascimento', 'month'),
        nascimento_day=Extract('nascimento', 'day'),
        passed_this_year=Case(
            When(nascimento_month__lt=mes_atual, then=Value(True)),
            When(nascimento_month=mes_atual, nascimento_day__lt=dia_atual, then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    ).order_by('passed_this_year', 'nascimento_month', 'nascimento_day')
    limite_aniversariantes = 10
    aniversariantes_proximos = list(aniversariantes_qs[:limite_aniversariantes])
    logger.info(f"Dashboard - Próximos Aniversariantes (até {limite_aniversariantes}): {[m.nome for m in aniversariantes_proximos]}")

     # --- NOVOS DADOS PARA CARDS DE RESUMO ---
    # Card 2: Novos Membros (Últimos 30 dias)
    from datetime import timedelta # Certifique-se que timedelta está importado de datetime
    
    trinta_dias_atras = hoje_data - timedelta(days=30) # hoje_data já foi definida
    novos_membros_30_dias = membros_para_relatorios.filter( # Usar membros_para_relatorios
        # status__considerar_ativo_relatorios=True, # Já filtrado em membros_para_relatorios
        
        data_entrada__gte=trinta_dias_atras
    ).count()

    # Card 3: Aniversariantes do Mês Atual
    aniversariantes_mes_atual_count = membros_para_relatorios.filter( # Usar membros_para_relatorios
        # status__considerar_ativo_relatorios=True, # Já filtrado em membros_para_relatorios
    nascimento__month=hoje_data.month
    ).count()

    # Card 4: Média de Idade dos Membros Ativos
     # Calcular idade em Python para maior compatibilidade com SQLite
    idades_para_media = []
    membros_ativos_com_nascimento = membros_para_relatorios.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
    
    for nascimento_dt in membros_ativos_com_nascimento:
        if nascimento_dt: # Garante que a data não é None
            idade = hoje_data.year - nascimento_dt.year - ((hoje_data.month, hoje_data.day) < (nascimento_dt.month, nascimento_dt.day))
            idades_para_media.append(idade)

    if idades_para_media:
        media_idade_membros = round(sum(idades_para_media) / len(idades_para_media))
    else:
        media_idade_membros = 0
    # --- FIM NOVOS DADOS PARA CARDS ---





    context = {
        'status_data_json': json.dumps(status_data_list),
        'genero_data_json': json.dumps(genero_data_normalized),
        'faixa_etaria_data_json': json.dumps(faixa_etaria_data),
        'total_membros_dashboard': total_membros_dashboard,
        'novos_membros_30_dias': novos_membros_30_dias,     # Card 2
        'aniversariantes_mes_atual_count': aniversariantes_mes_atual_count, # Card 3
        'media_idade_membros': media_idade_membros,         # Card 4
        'organizacao': organizacao,
        'aniversariantes_proximos': aniversariantes_proximos,
        'titulo_pagina': titulo_contextual_dashboard,
        'igreja_ativa_atual': request.igreja_ativa

    }
    return render(request, 'dashboard.html', context)


@login_required
@user_passes_test(has_membro_view_permission, login_url=reverse_lazy('login'), redirect_field_name=None)
def lista_membros(request):
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)

   # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        membros_queryset = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        membros_queryset = Membro.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user): # Admin da Org sem igrejas no perfil e sem igreja ativa
        membros_queryset = Membro.objects.filter(igreja__organizacao=organizacao)
    else:
        membros_queryset = Membro.objects.none()
    # --- Fim Lógica de Filtragem Inicial ---

    membros_queryset = membros_queryset.select_related('igreja', 'status').order_by('nome')


    query = request.GET.get('q')
    if query:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=query) | Q(apelido__icontains=query)
        )
    # Filtro GET de igreja na página (só se nenhuma igreja ativa globalmente)
    igreja_id_get = request.GET.get('igreja')
    if igreja_id_get and not request.igreja_ativa:
        if allowed_churches.filter(pk=igreja_id_get).exists() or is_admin_org(request.user):
            membros_queryset = membros_queryset.filter(igreja_id=igreja_id_get)

    can_edit = has_membro_edit_permission(request.user)
    igrejas_para_filtro_template = allowed_churches if not request.igreja_ativa else Igreja.objects.filter(pk=request.igreja_ativa.pk)

    context = {
        'membros': membros_queryset,
        'organizacao': organizacao,
        'query': query,
        'can_edit_membros': can_edit,
        'titulo_pagina': f"Lista de Membros{': ' + request.igreja_ativa.nome_igreja if request.igreja_ativa else ' (Consolidado)'}",
        'igrejas_org': igrejas_para_filtro_template, # Para o filtro da página
        'igreja_selecionada': str(request.igreja_ativa.pk) if request.igreja_ativa else igreja_id_get,
    }
    return render(request, 'secretaria/lista_membros.html', context)


@login_required
@user_passes_test(has_membro_edit_permission, login_url=reverse_lazy('login'), redirect_field_name=None)
def editar_membro(request, membro_id):
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)

    if request.method == 'POST':
        # Ao editar, a igreja do membro não deve mudar via seletor global, mas o form precisa das allowed_churches
        form = MembroForm(request.POST, instance=membro, 
                          organizacao=organizacao, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=membro.igreja) # Passa a igreja atual do membro
        print(f"DEBUG POST - request.POST: {request.POST}") # Veja os dados brutos do POST
        if form.is_valid():
            print(f"DEBUG POST - form.cleaned_data: {form.cleaned_data}") # Veja os dados limpos
            nascimento_do_form = form.cleaned_data.get('nascimento')
            print(f"DEBUG POST - Nascimento do form.cleaned_data: {nascimento_do_form}, Tipo: {type(nascimento_do_form)}")
            try:
                membro_editado = form.save(commit=False)
                print(f"DEBUG POST - membro_editado.nascimento ANTES do save: {membro_editado.nascimento}, Tipo: {type(membro_editado.nascimento)}")
                if not is_admin_org(request.user) and membro_editado.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                else:
                    membro_editado.save()
                    messages.success(request, f'Membro "{membro_editado.nome}" atualizado com sucesso!')
                    return redirect('secretaria:lista_membros')
            except Exception as e:
                print(f"DEBUG POST - Exceção ao salvar: {e}")

                logger.exception(f"Erro ao salvar edição do membro {membro_id} para organização {organizacao.id}")
                messages.error(request, f"Ocorreu um erro ao salvar as alterações: {e}")
        else:
            # Adicionar este print para depuração quando o formulário é carregado (GET)
            print(f"DEBUG POST - Form inválido. Erros: {form.errors.as_json()}")

            messages.error(request, "Erro ao atualizar membro. Verifique os campos.")
    else:
        form = MembroForm(instance=membro, 
                          organizacao=organizacao, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=membro.igreja) # Passa a igreja atual do membro
        # Print para quando o formulário é carregado (GET)
        print(f"DEBUG GET - Editando Membro ID: {membro.pk}")
        print(f"DEBUG GET - Valor de membro.nascimento no BD: {membro.nascimento}")
        print(f"DEBUG GET - Tipo de membro.nascimento no BD: {type(membro.nascimento)}")

    context = {
        'form': form,
        'membro_id': membro_id,
        'organizacao': organizacao,
        'titulo_pagina': f'Editar Membro: {membro.nome}'
    }
    return render(request, 'secretaria/editar_membro.html', context)


@login_required
@user_passes_test(has_membro_edit_permission, login_url=reverse_lazy('login'), redirect_field_name=None)
def criar_membro(request):
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja_inicial_para_form = None


    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar membros ou não está associado a nenhuma igreja específica.")
        return redirect('secretaria:lista_membros')

    if request.method == 'POST':
        # Ao criar, a igreja_ativa (se houver) deve ser a sugestão inicial
        form = MembroForm(request.POST, 
                          organizacao=organizacao, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=request.igreja_ativa) # Passa request.igreja_ativa
        if form.is_valid():
            print(f"DEBUG POST - form.cleaned_data: {form.cleaned_data}")
            nascimento_do_form = form.cleaned_data.get('nascimento')
            print(f"DEBUG POST - Nascimento do form.cleaned_data: {nascimento_do_form}, Tipo: {type(nascimento_do_form)}")

            try:
                membro_editado = form.save(commit=False)

                novo_membro = form.save(commit=False)
                if not is_admin_org(request.user) and novo_membro.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                else:
                    novo_membro.save()
                    messages.success(request, f'Membro "{novo_membro.nome}" cadastrado com sucesso!')
                    return redirect('secretaria:lista_membros')
            except Exception as e:
                logger.exception(f"Erro ao salvar novo membro para organização {organizacao.id}")
                messages.error(request, f"Ocorreu um erro ao salvar o membro: {e}")
        else:
             messages.error(request, "Erro ao cadastrar membro. Verifique os campos.")
    else:
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_inicial_para_form = request.igreja_ativa
        elif allowed_churches.count() == 1:
            igreja_inicial_para_form = allowed_churches.first()

        form = MembroForm(organizacao=organizacao, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=igreja_inicial_para_form)

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': 'Cadastrar Novo Membro'
    }
    return render(request, 'secretaria/criar_membro.html', context)


# --- Views de Backup (Restritas a Superusuários) ---
@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/login/') # login_url pode ser ajustado se necessário
def backup_database_view(request): # Adicionado 'request'
    data_hora_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dir = os.path.join(settings.BASE_DIR, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = f"backup_banco_{data_hora_atual}.sqlite3"
    backup_path = os.path.join(backup_dir, backup_file)
    db_path = settings.DATABASES['default']['NAME']
    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"Backup do banco de dados realizado com sucesso em: {backup_path}")
        return True, backup_path
    except Exception as e:
        logger.error(f"Erro ao realizar backup do banco de dados: {e}")
        return False, None

@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/login/') # login_url pode ser ajustado
def backup_site_files_view(request): # Adicionado 'request'
    data_hora_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_dir = os.path.join(settings.BASE_DIR, 'backup')
    os.makedirs(backup_dir, exist_ok=True)
    backup_file = f"backup_arquivos_{data_hora_atual}.zip"
    backup_path = os.path.join(backup_dir, backup_file)
    site_path = settings.BASE_DIR
    folders_to_ignore = [
        os.path.join(settings.BASE_DIR, 'backup'),
        os.path.join(settings.BASE_DIR, 'static'), # Se staticfiles_dirs estiver configurado, pode ser redundante
        os.path.join(settings.BASE_DIR, 'staticfiles'), # Diretório do collectstatic
        os.path.join(settings.BASE_DIR, 'media'),
        os.path.join(settings.BASE_DIR, '__pycache__'),
        os.path.join(settings.BASE_DIR, '.venv'),
        os.path.join(settings.BASE_DIR, 'venv'),
        os.path.join(settings.BASE_DIR, '.git'),
        # Adicionar outros diretórios/arquivos se necessário
    ]
    try:
        logger.info(f"Iniciando backup dos arquivos do site.")
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(site_path):
                # Ignorar diretórios
                dirs[:] = [d for d in dirs if os.path.join(root, d) not in folders_to_ignore and not d.startswith('.') and d != '__pycache__']

                if any(root.startswith(folder) for folder in folders_to_ignore):
                    continue

                for file in files:
                    if file.startswith('.'):
                        continue
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, site_path)
                    zipf.write(file_path, arcname=relative_path)
        logger.info(f"Backup dos arquivos do site realizado com sucesso em: {backup_path}")
        return True, backup_path
    except Exception as e:
        logger.exception(f"Erro ao realizar backup dos arquivos do site")
        return False, None

@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='/admin/login/')
def backup_page(request):
    if request.method == 'POST':
        fazer_backup_database = 'backup_database' in request.POST
        fazer_backup_files = 'backup_files' in request.POST
        storage = messages.get_messages(request)
        storage.used = True
        db_success, file_success = None, None
        db_path, file_path = None, None

        if fazer_backup_database:
            db_success, db_path = backup_database_view(request) # Passado 'request'
        if fazer_backup_files:
            file_success, file_path = backup_site_files_view(request) # Passado 'request'

        if fazer_backup_database and fazer_backup_files:
            if db_success and file_success:
                messages.success(request, f'Backup Completo realizado com sucesso! <br>Banco: {db_path} <br> Arquivos: {file_path}')
            elif db_success:
                messages.warning(request, f'Backup parcial! <br>Banco: {db_path} <br> Erro nos arquivos.')
            elif file_success:
                 messages.warning(request, f'Backup parcial! <br>Arquivos: {file_path} <br> Erro no banco.')
            else:
                messages.error(request, 'Erro ao fazer backup do banco de dados e dos arquivos!')
        elif fazer_backup_database:
            if db_success:
                messages.success(request, f'Backup do banco de dados realizado com sucesso: {db_path}')
            else:
                messages.error(request, 'Erro ao fazer backup do banco de dados!')
        elif fazer_backup_files:
            if file_success:
                messages.success(request, f'Backup dos arquivos realizado com sucesso: {file_path}')
            else:
                messages.error(request, 'Erro ao fazer backup dos arquivos!')
        else:
            messages.warning(request, 'Nenhum tipo de backup selecionado!')
        return redirect('backup_page')
    return render(request, 'secretaria/backup_page.html')

# --- NOVA VIEW PARA ALTERNAR STATUS DO MEMBRO ---
@login_required
@user_passes_test(has_membro_edit_permission, login_url=reverse_lazy('login'), redirect_field_name=None)
def alternar_status_membro(request, membro_id):
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)

    # Defina os nomes dos seus Tiposstatus padrão para ativo e inativo
    # Estes nomes devem corresponder exatamente aos cadastrados no seu modelo Tiposstatus
    NOME_STATUS_ATIVO_PADRAO = "MEMBRO ATIVO"
    NOME_STATUS_INATIVO_PADRAO = "MEMBRO INATIVO"

    if request.method == 'POST':
        try:
            status_ativo_padrao = Tiposstatus.objects.get(status=NOME_STATUS_ATIVO_PADRAO)
            status_inativo_padrao = Tiposstatus.objects.get(status=NOME_STATUS_INATIVO_PADRAO)

            acao = ""
            if membro.status and membro.status.considerar_ativo_relatorios:
                # Se está ativo para relatórios, inativa
                membro.status = status_inativo_padrao
                acao = "inativado (para relatórios)"
            else:
                # Se está inativo para relatórios (ou sem status), ativa
                membro.status = status_ativo_padrao
                acao = "ativado (para relatórios)"

            membro.save(update_fields=['status'])
            messages.success(request, f'Membro "{membro.nome}" foi {acao} com sucesso.')

        except Tiposstatus.DoesNotExist:
            messages.error(request, f"Erro: Os status '{NOME_STATUS_ATIVO_PADRAO}' ou '{NOME_STATUS_INATIVO_PADRAO}' não foram encontrados. Verifique o cadastro de Tipos de Status.")
        except Exception as e:
            logger.exception(f"Erro ao alternar status do membro {membro_id} para organização {organizacao.id}")
            messages.error(request, f"Ocorreu um erro ao alternar o status do membro: {e}")
        return redirect('secretaria:lista_membros') # Sempre redireciona para a lista
    else:
        # GET request não é permitido para esta ação
        messages.error(request, "Ação inválida.")
        return redirect('secretaria:lista_membros')
# --- FIM NOVA VIEW ---

@login_required
@user_passes_test(is_secretaria_leader, login_url='core:home') # Apenas líderes da secretaria
def painel_lideranca_secretaria(request):
    try:
        # Chama get_organizacao_or_error no início para validar o acesso à organização
        organizacao_usuario = get_organizacao_or_error(request) # Usar a função centralizada
        # Obtém o conjunto base de igrejas que este líder pode acessar

        allowed_churches_base_secretaria = get_allowed_churches_for_membros(request.user, organizacao_usuario) # Passa organizacao_usuario
        
        print(f"DEBUG (Secretaria): Usuário: {request.user.username}, É Líder Secretaria: {is_secretaria_leader(request.user)}")
        print(f"DEBUG (Secretaria): allowed_churches_base_secretaria: {list(allowed_churches_base_secretaria)}")
        if not allowed_churches_base_secretaria.exists() and not is_admin_org(request.user):

            messages.warning(request, "Nenhuma igreja encontrada para visualização no painel de liderança da secretaria.")
            # Adiciona organizacao_usuario ao contexto para o template base
            return render(request, 'secretaria/painel_lideranca_secretaria.html', {
                'nenhuma_igreja_permissao': True, 
                'organizacao_usuario': organizacao_usuario,
                'titulo_dashboard': f"Liderança Secretaria - {organizacao_usuario.nome_fantasia}"
            })


        # --- Lógica do Filtro de Igreja/Regional (similar ao financeiro) ---
        churches_for_queries = None # Igrejas que serão usadas para buscar os dados
        titulo_escopo_igreja = f"Consolidado - {organizacao_usuario.nome_fantasia}" 
        ver_apenas_entidade_foco = False
        
        titulo_escopo_igreja = f"Consolidado - {organizacao_usuario.nome_fantasia}"
        
        # Para o dropdown de filtro na página (será ajustado abaixo)

        opcoes_filtro_pagina = allowed_churches_base_secretaria.order_by('nome_igreja')
        igreja_id_filtro_selecionado_template_lider_sec = request.GET.get('igreja_filtro', '')
        if request.igreja_ativa and request.igreja_ativa in allowed_churches_base_secretaria:
            igreja_em_foco_obj = request.igreja_ativa
            
            temp_pks_dropdown = {request.igreja_ativa.pk}
            if hasattr(request.igreja_ativa, 'get_descendants'):
                desc_dropdown_qs = request.igreja_ativa.get_descendants(include_self=False).filter(
                    pk__in=allowed_churches_base_secretaria.values_list('pk', flat=True)
                )
                if desc_dropdown_qs.exists():
                    temp_pks_dropdown.update(desc_dropdown_qs.values_list('pk', flat=True))
            opcoes_filtro_pagina = Igreja.objects.filter(pk__in=list(temp_pks_dropdown)).order_by('nome_igreja')

            if not igreja_id_filtro_selecionado_template_lider_sec: # Se filtro da página vazio, assume o global
                igreja_id_filtro_selecionado_template_lider_sec = str(request.igreja_ativa.pk)
            # Se o filtro da página é a própria igreja global


            if igreja_id_filtro_selecionado_template_lider_sec == str(request.igreja_ativa.pk):
                igreja_em_foco_obj = request.igreja_ativa
                # Se o filtro GET da página é explicitamente a igreja global E ela tem descendentes, vemos SÓ ela

                if request.GET.get('igreja_filtro') == str(request.igreja_ativa.pk) and \
                   hasattr(request.igreja_ativa, 'get_descendants') and \
                   request.igreja_ativa.get_descendants(include_self=False).filter(pk__in=allowed_churches_base_secretaria.values_list('pk', flat=True)).exists():
                    ver_apenas_entidade_foco = True
                    titulo_escopo_igreja = f"Apenas: {request.igreja_ativa.nome_igreja}"
                else: # Filtro da página vazio ou igreja global é folha -> visão de rede
                    ver_apenas_entidade_foco = False
                    titulo_escopo_igreja = f"Rede: {request.igreja_ativa.nome_igreja}" if len(temp_pks_dropdown) > 1 else f"Igreja: {request.igreja_ativa.nome_igreja}"
            else: # Filtro da página selecionou uma descendente específica
                try:
                    igreja_descendente_selecionada = opcoes_filtro_pagina.get(pk=igreja_id_filtro_selecionado_template_lider_sec)
                    igreja_em_foco_obj = igreja_descendente_selecionada
                    ver_apenas_entidade_foco = True
                    titulo_escopo_igreja = f"Igreja: {igreja_descendente_selecionada.nome_igreja}"
                    # id_selecionado_filtro_pagina já é o da descendente

                except Igreja.DoesNotExist:
                    igreja_id_filtro_selecionado_template_lider_sec = str(request.igreja_ativa.pk)
                    igreja_em_foco_obj = request.igreja_ativa
                    ver_apenas_entidade_foco = False
                    titulo_escopo_igreja = f"Rede: {request.igreja_ativa.nome_igreja}" if len(temp_pks_dropdown) > 1 else f"Igreja: {request.igreja_ativa.nome_igreja}"
        else: 
            opcoes_filtro_pagina = allowed_churches_base_secretaria.order_by('nome_igreja')
            if igreja_id_filtro_selecionado_template_lider_sec:
                try:
                    igreja_em_foco_obj = allowed_churches_base_secretaria.get(pk=igreja_id_filtro_selecionado_template_lider_sec)
                    ver_apenas_entidade_foco = False 
                    # Título será definido ao construir pks_to_include

                except Igreja.DoesNotExist:
                    messages.warning(request, "Igreja selecionada no filtro inválida. Mostrando consolidado.")
                    igreja_id_filtro_selecionado_template_lider_sec = ''
                    igreja_em_foco_obj = None
                    titulo_escopo_igreja = f"Consolidado - {organizacao_usuario.nome_fantasia}"
            else: 
                igreja_em_foco_obj = None
                igreja_id_filtro_selecionado_template_lider_sec = ''
                titulo_escopo_igreja = f"Consolidado - {organizacao_usuario.nome_fantasia}"
       
        # --- Construir churches_for_queries e título final com base no foco e flag ---
        if igreja_em_foco_obj:
            if ver_apenas_entidade_foco:
                churches_for_queries = Igreja.objects.filter(pk=igreja_em_foco_obj.pk)
                # Título já deve estar como "Apenas:" ou "Igreja:"

            else: 
                pks_to_include = {igreja_em_foco_obj.pk}
                if hasattr(igreja_em_foco_obj, 'get_descendants'):
                    desc_qs = igreja_em_foco_obj.get_descendants(include_self=False).filter(
                        pk__in=allowed_churches_base_secretaria.values_list('pk', flat=True)
                    )
                    if desc_qs.exists():
                        pks_to_include.update(desc_qs.values_list('pk', flat=True))
                churches_for_queries = Igreja.objects.filter(pk__in=list(pks_to_include), organizacao=organizacao_usuario)
                if len(pks_to_include) > 1 and not ver_apenas_entidade_foco:
                    titulo_escopo_igreja = f"Rede: {igreja_em_foco_obj.nome_igreja}"
                elif not ver_apenas_entidade_foco:
                    titulo_escopo_igreja = f"Igreja: {igreja_em_foco_obj.nome_igreja}"
        else: 
            churches_for_queries = allowed_churches_base_secretaria
            # titulo_escopo_igreja já é "Consolidado - Organização"

        if not churches_for_queries or not churches_for_queries.exists():
            messages.warning(request, "Nenhuma igreja corresponde aos filtros aplicados.")
            return render(request, 'secretaria/painel_lideranca_secretaria.html', {
                'nenhuma_igreja_filtro': True, 
                'organizacao_usuario': organizacao_usuario,
                'titulo_dashboard': f"Liderança Secretaria - {organizacao_usuario.nome_fantasia}",
                'igrejas_permitidas_filtro': allowed_churches_base_secretaria.order_by('nome_igreja'),
                'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template_lider_sec,
            })

        # --- Cálculos de dados para o painel da secretaria ---
        total_membros_rede = Membro.objects.filter(
            igreja__in=churches_for_queries, 
            status__considerar_ativo_relatorios=True
        ).count()

        from datetime import date, timedelta # Já importado no topo do arquivo
        hoje_data_lider = date.today()
        trinta_dias_atras_lider = hoje_data_lider - timedelta(days=30)
        novos_membros_rede_30_dias = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status__considerar_ativo_relatorios=True, 
            data_entrada__gte=trinta_dias_atras_lider
        ).count()

        num_igrejas_consideradas = churches_for_queries.count() 
        media_membros_por_igreja = (total_membros_rede / num_igrejas_consideradas) if num_igrejas_consideradas > 0 else 0 # noqa
        media_membros_por_igreja = round(media_membros_por_igreja, 1)

        membros_por_status_qs = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status__considerar_ativo_relatorios=True
        ).values('status__status').annotate(total=Count('chave')).order_by('status__status')
        grafico_membros_status_labels = [item['status__status'] if item['status__status'] else "Sem Status" for item in membros_por_status_qs]
        grafico_membros_status_valores = [item['total'] for item in membros_por_status_qs]

        membros_lideranca_ativos = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status__considerar_ativo_relatorios=True
        )
        genero_data_lider_qs = membros_lideranca_ativos.values('genero').annotate(total=Count('chave'))
        genero_map_lider = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
        aggregated_genero_lider = {}
        for item_gen_lid in genero_data_lider_qs:
            genero_display_lid = genero_map_lider.get(item_gen_lid['genero'], 'Não Informado')
            aggregated_genero_lider[genero_display_lid] = aggregated_genero_lider.get(genero_display_lid, 0) + item_gen_lid['total']
        grafico_membros_genero_labels = [key for key, value in aggregated_genero_lider.items()]
        grafico_membros_genero_valores = [value for key, value in aggregated_genero_lider.items()]

        membros_com_nascimento_lider = membros_lideranca_ativos.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
        idades_lider = []
        for nascimento_lid in membros_com_nascimento_lider:
            if nascimento_lid:
                idade_lid = hoje_data_lider.year - nascimento_lid.year - ((hoje_data_lider.month, hoje_data_lider.day) < (nascimento_lid.month, nascimento_lid.day))
                idades_lider.append(idade_lid)
        faixas_lider = {
            '0-5 anos': 0, '6-10 anos': 0, '11-14 anos': 0, '15-17 anos': 0,
            '18-30 anos': 0, '31-50 anos': 0, '51-65 anos': 0, 'Mais de 65 anos': 0,
            'Não Informado': membros_lideranca_ativos.filter(nascimento__isnull=True).count()
        }
        for idade_val_lid in idades_lider:
            if 0 <= idade_val_lid <= 5: faixas_lider['0-5 anos'] += 1
            elif 6 <= idade_val_lid <= 10: faixas_lider['6-10 anos'] += 1
            elif 11 <= idade_val_lid <= 14: faixas_lider['11-14 anos'] += 1
            elif 15 <= idade_val_lid <= 17: faixas_lider['15-17 anos'] += 1
            elif 18 <= idade_val_lid <= 30: faixas_lider['18-30 anos'] += 1
            elif 31 <= idade_val_lid <= 50: faixas_lider['31-50 anos'] += 1
            elif 51 <= idade_val_lid <= 65: faixas_lider['51-65 anos'] += 1
            elif idade_val_lid > 65: faixas_lider['Mais de 65 anos'] += 1
        grafico_membros_faixa_labels = [k for k, v in faixas_lider.items()]
        grafico_membros_faixa_valores = [v for k, v in faixas_lider.items()]

        context = {
            'titulo_dashboard': f"Liderança Secretaria - {titulo_escopo_igreja}", # Usar o título do escopo
            'total_membros_rede': total_membros_rede,
            'novos_membros_rede_30_dias': novos_membros_rede_30_dias,
            'media_membros_por_igreja': media_membros_por_igreja,
            'grafico_membros_status_labels_json': json.dumps(grafico_membros_status_labels),
            'grafico_membros_status_valores_json': json.dumps(grafico_membros_status_valores),
            'grafico_membros_genero_labels_json': json.dumps(grafico_membros_genero_labels),
            'grafico_membros_genero_valores_json': json.dumps(grafico_membros_genero_valores),
            'grafico_membros_faixa_labels_json': json.dumps(grafico_membros_faixa_labels),
            'grafico_membros_faixa_valores_json': json.dumps(grafico_membros_faixa_valores),
            'igrejas_permitidas_filtro': opcoes_filtro_pagina, 
            'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template_lider_sec,
            'allowed_churches_count': churches_for_queries.count() if churches_for_queries else 0,
            'organizacao_usuario': organizacao_usuario,
        }
        return render(request, 'secretaria/painel_lideranca_secretaria.html', context)
    except PermissionDenied:
        raise 
    except Http404:
        raise
    except Exception as e: 
        org_nome_log = getattr(getattr(getattr(request.user, 'perfil', None), 'organizacao', None), 'nome_fantasia', "N/A")
        logger.exception(f"Erro inesperado no painel de liderança da secretaria para organização '{org_nome_log}': {e}")
        messages.error(request, f"Ocorreu um erro ao carregar o painel de liderança da secretaria: {e}")
        return redirect('secretaria:dashboard')
