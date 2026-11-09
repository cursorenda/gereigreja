Pasta:
docs/apps/

Arquivo:
03-Financeiro.md

Documento:
APP-03

Família:
Apps — Documentação Funcional

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Setembro de 2026

# 03 — Financeiro

> O Financeiro é o domínio responsável por registrar, organizar, controlar e auditar movimentações financeiras da igreja, preservando segregação por escopo, rastreabilidade e coerência entre receitas, despesas, contas, fundos e fechamentos.

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Conceitos Centrais
5. Contas Bancárias
6. Receitas
7. Despesas
8. Transferências
9. Fechamento de Caixa
10. Fundos Departamentais
11. Política de Categorias por Fundo
12. Dashboard e KPIs
13. Conciliação Bancária OFX
14. Departamentos Financeiros
15. Permissões e Escopo
16. Multi-Tenancy
17. Auditoria Financeira
18. Integrações
19. Segurança e Privacidade
20. Testes e Qualidade
21. Compatibilidade e Migração
22. Evolução e Itens Planejados
23. Documentos Relacionados
24. Princípios Finais
25. Status

---

# 1. Objetivo

Este documento consolida a visão funcional canônica do módulo Financeiro do GereIgreja.

Seu objetivo é registrar:

- quais capacidades financeiras pertencem ao domínio;
- como receitas, despesas, contas, transferências e fechamentos se relacionam;
- como fundos e departamentos segregam contexto;
- quais regras funcionais já estão documentadas como implementadas;
- quais capacidades ainda pertencem a planos de evolução;
- como auditoria, permissões e multi-tenancy devem influenciar a operação.

Este documento não substitui documentação de Models, Services, Selectors, Views, Forms, API, Segurança, Infraestrutura ou Qualidade.

---

# 2. Escopo

O domínio Financeiro cobre, conforme a documentação existente:

- contas bancárias;
- receitas;
- despesas;
- transferências entre caixas/contas;
- fechamento de caixa;
- fundos departamentais;
- categorias financeiras;
- dashboards e KPIs;
- filtros por fundo;
- auditoria financeira;
- importação de extrato OFX;
- sugestões e confirmação assistida de conciliação;
- evolução para departamentos financeiros;
- prestação de contas;
- documentos financeiros e integração com contabilidade.

Nem todos os itens de evolução departamental estão necessariamente implementados em produção.

---

# 3. Papel deste Documento

Este é o documento funcional canônico do Financeiro em `docs/apps/`.

A relação esperada é:

```text
docs/apps/03-Financeiro.md
        ↓
Visão funcional do domínio
        ↓
docs/backend/
docs/seguranca/
docs/qualidade/
docs/sistema/
docs/relatorios/
docs/release-notes/
        ↓
Detalhes técnicos, operacionais e históricos
```

Documentos de fase continuam relevantes como evidência de evolução, mas este arquivo deve concentrar o comportamento funcional permanente.

---

# 4. Conceitos Centrais

O Financeiro trabalha com quatro eixos principais:

```text
Igreja
  ↓
Conta / Caixa
  ↓
Receita / Despesa / Transferência
  ↓
Fundo / Departamento / Categoria
  ↓
Auditoria / Fechamento / Relatórios
```

Toda operação deve manter coerência entre esses eixos.

Uma movimentação financeira não deve ser considerada válida apenas porque possui valor e data.

Ela também deve pertencer ao escopo correto de:

- igreja;
- conta;
- fundo ou departamento;
- categoria;
- usuário autorizado;
- período operacional.

---

# 5. Contas Bancárias

O sistema documenta `ContaBancaria` como a entidade responsável por representar contas associadas à igreja.

Funcionalmente, a conta bancária serve como referência para:

- entradas;
- saídas;
- transferências;
- fechamento;
- integração OFX;
- conciliação;
- eventualmente, vínculo com departamento financeiro.

Contas devem permanecer vinculadas ao tenant correto.

---

# 6. Receitas

Receitas representam entradas financeiras.

A documentação existente registra:

- classificação por categoria;
- vínculo com igreja;
- vínculo opcional com fundo departamental;
- integração com eventos;
- inclusão em KPIs;
- auditoria de criação, atualização e exclusão.

Quando o fundo estiver presente, a categoria deve respeitar a política correspondente.

---

# 7. Despesas

Despesas representam saídas financeiras.

A documentação existente registra:

- vínculo com igreja;
- vínculo opcional com fundo;
- participação em fechamentos;
- auditoria;
- evolução futura para documentação comprobatória, aprovação e prestação por departamento.

Despesas não devem atravessar escopo de igreja ou caixa.

Quando políticas documentais forem ativadas no futuro, a despesa poderá depender de comprovantes e validações antes do fechamento.

---

# 8. Transferências

`TransferenciaCaixa` representa movimentação entre contas/caixas internos.

O domínio deve garantir:

- origem válida;
- destino válido;
- coerência de igreja;
- rastreabilidade;
- efeito correto nos saldos;
- auditoria.

Transferências não devem ser tratadas como receita externa nem como despesa definitiva do tenant.

---

# 9. Fechamento de Caixa

O sistema documenta `FechamentoCaixaService` como responsável pela lógica de fechamento.

Funcionalmente, o fechamento consolida um período e protege sua integridade.

A documentação mais recente também trata como regra vigente que lançamentos fechados não devem ser livremente editados ou excluídos.

A evolução por departamento propõe ampliar esse princípio para fechamentos segmentados.

---

# 10. Fundos Departamentais

A Fase 1 introduziu o conceito de `FundoDepartamental` por igreja.

Os códigos documentados são:

- `LOCAL`;
- `EVENTOS`;
- `MISSOES`;
- `ASSISTENCIA`.

O objetivo funcional foi separar movimentações por contexto sem quebrar o fluxo existente.

A documentação registra:

```text
lançamento com evento
→ fundo EVENTOS

lançamento sem evento
→ fundo LOCAL
```

Também registra backfill para dados antigos e validação de que o fundo deve pertencer à mesma igreja do lançamento.

---

# 11. Política de Categorias por Fundo

A documentação consolidou política central de categorias para receitas.

Regras documentadas:

| Fundo | Categorias permitidas | Padrão |
|---|---|---|
| LOCAL | `dizimo`, `oferta`, `voto`, `campanha`, `outro` | `oferta` |
| EVENTOS | `doacao` | `doacao` |
| MISSOES | `oferta`, `campanha`, `outro` | `oferta` |
| ASSISTENCIA | `doacao`, `campanha`, `outro` | `doacao` |

Essa política foi centralizada para evitar divergência entre domínio, Forms, Selectors e Views.

A documentação funcional deve considerar essas combinações como regra consolidada enquanto não houver documento posterior que formalmente as substitua.

---

# 12. Dashboard e KPIs

A Fase 4A documenta como implementados:

- filtro por fundo no painel;
- filtro por fundo em receitas;
- filtro por fundo em despesas;
- validação do fundo selecionado;
- KPIs resumidos por fundo;
- chip indicando o escopo ativo.

Os fundos exibidos nos KPIs são:

- LOCAL;
- EVENTOS;
- MISSOES;
- ASSISTENCIA.

O princípio funcional é que a leitura financeira deve deixar claro o escopo em uso.

---

# 13. Conciliação Bancária OFX

A documentação `FINANCEIRO_OVERVIEW.md` registra uma integração bancária OFX já implementada em etapas.

## 13.1 Importação

Capacidades documentadas:

- leitura de metadados da conta;
- leitura de saldo final;
- normalização de transações;
- classificação em entrada e saída;
- persistência de importação;
- persistência de lançamentos;
- proteção contra reimportação duplicada do mesmo arquivo na mesma conta.

## 13.2 Sugestões de conciliação

Critérios documentados:

- valor exato;
- janela de data configurável;
- priorização por mesma conta bancária;
- semelhança simples de texto.

## 13.3 Confirmação assistida

A confirmação documentada deve:

- validar tipo;
- impedir reconciliação duplicada;
- validar mesma igreja;
- validar compatibilidade de valor;
- registrar rastreabilidade.

Campos de rastreabilidade documentados incluem:

- `conciliado`;
- `conciliado_tipo`;
- `conciliado_referencia_id`;
- `conciliado_por`;
- `conciliado_em`.

A documentação também registra como próximos passos a conciliação manual/parcial, dashboard de divergências e interface operacional de conciliação.

Portanto, esses próximos passos não devem ser tratados como concluídos sem validação.

---

# 14. Departamentos Financeiros

A Fase 4B descreve uma evolução do modelo de fundos para gestão financeira por departamentos.

Esse material deve ser interpretado com cuidado: o próprio documento apresenta um **plano de implementação recomendado**, portanto nem toda capacidade descrita deve ser considerada vigente.

Conceitos propostos:

- departamento financeiro como entidade de negócio;
- vínculo departamento × caixa;
- políticas operacionais por departamento;
- prestação de contas;
- documentação financeira;
- envio para contabilidade;
- fechamento segmentado.

Também propõe compatibilidade com os fundos legados:

```text
LOCAL       → Tesouraria Local
EVENTOS     → Eventos
MISSOES     → Missoes
ASSISTENCIA → Assistencia Social
```

Esse mapeamento deve ser validado no código atual antes de ser tratado como arquitetura final de produção.

---

# 15. Permissões e Escopo

O Financeiro é domínio sensível e deve possuir autorização explícita.

A documentação de evolução registra como padrão:

- autenticação obrigatória;
- controle de acesso à página Financeiro;
- validação adicional por objeto;
- segregação por igreja;
- segregação por fundo ou departamento quando aplicável.

Permissões funcionais propostas para departamentos incluem:

- visualizar;
- lançar entrada;
- lançar saída;
- aprovar saída;
- fechar período;
- reabrir período;
- enviar para contabilidade.

Como essas permissões aparecem em plano de evolução, sua implementação atual deve ser verificada antes de serem tratadas como concedidas pelo sistema.

---

# 16. Multi-Tenancy

Toda movimentação deve pertencer à igreja correta.

Devem ser coerentes entre si:

```text
igreja
+
conta
+
receita/despesa
+
fundo/departamento
+
evento, quando houver
```

A documentação de fundos e conciliação explicita validações de mesma igreja.

Nenhum filtro, importação, conciliação ou relatório deve permitir atravessar tenants.

---

# 17. Auditoria Financeira

A documentação registra `LogTransacaoFinanceira` como mecanismo de auditoria de operações críticas.

Cobertura documentada:

- Receitas: criação, atualização e exclusão;
- Despesas: criação, atualização e exclusão;
- TransferenciaCaixa: criação, atualização e exclusão;
- FechamentoCaixa: criação, atualização e exclusão.

Campos principais documentados:

- igreja;
- usuário;
- tipo do lançamento;
- ação;
- referência do objeto;
- valor;
- detalhes;
- data/hora.

Auditoria financeira deve preservar rastreabilidade sem expor informações além do necessário.

---

# 18. Integrações

## Eventos

Há relação direta com o fundo `EVENTOS`.

A documentação de fundos registra que lançamentos associados a evento foram migrados para esse fundo.

A evolução departamental também prevê manter retrocompatibilidade com esse comportamento.

## Departamentos

A documentação mais recente propõe integração entre departamentos organizacionais e Financeiro, mas enfatiza uma separação importante:

```text
vínculo em departamento
≠
autorização financeira
```

Cargo, participação em equipe ou vínculo ministerial não devem conceder acesso financeiro automaticamente.

## Secretaria

Existem testes de integração de escopo entre Secretaria e Financeiro.

O acesso à Secretaria não deve ampliar permissões financeiras.

## Contabilidade

A evolução por departamento propõe pacote de exportação contendo:

- resumo financeiro;
- lançamentos;
- comprovantes;
- status de conformidade.

Integração nativa via API com sistemas contábeis é descrita como evolução futura.

---

# 19. Segurança e Privacidade

Dados financeiros são confidenciais.

O módulo deve seguir:

- GSF;
- Segurança de Dados e Privacidade;
- Conformidade e LGPD;
- menor privilégio;
- auditoria;
- isolamento multi-tenant.

Cuidados obrigatórios:

- não expor valores a perfis sem autorização;
- validar tenant em todos os objetos;
- proteger exports;
- proteger arquivos financeiros;
- limitar logs ao necessário;
- preservar trilha de auditoria;
- impedir alterações indevidas após fechamento.

---

# 20. Testes e Qualidade

A documentação registra cobertura principal em:

- `tests/test_financeiro.py`;
- `tests/test_integracao_escopo_secretaria_financeiro.py`.

Também registra testes para:

- auditoria;
- filtro por fundo;
- OFX;
- persistência;
- sugestões de conciliação;
- confirmação;
- divergência de valor.

Na evolução por departamentos, são indicados testes adicionais para:

- escopo;
- políticas;
- migração;
- backfill;
- fechamento;
- permissões;
- anexos;
- conformidade.

Testes pertencem ao processo geral do GQF e `docs/qualidade/`.

---

# 21. Compatibilidade e Migração

Uma característica recorrente da evolução financeira é preservação de compatibilidade.

A documentação das fases enfatiza:

- campos novos opcionais;
- backfill;
- ausência de ruptura imediata de telas e rotas;
- manutenção de comportamento legado;
- dupla leitura durante transição;
- adaptadores;
- feature flags quando necessário.

Esse princípio deve ser preservado em futuras migrações.

Mudanças estruturais não devem invalidar lançamentos históricos ou quebrar relatórios anteriores sem plano explícito de migração.

---

# 22. Evolução e Itens Planejados

Itens encontrados como planos ou próximos passos, e não necessariamente como implementação atual:

- conciliação parcial/manual;
- dashboard de divergências bancárias;
- interface completa de conciliação;
- departamentos financeiros completos;
- múltiplos caixas por departamento;
- políticas documentais por departamento;
- aprovação de saídas;
- prestação de contas segmentada;
- anexos de comprovantes;
- envio para contabilidade;
- workflow de alçadas;
- integração nativa com ERP contábil;
- inteligência preditiva de risco.

Esses itens não devem ser promovidos a funcionalidade vigente sem confirmação no código e ambiente atual.

---

# 23. Documentos Relacionados

## Canônicos

- `docs/apps/README.md`
- `docs/apps/02-Secretaria.md`
- `docs/apps/05-Departamentos.md`

## Financeiro — fontes existentes

- `docs/sistema/FINANCEIRO_OVERVIEW.md`
- `docs/sistema/FINANCEIRO_FUNDOS_DEPARTAMENTAIS_FASE1.md`
- `docs/sistema/FINANCEIRO_FUNDOS_DEPARTAMENTAIS_FASE2.md`
- `docs/sistema/FINANCEIRO_FASE3A_SELECTORS_SERVICES.md`
- `docs/sistema/FINANCEIRO_FASE3B_POLITICA_CATEGORIAS.md`
- `docs/sistema/FINANCEIRO_FASE3C_FLUXO_SERVICES.md`
- `docs/sistema/FINANCEIRO_FASE4A_FILTRO_FUNDO_KPIS.md`
- `docs/sistema/FINANCEIRO_FASE4B_GESTAO_DEPARTAMENTOS_PREMIUM.md`

## Engenharia e segurança

- `docs/backend/README.md`
- `docs/seguranca/08-Seguranca-de-Dados-e-Privacidade.md`
- `docs/seguranca/14-Conformidade-e-LGPD.md`
- `docs/qualidade/README.md`

---

# 24. Princípios Finais

O Financeiro deve manter coerência entre:

```text
igreja
+
conta
+
movimentação
+
categoria
+
fundo/departamento
+
permissão
+
período
+
auditoria
```

Nenhuma dessas dimensões deve ser ignorada em uma operação crítica.

A documentação funcional deve explicar **o que o Financeiro faz e quais regras permanentes governam o domínio**.

A documentação técnica deve explicar **como essas regras são implementadas**.

---

# 25. Status

**Pasta:** `docs/apps/`

**Arquivo:** `03-Financeiro.md`

**Documento:** `APP-03`

**Versão:** `1.0`

**Status:** **OFICIAL**

Este documento consolida uma documentação anteriormente fragmentada entre overview, fases de fundos, políticas, services, KPIs e evolução departamental.

Capacidades descritas em documentos de planejamento devem ser validadas no código atual antes de serem consideradas vigentes.
