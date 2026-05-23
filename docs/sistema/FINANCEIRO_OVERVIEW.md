# Documentação do Sistema Financeiro

## Visão Geral
O sistema financeiro do Gereigreja é responsável por gerenciar as operações financeiras da igreja, incluindo receitas, despesas, transferências e fechamento de caixa. Ele foi projetado para oferecer controle financeiro robusto e relatórios detalhados para facilitar a tomada de decisões.

## Funcionalidades Principais

### 1. Gerenciamento de Contas Bancárias
- **Modelos**: `ContaBancaria`
- **Descrição**: Permite o cadastro e gerenciamento de contas bancárias associadas à igreja.

### 2. Controle de Receitas e Despesas
- **Modelos**: `Receitas`, `Despesas`
- **Descrição**: Registra entradas e saídas financeiras, categorizando-as para melhor organização.

### 3. Transferências entre Contas
- **Modelos**: `TransferenciaCaixa`
- **Descrição**: Facilita a movimentação de valores entre contas bancárias internas.

### 4. Fechamento de Caixa
- **Serviço**: `FechamentoCaixaService`
- **Descrição**: Automatiza o processo de fechamento de caixa, garantindo precisão nos saldos finais.

## Estrutura do Código

### Modelos
Os modelos estão localizados em `financeiro/models.py` e incluem:
- `ContaBancaria`
- `Receitas`
- `Despesas`
- `TransferenciaCaixa`

### Views
As views estão em `financeiro/views.py` e gerenciam as interações do usuário com o sistema financeiro.

### Serviços
Os serviços, como o `FechamentoCaixaService`, implementam a lógica de negócios e estão em `financeiro/services.py`.

### Templates
Os templates para relatórios e dashboards financeiros estão localizados em `financeiro/templates/`.

## Testes

### Onde ficam
- `tests/test_financeiro.py` (cobertura principal do módulo financeiro)
- `tests/test_integracao_escopo_secretaria_financeiro.py` (integração de escopo/permissões entre secretaria e financeiro)

### Como executar
Na raiz do projeto (`c:/Gereigreja`), execute:

```powershell
C:/Gereigreja/.venv/Scripts/python.exe manage.py test tests.test_financeiro --settings=core.settings_test -v2
```

Para rodar também os testes de integração de escopo:

```powershell
C:/Gereigreja/.venv/Scripts/python.exe manage.py test tests.test_integracao_escopo_secretaria_financeiro --settings=core.settings_test -v2
```

## Auditoria Financeira

### Objetivo
Registrar trilha de auditoria para operações críticas de movimentação financeira.

### Cobertura implementada
- `Receitas`: criação, atualização e exclusão.
- `Despesas`: criação, atualização e exclusão.
- `TransferenciaCaixa`: criação, atualização e exclusão.
- `FechamentoCaixa`: criação, atualização e exclusão.

### Modelo de log
- `financeiro.LogTransacaoFinanceira`
- Campos principais: igreja, usuário, tipo do lançamento, ação, referência do objeto, valor, detalhes, data/hora.

### Testes da auditoria
Os cenários de auditoria estão em `tests/test_financeiro.py`.

Execução:

```powershell
C:/Gereigreja/.venv/Scripts/python.exe manage.py test tests.test_financeiro --settings=core.settings_test -v2
```

## Integração Bancária OFX

### Etapa implementada
Foi entregue o primeiro slice persistente da integração bancária:
- parser OFX em `financeiro.services.OFXImportService`
- leitura de metadados da conta
- leitura do saldo final do extrato
- normalização de transações em formato interno
- classificação de lançamentos em `entrada` e `saida`
- gravação da importação no banco
- gravação dos lançamentos do extrato no banco
- proteção contra reimportação duplicada do mesmo arquivo na mesma conta

### Limite desta etapa
Nesta fase, o sistema já grava o extrato e os lançamentos no banco, mas ainda não faz conciliação automática com receitas e despesas internas.

### Modelos adicionados
- `financeiro.ImportacaoExtratoOFX`
- `financeiro.LancamentoExtratoOFX`

### Cobertura de testes
Os cenários do parser e da persistência OFX estão em `tests/test_financeiro.py`.

## Reconciliação (Sugestões)

### Etapa implementada
Foi adicionada a primeira versão de sugestões automáticas de conciliação para lançamentos OFX.

### Serviço
- `financeiro.services.OFXImportService.gerar_sugestoes_conciliacao(...)`

### Critérios usados na sugestão
- valor exato (absoluto para saídas)
- janela de data configurável (padrão: 3 dias)
- priorização por mesma conta bancária
- bônus simples por semelhança de texto (`memo` do OFX vs descrição/observação do lançamento interno)

### Resultado
Para cada lançamento importado, o serviço retorna uma lista ordenada de candidatos (receita ou despesa) com score.

## Conciliação Assistida (Confirmação)

### Etapa implementada
Foi adicionada a ação de confirmação da sugestão para consolidar a conciliação no banco.

### Serviço
- `financeiro.services.OFXImportService.confirmar_conciliacao(...)`

### O que a confirmação faz
- valida o tipo (`receita` ou `despesa`)
- garante que o lançamento OFX ainda não está conciliado
- valida que o lançamento interno pertence à mesma igreja da importação
- valida valor compatível entre OFX e lançamento interno
- marca o OFX como conciliado e registra rastreabilidade

### Rastreabilidade persistida no lançamento OFX
- `conciliado=True`
- `conciliado_tipo`
- `conciliado_referencia_id`
- `conciliado_por`
- `conciliado_em`

### Cobertura de testes
Os cenários de confirmação de conciliação e validação de divergência de valor estão em `tests/test_financeiro.py`.

## Próximos Passos
1. **Conciliação Parcial/Manual**: Permitir vínculo manual quando não houver match automático.
2. **Conferência Operacional**: Criar dashboard de divergências (lançamentos x saldo por conta).
3. **Interface de Conciliação**: Expor fluxo em tela para revisar sugestões e confirmar/desfazer conciliações.

---

Para mais detalhes, consulte os arquivos relevantes no diretório `financeiro/`.
