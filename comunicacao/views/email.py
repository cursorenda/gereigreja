from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError
from django.shortcuts import redirect, render

from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error

from ..forms import EmailMassaForm
from ..selectors import filtrar_membros_email_destino, listar_destinatarios_email
from ..services import enviar_email_massa as enviar_email_massa_service


@login_required
@verificar_assinatura_valida
def templates_email(request):
    """Exibe os templates de e-mail disponíveis."""
    return render(request, 'comunicacao/templates_email.html')


@login_required
def visualizar_template_email_massa(request):
    """Renderiza preview do template de e-mail em massa."""
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
    """Renderiza preview do template de redefinição de senha."""
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

            membros_qs = filtrar_membros_email_destino(
                ministerio=ministerio,
                igrejas_destino=igrejas_destino,
                tipos_pessoa=tipos_pessoa,
                status_pessoa=status_pessoa,
                apenas_ativos_para_relatorios=apenas_ativos_para_relatorios,
                aniversariantes_do_mes=aniversariantes_do_mes,
            )
            destinatarios_emails = listar_destinatarios_email(membros_qs)

            if not destinatarios_emails:
                messages.warning(request, 'Nenhum destinatário encontrado com os critérios selecionados.')
                return redirect('comunicacao:enviar_email_massa')

            try:
                total_enviados = enviar_email_massa_service(
                    ministerio=ministerio,
                    assunto=assunto,
                    mensagem=mensagem,
                    destinatarios_emails=destinatarios_emails,
                    igrejas_destino=igrejas_destino,
                )
                messages.success(request, f'E-mail enviado com sucesso para {total_enviados} destinatário(s)!')
                return redirect('comunicacao:enviar_email_massa')
            except BadHeaderError:
                messages.error(request, 'Assunto inválido.')
            except Exception as exc:
                messages.error(request, f'Erro ao enviar e-mail: {exc}')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = EmailMassaForm(ministerio=ministerio)

    return render(
        request,
        'comunicacao/email/form_email_massa.html',
        {
            'form': form,
            'ministerio': ministerio,
            'titulo_pagina': 'Enviar E-mail em Massa',
        },
    )
