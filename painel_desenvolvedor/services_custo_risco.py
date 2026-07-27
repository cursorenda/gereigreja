from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from typing import Any

import requests
from django.conf import settings
from django.core.cache import cache


def to_decimal(value: Any) -> Decimal:
    if value in (None, ''):
        return Decimal('0.00')
    return Decimal(str(value))


def buscar_cotacao_usd_brl() -> dict[str, Any]:
    """Busca cotação USD->BRL automaticamente com cache curto.

    Retorna dict com:
      rate: Decimal | None
      source: str | None
      fetched_at: str | None
    """
    cache_key = 'painel_risco_usd_brl_rate_v1'
    cached = cache.get(cache_key)
    if cached:
        return cached

    providers = [
        {
            'source': 'awesomeapi',
            'url': 'https://economia.awesomeapi.com.br/json/last/USD-BRL',
            'parser': lambda body: (
                to_decimal((body.get('USDBRL') or {}).get('bid')),
                (body.get('USDBRL') or {}).get('create_date'),
            ),
        },
        {
            'source': 'open-er-api',
            'url': 'https://open.er-api.com/v6/latest/USD',
            'parser': lambda body: (
                to_decimal((body.get('rates') or {}).get('BRL')),
                body.get('time_last_update_utc'),
            ),
        },
    ]

    for provider in providers:
        try:
            response = requests.get(provider['url'], timeout=6)
            if response.status_code != 200:
                continue
            body = response.json()
            rate, fetched_at = provider['parser'](body)
            if rate > 0:
                result = {
                    'rate': rate,
                    'source': provider['source'],
                    'fetched_at': fetched_at,
                }
                cache.set(cache_key, result, 3600)
                return result
        except Exception:
            continue

    return {
        'rate': None,
        'source': None,
        'fetched_at': None,
    }


def converter_usd_para_brl(valor_usd: Decimal | None, cotacao: Decimal | None) -> Decimal | None:
    """Converte valor em USD para BRL usando a cotação informada."""
    if valor_usd is None or cotacao is None:
        return None
    if cotacao <= 0:
        return None
    return to_decimal(valor_usd) * to_decimal(cotacao)


def calcular_risco_custo_whatsapp(custo_mensal, receita_mensal, margem) -> dict[str, Decimal | str]:
    """Calcula risco conservador para custo WhatsApp em relação à receita."""
    margem_valor = to_decimal(margem)
    custo_valor = to_decimal(custo_mensal)
    receita_valor = to_decimal(receita_mensal)

    percentual_custo_receita = Decimal('0.00')
    nivel = 'baixo'

    if receita_valor <= 0 and custo_valor <= 0:
        return {
            'margem': margem_valor,
            'custo_mensal': custo_valor,
            'receita_mensal': receita_valor,
            'percentual_custo_receita': percentual_custo_receita,
            'nivel': 'indefinido',
        }

    if receita_valor <= 0 and custo_valor > 0:
        return {
            'margem': margem_valor,
            'custo_mensal': custo_valor,
            'receita_mensal': receita_valor,
            'percentual_custo_receita': Decimal('1.00'),
            'nivel': 'alto',
        }

    if receita_valor > 0:
        percentual_custo_receita = custo_valor / receita_valor

    if margem_valor < Decimal('0.40') or percentual_custo_receita >= Decimal('0.25'):
        nivel = 'alto'
    elif margem_valor < Decimal('0.60'):
        nivel = 'medio'

    return {
        'margem': margem_valor,
        'custo_mensal': custo_valor,
        'receita_mensal': receita_valor,
        'percentual_custo_receita': percentual_custo_receita,
        'nivel': nivel,
    }


def railway_config() -> dict[str, str]:
    """Retorna configuração Railway para métricas de custo."""
    token = (
        getattr(settings, 'RAILWAY_API_TOKEN', '')
        or getattr(settings, 'RAILWAY_TOKEN', '')
    )
    project_id = (
        getattr(settings, 'RAILWAY_PROJECT_ID', '')
        or getattr(settings, 'RAILWAY_PROJECT', '')
    )
    service_id = (
        getattr(settings, 'RAILWAY_WAHA_SERVICE_ID', '')
        or getattr(settings, 'RAILWAY_SERVICE_ID', '')
    )
    workspace_id = getattr(settings, 'RAILWAY_WORKSPACE_ID', '')

    return {
        'token': token,
        'project_id': project_id,
        'service_id': service_id,
        'workspace_id': workspace_id,
        # Endpoint oficial da API pública Railway (v2).
        'api_url': getattr(settings, 'RAILWAY_API_URL', 'https://backboard.railway.com/graphql/v2'),
    }


def _workspace_id_from_token(api_url: str, token: str) -> str:
    """Resolve workspace id from bearer token when not explicitly configured."""
    headers = {'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'}
    try:
        r_me = requests.post(
            api_url,
            headers=headers,
            json={'query': '{ me { workspaces { id } } }'},
            timeout=10,
        )
        if r_me.status_code != 200:
            return ''
        body_me = r_me.json()
        workspaces = ((body_me.get('data') or {}).get('me', {}).get('workspaces') or [])
        if not workspaces:
            return ''
        return workspaces[0].get('id', '') or ''
    except Exception:
        return ''


def _periodo_fechamento_workspace(api_url: str, token: str, workspace_id: str) -> str | None:
    """Returns the workspace billing period end in ISO format, when available."""
    if not workspace_id:
        return None

    headers = {'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'}
    payload = {
        'query': '''
        query WorkspacePeriod($wsId: String!) {
          workspace(workspaceId: $wsId) {
            customer {
              invoices {
                periodEnd
              }
            }
          }
        }
        ''',
        'variables': {'wsId': workspace_id},
    }
    try:
        r = requests.post(api_url, headers=headers, json=payload, timeout=12)
        if r.status_code != 200:
            return None
        body = r.json()
        if body.get('errors'):
            return None
        invoices = (
            ((body.get('data') or {}).get('workspace') or {})
            .get('customer', {})
            .get('invoices')
            or []
        )
        if not invoices:
            return None

        valid_dates = [inv.get('periodEnd') for inv in invoices if inv.get('periodEnd')]
        if not valid_dates:
            return None
        return max(valid_dates)
    except Exception:
        return None


def formatar_data_iso_ptbr(iso_date: str | None) -> str | None:
    """Converte data ISO para dd/mm/aaaa (pt-BR)."""
    if not iso_date:
        return None
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y')
    except Exception:
        return None


def parse_iso_datetime(iso_date: str | None) -> datetime | None:
    """Converte string ISO para datetime aware quando possível."""
    if not iso_date:
        return None
    try:
        return datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
    except Exception:
        return None


def _workspace_customer_usage(api_url: str, token: str, workspace_id: str) -> dict[str, Any] | None:
    """Retorna currentUsage e faturas do workspace Railway."""
    if not workspace_id:
        return None

    headers = {'Authorization': f"Bearer {token}", 'Content-Type': 'application/json'}
    payload = {
        'query': '''
        query WorkspaceUsage($wsId: String!) {
          workspace(workspaceId: $wsId) {
            customer {
              currentUsage
              invoices {
                invoiceId
                total
                periodStart
                periodEnd
                status
              }
            }
          }
        }
        ''',
        'variables': {'wsId': workspace_id},
    }
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=12)
        if response.status_code != 200:
            return None
        body = response.json()
        if body.get('errors'):
            return None
        return ((body.get('data') or {}).get('workspace') or {}).get('customer')
    except Exception:
        return None


def listar_ciclos_custo_railway() -> list[dict[str, Any]]:
    """Lista ciclos de custo Railway: atual em aberto + faturas anteriores."""
    cfg = railway_config()
    if not cfg['token']:
        return []

    api_url = cfg['api_url'] or 'https://backboard.railway.com/graphql/v2'
    workspace_id = (cfg.get('workspace_id') or '').strip()
    if not workspace_id:
        workspace_id = _workspace_id_from_token(api_url, cfg['token'])
    if not workspace_id:
        return []

    customer = _workspace_customer_usage(api_url, cfg['token'], workspace_id)
    if not customer:
        return []

    cycles: list[dict[str, Any]] = []
    invoices = customer.get('invoices') or []
    invoices_sorted = sorted(
        invoices,
        key=lambda inv: inv.get('periodEnd') or '',
        reverse=True,
    )

    invoices_non_zero = [inv for inv in invoices_sorted if to_decimal(inv.get('total', 0)) > 0]
    latest_period_end = (
        (invoices_non_zero[0].get('periodEnd') if invoices_non_zero else None)
        or (invoices_sorted[0].get('periodEnd') if invoices_sorted else None)
    )
    current_usage = customer.get('currentUsage')
    if current_usage is not None:
        hoje_pt = datetime.now().strftime('%d/%m/%Y')
        inicio_pt = formatar_data_iso_ptbr(latest_period_end) or 'Início do ciclo'
        cycles.append({
            'key': 'current',
            'label': 'Atual (em aberto)',
            'custo': to_decimal(current_usage),
            'period_start': latest_period_end,
            'period_end': None,
            'period_label': f"{inicio_pt} a {hoje_pt}",
            'status': 'open',
        })

    seen_labels: set[str] = set()
    for inv in invoices_non_zero:
        invoice_id = inv.get('invoiceId')
        if not invoice_id:
            continue
        total_cents = inv.get('total')
        custo = to_decimal(total_cents) / Decimal('100') if total_cents is not None else Decimal('0.00')
        start_iso = inv.get('periodStart')
        end_iso = inv.get('periodEnd')
        start_pt = formatar_data_iso_ptbr(start_iso) or 'N/D'
        end_pt = formatar_data_iso_ptbr(end_iso) or 'N/D'
        periodo_label = f"{start_pt} a {end_pt}"
        status = inv.get('status') or 'unknown'
        unique_label = f"{periodo_label}|{custo}|{status}"
        if unique_label in seen_labels:
            continue
        seen_labels.add(unique_label)

        cycles.append({
            'key': f"invoice:{invoice_id}",
            'label': f"{periodo_label} ({status})",
            'custo': custo,
            'period_start': start_iso,
            'period_end': end_iso,
            'period_label': periodo_label,
            'status': status,
        })

    return cycles


def missing_railway_keys() -> list[str]:
    cfg = railway_config()
    missing: list[str] = []
    if not cfg['token']:
        missing.append('RAILWAY_API_TOKEN')
    if not cfg['project_id']:
        missing.append('RAILWAY_PROJECT_ID')
    if not cfg['service_id']:
        missing.append('RAILWAY_WAHA_SERVICE_ID')
    return missing


def buscar_custo_agentusage_railway() -> Decimal | None:
    """Busca custo monetário real da Railway para o workspace/projeto.

    Fonte principal: workspace.customer.currentUsage (em dólares), que é o
    valor monetário mostrado no painel de uso por projeto/workspace.

    Fallback: agentUsage.totalUsedCents (consumo do agente) apenas quando
    currentUsage não estiver acessível.
    """
    cfg = railway_config()
    if not cfg['token']:
        return None

    api_url = cfg['api_url'] or 'https://backboard.railway.com/graphql/v2'
    h = {'Authorization': f"Bearer {cfg['token']}", 'Content-Type': 'application/json'}

    workspace_id = cfg.get('workspace_id', '').strip()

    if not workspace_id:
        workspace_id = _workspace_id_from_token(api_url, cfg['token'])

    if not workspace_id:
        return None

    try:
        # 1) Caminho monetário principal (bate com os valores do painel Railway).
        payload_current_usage = {
            'query': '''
            query WorkspaceCurrentUsage($wsId: String!) {
              workspace(workspaceId: $wsId) {
                customer {
                  currentUsage
                }
              }
            }
            ''',
            'variables': {'wsId': workspace_id},
        }
        r_current = requests.post(api_url, headers=h, json=payload_current_usage, timeout=12)
        if r_current.status_code == 200:
            body_current = r_current.json()
            if not body_current.get('errors'):
                current_usage = (
                    (body_current.get('data') or {})
                    .get('workspace', {})
                    .get('customer', {})
                    .get('currentUsage')
                )
                if current_usage is not None:
                    return to_decimal(current_usage)

        # 2) Fallback técnico (limite/consumo de agente, não custo total do projeto).
        payload_agent_usage = {
            'query': '''
            query AgentUsage($wsId: String!) {
              agentUsage(workspaceId: $wsId) {
                totalUsedCents
                hardLimitCents
                billingPeriodEnd
              }
            }
            ''',
            'variables': {'wsId': workspace_id},
        }
        r = requests.post(api_url, headers=h, json=payload_agent_usage, timeout=12)
        if r.status_code != 200:
            return None
        body = r.json()
        if body.get('errors'):
            return None
        cents = (body.get('data') or {}).get('agentUsage', {}).get('totalUsedCents')
        if cents is None:
            return None
        return to_decimal(cents) / Decimal('100')
    except Exception:
        return None


def buscar_periodo_fechamento_railway() -> str | None:
    """Retorna o fechamento do período de cobrança (ISO), quando disponível."""
    cfg = railway_config()
    if not cfg['token']:
        return None

    api_url = cfg['api_url'] or 'https://backboard.railway.com/graphql/v2'
    workspace_id = (cfg.get('workspace_id') or '').strip()
    if not workspace_id:
        workspace_id = _workspace_id_from_token(api_url, cfg['token'])
    if not workspace_id:
        return None
    return _periodo_fechamento_workspace(api_url, cfg['token'], workspace_id)


def buscar_custos_railway() -> list[dict[str, Any]]:
    """Busca snapshot de custo mensal da Railway para o serviço WAHA."""
    cfg = railway_config()
    if not cfg['token'] or not cfg['project_id'] or not cfg['service_id']:
        return []

    api_url = cfg['api_url'] or 'https://backboard.railway.com/graphql/v2'
    if api_url.endswith('/graphql'):
        api_url = f"{api_url}/v2"

    payload = {
        'query': '''
        query ProjectUsage($projectId: String!, $serviceId: String!) {
          project(id: $projectId) {
            services(id: $serviceId) {
              metrics {
                month {
                  cost
                  usage {
                    total
                  }
                }
              }
            }
          }
        }
        ''',
        'variables': {
            'projectId': cfg['project_id'],
            'serviceId': cfg['service_id'],
        },
    }
    header_variants = [
        {
            'Authorization': f"Bearer {cfg['token']}",
            'Content-Type': 'application/json',
        },
        {
            'Project-Access-Token': cfg['token'],
            'Content-Type': 'application/json',
        },
    ]

    try:
        for headers in header_variants:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=12,
            )
            if response.status_code >= 500:
                continue

            try:
                body = response.json()
            except Exception:
                continue

            services = body.get('data', {}).get('project', {}).get('services', [])
            if isinstance(services, list):
                return services

        return []
    except Exception:
        return []


def buscar_uso_estimado_railway() -> list[dict[str, Any]]:
    """Busca uso estimado do projeto na Railway v2 (disponível com project token).

    Retorna a lista de medidas estimadas quando o custo monetário direto não está
    acessível pelo token atual. Útil para manter o status 'info' no painel em vez
    de 'warn' (fallback), sinalizando que a integração está ativa mas com escopo
    limitado.
    """
    cfg = railway_config()
    if not cfg['token'] or not cfg['project_id']:
        return []

    payload = {
        'query': '''
        query EstimatedUsage($projectId: String!, $measurements: [MetricMeasurement!]!) {
          estimatedUsage(projectId: $projectId, measurements: $measurements) {
            measurement
            estimatedValue
            projectId
          }
        }
        ''',
        'variables': {
            'projectId': cfg['project_id'],
            'measurements': [
                'CPU_USAGE',
                'MEMORY_USAGE_GB',
                'DISK_USAGE_GB',
                'NETWORK_TX_GB',
                'NETWORK_RX_GB',
            ],
        },
    }

    try:
        api_url = cfg['api_url'] or 'https://backboard.railway.com/graphql/v2'
        if api_url.endswith('/graphql'):
            api_url = f"{api_url}/v2"
        header_variants = [
            {'Authorization': f"Bearer {cfg['token']}", 'Content-Type': 'application/json'},
            {'Project-Access-Token': cfg['token'], 'Content-Type': 'application/json'},
        ]

        for headers in header_variants:
            response = requests.post(api_url, headers=headers, json=payload, timeout=12)
            if response.status_code >= 500:
                continue
            try:
                body = response.json()
            except Exception:
                continue
            usage = body.get('data', {}).get('estimatedUsage', [])
            if isinstance(usage, list):
                return usage
        return []
    except Exception:
        return []


def railway_status(
    custo_total_railway: Decimal | None,
    uso_estimado_railway: list[dict[str, Any]],
) -> dict[str, Any]:
    """Retorna o status mais preciso disponível para a integração Railway.

    Três níveis:
      ok   – custo monetário real disponível (token de account)
      info – custo indisponível mas métricas técnicas acessíveis (token workspace/project)
      warn – integração sem dados (sem token ou fallback)
    """
    if custo_total_railway is not None:
        return {
            'nivel': 'ok',
            'label': 'Custo real',
            'detail': 'Custo mensal retornado pela Railway',
            'uso_estimado': uso_estimado_railway,
            'precisa_account_token': False,
        }
    if uso_estimado_railway:
        medidas = [item.get('measurement', '') for item in uso_estimado_railway]
        return {
            'nivel': 'info',
            'label': 'Uso estimado',
            'detail': (
                f'{len(uso_estimado_railway)} métricas técnicas disponíveis '
                f'({len(medidas)} medições). '
                'Para custo monetário real, use um Account Token da Railway.'
            ),
            'uso_estimado': uso_estimado_railway,
            'precisa_account_token': True,
        }
    return {
        'nivel': 'warn',
        'label': 'Fallback',
        'detail': 'Sem dados Railway disponíveis. Verifique as variáveis de ambiente.',
        'uso_estimado': [],
        'precisa_account_token': True,
    }


def extrair_custo_mensal_railway(custos_railway: list[dict[str, Any]]) -> Decimal | None:
    """Extrai o custo mensal da resposta da Railway em formato Decimal."""
    if not custos_railway:
        return None

    try:
        metrics = custos_railway[0].get('metrics', {})
        month = metrics.get('month', {})
        cost_value = month.get('cost')
        if cost_value in (None, ''):
            return None
        return to_decimal(cost_value)
    except Exception:
        return None


def analisar_risco_whatsapp_assinaturas(
    assinaturas,
    logs_por_ministerio: dict[int, int],
    custo_total_railway: Decimal | None,
) -> dict[str, Any]:
    """Monta análise de risco por ministério com share custo/receita consistente."""
    dados: list[dict[str, Any]] = []
    total_assinaturas = len(assinaturas)
    total_logs_assinaturas = sum(logs_por_ministerio.get(item.ministerio_id, 0) for item in assinaturas)

    rateio_uniforme = Decimal('0.00')
    if custo_total_railway is not None and total_assinaturas > 0 and total_logs_assinaturas == 0:
        rateio_uniforme = custo_total_railway / Decimal(total_assinaturas)

    for assinatura in assinaturas:
        ministerio = assinatura.ministerio
        receita_mensal = Decimal('0.00')
        if assinatura.plano and assinatura.plano.preco_mensal:
            receita_mensal = to_decimal(assinatura.plano.preco_mensal)

        quantidade_logs = int(logs_por_ministerio.get(ministerio.id, 0))

        if custo_total_railway is None:
            custo_mensal = Decimal('0.00')
            custo_origem = 'sem_dados_railway'
        elif total_logs_assinaturas > 0:
            peso = Decimal(quantidade_logs) / Decimal(total_logs_assinaturas)
            custo_mensal = custo_total_railway * peso
            custo_origem = 'railway_rateio_por_logs'
        else:
            custo_mensal = rateio_uniforme
            custo_origem = 'railway_rateio_uniforme'

        margem = Decimal('0.00')
        if receita_mensal > 0:
            margem = (receita_mensal - custo_mensal) / receita_mensal

        risco = calcular_risco_custo_whatsapp(
            custo_mensal=custo_mensal,
            receita_mensal=receita_mensal,
            margem=margem,
        )

        dados.append({
            'ministerio': ministerio,
            'plano': assinatura.plano,
            'receita_mensal': receita_mensal,
            'custo_mensal': custo_mensal,
            'quantidade_logs': quantidade_logs,
            'risco': risco,
            'custo_origem': custo_origem,
        })

    prioridade_risco = {
        'alto': 0,
        'medio': 1,
        'baixo': 2,
        'indefinido': 3,
    }
    dados.sort(
        key=lambda item: (
            prioridade_risco.get(item['risco']['nivel'], 4),
            -item['risco']['percentual_custo_receita'],
            -item['quantidade_logs'],
        )
    )

    resumo = resumir_risco_global(dados)

    if custo_total_railway is None:
        origem = 'fallback_sem_railway'
    elif total_logs_assinaturas > 0:
        origem = 'railway_rateio_por_logs'
    else:
        origem = 'railway_rateio_uniforme'

    return {
        'dados': dados,
        'resumo': resumo,
        'origem_custo': origem,
        'custo_total_railway': custo_total_railway,
        'total_logs_assinaturas': total_logs_assinaturas,
    }


def resumir_risco_global(dados: list[dict[str, Any]]) -> dict[str, Any]:
    """Consolida os riscos por ministério em um resumo executivo consistente."""
    total_custos = sum((item['custo_mensal'] for item in dados), Decimal('0.00'))
    total_receitas = sum((item['receita_mensal'] for item in dados), Decimal('0.00'))
    total_logs = sum((item['quantidade_logs'] for item in dados), 0)

    risco_alto = sum(1 for item in dados if item['risco']['nivel'] == 'alto')
    risco_medio = sum(1 for item in dados if item['risco']['nivel'] == 'medio')
    risco_baixo = sum(1 for item in dados if item['risco']['nivel'] == 'baixo')
    risco_indefinido = sum(1 for item in dados if item['risco']['nivel'] == 'indefinido')

    share_total = Decimal('0.00')
    margem_total = Decimal('0.00')
    if total_receitas > 0:
        share_total = total_custos / total_receitas
        margem_total = (total_receitas - total_custos) / total_receitas

    if risco_alto > 0:
        risco_global = 'alto'
    elif risco_medio > 0:
        risco_global = 'medio'
    elif risco_indefinido > 0:
        risco_global = 'indefinido'
    elif risco_baixo > 0:
        risco_global = 'baixo'
    else:
        risco_global = 'indefinido'

    return {
        'total_custos': total_custos,
        'total_receitas': total_receitas,
        'total_logs': total_logs,
        'share_total': share_total,
        'margem_total': margem_total,
        'risco_global': risco_global,
        'risco_alto': risco_alto,
        'risco_medio': risco_medio,
        'risco_baixo': risco_baixo,
        'risco_indefinido': risco_indefinido,
    }
