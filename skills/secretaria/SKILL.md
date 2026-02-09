---
name: "gerenciando-secretaria"
description: "Gerencia cadastro de pessoas, famílias e histórico de membros. Use para cadastro, edição de pessoas ou relatórios de secretaria."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Cadastrar ou editar pessoas (membros/visitantes)
- Gerenciar famílias e relacionamentos
- Controlar status de membros (ativo, inativo, visitante)
- Gerar relatórios de secretaria
- Registrar histórico de mudanças

## Estrutura de Dados

### Pessoa (Membro/Visitante)
```python
class Pessoa(models.Model):
    STATUS_CHOICES = [
        ('ativo', 'Membro Ativo'),
        ('inativo', 'Membro Inativo'),
        ('visitante', 'Visitante'),
        ('congregado', 'Congregado')
    ]
    
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    familia = models.ForeignKey(Familia, null=True)
    organizacao = models.ForeignKey(Organizacao)
    data_cadastro = models.DateTimeField(auto_now_add=True)
```

### Família
```python
class Familia(models.Model):
    nome = models.CharField(max_length=200)  # Ex: "Família Silva"
    responsavel = models.ForeignKey(Pessoa, related_name='familia_responsavel')
    endereco = models.CharField(max_length=300)
    organizacao = models.ForeignKey(Organizacao)
```

### Histórico de Status
```python
class HistoricoStatus(models.Model):
    pessoa = models.ForeignKey(Pessoa)
    status_anterior = models.CharField(max_length=20)
    status_novo = models.CharField(max_length=20)
    data_mudanca = models.DateTimeField(auto_now_add=True)
    motivo = models.TextField()
    usuario = models.ForeignKey(User)
```

## Regras de Negócio

1. **CPF Único**: Validar e não permitir duplicados
2. **Idade Mínima**: Crianças devem ter responsável
3. **Status**: Registrar histórico de todas as mudanças
4. **Família**: Responsável deve ser membro ativo
5. **LGPD**: Consentimento para uso de dados pessoais

## Exemplos de Uso

### Cadastrar Pessoa
```python
pessoa = Pessoa.objects.create(
    nome='João Silva',
    cpf='123.456.789-00',
    data_nascimento='1990-05-15',
    telefone='(11) 98765-4321',
    email='joao@email.com',
    status='visitante',
    organizacao=organizacao
)
```

### Criar Família
```python
familia = Familia.objects.create(
    nome='Família Silva',
    responsavel=joao_silva,
    endereco='Rua das Flores, 123',
    organizacao=organizacao
)

# Adicionar membros à família
maria = Pessoa.objects.get(nome='Maria Silva')
maria.familia = familia
maria.save()
```

### Mudar Status (com histórico)
```python
def mudar_status(pessoa_id, novo_status, motivo, usuario):
    pessoa = Pessoa.objects.get(id=pessoa_id)
    status_anterior = pessoa.status
    
    # Registrar histórico
    HistoricoStatus.objects.create(
        pessoa=pessoa,
        status_anterior=status_anterior,
        status_novo=novo_status,
        motivo=motivo,
        usuario=usuario
    )
    
    # Atualizar status
    pessoa.status = novo_status
    pessoa.save()
```

### Relatório de Membros Ativos
```python
def relatorio_membros_ativos():
    membros = Pessoa.objects.filter(status='ativo')
    
    return {
        'total': membros.count(),
        'homens': membros.filter(sexo='M').count(),
        'mulheres': membros.filter(sexo='F').count(),
        'faixa_etaria': {
            'criancas': membros.filter(data_nascimento__gte=date.today() - timedelta(days=365*12)).count(),
            'jovens': membros.filter(data_nascimento__range=[date.today() - timedelta(days=365*30), date.today() - timedelta(days=365*12)]).count(),
            'adultos': membros.filter(data_nascimento__lt=date.today() - timedelta(days=365*30)).count()
        }
    }
```

## Validações Importantes

### Validar CPF
```python
def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    if len(cpf) != 11:
        return False
    
    # Algoritmo de validação do CPF
    # ... (implementar)
    return True
```

### Validar Idade
```python
def calcular_idade(data_nascimento):
    hoje = date.today()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))
```

## Scripts Úteis

### Relatório de Membros
```bash
# Exibir no terminal
python skills/secretaria/scripts/relatorio_membros.py

# Gerar CSV
python skills/secretaria/scripts/relatorio_membros.py csv

# Gerar JSON
python skills/secretaria/scripts/relatorio_membros.py json
```

Gera estatísticas:
- Total de membros (ativos/inativos)
- Distribuição por sexo
- Distribuição por faixa etária
- Percentuais e totais

### Lista de Aniversariantes
```bash
# Mês atual
python skills/secretaria/scripts/aniversariantes.py

# Mês específico (ex: fevereiro)
python skills/secretaria/scripts/aniversariantes.py --mes 2

# Com mensagem para WhatsApp
python skills/secretaria/scripts/aniversariantes.py --whatsapp
```

Gera listagem com:
- Aniversariantes agrupados por dia
- Idade que farão
- Telefone de contato
- Mensagem formatada para WhatsApp

## Boas Práticas

1. **Sempre validar CPF** antes de salvar
2. **Registrar histórico** de todas as mudanças de status
3. **Soft delete** - marcar como inativo ao invés de deletar
4. **Permissões** - apenas secretaria pode editar dados sensíveis
5. **LGPD** - permitir exportação e exclusão de dados pessoais
6. **Busca eficiente** - indexar campos de busca (nome, CPF)
7. **Fotos** - armazenar no Cloudinary, não no banco
8. **Relatórios regulares** - gerar relatórios mensalmente para análise
