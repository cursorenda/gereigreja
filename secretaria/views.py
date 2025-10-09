from django.http import JsonResponse
from django.db import models
# --- VIEW AJAX: BUSCAR VISITANTES POR NOME OU APELIDO ---
def buscar_visitantes(request):
    termo = request.GET.get('q', '').strip()
    # Busca ignorando acentuação (PostgreSQL: unaccent)
    import unicodedata
    from .models import Membro
    from eventos.models import Evento
    def remover_acentos(txt):
        return unicodedata.normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII') if txt else ''

    visitantes = []
    evento_id = request.GET.get('evento')
    tipos_ids = []
    status_ids = []
    if evento_id:
        try:
            evento = Evento.objects.get(pk=evento_id)
            tipos_ids = list(evento.tipos_participantes.values_list('id', flat=True))
            status_ids = list(evento.status_participantes.values_list('id', flat=True))
        except Evento.DoesNotExist:
            pass
    if termo:
        termo_sem_acento = remover_acentos(termo.lower())
        membros = Membro.objects.all()
        if tipos_ids:
            membros = membros.filter(tipo_pessoa_id__in=tipos_ids)
        if status_ids:
            membros = membros.filter(status_pessoa_id__in=status_ids)
        for v in membros:
            nome = v.nome or ''
            apelido = v.apelido or ''
            if termo_sem_acento in remover_acentos(nome.lower()) or termo_sem_acento in remover_acentos(apelido.lower()):
                visitantes.append({'id': v.chave, 'nome': v.nome, 'apelido': v.apelido})
            if len(visitantes) >= 20:
                break
    return JsonResponse(visitantes, safe=False)
    return JsonResponse(list(visitantes), safe=False)
from .forms_presenca_visitante_evento import PresencaVisitanteEventoForm
from eventos.models import Evento
from .models import PresencaVisitanteEvento, Visitante
from django.utils import timezone

# --- VIEW: REGISTRAR PRESENÇA DE VISITANTE EM EVENTO ---
from django.contrib.auth.decorators import login_required
@login_required
def registrar_presenca_visitante_evento(request):
    print(f"[DEBUG] igreja_ativa: {getattr(request, 'igreja_ativa', None)} | id: {getattr(getattr(request, 'igreja_ativa', None), 'id', None)} | user: {request.user}")
    hoje = timezone.localdate()
    fim = hoje + timezone.timedelta(days=7)
    eventos_do_dia = Evento.objects.none()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        eventos_do_dia = Evento.objects.filter(
            igreja=request.igreja_ativa,
            data_inicio__date__gte=hoje,
            data_inicio__date__lte=fim
        ).order_by('data_inicio')
    evento_id = request.GET.get('evento')
    evento_selecionado = None
    pessoas_presentes = []
    if evento_id:
        evento_selecionado = Evento.objects.get(pk=evento_id)
        pessoas_presentes = PresencaVisitanteEvento.objects.filter(evento=evento_selecionado).select_related('membro').order_by('-data_registro')
    if request.method == 'POST':
        form = PresencaVisitanteEventoForm(request.POST, request=request)
        if form.is_valid():
            membro = form.cleaned_data['membro']
            evento = form.cleaned_data['evento']
            # Verifica se já existe presença para este membro neste evento
            if PresencaVisitanteEvento.objects.filter(membro=membro, evento=evento).exists():
                messages.warning(request, f'A pessoa "{membro.nome}" já está registrada neste evento!')
            else:
                presenca = form.save(commit=False)
                presenca.responsavel_registro = request.user
                presenca.save()
                messages.success(request, f'Presença de "{presenca.membro.nome}" registrada no evento!')
            return redirect(f'?evento={evento.id}')
    else:
        form = PresencaVisitanteEventoForm(request=request)
        if evento_selecionado:
            form.fields['evento'].initial = evento_selecionado.id
    context = {
        'form': form,
        'eventos_do_dia': eventos_do_dia,
        'evento_selecionado': evento_selecionado,
        'visitantes_presentes': pessoas_presentes,
        'titulo_pagina': 'Registrar Presença no Evento',
    }
    return render(request, 'secretaria/registrar_presenca_visitante_evento.html', context)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from .models import Visitante, AcompanhamentoVisita, Membro
from .forms_visitante import VisitanteForm
from .forms_acompanhamento import AcompanhamentoVisitaForm
from .forms import AssociarUsuarioMembroForm

# --- VIEW: EXCLUIR VISITANTE ---
@login_required
def excluir_visitante(request, visitante_id):
    visitante = get_object_or_404(Visitante, pk=visitante_id)
    if request.method == 'POST':
        nome = visitante.nome
        visitante.delete()
        messages.success(request, f'Visitante "{nome}" excluído com sucesso!')
        return redirect('secretaria:lista_visitantes')
    context = {
        'visitante': visitante,
        'titulo_pagina': f'Excluir Visitante: {visitante.nome}',
    }
    return render(request, 'secretaria/excluir_visitante.html', context)
# --- VIEW: EDITAR VISITANTE ---
@login_required
def editar_visitante(request, visitante_id):
    visitante = get_object_or_404(Visitante, pk=visitante_id)
    if request.method == 'POST':
        form = VisitanteForm(request.POST, instance=visitante)
        if form.is_valid():
            visitante = form.save(commit=False)
            visitante.responsavel = request.user
            visitante.save()
            messages.success(request, f'Visitante "{visitante.nome}" atualizado com sucesso!')
            return redirect('secretaria:lista_visitantes')
    else:
        form = VisitanteForm(instance=visitante)
    context = {
        'form': form,
        'visitante': visitante,
        'titulo_pagina': f'Editar Visitante: {visitante.nome}',
    }
    return render(request, 'secretaria/editar_visitante.html', context)

# --- VIEW: LISTA DE VISITANTES ---
@login_required
def lista_visitantes(request):
    visitantes = Visitante.objects.select_related('igreja', 'responsavel').order_by('-data_primeira_visita', 'nome')
    query = request.GET.get('q', '').strip()
    if query:
        visitantes = visitantes.filter(
            Q(nome__icontains=query) | Q(telefone__icontains=query) | Q(email__icontains=query)
        )
    status = request.GET.get('status')
    if status:
        visitantes = visitantes.filter(status_acompanhamento=status)
    igreja_id = request.GET.get('igreja')
    if igreja_id:
        visitantes = visitantes.filter(igreja_id=igreja_id)
    # Determina igreja_selecionada para o template (compatível com padrão das outras telas)
    igreja_selecionada = str(igreja_id) if igreja_id else (str(request.igreja_ativa.pk) if hasattr(request, 'igreja_ativa') and request.igreja_ativa else '0')
    context = {
        'visitantes': visitantes,
        'query': query,
        'status': status,
        'igreja_id': igreja_id,
        'igreja_selecionada': igreja_selecionada,
        'titulo_pagina': 'Lista de Visitantes',
    }
    return render(request, 'secretaria/lista_visitantes.html', context)

# --- VIEW: CADASTRAR VISITANTE ---
@login_required
def criar_visitante(request):
    if request.method == 'POST':
        form = VisitanteForm(request.POST)
        if form.is_valid():
            visitante = form.save(commit=False)
            visitante.responsavel = request.user
            # Define a igreja ativa do request
            if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
                visitante.igreja = request.igreja_ativa
            # Define a data da primeira visita como hoje
            from django.utils import timezone
            visitante.data_primeira_visita = timezone.localdate()
            visitante.save()
            messages.success(request, f'Visitante "{visitante.nome}" cadastrado com sucesso!')
            return redirect('secretaria:lista_visitantes')
    else:
        form = VisitanteForm()
    context = {
        'form': form,
        'titulo_pagina': 'Cadastrar Novo Visitante',
    }
    return render(request, 'secretaria/criar_visitante.html', context)
from .forms_acompanhamento import AcompanhamentoVisitaForm
# View para registrar acompanhamento de visita
from .models import AcompanhamentoVisita, Membro
from django.contrib.auth.decorators import login_required

@login_required
def registrar_acompanhamento_visita(request, membro_id):
    membro = get_object_or_404(Membro, pk=membro_id)
    if request.method == 'POST':
        form = AcompanhamentoVisitaForm(request.POST)
        if form.is_valid():
            acompanhamento = form.save(commit=False)
            acompanhamento.membro = membro
            acompanhamento.responsavel = request.user
            from django.utils import timezone
            acompanhamento.data = timezone.now()  # Preenche automaticamente
            acompanhamento.save()
            messages.success(request, 'Acompanhamento registrado com sucesso!')
            return redirect('secretaria:editar_membro', membro_id=membro_id)
    else:
        form = AcompanhamentoVisitaForm()
    acompanhamentos = AcompanhamentoVisita.objects.filter(membro=membro).order_by('-data')
    context = {
        'form': form,
        'membro': membro,
        'acompanhamentos': acompanhamentos
    }
    return render(request, 'secretaria/registrar_acompanhamento_visita.html', context)
# Decorators precisam ser importados antes do uso
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .forms import AssociarUsuarioMembroForm
# Função de permissão para uso em decorators (deve vir antes do uso)
def is_admin_or_pastor(user):
    grupos_permitidos = ["Pastor", "Administrador", "Admin Ministerio", "Lider Igreja"]
    return user.is_superuser or user.groups.filter(name__in=grupos_permitidos).exists()

# --- Associação em massa de membros a usuários ---
@login_required
@user_passes_test(is_admin_or_pastor)
def associar_usuarios_membros(request):
    membros_sem_usuario = Membro.objects.none()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        membros_sem_usuario = Membro.objects.filter(usuario__isnull=True, igreja=request.igreja_ativa).order_by('nome')
    User = get_user_model()
    sugestoes = {}
    if request.method == 'POST':
        forms_list = []
        for membro in membros_sem_usuario:
            form = AssociarUsuarioMembroForm(request.POST, prefix=str(membro.pk), membro=membro)
            if form.is_valid():
                usuario = form.cleaned_data['usuario']
                membro.usuario = usuario
                membro.save()
            # Guardar sugestão para template
            sugestao_id = form.fields['sugestao_usuario_id'].initial
            sugestoes[membro.pk] = int(sugestao_id) if sugestao_id else None
            forms_list.append(form)
        messages.success(request, 'Associações salvas com sucesso!')
        return redirect('secretaria:associar_usuarios_membros')
    else:
        forms_list = []
        for m in membros_sem_usuario:
            form = AssociarUsuarioMembroForm(prefix=str(m.pk), membro=m)
            sugestao_id = form.fields['sugestao_usuario_id'].initial
            sugestoes[m.pk] = int(sugestao_id) if sugestao_id else None
            forms_list.append(form)
    context = {
        'membros_sem_usuario': membros_sem_usuario,
        'forms_list': forms_list,
        'sugestoes': sugestoes,
    }
    return render(request, 'secretaria/associar_usuarios_membros.html', context)

# Função de permissão para uso em decorators (deve vir antes do uso)
def is_admin_or_pastor(user):
    grupos_permitidos = ["Pastor", "Administrador", "Admin Ministerio", "Lider Igreja"]
    return user.is_superuser or user.groups.filter(name__in=grupos_permitidos).exists()

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_GET
from django.db.models import Count, Q, Sum, Case, When, Value, BooleanField
from django.db.models.functions import Extract
from django.utils.crypto import get_random_string
from django.utils import timezone
import zipfile
from django import forms

# Gerenciar ocupantes do cargo

from .forms import GerenciarOcupantesForm, CargoForm



# --- NOVA VIEW: Gerenciar Ocupantes (usando novos modelos) ---
from .models import Cargo, MembroCargo

@login_required
@user_passes_test(is_admin_or_pastor)
def gerenciar_ocupantes(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    membros = list(Membro.objects.all().order_by('nome'))
    ocupantes_atual = list(MembroCargo.objects.filter(cargo=cargo).select_related('membro'))
    if request.method == 'POST':
        ocupantes_ids = request.POST.get('ocupantes', '')
        if ocupantes_ids:
            ids = [int(i) for i in ocupantes_ids.split(',') if i.isdigit()]
            novos_ocupantes = Membro.objects.filter(chave__in=ids)
        else:
            novos_ocupantes = Membro.objects.none()
        # Remove todos os ocupantes antigos desse cargo
        MembroCargo.objects.filter(cargo=cargo).exclude(membro__in=novos_ocupantes).delete()
        # Adiciona novos ocupantes (evita duplicidade)
        for membro in novos_ocupantes:
            # Sempre garantir data_inicio preenchida corretamente
            vinculo, created = MembroCargo.objects.get_or_create(
                cargo=cargo, membro=membro,
                defaults={'data_inicio': timezone.now().date()}
            )
            if not vinculo.data_inicio:
                vinculo.data_inicio = timezone.now().date()
                vinculo.save()
        messages.success(request, 'Ocupantes do cargo atualizados com sucesso!')
        return redirect('secretaria:lista_cargos')
    else:
        ocupantes_iniciais = [mc.membro.chave for mc in ocupantes_atual]
    return render(request, 'secretaria/gerenciar_ocupantes.html', {
        'cargo': cargo,
        'membros': membros,
        'ocupantes_iniciais': ocupantes_iniciais,
    })



# Função de permissão para uso em decorators (deve vir antes do uso)
def is_admin_or_pastor(user):
    grupos_permitidos = ["Pastor", "Administrador", "Admin Ministerio", "Lider Igreja"]
    return user.is_superuser or user.groups.filter(name__in=grupos_permitidos).exists()

# Exclusão de cargo

@login_required
@user_passes_test(is_admin_or_pastor)
def excluir_cargo(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    ocupantes = MembroCargo.objects.filter(cargo=cargo)
    if request.method == 'POST':
        if ocupantes.exists():
            messages.error(request, 'Não é possível excluir um cargo que possui ocupantes.')
            return redirect('secretaria:lista_cargos')
        cargo.delete()
        messages.success(request, 'Cargo excluído com sucesso!')
        return redirect('secretaria:lista_cargos')
    return render(request, 'secretaria/excluir_cargo.html', {'cargo': cargo, 'ocupantes': ocupantes})
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_GET
from django.db.models import Count, Q, Sum, Case, When, Value, BooleanField
from django.db.models.functions import Extract
from django.utils.crypto import get_random_string
from django.utils import timezone
from django import forms
# --- STUBS PARA CRIAR E EDITAR CARGO ---
from django.http import HttpResponse





@login_required
@user_passes_test(is_admin_or_pastor)
def criar_cargo(request):
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo criado com sucesso!')
            return redirect('secretaria:lista_cargos')
    else:
        form = CargoForm()
    return render(request, 'secretaria/criar_cargo.html', {'form': form})



@login_required
@user_passes_test(is_admin_or_pastor)
def editar_cargo(request, cargo_id):
    cargo = get_object_or_404(Cargo, id=cargo_id)
    if request.method == 'POST':
        form = CargoForm(request.POST, instance=cargo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cargo atualizado com sucesso!')
            return redirect('secretaria:lista_cargos')
    else:
        form = CargoForm(instance=cargo)
    return render(request, 'secretaria/editar_cargo.html', {'form': form, 'cargo': cargo})

# --- IMPORTS DJANGO (antes de qualquer uso de decorador) ---
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_GET
from django.db.models import Count, Q, Sum, Case, When, Value, BooleanField
from django.db.models.functions import Extract
from django.utils.crypto import get_random_string
from django.utils import timezone
from django import forms

def is_admin_or_pastor(user):
    grupos_permitidos = ["Pastor", "Administrador", "Admin Ministerio", "Lider Igreja"]
    return user.is_superuser or user.groups.filter(name__in=grupos_permitidos).exists()

# --- IMPORTS DJANGO (antes de qualquer uso de decorador) ---
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_GET
from django.db.models import Count, Q, Sum, Case, When, Value, BooleanField
from django.db.models.functions import Extract
from django.utils.crypto import get_random_string
from django.utils import timezone
from django import forms

# --- Função de permissão para uso em decorators ---
def is_admin_or_pastor(user):
    grupos_permitidos = ["Pastor", "Administrador", "Admin Ministerio", "Lider Igreja"]
    return user.is_superuser or user.groups.filter(name__in=grupos_permitidos).exists()

# --- VIEW: LISTA DE CARGOS ---



# --- NOVA VIEW: Lista deCargo (usando novos modelos) ---
@login_required
@user_passes_test(is_admin_or_pastor)
def lista_cargos(request):
    cargos = Cargo.objects.all().prefetch_related('membrocargo_set__membro', 'grupo_permissao')
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        # Filtra ocupantes dos cargos pela igreja ativa
        for cargo in cargos:
            cargo.ocupantes = [mc.membro for mc in cargo.membrocargo_set.all() if mc.membro and mc.membro.igreja_id == request.igreja_ativa.id]
    else:
        for cargo in cargos:
            cargo.ocupantes = [mc.membro for mc in cargo.membrocargo_set.all() if mc.membro]
    context = {'cargos': cargos}
    return render(request, 'secretaria/lista_cargos.html', context)
# --- LINHA DO TEMPO DOS MEMBROS ---
from django import forms
from .models import TimelineEvent
from django.contrib.auth.decorators import login_required, user_passes_test


# Apenas para administradores/pastores (ajuste conforme seu sistema de permissões)

# --- IMPORTS PADRÃO PYTHON ---
import os
import logging
from datetime import date, datetime
import json

# --- IMPORTS DJANGO ---
from django import forms
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Sum, Case, When, Value, BooleanField
from django.db.models.functions import Extract
from django.utils.crypto import get_random_string
from django.utils import timezone

# --- OUTROS IMPORTS DO PROJETO ---
from .models import TimelineEvent, Membro, TipoPessoa, StatusPessoa, StatusHistorico
from .forms import MembroForm, MembroUserManagementForm, StatusHistoricoManualForm
from core.utils import get_ministerio_or_error
from secretaria.utils import get_allowed_churches_for_membros, is_admin_org, has_membro_view_permission, has_membro_edit_permission
from core.decorators import check_permission
from configuracao.models import AssinaturaMinisterio, Igreja, PerfilUsuario

# --- Função de permissão para uso em decorators ---

# --- Função de permissão para uso em decorators ---
def is_admin_or_pastor(user):
    grupos_permitidos = ["Pastor", "Administrador", "Admin Ministerio", "Lider Igreja"]
    return user.is_superuser or user.groups.filter(name__in=grupos_permitidos).exists()

# Formulário de filtro para a linha do tempo
class TimelineFilterForm(forms.Form):
    tipo_evento = forms.MultipleChoiceField(
        choices=TimelineEvent.TIPO_EVENTO_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Tipos de Evento"
    )
    data_inicio = forms.DateField(required=False, label="Data inicial", widget=forms.DateInput(attrs={"type": "date"}))
    data_fim = forms.DateField(required=False, label="Data final", widget=forms.DateInput(attrs={"type": "date"}))

@login_required
@user_passes_test(is_admin_or_pastor)
def linha_do_tempo(request):
    eventos = TimelineEvent.objects.select_related('membro').all()
    if hasattr(request, 'igreja_ativa') and request.igreja_ativa:
        eventos = eventos.filter(membro__igreja=request.igreja_ativa)
    form = TimelineFilterForm(request.GET or None)

    if form.is_valid():
        tipos = form.cleaned_data.get('tipo_evento')
        data_inicio = form.cleaned_data.get('data_inicio')
        data_fim = form.cleaned_data.get('data_fim')
        if tipos:
            eventos = eventos.filter(tipo_evento__in=tipos)
        if data_inicio:
            eventos = eventos.filter(data__date__gte=data_inicio)
        if data_fim:
            eventos = eventos.filter(data__date__lte=data_fim)

    eventos = eventos.order_by('-data')
    context = {
        'eventos': eventos,
        'form': form,
    }
    return render(request, 'secretaria/linha_do_tempo.html', context)

from django.views.decorators.http import require_GET
from django.http import JsonResponse

@require_GET
def autocomplete_nome_membro(request):
    """Retorna nomes de membros para autocomplete AJAX."""
    termo = request.GET.get('q', '').strip()
    results = []
    if termo:
        membros = Membro.objects.filter(nome__icontains=termo)[:20]
        results = [{'id': m.id, 'nome': m.nome} for m in membros]
    return JsonResponse({'results': results})
from datetime import date, datetime
import os
import shutil
from django.conf import settings
from django.http import JsonResponse
# c:\Gereigreja\secretaria\views.py

from configuracao.models import AssinaturaMinisterio, Igreja, PerfilUsuario
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from .models import Membro, TipoPessoa, StatusPessoa, StatusHistorico
from .forms import MembroForm, MembroUserManagementForm, StatusHistoricoManualForm
from core.utils import get_ministerio_or_error
from secretaria.utils import get_allowed_churches_for_membros, is_admin_org, has_membro_view_permission, has_membro_edit_permission
from core.decorators import check_permission
from django.db.models import Count, Q, Sum, Case, When, Value, BooleanField
from django.db.models.functions import Extract
from django.utils.crypto import get_random_string
import json
import logging






@login_required
def index(request):
    if request.user.is_superuser:
        return redirect('admin:index')

    if request.user.groups.filter(name='Membro Comum').exists() and not request.user.is_staff:
        return redirect('secretaria:portal_membro')

    ministerio = get_ministerio_or_error(request)
    allowed_churches_secretaria = get_allowed_churches_for_membros(request.user)
    titulo_contextual = f"Visão Geral - {ministerio.nome_fantasia}"
    membros_para_relatorios = Membro.objects.none()

    if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
        membros_para_relatorios = Membro.objects.filter(
            igreja=request.igreja_ativa,
            status_pessoa__considerar_ativo_relatorios=True,
            tipo_pessoa__nome__iexact="Membro"
        )
        titulo_contextual = f"Visão Geral - Igreja: {request.igreja_ativa.nome_igreja}"
    elif allowed_churches_secretaria.exists():
        membros_para_relatorios = Membro.objects.filter(
            igreja__in=allowed_churches_secretaria,
            status_pessoa__considerar_ativo_relatorios=True,
            tipo_pessoa__nome__iexact="Membro"
        )
        titulo_contextual += " (Consolidado)"
    elif is_admin_org(request.user):
        membros_para_relatorios = Membro.objects.filter(
            igreja__ministerio=ministerio,
            status_pessoa__considerar_ativo_relatorios=True,
            tipo_pessoa__nome__iexact="Membro"
        )
        titulo_contextual += " (Ministério)"

    # Gráficos e cards
    membros_base_para_grafico_status = (
        Membro.objects.filter(igreja=request.igreja_ativa) if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria
        else Membro.objects.filter(igreja__in=allowed_churches_secretaria) if allowed_churches_secretaria.exists()
        else Membro.objects.filter(igreja__ministerio=ministerio) if is_admin_org(request.user)
        else Membro.objects.none()
    )

    status_data_qs = membros_base_para_grafico_status.values('status_pessoa__nome').annotate(total=Count('chave')).order_by('status_pessoa__nome')
    status_data_list = [{'status': item['status_pessoa__nome'], 'total': item['total']} for item in status_data_qs if item['status_pessoa__nome']]

    genero_data_qs = membros_para_relatorios.values('genero').annotate(total=Count('chave'))
    genero_map = {'F': 'Feminino', 'M': 'Masculino', '': 'Não Informado', None: 'Não Informado'}
    aggregated_genero = {}
    for item in genero_data_qs:
        genero_display = genero_map.get(item['genero'], 'Não Informado')
        aggregated_genero[genero_display] = aggregated_genero.get(genero_display, 0) + item['total']
    genero_data_normalized = [{'genero': key, 'total': value} for key, value in aggregated_genero.items()]

    membros_com_nascimento = membros_para_relatorios.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
    idades = []
    hoje_data = date.today()
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
        '18-30 anos': 0,
        '31-50 anos': 0,
        '51-65 anos': 0,
        'Mais de 65 anos': 0,
        'Não Informado': membros_para_relatorios.filter(nascimento__isnull=True).count()
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
        elif 18 <= idade_val <= 30:
            faixas['18-30 anos'] += 1
        elif 31 <= idade_val <= 50:
            faixas['31-50 anos'] += 1
        elif 51 <= idade_val <= 65:
            faixas['51-65 anos'] += 1
        elif idade_val > 65:
            faixas['Mais de 65 anos'] += 1
    faixa_etaria_data = [{'faixa_etaria': k, 'total': v} for k, v in faixas.items()]

    total_membros_dashboard = membros_para_relatorios.count()

    from datetime import timedelta
    trinta_dias_atras = hoje_data - timedelta(days=30)
    novos_membros_30_dias = membros_para_relatorios.filter(data_entrada__gte=trinta_dias_atras).count()
    aniversariantes_mes_atual_count = membros_para_relatorios.filter(nascimento__month=hoje_data.month).count()
    idades_para_media = []
    membros_ativos_com_nascimento = membros_para_relatorios.filter(nascimento__isnull=False).values_list('nascimento', flat=True)
    for nascimento_dt in membros_ativos_com_nascimento:
        if nascimento_dt:
            idade = hoje_data.year - nascimento_dt.year - ((hoje_data.month, hoje_data.day) < (nascimento_dt.month, nascimento_dt.day))
            idades_para_media.append(idade)
    media_idade_membros = round(sum(idades_para_media) / len(idades_para_media)) if idades_para_media else 0

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

    # Cards e alertas esperados pelo template
    # --- Pendências de cadastro ---
    pendencias_cadastro = membros_para_relatorios.filter(Q(nascimento__isnull=True) | Q(email__isnull=True) | Q(email=''))
    total_pendencias_cadastro = pendencias_cadastro.count()

    # --- Contas vencidas (financeiro) ---
    igrejas_ids = membros_para_relatorios.values_list('igreja_id', flat=True).distinct()
    from financeiro.models import ContaPagar
    contas_vencidas = ContaPagar.objects.filter(
        igreja_id__in=igrejas_ids,
        status='VEN'
    )
    total_contas_vencidas = contas_vencidas.count()
    valor_total_contas_vencidas = contas_vencidas.aggregate(total=Sum('valor'))['total'] or 0

    # --- Assinatura prestes a vencer (exemplo: menos de 10 dias) ---
    assinatura_alerta = None
    hoje = hoje_data
    if hasattr(ministerio, 'assinatura') and ministerio.assinatura:
        dias_restantes = (ministerio.assinatura.data_fim - hoje).days if ministerio.assinatura.data_fim else None
        if dias_restantes is not None and dias_restantes <= 10 and ministerio.assinatura.status != 'ATIVA':
            assinatura_alerta = {
                'dias_restantes': dias_restantes,
                'status': ministerio.assinatura.get_status_display(),
            }

    # --- Evolução de membros nos últimos 12 meses (filtrado pelo contexto do dashboard) ---
    meses = []
    membros_evolucao = []
    for i in range(11, -1, -1):
        mes_ref = (hoje.replace(day=1) - timedelta(days=30*i))
        ano_mes = mes_ref.strftime('%Y-%m')
        meses.append(ano_mes)
        membros_count = membros_para_relatorios.filter(
            data_entrada__lte=mes_ref.replace(day=28) + timedelta(days=4)
        ).count()
        membros_evolucao.append(membros_count)

    # --- Novos membros por mês (últimos 12 meses) ---
    novos_membros_por_mes = []
    for i in range(11, -1, -1):
        mes_ref = (hoje.replace(day=1) - timedelta(days=30*i))
        ano = mes_ref.year
        mes = mes_ref.month
        count = membros_para_relatorios.filter(
            data_entrada__year=ano,
            data_entrada__month=mes
        ).count()
        novos_membros_por_mes.append(count)

    # --- Aniversariantes (ontem, hoje, amanhã) ---
    ontem = hoje - timedelta(days=1)
    amanha = hoje + timedelta(days=1)
    aniversariantes_hoje = membros_para_relatorios.filter(nascimento__month=hoje.month, nascimento__day=hoje.day)
    aniversariantes_ontem = membros_para_relatorios.filter(nascimento__month=ontem.month, nascimento__day=ontem.day)
    aniversariantes_amanha = membros_para_relatorios.filter(nascimento__month=amanha.month, nascimento__day=amanha.day)

    context = {
        'status_data_json': json.dumps(status_data_list),
        'genero_data_json': json.dumps(genero_data_normalized),
        'faixa_etaria_data_json': json.dumps(faixa_etaria_data),
        'total_membros_dashboard': total_membros_dashboard,
        'novos_membros_30_dias': novos_membros_30_dias,
        'aniversariantes_mes_atual_count': aniversariantes_mes_atual_count,
        'media_idade_membros': media_idade_membros,
        'ministerio': ministerio,
        'aniversariantes_proximos': aniversariantes_proximos,
        'titulo_pagina': titulo_contextual,
        'igreja_ativa_atual': request.igreja_ativa,
        # Cards e gráficos esperados pelo template:
        'total_membros_ativos': total_membros_dashboard,
        'novos_membros_ultimo_mes': novos_membros_30_dias,
        'total_pendencias_cadastro': total_pendencias_cadastro,
        'total_contas_vencidas': total_contas_vencidas,
        'valor_total_contas_vencidas': valor_total_contas_vencidas,
        'assinatura_alerta': assinatura_alerta,
        'evolucao_meses': meses,
        'evolucao_membros': membros_evolucao,
        'novos_membros_por_mes': novos_membros_por_mes,
        'aniversariantes_ontem': aniversariantes_ontem,
        'aniversariantes_hoje': aniversariantes_hoje,
        'aniversariantes_amanha': aniversariantes_amanha,
    }
    return render(request, 'secretaria/index.html', context)




@login_required
def dashboard(request):
    ministerio = get_ministerio_or_error(request)
    allowed_churches_secretaria = get_allowed_churches_for_membros(request.user)
    titulo_contextual_dashboard = f"Dashboard - {ministerio.nome_fantasia}"
    membros_para_relatorios = Membro.objects.none()




    # Verificar permissão de visualização de membros antes de prosseguir
    if not has_membro_view_permission(request.user):
        messages.warning(request, "Você não tem permissão para visualizar os dados do dashboard.")
        context = {
            'ministerio': ministerio,
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
            status_pessoa__considerar_ativo_relatorios=True # CORRIGIDO AQUI
        )
        titulo_contextual_dashboard = f"Dashboard - Igreja: {request.igreja_ativa.nome_igreja}"
    elif allowed_churches_secretaria.exists():
        membros_para_relatorios = Membro.objects.filter(
            igreja__in=allowed_churches_secretaria,
            status_pessoa__considerar_ativo_relatorios=True # Alterado
        )
        titulo_contextual_dashboard += " (Visão Consolidada)"
    elif is_admin_org(request.user): # Admin do Minist. sem igrejas no perfil e sem igreja ativa
        membros_para_relatorios = Membro.objects.filter(
            igreja__ministerio=ministerio,
            status_pessoa__considerar_ativo_relatorios=True # Alterado
        )
        titulo_contextual_dashboard += " (Visão da Ministério)"
    else:
        # Se não tem igreja ativa, nem igrejas permitidas (e não é admin org),
        # membros_para_relatorios continuará como queryset vazio.
        messages.info(request, "Nenhuma igreja selecionada ou permitida para visualização de dados no dashboard.")
        # Os cálculos abaixo resultarão em zero ou listas vazias, o que é o comportamento esperado.

    # --- Fim Lógica de Filtragem Inicial ---



    # Base de membros para o gráfico de status (sem filtro de 'considerar_ativo_relatorios')
    if request.igreja_ativa and request.igreja_ativa in allowed_churches_secretaria:
        membros_base_para_grafico_status = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches_secretaria.exists():
        membros_base_para_grafico_status = Membro.objects.filter(igreja__in=allowed_churches_secretaria)
    elif is_admin_org(request.user):
        membros_base_para_grafico_status = Membro.objects.filter(igreja__ministerio=ministerio)
    else:
        membros_base_para_grafico_status = Membro.objects.none()

    # 1. Contagem por Status (para o gráfico, usando a base sem filtro de 'ativo para relatórios')
    status_data_qs = membros_base_para_grafico_status.values(

        'status_pessoa__nome' # Alterado para novo campo e nome
    ).annotate(
        total=Count('chave')
    ).order_by('status_pessoa__nome') # Alterado
    # Ajustar a chave do dicionário para o template, se necessário
    status_data_list = [{'status': item['status_pessoa__nome'], 'total': item['total']} for item in status_data_qs]
    status_data_list = [item for item in status_data_list if item['status']] # Remove entradas onde status_pessoa__nome é None
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
    # Calcular idade em Python
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
        'ministerio': ministerio,
        'aniversariantes_proximos': aniversariantes_proximos,
        'titulo_pagina': titulo_contextual_dashboard,
        'igreja_ativa_atual': request.igreja_ativa

    }
    return render(request, 'dashboard.html', context)


@check_permission(has_membro_view_permission, login_url_name='login')
def lista_membros(request): # noqa: E302
    # Filtro por nome/apelido (busca parcial)
    nome_apelido = request.GET.get('nome_apelido')
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)

    # --- Lógica para filtrar pela igreja ativa ou por todas permitidas ---
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        membros_queryset = Membro.objects.filter(igreja=request.igreja_ativa)
    elif allowed_churches.exists():
        membros_queryset = Membro.objects.filter(igreja__in=allowed_churches)
    elif is_admin_org(request.user): # Admin do Minist. sem igrejas no perfil e sem igreja ativa
        membros_queryset = Membro.objects.filter(igreja__ministerio=ministerio)
    else:
        membros_queryset = Membro.objects.none()
    # --- Fim Lógica de Filtragem Inicial ---

    if nome_apelido:
        membros_queryset = membros_queryset.filter(
            Q(nome__icontains=nome_apelido) | Q(apelido__icontains=nome_apelido)
        )

    membros_queryset = membros_queryset.select_related('igreja', 'tipo_pessoa', 'status_pessoa').order_by('nome') # Adicionado tipo_pessoa, status_pessoa


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

    from .models import TipoPessoa, StatusPessoa

    tipos_pessoa = TipoPessoa.objects.all().order_by('nome')
    status_pessoa = StatusPessoa.objects.all().order_by('nome')

    # Filtros extras
    tipo_id = request.GET.get('tipo')
    if tipo_id:
        membros_queryset = membros_queryset.filter(tipo_pessoa_id=tipo_id)
    status_id = request.GET.get('status')
    if status_id:
        membros_queryset = membros_queryset.filter(status_pessoa_id=status_id)
    genero = request.GET.get('genero')
    if genero:
        membros_queryset = membros_queryset.filter(genero=genero)

    context = {
        'membros': membros_queryset,
        'ministerio': ministerio,
        'query': query,
        'can_edit_membros': can_edit,
        'titulo_pagina': f"Lista de Membros{': ' + request.igreja_ativa.nome_igreja if request.igreja_ativa else ' (Consolidado)'}",
        'igrejas_org': igrejas_para_filtro_template, # Para o filtro da página
        'igreja_selecionada': str(request.igreja_ativa.pk) if request.igreja_ativa else igreja_id_get,
        'tipos_pessoa': tipos_pessoa,
        'status_pessoa': status_pessoa,
    }
    return render(request, 'secretaria/lista_membros.html', context)


@check_permission(has_membro_edit_permission, login_url_name='login')
def editar_membro(request, membro_id): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)
     # DEBUG: Verificar o membro que está sendo editado
    
     # Tenta encontrar o User e PerfilUsuario associados ao membro
    user_associado = User.objects.filter(email__iexact=membro.email, perfil__ministerio=ministerio).first()
    perfil_associado = user_associado.perfil if user_associado else None
    # print(f"DEBUG [editar_membro]: Editando membro: {membro.nome} (ID: {membro.pk})") # Removido para produção

    if request.method == 'POST':
        # Ao editar, a igreja do membro não deve mudar via seletor global, mas o form precisa das allowed_churches
        form = MembroForm(request.POST, request.FILES, instance=membro, 
                          ministerio=ministerio, 
                          user=request.user, 
                          allowed_churches=allowed_churches, # noqa
                          igreja_inicial=membro.igreja) # Passa a igreja atual do membro 
    # print(f"DEBUG POST - request.POST: {request.POST}") # Removido para produção
        # --- Lógica para o formulário de gerenciamento de usuário ---
        user_management_form = MembroUserManagementForm(
            request.POST,
            membro_instance=membro,
            ministerio=ministerio,
            user_instance=user_associado,
            perfil_instance=perfil_associado
        )

        if 'submit_membro_form' in request.POST: # Se o formulário principal do membro foi submetido
            if form.is_valid():
                # print(f"DEBUG POST - form.cleaned_data: {form.cleaned_data}") # Removido para produção
                nascimento_do_form = form.cleaned_data.get('nascimento')
                # print(f"DEBUG POST - Nascimento do form.cleaned_data: {nascimento_do_form}, Tipo: {type(nascimento_do_form)}") # Removido para produção
                try:
                    membro_editado = form.save(commit=False)
                    # print(f"DEBUG POST - membro_editado.nascimento ANTES do save: {membro_editado.nascimento}, Tipo: {type(membro_editado.nascimento)}") # Removido para produção
                    if not is_admin_org(request.user) and membro_editado.igreja not in allowed_churches:
                        messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                   
                   
                    else:
                        membro_editado.save(user=request.user) # Passa o usuário
                        messages.success(request, f'Membro "{membro_editado.nome}" atualizado com sucesso!')
                        # Verifica o VALOR do botão pressionado, não a presença de uma chave.
                        # O botão "Salvar e Continuar" envia o valor "_save_and_continue".
                        # O botão "Salvar Alterações" não tem valor, então o get() retornará None.
                        if request.POST.get('submit_membro_form') == '_save_and_continue':
                            return redirect('secretaria:editar_membro', membro_id=membro_id)
                        else:
                            return redirect('secretaria:lista_membros')
                except Exception as e:
                    # print(f"DEBUG POST - Exceção ao salvar: {e}") # Removido para produção

                    logger.exception(f"Erro ao salvar edição do membro {membro_id} para ministério {ministerio.id}")
                    messages.error(request, f"Ocorreu um erro ao salvar as alterações: {e}")
            else:
                # print(f"DEBUG POST - Membro Form inválido. Erros: {form.errors.as_json()}") # Removido para produção
                messages.error(request, "Erro ao atualizar membro. Verifique os campos.")

        elif 'submit_user_management_form' in request.POST: # Se o formulário de gerenciamento de usuário foi submetido
            if user_management_form.is_valid():
                try:
                    with transaction.atomic():
                        # 1. Criar ou obter o User
                        if not user_associado:
                            # Se não existe User, cria um novo com senha aleatória e inativa
                            # O usuário terá que usar o fluxo de "esqueci a senha" para definir a primeira senha
                            random_password = get_random_string(length=20)
                            user_associado = User.objects.create_user(
                                username=user_management_form.cleaned_data['email_usuario'],
                                email=user_management_form.cleaned_data['email_usuario'],
                                password=random_password,
                                is_active=user_management_form.cleaned_data.get('is_active', False),
                                first_name=membro.nome, # Usa o nome do membro
                                last_name=membro.apelido or ''
                            )
                            messages.info(request, "Nova conta de usuário criada. O usuário precisará usar a função 'Esqueci a senha' para definir sua primeira senha.")
                        
                        # 2. Atualizar dados do User
                        user_associado.is_active = user_management_form.cleaned_data['is_active']
                        user_associado.is_staff = user_management_form.cleaned_data['is_staff']
                        user_associado.save()

                        # 3. Atualizar grupos do User
                        user_associado.groups.set(user_management_form.cleaned_data['grupos'])

                        # 4. Criar ou obter PerfilUsuario e atualizar igrejas permitidas
                        perfil_associado, created = PerfilUsuario.objects.get_or_create(user=user_associado, defaults={'ministerio': ministerio})
                        perfil_associado.igrejas_permitidas.set(user_management_form.cleaned_data['igrejas_permitidas'])
                        perfil_associado.ministerio = ministerio # Garante que a ministério está correta
                        perfil_associado.save()

                    messages.success(request, f"Acesso do usuário {user_associado.username} atualizado com sucesso!")
                    # Redireciona de volta para a mesma página, na aba correta
                    redirect_url = reverse('secretaria:editar_membro', args=[membro_id]) + '?tab=acesso-sistema'
                    return redirect(redirect_url)
                except Exception as e:
                    logger.exception(f"Erro ao gerenciar acesso do usuário para membro {membro_id}: {e}")
                    messages.error(request, f"Erro ao gerenciar acesso do usuário: {e}")
                    # RECARREGA O FORMULÁRIO PRINCIPAL PARA NÃO PERDER OS DADOS
                form = MembroForm(instance=membro, ministerio=ministerio, user=request.user,
                                  allowed_churches=allowed_churches, igreja_inicial=membro.igreja)
            
           
            else:
                # print(f"DEBUG POST - User Management Form inválido. Erros: {user_management_form.errors.as_json()}") # Removido para produção
                messages.error(request, "Erro ao gerenciar acesso do usuário. Verifique os campos.")
                # RECARREGA O FORMULÁRIO PRINCIPAL PARA NÃO PERDER OS DADOS
                form = MembroForm(instance=membro, ministerio=ministerio, user=request.user, allowed_churches=allowed_churches, igreja_inicial=membro.igreja)
       
    else:
        form = MembroForm(instance=membro, 
                          ministerio=ministerio, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=membro.igreja) # Passa a igreja atual do membro
        
        user_management_form = MembroUserManagementForm(
            membro_instance=membro,
            ministerio=ministerio,
            user_instance=user_associado,
            perfil_instance=perfil_associado
        )    
        # Print para quando o formulário é carregado (GET)
    # print(f"DEBUG GET - Editando Membro ID: {membro.pk}") # Removido para produção
    # print(f"DEBUG GET - Valor de membro.nascimento no BD: {membro.nascimento}") # Removido para produção
    # print(f"DEBUG GET - Tipo de membro.nascimento no BD: {type(membro.nascimento)}") # Removido para produção
    # Buscar histórico de contribuições do membro
    contribuicoes = Receitas.objects.filter(membro=membro).select_related(
        'igreja', 'conta_bancaria'
    ).order_by('-data')
    
     # DEBUG: Verificar as contribuições encontradas
    # print(f"DEBUG [editar_membro]: Contribuições encontradas para {membro.nome} (ID: {membro.pk}): {list(contribuicoes)}") # Removido para produção
    # Para ver a query SQL gerada (pode ajudar a identificar problemas no filtro):
    # print(f"DEBUG [editar_membro]: Query SQL para contribuições: {str(contribuicoes.query)}")

    # >>> ADICIONAR ESTE LOG <<<
    historico_status_membro = membro.transicoes_status_secretaria.all()
    # print(f"DEBUG [editar_membro]: Histórico de Status para {membro.nome} (ID: {membro.pk}): {list(historico_status_membro)}") # Removido para produção

    for h in historico_status_membro:
        pass  # Bloco mantido para evitar erro de indentação
    # >>> FIM DO LOG ADICIONADO <<<

    # --- FILTRO DE ACOMPANHAMENTO DE VISITA ---
    acompanhamentos_visita = membro.acompanhamentos_visita.all()
    filtro_tipo = request.GET.get('filtro_tipo', '').strip()
    filtro_data = request.GET.get('filtro_data', '').strip()
    if filtro_tipo:
        acompanhamentos_visita = acompanhamentos_visita.filter(tipo_contato=filtro_tipo)
    if filtro_data:
        try:
            from datetime import datetime
            filtro_data_dt = datetime.strptime(filtro_data, '%Y-%m-%d').date()
            acompanhamentos_visita = acompanhamentos_visita.filter(data__date=filtro_data_dt)
        except Exception:
            pass
    context = {
        'form': form,
        'membro_id': membro_id,
        'ministerio': ministerio,
        'titulo_pagina': f'Editar Membro: {membro.nome}',
        'contribuicoes': contribuicoes,
        'user_management_form': user_management_form,
        'user_associado': user_associado,
        'acompanhamentos_visita': acompanhamentos_visita,
        'filtro_tipo': filtro_tipo,
        'filtro_data': filtro_data,
    }
    return render(request, 'secretaria/editar_membro.html', context)


@check_permission(has_membro_edit_permission, login_url_name='login')
def criar_membro(request): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja_inicial_para_form = None


    if not is_admin_org(request.user) and not allowed_churches.exists():
        messages.error(request, "Você não tem permissão para adicionar membros ou não está associado a nenhuma igreja específica.")
        return redirect('secretaria:lista_membros')

    if request.method == 'POST':
        # Ao criar, a igreja_ativa (se houver) deve ser a sugestão inicial
        form = MembroForm(request.POST, request.FILES, 
                          ministerio=ministerio, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=request.igreja_ativa) # Passa request.igreja_ativa
        if form.is_valid():
            # print(f"DEBUG POST - form.cleaned_data: {form.cleaned_data}") # Removido para produção
            nascimento_do_form = form.cleaned_data.get('nascimento')
            # print(f"DEBUG POST - Nascimento do form.cleaned_data: {nascimento_do_form}, Tipo: {type(nascimento_do_form)}") # Removido para produção

            try:
                membro_editado = form.save(commit=False)

                novo_membro = form.save(commit=False)
                if not is_admin_org(request.user) and novo_membro.igreja not in allowed_churches:
                    messages.error(request, "Erro: Igreja selecionada inválida para sua permissão.")
                else:
                    novo_membro.save(user=request.user) # Passa o usuário
                    messages.success(request, f'Membro "{novo_membro.nome}" cadastrado com sucesso!')
                    return redirect('secretaria:lista_membros')
            except Exception as e:
                logger.exception(f"Erro ao salvar novo membro para ministério {ministerio.id}")
                messages.error(request, f"Ocorreu um erro ao salvar o membro: {e}")
        else:
             messages.error(request, "Erro ao cadastrar membro. Verifique os campos.")
    else:
        if request.igreja_ativa and request.igreja_ativa in allowed_churches:
            igreja_inicial_para_form = request.igreja_ativa
        elif allowed_churches.count() == 1:
            igreja_inicial_para_form = allowed_churches.first()

        form = MembroForm(ministerio=ministerio, 
                          user=request.user, 
                          allowed_churches=allowed_churches,
                          igreja_inicial=igreja_inicial_para_form)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': 'Cadastrar Novo Membro'
    }
    return render(request, 'secretaria/criar_membro.html', context)



# --- NOVA VIEW PARA ALTERNAR STATUS DO MEMBRO ---
@check_permission(has_membro_edit_permission, login_url_name='login')
def alternar_status_membro(request, membro_id): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    membro = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)

    # Nomes dos novos StatusPessoa para Ativo e Inativo
    # Certifique-se que estes existem na sua tabela StatusPessoa
    NOME_STATUSPESSOA_ATIVO = "Ativo" # Ajuste se o nome do seu status Ativo for diferente
    NOME_STATUSPESSOA_INATIVO = "Inativo" # Ajuste se o nome do seu status Inativo for diferente


    if request.method == 'POST':
        try:
            status_ativo_novo = StatusPessoa.objects.get(nome=NOME_STATUSPESSOA_ATIVO)
            status_inativo_novo = StatusPessoa.objects.get(nome=NOME_STATUSPESSOA_INATIVO)

            acao = ""
             # Agora verificamos o novo campo status_pessoa
            if membro.status_pessoa and membro.status_pessoa.considerar_ativo_relatorios:

                # Se está ativo para relatórios, inativa
                membro.status_pessoa = status_inativo_novo
                acao = "inativado (para relatórios)"
            else:
                # Se está inativo para relatórios (ou sem status), ativa
                membro.status_pessoa = status_ativo_novo
                acao = "ativado (para relatórios)"

            membro.save(update_fields=['status_pessoa']) # Salva o novo campo
            messages.success(request, f'Membro "{membro.nome}" foi {acao} com sucesso.')

        except StatusPessoa.DoesNotExist:
            messages.error(request, f"Erro: Os status '{NOME_STATUSPESSOA_ATIVO}' ou '{NOME_STATUSPESSOA_INATIVO}' não foram encontrados no cadastro de Status de Pessoa. Verifique os nomes e o cadastro.")
        except Exception as e:
            logger.exception(f"Erro ao alternar status do membro {membro_id} para ministério {ministerio.id}")
            messages.error(request, f"Ocorreu um erro ao alternar o status do membro: {e}")
        return redirect('secretaria:lista_membros') # Sempre redireciona para a lista
    else:
        # GET request não é permitido para esta ação
        messages.error(request, "Ação inválida.")
        return redirect('secretaria:lista_membros')
# --- FIM NOVA VIEW ---


# --- NOVA VIEW PARA FICHA DE MEMBRO PARA IMPRESSÃO ---
@check_permission(has_membro_view_permission, login_url_name='login')
def ficha_membro_impressao(request, membro_id): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    
    # Usar select_related e prefetch_related para otimizar a busca de dados relacionados
    membro = get_object_or_404(
        Membro.objects.select_related(
            'igreja',
            'tipo_pessoa', 'status_pessoa', # Adicionados novos campos

            # Adicione outros select_related para ForeignKeys diretos se necessário
        ).prefetch_related(
            'contatos_set', # related_name padrão se não definido explicitamente
            'infoeclesiastica_set',
            'familia_set',
            'filhos_set',
            'observacoes_set',
            'membrocargo_set', # Para cargos (novo related_name padrão)
            'membrocargo_set__cargo', # Para acessar o nome do cargo
            # Adicione outros prefetch_related para ManyToMany ou Reverse ForeignKeys
        ),
        pk=membro_id, 
        igreja__in=allowed_churches
    )

    context = {
        'membro': membro,
        'ministerio_sistema': ministerio, # Para diferenciar do ministério do membro, se necessário
        'titulo_pagina': f"Ficha Cadastral - {membro.nome}",
        # Passar dados relacionados específicos se o template precisar deles de forma mais direta
        # Ex: 'contatos': membro.contatos_set.first() # Se for OneToOne ou você só quer o primeiro
    }
    return render(request, 'secretaria/membro/ficha_membro_impressao.html', context)
# --- FIM NOVA VIEW ---

from secretaria.utils import is_secretaria_leader
@check_permission(is_secretaria_leader, login_url_name='login') # Ajuste login_url_name se 'core:home' for diferente de 'login'
def painel_lideranca_secretaria(request): # noqa: E302
    try:
        # Chama get_ministerio_or_error no início para validar o acesso à ministério
        ministerio_usuario = get_ministerio_or_error(request) # Usar a função centralizada
        # Obtém o conjunto base de igrejas que este líder pode acessar

        allowed_churches_base_secretaria = get_allowed_churches_for_membros(request.user, ministerio_usuario) # Passa ministerio_usuario
        
    # print(f"DEBUG (Secretaria): Usuário: {request.user.username}, É Líder Secretaria: {is_secretaria_leader(request.user)}") # Removido para produção

        if not allowed_churches_base_secretaria.exists() and not is_admin_org(request.user):

            messages.warning(request, "Nenhuma igreja encontrada para visualização no painel de liderança da secretaria.")
            # Adiciona ministerio_usuario ao contexto para o template base
            return render(request, 'secretaria/painel_lideranca_secretaria.html', {
                'nenhuma_igreja_permissao': True, 
                'ministerio_usuario': ministerio_usuario,
                'titulo_dashboard': f"Liderança Secretaria - {ministerio_usuario.nome_fantasia}"
            })


        # --- Lógica do Filtro de Igreja/Regional (similar ao financeiro) ---
        churches_for_queries = None # Igrejas que serão usadas para buscar os dados
        titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}" 
        ver_apenas_entidade_foco = False
        
        titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
        
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
                    titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
            else: 
                igreja_em_foco_obj = None
                igreja_id_filtro_selecionado_template_lider_sec = ''
                titulo_escopo_igreja = f"Consolidado - {ministerio_usuario.nome_fantasia}"
       
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
                churches_for_queries = Igreja.objects.filter(pk__in=list(pks_to_include), ministerio=ministerio_usuario)
                if len(pks_to_include) > 1 and not ver_apenas_entidade_foco:
                    titulo_escopo_igreja = f"Rede: {igreja_em_foco_obj.nome_igreja}"
                elif not ver_apenas_entidade_foco:
                    titulo_escopo_igreja = f"Igreja: {igreja_em_foco_obj.nome_igreja}"
        else: 
            churches_for_queries = allowed_churches_base_secretaria
            # titulo_escopo_igreja já é "Consolidado - Ministério"

        if not churches_for_queries or not churches_for_queries.exists():
            messages.warning(request, "Nenhuma igreja corresponde aos filtros aplicados.")
            return render(request, 'secretaria/painel_lideranca_secretaria.html', {
                'nenhuma_igreja_filtro': True, 
                'ministerio_usuario': ministerio_usuario,
                'titulo_dashboard': f"Liderança Secretaria - {ministerio_usuario.nome_fantasia}",
                'igrejas_permitidas_filtro': allowed_churches_base_secretaria.order_by('nome_igreja'),
                'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template_lider_sec,
            })

        # --- Cálculos de dados para o painel da secretaria ---
        total_membros_rede = Membro.objects.filter(
            igreja__in=churches_for_queries, 
            # status__considerar_ativo_relatorios=True # Lógica antiga
            status_pessoa__considerar_ativo_relatorios=True # Nova lógica
        ).count()

        from datetime import date, timedelta # Já importado no topo do arquivo
        hoje_data_lider = date.today()
        trinta_dias_atras_lider = hoje_data_lider - timedelta(days=30)
        novos_membros_rede_30_dias = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status_pessoa__considerar_ativo_relatorios=True, # Alterado
            data_entrada__gte=trinta_dias_atras_lider
        ).count()

        num_igrejas_consideradas = churches_for_queries.count() 
        media_membros_por_igreja = (total_membros_rede / num_igrejas_consideradas) if num_igrejas_consideradas > 0 else 0 # noqa
        media_membros_por_igreja = round(media_membros_por_igreja, 1)

        membros_por_status_qs = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status_pessoa__considerar_ativo_relatorios=True # Alterado
        ).values('status_pessoa__nome').annotate(total=Count('chave')).order_by('status_pessoa__nome') # Alterado
        grafico_membros_status_labels = [item['status_pessoa__nome'] if item['status_pessoa__nome'] else "Sem Status" for item in membros_por_status_qs]
        grafico_membros_status_valores = [item['total'] for item in membros_por_status_qs]

        membros_lideranca_ativos = Membro.objects.filter(
            igreja__in=churches_for_queries,
            status_pessoa__considerar_ativo_relatorios=True # Alterado
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

         # Novo: Gráfico de Membros por Tipo de Pessoa (Consolidado)
        membros_por_tipo_qs = membros_lideranca_ativos.values(
            'tipo_pessoa__nome'
        ).annotate(total=Count('chave')).order_by('tipo_pessoa__nome')
        grafico_membros_tipo_labels = [item['tipo_pessoa__nome'] if item['tipo_pessoa__nome'] else "Sem Tipo" for item in membros_por_tipo_qs]
        grafico_membros_tipo_valores = [item['total'] for item in membros_por_tipo_qs]

        # Novo: Gráfico de Membros por Status Pessoa (Consolidado - todos os status, não apenas os ativos para relatório)
        # Usaremos 'churches_for_queries' para pegar todos os membros da rede, sem o filtro de 'considerar_ativo_relatorios'
        membros_rede_completa_para_status = Membro.objects.filter(igreja__in=churches_for_queries)
        membros_por_status_geral_qs = membros_rede_completa_para_status.values(
            'status_pessoa__nome'
        ).annotate(total=Count('chave')).order_by('status_pessoa__nome')
        grafico_membros_status_geral_labels = [item['status_pessoa__nome'] if item['status_pessoa__nome'] else "Sem Status" for item in membros_por_status_geral_qs]
        grafico_membros_status_geral_valores = [item['total'] for item in membros_por_status_geral_qs]

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
             'grafico_membros_tipo_labels_json': json.dumps(grafico_membros_tipo_labels), # Novo
            'grafico_membros_tipo_valores_json': json.dumps(grafico_membros_tipo_valores), # Novo
            'grafico_membros_status_geral_labels_json': json.dumps(grafico_membros_status_geral_labels), # Novo
            'grafico_membros_status_geral_valores_json': json.dumps(grafico_membros_status_geral_valores), # Novo
    
            'igrejas_permitidas_filtro': opcoes_filtro_pagina, 
            'igreja_id_filtro_selecionado': igreja_id_filtro_selecionado_template_lider_sec,
            'allowed_churches_count': churches_for_queries.count() if churches_for_queries else 0,
            'ministerio_usuario': ministerio_usuario,
        }
        return render(request, 'secretaria/painel_lideranca_secretaria.html', context)
    except PermissionDenied:
        raise 
    except Http404:
        raise
    except Exception as e: 
        org_nome_log = getattr(getattr(getattr(request.user, 'perfil', None), 'ministerio', None), 'nome_fantasia', "N/A")
        logger.exception(f"Erro inesperado no painel de liderança da secretaria para ministério '{org_nome_log}': {e}")
        messages.error(request, f"Ocorreu um erro ao carregar o painel de liderança da secretaria: {e}")
        return redirect('secretaria:dashboard')

# --- VIEW PARA ADICIONAR HISTÓRICO DE STATUS MANUALMENTE ---
@check_permission(has_membro_edit_permission, login_url_name='login')
def adicionar_historico_status_manual(request, membro_id=None): # noqa: E302
    ministerio = get_ministerio_or_error(request)
    membro_obj = None
    if membro_id:
        # Garante que o membro_id pertence à ministério do usuário
        allowed_churches = get_allowed_churches_for_membros(request.user)
        membro_obj = get_object_or_404(Membro, pk=membro_id, igreja__in=allowed_churches)

    if request.method == 'POST':
        form = StatusHistoricoManualForm(request.POST, ministerio=ministerio, membro_inicial=membro_obj)
        if form.is_valid():
            try:
                historico = form.save(commit=False)
                if membro_obj: # Se o membro veio da URL, garante que é ele
                    historico.membro = membro_obj
                
                historico.registrado_por = request.user
                historico.save()
                messages.success(request, f"Entrada de histórico manual adicionada para {historico.membro.nome}.")
                # Redireciona para a página de edição do membro, na aba de histórico
                return redirect(reverse('secretaria:editar_membro', args=[historico.membro.pk]) + '?tab=historico-status')
            except Exception as e:
                logger.error(f"Erro ao salvar histórico manual para ministério {ministerio.id}: {e}")
                messages.error(request, f"Ocorreu um erro ao salvar o histórico: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = StatusHistoricoManualForm(ministerio=ministerio, membro_inicial=membro_obj)

    context = {
        'form': form,
        'ministerio': ministerio,
        'membro_obj': membro_obj, # Passa o objeto do membro para o template, se houver
        'titulo_pagina': f"Adicionar Histórico Manual para {membro_obj.nome}" if membro_obj else "Adicionar Histórico Manual de Tipo/Status"
    }
    return render(request, 'secretaria/membro/adicionar_historico_status_manual.html', context)

# --- FIM VIEW HISTÓRICO MANUAL ---

# --- NOVA VIEW PARA O PORTAL DO MEMBRO COMUM ---
@login_required
def portal_membro(request):
    """
    Página inicial para usuários do grupo 'Membro Comum'.
    Exibe um resumo dos dados pessoais e atalhos.
    """
    ministerio = get_ministerio_or_error(request)
    try:
        # Busca o objeto Membro associado ao usuário logado
        membro_obj = Membro.objects.get(email__iexact=request.user.email, igreja__ministerio=ministerio)
    except Membro.DoesNotExist:
        # Se não encontrar um registro de membro correspondente, mostra uma mensagem.
        # Isso pode acontecer se o e-mail do usuário não corresponder ao e-mail no cadastro de membro.
        messages.warning(request, "Seu cadastro de membro não foi encontrado. Por favor, contate a secretaria da sua igreja para verificar seus dados.")
        membro_obj = None

    # Busca o histórico de contribuições se o membro foi encontrado
    contribuicoes = []
    if membro_obj:
        contribuicoes = Receitas.objects.filter(membro=membro_obj).order_by('-data')[:10] # Pega as 10 últimas

    context = {
        'ministerio': ministerio,
        'membro': membro_obj,
        'contribuicoes': contribuicoes,
        'titulo_pagina': "Meu Portal"
    }
    return render(request, 'secretaria/portal_membro.html', context)


# ...existing code...
from django.db.models.functions import Extract
from django.urls import reverse
from financeiro.models import Receitas
from django.db import transaction
from django.contrib.auth import get_user_model
User = get_user_model()
logger = logging.getLogger(__name__)

# --- NOVA VIEW: RELATÓRIO DE REUNIÃO DE MEMBROS ---
from django.utils import timezone
@login_required
def relatorio_reuniao_membros(request):
    """
    Gera relatório HTML para impressão da reunião de membros, listando membros ativos em ordem alfabética.
    """
    ministerio = get_ministerio_or_error(request)
    allowed_churches = get_allowed_churches_for_membros(request.user)
    igreja = None
    if request.igreja_ativa and request.igreja_ativa in allowed_churches:
        igreja = request.igreja_ativa
    elif allowed_churches.exists():
        igreja = allowed_churches.first()
    else:
        messages.error(request, "Nenhuma igreja selecionada ou permitida para gerar relatório.")
        return redirect('secretaria:dashboard')

    # Buscar membros ativos para relatórios

    # Buscar apenas membros do tipo 'Membro' (não visitantes, congregados, etc)
    membros = Membro.objects.filter(
        igreja=igreja,
        tipo_pessoa__nome__in=['Membro', 'Obreiro'],
        status_pessoa__nome__in=['Ativo', 'Em Disciplina']
    ).order_by('nome')

    # Dados do cabeçalho
    nome_igreja = igreja.nome_igreja if hasattr(igreja, 'nome_igreja') else str(igreja)
    bairro = getattr(igreja, 'bairro', '')
    cidade = getattr(igreja, 'cidade', '')
    nome_ministerio = getattr(ministerio, 'nome_fantasia', str(ministerio))
    pastor_local = getattr(igreja, 'pastor_local', '')
    pastor_regional = getattr(igreja, 'pastor_regional', '')
    data_reuniao = timezone.now().strftime('%d de %B de %Y')


    # URLs dos logos (preferencialmente logo1 da igreja e logo do ministério)
    if hasattr(igreja, 'logo1') and igreja.logo1:
        logo_igreja_url = igreja.logo1.url
    else:
        logo_igreja_url = '/static/favicon.ico'

    if hasattr(ministerio, 'logo') and ministerio.logo:
        logo_ministerio_url = ministerio.logo.url
    else:
        logo_ministerio_url = '/static/favicon.ico'

    context = {
        'membros': membros,
        'nome_igreja': nome_igreja,
        'bairro': bairro,
        'cidade': cidade,
        'nome_ministerio': nome_ministerio,
        'pastor_local': pastor_local,
        'pastor_regional': pastor_regional,
        'data_reuniao': data_reuniao,
        'logo_igreja_url': logo_igreja_url,
        'logo_ministerio_url': logo_ministerio_url,
    }
    return render(request, 'secretaria/relatorio_reuniao_membros.html', context)
# --- FIM NOVA VIEW ---