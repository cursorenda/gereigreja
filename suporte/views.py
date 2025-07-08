from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Ticket, RespostaTicket
from .forms import TicketForm, RespostaTicketForm
from core.utils import get_organizacao_or_error
from core.decorators import verificar_assinatura_valida
from django.db.models import Q

@login_required
@verificar_assinatura_valida
def lista_tickets(request):
    organizacao = get_organizacao_or_error(request)
    # Admin da Org vê todos os tickets da organização, usuário comum vê apenas os seus.
    if request.user.groups.filter(name='Admin Organizacao').exists():
        tickets_qs = Ticket.objects.filter(organizacao=organizacao)
    else:
        tickets_qs = Ticket.objects.filter(user=request.user)

    context = {
        'tickets': tickets_qs.order_by('-data_criacao'),
        'organizacao': organizacao,
        'titulo_pagina': "Meus Tickets de Suporte",
    }
    return render(request, 'suporte/lista_tickets.html', context)

@login_required
@verificar_assinatura_valida
def criar_ticket(request):
    organizacao = get_organizacao_or_error(request)
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.organizacao = organizacao
            ticket.save()
            messages.success(request, "Seu ticket de suporte foi aberto com sucesso! Responderemos em breve.")
            return redirect('suporte:lista_tickets')
    else:
        form = TicketForm()

    context = {
        'form': form,
        'organizacao': organizacao,
        'titulo_pagina': "Abrir Novo Ticket de Suporte",
    }
    return render(request, 'suporte/criar_ticket.html', context)

@login_required
@verificar_assinatura_valida
def detalhe_ticket(request, pk):
    organizacao = get_organizacao_or_error(request)

    # Garante que o usuário só pode ver seus próprios tickets,
    # ou que um admin da org pode ver todos os tickets da org.
    query_filter = Q(pk=pk)
    if not request.user.groups.filter(name='Admin Organizacao').exists():
        query_filter &= Q(user=request.user)
    else:
        query_filter &= Q(organizacao=organizacao)

    ticket = get_object_or_404(Ticket, query_filter)
    respostas = ticket.respostas.all().order_by('data_criacao')

    if request.method == 'POST':
        form = RespostaTicketForm(request.POST)
        if form.is_valid():
            resposta = form.save(commit=False)
            resposta.ticket = ticket
            resposta.autor = request.user
            resposta.save()
            messages.success(request, "Sua resposta foi enviada com sucesso.")
            return redirect('suporte:detalhe_ticket', pk=ticket.pk)
    else:
        form = RespostaTicketForm()

    context = {
        'ticket': ticket, 'respostas': respostas, 'form': form, 'organizacao': organizacao,
        'titulo_pagina': f"Ticket #{ticket.pk}: {ticket.assunto}",
    }
    return render(request, 'suporte/detalhe_ticket.html', context)
