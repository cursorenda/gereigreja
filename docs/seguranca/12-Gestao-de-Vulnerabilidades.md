Pasta:

docs/seguranca/

Arquivo:

12-Gestao-de-Vulnerabilidades.md

Documento:

GSF-12

Código:

GSF-VULNERABILITY-MANAGEMENT

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

# GSF-12 — Gestão de Vulnerabilidades

> "Vulnerabilidades fazem parte da evolução de qualquer plataforma. O risco não está apenas em sua existência, mas em não identificá-las, não classificá-las e não corrigi-las de maneira controlada."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação com o GSF
5. Princípios
6. O que é uma Vulnerabilidade
7. Vulnerabilidade, Ameaça e Risco
8. Superfície de Ataque
9. Ciclo de Gestão de Vulnerabilidades
10. Inventário
11. Código da Aplicação
12. Dependências Python
13. Dependências Frontend
14. Django
15. Banco de Dados
16. Sistema Operacional
17. Containers e Runtime
18. Infraestrutura
19. Serviços Externos
20. Integrações
21. APIs
22. Autenticação
23. Autorização
24. Multi-Tenant
25. Configurações
26. Secrets
27. Arquivos e Uploads
28. Tasks e Automações
29. Dependências Transitivas
30. Fontes de Vulnerabilidades
31. Revisão de Código
32. Testes
33. Scanners
34. Advisories
35. Atualizações de Segurança
36. Relatórios Internos
37. Incidentes
38. Usuários e Equipe
39. Triagem
40. Validação
41. Falso Positivo
42. Classificação de Severidade
43. Critérios de Severidade
44. Criticidade do Ativo
45. Exploração
46. Exposição
47. Impacto
48. Dados Afetados
49. Multi-Tenant como Agravante
50. Autenticação como Agravante
51. Financeiro como Agravante
52. Severidade Crítica
53. Severidade Alta
54. Severidade Média
55. Severidade Baixa
56. Priorização
57. Correção
58. Mitigação
59. Aceitação de Risco
60. Compensação de Controle
61. Atualização de Dependências
62. Atualização do Django
63. Atualização do Python
64. Atualização de Bibliotecas Frontend
65. Breaking Changes
66. Testes após Correção
67. Regressão
68. Deploy da Correção
69. Correção Emergencial
70. Hotfix de Segurança
71. Rollback
72. Validação Pós-Deploy
73. Evidências
74. Registro de Vulnerabilidades
75. Identificador
76. Descrição
77. Componente Afetado
78. Versão Afetada
79. Severidade
80. Status
81. Responsável
82. Prazo
83. Correção Aplicada
84. Histórico
85. SLA de Correção
86. Vulnerabilidades Críticas
87. Vulnerabilidades Altas
88. Vulnerabilidades Médias
89. Vulnerabilidades Baixas
90. Exceções de Prazo
91. Vulnerabilidades Conhecidas
92. Vulnerabilidades sem Correção Disponível
93. Zero-Day
94. Dependência Abandonada
95. Vulnerabilidade em Serviço Externo
96. Vulnerabilidade em Integração
97. Vulnerabilidade em Código Próprio
98. Vulnerabilidade de Configuração
99. Vulnerabilidade de Autorização
100. Vulnerabilidade Multi-Tenant
101. Vulnerabilidade de Dados
102. Vulnerabilidade de Infraestrutura
103. OWASP
104. CWE
105. CVE
106. CVSS
107. Secure Development Lifecycle
108. Desenvolvimento
109. Pull Requests
110. Code Review
111. CI/CD
112. Testes de Segurança
113. Release
114. Produção
115. Monitoramento
116. Logging
117. Incidentes
118. Divulgação Responsável
119. Confidencialidade
120. Comunicação
121. Terceiros
122. Auditoria
123. Revisões Periódicas
124. Métricas
125. Indicadores
126. Dívida de Segurança
127. Exceções
128. Evidências Arquiteturais
129. Especificações Oficiais
130. Anti-Padrões
131. Checklist
132. Documentos Relacionados
133. Princípios Finais
134. Status do Documento

---

# 1. Objetivo

Este documento estabelece o processo oficial de Gestão de Vulnerabilidades do GereIgreja.

Seu objetivo é garantir que vulnerabilidades sejam:

- identificadas;
- registradas;
- analisadas;
- classificadas;
- priorizadas;
- corrigidas;
- mitigadas quando necessário;
- testadas;
- acompanhadas até seu encerramento.

A gestão de vulnerabilidades deverá fazer parte do ciclo normal de Engenharia.

Segurança não deverá depender exclusivamente da descoberta de problemas após a publicação em produção.

---

# 2. Escopo

Este documento aplica-se a:

- código Python;
- Django;
- templates;
- JavaScript;
- HTMX;
- Alpine.js;
- CSS quando possuir implicações de segurança;
- APIs;
- banco de dados;
- dependências;
- bibliotecas;
- configurações;
- infraestrutura;
- deploy;
- integrações;
- tasks;
- cron jobs;
- automações;
- serviços externos utilizados pela plataforma;
- autenticação;
- autorização;
- arquitetura multi-tenant;
- tratamento de dados.

Também se aplica a todos os módulos funcionais do GereIgreja.

---

# 3. Papel deste Documento

O GSF-12 especializa o requisito de gestão contínua de vulnerabilidades estabelecido pelo GereIgreja Security Framework.

Sua posição é:

```text
GSF-09
Infraestrutura e Segredos
        ↓
GSF-10
Logging, Monitoramento e Auditoria
        ↓
GSF-11
Backup, Continuidade e Recuperação
        ↓
GSF-12
Gestão de Vulnerabilidades
        ↓
GSF-13
Gestão de Incidentes
        ↓
GSF-15
Secure Development Lifecycle
````

O GSF-12 atua principalmente antes que uma vulnerabilidade se transforme em incidente.

---

# 4. Relação com o GSF

O GereIgreja Security Framework determina que a plataforma seja revisada periodicamente.

Os principais itens definidos pelo framework incluem:

* dependências;
* bibliotecas;
* configurações;
* permissões;
* infraestrutura.

O GSF também estabelece:

```text
Correções críticas
deverão possuir
prioridade máxima.
```

Este documento detalha como essa diretriz deverá ser aplicada.

---

# 5. Princípios

A gestão de vulnerabilidades deverá seguir:

* prevenção;
* identificação contínua;
* priorização baseada em risco;
* correção rápida;
* rastreabilidade;
* validação;
* menor privilégio;
* defesa em profundidade;
* melhoria contínua.

O objetivo não é afirmar que a plataforma nunca possuirá vulnerabilidades.

O objetivo é possuir capacidade consistente para encontrá-las e tratá-las.

---

# 6. O que é uma Vulnerabilidade

Vulnerabilidade é uma fraqueza que pode comprometer:

* confidencialidade;
* integridade;
* disponibilidade;
* autenticação;
* autorização;
* isolamento;
* rastreabilidade.

Pode existir em:

```text
Código
Configuração
Dependência
Infraestrutura
Processo
Integração
Arquitetura
```

---

# 7. Vulnerabilidade, Ameaça e Risco

Os conceitos não deverão ser confundidos.

```text
Vulnerabilidade
    ↓
Fraqueza existente

Ameaça
    ↓
Algo capaz de explorar a fraqueza

Risco
    ↓
Probabilidade + impacto
da exploração
```

Uma vulnerabilidade deverá ser priorizada considerando o contexto real do GereIgreja.

---

# 8. Superfície de Ataque

A superfície de ataque representa os pontos pelos quais a plataforma pode ser atacada ou utilizada de maneira indevida.

Inclui:

* páginas públicas;
* autenticação;
* APIs;
* formulários;
* uploads;
* integrações;
* webhooks;
* Admin;
* infraestrutura;
* serviços externos;
* endpoints internos acessíveis;
* operações administrativas.

Reduzir superfície de ataque reduz oportunidades de exploração.

---

# 9. Ciclo de Gestão de Vulnerabilidades

O processo oficial deverá seguir:

```text
Descoberta
    ↓
Registro
    ↓
Validação
    ↓
Classificação
    ↓
Priorização
    ↓
Correção ou Mitigação
    ↓
Testes
    ↓
Deploy
    ↓
Validação
    ↓
Encerramento
```

Vulnerabilidades não deverão simplesmente desaparecer de uma lista sem evidência de tratamento.

---

# 10. Inventário

Não é possível proteger adequadamente componentes desconhecidos.

A Engenharia deverá conhecer, conforme aplicável:

* aplicações;
* frameworks;
* bibliotecas;
* runtimes;
* serviços;
* integrações;
* bancos;
* componentes de infraestrutura.

---

# 11. Código da Aplicação

Código próprio deverá ser analisado quanto a falhas como:

* autorização incorreta;
* ausência de filtro por tenant;
* validação insuficiente;
* exposição de dados;
* manipulação insegura de arquivos;
* tratamento inadequado de entrada;
* uso inseguro de APIs.

---

# 12. Dependências Python

Dependências Python deverão ser acompanhadas quanto a vulnerabilidades conhecidas.

O projeto deverá manter suas dependências identificáveis e versionadas de forma compatível com sua estratégia de build.

---

# 13. Dependências Frontend

Bibliotecas JavaScript e outros pacotes frontend deverão ser avaliados quando utilizados.

Dependências adicionadas somente por conveniência deverão ser evitadas.

Cada dependência aumenta:

```text
Código de terceiros
+
Superfície de manutenção
+
Possibilidade de vulnerabilidade
```

---

# 14. Django

Atualizações de segurança do Django deverão receber atenção prioritária.

A atualização deverá considerar:

* versão suportada;
* compatibilidade;
* migrations;
* dependências;
* regressões.

---

# 15. Banco de Dados

O banco deverá ser avaliado quanto a:

* versão;
* configuração;
* acesso;
* exposição;
* permissões;
* atualizações relevantes.

---

# 16. Sistema Operacional

Quando a Engenharia for responsável pela camada operacional correspondente, atualizações de segurança deverão fazer parte da gestão de vulnerabilidades.

Em serviços gerenciados, deverá ser compreendida a responsabilidade do provedor.

---

# 17. Containers e Runtime

Quando utilizados, imagens, runtimes e componentes de execução deverão ser mantidos atualizados e controlados.

Imagens obsoletas não deverão permanecer indefinidamente apenas porque continuam funcionando.

---

# 18. Infraestrutura

A infraestrutura deverá ser revisada quanto a:

* serviços expostos;
* portas;
* TLS;
* firewall;
* permissões;
* secrets;
* configurações;
* componentes obsoletos.

---

# 19. Serviços Externos

O GereIgreja depende de serviços externos em determinadas funcionalidades.

Problemas de segurança nesses serviços deverão ser avaliados conforme impacto na plataforma.

---

# 20. Integrações

Integrações deverão ser avaliadas quanto a:

* autenticação;
* autorização;
* validação;
* secrets;
* endpoints;
* webhooks;
* payloads;
* dependências externas.

---

# 21. APIs

As APIs deverão seguir os controles definidos pelo GSF-07.

Vulnerabilidades comuns incluem:

* ausência de autorização;
* IDOR;
* exposição excessiva de dados;
* validação insuficiente;
* rate limiting inadequado;
* falhas de autenticação.

---

# 22. Autenticação

Vulnerabilidades de autenticação deverão ser tratadas com prioridade compatível com seu impacto.

Exemplos:

* bypass de login;
* recuperação insegura;
* sessão inadequada;
* credencial exposta;
* ausência de revogação.

---

# 23. Autorização

Falhas de autorização possuem elevada relevância para o GereIgreja.

Exemplo:

```text
Usuário autenticado
        ↓
não possui permissão
        ↓
consegue executar operação
```

Autenticação bem implementada não corrige autorização incorreta.

---

# 24. Multi-Tenant

Falhas de isolamento entre organizações deverão receber prioridade elevada.

Exemplo:

```text
Igreja A
   ↓
acessa
   ↓
dados da Igreja B
```

Esse cenário deverá ser tratado como vulnerabilidade grave e poderá constituir incidente de segurança.

---

# 25. Configurações

Configurações inseguras também são vulnerabilidades.

Exemplos:

* `DEBUG` inadequado;
* permissões excessivas;
* endpoint exposto;
* CORS incorreto;
* configuração insegura de cookies;
* TLS inadequado.

---

# 26. Secrets

Secrets expostos deverão ser tratados imediatamente.

A correção não consiste apenas em remover o secret do local indevido.

Fluxo esperado:

```text
Detectar exposição
      ↓
Revogar ou rotacionar
      ↓
Remover exposição
      ↓
Investigar uso
      ↓
Corrigir causa
```

---

# 27. Arquivos e Uploads

Uploads deverão ser avaliados quanto a:

* extensão;
* conteúdo;
* tamanho;
* armazenamento;
* acesso;
* execução;
* associação ao tenant.

---

# 28. Tasks e Automações

Tasks podem introduzir vulnerabilidades quando:

* ignoram tenant;
* utilizam permissões excessivas;
* expõem secrets;
* processam entrada insegura;
* executam ações duplicadas.

---

# 29. Dependências Transitivas

Uma biblioteca utilizada pelo projeto pode depender de outras bibliotecas vulneráveis.

Por isso, a análise não deverá considerar apenas dependências declaradas diretamente.

---

# 30. Fontes de Vulnerabilidades

Vulnerabilidades poderão ser identificadas por:

* desenvolvimento;
* code review;
* testes;
* scanners;
* advisories;
* monitoramento;
* auditoria;
* incidentes;
* pesquisadores;
* fornecedores;
* comunidade.

---

# 31. Revisão de Código

Code review deverá observar também aspectos de segurança.

Perguntas úteis:

```text
Existe autorização?

Existe filtro por tenant?

A entrada é validada?

Há exposição de dado?

Existe secret?

A operação crítica é auditável?
```

---

# 32. Testes

Testes deverão proteger controles importantes contra regressões.

Especialmente:

* autorização;
* multi-tenant;
* autenticação;
* APIs;
* dados sensíveis.

---

# 33. Scanners

Ferramentas automatizadas poderão ser utilizadas para detectar:

* dependências vulneráveis;
* configurações;
* padrões inseguros;
* secrets expostos.

Scanners são apoio.

Não substituem análise humana.

---

# 34. Advisories

A Engenharia deverá acompanhar advisories relevantes para tecnologias utilizadas.

Especial atenção a:

* Python;
* Django;
* banco de dados;
* bibliotecas críticas;
* infraestrutura utilizada.

---

# 35. Atualizações de Segurança

Atualizações explicitamente classificadas como segurança deverão ser avaliadas com prioridade.

---

# 36. Relatórios Internos

Membros da equipe poderão identificar vulnerabilidades durante:

* desenvolvimento;
* testes;
* operação;
* suporte;
* auditoria.

O problema deverá ser registrado e encaminhado.

---

# 37. Incidentes

Um incidente pode revelar uma vulnerabilidade ainda desconhecida.

Nesse caso:

```text
Incidente
   ↓
identifica vulnerabilidade
   ↓
vulnerabilidade é corrigida
   ↓
controle é melhorado
```

---

# 38. Usuários e Equipe

Relatos de comportamento inesperado não deverão ser descartados automaticamente.

Um erro aparentemente funcional poderá revelar problema de segurança.

---

# 39. Triagem

Toda vulnerabilidade reportada deverá passar por triagem.

A triagem deverá determinar:

* validade;
* componente;
* impacto;
* exposição;
* prioridade;
* responsável.

---

# 40. Validação

Antes de classificar definitivamente uma vulnerabilidade, a Engenharia deverá reproduzi-la ou obter evidência suficiente quando possível.

A reprodução deverá ocorrer de maneira segura.

---

# 41. Falso Positivo

Ferramentas automatizadas podem produzir falsos positivos.

Um alerta deverá ser analisado antes de ser descartado.

O descarte deverá possuir justificativa quando relevante.

---

# 42. Classificação de Severidade

O GereIgreja deverá classificar vulnerabilidades conforme risco real.

Modelo:

```text
CRÍTICA
ALTA
MÉDIA
BAIXA
```

A classificação não deverá depender exclusivamente de uma pontuação automática.

---

# 43. Critérios de Severidade

Avaliar:

* facilidade de exploração;
* autenticação necessária;
* privilégios necessários;
* exposição;
* impacto;
* dados envolvidos;
* quantidade de tenants;
* disponibilidade;
* integridade;
* possibilidade de persistência.

---

# 44. Criticidade do Ativo

Uma mesma falha pode possuir severidade diferente conforme o componente afetado.

Exemplo:

```text
Falha em página informativa

≠

Falha na autorização financeira
```

---

# 45. Exploração

Deverá ser avaliado se a exploração:

* é teórica;
* exige condições especiais;
* é simples;
* possui exploit conhecido;
* está sendo explorada ativamente.

---

# 46. Exposição

Componentes públicos tendem a possuir maior exposição.

Entretanto, componentes internos com privilégios elevados também podem representar alto risco.

---

# 47. Impacto

Avaliar impacto sobre:

```text
Confidencialidade
Integridade
Disponibilidade
Rastreabilidade
Isolamento
```

---

# 48. Dados Afetados

A classificação deverá considerar o tipo de informação envolvida.

Dados:

* públicos;
* internos;
* restritos;
* confidenciais;

possuem impactos diferentes.

---

# 49. Multi-Tenant como Agravante

Vulnerabilidade que permita cruzar limites de tenant deverá receber atenção especial.

O isolamento organizacional é controle estrutural do GereIgreja.

---

# 50. Autenticação como Agravante

Bypass de autenticação ou comprometimento amplo de contas poderá elevar significativamente a severidade.

---

# 51. Financeiro como Agravante

Falhas capazes de alterar movimentações financeiras sem autorização adequada deverão receber prioridade elevada.

---

# 52. Severidade Crítica

Uma vulnerabilidade poderá ser considerada Crítica quando permitir, conforme o contexto:

* comprometimento amplo;
* acesso administrativo indevido;
* acesso entre tenants em grande escala;
* execução remota grave;
* exposição massiva de dados confidenciais;
* alteração financeira ampla;
* comprometimento de secrets centrais.

Correções críticas possuem prioridade máxima conforme o GSF.

---

# 53. Severidade Alta

Pode envolver:

* bypass relevante de autorização;
* exposição significativa de dados;
* alteração indevida de recursos críticos;
* comprometimento limitado, mas relevante;
* exploração com impacto elevado.

---

# 54. Severidade Média

Pode envolver falha com:

* impacto limitado;
* pré-condições significativas;
* baixa exposição;
* controle compensatório existente.

Ainda deverá ser corrigida.

---

# 55. Severidade Baixa

Pode incluir:

* exposição de baixo impacto;
* hardening;
* informação técnica limitada;
* configuração com risco reduzido.

Baixa severidade não significa "não corrigir".

---

# 56. Priorização

A ordem de correção deverá considerar:

```text
Severidade
+
Exploração
+
Exposição
+
Criticidade
+
Dados
+
Capacidade de mitigação
```

---

# 57. Correção

A correção deverá eliminar a causa da vulnerabilidade quando possível.

Exemplo:

```text
Falha:
objeto carregado apenas por ID

Correção:
objeto carregado por
tenant + ID
```

A correção deverá ser feita na camada apropriada.

---

# 58. Mitigação

Quando correção definitiva não puder ser aplicada imediatamente, poderá existir mitigação.

Exemplos:

* desabilitar funcionalidade;
* restringir acesso;
* bloquear endpoint;
* alterar configuração;
* revogar credencial.

Mitigação não deverá ser confundida com encerramento definitivo.

---

# 59. Aceitação de Risco

Risco poderá ser aceito somente quando houver justificativa formal e responsável adequado.

Não deverá existir:

```text
Não vamos corrigir
porque parece difícil.
```

como aceitação válida.

---

# 60. Compensação de Controle

Um controle compensatório poderá reduzir temporariamente o risco.

Exemplo:

```text
Falha existente
+
acesso temporariamente bloqueado
```

A vulnerabilidade continuará registrada até tratamento adequado.

---

# 61. Atualização de Dependências

Dependências vulneráveis deverão ser atualizadas quando existir versão corrigida compatível.

---

# 62. Atualização do Django

Atualizações de segurança do Django deverão receber prioridade.

Antes do deploy:

* revisar release;
* testar aplicação;
* testar autenticação;
* testar autorização;
* testar módulos críticos.

---

# 63. Atualização do Python

Versões de Python fora de suporte deverão ser evitadas.

Mudanças de versão deverão seguir processo de compatibilidade e testes.

---

# 64. Atualização de Bibliotecas Frontend

Dependências frontend deverão ser atualizadas quando necessário.

Não atualizar cegamente sem avaliar compatibilidade.

---

# 65. Breaking Changes

Correções de segurança podem exigir alterações incompatíveis.

Segurança não deverá ser ignorada apenas para evitar trabalho de migração.

O impacto deverá ser planejado.

---

# 66. Testes após Correção

Toda correção deverá possuir validação.

Fluxo:

```text
Reproduzir falha
      ↓
Aplicar correção
      ↓
Confirmar que falha não ocorre
      ↓
Executar regressão
```

---

# 67. Regressão

Quando adequado, deverá ser criado teste automatizado que impeça retorno da vulnerabilidade.

Isso é especialmente importante para:

* tenant;
* autorização;
* autenticação;
* validação;
* APIs.

---

# 68. Deploy da Correção

A correção deverá seguir o processo de deploy compatível com sua severidade.

---

# 69. Correção Emergencial

Vulnerabilidade crítica poderá exigir fluxo acelerado.

A aceleração não deverá eliminar:

* revisão mínima;
* testes essenciais;
* registro;
* validação pós-deploy.

---

# 70. Hotfix de Segurança

Hotfix deverá ser:

* pequeno;
* focado;
* rastreável;
* testado;
* revisado.

Mudanças não relacionadas deverão ser evitadas no mesmo hotfix.

---

# 71. Rollback

Toda correção crítica deverá avaliar possibilidade de rollback.

Entretanto, rollback que reintroduza vulnerabilidade conhecida deverá ser analisado cuidadosamente.

---

# 72. Validação Pós-Deploy

Após publicação, confirmar:

* correção ativa;
* aplicação funcional;
* logs;
* erros;
* regressões;
* comportamento de segurança.

---

# 73. Evidências

O encerramento deverá possuir evidência suficiente.

Pode incluir:

* commit;
* pull request;
* teste;
* versão;
* deploy;
* validação.

---

# 74. Registro de Vulnerabilidades

Vulnerabilidades relevantes deverão possuir registro estruturado.

Modelo conceitual:

```text
ID
Título
Origem
Componente
Descrição
Severidade
Status
Responsável
Prazo
Mitigação
Correção
Evidência
```

---

# 75. Identificador

Cada vulnerabilidade interna deverá possuir identificador quando o processo formal exigir.

Exemplo conceitual:

```text
VULN-2026-001
```

O padrão definitivo poderá ser estabelecido pela governança.

---

# 76. Descrição

A descrição deverá explicar a falha de forma suficiente para correção sem expor detalhes desnecessários a pessoas não autorizadas.

---

# 77. Componente Afetado

Identificar:

* módulo;
* serviço;
* endpoint;
* dependência;
* infraestrutura.

---

# 78. Versão Afetada

Quando aplicável, registrar versões afetadas.

---

# 79. Severidade

Registrar classificação vigente.

Se novas evidências surgirem, a severidade poderá ser reavaliada.

---

# 80. Status

Estados conceituais:

```text
IDENTIFICADA
EM_TRIAGEM
CONFIRMADA
EM_CORRECAO
MITIGADA
CORRIGIDA
VALIDADA
ENCERRADA
```

A nomenclatura final deverá ser padronizada antes da implementação em ferramenta.

---

# 81. Responsável

Toda vulnerabilidade confirmada deverá possuir responsável pelo acompanhamento.

---

# 82. Prazo

O prazo deverá refletir severidade e risco.

---

# 83. Correção Aplicada

Registrar resumidamente o tratamento realizado.

---

# 84. Histórico

Mudanças relevantes de:

* severidade;
* status;
* responsável;
* mitigação;
* prazo;

deverão permanecer rastreáveis quando o processo formal estiver implantado.

---

# 85. SLA de Correção

A plataforma deverá possuir metas de tratamento por severidade.

Os valores exatos deverão ser definidos pela Engenharia e Operações conforme capacidade real.

Não deverão ser inventados prazos apenas para parecer aderente a uma política.

---

# 86. Vulnerabilidades Críticas

Deverão possuir prioridade máxima.

A resposta deverá começar imediatamente após confirmação quando houver risco ativo relevante.

---

# 87. Vulnerabilidades Altas

Deverão possuir prioridade elevada e prazo reduzido.

---

# 88. Vulnerabilidades Médias

Deverão entrar no planejamento de correção dentro do ciclo adequado.

---

# 89. Vulnerabilidades Baixas

Deverão ser acompanhadas para evitar acúmulo indefinido de dívida de segurança.

---

# 90. Exceções de Prazo

Quando uma correção não puder ocorrer no prazo definido, deverá existir:

* justificativa;
* risco;
* mitigação;
* responsável;
* nova previsão.

---

# 91. Vulnerabilidades Conhecidas

Não deverá existir dependência vulnerável conhecida mantida indefinidamente sem análise.

---

# 92. Vulnerabilidades sem Correção Disponível

Quando não houver patch:

```text
Avaliar exposição
      ↓
Mitigar
      ↓
Monitorar
      ↓
Acompanhar fornecedor
      ↓
Atualizar quando disponível
```

---

# 93. Zero-Day

Vulnerabilidade sem correção disponível e com risco elevado poderá exigir:

* desativação;
* isolamento;
* bloqueio;
* monitoramento reforçado;
* controle compensatório.

---

# 94. Dependência Abandonada

Dependências sem manutenção representam risco crescente.

A Engenharia deverá avaliar substituição quando:

* não recebem correções;
* acumulam vulnerabilidades;
* impedem atualização da plataforma.

---

# 95. Vulnerabilidade em Serviço Externo

Quando o problema estiver em provedor externo:

* avaliar impacto;
* acompanhar fornecedor;
* aplicar mitigação;
* restringir integração quando necessário.

---

# 96. Vulnerabilidade em Integração

Integração comprometida poderá exigir:

* desativação;
* revogação de token;
* rotação de secret;
* bloqueio de webhook;
* investigação.

---

# 97. Vulnerabilidade em Código Próprio

Código próprio deverá ser corrigido pela Engenharia seguindo o processo definido neste documento.

---

# 98. Vulnerabilidade de Configuração

Nem toda correção exige alteração de código.

Pode exigir:

* variável;
* header;
* permissão;
* firewall;
* configuração Django;
* configuração de serviço.

---

# 99. Vulnerabilidade de Autorização

Falhas de autorização deverão ser corrigidas preferencialmente em controles centralizados.

Evitar correções locais inconsistentes.

A implementação deverá respeitar o GAF e o GSF-04.

---

# 100. Vulnerabilidade Multi-Tenant

Falha multi-tenant deverá avaliar imediatamente:

```text
Houve somente possibilidade?

Houve acesso real?

Quais tenants?

Quais dados?

Por quanto tempo?

Existem logs?
```

Se houver evidência de exploração ou exposição, o GSF-13 deverá ser acionado.

---

# 101. Vulnerabilidade de Dados

Falhas que exponham dados deverão considerar:

* classificação;
* quantidade;
* tenants;
* pessoas afetadas;
* logs;
* requisitos de conformidade.

---

# 102. Vulnerabilidade de Infraestrutura

Falhas de infraestrutura deverão ser tratadas conforme responsabilidade definida no GSF-09.

---

# 103. OWASP

As categorias e recomendações da OWASP deverão ser utilizadas como referência técnica.

O GereIgreja deverá considerar especialmente riscos relacionados a:

* controle de acesso;
* autenticação;
* injeção;
* configuração;
* componentes vulneráveis;
* logging;
* integridade;
* SSRF e riscos equivalentes quando aplicáveis.

O OWASP não substitui análise específica da arquitetura GereIgreja.

---

# 104. CWE

CWE poderá ser utilizado para classificar tipos de fraquezas.

Seu uso é recomendado quando auxiliar comunicação técnica e rastreabilidade.

---

# 105. CVE

CVE identifica vulnerabilidades publicamente conhecidas em componentes.

Quando uma dependência utilizada possuir CVE relevante, deverá ser analisado:

```text
Usamos o componente?

Usamos a versão afetada?

O caminho vulnerável é aplicável?

Qual o impacto?
```

---

# 106. CVSS

CVSS poderá auxiliar na classificação técnica.

Entretanto:

```text
CVSS
≠
Risco final do GereIgreja
```

O contexto da plataforma deverá ser considerado.

---

# 107. Secure Development Lifecycle

Gestão de vulnerabilidades deverá integrar-se ao Secure Development Lifecycle definido pelo GSF-15.

O objetivo é deslocar segurança para todo o ciclo de desenvolvimento.

---

# 108. Desenvolvimento

Durante desenvolvimento, vulnerabilidades identificadas deverão ser corrigidas antes de publicação quando possível.

---

# 109. Pull Requests

Pull Requests deverão permitir revisão de alterações sensíveis.

Mudanças envolvendo:

* autenticação;
* autorização;
* tenant;
* dados;
* secrets;
* integrações;

merecem atenção adicional.

---

# 110. Code Review

Revisores deverão verificar riscos além da funcionalidade.

Pergunta central:

```text
Funciona?

+

Funciona com segurança?
```

---

# 111. CI/CD

A evolução da plataforma poderá incluir verificações automatizadas no pipeline.

Exemplos:

* análise de dependências;
* testes;
* detecção de secrets;
* verificações de segurança.

A adoção deverá corresponder às ferramentas realmente implantadas.

---

# 112. Testes de Segurança

Testes deverão existir especialmente para controles críticos.

Exemplo:

```python
def test_usuario_nao_acessa_objeto_de_outro_tenant():
    ...
```

O teste deverá verificar o comportamento real da arquitetura.

---

# 113. Release

Antes de releases relevantes, vulnerabilidades conhecidas de alta criticidade deverão ser avaliadas.

---

# 114. Produção

Produção deverá possuir monitoramento suficiente para detectar sinais de exploração quando tecnicamente possível.

---

# 115. Monitoramento

O GSF-10 deverá apoiar a identificação de comportamentos relacionados a vulnerabilidades.

---

# 116. Logging

Logs poderão ajudar a identificar:

* exploração;
* enumeração;
* falhas repetidas;
* acessos negados;
* comportamento inesperado.

Logs não deverão conter payloads sensíveis apenas para facilitar investigação.

---

# 117. Incidentes

Quando uma vulnerabilidade for explorada, a gestão deixa de ser somente preventiva.

Fluxo:

```text
Vulnerabilidade
      ↓
Exploração
      ↓
Incidente
      ↓
GSF-13
```

A correção da vulnerabilidade continuará sendo necessária durante ou após a resposta ao incidente.

---

# 118. Divulgação Responsável

Relatos externos de vulnerabilidades deverão ser tratados de maneira profissional.

A equipe deverá:

* receber;
* preservar evidências;
* validar;
* classificar;
* corrigir;
* responder adequadamente quando aplicável.

---

# 119. Confidencialidade

Detalhes de vulnerabilidades não corrigidas deverão possuir acesso restrito conforme necessidade.

---

# 120. Comunicação

Comunicação sobre vulnerabilidade deverá considerar:

* severidade;
* público;
* risco de exploração;
* necessidade operacional;
* conformidade.

Não divulgar detalhes exploráveis desnecessariamente antes da correção.

---

# 121. Terceiros

Quando terceiros participarem da operação ou desenvolvimento, vulnerabilidades relevantes deverão seguir o mesmo processo de rastreabilidade.

---

# 122. Auditoria

O processo de gestão deverá permitir verificar:

```text
O que foi identificado?

Quando?

Qual severidade?

Quem tratou?

Como foi corrigido?

Foi validado?
```

---

# 123. Revisões Periódicas

A plataforma deverá realizar revisões periódicas conforme determinado pelo GSF.

Áreas mínimas:

* dependências;
* bibliotecas;
* configurações;
* permissões;
* infraestrutura.

Também deverão ser considerados:

* APIs;
* tenant;
* autenticação;
* secrets.

---

# 124. Métricas

A Engenharia poderá acompanhar métricas como:

* vulnerabilidades abertas;
* vulnerabilidades por severidade;
* tempo de correção;
* vulnerabilidades recorrentes;
* dependências desatualizadas.

Métricas deverão auxiliar decisão e não estimular fechamento artificial de registros.

---

# 125. Indicadores

Indicadores úteis poderão incluir:

```text
Críticas abertas
Altas abertas
Tempo médio de correção
Itens vencidos
Recorrência
```

---

# 126. Dívida de Segurança

Vulnerabilidades adiadas acumulam dívida de segurança.

Essa dívida deverá ser visível.

Não deverá ser escondida dentro de backlog genérico sem classificação.

---

# 127. Exceções

Exceções de segurança deverão possuir:

* justificativa;
* responsável;
* risco;
* mitigação;
* prazo de revisão.

Exceção permanente deverá ser evitada.

---

# 128. Evidências Arquiteturais

## EA-GSF-VULN-001

O GSF estabelece revisão periódica de dependências, bibliotecas, configurações, permissões e infraestrutura.

## EA-GSF-VULN-002

O GSF estabelece prioridade máxima para correções críticas.

## EA-GSF-VULN-003

O GereIgreja utiliza Django como base da aplicação e deverá acompanhar atualizações de segurança do framework.

## EA-GSF-VULN-004

O GereIgreja possui arquitetura multi-tenant, tornando falhas de isolamento especialmente relevantes.

## EA-GSF-VULN-005

O GereIgreja possui framework próprio de autenticação e autorização, tornando esses controles parte essencial da análise de vulnerabilidades.

## EA-GSF-VULN-006

O projeto possui APIs, integrações, tasks e automações que ampliam a superfície de ataque e deverão fazer parte das revisões.

## EA-GSF-VULN-007

O backend possui documentação de Testing, Logging, Exceptions e Performance que apoia validação e diagnóstico.

## EA-GSF-VULN-008

O GSF-09 estabelece controles de infraestrutura e secrets relacionados diretamente à gestão de vulnerabilidades.

## EA-GSF-VULN-009

O GSF-10 estabelece logging, monitoramento e auditoria necessários para identificar sinais de exploração.

## EA-GSF-VULN-010

O GSF-11 estabelece continuidade e recuperação necessárias quando uma vulnerabilidade provocar impacto operacional.

---

# 129. Especificações Oficiais

## GSF-VULN-001

A plataforma deverá possuir processo contínuo de gestão de vulnerabilidades.

## GSF-VULN-002

Dependências deverão ser revisadas periodicamente.

## GSF-VULN-003

Bibliotecas deverão ser revisadas quanto a vulnerabilidades conhecidas.

## GSF-VULN-004

Configurações de segurança deverão ser revisadas periodicamente.

## GSF-VULN-005

Permissões deverão fazer parte das revisões de segurança.

## GSF-VULN-006

Infraestrutura deverá fazer parte das revisões de segurança.

## GSF-VULN-007

Vulnerabilidades confirmadas deverão possuir classificação de severidade.

## GSF-VULN-008

A classificação deverá considerar o contexto real do GereIgreja.

## GSF-VULN-009

CVSS poderá auxiliar, mas não deverá determinar sozinho o risco final.

## GSF-VULN-010

Correções críticas deverão possuir prioridade máxima.

## GSF-VULN-011

Falhas de isolamento multi-tenant deverão receber prioridade elevada.

## GSF-VULN-012

Falhas relevantes de autorização deverão receber prioridade elevada.

## GSF-VULN-013

Exposição de secrets deverá provocar revogação ou rotação quando aplicável.

## GSF-VULN-014

Remover um secret exposto do código não deverá ser considerado suficiente sem avaliar comprometimento.

## GSF-VULN-015

Vulnerabilidades deverão possuir responsável pelo acompanhamento.

## GSF-VULN-016

Correções deverão ser testadas antes do encerramento.

## GSF-VULN-017

Correções de segurança deverão possuir validação pós-deploy quando aplicável.

## GSF-VULN-018

Regressões de segurança deverão receber testes automatizados quando adequado.

## GSF-VULN-019

Mitigações temporárias não deverão encerrar automaticamente a vulnerabilidade.

## GSF-VULN-020

Aceitação de risco deverá possuir justificativa.

## GSF-VULN-021

Exceções deverão possuir revisão futura.

## GSF-VULN-022

Dependências abandonadas deverão ser avaliadas para substituição.

## GSF-VULN-023

Vulnerabilidades sem patch deverão possuir mitigação quando possível.

## GSF-VULN-024

Vulnerabilidades exploradas deverão acionar o processo de gestão de incidentes.

## GSF-VULN-025

Detalhes de vulnerabilidades não corrigidas deverão possuir acesso restrito.

## GSF-VULN-026

Code review deverá considerar segurança.

## GSF-VULN-027

Mudanças envolvendo autenticação, autorização e tenant deverão receber atenção adicional em revisão.

## GSF-VULN-028

Scanners não deverão substituir análise humana.

## GSF-VULN-029

Alertas automatizados não deverão ser descartados sem análise adequada.

## GSF-VULN-030

Falsos positivos relevantes deverão possuir justificativa de descarte.

## GSF-VULN-031

Hotfixes de segurança deverão ser pequenos, focados e rastreáveis.

## GSF-VULN-032

O processo deverá preservar evidências de correção e validação.

## GSF-VULN-033

Vulnerabilidades conhecidas não deverão permanecer indefinidamente sem decisão explícita.

## GSF-VULN-034

Dívida de segurança deverá permanecer visível.

## GSF-VULN-035

Revisões periódicas deverão acompanhar a evolução tecnológica da plataforma.

---

# 130. Anti-Padrões

São considerados anti-padrões:

```text
Scanner não encontrou nada
=
não existem vulnerabilidades
```

---

```text
CVSS baixo
=
ignorar automaticamente
```

---

```text
CVSS crítico
=
impacto crítico automaticamente
```

sem avaliar o contexto.

---

```text
Dependência funciona
=
não precisa atualizar
```

---

```text
Versão antiga
+
sem manutenção
+
sem vulnerabilidade conhecida hoje
=
segura para sempre
```

---

```text
Secret apareceu no Git
        ↓
apagar do arquivo
        ↓
problema resolvido
```

sem rotação.

---

```text
Falha multi-tenant
=
bug funcional comum
```

---

```text
Usuário precisa estar autenticado
=
falha de autorização não é grave
```

---

```text
Mitigação temporária
=
vulnerabilidade encerrada
```

---

```text
Correção aplicada
=
não precisa testar
```

---

```text
Hotfix crítico
=
pular todos os testes
```

---

```text
Vulnerabilidade sem patch
=
não há nada a fazer
```

---

```text
Dependência vulnerável
=
esperar próxima grande atualização
```

sem avaliar mitigação.

---

```text
Falso positivo
=
fechar sem justificativa
```

---

```text
Problema de segurança
escondido em backlog genérico
sem severidade
```

---

```text
Vulnerabilidade explorada
=
corrigir código
e não investigar incidente
```

---

# 131. Checklist

## Inventário

* [ ] Python identificado;
* [ ] Django identificado;
* [ ] dependências Python identificadas;
* [ ] dependências frontend identificadas;
* [ ] banco identificado;
* [ ] infraestrutura identificada;
* [ ] integrações identificadas;
* [ ] serviços externos relevantes identificados.

## Descoberta

* [ ] advisories acompanhados;
* [ ] dependências revisadas;
* [ ] code review;
* [ ] testes;
* [ ] scanners avaliados;
* [ ] relatos internos tratados.

## Triagem

* [ ] vulnerabilidade validada;
* [ ] falso positivo avaliado;
* [ ] componente identificado;
* [ ] versão identificada quando aplicável;
* [ ] impacto analisado;
* [ ] exposição analisada.

## Severidade

* [ ] confidencialidade;
* [ ] integridade;
* [ ] disponibilidade;
* [ ] autenticação;
* [ ] autorização;
* [ ] tenant;
* [ ] dados;
* [ ] financeiro;
* [ ] exploração conhecida.

## Registro

* [ ] identificador;
* [ ] descrição;
* [ ] componente;
* [ ] severidade;
* [ ] status;
* [ ] responsável;
* [ ] prazo;
* [ ] mitigação;
* [ ] evidência.

## Correção

* [ ] causa identificada;
* [ ] correção aplicada;
* [ ] mitigação quando necessária;
* [ ] dependência atualizada quando aplicável;
* [ ] secret rotacionado quando necessário.

## Testes

* [ ] vulnerabilidade reproduzida quando possível;
* [ ] correção validada;
* [ ] regressão executada;
* [ ] teste automatizado avaliado;
* [ ] tenant testado;
* [ ] autorização testada.

## Deploy

* [ ] release preparada;
* [ ] rollback avaliado;
* [ ] deploy realizado;
* [ ] logs verificados;
* [ ] correção confirmada em ambiente aplicável.

## Críticas

* [ ] prioridade máxima;
* [ ] responsável imediato;
* [ ] exploração avaliada;
* [ ] mitigação imediata avaliada;
* [ ] incidente avaliado;
* [ ] comunicação adequada.

## Dependências

* [ ] vulnerabilidades conhecidas verificadas;
* [ ] dependências transitivas consideradas;
* [ ] versões abandonadas avaliadas;
* [ ] atualizações de segurança priorizadas.

## Secrets

* [ ] exposição investigada;
* [ ] secret revogado;
* [ ] secret rotacionado;
* [ ] origem da exposição corrigida;
* [ ] logs avaliados quando necessário.

## Multi-Tenant

* [ ] possibilidade de acesso cruzado avaliada;
* [ ] tenants afetados identificados;
* [ ] dados afetados identificados;
* [ ] logs analisados;
* [ ] incidente acionado quando aplicável.

## Encerramento

* [ ] correção comprovada;
* [ ] evidência registrada;
* [ ] status atualizado;
* [ ] mitigação temporária removida quando aplicável;
* [ ] lição incorporada;
* [ ] documentação atualizada quando necessária.

---

# 132. Documentos Relacionados

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
* GSF-13 — Gestão de Incidentes de Segurança
* GSF-14 — Conformidade e LGPD
* GSF-15 — Secure Development Lifecycle

## Backend

* Componentes relacionados a dependências
* APIs
* Tasks
* Logging
* Exceptions
* Testing
* Performance

## Governança

* Padrões de Segurança
* Padrões de Permissões
* Padrões de Testes
* Checklist de Release
* Auditoria 360 do GereIgreja

## Deploy e Operações

* documentação existente em `docs/deploy/`
* documentação existente em `docs/operacoes/`
* documentação de release
* documentação de infraestrutura
* documentação de monitoramento

---

# 133. Princípios Finais

Vulnerabilidades não deverão ser tratadas como eventos excepcionais que só aparecem quando algo dá errado.

Elas fazem parte do ciclo de evolução de software.

O GereIgreja deverá possuir capacidade permanente de:

```text
Descobrir
    ↓
Entender
    ↓
Classificar
    ↓
Priorizar
    ↓
Corrigir
    ↓
Testar
    ↓
Aprender
```

Uma plataforma segura não é aquela que afirma não possuir vulnerabilidades.

É aquela que consegue identificá-las e responder adequadamente quando surgem.

A gestão deverá evitar dois extremos:

```text
Ignorar todo risco
```

e:

```text
Tratar qualquer alerta
como emergência crítica
```

O tratamento deverá ser proporcional ao risco real.

Entretanto, determinados controles estruturais do GereIgreja exigem atenção especial:

```text
Autenticação
+
Autorização
+
Multi-Tenant
+
Dados Confidenciais
+
Financeiro
+
Secrets
```

Falhas nessas áreas deverão receber prioridade compatível com seu potencial de impacto.

Dependências deverão evoluir.

Frameworks deverão evoluir.

Infraestrutura deverá evoluir.

Controles deverão evoluir.

E cada vulnerabilidade encontrada deverá melhorar a capacidade da plataforma de evitar a próxima.

A regra final é:

```text
Vulnerabilidade conhecida
sem análise,
sem responsável
e sem plano
é risco aceito por omissão.
```

No GereIgreja, risco deverá ser tratado por decisão consciente, documentada e proporcional — nunca por esquecimento.

---

# 134. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`12-Gestao-de-Vulnerabilidades.md`

**Documento**

`GSF-12`

**Código**

`GSF-VULNERABILITY-MANAGEMENT`

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

`13-Gestao-de-Incidentes-de-Seguranca.md`

**Código do próximo documento**

`GSF-13`

```
```
