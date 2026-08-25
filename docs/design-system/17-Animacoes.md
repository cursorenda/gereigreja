Pasta:
`docs/design-system/`

Arquivo:
`17-Animacoes.md`

Documento:
GDS-17

Código:
GDS-MOTION

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

# GDS-17 — Animações e Movimento

> "No GereIgreja, movimento deve explicar mudanças de estado, orientar a atenção e tornar a interação mais compreensível. Animação sem função é ruído."

---

# Sumário

1. Objetivo
2. Escopo
3. Filosofia de Movimento
4. Princípios
5. Papel das Animações no GereIgreja
6. Movimento Funcional
7. Movimento Decorativo
8. Arquitetura de Movimento
9. Design Tokens de Movimento
10. Duração
11. Easing
12. Delay
13. Distância
14. Opacidade
15. Transformações
16. Estados
17. Hover
18. Focus
19. Active
20. Loading
21. Success
22. Warning
23. Error
24. Disabled
25. Transições de Botões
26. Cards
27. Modais
28. Dropdowns
29. Submenus
30. Sidebar
31. Dashboards Premium
32. `dashboard-sidebar.js`
33. Anti-FOUC
34. Tabelas
35. Formulários
36. Alerts
37. Toasts
38. Tooltips
39. Abas
40. Acordeões
41. Filtros
42. Paginação
43. Gráficos
44. KPIs
45. Skeletons
46. Spinners
47. Barras de Progresso
48. HTMX
49. Indicadores HTMX
50. Swap de Conteúdo
51. Alpine.js
52. Bootstrap
53. Django Templates
54. JavaScript Nativo
55. CSS
56. Responsividade
57. Smartphones
58. Dispositivos Touch
59. Acessibilidade
60. `prefers-reduced-motion`
61. Redução de Movimento
62. Foco e Movimento
63. Flash e Piscadas
64. Autoplay
65. Performance
66. Propriedades Recomendadas
67. Propriedades a Evitar
68. Layout Shift
69. Secretaria
70. Financeiro
71. Eventos
72. Escola Bíblica
73. Comunicação
74. Patrimônio
75. Relatórios
76. Administração
77. Operações Críticas
78. Feedback de Sucesso
79. Feedback de Erro
80. Processamentos Longos
81. Estados Vazios
82. Carregamento Assíncrono
83. Navegação
84. Portal Público
85. Anti-Patterns
86. Regras de Implementação
87. Evidências Arquiteturais
88. Especificações Oficiais
89. Checklist
90. Governança
91. Roadmap
92. Documentos Relacionados
93. Princípios Finais
94. Status do Documento

---

# 1. Objetivo

Este documento estabelece os padrões oficiais de animação, transição e movimento utilizados no GereIgreja.

Seu objetivo é garantir que o movimento da interface seja:

* funcional;
* discreto;
* previsível;
* acessível;
* performático;
* consistente;
* reutilizável;
* compatível com a arquitetura frontend da plataforma.

As animações deverão auxiliar a compreensão da interface.

Não deverão existir apenas para tornar a aplicação visualmente mais chamativa.

---

# 2. Escopo

Este documento aplica-se a:

* Área de Gestão;
* Dashboards Premium;
* Portal Público;
* Landing Pages;
* sidebar;
* navbar;
* menus;
* submenus;
* cards;
* botões;
* formulários;
* modais;
* alerts;
* toasts;
* tabelas;
* filtros;
* gráficos;
* skeletons;
* spinners;
* estados de loading;
* componentes HTMX;
* interações Alpine.js;
* componentes Bootstrap;
* JavaScript compartilhado.

A Administração Técnica baseada no Django Admin deverá preservar sua própria arquitetura e não deverá receber animações específicas sem necessidade funcional.

---

# 3. Filosofia de Movimento

Movimento no GereIgreja deverá comunicar mudança.

A animação deverá responder a alguma pergunta real do usuário:

```text
O elemento apareceu?

O conteúdo foi atualizado?

A ação foi executada?

O menu abriu?

O painel fechou?

Os dados estão sendo carregados?

O estado mudou?
```

Se uma animação não melhora nenhuma dessas respostas, sua utilização deverá ser reconsiderada.

---

# 4. Princípios

Toda animação deverá respeitar:

* propósito;
* simplicidade;
* velocidade;
* continuidade;
* previsibilidade;
* acessibilidade;
* performance;
* consistência.

A regra principal é:

```text
Movimento deve explicar.
Movimento não deve distrair.
```

---

# 5. Papel das Animações no GereIgreja

A interface do GereIgreja é predominantemente operacional.

Usuários realizam tarefas como:

* cadastrar membros;
* localizar registros;
* registrar lançamentos;
* consultar relatórios;
* cadastrar eventos;
* acompanhar turmas;
* enviar comunicações;
* administrar configurações.

Por esse motivo, animações longas ou decorativas deverão ser evitadas.

A produtividade possui prioridade sobre efeitos visuais.

---

# 6. Movimento Funcional

Movimento funcional é aquele que comunica uma alteração real.

Exemplos:

```text
Sidebar fechando
Modal abrindo
Toast aparecendo
Card expandindo
Spinner indicando processamento
Skeleton representando carregamento
Linha de tabela sendo atualizada
```

Esse é o principal tipo de movimento permitido pelo GDS.

---

# 7. Movimento Decorativo

Movimento exclusivamente decorativo deverá ser utilizado com extrema moderação.

Evitar:

* cards flutuando continuamente;
* ícones pulsando sem necessidade;
* textos entrando lateralmente;
* elementos saltando;
* fundos animados;
* números continuamente contando;
* efeitos 3D.

Na Área de Gestão, o padrão deverá ser predominantemente funcional.

---

# 8. Arquitetura de Movimento

A arquitetura conceitual deverá seguir:

```text
Design Token
     ↓
Componente
     ↓
Estado
     ↓
Transição
     ↓
Interface
```

A duração e o easing não deverão ser definidos arbitrariamente em cada página.

---

# 9. Design Tokens de Movimento

O GereIgreja deverá evoluir para centralizar propriedades de movimento em Design Tokens.

Estrutura conceitual:

```text
motion-duration-fast
motion-duration-default
motion-duration-slow

motion-easing-standard
motion-easing-enter
motion-easing-exit
```

Os nomes exatos deverão corresponder à implementação oficial do `design_system.css`.

Não inventar tokens diretamente em componentes isolados.

---

# 10. Duração

A duração deverá ser proporcional à ação.

Escala recomendada:

| Categoria   |                      Duração de referência |
| ----------- | -----------------------------------------: |
| Instantânea |                                   0–100 ms |
| Rápida      |                                 100–150 ms |
| Padrão      |                                 150–250 ms |
| Moderada    |                                 250–350 ms |
| Longa       | acima de 350 ms somente quando justificada |

A maioria das transições do GereIgreja deverá ocorrer entre:

```text
150 ms
e
250 ms
```

---

# 11. Easing

O easing deverá produzir movimento natural.

Padrões conceituais:

```text
Standard
→ transições comuns

Enter
→ elementos entrando

Exit
→ elementos saindo
```

Evitar easings elásticos ou com bounce em interfaces administrativas.

---

# 12. Delay

Delays deverão ser evitados na maioria das interações.

O usuário não deverá esperar artificialmente para receber feedback.

Delay poderá ser utilizado quando necessário para:

* evitar tooltip acidental;
* impedir flicker;
* coordenar pequenas sequências.

---

# 13. Distância

Movimentos espaciais deverão utilizar pequenas distâncias.

Exemplo apropriado:

```text
4 px
8 px
12 px
```

Evitar elementos percorrendo grandes áreas da tela.

---

# 14. Opacidade

Transições de opacidade são recomendadas por serem discretas e performáticas.

Exemplos:

```text
opacity: 0
      ↓
opacity: 1
```

Podem ser utilizadas em:

* toast;
* tooltip;
* dropdown;
* pequenas mensagens;
* overlays.

---

# 15. Transformações

Transformações deverão ser utilizadas com moderação.

Exemplos apropriados:

```text
translateY
translateX
scale
```

Para interações leves.

Evitar escalas exageradas.

---

# 16. Estados

Componentes poderão utilizar movimento para representar transições entre:

```text
Default
Hover
Focus
Active
Loading
Success
Warning
Error
Disabled
```

Nem todo estado necessita animação.

---

# 17. Hover

Hover poderá utilizar transição breve.

Exemplo conceitual:

```text
Default
   ↓
150 ms
   ↓
Hover
```

Aplicável a:

* botões;
* links;
* cards clicáveis;
* menus.

Não mover significativamente elementos durante hover.

---

# 18. Focus

O estado de foco deverá aparecer imediatamente.

Não atrasar o indicador de foco.

A acessibilidade possui prioridade sobre suavidade visual.

---

# 19. Active

Ao pressionar um botão, pequena alteração visual poderá comunicar a interação.

Evitar efeitos exagerados de escala.

---

# 20. Loading

Loading deverá representar processamento real.

Exemplos:

```text
Salvando...

Carregando membros...

Gerando relatório...

Processando lançamento...
```

A animação deverá interromper quando o processo terminar.

---

# 21. Success

O sucesso poderá utilizar transição curta.

Exemplo:

```text
Loading
   ↓
Success
```

Não utilizar celebrações ou animações exageradas em operações administrativas comuns.

---

# 22. Warning

Warning não necessita obrigatoriamente movimento.

A informação deverá ser compreendida principalmente por:

* texto;
* ícone;
* cor semântica.

---

# 23. Error

Erros não deverão utilizar animações agressivas.

Evitar:

* shake forte;
* piscadas;
* movimentos repetitivos.

O foco deverá permanecer na compreensão e correção do problema.

---

# 24. Disabled

Estados disabled normalmente não deverão utilizar animação.

---

# 25. Transições de Botões

Botões poderão possuir transição para:

* background;
* border;
* color;
* transform discreto;
* loading.

Exemplo conceitual:

```text
Salvar
   ↓
Salvando...
   ↓
Salvo
```

O estado deverá acompanhar a operação real.

---

# 26. Cards

Cards clicáveis poderão utilizar:

* pequena mudança de borda;
* sombra discreta;
* leve transformação.

Evitar:

```text
card sobe 20 px
card aumenta 15%
```

O GDS-10 continua sendo a referência principal.

---

# 27. Modais

A abertura de modal poderá utilizar:

```text
Overlay
   ↓
Fade

Modal
   ↓
Fade + pequeno scale
```

A duração deverá permanecer curta.

O fechamento deverá ser igualmente previsível.

As regras funcionais seguem o GDS-12.

---

# 28. Dropdowns

Dropdowns poderão utilizar:

```text
opacity
+
pequeno translateY
```

Evitar menus deslizando por grandes distâncias.

---

# 29. Submenus

Submenus deverão comunicar expansão e recolhimento.

Uma pequena rotação do indicador poderá ser utilizada.

Exemplo:

```text
>
↓
v
```

A navegação deverá funcionar mesmo sem animação.

---

# 30. Sidebar

A sidebar representa um dos movimentos estruturais mais importantes da Área de Gestão.

Sua abertura e fechamento deverão:

* ser rápidas;
* preservar contexto;
* evitar flicker;
* evitar layout shift excessivo;
* permanecer consistentes entre dashboards.

---

# 31. Dashboards Premium

Os Dashboards Premium possuem infraestrutura compartilhada para sidebar.

O movimento deverá permanecer compatível com:

`dashboard_base.html`

e:

`static/js/dashboard-sidebar.js`

Dashboards individuais não deverão criar animações próprias de sidebar.

---

# 32. `dashboard-sidebar.js`

Esse script constitui a infraestrutura atual responsável pelo comportamento da sidebar dos Dashboards Premium.

Entre suas responsabilidades já documentadas estão:

* abrir;
* fechar;
* persistir estado;
* atualizar layout;
* coordenar interface.

Qualquer evolução visual deverá preservar essa centralização.

---

# 33. Anti-FOUC

O GereIgreja possui estratégia para evitar que o estado visual da sidebar seja aplicado somente após a primeira pintura da página.

Objetivo:

```text
Estado salvo
   ↓
Aplicação antecipada
   ↓
Render correto
```

e não:

```text
Sidebar aparece
   ↓
JavaScript carrega
   ↓
Sidebar desaparece
```

Esse comportamento deverá ser preservado.

---

# 34. Tabelas

Tabelas não deverão possuir animação linha por linha durante carregamento inicial.

Atualizações individuais poderão utilizar destaque discreto temporário quando isso ajudar o usuário a identificar o registro alterado.

Exemplo:

```text
Linha atualizada
   ↓
destaque discreto
   ↓
estado normal
```

---

# 35. Formulários

Formulários deverão evitar movimento durante validação.

Erros poderão aparecer suavemente, mas não deverão provocar grandes deslocamentos inesperados.

---

# 36. Alerts

Alerts poderão utilizar fade curto quando adicionados dinamicamente.

Alerts persistentes carregados com a página não necessitam animação.

---

# 37. Toasts

Toasts poderão possuir entrada e saída suaves.

Exemplo:

```text
Fade + pequeno translateY
```

A animação deverá ser breve.

As regras completas seguem o GDS-13.

---

# 38. Tooltips

Tooltips deverão aparecer rapidamente.

Podem possuir pequeno delay para evitar abertura acidental.

A informação essencial nunca deverá existir apenas em tooltip.

---

# 39. Abas

Mudanças entre abas deverão ser rápidas.

Não utilizar animações de página inteira.

Quando HTMX atualizar o conteúdo, poderá existir transição discreta no conteúdo carregado.

---

# 40. Acordeões

A expansão deverá comunicar claramente a abertura.

O movimento deverá acompanhar o tamanho do conteúdo sem ser excessivamente lento.

---

# 41. Filtros

Painéis de filtro expansíveis poderão utilizar transição discreta.

Em dashboards, Alpine.js poderá futuramente controlar esse estado local quando apropriado.

---

# 42. Paginação

Mudanças de página normalmente não necessitam animação.

Quando HTMX for utilizado:

```text
Loading
   ↓
Swap
   ↓
Conteúdo atualizado
```

poderá haver transição curta.

---

# 43. Gráficos

Gráficos deverão evitar animações longas durante cada atualização.

A animação inicial deverá ser discreta.

Não utilizar gráficos continuamente animados em dashboards administrativos.

---

# 44. KPIs

KPIs não deverão utilizar contadores animados como padrão.

Exemplo inadequado:

```text
0
↓
100
↓
500
↓
1.248
```

A apresentação imediata do valor normalmente oferece melhor produtividade.

---

# 45. Skeletons

Skeletons poderão ser utilizados durante carregamento perceptível.

Devem representar aproximadamente:

* largura;
* altura;
* distribuição

do conteúdo final.

Evitar skeletons excessivamente animados.

---

# 46. Spinners

Spinners são apropriados para processos cuja duração seja desconhecida.

Exemplos:

```text
Salvando...
[spinner]
```

Evitar spinner sem texto em operações importantes.

---

# 47. Barras de Progresso

Utilizar quando houver progresso real mensurável.

Exemplos futuros ou específicos:

* importação;
* upload;
* processamento extenso.

Não utilizar barra fictícia quando o progresso não puder ser calculado.

---

# 48. HTMX

HTMX deverá permitir feedback de processamento sem transformar a interface em SPA.

Fluxo:

```text
Ação
   ↓
hx-request
   ↓
Loading
   ↓
Response
   ↓
Swap
   ↓
Novo estado
```

---

# 49. Indicadores HTMX

Atributos como:

`hx-indicator`

poderão ser utilizados para controlar indicadores de processamento.

Exemplo conceitual:

```html
<button
    hx-post="..."
    hx-indicator="#loading">
    Salvar
</button>
```

A implementação deverá permanecer compatível com a arquitetura real do projeto.

---

# 50. Swap de Conteúdo

Atualizações HTMX não deverão causar mudanças bruscas desnecessárias.

Sempre que possível, preservar:

* altura aproximada;
* foco;
* scroll;
* contexto.

---

# 51. Alpine.js

Alpine.js poderá controlar movimentos simples de estados locais.

Exemplo conceitual:

```text
x-show
x-transition
```

Aplicações apropriadas:

* dropdown;
* filtro;
* painel;
* submenu;
* pequenas regiões.

A adoção prática no GereIgreja permanece gradual.

---

# 52. Bootstrap

Bootstrap possui transições próprias em componentes como:

* modal;
* collapse;
* dropdown.

Esses comportamentos poderão ser reutilizados quando compatíveis com o GDS.

Evitar sobrescrever indiscriminadamente transições internas do framework.

---

# 53. Django Templates

Django Templates permanecem como base de renderização.

O conteúdo deverá estar disponível no servidor.

Animação deverá complementar a experiência, e não definir a existência funcional da interface.

---

# 54. JavaScript Nativo

JavaScript nativo continuará sendo utilizado para infraestrutura compartilhada mais complexa.

Exemplo consolidado:

`dashboard-sidebar.js`

Evitar scripts independentes para animações pequenas quando CSS for suficiente.

---

# 55. CSS

Movimento simples deverá preferir CSS.

Exemplo conceitual:

```css
transition:
    opacity 180ms ease,
    transform 180ms ease;
```

Valores finais deverão utilizar tokens oficiais quando implementados.

---

# 56. Responsividade

A quantidade e intensidade de movimento poderá diminuir em dispositivos menores.

A responsividade deverá considerar:

* performance;
* espaço;
* toque;
* contexto visual.

---

# 57. Smartphones

Em smartphones:

* evitar movimentos laterais extensos;
* evitar zoom de componentes;
* priorizar fade;
* priorizar transições simples;
* manter resposta rápida.

---

# 58. Dispositivos Touch

Hover não deverá ser requisito funcional.

Toda informação disponível apenas em hover deverá possuir alternativa para touch.

---

# 59. Acessibilidade

Movimento deverá respeitar o GDS-16.

Animações não poderão:

* impedir leitura;
* alterar foco inesperadamente;
* esconder conteúdo essencial;
* provocar flashes;
* exigir percepção visual para compreensão.

---

# 60. `prefers-reduced-motion`

O GereIgreja deverá respeitar a preferência do sistema operacional quando aplicável.

Estrutura recomendada:

```css
@media (prefers-reduced-motion: reduce) {
    /*
     * Reduzir ou remover animações não essenciais.
     */
}
```

---

# 61. Redução de Movimento

Quando `reduced-motion` estiver ativo:

* eliminar transições decorativas;
* reduzir deslocamentos;
* remover parallax;
* desabilitar animações contínuas;
* preservar mudanças instantâneas de estado.

Funcionalidade não deverá ser removida.

---

# 62. Foco e Movimento

Animações nunca deverão atrasar o foco.

Ao abrir modal, menu ou componente acessível, a gestão do foco deverá possuir prioridade.

---

# 63. Flash e Piscadas

Evitar elementos piscando repetidamente.

O GereIgreja não deverá utilizar flash visual como mecanismo de atenção.

---

# 64. Autoplay

Animações contínuas iniciadas automaticamente deverão ser evitadas.

Caso algum conteúdo futuro necessite autoplay, deverão existir mecanismos adequados de controle.

---

# 65. Performance

Animações deverão utilizar propriedades que reduzam custo de renderização.

Preferir:

* `opacity`;
* `transform`.

Utilizar outras propriedades somente quando necessárias.

---

# 66. Propriedades Recomendadas

Priorizar:

```text
opacity
transform
```

quando visualmente adequadas.

Essas propriedades normalmente possuem melhor desempenho para movimento.

---

# 67. Propriedades a Evitar

Evitar animação constante de propriedades como:

```text
width
height
top
left
margin
padding
```

quando uma transformação puder produzir resultado equivalente.

Algumas alterações estruturais inevitavelmente utilizarão layout; nesses casos, avaliar performance.

---

# 68. Layout Shift

Movimento não deverá produzir deslocamento inesperado dos componentes.

Especial atenção em:

* dashboards;
* cards;
* tabelas;
* mensagens;
* skeletons;
* sidebar.

---

# 69. Secretaria

A Secretaria deverá priorizar movimento mínimo.

Aplicações adequadas:

* loading de busca;
* atualização de listagem;
* modal;
* confirmação;
* feedback de cadastro.

Cadastro de membros não deverá possuir animações decorativas.

---

# 70. Financeiro

O Financeiro deverá utilizar movimento apenas para:

* processamento;
* filtros;
* atualização de dados;
* modais;
* feedback;
* gráficos.

Operações financeiras críticas não deverão utilizar animação que transmita informalidade.

---

# 71. Eventos

O módulo de Eventos poderá utilizar transições discretas em:

* cards;
* filtros;
* modais;
* agenda;
* atualização de status.

---

# 72. Escola Bíblica

Movimento poderá auxiliar:

* filtros;
* turmas;
* presença;
* modais;
* atualização de listagens.

---

# 73. Comunicação

Estados de processamento são especialmente importantes para:

* envio;
* agendamento;
* carregamento;
* atualização de status.

Exemplo:

```text
Enviando...
```

Não comunicar sucesso antes da confirmação do backend.

---

# 74. Patrimônio

As animações deverão seguir os mesmos padrões operacionais da Área de Gestão.

---

# 75. Relatórios

Relatórios normalmente não necessitam animação.

Loading poderá ser utilizado durante geração ou filtragem.

Versões destinadas à impressão não deverão depender de movimento.

---

# 76. Administração

Telas de configuração e administração deverão utilizar movimento discreto.

Alterações de permissões e configurações críticas deverão priorizar clareza.

---

# 77. Operações Críticas

Exclusões, estornos e outras operações críticas não deverão utilizar animações celebratórias.

O fluxo correto é:

```text
Confirmação
    ↓
Loading
    ↓
Resultado
    ↓
Feedback
```

---

# 78. Feedback de Sucesso

O sucesso poderá utilizar:

* ícone;
* mudança de estado;
* pequena transição.

Evitar:

* confete;
* fogos;
* bounce;
* efeitos exagerados.

---

# 79. Feedback de Erro

Erros deverão ser estáveis visualmente.

Evitar campos balançando repetidamente.

O usuário precisa ler e corrigir o problema.

---

# 80. Processamentos Longos

Processamentos longos deverão utilizar feedback persistente.

Exemplos:

```text
Importando membros...

Gerando relatório...

Processando comunicação...
```

Quando houver progresso mensurável, considerar barra de progresso.

---

# 81. Estados Vazios

Estados vazios não necessitam animação.

A mensagem e a ação contextual são mais importantes.

---

# 82. Carregamento Assíncrono

Widgets independentes poderão possuir skeleton ou spinner local.

Evitar bloquear toda a página quando somente um componente está carregando.

---

# 83. Navegação

A navegação principal entre módulos não deverá utilizar transições de tela como SPA por padrão.

O GereIgreja permanece baseado em renderização pelo servidor e Progressive Enhancement.

---

# 84. Portal Público

O Portal Público poderá possuir movimento visual ligeiramente mais editorial do que a Área de Gestão.

Ainda assim deverá respeitar:

* identidade;
* acessibilidade;
* performance;
* redução de movimento.

Landing Pages não deverão utilizar animações que atrasem acesso ao conteúdo.

---

# 85. Anti-Patterns

São proibidos ou fortemente desencorajados:

* animações sem finalidade;
* bounce em componentes administrativos;
* cards flutuantes;
* confete em operações comuns;
* animação contínua de KPIs;
* números contando ao carregar;
* elementos piscando;
* movimentos extensos;
* transições acima de 500 ms sem justificativa;
* delays artificiais;
* loading falso;
* barra de progresso falsa;
* animações bloqueando interação;
* animações alterando foco;
* movimento como único indicador de estado;
* scripts duplicados por módulo;
* animações JavaScript que poderiam ser CSS simples;
* múltiplas bibliotecas de animação;
* animações que quebram `prefers-reduced-motion`;
* animações que causam layout shift;
* animações em relatórios impressos;
* HTMX utilizado para criar transições de SPA sem necessidade;
* lógica de negócio associada à animação.

---

# 86. Regras de Implementação

Antes de criar uma nova animação:

```text
Existe necessidade funcional?
        ↓
SIM
        ↓
Existe padrão já definido?
        ↓
SIM → reutilizar

NÃO
        ↓
Pode ser resolvido com CSS?
        ↓
SIM → CSS

NÃO
        ↓
Existe infraestrutura compartilhada?
        ↓
SIM → reutilizar

NÃO
        ↓
Avaliar JavaScript
```

A prioridade deverá ser sempre a solução mais simples.

---

# 87. Evidências Arquiteturais

## EA-GDS-MOTION-001

Django Templates permanecem como base de renderização da Área de Gestão.

## EA-GDS-MOTION-002

Bootstrap participa da infraestrutura visual e de componentes.

## EA-GDS-MOTION-003

Font Awesome está consolidado na interface atual.

## EA-GDS-MOTION-004

Dashboards Premium utilizam `dashboard_base.html`.

## EA-GDS-MOTION-005

Dashboards Premium utilizam `static/js/dashboard-sidebar.js`.

## EA-GDS-MOTION-006

O estado da sidebar utiliza persistência local.

## EA-GDS-MOTION-007

A infraestrutura do dashboard possui tratamento anti-FOUC para o estado da sidebar.

## EA-GDS-MOTION-008

HTMX constitui diretriz para atualizações parciais com adoção gradual.

## EA-GDS-MOTION-009

Alpine.js constitui diretriz para estados locais leves com adoção gradual.

## EA-GDS-MOTION-010

O GDS utiliza `static/css/design_system.css` como infraestrutura central de estilização.

## EA-GDS-MOTION-011

O GereIgreja segue estratégia de Progressive Enhancement.

## EA-GDS-MOTION-012

A Administração Técnica baseada no Django Admin possui arquitetura distinta da Área de Gestão.

---

# 88. Especificações Oficiais

## GDS-MOTION-001

Toda animação deverá possuir finalidade funcional ou comunicacional.

## GDS-MOTION-002

Animações decorativas deverão ser minimizadas na Área de Gestão.

## GDS-MOTION-003

A maioria das transições deverá possuir duração entre 150 ms e 250 ms.

## GDS-MOTION-004

Transições longas deverão possuir justificativa funcional.

## GDS-MOTION-005

A interface deverá responder imediatamente ao foco.

## GDS-MOTION-006

Hover não deverá ser necessário para acessar funcionalidade.

## GDS-MOTION-007

Loading deverá representar processamento real.

## GDS-MOTION-008

Sucesso somente deverá ser apresentado após confirmação real da operação.

## GDS-MOTION-009

Animações de erro não deverão prejudicar a leitura.

## GDS-MOTION-010

Modais deverão utilizar movimento discreto.

## GDS-MOTION-011

Sidebars deverão reutilizar infraestrutura compartilhada.

## GDS-MOTION-012

Dashboards não deverão criar scripts próprios de sidebar.

## GDS-MOTION-013

O anti-FOUC da sidebar deverá ser preservado.

## GDS-MOTION-014

Skeletons deverão representar aproximadamente o conteúdo final.

## GDS-MOTION-015

Spinners deverão possuir contexto textual quando necessário.

## GDS-MOTION-016

Barras de progresso deverão representar progresso real.

## GDS-MOTION-017

HTMX deverá fornecer feedback de processamento quando apropriado.

## GDS-MOTION-018

Alpine.js deverá limitar-se a estados locais e interações leves.

## GDS-MOTION-019

CSS deverá ser preferido para animações simples.

## GDS-MOTION-020

JavaScript deverá ser utilizado apenas quando CSS não atender adequadamente ao comportamento.

## GDS-MOTION-021

`opacity` e `transform` deverão ser preferidos quando tecnicamente adequados.

## GDS-MOTION-022

A interface deverá evitar layout shift causado por animações.

## GDS-MOTION-023

A preferência `prefers-reduced-motion` deverá ser considerada.

## GDS-MOTION-024

A redução de movimento não deverá remover funcionalidade.

## GDS-MOTION-025

Ações críticas não deverão utilizar animações celebratórias.

## GDS-MOTION-026

KPIs não deverão utilizar contadores animados como padrão.

## GDS-MOTION-027

Gráficos não deverão permanecer em animação contínua.

## GDS-MOTION-028

A navegação entre módulos não deverá simular SPA apenas por efeito visual.

## GDS-MOTION-029

Nenhuma biblioteca adicional de animação deverá ser introduzida sem decisão arquitetural.

## GDS-MOTION-030

Novos padrões de movimento deverão ser documentados antes da adoção ampla.

---

# 89. Checklist

## Propósito

* [ ] a animação possui finalidade;
* [ ] comunica mudança de estado;
* [ ] facilita compreensão;
* [ ] não é apenas decorativa.

## Duração

* [ ] rápida;
* [ ] proporcional;
* [ ] não atrasa operação;
* [ ] não possui delay desnecessário.

## Movimento

* [ ] distância pequena;
* [ ] sem bounce;
* [ ] sem movimento contínuo;
* [ ] sem piscadas;
* [ ] sem deslocamento excessivo.

## Estados

* [ ] hover;
* [ ] focus;
* [ ] active;
* [ ] loading;
* [ ] success;
* [ ] error;
* [ ] disabled.

## Loading

* [ ] processamento real;
* [ ] feedback compreensível;
* [ ] spinner contextualizado;
* [ ] skeleton apropriado;
* [ ] resultado final apresentado.

## Sidebar

* [ ] reutiliza `dashboard-sidebar.js`;
* [ ] preserva Local Storage;
* [ ] preserva anti-FOUC;
* [ ] não possui lógica duplicada;
* [ ] responsiva.

## HTMX

* [ ] request possui feedback quando necessário;
* [ ] swap não causa salto excessivo;
* [ ] foco preservado;
* [ ] contexto preservado;
* [ ] loading encerrado corretamente.

## Alpine.js

* [ ] utilizado apenas para estado local;
* [ ] sem regra de negócio;
* [ ] transição acessível;
* [ ] comportamento funciona sem depender de animação.

## CSS

* [ ] utiliza tokens;
* [ ] utiliza `design_system.css`;
* [ ] prefere `opacity`;
* [ ] prefere `transform`;
* [ ] evita propriedades de alto custo quando possível.

## Acessibilidade

* [ ] `prefers-reduced-motion`;
* [ ] foco imediato;
* [ ] sem flash;
* [ ] sem autoplay desnecessário;
* [ ] funcionalidade preservada sem movimento.

## Responsividade

* [ ] desktop;
* [ ] notebook;
* [ ] tablet;
* [ ] smartphone;
* [ ] touch.

## Performance

* [ ] sem biblioteca redundante;
* [ ] sem listeners duplicados;
* [ ] sem animações constantes;
* [ ] sem layout shift relevante;
* [ ] sem trabalho JavaScript desnecessário.

---

# 90. Governança

O movimento faz parte da identidade do GereIgreja Design System.

Novas animações deverão ser tratadas como componentes de comportamento reutilizáveis.

Nenhum módulo deverá criar uma linguagem de movimento independente.

Alterações globais deverão avaliar impacto em:

* Secretaria;
* Financeiro;
* Eventos;
* Escola Bíblica;
* Comunicação;
* Patrimônio;
* Relatórios;
* Administração;
* Portal Público.

---

# 91. Roadmap

## Fase 1 — Inventário

* identificar animações existentes;
* mapear transições;
* remover duplicações;
* identificar movimentos inconsistentes.

## Fase 2 — Tokens

Definir oficialmente:

* durações;
* easings;
* transições;
* estados.

Centralizar no Design System.

## Fase 3 — Acessibilidade

Implementar e validar:

```text
prefers-reduced-motion
```

nos componentes animados.

## Fase 4 — HTMX

Padronizar:

* loading;
* indicadores;
* swaps;
* transições discretas;
* feedback pós-operação.

## Fase 5 — Alpine.js

Adotar progressivamente:

* `x-show`;
* estados locais;
* transições leves;

quando isso reduzir JavaScript customizado.

## Fase 6 — Dashboards

Consolidar:

* sidebar;
* widgets;
* loading;
* skeletons;
* gráficos;
* estados.

## Fase 7 — Qualidade

Incorporar verificações de:

* performance;
* movimento reduzido;
* layout shift;
* acessibilidade;
* consistência.

---

# 92. Documentos Relacionados

* GDS-01 — Introdução
* GDS-02 — Princípios
* GDS-03 — Cores
* GDS-04 — Tipografia
* GDS-05 — Espaçamento
* GDS-06 — Grid
* GDS-07 — Iconografia
* GDS-08 — Botões
* GDS-09 — Formulários
* GDS-10 — Cards
* GDS-11 — Tabelas e Listagens
* GDS-12 — Modais, Dialogs e Confirmações
* GDS-13 — Alertas, Toasts e Feedback
* GDS-14 — Navegação
* GDS-15 — Dashboards
* GDS-16 — Acessibilidade
* GDS-18 — Boas Práticas
* GDS-19 — Governança
* GFE-01 — Frontend Architecture
* GFE-03 — Componentes
* GFE-04 — Layouts
* GFE-05 — Templates
* GFE-07 — CSS
* GFE-08 — JavaScript
* GFE-09 — HTMX
* GFE-10 — Alpine.js
* GFE-11 — Dashboards

---

# 93. Princípios Finais

O GereIgreja é uma plataforma de trabalho.

Por isso, movimento deverá aumentar produtividade e compreensão, nunca competir com elas.

A arquitetura ideal é:

```text
Usuário executa ação
        ↓
Interface responde imediatamente
        ↓
Movimento explica a mudança
        ↓
Novo estado fica claro
        ↓
Usuário continua trabalhando
```

O movimento deverá permanecer:

```text
Curto
+
Discreto
+
Funcional
+
Acessível
+
Performático
```

A plataforma não deverá adotar uma estética de animações constantes.

Secretaria, Financeiro, Eventos, Escola Bíblica, Comunicação, Patrimônio e Administração deverão compartilhar a mesma linguagem de movimento.

Django Templates continuarão garantindo a base funcional da interface.

Bootstrap fornecerá parte da infraestrutura visual.

HTMX permitirá evolução das atualizações parciais.

Alpine.js poderá complementar estados locais.

JavaScript compartilhado continuará responsável por comportamentos estruturais mais complexos, como a sidebar dos Dashboards Premium.

Toda essa evolução deverá respeitar:

```text
Progressive Enhancement
+
Acessibilidade
+
Performance
+
Design System
```

O objetivo final é que o usuário perceba uma interface fluida sem perceber a animação como protagonista.

Quando o movimento está correto, ele explica a interface e desaparece da atenção consciente do usuário.

---

# 94. Status do Documento

**Pasta**

`docs/design-system/`

**Arquivo**

`17-Animacoes.md`

**Documento**

`GDS-17`

**Código**

`GDS-MOTION`

**Framework**

`GereIgreja Design System (GDS)`

**Versão**

`1.0`

**Status**

`OFICIAL`

**Responsável**

`Equipe de Engenharia`

**Última atualização**

`Agosto de 2026`

---

# Fim do Documento

**GDS-17 — Animações e Movimento**
**GereIgreja Design System**
