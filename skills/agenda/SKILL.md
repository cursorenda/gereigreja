---
name: "gerenciando-agenda"
description: "Gerencia compromissos, reuniões e agenda da igreja. Use para criar compromissos, agendar reuniões ou ver calendário geral."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Criar ou editar compromissos da agenda
- Agendar reuniões e cultos
- Gerenciar calendário da igreja
- Enviar lembretes de compromissos
- Verificar disponibilidade de horários

## Estrutura de Dados

### Compromisso
```python
class Compromisso(models.Model):
    TIPO_CHOICES = [
        ('culto', 'Culto'),
        ('reuniao', 'Reunião'),
        ('ensaio', 'Ensaio'),
        ('evento', 'Evento'),
        ('outro', 'Outro')
    ]
    
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local = models.CharField(max_length=200)
    responsavel = models.ForeignKey(Pessoa)
    organizacao = models.ForeignKey(Organizacao)
    recorrente = models.BooleanField(default=False)
    frequencia = models.CharField(max_length=20, blank=True)  # diaria, semanal, mensal
    ativo = models.BooleanField(default=True)
```

### Participante
```python
class Participante(models.Model):
    compromisso = models.ForeignKey(Compromisso)
    pessoa = models.ForeignKey(Pessoa)
    confirmado = models.BooleanField(default=False)
    data_confirmacao = models.DateTimeField(null=True)
```

### Lembrete
```python
class Lembrete(models.Model):
    compromisso = models.ForeignKey(Compromisso)
    antecedencia = models.IntegerField()  # Em minutos
    enviado = models.BooleanField(default=False)
    data_envio = models.DateTimeField(null=True)
```

## Regras de Negócio

1. **Data Fim > Data Início**: Validar sempre
2. **Conflito de Horário**: Alertar se mesmo local/horário
3. **Lembrete**: Enviar com até 24h de antecedência
4. **Recorrência**: Criar automaticamente próximas ocorrências
5. **Cancelamento**: Notificar todos os participantes

## Exemplos de Uso

### Criar Compromisso
```python
compromisso = Compromisso.objects.create(
    titulo='Culto de Domingo',
    descricao='Culto dominical regular',
    tipo='culto',
    data_inicio=datetime(2026, 2, 9, 19, 0),
    data_fim=datetime(2026, 2, 9, 21, 0),
    local='Templo Principal',
    responsavel=pastor,
    organizacao=organizacao,
    recorrente=True,
    frequencia='semanal'
)
```

### Criar Compromisso Recorrente
```python
def criar_compromisso_recorrente(dados, repeticoes=12):
    """
    Cria compromisso que se repete (ex: cultos semanais)
    """
    compromisso_pai = Compromisso.objects.create(**dados)
    
    # Criar ocorrências futuras
    data_atual = dados['data_inicio']
    
    for i in range(1, repeticoes):
        if dados['frequencia'] == 'semanal':
            data_atual += timedelta(weeks=1)
        elif dados['frequencia'] == 'mensal':
            data_atual += relativedelta(months=1)
        elif dados['frequencia'] == 'diaria':
            data_atual += timedelta(days=1)
        
        Compromisso.objects.create(
            titulo=dados['titulo'],
            descricao=dados['descricao'],
            tipo=dados['tipo'],
            data_inicio=data_atual,
            data_fim=data_atual.replace(hour=dados['data_fim'].hour),
            local=dados['local'],
            responsavel=dados['responsavel'],
            organizacao=dados['organizacao']
        )
    
    return compromisso_pai
```

### Adicionar Participantes
```python
def adicionar_participantes(compromisso_id, pessoas_ids):
    compromisso = Compromisso.objects.get(id=compromisso_id)
    
    for pessoa_id in pessoas_ids:
        Participante.objects.create(
            compromisso=compromisso,
            pessoa_id=pessoa_id
        )
        
        # Enviar convite por e-mail
        enviar_convite_compromisso(compromisso, pessoa_id)
```

### Verificar Conflito de Horário
```python
def verificar_conflito(local, data_inicio, data_fim, compromisso_id=None):
    """
    Verifica se há outro compromisso no mesmo local e horário
    """
    conflitos = Compromisso.objects.filter(
        local=local,
        ativo=True
    ).filter(
        # Sobreposição de horários
        Q(data_inicio__lt=data_fim) & Q(data_fim__gt=data_inicio)
    )
    
    # Excluir o próprio compromisso (em caso de edição)
    if compromisso_id:
        conflitos = conflitos.exclude(id=compromisso_id)
    
    return conflitos.exists()
```

### Agenda do Dia
```python
def agenda_do_dia(organizacao_id, data=None):
    if not data:
        data = date.today()
    
    compromissos = Compromisso.objects.filter(
        organizacao_id=organizacao_id,
        data_inicio__date=data,
        ativo=True
    ).order_by('data_inicio')
    
    return [{
        'titulo': c.titulo,
        'horario': c.data_inicio.strftime('%H:%M'),
        'local': c.local,
        'responsavel': c.responsavel.nome,
        'participantes': c.participante_set.count()
    } for c in compromissos]
```

### Enviar Lembretes
```python
from django.utils import timezone

def enviar_lembretes_pendentes():
    """
    Executar via cron job a cada hora
    """
    agora = timezone.now()
    
    # Buscar compromissos nas próximas 24h sem lembrete enviado
    compromissos = Compromisso.objects.filter(
        data_inicio__gt=agora,
        data_inicio__lt=agora + timedelta(hours=24),
        ativo=True
    )
    
    for compromisso in compromissos:
        # Verificar se já tem lembrete enviado
        lembrete = Lembrete.objects.filter(
            compromisso=compromisso,
            enviado=True
        ).first()
        
        if not lembrete:
            # Enviar para todos os participantes
            participantes = Participante.objects.filter(compromisso=compromisso)
            
            for p in participantes:
                enviar_email_lembrete(compromisso, p.pessoa)
            
            # Registrar lembrete
            Lembrete.objects.create(
                compromisso=compromisso,
                antecedencia=24*60,  # 24 horas
                enviado=True,
                data_envio=agora
            )
```

### Calendário Mensal
```python
def calendario_mensal(organizacao_id, mes, ano):
    primeiro_dia = date(ano, mes, 1)
    ultimo_dia = date(ano, mes, calendar.monthrange(ano, mes)[1])
    
    compromissos = Compromisso.objects.filter(
        organizacao_id=organizacao_id,
        data_inicio__date__gte=primeiro_dia,
        data_inicio__date__lte=ultimo_dia,
        ativo=True
    ).order_by('data_inicio')
    
    # Agrupar por dia
    calendario = {}
    for c in compromissos:
        dia = c.data_inicio.date()
        if dia not in calendario:
            calendario[dia] = []
        calendario[dia].append({
            'titulo': c.titulo,
            'horario': c.data_inicio.strftime('%H:%M'),
            'tipo': c.get_tipo_display()
        })
    
    return calendario
```

## Integração com Google Calendar (Opcional)

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def sincronizar_com_google(compromisso):
    """
    Adiciona compromisso no Google Calendar
    """
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('calendar', 'v3', credentials=creds)
    
    evento = {
        'summary': compromisso.titulo,
        'location': compromisso.local,
        'description': compromisso.descricao,
        'start': {
            'dateTime': compromisso.data_inicio.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
        'end': {
            'dateTime': compromisso.data_fim.isoformat(),
            'timeZone': 'America/Sao_Paulo',
        },
    }
    
    event = service.events().insert(calendarId='primary', body=evento).execute()
    return event['id']
```

## Boas Práticas

1. **Verificar conflitos** antes de criar compromisso
2. **Enviar lembretes** 24h antes
3. **Confirmação de presença** para reuniões importantes
4. **Recorrência automática** para compromissos fixos (cultos)
5. **Notificar cancelamento** imediatamente
6. **Backup da agenda** semanalmente
7. **Logs de alterações** - quem mudou o quê e quando
8. **Visualização por tipo** - filtrar cultos, reuniões, etc.

## Templates de Compromissos Comuns

```python
TEMPLATES_COMPROMISSOS = {
    'culto_domingo': {
        'titulo': 'Culto de Domingo',
        'tipo': 'culto',
        'horario': '19:00',
        'duracao': 2,  # horas
        'recorrente': True,
        'frequencia': 'semanal'
    },
    'ensaio_louvor': {
        'titulo': 'Ensaio de Louvor',
        'tipo': 'ensaio',
        'horario': '19:30',
        'duracao': 1.5,
        'recorrente': True,
        'frequencia': 'semanal'
    },
    'reuniao_lideranca': {
        'titulo': 'Reunião de Liderança',
        'tipo': 'reuniao',
        'horario': '20:00',
        'duracao': 2,
        'recorrente': True,
        'frequencia': 'mensal'
    }
}
```
