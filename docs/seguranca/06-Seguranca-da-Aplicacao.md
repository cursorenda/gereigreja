Pasta:

docs/seguranca/

Arquivo:

06-Seguranca-da-Aplicacao.md

Documento:

GSF-06

Código:

GSF-APPLICATION-SECURITY

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

# GSF-06 — Segurança da Aplicação

> "A aplicação deverá permanecer segura mesmo quando entradas forem manipuladas, URLs forem acessadas diretamente, requests forem forjados e usuários tentarem ultrapassar os limites previstos pela interface."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação com os Fundamentos
5. Princípios
6. Django como Base de Segurança
7. Security by Design na Aplicação
8. Superfície de Ataque
9. Entrada Não Confiável
10. Validação
11. Sanitização
12. Normalização
13. CSRF
14. XSS
15. SQL Injection
16. ORM
17. Queries Raw
18. Templates Django
19. Autoescape
20. HTML Seguro
21. JavaScript e Conteúdo Dinâmico
22. HTMX
23. Alpine.js
24. Uploads
25. Arquivos
26. Content-Type
27. Tamanho de Entrada
28. Manipulação de Parâmetros
29. URLs
30. Query Strings
31. Formulários
32. Hidden Fields
33. ModelForms
34. APIs
35. Serialização
36. Autenticação
37. Autorização
38. Multi-Tenant
39. Sessões
40. Cookies
41. HTTPS
42. Headers de Segurança
43. Redirects
44. Open Redirect
45. Exceções
46. Mensagens de Erro
47. Debug
48. Logging
49. Segredos
50. Configurações
51. Variáveis de Ambiente
52. Dependências
53. Bibliotecas Frontend
54. Bibliotecas Python
55. Django Admin
56. Middlewares
57. Decorators
58. Services
59. Selectors
60. Signals
61. Tasks
62. Cache
63. Rate Limiting
64. Idempotência
65. Operações Críticas
66. Financeiro
67. Secretaria
68. Comunicação
69. Eventos
70. Escola Bíblica
71. Patrimônio
72. Administração
73. Portal Público
74. Enumeração
75. Brute Force
76. Abuso de Funcionalidade
77. SSRF e Integrações
78. Segurança em E-mails e Mensagens
79. Segurança de Dados Temporários
80. Testes de Segurança
81. Testes Negativos
82. Revisão de Código
83. Deploy Seguro
84. Evidências Arquiteturais
85. Especificações Oficiais
86. Anti-Padrões
87. Checklist
88. Documentos Relacionados
89. Princípios Finais
90. Status do Documento

---

# 1. Objetivo

Este documento estabelece os padrões oficiais de segurança da aplicação GereIgreja.

Seu objetivo é definir como o software deverá prevenir, limitar e tratar vulnerabilidades relacionadas à camada de aplicação.

Os controles aqui definidos deverão proteger fluxos implementados com:

- Django;
- Django Templates;
- Django Forms;
- ORM;
- middlewares;
- views;
- services;
- selectors;
- JavaScript;
- HTMX;
- Alpine.js;
- Bootstrap;
- integrações;
- tasks;
- cache.

O documento deverá ser aplicado durante:

- arquitetura;
- implementação;
- code review;
- testes;
- release;
- manutenção.

---

# 2. Escopo

Aplica-se a:

- Área de Gestão;
- Portal Público;
- Django Admin;
- Core;
- Secretaria;
- Financeiro;
- Comunicação;
- Eventos;
- Escola Bíblica;
- Patrimônio;
- Relatórios;
- Configurações;
- APIs;
- automações;
- integrações;
- tarefas.

Não deverá existir módulo isento das regras básicas de segurança de aplicação.

---

# 3. Papel deste Documento

O GSF-06 transforma princípios de segurança em regras concretas para a camada de software.

Sua relação é:

```text
GSF-01 — Fundamentos
        ↓
GSF-04 — Autorização
        ↓
GSF-05 — Multi-Tenant
        ↓
GSF-06 — Segurança da Aplicação
````

O GSF-06 deverá ser utilizado em conjunto com esses documentos.

---

# 4. Relação com os Fundamentos

Os principais fundamentos aplicados aqui são:

* Security by Design;
* Security by Default;
* menor privilégio;
* defesa em profundidade;
* entrada não confiável;
* autorização no backend;
* isolamento multi-tenant;
* falha segura;
* minimização;
* rastreabilidade.

---

# 5. Princípios

A segurança da aplicação deverá seguir:

* preferir mecanismos nativos do Django;
* validar no servidor;
* escapar saída;
* limitar exposição;
* negar por padrão;
* isolar tenant;
* tratar erros com segurança;
* proteger segredos;
* manter dependências atualizadas;
* testar caminhos negativos.

---

# 6. Django como Base de Segurança

O GereIgreja utiliza Django como base da aplicação.

Sempre que possível deverão ser utilizados os mecanismos nativos do framework para:

* CSRF;
* escaping;
* sessões;
* cookies;
* autenticação;
* ORM;
* validação;
* middleware;
* permissões;
* forms.

Evitar substituir mecanismos maduros do Django por implementações próprias sem necessidade comprovada.

---

# 7. Security by Design na Aplicação

Toda nova funcionalidade deverá avaliar previamente:

```text
Quais dados recebe?

Quem pode acessar?

Qual tenant?

Quais dados retorna?

Existe ação crítica?

Existe upload?

Existe integração?

Existe risco de abuso?

Existe necessidade de auditoria?
```

A segurança não deverá ser adicionada somente depois da implementação.

---

# 8. Superfície de Ataque

Toda entrada ou endpoint representa potencial superfície de ataque.

Inclui:

* páginas;
* formulários;
* APIs;
* endpoints HTMX;
* uploads;
* integrações;
* webhooks;
* tasks;
* comandos administrativos;
* Django Admin.

Quanto maior a superfície, maior deverá ser a atenção aos controles.

---

# 9. Entrada Não Confiável

Toda entrada externa deverá ser tratada como não confiável.

Inclui:

```text
request.GET
request.POST
request.FILES
headers
cookies
JSON
query strings
IDs
dados de integração
```

Mesmo valores produzidos pelo frontend poderão ser modificados manualmente.

---

# 10. Validação

Toda entrada deverá ser validada.

A validação poderá envolver:

* tipo;
* formato;
* tamanho;
* intervalo;
* enumeração;
* relacionamento;
* permissão;
* tenant;
* regra de negócio.

Validação JavaScript é auxiliar.

Validação backend é obrigatória.

---

# 11. Sanitização

Sanitização deverá ser aplicada quando conteúdo livre puder conter dados não seguros para o destino em que será utilizado.

Ela não deverá ser confundida com validação.

```text
Validação
→ o dado é permitido?

Sanitização
→ como torná-lo seguro para determinado uso?
```

---

# 12. Normalização

Dados deverão ser normalizados quando isso reduzir ambiguidades.

Exemplos:

* espaços;
* caixa;
* formatos;
* telefones;
* documentos.

Normalização não deverá alterar silenciosamente informações de maneira incompatível com a regra de negócio.

---

# 13. CSRF

Operações que alterem estado deverão utilizar proteção CSRF conforme os mecanismos do Django.

Isso inclui requests realizados por:

* forms tradicionais;
* HTMX;
* JavaScript.

Não remover a proteção apenas para facilitar integração frontend.

---

# 14. XSS

A aplicação deverá impedir injeção de scripts em conteúdo exibido.

Entradas de usuário não deverão ser renderizadas como HTML confiável sem análise explícita.

Especial atenção a:

* campos de texto;
* mensagens;
* descrições;
* conteúdo de comunicação;
* comentários;
* parâmetros refletidos.

---

# 15. SQL Injection

O ORM do Django deverá ser preferido para consultas.

Valores recebidos do usuário não deverão ser concatenados diretamente em SQL.

Exemplo inadequado:

```python
query = f"SELECT * FROM tabela WHERE nome = '{nome}'"
```

Preferir ORM ou parâmetros seguros.

---

# 16. ORM

O ORM reduz riscos de SQL Injection quando utilizado corretamente.

Entretanto, ele não resolve:

* autorização;
* tenant;
* exposição indevida;
* consultas amplas;
* regras de negócio.

ORM seguro não significa aplicação segura.

---

# 17. Queries Raw

Queries SQL manuais deverão ser excepcionais.

Quando utilizadas:

* usar parâmetros;
* revisar segurança;
* testar;
* documentar justificativa;
* preservar isolamento multi-tenant.

---

# 18. Templates Django

Templates deverão utilizar escaping padrão.

Conteúdo vindo do usuário não deverá ser marcado como seguro sem necessidade real.

---

# 19. Autoescape

O autoescape do Django deverá permanecer ativo como padrão.

Desativação deverá ser extremamente restrita e revisada.

---

# 20. HTML Seguro

Uso de mecanismos equivalentes a:

```text
safe
mark_safe
```

deverá ocorrer apenas quando o conteúdo for realmente confiável.

Aplicação indiscriminada poderá introduzir XSS.

---

# 21. JavaScript e Conteúdo Dinâmico

Conteúdo inserido dinamicamente pelo frontend deverá evitar APIs inseguras quando houver dados não confiáveis.

Preferir inserção textual quando HTML não for necessário.

---

# 22. HTMX

HTMX deverá preservar:

* CSRF;
* autorização;
* tenant;
* validação;
* escaping.

Endpoints HTMX não são endpoints internos confiáveis.

---

# 23. Alpine.js

Alpine.js deverá ser utilizado apenas para estado local.

Valores provenientes do backend ainda deverão ser apresentados com escaping adequado.

Alpine.js não deverá executar regras de segurança.

---

# 24. Uploads

Uploads representam superfície de risco elevada.

Deverão ser considerados:

* tipo;
* tamanho;
* nome;
* extensão;
* conteúdo;
* armazenamento;
* autorização;
* tenant;
* download.

Não confiar apenas na extensão do arquivo.

---

# 25. Arquivos

Arquivos privados não deverão se tornar públicos apenas por possuírem URL.

O acesso deverá seguir a classificação da informação e o tenant.

---

# 26. Content-Type

O Content-Type deverá ser tratado adequadamente.

A aplicação não deverá assumir que um arquivo é seguro apenas porque o cliente informou um MIME type esperado.

---

# 27. Tamanho de Entrada

Limites deverão existir quando entradas muito grandes puderem causar:

* consumo de memória;
* processamento excessivo;
* abuso;
* indisponibilidade.

Isso inclui:

* uploads;
* textos;
* imports;
* payloads.

---

# 28. Manipulação de Parâmetros

Parâmetros deverão ser validados.

Exemplos críticos:

```text
user_id
tenant_id
igreja_id
congregacao_id
permission_id
role
status
valor
```

Nunca confiar na origem visual do campo.

---

# 29. URLs

URLs são entrada não confiável.

IDs presentes em caminhos deverão passar por:

* autorização;
* tenant;
* validação do recurso.

---

# 30. Query Strings

Query strings deverão atuar sobre um universo já autorizado.

Não deverão ampliar o acesso.

---

# 31. Formulários

Django Forms deverá ser preferido quando apropriado.

Eles deverão:

* validar;
* limpar;
* limitar escolhas;
* apresentar erros;
* preservar regras de domínio.

---

# 32. Hidden Fields

Campos hidden não são seguros.

O usuário poderá alterá-los.

Dados críticos deverão ser derivados do servidor sempre que possível.

---

# 33. ModelForms

ModelForms deverão limitar campos explicitamente.

Evitar exposição acidental de propriedades internas por uso amplo de campos automáticos.

Relacionamentos deverão ser limitados ao escopo permitido.

---

# 34. APIs

APIs deverão aplicar os mesmos controles da aplicação.

Autenticação não substitui:

* autorização;
* tenant;
* validação;
* rate limiting;
* minimização de resposta.

---

# 35. Serialização

APIs deverão retornar somente campos necessários.

Evitar serialização indiscriminada de models completos.

---

# 36. Autenticação

A autenticação deverá seguir o GAF.

A aplicação não deverá criar mecanismos paralelos sem decisão arquitetural.

---

# 37. Autorização

Toda operação protegida deverá aplicar o GSF-04.

A segurança da aplicação não deverá depender de menus ocultos.

---

# 38. Multi-Tenant

Toda entidade organizacional deverá seguir o GSF-05.

Queries deverão ser restritas antes de retornar ou alterar dados.

---

# 39. Sessões

Sessões deverão ser utilizadas de forma compatível com o GAF e o Django.

Dados críticos armazenados em sessão deverão ser minimizados.

Contextos organizacionais armazenados em sessão deverão ser revalidados quando aplicável.

---

# 40. Cookies

Cookies relacionados a segurança deverão utilizar configurações adequadas conforme o ambiente.

Deverão ser avaliados atributos como:

* Secure;
* HttpOnly;
* SameSite.

A configuração final deverá considerar arquitetura, domínio e fluxo de autenticação.

---

# 41. HTTPS

Produção deverá utilizar HTTPS.

Credenciais ou sessões não deverão trafegar por HTTP inseguro.

---

# 42. Headers de Segurança

A aplicação deverá avaliar headers relevantes oferecidos pelo Django e pela infraestrutura.

Exemplos poderão incluir:

* proteção de conteúdo;
* frame embedding;
* MIME sniffing;
* política de referrer.

A configuração deverá ser compatível com o funcionamento real da plataforma.

---

# 43. Redirects

Destinos de redirect derivados de entrada do usuário deverão ser validados.

---

# 44. Open Redirect

Parâmetros como:

```text
next
return_url
redirect
```

não deverão permitir redirecionamento arbitrário para domínios maliciosos.

---

# 45. Exceções

Exceções deverão ser tratadas de forma segura.

A interface não deverá revelar detalhes internos desnecessários.

---

# 46. Mensagens de Erro

Evitar mostrar:

```text
Traceback
SQL
path interno
secret
configuração
stack trace
```

ao usuário final.

Mensagens deverão ser úteis sem expor arquitetura.

---

# 47. Debug

Modo de debug não deverá permanecer habilitado em produção.

Páginas de debug podem revelar:

* configurações;
* ambiente;
* paths;
* variáveis;
* código;
* detalhes internos.

---

# 48. Logging

Logs deverão ser suficientes para diagnóstico, mas não deverão registrar indiscriminadamente:

* senhas;
* tokens;
* secrets;
* payloads confidenciais completos.

---

# 49. Segredos

Segredos deverão ser mantidos fora do código-fonte.

Incluem:

* secret keys;
* senhas;
* tokens;
* chaves de API;
* credenciais externas.

---

# 50. Configurações

Configurações de produção deverão possuir valores seguros por padrão.

A aplicação deverá evitar configuração permissiva apenas para facilitar desenvolvimento.

---

# 51. Variáveis de Ambiente

Credenciais e configurações sensíveis poderão utilizar variáveis de ambiente ou mecanismo equivalente adotado pela infraestrutura.

Segredos não deverão ser incluídos em documentação pública ou logs.

---

# 52. Dependências

Dependências deverão ser revisadas quanto a:

* necessidade;
* manutenção;
* vulnerabilidades;
* compatibilidade;
* origem.

Bibliotecas abandonadas representam risco.

---

# 53. Bibliotecas Frontend

Bibliotecas JavaScript deverão ser introduzidas de forma controlada.

Evitar múltiplas dependências para resolver problemas simples.

---

# 54. Bibliotecas Python

Pacotes Python deverão seguir processo de revisão e atualização.

Dependências transitivas também podem introduzir risco.

---

# 55. Django Admin

O Django Admin deverá permanecer protegido por:

* autenticação;
* permissões;
* restrição de acesso;
* controle de ações;
* tenant quando aplicável.

Ele não deverá ser utilizado como substituto da Área de Gestão para usuários comuns.

---

# 56. Middlewares

Middlewares poderão fornecer controles transversais.

Exemplos:

* contexto;
* segurança;
* headers;
* autenticação complementar;
* auditoria.

Não concentrar regras de negócio complexas indevidamente em middleware.

---

# 57. Decorators

Decorators de segurança deverão possuir responsabilidade clara.

Exemplo:

```text
verificar autenticação
verificar permissão
verificar contexto
```

Não criar decorators duplicados com pequenas diferenças sem necessidade.

---

# 58. Services

Services deverão preservar:

* regra de negócio;
* coerência de tenant;
* integridade;
* transações quando necessárias.

Não assumir que todo chamador já validou tudo sem contrato explícito.

---

# 59. Selectors

Selectors deverão limitar consultas ao universo autorizado.

Não retornar conjuntos globais para o frontend filtrar.

---

# 60. Signals

Signals deverão ser utilizados com cautela.

Comportamentos críticos escondidos em signals podem dificultar:

* rastreabilidade;
* testes;
* transações;
* análise de segurança.

---

# 61. Tasks

Tasks assíncronas deverão validar:

* tenant;
* recurso;
* entrada;
* estado;
* idempotência quando necessária.

Dados recebidos da fila não deverão ser tratados como automaticamente confiáveis.

---

# 62. Cache

Cache deverá preservar:

* tenant;
* usuário quando necessário;
* permissões;
* filtros;
* invalidação.

Cache incorreto pode resultar em vazamento de dados ou autorização obsoleta.

---

# 63. Rate Limiting

Funcionalidades suscetíveis a abuso deverão avaliar rate limiting.

Exemplos:

* login;
* recuperação;
* APIs;
* envio de comunicação;
* endpoints públicos.

O mecanismo exato será definido conforme a infraestrutura disponível.

---

# 64. Idempotência

Operações sensíveis ou passíveis de repetição poderão exigir proteção contra duplicidade.

Especial atenção a:

* financeiro;
* webhooks;
* tasks;
* integrações;
* envio de mensagens.

---

# 65. Operações Críticas

Ações críticas deverão possuir controles adicionais conforme risco.

Exemplos:

* exclusão;
* estorno;
* exportação;
* alteração de permissões;
* alteração de configuração;
* envio em massa.

---

# 66. Financeiro

O Financeiro deverá proteger:

* valores;
* lançamentos;
* receitas;
* despesas;
* estornos;
* relatórios;
* exports.

Especial atenção a:

* duplicidade;
* autorização;
* tenant;
* integridade;
* auditoria.

---

# 67. Secretaria

A Secretaria deverá proteger:

* dados pessoais;
* documentos;
* informações cadastrais;
* exports;
* relacionamentos.

Formulários extensos deverão possuir validação backend completa.

---

# 68. Comunicação

O módulo deverá prevenir abuso em:

* envio;
* agendamento;
* destinatários;
* conteúdo;
* integrações;
* automações.

Envios em massa exigem controles proporcionais ao impacto.

---

# 69. Eventos

Eventos públicos e administrativos deverão ser diferenciados.

Publicação pública não deverá permitir edição pública.

---

# 70. Escola Bíblica

Deverão ser protegidos:

* alunos;
* professores;
* frequência;
* turmas;
* dados relacionados.

---

# 71. Patrimônio

Operações patrimoniais deverão preservar tenant, autorização e integridade.

---

# 72. Administração

Mudanças em:

* usuários;
* grupos;
* permissões;
* integrações;
* configurações;

deverão possuir proteção reforçada.

---

# 73. Portal Público

O Portal Público possui superfície não autenticada maior.

Deverá receber atenção especial a:

* formulários;
* spam;
* abuso;
* validação;
* rate limiting;
* XSS;
* uploads quando existirem.

---

# 74. Enumeração

A aplicação deverá evitar fornecer pistas desnecessárias sobre:

* usuários;
* e-mails;
* registros;
* tenants;
* recursos.

Mensagens diferentes poderão facilitar enumeração.

---

# 75. Brute Force

Fluxos de autenticação e recuperação deverão possuir controles contra tentativas automatizadas conforme o GAF e a infraestrutura disponível.

---

# 76. Abuso de Funcionalidade

Uma funcionalidade legítima poderá ser utilizada abusivamente.

Exemplos:

* exportação repetitiva;
* envio em massa;
* busca automatizada;
* criação excessiva de registros;
* geração de relatórios caros.

Segurança deverá considerar abuso, não apenas invasão técnica.

---

# 77. SSRF e Integrações

Quando a aplicação acessar URLs fornecidas direta ou indiretamente pelo usuário, deverá avaliar risco de SSRF.

Não permitir acesso arbitrário a endpoints internos ou metadados de infraestrutura.

---

# 78. Segurança em E-mails e Mensagens

Conteúdo enviado externamente deverá ser tratado com cuidado.

Não incluir:

* secrets;
* tokens desnecessários;
* informações confidenciais sem finalidade.

Links gerados deverão possuir escopo e validade adequados quando aplicável.

---

# 79. Segurança de Dados Temporários

Arquivos temporários, exports e dados intermediários continuam sujeitos à classificação de segurança.

Não presumir que conteúdo temporário não precisa de proteção.

---

# 80. Testes de Segurança

Testes deverão incluir:

* validação;
* autorização;
* tenant;
* CSRF;
* XSS quando aplicável;
* manipulação de IDs;
* uploads;
* redirects;
* APIs;
* cache;
* tasks.

---

# 81. Testes Negativos

Toda funcionalidade crítica deverá possuir testes negativos.

Exemplos:

```text
usuário sem permissão
outro tenant
payload alterado
ID inválido
CSRF ausente
arquivo inválido
parâmetro manipulado
```

---

# 82. Revisão de Código

Code review deverá procurar:

* queries globais;
* `safe`;
* `mark_safe`;
* raw SQL;
* validação ausente;
* hidden fields confiados;
* secrets;
* endpoints desprotegidos;
* cache sem tenant;
* permissões insuficientes.

---

# 83. Deploy Seguro

Antes do deploy, revisar:

* DEBUG;
* HTTPS;
* secrets;
* dependências;
* migrations;
* configurações;
* arquivos;
* permissões;
* endpoints públicos.

---

# 84. Evidências Arquiteturais

## EA-GSF-APP-001

O GereIgreja utiliza Django como framework principal da aplicação.

## EA-GSF-APP-002

O backend possui documentação específica de Views.

## EA-GSF-APP-003

O backend possui documentação específica de Forms.

## EA-GSF-APP-004

O backend possui documentação específica de Validators.

## EA-GSF-APP-005

O backend possui documentação específica de Permissions.

## EA-GSF-APP-006

O backend possui documentação específica de Middlewares.

## EA-GSF-APP-007

O backend possui documentação específica de Services e Selectors.

## EA-GSF-APP-008

O backend possui documentação específica de Tasks, Cache, Logging e Exceptions.

## EA-GSF-APP-009

O frontend utiliza Django Templates como base de renderização.

## EA-GSF-APP-010

HTMX e Alpine.js fazem parte da estratégia frontend documentada.

## EA-GSF-APP-011

O GereIgreja possui arquitetura multi-tenant documentada.

## EA-GSF-APP-012

O GSF determina o uso preferencial dos mecanismos nativos de segurança do Django.

---

# 85. Especificações Oficiais

## GSF-APP-001

Entradas externas deverão ser tratadas como não confiáveis.

## GSF-APP-002

Validação de segurança deverá ocorrer no backend.

## GSF-APP-003

Proteção CSRF deverá permanecer ativa nas operações aplicáveis.

## GSF-APP-004

Conteúdo de usuário não deverá ser renderizado como HTML seguro sem validação explícita.

## GSF-APP-005

O autoescape do Django deverá permanecer ativo por padrão.

## GSF-APP-006

Raw SQL deverá utilizar parâmetros seguros e possuir justificativa.

## GSF-APP-007

ORM não deverá ser tratado como substituto de autorização ou tenant.

## GSF-APP-008

Uploads deverão possuir validação adequada.

## GSF-APP-009

Hidden fields não deverão ser considerados confiáveis.

## GSF-APP-010

ModelForms deverão limitar campos e relacionamentos.

## GSF-APP-011

APIs deverão aplicar autorização, tenant e validação.

## GSF-APP-012

HTMX deverá utilizar os mesmos controles de segurança das demais requisições.

## GSF-APP-013

Alpine.js não deverá executar decisões finais de autorização.

## GSF-APP-014

Sessões e cookies deverão utilizar configurações adequadas ao ambiente.

## GSF-APP-015

Produção deverá utilizar HTTPS.

## GSF-APP-016

Redirects derivados de entrada do usuário deverão ser validados.

## GSF-APP-017

DEBUG não deverá permanecer habilitado em produção.

## GSF-APP-018

Mensagens de erro não deverão revelar detalhes internos desnecessários.

## GSF-APP-019

Secrets não deverão ser armazenados diretamente no código-fonte.

## GSF-APP-020

Dependências deverão ser revisadas e mantidas.

## GSF-APP-021

Django Admin deverá permanecer restrito a usuários autorizados.

## GSF-APP-022

Decorators de segurança deverão possuir responsabilidade clara e reutilizável.

## GSF-APP-023

Services deverão preservar integridade e escopo.

## GSF-APP-024

Selectors deverão limitar dados ao universo autorizado.

## GSF-APP-025

Tasks deverão validar contexto e recursos.

## GSF-APP-026

Cache deverá preservar tenant e autorização quando aplicável.

## GSF-APP-027

Rate limiting deverá ser considerado em funcionalidades sujeitas a abuso.

## GSF-APP-028

Operações críticas deverão possuir controles proporcionais ao risco.

## GSF-APP-029

Portal Público deverá receber controles contra abuso e entrada maliciosa.

## GSF-APP-030

Testes negativos deverão fazer parte de funcionalidades críticas.

---

# 86. Anti-Padrões

São considerados anti-padrões:

```text
DEBUG=True
em produção
```

---

```python
mark_safe(conteudo_do_usuario)
```

sem garantia de confiança.

---

```django
{{ dado|safe }}
```

aplicado indiscriminadamente.

---

```python
sql = "SELECT * FROM tabela WHERE id = " + request.GET["id"]
```

---

```text
Campo hidden
=
valor confiável
```

---

```text
Endpoint HTMX
=
endpoint interno
=
não precisa CSRF ou autorização
```

---

```text
Extensão .jpg
=
arquivo é imagem segura
```

---

```text
Usuário autenticado
=
API autorizada
```

---

```text
Erro inesperado
=
mostrar traceback
```

---

```text
Secret no settings.py
versionado no repositório
```

---

```text
Cache global
para conteúdo de tenant
```

---

```text
Instalar biblioteca
sem avaliar necessidade ou manutenção
```

---

# 87. Checklist

## Entrada

* [ ] GET validado;
* [ ] POST validado;
* [ ] JSON validado;
* [ ] IDs validados;
* [ ] tamanho limitado quando necessário;
* [ ] normalização avaliada.

## Django

* [ ] Forms utilizados quando apropriado;
* [ ] Validators adequados;
* [ ] ORM utilizado com segurança;
* [ ] autoescape preservado;
* [ ] `safe` revisado;
* [ ] raw SQL revisado.

## CSRF

* [ ] forms protegidos;
* [ ] HTMX protegido;
* [ ] requests customizados revisados.

## Autorização

* [ ] identidade;
* [ ] permissão;
* [ ] tenant;
* [ ] recurso;
* [ ] operação.

## Uploads

* [ ] tipo validado;
* [ ] tamanho validado;
* [ ] nome controlado;
* [ ] acesso protegido;
* [ ] tenant associado.

## APIs

* [ ] autenticação;
* [ ] autorização;
* [ ] tenant;
* [ ] campos minimizados;
* [ ] rate limiting avaliado.

## Sessão

* [ ] cookies seguros;
* [ ] contexto validado;
* [ ] dados sensíveis minimizados.

## Configuração

* [ ] DEBUG desabilitado em produção;
* [ ] HTTPS;
* [ ] secrets fora do código;
* [ ] variáveis de ambiente revisadas;
* [ ] headers avaliados.

## Dependências

* [ ] necessidade;
* [ ] manutenção;
* [ ] vulnerabilidades;
* [ ] versão;
* [ ] origem.

## Cache

* [ ] chave segura;
* [ ] tenant;
* [ ] usuário quando necessário;
* [ ] invalidação;
* [ ] dados sensíveis revisados.

## Tasks

* [ ] tenant;
* [ ] recurso;
* [ ] entrada;
* [ ] duplicidade;
* [ ] logging.

## Testes

* [ ] CSRF;
* [ ] XSS quando aplicável;
* [ ] outro tenant;
* [ ] usuário sem permissão;
* [ ] ID manipulado;
* [ ] upload inválido;
* [ ] redirect manipulado;
* [ ] API direta;
* [ ] HTMX direto.

---

# 88. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-02 — Classificação e Proteção da Informação
* GSF-03 — Gestão de Identidade
* GSF-04 — Autorização e Controle de Acesso
* GSF-05 — Segurança Multi-Tenant
* GSF-07 — Segurança das APIs
* GSF-08 — Segurança de Dados e Privacidade
* GSF-09 — Segurança de Infraestrutura e Segredos
* GSF-10 — Logging, Monitoramento e Auditoria
* GSF-12 — Gestão de Vulnerabilidades

## Arquitetura

* GEA-03 — Arquitetura do Backend
* GEA-04 — Arquitetura do Frontend
* GEA-07 — Arquitetura da Segurança
* GEA-08 — Arquitetura Multi-Tenant

## Backend

* Views
* Forms
* Validators
* Permissions
* Middlewares
* Services
* Selectors
* Signals
* Tasks
* Cache
* Logging
* Exceptions
* Testing

## Frontend

* Templates
* JavaScript
* HTMX
* Alpine.js

## Governança

* Padrões de Views
* Padrões de Forms
* Padrões de Permissões
* Padrões de Segurança
* Padrões de Testes

---

# 89. Princípios Finais

A segurança da aplicação deverá partir da premissa de que o cliente pode manipular qualquer informação que envie.

Por isso:

```text
Frontend
não é fronteira de confiança.
```

A aplicação deverá preservar controles em:

```text
Entrada
+
Validação
+
Autenticação
+
Autorização
+
Tenant
+
Domínio
+
Saída
```

O Django deverá ser utilizado como aliado de segurança.

Seus mecanismos nativos deverão ser preservados sempre que adequados.

A regra final é:

```text
Não confiar na entrada.

Não confiar na URL.

Não confiar no hidden field.

Não confiar no JavaScript.

Não confiar no ID.

Não confiar apenas na autenticação.

Validar no backend.
```

Uma aplicação segura deverá continuar protegida mesmo quando o usuário não utilizar a interface exatamente como foi projetada.

---

# 90. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`06-Seguranca-da-Aplicacao.md`

**Documento**

`GSF-06`

**Código**

`GSF-APPLICATION-SECURITY`

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

`07-Seguranca-das-APIs.md`

**Código do próximo documento**

`GSF-07`

```
```
