# 06 - Padrões de Views

> "As Views coordenam o fluxo da aplicação. Elas não são responsáveis pela lógica de negócio."

---

# Sumário

1. Objetivo
2. Filosofia das Views
3. Responsabilidades
4. Class Based Views
5. Function Based Views
6. Organização
7. Contexto
8. Integração com Services
9. Permissões
10. Tratamento de Erros
11. Performance
12. Logging
13. Testes
14. Checklist
15. Princípios Finais

---

# 1. Objetivo

Este documento estabelece os padrões oficiais para implementação das Views do GereIgreja.

As Views possuem como responsabilidade coordenar o fluxo entre o usuário, os serviços da aplicação e a interface.

Toda View deverá permanecer simples, organizada e previsível.

---

# 2. Filosofia das Views

As Views existem para controlar o fluxo da aplicação.

Uma View deve:

- receber a requisição;
- validar permissões;
- validar formulários;
- chamar Services;
- montar o contexto;
- devolver a resposta.

A View nunca deverá concentrar regras complexas de negócio.

---

# 3. Responsabilidades

As responsabilidades das Views incluem:

- autenticação;
- autorização;
- validação inicial;
- renderização;
- redirecionamentos;
- comunicação com Services.

Qualquer processamento complexo deverá ser delegado aos Services.

---

# 4. Class Based Views

O GereIgreja adotará prioritariamente Class Based Views (CBVs).

Sempre que possível utilizar:

- ListView;
- DetailView;
- CreateView;
- UpdateView;
- DeleteView;
- TemplateView.

As CBVs reduzem duplicação de código, facilitam reutilização e mantêm maior padronização arquitetural.

---

# 5. Function Based Views

Function Based Views poderão ser utilizadas quando a simplicidade justificar.

Exemplos:

- APIs pequenas;
- endpoints AJAX;
- webhooks;
- rotinas muito específicas.

A escolha deverá considerar clareza, legibilidade e facilidade de manutenção.

---

# 6. Organização

Uma View deverá possuir fluxo simples.

Ordem recomendada:

- decorators;
- classe;
- atributos;
- métodos públicos;
- métodos privados.

Métodos extensos deverão ser refatorados em funções auxiliares ou Services.

---

# 7. Contexto

O contexto enviado aos Templates deverá conter apenas as informações necessárias.

Evitar:

- consultas repetidas;
- processamento excessivo;
- objetos desnecessários.

Sempre priorizar simplicidade e desempenho.

---

# 8. Integração com Services

Toda regra de negócio deverá ser executada por Services.

Fluxo recomendado:

View

↓

Service

↓

Model

Essa separação facilita manutenção, testes e reutilização de código.

---

# 9. Permissões

Toda View deverá validar permissões antes de executar operações críticas.

Sempre utilizar, quando aplicável:

- LoginRequiredMixin;
- PermissionRequiredMixin;
- decorators;
- classes de permissões próprias.

Nunca confiar apenas na interface para restringir acesso.

---

# 10. Tratamento de Erros

Toda View deverá tratar situações inesperadas.

Exemplos:

- objetos inexistentes;
- permissões negadas;
- formulários inválidos;
- exceções conhecidas.

Mensagens apresentadas ao usuário deverão ser claras e orientativas.

Erros técnicos deverão ser registrados em log.

---

# 11. Performance

As Views deverão evitar:

- consultas duplicadas;
- loops contendo consultas ao banco;
- processamento excessivo.

Sempre considerar:

- select_related();
- prefetch_related();
- paginação;
- cache quando apropriado.

Performance deve ser considerada desde o desenvolvimento.

---

# 12. Logging

Eventos relevantes poderão ser registrados.

Exemplos:

- operações críticas;
- erros inesperados;
- alterações administrativas;
- tentativas de acesso não autorizado.

O Logging deverá apoiar auditoria, suporte e monitoramento.

---

# 13. Testes

Toda View importante deverá possuir testes automatizados.

Priorizar testes de:

- autenticação;
- permissões;
- respostas HTTP;
- contexto;
- formulários;
- redirecionamentos.

---

# 14. Checklist

Antes da publicação verificar:

- responsabilidades bem definidas;
- permissões implementadas;
- Services utilizados corretamente;
- consultas otimizadas;
- tratamento de erros implementado;
- documentação atualizada;
- testes previstos ou implementados.

---

# 15. Princípios Finais

As Views representam o ponto de entrada da aplicação.

Seu papel é coordenar o fluxo entre usuários, regras de negócio e interface.

Uma View deve permanecer leve, previsível e focada exclusivamente na coordenação das requisições.

Views simples produzem sistemas mais organizados, reutilizáveis, testáveis e fáceis de evoluir, preservando a arquitetura definida pelo GereIgreja Engineering Architecture (GEA).