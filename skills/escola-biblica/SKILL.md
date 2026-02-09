---
name: "gerenciando-escola-biblica"
description: "Gerencia turmas, alunos, professores e materiais da escola bíblica. Use para cadastro de turmas, frequência ou planejamento de aulas."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Criar ou editar turmas da escola bíblica
- Gerenciar alunos e professores
- Controlar frequência e presença
- Planejar aulas e conteúdo
- Gerar relatórios de participação

## Estrutura de Dados

### Turma
```python
class Turma(models.Model):
    nome = models.CharField(max_length=100)  # Ex: "Adolescentes", "Adultos"
    descricao = models.TextField()
    faixa_etaria_min = models.IntegerField()  # Idade mínima
    faixa_etaria_max = models.IntegerField()  # Idade máxima
    professor = models.ForeignKey(Pessoa, related_name='turmas_professor')
    dia_semana = models.CharField(max_length=20)  # Domingo, Sábado
    horario = models.TimeField()
    sala = models.CharField(max_length=50)
    organizacao = models.ForeignKey(Organizacao)
    ativa = models.BooleanField(default=True)
```

### Matrícula (Aluno na Turma)
```python
class Matricula(models.Model):
    turma = models.ForeignKey(Turma)
    aluno = models.ForeignKey(Pessoa)
    data_matricula = models.DateField(auto_now_add=True)
    ativa = models.BooleanField(default=True)
```

### Aula
```python
class Aula(models.Model):
    turma = models.ForeignKey(Turma)
    data = models.DateField()
    tema = models.CharField(max_length=200)
    conteudo = models.TextField()
    material_utilizado = models.TextField(blank=True)
    professor = models.ForeignKey(Pessoa)
    realizada = models.BooleanField(default=False)
```

### Frequência
```python
class Frequencia(models.Model):
    aula = models.ForeignKey(Aula)
    aluno = models.ForeignKey(Pessoa)
    presente = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True)
```

## Regras de Negócio

1. **Faixa Etária**: Aluno deve estar na faixa etária da turma
2. **Professor Ativo**: Apenas membros ativos podem ser professores
3. **Frequência**: Registrar no máximo 24h após a aula
4. **Capacidade**: Limitar número de alunos por turma
5. **Matrícula Única**: Aluno não pode estar em duas turmas do mesmo horário

## Exemplos de Uso

### Criar Turma
```python
turma = Turma.objects.create(
    nome='Adolescentes',
    descricao='Turma para adolescentes de 12 a 17 anos',
    faixa_etaria_min=12,
    faixa_etaria_max=17,
    professor=professor_joao,
    dia_semana='Domingo',
    horario='09:00',
    sala='Sala 3',
    organizacao=organizacao
)
```

### Matricular Aluno
```python
def matricular_aluno(turma_id, aluno_id):
    turma = Turma.objects.get(id=turma_id)
    aluno = Pessoa.objects.get(id=aluno_id)
    
    # Validar faixa etária
    idade = calcular_idade(aluno.data_nascimento)
    if not (turma.faixa_etaria_min <= idade <= turma.faixa_etaria_max):
        raise Exception(f'Aluno fora da faixa etária ({turma.faixa_etaria_min}-{turma.faixa_etaria_max} anos)')
    
    # Verificar conflito de horário
    matriculas_ativas = Matricula.objects.filter(
        aluno=aluno,
        ativa=True,
        turma__dia_semana=turma.dia_semana,
        turma__horario=turma.horario
    )
    if matriculas_ativas.exists():
        raise Exception('Aluno já matriculado em outra turma neste horário')
    
    # Criar matrícula
    return Matricula.objects.create(turma=turma, aluno=aluno)
```

### Registrar Aula
```python
aula = Aula.objects.create(
    turma=turma_adolescentes,
    data=date.today(),
    tema='O Amor de Deus',
    conteudo='Estudo sobre João 3:16...',
    material_utilizado='Bíblia, vídeo, slides',
    professor=professor_joao,
    realizada=True
)
```

### Registrar Frequência
```python
def registrar_frequencia(aula_id, presencas):
    """
    presencas = [
        {'aluno_id': 1, 'presente': True},
        {'aluno_id': 2, 'presente': False, 'observacoes': 'Viajando'},
        ...
    ]
    """
    aula = Aula.objects.get(id=aula_id)
    
    for p in presencas:
        Frequencia.objects.create(
            aula=aula,
            aluno_id=p['aluno_id'],
            presente=p['presente'],
            observacoes=p.get('observacoes', '')
        )
```

### Relatório de Frequência
```python
def relatorio_frequencia_aluno(aluno_id, turma_id, mes, ano):
    frequencias = Frequencia.objects.filter(
        aluno_id=aluno_id,
        aula__turma_id=turma_id,
        aula__data__month=mes,
        aula__data__year=ano
    )
    
    total_aulas = frequencias.count()
    presencas = frequencias.filter(presente=True).count()
    
    return {
        'total_aulas': total_aulas,
        'presencas': presencas,
        'faltas': total_aulas - presencas,
        'percentual': (presencas / total_aulas * 100) if total_aulas > 0 else 0
    }
```

### Planejar Aulas do Trimestre
```python
from dateutil.relativedelta import relativedelta

def planejar_trimestre(turma_id, data_inicio, temas):
    """
    temas = [
        'O Amor de Deus',
        'A Graça de Jesus',
        'O Poder do Espírito Santo',
        ...
    ]
    """
    turma = Turma.objects.get(id=turma_id)
    data_aula = data_inicio
    
    for tema in temas:
        Aula.objects.create(
            turma=turma,
            data=data_aula,
            tema=tema,
            professor=turma.professor,
            realizada=False
        )
        # Próxima aula (1 semana depois)
        data_aula += timedelta(days=7)
```

## Dashboard de Escola Bíblica

### Estatísticas Gerais
```python
def dashboard_escola_biblica(organizacao_id):
    turmas = Turma.objects.filter(organizacao_id=organizacao_id, ativa=True)
    
    return {
        'total_turmas': turmas.count(),
        'total_alunos': Matricula.objects.filter(turma__in=turmas, ativa=True).count(),
        'total_professores': turmas.values('professor').distinct().count(),
        'aulas_mes': Aula.objects.filter(
            turma__in=turmas,
            data__month=date.today().month,
            realizada=True
        ).count(),
        'media_frequencia': calcular_media_frequencia(turmas)
    }
```

## Boas Práticas

1. **Validar faixa etária** antes de matricular
2. **Notificar professor** quando aluno é matriculado
3. **Lembrete de aula** - enviar no dia anterior
4. **Frequência obrigatória** - registrar todas as aulas
5. **Backup de conteúdo** - salvar planejamento de aulas
6. **Relatórios mensais** - enviar para pais/responsáveis
7. **Material didático** - organizar por trimestre/semestre
8. **Reunião de professores** - agendar mensalmente

## Planejamento Anual Sugerido

```
Trimestre 1 (Jan-Mar): Fundamentos da Fé
Trimestre 2 (Abr-Jun): Vida de Jesus
Trimestre 3 (Jul-Set): Livro de Atos
Trimestre 4 (Out-Dez): Preparação para Natal
```
