Pasta:

docs/infraestrutura/

Arquivo:

12-Infraestrutura-como-Codigo-e-Automacao.md

Documento:

GINF-12

Código:

GINF-IAC-AUTOMATION

Família:

GINF --- GereIgreja Infrastructure Engineering

Frameworks relacionados:

GEA --- GereIgreja Enterprise Architecture GSF --- GereIgreja Security
Framework GOC --- GereIgreja Operations Center GQF --- GereIgreja
Quality Framework GereIgreja Backend Engineering

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GINF-12 --- Infraestrutura como Código e Automação

> "Infraestrutura crítica não deve depender da memória de uma pessoa nem
> de alterações manuais impossíveis de reproduzir."

------------------------------------------------------------------------

# Sumário

1.  Objetivo
2.  Escopo
3.  Relação com a Arquitetura
4.  Princípios Fundamentais
5.  Infraestrutura como Código
6.  Automação Operacional
7.  Fonte de Verdade
8.  Repositórios
9.  Organização do Código
10. Ambientes
11. Isolamento entre Ambientes
12. Estado Desejado
13. Estado Real
14. Drift
15. Detecção de Drift
16. Reconciliação
17. Idempotência
18. Reprodutibilidade
19. Imutabilidade
20. Provisionamento
21. Configuração
22. Recursos Gerenciados
23. Recursos Não Gerenciados
24. Rede
25. DNS
26. TLS
27. Compute
28. Containers
29. Banco de Dados
30. Redis
31. Storage
32. Observabilidade
33. Backup
34. Registry
35. Identidades
36. Permissões
37. Secrets
38. Outputs
39. Variáveis
40. Módulos
41. Reutilização
42. Versionamento
43. Dependências
44. Providers
45. Lock Files
46. State
47. State Remoto
48. Segurança do State
49. Locking
50. Backup do State
51. Importação de Recursos
52. Recursos Existentes
53. Plan
54. Review
55. Apply
56. Destroy
57. Proteção contra Destruição
58. CI/CD
59. Pipeline de Infraestrutura
60. Aprovação
61. Produção
62. Credenciais do Pipeline
63. Menor Privilégio
64. Mudanças Manuais
65. Break Glass
66. Auditoria
67. Logging
68. Evidências
69. Testes
70. Validação Estática
71. Policy as Code
72. Segurança
73. Scanning
74. Custos
75. FinOps
76. Tags e Labels
77. Naming
78. Inventário
79. Documentação
80. Runbooks
81. Bootstrap
82. Dependências Circulares
83. Migrações de Infraestrutura
84. Refactoring
85. Mudança de Provider
86. Disaster Recovery
87. Reconstrução
88. Automação de Rotinas
89. Jobs Operacionais
90. Scripts
91. Linguagens e Ferramentas
92. Observabilidade da Automação
93. Falhas
94. Retry
95. Timeouts
96. Concorrência
97. Segurança de Automação
98. Desenvolvimento
99. Staging
100. Produção
101. Anti-Padrões
102. Arquitetura de Referência
103. Checklist
104. Documentos Relacionados
105. Princípios Finais
106. Status do Documento

------------------------------------------------------------------------

# 1. Objetivo

Este documento estabelece o padrão oficial para Infraestrutura como
Código (IaC) e automação operacional do GereIgreja.

Seu objetivo é tornar a infraestrutura:

-   reproduzível;
-   versionada;
-   revisável;
-   auditável;
-   segura;
-   recuperável;
-   consistente entre ambientes.

------------------------------------------------------------------------

# 2. Escopo

Aplica-se a recursos como:

-   rede;
-   DNS;
-   TLS;
-   compute;
-   containers;
-   banco;
-   Redis;
-   storage;
-   registry;
-   observabilidade;
-   backups;
-   identidades;
-   permissões;
-   automações operacionais.

------------------------------------------------------------------------

# 3. Relação com a Arquitetura

``` text
Git
 │
 ▼
IaC
 │
 ▼
Plan
 │
 ▼
Review
 │
 ▼
Apply
 │
 ▼
Infraestrutura
 │
 ▼
Observabilidade
```

Mudanças deverão seguir fluxo controlado.

------------------------------------------------------------------------

# 4. Princípios Fundamentais

Aplicar:

-   código como fonte de verdade;
-   revisão;
-   idempotência;
-   mínimo acesso;
-   separação de ambientes;
-   state protegido;
-   automação;
-   rastreabilidade;
-   recuperação.

------------------------------------------------------------------------

# 5. Infraestrutura como Código

IaC descreve recursos de infraestrutura em arquivos versionáveis.

Objetivo:

``` text
infraestrutura
deixa de ser
configuração artesanal
```

------------------------------------------------------------------------

# 6. Automação Operacional

Nem toda automação é IaC.

Exemplos:

``` text
IaC
→ cria banco

Automação
→ executa verificação periódica
```

Ambos deverão seguir padrões de engenharia.

------------------------------------------------------------------------

# 7. Fonte de Verdade

Quando um recurso for gerenciado por IaC, o código deverá ser
considerado sua definição oficial.

------------------------------------------------------------------------

# 8. Repositórios

Código de infraestrutura deverá estar em repositório autorizado e com
histórico.

------------------------------------------------------------------------

# 9. Organização do Código

Estrutura deverá separar claramente:

-   módulos;
-   ambientes;
-   componentes;
-   configurações.

Evitar duplicação excessiva.

------------------------------------------------------------------------

# 10. Ambientes

Development, staging e production deverão possuir configuração
explícita.

------------------------------------------------------------------------

# 11. Isolamento entre Ambientes

State, credenciais e recursos deverão ser isolados.

``` text
state de staging
≠
state de production
```

------------------------------------------------------------------------

# 12. Estado Desejado

IaC descreve como a infraestrutura deve estar.

------------------------------------------------------------------------

# 13. Estado Real

É o que existe no provedor.

------------------------------------------------------------------------

# 14. Drift

Drift ocorre quando:

``` text
estado real
≠
estado declarado
```

------------------------------------------------------------------------

# 15. Detecção de Drift

Executar verificações periódicas ou plans controlados para identificar
divergências relevantes.

------------------------------------------------------------------------

# 16. Reconciliação

Drift deverá ser:

-   compreendido;
-   corrigido;
-   importado para código quando legítimo;
-   documentado quando excepcional.

------------------------------------------------------------------------

# 17. Idempotência

Executar novamente a automação com o mesmo estado desejado não deverá
causar mudanças desnecessárias.

------------------------------------------------------------------------

# 18. Reprodutibilidade

A infraestrutura deverá poder ser reconstruída com o menor número
possível de passos manuais.

------------------------------------------------------------------------

# 19. Imutabilidade

Quando apropriado, preferir substituir recursos ao invés de modificá-los
artesanalmente.

------------------------------------------------------------------------

# 20. Provisionamento

Provisionamento deverá ocorrer por mecanismo oficial.

------------------------------------------------------------------------

# 21. Configuração

Separar:

``` text
infraestrutura
configuração de aplicação
secrets
```

Aplicar GINF-02.

------------------------------------------------------------------------

# 22. Recursos Gerenciados

Todo recurso gerenciado deverá possuir owner e localização de sua
definição.

------------------------------------------------------------------------

# 23. Recursos Não Gerenciados

Recursos ainda manuais deverão ser inventariados.

O objetivo é reduzir progressivamente essa categoria.

------------------------------------------------------------------------

# 24. Rede

Rede deverá ser declarada conforme GINF-03 quando a plataforma adotada
permitir.

------------------------------------------------------------------------

# 25. DNS

Registros críticos deverão evoluir para gestão versionada quando
tecnicamente adequado.

------------------------------------------------------------------------

# 26. TLS

Automação deverá favorecer emissão e renovação controlada de
certificados.

------------------------------------------------------------------------

# 27. Compute

Instâncias, serviços e capacidades deverão ser reproduzíveis.

------------------------------------------------------------------------

# 28. Containers

Definições de runtime deverão referenciar imagens imutáveis conforme
GINF-08.

------------------------------------------------------------------------

# 29. Banco de Dados

Recursos de banco deverão ser protegidos contra destruição acidental.

Mudanças de schema pertencem às migrations da aplicação, não ao IaC de
infraestrutura.

------------------------------------------------------------------------

# 30. Redis

Configuração de infraestrutura Redis deverá ser reproduzível e separada
do conteúdo transitório.

------------------------------------------------------------------------

# 31. Storage

Buckets/containers e políticas deverão ser declarados quando possível.

------------------------------------------------------------------------

# 32. Observabilidade

Dashboards, alertas e integrações deverão evoluir para definições
versionadas quando a ferramenta suportar.

------------------------------------------------------------------------

# 33. Backup

Políticas de backup deverão ser automatizadas conforme GINF-11.

------------------------------------------------------------------------

# 34. Registry

Registry e políticas associadas deverão possuir configuração controlada.

------------------------------------------------------------------------

# 35. Identidades

Service accounts e identidades técnicas deverão ser criadas por processo
rastreável.

------------------------------------------------------------------------

# 36. Permissões

Permissões deverão seguir menor privilégio.

Mudanças deverão ser revisáveis.

------------------------------------------------------------------------

# 37. Secrets

Secrets não deverão estar no código IaC em texto aberto.

Referenciar mecanismos seguros.

------------------------------------------------------------------------

# 38. Outputs

Outputs não deverão revelar secrets.

------------------------------------------------------------------------

# 39. Variáveis

Variáveis deverão representar diferenças legítimas entre ambientes.

Não duplicar módulos inteiros apenas para mudar valores.

------------------------------------------------------------------------

# 40. Módulos

Módulos deverão encapsular padrões reutilizáveis.

------------------------------------------------------------------------

# 41. Reutilização

Reutilização não deverá esconder complexidade excessiva.

Preferir módulos claros e específicos.

------------------------------------------------------------------------

# 42. Versionamento

Mudanças de infraestrutura deverão possuir histórico e associação a
commits.

------------------------------------------------------------------------

# 43. Dependências

Dependências de módulos e ferramentas deverão ser controladas.

------------------------------------------------------------------------

# 44. Providers

Versões de providers deverão ser explicitamente gerenciadas.

------------------------------------------------------------------------

# 45. Lock Files

Lock files deverão ser versionados quando recomendados pela ferramenta
adotada.

------------------------------------------------------------------------

# 46. State

Ferramentas stateful exigem proteção especial do state.

Ele pode conter:

-   IDs;
-   topologia;
-   endpoints;
-   informações sensíveis.

------------------------------------------------------------------------

# 47. State Remoto

Produção deverá preferir backend remoto seguro quando a ferramenta
utilizar state.

------------------------------------------------------------------------

# 48. Segurança do State

Aplicar:

-   criptografia;
-   acesso restrito;
-   auditoria quando disponível;
-   separação por ambiente.

------------------------------------------------------------------------

# 49. Locking

State compartilhado deverá possuir locking quando suportado.

Evitar applies concorrentes.

------------------------------------------------------------------------

# 50. Backup do State

State crítico deverá possuir estratégia de recuperação.

------------------------------------------------------------------------

# 51. Importação de Recursos

Recursos existentes poderão ser importados para gestão IaC.

Antes:

``` text
inventariar
→ modelar
→ plan sem destruição
→ importar
→ validar
```

------------------------------------------------------------------------

# 52. Recursos Existentes

Não recriar recurso crítico apenas para colocá-lo sob IaC sem plano de
migração.

------------------------------------------------------------------------

# 53. Plan

Toda mudança deverá produzir plano quando a ferramenta suportar.

------------------------------------------------------------------------

# 54. Review

Plan deverá ser revisado antes de production.

A revisão deverá observar:

-   criação;
-   alteração;
-   destruição;
-   permissões;
-   custos;
-   impacto.

------------------------------------------------------------------------

# 55. Apply

Apply de production deverá ocorrer pelo processo oficial.

------------------------------------------------------------------------

# 56. Destroy

Destroy é operação de alto risco.

Deverá possuir controles adicionais para recursos críticos.

------------------------------------------------------------------------

# 57. Proteção contra Destruição

Utilizar mecanismos como:

-   deletion protection;
-   lifecycle protection;
-   approvals;
-   backups.

Especialmente para:

-   banco;
-   storage;
-   state.

------------------------------------------------------------------------

# 58. CI/CD

IaC deverá integrar-se ao pipeline.

Aplicar GINF-09.

------------------------------------------------------------------------

# 59. Pipeline de Infraestrutura

Fluxo recomendado:

``` text
PR
↓
format
↓
validate
↓
security scan
↓
plan
↓
review
↓
merge
↓
approval
↓
apply
```

------------------------------------------------------------------------

# 60. Aprovação

Mudanças críticas em production deverão possuir aprovação proporcional
ao risco.

------------------------------------------------------------------------

# 61. Produção

Apply manual em workstation pessoal deverá ser exceção.

Preferir execução controlada por CI/CD.

------------------------------------------------------------------------

# 62. Credenciais do Pipeline

Pipeline deverá usar identidade técnica própria.

------------------------------------------------------------------------

# 63. Menor Privilégio

Não conceder permissão administrativa global quando o pipeline necessita
apenas de subconjunto.

------------------------------------------------------------------------

# 64. Mudanças Manuais

Mudanças manuais em production deverão ser excepcionais.

Depois:

``` text
registrar
→ reconciliar com código
→ executar plan
→ remover drift
```

------------------------------------------------------------------------

# 65. Break Glass

Acesso emergencial deverá existir quando necessário, mas ser:

-   restrito;
-   auditado;
-   temporário;
-   revisado posteriormente.

------------------------------------------------------------------------

# 66. Auditoria

Deverá ser possível identificar:

-   quem propôs;
-   quem aprovou;
-   qual plan;
-   qual apply;
-   resultado.

------------------------------------------------------------------------

# 67. Logging

Automação deverá registrar execução e falhas sem expor secrets.

------------------------------------------------------------------------

# 68. Evidências

Preservar logs e plans de mudanças relevantes conforme política de
retenção.

------------------------------------------------------------------------

# 69. Testes

Código de infraestrutura também deverá ser testado.

------------------------------------------------------------------------

# 70. Validação Estática

Executar:

-   format;
-   validate;
-   lint;
-   análise de configuração.

------------------------------------------------------------------------

# 71. Policy as Code

Políticas automatizadas poderão impedir configurações inseguras.

Exemplos:

``` text
bucket público
porta administrativa aberta
recurso sem criptografia
```

A adoção deverá acompanhar maturidade.

------------------------------------------------------------------------

# 72. Segurança

IaC é código privilegiado.

Revisão de segurança é especialmente importante.

------------------------------------------------------------------------

# 73. Scanning

Ferramentas de scanning poderão identificar:

-   exposição pública;
-   permissões amplas;
-   criptografia ausente;
-   configurações inseguras.

------------------------------------------------------------------------

# 74. Custos

Plan deverá permitir avaliar impacto financeiro quando possível.

------------------------------------------------------------------------

# 75. FinOps

Infraestrutura deverá possuir visibilidade de custos suficiente para
evitar crescimento sem controle.

------------------------------------------------------------------------

# 76. Tags e Labels

Recursos deverão possuir tags/labels padronizados quando suportados.

Exemplos:

``` text
environment
service
owner
managed_by
```

------------------------------------------------------------------------

# 77. Naming

Nomes deverão ser consistentes e previsíveis.

Evitar depender de nomes que contenham dados sensíveis.

------------------------------------------------------------------------

# 78. Inventário

IaC deverá ajudar a manter inventário da infraestrutura.

------------------------------------------------------------------------

# 79. Documentação

Componentes complexos deverão possuir documentação complementar.

Código não substitui explicação arquitetural.

------------------------------------------------------------------------

# 80. Runbooks

Operações de alto risco deverão possuir runbooks.

------------------------------------------------------------------------

# 81. Bootstrap

Alguns recursos podem ser necessários antes do próprio IaC funcionar.

Exemplos:

-   backend de state;
-   identidade inicial;
-   repositório.

O bootstrap deverá ser documentado.

------------------------------------------------------------------------

# 82. Dependências Circulares

Evitar arquiteturas em que a ferramenta precisa de recurso que só ela
própria consegue criar sem bootstrap definido.

------------------------------------------------------------------------

# 83. Migrações de Infraestrutura

Mudanças grandes deverão ser realizadas em etapas.

------------------------------------------------------------------------

# 84. Refactoring

Refatorar código IaC sem alterar infraestrutura real exige atenção a
identificadores e state.

Sempre revisar plan.

------------------------------------------------------------------------

# 85. Mudança de Provider

Mudanças de provedor são projetos de migração.

Exigem:

-   inventário;
-   compatibilidade;
-   dados;
-   DNS;
-   rollback;
-   validação.

------------------------------------------------------------------------

# 86. Disaster Recovery

IaC deverá contribuir para reconstrução após desastre.

Aplicar GINF-11.

------------------------------------------------------------------------

# 87. Reconstrução

A equipe deverá ser capaz de reconstruir componentes essenciais sem
depender de configuração manual desconhecida.

------------------------------------------------------------------------

# 88. Automação de Rotinas

Automatizar operações repetitivas como:

-   limpeza;
-   validação;
-   rotação;
-   verificação;
-   reconciliação;
-   manutenção.

------------------------------------------------------------------------

# 89. Jobs Operacionais

Jobs deverão possuir:

-   owner;
-   finalidade;
-   logs;
-   timeout;
-   resultado;
-   alerta quando crítico.

------------------------------------------------------------------------

# 90. Scripts

Scripts operacionais são software.

Devem possuir:

-   versionamento;
-   tratamento de erros;
-   parâmetros;
-   documentação;
-   testes proporcionais ao risco.

------------------------------------------------------------------------

# 91. Linguagens e Ferramentas

Preferir ferramentas padronizadas pela Engenharia.

Evitar proliferação de tecnologias para tarefas equivalentes.

------------------------------------------------------------------------

# 92. Observabilidade da Automação

Automação crítica deverá informar:

``` text
iniciou
terminou
falhou
quanto demorou
o que alterou
```

------------------------------------------------------------------------

# 93. Falhas

Falha deverá deixar estado conhecido ou exigir reconciliação explícita.

------------------------------------------------------------------------

# 94. Retry

Retries deverão ser seguros.

Operações precisam ser idempotentes sempre que possível.

------------------------------------------------------------------------

# 95. Timeouts

Toda automação que depende de rede deverá possuir timeout adequado.

------------------------------------------------------------------------

# 96. Concorrência

Execuções concorrentes deverão ser controladas quando puderem alterar o
mesmo recurso.

------------------------------------------------------------------------

# 97. Segurança de Automação

Scripts não deverão:

-   imprimir secrets;
-   aceitar comandos arbitrários sem validação;
-   usar credenciais administrativas desnecessárias;
-   ignorar erros críticos.

------------------------------------------------------------------------

# 98. Desenvolvimento

Development deverá permitir testar mudanças sem acessar production.

------------------------------------------------------------------------

# 99. Staging

Mudanças relevantes deverão ser validadas em staging quando aplicável.

------------------------------------------------------------------------

# 100. Produção

Production deverá possuir:

-   state separado;
-   credenciais separadas;
-   approvals;
-   proteção contra destruição;
-   auditoria;
-   backups.

------------------------------------------------------------------------

# 101. Anti-Padrões

Evitar:

``` text
"funciona porque
alguém configurou
no console"
```

------------------------------------------------------------------------

``` text
state de production
no notebook local
sem proteção
```

------------------------------------------------------------------------

``` text
secret
hardcoded
no IaC
```

------------------------------------------------------------------------

``` text
apply production
sem revisar plan
```

------------------------------------------------------------------------

``` text
terraform destroy
ou equivalente
sem proteção
```

------------------------------------------------------------------------

``` text
mudança manual
sem reconciliar
com código
```

------------------------------------------------------------------------

``` text
um único state
para todos os ambientes
```

------------------------------------------------------------------------

``` text
pipeline
com administrador global
sem necessidade
```

------------------------------------------------------------------------

``` text
script operacional
sem logs
e sem tratamento de erro
```

------------------------------------------------------------------------

# 102. Arquitetura de Referência

``` text
                    ENGINEERING
                         │
                         ▼
                    SOURCE CONTROL
                         │
                         ▼
                    PULL REQUEST
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
           VALIDATE    SECURITY     PLAN
              └──────────┼──────────┘
                         ▼
                       REVIEW
                         │
                         ▼
                      APPROVAL
                         │
                         ▼
                       APPLY
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
       NETWORK        DATA LAYER      RUNTIME
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                  OBSERVABILITY
                         │
                         ▼
                   DRIFT / AUDIT

State remoto protegido
e separado por ambiente.
```

------------------------------------------------------------------------

# 103. Checklist

## Código

-   [ ] versionado;
-   [ ] organizado;
-   [ ] formatado;
-   [ ] validado;
-   [ ] revisado.

## Ambientes

-   [ ] state separado;
-   [ ] credenciais separadas;
-   [ ] variáveis explícitas;
-   [ ] production protegida.

## State

-   [ ] remoto quando aplicável;
-   [ ] criptografado;
-   [ ] acesso restrito;
-   [ ] locking;
-   [ ] backup/recuperação.

## Pipeline

-   [ ] validate;
-   [ ] scan;
-   [ ] plan;
-   [ ] review;
-   [ ] approval;
-   [ ] apply controlado.

## Segurança

-   [ ] sem secrets no código;
-   [ ] menor privilégio;
-   [ ] proteção contra destroy;
-   [ ] break glass controlado;
-   [ ] auditoria.

## Operação

-   [ ] drift detectável;
-   [ ] mudanças manuais reconciliadas;
-   [ ] jobs observáveis;
-   [ ] retries seguros;
-   [ ] timeouts;
-   [ ] runbooks.

## Recuperação

-   [ ] infraestrutura reconstruível;
-   [ ] bootstrap documentado;
-   [ ] dependências conhecidas;
-   [ ] integração com DR.

------------------------------------------------------------------------

# 104. Documentos Relacionados

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
-   GSF-09 --- Gestão de Segredos e Criptografia
-   GSF-12 --- Gestão de Vulnerabilidades
-   GSF-13 --- Gestão de Incidentes de Segurança
-   GSF-15 --- Secure Development Lifecycle
-   GOC --- GereIgreja Operations Center
-   GQF --- GereIgreja Quality Framework

------------------------------------------------------------------------

# 105. Princípios Finais

A infraestrutura do GereIgreja deverá evoluir de configuração manual
para estado declarado e reproduzível.

``` text
Código
+
Review
+
Plan
+
Automação
+
Auditoria
=
Infraestrutura controlada
```

O princípio central é:

``` text
Se um recurso é crítico,
devemos saber
como ele foi criado,
como alterá-lo
e como reconstruí-lo.
```

Automação não elimina responsabilidade humana.

Ela transforma conhecimento operacional em processo repetível, revisável
e recuperável.

------------------------------------------------------------------------

# 106. Status do Documento

**Pasta**

`docs/infraestrutura/`

**Arquivo**

`12-Infraestrutura-como-Codigo-e-Automacao.md`

**Documento**

`GINF-12`

**Código**

`GINF-IAC-AUTOMATION`

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

`GINF-11 — Backup, Restore e Disaster Recovery`

**Próximo documento recomendado**

`13-Escalabilidade-Alta-Disponibilidade-e-Capacidade.md`
