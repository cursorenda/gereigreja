---
name: "gerenciando-suporte"
description: "Gerencia tickets de suporte e atendimento aos usuários. Use para abrir chamados, responder dúvidas ou resolver problemas técnicos."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Criar ou responder tickets de suporte
- Registrar problemas técnicos
- Gerenciar atendimento aos usuários
- Categorizar e priorizar chamados
- Gerar relatórios de suporte

## Estrutura de Dados

### Ticket
```python
class Ticket(models.Model):
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('em_andamento', 'Em Andamento'),
        ('aguardando', 'Aguardando Usuário'),
        ('resolvido', 'Resolvido'),
        ('fechado', 'Fechado')
    ]
    
    PRIORIDADE_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente')
    ]
    
    CATEGORIA_CHOICES = [
        ('bug', 'Bug/Erro'),
        ('duvida', 'Dúvida'),
        ('feature', 'Nova Funcionalidade'),
        ('melhoria', 'Melhoria'),
        ('outro', 'Outro')
    ]
    
    numero = models.CharField(max_length=20, unique=True)  # Ex: #2026-001
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto')
    
    solicitante = models.ForeignKey(User, related_name='tickets_solicitados')
    responsavel = models.ForeignKey(User, related_name='tickets_responsavel', null=True)
    organizacao = models.ForeignKey(Organizacao)
    
    data_abertura = models.DateTimeField(auto_now_add=True)
    data_fechamento = models.DateTimeField(null=True)
    
    anexos = models.JSONField(default=list)  # URLs de prints/arquivos
```

### Resposta
```python
class Resposta(models.Model):
    ticket = models.ForeignKey(Ticket)
    usuario = models.ForeignKey(User)
    mensagem = models.TextField()
    interna = models.BooleanField(default=False)  # Nota interna (não visível ao solicitante)
    data_criacao = models.DateTimeField(auto_now_add=True)
    anexos = models.JSONField(default=list)
```

### Categoria Base de Conhecimento
```python
class ArtigoKnowledgeBase(models.Model):
    titulo = models.CharField(max_length=200)
    conteudo = models.TextField()
    categoria = models.CharField(max_length=50)
    tags = models.JSONField(default=list)
    visualizacoes = models.IntegerField(default=0)
    util = models.IntegerField(default=0)  # Quantas pessoas marcaram como útil
    ativo = models.BooleanField(default=True)
```

## Regras de Negócio

1. **Número Único**: Formato YYYY-NNN (ex: 2026-001)
2. **SLA por Prioridade**:
   - Urgente: 2h
   - Alta: 8h
   - Média: 24h
   - Baixa: 72h
3. **Auto-atribuição**: Responsável pode pegar tickets abertos
4. **Feedback**: Solicitar após fechamento
5. **Reabrir**: Permitir até 7 dias após fechamento

## Exemplos de Uso

### Criar Ticket
```python
def criar_ticket(solicitante, titulo, descricao, categoria, prioridade):
    # Gerar número único
    ano_atual = date.today().year
    ultimo = Ticket.objects.filter(
        numero__startswith=str(ano_atual)
    ).order_by('-numero').first()
    
    if ultimo:
        ultimo_num = int(ultimo.numero.split('-')[1])
        novo_num = f"{ano_atual}-{(ultimo_num + 1):03d}"
    else:
        novo_num = f"{ano_atual}-001"
    
    ticket = Ticket.objects.create(
        numero=novo_num,
        titulo=titulo,
        descricao=descricao,
        categoria=categoria,
        prioridade=prioridade,
        solicitante=solicitante,
        organizacao=solicitante.perfil.organizacao
    )
    
    # Notificar equipe de suporte
    notificar_novo_ticket(ticket)
    
    return ticket
```

### Responder Ticket
```python
def responder_ticket(ticket_id, usuario, mensagem, mudar_status=None):
    ticket = Ticket.objects.get(id=ticket_id)
    
    # Criar resposta
    resposta = Resposta.objects.create(
        ticket=ticket,
        usuario=usuario,
        mensagem=mensagem
    )
    
    # Atualizar status se necessário
    if mudar_status:
        ticket.status = mudar_status
        ticket.save()
    
    # Notificar solicitante (se não for nota interna)
    if not resposta.interna:
        notificar_solicitante(ticket, resposta)
    
    return resposta
```

### Atribuir Responsável
```python
def atribuir_ticket(ticket_id, responsavel_id):
    ticket = Ticket.objects.get(id=ticket_id)
    ticket.responsavel_id = responsavel_id
    ticket.status = 'em_andamento'
    ticket.save()
    
    # Notificar responsável
    notificar_atribuicao(ticket)
```

### Fechar Ticket
```python
def fechar_ticket(ticket_id, solucao):
    ticket = Ticket.objects.get(id=ticket_id)
    
    # Adicionar solução como resposta
    Resposta.objects.create(
        ticket=ticket,
        usuario=ticket.responsavel,
        mensagem=f"**Solução:**\n{solucao}"
    )
    
    # Atualizar status
    ticket.status = 'resolvido'
    ticket.data_fechamento = timezone.now()
    ticket.save()
    
    # Solicitar feedback
    enviar_pesquisa_satisfacao(ticket)
```

### Dashboard de Suporte
```python
def dashboard_suporte(periodo_dias=30):
    data_inicio = timezone.now() - timedelta(days=periodo_dias)
    
    tickets = Ticket.objects.filter(data_abertura__gte=data_inicio)
    
    return {
        'total_tickets': tickets.count(),
        'abertos': tickets.filter(status='aberto').count(),
        'em_andamento': tickets.filter(status='em_andamento').count(),
        'resolvidos': tickets.filter(status='resolvido').count(),
        'por_categoria': tickets.values('categoria').annotate(total=Count('id')),
        'por_prioridade': tickets.values('prioridade').annotate(total=Count('id')),
        'tempo_medio_resolucao': calcular_tempo_medio(tickets.filter(status='resolvido')),
        'sla_compliance': calcular_sla_compliance(tickets)
    }
```

### Calcular Tempo de Resolução
```python
def calcular_tempo_medio(tickets_resolvidos):
    tempos = []
    
    for ticket in tickets_resolvidos:
        if ticket.data_fechamento:
            tempo = ticket.data_fechamento - ticket.data_abertura
            tempos.append(tempo.total_seconds() / 3600)  # Em horas
    
    if tempos:
        return sum(tempos) / len(tempos)
    return 0
```

### Verificar SLA
```python
def verificar_sla(ticket):
    """
    Retorna se ticket está dentro do SLA
    """
    sla_horas = {
        'urgente': 2,
        'alta': 8,
        'media': 24,
        'baixa': 72
    }
    
    limite = sla_horas.get(ticket.prioridade, 24)
    tempo_decorrido = (timezone.now() - ticket.data_abertura).total_seconds() / 3600
    
    return {
        'dentro_sla': tempo_decorrido < limite,
        'tempo_decorrido': tempo_decorrido,
        'tempo_restante': limite - tempo_decorrido
    }
```

### Buscar Artigos da Base de Conhecimento
```python
def buscar_solucao(query):
    """
    Busca artigos relacionados ao problema
    """
    artigos = ArtigoKnowledgeBase.objects.filter(
        Q(titulo__icontains=query) | Q(conteudo__icontains=query),
        ativo=True
    ).order_by('-util')[:5]
    
    return artigos
```

### Relatório de Tickets por Usuário
```python
def relatorio_responsavel(responsavel_id, mes, ano):
    tickets = Ticket.objects.filter(
        responsavel_id=responsavel_id,
        data_abertura__month=mes,
        data_abertura__year=ano
    )
    
    return {
        'total_atendidos': tickets.count(),
        'resolvidos': tickets.filter(status='resolvido').count(),
        'em_andamento': tickets.filter(status='em_andamento').count(),
        'tempo_medio': calcular_tempo_medio(tickets.filter(status='resolvido')),
        'satisfacao_media': calcular_satisfacao_media(tickets)
    }
```

## Templates de Resposta Rápida

```python
RESPOSTAS_RAPIDAS = {
    'aguardando_informacoes': """
Olá! Para melhor atender sua solicitação, preciso de mais informações:

1. Quando o problema começou?
2. Você consegue reproduzir o erro?
3. Pode enviar um print da tela?

Aguardo seu retorno. Obrigado!
    """,
    
    'resolvido_comum': """
O problema foi resolvido! 

A causa era: [DESCREVER]

Se o problema persistir, por favor reabra este ticket.

Obrigado!
    """,
    
    'orientacao_uso': """
Entendo sua dúvida. Vou orientar o passo a passo:

1. [PASSO 1]
2. [PASSO 2]
3. [PASSO 3]

Se precisar de mais ajuda, estou à disposição!
    """
}
```

## Boas Práticas

1. **Priorizar urgências** - SLA rigoroso para tickets urgentes
2. **Base de conhecimento** - documentar soluções comuns
3. **Resposta inicial rápida** - reconhecer ticket em até 1h
4. **Notas internas** - registrar tentativas de solução
5. **Satisfação do cliente** - pesquisa após fechamento
6. **Auto-atendimento** - incentivar busca na KB
7. **Escalação** - tickets não resolvidos sobem prioridade
8. **Métricas** - acompanhar tempo médio e satisfação

## Notificações

### Por E-mail
- Novo ticket criado → Equipe de suporte
- Ticket atribuído → Responsável
- Nova resposta → Solicitante
- Ticket resolvido → Solicitante (com pesquisa)
- SLA próximo do limite → Responsável

### No Sistema
- Badge com número de tickets abertos
- Alerta para tickets fora do SLA
- Notificação de nova resposta
