# Financeiro - Fase 4B (Gestao de Departamentos Premium)

Data: 11/08/2026  
Escopo: app financeiro + integracoes com eventos e configuracao

## Objetivo

Evoluir o modelo de fundos departamentais para uma gestao premium de departamentos financeiros, com operacao escalavel para igrejas grandes, sem ruptura do fluxo atual.

A fase formaliza tres pilares:
- Departamento financeiro como entidade de negocio.
- Integracao de departamentos com caixas/contas bancarias.
- Politicas operacionais e contabeis por departamento.

## Contexto e motivacao

O sistema atual ja possui base por fundo (LOCAL, EVENTOS, MISSOES, ASSISTENCIA), com ganhos relevantes de segregacao. Contudo, grandes ministerios exigem:
- criacao de departamentos adicionais pelo usuario (senhoras, jovens, kids, construcao, etc);
- operacao com multiplos caixas por departamento;
- regras diferentes de prestacao de contas por departamento;
- trilha de auditoria e governanca documental para contabilidade.

Esta fase cria a base para esse nivel de maturidade mantendo compatibilidade com as fases anteriores.

## Alinhamento com documentacao existente

Este documento estende, sem substituir, as diretrizes abaixo:
- FINANCEIRO_FUNDOS_DEPARTAMENTAIS_FASE1.md
- FINANCEIRO_FUNDOS_DEPARTAMENTAIS_FASE2.md
- FINANCEIRO_FASE3A_SELECTORS_SERVICES.md
- FINANCEIRO_FASE3B_POLITICA_CATEGORIAS.md
- FINANCEIRO_FASE3C_FLUXO_SERVICES.md
- FINANCEIRO_FASE4A_FILTRO_FUNDO_KPIS.md

Regra de continuidade:
- o comportamento atual de LOCAL/EVENTOS/MISSOES/ASSISTENCIA permanece valido;
- as novas capacidades entram de forma progressiva e com flags de configuracao.

## Principios de arquitetura

1. Compatibilidade primeiro
- Nao quebrar schema funcional existente.
- Nao remover campos legados em fase inicial.
- Introduzir adaptadores para leitura/escrita durante transicao.

2. Governanca por configuracao
- Politica financeira deve ser definida por departamento, nao por regra fixa em view.

3. Segregacao forte por escopo
- Igreja, departamento e caixa devem ser validados em toda operacao.

4. Auditoria por padrao
- Toda mudanca critica deve gerar trilha auditavel com usuario, data/hora e contexto.

## Escopo funcional da Fase 4B

### 1) Cadastro e gestao de departamentos

Capacidades:
- Criar departamento financeiro customizado por igreja.
- Inativar departamento sem perda de historico.
- Definir departamentos padrao do sistema na inicializacao:
  - Tesouraria Local
  - Eventos
  - Missoes
  - Assistencia Social
- Permitir departamentos ilimitados por igreja.

Campos minimos sugeridos:
- igreja
- codigo_interno (unico por igreja)
- nome_exibicao
- tipo_departamento (PADRAO, PERSONALIZADO)
- ativo
- ordem_exibicao
- criado_em, atualizado_em

### 2) Integracao departamento x caixa

Capacidades:
- Vincular um departamento a um ou mais caixas/contas.
- Definir caixa padrao do departamento.
- Validar que caixa e departamento pertencem a mesma igreja.

Regras:
- lancamento em departamento deve usar caixa permitida para o departamento;
- fallback de caixa padrao so quando politica permitir.

### 3) Politica operacional por departamento

Capacidades:
- Configurar comportamento sem hardcode por departamento.

Politicas minimas:
- exige_nota_fiscal (bool)
- exige_envio_contabilidade (bool)
- permite_prestacao_local_simplificada (bool)
- exige_aprovacao_para_saida (bool)
- valor_minimo_para_anexo (decimal, opcional)
- valor_minimo_para_aprovacao (decimal, opcional)

### 4) Prestacao de contas por departamento

Capacidades:
- Tela de prestacao com consolidado de entradas e saidas por departamento.
- Fechamento por periodo com bloqueio operacional (editar/excluir).
- Visao de pendencias documentais antes do fechamento.

### 5) Documentos e envio para contabilidade

Capacidades:
- Anexar comprovantes/notas por despesa.
- Status de conformidade documental por lancamento.
- Estado de envio para contabilidade quando aplicavel.

Estados sugeridos:
- pendente
- enviado
- aceito
- rejeitado

## Modelo de dados (proposta)

Observacao: nomes finais podem ajustar ao padrao de codigo do projeto.

### Entidades novas

1. DepartamentoFinanceiro
- igreja (FK)
- codigo_interno (CharField)
- nome_exibicao (CharField)
- tipo_departamento (choices)
- ativo (BooleanField)
- ordem_exibicao (IntegerField)
- created_at, updated_at

2. DepartamentoCaixa
- departamento (FK)
- conta_bancaria (FK)
- is_padrao (BooleanField)
- ativo (BooleanField)
- unique_together(departamento, conta_bancaria)

3. PoliticaDepartamentoFinanceiro
- departamento (OneToOne FK)
- exige_nota_fiscal
- exige_envio_contabilidade
- permite_prestacao_local_simplificada
- exige_aprovacao_para_saida
- valor_minimo_para_anexo
- valor_minimo_para_aprovacao

4. DocumentoFinanceiro
- igreja (FK)
- departamento (FK)
- despesa (FK, opcional)
- arquivo
- tipo_documento
- status_validacao
- enviado_contabilidade_em
- enviado_contabilidade_por

### Ajustes em entidades existentes

1. Receitas
- incluir campo departamento_financeiro (FK, opcional na transicao)
- manter fundo_departamental durante fase de compatibilidade

2. Despesas
- incluir campo departamento_financeiro (FK, opcional na transicao)
- manter fundo_departamental durante fase de compatibilidade

3. FechamentoCaixa
- permitir fechamento segmentado por departamento

## Mapeamento de compatibilidade (legado -> novo)

Durante migracao:
- LOCAL -> Departamento padrao Tesouraria Local
- EVENTOS -> Departamento padrao Eventos
- MISSOES -> Departamento padrao Missoes
- ASSISTENCIA -> Departamento padrao Assistencia Social

Regra transitoria:
- se departamento_financeiro for nulo e fundo_departamental existir, resolver automaticamente via mapeamento;
- logs devem registrar resolucao automatica para rastreabilidade.

## Regras de dominio e validacoes

1. Coerencia de escopo
- departamento, caixa, receita/despesa e igreja devem pertencer ao mesmo escopo.

2. Politicas por departamento
- se exige_nota_fiscal for true, bloquear fechamento com pendencia documental.
- se exige_envio_contabilidade for true, sinalizar pendencia ate envio.

3. Fechamento
- lancamentos fechados nao podem editar/excluir (regra ja vigente, manter e ampliar por departamento).

4. Eventos
- evento deve operar em departamento configurado para eventos.
- manter retrocompatibilidade com regras de fundo EVENTOS na transicao.

## Permissoes e seguranca

Padrao obrigatorio:
- login_required
- page_access_required("financeiro")
- validacoes adicionais de escopo por objeto

Permissoes funcionais recomendadas por departamento:
- visualizar
- lancar_entrada
- lancar_saida
- aprovar_saida
- fechar_periodo
- reabrir_periodo
- enviar_contabilidade

Observacao:
- nomes de grupos/permissoes devem seguir os padroes oficiais de documentacao de grupos.

## UX e operacao (premium)

### Menu e navegacao
- Novo item: Gestao de Departamentos (financeiro).
- Atalhos de operacao por departamento no painel financeiro.

### Tela de Gestao de Departamentos
- Lista com status, caixas vinculados e politicas.
- Acoes: criar, editar, inativar, configurar politica, vincular caixas.

### Tela de Prestacao por Departamento
- Filtros: igreja, departamento, periodo, status documental.
- KPIs: entradas, saidas, saldo, pendencias de documentos, pendencias de envio.
- Acao de fechamento com checklist de conformidade.

## Integracao com contabilidade

Objetivo:
- padronizar exportacao e envio de evidencias por departamento.

Escopo inicial:
- pacote de exportacao por periodo contendo:
  - resumo financeiro
  - lista de lancamentos
  - comprovantes anexos
  - status de conformidade

Evolucao futura:
- integracao direta com sistemas contabeis (API).

## Plano de implementacao recomendado

### Sprint 1 - Base de dados e compatibilidade
- Criar modelos DepartamentoFinanceiro, DepartamentoCaixa e PoliticaDepartamentoFinanceiro.
- Criar seed de departamentos padrao por igreja.
- Incluir FK de departamento em Receitas/Despesas (opcional na transicao).
- Criar camada de mapeamento legado (fundo -> departamento).

### Sprint 2 - Operacao e validacoes
- Adaptar forms/views/services para operar por departamento.
- Aplicar validacoes de caixa permitido por departamento.
- Aplicar politicas documentais no fluxo de despesa e fechamento.

### Sprint 3 - UX premium e prestacao
- Entregar tela de Gestao de Departamentos.
- Entregar prestacao de contas por departamento com checklist.
- Entregar painel de pendencias para contabilidade.

### Sprint 4 - endurecimento e escala
- Cobertura de testes completa.
- Otimizacoes de consulta e indices.
- telemetria operacional e alertas.

## Criterios de aceite

1. Funcionais
- Usuario cria departamento customizado e vincula caixas.
- Lancamentos respeitam departamento e caixa valido.
- Politicas por departamento afetam o comportamento sem alteracao de codigo.

2. Governanca
- Fechamento bloqueia alteracoes de lancamentos fechados.
- Pendencias documentais aparecem de forma auditavel.

3. Compatibilidade
- Fluxos legados continuam operacionais sem erro.
- Mapeamento de fundo para departamento funciona para dados antigos.

4. Performance
- Painel e listagens com filtros de departamento respondem em tempo aceitavel no escopo de igrejas grandes.

## Estrategia de testes

Testes minimos obrigatorios:
- model tests para validacoes de escopo e politicas.
- tests de migracao e backfill de compatibilidade.
- tests de view para filtros, fechamento e bloqueios.
- tests de permissao por perfil e igreja.
- tests de integracao de anexos e conformidade.

Comandos de validacao:
- manage.py check
- manage.py makemigrations --check --dry-run
- suites focadas em tests/test_financeiro.py

## Riscos e mitigacoes

1. Risco: complexidade de transicao legado
- Mitigacao: dupla leitura controlada (fundo + departamento) com feature flag.

2. Risco: regressao em fluxo de eventos
- Mitigacao: manter regras atuais de EVENTOS e ampliar cobertura de testes.

3. Risco: aumento de carga em consultas
- Mitigacao: indices compostos por igreja/departamento/data e cache de KPIs.

4. Risco: confusao de usuario na adocao
- Mitigacao: onboarding guiado, defaults inteligentes e nomenclatura padronizada.

## Metricas de sucesso

Operacao:
- reducao de erros de classificacao de lancamentos por contexto.
- reducao de retrabalho na prestacao de contas.

Governanca:
- aumento do percentual de despesas com documento valido.
- reducao de pendencias no envio para contabilidade.

Escala:
- capacidade de operar multiplos departamentos por igreja com clareza e sem perda de performance.

## Fora do escopo desta fase

- Integracao nativa com ERPs contabeis externos por API.
- Assinatura digital com certificado ICP em relatorios.
- Inteligencia preditiva de risco financeiro.

## Proximos documentos previstos

- FINANCEIRO_FASE5_WORKFLOW_APROVACAO_E_ALCADAS.md
- FINANCEIRO_FASE6_COMPLIANCE_DOCUMENTAL_E_EXPORTACAO_CONTABIL.md
- FINANCEIRO_RUNBOOK_OPERACAO_FINANCEIRO.md

## Status

Documento de arquitetura e execucao aprovado para orientar implementacao incremental premium.
