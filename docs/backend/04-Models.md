Pasta:
docs/backend/

Arquivo:
04-Models.md

Documento:
GBE-04

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

# 04 - Models

> "Os Models representam o coração dos dados da plataforma. Uma boa modelagem reduz complexidade, melhora o desempenho e facilita a evolução do sistema."

---

# Sumário

1. Objetivo
2. Filosofia dos Models
3. Papel dos Models na Arquitetura
4. Responsabilidade dos Models
5. Estrutura Oficial
6. Organização do Diretório models/
7. BaseModel
8. Herança entre Models
9. Campos Padronizados
10. Tipos de Relacionamentos
11. Meta Class
12. Managers
13. Métodos dos Models
14. Signals
15. Índices
16. Constraints
17. Multi-Tenant
18. Soft Delete
19. Auditoria
20. Performance
21. Convenções de Nomenclatura
22. Anti-patterns
23. Checklist
24. Documentos Relacionados
25. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para implementação dos Models do GereIgreja.

Seu objetivo é garantir consistência estrutural, facilidade de manutenção, desempenho e integridade dos dados em toda a plataforma.

Todo Model deverá seguir estas diretrizes.

---

# 2. Filosofia dos Models

Os Models representam os dados do domínio.

Eles não representam regras de negócio.

No GereIgreja adotamos o princípio:

> **Models ricos em comportamento do domínio e pobres em processos de negócio.**

Isso significa que um Model pode possuir:

- propriedades;
- pequenos métodos relacionados ao próprio objeto;
- validações locais;
- representações textuais.

Entretanto, regras complexas deverão permanecer nos Services.

---

# 3. Papel dos Models na Arquitetura

Na arquitetura oficial do GereIgreja:

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

O Model representa apenas a persistência e o comportamento intrínseco da entidade.

---

# 4. Responsabilidade dos Models

Um Model poderá conter:

- definição dos campos;
- relacionamentos;
- propriedades;
- pequenos métodos;
- validações simples;
- Meta;
- Managers;
- índices;
- constraints.

Não deverá conter:

- envio de e-mails;
- geração de relatórios;
- integração com APIs;
- regras financeiras complexas;
- regras de negócio extensas.

---

# 5. Estrutura Oficial

Preferencialmente um Model por arquivo.

Exemplo:

```text
models/

__init__.py

membro.py

familia.py

cargo.py

congregacao.py

historico.py
```

Essa organização facilita manutenção e localização.

---

# 6. Organização do Diretório models/

O arquivo `__init__.py` deverá exportar os Models públicos do módulo.

Exemplo:

```python
from .membro import Membro
from .familia import Familia
from .cargo import Cargo
```

Assim, os demais módulos continuam importando normalmente:

```python
from apps.membros.models import Membro
```

---

# 7. BaseModel

Todos os Models persistentes deverão herdar de uma classe base compartilhada.

Exemplo:

```python
class BaseModel(models.Model):

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

Outros campos comuns poderão ser adicionados futuramente, conforme a evolução da plataforma.

A utilização de um BaseModel padroniza todas as entidades e reduz duplicação de código.

---

# 8. Herança entre Models

A herança deverá ser utilizada apenas quando representar uma relação clara de abstração.

Preferir:

- composição;
- relacionamentos;
- classes abstratas.

Evitar cadeias profundas de herança.

---

# 9. Campos Padronizados

Sempre que aplicável, utilizar nomes padronizados.

Exemplos:

```text
nome

descricao

ativo

criado_em

atualizado_em

criado_por

atualizado_por
```

Evitar abreviações.

Utilizar nomes descritivos.

---

# 10. Tipos de Relacionamentos

O GereIgreja utilizará prioritariamente:

## ForeignKey

Relacionamento um para muitos.

---

## OneToOneField

Relacionamentos exclusivos.

---

## ManyToManyField

Relacionamentos muitos para muitos.

Cada relacionamento deverá possuir justificativa clara.

Relacionamentos excessivos aumentam o acoplamento entre módulos.

---

# 11. Meta Class

Sempre utilizar a classe Meta para definir comportamentos do Model.

Exemplos:

- verbose_name;
- verbose_name_plural;
- ordering;
- indexes;
- constraints;
- permissions.

A Meta deverá concentrar apenas configurações estruturais.

---

# 12. Managers

Consultas reutilizáveis diretamente relacionadas ao Model poderão ser implementadas em Managers.

Consultas muito complexas deverão migrar para Selectors.

Managers não substituem Services.

---

# 13. Métodos dos Models

Os métodos deverão representar comportamentos próprios da entidade.

Exemplos válidos:

```python
nome_completo()

idade()

esta_ativo()
```

Exemplos inválidos:

```python
gerar_relatorio()

enviar_email()

importar_planilha()

gerar_pdf()
```

Essas responsabilidades pertencem aos Services.

---

# 14. Signals

Signals deverão ser utilizados apenas para eventos desacoplados.

Nunca implementar regras críticas utilizando Signals.

---

# 15. Índices (Indexes)

Os índices são fundamentais para manter o desempenho da plataforma à medida que o volume de dados cresce.

Todo Model deverá avaliar a necessidade de índices desde sua criação.

Utilizar índices para:

- campos frequentemente pesquisados;
- chaves estrangeiras muito utilizadas;
- filtros recorrentes;
- ordenações frequentes.

Exemplo:

```python
class Meta:
    indexes = [
        models.Index(fields=["nome"]),
        models.Index(fields=["ativo"]),
        models.Index(fields=["criado_em"]),
    ]
```

Evitar criar índices desnecessários, pois eles aumentam o custo de escrita no banco de dados.

Cada índice deverá possuir justificativa técnica.

---

# 16. Constraints

As Constraints garantem integridade dos dados diretamente no banco.

Sempre que possível, utilizar:

- UniqueConstraint;
- CheckConstraint.

Exemplo:

```python
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["igreja", "cpf"],
            name="uq_membro_cpf"
        )
    ]
```

Exemplo de CheckConstraint:

```python
models.CheckConstraint(
    check=Q(idade__gte=0),
    name="idade_positiva"
)
```

A integridade dos dados não deve depender apenas da aplicação.

---

# 17. Multi-Tenant

O GereIgreja é uma plataforma Multi-Tenant.

Todo Model deverá considerar o isolamento entre igrejas.

Sempre que aplicável:

```python
igreja = models.ForeignKey(
    Igreja,
    on_delete=models.PROTECT
)
```

Toda consulta deverá respeitar o tenant ativo.

Jamais permitir acesso aos registros de outra igreja.

O isolamento dos dados é obrigatório.

---

# 18. Soft Delete

Registros importantes não deverão ser removidos fisicamente.

O padrão oficial será Soft Delete.

Exemplo:

```python
ativo = models.BooleanField(default=True)

excluido_em = models.DateTimeField(
    null=True,
    blank=True
)

excluido_por = models.ForeignKey(
    User,
    null=True,
    blank=True,
    on_delete=models.SET_NULL
)
```

Exclusões físicas deverão ocorrer apenas em situações específicas.

Exemplos:

- logs temporários;
- cache;
- sessões;
- tabelas auxiliares.

---

# 19. Auditoria

Sempre que necessário, os Models deverão permitir rastreabilidade.

Campos recomendados:

```python
criado_por

atualizado_por

criado_em

atualizado_em
```

Esses campos poderão ser herdados do BaseModel quando aplicável.

A auditoria complementa o framework GSF (Segurança) e o GOC (Operações).

---

# 20. Performance

Os Models deverão ser projetados considerando desempenho.

Boas práticas:

- evitar relacionamentos desnecessários;
- evitar campos duplicados;
- utilizar tipos corretos;
- criar índices apenas quando necessários;
- evitar consultas N+1;
- revisar consultas frequentes.

O desempenho começa na modelagem.

---

# 21. Tipos de Campos

Utilizar sempre o tipo mais adequado.

Exemplos:

```python
CharField

TextField

BooleanField

DateField

DateTimeField

DecimalField

IntegerField

PositiveIntegerField

EmailField

URLField

UUIDField

JSONField
```

Evitar utilizar `TextField` quando um `CharField` for suficiente.

Da mesma forma, evitar `CharField` para armazenar grandes volumes de texto.

---

# 22. Campos Obrigatórios

Campos obrigatórios deverão refletir necessidades reais do domínio.

Evitar:

```python
null=True
blank=True
```

sem justificativa.

Valores opcionais devem representar uma decisão de negócio.

---

# 23. Escolha de Tipos Numéricos

Para valores financeiros utilizar sempre:

```python
DecimalField
```

Nunca utilizar:

```python
FloatField
```

para valores monetários.

O padrão oficial será:

```python
DecimalField(
    max_digits=12,
    decimal_places=2
)
```

---

# 24. Campos de Escolha (Choices)

Sempre utilizar constantes ou classes de escolha.

Exemplo:

```python
class Status(models.TextChoices):

    ATIVO = "A", "Ativo"

    INATIVO = "I", "Inativo"

    SUSPENSO = "S", "Suspenso"
```

Evitar strings "mágicas" espalhadas pelo sistema.

---

# 25. UUID

Sempre avaliar o uso de UUID para entidades públicas.

Exemplo:

```python
id_publico = models.UUIDField(
    default=uuid.uuid4,
    editable=False,
    unique=True
)
```

Isso reduz exposição de IDs sequenciais.

---

# 26. Exclusão de Registros

Ao definir um relacionamento, escolher cuidadosamente o comportamento de exclusão.

Preferências da plataforma:

```text
PROTECT
```

quando a integridade for prioritária.

```text
SET_NULL
```

quando a relação puder ser perdida.

```text
CASCADE
```

apenas quando a exclusão em cadeia fizer sentido.

Evitar o uso indiscriminado de CASCADE.

---

# 27. Documentação dos Models

Todo Model importante deverá possuir documentação.

Exemplo:

```python
class Membro(BaseModel):
    """
    Representa um membro ativo da igreja.

    Responsável por armazenar os dados
    cadastrais e ministeriais.
    """
```

A documentação facilita manutenção e onboarding.

---

# 28. Exemplos de Modelagem

Boa modelagem:

```text
Membro

↓

Família

↓

Congregação
```

Má modelagem:

```text
Tabela única contendo
centenas de campos
para vários domínios.
```

A separação por entidades facilita evolução e reutilização.

---

# 29. Versionamento da Estrutura

Alterações estruturais deverão ocorrer por meio de migrations.

Nunca alterar diretamente o banco de dados em produção.

Toda migration deverá:

- possuir objetivo claro;
- ser reversível quando possível;
- ser revisada antes do deploy.

---

# 30. Revisão Arquitetural

Antes da criação de um novo Model verificar:

- representa uma entidade do domínio;
- possui responsabilidade única;
- utiliza tipos corretos;
- relacionamentos bem definidos;
- índices necessários;
- constraints adequadas;
- preparado para auditoria;
- preparado para Multi-Tenant;
- documentação iniciada.

---

# 31. BaseModel Oficial do GereIgreja

Todos os Models persistentes da plataforma deverão herdar, direta ou indiretamente, do BaseModel oficial.

Objetivos:

- eliminar duplicação de código;
- padronizar auditoria;
- facilitar evolução da plataforma;
- garantir consistência entre os módulos.

O BaseModel deverá ser abstrato.

Exemplo conceitual:

```python
class BaseModel(models.Model):

    criado_em = models.DateTimeField(auto_now_add=True)

    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

Novos campos comuns poderão ser incorporados futuramente sem necessidade de alterar todos os Models da aplicação.

---

# 32. Evolução do BaseModel

Conforme a plataforma evoluir, o BaseModel poderá ser especializado.

Exemplo:

```text
BaseModel

│

├── AuditModel

├── TenantModel

├── SoftDeleteModel

└── PublicModel
```

Cada classe deverá adicionar apenas responsabilidades relacionadas ao seu objetivo.

Essa abordagem reduz duplicação e melhora a organização.

---

# 33. Exemplo de Modelagem

Exemplo simplificado.

```text
Igreja

│

├── Congregação

│       │

│       ├── Membro

│       │       │

│       │       ├── Cargo

│       │       ├── Ministério

│       │       └── Histórico

│

├── Financeiro

├── Eventos

└── Escola Bíblica
```

A estrutura deve refletir o domínio do negócio.

---

# 34. Exemplo de um Model Bem Estruturado

Características esperadas:

- responsabilidade única;
- poucos métodos;
- relacionamentos claros;
- documentação;
- Meta organizada;
- índices definidos;
- constraints quando necessárias.

Um Model deve ser simples de compreender.

---

# 35. Refatoração de Models

A evolução dos Models faz parte do ciclo natural da plataforma.

Sempre que necessário:

- dividir Models muito grandes;
- remover duplicações;
- revisar relacionamentos;
- melhorar nomes;
- criar índices;
- revisar constraints.

Refatorações deverão preservar compatibilidade sempre que possível.

---

# 36. Estratégia para Crescimento

À medida que a plataforma crescer:

- novos campos deverão ser cuidadosamente avaliados;
- novos relacionamentos deverão respeitar o domínio;
- migrations deverão permanecer pequenas;
- alterações estruturais deverão ser documentadas.

Evitar grandes mudanças estruturais em uma única migration.

---

# 37. Integração com Outros Componentes

Os Models deverão integrar-se naturalmente com:

- Services;
- Selectors;
- Forms;
- APIs;
- Admin;
- Auditoria;
- Permissões.

Cada camada possui responsabilidades distintas.

Os Models não deverão conhecer detalhes dessas implementações.

---

# 38. Exemplos de Entidades do GereIgreja

Exemplos de Models previstos:

Administrativo

- Igreja
- Congregacao
- Usuario
- Perfil

Secretaria

- Membro
- Familia
- Visitante
- Cargo
- HistoricoMinisterial

Financeiro

- Conta
- CategoriaFinanceira
- Lancamento
- CentroDeCusto

Eventos

- Evento
- Inscricao
- Participante

Escola Bíblica

- Classe
- Professor
- Matricula
- Frequencia

Patrimônio

- BemPatrimonial
- Localizacao
- Movimentacao

Essas entidades representam apenas exemplos e poderão evoluir conforme o crescimento da plataforma.

---

# 39. Anti-patterns

Evitar:

- Models com centenas de campos;
- regras de negócio complexas;
- consultas ao banco dentro de propriedades;
- envio de e-mails;
- chamadas para APIs;
- geração de PDFs;
- geração de planilhas;
- processamento financeiro;
- importações de arquivos.

Essas responsabilidades pertencem aos Services.

---

# 40. Padrões Obrigatórios

Todo Model deverá:

- herdar do BaseModel quando aplicável;
- possuir nome descritivo;
- utilizar nomes no singular;
- possuir Meta organizada;
- possuir documentação quando necessário;
- possuir relacionamentos claros;
- possuir tipos corretos;
- respeitar a arquitetura Multi-Tenant.

---

# 41. Checklist para Criação de um Novo Model

Antes da implementação verificar:

- representa uma entidade real do domínio;
- possui responsabilidade única;
- nome adequado;
- tipos de campos corretos;
- relacionamentos revisados;
- índices avaliados;
- constraints definidas;
- auditoria prevista;
- isolamento Multi-Tenant considerado;
- documentação criada;
- migration revisada;
- testes planejados.

Todo novo Model deverá nascer seguindo este padrão.

---

# 42. Checklist para Revisão de um Model Existente

Durante uma revisão arquitetural verificar:

- código limpo;
- métodos pequenos;
- ausência de lógica de negócio;
- ausência de duplicação;
- relacionamentos corretos;
- índices eficientes;
- constraints adequadas;
- documentação atualizada;
- migrations consistentes.

A revisão contínua faz parte da engenharia da plataforma.

---

# 43. Evolução Contínua

Nenhum Model será considerado definitivo.

A evolução da plataforma poderá exigir:

- novos campos;
- novos relacionamentos;
- especialização de entidades;
- otimizações;
- melhorias de desempenho.

Essas mudanças deverão preservar a integridade dos dados e a estabilidade da aplicação.

---

# 44. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GEA-05 — Arquitetura do Banco de Dados
- GBE-01 — Estrutura do Projeto
- GBE-02 — Core da Plataforma
- GBE-03 — Arquitetura dos Apps
- GBE-05 — Managers
- GBE-06 — Selectors
- GAF — Framework de Autenticação
- GQF — Framework de Qualidade

---

# 45. Princípios Finais

Os Models constituem a base estrutural do GereIgreja.

Uma modelagem bem planejada proporciona desempenho, segurança, consistência e facilidade de evolução.

Cada entidade criada deverá refletir fielmente o domínio do negócio, respeitando os princípios arquiteturais definidos pela Engenharia da plataforma.

A qualidade dos Models influencia diretamente todas as demais camadas do sistema.

Por esse motivo, toda nova entidade deverá ser concebida não apenas para atender às necessidades atuais, mas também para permanecer compreensível, consistente e sustentável ao longo dos anos.

A excelência da plataforma começa na qualidade da sua modelagem de dados.

