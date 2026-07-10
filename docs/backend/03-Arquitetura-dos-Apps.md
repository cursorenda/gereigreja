Pasta:
docs/backend/

Arquivo:
03-Arquitetura-dos-Apps.md

Documento:
GBE-03

Seção:
Backend

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 03 - Arquitetura dos Apps

> "Cada App do GereIgreja deve representar um domínio de negócio bem definido, mantendo independência, organização e baixo acoplamento."

---

# Sumário

1. Objetivo
2. Filosofia dos Apps
3. O que é um App
4. Princípios Arquiteturais
5. Tipos de Apps
6. Estrutura Oficial dos Apps
7. Organização dos Diretórios
8. Responsabilidade dos Diretórios
9. Convenções Gerais
10. Fluxo Arquitetural
11. Boas Práticas
12. Anti-patterns
13. Documentos Relacionados
14. Princípios Finais

---

# 1. Objetivo

Este documento estabelece a arquitetura oficial dos Apps Django do GereIgreja.

Seu objetivo é garantir que todos os módulos da plataforma sejam desenvolvidos seguindo a mesma estrutura física, lógica e arquitetural, independentemente do desenvolvedor responsável.

Cada App deverá apresentar organização consistente, alta coesão e baixo acoplamento.

---

# 2. Filosofia dos Apps

No GereIgreja, um App representa um domínio de negócio.

Ele não é apenas uma divisão técnica do projeto.

Cada App deve possuir responsabilidade única e encapsular todas as funcionalidades relacionadas ao seu domínio.

Exemplos:

- Secretaria
- Financeiro
- Eventos
- Escola Bíblica
- Comunicação
- Patrimônio
- Agenda
- Relatórios

Cada domínio deve evoluir de forma independente.

---

# 3. O que é um App

Um App é um módulo funcional da plataforma.

Ele reúne:

- Models;
- Services;
- Selectors;
- Views;
- Forms;
- Templates;
- APIs;
- Permissões;
- Testes;
- Componentes administrativos.

Um App deve conter tudo o que pertence ao seu domínio.

O que for compartilhado entre diversos Apps deverá permanecer no Core.

---

# 4. Princípios Arquiteturais

Todos os Apps deverão respeitar os seguintes princípios.

## Responsabilidade Única

Cada App resolve um único domínio.

---

## Alta Coesão

Todos os componentes internos pertencem ao mesmo contexto de negócio.

---

## Baixo Acoplamento

Apps não deverão depender diretamente uns dos outros.

A comunicação ocorrerá preferencialmente através de:

- Services;
- APIs internas;
- Eventos;
- Componentes compartilhados do Core.

---

## Reutilização

Código compartilhado deverá migrar para o Core.

Duplicação deve ser evitada.

---

## Evolução Independente

Um App deverá poder evoluir sem provocar alterações significativas em outros módulos.

---

# 5. Tipos de Apps

Os Apps do GereIgreja podem ser classificados em quatro categorias.

## Apps de Negócio

Implementam funcionalidades utilizadas pelas igrejas.

Exemplos:

- membros;
- financeiro;
- eventos;
- patrimônio;
- comunicação.

---

## Apps de Infraestrutura

Fornecem recursos para toda a plataforma.

Exemplos:

- core;
- auditoria;
- notificações;
- autenticação.

---

## Apps de Integração

Responsáveis pela comunicação com serviços externos.

Exemplos:

- WhatsApp;
- Google Calendar;
- E-mail;
- SMS;
- APIs externas.

---

## Apps Administrativos

Suporte operacional da plataforma.

Exemplos:

- painel administrativo;
- monitoramento;
- métricas;
- suporte.

---

# 6. Estrutura Oficial dos Apps

Todo App deverá seguir a estrutura oficial.

```text
nome_do_app/

admin/
api/
forms/
models/
permissions/
selectors/
services/
signals/
tests/
urls/
validators/
views/

templates/
static/

apps.py
__init__.py
```

Conforme o crescimento do módulo, novos diretórios poderão ser adicionados, desde que respeitem os padrões oficiais da Engenharia.

---

# 7. Organização dos Diretórios

Cada diretório deverá possuir responsabilidade exclusiva.

Nunca misturar responsabilidades.

Exemplo:

```text
services/

membro_service.py

visitante_service.py

familia_service.py
```

Evitar arquivos excessivamente grandes.

Sempre que necessário dividir por contexto.

---

# 8. Responsabilidade dos Diretórios

| Diretório | Responsabilidade |
|------------|------------------|
| admin | Django Admin |
| api | Endpoints REST |
| forms | Formulários |
| models | Entidades |
| permissions | Regras de autorização |
| selectors | Consultas complexas |
| services | Regras de negócio |
| signals | Eventos |
| tests | Testes |
| urls | Rotas |
| validators | Validações |
| views | Interface Web |
| templates | HTML |
| static | CSS, JS e imagens |

Cada diretório deverá conter apenas arquivos relacionados à sua finalidade.

---

# 9. Convenções Gerais

Todos os Apps deverão seguir convenções padronizadas.

Exemplos:

Classes:

```python
MembroService
```

Arquivos:

```text
membro_service.py
```

Selectors:

```text
membro_selector.py
```

Validators:

```text
cpf_validator.py
```

Views:

```text
membro_views.py
```

A nomenclatura deverá facilitar a localização do código.

---

# 10. Fluxo Arquitetural

Toda requisição deverá seguir o fluxo oficial.

```text
Usuário

↓

URL

↓

View

↓

Permission

↓

Form

↓

Service

↓

Selector

↓

Model

↓

Banco de Dados

↓

Service

↓

View

↓

Template

↓

Resposta
```

Nenhuma etapa deverá ser ignorada sem justificativa técnica.

---

# 11. Boas Práticas

Os Apps deverão:

- possuir responsabilidade única;
- evitar dependências externas desnecessárias;
- utilizar tipagem sempre que possível;
- possuir documentação;
- possuir testes;
- respeitar o GEA;
- respeitar o GAF;
- respeitar o GQF;
- respeitar o GDF.

A consistência entre Apps reduz significativamente o custo de manutenção.

---

# 12. Anti-patterns

Evitar:

- Apps gigantes;
- Services dentro de Views;
- consultas complexas em Templates;
- lógica de negócio em Models;
- dependências circulares;
- código duplicado;
- importações cruzadas desnecessárias.

Esses padrões comprometem a evolução da plataforma.

---

# 13. Documentos Relacionados

- GEA-03 — Arquitetura dos Módulos
- GBE-01 — Estrutura do Projeto
- GBE-02 — Core da Plataforma
- GAF — Authentication Framework
- GQF — Quality Framework

---

# 14. Princípios Finais

Os Apps representam a principal unidade de organização funcional do GereIgreja.

Sua arquitetura deverá permanecer simples, consistente e previsível.

Cada novo módulo deverá parecer uma continuação natural dos módulos existentes, preservando a identidade técnica da plataforma e permitindo sua evolução sustentável ao longo dos anos.

---

# 15. Organização dos Models

O diretório `models/` é responsável por representar as entidades do domínio.

Cada arquivo deverá conter apenas modelos relacionados ao mesmo contexto.

Estrutura recomendada:

```text
models/

__init__.py

membro.py

familia.py

congregacao.py

cargo.py

historico.py
```

### Boas práticas

- Um Model por arquivo (preferencialmente);
- Classes pequenas;
- Métodos relacionados apenas ao próprio domínio;
- Evitar regras complexas;
- Evitar consultas ao banco dentro do Model.

O Model representa dados.

As regras pertencem aos Services.

---

# 16. Organização dos Services

Os Services representam a camada de negócio.

Toda regra importante deverá estar aqui.

Estrutura:

```text
services/

__init__.py

membro_service.py

familia_service.py

cargo_service.py

relatorio_service.py
```

Exemplos de responsabilidades:

- criação;
- atualização;
- exclusão;
- cálculos;
- integrações;
- processamento;
- validações complexas.

Fluxo:

```text
View

↓

Service

↓

Selector

↓

Model
```

Nenhuma View deverá conter regras de negócio.

---

# 17. Organização dos Selectors

Selectors são responsáveis exclusivamente pela leitura de dados.

Estrutura:

```text
selectors/

__init__.py

membro_selector.py

relatorio_selector.py

estatistica_selector.py
```

Responsabilidades:

- consultas complexas;
- filtros;
- agregações;
- otimização;
- paginação.

Selectors nunca deverão:

- alterar registros;
- criar objetos;
- excluir dados.

---

# 18. Organização das Views

As Views coordenam o fluxo da aplicação.

Estrutura:

```text
views/

__init__.py

membro_views.py

familia_views.py

relatorio_views.py
```

Responsabilidades:

- autenticação;
- autorização;
- formulários;
- contexto;
- renderização;
- redirecionamentos.

Fluxo:

```text
URL

↓

View

↓

Service

↓

Template
```

As Views devem permanecer pequenas.

---

# 19. Organização dos Forms

Estrutura:

```text
forms/

__init__.py

membro_form.py

familia_form.py

cargo_form.py
```

Responsabilidades:

- validação inicial;
- widgets;
- mensagens;
- organização visual.

Não implementar regras de negócio.

---

# 20. Organização das URLs

Estrutura:

```text
urls/

__init__.py

web.py

api.py

admin.py
```

O arquivo principal do App deverá importar as rotas específicas.

Exemplo:

```python
urlpatterns = []

urlpatterns += web_urlpatterns
urlpatterns += api_urlpatterns
```

Benefícios:

- organização;
- facilidade de manutenção;
- separação entre Web e API.

---

# 21. Organização das APIs

Quando houver APIs REST.

Estrutura:

```text
api/

serializers.py

views.py

permissions.py

urls.py
```

Responsabilidades:

- Serializers;
- Endpoints;
- Autenticação;
- Versionamento.

As APIs deverão seguir integralmente o documento GEA-06.

---

# 22. Organização das Permissões

Estrutura:

```text
permissions/

__init__.py

membro_permissions.py

financeiro_permissions.py
```

Responsabilidades:

- autorização;
- permissões customizadas;
- regras reutilizáveis.

Nunca espalhar regras de autorização pelas Views.

---

# 23. Organização dos Validators

Estrutura:

```text
validators/

__init__.py

cpf_validator.py

telefone_validator.py

email_validator.py
```

Validações reutilizáveis deverão permanecer neste diretório.

Evitar duplicação.

---

# 24. Organização dos Signals

Estrutura:

```text
signals/

__init__.py

membro_signals.py

financeiro_signals.py
```

Signals deverão ser utilizados apenas para eventos desacoplados.

Exemplos:

- criação de logs;
- notificações;
- auditoria;
- sincronizações.

Nunca utilizar Signals para regras críticas do sistema.

---

# 25. Organização dos Testes

Estrutura recomendada:

```text
tests/

__init__.py

test_models.py

test_services.py

test_selectors.py

test_views.py

test_forms.py

test_permissions.py

test_api.py
```

Para módulos grandes:

```text
tests/

models/

services/

views/

api/

permissions/
```

A organização deverá acompanhar o crescimento do módulo.

---

# 26. Organização dos Arquivos Estáticos

Estrutura:

```text
static/

app/

css/

js/

img/
```

Nunca misturar recursos de módulos diferentes.

---

# 27. Organização dos Templates

Estrutura:

```text
templates/

app/

lista.html

detalhe.html

form.html

componentes/

modais/

emails/
```

Os Templates deverão seguir integralmente o GDS.

---

# 28. Organização do Django Admin

Estrutura:

```text
admin/

__init__.py

membro_admin.py

familia_admin.py

cargo_admin.py
```

Nunca concentrar todo o Admin em um único arquivo.

Cada entidade deverá possuir seu próprio arquivo quando o módulo crescer.

---

# 29. Organização das Tasks

Quando houver processamento assíncrono.

Estrutura:

```text
tasks/

__init__.py

emails.py

relatorios.py

importacoes.py
```

Tasks deverão executar operações demoradas.

Nunca bloquear requisições Web.

---

# 30. Organização dos Managers

Estrutura:

```text
managers/

__init__.py

membro_manager.py
```

Managers deverão conter consultas reutilizáveis diretamente relacionadas ao Model.

Consultas muito complexas deverão migrar para Selectors.

---

# 31. Organização dos Context Processors

Estrutura:

```text
context_processors/

__init__.py

usuario.py

empresa.py

configuracoes.py
```

Utilizar apenas para informações compartilhadas entre diversas telas.

Evitar consultas pesadas.

---

# 32. Organização dos Helpers

Quando realmente necessários.

Estrutura:

```text
helpers/

__init__.py

formatacao.py

datas.py

arquivos.py
```

Helpers deverão permanecer pequenos e reutilizáveis.

Quando crescerem excessivamente, avaliar migração para o Core.

---

# 33. Fluxo Completo de uma Requisição

Toda requisição dentro do GereIgreja deverá seguir o fluxo arquitetural oficial.

```text
                Usuário
                    │
                    ▼
                 URL Router
                    │
                    ▼
                  View
                    │
                    ▼
         Autenticação / Permissões
                    │
                    ▼
                  Form
                    │
                    ▼
                 Service
              ┌──────────┐
              │          │
              ▼          ▼
         Validator   Selector
              │          │
              └────┬─────┘
                   ▼
                 Model
                   │
                   ▼
            Banco de Dados
                   │
                   ▼
                 Service
                   │
                   ▼
                  View
                   │
                   ▼
          Template ou API
                   │
                   ▼
                Usuário
```

Cada camada possui responsabilidades próprias.

Nenhuma camada deverá assumir responsabilidades pertencentes à outra.

---

# 34. Comunicação entre Apps

Os Apps deverão permanecer independentes.

Sempre que houver necessidade de comunicação entre módulos, deverão ser utilizadas as seguintes estratégias.

## Services

A forma preferencial de integração.

Exemplo:

```python
FinanceiroService.registrar_pagamento()
```

---

## APIs Internas

Quando houver necessidade de desacoplamento entre aplicações.

---

## Eventos

Utilizar Signals apenas para eventos não críticos.

Exemplo:

- envio de notificações;
- auditoria;
- atualização de estatísticas.

---

## Core

Componentes compartilhados deverão migrar para o Core.

---

Nunca importar diretamente Models de outro domínio quando existir alternativa arquitetural melhor.

---

# 35. Dependências Permitidas

Um App poderá depender de:

- Django;
- Python;
- Core;
- bibliotecas homologadas;
- APIs oficiais;
- Services de outros Apps (quando necessário).

Fluxo permitido:

```text
App

↓

Core

↓

Django
```

---

# 36. Dependências Proibidas

Não deverão existir:

- dependências circulares;
- importações cruzadas entre Models;
- lógica compartilhada duplicada;
- consultas SQL espalhadas pelo projeto;
- regras de negócio dentro das Views.

Também deverá ser evitado:

```python
Financeiro

↓

Secretaria

↓

Eventos

↓

Financeiro
```

Esse tipo de dependência compromete toda a arquitetura.

---

# 37. Organização de Módulos Grandes

Quando um App crescer significativamente, sua estrutura poderá ser expandida.

Exemplo:

```text
financeiro/

admin/
api/
forms/
models/
permissions/
selectors/
services/
signals/
tasks/
tests/
urls/
validators/
views/

templates/
    contas/
    categorias/
    relatorios/
    dashboard/

static/
    css/
    js/
    img/

docs/
```

O crescimento deverá preservar a organização.

Jamais utilizar arquivos com milhares de linhas.

---

# 38. Exemplo Completo de um App

Estrutura sugerida para o módulo **Membros**.

```text
membros/

admin/

    membro_admin.py
    familia_admin.py

api/

    serializers.py
    views.py
    urls.py

forms/

    membro_form.py
    familia_form.py

models/

    membro.py
    familia.py
    cargo.py
    historico.py

permissions/

    membro_permissions.py

selectors/

    membro_selector.py
    relatorios_selector.py

services/

    membro_service.py
    familia_service.py
    importacao_service.py

validators/

    cpf_validator.py

views/

    membro_views.py
    familia_views.py

urls/

    web.py
    api.py

templates/

    membros/

static/

    membros/

tests/

signals/

apps.py
```

Essa organização deverá servir como referência para todos os novos módulos.

---

# 39. Convenções de Desenvolvimento

Todo App deverá seguir convenções padronizadas.

## Classes

```python
MembroService

MembroSelector

MembroValidator

MembroForm

MembroPermission
```

---

## Arquivos

```text
membro_service.py

membro_selector.py

membro_form.py

membro_views.py
```

---

## Models

Utilizar nomes no singular.

Exemplo:

```python
class Membro
```

---

## Services

Sempre utilizar verbos.

Exemplos:

```python
criar_membro()

atualizar_membro()

desativar_membro()

importar_membros()
```

---

## Selectors

Sempre utilizar nomes que indiquem consulta.

```python
buscar_membros()

listar_ativos()

obter_por_cpf()

listar_por_congregacao()
```

---

# 40. Checklist para Criação de um Novo App

Antes da implementação verificar:

- domínio bem definido;
- nome adequado;
- estrutura oficial criada;
- documentação iniciada;
- URLs organizadas;
- Services planejados;
- Selectors planejados;
- Validators definidos;
- permissões planejadas;
- integração com o Core avaliada;
- testes previstos.

Todo novo módulo deverá nascer seguindo a arquitetura oficial.

---

# 41. Anti-patterns Avançados

Evitar:

- Models gigantes;
- Views com centenas de linhas;
- Services genéricos demais;
- Selectors alterando dados;
- Forms realizando processamento;
- Templates contendo lógica complexa;
- Signals executando regras críticas;
- Dependências circulares;
- Código duplicado.

A simplicidade deverá prevalecer.

---

# 42. Evolução dos Apps

A evolução dos Apps deverá ocorrer continuamente.

Sempre que necessário:

- dividir arquivos;
- criar novos Services;
- criar novos Selectors;
- melhorar testes;
- atualizar documentação.

A evolução deverá preservar compatibilidade e organização.

---

# 43. Checklist de Revisão Arquitetural

Antes da publicação de um módulo verificar:

- arquitetura respeitada;
- diretórios organizados;
- responsabilidades corretas;
- nomenclatura padronizada;
- documentação atualizada;
- testes implementados;
- integração validada;
- permissões revisadas;
- auditoria prevista;
- performance analisada.

---

# 44. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GEA-10 — Arquitetura do Core
- GBE-01 — Estrutura do Projeto
- GBE-02 — Core da Plataforma
- GAF — Authentication Framework
- GQF — Quality Framework
- GDF — Documentation Framework

---

# 45. Princípios Finais

Os Apps representam a principal unidade funcional do GereIgreja.

Sua arquitetura deverá preservar organização, independência, reutilização e simplicidade.

Cada novo módulo deverá integrar-se naturalmente aos demais, respeitando os padrões estabelecidos pela Engenharia da plataforma.

A consistência entre os Apps é um dos principais fatores para garantir que o GereIgreja permaneça sustentável, escalável e de fácil manutenção ao longo dos anos.

Mais importante do que desenvolver rapidamente é desenvolver de forma organizada.

Toda funcionalidade criada hoje deverá continuar compreensível e evolutiva muitos anos no futuro.

