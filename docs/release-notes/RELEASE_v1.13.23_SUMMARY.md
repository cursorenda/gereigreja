# RELEASE v1.13.23 - Admin Dev Premium, Funil Reconciliado e Financeiro do Sistema

Data: 22/06/2026

## Resumo Executivo
A release v1.13.23 consolida o painel técnico do produto com três evoluções estratégicas:
- observabilidade profunda de usuários no admin (navegação, IP, timeline);
- reconciliação de faturamento no funil de vendas com base em pagamentos confirmados;
- novo Financeiro do Sistema no Admin Django para gestão de entradas automáticas e gastos manuais do SaaS.

## Entregas Principais

### 1) Auditoria Premium no /admin/
- Painel principal em `/admin/auditoria/painel/`.
- Captura de pageviews por usuário com:
  - path
  - método HTTP
  - status HTTP
  - IP
  - referer
  - duração (ms)
- Timeline por usuário e exportação CSV de navegação.

### 2) Funil Financeiro Reconciliado
- Webhook Stripe robustecido para ausência de assinatura.
- Correção de estado anterior em `customer.subscription.updated`.
- Novo evento `pagamento_confirmado` disparado em `invoice.paid`.
- Dashboard de funil atualizado para:
  - usar pagamentos confirmados como base de receita;
  - reconciliar eventos do funil vs histórico de mensalidades pagas;
  - exibir deltas de consistência.

### 3) Financeiro do Sistema (Admin Dev)
- Nova página: `/admin/financeiro-sistema/`.
- Entradas automáticas via `HistoricoAssinatura` (`tipo=mensalidade`, `status=paga`).
- Gastos manuais com categorias padrão:
  - Hospedagens
  - Domínios
  - IA
  - Outros
- Indicadores executivos:
  - Entradas do mês
  - Gastos do mês
  - Líquido do mês
  - Receita acumulada
  - Resultado acumulado
- Gráfico de 12 meses (Entradas x Gastos x Líquido).

## Segurança e Acesso
- Controle de acesso dev-only no financeiro interno:
  - requer `is_superuser`;
  - whitelist opcional por `.env` em `DEV_FINANCEIRO_USERNAMES`.

## Migrações Aplicadas
- `auditoria/migrations/0003_auditpageview.py`
- `configuracao/migrations/0035_alter_eventofunil_tipo.py`
- `configuracao/migrations/0036_categoriagastosistema_gastosistema.py`

## Validação
- `python manage.py check` executado sem erros.
- `python manage.py migrate` executado com sucesso para os novos schemas.

## Observações Operacionais
- Permanece warning não bloqueante de compatibilidade `requests/urllib3` no ambiente local.
- Sem breaking changes de API pública.
