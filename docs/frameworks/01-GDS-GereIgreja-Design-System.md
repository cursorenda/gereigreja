Pasta:
docs/frameworks/

Arquivo:
01-GDS-GereIgreja-Design-System.md

Documento:
GDS-01

Framework:
GDS — GereIgreja Design System

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 01 - GereIgreja Design System (GDS)

> "A identidade visual da plataforma deve transmitir organização, confiança e profissionalismo antes mesmo do usuário interagir com suas funcionalidades."

---

# Sumário

1. Objetivo
2. O que é o GDS
3. Filosofia do Design System
4. Princípios de Design
5. Identidade Visual
6. Paleta Oficial
7. Tipografia
8. Espaçamentos
9. Componentes
10. Layout
11. Responsividade
12. Acessibilidade
13. Organização do CSS
14. Evolução do GDS
15. Checklist
16. Documentos Relacionados
17. Princípios Finais

---

# 1. Objetivo

O GereIgreja Design System (GDS) define os padrões oficiais de interface utilizados em toda a plataforma.

Seu objetivo é garantir consistência visual, reutilização de componentes, acessibilidade, facilidade de manutenção e uma experiência uniforme para todos os usuários.

Toda interface desenvolvida para o GereIgreja deverá seguir este framework.

---

# 2. O que é o GDS

O GDS é o conjunto oficial de diretrizes visuais e componentes reutilizáveis da plataforma.

Ele define como a interface deve ser construída, evoluída e mantida.

O Design System não é apenas um conjunto de estilos, mas uma linguagem visual compartilhada por todos os módulos do GereIgreja.

---

# 3. Filosofia do Design System

Toda interface deverá transmitir:

- simplicidade;
- organização;
- clareza;
- confiança;
- consistência;
- acessibilidade.

O usuário nunca deverá perceber diferenças visuais entre módulos desenvolvidos por equipes distintas.

---

# 4. Princípios de Design

O GDS é baseado nos seguintes princípios:

- consistência;
- reutilização;
- simplicidade;
- acessibilidade;
- responsividade;
- previsibilidade;
- evolução contínua.

Cada componente deverá possuir comportamento uniforme em toda a plataforma.

---

# 5. Identidade Visual

A identidade visual oficial do GereIgreja utiliza uma linguagem moderna, limpa e profissional.

Os elementos visuais deverão privilegiar:

- boa legibilidade;
- contraste adequado;
- espaçamento consistente;
- baixo ruído visual;
- foco no conteúdo.

O design deve apoiar a produtividade dos usuários.

---

# 6. Paleta Oficial

A paleta oficial utiliza o turquesa como cor institucional.

### Cor da Marca

- Brand 700 — #0D8281
- Brand 900 — #0A6665
- Brand Soft — #DFF4F3

### Neutros

- Background — #F1F5F9
- Surface — #FFFFFF
- Border — #D7E2E8
- Text — #1E293B
- Text Muted — #64748B

### Semânticas

- Success — #10B981
- Warning — #D97706
- Danger — #EF4444

Todas as cores deverão ser utilizadas através dos tokens oficiais do Design System.

---

# 7. Tipografia

A plataforma utilizará exclusivamente as famílias tipográficas definidas no Design System.

Padrões:

- Fonte principal (Sans)
- Fonte monoespaçada (Mono)
- Escala tipográfica oficial
- Hierarquia consistente de títulos

Não deverão ser introduzidas novas fontes sem aprovação da Engenharia.

---

# 8. Espaçamentos

Todos os componentes deverão utilizar a escala oficial de espaçamentos.

Evitar margens e paddings arbitrários.

O alinhamento consistente melhora a percepção de qualidade da interface.

---

# 9. Componentes

Todos os componentes reutilizáveis deverão seguir o GDS.

Exemplos:

- botões;
- cards;
- formulários;
- tabelas;
- badges;
- modais;
- alertas;
- dropdowns;
- breadcrumbs;
- paginação;
- menus;
- abas;
- indicadores.

Novos componentes deverão ser documentados antes de serem utilizados.

---

# 10. Layout

Todas as telas deverão seguir uma estrutura comum.

```text
Cabeçalho
    │
    ▼
Menu de Navegação
    │
    ▼
Área de Conteúdo
    │
    ▼
Componentes
    │
    ▼
Rodapé (quando aplicável)
```

Essa organização facilita navegação e aprendizado da plataforma.

---

# 11. Responsividade

Toda interface deverá funcionar adequadamente em:

- desktops;
- notebooks;
- tablets;
- smartphones.

A experiência deverá permanecer consistente em diferentes tamanhos de tela.

---

# 12. Acessibilidade

O Design System deverá seguir boas práticas de acessibilidade.

Entre elas:

- contraste adequado;
- foco visível;
- navegação por teclado;
- textos alternativos;
- hierarquia correta de títulos;
- componentes acessíveis.

A acessibilidade faz parte da qualidade da plataforma.

---

# 13. Organização do CSS

Toda estilização deverá utilizar os tokens oficiais definidos em:

```text
static/css/design_system.css
```

Não deverão existir:

- cores hardcoded;
- estilos inline desnecessários;
- duplicação de regras;
- componentes fora do padrão.

O CSS deverá ser organizado por responsabilidade.

---

# 14. Evolução do GDS

O Design System deverá evoluir continuamente.

Toda alteração deverá preservar compatibilidade sempre que possível.

Novos componentes deverão seguir a identidade visual já estabelecida.

A evolução deverá ocorrer de forma controlada e documentada.

---

# 15. Checklist

Antes da publicação de qualquer interface verificar:

- utiliza componentes oficiais;
- utiliza tokens do GDS;
- respeita a paleta oficial;
- possui responsividade;
- atende aos critérios de acessibilidade;
- evita CSS inline;
- segue os padrões de layout.

---

# 16. Documentos Relacionados

- GEA-02 — Arquitetura da Plataforma
- GEA-04 — Arquitetura do Frontend
- GDF — Framework de Documentação
- GQF — Framework de Qualidade

---

# 17. Princípios Finais

O GereIgreja Design System representa a identidade visual oficial da plataforma.

Seu objetivo é garantir que todas as telas transmitam a mesma sensação de organização, profissionalismo e confiabilidade.

A consistência visual reduz a curva de aprendizado, melhora a experiência do usuário e fortalece a identidade do GereIgreja como plataforma de gestão para igrejas.