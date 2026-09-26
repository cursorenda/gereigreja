"""
Context processor unificado para status da assinatura e limites do plano.
Centraliza toda a lógica de alertas em um único ponto.
Evita import circular ao fazer inline a extração do ministério.
"""
import logging
from django.urls import reverse
from django.http import Http404

logger = logging.getLogger(__name__)


def status_plano_unificado(request):
    """
    Avalia o status da assinatura e limites do plano do ministério.
    Retorna um dict com prioridade: crítico (vencido) > aviso (100%) > atenção (80%).
    
    Retorna:
        - {'status_plano': None} se OK ou usuário não autenticado
        - {'status_plano': dict} com: nivel, tipo, mensagem, cta_url, cta_texto, percentual, restante
    """
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'status_plano': None}

    if request.user.is_superuser:
        return {'status_plano': None}

    try:
        from configuracao.models import LiberacaoPlanoMinisterio
        from configuracao.services_assinatura import (
            assinatura_esta_regular,
            assinatura_em_graca_inadimplencia,
            dias_restantes_graca,
            dias_restantes_trial,
            contar_pessoas_ativas,
            is_trial_ativo,
            obter_assinatura_ministerio,
            obter_ministerio_do_usuario,
            obter_plano_efetivo_ministerio,
            obter_limite_pessoas_ativas,
        )

        ministerio = obter_ministerio_do_usuario(request.user)

        if not ministerio or not ministerio.ativo:
            # Ministério inativo ou não encontrado - sem status a mostrar
            return {'status_plano': None}

        if ministerio.is_demo:
            return {'status_plano': None}

        # --- PRIORITARIO: Assinatura vencida/irregular ---
        assinatura = obter_assinatura_ministerio(ministerio)
        liberacao_beta_ativa = LiberacaoPlanoMinisterio.objects.filter(
            ministerio=ministerio,
            ativo=True,
            acesso_beta=True,
            pode_visualizar=True,
        ).exists()

        if not assinatura_esta_regular(assinatura, ministerio) and not liberacao_beta_ativa:
            url_regularizar = reverse('configuracao:gerenciar_assinatura') + '#secao-planos'
            if assinatura is None:
                return {
                    'status_plano': {
                        'nivel': 'critico',
                        'tipo': 'sem_assinatura',
                        'mensagem': 'Seu ministério não possui uma assinatura ativa. Por favor, escolha um plano ou ative sua cortesia.',
                        'cta_url': url_regularizar,
                        'cta_texto': 'Escolher plano',
                        'icon': 'fas fa-exclamation-triangle',
                    }
                }
            else:
                if assinatura.trial_ativo and not is_trial_ativo(assinatura):
                    return {
                        'status_plano': {
                            'nivel': 'critico',
                            'tipo': 'trial_expirado',
                            'mensagem': 'Seu período de teste de 14 dias expirou. Escolha um plano para continuar usando todos os recursos.',
                            'cta_url': url_regularizar,
                            'cta_texto': 'Escolher plano',
                            'icon': 'fas fa-hourglass-end',
                        }
                    }

                plano_efetivo = obter_plano_efetivo_ministerio(ministerio)
                plano_nome = plano_efetivo.get_nome_display() if plano_efetivo else 'Atual'
                return {
                    'status_plano': {
                        'nivel': 'critico',
                        'tipo': 'assinatura_vencida',
                        'mensagem': f'Sua assinatura do plano {plano_nome} está {assinatura.get_status_display()}. Regularize agora sua situação.',
                        'cta_url': url_regularizar,
                        'cta_texto': 'Regularizar assinatura',
                        'icon': 'fas fa-exclamation-circle',
                    }
                }

        # --- SECUNDÁRIO: Em grace period por inadimplência ---
        if assinatura_em_graca_inadimplencia(assinatura):
            dias = dias_restantes_graca(assinatura)
            return {
                'status_plano': {
                    'nivel': 'aviso',
                    'tipo': 'graca_inadimplencia',
                    'mensagem': f'Seu pagamento falhou. Você tem {dias} dia{"s" if dias != 1 else ""} para regularizar antes de perder acesso.',
                    'cta_url': reverse('configuracao:gerenciar_assinatura') + '#secao-planos',
                    'cta_texto': 'Regularizar pagamento',
                    'icon': 'fas fa-exclamation-triangle',
                }
            }

        # --- SECUNDÁRIO: Trial ativo (contagem regressiva) ---
        if is_trial_ativo(assinatura):
            dias = dias_restantes_trial(assinatura)
            return {
                'status_plano': {
                    'nivel': 'atencao',
                    'tipo': 'trial_ativo',
                    'mensagem': f'Seu período de teste termina em {dias} dia{"s" if dias != 1 else ""}. Escolha um plano para continuar sem interrupções.',
                    'cta_url': reverse('configuracao:gerenciar_assinatura') + '#secao-planos',
                    'cta_texto': 'Escolher plano',
                    'icon': 'fas fa-flask',
                }
            }

        # --- SECUNDÁRIO: Limite atingido (100%) ---
        limite = obter_limite_pessoas_ativas(ministerio)
        if limite and limite > 0:
            total_ativos = contar_pessoas_ativas(ministerio)
            percentual = round((total_ativos / limite) * 100, 1)

            if total_ativos >= limite:
                return {
                    'status_plano': {
                        'nivel': 'aviso',
                        'tipo': 'limite_atingido',
                        'mensagem': f'Você atingiu o limite de {limite} pessoas ativas ({total_ativos}/{limite}). Não é possível cadastrar novos membros.',
                        'cta_url': reverse('configuracao:gerenciar_assinatura'),
                        'cta_texto': 'Fazer upgrade',
                        'percentual': percentual,
                        'restante': 0,
                        'icon': 'fas fa-ban',
                    }
                }

            # --- TERCIÁRIO: Limite próximo (80-99%) ---
            if percentual >= 80:
                restante = max(limite - total_ativos, 0)
                return {
                    'status_plano': {
                        'nivel': 'atencao',
                        'tipo': 'limite_proximo',
                        'mensagem': f'Você está usando {percentual}% do limite de pessoas ativas ({total_ativos}/{limite}). Restam {restante} vaga{"s" if restante != 1 else ""}.',
                        'cta_url': reverse('configuracao:gerenciar_assinatura'),
                        'cta_texto': 'Fazer upgrade',
                        'percentual': percentual,
                        'restante': restante,
                        'icon': 'fas fa-chart-line',
                    }
                }

        # --- Tudo OK ---
        return {'status_plano': None}

    except Exception as e:
        # Falha segura para não quebrar renderização
        logger.warning(f'Erro ao avaliar status_plano_unificado: {e}', exc_info=True)
        return {'status_plano': None}
