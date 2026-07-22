Pasta:
docs/backend/

Arquivo:
15-Cache.md

Documento:
GBE-15

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

# 15 - Cache

> *"Cache não serve apenas para acelerar consultas. Ele existe para reduzir processamento desnecessário, melhorar a escalabilidade e aumentar a capacidade da plataforma sem comprometer a consistência dos dados."*

---

# Sumário

1. Objetivo
2. Filosofia do Cache
3. O Papel do Cache no GereIgreja
4. Arquitetura Oficial
5. Tipos de Cache
6. Quando Utilizar Cache
7. Quando NÃO Utilizar Cache
8. Estrutura Oficial
9. Organização das Chaves
10. Documentos Relacionados
11. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para implementação, organização e utilização de mecanismos de cache no Backend do GereIgreja.

Seu objetivo é garantir ganho de desempenho sem comprometer a consistência, a segurança e a previsibilidade da plataforma.

Toda estratégia de cache deverá seguir as diretrizes aqui estabelecidas.

---

# 2. Filosofia do Cache

Cache é uma camada temporária de armazenamento.

Sua finalidade é evitar processamento repetitivo de informações cujo resultado permanece válido por determinado período.

No GereIgreja, o cache deverá ser tratado como uma otimização da arquitetura, nunca como fonte oficial dos dados.

A fonte da verdade continuará sendo o banco de dados.

---

# 3. O Papel do Cache no GereIgreja

O cache possui quatro objetivos principais:

- reduzir consultas ao banco;
- diminuir tempo de resposta;
- reduzir consumo de recursos;
- aumentar a escalabilidade da plataforma.

Sempre que uma informação puder ser reutilizada com segurança, deverá ser avaliada a utilização de cache.

---

# 4. Arquitetura Oficial

Fluxo recomendado:

```text
Usuário

↓

View

↓

Service

↓

Selector

↓

Cache

↓

Banco de Dados
```

Funcionamento:

```text
Existe no Cache?

↓

SIM

↓

Retorna imediatamente

↓

NÃO

↓

Consulta Banco

↓

Armazena Cache

↓

Retorna Resultado
```

Essa estratégia reduz significativamente consultas repetitivas.

---

# 5. Tipos de Cache

O GereIgreja poderá utilizar diferentes estratégias.

## Cache de Objetos

Armazena objetos individuais.

Exemplos:

- configurações;
- ministérios;
- igrejas;
- congregações;
- perfis.

---

## Cache de Consultas

Armazena resultados de consultas reutilizadas.

Exemplos:

- dashboard;
- estatísticas;
- indicadores;
- relatórios.

---

## Cache de Templates

Armazena fragmentos da interface.

Exemplos:

- menus;
- cards;
- widgets;
- painéis.

---

## Cache de Views

Armazena respostas completas.

Utilizar apenas quando a resposta não depender significativamente do usuário autenticado.

---

## Cache Distribuído

Utilizado quando houver múltiplos servidores.

O Redis será o mecanismo oficial.

---

# 6. Quando Utilizar Cache

Recomenda-se cache para:

- consultas frequentes;
- dashboards;
- estatísticas;
- configurações;
- listas pouco alteradas;
- parâmetros do sistema;
- permissões consolidadas;
- indicadores administrativos.

---

# 7. Quando NÃO Utilizar Cache

Evitar cache para:

- autenticação;
- sessões críticas;
- permissões temporárias;
- operações financeiras em andamento;
- dados altamente voláteis;
- informações sensíveis em memória sem necessidade.

Sempre avaliar o risco de inconsistência.

---

# 8. Estrutura Oficial

As funções de cache deverão permanecer desacopladas da lógica de negócio.

Estrutura sugerida:

```text
core/

cache/

__init__.py

keys.py

services.py

utils.py

invalidations.py
```

Cada arquivo deverá possuir responsabilidade específica.

---

# 9. Organização das Chaves

As chaves deverão seguir um padrão único.

Exemplo:

```text
gereigreja:

config:

ministerio:15

igreja:8

dashboard:usuario:42

estatisticas:financeiro

congregacao:17
```

Nunca utilizar chaves aleatórias ou sem padronização.

A nomenclatura deverá facilitar identificação, manutenção e invalidação.

---

# 10. Documentos Relacionados

- GBE-05 — Services
- GBE-06 — Selectors
- GBE-14 — Tasks
- GEA-03 — Arquitetura do Backend
- GOC — GereIgreja Operations Center

---

# 11. Princípios Finais

O cache representa uma camada estratégica da arquitetura do GereIgreja.

Sua utilização deverá aumentar a performance da plataforma sem comprometer a integridade das informações.

Toda implementação deverá privilegiar simplicidade, previsibilidade e facilidade de manutenção.

---

## ✅ Parte 1 concluída

---

# 12. Redis como Padrão Oficial

O GereIgreja adota o Redis como mecanismo oficial de cache distribuído.

O Redis oferece:

- alta velocidade;
- armazenamento em memória;
- suporte à distribuição;
- gerenciamento de expiração;
- integração nativa com Django e Celery.

Sua utilização garante consistência entre múltiplas instâncias da aplicação.

---

# 13. Estratégias de Cache

A arquitetura oficial suporta diferentes estratégias de cache, escolhidas conforme a necessidade do domínio.

## Cache Aside (Lazy Loading)

É a estratégia padrão do GereIgreja.

Fluxo:

```text
Consulta

↓

Existe no Cache?

↓

SIM

↓

Retorna

↓

NÃO

↓

Consulta Banco

↓

Armazena no Cache

↓

Retorna
```

Essa abordagem reduz consultas repetitivas sem aumentar a complexidade da aplicação.

---

## Write Through

Os dados são gravados simultaneamente no banco e no cache.

Fluxo:

```text
Service

↓

Banco

↓

Cache
```

Indicado apenas para cenários específicos em que a leitura imediata é frequente.

---

## Write Behind

A gravação no cache ocorre imediatamente, enquanto a persistência definitiva é realizada posteriormente.

Essa estratégia não será utilizada como padrão no GereIgreja devido ao maior risco de inconsistências.

---

# 14. Time To Live (TTL)

Toda chave deverá possuir um tempo de expiração apropriado.

Exemplos:

- configurações do sistema: longo prazo;
- dashboards: curto prazo;
- estatísticas: médio prazo;
- listas administrativas: médio prazo.

Evitar chaves permanentes sem necessidade.

O TTL deverá ser definido conforme a volatilidade da informação.

---

# 15. Invalidação de Cache

A invalidação é tão importante quanto o armazenamento.

Sempre que um dado for alterado, avaliar se o cache correspondente precisa ser removido.

Exemplo:

```text
Editar Congregação

↓

Salvar Banco

↓

Invalidar Cache

↓

Próxima consulta recria o cache
```

Nunca manter informações desatualizadas por longos períodos.

---

# 16. Cache por Tenant

Como o GereIgreja é uma plataforma Multi-Tenant, toda chave deverá considerar o contexto organizacional.

Exemplo:

```text
gereigreja:

tenant:15:

dashboard

gereigreja:

tenant:15:

estatisticas

gereigreja:

tenant:15:

configuracoes
```

Jamais compartilhar cache entre tenants distintos.

Essa regra é obrigatória.

---

# 17. Cache por Usuário

Algumas informações dependem exclusivamente do usuário autenticado.

Exemplo:

- dashboard personalizado;
- notificações;
- preferências;
- atalhos;
- permissões consolidadas.

Nesses casos, a chave deverá incluir o identificador do usuário.

Exemplo:

```text
dashboard:user:42

notificacoes:user:42
```

---

# 18. Cache em Selectors

Os Selectors representam o principal ponto para reutilização de consultas.

Sempre que uma consulta for executada frequentemente e possuir baixo índice de alteração, considerar sua utilização com cache.

Exemplos:

- estatísticas;
- indicadores;
- relatórios;
- configurações;
- listas de apoio.

Evitar implementar cache diretamente nas Views.

---

# 19. Cache em Services

Services poderão utilizar cache quando a operação envolver processamento intenso.

Entretanto, a lógica de invalidação deverá permanecer clara e documentada.

Nunca utilizar cache para mascarar consultas ineficientes.

Primeiro otimizar a consulta; depois considerar o cache.

---

# 20. Cache em APIs

APIs públicas poderão utilizar cache para respostas estáveis.

Exemplos:

- catálogos;
- configurações públicas;
- informações institucionais.

APIs autenticadas deverão considerar:

- usuário;
- tenant;
- permissões;
- contexto da requisição.

---

# 21. Cache em Dashboards

Dashboards representam um dos principais candidatos ao uso de cache.

Os indicadores podem ser processados previamente e reutilizados durante um período determinado.

Sempre equilibrar desempenho e atualização das informações.

---

# 22. Cache Warming

Sempre que necessário, o sistema poderá gerar determinados caches antecipadamente.

Exemplos:

- dashboard principal;
- estatísticas administrativas;
- relatórios recorrentes;
- parâmetros do sistema.

Essa estratégia reduz o tempo da primeira consulta.

---

# 23. Monitoramento

Toda infraestrutura de cache deverá permitir monitoramento.

Indicadores importantes:

- Cache Hit;
- Cache Miss;
- tempo médio de resposta;
- quantidade de chaves;
- memória utilizada;
- taxa de invalidação;
- TTL médio.

Essas métricas auxiliam na evolução da plataforma.

---

# 24. Boas Práticas

Sempre:

- utilizar nomenclatura padronizada;
- definir TTL adequado;
- invalidar corretamente;
- reutilizar Selectors;
- documentar estratégias;
- monitorar desempenho;
- evitar duplicação de chaves.

O cache deve simplificar a arquitetura, nunca dificultá-la.

---

# 25. Anti-patterns

Evitar:

- cache permanente sem expiração;
- armazenar dados sensíveis sem necessidade;
- compartilhar cache entre tenants;
- utilizar cache para ocultar problemas de modelagem;
- criar chaves sem padrão;
- duplicar dados desnecessariamente;
- esquecer de invalidar informações alteradas.

---

# 26. Checklist

Antes de implementar cache verificar:

- a consulta realmente é reutilizada?
- existe ganho mensurável?
- a chave segue o padrão oficial?
- possui TTL definido?
- considera o tenant?
- considera o usuário quando necessário?
- possui estratégia de invalidação?
- está documentado?
- foi monitorado em ambiente de testes?

---

# 27. Evolução Futura

A arquitetura foi projetada para suportar:

- Redis Cluster;
- cache distribuído;
- cache em múltiplas regiões;
- pré-aquecimento inteligente;
- invalidação orientada a eventos;
- integração com CDN;
- cache adaptativo baseado em uso;
- observabilidade avançada.

Essas evoluções deverão preservar os princípios estabelecidos neste documento.

---

# 28. Documentos Relacionados

- GBE-05 — Services
- GBE-06 — Selectors
- GBE-13 — Signals
- GBE-14 — Tasks
- GEA-09 — Arquitetura Multi-Tenant
- GOC — GereIgreja Operations Center

---

# 29. Princípios Finais

O cache é um componente estratégico da arquitetura do GereIgreja.

Sua utilização deverá reduzir processamento desnecessário, melhorar o desempenho e permitir o crescimento sustentável da plataforma, preservando a consistência dos dados e o isolamento entre tenants.

Toda implementação deverá ser planejada, documentada e monitorada, garantindo que o cache permaneça uma otimização da arquitetura e nunca uma fonte alternativa da verdade.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `15-Cache.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece o padrão oficial para implementação e gerenciamento de cache no Backend do GereIgreja, definindo estratégias, responsabilidades e boas práticas para toda a plataforma.


