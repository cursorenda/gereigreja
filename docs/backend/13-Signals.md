Pasta:
docs/backend/

Arquivo:
13-Signals.md

Documento:
GBE-13

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

# 13 - Signals

> *"Signals conectam eventos da aplicação de forma desacoplada. Eles existem para reagir a acontecimentos, nunca para controlar o fluxo principal do negócio."*

---

# Sumário

1. Objetivo
2. Filosofia dos Signals
3. O Papel dos Signals no GereIgreja
4. Fluxo de Execução
5. Quando Utilizar Signals
6. Quando NÃO Utilizar Signals
7. Estrutura Oficial
8. Organização dos Signals
9. Registro dos Signals
10. Documentos Relacionados
11. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação, organização e utilização dos Signals no Backend do GereIgreja.

Seu objetivo é garantir que eventos do sistema sejam tratados de maneira desacoplada, previsível e de fácil manutenção, evitando que regras de negócio sejam distribuídas de forma inadequada.

---

# 2. Filosofia dos Signals

Signals representam eventos.

Eles permitem que uma parte da aplicação reaja a acontecimentos ocorridos em outra parte, sem criar dependências diretas.

No GereIgreja, Signals deverão ser utilizados para complementar o fluxo da aplicação, nunca para controlá-lo.

---

# 3. O Papel dos Signals no GereIgreja

Os Signals possuem responsabilidades específicas.

Exemplos:

- registrar auditoria;
- atualizar índices;
- limpar cache;
- criar registros auxiliares;
- enviar notificações assíncronas;
- disparar tarefas em segundo plano;
- sincronizar informações entre módulos.

Sempre que um evento puder ser tratado de forma independente da operação principal, um Signal poderá ser considerado.

---

# 4. Fluxo de Execução

Fluxo simplificado:

```text
View

↓

Service

↓

Model.save()

↓

Signal

↓

Ações complementares
```

O Service continua sendo responsável pela regra de negócio.

O Signal apenas reage ao evento.

---

# 5. Quando Utilizar Signals

Os Signals são recomendados quando:

- a ação é consequência de um evento;
- a operação é complementar;
- o fluxo principal não depende do resultado;
- existe interesse em manter baixo acoplamento.

Exemplos:

- registrar log após criação de membro;
- criar histórico de alterações;
- atualizar estatísticas;
- invalidar cache;
- enviar evento para fila.

---

# 6. Quando NÃO Utilizar Signals

Signals não devem ser utilizados para:

- regras financeiras;
- cálculos de negócio;
- validações;
- controle de permissões;
- autenticação;
- decisões críticas;
- fluxos obrigatórios.

Essas responsabilidades pertencem aos Services.

Uma operação que precisa obrigatoriamente acontecer para concluir uma funcionalidade não deve depender de um Signal.

---

# 7. Estrutura Oficial

Os Signals deverão permanecer organizados por App.

Exemplo:

```text
membros/

signals.py

financeiro/

signals.py

eventos/

signals.py
```

Quando houver grande quantidade de Signals:

```text
signals/

__init__.py

membros.py

financeiro.py

usuarios.py
```

A organização deverá privilegiar clareza e facilidade de manutenção.

---

# 8. Organização dos Signals

Cada Signal deverá possuir responsabilidade única.

Evitar arquivos extensos contendo dezenas de eventos distintos.

Sempre agrupar eventos relacionados ao mesmo domínio.

---

# 9. Registro dos Signals

Todo Signal deverá ser registrado durante a inicialização da aplicação.

Preferencialmente utilizando:

```python
apps.py
```

Exemplo conceitual:

```python
class MembrosConfig(AppConfig):

    def ready(self):

        import membros.signals
```

Essa abordagem garante que todos os handlers sejam carregados corretamente durante a inicialização do Django.

---

# 10. Documentos Relacionados

- GBE-04 — Models
- GBE-05 — Services
- GBE-12 — Middlewares
- GQF — GereIgreja Quality Framework
- GEA-03 — Arquitetura do Backend

---

# 11. Princípios Finais

Signals existem para responder a eventos da aplicação.

Eles devem permanecer desacoplados, simples e previsíveis.

Toda regra crítica deverá continuar centralizada nos Services.

Signals complementam a arquitetura; nunca substituem o domínio de negócio.

---

# 12. Signals Síncronos e Assíncronos

Nem todo evento deve ser executado imediatamente.

O GereIgreja adota dois modelos de processamento.

## Signals Síncronos

São executados durante a própria requisição.

Devem ser utilizados apenas quando:

- a operação é muito rápida;
- não envolve comunicação externa;
- não impacta significativamente o tempo de resposta.

Exemplos:

- atualizar cache local;
- registrar histórico simples;
- atualizar contador interno.

---

## Signals Assíncronos

Operações demoradas deverão ser encaminhadas para processamento em segundo plano.

Exemplos:

- envio de e-mails;
- envio de WhatsApp;
- geração de PDFs;
- exportações;
- sincronizações externas;
- processamento de imagens.

Sempre que possível, o Signal deverá apenas disparar uma Task.

Fluxo recomendado:

```text
Model.save()

↓

Signal

↓

Task

↓

Worker

↓

Processamento
```

---

# 13. Integração com Celery

Signals não devem executar tarefas demoradas.

O padrão oficial será:

```python
post_save

↓

Signal

↓

Celery Task

↓

Execução em Background
```

Essa abordagem melhora:

- desempenho;
- escalabilidade;
- experiência do usuário;
- confiabilidade.

---

# 14. Signals e Auditoria

Uma das principais aplicações dos Signals é a auditoria.

Exemplos:

- membro criado;
- membro removido;
- lançamento financeiro alterado;
- alteração de permissões;
- criação de usuário;
- redefinição de senha.

O Signal apenas comunica o evento.

O mecanismo de auditoria decide como registrá-lo.

---

# 15. Signals e Cache

Sempre que um objeto relevante sofrer alteração, o cache poderá ser invalidado.

Exemplo:

```text
Membro alterado

↓

Signal

↓

Limpar Cache

↓

Próxima consulta gera novo cache
```

Essa estratégia mantém os dados consistentes sem acoplamento ao domínio.

---

# 16. Signals e Notificações

Signals podem iniciar processos de notificação.

Exemplo:

```text
Novo evento criado

↓

Signal

↓

Task

↓

Enviar WhatsApp

↓

Enviar Email
```

A regra de envio permanece fora do Signal.

---

# 17. Signals e Integrações

Sempre que houver integração com sistemas externos, o Signal deverá apenas iniciar o processo.

Exemplos:

- Google Calendar;
- Google Drive;
- WhatsApp;
- APIs de pagamento;
- serviços governamentais.

A integração propriamente dita deverá ocorrer em Services ou Tasks.

---

# 18. Prevenção de Loops

Um Signal nunca deverá provocar outro evento que gere o mesmo Signal indefinidamente.

Exemplo inadequado:

```text
post_save

↓

save()

↓

post_save

↓

save()

↓

...
```

Sempre verificar possíveis ciclos antes da implementação.

---

# 19. Idempotência

Sempre que possível, os handlers deverão ser idempotentes.

Isso significa que uma mesma operação poderá ser executada mais de uma vez sem gerar inconsistências.

Exemplos:

- não duplicar registros;
- não enviar notificações repetidas;
- não gerar histórico duplicado.

---

# 20. Tratamento de Erros

Falhas em um Signal não devem comprometer desnecessariamente o fluxo principal.

Quando apropriado:

- registrar logs;
- registrar auditoria;
- encaminhar para monitoramento;
- permitir nova tentativa quando houver processamento assíncrono.

---

# 21. Organização dos Handlers

Cada handler deverá possuir responsabilidade única.

Exemplo:

```text
signals/

membros.py

usuarios.py

financeiro.py

eventos.py

comunicacao.py
```

Evitar arquivos excessivamente grandes.

---

# 22. Signals x Services

Services:

- executam regras de negócio.

Signals:

- reagem a eventos.

Pergunta orientadora:

"A operação precisa acontecer obrigatoriamente para concluir a funcionalidade?"

Se a resposta for "sim", pertence ao Service.

Caso contrário, poderá ser um Signal.

---

# 23. Signals x Middlewares

Middlewares:

- trabalham durante requisições HTTP.

Signals:

- trabalham durante eventos do domínio.

São mecanismos distintos.

---

# 24. Signals x Decorators

Decorators:

- atuam sobre funções e Views.

Signals:

- atuam sobre eventos do sistema.

Nunca utilizar um para substituir o outro.

---

# 25. Boas Práticas

Sempre:

- manter handlers pequenos;
- responsabilidade única;
- evitar dependências circulares;
- utilizar Tasks para operações demoradas;
- registrar eventos importantes;
- documentar Signals críticos;
- criar testes automatizados.

---

# 26. Anti-patterns

Evitar:

- regras de negócio críticas;
- consultas SQL pesadas;
- chamadas HTTP externas;
- envio direto de e-mails;
- múltiplas responsabilidades;
- dependência entre Signals;
- efeitos colaterais inesperados.

Signals devem permanecer previsíveis.

---

# 27. Checklist

Antes de criar um Signal verificar:

- realmente representa um evento?
- não pertence ao Service?
- não pertence ao Middleware?
- não depende da interface?
- possui responsabilidade única?
- pode gerar loop?
- está documentado?
- possui testes?
- precisa ser assíncrono?

---

# 28. Evolução Futura

A arquitetura foi projetada para suportar:

- Event Bus;
- Domain Events;
- Event Sourcing parcial;
- Mensageria distribuída;
- Apache Kafka;
- RabbitMQ;
- Integrações orientadas a eventos.

A evolução deverá preservar compatibilidade com os princípios estabelecidos neste documento.

---

# 29. Documentos Relacionados

- GBE-04 — Models
- GBE-05 — Services
- GBE-12 — Middlewares
- GBE-14 — Tasks
- GSF — GereIgreja Security Framework
- GQF — GereIgreja Quality Framework
- GEA-03 — Arquitetura do Backend

---

# 30. Princípios Finais

Os Signals permitem que a plataforma reaja a eventos de maneira desacoplada, reutilizável e organizada.

Seu uso deve fortalecer a arquitetura, reduzindo dependências entre módulos e facilitando a evolução do sistema.

Toda lógica crítica permanecerá centralizada nos Services.

Signals deverão atuar apenas como mecanismos de reação aos eventos do domínio.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `13-Signals.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece o padrão oficial para utilização de Signals no Backend do GereIgreja, definindo responsabilidades, boas práticas, limitações e diretrizes para evolução da arquitetura orientada a eventos.

