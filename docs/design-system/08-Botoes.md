Pasta:
docs/design-system/

Arquivo:
08-Botoes.md

Documento:
GDS-08

Código:
GDS-BUTTONS

Framework:
GereIgreja Design System (GDS)

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Agosto de 2026

# GDS-08 — Botões

> *"Os botões são o principal ponto de interação entre o usuário e a plataforma. No GereIgreja, eles devem transmitir claramente sua finalidade, prioridade e impacto, oferecendo uma experiência consistente, acessível e previsível em todos os módulos."*

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia dos Botões
4. Princípios
5. Arquitetura
6. Hierarquia de Ações
7. Variantes Oficiais
8. Tamanhos
9. Ícones
10. Estados
11. Casos Reais do GereIgreja
12. Relação com os Demais Frameworks

---

# 1. Objetivo

Este documento estabelece o padrão oficial para todos os botões utilizados no GereIgreja.

Seu objetivo é garantir:

- consistência visual;
- previsibilidade das ações;
- excelente experiência do usuário;
- acessibilidade;
- reutilização de componentes;
- facilidade de manutenção.

Nenhum botão deverá ser implementado fora das diretrizes deste documento.

---

# 2. Escopo

Aplica-se a:

- Área de Gestão;
- Portal Público;
- Landing Pages;
- Dashboards;
- Formulários;
- Tabelas;
- Modais;
- Alertas;
- Wizards;
- Componentes reutilizáveis.

---

# 3. Filosofia dos Botões

Cada botão comunica ao usuário uma intenção.

Sua aparência deve indicar imediatamente:

- prioridade;
- nível de risco;
- consequência da ação;
- frequência de utilização.

Botões são elementos de decisão e não apenas componentes visuais.

---

# 4. Princípios

Todo botão deverá respeitar:

- clareza;
- simplicidade;
- consistência;
- acessibilidade;
- previsibilidade;
- reutilização;
- responsividade.

---

# 5. Arquitetura

Todo botão deverá ser composto por:

```
Container

↓

Ícone (opcional)

↓

Texto

↓

Estado

↓

Evento
```

A separação dessas responsabilidades facilita evolução e manutenção.

---

# 6. Hierarquia de Ações

O GereIgreja adota uma hierarquia clara para evitar dúvidas.

## Ação Primária

Representa a principal ação da tela.

Exemplos:

- Salvar
- Confirmar
- Criar
- Finalizar

Deve existir apenas uma ação primária por contexto principal.

---

## Ação Secundária

Complementa a ação principal.

Exemplos:

- Editar
- Filtrar
- Exportar
- Imprimir

---

## Ação Terciária

Baixa prioridade.

Exemplos:

- Voltar
- Fechar
- Cancelar
- Limpar filtros

---

## Ações Críticas

Envolvem risco ao usuário.

Exemplos:

- Excluir membro
- Excluir congregação
- Cancelar lançamento financeiro
- Restaurar backup
- Remover usuário

Devem utilizar sempre a variante Danger e, quando apropriado, exigir confirmação.

---

# 7. Variantes Oficiais

## Primary

Uso:

Principal ação da tela.

Cor:

Brand 700

Exemplos:

- Salvar
- Criar
- Confirmar

---

## Secondary

Uso:

Ações auxiliares.

Exemplos:

- Editar
- Atualizar
- Exportar

---

## Outline

Uso:

Baixa prioridade visual.

Exemplos:

- Voltar
- Cancelar
- Fechar

---

## Ghost

Uso:

Interfaces compactas.

Muito utilizado em:

- tabelas;
- cards;
- menus;
- dashboards.

---

## Success

Uso:

Confirmações positivas.

Exemplos:

- Aprovar
- Concluir
- Publicar

---

## Warning

Uso:

Ações que exigem atenção.

Exemplos:

- Reabrir período
- Alterar permissões
- Reprocessar dados

---

## Danger

Uso:

Ações destrutivas.

Exemplos:

- Excluir
- Cancelar definitivamente
- Remover registro
- Apagar backup

---

# 8. Tamanhos Oficiais

| Tamanho | Altura |
|----------|--------:|
| XS | 28 px |
| Small | 34 px |
| Medium | 40 px |
| Large | 48 px |

O tamanho **Medium** é o padrão da plataforma.

---

## Utilização Recomendada

### XS

Tabelas e ações compactas.

---

### Small

Filtros e ferramentas.

---

### Medium

Formulários, dashboards e páginas administrativas.

---

### Large

Landing Pages e Portal Público.

---

# 9. Ícones

Os botões poderão conter ícones quando estes facilitarem o reconhecimento da ação.

Estrutura oficial:

```
[Ícone] Space-2 Texto
```

Ícones deverão seguir o documento:

```
GDS-07 — Iconografia
```

---

## Ícones Recomendados

| Ação | Ícone |
|------|--------|
| Salvar | bi-floppy |
| Criar | bi-plus-circle |
| Editar | bi-pencil-square |
| Excluir | bi-trash |
| Visualizar | bi-eye |
| Pesquisar | bi-search |
| Exportar | bi-download |
| Importar | bi-upload |
| Imprimir | bi-printer |
| Compartilhar | bi-share |

---

# 10. Estados

Todo botão deverá possuir estados claramente definidos.

## Normal

Estado padrão.

---

## Hover

Pequena alteração de cor e feedback visual.

---

## Focus

Indicação visível para navegação por teclado.

---

## Active

Representa interação em andamento.

---

## Disabled

Botão indisponível.

Não deverá permitir interação.

---

## Loading

Durante operações assíncronas.

Exemplos:

- salvar cadastro;
- gerar relatório;
- importar membros;
- enviar comunicados.

O botão deverá impedir múltiplos cliques.

---

# 11. Casos Reais do GereIgreja

## Cadastro de Membros

```
[Salvar]

[Cancelar]
```

---

## Financeiro

```
[Novo Lançamento]

[Exportar]

[Filtrar]
```

---

## Escola Bíblica

```
[Nova Turma]

[Adicionar Aluno]
```

---

## Comunicação

```
[Enviar Comunicado]

[Agendar]
```

---

## Eventos

```
[Criar Evento]

[Publicar]
```

---

## Administração

```
[Salvar Configurações]

[Restaurar Backup]

[Excluir]
```

---

# 12. Relação com os Demais Frameworks

Este documento integra-se diretamente com:

- GDS-03 — Cores
- GDS-05 — Espaçamento
- GDS-06 — Grid
- GDS-07 — Iconografia
- GDS-09 — Formulários
- GFE — Frontend Engineering

Toda implementação deverá reutilizar os componentes definidos neste documento.

---

# 13. Botões em Formulários

Os formulários representam o principal fluxo operacional do GereIgreja. Os botões devem orientar claramente o usuário sobre a próxima ação.

---

## Ordem Recomendada

A disposição padrão deverá seguir a seguinte ordem:

```
[Salvar]

[Salvar e Novo]

[Cancelar]
```

Quando houver apenas duas ações:

```
[Salvar]

[Cancelar]
```

---

## Alinhamento

Os botões deverão permanecer alinhados à direita em formulários administrativos.

Exceções:

- assistentes (wizard);
- telas de confirmação;
- landing pages.

---

## Espaçamento

Entre botões:

```
Space-2
```

Entre formulário e grupo de ações:

```
Space-6
```

---

# 14. Botões em Tabelas

As tabelas utilizam botões compactos para ações rápidas.

---

## Ações por Linha

Exemplo:

```
👁  ✏️  🗑
```

Ícones oficiais:

Visualizar

```
bi-eye
```

Editar

```
bi-pencil-square
```

Excluir

```
bi-trash
```

Duplicar

```
bi-files
```

Histórico

```
bi-clock-history
```

---

## Ações em Massa

Exemplos:

- Excluir selecionados
- Exportar selecionados
- Alterar congregação
- Alterar departamento

Essas ações deverão permanecer desabilitadas até que haja registros selecionados.

---

# 15. Botões em Dashboards

Os dashboards utilizam botões para ações rápidas.

Exemplos:

```
Novo Membro

Novo Evento

Novo Lançamento

Enviar Comunicado
```

Priorizar variantes:

- Primary
- Secondary

Evitar excesso de ações no mesmo card.

---

# 16. Botões em Modais

Todo modal deverá possuir ações claramente organizadas.

---

## Confirmação

```
[Confirmar]

[Cancelar]
```

---

## Exclusão

```
[Excluir]

[Cancelar]
```

O botão de exclusão deverá utilizar sempre a variante Danger.

---

## Configuração

```
[Salvar]

[Fechar]
```

---

# 17. Grupos de Botões

Quando múltiplas ações fizerem parte do mesmo contexto, deverão ser agrupadas.

Exemplo:

```
[Salvar]

[Salvar e Continuar]

[Salvar e Novo]
```

Evitar apresentar mais de quatro ações primárias simultaneamente.

Quando necessário, utilizar menus de contexto ("Mais ações").

---

# 18. Botões com HTMX

O GereIgreja utiliza HTMX como padrão para interações assíncronas.

Botões deverão suportar atributos como:

```html
hx-post
hx-get
hx-delete
hx-put
hx-target
hx-swap
hx-confirm
hx-indicator
```

Exemplo:

```html
<button
    class="btn btn-primary"
    hx-post="/membros/salvar/"
    hx-target="#form-container"
    hx-swap="outerHTML">
    Salvar
</button>
```

Sempre que possível, utilizar HTMX para evitar recarregamentos completos da página.

---

# 19. Botões com Alpine.js

O Alpine.js deverá complementar o comportamento dos botões quando necessário.

Exemplos:

- abrir menus;
- exibir modais;
- controlar estados locais;
- alternar filtros;
- expandir painéis.

Exemplo:

```html
<button
    class="btn btn-secondary"
    @click="mostrarFiltros = !mostrarFiltros">
    Filtros
</button>
```

A lógica de negócio não deverá ficar concentrada no Alpine.js.

---

# 20. Ações Críticas

Toda ação destrutiva deverá seguir regras específicas.

Exemplos:

- excluir membro;
- excluir congregação;
- apagar patrimônio;
- excluir usuário;
- restaurar backup.

Requisitos obrigatórios:

- variante Danger;
- confirmação explícita;
- mensagem clara sobre as consequências.

Quando possível, utilizar exclusão lógica (*soft delete*) em vez de exclusão física.

---

# 21. Responsividade

Os botões deverão adaptar-se automaticamente aos diferentes dispositivos.

### Desktop

Texto + ícone.

---

### Tablet

Priorizar largura adequada e evitar quebra de texto.

---

### Smartphone

Permitir largura total (`w-100`) quando necessário.

Em telas muito pequenas, ações secundárias poderão ser agrupadas em um menu de opções.

---

# 22. Acessibilidade

Todos os botões deverão atender às diretrizes de acessibilidade.

---

## Navegação por Teclado

Todo botão deverá ser acessível por:

- Tab;
- Shift + Tab;
- Enter;
- Espaço (quando aplicável).

---

## Foco Visível

O estado de foco deverá ser claramente perceptível.

Nunca remover o outline sem substituí-lo por outro indicador visual equivalente.

---

## Botões Apenas com Ícones

Quando um botão possuir somente um ícone, deverá conter descrição acessível.

Exemplo:

```html
<button
    class="btn btn-outline-primary"
    aria-label="Editar membro">
    <i class="bi bi-pencil-square"></i>
</button>
```

---

## Área de Clique

A área mínima recomendada para interação é de aproximadamente:

```
44 × 44 px
```

Principalmente em smartphones e tablets.

---

# 23. Evidências Arquiteturais

As diretrizes deste documento refletem a implementação oficial do GereIgreja.

---

## EA-GDS-041

Bootstrap fornece a base estrutural dos botões.

---

## EA-GDS-042

O Design System padroniza variantes e estados.

---

## EA-GDS-043

HTMX é utilizado para ações assíncronas.

---

## EA-GDS-044

Alpine.js complementa interações locais.

---

## EA-GDS-045

Todos os módulos reutilizam os mesmos componentes de botão.

---

# 24. Especificações Oficiais

## GDS-BUTTON-001

Toda interface deverá utilizar os componentes oficiais de botão.

---

## GDS-BUTTON-002

Toda ação principal deverá utilizar a variante Primary.

---

## GDS-BUTTON-003

Ações destrutivas deverão utilizar a variante Danger.

---

## GDS-BUTTON-004

Todo botão deverá possuir estados visuais definidos.

---

## GDS-BUTTON-005

Ícones deverão seguir o GDS-07.

---

## GDS-BUTTON-006

Botões deverão respeitar os tamanhos oficiais.

---

## GDS-BUTTON-007

Operações assíncronas deverão exibir estado de carregamento.

---

## GDS-BUTTON-008

Botões compostos apenas por ícones deverão possuir `aria-label`.

---

## GDS-BUTTON-009

Novas variantes deverão ser documentadas antes de sua utilização.

---

## GDS-BUTTON-010

Toda evolução deverá preservar a consistência visual do GereIgreja.

---