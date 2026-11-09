Pasta:

docs/seguranca/

Arquivo:

15-Secure-Development-Lifecycle.md

Documento:

GSF-15

Código:

GSF-SECURE-DEVELOPMENT-LIFECYCLE

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

# GSF-15 — Secure Development Lifecycle

> "Segurança não deve ser adicionada ao final do desenvolvimento. Ela deve acompanhar a funcionalidade desde o requisito até sua operação em produção."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação com o GSF
5. Princípios
6. O que é o Secure Development Lifecycle
7. Segurança no Ciclo de Desenvolvimento
8. Fluxo Oficial
9. Fase de Requisito
10. Requisitos Funcionais
11. Requisitos de Segurança
12. Classificação da Informação
13. Privacidade
14. Multi-Tenant
15. Autenticação
16. Autorização
17. Auditoria
18. Disponibilidade
19. Integrações
20. Criticidade da Funcionalidade
21. Fase de Arquitetura
22. Security by Design
23. Privacy by Design
24. Trust Boundaries
25. Superfície de Ataque
26. Fluxo de Dados
27. Modelagem de Ameaças
28. Ativos
29. Ameaças
30. Vetores de Ataque
31. Controles
32. Risco Residual
33. Decisões Arquiteturais
34. Fase de Design Técnico
35. Models
36. Managers e QuerySets
37. Services
38. Selectors
39. Views
40. Forms
41. Serializers
42. APIs
43. Templates
44. HTMX
45. Alpine.js
46. JavaScript
47. Tasks
48. Automações
49. Integrações Externas
50. Arquivos e Uploads
51. Relatórios
52. Exportações
53. Cache
54. Sessões
55. Fase de Implementação
56. Desenvolvimento Seguro
57. Django
58. Validação de Entrada
59. Validação de Saída
60. SQL Injection
61. XSS
62. CSRF
63. Mass Assignment
64. Path Traversal
65. Open Redirect
66. SSRF
67. Upload de Arquivos
68. Desserialização
69. Tratamento de Exceções
70. Informações Sensíveis
71. Secrets
72. Configuração
73. Dependências
74. Logging
75. Auditoria
76. Segurança Multi-Tenant no Código
77. Segurança de Autorização no Código
78. Segurança das APIs no Código
79. Segurança de Dados no Código
80. Code Review
81. Revisão Funcional
82. Revisão Arquitetural
83. Revisão de Segurança
84. Pull Requests
85. Critérios de Revisão
86. Mudanças de Alto Risco
87. Revisão de Permissões
88. Revisão Multi-Tenant
89. Revisão de Migrações
90. Revisão de Dependências
91. Revisão de Configuração
92. Fase de Testes
93. Estratégia de Testes
94. Testes Unitários
95. Testes de Integração
96. Testes de Autorização
97. Testes Multi-Tenant
98. Testes de APIs
99. Testes de Validação
100. Testes de Segurança
101. Testes de Regressão
102. Testes de Vulnerabilidades Corrigidas
103. Testes de Dados
104. Testes de Arquivos
105. Testes de Tasks
106. Testes de Integrações
107. Testes de Exportações
108. Testes de Auditoria
109. Dados de Teste
110. Ferramentas Automatizadas
111. Análise Estática
112. Dependências Vulneráveis
113. Secret Scanning
114. Linters
115. Pipelines
116. Quality Gates
117. Fase de Release
118. Checklist de Release
119. Migrações
120. Configurações de Produção
121. Variáveis de Ambiente
122. Secrets de Produção
123. DEBUG
124. HTTPS
125. Cookies
126. Hosts
127. CORS
128. CSRF
129. Permissões
130. Jobs e Cron
131. Assets
132. Dependências
133. Backup Antes do Release
134. Rollback
135. Aprovação
136. Deploy
137. Separação de Ambientes
138. Privilégios de Deploy
139. Rastreabilidade do Deploy
140. Validação Pós-Deploy
141. Smoke Tests
142. Monitoramento Pós-Deploy
143. Operação Segura
144. Logging em Produção
145. Monitoramento
146. Alertas
147. Auditoria
148. Gestão de Vulnerabilidades
149. Incidentes
150. Patching
151. Dependências em Produção
152. Mudanças Emergenciais
153. Hotfixes
154. Rollback de Segurança
155. Depreciação
156. Remoção de Funcionalidades
157. Remoção de Dados
158. Remoção de Secrets
159. Segurança por Tipo de Mudança
160. Novos Módulos
161. Novos Endpoints
162. Novos Models
163. Novos Campos
164. Novas Permissões
165. Novas Integrações
166. Novas Tasks
167. Novos Relatórios
168. Novas Exportações
169. Novos Uploads
170. Novas Dependências
171. Alterações de Infraestrutura
172. Alterações de Autenticação
173. Alterações Financeiras
174. Alterações Multi-Tenant
175. Alterações de Dados Pessoais
176. Definition of Ready
177. Definition of Done
178. Evidências do Desenvolvimento Seguro
179. Documentação
180. Responsabilidades
181. Engenharia
182. Revisores
183. Qualidade
184. Operações
185. Segurança
186. Produto
187. Exceções
188. Débitos de Segurança
189. Métricas
190. Melhoria Contínua
191. Evidências Arquiteturais
192. Especificações Oficiais
193. Anti-Padrões
194. Checklist
195. Documentos Relacionados
196. Princípios Finais
197. Status do Documento

---

# 1. Objetivo

Este documento estabelece o ciclo oficial de desenvolvimento seguro do GereIgreja.

Seu objetivo é garantir que segurança seja considerada durante todo o processo de criação, alteração, publicação e manutenção de software.

O Secure Development Lifecycle deverá integrar segurança às etapas de:

```text
Requisito
    ↓
Arquitetura
    ↓
Design
    ↓
Implementação
    ↓
Revisão
    ↓
Testes
    ↓
Release
    ↓
Deploy
    ↓
Operação
    ↓
Evolução
````

O objetivo não é criar uma etapa isolada chamada "segurança".

O objetivo é tornar segurança parte do processo normal de Engenharia.

---

# 2. Escopo

Este documento aplica-se a:

* backend Django;
* frontend;
* APIs;
* módulos;
* integrações;
* tasks;
* automações;
* relatórios;
* exportações;
* uploads;
* infraestrutura relacionada à aplicação;
* configurações;
* dependências;
* migrações;
* ferramentas internas.

Aplica-se a:

* novas funcionalidades;
* correções;
* refatorações;
* hotfixes;
* mudanças arquiteturais;
* atualizações de dependências;
* alterações operacionais.

---

# 3. Papel deste Documento

O GSF-15 transforma os controles definidos pelos documentos anteriores em processo de Engenharia.

```text
GSF-01 até GSF-14
        ↓
requisitos e controles
        ↓
GSF-15
Secure Development Lifecycle
        ↓
processo de desenvolvimento
        ↓
código
        ↓
testes
        ↓
release
        ↓
produção
```

O GSF-15 deverá evitar que segurança seja tratada apenas após a implementação.

---

# 4. Relação com o GSF

O GSF estabelece o princípio:

**Security by Design.**

O GSF-15 operacionaliza esse princípio.

Ele deverá utilizar controles definidos por:

* GSF-02 para classificação da informação;
* GSF-03 para identidade;
* GSF-04 para autorização;
* GSF-05 para multi-tenant;
* GSF-06 para segurança da aplicação;
* GSF-07 para APIs;
* GSF-08 para dados e privacidade;
* GSF-09 para infraestrutura e secrets;
* GSF-10 para logging, monitoramento e auditoria;
* GSF-11 para continuidade;
* GSF-12 para vulnerabilidades;
* GSF-13 para incidentes;
* GSF-14 para conformidade e LGPD.

---

# 5. Princípios

Todo desenvolvimento deverá observar:

* Security by Design;
* Privacy by Design;
* Privacy by Default;
* menor privilégio;
* defesa em profundidade;
* isolamento multi-tenant;
* validação explícita;
* rastreabilidade;
* revisão;
* testes;
* automação;
* simplicidade;
* melhoria contínua.

---

# 6. O que é o Secure Development Lifecycle

Secure Development Lifecycle, ou SDL, é o processo pelo qual controles de segurança são incorporados ao ciclo de desenvolvimento.

Não deverá ser interpretado como:

```text
Desenvolver tudo
      ↓
terminar
      ↓
perguntar se é seguro
```

O modelo correto é:

```text
Planejar com segurança
        ↓
Projetar com segurança
        ↓
Implementar com segurança
        ↓
Testar segurança
        ↓
Publicar com segurança
        ↓
Operar com segurança
```

---

# 7. Segurança no Ciclo de Desenvolvimento

Cada etapa deverá produzir perguntas específicas.

```text
Requisito
→ quais dados e riscos?

Arquitetura
→ quais limites e controles?

Implementação
→ os controles foram aplicados?

Testes
→ os controles realmente funcionam?

Release
→ a configuração está segura?

Produção
→ conseguimos detectar problemas?
```

---

# 8. Fluxo Oficial

O fluxo oficial será:

```text
Requisito
    │
    ▼
Classificação
    │
    ▼
Análise de Segurança
    │
    ▼
Arquitetura
    │
    ▼
Implementação
    │
    ▼
Code Review
    │
    ▼
Testes
    │
    ▼
Quality Gate
    │
    ▼
Release
    │
    ▼
Deploy
    │
    ▼
Validação
    │
    ▼
Monitoramento
```

Mudanças de maior risco deverão receber controles adicionais.

---

# 9. Fase de Requisito

Segurança começa antes do código.

Todo requisito relevante deverá permitir compreender:

* funcionalidade;
* atores;
* dados;
* permissões;
* tenant;
* integrações;
* impacto;
* auditoria.

---

# 10. Requisitos Funcionais

O requisito funcional deverá descrever o comportamento esperado.

Entretanto, comportamento funcional sem limites de segurança é incompleto.

Exemplo:

```text
"O usuário pode exportar membros."
```

deverá ser complementado por:

```text
Qual usuário?

De qual organização?

Quais campos?

Em qual formato?

A operação será auditada?
```

---

# 11. Requisitos de Segurança

Funcionalidades relevantes deverão possuir requisitos de segurança explícitos.

Exemplos:

```text
Somente usuários com permissão X.

Somente registros do tenant atual.

Operação deve gerar auditoria.

Arquivo deve expirar.

Endpoint exige autenticação.
```

---

# 12. Classificação da Informação

Os dados envolvidos deverão ser classificados conforme GSF-02.

Categorias:

* Pública;
* Interna;
* Restrita;
* Confidencial.

A classificação deverá influenciar os controles.

---

# 13. Privacidade

Quando existirem dados pessoais, o requisito deverá considerar GSF-14.

Perguntas:

```text
Qual finalidade?

Quais dados são necessários?

Existe exportação?

Existe compartilhamento?

Existe retenção?
```

---

# 14. Multi-Tenant

Toda funcionalidade que acesse dados organizacionais deverá definir explicitamente seu escopo de tenant.

Nunca assumir:

```text
Depois colocamos
o filtro da igreja.
```

O tenant é parte do requisito.

---

# 15. Autenticação

Deverá ser definido se a funcionalidade exige:

* usuário autenticado;
* sessão;
* API token;
* outro mecanismo aprovado.

---

# 16. Autorização

O requisito deverá identificar quem poderá executar cada ação.

Exemplo:

```text
Visualizar
Criar
Editar
Excluir
Exportar
Aprovar
Administrar
```

---

# 17. Auditoria

Operações relevantes deverão identificar necessidade de auditoria antes da implementação.

---

# 18. Disponibilidade

Funcionalidades críticas deverão avaliar impacto de indisponibilidade.

Isso poderá influenciar:

* arquitetura;
* retries;
* filas;
* backups;
* monitoramento.

---

# 19. Integrações

Toda integração deverá definir:

* sistema externo;
* dados enviados;
* dados recebidos;
* autenticação;
* secrets;
* falhas;
* retries;
* auditoria.

---

# 20. Criticidade da Funcionalidade

Mudanças deverão ser classificadas conforme risco.

Exemplo conceitual:

```text
BAIXO
MÉDIO
ALTO
CRÍTICO
```

Quanto maior o risco, maior deverá ser o nível de revisão e validação.

---

# 21. Fase de Arquitetura

A arquitetura deverá estabelecer os limites de confiança e os controles principais.

---

# 22. Security by Design

Controles deverão fazer parte da arquitetura.

Não deverão depender exclusivamente de desenvolvedores lembrarem de aplicá-los manualmente em cada ponto.

---

# 23. Privacy by Design

O fluxo de dados deverá considerar privacidade desde o projeto.

---

# 24. Trust Boundaries

Limites de confiança deverão ser identificados.

Exemplo:

```text
Internet
   │
   ▼
Aplicação
   │
   ▼
Services
   │
   ▼
Banco

Aplicação
   │
   └────► Serviço Externo
```

Toda transição representa um limite que deverá ser avaliado.

---

# 25. Superfície de Ataque

A superfície de ataque inclui pontos pelos quais dados ou comandos entram no sistema.

Exemplos:

* forms;
* APIs;
* uploads;
* webhooks;
* parâmetros de URL;
* integrações;
* Django Admin.

---

# 26. Fluxo de Dados

Funcionalidades relevantes deverão permitir compreender:

```text
Origem
   ↓
Entrada
   ↓
Validação
   ↓
Processamento
   ↓
Persistência
   ↓
Saída
```

---

# 27. Modelagem de Ameaças

Mudanças de maior risco deverão considerar modelagem de ameaças.

O processo poderá ser simples, desde que responda:

```text
O que estamos protegendo?

De quem?

Como poderia ser atacado?

Quais controles existem?

O que acontece se eles falharem?
```

---

# 28. Ativos

Ativos poderão incluir:

* dados;
* credenciais;
* dinheiro;
* arquivos;
* identidade;
* permissões;
* disponibilidade;
* reputação.

---

# 29. Ameaças

Exemplos:

* usuário malicioso;
* conta comprometida;
* atacante externo;
* integração comprometida;
* erro humano;
* falha de software.

---

# 30. Vetores de Ataque

Exemplos:

```text
Form
API
Upload
Webhook
Login
Export
Admin
Task
Integration
```

---

# 31. Controles

Para cada ameaça relevante deverão existir controles proporcionais.

Exemplo:

```text
Ameaça:
acesso entre tenants

Controles:
tenant obrigatório
+
selector seguro
+
permission
+
teste
+
auditoria
```

---

# 32. Risco Residual

Nem todo risco poderá ser eliminado.

Riscos residuais relevantes deverão ser conhecidos e documentados.

---

# 33. Decisões Arquiteturais

Decisões de segurança com impacto estrutural deverão ser documentadas conforme os padrões arquiteturais e de documentação do GereIgreja.

---

# 34. Fase de Design Técnico

O design deverá definir onde cada responsabilidade será implementada.

---

# 35. Models

Models deverão proteger invariantes próprias da entidade quando apropriado.

Não deverão substituir autorização da camada de aplicação.

---

# 36. Managers e QuerySets

Managers e QuerySets poderão centralizar filtros seguros quando compatíveis com a arquitetura.

Especial atenção deverá ser dada ao tenant.

---

# 37. Services

Services deverão concentrar regras de negócio e operações relevantes conforme os padrões de backend.

Autorização e tenant deverão estar claros na operação.

---

# 38. Selectors

Selectors deverão fornecer consultas reutilizáveis e seguras.

Exemplo conceitual:

```python
def get_membros_for_tenant(*, tenant, user):
    ...
```

é preferível a espalhar consultas inseguras por múltiplas views.

---

# 39. Views

Views deverão:

* validar autenticação;
* aplicar autorização;
* resolver tenant;
* validar entrada;
* chamar serviços apropriados.

---

# 40. Forms

Forms deverão validar entradas provenientes do usuário.

Validação de interface não substitui validação do servidor.

---

# 41. Serializers

Serializers deverão evitar:

* campos excessivos;
* escrita indevida;
* mass assignment;
* exposição de atributos internos.

---

# 42. APIs

APIs deverão seguir GSF-07.

Cada endpoint deverá definir:

```text
Authentication
Authorization
Tenant
Input
Output
Rate Limit
Audit
```

quando aplicável.

---

# 43. Templates

Templates deverão utilizar os mecanismos seguros do framework.

Escape automático não deverá ser desativado sem necessidade comprovada.

---

# 44. HTMX

Requisições HTMX continuam sendo requisições HTTP normais do ponto de vista de segurança.

Elas deverão aplicar:

* autenticação;
* autorização;
* CSRF;
* tenant;
* validação.

---

# 45. Alpine.js

Alpine.js deverá ser utilizado para comportamento de interface.

Decisões de segurança não deverão depender exclusivamente do estado do frontend.

---

# 46. JavaScript

JavaScript não deverá ser considerado barreira de autorização.

Exemplo inseguro:

```text
Botão escondido
=
usuário sem acesso
```

O backend deverá aplicar a autorização real.

---

# 47. Tasks

Tasks deverão receber contexto suficiente para operar com segurança.

Especialmente:

* tenant;
* usuário quando aplicável;
* IDs;
* idempotência;
* rastreabilidade.

---

# 48. Automações

Automações deverão possuir limites claros.

Uma automação não deverá atravessar tenants por erro de contexto.

---

# 49. Integrações Externas

Integrações deverão possuir camada de abstração apropriada e gestão segura de credenciais.

---

# 50. Arquivos e Uploads

O design deverá considerar:

* tamanho;
* extensão;
* tipo;
* nome;
* armazenamento;
* tenant;
* autorização;
* exposição.

---

# 51. Relatórios

Relatórios deverão aplicar permissões e tenant desde sua consulta de origem.

---

# 52. Exportações

Exportações deverão possuir controle reforçado porque transferem dados para fora do ambiente normal da aplicação.

---

# 53. Cache

Cache deverá considerar tenant e usuário quando o conteúdo depender desses contextos.

Uma chave de cache incorreta poderá produzir vazamento entre organizações.

---

# 54. Sessões

Sessões deverão seguir o GAF.

Dados sensíveis desnecessários não deverão ser armazenados na sessão.

---

# 55. Fase de Implementação

Durante a implementação, controles definidos no requisito e arquitetura deverão tornar-se código verificável.

---

# 56. Desenvolvimento Seguro

O desenvolvedor deverá preferir mecanismos nativos e consolidados do framework.

Código de segurança personalizado deverá existir somente quando necessário.

---

# 57. Django

O GereIgreja deverá aproveitar os mecanismos nativos do Django para:

* ORM;
* CSRF;
* escaping;
* autenticação;
* sessões;
* forms;
* validação;
* configurações de segurança.

---

# 58. Validação de Entrada

Toda entrada externa deverá ser considerada não confiável.

Exemplos:

* POST;
* GET;
* headers;
* JSON;
* arquivos;
* webhooks;
* dados externos.

---

# 59. Validação de Saída

A saída deverá ser adequada ao contexto.

Dados retornados deverão ser limitados ao necessário.

---

# 60. SQL Injection

Queries deverão utilizar ORM ou parametrização segura.

Não concatenar entrada do usuário em SQL.

---

# 61. XSS

Templates deverão preservar escaping.

Conteúdo HTML permitido deverá possuir tratamento específico e controlado.

---

# 62. CSRF

Operações mutáveis baseadas em sessão deverão utilizar proteção CSRF conforme mecanismos do Django.

---

# 63. Mass Assignment

Endpoints não deverão aceitar automaticamente qualquer campo enviado pelo cliente.

Campos editáveis deverão ser explicitamente controlados.

---

# 64. Path Traversal

Nomes ou caminhos fornecidos pelo usuário não deverão permitir acesso arbitrário ao filesystem.

---

# 65. Open Redirect

Destinos de redirecionamento controlados pelo usuário deverão ser validados.

---

# 66. SSRF

Funcionalidades que façam requisições para URLs fornecidas externamente deverão possuir controles específicos.

Não deverão permitir acesso arbitrário a recursos internos.

---

# 67. Upload de Arquivos

Uploads deverão validar:

* tamanho;
* extensão;
* tipo esperado;
* armazenamento;
* autorização;
* tenant.

O nome fornecido pelo usuário não deverá controlar diretamente caminhos internos.

---

# 68. Desserialização

Dados externos não deverão ser desserializados utilizando mecanismos inseguros capazes de executar código arbitrário.

---

# 69. Tratamento de Exceções

Erros deverão ser tratados sem expor detalhes internos desnecessários.

---

# 70. Informações Sensíveis

Não deverão aparecer em respostas ou mensagens de erro:

* secrets;
* senhas;
* tokens;
* connection strings;
* detalhes internos desnecessários.

---

# 71. Secrets

Secrets deverão seguir GSF-09.

Nunca deverão ser:

* hardcoded;
* commitados;
* registrados em logs;
* incluídos em fixtures públicas.

---

# 72. Configuração

Configurações inseguras não deverão ser utilizadas como solução temporária sem controle.

---

# 73. Dependências

Toda nova dependência deverá ser avaliada quanto a:

* necessidade;
* manutenção;
* segurança;
* compatibilidade;
* licença quando aplicável.

---

# 74. Logging

Logs deverão seguir GSF-10.

Eles deverão ajudar investigação sem criar vazamentos adicionais.

---

# 75. Auditoria

Eventos relevantes deverão produzir registros de auditoria conforme padrões da plataforma.

---

# 76. Segurança Multi-Tenant no Código

Consultas deverão aplicar o tenant correto.

Exemplo inseguro:

```python
membro = Membro.objects.get(pk=membro_id)
```

quando o recurso pertence a tenant.

Padrão conceitual seguro:

```python
membro = Membro.objects.get(
    pk=membro_id,
    tenant=tenant,
)
```

ou abstração equivalente definida pela arquitetura.

---

# 77. Segurança de Autorização no Código

Autenticação não deverá ser confundida com autorização.

```text
Está logado
≠
pode executar qualquer ação
```

---

# 78. Segurança das APIs no Código

Endpoints deverão validar:

* identidade;
* permissão;
* tenant;
* entrada;
* saída.

---

# 79. Segurança de Dados no Código

Dados Confidenciais deverão receber tratamento compatível com GSF-08 e GSF-14.

---

# 80. Code Review

Mudanças relevantes deverão passar por revisão antes da integração ao código principal.

---

# 81. Revisão Funcional

O revisor deverá confirmar se o código implementa corretamente o requisito.

---

# 82. Revisão Arquitetural

Mudanças estruturais deverão ser verificadas quanto à aderência aos padrões do GereIgreja.

---

# 83. Revisão de Segurança

A revisão deverá procurar, quando aplicável:

* falhas de autorização;
* falhas de tenant;
* validações ausentes;
* exposição de dados;
* secrets;
* logs inadequados;
* configurações inseguras.

---

# 84. Pull Requests

Pull Requests deverão possuir contexto suficiente para revisão.

Mudanças de segurança não deverão ser escondidas dentro de PRs excessivamente amplos sem justificativa.

---

# 85. Critérios de Revisão

O revisor deverá perguntar:

```text
Quem pode executar?

De qual tenant?

Quais dados entram?

Quais dados saem?

Existe auditoria?

Existe teste?

Existe risco de regressão?
```

---

# 86. Mudanças de Alto Risco

Exigem atenção reforçada:

* autenticação;
* autorização;
* multi-tenant;
* financeiro;
* dados pessoais;
* secrets;
* uploads;
* APIs públicas;
* integrações;
* infraestrutura.

---

# 87. Revisão de Permissões

Toda alteração de permissão deverá verificar:

* escopo;
* grupos;
* papéis;
* efeitos existentes;
* menor privilégio.

---

# 88. Revisão Multi-Tenant

Mudanças em queries deverão verificar risco de acesso entre organizações.

---

# 89. Revisão de Migrações

Migrações deverão ser avaliadas quanto a:

* integridade;
* perda de dados;
* downtime;
* rollback;
* dados pessoais;
* tenant.

---

# 90. Revisão de Dependências

Mudanças de dependências deverão avaliar riscos de segurança e compatibilidade.

---

# 91. Revisão de Configuração

Alterações em settings e infraestrutura deverão receber revisão proporcional ao risco.

---

# 92. Fase de Testes

Segurança deverá possuir testes verificáveis.

Não deverá depender somente de inspeção manual.

---

# 93. Estratégia de Testes

Os testes deverão combinar diferentes níveis.

```text
Unitários
   +
Integração
   +
Autorização
   +
Multi-Tenant
   +
Regressão
```

---

# 94. Testes Unitários

Deverão validar regras isoladas quando apropriado.

---

# 95. Testes de Integração

Deverão validar o comportamento entre componentes.

---

# 96. Testes de Autorização

Exemplo:

```python
def test_usuario_sem_permissao_nao_pode_excluir_membro():
    ...
```

---

# 97. Testes Multi-Tenant

Exemplo:

```python
def test_usuario_nao_acessa_membro_de_outro_tenant():
    ...
```

Esse tipo de teste deverá existir em funcionalidades de risco relevante.

---

# 98. Testes de APIs

Deverão incluir:

* sem autenticação;
* sem permissão;
* tenant incorreto;
* payload inválido;
* recurso inexistente;
* operação válida.

---

# 99. Testes de Validação

Entradas inválidas deverão ser testadas.

---

# 100. Testes de Segurança

Testes específicos deverão ser criados quando uma ameaça não estiver suficientemente coberta pelos testes funcionais.

---

# 101. Testes de Regressão

Falhas corrigidas deverão possuir teste que impeça retorno do problema quando tecnicamente apropriado.

---

# 102. Testes de Vulnerabilidades Corrigidas

Uma vulnerabilidade corrigida deverá preferencialmente gerar:

```text
Vulnerabilidade
      ↓
Correção
      ↓
Teste de regressão
```

---

# 103. Testes de Dados

Mudanças de dados deverão verificar integridade e isolamento.

---

# 104. Testes de Arquivos

Uploads deverão possuir testes para entradas inválidas e acesso indevido.

---

# 105. Testes de Tasks

Tasks deverão testar:

* tenant;
* retries;
* idempotência;
* falhas;
* efeitos duplicados.

---

# 106. Testes de Integrações

Integrações deverão testar:

* timeout;
* erro externo;
* credencial inválida;
* resposta inválida;
* retry;
* idempotência quando aplicável.

---

# 107. Testes de Exportações

Exportações deverão verificar:

* permissão;
* tenant;
* campos;
* dados de terceiros;
* formato.

---

# 108. Testes de Auditoria

Operações críticas deverão testar se os eventos esperados são registrados.

---

# 109. Dados de Teste

Testes deverão utilizar dados fictícios sempre que possível.

Dados reais de produção não deverão ser requisito para reproduzir cenários normais.

---

# 110. Ferramentas Automatizadas

Automação deverá complementar revisão humana.

---

# 111. Análise Estática

Ferramentas de análise estática poderão ser incorporadas ao pipeline para identificar padrões inseguros.

---

# 112. Dependências Vulneráveis

Dependências deverão ser verificadas periodicamente conforme GSF-12.

---

# 113. Secret Scanning

O repositório deverá possuir mecanismos para reduzir risco de secrets commitados quando a infraestrutura permitir.

---

# 114. Linters

Linters ajudam a manter consistência e identificar determinados problemas antes do merge.

---

# 115. Pipelines

Pipelines deverão executar verificações automáticas adequadas ao projeto.

Exemplo conceitual:

```text
Commit
   ↓
Lint
   ↓
Tests
   ↓
Security Checks
   ↓
Build
   ↓
Release
```

---

# 116. Quality Gates

Falhas críticas não deverão ser ignoradas apenas para concluir um release.

Exceções deverão possuir processo explícito.

---

# 117. Fase de Release

Antes do release, a versão deverá possuir nível de confiança compatível com seu risco.

---

# 118. Checklist de Release

O checklist oficial de release deverá incluir segurança.

---

# 119. Migrações

Migrações deverão ser revisadas antes da produção.

---

# 120. Configurações de Produção

Produção deverá utilizar configurações específicas e seguras.

---

# 121. Variáveis de Ambiente

Valores sensíveis ou específicos do ambiente deverão ser fornecidos por mecanismos apropriados.

---

# 122. Secrets de Produção

Secrets de produção não deverão existir no código-fonte.

---

# 123. DEBUG

Produção deverá operar com:

```python
DEBUG = False
```

salvo cenário excepcional formalmente controlado e temporário.

---

# 124. HTTPS

Produção deverá utilizar HTTPS.

---

# 125. Cookies

Cookies sensíveis deverão utilizar configurações adequadas de segurança conforme arquitetura e ambiente.

---

# 126. Hosts

Hosts permitidos deverão ser explicitamente configurados.

---

# 127. CORS

CORS deverá ser configurado de forma restritiva conforme necessidades reais.

---

# 128. CSRF

Configurações CSRF deverão permanecer compatíveis com a arquitetura de produção.

---

# 129. Permissões

Mudanças de permissões deverão ser verificadas antes do release.

---

# 130. Jobs e Cron

Novos jobs deverão possuir:

* contexto;
* logs;
* falhas;
* idempotência;
* tenant quando aplicável.

---

# 131. Assets

Assets não deverão conter informações sensíveis ou configurações secretas.

---

# 132. Dependências

Versões implantadas deverão ser rastreáveis.

---

# 133. Backup Antes do Release

Mudanças de alto impacto em dados deverão avaliar necessidade de backup ou ponto de recuperação antes da implantação.

---

# 134. Rollback

Mudanças relevantes deverão possuir estratégia de rollback quando tecnicamente possível.

---

# 135. Aprovação

Releases de alto risco poderão exigir aprovação adicional conforme governança.

---

# 136. Deploy

Deploy deverá ser processo controlado.

---

# 137. Separação de Ambientes

Desenvolvimento, homologação e produção deverão permanecer separados.

---

# 138. Privilégios de Deploy

Somente identidades autorizadas deverão executar deploys.

---

# 139. Rastreabilidade do Deploy

Deverá ser possível identificar:

* versão;
* momento;
* responsável ou processo;
* mudanças;
* resultado.

---

# 140. Validação Pós-Deploy

Após deploy relevante deverão ser executadas validações mínimas.

---

# 141. Smoke Tests

Smoke tests deverão verificar os fluxos essenciais da aplicação.

---

# 142. Monitoramento Pós-Deploy

Mudanças relevantes deverão receber observação após publicação.

---

# 143. Operação Segura

O SDL não termina no deploy.

Produção continua fazendo parte do ciclo de desenvolvimento seguro.

---

# 144. Logging em Produção

Logs deverão permitir diagnóstico sem expor secrets ou dados desnecessários.

---

# 145. Monitoramento

Serviços relevantes deverão possuir monitoramento conforme GSF-10.

---

# 146. Alertas

Falhas críticas deverão produzir alertas acionáveis quando tecnicamente aplicável.

---

# 147. Auditoria

Operações críticas deverão permanecer rastreáveis.

---

# 148. Gestão de Vulnerabilidades

Vulnerabilidades identificadas após o release deverão seguir GSF-12.

---

# 149. Incidentes

Exploração ou comprometimento deverá seguir GSF-13.

---

# 150. Patching

Correções de segurança deverão ser priorizadas conforme risco.

---

# 151. Dependências em Produção

Dependências utilizadas deverão continuar sendo acompanhadas após o release.

---

# 152. Mudanças Emergenciais

Emergência poderá reduzir etapas, mas não eliminar responsabilidade.

Toda mudança emergencial deverá possuir registro.

---

# 153. Hotfixes

Hotfixes de segurança deverão ser:

* pequenos quando possível;
* revisados;
* testados;
* rastreáveis;
* acompanhados após deploy.

---

# 154. Rollback de Segurança

Quando uma versão introduzir risco grave, rollback poderá ser a ação mais segura.

---

# 155. Depreciação

Funcionalidades antigas deverão ser avaliadas quanto ao custo e risco de manutenção.

---

# 156. Remoção de Funcionalidades

Código desativado não deverá permanecer indefinidamente acessível sem necessidade.

---

# 157. Remoção de Dados

Mudanças que removam dados deverão considerar GSF-14.

---

# 158. Remoção de Secrets

Secrets antigos deverão ser revogados quando deixarem de ser utilizados.

---

# 159. Segurança por Tipo de Mudança

Nem toda mudança exige os mesmos controles.

O nível de validação deverá ser proporcional ao risco.

---

# 160. Novos Módulos

Novos módulos deverão definir:

* dados;
* tenant;
* permissões;
* auditoria;
* APIs;
* integrações;
* criticidade.

---

# 161. Novos Endpoints

Todo novo endpoint deverá avaliar:

```text
Authentication
Authorization
Tenant
Input
Output
Audit
Rate Limit
```

quando aplicável.

---

# 162. Novos Models

Novos models deverão avaliar:

* tenant;
* classificação;
* ownership;
* retenção;
* auditoria.

---

# 163. Novos Campos

Novos campos deverão avaliar:

* finalidade;
* classificação;
* necessidade;
* exposição;
* exportação.

---

# 164. Novas Permissões

Permissões deverão ser específicas o suficiente para suportar menor privilégio.

---

# 165. Novas Integrações

Novas integrações deverão seguir GSF-07, GSF-08, GSF-09 e GSF-14 conforme aplicável.

---

# 166. Novas Tasks

Tasks deverão possuir contexto explícito de tenant quando processarem dados organizacionais.

---

# 167. Novos Relatórios

Relatórios deverão aplicar tenant e autorização na origem da consulta.

---

# 168. Novas Exportações

Exportações deverão ser consideradas operações de risco elevado quando incluírem dados Restritos ou Confidenciais.

---

# 169. Novos Uploads

Uploads deverão receber análise específica de segurança.

---

# 170. Novas Dependências

Uma dependência não deverá ser adicionada somente para evitar pequena quantidade de código quando ela introduzir risco ou complexidade desproporcional.

---

# 171. Alterações de Infraestrutura

Mudanças de infraestrutura deverão seguir GSF-09 e os processos de operações e deploy.

---

# 172. Alterações de Autenticação

Mudanças no processo de autenticação deverão receber revisão reforçada e seguir o GAF.

---

# 173. Alterações Financeiras

Mudanças financeiras deverão considerar:

* autorização;
* auditoria;
* integridade;
* idempotência;
* regressão;
* tenant.

---

# 174. Alterações Multi-Tenant

Mudanças que afetem isolamento deverão receber prioridade máxima de revisão.

---

# 175. Alterações de Dados Pessoais

Mudanças que introduzam novos tratamentos deverão seguir GSF-14.

---

# 176. Definition of Ready

Uma mudança de risco relevante não deverá ser considerada pronta para desenvolvimento enquanto aspectos essenciais de segurança estiverem indefinidos.

Exemplo:

```text
[ ] atores definidos
[ ] tenant definido
[ ] permissões definidas
[ ] dados identificados
[ ] classificação avaliada
[ ] integrações identificadas
[ ] riscos principais conhecidos
```

---

# 177. Definition of Done

Uma funcionalidade relevante não deverá ser considerada concluída apenas porque seu fluxo principal funciona.

Exemplo:

```text
[ ] requisito implementado
[ ] autorização implementada
[ ] tenant validado
[ ] entradas validadas
[ ] auditoria implementada quando necessária
[ ] testes criados
[ ] revisão concluída
[ ] documentação atualizada
[ ] monitoramento avaliado
```

---

# 178. Evidências do Desenvolvimento Seguro

O processo deverá produzir evidências.

Exemplos:

* requisitos;
* documentação;
* commits;
* Pull Requests;
* revisões;
* testes;
* pipelines;
* releases;
* auditorias;
* registros de vulnerabilidades;
* registros de incidentes.

---

# 179. Documentação

Mudanças arquiteturais ou operacionais relevantes deverão atualizar a documentação correspondente.

Código e documentação não deverão evoluir em direções incompatíveis.

---

# 180. Responsabilidades

Desenvolvimento seguro é responsabilidade compartilhada.

---

# 181. Engenharia

A Engenharia deverá:

* projetar;
* implementar;
* revisar;
* testar;
* corrigir;
* documentar.

---

# 182. Revisores

Revisores deverão avaliar não apenas estilo de código, mas também impacto funcional e de segurança.

---

# 183. Qualidade

Qualidade deverá apoiar:

* cenários;
* regressões;
* validações;
* critérios de aceite;
* testes.

---

# 184. Operações

Operações deverá garantir ambiente seguro para implantação e execução.

---

# 185. Segurança

A função de Segurança deverá definir e revisar controles conforme a maturidade organizacional.

Enquanto essa responsabilidade estiver incorporada à Engenharia, ela continuará explicitamente necessária.

---

# 186. Produto

Produto deverá evitar requisitos que exijam coleta ou exposição desnecessária.

---

# 187. Exceções

Exceções aos controles deverão possuir:

* justificativa;
* risco;
* responsável;
* prazo;
* compensação;
* revisão.

---

# 188. Débitos de Segurança

Débitos identificados deverão ser registrados.

Não deverão permanecer apenas em comentários ou conhecimento informal.

---

# 189. Métricas

A evolução do SDL poderá utilizar métricas como:

* vulnerabilidades abertas;
* tempo de correção;
* reincidência;
* cobertura de testes críticos;
* incidentes originados por regressão;
* dependências vulneráveis;
* falhas de pipeline.

Métricas deverão orientar melhoria e não incentivar manipulação de números.

---

# 190. Melhoria Contínua

O SDL deverá evoluir conforme:

```text
Incidentes
    +
Vulnerabilidades
    +
Auditorias
    +
Revisões
    +
Experiência
    ↓
Melhoria do processo
```

---

# 191. Evidências Arquiteturais

## EA-GSF-SDL-001

O GSF estabelece Security by Design como princípio oficial da plataforma.

## EA-GSF-SDL-002

O GereIgreja utiliza Django e deverá aproveitar seus mecanismos nativos de segurança.

## EA-GSF-SDL-003

O GereIgreja possui arquitetura multi-tenant e requer isolamento entre organizações.

## EA-GSF-SDL-004

O GAF estabelece autenticação e autorização como componentes estruturais da plataforma.

## EA-GSF-SDL-005

O GSF-06 estabelece práticas de segurança da aplicação.

## EA-GSF-SDL-006

O GSF-07 estabelece controles para APIs.

## EA-GSF-SDL-007

O GSF-08 estabelece controles para proteção de dados e privacidade.

## EA-GSF-SDL-008

O GSF-09 estabelece requisitos para infraestrutura e secrets.

## EA-GSF-SDL-009

O GSF-10 estabelece logging, monitoramento e auditoria.

## EA-GSF-SDL-010

O GSF-11 estabelece continuidade e recuperação.

## EA-GSF-SDL-011

O GSF-12 estabelece gestão contínua de vulnerabilidades.

## EA-GSF-SDL-012

O GSF-13 estabelece gestão de incidentes.

## EA-GSF-SDL-013

O GSF-14 estabelece Privacy by Design, minimização e requisitos de conformidade.

## EA-GSF-SDL-014

A arquitetura do GereIgreja utiliza services, selectors, views, forms, APIs, tasks e integrações como componentes que deverão aplicar controles de segurança conforme sua responsabilidade.

## EA-GSF-SDL-015

O frontend do GereIgreja utiliza tecnologias como HTMX, Alpine.js e JavaScript, sem transferir ao cliente a responsabilidade final por autorização.

## EA-GSF-SDL-016

O projeto possui processos de testes, deploy, operações, governança e documentação que deverão participar do ciclo seguro.

---

# 192. Especificações Oficiais

## GSF-SDL-001

Segurança deverá ser considerada desde a definição do requisito.

## GSF-SDL-002

Toda funcionalidade organizacional deverá possuir escopo de tenant definido.

## GSF-SDL-003

Toda operação protegida deverá possuir requisitos de autorização definidos.

## GSF-SDL-004

Dados deverão ser classificados antes da definição de controles relevantes.

## GSF-SDL-005

Tratamentos de dados pessoais deverão seguir Privacy by Design.

## GSF-SDL-006

Mudanças de maior risco deverão receber análise de segurança proporcional.

## GSF-SDL-007

Trust boundaries relevantes deverão ser considerados na arquitetura.

## GSF-SDL-008

A superfície de ataque deverá ser minimizada.

## GSF-SDL-009

Controles de segurança reutilizáveis deverão ser preferidos a verificações manuais repetidas.

## GSF-SDL-010

O backend deverá ser a autoridade final de autorização.

## GSF-SDL-011

JavaScript, Alpine.js ou HTMX não deverão ser utilizados como mecanismo exclusivo de autorização.

## GSF-SDL-012

Consultas organizacionais deverão respeitar tenant.

## GSF-SDL-013

Cache de dados organizacionais deverá possuir isolamento adequado.

## GSF-SDL-014

Tasks organizacionais deverão possuir contexto de tenant.

## GSF-SDL-015

Relatórios deverão aplicar tenant e autorização.

## GSF-SDL-016

Exportações deverão possuir autorização e minimização.

## GSF-SDL-017

Entradas externas deverão ser consideradas não confiáveis.

## GSF-SDL-018

Mecanismos nativos de segurança do Django deverão ser preferidos.

## GSF-SDL-019

SQL deverá ser parametrizado ou executado através de mecanismos seguros.

## GSF-SDL-020

Proteção CSRF não deverá ser desativada sem justificativa formal.

## GSF-SDL-021

Escape de templates não deverá ser desativado indiscriminadamente.

## GSF-SDL-022

Secrets não deverão existir no código-fonte.

## GSF-SDL-023

Secrets não deverão aparecer em logs.

## GSF-SDL-024

Erros não deverão expor informações internas desnecessárias.

## GSF-SDL-025

Mudanças relevantes deverão passar por code review.

## GSF-SDL-026

Mudanças de autenticação, autorização e multi-tenant deverão receber revisão reforçada.

## GSF-SDL-027

Mudanças financeiras deverão receber testes de integridade e autorização.

## GSF-SDL-028

Testes de autorização deverão cobrir acessos negados.

## GSF-SDL-029

Testes multi-tenant deverão verificar acesso cruzado entre organizações.

## GSF-SDL-030

Vulnerabilidades corrigidas deverão gerar testes de regressão quando tecnicamente apropriado.

## GSF-SDL-031

Dados reais de produção não deverão ser utilizados indiscriminadamente em testes.

## GSF-SDL-032

Dependências deverão ser avaliadas antes da adoção.

## GSF-SDL-033

Dependências deverão continuar sendo monitoradas após adoção.

## GSF-SDL-034

Pipelines deverão executar verificações automatizadas compatíveis com a maturidade do projeto.

## GSF-SDL-035

Falhas críticas de segurança não deverão ser ignoradas sem exceção formal.

## GSF-SDL-036

Produção deverá operar com DEBUG desabilitado.

## GSF-SDL-037

Produção deverá utilizar HTTPS.

## GSF-SDL-038

Configurações de CORS e CSRF deverão ser restritivas ao necessário.

## GSF-SDL-039

Ambientes deverão permanecer segregados.

## GSF-SDL-040

Deploys deverão ser rastreáveis.

## GSF-SDL-041

Mudanças relevantes deverão possuir validação pós-deploy.

## GSF-SDL-042

Monitoramento deverá ser avaliado como parte do release.

## GSF-SDL-043

Vulnerabilidades descobertas em produção deverão seguir GSF-12.

## GSF-SDL-044

Incidentes deverão seguir GSF-13.

## GSF-SDL-045

Hotfixes deverão continuar sendo revisados, testados e rastreáveis.

## GSF-SDL-046

Exceções de segurança deverão possuir justificativa e responsável.

## GSF-SDL-047

Débitos de segurança deverão ser registrados.

## GSF-SDL-048

Mudanças relevantes deverão atualizar documentação quando necessário.

## GSF-SDL-049

Definition of Done deverá incluir controles de segurança aplicáveis.

## GSF-SDL-050

O SDL deverá evoluir com base em vulnerabilidades, incidentes, auditorias e experiência operacional.

---

# 193. Anti-Padrões

São considerados anti-padrões:

```text
Implementar
    ↓
publicar
    ↓
depois revisar segurança
```

---

```text
Usuário está autenticado
=
usuário está autorizado
```

---

```text
Botão está escondido
=
operação está protegida
```

---

```text
Frontend validou
=
backend não precisa validar
```

---

```text
Membro.objects.get(pk=id)
```

em contexto multi-tenant sem garantia adicional de isolamento.

---

```text
Task recebeu ID
=
já sabe qual tenant usar
```

---

```text
Cache funciona
=
chave não precisa considerar tenant
```

---

```text
É apenas relatório
=
não precisa de permission
```

---

```text
É apenas exportação
=
não precisa de auditoria
```

---

```text
É endpoint interno
=
não precisa de autorização
```

---

```text
É hotfix
=
não precisa de teste
```

---

```text
É emergência
=
não precisa de registro
```

---

```text
Framework protege automaticamente
=
código não pode criar vulnerabilidade
```

---

```text
Passou nos testes funcionais
=
está seguro
```

---

```text
Dependência popular
=
dependência segura para sempre
```

---

```text
Secret está em variável JavaScript
=
não está exposto
```

---

```text
DEBUG facilita suporte
=
pode permanecer ligado em produção
```

---

```text
Funcionou após deploy
=
release validado
```

---

```text
Vulnerabilidade corrigida
=
não precisa de teste de regressão
```

---

```text
Documentação pode ser atualizada depois
```

quando a mudança altera arquitetura ou operação crítica.

---

# 194. Checklist

## Requisito

* [ ] atores identificados;
* [ ] dados identificados;
* [ ] classificação definida;
* [ ] tenant definido;
* [ ] permissões definidas;
* [ ] privacidade avaliada;
* [ ] auditoria avaliada;
* [ ] integrações identificadas;
* [ ] criticidade avaliada.

## Arquitetura

* [ ] Security by Design;
* [ ] Privacy by Design;
* [ ] trust boundaries;
* [ ] superfície de ataque;
* [ ] fluxo de dados;
* [ ] ameaças principais;
* [ ] controles;
* [ ] risco residual.

## Backend

* [ ] autenticação;
* [ ] autorização;
* [ ] tenant;
* [ ] services;
* [ ] selectors;
* [ ] forms;
* [ ] serializers;
* [ ] validações;
* [ ] exceptions.

## Frontend

* [ ] nenhuma autorização exclusivamente no cliente;
* [ ] HTMX protegido;
* [ ] CSRF;
* [ ] dados mínimos;
* [ ] conteúdo seguro;
* [ ] ausência de secrets.

## APIs

* [ ] autenticação;
* [ ] autorização;
* [ ] tenant;
* [ ] validação;
* [ ] output mínimo;
* [ ] rate limiting avaliado;
* [ ] auditoria avaliada.

## Dados

* [ ] classificação;
* [ ] minimização;
* [ ] retenção;
* [ ] logs;
* [ ] exports;
* [ ] backups;
* [ ] privacidade.

## Multi-Tenant

* [ ] queries;
* [ ] selectors;
* [ ] services;
* [ ] APIs;
* [ ] relatórios;
* [ ] exports;
* [ ] tasks;
* [ ] cache;
* [ ] arquivos.

## Código

* [ ] SQL seguro;
* [ ] XSS;
* [ ] CSRF;
* [ ] mass assignment;
* [ ] uploads;
* [ ] redirects;
* [ ] SSRF quando aplicável;
* [ ] erros;
* [ ] secrets.

## Code Review

* [ ] requisito revisado;
* [ ] arquitetura revisada;
* [ ] permissões;
* [ ] tenant;
* [ ] dados;
* [ ] logs;
* [ ] configuração;
* [ ] dependências.

## Testes

* [ ] unitários;
* [ ] integração;
* [ ] autorização;
* [ ] multi-tenant;
* [ ] APIs;
* [ ] validação;
* [ ] regressão;
* [ ] auditoria;
* [ ] tasks;
* [ ] integrações.

## Pipeline

* [ ] lint;
* [ ] testes;
* [ ] dependências;
* [ ] secret scanning quando disponível;
* [ ] análise de segurança quando disponível;
* [ ] quality gates.

## Release

* [ ] migrações revisadas;
* [ ] settings;
* [ ] DEBUG;
* [ ] HTTPS;
* [ ] cookies;
* [ ] CORS;
* [ ] CSRF;
* [ ] secrets;
* [ ] jobs;
* [ ] rollback;
* [ ] backup avaliado.

## Deploy

* [ ] ambiente correto;
* [ ] identidade autorizada;
* [ ] versão rastreável;
* [ ] smoke tests;
* [ ] validação;
* [ ] monitoramento.

## Pós-Deploy

* [ ] erros;
* [ ] logs;
* [ ] alertas;
* [ ] métricas;
* [ ] comportamento funcional;
* [ ] segurança;
* [ ] regressões.

## Encerramento

* [ ] Definition of Done;
* [ ] documentação atualizada;
* [ ] débitos registrados;
* [ ] riscos conhecidos;
* [ ] evidências preservadas.

---

# 195. Documentos Relacionados

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
* GSF-13 — Gestão de Incidentes de Segurança
* GSF-14 — Conformidade e LGPD
* GSF-16 — Governança de Segurança

## Arquitetura

* GEA-07 — Arquitetura da Segurança
* GEA-08 — Arquitetura Multi-Tenant

## Backend Engineering

* documentação existente em `docs/backend/`
* arquitetura backend
* models
* services
* selectors
* permissions
* middlewares
* APIs
* tasks
* logging
* exceptions
* testing

## Frontend Engineering

* GFE-01 — Frontend Architecture
* GFE-02 — Estrutura de Pastas
* GFE-03 — Componentes
* GFE-04 — Layouts
* GFE-05 — Templates
* GFE-06 — Assets
* GFE-07 — CSS
* GFE-08 — JavaScript
* GFE-09 — HTMX
* GFE-10 — Alpine.js
* GFE-11 — Dashboards

## Qualidade

* documentação existente em `docs/qualidade/`
* padrões de testes
* estratégia de testes
* checklists de qualidade

## Deploy e Operações

* documentação existente em `docs/deploy/`
* documentação existente em `docs/operacoes/`
* releases
* backups
* monitoramento
* rollback
* cron jobs

## Governança

* Padrões de Segurança
* Padrões de Permissões
* Padrões de Testes
* Padrões de APIs
* Checklist de Release
* Auditoria 360 do GereIgreja

## LGPD

* documentação existente em `docs/lgpd/`
* políticas de privacidade
* retenção
* direitos dos titulares
* inventário e tratamento de dados

---

# 196. Princípios Finais

O Secure Development Lifecycle deverá transformar segurança em comportamento normal da Engenharia.

O GereIgreja não deverá utilizar o modelo:

```text
Funcionalidade pronta
       ↓
revisão de segurança
       ↓
correções tardias
```

O modelo oficial deverá ser:

```text
Requisito seguro
      ↓
Arquitetura segura
      ↓
Implementação segura
      ↓
Revisão
      ↓
Testes
      ↓
Release seguro
      ↓
Operação monitorada
```

A segurança deverá existir onde a decisão é tomada.

Autorização deverá existir no backend.

Isolamento deverá existir nas consultas.

Validação deverá existir na entrada.

Minimização deverá existir na saída.

Auditoria deverá existir nas operações relevantes.

Secrets deverão permanecer fora do código.

Testes deverão provar os limites esperados.

Monitoramento deverá revelar falhas após o deploy.

O princípio central é:

```text
Segurança não é
uma etapa do desenvolvimento.

Segurança é uma propriedade
do desenvolvimento.
```

Cada vulnerabilidade deverá produzir aprendizado.

Cada incidente deverá melhorar o processo.

Cada revisão deverá reduzir a possibilidade de regressão.

Cada nova arquitetura deverá tentar tornar o caminho seguro mais fácil do que o caminho inseguro.

O objetivo final é:

```text
Código seguro
não depender
de memória individual.

Deve depender
de arquitetura
+
padrões
+
processos
+
testes
+
automação.
```

Dessa forma, o GereIgreja poderá crescer sem transformar o aumento da plataforma em aumento descontrolado de risco.

---

# 197. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`15-Secure-Development-Lifecycle.md`

**Documento**

`GSF-15`

**Código**

`GSF-SECURE-DEVELOPMENT-LIFECYCLE`

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

`16-Governanca-de-Seguranca.md`

**Código do próximo documento**

`GSF-16`

```
```
