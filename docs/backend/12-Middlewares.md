Pasta:
docs/backend/

Arquivo:
12-Middlewares.md

Documento:
GBE-12

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

# 12 - Middlewares

> *"Um Middleware deve interceptar o fluxo da aplicação, nunca assumir responsabilidades de negócio."*

---

# Sumário

1. Objetivo
2. Filosofia dos Middlewares
3. O Papel dos Middlewares no GereIgreja
4. Fluxo de Execução
5. Responsabilidades
6. O que NÃO deve existir em um Middleware
7. Estrutura Oficial
8. Organização dos Middlewares
9. Ordem de Execução
10. Documentos Relacionados
11. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação, organização e utilização de Middlewares no Backend do GereIgreja.

Seu propósito é garantir que funcionalidades transversais da plataforma sejam implementadas de forma padronizada, desacoplada e reutilizável.

Middlewares não pertencem ao domínio de negócio.

Eles pertencem à infraestrutura da aplicação.

---

# 2. Filosofia dos Middlewares

Middlewares existem para interceptar o ciclo de vida de uma requisição.

Eles podem:

- analisar;
- modificar;
- bloquear;
- complementar;

uma requisição ou resposta.

Nunca devem conter regras de negócio.

Seu papel é fornecer serviços transversais utilizados por toda a plataforma.

---

# 3. O Papel dos Middlewares no GereIgreja

No GereIgreja, os Middlewares são responsáveis por funcionalidades que afetam toda a aplicação.

Exemplos:

- autenticação complementar;
- identificação do tenant;
- auditoria;
- logs;
- segurança;
- métricas;
- internacionalização;
- contexto global;
- rastreamento de requisições.

Sempre que uma funcionalidade precisar atuar antes ou depois das Views, deve-se avaliar o uso de um Middleware.

---

# 4. Fluxo de Execução

O ciclo oficial de uma requisição é:

```text
Cliente

↓

Servidor Web

↓

Middleware 1

↓

Middleware 2

↓

Middleware 3

↓

URL Dispatcher

↓

View

↓

Service

↓

Model

↓

Banco de Dados

↓

Response

↓

Middleware 3

↓

Middleware 2

↓

Middleware 1

↓

Cliente
```

Todo Middleware participa tanto da entrada quanto da saída da requisição.

---

# 5. Responsabilidades

Um Middleware pode:

- adicionar informações ao request;
- adicionar informações ao response;
- registrar logs;
- validar contexto;
- identificar organização;
- medir tempo de execução;
- verificar cabeçalhos;
- aplicar políticas globais;
- interceptar exceções.

Cada Middleware deverá possuir apenas uma responsabilidade.

---

# 6. O que NÃO deve existir em um Middleware

É proibido implementar:

- regras financeiras;
- regras ministeriais;
- cálculos de negócio;
- envio de mensagens;
- consultas complexas;
- manipulação de formulários;
- renderização de templates;
- decisões específicas de módulos.

Essas responsabilidades pertencem aos Services e demais camadas do domínio.

---

# 7. Estrutura Oficial

Os Middlewares deverão permanecer organizados em um pacote dedicado.

Exemplo:

```text
core/

middlewares/

__init__.py

tenant.py

auditoria.py

request_id.py

security.py

performance.py

timezone.py
```

Cada arquivo deverá conter apenas um Middleware principal.

---

# 8. Organização dos Middlewares

Os Middlewares deverão ser classificados conforme sua responsabilidade.

### Contexto

Responsáveis por preparar informações globais.

Exemplos:

- tenant;
- igreja ativa;
- congregação ativa;
- idioma.

---

### Segurança

Responsáveis por políticas globais.

Exemplos:

- CSP;
- Headers;
- CSRF complementar;
- bloqueios.

---

### Observabilidade

Responsáveis por monitoramento.

Exemplos:

- Request ID;
- métricas;
- logs;
- auditoria.

---

### Performance

Responsáveis por medições.

Exemplos:

- tempo de resposta;
- consumo;
- profiling.

---

# 9. Ordem de Execução

A ordem dos Middlewares influencia diretamente o comportamento da aplicação.

A sequência deverá seguir uma lógica previsível.

Exemplo:

1. Segurança
2. Sessão
3. Autenticação
4. Tenant
5. Contexto
6. Auditoria
7. Performance
8. Logs

Alterações nessa ordem deverão ser cuidadosamente avaliadas e documentadas.

---

# 10. Documentos Relacionados

- GEA-03 — Arquitetura do Backend
- GSF — GereIgreja Security Framework
- GOC — GereIgreja Operations Center
- GBE-05 — Services
- GBE-08 — Views

---

# 11. Princípios Finais

Middlewares existem para implementar comportamentos globais da plataforma.

Eles devem permanecer simples, independentes e focados em infraestrutura.

Quando corretamente utilizados, reduzem duplicação, aumentam a organização do código e fortalecem a arquitetura do GereIgreja.

---

# 12. Middlewares Oficiais do GereIgreja

A plataforma deverá possuir um conjunto oficial de Middlewares responsáveis por funcionalidades transversais.

Cada Middleware deverá possuir responsabilidade única.

A inclusão de novos Middlewares deverá ser cuidadosamente avaliada para evitar aumento desnecessário da complexidade do fluxo de requisições.

---

# 13. TenantMiddleware

Responsável por identificar o tenant ativo da requisição.

Suas responsabilidades incluem:

- identificar o ministério;
- identificar a igreja;
- identificar a congregação;
- disponibilizar essas informações durante todo o ciclo da requisição.

Exemplo:

```text
Request

↓

TenantMiddleware

↓

request.tenant

↓

Views

↓

Services
```

Nenhuma regra de negócio deverá ser executada neste Middleware.

---

# 14. OrganizationContextMiddleware

Responsável por preparar o contexto organizacional da aplicação.

Exemplo:

```python
request.ministerio

request.igreja

request.congregacao

request.usuario
```

Esse contexto poderá ser utilizado pelas Views, Templates e Services.

---

# 15. RequestIDMiddleware

Cada requisição deverá receber um identificador único.

Exemplo:

```text
REQ-8D7A91C4
```

Esse identificador facilitará:

- auditoria;
- rastreamento;
- análise de erros;
- correlação de logs.

Sempre que possível, o Request ID deverá acompanhar toda a execução da requisição.

---

# 16. AuditMiddleware

Responsável por registrar eventos relevantes da plataforma.

Exemplos:

- login;
- logout;
- alteração de permissões;
- criação de usuários;
- exclusões;
- exportações;
- alterações financeiras.

O Middleware apenas registra eventos.

As regras de auditoria permanecem desacopladas.

---

# 17. PerformanceMiddleware

Responsável por medir o desempenho das requisições.

Exemplo:

```text
Tempo total

Consultas SQL

Tempo de renderização

Tempo dos Services
```

Essas informações poderão alimentar métricas e monitoramento.

Nunca utilizar esse Middleware para otimizações específicas de módulos.

---

# 18. SecurityHeadersMiddleware

Responsável por adicionar cabeçalhos globais de segurança.

Exemplos:

- Content-Security-Policy
- X-Frame-Options
- Referrer-Policy
- Permissions-Policy
- X-Content-Type-Options

Esse Middleware complementa as configurações do Django.

---

# 19. SubscriptionMiddleware

Aplicável ao modelo SaaS do GereIgreja.

Responsável por identificar:

- plano contratado;
- validade da assinatura;
- bloqueios administrativos;
- suspensão da conta.

Esse Middleware apenas disponibiliza o contexto.

A lógica de cobrança permanece em Services.

---

# 20. FeatureFlagMiddleware

Responsável por disponibilizar funcionalidades experimentais.

Exemplo:

```text
Plano Premium

↓

Nova funcionalidade habilitada
```

ou

```text
Versão Beta

↓

Módulo experimental disponível
```

As Feature Flags facilitam implantações graduais.

---

# 21. TimezoneMiddleware

Responsável por definir o fuso horário da requisição.

Poderá considerar:

- configuração do sistema;
- configuração do ministério;
- configuração do usuário.

Toda manipulação de datas deverá respeitar esse contexto.

---

# 22. LocaleMiddleware

Responsável pela internacionalização da plataforma.

Mesmo que inicialmente o GereIgreja opere apenas em português, a arquitetura deverá permanecer preparada para múltiplos idiomas.

---

# 23. LoggingMiddleware

Responsável por registrar informações técnicas da requisição.

Exemplos:

- método HTTP;
- URL;
- IP;
- navegador;
- sistema operacional;
- tempo de resposta;
- status HTTP.

Esses registros apoiam monitoramento e diagnóstico.

---

# 24. Middleware x Signals

Não confundir responsabilidades.

Middleware:

- atua durante requisições HTTP.

Signals:

- atuam durante eventos do domínio.

Exemplo:

```text
HTTP Request

↓

Middleware

↓

View

↓

Service

↓

Model.save()

↓

Signal
```

Cada mecanismo possui responsabilidades distintas.

---

# 25. Middleware x Services

Services implementam regras de negócio.

Middlewares implementam infraestrutura.

Nunca utilizar Middlewares para:

- cálculos;
- pagamentos;
- regras ministeriais;
- envio de mensagens;
- geração de documentos.

---

# 26. Middleware x Decorators

Decorators atuam sobre Views específicas.

Middlewares atuam sobre toda a aplicação.

Pergunta orientadora:

"A funcionalidade deve ocorrer em todas as requisições?"

Se a resposta for "sim", avaliar um Middleware.

Caso contrário, utilizar Decorators ou outras abordagens.

---

# 27. Boas Práticas

Sempre:

- responsabilidade única;
- baixo acoplamento;
- alta reutilização;
- independência entre Middlewares;
- configuração centralizada;
- documentação atualizada;
- testes automatizados.

---

# 28. Anti-patterns

Evitar:

- regras de negócio;
- consultas SQL complexas;
- chamadas HTTP externas;
- envio de e-mails;
- renderização de Templates;
- acesso direto aos Models;
- dependência entre Middlewares.

Middlewares devem permanecer leves.

---

# 29. Checklist

Antes de criar um Middleware verificar:

- realmente pertence à infraestrutura?
- será utilizado por toda a aplicação?
- possui responsabilidade única?
- pode ser reutilizado?
- interfere na performance?
- está documentado?
- possui testes previstos?
- foi adicionada a configuração em `settings.py`?

---

# 30. Evolução Futura

A arquitetura dos Middlewares foi projetada para suportar futuras expansões.

Exemplos:

- Rate Limiting;
- Distributed Tracing;
- OpenTelemetry;
- Observabilidade avançada;
- Cache distribuído;
- Monitoramento em tempo real;
- Integração com APM;
- Inteligência Artificial para detecção de anomalias.

Essas funcionalidades deverão ser implementadas preservando os princípios definidos neste documento.

---

# 31. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-09 — Arquitetura Multi-Tenant
- GSF — GereIgreja Security Framework
- GOC — GereIgreja Operations Center
- GBE-05 — Services
- GBE-08 — Views
- GBE-11 — Permissions

---

# 32. Princípios Finais

Os Middlewares representam a camada de infraestrutura responsável por comportamentos transversais da plataforma.

Eles não implementam regras de negócio, mas fornecem os mecanismos necessários para que segurança, observabilidade, contexto organizacional e desempenho sejam aplicados de maneira uniforme em toda a aplicação.

Todo novo Middleware deverá possuir uma responsabilidade claramente definida, ser independente dos demais e preservar a simplicidade da arquitetura do GereIgreja.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `12-Middlewares.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece o padrão oficial para criação, organização e utilização de Middlewares no Backend do GereIgreja.

