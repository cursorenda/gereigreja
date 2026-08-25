````markdown id="gsf05"
Pasta:

docs/seguranca/

Arquivo:

05-Seguranca-Multi-Tenant.md

Documento:

GSF-05

Código:

GSF-MULTI-TENANT

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

# GSF-05 — Segurança Multi-Tenant

> "No GereIgreja, o isolamento entre organizações não é apenas uma regra de negócio. É uma fronteira de segurança que deve ser preservada em toda consulta, operação, integração, tarefa e resposta da plataforma."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Conceito de Multi-Tenant no GereIgreja
5. Princípios
6. Tenant como Fronteira de Segurança
7. Organização e Contexto
8. Igreja e Escopo Organizacional
9. Congregações
10. Identidade e Tenant
11. Autorização e Tenant
12. Regra de Ouro do Isolamento
13. Entrada Não Confiável
14. Identificadores de Tenant
15. URLs
16. Query Strings
17. Formulários
18. Campos Ocultos
19. Payloads
20. Views
21. QuerySets
22. Selectors
23. Managers
24. Services
25. Forms Django
26. ModelForms
27. Relacionamentos
28. Validação de Foreign Keys
29. Django Admin
30. Templates
31. Frontend
32. HTMX
33. APIs
34. Serializers e Respostas
35. Tasks
36. Automações
37. Integrações
38. Cache
39. Chaves de Cache
40. Sessão
41. Troca de Tenant
42. Contexto Ativo
43. Revogação de Contexto
44. Relatórios
45. Dashboards
46. Exportações
47. Importações
48. Arquivos e Uploads
49. Financeiro
50. Secretaria
51. Escola Bíblica
52. Eventos
53. Comunicação
54. Patrimônio
55. Configurações
56. Dados Compartilhados
57. Dados Globais
58. Recursos sem Tenant
59. Operações em Massa
60. Busca Global
61. Auditoria
62. Logging
63. Monitoramento
64. Vazamento Horizontal
65. IDOR Multi-Tenant
66. Elevação de Escopo
67. Enumeração
68. Falhas de Query
69. Falhas de Cache
70. Falhas em Tasks
71. Falhas em Relatórios
72. Falhas em Exportações
73. Fail Closed
74. Testes
75. Testes entre Tenants
76. Testes de Formulários
77. Testes de APIs
78. Testes de Cache
79. Testes de Tasks
80. Testes de Relatórios
81. Evidências Arquiteturais
82. Especificações Oficiais
83. Anti-Padrões
84. Checklist
85. Documentos Relacionados
86. Princípios Finais
87. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial de segurança multi-tenant do GereIgreja.

Seu objetivo é impedir que usuários, processos, integrações ou operações pertencentes a uma organização acessem, modifiquem, exportem ou processem dados de outra organização sem autorização explícita.

O isolamento deverá ser aplicado em toda a cadeia:

```text
Request
   ↓
Identidade
   ↓
Tenant
   ↓
Autorização
   ↓
Query
   ↓
Regra de negócio
   ↓
Resposta
````

O tenant deverá ser tratado como parte da decisão de segurança e não apenas como filtro visual ou parâmetro de interface.

---

# 2. Escopo

Este documento aplica-se a:

* Área de Gestão;
* Django Admin;
* Core;
* Secretaria;
* Financeiro;
* Escola Bíblica;
* Eventos;
* Comunicação;
* Patrimônio;
* Relatórios;
* Configurações;
* APIs;
* HTMX;
* tasks;
* automações;
* integrações;
* caches;
* exports;
* imports;
* arquivos;
* dashboards;
* processos assíncronos.

Aplica-se a qualquer entidade cuja propriedade, visibilidade ou operação dependa do contexto organizacional.

---

# 3. Papel deste Documento

O GSF-05 especializa dois fundamentos já definidos:

```text
GSF-03 — Identidade
        ↓
Quem é o usuário?

GSF-04 — Autorização
        ↓
O que ele pode fazer?

GSF-05 — Multi-Tenant
        ↓
Em qual organização ele pode fazer?
```

O isolamento multi-tenant deverá ser considerado parte inseparável da autorização efetiva.

---

# 4. Conceito de Multi-Tenant no GereIgreja

O GereIgreja atende múltiplas organizações dentro da mesma plataforma.

Essas organizações compartilham infraestrutura, mas não deverão compartilhar dados indevidamente.

Modelo conceitual:

```text
Plataforma GereIgreja
│
├── Igreja A
│   ├── membros
│   ├── financeiro
│   ├── eventos
│   └── configurações
│
├── Igreja B
│   ├── membros
│   ├── financeiro
│   ├── eventos
│   └── configurações
│
└── Igreja C
    ├── membros
    ├── financeiro
    ├── eventos
    └── configurações
```

A infraestrutura pode ser compartilhada.

Os dados, quando organizacionalmente privados, não.

---

# 5. Princípios

A segurança multi-tenant deverá seguir:

* isolamento por padrão;
* validação no backend;
* menor privilégio;
* escopo explícito;
* queries restritas;
* fail closed;
* rastreabilidade;
* consistência;
* proteção em todas as camadas.

---

# 6. Tenant como Fronteira de Segurança

Tenant deverá ser tratado como uma fronteira semelhante a outras barreiras de autorização.

Regra:

```text
Usuário da Igreja A
        X
Dados privados da Igreja B
```

A aplicação deverá impedir:

* leitura;
* alteração;
* exclusão;
* exportação;
* processamento;
* inclusão de relacionamento cruzado indevido.

---

# 7. Organização e Contexto

O GereIgreja poderá possuir entidades organizacionais diferentes conforme a arquitetura.

O documento utilizará `tenant` como conceito de segurança para representar o escopo organizacional principal.

A implementação deverá utilizar os modelos e relacionamentos reais do projeto.

Não deverá ser criado um novo conceito técnico apenas para satisfazer esta documentação.

---

# 8. Igreja e Escopo Organizacional

A igreja ou organização associada ao usuário deverá determinar o universo de dados acessível, conforme permissões e regras de negócio.

Modelo conceitual:

```text
Usuário
  ↓
Organização autorizada
  ↓
Permissões
  ↓
Recursos da organização
```

---

# 9. Congregações

Congregações poderão representar subdivisões dentro de uma organização.

Elas não deverão ser automaticamente tratadas como tenants independentes sem que a arquitetura as defina dessa forma.

Entretanto, quando houver restrições por congregação, o mesmo princípio de isolamento deverá ser aplicado ao escopo correspondente.

---

# 10. Identidade e Tenant

Toda identidade deverá possuir contexto organizacional válido antes de acessar dados protegidos por tenant.

Autenticação isolada não deverá ser suficiente.

```text
Identidade válida
        ↓
Tenant autorizado?
        ├── Não → negar
        └── Sim
```

---

# 11. Autorização e Tenant

A autorização efetiva deverá considerar:

```text
Permissão
+
Tenant
+
Recurso
+
Regra de negócio
```

Uma permissão válida em um tenant não deverá ser automaticamente válida em outro.

---

# 12. Regra de Ouro do Isolamento

A regra fundamental é:

```text
NUNCA confiar
no tenant informado pelo cliente
sem validar seu vínculo no backend.
```

Isso vale para:

* URL;
* query string;
* formulário;
* hidden input;
* payload;
* header;
* JavaScript;
* HTMX;
* API.

---

# 13. Entrada Não Confiável

Toda informação recebida do cliente deverá ser considerada manipulável.

Exemplos:

```text
tenant_id
igreja_id
congregacao_id
organizacao_id
```

Mesmo que o frontend gere corretamente esses valores, o usuário poderá alterá-los manualmente.

---

# 14. Identificadores de Tenant

Identificadores de tenant não deverão funcionar como prova de autorização.

Exemplo inadequado:

```text
tenant_id = 25
        ↓
carregar tenant 25
        ↓
permitir
```

O correto é:

```text
tenant_id = 25
        ↓
carregar somente dentro
dos tenants autorizados
        ↓
prosseguir ou negar
```

---

# 15. URLs

URLs contendo IDs organizacionais deverão ser validadas.

Exemplo:

```text
/igrejas/10/membros/50/
```

O backend deverá verificar:

* usuário;
* acesso à igreja 10;
* acesso ao membro 50;
* relação entre o membro e a igreja 10;
* permissão da operação.

---

# 16. Query Strings

Filtros como:

```text
?igreja=10
?congregacao=5
```

não deverão alterar o escopo para entidades não autorizadas.

Filtros deverão restringir uma base já autorizada, nunca ampliar o universo de dados.

---

# 17. Formulários

Formulários deverão limitar opções ao contexto permitido.

Exemplo:

```text
Congregação
[lista somente congregações autorizadas]
```

Não apresentar todas as organizações e confiar que o usuário selecionará corretamente.

---

# 18. Campos Ocultos

Hidden inputs são manipuláveis.

Exemplo inadequado:

```html
<input type="hidden" name="tenant_id" value="10">
```

seguido de confiança automática no backend.

O valor deverá ser validado contra o contexto autorizado ou derivado do próprio contexto do servidor quando possível.

---

# 19. Payloads

Payloads JSON, POST ou HTMX deverão ser tratados da mesma forma.

Exemplo de risco:

```json
{
  "tenant_id": 99,
  "membro_id": 50
}
```

A aplicação deverá validar ambos dentro do escopo permitido.

---

# 20. Views

Views deverão iniciar suas consultas a partir do contexto autorizado.

Preferir conceitualmente:

```text
objetos_do_tenant_autorizado
        ↓
get(pk=id)
```

em vez de:

```text
Objeto.objects.get(pk=id)
        ↓
verificar depois
```

quando isso puder reduzir o risco de exposição.

---

# 21. QuerySets

QuerySets deverão ser restritos ao tenant o mais cedo possível.

Exemplo conceitual:

```python
Objeto.objects.filter(
    igreja=igreja_autorizada
)
```

A implementação exata deverá seguir os modelos reais.

---

# 22. Selectors

Selectors são uma camada importante para consolidar consultas seguras.

Exemplo conceitual:

```text
selector
   ↓
recebe contexto autorizado
   ↓
retorna somente dados do tenant
```

Isso reduz duplicação de filtros de segurança em múltiplas views.

---

# 23. Managers

Managers poderão centralizar escopos estruturais quando isso fizer parte da arquitetura.

Entretanto, seu comportamento deverá ser explícito e testável.

---

# 24. Services

Services deverão receber contexto suficiente para impedir operações cruzadas.

Exemplo conceitual:

```text
service.execute(
    tenant=tenant_autorizado,
    objeto=objeto_autorizado
)
```

O service não deverá assumir que qualquer objeto fornecido pelo chamador pertence ao tenant correto.

---

# 25. Forms Django

Forms deverão limitar querysets de campos relacionais.

Exemplo:

```text
ModelChoiceField
        ↓
queryset somente
do tenant autorizado
```

Isso melhora experiência e segurança.

A validação final deverá continuar no servidor.

---

# 26. ModelForms

ModelForms merecem atenção especial porque podem aceitar relacionamentos diretamente.

Campos relacionados deverão ser restringidos ao escopo autorizado.

---

# 27. Relacionamentos

Não deverá ser possível criar relações inconsistentes entre tenants.

Exemplo:

```text
Membro da Igreja A
        +
Congregação da Igreja B
        =
INVÁLIDO
```

A integridade deverá ser validada no domínio e, quando apropriado, reforçada pelo modelo ou banco.

---

# 28. Validação de Foreign Keys

IDs de objetos relacionados deverão ser validados dentro do tenant.

Nunca confiar apenas no fato de o ID existir.

---

# 29. Django Admin

O Django Admin deverá respeitar escopo organizacional quando usuários administrativos não possuírem acesso global.

QuerySets, campos relacionados e ações deverão ser revisados.

Acesso técnico global deverá ser explicitamente diferenciado de administração organizacional.

---

# 30. Templates

Templates não deverão receber dados de tenants não autorizados apenas para escondê-los com condições.

Regra:

```text
Não autorizado
        ↓
não enviar para o template
```

---

# 31. Frontend

Frontend poderá manter contexto visual do tenant atual.

Entretanto:

```text
tenant exibido na UI
≠
tenant autorizado no backend
```

Toda operação continuará sujeita à validação do servidor.

---

# 32. HTMX

HTMX não altera a fronteira de segurança.

Requests HTMX deverão validar tenant exatamente como requests convencionais.

Exemplo:

```text
hx-get="/financeiro/?igreja=20"
```

não deverá permitir acesso à igreja 20 sem autorização.

---

# 33. APIs

APIs possuem alto risco de vazamento horizontal.

Toda API multi-tenant deverá considerar:

```text
Identidade
+
Tenant
+
Permissão
+
Objeto
+
Campos retornados
```

Filtros enviados pelo cliente não deverão ampliar o escopo autorizado.

---

# 34. Serializers e Respostas

APIs deverão retornar somente objetos e campos pertencentes ao escopo correto.

Não serializar dados globais e filtrá-los no frontend.

---

# 35. Tasks

Tasks deverão transportar ou reconstruir o tenant de maneira segura.

Exemplo conceitual:

```text
task(
    tenant_id,
    recurso_id
)
```

Ao executar, a task deverá validar a relação entre ambos.

Não assumir que parâmetros de fila são sempre confiáveis ou coerentes.

---

# 36. Automações

Automações diárias, agendadas ou em massa deverão iterar explicitamente por contexto organizacional quando necessário.

Anti-padrão:

```text
buscar todos os registros
        ↓
processar tudo
```

quando o processamento deveria ser segmentado por tenant.

---

# 37. Integrações

Integrações deverão preservar o tenant de origem.

Dados enviados a serviços externos deverão ser associados ao contexto correto e minimizados.

Uma integração não deverá reutilizar dados entre organizações por erro de estado ou configuração.

---

# 38. Cache

Cache é uma superfície crítica de vazamento multi-tenant.

Exemplo inadequado:

```text
cache key:
dashboard_financeiro
```

para conteúdo específico de uma igreja.

Isso poderá entregar dados de uma organização a outra.

---

# 39. Chaves de Cache

Quando o conteúdo depender de tenant, a chave deverá incluir contexto suficiente.

Exemplo conceitual:

```text
dashboard_financeiro:{tenant_id}
```

Outros fatores poderão ser necessários:

* usuário;
* período;
* congregação;
* filtro.

A chave deverá refletir todas as dimensões que alterem o conteúdo protegido.

---

# 40. Sessão

Quando o tenant ativo for mantido em sessão, o valor deverá ser validado.

Uma sessão antiga não deverá preservar acesso depois de revogação.

---

# 41. Troca de Tenant

Se existir funcionalidade de troca de organização:

```text
Usuário solicita tenant
        ↓
Backend valida vínculo atual
        ↓
Atualiza contexto
```

Nunca:

```text
Recebe tenant_id
        ↓
salva na sessão
```

sem validação.

---

# 42. Contexto Ativo

A interface deverá deixar claro quando operações dependem de contexto organizacional atual.

O contexto não deverá ser invisível em operações cujo impacto possa atingir outra organização.

---

# 43. Revogação de Contexto

Se o usuário perder acesso ao tenant ativo:

* novas requisições deverão ser negadas;
* sessão deverá ser ajustada quando aplicável;
* caches derivados deverão ser invalidados;
* contextos antigos não deverão continuar válidos.

---

# 44. Relatórios

Relatórios deverão aplicar tenant antes de agregações.

Exemplo inadequado:

```text
agregar dados globais
        ↓
filtrar visualmente
```

Preferir:

```text
filtrar tenant
        ↓
agregar
```

---

# 45. Dashboards

KPIs e gráficos deverão ser calculados somente sobre dados do escopo autorizado.

Um único KPI incorretamente agregado poderá constituir vazamento de informação.

---

# 46. Exportações

Exportações deverão ser geradas a partir de querysets já limitados ao tenant.

O arquivo final deverá conter somente informações autorizadas.

---

# 47. Importações

Importações deverão associar registros ao tenant correto.

O tenant não deverá ser definido arbitrariamente por uma coluna não confiável do arquivo quando o contexto puder ser derivado do servidor.

---

# 48. Arquivos e Uploads

Arquivos pertencentes a uma organização deverão manter associação e controle de acesso adequados.

URLs de arquivos não deverão permitir acesso cruzado.

---

# 49. Financeiro

Financeiro constitui área de alta criticidade multi-tenant.

Devem ser isolados:

* lançamentos;
* receitas;
* despesas;
* categorias;
* fundos;
* relatórios;
* saldos;
* exports.

Vazamento financeiro entre igrejas é incidente crítico.

---

# 50. Secretaria

Devem ser isolados, conforme o domínio:

* membros;
* visitantes;
* congregações;
* cadastros;
* documentos;
* relatórios;
* exports.

---

# 51. Escola Bíblica

Devem ser isolados:

* turmas;
* alunos;
* professores;
* frequências;
* relatórios relacionados.

---

# 52. Eventos

Eventos privados ou administrativos deverão respeitar tenant.

Conteúdo explicitamente público poderá possuir outro tratamento, mas sua administração continuará vinculada ao tenant de origem.

---

# 53. Comunicação

Comunicação deverá preservar isolamento em:

* listas;
* contatos;
* campanhas;
* destinatários;
* históricos;
* templates internos;
* automações.

Uma igreja não deverá utilizar destinatários de outra por erro de query ou cache.

---

# 54. Patrimônio

Registros patrimoniais deverão permanecer vinculados à organização correta.

---

# 55. Configurações

Configurações específicas da igreja deverão utilizar escopo de tenant.

Configurações globais da plataforma deverão ser claramente diferenciadas.

---

# 56. Dados Compartilhados

Alguns dados poderão ser compartilhados intencionalmente entre tenants.

Isso somente deverá ocorrer quando a arquitetura definir explicitamente essa característica.

Não presumir compartilhamento.

---

# 57. Dados Globais

Dados globais pertencem à plataforma e não a um tenant específico.

Exemplos possíveis:

* tabelas de referência;
* configurações centrais;
* metadados globais.

A classificação como global deverá ser deliberada.

---

# 58. Recursos sem Tenant

Nem toda entidade precisa possuir tenant.

Entretanto, recursos sem tenant deverão ser identificados conscientemente.

Pergunta obrigatória:

```text
Este dado é realmente global
ou apenas esqueceu-se de aplicar tenant?
```

---

# 59. Operações em Massa

Operações em massa deverão assegurar que todos os registros pertencem ao escopo autorizado.

Nunca confiar apenas nos IDs selecionados pelo frontend.

---

# 60. Busca Global

Buscas deverão começar pelo universo autorizado.

Não buscar globalmente e filtrar depois na interface.

---

# 61. Auditoria

Eventos multi-tenant relevantes deverão registrar o contexto organizacional quando aplicável.

Exemplo:

```text
Usuário
Tenant
Operação
Recurso
Resultado
```

---

# 62. Logging

Logs deverão permitir identificar o contexto sem expor dados desnecessários.

Quando apropriado, utilizar identificadores técnicos em vez de reproduzir conteúdos confidenciais.

---

# 63. Monitoramento

Eventos suspeitos incluem:

* repetidas tentativas de acesso a tenants diferentes;
* manipulação de IDs;
* acesso negado em recursos sequenciais;
* falhas recorrentes de escopo.

Esses eventos poderão alimentar monitoramento conforme política oficial.

---

# 64. Vazamento Horizontal

Vazamento horizontal ocorre quando usuário de um contexto acessa dados de outro contexto com nível semelhante de privilégio.

Exemplo:

```text
Usuário comum da Igreja A
        ↓
acessa membro da Igreja B
```

Esse é um dos riscos centrais de uma aplicação multi-tenant.

---

# 65. IDOR Multi-Tenant

Referências diretas inseguras a objetos são especialmente perigosas.

Exemplo:

```text
/membros/101/
```

Se alterar para:

```text
/membros/102/
```

não deverá permitir acesso a membro de outro tenant.

---

# 66. Elevação de Escopo

Um usuário não deverá ampliar seu próprio universo de acesso.

Exemplos de risco:

```text
alterar tenant_id
alterar igreja_id
alterar congregacao_id
alterar organização ativa
```

Toda mudança deverá ser autorizada.

---

# 67. Enumeração

Mensagens e respostas não deverão facilitar descoberta de dados pertencentes a outras organizações.

Quando necessário, retornar respostas indistinguíveis entre:

* inexistente;
* fora do escopo.

---

# 68. Falhas de Query

Erros comuns incluem:

```text
.objects.all()
```

em contexto multi-tenant.

```text
.objects.get(pk=id)
```

sem escopo.

```text
filter(id__in=ids)
```

sem tenant em operação em massa.

Esses padrões deverão ser revisados conforme o contexto.

---

# 69. Falhas de Cache

Riscos incluem:

* chave sem tenant;
* cache global de queryset;
* invalidação incorreta;
* reutilização entre usuários.

Cache deverá ser revisado como parte da segurança multi-tenant.

---

# 70. Falhas em Tasks

Riscos incluem:

* tenant incorreto;
* objeto de outro tenant;
* contexto perdido;
* lote global indevido.

Tasks deverão possuir testes específicos quando processarem dados organizacionais.

---

# 71. Falhas em Relatórios

Relatórios podem vazar grandes volumes de dados.

Filtros de tenant deverão ocorrer antes da consolidação.

---

# 72. Falhas em Exportações

Exportações indevidas podem transformar pequeno erro de autorização em incidente de grande impacto.

Por isso, devem receber atenção reforçada.

---

# 73. Fail Closed

Quando o sistema não conseguir determinar corretamente o tenant:

```text
NEGAR
```

Nunca assumir tenant padrão arbitrário para operação protegida.

---

# 74. Testes

Testes multi-tenant são obrigatórios em funcionalidades que processam dados organizacionais.

Não basta testar o caminho autorizado.

---

# 75. Testes entre Tenants

Padrão mínimo:

```text
Tenant A
  └── recurso A

Tenant B
  └── recurso B

Usuário A
  ├── acessa recurso A → permitido
  └── acessa recurso B → negado
```

---

# 76. Testes de Formulários

Testar:

* opções exibidas;
* IDs alterados manualmente;
* relações cruzadas;
* POST direto;
* ModelChoiceField.

---

# 77. Testes de APIs

Testar:

* listagem;
* detalhe;
* criação;
* alteração;
* exclusão;
* filtros;
* IDs;
* paginação;
* exportação.

Sempre com cenários cruzados entre tenants.

---

# 78. Testes de Cache

Testar:

```text
Tenant A gera cache
        ↓
Tenant B acessa
        ↓
não recebe dados de A
```

---

# 79. Testes de Tasks

Testar:

* tenant correto;
* objeto correto;
* parâmetros manipulados;
* processamento em lote;
* isolamento.

---

# 80. Testes de Relatórios

Testar:

* totais;
* agregações;
* gráficos;
* exportações;
* filtros.

Nenhum número deverá incorporar dados externos ao tenant.

---

# 81. Evidências Arquiteturais

## EA-GSF-MT-001

O GereIgreja possui arquitetura Multi-Tenant documentada em GEA-08.

## EA-GSF-MT-002

O backend possui documentação de Selectors.

## EA-GSF-MT-003

O backend possui documentação de Managers.

## EA-GSF-MT-004

O backend possui documentação de Services.

## EA-GSF-MT-005

O backend possui documentação de Permissions.

## EA-GSF-MT-006

O backend possui documentação de Forms.

## EA-GSF-MT-007

O backend possui documentação de Cache.

## EA-GSF-MT-008

O backend possui documentação de Tasks.

## EA-GSF-MT-009

A governança possui padrões de segurança e permissões.

## EA-GSF-MT-010

O GereIgreja possui módulos administrativos com dados pessoais, financeiros e operacionais que exigem isolamento organizacional.

---

# 82. Especificações Oficiais

## GSF-MT-001

Todo recurso organizacional deverá possuir isolamento compatível com seu tenant.

## GSF-MT-002

O tenant informado pelo cliente nunca deverá ser considerado autorizado sem validação backend.

## GSF-MT-003

QuerySets deverão ser limitados ao tenant antes de retornar dados protegidos.

## GSF-MT-004

IDs de objetos deverão ser validados dentro do escopo organizacional.

## GSF-MT-005

Views deverão aplicar escopo multi-tenant.

## GSF-MT-006

Selectors deverão preservar isolamento.

## GSF-MT-007

Services deverão validar coerência entre tenant e recursos.

## GSF-MT-008

Forms deverão limitar opções ao tenant autorizado.

## GSF-MT-009

Relacionamentos entre entidades de tenants diferentes deverão ser impedidos quando inválidos pelo domínio.

## GSF-MT-010

Templates não deverão receber dados de tenants não autorizados.

## GSF-MT-011

Frontend não deverá ser considerado mecanismo de isolamento.

## GSF-MT-012

HTMX deverá aplicar os mesmos controles multi-tenant das demais requisições.

## GSF-MT-013

APIs deverão filtrar objetos pelo tenant antes da serialização.

## GSF-MT-014

Tasks deverão preservar o tenant correto.

## GSF-MT-015

Automações deverão processar dados por contexto organizacional quando aplicável.

## GSF-MT-016

Caches de conteúdo organizacional deverão incluir tenant em sua estratégia de chave.

## GSF-MT-017

Sessões não deverão manter tenant revogado como válido.

## GSF-MT-018

Relatórios deverão filtrar tenant antes de agregações.

## GSF-MT-019

Dashboards deverão calcular KPIs exclusivamente sobre o escopo autorizado.

## GSF-MT-020

Exportações deverão conter somente registros do tenant autorizado.

## GSF-MT-021

Importações deverão associar dados ao tenant validado pelo servidor.

## GSF-MT-022

Arquivos deverão possuir controle de acesso compatível com o tenant.

## GSF-MT-023

Operações em massa deverão validar todos os registros afetados.

## GSF-MT-024

Buscas globais deverão respeitar o universo autorizado.

## GSF-MT-025

Eventos relevantes deverão registrar o tenant quando aplicável.

## GSF-MT-026

Falha na determinação do tenant deverá resultar em negação.

## GSF-MT-027

Testes entre tenants deverão fazer parte das funcionalidades organizacionais.

## GSF-MT-028

Dados globais deverão ser explicitamente identificados como globais.

## GSF-MT-029

A ausência de campo tenant em uma entidade não deverá ser presumida automaticamente como decisão correta.

## GSF-MT-030

Vazamento entre tenants deverá ser tratado como incidente de segurança.

---

# 83. Anti-Padrões

São considerados anti-padrões:

```text
Objeto.objects.all()
```

em fluxo que deveria ser multi-tenant.

---

```text
Objeto.objects.get(pk=id)
```

sem validação de tenant.

---

```text
tenant = Tenant.objects.get(
    pk=request.POST["tenant_id"]
)
```

seguido de confiança automática.

---

```text
<input type="hidden" name="igreja_id">
```

tratado como autoridade.

---

```text
cache.set(
    "dashboard",
    dados
)
```

para dashboard específico de tenant.

---

```text
Task recebe objeto_id
e não recebe nem valida tenant
```

---

```text
Relatório agrega tudo
e filtra depois
```

---

```text
Exportação usa queryset global
```

---

```text
Template recebe todos os dados
e esconde os não autorizados
```

---

```text
API autentica usuário
e retorna qualquer objeto por ID
```

---

```text
Tenant inexistente ou inválido
→ usar primeiro tenant disponível
```

---

# 84. Checklist

## Request

* [ ] identidade validada;
* [ ] tenant identificado;
* [ ] vínculo do usuário validado;
* [ ] permissão validada.

## Query

* [ ] queryset restrito;
* [ ] selector restrito;
* [ ] manager revisado;
* [ ] IDs dentro do tenant.

## Forms

* [ ] querysets de campos limitados;
* [ ] hidden inputs não confiáveis;
* [ ] foreign keys validadas;
* [ ] relações cruzadas testadas.

## Services

* [ ] tenant explícito quando necessário;
* [ ] recursos coerentes;
* [ ] regra de negócio preserva isolamento.

## Frontend

* [ ] contexto exibido corretamente;
* [ ] frontend não define autorização;
* [ ] URLs manipuladas testadas;
* [ ] payloads manipulados testados.

## HTMX

* [ ] tenant validado;
* [ ] endpoint protegido;
* [ ] IDs testados.

## APIs

* [ ] tenant filtrado;
* [ ] objeto filtrado;
* [ ] campos revisados;
* [ ] listagem cruzada testada;
* [ ] detalhe cruzado testado.

## Cache

* [ ] chave contém tenant;
* [ ] usuário incluído quando necessário;
* [ ] filtros incluídos quando necessário;
* [ ] invalidação correta.

## Tasks

* [ ] tenant preservado;
* [ ] objeto validado;
* [ ] lote isolado;
* [ ] logging contextual.

## Relatórios

* [ ] filtro antes da agregação;
* [ ] KPIs corretos;
* [ ] exportações corretas;
* [ ] outro tenant testado.

## Segurança

* [ ] acesso horizontal negado;
* [ ] IDOR testado;
* [ ] fail closed;
* [ ] vazamento em mensagens revisado;
* [ ] auditoria considerada.

---

# 85. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-02 — Classificação e Proteção da Informação
* GSF-03 — Gestão de Identidade
* GSF-04 — Autorização e Controle de Acesso
* GSF-06 — Segurança da Aplicação
* GSF-07 — Segurança das APIs
* GSF-08 — Segurança de Dados e Privacidade
* GSF-10 — Logging, Monitoramento e Auditoria
* GSF-13 — Gestão de Incidentes de Segurança

## Arquitetura

* GEA-07 — Arquitetura da Segurança
* GEA-08 — Arquitetura Multi-Tenant
* GEA-05 — Arquitetura do Banco de Dados

## Backend

* Models
* Services
* Selectors
* Managers
* Views
* Forms
* Permissions
* Middlewares
* Tasks
* Cache
* Testing

## Governança

* Padrões de Models
* Padrões de Views
* Padrões de Forms
* Padrões de Permissões
* Padrões de Segurança
* Padrões de Testes

---

# 86. Princípios Finais

O isolamento multi-tenant deverá ser tratado como propriedade estrutural da plataforma.

A pergunta:

```text
O usuário possui permissão?
```

é incompleta.

A pergunta correta é:

```text
O usuário possui permissão
para realizar esta operação
sobre este recurso
nesta organização?
```

O fluxo de segurança deverá permanecer:

```text
Identidade
    ↓
Tenant autorizado
    ↓
Permissão
    ↓
Query limitada
    ↓
Recurso validado
    ↓
Regra de negócio
    ↓
Operação
```

Nunca confiar em:

```text
URL
Hidden input
Query string
JavaScript
HTMX
Payload
ID
```

como prova de tenant.

O isolamento deverá existir em:

```text
Views
+
Selectors
+
Services
+
Forms
+
Managers
+
APIs
+
Tasks
+
Cache
+
Relatórios
+
Exports
```

Um único ponto esquecido poderá quebrar a fronteira organizacional.

No GereIgreja, o princípio final é:

```text
Infraestrutura pode ser compartilhada.

Dados privados não.
```

---

# 87. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`05-Seguranca-Multi-Tenant.md`

**Documento**

`GSF-05`

**Código**

`GSF-MULTI-TENANT`

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

`06-Seguranca-da-Aplicacao.md`

**Código do próximo documento**

`GSF-06`

```
```
