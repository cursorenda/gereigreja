Pasta:
docs/backend/

Arquivo:
20-Code-Standards.md

Documento:
GBE-20

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

# 20 - Code Standards

> *"Código limpo não é um luxo. É um compromisso com a qualidade, a manutenção e o futuro da plataforma."*

---

# Sumário

1. Objetivo
2. Filosofia de Desenvolvimento
3. Princípios Gerais
4. Organização do Código
5. Convenções de Nomenclatura
6. Organização de Arquivos
7. Organização de Imports
8. Tipagem (Type Hints)
9. Documentação do Código
10. Documentos Relacionados
11. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais de codificação utilizados no Backend do GereIgreja.

Seu objetivo é garantir consistência, legibilidade, facilidade de manutenção e colaboração entre todos os desenvolvedores da plataforma.

Todo código incorporado ao projeto deverá seguir as diretrizes aqui definidas.

---

# 2. Filosofia de Desenvolvimento

O código do GereIgreja deverá priorizar:

- simplicidade;
- clareza;
- previsibilidade;
- reutilização;
- baixo acoplamento;
- alta coesão;
- facilidade de testes;
- facilidade de manutenção.

Código elegante é consequência de boas decisões arquiteturais.

---

# 3. Princípios Gerais

Todo desenvolvimento deverá respeitar os seguintes princípios:

- responsabilidade única;
- separação de responsabilidades;
- reutilização antes da duplicação;
- legibilidade acima de otimizações prematuras;
- composição antes de herança sempre que possível;
- funções pequenas e objetivas;
- classes com responsabilidade claramente definida.

Sempre que houver dúvida, optar pela solução mais simples.

---

# 4. Organização do Código

Cada componente deverá permanecer na camada apropriada.

Exemplo:

```text
Views

↓

Services

↓

Selectors

↓

Models

↓

Banco de Dados
```

As regras de negócio nunca deverão permanecer nas Views.

Da mesma forma, consultas complexas não deverão ser implementadas diretamente nas Views ou Templates.

---

# 5. Convenções de Nomenclatura

Seguir o padrão oficial da linguagem Python.

Classes:

```python
MembroService
```

```python
EventoSelector
```

Funções:

```python
criar_membro()
```

```python
buscar_eventos()
```

Variáveis:

```python
nome_membro
```

Constantes:

```python
MAX_TENTATIVAS_LOGIN
```

Arquivos:

```text
services.py

selectors.py

validators.py

permissions.py
```

Evitar abreviações desnecessárias.

Os nomes devem comunicar claramente sua finalidade.

---

# 6. Organização de Arquivos

Cada arquivo deverá possuir responsabilidade única.

Exemplo:

```text
services.py

↓

Somente regras de negócio
```

```text
selectors.py

↓

Somente consultas
```

```text
validators.py

↓

Somente validações
```

Evitar arquivos com centenas de responsabilidades diferentes.

Quando necessário, dividir em módulos especializados.

---

# 7. Organização de Imports

A ordem oficial será:

```python
# Biblioteca padrão

# Bibliotecas externas

# Django

# Aplicações internas

# Imports locais
```

Exemplo:

```python
import datetime

from decimal import Decimal

from django.db import models

from membros.services import MembroService

from .validators import validar_cpf
```

Imports circulares deverão ser evitados.

---

# 8. Tipagem (Type Hints)

Sempre que possível utilizar tipagem.

Exemplo:

```python
def calcular_idade(data_nascimento: date) -> int:
```

```python
def buscar_membros() -> QuerySet[Membro]:
```

A tipagem melhora:

- legibilidade;
- autocomplete;
- análise estática;
- documentação.

---

# 9. Documentação do Código

Métodos públicos deverão possuir docstrings quando necessário.

Exemplo:

```python
def criar_membro(...):
    """
    Cria um novo membro realizando todas as validações de domínio.
    """
```

Comentários devem explicar decisões de negócio e não repetir o código.

Ruído deve ser evitado.

---

# 10. Documentos Relacionados

- GBE-05 — Services
- GBE-06 — Selectors
- GBE-17 — Exceptions
- GBE-18 — Testing
- GQF — GereIgreja Quality Framework

---

# 11. Princípios Finais

A padronização do código reduz a complexidade do projeto e facilita sua evolução.

Cada desenvolvedor deverá escrever código como se outra pessoa fosse mantê-lo por muitos anos.

A consistência é mais importante que preferências individuais.

---

## ✅ Parte 1 concluída

---

# 12. Docstrings

Docstrings deverão ser utilizadas em funções públicas, classes e componentes cuja finalidade não seja imediatamente evidente.

Preferir o padrão do Python.

Exemplo:

```python
def criar_membro(dados: dict) -> Membro:
    """
    Cria um novo membro após validar os dados recebidos.

    Args:
        dados: Informações do membro.

    Returns:
        Instância de Membro criada.

    Raises:
        ValidationException:
            Quando os dados forem inválidos.
    """
```

Docstrings não substituem código legível.

---

# 13. Comentários

Comentários deverão explicar decisões, nunca repetir o código.

Bom exemplo:

```python
# Mantém compatibilidade com versões anteriores da API.
```

Ruim exemplo:

```python
# Soma um ao contador.
contador += 1
```

Código claro necessita de poucos comentários.

---

# 14. SOLID

O GereIgreja adota os princípios SOLID.

## S — Single Responsibility

Cada classe possui uma responsabilidade.

---

## O — Open/Closed

Componentes devem permitir extensão sem alteração desnecessária.

---

## L — Liskov

Subclasses devem respeitar o comportamento esperado da classe base.

---

## I — Interface Segregation

Interfaces devem possuir responsabilidades específicas.

---

## D — Dependency Inversion

Sempre depender de abstrações quando apropriado.

---

# 15. Clean Code

Todo código deverá buscar:

- legibilidade;
- simplicidade;
- previsibilidade;
- baixa complexidade;
- facilidade de testes;
- reutilização.

A leitura do código deve ser intuitiva.

---

# 16. DRY, KISS e YAGNI

## DRY (Don't Repeat Yourself)

Evitar duplicação de código.

Sempre avaliar possibilidades de reutilização.

---

## KISS (Keep It Simple, Stupid)

Optar pela solução mais simples que resolva corretamente o problema.

Complexidade desnecessária aumenta o custo de manutenção.

---

## YAGNI (You Aren't Gonna Need It)

Não implementar funcionalidades apenas por imaginar que poderão ser úteis no futuro.

Desenvolver conforme necessidades reais.

---

# 17. TODO, FIXME e HACK

Marcadores temporários deverão ser utilizados com responsabilidade.

Exemplos:

```python
# TODO:
# Implementar cache distribuído.
```

```python
# FIXME:
# Corrigir tratamento de timeout da API externa.
```

```python
# HACK:
# Solução temporária até atualização da biblioteca.
```

Nenhum marcador deverá permanecer indefinidamente no código.

Todos deverão possuir acompanhamento no backlog técnico.

---

# 18. Constantes e Configurações

Valores reutilizáveis não deverão permanecer espalhados pelo código.

Preferir:

- constantes;
- arquivos de configuração;
- variáveis de ambiente;
- Settings do Django.

Evitar "números mágicos" e textos repetidos.

---

# 19. Enums

Sempre que representar conjuntos fixos de opções, utilizar Enums.

Exemplo:

```python
class StatusMembro(TextChoices):
    ATIVO = "ATIVO", "Ativo"
    INATIVO = "INATIVO", "Inativo"
```

Enums aumentam legibilidade e reduzem erros.

---

# 20. Ferramentas de Padronização

O projeto adota ferramentas para manter consistência automática.

Ferramentas recomendadas:

- Ruff;
- Black;
- isort;
- pre-commit;
- mypy (quando aplicável).

Essas ferramentas devem ser executadas antes da abertura de Pull Requests.

---

# 21. Boas Práticas

Sempre:

- escrever código legível;
- utilizar nomes claros;
- evitar duplicação;
- separar responsabilidades;
- utilizar tipagem;
- documentar decisões relevantes;
- revisar código antes do commit;
- manter compatibilidade arquitetural.

A qualidade do código deve ser preservada durante toda a evolução da plataforma.

---

# 22. Anti-patterns

Evitar:

- funções gigantes;
- classes com múltiplas responsabilidades;
- lógica de negócio em Views;
- consultas SQL em Templates;
- duplicação de código;
- comentários desnecessários;
- nomes genéricos;
- imports circulares;
- acoplamento excessivo;
- otimizações prematuras.

Todo anti-pattern aumenta o débito técnico da plataforma.

---

# 23. Checklist Antes do Pull Request

Antes de abrir um Pull Request verificar:

- código formatado;
- imports organizados;
- lint executado;
- testes passando;
- tipagem revisada;
- documentação atualizada;
- comentários desnecessários removidos;
- arquitetura respeitada.

Nenhum Pull Request deverá ser aprovado sem atender a esses critérios.

---

# 24. Evolução Futura

Os padrões definidos neste documento deverão evoluir juntamente com a plataforma.

Novas ferramentas, linguagens e práticas poderão ser incorporadas, desde que preservem:

- consistência;
- simplicidade;
- legibilidade;
- qualidade;
- facilidade de manutenção.

Mudanças significativas deverão ser registradas por meio de ADRs (Architecture Decision Records).

---

# 25. Documentos Relacionados

- GBE-05 — Services
- GBE-06 — Selectors
- GBE-08 — Views
- GBE-17 — Exceptions
- GBE-18 — Testing
- GBE-19 — Performance
- GQF — GereIgreja Quality Framework
- GDF — GereIgreja Documentation Framework

---

# 26. Princípios Finais

O código do GereIgreja representa um patrimônio coletivo da equipe de desenvolvimento.

Cada linha escrita deverá contribuir para uma plataforma mais simples, segura, previsível e sustentável.

A padronização não limita a criatividade do desenvolvedor; ela cria uma base comum que permite inovação com qualidade, reduzindo custos de manutenção e facilitando a evolução contínua do sistema.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `20-Code-Standards.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento consolida o padrão oficial de desenvolvimento do Backend do GereIgreja e encerra a documentação estrutural da engenharia de backend.

