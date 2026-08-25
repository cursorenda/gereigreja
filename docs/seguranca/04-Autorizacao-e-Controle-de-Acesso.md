````markdown
Pasta:

docs/seguranca/

Arquivo:

04-Autorizacao-e-Controle-de-Acesso.md

Documento:

GSF-04

Código:

GSF-AUTHORIZATION

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

# GSF-04 — Autorização e Controle de Acesso

> "Estar autenticado no GereIgreja significa saber quem é o usuário. Estar autorizado significa determinar, com segurança, o que ele pode fazer, sobre quais recursos e em qual contexto organizacional."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel deste Documento
4. Relação com o GAF
5. Relação com Gestão de Identidade
6. Princípios
7. Autenticação versus Autorização
8. Modelo de Autorização do GereIgreja
9. Menor Privilégio
10. Negação por Padrão
11. Permissões
12. Grupos
13. Papéis
14. Escopo Organizacional
15. Tenant
16. Congregação
17. Recurso
18. Operação
19. Regra de Negócio
20. Autorização Efetiva
21. Autorização no Backend
22. Autorização no Frontend
23. Views
24. Services
25. Selectors
26. Managers
27. Forms
28. Templates
29. Django Admin
30. APIs
31. HTMX
32. Tasks e Automações
33. Exportações
34. Relatórios
35. Operações em Massa
36. Operações Críticas
37. Financeiro
38. Secretaria
39. Escola Bíblica
40. Eventos
41. Comunicação
42. Patrimônio
43. Configurações e Administração
44. Permissões de Leitura
45. Permissões de Criação
46. Permissões de Alteração
47. Permissões de Exclusão
48. Permissões Administrativas
49. Permissões de Exportação
50. Permissões Financeiras
51. Alteração de Permissões
52. Concessão de Acesso
53. Revogação de Acesso
54. Expiração e Mudança de Contexto
55. Cache de Permissões
56. Auditoria
57. Logging
58. Acesso Negado
59. Mensagens de Erro
60. Enumeração de Recursos
61. IDOR e Acesso Horizontal
62. Elevação de Privilégio
63. Bypass de Interface
64. Manipulação de URLs
65. Manipulação de Payloads
66. Controle de Acesso em Objetos
67. Testes Positivos
68. Testes Negativos
69. Testes Multi-Tenant
70. Evidências Arquiteturais
71. Especificações Oficiais
72. Anti-Padrões
73. Checklist
74. Documentos Relacionados
75. Princípios Finais
76. Status do Documento

---

# 1. Objetivo

Este documento estabelece o padrão oficial de autorização e controle de acesso do GereIgreja.

Seu objetivo é garantir que toda operação protegida considere, conforme aplicável:

- identidade;
- autenticação;
- status do usuário;
- grupos;
- papéis;
- permissões;
- organização;
- tenant;
- congregação;
- recurso;
- operação;
- regras de negócio.

A autorização deverá impedir tanto acessos indevidos evidentes quanto bypasses obtidos por:

- manipulação de URLs;
- alteração de IDs;
- requisições manuais;
- chamadas diretas a endpoints;
- modificação de payloads;
- acesso entre tenants;
- reaproveitamento indevido de permissões.

---

# 2. Escopo

Este documento aplica-se a:

- Área de Gestão;
- Django Admin;
- Core;
- Secretaria;
- Financeiro;
- Eventos;
- Escola Bíblica;
- Comunicação;
- Patrimônio;
- Relatórios;
- Configurações;
- APIs;
- integrações;
- HTMX;
- automações;
- tarefas;
- exportações;
- operações administrativas;
- ações financeiras.

Aplica-se a qualquer funcionalidade cujo acesso não seja explicitamente público.

---

# 3. Papel deste Documento

O GSF-04 especializa o princípio de controle de acesso definido pelo GereIgreja Security Framework.

Sua posição documental é:

```text
GSF-01 — Fundamentos
        ↓
GSF-02 — Classificação da Informação
        ↓
GSF-03 — Gestão de Identidade
        ↓
GSF-04 — Autorização e Controle de Acesso
        ↓
GSF-05 — Segurança Multi-Tenant
````

O GSF-04 define **quem pode fazer o quê**.

O GSF-05 detalhará **em qual tenant e contexto organizacional esse acesso é válido**.

---

# 4. Relação com o GAF

O GAF — GereIgreja Authentication Framework responde principalmente:

```text
Quem é o usuário?
```

O GSF-04 responde:

```text
O que esse usuário pode fazer?
```

Portanto:

```text
Autenticação
      ≠
Autorização
```

Um usuário autenticado poderá continuar sem permissão para determinada funcionalidade.

---

# 5. Relação com Gestão de Identidade

O GSF-03 estabelece o ciclo de vida da identidade.

A autorização deverá utilizar essa identidade como ponto de partida.

Fluxo:

```text
Identidade
    ↓
Autenticação
    ↓
Status
    ↓
Autorização
    ↓
Escopo
    ↓
Recurso
```

Se a identidade estiver inativa, suspensa ou revogada, o acesso não deverá prosseguir normalmente.

---

# 6. Princípios

A autorização deverá seguir:

* menor privilégio;
* negação por padrão;
* autorização explícita;
* separação de responsabilidades;
* controle no backend;
* isolamento multi-tenant;
* rastreabilidade;
* consistência;
* granularidade proporcional ao risco.

---

# 7. Autenticação versus Autorização

Exemplo:

```text
Usuário autenticado
       ↓
Acessa /financeiro/
       ↓
Possui permissão financeira?
       ├── Não → negar
       └── Sim
             ↓
        Tenant autorizado?
             ├── Não → negar
             └── Sim
                   ↓
              Recurso permitido?
```

A autenticação resolve somente a primeira parte.

---

# 8. Modelo de Autorização do GereIgreja

A autorização efetiva deverá ser entendida conceitualmente como:

```text
Autorização Efetiva
=
Identidade válida
+
Permissão
+
Grupo ou papel aplicável
+
Tenant
+
Escopo organizacional
+
Recurso
+
Operação
+
Regra de negócio
```

Nem toda funcionalidade utilizará todos esses elementos de forma explícita, mas a decisão deverá considerar os que forem relevantes ao domínio.

---

# 9. Menor Privilégio

Usuários deverão receber somente as capacidades necessárias.

Exemplo inadequado:

```text
Usuário precisa consultar relatório
        ↓
recebe acesso administrativo completo
```

Preferir:

```text
Usuário precisa consultar relatório
        ↓
permissão específica de visualização
```

---

# 10. Negação por Padrão

Se não houver regra clara que permita a operação:

```text
NEGAR
```

A aplicação não deverá interpretar ausência de configuração como permissão.

---

# 11. Permissões

Permissões representam capacidades específicas.

Exemplos conceituais:

```text
view
add
change
delete
export
approve
manage
```

O GereIgreja poderá utilizar permissões nativas do Django e controles adicionais conforme a arquitetura real.

Permissões deverão representar ações reais e compreensíveis.

---

# 12. Grupos

Grupos poderão reunir permissões relacionadas a responsabilidades comuns.

Exemplo conceitual:

```text
Grupo Financeiro
    ├── visualizar lançamentos
    ├── cadastrar lançamentos
    └── gerar relatórios
```

A composição real deverá respeitar as regras existentes no GereIgreja.

Grupo não substitui escopo organizacional.

---

# 13. Papéis

Papéis poderão representar conceitos de negócio mais amplos.

Exemplos:

* administrador;
* secretário;
* operador financeiro;
* liderança;
* usuário de módulo.

Papel e grupo não deverão ser tratados automaticamente como sinônimos se a arquitetura distinguir esses conceitos.

---

# 14. Escopo Organizacional

Autorização deverá considerar a organização correta.

Exemplo:

```text
Usuário possui permissão de visualizar membros
                 ↓
         de qual organização?
```

A permissão não deverá ser aplicada fora de seu escopo legítimo.

---

# 15. Tenant

O tenant constitui fronteira de segurança.

Uma permissão válida em um tenant não deverá ser reutilizada automaticamente em outro.

Exemplo:

```text
Usuário
 ├── Igreja A → autorizado
 └── Igreja B → não autorizado
```

A manipulação do identificador da Igreja B não deverá permitir acesso.

---

# 16. Congregação

Quando congregações constituírem subdivisões relevantes de acesso, a autorização deverá considerar esse escopo.

A regra real dependerá do módulo e da arquitetura vigente.

Não deverá ser presumido que acesso à igreja implica acesso irrestrito a todas as congregações em todos os contextos.

---

# 17. Recurso

A autorização deverá considerar o objeto ou conjunto de objetos afetados.

Exemplo:

```text
Pode editar membros?
        ↓
Pode editar este membro?
```

A permissão geral não elimina a necessidade de validar o recurso correto.

---

# 18. Operação

Operações diferentes deverão poder possuir controles diferentes.

```text
Visualizar
Criar
Editar
Excluir
Exportar
Administrar
```

Não deverá existir presunção de que quem pode visualizar também pode alterar.

---

# 19. Regra de Negócio

Mesmo com permissão válida, uma regra de domínio poderá impedir a operação.

Exemplo conceitual:

```text
Usuário possui permissão
        ↓
mas registro está em estado
que não permite alteração
        ↓
operação negada
```

A autorização deverá coexistir com regras de negócio.

---

# 20. Autorização Efetiva

Modelo completo:

```text
Usuário
  ↓
Identidade válida?
  ↓
Autenticado?
  ↓
Ativo?
  ↓
Possui permissão?
  ↓
Tenant permitido?
  ↓
Recurso pertence ao escopo?
  ↓
Regra de negócio permite?
  ↓
Operação autorizada
```

---

# 21. Autorização no Backend

O backend deverá ser a autoridade final.

A autorização poderá ser aplicada em:

* decorators;
* mixins;
* views;
* services;
* selectors;
* permission classes;
* middlewares;
* regras de domínio.

A escolha deverá seguir a arquitetura real do GereIgreja.

---

# 22. Autorização no Frontend

O frontend deverá refletir as permissões para melhorar a experiência.

Exemplos:

```text
Usuário sem permissão de excluir
→ botão Excluir não aparece
```

Entretanto:

```text
botão não aparece
≠
endpoint protegido
```

O endpoint deverá negar a operação independentemente da UI.

---

# 23. Views

Views deverão validar acesso antes de executar operações protegidas.

Exemplo conceitual:

```text
request
  ↓
autenticação
  ↓
permissão
  ↓
tenant
  ↓
objeto
  ↓
ação
```

Nunca buscar objeto globalmente e só depois tentar esconder o resultado.

---

# 24. Services

Services responsáveis por operações críticas deverão preservar regras de autorização ou receber contexto já validado de forma segura, conforme arquitetura definida.

Services não deverão assumir automaticamente que todos os chamadores são confiáveis.

---

# 25. Selectors

Selectors deverão ajudar a restringir consultas ao escopo autorizado.

Exemplo conceitual:

```text
membros_visiveis_para(usuario, tenant)
```

em vez de:

```text
Membro.objects.all()
```

quando a consulta exigir escopo.

---

# 26. Managers

Managers customizados poderão reforçar filtros estruturais quando isso fizer parte da arquitetura.

Entretanto, não deverão ocultar regras críticas de maneira imprevisível.

---

# 27. Forms

Forms não deverão permitir relações que o usuário não possui autorização para selecionar.

Exemplo:

```text
campo Congregação
```

deverá listar apenas opções autorizadas quando aplicável.

A validação final deverá ocorrer no backend.

---

# 28. Templates

Templates poderão usar verificações de permissão para controlar apresentação.

Exemplo conceitual:

```django
{% if perms.app.change_objeto %}
    ...
{% endif %}
```

quando compatível com a implementação.

Isso não deverá substituir a proteção das views.

---

# 29. Django Admin

O Django Admin deverá respeitar controles próprios de:

* acesso;
* grupos;
* permissões;
* objetos;
* ações;
* filtros.

O acesso ao Django Admin deverá ser restrito às identidades explicitamente autorizadas.

---

# 30. APIs

APIs deverão aplicar autorização por endpoint e, quando necessário, por objeto.

Não deverá existir endpoint autenticado que retorne dados de qualquer tenant apenas porque o usuário possui token ou sessão válida.

---

# 31. HTMX

Requests HTMX são requests HTTP normais do ponto de vista de segurança.

Portanto:

```text
hx-get
hx-post
hx-delete
```

não recebem confiança adicional.

A autorização deverá ser idêntica à de requisições convencionais.

---

# 32. Tasks e Automações

Tasks poderão executar operações após o request original.

Deverão preservar contexto suficiente para garantir:

* tenant correto;
* recurso correto;
* identidade originadora quando relevante;
* autorização compatível com a operação.

Não utilizar task para contornar controles existentes.

---

# 33. Exportações

Exportações merecem autorização específica quando possuírem maior impacto.

Exemplo:

```text
Visualizar tabela
≠
exportar todos os registros
```

Exportações podem ampliar o alcance dos dados.

---

# 34. Relatórios

Relatórios deverão utilizar dados filtrados pelo mesmo contexto autorizado.

Relatório não deverá ignorar tenant ou permissões por ser uma visão consolidada.

---

# 35. Operações em Massa

Ações em massa deverão validar cada conjunto de registros afetados.

Exemplo:

```text
Selecionar 20 registros
        ↓
validar escopo de todos
        ↓
executar
```

Não assumir que a seleção do frontend garante legitimidade.

---

# 36. Operações Críticas

Operações críticas poderão exigir controles adicionais.

Exemplos:

* exclusão;
* alteração de permissões;
* administração de usuários;
* estorno;
* exportação;
* alteração de configurações sensíveis.

Os controles deverão ser proporcionais ao risco.

---

# 37. Financeiro

O Financeiro exige atenção especial.

Permissões poderão precisar distinguir:

```text
visualizar
registrar
editar
estornar
relatar
administrar
```

A terminologia e granularidade reais deverão seguir o módulo.

Dados financeiros não deverão ser acessíveis apenas por pertencerem ao mesmo tenant.

---

# 38. Secretaria

A Secretaria processa dados pessoais e administrativos.

Permissões deverão considerar:

* consulta;
* cadastro;
* alteração;
* exclusão ou inativação;
* exportação;
* administração.

---

# 39. Escola Bíblica

A autorização deverá limitar acesso aos dados de:

* turmas;
* alunos;
* professores;
* frequência;

conforme o perfil e contexto definidos pela plataforma.

---

# 40. Eventos

Operações poderão distinguir:

* visualizar;
* criar;
* editar;
* cancelar;
* excluir;
* administrar.

---

# 41. Comunicação

Permissões poderão distinguir ações como:

* criar comunicação;
* editar;
* agendar;
* enviar;
* consultar histórico;
* administrar.

Enviar comunicação deverá possuir controle proporcional ao impacto.

---

# 42. Patrimônio

O módulo deverá utilizar os mesmos princípios de autorização da Área de Gestão.

Nenhuma implementação local deverá ignorar a infraestrutura central de permissões.

---

# 43. Configurações e Administração

Configurações globais ou sensíveis deverão possuir acesso mais restrito.

Exemplos:

* permissões;
* usuários;
* integrações;
* parâmetros institucionais;
* configurações de segurança.

---

# 44. Permissões de Leitura

Visualização deverá ser controlada quando o conteúdo não for público.

A leitura poderá parecer inofensiva, mas poderá expor dados confidenciais.

---

# 45. Permissões de Criação

Criar registros poderá afetar:

* integridade;
* relatórios;
* financeiro;
* comunicação;
* auditoria.

Portanto, criação deverá possuir autorização adequada.

---

# 46. Permissões de Alteração

Alterações poderão possuir impacto maior que leitura.

A aplicação deverá verificar tanto permissão quanto escopo do objeto alterado.

---

# 47. Permissões de Exclusão

Exclusão deverá possuir autorização específica quando o risco justificar.

Excluir e inativar não deverão ser tratados automaticamente como a mesma operação.

---

# 48. Permissões Administrativas

Capacidades administrativas deverão ser concedidas com parcimônia.

Anti-padrão:

```text
problema operacional
      ↓
dar admin
```

---

# 49. Permissões de Exportação

Exportação poderá exigir permissão adicional mesmo quando o usuário consegue consultar parte dos dados.

Isso deverá ser definido conforme o risco do módulo.

---

# 50. Permissões Financeiras

Operações financeiras deverão ser particularmente granulares quando necessário.

O princípio é:

```text
acesso financeiro
≠
controle financeiro total
```

---

# 51. Alteração de Permissões

Mudanças em permissões deverão ser controladas.

Quando aplicável, registrar:

```text
Quem alterou?
Quem foi afetado?
Qual permissão mudou?
Quando?
```

---

# 52. Concessão de Acesso

A concessão deverá partir da necessidade funcional.

Não deverá existir prática de conceder grupos amplos apenas para evitar configuração adequada.

---

# 53. Revogação de Acesso

Quando uma permissão deixar de ser necessária, deverá ser removida.

Revogação deverá ser refletida também em caches ou sessões quando a arquitetura utilizar estados derivados de autorização.

---

# 54. Expiração e Mudança de Contexto

Autorização poderá mudar ao longo do tempo.

Exemplos:

* usuário muda de função;
* deixa organização;
* perde acesso a congregação;
* grupo é alterado;
* permissão é revogada.

O sistema não deverá considerar autorização antiga indefinidamente válida.

---

# 55. Cache de Permissões

Se permissões forem armazenadas em cache, deverá existir estratégia segura de invalidação.

Risco:

```text
permissão revogada
       ↓
cache continua permitindo
```

Esse comportamento deverá ser evitado.

---

# 56. Auditoria

Ações de autorização sensíveis poderão gerar evidência de auditoria.

Especial atenção a:

* alterações de grupo;
* permissões;
* elevação de privilégios;
* operações financeiras;
* exportações;
* acessos administrativos.

---

# 57. Logging

Falhas repetidas de autorização poderão ser registradas quando úteis para segurança e monitoramento.

Logs não deverão expor desnecessariamente dados confidenciais.

---

# 58. Acesso Negado

A resposta deverá ser segura e coerente.

Exemplo:

```text
Você não possui permissão para realizar esta ação.
```

Entretanto, quando revelar a existência do recurso for inadequado, o sistema poderá responder de maneira que não permita enumeração.

---

# 59. Mensagens de Erro

Evitar mensagens como:

```text
O membro João da Silva existe,
mas você não pode acessá-lo.
```

quando o usuário não deveria saber da existência desse registro.

---

# 60. Enumeração de Recursos

A aplicação deverá evitar fornecer pistas sobre recursos não autorizados.

Exemplos de risco:

* IDs sequenciais;
* mensagens diferentes;
* status distintos;
* tempos de resposta excessivamente reveladores.

A estratégia deverá ser compatível com a criticidade do recurso.

---

# 61. IDOR e Acesso Horizontal

Um dos riscos críticos em ambientes multi-tenant é o acesso direto inseguro a objetos.

Exemplo inadequado:

```python
obj = Objeto.objects.get(pk=request.GET["id"])
```

sem validar tenant e autorização.

O acesso deverá restringir o queryset ou validar explicitamente o objeto.

---

# 62. Elevação de Privilégio

Um usuário não deverá conseguir aumentar seus próprios privilégios sem autorização.

Exemplos de risco:

* alteração de grupo via payload;
* campo de permissão editável;
* parâmetro de perfil;
* endpoint administrativo desprotegido.

---

# 63. Bypass de Interface

Ações escondidas na interface ainda poderão ser executadas diretamente.

Por isso, deverão ser testados:

```text
POST manual
URL direta
HTMX direto
API direta
payload alterado
```

---

# 64. Manipulação de URLs

URLs deverão ser tratadas como entrada não confiável.

Exemplo:

```text
/igreja/10/membro/50/
```

não deverá ser autorizado apenas porque a URL é válida.

O backend deverá verificar contexto e objeto.

---

# 65. Manipulação de Payloads

Campos enviados pelo cliente poderão ser alterados.

Exemplos:

```text
tenant_id
igreja_id
congregacao_id
user_id
role
group
permission
```

Nenhum desses deverá ser confiado sem validação.

---

# 66. Controle de Acesso em Objetos

Quando a permissão depender do objeto, deverá existir autorização em nível de objeto ou escopo equivalente.

Exemplo:

```text
Usuário pode editar membros
+
este membro pertence ao tenant autorizado
=
pode editar este membro
```

---

# 67. Testes Positivos

Testes deverão verificar usuários legitimamente autorizados.

Exemplos:

```text
usuário autorizado visualiza
usuário autorizado cria
usuário autorizado altera
```

---

# 68. Testes Negativos

Testes negativos são obrigatórios para operações críticas.

Exemplos:

```text
usuário sem permissão
usuário inativo
usuário com grupo incorreto
usuário sem acesso ao recurso
```

---

# 69. Testes Multi-Tenant

Deverão existir testes específicos para tentativas de acesso cruzado.

Exemplo:

```text
Usuário da Igreja A
        ↓
ID da Igreja B
        ↓
acesso deve ser negado
```

Também testar:

* forms;
* selectors;
* APIs;
* exports;
* tasks;
* relatórios.

---

# 70. Evidências Arquiteturais

## EA-GSF-AUTHZ-001

O GSF estabelece grupos, permissões, papéis e escopo organizacional como mecanismos de controle de acesso.

## EA-GSF-AUTHZ-002

O GAF é responsável pela autenticação.

## EA-GSF-AUTHZ-003

O backend possui documentação específica de Permissions.

## EA-GSF-AUTHZ-004

O backend possui documentação específica de Services.

## EA-GSF-AUTHZ-005

O backend possui documentação específica de Selectors.

## EA-GSF-AUTHZ-006

O backend possui documentação específica de Managers.

## EA-GSF-AUTHZ-007

O backend possui documentação específica de Views e Forms.

## EA-GSF-AUTHZ-008

A governança possui padrões específicos de permissões.

## EA-GSF-AUTHZ-009

O GereIgreja possui arquitetura multi-tenant documentada.

## EA-GSF-AUTHZ-010

O projeto possui documentação específica de grupos, permissões e decorators de segurança.

---

# 71. Especificações Oficiais

## GSF-AUTHZ-001

Toda operação protegida deverá possuir autorização no backend.

## GSF-AUTHZ-002

Autenticação não deverá implicar autorização automática.

## GSF-AUTHZ-003

A ausência de autorização válida deverá resultar em negação.

## GSF-AUTHZ-004

Permissões deverão seguir o princípio do menor privilégio.

## GSF-AUTHZ-005

Grupos não deverão substituir validação de tenant.

## GSF-AUTHZ-006

Papéis não deverão conceder acesso fora do escopo permitido.

## GSF-AUTHZ-007

Identificadores fornecidos pelo cliente deverão ser validados.

## GSF-AUTHZ-008

Controles visuais não deverão substituir controles no servidor.

## GSF-AUTHZ-009

Views deverão proteger operações antes de executá-las.

## GSF-AUTHZ-010

Selectors deverão limitar dados ao escopo autorizado quando aplicável.

## GSF-AUTHZ-011

Services não deverão assumir chamadores confiáveis sem contrato explícito.

## GSF-AUTHZ-012

Forms deverão limitar opções ao escopo autorizado quando aplicável.

## GSF-AUTHZ-013

Django Admin deverá possuir acesso explicitamente controlado.

## GSF-AUTHZ-014

APIs deverão aplicar autorização por endpoint e recurso quando necessário.

## GSF-AUTHZ-015

Requests HTMX deverão seguir exatamente os mesmos controles de autorização das demais requisições HTTP.

## GSF-AUTHZ-016

Tasks deverão preservar tenant e contexto apropriados.

## GSF-AUTHZ-017

Exports deverão possuir autorização compatível com seu impacto.

## GSF-AUTHZ-018

Relatórios deverão respeitar permissões e tenant.

## GSF-AUTHZ-019

Operações em massa deverão validar todo o conjunto afetado.

## GSF-AUTHZ-020

Operações críticas deverão possuir controles proporcionais ao risco.

## GSF-AUTHZ-021

Alterações de permissões relevantes deverão ser auditáveis quando aplicável.

## GSF-AUTHZ-022

Caches de autorização deverão ser invalidados após revogação quando existirem.

## GSF-AUTHZ-023

A aplicação deverá reduzir riscos de enumeração de recursos.

## GSF-AUTHZ-024

Acesso direto a objetos deverá validar escopo e autorização.

## GSF-AUTHZ-025

Testes deverão incluir cenários negativos e multi-tenant.

## GSF-AUTHZ-026

Usuários não deverão conseguir elevar os próprios privilégios sem autorização específica.

## GSF-AUTHZ-027

Permissão de visualização não deverá implicar permissão de alteração.

## GSF-AUTHZ-028

Permissão de módulo não deverá implicar acesso administrativo completo.

## GSF-AUTHZ-029

Permissão de acesso a um tenant não deverá ser reutilizada em outro.

## GSF-AUTHZ-030

A autorização efetiva deverá considerar regras de negócio relevantes.

---

# 72. Anti-Padrões

São considerados anti-padrões:

```text
@login_required
=
segurança completa
```

---

```text
if user.is_authenticated:
    permitir()
```

---

```text
if user.is_staff:
    permitir_tudo()
```

sem análise de escopo.

---

```text
Botão escondido
=
endpoint protegido
```

---

```text
tenant_id recebido
=
tenant autorizado
```

---

```text
Membro.objects.get(pk=id)
```

sem restringir escopo.

---

```text
Usuário pode visualizar
=
usuário pode exportar
```

---

```text
Usuário pertence ao grupo Financeiro
=
pode estornar qualquer lançamento
```

---

```text
Permissão revogada
+
cache antigo
=
acesso continua
```

---

```text
Endpoint HTMX
=
endpoint interno
=
não precisa autorização
```

---

```text
Task executa fora do request
=
não precisa validar tenant
```

---

# 73. Checklist

## Identidade

* [ ] usuário identificado;
* [ ] status válido;
* [ ] autenticação aplicada quando necessária.

## Permissões

* [ ] permissão correta definida;
* [ ] menor privilégio;
* [ ] leitura separada de alteração;
* [ ] exclusão separada quando necessário;
* [ ] exportação revisada;
* [ ] administração revisada.

## Tenant

* [ ] tenant identificado;
* [ ] vínculo validado;
* [ ] recurso pertence ao tenant;
* [ ] manipulação de tenant testada.

## Backend

* [ ] view protegida;
* [ ] selector limitado;
* [ ] service revisado;
* [ ] form limitado;
* [ ] manager revisado quando aplicável.

## Frontend

* [ ] ações indisponíveis não são exibidas;
* [ ] frontend não é considerado autoridade;
* [ ] payloads manipulados testados.

## APIs

* [ ] endpoint autorizado;
* [ ] objeto autorizado;
* [ ] tenant validado;
* [ ] campos retornados revisados.

## HTMX

* [ ] mesma autorização da view convencional;
* [ ] POST manual testado;
* [ ] URLs manipuladas testadas.

## Financeiro

* [ ] visualização;
* [ ] criação;
* [ ] edição;
* [ ] estorno;
* [ ] relatórios;
* [ ] administração.

## Administração

* [ ] alteração de usuários controlada;
* [ ] alteração de grupos controlada;
* [ ] permissões controladas;
* [ ] Django Admin controlado.

## Auditoria

* [ ] alterações relevantes registradas;
* [ ] elevação de privilégios rastreável;
* [ ] revogações relevantes rastreáveis.

## Testes

* [ ] usuário autorizado;
* [ ] usuário sem permissão;
* [ ] usuário inativo;
* [ ] outro tenant;
* [ ] ID manipulado;
* [ ] payload manipulado;
* [ ] URL direta;
* [ ] operação em massa;
* [ ] exportação.

---

# 74. Documentos Relacionados

## Frameworks

* GSF — GereIgreja Security Framework
* GAF — GereIgreja Authentication Framework
* GQF — GereIgreja Quality Framework

## Segurança

* GSF-01 — Fundamentos de Segurança
* GSF-02 — Classificação e Proteção da Informação
* GSF-03 — Gestão de Identidade
* GSF-05 — Segurança Multi-Tenant
* GSF-06 — Segurança da Aplicação
* GSF-07 — Segurança das APIs
* GSF-10 — Logging, Monitoramento e Auditoria

## Arquitetura

* GEA-07 — Arquitetura da Segurança
* GEA-08 — Arquitetura Multi-Tenant

## Backend

* Services
* Selectors
* Managers
* Views
* Forms
* Permissions
* Middlewares
* Testing

## Governança

* Padrões de Permissões
* Padrões de Segurança
* Padrões de Django Admin
* Padrões de Views
* Padrões de Forms
* Padrões de Testes

---

# 75. Princípios Finais

A autorização no GereIgreja deverá responder corretamente a cinco perguntas:

```text
Quem?
+
Pode fazer o quê?
+
Sobre qual recurso?
+
Em qual organização?
+
Em qual contexto?
```

A decisão nunca deverá se resumir a:

```text
está logado?
```

O modelo correto é:

```text
Identidade válida
      +
Permissão
      +
Escopo
      +
Tenant
      +
Recurso
      +
Regra de negócio
      =
Autorização efetiva
```

O frontend deverá refletir a autorização.

O backend deverá aplicá-la.

Selectors deverão limitar dados.

Services deverão respeitar regras de domínio.

Forms deverão impedir relações fora do escopo.

APIs deverão validar acesso por recurso.

HTMX deverá utilizar exatamente os mesmos controles.

Tasks deverão preservar contexto.

Relatórios e exports deverão obedecer às mesmas fronteiras de segurança.

A regra final é:

```text
Nunca confiar
na possibilidade de o usuário
não encontrar o endpoint.
```

Todo endpoint protegido deverá continuar seguro mesmo quando acessado diretamente.

---

# 76. Status do Documento

**Pasta**

`docs/seguranca/`

**Arquivo**

`04-Autorizacao-e-Controle-de-Acesso.md`

**Documento**

`GSF-04`

**Código**

`GSF-AUTHORIZATION`

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

`05-Seguranca-Multi-Tenant.md`

**Código do próximo documento**

`GSF-05`

```
```
