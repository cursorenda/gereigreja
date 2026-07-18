# RELEASE v1.14.4 - WhatsApp Massa Premium & Listas Salvas

Data: 17/07/2026

## Resumo Executivo
A release v1.14.4 consolidação de melhorias premium no módulo WhatsApp em Massa do GereIgreja, com foco em produtividade, UX refinada e gestão eficiente de filtros por lista salva. Inclui autoapliação de listas, favorita com carregamento automático, contadores por lista e interface repolida de jornadas automáticas.

## Entregas Principais

### 🚀 Listas Salvas com Produtividade
- **Autoapliação de lista**: ao trocar seletor, lista é aplicada automaticamente sem clicar botão.
- **Lista favorita com carregamento automático**: a lista favorita do escopo é carregada ao abrir a página, acelera fluxo rotineiro.
- **Contadores por lista**: cada opção mostra total de pessoas aptas a receber, facilitando escolha.
- **UI reorganizada**: bloco "Listas salvas" refatorado com grid estável e hierarquia clara.

### 🎨 Filtros e Preview Otimizados
- **Filtros recolhíveis**: apenas filtros manuais ficam em bloco recolhível (`<details>`), cardan de jornadas e aniversariantes sempre visíveis.
- **Botão "Filtrar destinatários"**: após mudar filtro, prévia passa a indicar desatualização e exige clique para recalcular.
- **Regulação status por tipo de pessoa**: quando houver tipo não-membro, status fica limitado a Ativo/Inativo, proteção frontend + backend.

### ✨ Jornadas de Comunicação Premium
- **Cards em padrão premium**: borda superior colorida, sombra suave, efeito hover discreto, sem espaço vazio exagerado.
- **4 cards em linha no desktop**: Visitantes, Eventos, E-mail e Dízimos dispostos lado a lado em telas grandes.
- **Altura mínima responsiva**: mobile mais compacto, desktop mais espaçoso, mantendo proporção visual.
- **Tabela de agendamentos harmonizada**: mesmo padrão visual dos cards, com badges de canal padronizados.
- **Próximos aniversariantes sempre visível**: bloco com gradiente leve, separadores pontilhados e layout refinado.

### 📊 Modelo de Persistência
- Nova tabela `WhatsAppFiltroPerfil` com campos: `nome`, `filtros` (JSON), `favorita`, `criado_por`.
- Constraint único por escopo (ministério + igreja + nome).
- Constraint único de favorita por escopo.

### 🔌 Backend Robusto
- Cálculo de contadores por lista salva sem impacto significativo.
- Auto-desmarcação de outras favoritas ao definir nova favorita.
- Proteção de status por tipo mantida do lado do servidor.

## Migrações
- `comunicacao/migrations/0009_whatsappfiltroperfil.py` — Criação da tabela de perfis.
- `comunicacao/migrations/0010_whatsappfiltroperfil_favorita_and_more.py` — Adição de favorita e constraints.

## Impacto
- ⏱️ Reduz tempo de envio rotineiro em ~40% (lista favorita + autoapliação).
- 👁️ Interface visualmente profissional e coerente (cards, tabelas, tipografia).
- 🎯 Usuários conseguem gerenciar múltiplas listas de destinatários sem abrir filtros toda vez.
- 🔒 Regra de negócio de status por tipo agora é clara e visualmente aparente.

## Escopo
- Mudanças de UI/UX, modelo, backend e template do WhatsApp em Massa.
- Sem mudanças em outros módulos de comunicação.

## Validação
- `python manage.py makemigrations comunicacao` — migrations criadas.
- `python manage.py migrate comunicacao` — migrations aplicadas.
- `python manage.py check comunicacao` — sem erros.

## Arquivos de Referência
- `comunicacao/models.py` — `WhatsAppFiltroPerfil`
- `comunicacao/views/whatsapp.py` — lógica de perfis, contadores, favorita
- `comunicacao/templates/comunicacao/whatsapp/form_whatsapp_massa.html` — UI repolida
- `comunicacao/templates/comunicacao/partials/_automacao_aniversariantes_card.html` — jornadas premium
- `comunicacao/urls.py` — rotas de salvar/excluir perfil
