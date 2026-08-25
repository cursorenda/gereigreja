Pasta:
`docs/frameworks/`

Arquivo:
`13-GDS-Alertas-Toasts-e-Feedback.md`

Documento:
GDS-13

Código:
GDS-FEEDBACK

Framework:
GDS — GereIgreja Design System

Versão:
1.0

Status:
Oficial

Responsável:
Equipe de Engenharia

Última atualização:
Agosto de 2026

# 13 — Alertas, Toasts e Feedback

> "Toda ação realizada no GereIgreja deve produzir uma resposta compreensível. O usuário nunca deverá precisar adivinhar se uma operação funcionou, falhou, está em processamento ou exige sua atenção."

---

# Sumário

1. Objetivo
2. Escopo
3. Papel do Feedback no GereIgreja
4. Princípios
5. Arquitetura de Feedback
6. Taxonomia Oficial
7. Feedback Inline
8. Alertas
9. Toasts
10. Mensagens Globais
11. Feedback de Formulários
12. Feedback de Operações
13. Estados Semânticos
14. Success
15. Warning
16. Danger
17. Informativo e Estado Neutro
18. Anatomia dos Alertas
19. Anatomia dos Toasts
20. Títulos
21. Mensagens
22. Ícones
23. Ações
24. Fechamento
25. Persistência
26. Duração
27. Posicionamento
28. Empilhamento
29. Responsividade
30. Acessibilidade
31. Leitores de Tela
32. Regiões Live
33. Foco
34. Uso de Cor
35. Feedback de Loading
36. Feedback de Sucesso
37. Feedback de Erro
38. Erros de Validação
39. Erros de Negócio
40. Erros de Permissão
41. Erros de Autenticação e Sessão
42. Erros de Rede
43. Erros do Servidor
44. Mensagens Técnicas
45. Feedback e Django Messages
46. Feedback e HTMX
47. Eventos HTMX
48. Feedback e Alpine.js
49. Feedback e Bootstrap
50. Feedback e Django Forms
51. Secretaria
52. Financeiro
53. Eventos
54. Escola Bíblica
55. Comunicação
56. Administração
57. Portal Público
58. Operações Financeiras
59. Exclusões
60. Estornos
61. Alterações de Status
62. Operações em Massa
63. Importações
64. Exportações
65. Processamentos Longos
66. Estados Vazios
67. Nenhum Resultado
68. Feedback em Tabelas
69. Feedback em Cards
70. Feedback em Modais
71. Feedback em Formulários
72. Feedback em Páginas
73. Feedback e Navegação
74. Preservação de Contexto
75. Permissões
76. Multi-Tenant
77. Segurança
78. Privacidade
79. Auditoria
80. Conteúdo das Mensagens
81. Linguagem
82. Mensagens Acionáveis
83. Mensagens Destrutivas
84. Mensagens Financeiras
85. Datas e Valores
86. Evitar Duplicidade
87. Prevenção de Spam Visual
88. Prioridade
89. Concorrência
90. Idempotência
91. Performance
92. Anti-Patterns
93. Implementação
94. Componentização
95. Tokens
96. CSS
97. Testes
98. Testes Funcionais
99. Testes Visuais
100. Testes de Acessibilidade
101. Testes de Responsividade
102. Testes de Segurança
103. Especificações Oficiais
104. Checklist
105. Governança
106. Evolução
107. Documentos Relacionados
108. Princípios Finais
109. Status do Documento

---

# 1. Objetivo

O GDS-13 estabelece o padrão oficial de feedback visual e textual do GereIgreja.

Seu objetivo é garantir que o usuário compreenda claramente o resultado das interações realizadas na plataforma.

Toda operação relevante deverá comunicar pelo menos um dos seguintes estados quando aplicável:

```text
Em processamento
Sucesso
Atenção
Erro
Informação
```

O feedback deverá responder, conforme o contexto:

```text
O que aconteceu?
A operação foi concluída?
Existe algo que o usuário precisa fazer?
É possível continuar?
Como corrigir o problema?
```

---

# 2. Escopo

Este documento aplica-se a:

* alertas;
* toasts;
* mensagens globais;
* mensagens inline;
* feedback de formulários;
* mensagens de validação;
* feedback de operações;
* carregamentos;
* erros;
* avisos;
* confirmações pós-operação;
* estados vazios;
* respostas HTMX;
* Django Messages;
* feedback administrativo;
* feedback do Portal Público.

Aplica-se aos módulos do GereIgreja, incluindo:

* Secretaria;
* Financeiro;
* Eventos;
* Escola Bíblica;
* Comunicação;
* Administração;
* demais módulos integrados à plataforma.

---

# 3. Papel do Feedback no GereIgreja

O GereIgreja é uma plataforma operacional.

O usuário realiza continuamente ações como:

```text
Cadastrar
Editar
Salvar
Excluir
Inativar
Reativar
Confirmar
Cancelar
Filtrar
Pesquisar
Enviar
Registrar
Estornar
Importar
Exportar
```

A interface deverá responder adequadamente a essas ações.

Exemplo:

```text
Usuário
   │
   ▼
Salva membro
   │
   ▼
Servidor processa
   │
   ├── Sucesso
   │      ↓
   │  "Membro cadastrado com sucesso."
   │
   └── Erro
          ↓
      Mensagem contextual
```

O silêncio da interface após uma operação relevante deverá ser evitado.

---

# 4. Princípios

O sistema de feedback deverá seguir:

* clareza;
* contexto;
* objetividade;
* consistência;
* proporcionalidade;
* acessibilidade;
* segurança;
* previsibilidade;
* baixa interrupção.

O nível de interrupção deverá ser proporcional à importância da informação.

---

# 5. Arquitetura de Feedback

A escolha do componente deverá considerar a relação da mensagem com o contexto.

```text
Mensagem ligada a um campo
        ↓
Feedback inline

Mensagem ligada a uma seção
        ↓
Alerta contextual

Resultado breve de uma operação
        ↓
Toast / mensagem global

Decisão obrigatória
        ↓
Dialog / confirmação

Erro estrutural da página
        ↓
Alerta persistente
```

O GereIgreja não deverá utilizar toast como solução universal para todas as mensagens.

---

# 6. Taxonomia Oficial

Os mecanismos oficiais são:

```text
Feedback
│
├── Inline
├── Alert
├── Toast
├── Global Message
├── Loading State
├── Empty State
└── Dialog
```

Dialogs e confirmações seguem o GDS-12.

---

# 7. Feedback Inline

Feedback inline deverá permanecer próximo ao elemento relacionado.

Exemplo:

```text
CPF

[123________________]

CPF inválido.
```

É indicado principalmente para:

* validação;
* orientação;
* campo obrigatório;
* inconsistência;
* informação contextual.

As regras completas de campos permanecem no GDS-09.

---

# 8. Alertas

Alertas deverão ser utilizados quando a informação precisar permanecer visível dentro do contexto atual.

Exemplo:

```text
┌──────────────────────────────────────────┐
│ Atenção                                  │
│                                          │
│ Existem lançamentos pendentes neste      │
│ período financeiro.                      │
└──────────────────────────────────────────┘
```

Alertas poderão aparecer:

* no topo do conteúdo;
* dentro de uma seção;
* acima de formulário;
* próximos ao componente afetado.

---

# 9. Toasts

Toast é uma mensagem temporária utilizada principalmente para comunicar o resultado de uma operação.

Exemplo:

```text
┌────────────────────────────────────┐
│ ✓ Membro atualizado com sucesso.  │
└────────────────────────────────────┘
```

É apropriado quando:

* a ação já terminou;
* não existe decisão obrigatória;
* o usuário pode continuar trabalhando;
* a mensagem é curta.

---

# 10. Mensagens Globais

Mensagens globais poderão comunicar situações que afetam toda a página ou sessão.

Exemplos:

* indisponibilidade temporária;
* alteração relevante no contexto;
* aviso de sessão;
* falha estrutural.

Não utilizar mensagens globais para erros restritos a um único campo.

---

# 11. Feedback de Formulários

Formulários deverão apresentar erros próximos aos respectivos campos.

Quando houver múltiplos erros, poderá existir também um resumo no início do formulário quando isso melhorar a acessibilidade e a compreensão.

Exemplo:

```text
Não foi possível salvar o membro.

Revise os campos destacados abaixo.
```

---

# 12. Feedback de Operações

Operações concluídas deverão gerar feedback proporcional.

Exemplos:

```text
Membro cadastrado com sucesso.

Evento atualizado com sucesso.

Congregação inativada.

Lançamento registrado com sucesso.
```

Evitar:

```text
Sucesso!

OK!

Operação realizada!
```

quando for possível informar exatamente o que ocorreu.

---

# 13. Estados Semânticos

O GDS define três cores semânticas oficiais no GDS-01:

```text
Success — #10B981
Warning — #D97706
Danger  — #EF4444
```

Estados informativos ou neutros deverão utilizar tokens compatíveis com a paleta oficial, sem introduzir arbitrariamente uma nova cor institucional.

---

# 14. Success

`Success` representa conclusão positiva.

Exemplos:

```text
Membro cadastrado com sucesso.

Pagamento registrado.

Evento atualizado.

Mensagem agendada com sucesso.
```

Não utilizar `Success` para simples informação sem resultado positivo.

---

# 15. Warning

`Warning` representa situação que merece atenção, mas que não necessariamente impede o fluxo.

Exemplo:

```text
Atenção

Este período possui lançamentos pendentes.
```

Warning não deverá ser tratado automaticamente como erro.

---

# 16. Danger

`Danger` deverá representar:

* erro;
* falha;
* risco;
* operação destrutiva;
* situação crítica.

Exemplo:

```text
Não foi possível registrar o lançamento.

Revise os dados e tente novamente.
```

---

# 17. Informativo e Estado Neutro

Mensagens puramente informativas deverão utilizar tratamento neutro ou institucional previsto pelos tokens do GDS.

Exemplo:

```text
Os dados deste relatório consideram o período
de 01/08/2026 a 31/08/2026.
```

Não utilizar `Warning` simplesmente para chamar atenção visual.

---

# 18. Anatomia dos Alertas

Estrutura recomendada:

```text
Alert
├── Icon opcional
├── Content
│   ├── Title opcional
│   └── Message
├── Action opcional
└── Close opcional
```

Exemplo:

```text
┌────────────────────────────────────────┐
│ ⚠ Atenção                         X    │
│                                        │
│ Existem dados que precisam ser         │
│ revisados antes de continuar.          │
│                                        │
│ [Revisar dados]                        │
└────────────────────────────────────────┘
```

---

# 19. Anatomia dos Toasts

Estrutura:

```text
Toast
├── Icon
├── Message
├── Action opcional
└── Close
```

O toast deverá ser compacto.

Não deverá conter formulários ou conteúdo complexo.

---

# 20. Títulos

Alertas poderão possuir título quando isso melhorar a compreensão.

Exemplos:

```text
Atenção

Não foi possível carregar os dados

Sessão expirada
```

Toasts simples normalmente não necessitam título separado.

---

# 21. Mensagens

A mensagem deverá ser:

* curta;
* específica;
* humana;
* acionável quando necessário.

Preferir:

```text
Não foi possível salvar o membro.
Verifique os campos destacados.
```

em vez de:

```text
Erro ao processar solicitação.
```

---

# 22. Ícones

Ícones poderão reforçar semanticamente a mensagem.

Exemplos conceituais:

```text
✓ Success
! Warning
× Danger
i Informação
```

O ícone não substitui o texto.

A iconografia deverá seguir o padrão oficial do GDS.

---

# 23. Ações

Alertas e toasts poderão possuir ação quando ela estiver diretamente relacionada à mensagem.

Exemplo:

```text
Não foi possível atualizar os dados.

[Tentar novamente]
```

Evitar múltiplas ações em toast.

---

# 24. Fechamento

Mensagens dispensáveis poderão possuir controle de fechamento.

O controle deverá:

* ser visível;
* possuir nome acessível;
* funcionar por teclado.

Mensagens críticas não deverão desaparecer apenas porque determinado tempo terminou.

---

# 25. Persistência

A duração deverá depender da importância.

```text
Sucesso simples
→ temporário

Informação importante
→ contextual/persistente

Erro que exige correção
→ persistente

Warning relevante
→ persistente até resolução ou dispensa
```

---

# 26. Duração

O usuário deverá possuir tempo suficiente para ler mensagens temporárias.

Não utilizar tempos extremamente curtos.

Mensagens que possuem ação não deverão desaparecer antes de o usuário ter oportunidade razoável de interagir.

---

# 27. Posicionamento

O GereIgreja deverá adotar posicionamento consistente para toasts.

O container de notificações deverá permanecer em posição previsível e não bloquear:

* navegação;
* botões essenciais;
* formulários;
* controles da sidebar.

Em telas pequenas, o componente deverá adaptar sua largura ao viewport.

---

# 28. Empilhamento

Quando múltiplos toasts forem apresentados, deverão formar uma pilha controlada.

Evitar:

```text
Toast
Toast
Toast
Toast
Toast
Toast
Toast
```

ocupando grande parte da interface.

Eventos repetitivos deverão ser consolidados quando possível.

Exemplo:

```text
8 registros atualizados com sucesso.
```

em vez de oito mensagens independentes.

---

# 29. Responsividade

Feedback deverá funcionar em:

* desktop;
* notebook;
* tablet;
* smartphone.

Em mobile:

* evitar largura fixa;
* preservar margens;
* permitir quebra de texto;
* manter controles acessíveis.

---

# 30. Acessibilidade

Feedback é informação funcional e deverá ser acessível.

Deverá considerar:

* contraste;
* leitores de tela;
* regiões live;
* foco;
* teclado;
* semântica;
* movimento.

---

# 31. Leitores de Tela

Mensagens importantes geradas dinamicamente deverão ser anunciadas adequadamente por tecnologias assistivas.

A estratégia deverá considerar o nível de urgência da mensagem.

---

# 32. Regiões Live

Feedback dinâmico poderá utilizar mecanismos como:

```html
aria-live="polite"
```

ou, para situações realmente urgentes:

```html
aria-live="assertive"
```

`assertive` não deverá ser utilizado indiscriminadamente.

Mensagens comuns de sucesso normalmente não justificam interrupção agressiva.

---

# 33. Foco

Um toast comum não deverá roubar foco automaticamente.

Erros de formulário poderão direcionar o usuário ao contexto do erro quando isso melhorar a acessibilidade.

Dialogs seguem as regras de foco do GDS-12.

---

# 34. Uso de Cor

Nenhum estado poderá depender exclusivamente de cor.

Inadequado:

```text
[caixa vermelha sem texto ou ícone]
```

Adequado:

```text
× Não foi possível salvar o registro.
```

---

# 35. Feedback de Loading

Operações assíncronas deverão indicar processamento quando houver atraso perceptível.

Exemplos:

```text
Salvando...

Carregando membros...

Gerando relatório...

Enviando comunicação...
```

A mensagem deverá refletir a operação real.

---

# 36. Feedback de Sucesso

Após sucesso, informar o resultado.

Exemplo:

```text
Congregação atualizada com sucesso.
```

Evitar mensagens redundantes quando a própria mudança da interface já torna o resultado evidente e não há risco de ambiguidade.

---

# 37. Feedback de Erro

Erros deverão explicar o problema em linguagem adequada ao usuário.

Sempre que possível, indicar uma ação de recuperação.

Exemplo:

```text
Não foi possível carregar os eventos.

[Tentar novamente]
```

---

# 38. Erros de Validação

Erros de validação deverão permanecer ligados ao campo ou conjunto de campos responsável.

Exemplo:

```text
Data do evento

[31/07/2026]

A data final não pode ser anterior à data inicial.
```

---

# 39. Erros de Negócio

Regras de domínio deverão produzir mensagens específicas.

Exemplo conceitual:

```text
Não foi possível concluir esta operação porque
o registro possui vínculos ativos.
```

A mensagem deverá refletir a regra real implementada.

---

# 40. Erros de Permissão

Quando apropriado, informar:

```text
Você não possui permissão para realizar esta ação.
```

Entretanto, a mensagem não deverá revelar registros ou informações que o usuário não deveria conhecer.

---

# 41. Erros de Autenticação e Sessão

Quando a sessão expirar, o usuário deverá receber orientação clara.

Quando houver dados não salvos, o fluxo deverá reduzir o risco de perda sempre que tecnicamente possível.

---

# 42. Erros de Rede

Em operações assíncronas:

```text
Não foi possível conectar ao servidor.

Verifique sua conexão e tente novamente.
```

A mensagem deverá ser utilizada somente quando esse diagnóstico for realmente apropriado.

---

# 43. Erros do Servidor

Erros inesperados deverão ser tratados.

O usuário poderá receber:

```text
Não foi possível concluir a operação.

Tente novamente. Se o problema continuar,
entre em contato com o responsável pelo sistema.
```

A implementação deverá registrar detalhes técnicos nos mecanismos apropriados de observabilidade.

---

# 44. Mensagens Técnicas

Nunca apresentar diretamente ao usuário final:

```text
Traceback
IntegrityError
OperationalError
DoesNotExist
KeyError
AttributeError
SQL
stack trace
```

Informações técnicas deverão permanecer nos mecanismos apropriados de diagnóstico.

---

# 45. Feedback e Django Messages

O framework de mensagens do Django poderá atuar como mecanismo servidor para feedback entre requests.

Exemplo conceitual:

```python
messages.success(
    request,
    "Membro cadastrado com sucesso."
)
```

As categorias do backend deverão ser mapeadas para a semântica do GDS.

A implementação deverá evitar que cada módulo crie um sistema independente de mensagens.

---

# 46. Feedback e HTMX

Operações HTMX deverão produzir feedback sem exigir recarregamento completo quando apropriado.

Fluxo:

```text
Usuário
   ↓
Ação HTMX
   ↓
Request Django
   ↓
Processamento
   ↓
Resposta
   ├── Atualiza conteúdo
   └── Gera feedback
```

---

# 47. Eventos HTMX

A aplicação poderá utilizar eventos HTMX padronizados para centralizar feedback de:

* sucesso;
* erro;
* falha de request;
* atualização;
* processamento.

Evitar listeners independentes e duplicados em cada página.

A implementação deverá permanecer compatível com a arquitetura frontend oficial.

---

# 48. Feedback e Alpine.js

Alpine.js poderá controlar:

* visibilidade;
* fechamento;
* temporização;
* pequenas interações;
* estado visual local.

Não deverá decidir regras de negócio ou autorização.

---

# 49. Feedback e Bootstrap

Bootstrap poderá fornecer infraestrutura de componentes como alerts e toasts.

Entretanto, a aparência e o comportamento deverão seguir o GDS.

Evitar utilizar diretamente variantes Bootstrap que introduzam padrões visuais conflitantes com a identidade do GereIgreja.

---

# 50. Feedback e Django Forms

Erros provenientes de Django Forms deverão ser apresentados pelo componente oficial de formulário.

Isso inclui:

* erros de campo;
* erros não associados a campo;
* validações customizadas.

O texto bruto retornado pelo backend deverá ser adequado à experiência do usuário.

---

# 51. Secretaria

Feedback da Secretaria deverá utilizar entidades reais do contexto.

Exemplos:

```text
Membro cadastrado com sucesso.

Membro atualizado com sucesso.

Visitante cadastrado.

Congregação atualizada.
```

Evitar:

```text
Registro salvo.
```

quando a entidade puder ser identificada.

---

# 52. Financeiro

Mensagens financeiras deverão possuir precisão superior.

Exemplos:

```text
Lançamento registrado com sucesso.

Despesa atualizada.

Receita registrada.

Estorno concluído.
```

Não utilizar mensagens que possam sugerir uma operação financeira diferente da realmente realizada.

---

# 53. Eventos

Exemplos:

```text
Evento cadastrado com sucesso.

Evento atualizado.

Evento cancelado.
```

Cancelamento e exclusão deverão permanecer semanticamente distintos.

---

# 54. Escola Bíblica

Exemplos:

```text
Turma cadastrada.

Aluno incluído na turma.

Frequência registrada.

Professor atualizado.
```

O texto deverá refletir a ação real do módulo.

---

# 55. Comunicação

O módulo de Comunicação exige diferenciação clara entre estados.

Exemplos conceituais:

```text
Mensagem salva como rascunho.

Comunicação agendada.

Envio iniciado.

Envio concluído.

Não foi possível enviar a comunicação.
```

`Agendado` não deverá ser comunicado como `Enviado`.

---

# 56. Administração

Exemplos:

```text
Usuário atualizado.

Permissões atualizadas.

Configuração salva.
```

Alterações de acesso deverão gerar feedback adequado ao impacto da operação.

---

# 57. Portal Público

O Portal Público deverá utilizar feedback somente quando houver interação que realmente o exija.

Exemplos:

* envio de formulário;
* inscrição;
* contato;
* falha de carregamento.

Mensagens administrativas internas não deverão aparecer no portal público.

---

# 58. Operações Financeiras

Mensagens financeiras deverão evitar ambiguidades.

Quando apropriado, o contexto poderá incluir:

```text
Descrição
Valor
Data
Status
```

Informações sensíveis somente deverão ser exibidas a usuários autorizados.

---

# 59. Exclusões

Após exclusão:

```text
Membro excluído.
```

somente se `excluído` representar corretamente a operação.

Se o sistema realizou inativação:

```text
Membro inativado.
```

A terminologia da mensagem deverá acompanhar a regra de domínio.

---

# 60. Estornos

Estorno é uma operação financeira distinta de exclusão.

Preferir:

```text
Lançamento estornado com sucesso.
```

Não utilizar:

```text
Lançamento excluído.
```

se houve estorno.

---

# 61. Alterações de Status

Feedback deverá informar o novo estado quando relevante.

Exemplo:

```text
Congregação marcada como ativa.
```

---

# 62. Operações em Massa

Uma operação em massa deverá gerar feedback consolidado.

Exemplo:

```text
18 membros foram atualizados.
```

Se houver sucesso parcial:

```text
15 registros foram atualizados.
3 registros não puderam ser processados.

[Ver detalhes]
```

---

# 63. Importações

Importações deverão distinguir:

```text
Arquivo recebido
Processamento
Sucesso
Sucesso parcial
Falha
```

Não comunicar sucesso antes de o processamento realmente terminar.

---

# 64. Exportações

Ao gerar exportação:

```text
Gerando arquivo...
```

Após conclusão:

```text
Arquivo gerado com sucesso.
```

A interface deverá fornecer a ação apropriada conforme a implementação real da exportação.

---

# 65. Processamentos Longos

Processos longos não deverão depender de toast temporário.

Utilizar componente persistente apropriado com:

* estado;
* progresso quando disponível;
* resultado;
* erro;
* ação posterior.

---

# 66. Estados Vazios

Estado vazio não é erro.

Exemplo:

```text
Nenhum evento cadastrado.

[Adicionar evento]
```

Não utilizar Danger.

---

# 67. Nenhum Resultado

Pesquisa sem resultado também não é erro.

Exemplo:

```text
Nenhum membro encontrado para os filtros aplicados.

[Limpar filtros]
```

---

# 68. Feedback em Tabelas

Tabelas deverão apresentar feedback no contexto da operação.

Exemplo:

```text
Editar membro
    ↓
Salvar
    ↓
Linha atualizada
    +
Toast de sucesso
```

Não recarregar desnecessariamente toda a página quando uma atualização parcial for suficiente.

---

# 69. Feedback em Cards

Cards dinâmicos poderão possuir estado próprio de:

* loading;
* erro;
* vazio.

O toast poderá complementar uma ação realizada pelo usuário, mas não deverá substituir o estado interno do card quando o problema pertence ao próprio componente.

---

# 70. Feedback em Modais

Em formulários de modal:

```text
Erro de validação
→ permanece no modal

Sucesso
→ modal pode fechar
→ contexto é atualizado
→ feedback é apresentado
```

Não fechar o modal quando houver erro que o usuário precise corrigir.

---

# 71. Feedback em Formulários

O usuário deverá conseguir identificar:

* qual campo possui problema;
* qual é o problema;
* como corrigi-lo.

Uma mensagem global isolada:

```text
Formulário inválido.
```

é insuficiente quando os erros específicos puderem ser apresentados.

---

# 72. Feedback em Páginas

Falhas que impedem o carregamento de uma seção relevante deverão aparecer dentro da própria página.

Exemplo:

```text
Não foi possível carregar os dados financeiros.

[Tentar novamente]
```

---

# 73. Feedback e Navegação

Mensagens pós-redirecionamento poderão utilizar Django Messages.

Exemplo:

```text
POST
 ↓
Sucesso
 ↓
Redirect
 ↓
Mensagem
```

Esse padrão deverá respeitar Post/Redirect/Get quando utilizado pela arquitetura do fluxo.

---

# 74. Preservação de Contexto

Uma mensagem não deverá causar perda desnecessária de:

* filtros;
* busca;
* paginação;
* aba selecionada;
* contexto da tela.

---

# 75. Permissões

Feedback não substitui autorização.

Fluxo obrigatório:

```text
Request
   ↓
Autorização backend
   ↓
Operação
   ↓
Feedback
```

Nunca:

```text
Botão oculto
   ↓
"segurança"
```

---

# 76. Multi-Tenant

Mensagens deverão respeitar o isolamento de dados do GereIgreja.

Um erro não deverá revelar:

* existência de registro de outra organização;
* nome de pessoa fora do escopo;
* informações financeiras de outro contexto;
* identificadores internos.

---

# 77. Segurança

Mensagens deverão evitar exposição de:

* caminhos internos;
* queries SQL;
* IDs sensíveis;
* tokens;
* secrets;
* detalhes de infraestrutura;
* stack traces.

---

# 78. Privacidade

Dados pessoais somente deverão aparecer em mensagens quando necessários para identificar a operação e quando o usuário possuir autorização.

Evitar incluir informações pessoais completas em toasts persistidos, logs frontend ou mensagens desnecessárias.

---

# 79. Auditoria

Feedback ao usuário e auditoria são responsabilidades diferentes.

```text
Feedback
→ comunica ao usuário

Auditoria
→ registra evento do sistema
```

Não utilizar toast como mecanismo de auditoria.

---

# 80. Conteúdo das Mensagens

A estrutura recomendada é:

```text
Ação + entidade + resultado
```

Exemplo:

```text
Membro atualizado com sucesso.
```

Para erro:

```text
Problema + ação possível
```

Exemplo:

```text
Não foi possível atualizar o membro.
Tente novamente.
```

---

# 81. Linguagem

A linguagem deverá ser:

* clara;
* profissional;
* direta;
* consistente;
* compreensível para usuários não técnicos.

Evitar jargão de engenharia.

---

# 82. Mensagens Acionáveis

Quando houver recuperação possível, informar a ação.

Exemplo:

```text
Não foi possível carregar os dados.

[Tentar novamente]
```

---

# 83. Mensagens Destrutivas

A confirmação ocorre antes da operação, conforme GDS-12.

Depois da operação, o feedback deverá comunicar o resultado.

```text
Confirmação
     ↓
Excluir
     ↓
Backend
     ↓
Registro excluído.
```

---

# 84. Mensagens Financeiras

Mensagens financeiras deverão diferenciar claramente:

* registrar;
* editar;
* cancelar;
* estornar;
* excluir, quando aplicável;
* confirmar.

Esses verbos não são intercambiáveis.

---

# 85. Datas e Valores

Quando datas ou valores forem necessários para desambiguar uma mensagem, utilizar os padrões oficiais da plataforma.

Exemplo:

```text
R$ 1.250,00
```

e:

```text
20/08/2026
```

Evitar excesso de dados dentro de toast.

---

# 86. Evitar Duplicidade

Uma mesma operação não deverá produzir simultaneamente:

```text
Toast
+
Alert
+
Modal
+
Mensagem inline
```

com o mesmo conteúdo sem necessidade.

Escolher o canal apropriado.

---

# 87. Prevenção de Spam Visual

Operações repetitivas deverão evitar dezenas de mensagens.

Exemplo inadequado:

```text
Registro 1 salvo.
Registro 2 salvo.
Registro 3 salvo.
...
```

Preferir:

```text
12 registros atualizados com sucesso.
```

---

# 88. Prioridade

Quando mensagens de prioridades diferentes ocorrerem simultaneamente, estados críticos deverão possuir precedência perceptiva.

Entretanto, o sistema não deverá simplesmente apagar feedback anterior importante.

---

# 89. Concorrência

Quando uma operação falhar porque o dado mudou desde sua leitura, o feedback deverá explicar a necessidade de atualização sem expor detalhes técnicos.

Exemplo:

```text
Este registro foi alterado enquanto você o editava.

Atualize os dados antes de continuar.
```

A mensagem somente deverá ser utilizada se esse mecanismo existir na implementação.

---

# 90. Idempotência

A interface deverá reduzir o risco de operações duplicadas.

Durante processamento:

```text
[Salvando...]
```

A ação poderá ser temporariamente desabilitada.

O backend deverá continuar responsável pela proteção adequada da operação.

---

# 91. Performance

O sistema de feedback deverá ser leve.

Evitar:

* bibliotecas redundantes;
* múltiplos sistemas de toast;
* listeners duplicados;
* containers repetidos;
* JavaScript específico por página sem necessidade.

---

# 92. Anti-Patterns

São proibidos ou desencorajados:

* `alert()` nativo do navegador como padrão de interface;
* mensagens técnicas;
* toast para erro de campo;
* toast para conteúdo crítico persistente;
* sucesso antes da confirmação do backend;
* mensagens genéricas;
* depender somente de cor;
* dezenas de toasts simultâneos;
* notificações duplicadas;
* modais usados apenas para informar sucesso;
* feedback sem contexto;
* erro sem possibilidade de recuperação quando ela existir;
* ocultar erro automaticamente antes da leitura;
* mensagens que revelam dados não autorizados.

---

# 93. Implementação

O sistema deverá possuir componentes reutilizáveis.

Estrutura conceitual:

```text
components/
└── feedback/
    ├── alert
    ├── toast
    ├── field-error
    ├── global-message
    └── loading
```

A organização física final deverá seguir a arquitetura oficial do projeto, e não necessariamente reproduzir literalmente essa estrutura.

---

# 94. Componentização

Não criar:

```text
financeiro_toast
secretaria_toast
eventos_toast
ebd_toast
```

quando todos representam o mesmo componente.

Preferir:

```text
Toast
+
variant
+
message
+
action
```

---

# 95. Tokens

Todos os componentes deverão utilizar os tokens do GDS.

Paleta base definida pelo GDS-01:

```text
Brand 700 — #0D8281
Brand 900 — #0A6665
Brand Soft — #DFF4F3

Background — #F1F5F9
Surface — #FFFFFF
Border — #D7E2E8
Text — #1E293B
Text Muted — #64748B

Success — #10B981
Warning — #D97706
Danger — #EF4444
```

Não criar cores hardcoded por módulo.

A estilização deverá permanecer centralizada em:

```text
static/css/design_system.css
```

---

# 96. CSS

Evitar:

```html
<div style="background: green;">
```

Preferir componentes e classes oficiais do GDS.

Bootstrap poderá ser utilizado como infraestrutura, mas os tokens do GereIgreja determinarão a identidade visual.

---

# 97. Testes

O sistema de feedback deverá ser testado em diferentes fluxos.

---

# 98. Testes Funcionais

Testar:

* sucesso;
* warning;
* erro;
* fechamento;
* ação;
* timeout;
* empilhamento;
* redirecionamento;
* HTMX;
* formulários;
* operações em massa.

---

# 99. Testes Visuais

Verificar:

* tipografia;
* espaçamento;
* ícone;
* contraste;
* quebra de linha;
* posicionamento;
* sobreposição;
* múltiplas mensagens.

---

# 100. Testes de Acessibilidade

Verificar:

* anúncio por leitor de tela;
* `aria-live`;
* foco;
* teclado;
* botão de fechar;
* contraste;
* dependência de cor.

---

# 101. Testes de Responsividade

Testar:

```text
Smartphone
Tablet
Notebook
Desktop
```

Toasts não deverão ultrapassar o viewport.

---

# 102. Testes de Segurança

Testar mensagens provenientes de:

* autorização negada;
* objetos inexistentes;
* erros de servidor;
* validação;
* isolamento organizacional.

Nenhuma resposta deverá revelar detalhes internos indevidos.

---

# 103. Especificações Oficiais

## GDS-FEEDBACK-001

Toda operação relevante deverá fornecer feedback quando seu resultado não for evidente.

## GDS-FEEDBACK-002

Feedback deverá utilizar linguagem específica ao contexto.

## GDS-FEEDBACK-003

Erros de campos deverão permanecer próximos aos campos correspondentes.

## GDS-FEEDBACK-004

Toasts deverão ser utilizados principalmente para feedback breve e não bloqueante.

## GDS-FEEDBACK-005

Mensagens críticas persistentes não deverão depender exclusivamente de toast temporário.

## GDS-FEEDBACK-006

Feedback não deverá depender somente de cor.

## GDS-FEEDBACK-007

Mensagens dinâmicas deverão considerar tecnologias assistivas.

## GDS-FEEDBACK-008

Detalhes técnicos não deverão ser exibidos ao usuário final.

## GDS-FEEDBACK-009

A autorização deverá ser validada no backend.

## GDS-FEEDBACK-010

Feedback deverá respeitar isolamento multi-tenant.

## GDS-FEEDBACK-011

Operações financeiras deverão utilizar terminologia precisa.

## GDS-FEEDBACK-012

Estorno, cancelamento, inativação e exclusão não deverão ser tratados como sinônimos.

## GDS-FEEDBACK-013

HTMX poderá atualizar feedback e conteúdo sem recarregamento completo quando apropriado.

## GDS-FEEDBACK-014

Alpine.js deverá limitar-se ao estado local da interface.

## GDS-FEEDBACK-015

Django Messages poderá ser utilizado como mecanismo servidor de mensagens entre requests.

## GDS-FEEDBACK-016

Bootstrap não deverá substituir a identidade visual do GDS.

## GDS-FEEDBACK-017

Mensagens repetitivas deverão ser consolidadas quando apropriado.

## GDS-FEEDBACK-018

Estados vazios não deverão ser apresentados como erro.

## GDS-FEEDBACK-019

Ausência de resultados de pesquisa não deverá ser apresentada como falha do sistema.

## GDS-FEEDBACK-020

Feedback deverá utilizar tokens oficiais do GDS.

## GDS-FEEDBACK-021

Componentes de feedback deverão ser reutilizáveis entre módulos.

## GDS-FEEDBACK-022

Uma operação não deverá gerar feedback duplicado sem justificativa.

## GDS-FEEDBACK-023

Mensagens não deverão revelar dados fora do escopo de acesso do usuário.

## GDS-FEEDBACK-024

Feedback de sucesso somente deverá ser emitido após confirmação real da operação.

## GDS-FEEDBACK-025

Processamentos longos deverão utilizar estados persistentes adequados.

---

# 104. Checklist

Antes da publicação de um fluxo, verificar:

## Conteúdo

* [ ] informa claramente o resultado;
* [ ] identifica a entidade quando apropriado;
* [ ] utiliza linguagem compreensível;
* [ ] não apresenta jargão técnico;
* [ ] oferece recuperação quando possível.

## Semântica

* [ ] Success utilizado corretamente;
* [ ] Warning utilizado corretamente;
* [ ] Danger utilizado corretamente;
* [ ] estado neutro utilizado para informação;
* [ ] não depende somente de cor.

## Componente

* [ ] inline quando ligado a campo;
* [ ] alert quando contextual/persistente;
* [ ] toast quando breve e não bloqueante;
* [ ] dialog somente quando exige decisão;
* [ ] loading quando há processamento perceptível.

## Acessibilidade

* [ ] contraste adequado;
* [ ] leitor de tela considerado;
* [ ] `aria-live` apropriado;
* [ ] botão de fechar acessível;
* [ ] foco não é roubado desnecessariamente;
* [ ] funciona por teclado.

## Responsividade

* [ ] smartphone;
* [ ] tablet;
* [ ] notebook;
* [ ] desktop;
* [ ] texto quebra corretamente;
* [ ] toast não bloqueia controles importantes.

## Backend

* [ ] resultado confirmado antes do sucesso;
* [ ] validação realizada no servidor;
* [ ] autorização validada;
* [ ] isolamento organizacional preservado;
* [ ] erros técnicos tratados.

## Django

* [ ] Django Messages utilizado de forma consistente quando aplicável;
* [ ] Django Forms fornece validações adequadas;
* [ ] mensagens do backend são apropriadas ao usuário.

## HTMX

* [ ] loading;
* [ ] sucesso;
* [ ] erro;
* [ ] atualização parcial;
* [ ] ausência de listeners duplicados;
* [ ] contexto preservado.

## Segurança

* [ ] sem stack trace;
* [ ] sem SQL;
* [ ] sem tokens;
* [ ] sem dados não autorizados;
* [ ] sem informações de outro tenant;
* [ ] sem detalhes internos desnecessários.

## Qualidade

* [ ] sem feedback duplicado;
* [ ] sem spam de toasts;
* [ ] mensagens consolidadas em operações em massa;
* [ ] terminologia consistente com o domínio;
* [ ] componente reutilizável.

---

# 105. Governança

O sistema de feedback pertence ao GereIgreja Design System e deverá ser mantido pela Equipe de Engenharia.

Nenhum módulo deverá criar:

* nova semântica;
* nova cor de status;
* novo sistema de toast;
* novo padrão de alerta;

sem avaliar primeiro os componentes existentes.

---

## 105.1 Nova Variante

Uma nova variante deverá possuir justificativa baseada em significado funcional.

Não criar variante apenas para obter uma nova cor.

---

## 105.2 Alteração Global

Mudanças no sistema de feedback deverão ser verificadas nos módulos:

```text
Secretaria
Financeiro
Eventos
Escola Bíblica
Comunicação
Administração
Portal Público
```

---

# 106. Evolução

A evolução deverá buscar:

* centralização;
* consistência;
* acessibilidade;
* redução de duplicações;
* integração uniforme com HTMX;
* integração uniforme com Django Messages;
* melhor tratamento de erros;
* observabilidade sem exposição técnica ao usuário.

A implementação poderá evoluir sem alterar a semântica definida neste documento.

---

# 107. Documentos Relacionados

* GDS-01 — GereIgreja Design System
* GDS-08 — Botões
* GDS-09 — Formulários
* GDS-10 — Cards
* GDS-11 — Tabelas e Listagens
* GDS-12 — Modais, Dialogs e Confirmações
* GEA-02 — Arquitetura da Plataforma
* GEA-04 — Arquitetura do Frontend
* GDF — Framework de Documentação
* GQF — Framework de Qualidade

---

# 108. Princípios Finais

O feedback é parte da interação, não um detalhe visual posterior.

No GereIgreja:

```text
Ação sem resposta
=
experiência incompleta
```

Cada mensagem deverá comunicar algo útil.

O sistema deverá evitar dois extremos:

```text
Silêncio
```

e:

```text
Excesso de notificações
```

O padrão ideal é:

```text
Ação
   ↓
Processamento perceptível quando necessário
   ↓
Resultado
   ↓
Feedback proporcional
   ↓
Continuidade do fluxo
```

O usuário deverá compreender o estado do sistema sem precisar interpretar cores, conhecer termos técnicos ou repetir ações por dúvida.

A consistência desse comportamento em Secretaria, Financeiro, Eventos, Escola Bíblica, Comunicação e Administração é essencial para que o GereIgreja transmita organização, segurança e confiabilidade.

---

# 109. Status do Documento

Pasta:

```text
docs/frameworks/
```

Arquivo:

```text
13-GDS-Alertas-Toasts-e-Feedback.md
```

Documento:

```text
GDS-13
```

Código:

```text
GDS-FEEDBACK
```

Framework:

```text
GDS — GereIgreja Design System
```

Versão:

```text
1.0
```

Status:

```text
Oficial
```

Responsável:

```text
Equipe de Engenharia
```

Última atualização:

```text
Agosto de 2026
```

---

# Fim do Documento

**GDS-13 — Alertas, Toasts e Feedback**
**GereIgreja Design System**
