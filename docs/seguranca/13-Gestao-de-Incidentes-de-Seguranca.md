Pasta:

docs/seguranca/

Arquivo:

13-Gestao-de-Incidentes-de-Seguranca.md

Documento:

GSF-13

Código:

GSF-SECURITY-INCIDENT-MANAGEMENT

Família:

GSF — GereIgreja Security

Framework:

GSF — GereIgreja Security Framework

Versão:

1.0

Status:

Oficial

Responsável:

Equipe de Engenharia

Última atualização:

Agosto de 2026

# GSF-13 — Gestão de Incidentes de Segurança

> "Um incidente de segurança não termina quando o sistema volta a funcionar. Ele termina quando o impacto foi compreendido, a causa foi tratada, as evidências foram preservadas e a plataforma ficou mais segura do que antes."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação com o GSF
5. Princípios
6. O que é um Incidente de Segurança
7. Evento, Vulnerabilidade e Incidente
8. Objetivos da Resposta
9. Ciclo Oficial de Resposta
10. Detecção
11. Fontes de Detecção
12. Logging
13. Monitoramento
14. Alertas
15. Relatos Internos
16. Relatos de Usuários
17. Vulnerabilidades Exploradas
18. Falhas de Infraestrutura
19. Falhas de Integração
20. Triagem Inicial
21. Registro do Incidente
22. Identificador
23. Data e Hora
24. Responsável
25. Serviços Afetados
26. Tenants Afetados
27. Dados Afetados
28. Classificação
29. Severidade
30. Criticidade
31. Impacto
32. Confidencialidade
33. Integridade
34. Disponibilidade
35. Rastreabilidade
36. Multi-Tenant
37. Dados Pessoais
38. Dados Financeiros
39. Dados Ministeriais
40. Autenticação
41. Autorização
42. Secrets
43. Infraestrutura
44. Níveis de Severidade
45. Incidente Crítico
46. Incidente Alto
47. Incidente Médio
48. Incidente Baixo
49. Escalonamento
50. Contenção
51. Contenção Imediata
52. Contenção Temporária
53. Isolamento
54. Bloqueio de Usuário
55. Revogação de Sessões
56. Revogação de Tokens
57. Rotação de Secrets
58. Desativação de Endpoint
59. Desativação de Integração
60. Bloqueio de Funcionalidade
61. Isolamento de Tenant
62. Preservação de Evidências
63. Logs
64. Registros de Auditoria
65. Banco de Dados
66. Arquivos
67. Configurações
68. Evidências de Infraestrutura
69. Linha do Tempo
70. Correlação
71. Investigação
72. Determinação da Causa
73. Causa Raiz
74. Vetor de Entrada
75. Escopo Real
76. Exploração
77. Persistência
78. Movimento Lateral
79. Acesso entre Tenants
80. Comprometimento de Conta
81. Comprometimento de Credencial
82. Exposição de Dados
83. Alteração de Dados
84. Exclusão de Dados
85. Indisponibilidade
86. Correção
87. Remediação
88. Vulnerabilidade Relacionada
89. Hotfix
90. Correção de Configuração
91. Atualização de Dependência
92. Rotação de Credenciais
93. Correção de Permissões
94. Correção Multi-Tenant
95. Recuperação
96. Backup
97. Restauração
98. Validação Pós-Recuperação
99. Retorno à Produção
100. Monitoramento Reforçado
101. Comunicação
102. Comunicação Interna
103. Comunicação Técnica
104. Comunicação Operacional
105. Comunicação com Organizações Afetadas
106. Comunicação Externa
107. Comunicação com Fornecedores
108. LGPD e Comunicação de Incidentes
109. Confidencialidade Durante o Incidente
110. Registro de Decisões
111. Responsabilidades
112. Engenharia
113. Operações
114. Qualidade
115. Segurança
116. Responsável pelo Incidente
117. Módulos Afetados
118. Incidentes de Autenticação
119. Incidentes de Autorização
120. Incidentes Multi-Tenant
121. Incidentes Financeiros
122. Incidentes de Secretaria
123. Incidentes de Comunicação
124. Incidentes de API
125. Incidentes de Integração
126. Incidentes de Infraestrutura
127. Incidentes de Backup
128. Incidentes de Dados
129. Incidentes de Secrets
130. Incidentes no Django Admin
131. Incidentes em Tasks e Automações
132. Incidentes no Portal Público
133. Abuso Interno
134. Erro Humano
135. Falso Positivo
136. Encerramento
137. Critérios de Encerramento
138. Relatório Pós-Incidente
139. Post-Mortem
140. Lições Aprendidas
141. Ações Corretivas
142. Ações Preventivas
143. Débitos de Segurança
144. Atualização da Documentação
145. Atualização de Testes
146. Atualização de Monitoramento
147. Atualização de Runbooks
148. Recorrência
149. Simulações
150. Exercícios de Incidente
151. Evidências Arquiteturais
152. Especificações Oficiais
153. Anti-Padrões
154. Checklist
155. Documentos Relacionados
156. Princípios Finais
157. Status do Documento

---

# 1. Objetivo

Este documento estabelece o processo oficial de Gestão de Incidentes de Segurança do GereIgreja.

Seu objetivo é garantir que incidentes sejam:

- detectados;
- registrados;
- classificados;
- contidos;
- investigados;
- corrigidos;
- recuperados;
- documentados;
- utilizados como fonte de melhoria.

Todo incidente deverá produzir uma resposta proporcional ao seu impacto.

O objetivo não deverá ser apenas restaurar o funcionamento técnico da plataforma.

A resposta deverá também:

- proteger dados;
- interromper exploração;
- preservar evidências;
- identificar causa;
- avaliar impacto;
- impedir recorrência.

---

# 2. Escopo

Este documento aplica-se a incidentes envolvendo:

- autenticação;
- autorização;
- multi-tenant;
- dados;
- APIs;
- infraestrutura;
- secrets;
- banco de dados;
- integrações;
- serviços externos;
- tasks;
- automações;
- Django Admin;
- Portal Público;
- módulos funcionais;
- backups;
- logging;
- monitoramento.

Aplica-se a ambientes de:

- produção;
- homologação;
- desenvolvimento;

quando o evento possuir impacto real ou potencial sobre a segurança da plataforma.

---

# 3. Papel deste Documento

O GSF-13 recebe informações produzidas pelos controles anteriores.

Sua posição é:

```text
GSF-10
Logging e Monitoramento
        ↓
GSF-11
Continuidade e Recuperação
        ↓
GSF-12
Gestão de Vulnerabilidades
        ↓
GSF-13
Gestão de Incidentes
        ↓
GSF-14
Conformidade e LGPD
````

Quando uma vulnerabilidade é explorada, o GSF-13 deverá ser acionado.

---

# 4. Relação com o GSF

O GereIgreja Security Framework estabelece o fluxo oficial:

```text
Detecção
    │
    ▼
Classificação
    │
    ▼
Contenção
    │
    ▼
Correção
    │
    ▼
Recuperação
    │
    ▼
Lições Aprendidas
```

Este documento detalha cada uma dessas etapas.

---

# 5. Princípios

A resposta a incidentes deverá seguir:

* rapidez proporcional;
* preservação de evidências;
* contenção segura;
* menor privilégio;
* rastreabilidade;
* comunicação controlada;
* recuperação validada;
* aprendizado;
* melhoria contínua.

---

# 6. O que é um Incidente de Segurança

Incidente é um evento confirmado ou suficientemente provável que afete ou ameace:

* confidencialidade;
* integridade;
* disponibilidade;
* autenticação;
* autorização;
* isolamento multi-tenant;
* privacidade;
* rastreabilidade.

Exemplos:

```text
Acesso entre tenants

Credencial comprometida

Secret exposto

Alteração financeira indevida

API vulnerável explorada

Conta administrativa comprometida

Dados confidenciais expostos

Backup indisponível durante recuperação
```

---

# 7. Evento, Vulnerabilidade e Incidente

Os conceitos deverão permanecer distintos.

```text
Evento
    ↓
Algo aconteceu

Vulnerabilidade
    ↓
Existe uma fraqueza

Incidente
    ↓
A segurança foi afetada
ou existe forte evidência de comprometimento
```

Exemplo:

```text
Endpoint sem filtro por tenant
→ Vulnerabilidade

Usuário acessou dados de outro tenant
→ Incidente
```

---

# 8. Objetivos da Resposta

Toda resposta deverá buscar:

```text
Parar o impacto

Preservar evidências

Determinar o escopo

Eliminar a causa

Recuperar com segurança

Evitar recorrência
```

---

# 9. Ciclo Oficial de Resposta

O ciclo completo deverá ser:

```text
Detecção
    ↓
Triagem
    ↓
Registro
    ↓
Classificação
    ↓
Contenção
    ↓
Preservação de Evidências
    ↓
Investigação
    ↓
Correção
    ↓
Recuperação
    ↓
Validação
    ↓
Comunicação
    ↓
Encerramento
    ↓
Lições Aprendidas
```

---

# 10. Detecção

Um incidente poderá ser detectado por:

* monitoramento;
* logs;
* auditoria;
* usuário;
* desenvolvedor;
* operação;
* fornecedor;
* alerta;
* teste;
* investigação;
* auditoria externa.

Todo relato relevante deverá receber triagem.

---

# 11. Fontes de Detecção

Fontes poderão incluir:

```text
Logs da aplicação

Logs de infraestrutura

Registros de auditoria

Alertas

Reports de erros

Relatos de usuários

Ferramentas de segurança

Fornecedores

Code review
```

---

# 12. Logging

O GSF-10 deverá fornecer informações suficientes para investigação.

Logs não deverão ser alterados desnecessariamente após detecção.

---

# 13. Monitoramento

Monitoramento deverá permitir detectar eventos como:

* aumento de falhas;
* acessos anormais;
* integrações quebradas;
* indisponibilidade;
* autenticação suspeita;
* acesso entre tenants.

---

# 14. Alertas

Alertas deverão indicar necessidade de ação.

Um alerta não significa automaticamente incidente.

Ele inicia investigação ou triagem.

---

# 15. Relatos Internos

Desenvolvedores, suporte ou operação poderão identificar comportamento suspeito.

O relato deverá ser registrado e avaliado.

---

# 16. Relatos de Usuários

Relato de usuário como:

```text
"Estou vendo dados de outra igreja."
```

deverá ser tratado com prioridade elevada.

Não deverá ser descartado inicialmente como simples erro visual.

---

# 17. Vulnerabilidades Exploradas

Quando existir evidência de exploração:

```text
GSF-12
    ↓
GSF-13
```

A vulnerabilidade continuará sendo corrigida, mas o evento deverá ser tratado também como incidente.

---

# 18. Falhas de Infraestrutura

Falhas de infraestrutura podem constituir incidentes de segurança quando afetarem:

* disponibilidade;
* integridade;
* confidencialidade;
* acesso.

---

# 19. Falhas de Integração

Falha de integração poderá ser incidente quando:

* expuser dados;
* gerar operações indevidas;
* utilizar credenciais comprometidas;
* provocar grande indisponibilidade.

---

# 20. Triagem Inicial

A triagem deverá responder rapidamente:

```text
É real?

Ainda está acontecendo?

Qual o provável impacto?

Precisa conter imediatamente?

Quais sistemas estão envolvidos?

Quais tenants podem estar afetados?
```

---

# 21. Registro do Incidente

Incidentes confirmados ou suficientemente relevantes deverão possuir registro formal.

Modelo:

```text
ID
Título
Data
Origem
Severidade
Status
Responsável
Serviços afetados
Tenants afetados
Dados afetados
Descrição
Ações
Evidências
```

---

# 22. Identificador

Cada incidente formal deverá possuir identificador.

Exemplo conceitual:

```text
INC-2026-001
```

O formato poderá ser padronizado pela governança.

---

# 23. Data e Hora

Registrar:

* momento de detecção;
* momento estimado de início;
* ações relevantes;
* momento de contenção;
* recuperação.

---

# 24. Responsável

Todo incidente deverá possuir responsável pela coordenação.

Essa pessoa não precisa executar todas as tarefas.

Sua função é manter:

* direção;
* comunicação;
* registro;
* acompanhamento.

---

# 25. Serviços Afetados

Identificar:

* aplicação;
* banco;
* API;
* integração;
* módulo;
* infraestrutura;
* serviço externo.

---

# 26. Tenants Afetados

Quando aplicável, determinar:

```text
Um tenant?

Alguns tenants?

Todos os tenants?

Ainda desconhecido?
```

"Desconhecido" deverá ser estado temporário durante investigação.

---

# 27. Dados Afetados

Avaliar:

* classificação;
* volume;
* tipo;
* período;
* tenants;
* pessoas.

---

# 28. Classificação

A classificação deverá considerar o impacto real e potencial.

---

# 29. Severidade

Modelo:

```text
CRÍTICA
ALTA
MÉDIA
BAIXA
```

O nível poderá ser ajustado conforme novas evidências.

---

# 30. Criticidade

A criticidade deverá levar em conta:

* ativo;
* impacto;
* duração;
* exposição;
* abrangência;
* possibilidade de exploração contínua.

---

# 31. Impacto

Avaliar impacto sobre:

```text
Confidencialidade
Integridade
Disponibilidade
Privacidade
Rastreabilidade
Isolamento
```

---

# 32. Confidencialidade

Incidente de confidencialidade ocorre quando informação é acessada ou divulgada de maneira indevida.

---

# 33. Integridade

Incidente de integridade ocorre quando dados são:

* alterados;
* corrompidos;
* excluídos;

sem autorização adequada.

---

# 34. Disponibilidade

Incidente de disponibilidade ocorre quando serviço ou dado necessário fica indisponível de forma relevante.

---

# 35. Rastreabilidade

Falha de auditoria ou perda de evidências também pode ampliar o impacto.

---

# 36. Multi-Tenant

Qualquer quebra confirmada de isolamento entre tenants deverá receber prioridade elevada.

Perguntas imediatas:

```text
Quais tenants?

Quais recursos?

Qual período?

Foi leitura?

Foi alteração?

Foi exportação?

Existem evidências?
```

---

# 37. Dados Pessoais

Incidentes envolvendo dados pessoais deverão seguir também o GSF-14.

---

# 38. Dados Financeiros

Exposição ou alteração indevida de dados financeiros possui alta criticidade.

---

# 39. Dados Ministeriais

Dados ministeriais deverão receber tratamento compatível com sua classificação Confidencial.

---

# 40. Autenticação

Incidentes poderão incluir:

* bypass;
* roubo de sessão;
* comprometimento de credencial;
* recuperação indevida;
* conta invadida.

---

# 41. Autorização

Exemplos:

```text
Usuário sem permissão
executa ação administrativa
```

```text
Usuário comum
altera permissões
```

---

# 42. Secrets

Secret exposto poderá exigir:

```text
Revogação imediata
+
Rotação
+
Investigação
```

---

# 43. Infraestrutura

Incidentes poderão envolver:

* banco;
* servidor;
* serviço gerenciado;
* storage;
* rede;
* configuração;
* deploy.

---

# 44. Níveis de Severidade

A classificação deverá orientar a resposta.

---

# 45. Incidente Crítico

Pode envolver:

* acesso massivo entre tenants;
* comprometimento administrativo amplo;
* exposição extensa de dados Confidenciais;
* alteração financeira ampla;
* indisponibilidade crítica prolongada;
* comprometimento central da infraestrutura;
* secret central explorado.

Deverá possuir resposta imediata.

---

# 46. Incidente Alto

Pode envolver impacto significativo, porém mais limitado em abrangência.

---

# 47. Incidente Médio

Pode envolver impacto controlado ou limitado, sem comprometimento amplo.

---

# 48. Incidente Baixo

Pode envolver situação de baixo impacto, já contida ou com exposição mínima.

Baixa severidade ainda deverá ser registrada quando relevante.

---

# 49. Escalonamento

Incidentes deverão ser escalonados conforme:

* severidade;
* dados;
* tenants;
* infraestrutura;
* necessidade jurídica;
* necessidade operacional.

---

# 50. Contenção

Contenção busca impedir continuidade do dano.

Regra:

```text
Primeiro:
parar a exploração.

Depois:
restaurar normalmente.
```

---

# 51. Contenção Imediata

Exemplos:

* bloquear endpoint;
* revogar token;
* suspender conta;
* desativar integração;
* restringir acesso.

---

# 52. Contenção Temporária

Pode ser utilizada enquanto a correção definitiva é preparada.

---

# 53. Isolamento

Um componente comprometido poderá precisar ser isolado.

---

# 54. Bloqueio de Usuário

Conta suspeita poderá ser suspensa temporariamente.

A ação deverá preservar evidências.

---

# 55. Revogação de Sessões

Quando credenciais ou sessão forem comprometidas, sessões existentes poderão precisar ser revogadas.

---

# 56. Revogação de Tokens

Tokens suspeitos deverão ser considerados não confiáveis.

---

# 57. Rotação de Secrets

Secrets expostos deverão ser rotacionados conforme GSF-09.

---

# 58. Desativação de Endpoint

Endpoint vulnerável poderá ser temporariamente desativado.

Disponibilidade não deverá prevalecer sobre segurança quando o risco for grave.

---

# 59. Desativação de Integração

Integração comprometida poderá ser suspensa.

---

# 60. Bloqueio de Funcionalidade

Funcionalidade vulnerável poderá ser temporariamente removida.

---

# 61. Isolamento de Tenant

Quando um incidente afetar tenant específico, medidas poderão ser aplicadas ao contexto afetado sem necessariamente interromper toda a plataforma.

A decisão deverá evitar ampliar o impacto.

---

# 62. Preservação de Evidências

Antes de alterar sistemas significativamente, preservar evidências quando isso não impedir contenção urgente.

---

# 63. Logs

Logs relevantes deverão ser preservados.

---

# 64. Registros de Auditoria

Auditoria funcional e de segurança deverá ser protegida contra alteração ou exclusão.

---

# 65. Banco de Dados

Quando necessário, poderão ser preservadas:

* consultas relevantes;
* registros;
* snapshots;
* informações de estado.

Sempre respeitando privacidade e segurança.

---

# 66. Arquivos

Arquivos relacionados ao incidente deverão ser preservados de forma segura quando necessários como evidência.

---

# 67. Configurações

Configurações antes da correção poderão ser importantes para entender a causa.

---

# 68. Evidências de Infraestrutura

Podem incluir:

* logs;
* eventos;
* deploys;
* alterações;
* configurações;
* acessos.

---

# 69. Linha do Tempo

Todo incidente relevante deverá possuir cronologia.

Exemplo:

```text
10:15 — primeiro evento conhecido
10:22 — alerta gerado
10:30 — incidente confirmado
10:36 — endpoint bloqueado
11:10 — causa identificada
12:00 — correção implantada
12:20 — validação concluída
```

---

# 70. Correlação

Request IDs, usuários, tenants e recursos deverão ser correlacionados quando possível.

---

# 71. Investigação

A investigação deverá determinar:

```text
O que aconteceu?

Como aconteceu?

Quando começou?

Quem ou o que foi afetado?

Ainda está acontecendo?

Qual a causa?
```

---

# 72. Determinação da Causa

A investigação deverá diferenciar sintoma e causa.

Exemplo:

```text
Sintoma:
dados de outra igreja apareceram

Causa:
query sem filtro por tenant
```

---

# 73. Causa Raiz

A análise deverá buscar a causa estrutural.

Exemplo:

```text
Falha local
        ↓
ausência de selector centralizado
        ↓
padrão de consulta inseguro
```

A correção poderá precisar ir além de uma única linha.

---

# 74. Vetor de Entrada

Identificar como o incidente ocorreu.

Exemplos:

* URL;
* API;
* conta comprometida;
* integração;
* secret;
* upload;
* configuração;
* ação administrativa.

---

# 75. Escopo Real

Não presumir que o primeiro caso detectado seja o único.

Buscar:

* outros recursos;
* outros tenants;
* outros usuários;
* outros períodos.

---

# 76. Exploração

Diferenciar:

```text
Vulnerabilidade existia
```

de:

```text
Vulnerabilidade foi explorada
```

Essa distinção afeta impacto e conformidade.

---

# 77. Persistência

Avaliar se o atacante ou processo indevido criou:

* conta;
* token;
* configuração;
* integração;
* alteração persistente.

---

# 78. Movimento Lateral

Avaliar se o comprometimento permitiu acesso a outros recursos.

---

# 79. Acesso entre Tenants

Esse cenário deverá receber investigação dedicada.

Verificar:

* objetos acessados;
* requests;
* exports;
* cache;
* relatórios;
* APIs;
* tasks.

---

# 80. Comprometimento de Conta

Conta comprometida deverá ser:

* contida;
* revisada;
* ter sessões revogadas;
* ter credenciais redefinidas quando aplicável;
* ter ações investigadas.

---

# 81. Comprometimento de Credencial

Credencial técnica comprometida deverá ser rotacionada.

---

# 82. Exposição de Dados

Determinar:

* dado;
* classificação;
* quantidade;
* tenant;
* pessoa;
* período;
* destino.

---

# 83. Alteração de Dados

Verificar:

* registros alterados;
* valores anteriores;
* impacto;
* auditoria;
* possibilidade de restauração.

---

# 84. Exclusão de Dados

Determinar se:

* existe soft delete;
* existe auditoria;
* existe backup;
* é possível recuperação seletiva.

---

# 85. Indisponibilidade

Determinar:

* início;
* duração;
* serviços;
* usuários;
* causa;
* recuperação.

---

# 86. Correção

Correção deverá eliminar ou reduzir a causa.

---

# 87. Remediação

Pode incluir:

* código;
* configuração;
* arquitetura;
* dependência;
* permissão;
* secret;
* infraestrutura.

---

# 88. Vulnerabilidade Relacionada

Se o incidente revelou vulnerabilidade, ela deverá ser registrada no processo GSF-12.

---

# 89. Hotfix

Incidentes críticos poderão exigir hotfix.

O hotfix deverá continuar:

* revisado;
* testado;
* rastreável.

---

# 90. Correção de Configuração

Incidentes nem sempre exigem código.

Exemplo:

```text
CORS incorreto
DEBUG habilitado
secret exposto
permissão excessiva
```

---

# 91. Atualização de Dependência

Se a causa estiver em dependência vulnerável, deverá ser avaliada atualização.

---

# 92. Rotação de Credenciais

Rotação deverá ocorrer quando houver possibilidade razoável de comprometimento.

---

# 93. Correção de Permissões

Permissões excessivas deverão ser reduzidas.

Também deverá ser investigado quem utilizou o acesso anteriormente.

---

# 94. Correção Multi-Tenant

Falhas multi-tenant deverão ser corrigidas preferencialmente em camada reutilizável.

Exemplo:

```text
Selector central
Manager
Service
Permission
```

quando compatível com a arquitetura.

---

# 95. Recuperação

Após a correção, a plataforma deverá voltar à operação de forma segura.

---

# 96. Backup

Backup poderá ser necessário quando houver perda ou corrupção de dados.

Seguir GSF-11.

---

# 97. Restauração

A restauração deverá ocorrer somente após contenção do comprometimento ativo.

---

# 98. Validação Pós-Recuperação

Verificar:

* aplicação;
* login;
* permissões;
* tenant;
* dados;
* integrações;
* financeiro;
* tasks;
* monitoramento.

---

# 99. Retorno à Produção

O retorno deverá ser deliberado.

Não deverá ocorrer somente porque "a página voltou a abrir".

---

# 100. Monitoramento Reforçado

Após incidente, poderá ser necessário monitoramento temporariamente mais detalhado.

O objetivo é detectar recorrência.

---

# 101. Comunicação

Comunicação deverá ser coordenada.

Informações incorretas ou prematuras podem ampliar impacto.

---

# 102. Comunicação Interna

A equipe deverá conhecer:

* status;
* impacto;
* responsável;
* ações;
* restrições.

---

# 103. Comunicação Técnica

Detalhes técnicos deverão ser compartilhados apenas com quem necessita.

---

# 104. Comunicação Operacional

Operações deverá saber quais serviços:

* estão indisponíveis;
* estão degradados;
* podem ser utilizados;
* devem permanecer bloqueados.

---

# 105. Comunicação com Organizações Afetadas

Quando necessário, a comunicação deverá ser:

* clara;
* factual;
* proporcional;
* coordenada;
* compatível com LGPD e políticas aplicáveis.

Não deverão ser feitas afirmações especulativas.

---

# 106. Comunicação Externa

Comunicação pública deverá ocorrer apenas quando apropriada e autorizada.

---

# 107. Comunicação com Fornecedores

Fornecedores envolvidos poderão precisar:

* investigar;
* bloquear;
* restaurar;
* rotacionar;
* fornecer logs.

---

# 108. LGPD e Comunicação de Incidentes

Incidentes relacionados a dados pessoais deverão ser avaliados conforme o GSF-14.

Este documento não deverá definir isoladamente obrigações legais específicas sem análise de conformidade.

---

# 109. Confidencialidade Durante o Incidente

Detalhes do incidente poderão ser Confidenciais.

Especialmente:

* vulnerabilidade;
* exploit;
* secrets;
* dados;
* evidências;
* credenciais.

---

# 110. Registro de Decisões

Decisões relevantes deverão ser documentadas.

Exemplo:

```text
Por que endpoint foi desligado?

Por que backup X foi escolhido?

Por que usuários foram suspensos?

Por que incidente foi reclassificado?
```

---

# 111. Responsabilidades

A resposta deverá possuir responsabilidades claras.

---

# 112. Engenharia

Responsável por:

* diagnóstico;
* correção;
* análise técnica;
* testes;
* deploy;
* investigação técnica.

---

# 113. Operações

Responsável por:

* infraestrutura;
* disponibilidade;
* acesso operacional;
* backups;
* recuperação;
* monitoramento.

---

# 114. Qualidade

Responsável por apoiar:

* validação;
* regressão;
* cenários afetados;
* confirmação da correção.

---

# 115. Segurança

A função de Segurança, quando formalizada, deverá coordenar controles, classificação e resposta junto à Engenharia.

Enquanto essa função estiver dentro da própria Engenharia, a responsabilidade continuará explicitamente atribuída à equipe.

---

# 116. Responsável pelo Incidente

O coordenador deverá:

* acompanhar;
* registrar;
* priorizar;
* comunicar;
* garantir encerramento.

---

# 117. Módulos Afetados

Cada módulo deverá apoiar investigação de regras específicas de negócio.

---

# 118. Incidentes de Autenticação

Exemplos:

* conta comprometida;
* sessão roubada;
* bypass;
* recuperação indevida.

Deverão utilizar também o GAF.

---

# 119. Incidentes de Autorização

Exemplos:

```text
Usuário comum acessa operação administrativa
```

```text
Usuário altera permissão própria
```

---

# 120. Incidentes Multi-Tenant

São considerados especialmente graves.

Exemplo:

```text
Igreja A
→ recebeu dados da Igreja B
```

O incidente deverá determinar se ocorreu por:

* query;
* cache;
* relatório;
* API;
* task;
* export;
* arquivo.

---

# 121. Incidentes Financeiros

Deverão preservar:

* registros;
* auditoria;
* valores;
* operações;
* identidade;
* tenant.

Correções deverão evitar duplicidade financeira.

---

# 122. Incidentes de Secretaria

Podem envolver exposição de grande volume de dados pessoais.

---

# 123. Incidentes de Comunicação

Podem incluir:

* envio ao destinatário incorreto;
* envio em massa não autorizado;
* vazamento de contatos;
* credencial de integração comprometida.

---

# 124. Incidentes de API

Deverão considerar:

* credenciais;
* endpoints;
* logs;
* tenant;
* rate limiting;
* recursos acessados.

---

# 125. Incidentes de Integração

Podem exigir:

```text
Desativar integração
+
Rotacionar credencial
+
Validar dados enviados
```

---

# 126. Incidentes de Infraestrutura

Deverão ser tratados junto ao GSF-09 e GSF-11.

---

# 127. Incidentes de Backup

Exemplos:

* backup corrompido;
* backup exposto;
* rotina não executada;
* restauração impossível.

---

# 128. Incidentes de Dados

Incluem:

* exposição;
* alteração;
* perda;
* corrupção;
* exclusão.

---

# 129. Incidentes de Secrets

Secret exposto deverá ser considerado potencialmente comprometido.

---

# 130. Incidentes no Django Admin

Acesso indevido ao Django Admin possui risco elevado.

Deverão ser revisadas:

* ações;
* alterações;
* usuários;
* permissões;
* configurações.

---

# 131. Incidentes em Tasks e Automações

Tasks podem causar grande impacto em pouco tempo.

Exemplo:

```text
Automação com tenant incorreto
        ↓
processa dados de várias igrejas
```

Contenção deverá considerar fila, retries e execuções pendentes.

---

# 132. Incidentes no Portal Público

Podem envolver:

* abuso;
* spam;
* XSS;
* exposição;
* indisponibilidade;
* exploração de endpoint público.

---

# 133. Abuso Interno

Usuário legitimamente autorizado pode utilizar seu acesso de maneira indevida.

O princípio do menor privilégio e auditoria deverão permitir limitação e investigação.

---

# 134. Erro Humano

Nem todo incidente possui atacante.

Exemplos:

* exclusão acidental;
* configuração incorreta;
* envio ao destinatário errado;
* secret publicado por engano.

O processo formal ainda poderá ser necessário.

---

# 135. Falso Positivo

Nem todo alerta será incidente.

Quando descartado, o motivo deverá ser documentado quando relevante.

---

# 136. Encerramento

Um incidente não deverá ser encerrado somente porque a operação voltou ao normal.

---

# 137. Critérios de Encerramento

Antes de encerrar, verificar:

```text
Contenção concluída?

Causa identificada?

Correção aplicada?

Recuperação validada?

Impacto conhecido?

Evidências preservadas?

Ações futuras registradas?
```

---

# 138. Relatório Pós-Incidente

Incidentes relevantes deverão possuir relatório pós-incidente.

Estrutura sugerida:

```text
Resumo

Impacto

Linha do tempo

Causa

Contenção

Correção

Recuperação

Dados afetados

Tenants afetados

Lições aprendidas

Ações futuras
```

---

# 139. Post-Mortem

O post-mortem deverá buscar aprendizado.

Seu objetivo não deverá ser encontrar culpados.

Deverá identificar:

* falhas técnicas;
* falhas de processo;
* falhas de monitoramento;
* falhas de documentação;
* falhas de controle.

---

# 140. Lições Aprendidas

Toda ocorrência relevante deverá melhorar a plataforma.

Perguntas:

```text
Como detectar antes?

Como impedir novamente?

Que teste faltou?

Que alerta faltou?

Que padrão precisa mudar?

Que documentação precisa mudar?
```

---

# 141. Ações Corretivas

Ações corretivas tratam a causa identificada.

---

# 142. Ações Preventivas

Ações preventivas reduzem probabilidade de recorrência em outros pontos.

Exemplo:

```text
Falha de tenant em uma view
        ↓
criar selector seguro reutilizável
        ↓
revisar views equivalentes
```

---

# 143. Débitos de Segurança

Ações que não puderem ser executadas imediatamente deverão ser registradas como dívida de segurança.

---

# 144. Atualização da Documentação

Incidentes poderão exigir atualização de:

* GSF;
* arquitetura;
* backend;
* governança;
* runbooks;
* operação.

---

# 145. Atualização de Testes

Toda vulnerabilidade corrigida durante incidente deverá, quando apropriado, produzir teste de regressão.

---

# 146. Atualização de Monitoramento

Se o incidente não foi detectado adequadamente, o monitoramento deverá ser revisado.

---

# 147. Atualização de Runbooks

Procedimentos operacionais deverão refletir as lições aprendidas.

---

# 148. Recorrência

Incidentes repetidos indicam falha no tratamento da causa.

Recorrência deverá elevar prioridade da melhoria estrutural.

---

# 149. Simulações

A equipe deverá avaliar simulações periódicas de incidentes relevantes.

---

# 150. Exercícios de Incidente

Cenários possíveis:

```text
Secret exposto

Banco indisponível

Conta administrativa comprometida

Falha multi-tenant

Integração comprometida

Backup não restaura
```

O objetivo é validar preparação e runbooks.

---

# 151. Evidências Arquiteturais

## EA-GSF-INC-001

O GSF estabelece processo formal de Detecção, Classificação, Contenção, Correção, Recuperação e Lições Aprendidas.

## EA-GSF-INC-002

O GSF estabelece monitoramento e auditoria como fontes fundamentais de detecção e investigação.

## EA-GSF-INC-003

O GSF-10 estabelece logging, monitoramento e auditoria como mecanismos de rastreabilidade.

## EA-GSF-INC-004

O GSF-11 estabelece backup, continuidade e recuperação para restauração após falhas.

## EA-GSF-INC-005

O GSF-12 estabelece gestão de vulnerabilidades, incluindo a transição de vulnerabilidade explorada para incidente.

## EA-GSF-INC-006

O GereIgreja possui arquitetura multi-tenant, tornando incidentes de isolamento especialmente críticos.

## EA-GSF-INC-007

O GereIgreja possui módulos Financeiro, Secretaria e Comunicação que processam dados Confidenciais ou operações de alto impacto.

## EA-GSF-INC-008

O projeto possui integrações, automações, tasks e cron jobs que poderão participar de incidentes ou processos de recuperação.

## EA-GSF-INC-009

O GSF estabelece proteção de dados pessoais, financeiros e ministeriais.

## EA-GSF-INC-010

O projeto possui documentação de LGPD que deverá ser considerada na avaliação de incidentes relacionados a dados pessoais.

---

# 152. Especificações Oficiais

## GSF-INC-001

Todo incidente relevante deverá possuir processo formal de resposta.

## GSF-INC-002

Incidentes deverão ser registrados e classificados.

## GSF-INC-003

Todo incidente formal deverá possuir responsável.

## GSF-INC-004

A contenção deverá ter prioridade sobre a restauração normal quando houver exploração ativa.

## GSF-INC-005

Evidências relevantes deverão ser preservadas sempre que isso não impedir contenção urgente.

## GSF-INC-006

Logs relevantes deverão ser preservados durante investigação.

## GSF-INC-007

Incidentes deverão possuir linha do tempo quando relevantes.

## GSF-INC-008

A investigação deverá buscar causa raiz, não apenas o sintoma.

## GSF-INC-009

O escopo do incidente deverá considerar todos os tenants potencialmente afetados.

## GSF-INC-010

Quebra confirmada de isolamento multi-tenant deverá receber prioridade elevada.

## GSF-INC-011

Incidentes envolvendo dados Confidenciais deverão receber tratamento reforçado.

## GSF-INC-012

Secrets expostos deverão ser revogados ou rotacionados conforme aplicável.

## GSF-INC-013

Contas comprometidas deverão possuir sessões e acessos avaliados para revogação.

## GSF-INC-014

Vulnerabilidades exploradas deverão ser registradas também no processo de gestão de vulnerabilidades.

## GSF-INC-015

Correções críticas deverão possuir validação antes do encerramento.

## GSF-INC-016

Recuperação deverá seguir o GSF-11 quando envolver restauração.

## GSF-INC-017

Backups comprometidos não deverão ser utilizados sem validação.

## GSF-INC-018

Secrets comprometidos não deverão ser restaurados como credenciais válidas.

## GSF-INC-019

O retorno à produção deverá ocorrer somente após validação mínima de segurança e funcionamento.

## GSF-INC-020

Monitoramento reforçado deverá ser avaliado após incidentes relevantes.

## GSF-INC-021

Comunicação externa deverá ser coordenada e baseada em fatos.

## GSF-INC-022

Incidentes envolvendo dados pessoais deverão ser avaliados conforme o GSF-14.

## GSF-INC-023

Detalhes exploráveis de incidentes ativos deverão possuir acesso restrito.

## GSF-INC-024

Decisões relevantes tomadas durante o incidente deverão ser registradas.

## GSF-INC-025

Incidentes financeiros deverão preservar evidências suficientes para reconstrução das operações.

## GSF-INC-026

Tasks e automações comprometidas deverão ter execuções pendentes e retries avaliados.

## GSF-INC-027

Incidentes relevantes deverão possuir relatório pós-incidente.

## GSF-INC-028

Lições aprendidas deverão gerar ações corretivas ou preventivas quando necessárias.

## GSF-INC-029

Correções deverão produzir testes de regressão quando tecnicamente apropriado.

## GSF-INC-030

Documentação e runbooks deverão ser atualizados quando o incidente revelar lacunas.

## GSF-INC-031

Recorrência deverá provocar reavaliação da causa raiz.

## GSF-INC-032

A resposta deverá preservar privacidade e minimização de dados.

## GSF-INC-033

Incidentes não deverão ser encerrados somente porque o serviço voltou a funcionar.

## GSF-INC-034

Falsos positivos relevantes deverão possuir justificativa de encerramento.

## GSF-INC-035

O processo de resposta deverá evoluir continuamente.

---

# 153. Anti-Padrões

São considerados anti-padrões:

```text
Sistema voltou
=
incidente encerrado
```

---

```text
Há suspeita de secret exposto
=
esperar confirmar uso
antes de rotacionar
```

---

```text
Usuário viu dados
de outra igreja
=
erro visual simples
```

sem investigação.

---

```text
Corrigir primeiro
apagando todos os logs
```

---

```text
Restaurar backup
antes de conter
o atacante
```

---

```text
Conta comprometida
+
trocar senha
=
problema resolvido
```

sem revisar sessões e ações.

---

```text
Falha multi-tenant
encontrada em uma view
=
corrigir somente aquela URL
```

sem procurar ocorrências equivalentes.

---

```text
Incidente financeiro
=
editar manualmente os dados
sem preservar evidência
```

---

```text
Payload malicioso
=
copiar integralmente
para documento público
```

---

```text
Toda pessoa da equipe
recebe todos os detalhes
do incidente
```

sem necessidade.

---

```text
Hotfix crítico
=
sem code review
sem teste
sem registro
```

---

```text
Serviço voltou
=
backup não precisa ser validado
```

---

```text
Erro foi humano
=
não é incidente de segurança
```

---

```text
Nenhum cliente reclamou
=
ninguém foi afetado
```

---

```text
Vulnerabilidade corrigida
=
não precisamos investigar
se foi explorada
```

---

# 154. Checklist

## Detecção

* [ ] evento identificado;
* [ ] fonte registrada;
* [ ] horário registrado;
* [ ] exploração ativa avaliada.

## Registro

* [ ] ID;
* [ ] título;
* [ ] descrição;
* [ ] responsável;
* [ ] severidade;
* [ ] status.

## Escopo

* [ ] serviços afetados;
* [ ] tenants afetados;
* [ ] usuários afetados;
* [ ] dados afetados;
* [ ] período;
* [ ] integrações afetadas.

## Classificação

* [ ] confidencialidade;
* [ ] integridade;
* [ ] disponibilidade;
* [ ] autenticação;
* [ ] autorização;
* [ ] multi-tenant;
* [ ] dados pessoais;
* [ ] financeiro;
* [ ] secrets.

## Contenção

* [ ] endpoint bloqueado quando necessário;
* [ ] conta suspensa quando necessário;
* [ ] sessões revogadas quando necessário;
* [ ] tokens revogados;
* [ ] secrets rotacionados;
* [ ] integração isolada;
* [ ] tasks interrompidas quando necessário.

## Evidências

* [ ] logs preservados;
* [ ] auditoria preservada;
* [ ] configurações registradas;
* [ ] arquivos preservados;
* [ ] linha do tempo;
* [ ] correlação disponível.

## Investigação

* [ ] vetor identificado;
* [ ] causa raiz;
* [ ] primeiro evento estimado;
* [ ] exploração confirmada ou descartada;
* [ ] persistência avaliada;
* [ ] outros recursos revisados.

## Multi-Tenant

* [ ] tenant origem;
* [ ] tenant destino;
* [ ] registros acessados;
* [ ] relatórios;
* [ ] exports;
* [ ] APIs;
* [ ] cache;
* [ ] tasks.

## Dados

* [ ] classificação;
* [ ] volume;
* [ ] pessoas;
* [ ] tenants;
* [ ] exposição;
* [ ] alteração;
* [ ] perda.

## Correção

* [ ] vulnerabilidade registrada;
* [ ] hotfix quando necessário;
* [ ] dependência atualizada;
* [ ] permissão corrigida;
* [ ] tenant corrigido;
* [ ] configuração corrigida;
* [ ] credentials rotacionadas.

## Recuperação

* [ ] comprometimento contido;
* [ ] backup validado quando usado;
* [ ] restauração concluída;
* [ ] aplicação validada;
* [ ] permissões validadas;
* [ ] tenant validado;
* [ ] financeiro validado;
* [ ] integrações validadas.

## Comunicação

* [ ] equipe informada;
* [ ] responsáveis definidos;
* [ ] organização afetada avaliada;
* [ ] fornecedor avaliado;
* [ ] LGPD avaliada;
* [ ] comunicação externa coordenada.

## Encerramento

* [ ] impacto compreendido;
* [ ] causa conhecida;
* [ ] correção validada;
* [ ] monitoramento reforçado avaliado;
* [ ] post-mortem realizado quando necessário;
* [ ] ações futuras registradas;
* [ ] testes atualizados;
* [ ] documentação atualizada.

---

# 155. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework
* GDF — GereIgreja Documentation Framework
* GOC — GereIgreja Operations Center

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-02 — Classificação e Proteção da Informação
* GSF-03 — Gestão de Identidade
* GSF-04 — Autorização e Controle de Acesso
* GSF-05 — Segurança Multi-Tenant
* GSF-06 — Segurança da Aplicação
* GSF-07 — Segurança das APIs
* GSF-08 — Segurança de Dados e Privacidade
* GSF-09 — Segurança de Infraestrutura e Segredos
* GSF-10 — Logging, Monitoramento e Auditoria
* GSF-11 — Backup, Continuidade e Recuperação
* GSF-12 — Gestão de Vulnerabilidades
* GSF-14 — Conformidade e LGPD
* GSF-15 — Secure Development Lifecycle
* GSF-16 — Governança de Segurança

## Arquitetura

* GEA-07 — Arquitetura da Segurança
* GEA-08 — Arquitetura Multi-Tenant

## Backend

* Permissions
* Middlewares
* Tasks
* Logging
* Exceptions
* Testing

## Governança

* Padrões de Permissões
* Padrões de Segurança
* Padrões de Testes
* Checklist de Release
* Auditoria 360 do GereIgreja

## Deploy e Operações

* documentação existente em `docs/deploy/`
* documentação existente em `docs/operacoes/`
* documentação de backups
* documentação de cron jobs
* documentação de releases
* documentação de incidentes e auditorias quando existentes

---

# 156. Princípios Finais

O GereIgreja deverá tratar incidentes com rapidez, mas não com improvisação.

A sequência deverá permanecer:

```text
Detectar
   ↓
Entender
   ↓
Conter
   ↓
Preservar
   ↓
Investigar
   ↓
Corrigir
   ↓
Recuperar
   ↓
Validar
   ↓
Aprender
```

A prioridade inicial deverá ser impedir que o impacto continue.

Entretanto, velocidade não deverá destruir as evidências necessárias para compreender o que aconteceu.

Incidentes multi-tenant deverão possuir atenção especial.

Incidentes financeiros deverão preservar integridade e rastreabilidade.

Incidentes de dados deverão considerar privacidade e LGPD.

Incidentes de secrets deverão provocar revogação e rotação.

Incidentes de infraestrutura deverão considerar continuidade.

Incidentes causados por erro humano deverão gerar aprendizado da mesma forma que incidentes provocados por agentes externos.

O princípio operacional é:

```text
Restaurar o serviço
não basta.

É preciso restaurar
a confiança no serviço.
```

Essa confiança somente poderá ser restabelecida quando:

```text
A exploração foi interrompida

A causa foi compreendida

A correção foi validada

O impacto foi determinado

As evidências foram preservadas

A recorrência foi reduzida
```

Todo incidente relevante deverá tornar o GereIgreja mais preparado para o próximo.

---

# 157. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`13-Gestao-de-Incidentes-de-Seguranca.md`

**Documento**

`GSF-13`

**Código**

`GSF-SECURITY-INCIDENT-MANAGEMENT`

**Framework**

`GSF — GereIgreja Security Framework`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

**Próximo documento**

`14-Conformidade-e-LGPD.md`

**Código do próximo documento**

`GSF-14`

```
```
