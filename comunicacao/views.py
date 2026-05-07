from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date

from .models import Aviso
from .forms import AvisoForm # Manter o AvisoForm
from .models import WhatsAppConfiguracao, WhatsAppMensagemLog

from core.utils import get_ministerio_or_error
from configuracao.models import Igreja # Para filtrar igrejas
from .utils import can_manage_avisos # Para contexto de template
from core.decorators import verificar_assinatura_valida, page_access_required # Decorator de assinatura
from .services_whatsapp import send_whatsapp_text, WhatsAppSendError

# Crie suas views aqui.

@login_required
@verificar_assinatura_valida
def templates_email(request):
    """
    View para exibir os templates de e-mail disponíveis.
    """
    return render(request, 'comunicacao/templates_email.html')

@login_required
def visualizar_template_email_massa(request):
    """
    Renderiza o template de e-mail em massa para visualização.
    """
    contexto = {
        'assunto': 'Exemplo de Assunto',
        'mensagem': 'Este é um exemplo de mensagem para o e-mail em massa.',
        'ministerio_nome': 'Nome do Ministério',
        'igreja_nome': 'Nome da Igreja',
        'remetente_email': 'contato@exemplo.com',
    }
    return render(request, 'comunicacao/email/email_massa_template.html', contexto)

@login_required
def visualizar_template_password_reset(request):
    """
    Renderiza o template de redefinição de senha para visualização.
    """
    contexto = {
        'site_name': 'Gereigreja',
        'protocol': 'https',
        'domain': 'gereigreja.site',
        'uid': 'uid-exemplo',
        'token': 'token-exemplo',
        'user': type('User', (), {'get_username': lambda self: 'usuario_exemplo'})(),
    }
    return render(request, 'contas/password_reset_email.html', contexto)

@login_required
@verificar_assinatura_valida
@page_access_required('mural_avisos')
def lista_avisos(request):
    ministerio = get_ministerio_or_error(request)
    avisos_qs = Aviso.objects.filter(ministerio=ministerio, publicado=True)

    # Filtra avisos que não expiraram ou não têm data de expiração
    avisos_qs = avisos_qs.filter(
        Q(data_expiracao__isnull=True) | Q(data_expiracao__gte=timezone.now().date())
    )

    # Filtra por igreja ativa (se houver) ou mostra avisos para toda a ministério
    # ou para as igrejas específicas que o usuário pode ver (se a lógica for mais complexa no futuro)
    if request.igreja_ativa:
        avisos_qs = avisos_qs.filter(
            Q(igrejas_destino__isnull=True) | Q(igrejas_destino=request.igreja_ativa)
        ).distinct() # distinct() é importante por causa do ManyToMany
    else:
        # Se nenhuma igreja ativa, mostra avisos para toda a ministério
        # ou aqueles que não têm igrejas destino específicas (são para toda a ministério)
        # Esta lógica pode precisar de ajuste dependendo de como você quer que "todas as igrejas" funcione
        # Por enquanto, mostra os que não têm igrejas_destino (para toda org)
        # ou os que têm alguma igreja destino (se o usuário for admin da org, por exemplo)
        # Para simplificar, se não há igreja ativa, mostramos os que são para toda a ministério.
        # Se o usuário for admin da org, ele verá todos os avisos do ministério de qualquer forma.
        avisos_qs = avisos_qs.filter(igrejas_destino__isnull=True).distinct()

    # Adicionar filtros de busca se necessário (ex: por título)
    query = request.GET.get('q')
    if query:
        avisos_qs = avisos_qs.filter(titulo__icontains=query)

    context = {
        'avisos': avisos_qs.order_by('-data_publicacao'),
        'ministerio': ministerio,
        'titulo_pagina': "Mural de Avisos",
        'can_manage': can_manage_avisos(request.user),
        'query': query,
    }
    return render(request, 'comunicacao/mural/lista_avisos.html', context)

@login_required
@verificar_assinatura_valida
@page_access_required('mural_avisos')
def detalhe_aviso(request, pk):
    ministerio = get_ministerio_or_error(request)
    aviso = get_object_or_404(Aviso, pk=pk, ministerio=ministerio, publicado=True)

    # Verifica se o aviso não expirou
    if aviso.data_expiracao and aviso.data_expiracao < timezone.now().date():
        raise PermissionDenied("Este aviso expirou.") # Ou redirecionar para lista com mensagem

    # Verifica se o aviso é para a igreja ativa do usuário ou para toda a ministério
    if request.igreja_ativa and aviso.igrejas_destino.exists() and request.igreja_ativa not in aviso.igrejas_destino.all():
        raise PermissionDenied("Você não tem permissão para ver este aviso específico para outra igreja.")

    context = {
        'aviso': aviso,
        'ministerio': ministerio,
        'titulo_pagina': aviso.titulo,
        'can_manage': can_manage_avisos(request.user),
    }
    return render(request, 'comunicacao/mural/detalhe_aviso.html', context)

@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def criar_aviso(request):
    ministerio = get_ministerio_or_error(request)
    if request.method == 'POST':
        form = AvisoForm(request.POST, ministerio=ministerio)
        form.fields['ministerio'].disabled = True
        if form.is_valid():
            try:
                aviso = form.save(commit=False)
                aviso.ministerio = ministerio # Garante a ministério correta
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
        form = AvisoForm(initial={'ministerio': ministerio, 'autor': request.user}, ministerio=ministerio)
        form.fields['ministerio'].disabled = True # Não permitir mudar a ministério
        # O campo autor pode ser preenchido automaticamente e desabilitado ou oculto
        # form.fields['autor'].disabled = True

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': "Criar Novo Aviso",
    }
    return render(request, 'comunicacao/mural/form_aviso.html', context)

@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def editar_aviso(request, pk):
    ministerio = get_ministerio_or_error(request)
    aviso = get_object_or_404(Aviso, pk=pk, ministerio=ministerio)

    if request.method == 'POST':
        form = AvisoForm(request.POST, instance=aviso, ministerio=ministerio)
        form.fields['ministerio'].disabled = True
        if form.is_valid():
            try:
                # Garante que a ministério não seja alterada
                if form.cleaned_data.get('ministerio') != ministerio:
                    raise PermissionDenied("Não é permitido alterar a ministério do aviso.")
                
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
        form = AvisoForm(instance=aviso, ministerio=ministerio)
        form.fields['ministerio'].disabled = True
        # form.fields['autor'].disabled = True # Se o autor não puder ser alterado

    context = {
        'form': form,
        'aviso': aviso,
        'ministerio': ministerio,
        'titulo_pagina': f"Editar Aviso: {aviso.titulo}",
    }
    return render(request, 'comunicacao/mural/form_aviso.html', context)

@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def excluir_aviso(request, pk):
    ministerio = get_ministerio_or_error(request)
    aviso = get_object_or_404(Aviso, pk=pk, ministerio=ministerio)

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
        'ministerio': ministerio,
        'titulo_pagina': f"Confirmar Exclusão: {aviso.titulo}",
    }
    return render(request, 'comunicacao/mural/confirmar_excluir_aviso.html', context)

# --- VIEWS PARA ENVIO DE E-MAIL EM MASSA ---
from .forms import EmailMassaForm, WhatsAppConfiguracaoForm, WhatsAppMassaForm # Importar formularios
from secretaria.models import Membro # Importar o modelo Membro

@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def enviar_email_massa(request):
    ministerio = get_ministerio_or_error(request)

    if request.method == 'POST':
        form = EmailMassaForm(request.POST, ministerio=ministerio)
        if form.is_valid():
            assunto = form.cleaned_data['assunto']
            mensagem = form.cleaned_data['mensagem']
            igrejas_destino = form.cleaned_data['igrejas_destino']
            tipos_pessoa = form.cleaned_data['tipos_pessoa']
            status_pessoa = form.cleaned_data['status_pessoa']
            apenas_ativos_para_relatorios = form.cleaned_data['apenas_ativos_para_relatorios']
            aniversariantes_do_mes = form.cleaned_data['aniversariantes_do_mes']

            # Construir o queryset de membros baseado nos filtros
            membros_qs = Membro.objects.filter(igreja__ministerio=ministerio)

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
                igreja_nome = None
                remetente_email = settings.DEFAULT_FROM_EMAIL
                # Se o filtro igrejas_destino retornar só uma igreja, use ela
                if igrejas_destino and igrejas_destino.count() == 1:
                    igreja = igrejas_destino.first()
                    igreja_nome = getattr(igreja, 'nome_igreja', None)
                    if getattr(igreja, 'email', None):
                        remetente_email = igreja.email

                html_message = render_to_string('comunicacao/email/email_massa_template.html', {
                    'assunto': assunto,
                    'mensagem': mensagem,
                    'ministerio_nome': ministerio.nome_fantasia,
                    'igreja_nome': igreja_nome,
                    'remetente_email': remetente_email,
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
        form = EmailMassaForm(ministerio=ministerio)

    context = {
        'form': form,
        'ministerio': ministerio,
        'titulo_pagina': "Enviar E-mail em Massa",
    }
    return render(request, 'comunicacao/email/form_email_massa.html', context)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def configurar_whatsapp(request):
    ministerio = get_ministerio_or_error(request)
    instance = None
    if request.igreja_ativa:
        instance = WhatsAppConfiguracao.objects.filter(igreja=request.igreja_ativa, ministerio=ministerio).first()

    if request.method == 'POST':
        form = WhatsAppConfiguracaoForm(request.POST, instance=instance, ministerio=ministerio)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ministerio = ministerio
            obj.save()
            messages.success(request, 'Configuracao de WhatsApp salva com sucesso.')
            return redirect('comunicacao:configurar_whatsapp')
        messages.error(request, 'Corrija os erros do formulario de configuracao WhatsApp.')
    else:
        initial = {}
        if request.igreja_ativa and not instance:
            initial['igreja'] = request.igreja_ativa
        form = WhatsAppConfiguracaoForm(instance=instance, initial=initial, ministerio=ministerio)

    return render(
        request,
        'comunicacao/whatsapp/configuracao_whatsapp.html',
        {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': 'Configuracao WhatsApp por Congregacao',
        },
    )


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def enviar_whatsapp_massa(request):
    ministerio = get_ministerio_or_error(request)

    if request.method == 'POST':
        form = WhatsAppMassaForm(request.POST, ministerio=ministerio)
        if form.is_valid():
            mensagem = form.cleaned_data['mensagem']
            igrejas_destino = form.cleaned_data['igrejas_destino']
            tipos_pessoa = form.cleaned_data['tipos_pessoa']
            status_pessoa = form.cleaned_data['status_pessoa']
            aniversariantes_do_mes = form.cleaned_data['aniversariantes_do_mes']
            somente_com_celular = form.cleaned_data['somente_com_celular']

            membros_qs = Membro.objects.filter(igreja__ministerio=ministerio)
            if igrejas_destino:
                membros_qs = membros_qs.filter(igreja__in=igrejas_destino)
            if tipos_pessoa:
                membros_qs = membros_qs.filter(tipo_pessoa__in=tipos_pessoa)
            if status_pessoa:
                membros_qs = membros_qs.filter(status_pessoa__in=status_pessoa)
            if aniversariantes_do_mes:
                hoje = date.today()
                membros_qs = membros_qs.filter(nascimento__month=hoje.month)
            if somente_com_celular:
                membros_qs = membros_qs.exclude(celular__isnull=True).exclude(celular='')

            enviados = 0
            falhas = 0
            for membro in membros_qs.select_related('igreja'):
                config = WhatsAppConfiguracao.objects.filter(
                    ministerio=ministerio,
                    igreja=membro.igreja,
                    ativo=True,
                ).first()
                if not config:
                    falhas += 1
                    continue
                texto = (
                    mensagem.replace('{nome}', membro.nome or '')
                    .replace('{igreja}', membro.igreja.nome_igreja if membro.igreja else '')
                    .replace('{ministerio}', ministerio.nome_fantasia)
                )
                try:
                    send_whatsapp_text(
                        config,
                        membro.celular,
                        texto,
                        tipo='manual',
                        ministerio=ministerio,
                        igreja=membro.igreja,
                        membro=membro,
                    )
                    enviados += 1
                except WhatsAppSendError:
                    falhas += 1

            if enviados:
                messages.success(request, f'WhatsApp enviado para {enviados} pessoa(s).')
            if falhas:
                messages.warning(request, f'{falhas} envio(s) falharam ou nao tinham configuracao ativa.')
            return redirect('comunicacao:enviar_whatsapp_massa')
        messages.error(request, 'Corrija os erros do formulario de envio WhatsApp.')
    else:
        form = WhatsAppMassaForm(ministerio=ministerio)

    return render(
        request,
        'comunicacao/whatsapp/form_whatsapp_massa.html',
        {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': 'Enviar WhatsApp em Massa',
        },
    )


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def logs_whatsapp(request):
    ministerio = get_ministerio_or_error(request)
    logs = WhatsAppMensagemLog.objects.filter(ministerio=ministerio).select_related('igreja', 'membro')[:200]
    return render(
        request,
        'comunicacao/whatsapp/logs_whatsapp.html',
        {
            'logs': logs,
            'ministerio': ministerio,
            'titulo_pagina': 'Logs de WhatsApp',
        },
    )


@csrf_exempt
@require_POST
def waha_webhook(request):
    token = request.headers.get('X-Webhook-Token') or request.GET.get('token')
    payload = request.body.decode('utf-8', errors='ignore')

    configuracao = None
    if token:
        configuracao = WhatsAppConfiguracao.objects.filter(webhook_token=token, ativo=True).first()
    if not configuracao:
        return HttpResponseForbidden('Webhook token invalido')

    WhatsAppMensagemLog.objects.create(
        ministerio=configuracao.ministerio,
        igreja=configuracao.igreja,
        configuracao=configuracao,
        tipo='webhook',
        status='recebido',
        telefone_destino='entrada',
        mensagem=payload[:3000],
        resposta_waha={'headers': dict(request.headers)},
    )
    return JsonResponse({'ok': True})
