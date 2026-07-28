# 12 - Padrões de Testes

> "Qualidade não é medida pela ausência de erros, mas pela capacidade de identificá-los antes que cheguem aos usuários."

---

# Sumário

1. Objetivo
2. Filosofia dos Testes
3. Pirâmide de Testes
4. Estrutura dos Testes
5. Testes Unitários
6. Testes de Integração
7. Testes Funcionais
8. Testes de Regressão
9. Cobertura de Código
10. Organização dos Arquivos
11. Boas Práticas
12. Automação
13. Checklist
14. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para desenvolvimento e manutenção dos testes automatizados do GereIgreja.

Seu objetivo é garantir que novas funcionalidades sejam implementadas com segurança, reduzindo regressões e aumentando a confiabilidade da plataforma.

Toda funcionalidade relevante deverá possuir estratégia de testes compatível com sua criticidade.

---

# 2. Filosofia dos Testes

Os testes fazem parte do desenvolvimento.

Eles não representam uma etapa opcional realizada apenas antes da publicação.

Cada funcionalidade deverá nascer acompanhada de testes proporcionais à sua importância.

Os testes existem para aumentar a confiança na evolução contínua do sistema.

---

# 3. Pirâmide de Testes

O GereIgreja adotará a pirâmide clássica de testes.

```text
          Testes Funcionais
        ---------------------
       Testes de Integração
     -------------------------
        Testes Unitários
```

Priorizar:

- muitos testes unitários;
- quantidade moderada de testes de integração;
- poucos testes funcionais.

Essa distribuição reduz tempo de execução e facilita manutenção.

---

# 4. Estrutura dos Testes

Cada módulo deverá manter seus próprios testes.

Exemplo:

```text
membros/

tests/

├── __init__.py
├── test_models.py
├── test_services.py
├── test_views.py
├── test_forms.py
├── test_permissions.py
└── test_urls.py
```

Os testes deverão acompanhar a organização do módulo.

---

# 5. Testes Unitários

Os testes unitários deverão validar componentes isolados.

Exemplos:

- Models;
- Services;
- Validators;
- Helpers;
- Selectors;
- Managers.

Cada teste deverá verificar apenas um comportamento específico.

---

# 6. Testes de Integração

Os testes de integração deverão validar a comunicação entre diferentes componentes da arquitetura.

Exemplos:

- View + Service;
- Service + Model;
- Form + Service;
- API + Banco de Dados.

O objetivo é garantir que os componentes funcionem corretamente em conjunto.

---

# 7. Testes Funcionais

Os testes funcionais deverão simular o comportamento do usuário.

Exemplos:

- autenticação;
- cadastro;
- edição;
- exclusão;
- navegação;
- fluxos completos.

Esses testes validam a experiência da aplicação como um todo.

---

# 8. Testes de Regressão

Sempre que um erro for corrigido, deverá ser criado um teste que impeça seu reaparecimento.

Cada bug corrigido representa uma oportunidade de fortalecer a qualidade da plataforma.

---

# 9. Cobertura de Código

A cobertura deverá ser utilizada como indicador, e não como objetivo absoluto.

Priorizar a cobertura das áreas críticas:

- autenticação;
- permissões;
- financeiro;
- secretaria;
- integrações;
- APIs.

Mais importante que a quantidade é a qualidade dos testes.

---

# 10. Organização dos Arquivos

Os testes deverão possuir nomes claros e padronizados.

Exemplos:

- test_models.py
- test_views.py
- test_services.py
- test_permissions.py
- test_forms.py

Cada arquivo deverá concentrar apenas testes relacionados ao seu componente.

---

# 11. Boas Práticas

Os testes deverão ser:

- independentes;
- rápidos;
- previsíveis;
- legíveis;
- reutilizáveis.

Evitar dependência entre testes.

Cada teste deverá preparar seu próprio ambiente.

---

# 12. Automação

Os testes deverão ser executados automaticamente sempre que possível.

O time deverá padronizar o comando de execução por contexto (local e CI),
evitando alternância aleatória de runners entre ambientes.

Para este projeto, é aceitável utilizar tanto `python manage.py test --settings=core.settings_test`
quanto `python -m pytest -q`, desde que o comando oficial do pipeline esteja documentado e seja
executado de forma consistente.

Quando houver inconsistência de descoberta por rótulo/pacote no Django test runner,
o pytest deverá ser adotado como alternativa preferencial para esse escopo.

Recomenda-se integração futura com pipelines de CI/CD para:

- execução automática;
- geração de relatórios;
- análise de cobertura;
- bloqueio de falhas antes do deploy.

A automação fortalece a confiabilidade da plataforma.

---

# 13. Checklist

Antes da publicação verificar:

- testes criados;
- cenários críticos cobertos;
- regressões verificadas;
- permissões testadas;
- documentação atualizada;
- cobertura analisada.

---

# 14. Princípios Finais

Os testes representam um investimento na qualidade e na evolução sustentável do GereIgreja.

Cada funcionalidade testada reduz riscos, facilita refatorações e aumenta a confiança da equipe durante o desenvolvimento.

Toda nova implementação deverá considerar os testes como parte integrante da arquitetura definida pela GereIgreja Engineering Architecture (GEA).