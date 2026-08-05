---
Documento: GFE-02
Título: Estrutura de Pastas do Frontend
Seção: Frontend Engineering
Versão: 2.0
Status: Oficial
Responsável: Equipe de Engenharia
Última atualização: Julho de 2026
---

# GFE-02 — Estrutura de Pastas do Frontend

> "Uma estrutura de diretórios consistente é fundamental para garantir escalabilidade, reutilização e facilidade de manutenção."

---

# Sumário

1. Objetivo
2. Escopo
3. Princípios da Organização
4. Estrutura Geral
5. Organização dos Templates
6. Organização dos Arquivos Estáticos
7. Organização por Apps
8. Convenções de Nomenclatura
9. Especificações Oficiais
10. Checklist
11. Documentos Relacionados

---

# 1. Objetivo

Este documento define a organização oficial da estrutura de diretórios da camada de Frontend do GereIgreja.

Seu objetivo é estabelecer um padrão único para armazenamento de templates, arquivos estáticos e recursos reutilizáveis, garantindo consistência entre todos os módulos da plataforma.

As diretrizes aqui descritas são obrigatórias para novos desenvolvimentos e para a evolução dos módulos existentes.

---

# 2. Escopo

Este documento aplica-se exclusivamente à camada de apresentação do GereIgreja, abrangendo:

- templates Django;
- arquivos HTML;
- layouts;
- includes;
- partials;
- arquivos CSS;
- arquivos JavaScript;
- imagens;
- fontes;
- demais recursos estáticos.

Não fazem parte deste documento:

- arquitetura do Backend;
- organização dos Apps Django;
- regras de negócio;
- modelos de dados;
- APIs.

Esses assuntos são documentados na coleção **GBE — GereIgreja Backend Engineering**.

---

# 3. Princípios da Organização

A estrutura do Frontend do GereIgreja foi concebida seguindo os seguintes princípios, que funcionam como guia oficial para evolução e manutenção.

Em muitos pontos o projeto já está alinhado a esses princípios; em outros, ainda há trechos legados que estão sendo migrados progressivamente para o padrão consolidado.

## 3.1 Clareza

Cada arquivo deve possuir um local único e previsível.

O desenvolvedor deve conseguir localizar rapidamente qualquer recurso sem depender de conhecimento prévio do projeto.

---

## 3.2 Reutilização

Layouts, componentes e recursos compartilhados devem ser centralizados sempre que possível.

Duplicação de arquivos deve ser evitada.

---

## 3.3 Modularização

Cada App mantém seus próprios recursos específicos, preservando independência entre módulos.

Recursos compartilhados permanecem centralizados.

---

## 3.4 Escalabilidade

A estrutura deve permitir crescimento contínuo da plataforma sem exigir reorganizações frequentes.

Novos módulos devem seguir o padrão estabelecido neste documento.

---

# 4. Estrutura Geral

A organização do Frontend baseia-se em duas grandes categorias:

```text
templates/
static/
```

Cada uma possui responsabilidades claramente definidas.

## Templates

Responsáveis pela renderização das páginas da aplicação.

Incluem:

- layouts;
- páginas;
- includes;
- partials;
- dashboards;
- templates específicos de cada App.

---

## Static

Responsável pelos recursos enviados diretamente ao navegador.

Inclui:

- CSS;
- JavaScript;
- imagens;
- ícones;
- fontes;
- arquivos auxiliares.

A separação entre templates e arquivos estáticos é obrigatória.

---

# 5. Organização dos Templates

Os templates seguem a estrutura oficial do Django Templates.

Os principais grupos atualmente utilizados são:

```text
templates/

admin/
includes/
partials/

<app_1>/
<app_2>/
<app_3>/
...
```

Cada grupo possui responsabilidades específicas.

A organização detalhada dos layouts será apresentada no documento **GFE-04 — Layouts**.

A organização dos templates será aprofundada no documento **GFE-05 — Templates**.

### Organização Atual

O GereIgreja adota um modelo híbrido para organização dos templates.

Atualmente coexistem:

- repositórios globais de templates compartilhados;
- templates específicos de cada App.

Essa estratégia permite alta reutilização sem comprometer a autonomia dos módulos.

#### Includes

Os arquivos presentes em `templates/includes/` representam infraestrutura compartilhada da interface.

Exemplos atuais:

- app_footer.html
- auth_footer.html
- public_footer.html
- footer_social_links.html

#### Partials

Os partials seguem duas abordagens complementares:

- um repositório global (`templates/partials/`) para fragmentos reutilizáveis;
- subpastas próprias dentro de alguns Apps para fragmentos específicos daquele domínio.

Essa organização reduz duplicação e preserva a independência entre módulos.

Não existe atualmente uma pasta `components/`.
A reutilização de interface é baseada em **layouts**, **includes** e **partials**.


---

# 6. Organização dos Arquivos Estáticos

A organização predominante dos arquivos estáticos é global.

Exemplo:

```text
static/

css/
js/
img/
fonts/
```

Além da estrutura global, alguns Apps possuem recursos próprios quando necessário.

Essa abordagem é utilizada apenas para arquivos fortemente relacionados ao domínio daquele módulo.

Atualmente não existe uma pasta `vendor/`.

As bibliotecas de terceiros, como Bootstrap e Font Awesome, são predominantemente carregadas por CDN nos templates base.

---

# 7. Organização por Apps

Cada App pode possuir seus próprios templates.

Exemplo conceitual:

```text
templates/

financeiro/
secretaria/
comunicacao/
eventos/
escola_biblica/
...
```

Essa organização reduz acoplamento e facilita manutenção.

Recursos compartilhados não devem ser duplicados entre Apps.

# 8. Convenções de Nomenclatura

A organização dos diretórios e arquivos do Frontend deve seguir um padrão consistente de nomenclatura, facilitando a localização de recursos e reduzindo ambiguidades durante o desenvolvimento.

## 8.1 Princípios Gerais

As convenções adotadas pelo GereIgreja seguem os seguintes princípios:

- nomes curtos e descritivos;
- utilização de letras minúsculas;
- separação de palavras por underscore (`_`) quando necessário;
- nomes coerentes com o domínio de negócio;
- evitar abreviações que não sejam amplamente conhecidas pela equipe.

Exemplos:

```text
base.html
base_com_menu.html
dashboard_base.html
gerenciar_assinatura.html
listar_membros.html
form_visitante.html
```

---

## 8.2 Templates

Os templates devem representar claramente sua finalidade.

Exemplos:

```text
listar_*.html
detalhes_*.html
editar_*.html
novo_*.html
form_*.html
modal_*.html
```

Templates genéricos devem permanecer nas pastas compartilhadas.

Templates específicos devem permanecer dentro do respectivo App.

---

## 8.3 Includes

Os arquivos da pasta `includes` representam infraestrutura compartilhada da interface.

Exemplos atuais:

```text
app_footer.html
auth_footer.html
public_footer.html
footer_social_links.html
```

Os includes não devem conter regras de negócio.

Sua responsabilidade é exclusivamente estrutural.

---

## 8.4 Partials

Os partials representam fragmentos reutilizáveis de interface.

Atualmente o GereIgreja adota um modelo híbrido:

- `templates/partials/` para fragmentos compartilhados;
- `partials/` internas em alguns Apps para componentes específicos daquele domínio.

Sempre que um partial passar a ser utilizado por mais de um módulo, recomenda-se sua migração para o repositório global.

---

## 8.5 Arquivos Estáticos

Os arquivos estáticos seguem nomenclatura coerente com sua finalidade.

Exemplos:

```text
dashboard-base.css
dashboard-sidebar.js
financeiro.css
secretaria.js
```

Evitar nomes genéricos como:

```text
novo.css
teste.js
arquivo2.css
```

---

# 9. Especificações Oficiais

As especificações desta seção estabelecem regras obrigatórias para a organização da camada de Frontend.

---

## GFE-STR-001

A separação entre templates e arquivos estáticos é obrigatória.

Templates pertencem à pasta `templates/`.

Arquivos CSS, JavaScript, imagens e fontes pertencem à pasta `static/`.

---

## GFE-STR-002

Recursos compartilhados deverão permanecer centralizados sempre que possível.

Duplicação entre módulos deve ser evitada.

---

## GFE-STR-003

Templates específicos de um domínio poderão permanecer dentro do respectivo App.

Essa organização preserva a independência entre os módulos da plataforma.

---

## GFE-STR-004

O GereIgreja adota oficialmente a reutilização baseada em:

- Layouts;
- Includes;
- Partials.

Atualmente não existe uma pasta oficial denominada `components`.

---

## GFE-STR-005

Os partials seguem um modelo híbrido.

São permitidos:

- partials globais para reutilização entre módulos;
- partials específicos dentro dos Apps quando representarem funcionalidades exclusivas daquele domínio.

---

## GFE-STR-006

Bibliotecas externas não devem ser copiadas para uma estrutura própria de `vendor` sem necessidade arquitetural.

O carregamento por CDN permanece o padrão atual da plataforma, salvo quando requisitos técnicos justificarem outra abordagem.

---

## GFE-STR-007

Toda nova estrutura de diretórios deverá respeitar a arquitetura oficial definida neste documento.

A criação de novas convenções paralelas deverá ser previamente avaliada pela equipe de arquitetura.

---

# 10. Checklist

Antes de concluir alterações na estrutura do Frontend, verificar:

- [ ] Templates armazenados na pasta correta.
- [ ] Arquivos estáticos separados dos templates.
- [ ] Includes utilizados apenas para infraestrutura compartilhada.
- [ ] Partials posicionados corretamente (global ou específico do App).
- [ ] Ausência de duplicação desnecessária.
- [ ] Nomenclatura consistente.
- [ ] Organização compatível com a arquitetura oficial.
- [ ] Referências aos layouts preservadas.
- [ ] Recursos compartilhados reutilizados sempre que possível.

---

# 11. Documentos Relacionados

- GFE-01 — Frontend Architecture
- GFE-03 — Componentes
- GFE-04 — Layouts
- GFE-05 — Templates
- GFE-06 — Assets
- GDS — GereIgreja Design System
- GDF — GereIgreja Documentation Framework
- GQF — GereIgreja Quality Framework

