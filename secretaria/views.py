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
        raise PermissionDenied("Usuário não autenticado.")
    try:
        # Superusuários não têm uma organização padrão nesta lógica
        if request.user.is_superuser:
             messages.info(request, "Superusuários devem usar o painel Admin para secretaria global.")
             raise PermissionDenied("Superusuário não acessa esta área.")

        perfil = request.user.perfil
        organizacao = perfil.organizacao
        if not organizacao:
            # Situação inesperada para um admin logado
            messages.error(request, "Seu usuário não está associado a nenhuma organização.")
            raise Http404("Organização não encontrada para o usuário.")
        return organizacao
    except PerfilUsuario.DoesNotExist:
        messages.error(request, "Perfil de usuário não encontrado. Contate o suporte.")
        raise PermissionDenied("Perfil de usuário não encontrado.")
    except Exception as e:
         logger.exception(f"Erro inesperado ao obter organização para usuário {request.user.username}")
         messages.error(request, f"Erro interno ao obter organização: {e}")
         raise PermissionDenied("Erro interno ao obter organização.")
# --- Fim função auxiliar ---


@login_required
def index(request):
    if request.user.is_superuser:
        return redirect('admin:index')
    try:
        organizacao = get_organizacao_or_error(request)

        can_view = has_membro_view_permission(request.user)
        can_edit = has_membro_edit_permission(request.user)

        total_membros_ativos_count = 0
        novos_membros_ultimo_mes_count = 0
        # proximo_evento_info = "Nenhum evento próximo." # Placeholder

        if can_view:
            allowed_churches = get_allowed_churches_for_membros(request.user)
            if allowed_churches.exists() or is_admin_org(request.user): # Admin Org pode ver mesmo sem igrejas específicas se a lógica de get_allowed_churches_for_membros retornar todas
                # Se for Admin Org, allowed_churches já deve conter todas as igrejas da organização
                # ou ser um queryset que abrange todas elas.
                membros_visiveis = Membro.objects.filter(igreja__in=allowed_churches)

                total_membros_ativos_count = membros_visiveis.filter(
                    status__considerar_ativo_relatorios=True
                ).count()

                # Para 'novos_membros_ultimo_mes', assumimos um campo 'data_cadastro' no modelo Membro.
                # Ajuste o nome do campo 'data_cadastro' se for diferente no seu modelo.
                from datetime import timedelta # Já importado no topo do arquivo
                um_mes_atras = date.today() - timedelta(days=30)
                novos_membros_ultimo_mes_count = membros_visiveis.filter(
                    data_entrada__gte=um_mes_atras # CORRIGIDO: Usando 'data_entrada'
                ).count()
        print(f"DEBUG VIEW: can_view = {can_view}")
        print(f"DEBUG VIEW: novos_membros_ultimo_mes_count = {novos_membros_ultimo_mes_count} (Tipo: {type(novos_membros_ultimo_mes_count)})")
        print(f"DEBUG VIEW: total_membros_ativos_count = {total_membros_ativos_count} (Tipo: {type(total_membros_ativos_count)})")
        
        context = {
            'organizacao': organizacao,
            'user': request.user,
            'titulo_pagina': 'Página Inicial',
            'can_view_membros': can_view,
            'can_edit_membros': can_edit,
            'total_membros_ativos': total_membros_ativos_count,
            'novos_membros_ultimo_mes': novos_membros_ultimo_mes_count,
            'proximo_evento': "Nenhum evento próximo." # Placeholder
        }
        return render(request, 'secretaria/index.html', context)
    except (PermissionDenied, Http404):
         return redirect('login')


@login_required
def dashboard(request):
    organizacao = get_organizacao_or_error(request)

    # Verificar permissão de visualização de membros antes de prosseguir
    if not has_membro_view_permission(request.user):
        messages.warning(request, "Você não tem permissão para visualizar os dados do dashboard.")
        context = {
            'organizacao': organizacao,
            'titulo_pagina': 'Dashboard da Organização',
            'status_data_json': json.dumps([]),
            'genero_data_json': json.dumps([]),
            'faixa_etaria_data_json': json.dumps([]),
            'total_membros_dashboard': 0,
            'aniversariantes_proximos': [],
            'permissao_negada': True # Flag para o template, se necessário
        }
        return render(request, 'dashboard.html', context)

    allowed_churches = get_allowed_churches_for_membros(request.user)

    if not allowed_churches.exists() and not is_admin_org(request.user):
        # Se não for Admin da Org e não tiver igrejas permitidas, não há dados para mostrar
        messages.info(request, "Nenhuma igreja associada para visualização de dados no dashboard.")
        context = {
            'organizacao': organizacao,
            'titulo_pagina': 'Dashboard da Organização',
            'status_data_json': json.dumps([]),
            'genero_data_json': json.dumps([]),
            'faixa_etaria_data_json': json.dumps([]),
            'total_membros_dashboard': 0,
            'aniversariantes_proximos': [],
        }
        return render(request, 'dashboard.html', context)

    membros_para_relatorios = Membro.objects.filter(
        igreja__in=allowed_churches,  # ALTERAÇÃO PRINCIPAL: Filtra pelas igrejas permitidas
        status__considerar_ativo_relatorios=True
    )

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
    trinta_dias_atras = hoje_data - timedelta(days=30)
    novos_membros_30_dias = Membro.objects.filter(
        igreja__in=allowed_churches,
        status__considerar_ativo_relatorios=True, # Opcional: contar apenas se já entram ativos
        data_entrada__gte=trinta_dias_atras
    ).count()

    # Card 3: Aniversariantes do Mês Atual
    aniversariantes_mes_atual_count = Membro.objects.filter(
        igreja__in=allowed_churches,
        status__considerar_ativo_relatorios=True,
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
        'titulo_pagina': 'Dashboard da Igreja'
    }
    return render(request, 'dashboard.html', context)


@login_required
@user_passes_test(has_membro_view_permission, login_url=reverse_lazy('login'), redirect_field_name=None)
def lista_membros(request):
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)

    # Filtra membros pelas igrejas permitidas
    membros_queryset = Membro.objects.filter(
        igreja__in=allowed_churches
    ).select_related('igreja', 'status').order_by('nome')

    query = request.GET.get('q')
    if query:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=query) | Q(apelido__icontains=query)
        )

    can_edit = has_membro_edit_permission(request.user)

    context = {
        'membros': membros_queryset,
        'organizacao': organizacao,
        'query': query,
        'can_edit_membros': can_edit,
        'titulo_pagina': 'Lista de Membros'
    }
    return render(request, 'secretaria/lista_membros.html', context)


@login_required
@user_passes_test(has_membro_edit_permission, login_url=reverse_lazy('login'), redirect_field_name=None)
def editar_membro(request, membro_id):
    organizacao = get_organizacao_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)

    if request.method == 'POST':
        form = MembroForm(request.POST, instance=membro, organizacao=organizacao, user=request.user, allowed_churches=allowed_churches)
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
                    return redirect('lista_membros')
            except Exception as e:
                print(f"DEBUG POST - Exceção ao salvar: {e}")

                logger.exception(f"Erro ao salvar edição do membro {membro_id} para organização {organizacao.id}")
                messages.error(request, f"Ocorreu um erro ao salvar as alterações: {e}")
        else:
            # Adicionar este print para depuração quando o formulário é carregado (GET)
            print(f"DEBUG POST - Form inválido. Erros: {form.errors.as_json()}")

            messages.error(request, "Erro ao atualizar membro. Verifique os campos.")
    else:
        form = MembroForm(instance=membro, organizacao=organizacao, user=request.user, allowed_churches=allowed_churches)
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

    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar membros ou não está associado a nenhuma igreja específica.")
        return redirect('lista_membros')

    if request.method == 'POST':
        form = MembroForm(request.POST, organizacao=organizacao, user=request.user, allowed_churches=allowed_churches)
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
                    return redirect('lista_membros')
            except Exception as e:
                logger.exception(f"Erro ao salvar novo membro para organização {organizacao.id}")
                messages.error(request, f"Ocorreu um erro ao salvar o membro: {e}")
        else:
             messages.error(request, "Erro ao cadastrar membro. Verifique os campos.")
    else:
        form = MembroForm(organizacao=organizacao, user=request.user, allowed_churches=allowed_churches)

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
        return redirect('lista_membros') # Sempre redireciona para a lista
    else:
        # GET request não é permitido para esta ação
        messages.error(request, "Ação inválida.")
        return redirect('lista_membros')
# --- FIM NOVA VIEW ---

@login_required
@user_passes_test(is_secretaria_leader, login_url='core:home') # Apenas líderes da secretaria
def painel_lideranca_secretaria(request):
    try:
        organizacao_usuario = request.user.perfil.organizacao
        allowed_churches_set = get_allowed_churches_for_membros(request.user)
        print(f"DEBUG (Secretaria): Usuário: {request.user.username}, É Líder Secretaria: {is_secretaria_leader(request.user)}")
        print(f"DEBUG (Secretaria): allowed_churches_set: {list(allowed_churches_set)}")
        if not allowed_churches_set.exists():
            messages.warning(request, "Nenhuma igreja encontrada para visualização no painel de liderança da secretaria.")
            return render(request, 'secretaria/painel_lideranca_secretaria.html', {'nenhuma_igreja': True})

        # --- Lógica do Filtro de Igreja/Regional (similar ao financeiro) ---
        igreja_id_filtro_selecionado = request.GET.get('igreja_filtro')
        igreja_selecionada_filtro = None
        churches_for_queries = allowed_churches_set
        titulo_igreja_filtro = "Consolidado"

        if igreja_id_filtro_selecionado:
            try:
                igreja_selecionada_filtro = allowed_churches_set.get(pk=igreja_id_filtro_selecionado)
                # Se uma igreja/regional específica foi selecionada, filtramos para ela e suas subordinadas
                # Coletar PKs da igreja selecionada e seus descendentes
                pks_to_include = {igreja_selecionada_filtro.pk} # Adiciona o PK da igreja selecionada
                if hasattr(igreja_selecionada_filtro, 'get_descendants'):
                    
                    
                    descendants_qs = igreja_selecionada_filtro.get_descendants(include_self=False)
                    pks_to_include.update(descendants_qs.values_list('pk', flat=True))
                
                churches_for_queries = Igreja.objects.filter(
                    pk__in=list(pks_to_include), 
                    organizacao=organizacao_usuario # Garante que são da mesma organização
                )
                
                titulo_igreja_filtro = igreja_selecionada_filtro.nome_igreja
            except Igreja.DoesNotExist:
                messages.warning(request, "A igreja selecionada não é válida ou não está na sua lista de permissões.")
        # --- Fim Lógica do Filtro de Igreja/Regional ---

        # Dados consolidados de membros
        # Card 1: Total de Membros Ativos na Rede
        total_membros_rede = Membro.objects.filter(
            igreja__in=churches_for_queries, 
            status__considerar_ativo_relatorios=True
        ).count()


         # --- NOVOS DADOS PARA CARDS DE RESUMO (LIDERANÇA) ---
        from datetime import date, timedelta # Certifique-se que estão importados
        hoje_data_lider = date.today()

        # Card 2: Novos Membros na Rede (Últimos 30 dias)
        trinta_dias_atras_lider = hoje_data_lider - timedelta(days=30)
        novos_membros_rede_30_dias = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status__considerar_ativo_relatorios=True, # Opcional
            data_entrada__gte=trinta_dias_atras_lider
        ).count()

        # Card 3: Média de Membros Ativos por Igreja
        num_igrejas_consideradas = churches_for_queries.count() # Já calculado como allowed_churches_count
        media_membros_por_igreja = (total_membros_rede / num_igrejas_consideradas) if num_igrejas_consideradas > 0 else 0
        media_membros_por_igreja = round(media_membros_por_igreja, 1)
        # Card 4: Total de Igrejas Consideradas (já temos em 'allowed_churches_count')

        # Gráfico: Membros por Status (Consolidado)
        # Agrupa os membros pelo campo 'status__status' (do modelo Tiposstatus)
        # e conta o total de membros para cada status.





        # Gráfico: Membros por Status (Consolidado)
        # Agrupa os membros pelo campo 'status__status' (do modelo Tiposstatus)
        # e conta o total de membros para cada status.
        membros_por_status_qs = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status__considerar_ativo_relatorios=True  # Filtra pelos status marcados para relatório
        ).values('status__status')\
            .annotate(total=Count('chave'))\
            .order_by('status__status') # Ordenar pelo mesmo campo que está sendo agrupado
        # Assumindo que item['status__status'] já é o nome do status que você quer exibir no gráfico.
        grafico_membros_status_labels = [item['status__status'] if item['status__status'] else "Sem Status" for item in membros_por_status_qs]
        grafico_membros_status_valores = [item['total'] for item in membros_por_status_qs]

        # --- NOVOS DADOS PARA GRÁFICOS DE LIDERANÇA (GÊNERO E FAIXA ETÁRIA) ---
        membros_lideranca_ativos = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status__considerar_ativo_relatorios=True # Considerar apenas ativos para estes gráficos
        )

        # Gráfico: Membros por Gênero (Consolidado)
        genero_data_lider_qs = membros_lideranca_ativos.values('genero').annotate(total=Count('chave'))
        genero_map_lider = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
        aggregated_genero_lider = {}
        for item_gen_lid in genero_data_lider_qs:
            genero_display_lid = genero_map_lider.get(item_gen_lid['genero'], 'Não Informado')
            aggregated_genero_lider[genero_display_lid] = aggregated_genero_lider.get(genero_display_lid, 0) + item_gen_lid['total']
        grafico_membros_genero_labels = [key for key, value in aggregated_genero_lider.items()]
        grafico_membros_genero_valores = [value for key, value in aggregated_genero_lider.items()]

        # Gráfico: Membros por Faixa Etária (Consolidado)
        membros_com_nascimento_lider = membros_lideranca_ativos.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
        idades_lider = []
        # hoje_data_lider já foi definida para os cards
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
        # --- FIM NOVOS DADOS PARA GRÁFICOS DE LIDERANÇA ---




        context = {
            'titulo_dashboard': f"Liderança Secretaria - {titulo_igreja_filtro}" 
                                if igreja_id_filtro_selecionado and igreja_selecionada_filtro
                                else f"Liderança Secretaria - {organizacao_usuario.nome_fantasia} (Rede)",            'total_membros_rede': total_membros_rede,
            'total_membros_rede': total_membros_rede,
            'novos_membros_rede_30_dias': novos_membros_rede_30_dias,
            'media_membros_por_igreja': media_membros_por_igreja,
            'grafico_membros_status_labels_json': json.dumps(grafico_membros_status_labels),
            'grafico_membros_status_valores_json': json.dumps(grafico_membros_status_valores),
            'grafico_membros_genero_labels_json': json.dumps(grafico_membros_genero_labels), # Novo
            'grafico_membros_genero_valores_json': json.dumps(grafico_membros_genero_valores), # Novo
            'grafico_membros_faixa_labels_json': json.dumps(grafico_membros_faixa_labels), # Novo
            'grafico_membros_faixa_valores_json': json.dumps(grafico_membros_faixa_valores), # Novo
           
            'igrejas_permitidas_filtro': allowed_churches_set.order_by('nome_igreja'),
            'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado,
            'allowed_churches_count': churches_for_queries.count(),
        }
        return render(request, 'secretaria/painel_lideranca_secretaria.html', context)
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao carregar o painel de liderança da secretaria: {e}")
        # logger.exception("Erro no painel de liderança da secretaria") # Adicionar logger
        return render(request, 'secretaria/painel_lideranca_secretaria.html', {'erro_painel': True})
