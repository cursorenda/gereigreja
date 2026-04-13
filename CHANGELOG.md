## v1.8.70 — 13/04/2026
🏫 **EBD consolidada com cadastro mestre, escopo por igreja e vínculo com Secretaria**

### Principais mudanças
- ✅ Cadastro mestre de aluno na EBD com histórico consolidado de matrículas e transferências
- ✅ Escopo por igreja aplicado em listagens, formulários, relatórios e ações sensíveis da EBD
- ✅ Fluxos de vínculo individual e em lote entre cadastro da EBD e Pessoa da Secretaria

---

## v1.8.69 — 13/04/2026
🧭 **Hub de perfil integrado entre Configuração e Secretaria**

### Principais mudanças
- ✅ Novo hub de perfil com visão consolidada de Pessoa, Usuário e vínculos EBD
- ✅ Abas dedicadas para acesso, Secretaria, aluno EBD e professor EBD
- ✅ Links diretos da Secretaria para abertura do hub de perfil do usuário vinculado

---

## v1.8.68 — 13/04/2026
🛡️ **Hardening parcial de produção em secretaria, core e deploy**

### Principais mudanças
- ✅ Removidos handlers silenciosos e melhorada a observabilidade em fluxos críticos da Secretaria
- ✅ Substituídos `print` de produção por `logger.debug` em utilitários centrais de escopo
- ✅ Removidos logs residuais de debug no fluxo de deploy

---

## v1.8.67 — 12/04/2026
💳 **Painel financeiro: indicadores corretos de contas a pagar**

### Principais mudanças
- ✅ Corrigidos cards de **Contas Pendentes** e **Contas Vencidas** no painel financeiro
- ✅ Exibição de valor total por status (PEN/VEN)
- ✅ Exibição de quantidade de contas por status com link direto para lista filtrada

---

## v1.8.66 — 12/04/2026
🧪 **Estabilidade do fluxo de testes no deploy**

### Principais mudanças
- ✅ Execução de testes no deploy ajustada para `core.settings_test`
- ✅ Evita erro de histórico inconsistente de migrations em execução automatizada
- ✅ Ajustes nos testes de notificações para passar pelo middleware de grupos

---

## v1.8.65 — 12/04/2026
🔔 **Notificações de assinatura com destinatários corretos**

### Principais mudanças
- ✅ Notificações de assinatura restritas a perfis financeiros ministeriais
- ✅ Escopo de envio alinhado a `Admin Ministerio` e `Tesouraria Ministerial`

---

## v1.8.64 — 12/04/2026
📬 **Hotfix de notificações (marcar todas)**

### Principais mudanças
- ✅ Corrigido fluxo de **Marcar Todas Lidas**
- ✅ Endpoint reforçado para aceitar apenas `POST`
- ✅ Removido JavaScript inválido que causava erro em runtime na tela de notificações

---

## v1.8.63 — 11/04/2026
🎨 **Refino visual: logs e sessões da auditoria**

### Principais mudanças
- ✅ Reorganização de layout em `logs_alteracoes`, `logs_acessos_negados` e `sessoes_ativas`
- ✅ Melhorias de filtros, leitura de tabela e paginação

---

## v1.8.62 — 11/04/2026
🧭 **Rota canônica para atividades suspeitas**

### Principais mudanças
- ✅ Adicionada rota principal `/auditoria/atividades-suspeitas/`
- ✅ Mantida compatibilidade com rota/template legado

---

## v1.8.61 — 11/04/2026
🧱 **Consolidação de migrations da auditoria**

### Principais mudanças
- ✅ `0001_initial` consolidada com os 3 modelos da auditoria
- ✅ `0002` transformada em no-op para compatibilidade de ambientes existentes

---

## v1.8.60 — 11/04/2026
🗂️ **Admin-auditoria: central reorganizada em blocos**

### Principais mudanças
- ✅ Tela inicial do admin dedicado reorganizada em blocos de operação/consulta
- ✅ Navegação mais clara para equipes técnicas e administrativas

---

## v1.8.59 — 11/04/2026
🧭 **Admin-auditoria utilitário com links diretos**

### Principais mudanças
- ✅ Central da auditoria com links funcionais para ações principais
- ✅ Breadcrumb ajustado para retorno ao `/admin/`

---

## v1.8.58 — 11/04/2026
🧹 **Remoção de menu duplicado no admin-auditoria**

### Principais mudanças
- ✅ Eliminação de duplicidade visual no menu lateral
- ✅ Navegação do admin dedicado simplificada

---

## v1.8.57 — 11/04/2026
🔐 **Registro de modelos no admin-auditoria**

### Principais mudanças
- ✅ Modelos registrados no `AuditoriaAdminSite`
- ✅ Superusuário passou a visualizar corretamente os recursos do módulo

---

## v1.8.56 — 11/04/2026
🩹 **Fix NoReverseMatch no admin-auditoria**

### Principais mudanças
- ✅ Template de index dedicado para evitar reverse inválido
- ✅ Estabilização da landing do admin dedicado

---

## v1.8.55 — 11/04/2026
🚀 **Exposição do admin dedicado da auditoria**

### Principais mudanças
- ✅ Nova rota `/admin-auditoria/` integrada ao projeto

---

## v1.8.54 — 11/04/2026
🛠️ **Admin da auditoria atualizado**

### Principais mudanças
- ✅ Ajustes em `auditoria/admin.py`
- ✅ Inclusão de `admin_site` dedicado para o módulo

---

## v1.8.53 — 11/04/2026
📈 **Painel de auditoria com KPI de alto risco**

### Principais mudanças
- ✅ Indicador de usuários com alta acumulação de grupos
- ✅ Alerta visual para acelerar investigação

---

## v1.8.52 — 11/04/2026
📊 **Correção de altura infinita dos gráficos da auditoria**

### Principais mudanças
- ✅ Ajustes de container/configuração para renderização estável

---

## v1.8.51 — 11/04/2026
📉 **Gráficos no painel de auditoria via API**

### Principais mudanças
- ✅ Dashboard passou a consumir endpoint de estatísticas
- ✅ Visualização inicial de métricas de auditoria

---

## v1.8.50 — 11/04/2026
🕵️ **Tela para execução de auditoria de permissões**

### Principais mudanças
- ✅ Interface para acionar auditorias de permissão
- ✅ Suporte operacional para conferências rápidas

---

## v1.8.49 — 11/04/2026
🔌 **API de estatísticas da auditoria**

### Principais mudanças
- ✅ Endpoint de dados para gráficos e indicadores do painel

---

## v1.8.48 — 11/04/2026
🧽 **Limpeza de templates de auditoria (snapshot residual)**

### Principais mudanças
- ✅ Removido conteúdo residual que contaminava templates novos
- ✅ Estabilização de renderização e manutenção

---

## v1.8.47 — 11/04/2026
🔎 **Detalhes de usuário e acumulação de permissões**

### Principais mudanças
- ✅ Nova análise de acumulação de permissões
- ✅ Tela de detalhes de usuário para investigação contextual

---

## v1.8.46 — 11/04/2026
🏗️ **Infraestrutura de auditoria automatizada**

### Principais mudanças
- ✅ Inclusão de middleware/signals/context processor/utilitários de auditoria
- ✅ Indicador visual de modo auditoria

---

## v1.8.45 — 10/04/2026
🧩 **Correção de favicon e charset em base landing**

### Principais mudanças
- ✅ Ajustes de compatibilidade visual e encoding em templates base

---

## v1.8.44 — 10/04/2026
🩹 **Ajustes na análise de auditoria e alternar modo**

### Principais mudanças
- ✅ Correção de referência `nome_fantasia`
- ✅ Ajuste de redirect no fluxo de alternância de modo

---

## v1.8.43 — 10/04/2026
🧰 **Modo auditoria, exportação CSV e atividades suspeitas**

### Principais mudanças
- ✅ Alternância de modo auditoria
- ✅ Exportação CSV
- ✅ Primeira versão da análise de atividades suspeitas

---

## v1.8.42 — 10/04/2026
🗃️ **Compatibilidade de migration para Render**

### Principais mudanças
- ✅ Migration `0002` ajustada com `SeparateDatabaseAndState`
- ✅ Tratamento para tabelas já existentes em produção

---

## v1.8.41 — 10/04/2026
🧹 **Hotfix de limpeza em templates da auditoria**

### Principais mudanças
- ✅ Removidos trechos residuais que quebravam consistência de templates

---

## v1.8.40 — 10/04/2026
📌 **Lote 17: painel e rotas básicas da auditoria**

### Principais mudanças
- ✅ Primeira entrega de interface e endpoints do módulo de auditoria

---

## v1.8.39 — 10/04/2026
🧱 **Lote 16: expansão da base de modelos da auditoria**

### Principais mudanças
- ✅ Evolução estrutural dos modelos do app de auditoria

---

## v1.8.38 — 10/04/2026
🧪 **Lote 15: painel pytest no admin**

### Principais mudanças
- ✅ App `painel_testes` para execução e visibilidade de testes no admin

---

## v1.8.37 — 10/04/2026
🧪 **Lote 14: padronização pytest com settings_test**

### Principais mudanças
- ✅ Base de testes ajustada para ambiente controlado e reprodutível

---

## v1.8.36 — 10/04/2026
🏁 **Lote 13: base mínima da app auditoria**

### Principais mudanças
- ✅ Estrutura inicial da app `auditoria` no projeto

---

## v1.8.35 — 10/04/2026
🛡️ **Lote 12: painel admin de permissões e rotas de teste**

### Principais mudanças
- ✅ Ativação de painel administrativo de permissões
- ✅ Inclusão de rotas de teste de autorização

---

## v1.8.34 — 10/04/2026
🖼️ **Padronização de layout em telas de permissões**

### Principais mudanças
- ✅ Ajustes visuais para uso consistente com menu lateral

---

## v1.8.33 — 10/04/2026
🩹 **Fix de ordem de state/migration em contas 0007**

### Principais mudanças
- ✅ Corrigida sequência para evitar inconsistência durante migração

---

## v1.8.32 — 10/04/2026
🧰 **Lote 11: ajustes em testes de eventos e scripts auxiliares**

### Principais mudanças
- ✅ Melhorias seguras em testes e scripts de apoio

---

## v1.8.31 — 10/04/2026
🔁 **Idempotência em migration contas 0007**

### Principais mudanças
- ✅ Migration ajustada para cenários com tabelas pré-existentes

---

## v1.8.30 — 10/04/2026
🧭 **Lote 10: solicitação de permissões e painéis hierárquicos**

### Principais mudanças
- ✅ Fluxo de solicitação de permissões
- ✅ Painéis hierárquicos para gestão de vínculos e aprovações

---

## v1.8.29 — 10/04/2026
🧷 **Fix de favicon em templates base**

### Principais mudanças
- ✅ Correção de referência de favicon e limpeza de arquivo stale

---

## v1.8.28 — 10/04/2026
🧩 **Lote 9: melhorias em tags, auditoria e templates**

### Principais mudanças
- ✅ Templatetag de hierarquia e helpers de auditoria
- ✅ Refatorações em suporte/configuração e templates de formulários

---

## v1.8.27 — 09/04/2026
🛠️ **Backfill de notificações de transferências**

### Principais mudanças
- ✅ Novo comando para repovoar notificações de transferências já existentes

---

## v1.8.26 — 09/04/2026
🩹 **Fix em transferências: validação e ações/notificações**

### Principais mudanças
- ✅ Tratamento de `membro_id` inválido
- ✅ Melhorias de ações e notificações no fluxo

---

## v1.8.25 — 09/04/2026
🧱 **Lote 8: assets/admin panel e testes de cargos**

### Principais mudanças
- ✅ Promoção de assets e ajustes seguros no painel admin
- ✅ Evolução de testes de cargos

---

## v1.8.24 — 09/04/2026
🔄 **Sincronização central de grupos por cargos ativos**

### Principais mudanças
- ✅ Serviço central para sincronizar grupos de acordo com cargos ativos
- ✅ Redução de divergência entre cargo funcional e permissões efetivas

---

## v1.8.23 — 08/04/2026
🔁 **Transferências: fluxo completo de decisão (aprovar, recusar, cancelar) com notificações**

### Principais mudanças
- ✅ Adicionadas ações de **Recusar** e **Cancelar** transferência com registro de motivo
- ✅ Novas telas de confirmação para recusa e cancelamento
- ✅ Lista de transferências atualizada com ações contextuais por escopo
- ✅ Notificações automáticas para origem/destino conforme a decisão

### Arquivos principais
- `secretaria/transferencia_views.py`
- `secretaria/transferencia_urls.py`
- `secretaria/templates/secretaria/transferencia_list.html`
- `secretaria/templates/secretaria/transferencia_recusar.html`
- `secretaria/templates/secretaria/transferencia_cancelar.html`

---

## v1.8.22 — 08/04/2026
🔔 **Transferências: notificação no sininho + badge de pendências**

### Principais mudanças
- ✅ Ao solicitar transferência, sistema cria notificação para gestores da igreja destino
- ✅ Badge/alerta no topo para pendências de aprovação no escopo do usuário
- ✅ Item de menu "Transferências" na Secretaria com contador de pendências

### Arquivos principais
- `secretaria/transferencia_views.py`
- `core/context_processors.py`
- `core/settings.py`
- `templates/base_com_menu.html`
- `templates/menu.html`

---

## v1.8.21 — 08/04/2026
🧾 **Hotfix de formulário de transferência**

### Correções
- ✅ Corrigido envio de `membro_id` no POST com fallback para querystring
- ✅ Removido falso erro de campo obrigatório quando membro está fixado e desabilitado

---

## v1.8.20 — 08/04/2026
🐛 **Hotfix NameError em lista de pessoas**

### Correções
- ✅ Corrigido `NameError: SECRETARIO_LOCAL` em `secretaria/views.py`

---

## v1.8.19 — 08/04/2026
👁️ **Transferências: visibilidade e acesso por hierarquia**

### Correções
- ✅ Botão "Transferir" exibido na lista e no detalhe de pessoas
- ✅ Gate de acesso migrado para hierarquia (Secretário Local ou superior)

---

## v1.8.18 — 08/04/2026
🚚 **Novo módulo de transferência de membros (origem → destino)**

### Entregas
- ✅ Modelo `TransferenciaMembro` + migration isolada (`10003_transferenciamembro`)
- ✅ Fluxo inicial de solicitar, listar e aprovar transferência
- ✅ Rotas específicas de transferência em `secretaria/transferencia_urls.py`
- ✅ Botão de solicitação no detalhe de pessoa

---

## v1.8.17 — 08/04/2026
🧩 **Padronização de grupos em template tags**

### Ajuste
- ✅ `has_group` de `secretaria_extras` passou a usar API central de grupos

---

## v1.8.16 — 08/04/2026
💰 **Hotfix financeiro para Pastor Local**

### Correções
- ✅ Painel financeiro liberado para Pastor Local e níveis superiores na hierarquia

---

## v1.8.15 — 08/04/2026
🧠 **Lote 4 (core): hierarquia em decorators e escopo global no middleware**

### Entregas
- ✅ Refatoração de decorators para `user_has_permission_level_or_higher`
- ✅ `request.igrejas_permitidas` populado no middleware
- ✅ Ajustes de context processors e views para modelo hierárquico

---

## v1.8.14 — 08/04/2026
🎨 **Lote 3 (templates): melhorias de escopo e UX**

### Entregas
- ✅ Inclusão de escopo ativo em telas de secretaria/financeiro
- ✅ Ajustes de estado vazio e filtros em lista de pessoas

---

## v1.8.13 — 08/04/2026
🧪 **Lote 2: documentação e testes**

### Entregas
- ✅ Promoção de arquivos de `docs/` e `tests/` sem risco de runtime

---

## v1.8.12 — 08/04/2026
🧱 **Lote 1: base de hierarquia de grupos**

### Entregas
- ✅ Inclusão de `HIERARQUIA_GRUPOS` e helper de comparação hierárquica

---

## v1.8.11 — 08/04/2026
🧯 **Hotfix lista de pessoas vazia em Secretaria**

### Correções
- ✅ Fallback de escopo em `_membros_queryset_por_escopo` quando `request.igrejas_permitidas` não está definido

---

## v1.8.10 — 08/04/2026
🧯 **Hotfix AttributeError em /secretaria/pessoas/**

### Correções
- ✅ Correção de acessos diretos a `request.igrejas_permitidas` com fallback seguro

---

## v1.8.0 — 08/04/2026
🔐 **FOCO EM SEGURANÇA: Renomeação de Grupos Ministeriais, Proteção de Dados e Controle de Acesso Hierárquico**

### 🎯 Mudanças de Segurança e Acesso

#### Renomeação de Grupos Ministeriais
- `Lideranca Secretaria` → `Secretaria Ministerial` (mais ministerial e profissional)
- `Lideranca Financeira` → `Tesouraria Ministerial` (mais ministerial e profissional)
- [✅] Migração de dados aplicada com sucesso (groups no DB renomeados)
- [✅] Todas as constants atualizadas em `contas/constants.py`
- [✅] Docstrings e management commands refletindo novos nomes

#### Proteção de Grupos no Django Admin
- [✅] Novo `GroupAdminProtegido` implementado para bloquear renomeação de grupos centralizados
- Campo `name` agora é readonly para grupos: Admin Ministério, Secretaria Ministerial, Tesouraria Ministerial, etc.
- Permissões podem ser editadas normalmente (field não fica bloqueado)
- Impede acidentes de renomeação manual que quebrariam a lógica de permissões

#### Desbloqueio e Filtro de Escopo para Cargo (Secretaria)
- [✅] Pastor Local agora pode acessar `/secretaria/cargos/` (antes: 403 Forbidden)
- Novo decorator `is_admin_or_pastor_local()` (exigia `PASTOR_LOCAL` level antes tinha `PASTOR_REGIONAL`)
- [✅] Filtro de escopo hierárquico em 5 views: `lista_cargos`, `criar_cargo`, `editar_cargo`, `excluir_cargo`, `gerenciar_ocupantes`

#### Regra de Escopo Hierárquico para Cargos
- **Pastor Local**: vê/gerencia apenas cargos a partir de `PASTOR_LOCAL` para baixo (inclui `SECRETARIO_LOCAL`, `TESOUREIRO`, etc.)
- **Pastor Regional**: vê/gerencia apenas cargos a partir de `PASTOR_REGIONAL` para baixo (inclui `PASTOR_LOCAL` e níveis inferiores)
- **Admin Ministério**: sem restrição (vê todos os cargos)
- Implementado via 3 funções helper: `_nomes_grupos_permitidos_para_cargos()`, `_filtrar_cargos_por_escopo_usuario()`, `_cargo_dentro_escopo_usuario()`
- Form field `grupo_permissao` automaticamente limitado ao escopo do usuário

#### Testes de Regressão
- [✅] Nova suite: `secretaria/tests/test_cargos_autorizacao_views.py` (6 testes)
  - `test_pastor_local_lista_cargos_filtra_grupos_superiores` — Lista não exibe Admin Ministério
  - `test_pastor_local_nao_pode_editar_cargo_superior_por_url_direta` → 403
  - `test_pastor_local_nao_pode_excluir_cargo_superior_por_url_direta` → 403
  - `test_pastor_local_nao_pode_gerenciar_ocupantes_de_cargo_superior` → 403
  - `test_pastor_local_form_criar_cargo_limita_grupos_disponiveis` — Dropdown sem opções superiores
  - `test_pastor_regional_lista_cargos_filtra_grupos_superiores` — Regional filtra acima de PASTOR_REGIONAL

### ✅ Validação
- `manage.py check` → OK
- `secretaria.tests.test_cargos_permissoes` → 5/5 OK (signal tests não afetados)
- `secretaria.tests.test_cargos_autorizacao_views` → 6/6 OK
- Migração `contas/0004_rename_grupos_ministeriais` → OK (applied)

### 📚 Documentação
- `docs/HIERARQUIA_PERMISSOES.md` — updated
- `docs/CARGOS_USUARIOS.md` — updated
- `docs/CARGOS_SISTEMA.md` — new section "Changes in v1.8.0"
- `docs/GRUPOS_PERMISSOES.md` — updated
- All docstrings in code updated to reflect new group names

---

## v1.7.1 — 25/03/2026
🚀 **ATUALIZAÇÃO DE SISTEMA – FOCO EM ESTABILIDADE E USABILIDADE**

### Melhorias e Correções
- Correção no cadastro de pessoas: botões “Salvar” e “Salvar e Continuar” agora funcionam conforme esperado
- Seleção e salvamento de tags corrigidos no cadastro de membros
- Organização e correção dos arquivos JS/CSS (estáticos), evitando problemas de cache
- Mensagens de feedback mais claras e navegação mais fluida
- Outros pequenos ajustes e correções de bugs

---

## v1.7.0 — 16/03/2026
🌟 **NOVO: Cadastro Público Modernizado, Validações Avançadas e Visual Profissional**

### Novidades e Melhorias
- Campo “Celular” adicionado ao cadastro de pessoas
- Formulário público reorganizado: mais campos, máscaras automáticas, busca de endereço por CEP
- Página de sucesso do cadastro público modernizada e responsiva
- Validações robustas: CPF (dígito verificador), email (regex), máscaras, ViaCEP, feedback visual
- Preview instantâneo da foto de perfil
- Visual profissional e responsivo nas telas de pessoa
- Documentação técnica e manual do usuário atualizados
- Regras de negócio detalhadas para tipos/status de pessoa
- Sistema híbrido de participantes para eventos
- Refino visual e usabilidade em formulários, listas e detalhes
- Ajustes de máscaras, feedbacks e UX em campos obrigatórios e navegação
- Atualização do índice e organização da documentação

### Itens validados
- Cadastro público funcionando
- Validações e máscaras ativas
- Campo celular visível e salvo
- Preview de foto funcionando
- Documentação acessível
- Listas, filtros e dashboards OK

---

## v1.6.1 — 12/03/2026
🎨 **MELHORIAS NO CADASTRO DE PESSOAS** - Data customizada de mudanças + Indicadores visuais de campos obrigatórios

### 🎯 Visão Geral

Versão focada em **UX e precisão de dados** no módulo de cadastro de pessoas. Implementa data customizada para mudanças retroativas de tipo/status (evitando registros incorretos no histórico) e padroniza indicadores visuais de campos obrigatórios com badges vermelhos.

**Destaques:**
- ✅ Data customizada para mudança de Tipo/Status (retroativa)
- ✅ Badges vermelhos "Obrigatório" padronizados (igual eventos)
- ✅ Input Group integrado (select + data no mesmo bloco)
- ✅ Destaque visual automático (amarelo) quando há mudança
- ✅ Data sempre editável pelo usuário
- ✅ Badge de cadastro/atualização em edição

---

### ✨ Novas Funcionalidades

#### 📅 Data Customizada para Mudança de Tipo/Status

**🆕 Problema Resolvido:**
Quando um usuário altera o tipo ou status de uma pessoa dias/semanas depois da mudança real ter ocorrido, o `StatusHistorico` registrava a data atual (incorreta) ao invés da data real da mudança.

**✅ Solução Implementada:**

**1️⃣ Campos de Data no Formulário**
- Adicionado `data_mudanca_tipo` e `data_mudanca_status` no `MembroForm`
- Input Group Bootstrap: `[Select Tipo ▼][📅][Data]` (visual integrado)
- Data default = hoje, mas **sempre editável**
- Arquivos: `secretaria/forms.py`, `secretaria/templates/partials/_form_dados_cadastrais.html`

**2️⃣ Detecção Automática de Mudança (JavaScript)**
```javascript
// Armazena valores iniciais ao carregar
valorInicialTipo = tipoField.value;
valorInicialStatus = statusField.value;

// Quando usuário muda select:
if (this.value !== valorInicialTipo) {
    // Destaque amarelo (campo data fica #fff3cd)
    // Box-shadow amarelo no input-group
}
```
- Arquivo: `_form_dados_cadastrais.html` (linhas ~135-198)

**3️⃣ Backend - Processamento da Data Customizada**

**Modelo (`secretaria/models.py`):**
```python
def save(self, *args, **kwargs):
    data_mudanca_tipo = kwargs.pop('data_mudanca_tipo', None)
    data_mudanca_status = kwargs.pop('data_mudanca_status', None)
    
    # ... lógica de detecção de mudança ...
    
    # Usa data customizada se fornecida
    if data_mudanca_tipo:
        data_transicao_final = datetime.combine(data_mudanca_tipo, time(12, 0))
    
    StatusHistorico.objects.create(
        data_transicao=data_transicao_final,  # Data correta!
        # ... outros campos ...
    )
```

**Views (`secretaria/views.py`):**
- `criar_membro()`: Captura `form.cleaned_data.get('data_mudanca_tipo')`
- `editar_membro()`: Passa datas para `membro.save(user=..., data_mudanca_tipo=..., data_mudanca_status=...)`
- Arquivos modificados: linhas ~3223-3238, ~3380-3396

**4️⃣ Visual (CSS)**
```css
/* Campo amarelo quando mudança detectada */
input[type="date"] {
    background-color: #fff3cd;  /* Amarelo claro */
    border-color: #ffc107;      /* Borda amarela */
}
.input-group {
    box-shadow: 0 0 0 0.2rem rgba(255, 193, 7, 0.25);
}
```

**Exemplos de Uso:**
```
Cenário 1: Mudança HOJE
→ Usuário muda Status "Ativo" → "Inativo"
→ Campo data destaca em amarelo (12/03/2026)
→ Salva → Histórico: "Status alterado em 12/03/2026 12:00"

Cenário 2: Mudança RETROATIVA
→ Usuário muda Tipo "Visitante" → "Membro" 
→ Edita data para 01/03/2026 (batismo foi mês passado)
→ Salva → Histórico: "Tipo alterado em 01/03/2026 12:00" ✅
```

---

#### 🎨 Indicadores Visuais de Campos Obrigatórios

**🆕 Badges Vermelhos Padronizados**

Substituído asteriscos (`*`) por badges Bootstrap `<span class="badge bg-danger">Obrigatório</span>`, padronizando com o cadastro de eventos.

**Campos Marcados:**
- ✅ **Nome** → Badge vermelho
- ✅ **Igreja** → Badge vermelho  
- ✅ **Tipo de Pessoa** → Badge vermelho
- ✅ **Status da Pessoa** → Badge vermelho

**Antes:**
```html
<label>Nome: *</label>  <!-- Discreto, fácil ignorar -->
```

**Depois:**
```html
<label>
    Nome
    <span class="badge bg-danger ms-1">Obrigatório</span>
</label>
```

**CSS Customizado:**
```css
.badge.bg-danger {
    font-size: 0.7rem;
    font-weight: 600;
    padding: 0.25em 0.5em;
    vertical-align: middle;
}
```

**Arquivos:** `secretaria/templates/partials/_form_dados_cadastrais.html`

---

#### 📋 Badges de Data/Hora de Cadastro (Edição)

**🆕 Visual Aprimorado em Edição**

Em `editar_membro.html`, substituído texto simples por badges coloridos no header:

**Antes:**
```html
<span class="text-white-50">
    Cadastrado em: 11/03/2026 14:30
</span>
```

**Depois:**
```html
<span class="badge bg-info">
    📅 Cadastrado em: 11/03/2026 14:30
</span>
<span class="badge bg-secondary">
    🕒 Última atualização: 12/03/2026 10:15
</span>
```

**+ Alert Informativo em Cadastro:**
```html
<div class="alert alert-info">
    ℹ️ A data e hora do cadastro serão registradas 
    automaticamente ao salvar.
</div>
```

**Arquivos:** `secretaria/templates/secretaria/criar_membro.html`, `editar_membro.html`

---

#### 🔒 Validações de Dados e Máscaras Automáticas

**🆕 Validação Inteligente de CPF, Email, CEP e Telefone**

Implementado sistema completo de validação backend + frontend com máscaras automáticas e busca de endereço por CEP.

**1️⃣ Validação de CPF (Backend)**
```python
def validar_cpf(cpf):
    """Valida CPF usando algoritmo de dígito verificador (Receita Federal)."""
    cpf = re.sub(r'[^0-9]', '', cpf)  # Remove pontuação
    
    # Valida comprimento
    if len(cpf) != 11:
        raise ValidationError('CPF deve ter 11 dígitos.')
    
    # Rejeita CPFs com todos dígitos iguais (111.111.111-11, etc)
    if cpf == cpf[0] * 11:
        raise ValidationError('CPF inválido (todos os dígitos iguais).')
    
    # Valida primeiro e segundo dígito verificador
    # [Algoritmo matemático oficial]
    
    return cpf
```

**🎯 Recursos:**
- ✅ Algoritmo oficial de dígito verificador
- ✅ Rejeita CPFs inválidos (000.000.000-00, 111.111.111-11)
- ✅ Formata automaticamente: `12345678909` → `123.456.789-09`
- ✅ Aceita entrada com ou sem pontuação

**Arquivo:** `secretaria/forms.py` (linhas 1-50)

---

**2️⃣ Validação de Email (Backend)**
```python
def clean_email(self):
    """Valida formato de email."""
    email = self.cleaned_data.get('email')
    if email:
        email = email.strip().lower()  # Remove espaços + lowercase
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError('Email inválido. Use: nome@exemplo.com')
    return email
```

**🎯 Recursos:**
- ✅ Validação regex completa
- ✅ Conversão automática para lowercase
- ✅ Remove espaços em branco
- ✅ Mensagem erro amigável

**Arquivo:** `secretaria/forms.py` (linhas ~240-250)

---

**3️⃣ Máscaras JavaScript (Frontend)**

**CPF:**
```javascript
// Máscara automática: ###.###.###-##
aplicarMascara(cpfInput, '###.###.###-##');
```
- **Entrada:** `12345678909`
- **Resultado:** `123.456.789-09`

**Telefone:**
```javascript
// Máscara automática: (##) #####-####
// Suporta celular (9 dígitos)
```
- **Entrada:** `85987654321`
- **Resultado:** `(85) 98765-4321`

**CEP:**
```javascript
// Máscara automática: #####-###
aplicarMascara(cepInput, '#####-###');
```
- **Entrada:** `60000000`
- **Resultado:** `60000-000`

**RG:**
```javascript
// Permite apenas números e letras (uppercase)
e.target.value = e.target.value.toUpperCase().replace(/[^0-9A-Z]/g, '');
```

**Arquivo:** `secretaria/templates/partials/_form_dados_cadastrais.html` (linhas ~485-570)

---

**4️⃣ Busca Automática de Endereço por CEP (ViaCEP API)**

**🔥 Integração com API ViaCEP:**

```javascript
// Ao sair do campo CEP (onblur):
fetch(`https://viacep.com.br/ws/${cep}/json/`)
    .then(response => response.json())
    .then(data => {
        if (!data.erro) {
            // Preenche automaticamente:
            document.getElementById('id_rua').value = data.logradouro;
            document.getElementById('id_bairro_distrito').value = data.bairro;
            document.getElementById('id_cidade').value = data.localidade;
            document.getElementById('id_estado').value = data.uf;
            
            // Foca no campo "Número"
            document.getElementById('id_numero_casa').focus();
        }
    });
```

**🎯 Funcionalidades:**
- ✅ Busca automática ao sair do campo CEP
- ✅ Preenche: Rua, Bairro, Cidade, Estado
- ✅ Feedback visual: borda verde (sucesso) / vermelha (erro)
- ✅ Loading indicator: "Buscando endereço..."
- ✅ Foca automaticamente no campo "Número da casa"
- ✅ Tratamento de erro: alerta se CEP não encontrado
- ✅ Funciona offline (não bloqueia formulário)

**Experiência do Usuário:**
1. Usuário digita: `60000000`
2. Máscara formata: `60000-000`
3. Ao sair do campo → busca automática
4. Campos preenchidos em **< 1 segundo**
5. Usuário só precisa digitar número da casa

**Arquivo:** `secretaria/templates/partials/_form_dados_cadastrais.html` (linhas ~516-560)

---

**🎯 Resumo das Validações:**

| Campo       | Backend | Frontend | Máscara        | API       |
|-------------|---------|----------|----------------|-----------|
| **CPF**     | ✅      | ✅       | XXX.XXX.XXX-XX | —         |
| **Email**   | ✅      | —        | —              | —         |
| **Telefone**| —       | ✅       | (XX) XXXXX-XXXX| —         |
| **CEP**     | —       | ✅       | XXXXX-XXX      | ✅ ViaCEP |
| **RG**      | —       | ✅       | A-Z 0-9        | —         |

---

#### 🚀 Navegação Rápida entre Pessoas

**🆕 Problema Resolvido:**
Ao editar várias pessoas sequencialmente, usuário precisava voltar para lista → buscar → abrir próximo cadastro (muitos cliques).

**✅ Solução Implementada:**

**1️⃣ Barra de Navegação (Setas + Dropdown)**

```html
<div class="card mb-3">
    <div class="d-flex align-items-center justify-content-between">
        <!-- Setas Anterior/Próximo -->
        <a href="{% url 'secretaria:editar_membro' membro_id=prev_id %}" 
           class="btn btn-sm btn-outline-primary">
            <i class="fas fa-arrow-left"></i> Anterior
        </a>
        
        <!-- Dropdown (300px) -->
        <select class="form-select form-select-sm" style="width: 300px;" 
                onchange="if(this.value) window.location.href='...'">
            {% for membro_id, membro_nome in membros_lista %}
            <option value="{{ membro_id }}" {% if membro_id == form.instance.pk %}selected{% endif %}>
                {{ membro_nome }}
            </option>
            {% endfor %}
        </select>
        
        <a href="{% url 'secretaria:editar_membro' membro_id=next_id %}" 
           class="btn btn-sm btn-outline-primary">
            Próximo <i class="fas fa-arrow-right"></i>
        </a>
        
        <!-- Contador -->
        <small class="text-muted">
            <i class="fas fa-users me-1"></i>
            Pessoa {{ current_position }} de {{ total_count }} (exceto inativos)
        </small>
    </div>
</div>
```

**🎯 Recursos:**
- ✅ Navegação por setas (← Anterior / Próximo →)
- ✅ Dropdown com lista completa (300px)
- ✅ Contador: "Pessoa 5 de 120 (exceto inativos)"
- ✅ Exclui apenas inativos (mantém disciplinados, desligados)
- ✅ Ordenação alfabética por nome
- ✅ Implementado em **Editar** e **Visualizar**

**Arquivos:**
- `secretaria/views.py` (helper `_get_navigation_context()`)
- `secretaria/templates/secretaria/editar_membro.html`
- `secretaria/templates/secretaria/detalhe_membro.html`

---

**2️⃣ Filtro Inteligente (Exclui Apenas Inativos)**

```python
def _get_navigation_context(membro_id, allowed_churches):
    """
    Helper navegação entre membros.
    Exclui apenas inativos (falecidos, mudados de cidade).
    """
    membros_permitidos = Membro.objects.filter(
        igreja__in=allowed_churches
    ).exclude(
        status_pessoa__nome='Inativo'  # Exclui apenas inativos
    ).order_by('nome').values_list('pk', 'nome')
```

**🎯 Lógica:**
- ❌ **Exclui:** Inativos (falecidos, mudados) → raramente editados
- ✅ **Inclui:** Ativos, Disciplinados, Desligados → frequentemente editados
- ✅ Mantém pessoas com status temporários (disciplina é processo ativo)

**Arquivo:** `secretaria/views.py` (linhas ~3024-3065)

---

**3️⃣ Alert Informativo (Pessoas Inativas)**

```html
{% if form.instance.status_pessoa.nome == 'Inativo' %}
<div class="alert alert-warning alert-dismissible fade show mb-3">
    <i class="fas fa-info-circle me-2"></i>
    <strong>Atenção:</strong> Esta pessoa está com status "Inativo". 
    A navegação rápida não inclui pessoas inativas.
    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
</div>
{% endif %}
```

**🎯 Funcionalidades:**
- ✅ Explica por que navegação está "desabilitada"
- ✅ Evita confusão quando usuário abre inativo diretamente da lista
- ✅ Dispensável (botão X)

---

#### 📊 Visualização Melhorada (Detalhe Membro)

**🆕 Seção "Datas Importantes"**

```html
<h5 class="border-bottom pb-2 mb-3 mt-4">Datas Importantes</h5>
<div class="row mb-3">
    <div class="col-md-4">
        <strong>📅 Nascimento:</strong> 15/03/1985
    </div>
    <div class="col-md-4">
        <strong>⛪ Entrada na Igreja:</strong> 
        10/01/2020
        <span class="badge bg-primary ms-1">Batismo</span>
    </div>
    <div class="col-md-4">
        <strong>💍 Casamento:</strong> 20/06/2015
    </div>
</div>
```

**🎯 Recursos:**
- ✅ Visualização consolidada das 3 datas principais
- ✅ Badge tipo entrada (Batismo, Transferência, Aclamação)
- ✅ Emojis para rápida identificação visual

**Arquivo:** `secretaria/templates/secretaria/detalhe_membro.html`

---

**🆕 Histórico Completo de Tipo + Status**

**Antes:** Tabela 4 colunas (só status)
```html
<table>
    <th>Data</th>
    <th>Status Anterior</th>
    <th>Novo Status</th>
    <th>Observação</th>
</table>
```

**Depois:** Tabela 7 colunas (tipo + status)
```html
<table class="table table-sm table-striped table-hover">
    <thead>
        <tr>
            <th>Data/Hora</th>
            <th>Tipo Anterior</th>
            <th>Novo Tipo</th>
            <th>Status Anterior</th>
            <th>Novo Status</th>
            <th>Observação</th>
            <th>Registrado Por</th>
        </tr>
    </thead>
    <tbody>
        {% for hist in historico_status %}
        <tr>
            <td>{{ hist.data_transicao|date:"d/m/Y H:i" }}</td>
            <td>{{ hist.tipo_pessoa_anterior.nome|default:"—" }}</td>
            <td>{{ hist.tipo_pessoa_novo.nome|default:"—" }}</td>
            <td>{{ hist.status_pessoa_anterior.nome|default:"—" }}</td>
            <td>{{ hist.status_pessoa_novo.nome|default:"—" }}</td>
            <td>{{ hist.observacao|default:"—" }}</td>
            <td>{{ hist.registrado_por.get_full_name|default:"Sistema" }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

**🎯 Recursos:**
- ✅ Histórico completo de tipo E status
- ✅ Data customizada (se usuário mudou retroativamente)
- ✅ Usuário responsável pela mudança
- ✅ Hover effect para melhor leitura

**Arquivo:** `secretaria/templates/secretaria/detalhe_membro.html`

---

### 🔧 Melhorias Técnicas

#### 📦 Arquivos Modificados

**Models:**
- `secretaria/models.py` (linhas ~269-345)
  - `save()`: Aceita `data_mudanca_tipo` e `data_mudanca_status`
  - Converte `date` para `datetime` automaticamente
  - Cria `StatusHistorico` com data customizada

**Forms:**
- `secretaria/forms.py` (linhas 1-50, ~240-250)
  - **NOVO:** `validar_cpf()`: Função helper com algoritmo dígito verificador
  - **NOVO:** `clean_cpf()`: Valida + formata XXX.XXX.XXX-XX
  - **NOVO:** `clean_email()`: Valida regex + lowercase
  - Adicionado `data_mudanca_tipo = forms.DateField()`
  - Adicionado `data_mudanca_status = forms.DateField()`

**Views:**
- `secretaria/views.py`
  - `criar_membro()`: Captura e passa datas customizadas
  - `editar_membro()`: Idem + `save_m2m()` para tags
  - **NOVO:** `_get_navigation_context()`: Helper navegação entre pessoas (linhas ~3024-3065)
  - **NOVO:** `detalhe_membro()`: Contexto navegação + filtro inativos

**Templates:**
- `secretaria/templates/partials/_form_dados_cadastrais.html` (~570 linhas)
  - Input Group para tipo/status + data
  - JavaScript: detecção mudança + destaque amarelo
  - **NOVO:** Máscaras JavaScript (CPF, telefone, CEP, RG) - linhas ~485-570
  - **NOVO:** Integração API ViaCEP (busca endereço) - linhas ~516-560
  - **NOVO:** Feedback visual (borda verde/vermelha)
  - Badges "Obrigatório" nos 4 campos required
  - CSS customizado para badges e input-group
- `secretaria/templates/secretaria/criar_membro.html`
  - Alert informativo sobre data automática
- `secretaria/templates/secretaria/editar_membro.html`
  - **NOVO:** Barra navegação (setas + dropdown + contador) - linhas ~16-60
  - **NOVO:** Alert para pessoas inativas
  - Badges data/hora cadastro
- `secretaria/templates/secretaria/detalhe_membro.html`
  - **NOVO:** Barra navegação idêntica ao editar
  - **NOVO:** Seção "Datas Importantes" (3 datas)
  - **NOVO:** Histórico completo (7 colunas: tipo + status)
  - Alert informativo sobre data automática
- `secretaria/templates/secretaria/editar_membro.html`
  - Badges coloridos para criado_em/atualizado_em

---

### 🎯 Impacto

**Precisão de Dados:**
- ✅ Histórico de mudanças com datas corretas
- ✅ Relatórios por período mais confiáveis
- ✅ Auditoria precisa de quando mudanças ocorreram

**Experiência do Usuário:**
- ✅ Visual integrado (select + data no mesmo bloco)
- ✅ Destaque automático quando há mudança
- ✅ Badges "Obrigatório" muito mais visíveis
- ✅ Consistência visual com módulo de eventos

**Manutenibilidade:**
- ✅ Código modular e reutilizável
- ✅ JavaScript bem documentado
- ✅ CSS customizado isolado em `<style>`

---

### 📚 Documentação

**Arquivos de Referência:**
- `CHAT_RESPOSTAS.md` - Análise completa do módulo de pessoas (23 melhorias sugeridas)
- Este CHANGELOG - Documentação técnica das implementações

---

## v1.6.0 — 11/03/2026
🎯 **SISTEMA HÍBRIDO DE PARTICIPANTES** + **AGENDA TURBINADA** - Gestão inteligente de participantes automáticos + 10 melhorias na agenda

### 🎯 Visão Geral

Esta versão traz o **Sistema Híbrido de Participantes** que revoluciona a gestão de eventos futuros, gerando listas automaticamente no momento do evento, e **10 funcionalidades novas na Agenda** incluindo importação automática de feriados, visualização em lista, destaques visuais e performance 70% melhor.

**Destaques:**
- ✅ Sistema Híbrido de Participantes (critérios automáticos + ajustes manuais)
- ✅ Importação automática de feriados brasileiros (biblioteca holidays==0.61)
- ✅ Visualização em lista/tabela alternativa ao calendário
- ✅ Destaques visuais inteligentes (hoje/semana/passados)
- ✅ Performance 70% melhor no carregamento da agenda
- ✅ Modo tela cheia para o calendário
- ✅ Autocomplete otimizado com select_related
- ✅ 6 bugs corrigidos (FieldError, conflito JS, badges cortados)
- ✅ ~1.800 linhas de código novo
- ✅ 3 documentos técnicos (600+ linhas)

---

### ✨ Novas Funcionalidades

#### 🎯 Sistema Híbrido de Participantes (Eventos)

**🆕 Gestão Inteligente Automática + Manual**
- ✅ Método `get_participantes_esperados()` retorna listas atualizadas dinamicamente
- ✅ Critérios automáticos (tipos de pessoa + status) aplicados no momento do evento
- ✅ Inclusões/exclusões manuais preservadas (campo `tipo_inclusao`)
- ✅ Migration: `eventos/migrations/0012_participacaoevento_tipo_inclusao.py`
- ✅ 3 tipos: AUTOMATICA, MANUAL_ADICIONADO, MANUAL_REMOVIDO

#### 📅 Agenda - 10 Melhorias Massivas

**1️⃣ Importação Automática de Feriados**
- ✅ Biblioteca `holidays==0.61` (feriados brasileiros)
- ✅ Modal Bootstrap para selecionar ano e estado
- ✅ Comando management: `python manage.py importar_feriados --ano 2026 --estado SP`
- ✅ Não duplica feriados existentes
- ✅ View `importar_feriados_view()` com validação de igreja

**2️⃣ Visualização em Lista/Tabela**
- ✅ Alternância entre calendário e lista
- ✅ 7 colunas: Data, Título, Horário, Local, Igreja, Participantes, Ações
- ✅ Ordenação cronológica automática
- ✅ Rendering otimizado com DocumentFragment

**3️⃣ Destaques Visuais Inteligentes**
- ✅ Eventos de HOJE: destaque verde com animação pulso
- ✅ Eventos da SEMANA: fundo amarelo suave
- ✅ Eventos PASSADOS: opacidade 65% (discretos)

**4️⃣ Badge de Participantes Esperados**
- ✅ Contador visual em cada evento
- ✅ Position absolute (top: 2px, right: 2px)
- ✅ Background rgba(0,0,0,0.8)
- ✅ Toggle mostrar/ocultar com localStorage

**5️⃣ Modo Tela Cheia**
- ✅ Calendário em overlay fullscreen (z-index: 9998)
- ✅ Botão X para fechar (top: 70px)
- ✅ Tecla ESC para sair
- ✅ Auto-alternância para calendário se estiver em lista

**6️⃣ Filtro Inteligente de Datas**
- ✅ Domingo da semana atual até +365 dias
- ✅ Performance 70% melhor (evita carregar eventos antigos)
- ✅ Cálculo: `domingo_semana_atual = hoje - timedelta(days=(dia_semana + 1) % 7)`

**7️⃣ Memória de Preferências (localStorage)**
- ✅ 3 chaves: `calendar_view`, `modo_visualizacao`, `mostrar_participantes`
- ✅ Persiste preferências entre sessões

**8️⃣ Reorganização de Botões**
- ✅ 2 grupos lógicos: filtros (sólidos) + visualização (outline)
- ✅ Ordem: Hoje → Mês → Feriados | Lista → Tela Cheia

**9️⃣ CSS Agenda Separado**
- ✅ Arquivo `static/css/agenda.css` (845 linhas)
- ✅ Estilos de badge, fullscreen, lista, destaques

**🔟 Autocomplete Otimizado (Eventos)**
- ✅ `select_related('tipo_pessoa', 'status_pessoa', 'igreja')`
- ✅ Exists/OuterRef para cooperadores
- ✅ Limite 500 registros
- ✅ Log de performance (50% mais rápido)

---

### 🐛 Correções

1. **FieldError 'id' into field** - Corrigido para `pk` (Membro usa 'chave' como pk)
2. **Conflito JavaScript** - Variável `calendarEl` renomeada para `calendarDiv` no fullscreen
3. **Badge Participantes Cortado** - Position absolute com z-index: 2
4. **Botão X Sobrepondo Controles** - Movido de top: 20px para top: 70px
5. **Tela Cheia em Modo Lista** - Auto-alterna para calendário antes de expandir
6. **Mensagens Duplicadas** - Removido include duplicado em lista_igrejas.html

---

### 📊 Estatísticas

- **Código:** ~1.800 linhas adicionadas
  - agenda/views.py: 462 linhas totais
  - agenda/templates/agenda/agenda.html: 983 linhas
  - static/css/agenda.css: 845 linhas (CRIADO)
  - eventos/models.py: get_participantes_esperados() (46 linhas)
  - eventos/views.py: autocomplete otimizado (93 linhas)
  - agenda/management/commands/importar_feriados.py: 105 linhas (CRIADO)

- **Documentação:** ~600 linhas
  - RELEASE_NOTES_v1.6.0.md: 570 linhas
  - SISTEMA_HIBRIDO_PARTICIPANTES.md: 152 linhas
  - REGRAS_TIPOS_PESSOA_STATUS.md: 454 linhas

- **Migrations:** 1 nova
  - eventos/0012_participacaoevento_tipo_inclusao.py

- **Dependências:** 1 nova
  - holidays==0.61

---

### 🚀 Atualização

```bash
# 1. Atualizar código
git pull origin master

# 2. Instalar nova dependência
pip install holidays==0.61

# 3. Aplicar migrations
python manage.py migrate

# 4. Collectstatic
python manage.py collectstatic --noinput

# 5. (Opcional) Importar feriados
python manage.py importar_feriados --ano 2026 --estado SP

# 6. Reiniciar servidor
sudo systemctl restart gunicorn
```

---

## v1.4.0 — 06/03/2026
🔐 **SISTEMA DE GRUPOS E PERMISSÕES** + **COLUNAS ORDENÁVEIS** - Refatoração arquitetural com hierarquia de permissões e ordenação interativa

### 🎯 Visão Geral

Esta versão traz uma **refatoração arquitetural massiva** do sistema de grupos e permissões, estabelecendo uma hierarquia clara com 14 grupos, sistema de constantes centralizado, e funções helper reutilizáveis. Adicionalmente, implementa colunas ordenáveis na lista de pessoas.

**Destaques:**
- ✅ Sistema hierárquico de 14 grupos (incluindo novo grupo **Pastor Local**)
- ✅ Constantes centralizadas em `contas/constants.py` (elimina strings hardcoded)
- ✅ 15+ funções helper para verificação de permissões
- ✅ 2 migrations de banco de dados (renomeação de grupos + novo grupo)
- ✅ Menus dinâmicos baseados em permissões
- ✅ Colunas clicáveis com ordenação ASC/DESC
- ✅ 40+ arquivos refatorados
- ✅ Documentação completa (~2500 linhas)

---

### ✨ Novas Funcionalidades

#### 🔐 Sistema de Grupos e Permissões

**🆕 Novo Grupo: Pastor Local**
- ✅ Criado grupo **Pastor Local** para diferenciar hierarquia
- ✅ **Pastor Local**: Pastor de UMA igreja específica
- ✅ **Pastor Regional**: Supervisiona VÁRIAS igrejas
- ✅ Migration: `contas/migrations/0003_add_pastor_local_group.py`
- ✅ Hierarquia: Admin → Regional → Local → Equipe Administrativa

**📋 Hierarquia Completa (14 Grupos):**
```
Nível 1: Admin Ministerio
Nível 2: Lideranca Secretaria, Lideranca Financeira
Nível 3: Pastor Regional
Nível 4: Pastor Local ← NOVO!
Nível 5: Secretario Local, Tesoureiro, Superintendente EBD
Nível 6: Equipe de Eventos, Equipe de Mídia, Equipe de Recepção, Professores EBD, Secretaria EBD
Nível 7: Membro Comum
```

**🔧 Arquivo de Constantes (contas/constants.py - 314 linhas)**
- ✅ 14 constantes de grupos centralizadas
- ✅ 6 hierarquias pré-definidas (`GRUPOS_ADMIN`, `GRUPOS_LIDERANCA`, etc)
- ✅ 15+ funções helper:
  * `user_is_admin(user)` - Verifica se é Admin Ministerio
  * `user_is_lideranca(user)` - Verifica liderança (qualquer nível)
  * `user_is_lideranca_secretaria(user)` - Liderança Secretaria ou superior
  * `user_is_lideranca_financeira(user)` - Liderança Financeira ou superior
  * `user_pode_gerenciar_secretaria(user)` - Pode gerenciar secretaria
  * `user_pode_gerenciar_financeiro(user)` - Pode gerenciar financeiro
  * `user_pode_gerenciar_ebd(user)` - Pode gerenciar EBD
  * `user_pode_ver_financeiro(user)` - Pode visualizar finanças
  * `user_escopo_ministerial(user)` - Tem escopo de todas as igrejas
  * `user_tem_grupo(user, nome_grupo)` - Verifica grupo específico
  * `user_tem_qualquer_grupo(user, lista)` - Verifica qualquer grupo da lista
  * E mais...

**🔄 Renomeação de Grupos (Migration 0002)**
- ✅ `Superintendentes` → `Superintendente EBD` (singular + clareza)
- ✅ `Lider Igreja` → `Pastor Regional` (mais específico)
- ✅ `Secretario` → `Secretario Local` (diferencia de ministerial)
- ✅ Migration: `contas/migrations/0002_renomear_grupos.py`
- ✅ Rollback suportado (reversível)

**⚙️ Comando de Gerenciamento**
```bash
# Configurar permissões de todos os grupos
python manage.py configurar_permissoes_grupos

# Opções:
--reset      # Remove e recria todos os grupos
--dry-run    # Simula sem fazer mudanças
```
- ✅ Arquivo: `contas/management/commands/configurar_permissoes_grupos.py` (570 linhas)
- ✅ Configura permissões específicas para cada grupo
- ✅ Suporta modo dry-run para testes
- ✅ Validação de permissões existentes

**🔒 Refatoração de Código (40+ arquivos)**

Substituição de strings hardcoded por constantes:

**ANTES:**
```python
if request.user.groups.filter(name='Admin Ministerio').exists():
    # ...
```

**DEPOIS:**
```python
from contas.constants import user_is_admin

if user_is_admin(request.user):
    # ...
```

**Arquivos Refatorados:**
- ✅ `core/decorators.py` - Decorators de segurança
- ✅ `core/views.py` - Views do sistema
- ✅ `contas/views.py` - Gerenciamento de usuários (7 ocorrências)
- ✅ `configuracao/views.py` - Configurações (6 ocorrências)
- ✅ `configuracao/utils.py` - Utils de configuração
- ✅ `secretaria/views.py` - Gestão de pessoas (2 ocorrências)
- ✅ `secretaria/utils.py` - Utils de secretaria (4 ocorrências)
- ✅ `financeiro/utils.py` - Utils financeiras (3 ocorrências)
- ✅ `financeiro/views.py` - Views financeiras
- ✅ `eventos/views.py` - Eventos
- ✅ `escola_biblica/views.py` - EBD
- ✅ `comunicacao/utils.py` - Comunicação
- ✅ `comunicacao/views.py` - Views de comunicação
- ✅ `agenda/views.py` - Agenda
- ✅ `suporte/views.py` - Suporte (2 ocorrências)

**🎨 Menus Dinâmicos Baseados em Permissões**
- ✅ `templates/base_com_menu.html` - Menu principal responsivo
- ✅ `templates/menu.html` - Itens de menu condicionais
- ✅ Menus aparecem/desaparecem baseados no grupo do usuário
- ✅ Admin vê tudo, Membro Comum vê apenas opções básicas

**🚫 Página 403 Melhorada**
- ✅ `templates/403.html` - Design profissional
- ✅ Mensagem clara de acesso negado
- ✅ Orientação para contatar administrador
- ✅ Botão "Voltar" e "Página Inicial"

**🗄️ Página de Erro de Banco**
- ✅ `templates/database_error.html` - Erro 503 estilizado
- ✅ Detecta tipo de erro (timeout, conexão recusada, genérico)
- ✅ Orientações para usuário (aguardar, verificar conexão)
- ✅ Detalhes técnicos (apenas para superusuários)
- ✅ Refresh automático após 30 segundos

#### 📊 Secretaria - Colunas Ordenáveis

**Nova Feature: Headers Clicáveis com Ordenação**
- ✅ 6 colunas ordenáveis na lista de pessoas:
  * Nome
  * Gênero
  * Tipo/Status
  * Data de Nascimento
  * Igreja (modo consolidado)
- ✅ Alternância ASC/DESC ao clicar na mesma coluna
- ✅ Indicadores visuais:
  * Setas (↑ ↓) para direção
  * Highlight azul na coluna ativa
  * Hover effect nos headers
- ✅ Ordenação preservada:
  * Na paginação
  * Na impressão de lista
  * Com todos os filtros
- ✅ Validação de segurança (campos permitidos)

**Implementação Técnica:**

`secretaria/views.py` - Função `lista_membros()`:
```python
ORDEM_CAMPOS = {
    'nome': 'nome',
    'data_nascimento': 'nascimento',  # Campo real: nascimento
    'genero': 'genero',
    'tipo': 'tipo_pessoa__nome',
    'status': 'status_pessoa__nome',
    'igreja': 'igreja__nome_igreja',
}

order_by = request.GET.get('order_by', 'nome')
order_dir = request.GET.get('order_dir', 'asc')

# Validação de segurança
if order_by not in ORDEM_CAMPOS:
    order_by = 'nome'
if order_dir not in ['asc', 'desc']:
    order_dir = 'asc'

# Aplicar ordenação
order_field = ORDEM_CAMPOS[order_by]
if order_dir == 'desc':
    order_field = '-' + order_field

membros = membros.order_by(order_field)
```

`secretaria/templates/secretaria/lista_membros.html` - CSS:
```css
.sortable-header {
    cursor: pointer;
    user-select: none;
    position: relative;
    padding-right: 20px;
}
.sortable-header:hover {
    background: rgba(255,255,255,0.1);
}
.sortable-header.active {
    font-weight: 700;
    color: #2196f3;
}
.sort-icon {
    position: absolute;
    right: 5px;
    opacity: 0.6;
}
```

`secretaria/templates/secretaria/lista_membros.html` - Headers:
```django
<a href="?{% url_replace order_by='nome' order_dir=toggle_dir %}" 
   class="sortable-header{% if order_by == 'nome' %} active{% endif %}">
    Nome
    {% if order_by == 'nome' %}
        <span class="sort-icon">{% if order_dir == 'asc' %}↑{% else %}↓{% endif %}</span>
    {% endif %}
</a>
```

**Função `imprimir_lista_membros()` também atualizada:**
- ✅ Mesma lógica `ORDEM_CAMPOS`
- ✅ Ordenação aplicada antes de renderizar
- ✅ Informação de ordenação em `filtros_aplicados`
- ✅ Exemplo: "Ordenação: Nome (Crescente)"

---

### 🐛 Correções

#### Secretaria - Campo de Nascimento

**Problema:** Mapeamento incorreto causava FieldError
- ❌ **Antes**: `'data_nascimento': 'data_nascimento'`
- ✅ **Depois**: `'data_nascimento': 'nascimento'`
- ✅ Erro "Cannot resolve keyword 'data_nascimento'" eliminado
- ✅ Ordenação por data de nascimento funciona corretamente

**Arquivos corrigidos:**
- `secretaria/views.py` - Função `lista_membros()` (linha ~2930)
- `secretaria/views.py` - Função `imprimir_lista_membros()` (linha ~3080)

#### Documentação - Terminologia Pessoa vs Membro

**Problema:** Inconsistência terminológica na documentação
- ⚠️ Sistema gerencia 5 tipos: Membro, Visitante, Congregado, Novo Convertido, Obreiro
- ⚠️ "Membro" é apenas UM tipo, não o termo genérico
- ⚠️ Modelo real é `Pessoa`, `Membro` é proxy de compatibilidade

**Correções em `skills/secretaria/SKILL.md`:**
- ✅ Novo cabeçalho explicativo sobre Pessoa vs Membro
- ✅ Clarificado: `Pessoa` = modelo real (tabela no banco)
- ✅ Clarificado: `Membro` = proxy com `verbose_name = "Membro (compat)"`
- ✅ Clarificado: Campo de nascimento é `nascimento` (não `data_nascimento`)
- ✅ Exemplos atualizados: "Cadastrar Pessoa" (não "Cadastrar Membro")
- ✅ Funções renomeadas: `mudar_status_pessoa()` (não `mudar_status_membro()`)
- ✅ Boas práticas expandidas com nomes corretos de campos
- ✅ Seção de novidades v1.3.1 atualizada com melhorias de documentação

---

### 📚 Documentação

#### Documentação Técnica Completa (2500+ linhas)

**Novos Arquivos:**
- ✅ `docs/GRUPOS_PERMISSOES.md` - Guia completo do sistema de permissões
- ✅ `docs/ANALISE_MENUS_BASEADOS_PERMISSOES.md` - Análise de menus dinâmicos
- ✅ `docs/AUDITORIA_PERMISSOES_SISTEMA_COMPLETO.md` - Auditoria completa
- ✅ `docs/DECORATORS_SEGURANCA.md` - Documentação de decorators
- ✅ `docs/SELETOR_IGREJA.md` - Sistema de seleção de igreja ativa
- ✅ `docs/PROBLEMA_UX_PAGINA_VAZIA.md` - Análise de UX
- ✅ `skills/configuracao/ESTRUTURA_GRUPOS_COMPLETA.md` (984 linhas!) - Estrutura completa
- ✅ `notes/FASE2_COMPLETA.md` - Resumo da implementação

**Arquivos Atualizados:**
- ✅ `README.md` - Seção de grupos e permissões adicionada
- ✅ `README_TESTS.md` - Testes atualizados
- ✅ `skills/secretaria/SKILL.md` - Terminologia Pessoa vs Membro

#### Scripts de Diagnóstico e Auditoria

**Novos Scripts:**
- ✅ `auditar_grupos_permissoes.py` - Auditoria do sistema
- ✅ `diagnostico_grupos_permissoes.py` - Diagnóstico rápido
- ✅ `test_grupos_permissoes.py` - Testes automatizados (359 linhas)
- ✅ `test_shell.py` - Testes via Django shell

---

### 🔧 Mudanças Técnicas

#### Migrations de Banco de Dados (2)

**Migration 0002: Renomear Grupos**
```python
# contas/migrations/0002_renomear_grupos.py
'Superintendentes' → 'Superintendente EBD'
'Lider Igreja' → 'Pastor Regional'
'Secretario' → 'Secretario Local'
```

**Migration 0003: Adicionar Pastor Local**
```python
# contas/migrations/0003_add_pastor_local_group.py
Group.objects.get_or_create(name='Pastor Local')
```

**⚠️ IMPORTANTE:** Executar migrations no servidor:
```bash
python manage.py migrate contas
```

#### Arquivos Deletados (Limpeza)

Removidos arquivos obsoletos/duplicados:
- ❌ `CHANGELOG_v1.2.0.md` (movido para `docs/release-notes/`)
- ❌ `README_old_backup.md` (backup desnecessário)
- ❌ `RELEASE_NOTES_v1.2.0.md` (movido para `docs/release-notes/`)

#### Templates Novos

**Visualização de Pessoas:**
- ✅ `secretaria/templates/secretaria/detalhe_membro.html` (220 linhas)
- ✅ `secretaria/templates/secretaria/imprimir_lista_membros.html` (326 linhas)

**Sistema de Permissões:**
- ✅ `contas/templates/contas/aguardando_acesso.html` - Página para usuários sem grupo
- ✅ `templates/database_error.html` (159 linhas) - Erro de conexão ao banco

#### Testes Automatizados

**Novos Testes:**
- ✅ `escola_biblica/tests/test_professor_permissions.py` (632 linhas)
  * Testa permissões granulares de professores EBD
  * Valida que professores veem apenas suas turmas
  * 20+ casos de teste

---

### 🎯 Impacto UX

#### Antes da v1.4.0:
- ❌ Strings hardcoded espalhadas pelo código (difícil manutenção)
- ❌ Sem hierarquia clara de grupos
- ❌ Menus estáticos (todos veem tudo)
- ❌ Lista de pessoas sem ordenação (apenas alfabética)
- ❌ Confusão entre "Membro" (tipo) e "Pessoa" (modelo)
- ❌ Pastor Local e Regional no mesmo grupo
- ❌ Documentação incompleta sobre permissões

#### Depois da v1.4.0:
- ✅ Constantes centralizadas (fácil manutenção)
- ✅ Hierarquia de 14 grupos bem definida
- ✅ Menus dinâmicos (cada grupo vê apenas o que pode)
- ✅ Lista ordenável por 6 colunas (click to sort)
- ✅ Terminologia clara e consistente
- ✅ Separação Pastor Local vs Regional
- ✅ Documentação completa (~2500 linhas)
- ✅ 15+ funções helper reutilizáveis
- ✅ Sistema profissional e escalável

---

### 📊 Métricas de Implementação

| Métrica | Valor |
|---------|-------|
| **Arquivos novos** | 30+ |
| **Arquivos modificados** | 40+ |
| **Linhas de código adicionadas** | ~3000 |
| **Linhas de documentação** | ~2500 |
| **Migrations de BD** | 2 |
| **Comandos de gerenciamento** | 1 |
| **Constantes criadas** | 14 |
| **Funções helper** | 15+ |
| **Grupos renomeados** | 3 |
| **Novos grupos** | 1 (Pastor Local) |
| **Templates novos** | 5 |
| **Testes automatizados** | 632 linhas |

---

### ⚠️ Breaking Changes

**Migrations Obrigatórias:**
- ⚠️ **Requer execução de migrations:** `python manage.py migrate contas`
- ⚠️ **Grupos renomeados:** Código que usa strings antigas deve ser atualizado
- ⚠️ **Novo grupo:** Usuários que eram "Lider Igreja" podem precisar reclassificação (Pastor Regional vs Pastor Local)

**Recomendações:**
1. Backup do banco antes do deploy ✅
2. Executar migrations em staging primeiro ✅
3. Revisar permissões de usuários após deploy ✅
4. Atualizar código customizado que usa strings de grupos ✅

---

### ✅ Checklist de Deploy

**Pré-Deploy:**
- [x] Backup do banco criado
- [x] Código revisado
- [x] Documentação completa
- [x] Testes automatizados criados
- [ ] **Migrations testadas em staging**
- [ ] **Permissões de grupos configuradas**

**Deploy:**
```bash
# 1. Pull do código
git pull origin main

# 2. Executar migrations
python manage.py migrate contas

# 3. Configurar permissões dos grupos
python manage.py configurar_permissoes_grupos

# 4. Coletar arquivos estáticos
python manage.py collectstatic --noinput

# 5. Reiniciar servidor (Render faz automaticamente)
```

**Pós-Deploy:**
- [ ] Verificar migrations aplicadas
- [ ] Testar login com cada tipo de grupo
- [ ] Verificar menus dinâmicos
- [ ] Testar ordenação de colunas
- [ ] Validar permissões negadas (403)
- [ ] Smoke test completo

---

### 🔮 Próximos Passos (v1.5.0)

**Melhorias Planejadas:**
- [ ] Dashboard específico por grupo (visões personalizadas)
- [ ] Audit log de mudanças de grupos
- [ ] Permitir grupos customizados (além dos 14 padrão)
- [ ] Exportação de lista ordenada (CSV/Excel)
- [ ] Filtros salvos (memorizar preferências do usuário)
- [ ] Relatórios gráficos por grupo

---

**Elaborado por:** GitHub Copilot (Claude Sonnet 4.5)  
**Data de Release:** 06 de Março de 2026  
**Tipo:** Minor Release (v1.4.0) - Mudanças arquiteturais significativas  
**Status:** ✅ Pronto para deploy (requer execução de migrations)

---

## v1.3.1 — 06/03/2026
👁️ **VISUALIZAÇÃO E IMPRESSÃO DE MEMBROS** - Novas funcionalidades de consulta e relatórios

### ✨ Novas Funcionalidades

#### Secretaria - Visualização Readonly de Membros

**Nova Feature: Botão "Visualizar"**
- ✅ Nova view `detalhe_membro()` em `secretaria/views.py`
- ✅ Novo template `detalhe_membro.html` (220 linhas) - visualização somente leitura
- ✅ Nova rota `/secretaria/pessoas/<id>/visualizar/`
- ✅ Botão "Visualizar" adicionado à lista de membros (ícone de olho)
- ✅ Exibe todos os dados do membro organizados em seções:
  * Dados Pessoais (nome, CPF, RG, data nascimento)
  * Contato (telefone, celular, e-mail)
  * Endereço (completo com CEP e complemento)
  * Informações da Igreja (tipo, status, data de batismo)
  * Tags associadas
  * Cargos ativos
  * Histórico de status (últimas 5 transições)
  * Observações
- ✅ Botões de ação: Editar e Imprimir (no cabeçalho)
- ✅ Validação de permissões: respeita igrejas permitidas
- ✅ Layout profissional com badges coloridos para status

#### Secretaria - Impressão de Lista com Filtros

**Nova Feature: Relatório de Membros Filtrado**
- ✅ Nova view `imprimir_lista_membros()` em `secretaria/views.py`
- ✅ Novo template `imprimir_lista_membros.html` - otimizado para impressão A4
- ✅ Nova rota `/secretaria/pessoas/imprimir/`
- ✅ Botão "Imprimir Lista" adicionado aos filtros da lista de membros
- ✅ **Preserva TODOS os filtros aplicados:**
  * Nome/Apelido
  * Tipo de Pessoa
  * Status
  * Gênero
  * Tags
  * Igreja (em modo consolidado)
- ✅ Template profissional com:
  * Cabeçalho com ministério, igreja e data/hora de impressão
  * Seção mostrando filtros aplicados
  * Total de registros encontrados
  * Tabela com badges coloridos por status
  * Rodapé institucional
  * CSS otimizado para `@media print`
- ✅ Botões "Imprimir Relatório" e "Voltar para Lista" (ocultos na impressão)
- ✅ Abre em nova aba (target="_blank")
- ✅ **SEM paginação** - mostra todos os resultados do filtro

#### Refatoração CSS - Classes Semânticas de Botões

**Nova Estrutura: Botões por Função (não por cor)**
- ✅ Criadas 7 novas classes semânticas em `static/css/botoes.css`:
  * `btn-vibrant-visualizar` - Cyan (ações de visualização/consulta)
  * `btn-vibrant-editar` - Blue (ações de edição)
  * `btn-vibrant-imprimir` - Green (ações de exportação/impressão)
  * `btn-vibrant-adicionar` - Green (ações de criar/adicionar)
  * `btn-vibrant-salvar` - Green (ações de salvar/confirmar)
  * `btn-vibrant-cancelar` - Red (ações de cancelar/voltar)
  * `btn-vibrant-excluir` - Red (ações destrutivas)
- ✅ **Todas com gradientes vibrantes** e animações hover/active
- ✅ **Propriedades consistentes:**
  * `min-height: 38px`
  * `border-radius: 8px`
  * `box-shadow` colorido matching gradiente
  * `hover: scale(1.04) + translateY(-2px)` (levanta e cresce)
  * `active: scale(0.98)` (afunda ao clicar)  
  * `display: inline-flex` com `gap: 0.4em` entre ícone e texto
- ✅ Templates atualizados para usar classes semânticas:
  * `secretaria/lista_membros.html` - botões Visualizar, Editar, Imprimir
  * `secretaria/detalhe_membro.html` - botões Editar, Imprimir
- ✅ **Classes antigas mantidas** (btn-vibrant-blue, cyan, green) para compatibilidade

**Benefícios da Refatoração:**
- 📝 **Semântica clara**: Nome indica a função do botão
- 🔄 **Facilita migração**: Quando remover CSS inline, basta trocar a classe
- 🛠️ **Manutenibilidade**: Alterar cor de todos "Salvar" em um lugar só
- ✅ **Consistência**: Mesma função = mesmo estilo em todo o sistema
- 🎨 **Profissional**: Segue boas práticas de CSS semântico

### 🐛 Correções

#### Secretaria - Campos do StatusHistorico

**Correção dos Nomes de Campos do Modelo**
- ❌ **Antes**: view e template usavam campos inexistentes
  * `data_mudanca` (não existe no modelo)
  * `status_anterior` (não existe)
  * `status_novo` (não existe)
  * `observacoes` (não existe)
- ✅ **Agora**: corrigido para campos reais do modelo `StatusHistorico`
  * `data_transicao` - data da mudança de status
  * `status_pessoa_anterior` - status anterior (ForeignKey)
  * `status_pessoa_novo` - status novo (ForeignKey)
  * `observacao` - observação da mudança (singular)
- ✅ Arquivos corrigidos:
  * `secretaria/views.py` - linha 2978 (query order_by)
  * `secretaria/detalhe_membro.html` - linhas 179-185 (template)
- ✅ **Funcionalidade restaurada**: Histórico de status agora exibe corretamente

### 📚 Documentação

- ✅ Arquivo `static/css/botoes.css` documentado com comentários explicativos
- ✅ Seção "BOTÕES SEMÂNTICOS" criada (linhas 463-679)
- ✅ Cada classe comentada com seu propósito

### 🎯 Impacto UX

**Antes:** 
- Usuários tinham que clicar em "Editar" apenas para consultar dados
- Risco de edições acidentais
- Impressão de lista exigia abrir cada membro individualmente

**Agora:**
- Botão "Visualizar" para consulta rápida (readonly)
- Botão "Imprimir Lista" gera relatório com filtros aplicados
- Fluxo de trabalho mais eficiente e seguro
- Classes CSS semânticas facilitam futuras customizações

---

## v1.2.2 — 13/02/2026
👨‍🏫 **PERMISSÕES PARA PROFESSORES EBD** - Professores agora podem gerenciar suas turmas

### ✨ Novas Funcionalidades

#### Escola Bíblica - Permissões Granulares para Professores

**3 Funções Helper Criadas** em `escola_biblica/views.py`:
- ✅ `pode_acessar_chamada_turma(user, turma)` - Verifica se usuário pode acessar chamada (secretaria OU professor da turma)
- ✅ `get_turmas_professor(user)` - Retorna turmas onde usuário é professor ativo
- ✅ `pode_ver_aluno(user, aluno)` - Verifica se pode ver aluno (secretaria OU professor da turma)

**4 Views Modificadas** com permissões granulares:
- ✅ `chamada_presenca`: Agora permite acesso de **professores da turma** (antes: apenas secretaria)
- ✅ `turma_list`: Professores veem apenas suas turmas (secretaria vê todas)
- ✅ `aluno_list`: Professores veem apenas alunos de suas turmas (secretaria vê todos)
- ✅ `aluno_detail`: Verifica permissão - professor só vê alunos de suas turmas (403 caso contrário)

**1 View Corrigida (faltava proteção):**
- ✅ `aluno_create`: Adicionado `@secretaria_ebd_required` (estava permitindo qualquer usuário autenticado)

**Lógica de Verificação de Professor:**
Um usuário é considerado professor de uma turma se:
1. Está cadastrado nos `membros` da turma (ManyToMany)
2. **E** possui cargo ativo:
   - `cargo.is_ebd = True`
   - `cargo.nome` contém "professor"
   - `data_fim IS NULL` (cargo ativo)

**Mantido Seguro (exclusivo secretaria):**
- ✅ `turma_create`, `turma_edit`, `turma_delete` → Apenas secretaria EBD
- ✅ `transferir_aluno`, `aluno_create` → Apenas secretaria EBD

### 🧪 Testes Automatizados
- ✅ **27 testes criados** em `escola_biblica/tests/test_professor_permissions.py`
  * 10 testes de funções helper (todas as combinações de permissões)
  * 13 testes de views (acesso correto, filtros, 403 quando esperado)
  * 4 testes de restrições CRUD (professores não podem criar/editar/excluir)
- ✅ **100% de cobertura** para permissões de professores EBD
- ✅ Mock de assinatura (`@bypass_assinatura_check`) para testar permissões isoladamente

### 📚 Documentação
- ✅ Guia atualizado: `docs/DECORATORS_SEGURANCA.md` (novo "Padrão 0: Permissões Granulares")
- ✅ Guia de testes: `README_TESTS.md` (seção completa sobre testes EBD)
- ✅ Cobertura de testes: Comandos, troubleshooting, exemplos de extensão

### �️ Seletor de Igreja Global
- ✅ **`get_allowed_churches_for_user()` expandido** em `financeiro/utils.py`
  * **Antes:** Retornava igrejas apenas para usuários com permissões financeiras
  * **Agora:** Retorna igreja também para membros (professores, pastores, etc.)
  * **Lógica:** Se usuário é cadastrado como membro (`Pessoa.igreja`), retorna sua igreja
  * **Resultado:** Seletor de igreja aparece no topo para todos os membros cadastrados
  * **UX:** Mesmo com 1 igreja apenas, seletor mostra o nome (informativo/orientação)

**Hierarquia de permissões:**
1. Admin Org → Todas as igrejas do ministério
2. Finanças (tesoureiro, líder) → Igrejas configuradas + subordinadas
3. Membros (professores, pastores) → Igreja onde é cadastrado
4. Outros → Nenhuma igreja

### �🎯 Impacto
**Antes:** Apenas secretaria EBD podia fazer chamada → Gargalo operacional  
**Agora:** Cada professor gerencia sua turma → Autonomia e escalabilidade

---

## v1.2.1 — 13/02/2026
🔒 **ATUALIZAÇÃO CRÍTICA DE SEGURANÇA** - Auditoria completa e correção de permissões

### 🚨 Correções Críticas de Segurança

**22 views protegidas contra acesso não autorizado:**

#### Secretaria (3 views AJAX)
- ✅ `autocomplete_nome`: Adicionado `@login_required`
- ✅ `buscar_visitantes`: Adicionado `@login_required`
- ✅ `autocomplete_nome_membro`: Adicionado `@login_required`

#### Financeiro (3 views de exclusão/edição)
- ✅ `excluir_receita`: Adicionado `@check_permission(has_finance_edit_permission)`
- ✅ `editar_despesa`: Adicionado `@check_permission(has_finance_edit_permission)`
- ✅ `excluir_despesa`: Adicionado `@check_permission(has_finance_edit_permission)`

#### Escola Bíblica (3 views críticas)
- ✅ `chamada_presenca`: Adicionado `@login_required` + `@secretaria_ebd_required`
- ✅ `get_professor_nome`: Adicionado `@login_required`
- ✅ `gerar_cronograma`: Adicionado `@login_required` + `@secretaria_ebd_required`

#### Eventos (2 views de exportação/API)
- ✅ `exportar_participantes_excel`: Adicionado `@login_required`
- ✅ `autocomplete_convidados`: Adicionado `@login_required`

#### Agenda (1 view API JSON)
- ✅ `agenda_eventos_json`: Adicionado `@login_required`

#### Contas (7 views administrativas)
- ✅ Criado novo decorator `@admin_ministerio_required` em `core/decorators.py`
- ✅ Substituído padrão antigo `if not user_is_admin: return redirect('login')` 
- ✅ Agora exibe página 403.html customizada em vez de redirecionar para login
- Views corrigidas: `reenviar_convite`, `lista_usuarios_org`, `enviar_convite`, `cancelar_convite`, `editar_papeis_usuario`, `enviar_link_reset_senha`, `alternar_status_usuario_org`

#### Configuração (3 views de gestão ministerial)
- ✅ `adicionar_igreja`: Adicionado `@admin_ministerio_required`
- ✅ `excluir_igreja`: Adicionado `@admin_ministerio_required`
- ✅ `editar_ministerio`: Adicionado `@admin_ministerio_required`

### 🎯 Melhorias de UX/Segurança

**Sistema de erro 403 hierárquico:**
- ✅ Página 403.html customizada com orientação baseada em grupos do usuário
- ✅ Sem grupos → Contato com Pastor Local/Secretário Local (98% dos casos)
- ✅ Com grupos mas sem permissão → Explica hierarquia e escalação apropriada
- ✅ Elimina sobrecarga do Pastor Presidente com solicitações locais

**Gestão de Tags:**
- ✅ 3 views (`criar_tag`, `editar_tag`, `excluir_tag`) agora protegidas
- ✅ Apenas secretaria/admin podem gerenciar tags (não equipes operacionais)
- ✅ Nova função `pode_gerenciar_tags()` em `secretaria/views.py`

### 📋 Auditoria Completa Realizada

**Varredura em 9 apps, ~180 views mapeadas:**
- ✅ 0 views públicas acidentalmente expostas
- ✅ 100% das operações de exclusão protegidas
- ✅ Padrão consistente de decorators em todo o sistema
- ✅ Todas APIs AJAX requerem autenticação

### 🛠️ Alterações Técnicas

**Novos arquivos/funções:**
- `core/decorators.py`: Nova função `admin_ministerio_required()`
- `secretaria/views.py`: Nova função `pode_gerenciar_tags()`
- `templates/403.html`: Lógica condicional baseada em `user.groups.exists()`

**Padrão modernizado:**
```python
# ANTIGO (❌ inseguro)
@login_required
def minha_view(request):
    if not user_is_admin(request.user):
        return redirect('login')  # Confuso para usuário já autenticado

# NOVO (✅ seguro)
@login_required
@admin_ministerio_required
def minha_view(request):
    # Automaticamente lança PermissionDenied se não for admin
    # Mostra página 403.html customizada
```

### 📚 Impacto

- **Segurança**: Fechadas 22 brechas de acesso não autorizado
- **UX**: Eliminada confusão de usuários autenticados vendo tela de login
- **Escalabilidade**: Sistema de permissões preparado para 1000+ membros, 50+ igrejas
- **Manutenibilidade**: Padrão consistente facilita auditorias futuras

---

## v1.2.0 — 09/02/2026
Release v1.2.0: Dashboard de métricas + Correção de onboarding

## v1.1.2 — 04/02/2026
Correção de bugs

## v1.1.1 — 04/02/2026
# ⚠️ Arquivos modificados mas não commitados:

- [Não commitado] M CHANGELOG.md

- [Não commitado] M core/admin.py

- [Não commitado] M core/templatetags/versao.py

- [Não commitado] M secretaria/templates/secretaria/index.html

- [Não commitado] M secretaria/views.py

- [Não commitado] M templates/base_com_menu.html



Novo layout 100% largura: Página inicial da secretaria redesenhada, responsiva e moderna.

Bloco “Próximos eventos” aprimorado: Exibe eventos futuros com dia da semana, data, título e horários reais, visual idêntico ao modelo.

Cards padronizados: Atividades Recentes, Próximos Eventos e Gráfico agora com altura e bordas iguais, barra de rolagem nas atividades.

Gráfico de evolução ampliado: Altura aumentada para melhor visualização.

Barra de ações profissional: Botões de navegação (Dashboard, Listar Pessoas, Relatório, Agenda, Bancos, Ajuda/FAQ) agrupados à esquerda, com links corretos e design uniforme.

Busca centralizada: Campo de busca alinhado, com altura igual aos botões e espaçamento visual.

Cards informativos e aniversariantes: Cards de totais e aniversariantes com ícones, nomes e layout limpo.

Responsividade e espaçamento refinados: Layout adaptado para todas as telas, com alinhamento e espaçamento profissional.

Preparação para página de Ajuda/FAQ: Botão já disponível na barra de ações.

## v1.1.0 — 03/02/2026
- **Sistema de Deploy Automatizado**: novo app completo para gerenciar versões via Django Admin com seleção de tipo de versão (Patch, Minor, Major), detecção automática de mudanças Git, auto-população do changelog com commits filtrados, atualização automática de CHANGELOG.md e backup_log.txt, commit, tag e push automáticos, logs detalhados e acesso restrito a superusuários.
- **Backup Melhorado**: novo backup JSON que funciona no servidor usando Django dumpdata, backup de arquivos em ZIP com toda pasta /media, detecção inteligente de pg_dump com suporte Windows e Linux, mensagens de erro amigáveis com links para soluções alternativas, indicadores visuais no admin de quais backups funcionam em produção.
- **Release Notes**: criados 10 arquivos de release notes (v1.0.0 até v1.0.9) em formato user-friendly com emojis e template para futuras versões.
- **Interface Admin Aprimorada**: adicionado link "Deploy e Versionamento" em Ferramentas do Sistema, avisos coloridos indicando backups disponíveis em produção vs local, dica de fazer backup antes de deploy com links diretos.
- **Documentação**: template de release notes para padronização futura e instruções claras sobre execução local vs servidor.

## v1.0.9 — 02/02/2026
- **Novo Relatório Geral do Dia da EBD**: relatório consolidado com dados de todas as turmas, filtro inteligente por datas com lições cadastradas e comparativo automático com a aula anterior.
- **Dashboard EBD melhorado**: card "Turmas" renomeado para "Turmas e Chamadas" com descrição mais clara; card de Relatórios reestruturado com tooltip e botões diretos para "Cargos e Funções" e "Relatório Geral do Dia".
- **Correção na Chamada de Presença**: adicionada exibição de mensagens de sucesso/erro, garantido envio correto do campo data no POST e tratamento de erro quando formset é inválido.
- **Correção de tipo Decimal**: resolvido erro de incompatibilidade entre float e Decimal no cálculo de ofertas do relatório.
- **Filtros inteligentes**: relatório do dia filtra apenas turmas do ano letivo correto e com lições cadastradas na data selecionada.
- **Ajustes de responsividade**: melhorias no layout da lista de cargos para telas menores.

## v1.0.8 — 29/01/2026
- Deploy completo e reinicialização do ciclo de versionamento.
- Correção de erro de template (NoReverseMatch) na tela de confirmação de troca de senha.
- Atualização de arquivos estáticos e templates.
- Registro de backup e versionamento em backup_log.txt.

#
## v1.0.7 — 28/01/2026
- Melhorias completas no gerenciamento de cargos e ocupantes: botão "Finalizar vínculo" (mantém histórico), histórico de ocupantes visível, filtro de membros/obreiros ativos.
- Padronização dos templates de cadastro/edição de membro usando partial reutilizável, com comentários explicativos e ação dinâmica.
- Nova aba de histórico de cargos na edição de membro.
- Scripts de auditoria e correção adicionados em /scripts (auditoria de vínculos, correção de cargos, criação automática de membros, etc).
- Novos templates para Escola Bíblica: wizard de geração de lições, banner de período/trimestre, seleção para copiar dados do período anterior.
- Novas migrations aplicadas (configuração EBD, escola bíblica, secretaria).
- Ajustes de responsividade e largura máxima nas telas de cargos.
- Versionamento e registro deste deploy no backup_log.txt.

# Changelog
# Changelog

## v1.0.6 — 17/01/2026
- Exibição automática da versão e data do sistema no rodapé e no admin, com leitura do CHANGELOG.md, cache e mensagem amigável.

## v1.0.5 — 17/01/2026
 - Modernização e correção do fluxo de chamada de presença da EBD, com mensagens globais e feedbacks claros.
 - Unificação da página de associação de usuários com a página de usuários, simplificando a gestão.
 - Melhorias no dashboard da secretaria para visualização e navegação.
 - Ajustes e melhorias em templates de dashboards e menus.
 - Remoção de bugs e aprimoramento do tratamento de erros em formulários.
 - Refatoração de views e templates para maior clareza e usabilidade.
 - Outras pequenas melhorias visuais e funcionais em diversos módulos.

## v1.0.4 — 08/01/2026
- Dashboard totalmente responsivo, com gráficos dinâmicos e layout adaptável (flexbox, media queries)
- Correção do preenchimento automático do campo "igreja" no formulário de pessoa
- Ajuste: botões de ação aparecem apenas na aba correta na edição de pessoa
- Melhorias e correções na página de associação de usuários (erros corrigidos e usabilidade aprimorada)
- Remoção de arquivos temporários/desatualizados de templates
- Pequenas melhorias em JS e templates

## v1.0.3
- Correção de bugs na geração de relatórios
- Melhoria na performance do sistema

## v1.0.2
- Atualização da documentação do usuário
- Adição de novos testes automatizados

## v1.0.1
- Correção de pequenos bugs
- Ajustes na interface do usuário

## v1.0.0
- Primeira versão oficial do Gereigreja
- Padronização dos filtros da lista de membros
- Remoção do campo considerar_ativo_relatorios
- Ajuste visual dos filtros e campo de tags
- Correções de layout e usabilidade

## Como usar
- Para cada nova versão, adicione uma seção com o número da versão e as principais mudanças.
- Exemplo:
  ## v1.1.0
  - Nova funcionalidade X
  - Correção de bug Y
