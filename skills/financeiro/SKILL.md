---
name: "gerenciando-financeiro"
description: "Gerencia receitas, despesas, contas bancárias e relatórios financeiros. Use quando trabalhar com transações, categorias financeiras ou dashboards."
---

# Quando Usar Esta Skill

Use esta skill quando:
- Criar ou editar transações financeiras (receitas/despesas)
- Trabalhar com contas bancárias e categorias
- Gerar relatórios ou dashboards financeiros
- Implementar validações de dados financeiros
- Criar visualizações de dados (gráficos, charts)

## Estrutura de Dados

### Conta Bancária
```python
class ContaBancaria(models.Model):
    organizacao = models.ForeignKey(Organizacao)
    nome = models.CharField(max_length=100)
    saldo_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    ativa = models.BooleanField(default=True)
```

### Transação Financeira
```python
class Transacao(models.Model):
    TIPO_CHOICES = [('receita', 'Receita'), ('despesa', 'Despesa')]
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField()
    categoria = models.ForeignKey(Categoria)
    conta = models.ForeignKey(ContaBancaria)
    descricao = models.TextField()
```

## Regras de Negócio

1. **Validação de Saldo**: Sempre verificar saldo antes de registrar despesa
2. **Categorias Obrigatórias**: Toda transação deve ter uma categoria
3. **Data Limite**: Não permitir transações futuras com mais de 1 ano
4. **Decimal**: Sempre usar 2 casas decimais para valores monetários

## Exemplos de Uso

### Criar receita
```python
receita = Transacao.objects.create(
    tipo='receita',
    valor=1500.00,
    data=timezone.now().date(),
    categoria=categoria_dizimos,
    conta=conta_principal,
    descricao='Dízimos do culto'
)
```

### Gerar relatório mensal
```python
def relatorio_mensal(mes, ano):
    receitas = Transacao.objects.filter(
        tipo='receita',
        data__month=mes,
        data__year=ano
    ).aggregate(total=Sum('valor'))
    
    despesas = Transacao.objects.filter(
        tipo='despesa',
        data__month=mes,
        data__year=ano
    ).aggregate(total=Sum('valor'))
    
    return {
        'receitas': receitas['total'] or 0,
        'despesas': despesas['total'] or 0,
        'saldo': (receitas['total'] or 0) - (despesas['total'] or 0)
    }
```

## Scripts Úteis

### Relatório Financeiro Mensal
```bash
# Mês atual
python skills/financeiro/scripts/relatorio_financeiro.py

# Mês específico
python skills/financeiro/scripts/relatorio_financeiro.py --mes 1 --ano 2026

# Abreviado
python skills/financeiro/scripts/relatorio_financeiro.py -m 1 -a 2026
```

Gera relatório com:
- Total de receitas e despesas
- Saldo do período
- Breakdown por categoria
- Percentuais e análise
- Alertas de déficit

## Boas Práticas

- Sempre usar `DecimalField` para valores monetários (nunca `FloatField`)
- Registrar logs de todas as transações para auditoria
- Implementar soft delete para histórico
- Validar permissões antes de criar/editar transações
- Usar transações atômicas do Django para operações múltiplas
- Gerar relatórios mensais para acompanhamento
