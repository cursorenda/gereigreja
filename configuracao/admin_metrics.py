"""
Métricas de produto/uso para desenvolvedores
Dashboard de análise do sistema no Admin Django
"""

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from notificacoes.models import Notificacao, NotificacaoEnviada


def _calcular_saude_admin(tickets_data, acessos_data, membros_data, financeiro_data, sistema_data):
    """Consolida um score simples de saude operacional do admin (0-100)."""
    score = 100
    checks = []

    backup_ok = bool(sistema_data.get('backup_ok'))
    checks.append({
        'item': 'Backup recente',
        'ok': backup_ok,
        'detalhe': 'OK' if backup_ok else 'Atrasado'
    })
    if not backup_ok:
        score -= 30

    tickets_pendentes = int(tickets_data.get('pendentes', 0) or 0)
    tickets_ok = tickets_pendentes <= 10
    checks.append({
        'item': 'Fila de tickets',
        'ok': tickets_ok,
        'detalhe': f'{tickets_pendentes} pendentes'
    })
    if tickets_pendentes > 20:
        score -= 20
    elif tickets_pendentes > 10:
        score -= 10

    bugs = int(tickets_data.get('bugs', 0) or 0)
    bugs_ok = bugs == 0
    checks.append({
        'item': 'Bugs abertos',
        'ok': bugs_ok,
        'detalhe': f'{bugs} bug(s)'
    })
    if bugs > 0:
        score -= 10

    retencao = float(acessos_data.get('taxa_retencao', 0) or 0)
    retencao_ok = retencao >= 70
    checks.append({
        'item': 'Retencao de usuarios (30d)',
        'ok': retencao_ok,
        'detalhe': f'{retencao}%'
    })
    if retencao < 50:
        score -= 20
    elif retencao < 70:
        score -= 10

    taxa_foto = float(membros_data.get('taxa_foto', 0) or 0)
    foto_ok = taxa_foto >= 50
    checks.append({
        'item': 'Qualidade cadastro (foto)',
        'ok': foto_ok,
        'detalhe': f'{taxa_foto}%'
    })
    if taxa_foto < 50:
        score -= 10

    taxa_comprovante = float(financeiro_data.get('taxa_comprovante', 0) or 0)
    comprovante_ok = taxa_comprovante >= 50
    checks.append({
        'item': 'Qualidade financeiro (comprovante)',
        'ok': comprovante_ok,
        'detalhe': f'{taxa_comprovante}%'
    })
    if taxa_comprovante < 50:
        score -= 10

    score = max(0, min(100, score))
    if score >= 80:
        status = 'ok'
    elif score >= 60:
        status = 'alerta'
    else:
        status = 'critico'

    return {
        'score': score,
        'status': status,
        'checks': checks,
    }


@staff_member_required
def metricas_produto(request):
    """API JSON com métricas de produto e uso do sistema"""
    
    # Imports dentro da função para evitar circular imports
    from secretaria.models import Pessoa
    from eventos.models import Evento, ParticipacaoEvento
    from financeiro.models import Receitas, Despesas
    from suporte.models import Ticket
    from django.contrib.auth.models import User
    from configuracao.models import Ministerio, Igreja
    import os
    import glob
    
    hoje = timezone.now()
    mes_atual = hoje.month
    ano_atual = hoje.year
    ultimos_30_dias = hoje - timedelta(days=30)
    ultimos_7_dias = hoje - timedelta(days=7)
    
    # ===== MEMBROS =====
    total_membros = Pessoa.objects.count()
    membros_ativos = Pessoa.objects.filter(
        Q(status_pessoa__nome='Ativo') | Q(status_pessoa__isnull=True)
    ).count()
    
    # Novos membros este mês
    try:
        novos_mes = Pessoa.objects.filter(
            created_at__month=mes_atual,
            created_at__year=ano_atual
        ).count()
    except:
        novos_mes = 0
    
    # Qualidade dos dados
    com_foto = Pessoa.objects.exclude(Q(foto='') | Q(foto__isnull=True)).count()
    com_telefone = Pessoa.objects.exclude(
        Q(telefone='') | Q(telefone__isnull=True) | Q(telefone='Sem telefone')
    ).count()
    
    membros_data = {
        'total': total_membros,
        'ativos': membros_ativos,
        'novos_mes': novos_mes,
        'taxa_ativos': round((membros_ativos / total_membros * 100) if total_membros > 0 else 0, 1),
        'com_foto': com_foto,
        'taxa_foto': round((com_foto / total_membros * 100) if total_membros > 0 else 0, 1),
        'com_telefone': com_telefone,
        'taxa_telefone': round((com_telefone / total_membros * 100) if total_membros > 0 else 0, 1)
    }
    
    # ===== EVENTOS =====
    total_eventos = Evento.objects.count()
    eventos_mes = Evento.objects.filter(
        data_inicio__month=mes_atual,
        data_inicio__year=ano_atual
    ).count()
    
    # Taxa de presença (eventos com participações)
    try:
        participacoes = ParticipacaoEvento.objects.all()
        total_participacoes = participacoes.count()
        participacoes_confirmadas = participacoes.filter(status='CONFIRMADO').count()
        taxa_presenca = round((participacoes_confirmadas / total_participacoes * 100) if total_participacoes > 0 else 0, 1)
        
        # Média de inscritos por evento
        eventos_com_participacao = participacoes.values('evento').distinct().count()
        media_inscritos = round(total_participacoes / eventos_com_participacao) if eventos_com_participacao > 0 else 0
    except:
        taxa_presenca = 0
        media_inscritos = 0
    
    eventos_data = {
        'total': total_eventos,
        'este_mes': eventos_mes,
        'media_inscritos': media_inscritos,
        'taxa_presenca': taxa_presenca
    }
    
    # ===== COMUNICAÇÃO =====
    try:
        emails_mes = NotificacaoEnviada.objects.filter(
            data_envio__month=mes_atual,
            data_envio__year=ano_atual
        ).count()
        
        # NotificacaoEnviada não tem campo de abertura, então taxa será 0
        taxa_abertura = 0
    except:
        emails_mes = 0
        taxa_abertura = 0
    
    try:
        notificacoes_mes = Notificacao.objects.filter(
            created_at__month=mes_atual,
            created_at__year=ano_atual
        ).count()
    except:
        notificacoes_mes = 0
    
    comunicacao_data = {
        'emails_mes': emails_mes,
        'taxa_abertura': taxa_abertura,
        'notificacoes_mes': notificacoes_mes
    }
    
    # ===== FINANCEIRO (apenas quantidades) =====
    try:
        lancamentos_mes = (
            Receitas.objects.filter(data__month=mes_atual, data__year=ano_atual).count() +
            Despesas.objects.filter(data__month=mes_atual, data__year=ano_atual).count()
        )
        
        # Qualidade: com comprovante
        try:
            receitas_com_comprov = Receitas.objects.filter(
                data__month=mes_atual,
                data__year=ano_atual
            ).exclude(Q(comprovante='') | Q(comprovante__isnull=True)).count()
            
            despesas_com_comprov = Despesas.objects.filter(
                data__month=mes_atual,
                data__year=ano_atual
            ).exclude(Q(comprovante='') | Q(comprovante__isnull=True)).count()
            
            com_comprovante = receitas_com_comprov + despesas_com_comprov
            taxa_comprovante = round((com_comprovante / lancamentos_mes * 100) if lancamentos_mes > 0 else 0, 1)
        except:
            taxa_comprovante = 0
    except:
        lancamentos_mes = 0
        taxa_comprovante = 0
    
    financeiro_data = {
        'lancamentos_mes': lancamentos_mes,
        'taxa_comprovante': taxa_comprovante
    }
    
    # ===== SUPORTE (TICKETS) =====
    try:
        total_tickets = Ticket.objects.count()
        tickets_abertos = Ticket.objects.filter(status='aberto').count()
        tickets_respondidos = Ticket.objects.filter(status__in=['respondido', 'resolvido', 'fechado']).count()
        tickets_pendentes = Ticket.objects.filter(
            Q(status='aberto') | Q(status='pendente')
        ).count()
        
        # Bugs reportados (se tiver campo categoria)
        try:
            bugs = Ticket.objects.filter(categoria__icontains='bug').count()
        except:
            bugs = 0
        
        # Tempo médio de resposta (em horas)
        try:
            tickets_com_resposta = Ticket.objects.filter(
                data_resposta__isnull=False
            )
            if tickets_com_resposta.exists():
                tempos = []
                for t in tickets_com_resposta:
                    delta = t.data_resposta - t.criado_em
                    tempos.append(delta.total_seconds() / 3600)
                tempo_medio = round(sum(tempos) / len(tempos), 1) if tempos else 0
            else:
                tempo_medio = 0
        except:
            tempo_medio = 0
        
        taxa_resposta = round((tickets_respondidos / total_tickets * 100) if total_tickets > 0 else 0, 1)
    except:
        total_tickets = 0
        tickets_respondidos = 0
        tickets_pendentes = 0
        bugs = 0
        tempo_medio = 0
        taxa_resposta = 0
    
    tickets_data = {
        'total': total_tickets,
        'respondidos': tickets_respondidos,
        'pendentes': tickets_pendentes,
        'bugs': bugs,
        'tempo_medio_horas': tempo_medio,
        'taxa_resposta': taxa_resposta
    }
    
    # ===== ACESSOS/ENGAGEMENT =====
    try:
        total_usuarios = User.objects.count()
        
        # Usuários ativos (com login nos últimos 7/30 dias)
        usuarios_7d = User.objects.filter(last_login__gte=ultimos_7_dias).count()
        usuarios_30d = User.objects.filter(last_login__gte=ultimos_30_dias).count()
        
        taxa_retencao = round((usuarios_30d / total_usuarios * 100) if total_usuarios > 0 else 0, 1)
        
        # Logins hoje (aproximado por last_login)
        logins_hoje = User.objects.filter(
            last_login__date=hoje.date()
        ).count()
    except:
        total_usuarios = 0
        usuarios_7d = 0
        usuarios_30d = 0
        taxa_retencao = 0
        logins_hoje = 0
    
    acessos_data = {
        'total_usuarios': total_usuarios,
        'usuarios_7d': usuarios_7d,
        'usuarios_30d': usuarios_30d,
        'taxa_retencao': taxa_retencao,
        'logins_hoje': logins_hoje
    }
    
    # ===== CRESCIMENTO (últimos 6 meses) =====
    crescimento_membros = []
    for i in range(5, -1, -1):
        mes = (hoje - timedelta(days=30*i)).month
        ano = (hoje - timedelta(days=30*i)).year
        try:
            count = Pessoa.objects.filter(
                created_at__month=mes,
                created_at__year=ano
            ).count()
        except:
            count = 0
        crescimento_membros.append({
            'mes': f"{mes}/{ano}",
            'count': count
        })
    
    # ===== MINISTÉRIOS (CLIENTES DO SISTEMA) =====
    try:
        total_ministerios = Ministerio.objects.count()
        ministerios_ativos = Ministerio.objects.filter(ativo=True).count()
        ministerios_inativos = Ministerio.objects.filter(ativo=False).count()
        
        # Novos ministérios este mês
        novos_ministerios_mes = Ministerio.objects.filter(
            data_criacao__month=mes_atual,
            data_criacao__year=ano_atual
        ).count()
        
        # Total de igrejas cadastradas
        total_igrejas = Igreja.objects.count()
        
        # Ministérios que não acessam há 30+ dias (simplificado)
        # Conta usuários com último login > 30 dias atrás
        usuarios_inativos_30d = User.objects.filter(
            last_login__lt=ultimos_30_dias
        ).values_list('perfil__ministerio', flat=True).distinct()
        ministerios_inativos_30d = len([m for m in usuarios_inativos_30d if m])
        
        # Distribuição por tamanho (pequeno < 50, médio 50-200, grande > 200)
        # Usa anotação para ser mais eficiente
        from django.db.models import Count
        ministerios_com_contagem = Ministerio.objects.annotate(
            num_membros=Count('igrejas__membros')
        )
        
        ministerios_pequenos = ministerios_com_contagem.filter(num_membros__lt=50).count()
        ministerios_medios = ministerios_com_contagem.filter(num_membros__gte=50, num_membros__lte=200).count()
        ministerios_grandes = ministerios_com_contagem.filter(num_membros__gt=200).count()
        
    except Exception as e:
        print(f"Erro em métricas de ministérios: {e}")
        total_ministerios = 0
        ministerios_ativos = 0
        ministerios_inativos = 0
        novos_ministerios_mes = 0
        total_igrejas = 0
        ministerios_inativos_30d = 0
        ministerios_pequenos = 0
        ministerios_medios = 0
        ministerios_grandes = 0
    
    ministerios_data = {
        'total': total_ministerios,
        'ativos': ministerios_ativos,
        'inativos': ministerios_inativos,
        'novos_mes': novos_ministerios_mes,
        'total_igrejas': total_igrejas,
        'sem_acesso_30d': ministerios_inativos_30d,
        'pequenos': ministerios_pequenos,
        'medios': ministerios_medios,
        'grandes': ministerios_grandes
    }
    
    # ===== STATUS DO SISTEMA (BACKUP & HEALTH) =====
    try:
        from django.conf import settings
        from deploy.models import BackupHistorico

        # Fonte de verdade: ultimo backup persistido no banco
        ultimo_backup_db = BackupHistorico.objects.order_by('-criado_em').first()
        if ultimo_backup_db:
            ultimo_backup_data = ultimo_backup_db.criado_em
            dias_desde_backup = (hoje - ultimo_backup_data).days
            backup_ok = dias_desde_backup <= 1
        else:
            # Fallback por arquivo para ambientes legados
            # Verificar último backup na pasta backup/ (todos os tipos: json, dump, sql, zip)
            base_dir = settings.BASE_DIR
            backup_dir = base_dir / 'backup'
            backup_files = []
            for ext in ('*.json', '*.dump', '*.sql', '*.zip'):
                backup_files.extend(glob.glob(str(backup_dir / ext)))
            # Remove arquivos de log e não-backup
            backup_files = [f for f in backup_files if os.path.basename(f).startswith('backup')]
            
            if backup_files:
                ultimo_backup = max(backup_files, key=os.path.getmtime)
                ultimo_backup_data = datetime.fromtimestamp(os.path.getmtime(ultimo_backup))
                ultimo_backup_data = timezone.make_aware(ultimo_backup_data)
                dias_desde_backup = (hoje - ultimo_backup_data).days
                backup_ok = dias_desde_backup <= 1
            else:
                # Fallback: checar backup_log.txt
                backup_log = base_dir / 'backup' / 'backup_log.txt'
                if not backup_log.exists():
                    backup_log = base_dir / 'backup_log.txt'
                if backup_log.exists():
                    linhas = backup_log.read_text(encoding='utf-8', errors='ignore').strip().splitlines()
                    ultima_linha = next((l for l in reversed(linhas) if l.strip()), None)
                    if ultima_linha:
                        try:
                            ts_str = ultima_linha.split(' ')[0]  # formato: 20260511_105227
                            ultimo_backup_data = datetime.strptime(ts_str, '%Y%m%d_%H%M%S')
                            ultimo_backup_data = timezone.make_aware(ultimo_backup_data)
                            dias_desde_backup = (hoje - ultimo_backup_data).days
                            backup_ok = dias_desde_backup <= 1
                        except Exception:
                            ultimo_backup_data = None
                            dias_desde_backup = 999
                            backup_ok = False
                    else:
                        ultimo_backup_data = None
                        dias_desde_backup = 999
                        backup_ok = False
                else:
                    ultimo_backup_data = None
                    dias_desde_backup = 999
                    backup_ok = False
        
        # Verificar erros recentes (últimas 24h) - simulado
        # Em produção, você pode integrar com sistema de logs
        erros_24h = 0
        
        # Storage usado (aproximado)
        try:
            media_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                           for dirpath, dirnames, filenames in os.walk(settings.MEDIA_ROOT)
                           for filename in filenames) / (1024**3)  # GB
            storage_usado = round(media_size, 2)
        except:
            storage_usado = 0
        
    except Exception as e:
        ultimo_backup_data = None
        dias_desde_backup = 999
        backup_ok = False
        erros_24h = 0
        storage_usado = 0
    
    sistema_data = {
        'ultimo_backup': ultimo_backup_data.isoformat() if ultimo_backup_data else None,
        'dias_desde_backup': dias_desde_backup,
        'backup_ok': backup_ok,
        'erros_24h': erros_24h,
        'storage_gb': storage_usado
    }
    
    admin_hub_data = _calcular_saude_admin(
        tickets_data=tickets_data,
        acessos_data=acessos_data,
        membros_data=membros_data,
        financeiro_data=financeiro_data,
        sistema_data=sistema_data,
    )

    return JsonResponse({
        'membros': membros_data,
        'eventos': eventos_data,
        'comunicacao': comunicacao_data,
        'financeiro': financeiro_data,
        'tickets': tickets_data,
        'acessos': acessos_data,
        'crescimento': crescimento_membros,
        'ministerios': ministerios_data,
        'sistema': sistema_data,
        'admin_hub': admin_hub_data,
        'timestamp': timezone.now().isoformat()
    })
