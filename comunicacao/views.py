from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import PermissionDenied

from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date

from .models import Aviso, Notificacao # Importar os modelos Aviso e Notificacao
from .forms import AvisoForm # Manter o AvisoForm

from core.utils import get_organizacao_or_error
from configuracao.models import Igreja # Para filtrar igrejas
from .utils import can_manage_avisos, can_view_avisos # Nossas funções de permissão
from core.decorators import verificar_assinatura_valida # Decorator de assinatura

# Crie suas views aqui.

@login_required
@verificar_assinatura_valida
@user_passes_test(can_view_avisos, login_url='login')
def lista_avisos(request):
    organizacao = get_organizacao_or_error(request)
    avisos_qs = Aviso.objects.filter(organizacao=organizacao, publicado=True)

    # Filtra avisos que não expiraram ou não têm data de expiração
    avisos_qs = avisos_qs.filter(
        Q(data_expiracao__isnull=True) | Q(data_expiracao__gte=timezone.now().date())
    )

    # Filtra por igreja ativa (se houver) ou mostra avisos para toda a organização
    # ou para as igrejas específicas que o usuário pode ver (se a lógica for mais complexa no futuro)
    if request.igreja_ativa:
        avisos_qs = avisos_qs.filter(
            Q(igrejas_destino__isnull=True) | Q(igrejas_destino=request.igreja_ativa)
        ).distinct() # distinct() é importante por causa do ManyToMany
    else:
        # Se nenhuma igreja ativa, mostra avisos para toda a organização
        # ou aqueles que não têm igrejas destino específicas (são para toda a organização)
        # Esta lógica pode precisar de ajuste dependendo de como você quer que "todas as igrejas" funcione
        # Por enquanto, mostra os que não têm igrejas_destino (para toda org)
        # ou os que têm alguma igreja destino (se o usuário for admin da org, por exemplo)
        # Para simplificar, se não há igreja ativa, mostramos os que são para toda a organização.
        # Se o usuário for admin da org, ele verá todos os avisos da organização de qualquer forma.
        avisos_qs = avisos_qs.filter(igrejas_destino__isnull=True).distinct()

    # Adicionar filtros de busca se necessário (ex: por título)
    query = request.GET.get('q')
    if query:
        avisos_qs = avisos_qs.filter(titulo__icontains=query)

    context = {
        'avisos': avisos_qs.order_by('-data_publicacao'),
        'organizacao': organizacao,
        'titulo_pagina': "Mural de Avisos",
        'can_manage': can_manage_avisos(request.user),
        'query': query,
    }
    return render(request, 'comunicacao/mural/lista_avisos.html', context)

@login_required
@verificar_assinatura_valida
@user_passes_test(can_view_avisos, login_url='login')
def detalhe_aviso(request, pk):
    organizacao = get_organizacao_or_error(request)
    aviso = get_object_or_404(Aviso, pk=pk, organizacao=organizacao, publicado=True)

    # Verifica se o aviso não expirou
    if aviso.data_expiracao and aviso.data_expiracao < timezone.now().date():
        raise PermissionDenied("Este aviso expirou.") # Ou redirecionar para lista com mensagem

    # Verifica se o aviso é para a igreja ativa do usuário ou para toda a organização
    if request.igreja_ativa and aviso.igrejas_destino.exists() and request.igreja_ativa not in aviso.igrejas_destino.all():
        raise PermissionDenied("Você não tem permissão para ver este aviso específico para outra igreja.")

    context = {
        'aviso': aviso,
        'organizacao': organizacao,
        'titulo_pagina': aviso.titulo,
        'can_manage': can_manage_avisos(request.user),
    }
    return render(request, 'comunicacao/mural/detalhe_aviso.html', context)

@login_required
@verificar_assinatura_valida
@user_passes_test(can_manage_avisos, login_url='login')
def criar_aviso(request):
    organizacao = get_organizacao_or_error(request)
    if request.method == 'POST':
        form = AvisoForm(request.POST)
        if form.is_valid():
            try:
                aviso = form.save(commit=False)
                aviso.organizacao = organizacao # Garante a organização correta
                if not aviso.autor: # Define o autor se não foi preenchido (ex: se o campo estiver oculto)
                    aviso.autor = request.user
                aviso.save()
                form.save_m2m() # Necessário para salvar ManyToManyFields
                messages.success(request, "Aviso criado com sucesso!")
                return redirect('comunicacao:lista_avisos')
            except Exception as e:
                messages.error(request, f"Erro ao criar o aviso: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = AvisoForm(initial={'organizacao': organizacao, 'autor': request.user})
        # Filtra o queryset de igrejas_destino para a organização atual
        form.fields['igrejas_destino'].queryset = Igreja.objects.filter(organizacao=organizacao).order_by('nome_igreja')
        form.fields['organizacao'].disabled = True # Não permitir mudar a organização
        # O campo autor pode ser preenchido automaticamente e desabilitado ou oculto
        # form.fields['autor'].disabled = True

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': "Criar Novo Aviso",
    }
    return render(request, 'comunicacao/mural/form_aviso.html', context)

@login_required
@verificar_assinatura_valida
@user_passes_test(can_manage_avisos, login_url='login')
def editar_aviso(request, pk):
    organizacao = get_organizacao_or_error(request)
    aviso = get_object_or_404(Aviso, pk=pk, organizacao=organizacao)

    if request.method == 'POST':
        form = AvisoForm(request.POST, instance=aviso)
        if form.is_valid():
            try:
                # Garante que a organização não seja alterada
                if form.cleaned_data.get('organizacao') != organizacao:
                    raise PermissionDenied("Não é permitido alterar a organização do aviso.")
                
                edited_aviso = form.save(commit=False)
                # Se o autor não puder ser alterado no form, garanta que ele não mude
                # edited_aviso.autor = aviso.autor # ou request.user se for o editor atual
                edited_aviso.save()
                form.save_m2m()
                messages.success(request, "Aviso atualizado com sucesso!")
                return redirect('comunicacao:lista_avisos')
            except PermissionDenied as pd:
                messages.error(request, str(pd))
            except Exception as e:
                messages.error(request, f"Erro ao atualizar o aviso: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = AvisoForm(instance=aviso)
        form.fields['igrejas_destino'].queryset = Igreja.objects.filter(organizacao=organizacao).order_by('nome_igreja')
        form.fields['organizacao'].disabled = True
        # form.fields['autor'].disabled = True # Se o autor não puder ser alterado

    context = {
        'form': form,
        'aviso': aviso,
        'organizacao': organizacao,
        'titulo_pagina': f"Editar Aviso: {aviso.titulo}",
    }
    return render(request, 'comunicacao/mural/form_aviso.html', context)

@login_required
@verificar_assinatura_valida
@user_passes_test(can_manage_avisos, login_url='login')
def excluir_aviso(request, pk):
    organizacao = get_organizacao_or_error(request)
    aviso = get_object_or_404(Aviso, pk=pk, organizacao=organizacao)

    if request.method == 'POST':
        try:
            aviso.delete()
            messages.success(request, "Aviso excluído com sucesso!")
            return redirect('comunicacao:lista_avisos')
        except Exception as e:
            messages.error(request, f"Erro ao excluir o aviso: {e}")
            return redirect('comunicacao:detalhe_aviso', pk=pk)

    context = {
        'aviso': aviso,
        'organizacao': organizacao,
        'titulo_pagina': f"Confirmar Exclusão: {aviso.titulo}",
    }
    return render(request, 'comunicacao/mural/confirmar_excluir_aviso.html', context)

# --- VIEWS PARA ENVIO DE E-MAIL EM MASSA ---
from .forms import EmailMassaForm # Importar o novo formulário
from secretaria.models import Membro # Importar o modelo Membro

@login_required
@verificar_assinatura_valida
@user_passes_test(can_manage_avisos, login_url='login') # Reutilizando a permissão de gerenciar avisos por enquanto
def enviar_email_massa(request):
    organizacao = get_organizacao_or_error(request)

    if request.method == 'POST':
        form = EmailMassaForm(request.POST, organizacao=organizacao)
        if form.is_valid():
            assunto = form.cleaned_data['assunto']
            mensagem = form.cleaned_data['mensagem']
            igrejas_destino = form.cleaned_data['igrejas_destino']
            tipos_pessoa = form.cleaned_data['tipos_pessoa']
            status_pessoa = form.cleaned_data['status_pessoa']
            apenas_ativos_para_relatorios = form.cleaned_data['apenas_ativos_para_relatorios']
            aniversariantes_do_mes = form.cleaned_data['aniversariantes_do_mes']

            # Construir o queryset de membros baseado nos filtros
            membros_qs = Membro.objects.filter(igreja__organizacao=organizacao)

            if igrejas_destino:
                membros_qs = membros_qs.filter(igreja__in=igrejas_destino)
            
            if tipos_pessoa:
                membros_qs = membros_qs.filter(tipo_pessoa__in=tipos_pessoa)
            
            if status_pessoa:
                membros_qs = membros_qs.filter(status_pessoa__in=status_pessoa)
            
            if apenas_ativos_para_relatorios:
                membros_qs = membros_qs.filter(status_pessoa__considerar_ativo_relatorios=True)
            
            if aniversariantes_do_mes:
                hoje = date.today()
                membros_qs = membros_qs.filter(nascimento__month=hoje.month)

            # Obter os e-mails dos destinatários
            destinatarios_emails = list(membros_qs.filter(email__isnull=False).exclude(email='').values_list('email', flat=True).distinct())

            if not destinatarios_emails:
                messages.warning(request, "Nenhum destinatário encontrado com os critérios selecionados.")
                return redirect('comunicacao:enviar_email_massa')

            try:
                html_message = render_to_string('comunicacao/email/email_massa_template.html', {
                    'assunto': assunto,
                    'mensagem': mensagem,
                    'organizacao_nome': organizacao.nome_fantasia,
                })
                send_mail(
                    assunto,
                    mensagem, # Versão texto puro (fallback)
                    settings.DEFAULT_FROM_EMAIL,
                    destinatarios_emails,
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, f"E-mail enviado com sucesso para {len(destinatarios_emails)} destinatário(s)!")
                return redirect('comunicacao:enviar_email_massa')
            except BadHeaderError:
                messages.error(request, "Assunto inválido.")
            except Exception as e:
                messages.error(request, f"Erro ao enviar e-mail: {e}")
        else:
            messages.error(request, "Por favor, corrija os erros no formulário.")
    else:
        form = EmailMassaForm(organizacao=organizacao)

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': "Enviar E-mail em Massa",
    }
    return render(request, 'comunicacao/email/form_email_massa.html', context)

# --- VIEWS PARA NOTIFICAÇÕES ---
@login_required
@verificar_assinatura_valida
def lista_notificacoes(request):
    """
    Lista todas as notificações do usuário logado.
    """
    organizacao = get_organizacao_or_error(request)
    notificacoes_qs = Notificacao.objects.filter(user=request.user, organizacao=organizacao).order_by('-created_at')

    # Opcional: Filtrar por lidas/não lidas
    status_filter = request.GET.get('status', 'todas')
    if status_filter == 'nao_lidas':
        notificacoes_qs = notificacoes_qs.filter(is_read=False)
    elif status_filter == 'lidas':
        notificacoes_qs = notificacoes_qs.filter(is_read=True)

    context = {
        'notificacoes': notificacoes_qs,
        'organizacao': organizacao,
        'titulo_pagina': "Minhas Notificações",
        'status_filter': status_filter,
    }
    return render(request, 'comunicacao/notificacoes/lista_notificacoes.html', context)

@login_required
@verificar_assinatura_valida
def marcar_notificacao_lida(request, pk):
    """
    Marca uma notificação específica como lida.
    """
    organizacao = get_organizacao_or_error(request)
    notificacao = get_object_or_404(Notificacao, pk=pk, user=request.user, organizacao=organizacao)

    if request.method == 'POST':
        notificacao.is_read = True
        notificacao.save()
        messages.success(request, "Notificação marcada como lida.")
        # Redireciona para a URL da notificação se houver, senão para a lista
        if notificacao.url:
            return redirect(notificacao.url)
        return redirect('comunicacao:lista_notificacoes')
    
    messages.error(request, "Método inválido para marcar notificação como lida.")
    return redirect('comunicacao:lista_notificacoes')

@login_required
@verificar_assinatura_valida
def marcar_todas_notificacoes_lidas(request):
    organizacao = get_organizacao_or_404(request)
    Notificacao.objects.filter(user=request.user, organizacao=organizacao, is_read=False).update(is_read=True)
    messages.success(request, "Todas as notificações foram marcadas como lidas.")
    return redirect('comunicacao:lista_notificacoes')