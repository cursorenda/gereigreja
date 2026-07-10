Pasta:
docs/backend/

Arquivo:
07-Managers.md

Documento:
GBE-07

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

# 07 - Managers

> "Managers existem para facilitar o acesso aos dados, não para concentrar regras de negócio."

---

# Sumário

1. Objetivo
2. Filosofia dos Managers
3. Papel dos Managers na Arquitetura
4. Responsabilidades
5. O que NÃO pertence aos Managers
6. Estrutura Oficial
7. Convenções de Nomenclatura
8. Comunicação com Models
9. Comunicação com Selectors
10. Comunicação com Services
11. Custom QuerySets
12. Boas Práticas
13. Documentos Relacionados
14. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para utilização de Managers no GereIgreja.

Seu objetivo é definir claramente suas responsabilidades, evitando que se tornem depósitos de regras de negócio ou consultas complexas.

Os Managers deverão permanecer simples, previsíveis e focados na camada de acesso aos dados.

---

# 2. Filosofia dos Managers

Os Managers existem para facilitar operações comuns sobre um Model.

Eles representam a porta de entrada para os QuerySets.

No GereIgreja adotamos o seguinte princípio:

> **Managers simplificam o acesso aos dados. Services executam regras de negócio. Selectors executam consultas reutilizáveis.**

Essa separação elimina sobreposição de responsabilidades.

---

# 3. Papel dos Managers na Arquitetura

Fluxo oficial:

```text
Model

↓

Manager

↓

QuerySet

↓

Banco de Dados
```

Os Managers pertencem exclusivamente à camada dos Models.

Eles não conhecem Views, Forms, APIs ou Templates.

---

# 4. Responsabilidades

Os Managers poderão ser responsáveis por:

- QuerySets padrão;
- filtros básicos;
- criação de QuerySets reutilizáveis;
- métodos auxiliares simples;
- recuperação de registros comuns.

Exemplos:

- ativos();
- inativos();
- publicados();
- ordenados();
- recentes();
- visiveis().

Sempre mantendo simplicidade.

---

# 5. O que NÃO pertence aos Managers

Managers não deverão conter:

- regras de negócio;
- validações de domínio;
- cálculos financeiros;
- envio de e-mails;
- chamadas HTTP;
- integrações externas;
- geração de relatórios;
- auditoria;
- notificações;
- importações.

Essas responsabilidades pertencem aos Services.

---

# 6. Estrutura Oficial

Exemplo:

```python
class MembroManager(models.Manager):

    def ativos(self):
        return self.get_queryset().filter(
            ativo=True
        )

    def inativos(self):
        return self.get_queryset().filter(
            ativo=False
        )
```

Cada método deverá ser pequeno e previsível.

---

# 7. Convenções de Nomenclatura

Classes:

```python
MembroManager

EventoManager

FinanceiroManager
```

Métodos:

```python
ativos()

inativos()

recentes()

publicados()

ordenados()

visiveis()
```

Utilizar nomes curtos e objetivos.

---

# 8. Comunicação com Models

Todo Manager pertence a um único Model.

Exemplo:

```python
class Membro(models.Model):

    objects = MembroManager()
```

Managers não deverão acessar outros Models diretamente.

---

# 9. Comunicação com Selectors

Quando uma consulta crescer em complexidade ou passar a ser reutilizada em diversos módulos, deverá ser movida para um Selector.

Exemplo:

```text
Manager

↓

Consulta simples

↓

Selector

↓

Consulta complexa
```

Essa separação melhora a organização da arquitetura.

---

# 10. Comunicação com Services

Os Services poderão utilizar Managers apenas para operações extremamente simples.

Quando a consulta envolver filtros elaborados, agregações ou otimizações, deverão utilizar Selectors.

Exemplo:

```python
Membro.objects.ativos()
```

Para consultas mais elaboradas:

```python
MembroSelector.listar_por_congregacao()
```

---

# 11. Custom QuerySets

Sempre que diversos métodos puderem ser reutilizados em cadeia, recomenda-se utilizar QuerySets personalizados.

Exemplo:

```python
class MembroQuerySet(models.QuerySet):

    def ativos(self):
        return self.filter(ativo=True)

    def ordenados(self):
        return self.order_by("nome")
```

Em seguida:

```python
class MembroManager(models.Manager):

    def get_queryset(self):
        return MembroQuerySet(
            self.model,
            using=self._db
        )
```

Essa abordagem melhora reutilização e composição.

---

# 12. Boas Práticas

Os Managers deverão:

- ser pequenos;
- retornar QuerySets;
- evitar lógica de negócio;
- possuir responsabilidade única;
- reutilizar QuerySets personalizados quando apropriado;
- manter alta legibilidade.

Sempre que um Manager crescer excessivamente, reavaliar sua responsabilidade.

---

# 13. Documentos Relacionados

- GBE-04 — Models
- GBE-05 — Services
- GBE-06 — Selectors
- GEA-03 — Arquitetura dos Módulos
- GQF — Framework de Qualidade

---

# 14. Princípios Finais

Os Managers representam uma camada auxiliar dos Models.

Sua função é simplificar operações comuns e disponibilizar QuerySets padronizados.

Ao limitar suas responsabilidades, preservamos uma arquitetura limpa, previsível e de fácil manutenção.

Toda regra de negócio continuará pertencendo aos Services, enquanto consultas reutilizáveis permanecerão nos Selectors.

---

# 15. Managers para Soft Delete

Quando um Model utilizar Soft Delete, o Manager deverá ocultar automaticamente os registros excluídos.

Exemplo conceitual:

```python
class AtivoManager(models.Manager):

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(excluido=False)
        )
```

Opcionalmente poderá existir um segundo Manager administrativo.

Exemplo:

```python
objects = AtivoManager()

all_objects = models.Manager()
```

Assim, apenas usuários administrativos terão acesso aos registros removidos logicamente.

---

# 16. Managers Multi-Tenant

Os Managers nunca deverão decidir qual Tenant está ativo.

O isolamento Multi-Tenant pertence às camadas superiores da arquitetura.

Exemplo correto:

```python
Membro.objects.filter(
    igreja=igreja
)
```

Exemplo incorreto:

```python
Membro.objects.da_igreja_atual()
```

O Manager não conhece contexto de requisição.

Essa responsabilidade pertence aos Services ou Selectors.

---

# 17. Managers para Registros Ativos

Managers podem disponibilizar QuerySets utilizados frequentemente.

Exemplo:

```python
class UsuarioManager(models.Manager):

    def ativos(self):
        return self.filter(
            ativo=True
        )
```

Esse tipo de método reduz repetição de filtros simples.

---

# 18. Managers para Publicação

Outro exemplo comum:

```python
class EventoManager(models.Manager):

    def publicados(self):
        return self.filter(
            publicado=True
        )
```

Consultas simples e recorrentes são apropriadas para Managers.

---

# 19. QuerySets Encadeáveis

Sempre que possível, os métodos deverão retornar QuerySets.

Exemplo:

```python
Membro.objects

.ativos()

.order_by("nome")

.select_related("congregacao")
```

Esse padrão aumenta a flexibilidade da API interna.

---

# 20. Managers Abstratos

Quando vários Models compartilharem o mesmo comportamento, utilizar Managers abstratos.

Exemplo:

```python
class BaseManager(models.Manager):

    def ativos(self):
        return self.filter(
            ativo=True
        )
```

Os Managers específicos poderão herdar dessa implementação.

Isso reduz duplicação de código.

---

# 21. Managers e Herança de Models

Em estruturas com herança de Models, cada classe poderá definir seu próprio Manager.

Exemplo:

```text
Pessoa

↓

Membro

↓

Obreiro

↓

Pastor
```

Cada Model poderá possuir comportamentos específicos sem comprometer a hierarquia.

---

# 22. Managers Personalizados

Sempre que houver necessidade de adicionar funcionalidades comuns ao acesso aos dados, utilizar Managers personalizados.

Exemplos:

- registros ativos;
- registros públicos;
- ordenação padrão;
- filtros básicos.

Evitar adicionar qualquer processamento complexo.

---

# 23. Performance

Managers deverão permanecer extremamente leves.

Evitar:

- annotate();
- aggregate();
- Subquery();
- Exists();
- consultas complexas.

Esses recursos pertencem aos Selectors.

---

# 24. Comunicação com QuerySets

O ideal é que o Manager apenas exponha um QuerySet especializado.

Exemplo:

```python
class MembroManager(models.Manager):

    def get_queryset(self):
        return MembroQuerySet(
            self.model,
            using=self._db
        )
```

Isso concentra a lógica de filtragem dentro do QuerySet.

---

# 25. Métodos Permitidos

Exemplos apropriados:

```python
ativos()

inativos()

recentes()

ordenados()

publicados()

visiveis()

disponiveis()
```

Todos possuem comportamento simples e previsível.

---

# 26. Métodos que Devem ser Evitados

Evitar métodos como:

```python
registrar_membro()

cancelar_evento()

calcular_financeiro()

enviar_email()

gerar_relatorio()

importar_planilha()
```

Todos esses pertencem aos Services.

---

# 27. Reutilização

Managers deverão ser reutilizados apenas dentro do próprio domínio do Model.

Quando uma consulta começar a ser utilizada por diversos módulos, ela deverá migrar para um Selector.

---

# 28. Integração com Selectors

Fluxo recomendado:

```text
Model

↓

Manager

↓

Selector

↓

Service

↓

View
```

Cada camada complementa a anterior.

Nenhuma substitui outra.

---

# 29. Organização

Quando necessário:

```text
models.py

↓

querysets.py

↓

managers.py
```

Essa divisão melhora bastante a organização dos Apps maiores.

---

# 30. Documentação

Managers públicos deverão possuir documentação.

Exemplo:

```python
class MembroManager(models.Manager):
    """
    Manager oficial dos membros.

    Contém QuerySets simples e reutilizáveis.
    """
```

A documentação reduz dúvidas durante o desenvolvimento.

---

# 31. Exemplo Completo de um Manager

Abaixo um exemplo de implementação seguindo o padrão oficial do GereIgreja.

```python
from django.db import models

class MembroQuerySet(models.QuerySet):

    def ativos(self):
        return self.filter(ativo=True)

    def inativos(self):
        return self.filter(ativo=False)

    def ordenados(self):
        return self.order_by("nome")


class MembroManager(models.Manager):

    def get_queryset(self):
        return MembroQuerySet(
            self.model,
            using=self._db
        )

    def ativos(self):
        return self.get_queryset().ativos()

    def inativos(self):
        return self.get_queryset().inativos()

    def ordenados(self):
        return self.get_queryset().ordenados()
```

Observe que o Manager apenas expõe métodos simples.

Toda consulta complexa deverá permanecer nos Selectors.

---

# 32. Fluxo Oficial da Arquitetura

A participação dos Managers dentro da arquitetura oficial ocorre da seguinte forma:

```text
View

↓

Service

↓

Selector

↓

Manager

↓

QuerySet

↓

Model

↓

Banco de Dados
```

Cada camada possui responsabilidades claramente definidas.

Essa separação reduz acoplamento e facilita manutenção.

---

# 33. Quando Criar um Manager

Criar um Manager quando houver necessidade de:

- disponibilizar QuerySets padrão;
- encapsular filtros simples;
- definir ordenações frequentes;
- personalizar o acesso padrão ao Model.

Caso contrário, utilizar apenas o Manager padrão do Django.

---

# 34. Quando NÃO Criar um Manager

Não criar Managers para:

- regras de negócio;
- validações complexas;
- integrações;
- relatórios;
- dashboards;
- cálculos;
- consultas estatísticas;
- agregações.

Esses cenários pertencem aos Services ou aos Selectors.

---

# 35. Anti-patterns

Evitar:

- Managers com centenas de linhas;
- chamadas HTTP;
- envio de e-mails;
- acesso a APIs;
- importações;
- lógica financeira;
- regras ministeriais;
- acesso a múltiplos Models;
- consultas extremamente complexas.

Managers não são Services.

Managers não são Selectors.

Managers não são Controllers.

---

# 36. Refatoração

Sempre que um Manager crescer excessivamente:

- mover consultas reutilizáveis para Selectors;
- mover regras de negócio para Services;
- extrair QuerySets personalizados;
- revisar responsabilidades.

O objetivo é manter Managers pequenos e previsíveis.

---

# 37. Checklist para Criação

Antes de implementar um Manager verificar:

- realmente há necessidade?
- o método é simples?
- retorna QuerySet?
- pertence ao próprio Model?
- evita lógica de negócio?
- nome está claro?
- pode ser reutilizado?

Se alguma resposta for negativa, reavaliar a implementação.

---

# 38. Checklist para Revisão

Durante revisões arquiteturais verificar:

- ausência de regras de negócio;
- ausência de integrações externas;
- ausência de cálculos complexos;
- métodos pequenos;
- boa legibilidade;
- documentação atualizada;
- QuerySets reutilizáveis.

Managers devem permanecer enxutos.

---

# 39. Integração com o Ecossistema GBE

Os Managers fazem parte do fluxo oficial da Engenharia do Backend.

```text
Models

↓

Managers

↓

Selectors

↓

Services

↓

Views / APIs
```

Essa organização estabelece uma separação clara entre:

- armazenamento;
- acesso;
- consulta;
- regras de negócio;
- apresentação.

---

# 40. Evolução Contínua

Os Managers deverão evoluir apenas para melhorar o acesso aos Models.

Novos requisitos deverão priorizar:

- reutilização;
- simplicidade;
- padronização;
- baixo acoplamento.

Qualquer aumento significativo de responsabilidade deverá ser tratado por outras camadas da arquitetura.

---

# 41. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GBE-03 — Arquitetura dos Apps
- GBE-04 — Models
- GBE-05 — Services
- GBE-06 — Selectors
- GAF — Framework de Autenticação
- GQF — Framework de Qualidade

---

# 42. Princípios Finais

Os Managers representam a camada mais próxima dos Models dentro da arquitetura do GereIgreja.

Sua missão é disponibilizar um acesso padronizado e conveniente aos dados, sem assumir responsabilidades que pertencem aos Services ou aos Selectors.

Ao manter os Managers pequenos, previsíveis e focados em consultas simples, garantimos uma arquitetura mais limpa, fácil de compreender e preparada para crescer.

A disciplina na utilização dos Managers contribui diretamente para a qualidade, testabilidade e longevidade da plataforma.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `07-Managers.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento passa a definir oficialmente o papel dos Managers na arquitetura do Backend do GereIgreja.


