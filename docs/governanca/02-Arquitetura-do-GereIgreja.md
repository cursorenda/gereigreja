# 02 - Arquitetura do GereIgreja

> "A arquitetura não define apenas como o sistema funciona. Ela define como ele continuará evoluindo pelos próximos anos."

---

# Sumário

1. Objetivo
2. Visão Geral da Arquitetura
3. Princípios Arquiteturais
4. Arquitetura em Camadas
5. Organização do Projeto
6. Organização dos Apps
7. Fluxo da Requisição
8. Core da Plataforma
9. Arquitetura dos Módulos
10. GereIgreja Operations Center (GOC)
11. GereIgreja Design System (GDS)
12. Banco de Dados
13. Armazenamento
14. Segurança
15. Performance
16. Escalabilidade
17. Observabilidade
18. Integrações
19. Inteligência Artificial
20. Roadmap Arquitetural
21. Checklist Arquitetural
22. Princípios Finais

---

# 1. Objetivo

Este documento define oficialmente a arquitetura do GereIgreja.

Seu propósito é estabelecer uma base técnica sólida para orientar o desenvolvimento, a evolução e a manutenção da plataforma.

Toda decisão arquitetural deverá estar alinhada aos princípios definidos neste documento.

A arquitetura existe para garantir:

- organização;
- previsibilidade;
- escalabilidade;
- segurança;
- reutilização;
- facilidade de manutenção;
- evolução contínua.

Este documento representa a principal referência técnica da plataforma.

---

# 2. Visão Geral da Arquitetura

O GereIgreja foi concebido como uma plataforma SaaS moderna, modular e escalável.

Sua arquitetura busca equilibrar simplicidade, desempenho e facilidade de evolução.

Os principais pilares são:

- Django como framework principal;
- arquitetura modular baseada em Apps;
- separação entre regras de negócio e interface;
- centralização dos componentes compartilhados;
- documentação como parte integrante do desenvolvimento;
- padronização visual através do GereIgreja Design System (GDS);
- administração centralizada pelo GereIgreja Operations Center (GOC).

Toda a plataforma deverá crescer preservando esses pilares.

---

# 3. Princípios Arquiteturais

Toda evolução do GereIgreja deverá respeitar os seguintes princípios.

## Simplicidade

A solução mais simples será sempre priorizada.

Complexidade somente será aceita quando produzir benefícios claros.

---

## Organização

Cada responsabilidade deverá possuir um local específico dentro da arquitetura.

Arquivos, módulos e componentes deverão permanecer organizados.

---

## Baixo Acoplamento

Os módulos deverão depender o mínimo possível entre si.

Integrações deverão ocorrer por meio de Services, APIs internas ou componentes compartilhados.

---

## Alta Coesão

Cada módulo deverá resolver um único domínio de negócio.

Misturar responsabilidades reduz a qualidade da arquitetura.

---

## Reutilização

Código duplicado deverá ser evitado.

Sempre que possível utilizar:

- Services;
- Mixins;
- Validators;
- Helpers;
- Componentes reutilizáveis;
- Classes Base.

---

## Escalabilidade

Toda decisão deverá considerar o crescimento futuro da plataforma.

Novos módulos deverão ser adicionados sem comprometer os existentes.

---

## Documentação

Toda funcionalidade importante deverá possuir documentação correspondente.

A documentação faz parte da engenharia.

---

# 4. Arquitetura em Camadas

A arquitetura oficial do GereIgreja é organizada em camadas.

```text
                Usuário
                   │
                   ▼
             Interface (Templates)
                   │
                   ▼
              Views / URLs
                   │
                   ▼
         Permissions / Forms
                   │
                   ▼
               Services
                   │
                   ▼
        Selectors / Managers
                   │
                   ▼
                Models
                   │
                   ▼
            Banco de Dados
```

Cada camada possui responsabilidades bem definidas.

Nenhuma camada deverá assumir responsabilidades pertencentes a outra.

---

# 5. Organização do Projeto

A estrutura principal do GereIgreja deverá permanecer organizada e previsível.

Estrutura simplificada:

```text
gereigreja/

├── apps/
├── core/
├── config/
├── templates/
├── static/
├── media/
├── docs/
├── requirements/
├── scripts/
├── tests/
└── manage.py
```

Cada diretório possui uma responsabilidade específica.

O crescimento da plataforma deverá preservar essa organização.

---

# 6. Organização dos Apps

Cada domínio funcional será implementado como um App Django independente.

Exemplos:

```text
apps/

├── membros/
├── financeiro/
├── eventos/
├── comunicacao/
├── agenda/
├── patrimonio/
├── secretaria/
├── blog/
├── site/
└── autenticacao/
```

Todos os Apps deverão seguir o padrão oficial definido no documento **03 - Arquitetura dos Módulos**.

Cada App deverá possuir:

- responsabilidade única;
- baixo acoplamento;
- alta coesão;
- documentação própria;
- testes automatizados sempre que possível.

Nenhum App deverá crescer de forma desorganizada.

Quando um domínio se tornar excessivamente grande, sua divisão em novos módulos deverá ser considerada.

---

## Continuação

Os próximos capítulos abordarão:

- Fluxo completo da requisição;
- Organização do Core;
- Arquitetura dos módulos;
- GOC (GereIgreja Operations Center);
- GDS (GereIgreja Design System);
- Banco de Dados;
- Segurança;
- Performance;
- Escalabilidade;
- Observabilidade;
- Inteligência Artificial;
- Roadmap Arquitetural;
- Checklist oficial da Engenharia.

---

# 7. Fluxo da Requisição

Toda requisição realizada no GereIgreja deverá seguir um fluxo arquitetural padronizado.

Nenhuma funcionalidade deverá ignorar esse fluxo sem justificativa técnica.

Fluxo oficial:

```text
                Usuário
                    │
                    ▼
                 Browser
                    │
                    ▼
                 URLConf
                    │
                    ▼
                  View
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
Permissions               Form Validation
        │                       │
        └───────────┬───────────┘
                    ▼
                 Service
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
     Selector               Manager
        │                       │
        └───────────┬───────────┘
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
                Template
                    │
                    ▼
              Resposta HTTP
```

Cada camada possui responsabilidades específicas.

A comunicação deverá ocorrer apenas entre camadas vizinhas.

Esta organização reduz acoplamento e facilita manutenção.

---

# 8. Core da Plataforma

O diretório **core/** representa a infraestrutura compartilhada do GereIgreja.

Nenhuma regra de negócio específica deverá permanecer no Core.

Seu objetivo é disponibilizar recursos reutilizáveis para toda a plataforma.

Estrutura sugerida:

```text
core/

├── admin/
├── auth/
├── cache/
├── constants/
├── context_processors/
├── decorators/
├── exceptions/
├── helpers/
├── logging/
├── management/
├── middleware/
├── mixins/
├── permissions/
├── services/
├── signals/
├── storage/
├── templates/
├── templatetags/
├── validators/
└── utils/
```

O Core deverá crescer lentamente.

Sempre que uma funcionalidade puder ser utilizada por mais de um módulo, deverá ser avaliada sua migração para o Core.

---

## O que pertence ao Core

Exemplos:

- autenticação compartilhada;
- componentes reutilizáveis;
- classes base;
- mixins;
- middlewares;
- decorators;
- sistema de permissões;
- auditoria;
- helpers;
- utilidades;
- cache;
- infraestrutura.

---

## O que NÃO pertence ao Core

Nunca deverão permanecer no Core:

- regras do Financeiro;
- regras da Secretaria;
- regras de Eventos;
- regras da Escola Bíblica;
- regras do Blog;
- regras específicas de qualquer módulo.

O Core não representa um módulo de negócio.

Ele representa a infraestrutura da plataforma.

---

# 9. Arquitetura dos Módulos

Cada módulo deverá representar um domínio específico.

Exemplo:

```text
apps/

├── membros/
├── financeiro/
├── secretaria/
├── eventos/
├── patrimonio/
├── agenda/
├── comunicacao/
├── blog/
├── site/
└── autenticacao/
```

Todos deverão seguir exatamente a mesma arquitetura.

Exemplo interno:

```text
financeiro/

├── admin.py
├── apps.py
├── forms.py
├── managers.py
├── models.py
├── permissions.py
├── selectors.py
├── services.py
├── signals.py
├── urls.py
├── validators.py
├── views.py
├── tests.py
├── templates/
├── static/
└── migrations/
```

A padronização reduz curva de aprendizado.

Todo desenvolvedor deverá conseguir navegar por qualquer módulo sem dificuldades.

---

## Dependências entre módulos

A comunicação deverá ocorrer prioritariamente por:

- Services;
- APIs internas;
- Selectors;
- Eventos;
- Sinais (quando apropriado).

Dependências diretas entre Models deverão ser evitadas sempre que possível.

---

# 10. GereIgreja Operations Center (GOC)

O GOC representa o centro operacional da plataforma.

Ele corresponde ao conjunto de funcionalidades administrativas responsáveis pela gestão do SaaS.

O GOC é implementado sobre o Django Admin, acrescido de funcionalidades próprias do GereIgreja.

Entre suas responsabilidades estão:

- administração da plataforma;
- monitoramento;
- suporte;
- auditoria;
- gestão de clientes;
- acompanhamento de métricas;
- engenharia;
- manutenção operacional.

O GOC não substitui o sistema utilizado pelas igrejas.

Seu público é composto por:

- administradores da plataforma;
- equipe de suporte;
- desenvolvedores;
- operadores internos.

---

## Áreas do GOC

O painel administrativo deverá ser organizado por grandes áreas.

Exemplo:

```text
GOC

├── Dashboard
├── Operação
├── Igrejas
├── Usuários
├── Financeiro
├── Blog
├── SEO
├── Auditoria
├── Engenharia
├── Monitoramento
├── Configurações
└── Segurança
```

Cada área deverá possuir organização consistente.

---

# 11. GereIgreja Design System (GDS)

Toda interface do GereIgreja deverá seguir integralmente o GereIgreja Design System.

O GDS representa a identidade visual oficial da plataforma.

Ele define:

- cores;
- tipografia;
- componentes;
- espaçamentos;
- formulários;
- tabelas;
- botões;
- badges;
- alertas;
- cards;
- navegação;
- menus;
- responsividade.

Nenhum módulo poderá criar sua própria identidade visual.

---

## Estrutura do GDS

```text
static/

└── css/

    ├── design_system.css
    ├── components/
    ├── utilities/
    └── themes/
```

Todos os componentes deverão consumir os tokens oficiais do Design System.

---

# 12. Banco de Dados

O GereIgreja utiliza o banco de dados como camada persistente da plataforma.

A modelagem deverá seguir princípios de normalização, simplicidade e desempenho.

Toda entidade deverá representar claramente um conceito do domínio.

Boas práticas:

- nomes consistentes;
- índices quando necessários;
- constraints explícitas;
- relacionamentos claros;
- migrations organizadas;
- campos documentados.

A evolução do banco deverá ocorrer exclusivamente por meio de migrations oficiais.

Nenhuma alteração manual deverá ser realizada em ambientes de produção.

---

# 13. Armazenamento

Os arquivos da plataforma deverão permanecer separados dos dados estruturados.

Categorias:

- uploads dos usuários;
- documentos;
- imagens;
- backups;
- arquivos temporários;
- relatórios exportados.

Estrutura sugerida:

```text
media/

├── igrejas/
├── membros/
├── documentos/
├── uploads/
├── relatorios/
└── temporarios/
```

O armazenamento deverá ser organizado para facilitar backup, restauração e futura migração para serviços externos quando necessário.

---

