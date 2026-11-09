Pasta:

docs/infraestrutura/

Arquivo:

16-Governanca-Padroes-e-Evolucao-da-Infraestrutura.md

Documento:

GINF-16

Código:

GINF-GOVERNANCE-STANDARDS-EVOLUTION

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GQF --- GereIgreja
Quality Framework GDF --- GereIgreja Documentation Framework GINF ---
GereIgreja Infrastructure Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-16 --- Governança, Padrões e Evolução da Infraestrutura

> "A infraestrutura evolui com segurança quando decisões, padrões,
> exceções e responsabilidades permanecem explícitos."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura
4.  Princípios Fundamentais
5.  Governança de Infraestrutura
6.  Objetivos da Governança
7.  Autoridade Técnica
8.  Ownership
9.  Responsabilidades
10. Catálogo de Padrões
11. Padrões Obrigatórios
12. Padrões Recomendados
13. Convenções
14. Exceções
15. Processo de Exceção
16. Prazo de Exceções
17. Technical Debt
18. Registro de Decisões
19. ADRs
20. RFCs
21. Revisão Arquitetural
22. Critérios de Revisão
23. Segurança
24. Disponibilidade
25. Escalabilidade
26. Recuperabilidade
27. Observabilidade
28. Operabilidade
29. Custos
30. Simplicidade
31. Portabilidade
32. Compliance
33. Ciclo de Vida de Tecnologias
34. Adoção de Tecnologia
35. Experimentação
36. Aprovação
37. Padronização
38. Depreciação
39. End of Life
40. Migração
41. Providers
42. Serviços Gerenciados
43. Open Source
44. Dependências
45. Versões
46. Upgrade Policy
47. Infraestrutura como Código
48. Configuração
49. Secrets
50. Naming
51. Tags e Labels
52. Ambientes
53. Produção
54. Acesso Administrativo
55. Mudanças
56. Deploy
57. Operação
58. Runbooks
59. Incidentes
60. Disaster Recovery
61. Backup
62. Observabilidade
63. Capacidade
64. FinOps
65. Inventário
66. CMDB e Catálogo
67. Recursos Órfãos
68. Ownership Review
69. Documentação
70. Documentos Normativos
71. Documentos Operacionais
72. Atualização Documental
73. Auditoria de Conformidade
74. Evidências
75. Métricas de Governança
76. Indicadores
77. Riscos
78. Risk Register
79. Aceitação de Risco
80. Revisões Periódicas
81. Revisão Trimestral
82. Revisão Semestral
83. Revisão Anual
84. Roadmap de Infraestrutura
85. Priorização
86. Evolução Incremental
87. Modernização
88. Migrações Grandes
89. Legado
90. Automação
91. Golden Paths
92. Templates
93. Self-Service
94. Guardrails
95. Policy as Code
96. Segurança por Padrão
97. Confiabilidade por Padrão
98. Custo por Padrão
99. Gestão do Conhecimento
100. Treinamento
101. Onboarding
102. Bus Factor
103. Continuidade da Equipe
104. Fornecedores
105. Lock-in
106. Exit Strategy
107. Anti-Padrões
108. Modelo de Governança de Referência
109. Checklist
110. Documentos Relacionados
111. Princípios Finais
112. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial de governança, padronização e
evolução da infraestrutura do GereIgreja.

Seu objetivo é garantir que decisões de infraestrutura sejam:

-   consistentes;
-   documentadas;
-   revisáveis;
-   seguras;
-   sustentáveis;
-   alinhadas à arquitetura;
-   evolutivas sem perda de controle.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a:

-   tecnologias de infraestrutura;
-   provedores;
-   serviços gerenciados;
-   rede;
-   compute;
-   containers;
-   dados;
-   storage;
-   observabilidade;
-   automação;
-   operação;
-   segurança;
-   custos;
-   decisões arquiteturais.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura

``` text
GEA / GSF / GQF
       │
       ▼
Governança GINF
       │
 ┌─────┼─────┐
 ▼     ▼     ▼
Padrões Decisões Exceções
 │      │       │
 └──────┼───────┘
        ▼
Infraestrutura
        │
        ▼
Operação
        │
        ▼
Métricas / Incidentes / Custos
        │
        ▼
Evolução
```

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Aplicar:

-   padrões explícitos;
-   ownership;
-   decisões registradas;
-   exceções temporárias;
-   simplicidade;
-   automação;
-   segurança por padrão;
-   revisão periódica;
-   evolução incremental.

------------------------------------------------------------------------

# 5. Governança de Infraestrutura

Governança define como decisões são tomadas e mantidas ao longo do
tempo.

Ela não deverá transformar Engenharia em processo burocrático
desnecessário.

------------------------------------------------------------------------

# 6. Objetivos da Governança

A governança deverá reduzir:

-   divergência tecnológica;
-   configuração insegura;
-   dependência de indivíduos;
-   custos invisíveis;
-   infraestrutura órfã;
-   decisões incompatíveis.

------------------------------------------------------------------------

# 7. Autoridade Técnica

Decisões estruturais deverão possuir responsável técnico claramente
identificado.

------------------------------------------------------------------------

# 8. Ownership

Cada componente relevante deverá possuir owner.

------------------------------------------------------------------------

# 9. Responsabilidades

Owners deverão acompanhar:

-   saúde;
-   evolução;
-   documentação;
-   custos;
-   riscos;
-   lifecycle.

------------------------------------------------------------------------

# 10. Catálogo de Padrões

A família GINF constitui o catálogo normativo de infraestrutura do
GereIgreja.

------------------------------------------------------------------------

# 11. Padrões Obrigatórios

Regras que protegem segurança, integridade, operação ou arquitetura
deverão ser obrigatórias.

------------------------------------------------------------------------

# 12. Padrões Recomendados

Algumas práticas poderão ser recomendadas enquanto a plataforma
amadurece.

A documentação deverá diferenciar recomendação de obrigação.

------------------------------------------------------------------------

# 13. Convenções

Convenções reduzem decisões repetitivas.

Exemplos:

-   naming;
-   tags;
-   organização de IaC;
-   ambientes;
-   logs.

------------------------------------------------------------------------

# 14. Exceções

Exceções poderão existir quando houver justificativa técnica real.

------------------------------------------------------------------------

# 15. Processo de Exceção

Toda exceção relevante deverá registrar:

``` text
padrão violado
motivo
risco
owner
mitigação
prazo
plano de regularização
```

------------------------------------------------------------------------

# 16. Prazo de Exceções

Exceção sem prazo tende a se tornar padrão informal.

Deverá possuir data de revisão.

------------------------------------------------------------------------

# 17. Technical Debt

Dívida de infraestrutura deverá ser registrada e priorizada conforme
risco e impacto.

------------------------------------------------------------------------

# 18. Registro de Decisões

Decisões relevantes deverão ser preservadas.

------------------------------------------------------------------------

# 19. ADRs

Architecture Decision Records deverão ser utilizados para decisões
arquiteturais significativas quando apropriado.

------------------------------------------------------------------------

# 20. RFCs

Mudanças amplas poderão utilizar RFC para discussão antes da
implementação.

------------------------------------------------------------------------

# 21. Revisão Arquitetural

Mudanças estruturais deverão ser avaliadas antes de production.

------------------------------------------------------------------------

# 22. Critérios de Revisão

Avaliar:

``` text
segurança
disponibilidade
escalabilidade
recuperação
observabilidade
operação
custos
complexidade
```

------------------------------------------------------------------------

# 23. Segurança

Aplicar GSF.

Nenhuma decisão de custo ou conveniência deverá enfraquecer controles
essenciais sem aceitação formal de risco.

------------------------------------------------------------------------

# 24. Disponibilidade

Requisitos deverão orientar redundância.

------------------------------------------------------------------------

# 25. Escalabilidade

Aplicar GINF-13.

Não introduzir arquitetura distribuída sem necessidade.

------------------------------------------------------------------------

# 26. Recuperabilidade

Aplicar GINF-11.

Todo componente crítico deverá possuir estratégia de recuperação.

------------------------------------------------------------------------

# 27. Observabilidade

Aplicar GINF-10.

Novo componente deverá possuir sinais operacionais adequados.

------------------------------------------------------------------------

# 28. Operabilidade

Aplicar GINF-15.

Uma tecnologia difícil de operar possui custo arquitetural.

------------------------------------------------------------------------

# 29. Custos

Aplicar GINF-14.

Custo deverá fazer parte das decisões.

------------------------------------------------------------------------

# 30. Simplicidade

Entre duas soluções que atendem aos requisitos, preferir a mais simples
de compreender e operar.

------------------------------------------------------------------------

# 31. Portabilidade

Portabilidade deverá ser avaliada proporcionalmente ao risco de lock-in.

Não é necessário abstrair todo serviço de provedor.

------------------------------------------------------------------------

# 32. Compliance

Decisões deverão respeitar requisitos legais e normativos aplicáveis.

------------------------------------------------------------------------

# 33. Ciclo de Vida de Tecnologias

Tecnologias deverão possuir lifecycle conhecido.

------------------------------------------------------------------------

# 34. Adoção de Tecnologia

Nova tecnologia deverá resolver problema concreto.

------------------------------------------------------------------------

# 35. Experimentação

Experimentos poderão ocorrer em ambiente controlado.

Não transformar prova de conceito diretamente em padrão de production.

------------------------------------------------------------------------

# 36. Aprovação

Adoções estruturais deverão ser aprovadas conforme impacto.

------------------------------------------------------------------------

# 37. Padronização

Tecnologia aprovada deverá possuir:

-   owner;
-   versão;
-   documentação;
-   padrão de configuração;
-   observabilidade;
-   segurança;
-   operação.

------------------------------------------------------------------------

# 38. Depreciação

Tecnologia substituída deverá ser formalmente marcada como deprecated.

------------------------------------------------------------------------

# 39. End of Life

Versões sem suporte deverão possuir plano de saída.

------------------------------------------------------------------------

# 40. Migração

Migração deverá possuir:

-   escopo;
-   etapas;
-   risco;
-   validação;
-   rollback;
-   prazo.

------------------------------------------------------------------------

# 41. Providers

Providers de infraestrutura deverão possuir versões controladas.

------------------------------------------------------------------------

# 42. Serviços Gerenciados

Avaliar:

-   confiabilidade;
-   custo;
-   suporte;
-   lock-in;
-   segurança;
-   operação.

------------------------------------------------------------------------

# 43. Open Source

Uso de open source deverá considerar:

-   manutenção;
-   comunidade;
-   segurança;
-   licença;
-   maturidade.

------------------------------------------------------------------------

# 44. Dependências

Reduzir dependências desnecessárias.

Cada componente adicional aumenta superfície operacional.

------------------------------------------------------------------------

# 45. Versões

Versões relevantes deverão ser explícitas e rastreáveis.

------------------------------------------------------------------------

# 46. Upgrade Policy

Upgrades deverão ocorrer antes de versões entrarem em estado crítico de
obsolescência.

------------------------------------------------------------------------

# 47. Infraestrutura como Código

Aplicar GINF-12.

IaC deverá ser caminho preferencial para recursos gerenciáveis.

------------------------------------------------------------------------

# 48. Configuração

Aplicar GINF-02.

Configuração deverá ser separada de código e secrets conforme
responsabilidade.

------------------------------------------------------------------------

# 49. Secrets

Aplicar GSF-09.

------------------------------------------------------------------------

# 50. Naming

Convenções de nomes deverão ser previsíveis e documentadas.

------------------------------------------------------------------------

# 51. Tags e Labels

Aplicar metadados mínimos para:

-   ambiente;
-   owner;
-   serviço;
-   gestão;
-   custo.

------------------------------------------------------------------------

# 52. Ambientes

Ambientes deverão permanecer isolados.

------------------------------------------------------------------------

# 53. Produção

Production deverá possuir governança superior aos ambientes não
produtivos.

------------------------------------------------------------------------

# 54. Acesso Administrativo

Acesso deverá seguir menor privilégio e possuir revisão periódica.

------------------------------------------------------------------------

# 55. Mudanças

Mudanças deverão seguir GINF-15 e GINF-12 conforme natureza.

------------------------------------------------------------------------

# 56. Deploy

Aplicar GINF-09.

------------------------------------------------------------------------

# 57. Operação

Operação deverá ser baseada em processos conhecidos.

------------------------------------------------------------------------

# 58. Runbooks

Runbooks críticos deverão possuir owner e revisão.

------------------------------------------------------------------------

# 59. Incidentes

Incidentes deverão retroalimentar governança.

Falha recorrente pode indicar padrão inadequado.

------------------------------------------------------------------------

# 60. Disaster Recovery

Resultados de exercícios de DR deverão gerar melhorias.

------------------------------------------------------------------------

# 61. Backup

Políticas deverão ser revisadas quando criticidade ou volume mudarem.

------------------------------------------------------------------------

# 62. Observabilidade

Dashboards e alertas deverão evoluir com arquitetura.

------------------------------------------------------------------------

# 63. Capacidade

Revisões deverão antecipar gargalos relevantes.

------------------------------------------------------------------------

# 64. FinOps

Custos deverão participar do roadmap de infraestrutura.

------------------------------------------------------------------------

# 65. Inventário

Todo componente de produção deverá ser identificável.

------------------------------------------------------------------------

# 66. CMDB e Catálogo

A plataforma poderá evoluir para catálogo formal de serviços e recursos
conforme complexidade justificar.

Não criar CMDB burocrática antes da necessidade.

------------------------------------------------------------------------

# 67. Recursos Órfãos

Recursos sem owner deverão ser investigados.

------------------------------------------------------------------------

# 68. Ownership Review

Revisar owners periodicamente, especialmente após mudanças de equipe.

------------------------------------------------------------------------

# 69. Documentação

Aplicar GDF.

Documentação deverá acompanhar mudanças estruturais.

------------------------------------------------------------------------

# 70. Documentos Normativos

Definem:

``` text
o que deve ser feito
```

Exemplo:

GINF.

------------------------------------------------------------------------

# 71. Documentos Operacionais

Definem:

``` text
como executar
```

Exemplo:

runbooks.

------------------------------------------------------------------------

# 72. Atualização Documental

Mudança que torna documentação incorreta não está completamente
concluída.

------------------------------------------------------------------------

# 73. Auditoria de Conformidade

Revisões poderão verificar aderência aos padrões.

------------------------------------------------------------------------

# 74. Evidências

Utilizar evidências automatizadas sempre que possível:

-   pipeline;
-   IaC;
-   logs;
-   scans;
-   dashboards.

------------------------------------------------------------------------

# 75. Métricas de Governança

A governança poderá acompanhar indicadores para avaliar eficácia.

------------------------------------------------------------------------

# 76. Indicadores

Exemplos:

-   percentual de recursos sob IaC;
-   recursos sem owner;
-   versões EOL;
-   exceções abertas;
-   falhas recorrentes;
-   cobertura de backup;
-   cobertura de observabilidade.

------------------------------------------------------------------------

# 77. Riscos

Riscos relevantes deverão ser explícitos.

------------------------------------------------------------------------

# 78. Risk Register

A Engenharia poderá manter registro de riscos de infraestrutura.

------------------------------------------------------------------------

# 79. Aceitação de Risco

Risco aceito deverá possuir:

-   responsável;
-   justificativa;
-   impacto;
-   validade;
-   revisão.

------------------------------------------------------------------------

# 80. Revisões Periódicas

Governança deverá possuir ciclos de revisão.

------------------------------------------------------------------------

# 81. Revisão Trimestral

Pode avaliar:

-   riscos;
-   custos;
-   capacidade;
-   exceções;
-   EOL;
-   incidentes.

------------------------------------------------------------------------

# 82. Revisão Semestral

Pode avaliar:

-   arquitetura;
-   providers;
-   automação;
-   DR;
-   padrões.

------------------------------------------------------------------------

# 83. Revisão Anual

Pode revisar o framework GINF como um todo.

Frequências poderão ser ajustadas conforme maturidade.

------------------------------------------------------------------------

# 84. Roadmap de Infraestrutura

Evoluções deverão compor roadmap priorizado.

------------------------------------------------------------------------

# 85. Priorização

Considerar:

``` text
risco
impacto
custo
esforço
urgência
dependências
```

------------------------------------------------------------------------

# 86. Evolução Incremental

Preferir mudanças pequenas e reversíveis.

------------------------------------------------------------------------

# 87. Modernização

Modernização deverá resolver problemas reais, não seguir tendências.

------------------------------------------------------------------------

# 88. Migrações Grandes

Deverão ser divididas em etapas quando possível.

------------------------------------------------------------------------

# 89. Legado

Legado deverá ser:

-   conhecido;
-   isolado;
-   monitorado;
-   documentado;
-   migrado quando justificável.

------------------------------------------------------------------------

# 90. Automação

Automação deverá reduzir variação operacional.

------------------------------------------------------------------------

# 91. Golden Paths

A Engenharia poderá definir caminhos recomendados para operações comuns.

Exemplo:

``` text
novo serviço
→ template
→ pipeline
→ observabilidade
→ IaC
```

------------------------------------------------------------------------

# 92. Templates

Templates deverão acelerar adoção de padrões sem copiar configurações
inseguras.

------------------------------------------------------------------------

# 93. Self-Service

Self-service poderá ser adotado quando guardrails forem suficientes.

------------------------------------------------------------------------

# 94. Guardrails

Guardrails deverão impedir erros graves sem bloquear decisões legítimas.

------------------------------------------------------------------------

# 95. Policy as Code

Políticas críticas poderão ser automatizadas conforme maturidade.

------------------------------------------------------------------------

# 96. Segurança por Padrão

Templates e módulos deverão nascer seguros.

------------------------------------------------------------------------

# 97. Confiabilidade por Padrão

Novos componentes deverão incluir:

-   health checks;
-   logs;
-   métricas;
-   backup quando aplicável.

------------------------------------------------------------------------

# 98. Custo por Padrão

Templates deverão evitar recursos superdimensionados por padrão.

------------------------------------------------------------------------

# 99. Gestão do Conhecimento

Conhecimento crítico deverá ser institucionalizado.

------------------------------------------------------------------------

# 100. Treinamento

Mudanças de padrão deverão ser comunicadas à equipe.

------------------------------------------------------------------------

# 101. Onboarding

Novos engenheiros deverão conseguir compreender a infraestrutura por
documentação e repositórios oficiais.

------------------------------------------------------------------------

# 102. Bus Factor

Reduzir dependência de indivíduos.

------------------------------------------------------------------------

# 103. Continuidade da Equipe

A saída ou ausência de uma pessoa não deverá impedir operação de
componente crítico.

------------------------------------------------------------------------

# 104. Fornecedores

Fornecedores críticos deverão possuir owner e dependências conhecidas.

------------------------------------------------------------------------

# 105. Lock-in

Lock-in deverá ser conscientemente aceito quando o benefício justificar.

------------------------------------------------------------------------

# 106. Exit Strategy

Para dependências críticas com alto lock-in, avaliar como dados e
operação seriam migrados.

------------------------------------------------------------------------

# 107. Anti-Padrões

Evitar:

``` text
nova tecnologia
porque está em tendência
```

------------------------------------------------------------------------

``` text
exceção
sem prazo
```

------------------------------------------------------------------------

``` text
recurso
sem owner
```

------------------------------------------------------------------------

``` text
produção
configurada manualmente
sem registro
```

------------------------------------------------------------------------

``` text
versão EOL
sem plano
```

------------------------------------------------------------------------

``` text
padrão
que ninguém consegue
explicar ou operar
```

------------------------------------------------------------------------

``` text
governança
como burocracia
sem redução de risco
```

------------------------------------------------------------------------

``` text
migração grande
sem etapas
nem rollback
```

------------------------------------------------------------------------

``` text
documentação
desatualizada
após mudança
```

------------------------------------------------------------------------

# 108. Modelo de Governança de Referência

``` text
                 ENTERPRISE ARCHITECTURE
                          │
                          ▼
                  GINF GOVERNANCE
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
    STANDARDS         DECISIONS          EXCEPTIONS
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
                   IMPLEMENTATION
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
             IaC        CI/CD      OPERATIONS
              │           │           │
              └───────────┼───────────┘
                          ▼
                    OBSERVABILITY
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          INCIDENTS      COSTS       CAPACITY
             │            │            │
             └────────────┼────────────┘
                          ▼
                       REVIEW
                          │
                          ▼
                      EVOLUTION
```

------------------------------------------------------------------------

# 109. Checklist

## Governança

-   [ ] padrões definidos;
-   [ ] owners;
-   [ ] responsabilidades;
-   [ ] exceções registradas;
-   [ ] riscos explícitos.

## Tecnologia

-   [ ] problema concreto;
-   [ ] lifecycle;
-   [ ] versão;
-   [ ] owner;
-   [ ] segurança;
-   [ ] observabilidade;
-   [ ] custo;
-   [ ] operação.

## Recursos

-   [ ] inventário;
-   [ ] tags;
-   [ ] owner;
-   [ ] ambiente;
-   [ ] IaC quando aplicável;
-   [ ] recursos órfãos revisados.

## Operação

-   [ ] runbooks;
-   [ ] backups;
-   [ ] DR;
-   [ ] observabilidade;
-   [ ] capacidade;
-   [ ] incidentes retroalimentam padrões.

## Evolução

-   [ ] roadmap;
-   [ ] dívida técnica;
-   [ ] versões EOL;
-   [ ] migrações planejadas;
-   [ ] modernização baseada em necessidade.

## Conhecimento

-   [ ] documentação;
-   [ ] onboarding;
-   [ ] treinamento;
-   [ ] bus factor reduzido;
-   [ ] decisões registradas.

------------------------------------------------------------------------

# 110. Documentos Relacionados

-   GINF-01 --- Arquitetura da Infraestrutura
-   GINF-02 --- Ambientes e Configuração
-   GINF-03 --- Rede, DNS, Proxy e TLS
-   GINF-04 --- Runtime Django e Workers
-   GINF-05 --- Banco de Dados e Persistência
-   GINF-06 --- Redis, Cache e Filas
-   GINF-07 --- Storage e Arquivos
-   GINF-08 --- Containers, Imagens e Registry
-   GINF-09 --- CI/CD, Deploy e Rollback
-   GINF-10 --- Observabilidade, Logs, Métricas e Alertas
-   GINF-11 --- Backup, Restore e Disaster Recovery
-   GINF-12 --- Infraestrutura como Código e Automação
-   GINF-13 --- Escalabilidade, Alta Disponibilidade e Capacidade
-   GINF-14 --- Custos, FinOps e Governança de Recursos
-   GINF-15 --- Operação, Manutenção e Runbooks de Infraestrutura
-   GEA --- GereIgreja Enterprise Architecture
-   GSF --- GereIgreja Security Framework
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework
-   GDF --- GereIgreja Documentation Framework

------------------------------------------------------------------------

# 111. Princípios Finais

A infraestrutura do GereIgreja deverá evoluir sem perder coerência.

``` text
Padrões
+
Ownership
+
Decisões registradas
+
Automação
+
Revisão
=
Evolução controlada
```

O princípio central é:

``` text
Toda tecnologia possui
um motivo para entrar,
um padrão para permanecer
e um plano para sair.
```

Governança não deverá impedir evolução.

Ela deverá permitir que a plataforma evolua rapidamente sem transformar
crescimento em fragmentação, risco operacional ou dívida invisível.

------------------------------------------------------------------------

# 112. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`16-Governanca-Padroes-e-Evolucao-da-Infraestrutura.md`

**Documento**

`GINF-16`

**Código**

`GINF-GOVERNANCE-STANDARDS-EVOLUTION`

**Família**

`GINF — GereIgreja Infrastructure Engineering`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Documento anterior**

`GINF-15 — Operação, Manutenção e Runbooks de Infraestrutura`

**Próximo documento recomendado**

`17-Checklist-de-Producao-e-Prontidao-Operacional.md`
