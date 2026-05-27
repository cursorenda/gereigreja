# Checklist de Regressao — Dashboard da Secretaria v1.13.2

## Objetivo

Validar rapidamente a entrega das Fases 1, 2 e 3 do Dashboard da Secretaria, cobrindo interface, comportamento operacional, permissões e consistência analítica.

---

## Escopo

- Rota principal: `/secretaria/dashboard/`
- Template: `secretaria/templates/secretaria/dashboard.html`
- View: `secretaria/views/dashboard.py`
- Assets:
  - `static/css/secretaria-dashboard.css`
  - `static/js/secretaria_dashboard_premium.js`

---

## Perfis Recomendados para Validação

1. Secretário Local
2. Pastor Local
3. Tesoureiro

---

## Pré-condições

1. Existir ao menos uma igreja com dados reais ou de demonstração no escopo do usuário.
2. Existirem membros ativos com datas de entrada distribuídas em meses diferentes.
3. Existirem alguns visitantes, cargos, grupos/casas, tags e acompanhamentos para validar os atalhos.
4. Opcional: existir conta vencida para validar o cartão de prioridade financeira.

---

## Checklist Rápido — 5 Minutos

### 1. Abertura e layout

1. Acessar `/secretaria/dashboard/` e confirmar carregamento sem erro visual.
2. Verificar se header, faixa de KPIs, Prioridades do Dia, Ações Operacionais e gráficos aparecem em ordem lógica.
3. Confirmar responsividade básica em desktop e largura reduzida.

### 2. Escopo e contexto

1. Confirmar exibição do chip de escopo no topo.
2. Validar que o texto muda conforme visão de igreja ativa ou consolidado.

### 3. KPIs principais

1. Conferir se aparecem valores para:
   - Novos membros (30 dias)
   - Aniversariantes do mês
   - Média de idade
   - Membros ativos
2. Clicar em `Ver lista` no card de aniversariantes e confirmar abertura do painel lateral.
3. Fechar o painel lateral e validar retorno ao estado normal.

### 4. Prioridades do Dia

1. Confirmar presença dos cartões:
   - Cadastro
   - Financeiro
   - Assinatura
2. Se houver pendências, validar mudança visual de severidade.
3. Confirmar que o cartão Financeiro segue a permissão do perfil:
   - Secretário Local: botão desabilitado com mensagem de sem permissão financeira
   - Pastor Local: acesso permitido quando possuir a permissão esperada
   - Tesoureiro: acesso permitido

### 5. Ações Operacionais

1. Validar presença dos cards de Pessoas, Recepção, Cargos, Grupos/Casas, Relatórios, Visita/Casa, Tags e Usuários.
2. Conferir se os botões principais navegam para rotas existentes.
3. Confirmar que contadores são renderizados sem quebrar layout quando estiverem zerados.

### 6. Gráficos e dados

1. Confirmar renderização dos gráficos de:
   - Evolução de Pessoas (12 meses)
   - Distribuição por Tipo
   - Pessoas por Status
   - Pessoas por Gênero
   - Participação por Categoria de Evento
   - Pessoas por Faixa Etária
2. Validar que gráficos sem dados mostram estado vazio legível.
3. Conferir se a série de evolução mensal não apresenta saltos incoerentes por troca de mês.

### 7. Regressão de acesso

1. Validar que usuário comum continua sendo redirecionado para o portal do membro.
2. Validar que superusuário continua sendo redirecionado para o admin.
3. Confirmar que o dashboard continua protegido por `page_access_required('dashboard_secretaria')`.

---

## Critérios de Aceite

1. Dashboard abre sem erro funcional nem quebra visual evidente.
2. Cards e gráficos respeitam dados reais do escopo do usuário.
3. Comportamento do cartão Financeiro permanece consistente com a política de permissões atual.
4. Séries mensais exibem tendência coerente com meses-calendário reais.

---

## Sinais de Regressão

1. Botão financeiro liberado para Secretário Local.
2. Gráficos vazios aparecendo como bloco quebrado ou canvas em branco sem contexto.
3. Painel de aniversariantes não abre ou não fecha.
4. Valores mensais variando de forma incompatível com o histórico conhecido.
5. Cards operacionais quebrando em telas menores.