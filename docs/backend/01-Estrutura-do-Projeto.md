Pasta:
docs/backend/

Arquivo:
01-Estrutura-do-Projeto.md

Documento:
GBE-01

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

# 01 - Estrutura do Projeto

> "Uma boa estrutura reduz a complexidade antes mesmo da primeira linha de código ser escrita."

---

# Sumário

1. Objetivo
2. Filosofia da Estrutura
3. Organização Geral
4. Diretórios Principais
5. Apps
6. Core
7. Configurações
8. Recursos Compartilhados
9. Organização dos Arquivos
10. Convenções
11. Evolução da Estrutura
12. Checklist
13. Documentos Relacionados
14. Princípios Finais

---

# 1. Objetivo

Este documento define a estrutura oficial do projeto Backend do GereIgreja.

Seu objetivo é garantir que todo o código permaneça organizado, previsível e fácil de manter durante toda a evolução da plataforma.

Toda alteração estrutural deverá respeitar as diretrizes aqui estabelecidas.

---

# 2. Filosofia da Estrutura

A organização do projeto deverá privilegiar:

- simplicidade;
- modularidade;
- separação de responsabilidades;
- reutilização;
- escalabilidade.

A estrutura do projeto deve facilitar a localização de qualquer componente em poucos segundos.

---

# 3. Organização Geral

Estrutura simplificada:

```text
gereigreja/

apps/

core/

config/

docs/

requirements/

static/

media/

templates/

manage.py
```

Cada diretório possui uma responsabilidade claramente definida.

---

# 4. Diretórios Principais

## apps/

Contém todos os módulos funcionais da plataforma.

Exemplos:

- membros;
- financeiro;
- eventos;
- ebd;
- patrimônio;
- comunicação.

Cada app representa um domínio específico do sistema.

---

## core/

Contém componentes compartilhados.

Exemplos:

- classes base;
- mixins;
- helpers;
- utilitários;
- permissões;
- componentes reutilizáveis.

O Core nunca deverá conter regras específicas de um módulo.

---

## config/

Centraliza a configuração da aplicação.

Inclui:

- settings;
- urls principais;
- ASGI;
- WSGI;
- configurações do ambiente.

---

## docs/

Documentação oficial da Engenharia.

Toda decisão arquitetural deverá ser registrada neste diretório.

---

## static/

Arquivos estáticos compartilhados.

Exemplos:

- CSS;
- JavaScript;
- imagens;
- ícones.

---

## media/

Arquivos enviados pelos usuários.

Seu conteúdo nunca deverá ser versionado no Git.

---

## templates/

Templates compartilhados entre diversos módulos.

Templates específicos deverão permanecer dentro do próprio app.

---

# 5. Apps

Cada App Django deverá seguir a arquitetura oficial definida pelo documento GEA-03.

Os Apps deverão ser independentes e representar um único domínio de negócio.

---

# 6. Core

O Core representa a base compartilhada da plataforma.

Seu objetivo é evitar duplicação de código.

Somente funcionalidades reutilizadas por dois ou mais módulos deverão ser movidas para o Core.

---

# 7. Configurações

As configurações deverão permanecer desacopladas do código.

Utilizar:

- variáveis de ambiente;
- arquivos específicos por ambiente;
- configurações centralizadas.

Nunca armazenar informações sensíveis diretamente no código.

---

# 8. Recursos Compartilhados

Os recursos compartilhados incluem:

- componentes de interface;
- classes base;
- permissões;
- middlewares;
- context processors;
- helpers;
- utilitários.

Esses recursos deverão permanecer organizados por responsabilidade.

---

# 9. Organização dos Arquivos

Cada arquivo deverá possuir responsabilidade única.

Evitar arquivos excessivamente grandes.

Sempre que necessário, dividir funcionalidades em novos módulos internos.

---

# 10. Convenções

O projeto deverá seguir convenções padronizadas para:

- nomes de arquivos;
- nomes de classes;
- nomes de funções;
- nomes de variáveis;
- estrutura dos diretórios.

A padronização reduz a curva de aprendizado da equipe.

---

# 11. Evolução da Estrutura

A estrutura poderá evoluir conforme a plataforma crescer.

Entretanto, mudanças estruturais deverão preservar compatibilidade e organização.

Toda alteração relevante deverá ser documentada.

---

# 12. Checklist

Antes de criar novos diretórios verificar:

- responsabilidade bem definida;
- aderência à arquitetura;
- ausência de duplicação;
- documentação atualizada;
- impacto nos demais módulos.

---

# 13. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-03 — Arquitetura dos Módulos
- GDF — Documentation Framework
- GQF — Quality Framework

---

# 14. Princípios Finais

A estrutura do projeto representa a organização física da Engenharia do GereIgreja.

Uma estrutura consistente reduz custos de manutenção, facilita o desenvolvimento colaborativo e permite que a plataforma evolua preservando simplicidade e qualidade.
