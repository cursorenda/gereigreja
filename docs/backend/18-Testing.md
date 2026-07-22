Pasta:
docs/backend/

Arquivo:
18-Testing.md

Documento:
GBE-18

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

# 18 - Testing

> *"Software confiável não é aquele que parece funcionar, mas aquele que prova continuamente que continua funcionando."*

---

# Sumário

1. Objetivo
2. Filosofia dos Testes
3. O Papel dos Testes no GereIgreja
4. Arquitetura Oficial
5. Pirâmide de Testes
6. Tipos de Testes
7. Organização dos Testes
8. Estrutura Oficial
9. Convenções de Nomenclatura
10. Documentos Relacionados
11. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para criação, organização e execução dos testes automatizados do Backend do GereIgreja.

Seu objetivo é garantir qualidade, estabilidade, segurança e evolução contínua da plataforma por meio de uma estratégia consistente de testes.

Todos os módulos do sistema deverão possuir cobertura de testes compatível com sua criticidade.

---

# 2. Filosofia dos Testes

Os testes automatizados são parte integrante do desenvolvimento.

Eles não devem ser vistos como uma etapa posterior, mas como um componente da própria engenharia de software.

Os testes têm como objetivos:

- prevenir regressões;
- validar regras de negócio;
- documentar comportamentos esperados;
- facilitar refatorações;
- aumentar a confiança durante evoluções.

---

# 3. O Papel dos Testes no GereIgreja

A suíte de testes possui cinco responsabilidades principais:

- validar funcionalidades;
- garantir estabilidade;
- proteger regras de negócio;
- apoiar integrações contínuas (CI);
- reduzir falhas em produção.

Todo novo recurso deverá ser acompanhado por testes adequados.

---

# 4. Arquitetura Oficial

Fluxo simplificado:

```text
Código

↓

Testes Automatizados

↓

Pipeline CI

↓

Homologação

↓

Produção
```

Nenhuma alteração crítica deverá ser promovida para produção sem validação automatizada.

---

# 5. Pirâmide de Testes

O GereIgreja adota a Pirâmide de Testes como referência.

```text
            Testes E2E
         ----------------
      Testes de Integração
   --------------------------
      Testes Unitários
```

A maior parte da suíte deverá ser composta por testes unitários.

Testes de integração e end-to-end deverão ser utilizados de forma estratégica.

---

# 6. Tipos de Testes

Os principais tipos de testes utilizados são:

## Testes Unitários

Validam componentes isolados.

Exemplos:

- Services;
- Validators;
- Managers;
- Selectors;
- funções utilitárias.

---

## Testes de Integração

Validam a comunicação entre componentes.

Exemplos:

- Service + Banco de Dados;
- API + Service;
- Task + Redis;
- Signal + Model.

---

## Testes Funcionais

Validam fluxos completos da aplicação.

Exemplos:

- cadastro de membro;
- lançamento financeiro;
- envio de e-mail;
- criação de evento.

---

## Smoke Tests

Executam verificações rápidas após alterações importantes.

Objetivo:

confirmar que a aplicação permanece operacional.

---

# 7. Organização dos Testes

Cada app deverá possuir sua própria pasta de testes.

Exemplo:

```text
membros/

tests/

test_models.py

test_services.py

test_selectors.py

test_views.py

test_forms.py

test_permissions.py

test_api.py
```

Evitar concentrar todos os testes em um único arquivo.

---

# 8. Estrutura Oficial

Estrutura recomendada:

```text
tests/

__init__.py

factories.py

fixtures.py

helpers.py

mixins.py

utils.py
```

Arquivos compartilhados deverão permanecer reutilizáveis.

---

# 9. Convenções de Nomenclatura

Utilizar nomes descritivos.

Exemplos:

```text
test_criar_membro()

test_editar_congregacao()

test_usuario_sem_permissao()

test_importacao_excel()

test_envio_email()
```

O nome do teste deve indicar claramente o comportamento esperado.

---

# 10. Documentos Relacionados

- GBE-05 — Services
- GBE-06 — Selectors
- GBE-08 — Views
- GBE-17 — Exceptions
- GQF — GereIgreja Quality Framework

---

# 11. Princípios Finais

Os testes representam um dos pilares da qualidade do GereIgreja.

Toda funcionalidade crítica deverá possuir cobertura automatizada, permitindo evolução contínua da plataforma com segurança e previsibilidade.

---

## ✅ Parte 1 concluída

---

# 12. Cobertura de Testes

Todo módulo deverá possuir cobertura proporcional à sua criticidade.

Recomendação:

| Tipo de Componente | Cobertura Esperada |
|--------------------|-------------------:|
| Services | Alta |
| Selectors | Média |
| Models | Alta |
| Validators | Alta |
| APIs | Alta |
| Views | Média |
| Tasks | Média |
| Signals | Média |
| Middlewares | Média |
| Utilitários | Alta |

A meta é proteger as regras de negócio mais importantes da plataforma.

---

# 13. Pytest

O framework oficial de testes do GereIgreja será o **pytest**, integrado ao Django.

Benefícios:

- sintaxe simples;
- melhor legibilidade;
- excelente integração com Django;
- suporte a fixtures;
- execução paralela;
- amplo ecossistema.

Todo novo teste deverá seguir o padrão definido pela equipe.

---

# 14. Fixtures

As fixtures deverão fornecer dados reutilizáveis para os testes.

Exemplos:

- usuário administrador;
- igreja;
- congregação;
- membro;
- plano ativo;
- categorias financeiras.

As fixtures deverão ser pequenas, independentes e reutilizáveis.

---

# 15. Factories

Sempre que possível, utilizar Factories para criação de objetos.

Exemplo de entidades:

- IgrejaFactory;
- UsuarioFactory;
- CongregacaoFactory;
- MembroFactory;
- EventoFactory;
- LancamentoFinanceiroFactory.

Factories reduzem duplicação e facilitam manutenção.

---

# 16. Mocks e Stubs

Dependências externas deverão ser simuladas.

Exemplos:

- envio de e-mail;
- WhatsApp;
- APIs externas;
- gateways de pagamento;
- armazenamento em nuvem.

Os testes não deverão depender da disponibilidade de serviços externos.

---

# 17. Testes de Permissões

Toda funcionalidade protegida deverá possuir testes específicos.

Validar:

- acesso autorizado;
- acesso negado;
- grupos de usuários;
- escopo da igreja;
- escopo da congregação;
- permissões administrativas.

Permissões representam uma das áreas mais críticas da plataforma.

---

# 18. Testes de APIs

Cada endpoint deverá validar:

- autenticação;
- autorização;
- respostas HTTP;
- estrutura do JSON;
- paginação;
- filtros;
- ordenação;
- validação de entrada;
- tratamento de erros.

As APIs deverão manter comportamento consistente em todas as versões.

---

# 19. Testes de Performance

Algumas funcionalidades deverão possuir testes específicos de desempenho.

Exemplos:

- geração de relatórios;
- importações;
- exportações;
- dashboards;
- consultas complexas.

Esses testes auxiliam na identificação precoce de degradações.

---

# 20. Integração Contínua (CI)

Toda alteração deverá executar automaticamente:

- testes unitários;
- testes de integração;
- verificações de qualidade;
- análise estática (quando aplicável).

A integração contínua reduz a probabilidade de regressões.

---

# 21. Cobertura de Código

A cobertura deverá ser utilizada como indicador de qualidade, e não como objetivo isolado.

Uma cobertura elevada não substitui testes bem projetados.

A prioridade é validar comportamentos relevantes.

---

# 22. Boas Práticas

Sempre:

- escrever testes simples;
- manter independência entre testes;
- utilizar nomes descritivos;
- evitar duplicação;
- reutilizar fixtures;
- reutilizar factories;
- validar regras de negócio;
- revisar testes durante refatorações.

---

# 23. Anti-patterns

Evitar:

- testes dependentes entre si;
- dados fixos desnecessários;
- testes excessivamente longos;
- duplicação de código;
- depender de serviços externos;
- validar detalhes internos da implementação em vez do comportamento.

Os testes devem ser resistentes a mudanças de implementação.

---

# 24. Checklist

Antes de concluir uma funcionalidade verificar:

- testes criados;
- regras de negócio cobertas;
- permissões testadas;
- APIs validadas;
- integrações simuladas;
- cobertura adequada;
- pipeline executando com sucesso.

---

# 25. Evolução Futura

A arquitetura foi preparada para suportar:

- execução paralela de testes;
- testes distribuídos;
- testes end-to-end automatizados;
- testes de carga;
- testes de segurança automatizados;
- integração com ferramentas de análise de cobertura;
- ambientes efêmeros para validação de Pull Requests.

---

# 26. Documentos Relacionados

- GBE-05 — Services
- GBE-08 — Views
- GBE-14 — Tasks
- GBE-16 — Logging
- GBE-17 — Exceptions
- GQF — GereIgreja Quality Framework

---

# 27. Princípios Finais

A qualidade do GereIgreja depende da confiabilidade de sua suíte de testes.

Os testes automatizados deverão evoluir juntamente com a plataforma, protegendo regras de negócio, reduzindo regressões e permitindo que novas funcionalidades sejam desenvolvidas com segurança.

Mais do que medir cobertura, a estratégia oficial de testes busca garantir confiança contínua na evolução do sistema.

---

## ✅ Status

**Pasta:** `docs/backend/`

**Arquivo:** `18-Testing.md`

**Status:** **CONCLUÍDO (v1.0)**

Este documento estabelece o padrão oficial para organização, implementação e execução dos testes automatizados do Backend do GereIgreja.


