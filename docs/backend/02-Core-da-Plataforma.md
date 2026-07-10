Pasta:
docs/backend/

Arquivo:
02-Core-da-Plataforma.md

Documento:
GBE-02

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

# 02 - Core da Plataforma

> "O Core existe para eliminar duplicações, padronizar comportamentos e fornecer uma base sólida para toda a plataforma."

---

# Sumário

1. Objetivo
2. O que é o Core
3. Filosofia do Core
4. Responsabilidades
5. O que pertence ao Core
6. O que NÃO pertence ao Core
7. Arquitetura Geral
8. Estrutura Oficial do Diretório
9. Dependências
10. Fluxo de Utilização
11. Boas Práticas
12. Anti-patterns
13. Evolução do Core
14. Checklist
15. Documentos Relacionados
16. Princípios Finais

---

# 1. Objetivo

O Core representa a camada compartilhada do GereIgreja.

Seu objetivo é fornecer componentes reutilizáveis para toda a plataforma, reduzindo duplicação de código e promovendo padronização entre os módulos.

Todo código presente no Core deverá possuir caráter genérico e reutilizável.

---

# 2. O que é o Core

O Core é um aplicativo interno da plataforma que concentra funcionalidades comuns utilizadas por dois ou mais módulos.

Ele não representa um domínio de negócio.

Seu propósito é oferecer infraestrutura para os demais aplicativos.

Enquanto os Apps implementam funcionalidades da igreja, o Core implementa funcionalidades da plataforma.

---

# 3. Filosofia do Core

O Core deverá permanecer pequeno, organizado e altamente reutilizável.

Cada componente incluído deverá responder à seguinte pergunta:

> "Esta funcionalidade será utilizada por mais de um módulo?"

Se a resposta for negativa, ela não deverá ser movida para o Core.

O crescimento do Core deverá ocorrer de forma criteriosa.

---

# 4. Responsabilidades

O Core poderá conter:

- classes base;
- componentes reutilizáveis;
- mixins;
- helpers;
- utilitários;
- validações genéricas;
- permissões compartilhadas;
- middlewares;
- context processors;
- exceções;
- serviços de infraestrutura;
- template tags;
- componentes administrativos.

O Core nunca deverá conter regras específicas de negócio.

---

# 5. O que pertence ao Core

São exemplos de componentes adequados para o Core:

- BaseModel
- BaseAdmin
- BaseService
- BaseManager
- BaseSelector
- BaseForm
- BaseAPIView
- Permission Mixins
- Audit Helpers
- Date Helpers
- Validators
- Formatadores
- Utilidades para CPF/CNPJ
- Utilidades para CEP
- Máscaras
- Classes de Paginação
- Componentes HTML reutilizáveis
- Tags de Template
- Helpers de Upload
- Sistema de Logs
- Sistema de Auditoria

Todo componente deverá ser independente de um domínio específico.

---

# 6. O que NÃO pertence ao Core

Nunca deverão ser colocados no Core:

- Models específicos;
- Services específicos;
- Views específicas;
- Regras financeiras;
- Regras da Secretaria;
- Regras da Escola Bíblica;
- Regras de Patrimônio;
- Regras de Comunicação;
- Relatórios específicos.

Esses componentes pertencem aos respectivos módulos.

---

# 7. Arquitetura Geral

O Core deverá permanecer na base da arquitetura.

```text
                 GereIgreja

                      │

      ┌───────────────┼───────────────┐

      │               │               │

 Financeiro      Secretaria      Eventos

      │               │               │

      └───────────────┼───────────────┘

                      │

                    Core

                      │

               Django Framework
```

Os Apps dependem do Core.

O Core nunca dependerá dos Apps.

Essa regra é obrigatória.

---

# 8. Estrutura Oficial do Diretório

Estrutura recomendada:

```text
core/

admin/

api/

authentication/

base/

cache/

choices/

constants/

context_processors/

decorators/

exceptions/

fields/

forms/

helpers/

logging/

management/

managers/

middlewares/

mixins/

models/

pagination/

permissions/

selectors/

services/

signals/

storage/

tasks/

templatetags/

tests/

utils/

validators/
```

Nem todos os diretórios serão criados imediatamente.

Eles deverão surgir conforme houver necessidade real.

A estrutura foi planejada para suportar o crescimento da plataforma sem necessidade de reorganizações futuras.

---

# 9. Dependências

O Core poderá depender apenas de:

- Django;
- bibliotecas oficiais da plataforma;
- componentes internos do próprio Core.

É proibido importar componentes de Apps específicos.

Exemplo incorreto:

```python
from apps.financeiro.models import Conta
```

Esse tipo de dependência quebra a arquitetura modular.

---

# 10. Fluxo de Utilização

O fluxo correto de utilização do Core deverá ser:

```text
Apps

↓

Core

↓

Django

↓

Python
```

O fluxo inverso nunca deverá ocorrer.

---

# 11. Boas Práticas

Todo componente do Core deverá:

- possuir responsabilidade única;
- ser reutilizável;
- possuir testes;
- ser documentado;
- evitar dependências desnecessárias;
- utilizar tipagem sempre que possível;
- seguir os padrões oficiais da Engenharia.

O Core deverá representar o mais alto nível de qualidade do projeto.

---

# 12. Anti-patterns

Evitar:

- mover código para o Core apenas para "organizar";
- criar classes gigantes;
- misturar regras de negócio;
- criar dependências circulares;
- adicionar funcionalidades sem reutilização comprovada;
- transformar o Core em um "depósito" de código.

Um Core excessivamente grande torna-se difícil de manter.

---

# 13. Evolução do Core

A evolução do Core deverá ocorrer de forma planejada.

Sempre que um componente passar a ser reutilizado por diversos módulos, sua migração poderá ser considerada.

Toda alteração deverá preservar compatibilidade com os Apps existentes.

---

# 14. Checklist

Antes de adicionar um componente ao Core verificar:

- será utilizado por dois ou mais módulos;
- não pertence a um domínio específico;
- está documentado;
- possui testes;
- segue os padrões oficiais;
- não cria dependências circulares.

---

# 15. Documentos Relacionados

- GEA-03 — Arquitetura dos Módulos
- GEA-10 — Arquitetura do Core
- GQF — GereIgreja Quality Framework
- GDF — GereIgreja Documentation Framework

---

# 16. Princípios Finais

O Core representa a fundação técnica do GereIgreja.

Sua qualidade impacta diretamente toda a plataforma.

Cada componente incluído deverá contribuir para uma arquitetura mais simples, reutilizável e sustentável.

A estabilidade do Core é um dos pilares para a evolução de longo prazo do GereIgreja.
