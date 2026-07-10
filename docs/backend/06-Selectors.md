Pasta:
docs/backend/

Arquivo:
06-Selectors.md

Documento:
GBE-06

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

# 06 - Selectors

> "Toda consulta complexa deve possuir um único lugar para existir. No GereIgreja, esse lugar são os Selectors."

---

# Sumário

1. Objetivo
2. Filosofia dos Selectors
3. Papel dos Selectors na Arquitetura
4. Responsabilidade dos Selectors
5. Estrutura Oficial
6. Organização do Diretório selectors/
7. Convenções de Nomenclatura
8. Fluxo de Execução
9. Comunicação com Models
10. Comunicação com Services
11. Comunicação com Views
12. Comunicação com APIs
13. Boas Práticas
14. Documentos Relacionados
15. Princípios Finais

---

# 1. Objetivo

Este documento define os padrões oficiais para implementação da camada de Selectors do GereIgreja.

Seu objetivo é centralizar toda lógica de leitura de dados da plataforma, promovendo reutilização, organização e desempenho.

Toda consulta reutilizável deverá ser implementada nesta camada.

---

# 2. Filosofia dos Selectors

Os Selectors existem exclusivamente para recuperar informações.

Eles não alteram dados.

Eles não executam regras de negócio.

Eles apenas consultam.

No GereIgreja adotamos o seguinte princípio:

> **Quem escreve dados é o Service. Quem lê dados é o Selector.**

Essa separação reduz duplicação de consultas e facilita manutenção.

---

# 3. Papel dos Selectors na Arquitetura

Fluxo oficial:

```text
Usuário

↓

View

↓

Service (quando necessário)

↓

Selector

↓

Model

↓

Banco de Dados
```

Quando uma operação envolver apenas leitura, a View poderá chamar diretamente um Selector.

Quando envolver regras de negócio, a View deverá chamar um Service, que utilizará os Selectors necessários.

---

# 4. Responsabilidade dos Selectors

Os Selectors poderão ser responsáveis por:

- consultas simples;
- consultas complexas;
- filtros;
- paginações;
- ordenações;
- agregações;
- estatísticas;
- consultas otimizadas;
- composição de QuerySets.

Não deverão:

- salvar registros;
- excluir registros;
- atualizar dados;
- executar regras de negócio;
- chamar APIs externas;
- enviar notificações.

Selectors nunca modificam o estado da aplicação.

---

# 5. Estrutura Oficial

Cada App poderá possuir um diretório próprio para Selectors.

Exemplo:

```text
selectors/

__init__.py

membro_selector.py

familia_selector.py

cargo_selector.py

estatistica_selector.py
```

Cada arquivo deverá representar um domínio específico.

---

# 6. Organização do Diretório selectors/

Exemplo:

```text
selectors/

membro_selector.py

↓

Consultas relacionadas aos membros

familia_selector.py

↓

Consultas relacionadas às famílias

financeiro_selector.py

↓

Consultas financeiras

dashboard_selector.py

↓

Indicadores e painéis
```

Evitar Selectors genéricos contendo consultas de múltiplos domínios.

---

# 7. Convenções de Nomenclatura

Classes:

```python
MembroSelector

FinanceiroSelector

EventoSelector
```

Métodos:

```python
listar()

buscar()

obter()

filtrar()

contar()

existe()

listar_ativos()

listar_por_congregacao()

buscar_por_cpf()
```

Os nomes deverão indicar claramente o resultado esperado.

---

# 8. Fluxo de Execução

Fluxo recomendado:

```text
Receber parâmetros

↓

Validar parâmetros mínimos

↓

Construir QuerySet

↓

Aplicar filtros

↓

Aplicar ordenação

↓

Aplicar otimizações

↓

Retornar QuerySet ou objeto
```

Selectors deverão permanecer previsíveis e simples.

---

# 9. Comunicação com Models

Selectors consultam diretamente os Models.

Exemplo:

```python
return Membro.objects.filter(
    ativo=True
)
```

Toda consulta reutilizável deverá ser encapsulada em um Selector.

---

# 10. Comunicação com Services

Os Services deverão utilizar Selectors sempre que necessitarem de consultas reutilizáveis.

Exemplo:

```python
membro = MembroSelector.buscar_por_cpf(cpf)
```

Isso evita duplicação de consultas dentro dos Services.

---

# 11. Comunicação com Views

Quando a funcionalidade envolver apenas leitura, a View poderá utilizar um Selector diretamente.

Exemplo:

```python
membros = MembroSelector.listar_ativos()
```

Caso exista qualquer regra de negócio, a View deverá utilizar um Service.

---

# 12. Comunicação com APIs

Serializers e ViewSets poderão consumir Selectors para recuperar dados.

Isso garante que Web e API utilizem exatamente as mesmas consultas.

---

# 13. Boas Práticas

Os Selectors deverão:

- retornar QuerySets sempre que possível;
- possuir responsabilidade única;
- reutilizar consultas;
- utilizar nomes descritivos;
- aplicar otimizações quando necessário;
- evitar lógica de negócio;
- facilitar testes.

---

# 14. Documentos Relacionados

- GEA-03 — Arquitetura dos Módulos
- GBE-03 — Arquitetura dos Apps
- GBE-04 — Models
- GBE-05 — Services
- GBE-07 — Managers
- GQF — Framework de Qualidade

---

# 15. Princípios Finais

Os Selectors representam a camada oficial de leitura do GereIgreja.

Toda consulta reutilizável deverá nascer nesta camada.

Ao centralizar as consultas, a plataforma reduz duplicação, melhora o desempenho e torna o código mais organizado e previsível.

A separação entre leitura e escrita é um dos pilares fundamentais da arquitetura do GereIgreja.

---

# 16. Otimização de Consultas

Todo Selector deverá ser desenvolvido considerando desempenho.

Antes de criar uma consulta, avaliar:

- quantidade de registros;
- frequência de execução;
- necessidade de relacionamentos;
- possibilidade de cache.

Consultas eficientes reduzem carga no banco e melhoram a experiência do usuário.

---

# 17. Uso de select_related()

Sempre que houver relacionamentos ForeignKey ou OneToOne, avaliar o uso de `select_related()`.

Exemplo:

```python
return (
    Membro.objects
    .select_related(
        "congregacao",
        "cargo"
    )
)
```

Isso reduz consultas adicionais ao banco.

Evitar carregamento repetitivo de objetos relacionados.

---

# 18. Uso de prefetch_related()

Relacionamentos ManyToMany e relações reversas deverão utilizar `prefetch_related()` quando necessário.

Exemplo:

```python
return (
    Evento.objects
    .prefetch_related(
        "participantes",
        "ministerios"
    )
)
```

O uso adequado evita o problema conhecido como N+1 Queries.

---

# 19. Campos Específicos

Quando apenas alguns campos forem necessários, utilizar:

```python
.only()
```

ou

```python
.defer()
```

Exemplo:

```python
Membro.objects.only(
    "id",
    "nome",
    "telefone"
)
```

Evitar carregar dados que não serão utilizados.

---

# 20. Agregações

Consultas estatísticas deverão utilizar funções de agregação do Django ORM.

Exemplos:

```python
Count()

Sum()

Avg()

Min()

Max()
```

Exemplo:

```python
from django.db.models import Count

Membro.objects.aggregate(
    total=Count("id")
)
```

Evitar processamento manual em Python quando o banco puder executar a operação.

---

# 21. Annotate()

Sempre que necessário enriquecer uma consulta utilizar `annotate()`.

Exemplo:

```python
Congregacao.objects.annotate(
    total_membros=Count("membros")
)
```

As anotações permitem gerar informações úteis sem consultas adicionais.

---

# 22. Exists()

Para verificar existência de registros utilizar `Exists()` ou `.exists()`.

Evitar:

```python
count() > 0
```

Preferir:

```python
queryset.exists()
```

Essa abordagem é significativamente mais eficiente.

---

# 23. Subqueries

Quando apropriado utilizar:

```python
Subquery()

OuterRef()
```

para evitar múltiplas consultas.

Esses recursos deverão ser utilizados apenas quando realmente agregarem desempenho ou simplificarem a lógica.

---

# 24. Paginação

Selectors que retornam grandes volumes deverão ser preparados para paginação.

Nunca retornar milhares de registros sem necessidade.

Sempre que possível:

- limitar resultados;
- ordenar registros;
- paginar respostas.

---

# 25. Ordenação

Toda consulta deverá possuir ordenação previsível.

Evitar depender da ordem natural do banco.

Exemplo:

```python
.order_by("nome")
```

ou

```python
.order_by("-criado_em")
```

Isso garante consistência entre diferentes bancos de dados.

---

# 26. Cache

Consultas muito frequentes poderão utilizar cache.

Exemplos:

- dashboard;
- estatísticas;
- indicadores;
- configurações;
- listas pouco alteradas.

O uso de cache deverá respeitar as políticas definidas pelo GOC (Framework de Operações).

---

# 27. Consultas Multi-Tenant

Toda consulta deverá respeitar o tenant ativo.

Exemplo:

```python
Membro.objects.filter(
    igreja=igreja_atual
)
```

Jamais permitir consultas que retornem dados de outras igrejas.

O isolamento entre tenants é obrigatório.

---

# 28. Dashboards

Consultas utilizadas em painéis deverão ser especialmente otimizadas.

Boas práticas:

- utilizar agregações;
- evitar consultas repetidas;
- utilizar cache;
- evitar loops sobre grandes QuerySets.

Dashboards deverão ser rápidos mesmo em igrejas com milhares de registros.

---

# 29. Padrão de Retorno

Sempre que possível, Selectors deverão retornar:

- QuerySet;
- objeto único;
- valores agregados;
- dicionários quando apropriado.

Evitar retornar estruturas inconsistentes entre métodos semelhantes.

A previsibilidade facilita reutilização.

---

# 30. Performance

Antes da conclusão de um Selector verificar:

- utiliza índices existentes;
- evita N+1 Queries;
- utiliza select_related quando necessário;
- utiliza prefetch_related quando necessário;
- evita consultas duplicadas;
- evita processamento desnecessário em Python.

O desempenho deve ser considerado desde a implementação inicial.

---

# 31. Exemplo de Estrutura de um Selector

Cada Selector deverá representar um domínio específico da aplicação.

Exemplo:

```python
class MembroSelector:

    @staticmethod
    def listar_ativos(igreja):
        ...

    @staticmethod
    def buscar_por_cpf(igreja, cpf):
        ...

    @staticmethod
    def listar_por_congregacao(congregacao):
        ...

    @staticmethod
    def contar_ativos(igreja):
        ...
```

Os métodos deverão ser pequenos, previsíveis e focados em uma única consulta.

---

# 32. Organização por Domínio

À medida que um App crescer, os Selectors deverão ser divididos por domínio.

Exemplo:

```text
selectors/

cadastro_selector.py

familia_selector.py

ministerio_selector.py

financeiro_selector.py

dashboard_selector.py

estatistica_selector.py

relatorio_selector.py
```

Essa organização facilita manutenção e localização das consultas.

---

# 33. Exemplos de Consultas

Exemplo de consulta simples:

```python
@staticmethod
def listar_ativos(igreja):
    return (
        Membro.objects
        .filter(
            igreja=igreja,
            ativo=True
        )
        .order_by("nome")
    )
```

---

Consulta por CPF:

```python
@staticmethod
def buscar_por_cpf(igreja, cpf):
    return (
        Membro.objects
        .filter(
            igreja=igreja,
            cpf=cpf
        )
        .first()
    )
```

---

Consulta estatística:

```python
@staticmethod
def total_membros(igreja):
    return (
        Membro.objects
        .filter(igreja=igreja)
        .count()
    )
```

Cada método deve possuir um objetivo único.

---

# 34. Integração com Services

Sempre que um Service necessitar consultar informações reutilizáveis, deverá utilizar um Selector.

Exemplo:

```python
membro = MembroSelector.buscar_por_cpf(
    igreja,
    cpf
)
```

Essa abordagem evita duplicação de consultas.

---

# 35. Integração com Managers

Os Managers deverão permanecer simples.

Consultas reutilizáveis deverão permanecer nos Selectors.

Exemplo recomendado:

```text
Manager

↓

consultas extremamente simples

↓

Selector

↓

consultas reutilizáveis

↓

Service

↓

regras de negócio
```

Essa divisão mantém cada camada com responsabilidade única.

---

# 36. Integração com Dashboards

Os Dashboards deverão consumir Selectors especializados.

Exemplo:

```python
DashboardSelector.indicadores_gerais()

DashboardSelector.financeiro_resumido()

DashboardSelector.aniversariantes()

DashboardSelector.estatisticas_ebd()
```

Isso facilita cache e otimização.

---

# 37. Reutilização

Os mesmos Selectors poderão ser utilizados por:

- Views;
- APIs REST;
- Services;
- Comandos administrativos;
- Tasks;
- Dashboards;
- Testes automatizados.

Toda consulta importante deverá existir apenas uma vez.

---

# 38. Anti-patterns

Evitar:

- consultas SQL espalhadas pelo sistema;
- QuerySets dentro das Views;
- consultas complexas dentro dos Services;
- duplicação de filtros;
- uso excessivo de `.all()`;
- consultas sem paginação;
- consultas sem ordenação;
- processamento em Python que poderia ser realizado pelo banco.

Esses problemas reduzem desempenho e dificultam manutenção.

---

# 39. Refatoração de Selectors

Sempre que um Selector crescer excessivamente:

- dividir por domínio;
- extrair consultas reutilizáveis;
- remover duplicações;
- revisar otimizações;
- documentar consultas críticas.

A evolução contínua faz parte da arquitetura.

---

# 40. Checklist para Criação de um Selector

Antes da implementação verificar:

- representa apenas leitura;
- possui responsabilidade única;
- nome descritivo;
- consulta otimizada;
- ordenação definida;
- filtros corretos;
- isolamento Multi-Tenant garantido;
- documentação quando necessária;
- possibilidade de reutilização.

---

# 41. Checklist para Revisão

Durante uma revisão arquitetural verificar:

- ausência de lógica de negócio;
- ausência de alterações de dados;
- uso adequado de índices;
- uso correto de select_related();
- uso correto de prefetch_related();
- consultas reutilizadas;
- ausência de N+1 Queries;
- documentação atualizada.

---

# 42. Evolução Contínua

Os Selectors deverão evoluir conforme a plataforma crescer.

Novos recursos poderão exigir:

- novas agregações;
- novos filtros;
- novos indicadores;
- otimizações;
- estratégias de cache.

Toda evolução deverá preservar simplicidade e previsibilidade.

---

# 43. Integração com o Ecossistema GBE

Os Selectors fazem parte do fluxo oficial da arquitetura do Backend.

```text
View

↓

Service

↓

Selector

↓

Model

↓

Banco de Dados
```

Essa separação elimina responsabilidades sobrepostas e facilita a manutenção da plataforma.

---

# 44. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GBE-03 — Arquitetura dos Apps
- GBE-04 — Models
- GBE-05 — Services
- GBE-07 — Managers
- GAF — Framework de Autenticação
- GSF — Framework de Segurança
- GQF — Framework de Qualidade

---

# 45. Princípios Finais

Os Selectors representam a camada oficial de acesso e leitura de dados do GereIgreja.

Ao concentrar todas as consultas reutilizáveis em uma única camada, a plataforma ganha organização, desempenho e previsibilidade.

A separação entre leitura (Selectors) e escrita (Services) reduz acoplamento, facilita testes e torna a evolução do sistema mais segura.

Todo novo desenvolvimento deverá respeitar esse princípio arquitetural, garantindo que consultas permaneçam simples, reutilizáveis e otimizadas.

Uma arquitetura sólida não depende apenas de bons Models ou bons Services, mas também de uma camada de consultas bem definida. Os Selectors cumprem esse papel e são parte fundamental da Engenharia do GereIgreja.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `06-Selectors.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento passa a ser a referência oficial para toda a camada de leitura de dados da plataforma.


