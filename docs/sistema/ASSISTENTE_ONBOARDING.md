# Assistente de Onboarding - Gereigreja

**Data de criação:** 18/04/2026  
**Versão:** v1.8.x+

---

## Visão Geral
O Assistente de Onboarding do Gereigreja é um guia interativo em etapas, exibido para novos usuários administradores de ministério, facilitando o preenchimento dos dados essenciais para o funcionamento do sistema.

- Modal flutuante, sempre disponível enquanto o onboarding não for concluído.
- Cada etapa mostra dados reais do sistema e oferece botões de ação (ex: editar, cadastrar).
- Totalmente modular: lógica em JS, dados via data-attributes, fácil de personalizar.

---

## Etapas do Onboarding

1. **Dados do Ministério**
   - Exibe informações do ministério (nome, razão social, CNPJ, responsável, etc).
   - Botão para editar dados do ministério.

2. **Dados da Igreja Principal**
   - Mostra dados da igreja principal vinculada ao ministério.
   - Exemplo de uso e botão para editar/cadastrar igreja.

3. **Configuração do Sistema**
   - Resumo das principais configurações (EBD, notificações, etc).
   - Botão para editar configurações do sistema.

4. **Cadastro de Membros**
   - Explica a importância do cadastro de membros.
   - Botão para cadastrar novo membro e link para lista de membros.

---

## Como Funciona
- O assistente só aparece se o usuário estiver autenticado e não tiver concluído todas as etapas.
- O backend (context processor) fornece os dados necessários para cada etapa.
- O template `partials/assistente_ajuda.html` inclui blocos ocultos com os dados, passados via data-attributes.
- O JS (`static/js/assistente.js`) lê esses dados e renderiza dinamicamente cada etapa.
- O progresso é salvo no `localStorage` do navegador.

---

## Personalização
- Para alterar textos, botões ou lógica de etapas, edite o array `etapasOnboarding` em `static/js/assistente.js`.
- Para adicionar/remover etapas, basta alterar o array e ajustar o backend se necessário.
- Os dados de cada etapa vêm dos data-attributes dos blocos ocultos no HTML.

---

## Dicas e Troubleshooting
- Se o assistente não aparecer, verifique se `mostrar_assistente` está sendo passado no contexto.
- Para forçar o assistente a reaparecer, limpe o `localStorage` do navegador (`onboarding_minimizado` e `onboarding_etapa`).
- Para customizar URLs de edição/cadastro, ajuste os data-attributes no template.

---

## Arquivos Relacionados
- `static/js/assistente.js` — lógica do assistente e etapas
- `templates/partials/assistente_ajuda.html` — HTML do modal e blocos de dados
- `configuracao/context_onboarding.py` — context processor que fornece os dados
- `static/css/assistente.css` — estilos do assistente

---

## Screenshots (Sugestão)
> Adicione capturas de tela de cada etapa para facilitar o entendimento visual.

---

Equipe Gereigreja
Abril/2026
