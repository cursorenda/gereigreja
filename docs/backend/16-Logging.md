Pasta:
docs/backend/

Arquivo:
16-Logging.md

Documento:
GBE-16

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

# 16 - Logging

> *"Logs não existem apenas para registrar erros. Eles representam a memória operacional da plataforma e permitem compreender o comportamento do sistema em qualquer momento."*

---

# Sumário

1. Objetivo
2. Filosofia dos Logs
3. O Papel do Logging no GereIgreja
4. Arquitetura Oficial
5. Níveis de Log
6. Quando Registrar Logs
7. Quando NÃO Registrar Logs
8. Estrutura Oficial
9. Organização dos Logs
10. Documentos Relacionados
11. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para geração, organização e utilização de logs no Backend do GereIgreja.

Seu objetivo é garantir rastreabilidade, auditoria técnica, diagnóstico de problemas e apoio à operação da plataforma.

Os logs deverão fornecer informações suficientes para compreender o comportamento da aplicação sem expor dados sensíveis.

---

# 2. Filosofia dos Logs

Logs representam eventos técnicos ocorridos durante a execução da plataforma.

Eles devem responder perguntas como:

- O que aconteceu?
- Quando aconteceu?
- Onde aconteceu?
- Quem executou a ação?
- Qual foi o resultado?

Os logs são uma ferramenta de observabilidade, não um mecanismo de regras de negócio.

---

# 3. O Papel do Logging no GereIgreja

O sistema de Logging possui cinco objetivos principais:

- facilitar diagnóstico de problemas;
- apoiar auditorias técnicas;
- monitorar a saúde da aplicação;
- registrar eventos importantes;
- fornecer informações para monitoramento e métricas.

Toda funcionalidade relevante deverá produzir logs adequados ao seu contexto.

---

# 4. Arquitetura Oficial

Fluxo simplificado:

```text
Usuário

↓

View

↓

Service

↓

Model

↓

Evento

↓

Logger

↓

Arquivo / Console / Plataforma de Monitoramento
```

Os logs poderão ser enviados para múltiplos destinos simultaneamente.

---

# 5. Níveis de Log

O GereIgreja adota os níveis padrão do Python Logging.

## DEBUG

Informações detalhadas para desenvolvimento.

Exemplos:

- parâmetros recebidos;
- consultas executadas;
- tempo de processamento.

Não recomendado em produção.

---

## INFO

Eventos esperados da aplicação.

Exemplos:

- login realizado;
- importação concluída;
- relatório gerado;
- sincronização finalizada.

---

## WARNING

Situações inesperadas que não impedem a continuidade da operação.

Exemplos:

- tentativa de acesso negada;
- configuração incompleta;
- recurso indisponível temporariamente.

---

## ERROR

Erros que impedem determinada operação.

Exemplos:

- falha ao gerar relatório;
- erro em integração externa;
- exceção tratada.

Esses eventos deverão ser investigados.

---

## CRITICAL

Falhas graves que comprometem a operação da plataforma.

Exemplos:

- indisponibilidade do banco;
- perda de conexão com serviços essenciais;
- falha crítica na inicialização.

Devem gerar alerta imediato para a equipe técnica.

---

# 6. Quando Registrar Logs

Registrar logs para:

- autenticação;
- autorização;
- falhas de integração;
- execução de Tasks;
- processamento de Signals;
- erros inesperados;
- importações;
- exportações;
- alterações críticas de configuração.

O registro deve agregar valor operacional.

---

# 7. Quando NÃO Registrar Logs

Evitar registrar:

- consultas triviais;
- operações repetitivas sem relevância;
- dados sensíveis;
- senhas;
- tokens;
- informações financeiras completas;
- dados pessoais desnecessários.

Logs excessivos dificultam o diagnóstico e aumentam o custo operacional.

---

# 8. Estrutura Oficial

A infraestrutura de logging deverá permanecer centralizada.

Estrutura sugerida:

```text
core/

logging/

__init__.py

config.py

formatters.py

filters.py

handlers.py

utils.py
```

Cada componente deverá possuir responsabilidade específica.

---

# 9. Organização dos Logs

Sempre que possível, utilizar loggers específicos por domínio.

Exemplo:

```text
gereigreja.auth

gereigreja.financeiro

gereigreja.comunicacao

gereigreja.api

gereigreja.tasks

gereigreja.security

gereigreja.cache
```

Essa organização facilita filtros e monitoramento.

---

# 10. Documentos Relacionados

- GBE-12 — Middlewares
- GBE-13 — Signals
- GBE-14 — Tasks
- GSF — GereIgreja Security Framework
- GOC — GereIgreja Operations Center

---

# 11. Princípios Finais

Os logs representam a principal fonte de diagnóstico operacional da plataforma.

Sua implementação deverá priorizar clareza, rastreabilidade, segurança e facilidade de monitoramento.

Todo log deverá possuir finalidade clara e contribuir para a operação e evolução do GereIgreja.

---

## ✅ Parte 1 concluída

---

# 12. Logging Estruturado

O GereIgreja adotará, sempre que possível, o padrão de logs estruturados.

Preferencialmente, os registros deverão utilizar formato JSON para facilitar integração com ferramentas de observabilidade.

Exemplo conceitual:

```json
{
  "timestamp": "2026-07-15T14:32:18Z",
  "level": "INFO",
  "logger": "gereigreja.financeiro",
  "request_id": "REQ-8D7A91C4",
  "tenant": 15,
  "user": 42,
  "message": "Lançamento financeiro criado."
}
```

Esse formato facilita pesquisas, filtros e criação de dashboards.

---

# 13. Correlation ID (Request ID)

Toda requisição deverá possuir um identificador único.

Exemplo:

```text
REQ-8D7A91C4
```

Esse identificador deverá acompanhar todos os logs gerados durante a execução da requisição.

Fluxo:

```text
Request

↓

RequestIDMiddleware

↓

View

↓

Service

↓

Task

↓

Logs
```

Isso permite rastrear toda a jornada da operação.

---

# 14. Logs de APIs

As APIs deverão registrar informações essenciais.

Exemplos:

- método HTTP;
- endpoint;
- código de resposta;
- tempo de execução;
- tenant;
- usuário autenticado;
- Request ID.

Jamais registrar:

- senhas;
- tokens;
- dados sensíveis;
- informações completas de cartões ou documentos.

---

# 15. Logs de Tasks

Toda Task relevante deverá registrar:

- início da execução;
- conclusão;
- tempo gasto;
- falhas;
- retries;
- Worker responsável.

Exemplo:

```text
Task: enviar_email_massa

Status: Concluída

Tempo: 3,2 s
```

---

# 16. Logs de Signals

Signals deverão registrar apenas eventos relevantes.

Exemplos:

- auditoria iniciada;
- cache invalidado;
- evento publicado.

Evitar excesso de registros para eventos de baixa relevância.

---

# 17. Logs de Cache

Sempre que necessário poderão ser registrados:

- Cache Hit;
- Cache Miss;
- tempo de recuperação;
- invalidação de chave.

Esses registros auxiliam na análise de desempenho.

---

# 18. Logs de Segurança

Eventos de segurança deverão possuir logger próprio.

Exemplos:

- tentativa de login inválida;
- bloqueio por força bruta;
- alteração de permissões;
- criação de administradores;
- redefinição de senha;
- alteração de configuração crítica.

Esses eventos poderão alimentar sistemas de monitoramento e auditoria.

---

# 19. Rotação de Logs

Os arquivos de log deverão possuir política de rotação.

Critérios recomendados:

- tamanho máximo;
- período;
- quantidade de versões mantidas.

A política de retenção deverá considerar requisitos operacionais e legais.

---

# 20. Retenção

Os logs não deverão permanecer indefinidamente.

A retenção dependerá do tipo de informação.

Exemplo:

- logs técnicos: curto ou médio prazo;
- logs operacionais: médio prazo;
- auditorias: conforme política institucional.

A política oficial deverá ser definida pelo GOC (GereIgreja Operations Center).

---

# 21. Monitoramento

A arquitetura deverá permitir integração com plataformas de observabilidade.

Exemplos:

- Grafana;
- Loki;
- ELK Stack;
- OpenSearch;
- OpenTelemetry;
- Sentry.

A escolha da ferramenta não altera os princípios definidos neste documento.

---

# 22. Logging e Auditoria

Logging e Auditoria possuem finalidades distintas.

Logging:

- diagnóstico técnico;
- operação;
- monitoramento.

Auditoria:

- rastreabilidade funcional;
- conformidade;
- histórico de ações do usuário.

Nem todo log é auditoria.

Nem toda auditoria é um log técnico.

---

# 23. Logging e Exceções

Toda exceção tratada deverá gerar registro apropriado.

As informações mínimas incluem:

- tipo da exceção;
- mensagem;
- Request ID;
- usuário (quando aplicável);
- tenant;
- módulo responsável.

O tratamento da exceção permanece centralizado na arquitetura de Exceptions.

---

# 24. Boas Práticas

Sempre:

- utilizar logger específico por domínio;
- registrar contexto suficiente;
- proteger informações sensíveis;
- manter padrão consistente;
- utilizar níveis corretamente;
- monitorar crescimento dos arquivos;
- revisar logs periodicamente.

---

# 25. Anti-patterns

Evitar:

- registrar senhas;
- registrar tokens;
- utilizar apenas `print()`;
- criar mensagens vagas;
- registrar exceções sem contexto;
- duplicar logs do mesmo evento;
- utilizar nível ERROR para eventos normais.

---

# 26. Checklist

Antes de adicionar um novo log verificar:

- agrega valor operacional?
- utiliza o nível correto?
- possui contexto suficiente?
- evita dados sensíveis?
- segue o logger oficial?
- facilita diagnóstico?
- está documentado?

---

# 27. Evolução Futura

A arquitetura foi preparada para suportar:

- observabilidade distribuída;
- tracing completo;
- dashboards em tempo real;
- detecção automática de anomalias;
- alertas inteligentes;
- integração com plataformas de APM;
- análise assistida por Inteligência Artificial.

Essas evoluções deverão preservar os princípios definidos neste documento.

---

# 28. Documentos Relacionados

- GBE-12 — Middlewares
- GBE-13 — Signals
- GBE-14 — Tasks
- GBE-17 — Exceptions
- GSF — GereIgreja Security Framework
- GOC — GereIgreja Operations Center

---

# 29. Princípios Finais

O sistema de Logging do GereIgreja constitui um dos pilares da observabilidade da plataforma.

Sua implementação deverá permitir que desenvolvedores e operadores compreendam o comportamento da aplicação de forma rápida, segura e consistente.

Todo log deverá possuir propósito claro, respeitar a privacidade dos usuários e contribuir para a evolução contínua da plataforma.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `16-Logging.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece o padrão oficial para geração, organização, retenção e monitoramento de logs no Backend do GereIgreja.

