Pasta:
docs/frontend/

Arquivo:
02-Estrutura-de-Pastas.md

Documento:
GFE-02

Framework:
GereIgreja Frontend Engineering (GFE)

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Julho de 2026

# 02 - Estrutura de Pastas

> *"Uma boa organização de arquivos reduz a complexidade, facilita a manutenção e torna o crescimento da aplicação previsível."*

---

# Sumário

1. Objetivo
2. Filosofia da Organização
3. Estrutura Geral
4. Organização por Responsabilidade
5. Templates
6. Assets
7. Componentes Compartilhados
8. Escalabilidade
9. Documentos Relacionados
10. Princípios Finais

---

# 1. Objetivo

Este documento define a estrutura oficial de diretórios utilizada pelo Frontend do GereIgreja.

Seu objetivo é garantir consistência, facilidade de manutenção e escalabilidade, permitindo que novos módulos sejam incorporados sem comprometer a organização da plataforma.

Toda nova funcionalidade deverá respeitar esta estrutura.

---

# 2. Filosofia da Organização

A organização do Frontend deve refletir a arquitetura da aplicação.

Os diretórios deverão seguir os princípios de:

- responsabilidade única;
- baixo acoplamento;
- reutilização;
- previsibilidade;
- facilidade de navegação;
- padronização.

Nenhuma pasta deverá concentrar responsabilidades distintas.

---

# 3. Estrutura Geral

Estrutura simplificada:

```text
frontend/

templates/

static/

components/

layouts/

partials/

css/

js/

images/

icons/

fonts/
```

Cada diretório possui responsabilidade claramente definida.

---

# 4. Organização por Responsabilidade

Cada grupo de arquivos deverá permanecer separado.

Exemplo:

```text
templates/

↓

Páginas HTML
```

```text
components/

↓

Componentes reutilizáveis
```

```text
layouts/

↓

Estruturas principais
```

```text
partials/

↓

Fragmentos compartilhados
```

Essa separação facilita manutenção e reaproveitamento.

---

# 5. Templates

Os templates representam as páginas da aplicação.

Exemplo:

```text
templates/

dashboard/

financeiro/

membros/

eventos/

escola/

comunicacao/
```

Cada módulo deverá possuir seu próprio conjunto de templates.

Evitar grandes arquivos contendo múltiplas responsabilidades.

---

# 6. Assets

Todos os recursos estáticos deverão permanecer organizados.

Exemplo:

```text
static/

css/

js/

images/

icons/

fonts/

vendor/
```

Bibliotecas externas deverão permanecer separadas dos arquivos produzidos pela equipe.

---

# 7. Componentes Compartilhados

Componentes reutilizados por diversos módulos deverão permanecer centralizados.

Exemplos:

- cards;
- tabelas;
- botões;
- breadcrumbs;
- modais;
- paginação;
- alertas;
- badges;
- dropdowns.

A duplicação de componentes deverá ser evitada.

---

# 8. Escalabilidade

A estrutura foi projetada para suportar:

- crescimento do sistema;
- novos módulos;
- novas áreas administrativas;
- aplicativos móveis;
- painéis especializados;
- temas futuros.

A expansão da plataforma não deverá exigir reorganização significativa dos diretórios.

---

# 9. Documentos Relacionados

- GFE-01 — Frontend Architecture
- GDS — GereIgreja Design System
- GBE-20 — Code Standards

---

# 10. Princípios Finais

Uma estrutura de diretórios consistente facilita a manutenção, reduz a curva de aprendizado de novos desenvolvedores e contribui para a evolução sustentável do Frontend do GereIgreja.

A organização dos arquivos deverá refletir a arquitetura da aplicação e favorecer a reutilização de componentes.

---

## ✅ Parte 1 concluída

---

# 11. Organização por Apps

Cada módulo deverá possuir seus próprios templates e recursos específicos.

Exemplo:

```text
templates/

membros/

financeiro/

eventos/

escola/

comunicacao/

secretaria/
```

Essa organização facilita manutenção e localização dos arquivos.

---

# 12. Convenções de Nomenclatura

Os nomes dos arquivos deverão ser claros e consistentes.

Exemplos:

```text
lista.html

detalhe.html

form.html

modal_excluir.html

card_membro.html

tabela_financeiro.html
```

Evitar abreviações e nomes genéricos.

---

# 13. Layouts

Os layouts representam a estrutura principal da aplicação.

Exemplo:

```text
layouts/

base.html

dashboard.html

auth.html

relatorio.html
```

Os layouts deverão ser reutilizados por todos os módulos.

---

# 14. Partials

Partials representam pequenos fragmentos reutilizáveis.

Exemplos:

- sidebar;
- navbar;
- footer;
- breadcrumbs;
- paginação;
- mensagens;
- filtros.

Evitar duplicação de código HTML.

---

# 15. JavaScript

Os scripts deverão permanecer organizados por responsabilidade.

Exemplo:

```text
js/

core/

components/

pages/

vendor/
```

Evitar grandes arquivos contendo funcionalidades de vários módulos.

---

# 16. CSS

A folha de estilos deverá seguir organização modular.

Exemplo:

```text
css/

base/

components/

layouts/

pages/

themes/
```

Cada arquivo deverá possuir responsabilidade única.

---

# 17. Bibliotecas Externas

Dependências de terceiros deverão permanecer separadas.

Exemplo:

```text
vendor/

bootstrap/

htmx/

alpine/

chartjs/
```

Arquivos externos nunca deverão ser misturados ao código desenvolvido pela equipe.

---

# 18. Boas Práticas

Sempre:

- reutilizar componentes;
- manter estrutura consistente;
- evitar duplicação;
- utilizar nomenclatura padronizada;
- documentar componentes compartilhados.

---

# 19. Anti-patterns

Evitar:

- templates gigantes;
- CSS duplicado;
- JavaScript global excessivo;
- componentes repetidos;
- mistura de responsabilidades;
- arquivos sem padrão de nomenclatura.

---

# 20. Checklist

Antes de criar um novo módulo verificar:

- estrutura criada;
- templates organizados;
- assets separados;
- componentes reutilizados;
- layouts utilizados;
- partials compartilhados;
- documentação atualizada.

---

# 21. Evolução Futura

A estrutura foi projetada para suportar:

- novos módulos;
- múltiplos temas;
- PWA;
- aplicativos móveis;
- componentes compartilhados entre plataformas.

---

# 22. Documentos Relacionados

- GFE-01 — Frontend Architecture
- GFE-03 — Componentes
- GDS — GereIgreja Design System
- GBE-20 — Code Standards

---

# 23. Princípios Finais

A organização dos diretórios do Frontend deve favorecer a manutenção, a reutilização e o crescimento contínuo da plataforma.

Uma estrutura consistente reduz o tempo de desenvolvimento e facilita a colaboração entre os membros da equipe.

---

## ✅ Status

**Pasta:** `docs/frontend/`

**Arquivo:** `02-Estrutura-de-Pastas.md`

**Status:** **CONCLUÍDO (v1.0)**

