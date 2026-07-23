from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError
from django.http import JsonResponse
from django.shortcuts import redirect, render

from core.decorators import page_access_required, verificar_assinatura_valida
from core.utils import get_ministerio_or_error
from secretaria.models import StatusPessoa, TipoPessoa

from ..forms import AutomacaoAniversariantesForm, EmailMassaForm
from ..selectors import (
    build_email_preview_data,
    filtrar_membros_email_destino,
    listar_agendamentos_aniversariantes,
    listar_destinatarios_email,
    listar_proximos_aniversariantes,
    obter_automacao_aniversariantes,
)
from ..services import enviar_email_massa as enviar_email_massa_service
from ..services import personalizar_template_comunicacao


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def preview_email_destinatarios(request):
    """Retorna uma prévia dos destinatários aptos para envio de e-mail em massa."""
    try:
        ministerio = get_ministerio_or_error(request)
        igreja_ativa = request.igreja_ativa

        tipos_pessoa_ids = [int(v) for v in request.GET.getlist('tipos_pessoa') if str(v).isdigit()]
        status_pessoa_ids = [int(v) for v in request.GET.getlist('status_pessoa') if str(v).isdigit()]
        graus_eclesiasticos = [v for v in request.GET.getlist('graus_eclesiasticos') if v]

        tipos_pessoa = TipoPessoa.objects.filter(pk__in=tipos_pessoa_ids) if tipos_pessoa_ids else TipoPessoa.objects.none()
        status_pessoa = StatusPessoa.objects.filter(pk__in=status_pessoa_ids) if status_pessoa_ids else StatusPessoa.objects.none()

        if igreja_ativa:
            igrejas_destino_ids = [igreja_ativa.pk]
        else:
            igrejas_destino_ids = [int(v) for v in request.GET.getlist('igrejas_destino') if str(v).isdigit()]

        membros_qs = filtrar_membros_email_destino(
            ministerio=ministerio,
            igrejas_destino=igrejas_destino_ids,
            tipos_pessoa=tipos_pessoa,
            graus_eclesiasticos=graus_eclesiasticos,
            status_pessoa=status_pessoa,
            aniversariantes_do_mes=request.GET.get('aniversariantes_do_mes') in ('on', 'true', '1'),
        )

        preview = build_email_preview_data(membros_qs=membros_qs, limite_nomes=200)
        return JsonResponse({'ok': True, **preview})
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def templates_email(request):
    """Exibe os templates de e-mail disponíveis."""
    return render(request, 'comunicacao/templates_email.html')


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
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
@verificar_assinatura_valida
@page_access_required('comunicacao')
def visualizar_template_email_aniversario(request):
    ministerio = get_ministerio_or_error(request)
    automacao = obter_automacao_aniversariantes(ministerio=ministerio)

    pessoa_fake = type(
        'PessoaPreview',
        (),
        {
            'nome': 'Maria de Souza',
            'nascimento': None,
            'igreja': type('IgrejaPreview', (), {'nome_igreja': 'Congregacao Central'})(),
            'email': 'maria@example.com',
        },
    )()
    contexto = {
        'assunto': personalizar_template_comunicacao(automacao.email_assunto_template, pessoa_fake, ministerio),
        'mensagem': personalizar_template_comunicacao(automacao.email_mensagem_template, pessoa_fake, ministerio),
        'ministerio_nome': ministerio.nome_fantasia,
        'igreja_nome': pessoa_fake.igreja.nome_igreja,
        'remetente_email': 'contato@exemplo.com',
    }
    return render(request, 'comunicacao/email/email_massa_template.html', contexto)


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
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
    igreja_ativa = request.igreja_ativa
    automacao_aniversarios = obter_automacao_aniversariantes(ministerio=ministerio)
    agendamentos_aniversario = listar_agendamentos_aniversariantes(ministerio=ministerio)
    proximos_aniversariantes = listar_proximos_aniversariantes(
        ministerio=ministerio,
        igreja=igreja_ativa,
    )

    if request.method == 'POST':
        form = EmailMassaForm(request.POST, ministerio=ministerio)
        if form.is_valid():
            assunto = form.cleaned_data['assunto']
            mensagem = form.cleaned_data['mensagem']
            if igreja_ativa:
                igrejas_destino = [igreja_ativa.pk]
            else:
                igrejas_destino = form.cleaned_data['igrejas_destino']
            tipos_pessoa = form.cleaned_data['tipos_pessoa']
            graus_eclesiasticos = form.cleaned_data['graus_eclesiasticos']
            status_pessoa = form.cleaned_data['status_pessoa']
            aniversariantes_do_mes = form.cleaned_data['aniversariantes_do_mes']

            membros_qs = filtrar_membros_email_destino(
                ministerio=ministerio,
                igrejas_destino=igrejas_destino,
                tipos_pessoa=tipos_pessoa,
                graus_eclesiasticos=graus_eclesiasticos,
                status_pessoa=status_pessoa,
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
            'igreja_ativa': igreja_ativa,
            'automacao_aniversarios': automacao_aniversarios,
            'agendamentos_aniversario': agendamentos_aniversario,
            'proximos_aniversariantes': proximos_aniversariantes,
            'titulo_pagina': 'Enviar E-mail em Massa',
        },
    )


@login_required
@verificar_assinatura_valida
@page_access_required('comunicacao')
def configurar_automacao_aniversariantes(request):
    ministerio = get_ministerio_or_error(request)
    automacao = obter_automacao_aniversariantes(ministerio=ministerio)

    if request.method == 'POST':
        form = AutomacaoAniversariantesForm(request.POST, instance=automacao)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.ministerio = ministerio
            obj.save()
            messages.success(request, 'Automacao de aniversariantes atualizada com sucesso.')
            return redirect('comunicacao:configurar_automacao_aniversariantes')
        messages.error(request, 'Corrija os erros da automacao de aniversariantes.')
    else:
        form = AutomacaoAniversariantesForm(instance=automacao)

    return render(
        request,
        'comunicacao/automacoes/aniversariantes.html',
        {
            'form': form,
            'ministerio': ministerio,
            'automacao': automacao,
            'agendamentos_aniversario': listar_agendamentos_aniversariantes(ministerio=ministerio),
            'proximos_aniversariantes': listar_proximos_aniversariantes(ministerio=ministerio),
            'titulo_pagina': 'Automacao de Aniversariantes',
        },
    )
