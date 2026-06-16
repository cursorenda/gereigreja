# RELEASE v1.13.17 - RESUMO EXECUTIVO

Data: 16/06/2026
Tipo: PATCH
Escopo: Centro Ministerial premium, liderança integrada e módulo de igrejas premium

## Resumo
A versão v1.13.17 consolida o Centro Ministerial como hub único de gestão administrativa, com navegação simplificada e painéis premium em Configuração, Secretaria e Financeiro. O pacote também fecha a premiumização do módulo de igrejas, incluindo cadastro, edição e confirmação de exclusão em padrão visual consistente.

## Principais Entregas
- Novo Centro Ministerial em Configuração:
  - rota dedicada para o painel central;
  - KPIs agregados de igrejas, membros, financeiro, eventos e convites;
  - fila de pendências operacionais com atalhos acionáveis.
- Simplificação de menu lateral:
  - seção ministerial consolidada para reduzir caminhos duplicados;
  - acesso direto ao painel central.
- Evolução premium das telas estratégicas:
  - detalhes do ministério (aba dados) em formato executivo;
  - edição do ministério com blocos organizados;
  - painel de liderança da Secretaria premium;
  - painel de liderança do Financeiro premium.
- Fechamento premium do módulo de igrejas:
  - lista de igrejas com coluna de tipo da igreja;
  - formulário de cadastro reorganizado por seções;
  - edição por abas com shell premium;
  - confirmação de exclusão premium.
- Correções de estabilidade no Centro Ministerial:
  - import de convites corrigido para `Convite`;
  - relacionamento de membros por igreja corrigido para `membros`;
  - reverse de URL ajustado para rota existente no app Contas.

## Arquivos Impactados
- Alterados:
  - `configuracao/forms.py`
  - `configuracao/models.py`
  - `configuracao/templates/configuracao/configuracoes_sistema.html`
  - `configuracao/templates/configuracao/igrejas/confirmar_excluir_igreja.html`
  - `configuracao/templates/configuracao/igrejas/editar_igreja_config.html`
  - `configuracao/templates/configuracao/igrejas/form_igreja.html`
  - `configuracao/templates/configuracao/igrejas/lista_igrejas.html`
  - `configuracao/templates/configuracao/ministerio/detalhes_ministerio.html`
  - `configuracao/templates/configuracao/ministerio/form_ministerio.html`
  - `configuracao/urls.py`
  - `configuracao/views.py`
  - `financeiro/templates/financeiro/painel_lideranca_financeiro.html`
  - `secretaria/templates/secretaria/painel_lideranca_secretaria.html`
  - `secretaria/urls.py`
  - `secretaria/views/__init__.py`
  - `templates/menu.html`
- Novos:
  - `configuracao/migrations/0029_ministerio_logo_grande_and_more.py`
  - `configuracao/migrations/0030_ministerio_carteirinha_permitir_secretaria_local.py`
  - `configuracao/templates/configuracao/ministerio/carteirinha_ministerio_editor.html`
  - `configuracao/templates/configuracao/ministerio/centro_ministerial.html`
  - `secretaria/templates/secretaria/documentos/carteirinha/` (arquivos de template)
  - `secretaria/views/carteirinha.py`

## Migrações
- `configuracao/migrations/0029_ministerio_logo_grande_and_more.py`
- `configuracao/migrations/0030_ministerio_carteirinha_permitir_secretaria_local.py`

## Validação
- `python manage.py check` executado com sucesso (0 issues).

## Impacto para o Usuário
- Visão central do ministério mais clara e acionável.
- Menos ruído no menu e maior previsibilidade de navegação.
- Experiência premium consistente nas telas de liderança e configuração.

## Impacto Técnico
- Evolução funcional com ajustes de estabilidade no domínio de convites/URLs/ORM.
- Mudança de schema controlada via duas migrações novas.
- Sem breaking changes de API pública.
