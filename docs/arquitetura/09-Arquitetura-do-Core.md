Pasta:
docs/arquitetura/

Arquivo:
09-Arquitetura-do-Core.md

Documento:
GEA-09

Framework:
GEA — GereIgreja Engineering Architecture

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 09 - Arquitetura do Core

> "O Core existe para evitar duplicação, centralizar responsabilidades compartilhadas e garantir consistência em toda a plataforma."

---

# Sumário

1. Objetivo
2. O que é o Core
3. Filosofia do Core
4. Responsabilidades
5. O que pertence ao Core
6. O que não pertence ao Core
7. Estrutura Recomendada
8. Organização dos Componentes
9. Fluxo de Utilização
10. Evolução do Core
11. Performance
12. Segurança
13. Checklist
14. Documentos Relacionados
15. Princípios Finais

---

# 1. Objetivo

Este documento estabelece a arquitetura oficial do Core do GereIgreja.

Seu objetivo é definir quais componentes devem ser compartilhados entre os módulos da plataforma, evitando duplicação de código e promovendo reutilização, padronização e facilidade de manutenção.

O Core representa a base comum utilizada por todos os módulos do sistema.

---

# 2. O que é o Core

O Core é o conjunto de componentes reutilizáveis da plataforma.

Ele não representa um módulo de negócio.

Seu papel é oferecer infraestrutura para todos os demais módulos.

Todo componente presente no Core deverá possuir potencial de reutilização.

---

# 3. Filosofia do Core

O Core deverá permanecer:

- pequeno;
- estável;
- reutilizável;
- desacoplado;
- bem documentado.

Seu crescimento deverá ocorrer apenas quando houver necessidade comprovada de compartilhamento entre diferentes módulos.

O Core não deverá concentrar regras específicas de negócio.

---

# 4. Responsabilidades

O Core é responsável por disponibilizar recursos compartilhados para toda a plataforma.

Exemplos:

- classes base;
- mixins;
- utilitários;
- helpers;
- validadores;
- middlewares;
- decorators;
- context processors;
- componentes reutilizáveis;
- configurações globais.

Cada recurso deverá possuir responsabilidade claramente definida.

---

# 5. O que pertence ao Core

Devem permanecer no Core apenas componentes reutilizados por múltiplos módulos.

Exemplos:

- BaseModel;
- BaseService;
- BaseManager;
- BasePermission;
- BaseView;
- utilidades para datas;
- geração de identificadores;
- auditoria;
- logging;
- paginação;
- exportação;
- notificações.

Esses componentes deverão ser independentes de qualquer domínio específico.

---

# 6. O que não pertence ao Core

Não deverão ser adicionados ao Core:

- regras do módulo Financeiro;
- regras da Secretaria;
- regras da EBD;
- regras de Eventos;
- regras da Agenda;
- consultas específicas;
- formulários exclusivos;
- templates de módulos.

Esses elementos deverão permanecer dentro de seus respectivos aplicativos.

---

# 7. Estrutura Recomendada

Estrutura sugerida para o Core:

```text
core/
│
├── admin/
├── auth/
├── decorators/
├── exceptions/
├── helpers/
├── management/
├── middleware/
├── mixins/
├── models/
├── permissions/
├── selectors/
├── services/
├── signals/
├── templatetags/
├── utils/
├── validators/
├── views/
└── widgets/
```

A estrutura poderá evoluir conforme o crescimento da plataforma.

---

# 8. Organização dos Componentes

Cada componente deverá possuir responsabilidade única.

Exemplos:

**Mixins**

Compartilhar comportamentos entre classes.

**Helpers**

Funções auxiliares simples.

**Services**

Serviços reutilizáveis.

**Validators**

Validações genéricas.

**Permissions**

Permissões compartilhadas.

**Middleware**

Processamentos globais da aplicação.

Essa separação facilita manutenção e testes.

---

# 9. Fluxo de Utilização

Todo módulo poderá consumir componentes do Core.

```text
Módulo
   │
   ▼
Core
   │
   ▼
Componente Compartilhado
   │
   ▼
Resultado
```

A dependência deverá ocorrer apenas nesse sentido.

O Core nunca deverá depender dos módulos.

---

# 10. Evolução do Core

Novos componentes somente deverão ser incorporados quando:

- forem reutilizados por mais de um módulo;
- representarem responsabilidade transversal;
- reduzirem duplicação;
- melhorarem a arquitetura.

O Core deverá crescer lentamente.

A simplicidade sempre deverá prevalecer.

---

# 11. Performance

Os componentes compartilhados deverão priorizar eficiência.

Boas práticas:

- baixo acoplamento;
- poucas dependências;
- código reutilizável;
- consultas otimizadas;
- processamento eficiente.

O Core deverá contribuir para o desempenho geral da plataforma.

---

# 12. Segurança

Todo componente do Core deverá seguir os princípios definidos pelo GSF.

Especial atenção para:

- autenticação;
- autorização;
- validações;
- tratamento de erros;
- proteção contra uso indevido.

Como o Core é utilizado por toda a plataforma, falhas nessa camada possuem impacto elevado.

---

# 13. Checklist

Antes de adicionar um novo componente ao Core, verificar:

- será utilizado por mais de um módulo;
- possui responsabilidade genérica;
- não depende de regras de negócio;
- está documentado;
- possui testes previstos;
- segue os padrões da plataforma.

---

# 14. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GEA-04 — Arquitetura do Backend
- GEA-07 — Arquitetura da Segurança
- GDF — Framework de Documentação
- GQF — Framework de Qualidade

---

# 15. Princípios Finais

O Core representa a fundação técnica do GereIgreja.

Seu objetivo é fornecer componentes reutilizáveis, consistentes e independentes, reduzindo duplicação e fortalecendo a arquitetura da plataforma.

Toda evolução deverá preservar simplicidade, baixo acoplamento e alta reutilização.

Um Core pequeno, organizado e bem documentado é essencial para garantir a evolução sustentável do GereIgreja ao longo dos próximos anos.