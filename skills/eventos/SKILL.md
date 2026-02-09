---
name: "gerenciando-eventos"
description: "Cria e gerencia eventos da igreja com controle de participantes. Use para cadastrar eventos, inscrições ou relatórios de presença."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Criar ou editar eventos da igreja
- Gerenciar inscrições de participantes
- Controlar presença em eventos
- Gerar relatórios de participação
- Enviar notificações de eventos

## Estrutura de Dados

### Evento
```python
class Evento(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data_inicio = models.DateTimeField()
    data_fim = models.DateTimeField()
    local = models.CharField(max_length=200)
    vagas_limitadas = models.BooleanField(default=False)
    numero_vagas = models.IntegerField(null=True, blank=True)
    organizacao = models.ForeignKey(Organizacao)
    ativo = models.BooleanField(default=True)
```

### Inscrição
```python
class Inscricao(models.Model):
    evento = models.ForeignKey(Evento)
    pessoa = models.ForeignKey(Pessoa)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=False)
    presente = models.BooleanField(default=False)
```

## Regras de Negócio

1. **Vagas Limitadas**: Verificar disponibilidade antes de aceitar inscrição
2. **Data de Início**: Não permitir eventos retroativos
3. **Confirmação**: Inscrição não é presença (confirmar separadamente)
4. **Notificações**: Enviar e-mail ao inscrever e 1 dia antes do evento

## Exemplos de Uso

### Criar Evento
```python
evento = Evento.objects.create(
    titulo='Culto de Celebração',
    descricao='Culto especial de aniversário da igreja',
    data_inicio=datetime(2026, 3, 15, 19, 0),
    data_fim=datetime(2026, 3, 15, 21, 0),
    local='Templo Principal',
    vagas_limitadas=True,
    numero_vagas=200,
    organizacao=organizacao
)
```

### Inscrever Participante
```python
def inscrever_participante(evento_id, pessoa_id):
    evento = Evento.objects.get(id=evento_id)
    
    # Verificar vagas
    if evento.vagas_limitadas:
        inscritos = Inscricao.objects.filter(evento=evento).count()
        if inscritos >= evento.numero_vagas:
            raise Exception('Evento lotado')
    
    # Criar inscrição
    inscricao = Inscricao.objects.create(
        evento=evento,
        pessoa_id=pessoa_id
    )
    
    # Enviar e-mail de confirmação
    enviar_email_inscricao(inscricao)
    
    return inscricao
```

### Relatório de Presença
```python
def relatorio_presenca(evento_id):
    inscricoes = Inscricao.objects.filter(evento_id=evento_id)
    
    return {
        'total_inscritos': inscricoes.count(),
        'confirmados': inscricoes.filter(confirmado=True).count(),
        'presentes': inscricoes.filter(presente=True).count(),
        'taxa_presenca': (inscricoes.filter(presente=True).count() / inscricoes.count() * 100) if inscricoes.count() > 0 else 0
    }
```

## Scripts Úteis

### Listar Inscritos
```bash
# Ver eventos disponíveis
python skills/eventos/scripts/listar_inscritos.py --lista

# Listar inscritos de um evento
python skills/eventos/scripts/listar_inscritos.py 15

# Exportar para CSV
python skills/eventos/scripts/listar_inscritos.py 15 --exportar csv
```

Gera listagem com:
- Total de inscritos e confirmados
- Nome, telefone e status de cada inscrito
- Data de inscrição
- Exportação para CSV com todos os dados

## Boas Práticas

- Sempre validar datas (início < fim)
- Enviar notificações 24h antes do evento
- Permitir cancelamento de inscrição até 2h antes
- Registrar histórico de presença para relatórios futuros
- Exportar lista de participantes em PDF/Excel
- Usar scripts para gerar listas atualizadas rapidamente
