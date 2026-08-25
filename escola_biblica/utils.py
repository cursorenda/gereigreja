# Utilitários para Escola Bíblica Dominical
import datetime
from dateutil.relativedelta import relativedelta

def calcular_frequencia_aluno(aluno):
    total = aluno.frequencia_set.count()
    presentes = aluno.frequencia_set.filter(presente=True).count()
    return {'total': total, 'presentes': presentes, 'percentual': (presentes/total*100) if total else 0}

def gerar_periodos_ebd(ano, tipo_periodo):
    """
    Gera uma lista de períodos (trimestre, quadrimestre, semestre, ano) para o ano informado.
    Retorna lista de dicts: {numero, data_inicio, data_fim}
    """
    periodos = []
    if tipo_periodo == 'trimestre':
        meses_por_periodo = 3
        total = 4
    elif tipo_periodo == 'quadrimestre':
        meses_por_periodo = 4
        total = 3
    elif tipo_periodo == 'semestre':
        meses_por_periodo = 6
        total = 2
    elif tipo_periodo == 'ano':
        meses_por_periodo = 12
        total = 1
    else:
        raise ValueError('Tipo de período inválido')

    for i in range(total):
        mes_inicio = 1 + i * meses_por_periodo
        data_inicio = datetime.date(ano, mes_inicio, 1)
        # Calcula último dia do período
        mes_fim = mes_inicio + meses_por_periodo - 1
        if mes_fim > 12:
            mes_fim = 12
        # Último dia do mês final
        ultimo_dia = (datetime.date(ano, mes_fim, 1) + relativedelta(months=1) - datetime.timedelta(days=1)).day
        data_fim = datetime.date(ano, mes_fim, ultimo_dia)
        periodos.append({
            'numero': i + 1,
            'data_inicio': data_inicio,
            'data_fim': data_fim
        })
    return periodos


def gerar_domingos_periodo(data_inicio, data_fim):
    """
    Retorna lista de datas de todos os domingos entre data_inicio e data_fim (inclusive).
    """
    return gerar_datas_semana_periodo(data_inicio, data_fim, dia_semana=6)


def gerar_datas_semana_periodo(data_inicio, data_fim, dia_semana=6):
    """
    Retorna lista de datas de um dia da semana entre data_inicio e data_fim (inclusive).

    dia_semana segue padrão do Python:
    0=segunda ... 6=domingo.
    """
    if dia_semana is None or dia_semana < 0 or dia_semana > 6:
        dia_semana = 6

    datas = []
    atual = data_inicio
    while atual.weekday() != dia_semana:
        atual += datetime.timedelta(days=1)
    while atual <= data_fim:
        datas.append(atual)
        atual += datetime.timedelta(days=7)
    return datas


# Função para gerar lições para todos os domingos de todos os períodos e turmas
def gerar_licoes_periodos(ano, tipo_periodo, turmas, material='', observacoes='', horario=None, status='ativa'):
    """
    Gera lições para cada domingo de cada período do ano, para cada turma ativa.
    Retorna lista de dicts com dados das lições (não salva no banco).
    """
    periodos = gerar_periodos_ebd(ano, tipo_periodo)
    licoes = []
    for periodo in periodos:
        domingos = gerar_domingos_periodo(periodo['data_inicio'], periodo['data_fim'])
        for turma in turmas:
            professor = turma.get_professor_ebd() if hasattr(turma, 'get_professor_ebd') else None
            for idx, domingo in enumerate(domingos, start=1):
                licoes.append({
                    'turma': turma,
                    'data': domingo,
                    'tema': f'Lição {idx} - {periodo["numero"]}º {tipo_periodo.capitalize()} {ano}',
                    'material': material,
                    'observacoes': observacoes,
                    'horario': horario,
                    'status': status,
                    'professor': professor,
                    'periodo_numero': periodo['numero'],
                    'periodo_tipo': tipo_periodo,
                    'ano': ano,
                })
    return licoes

def is_professor_ebd(membro):
    """
    Retorna True se o membro possui cargo ativo de EBD com nome contendo 'professor'.
    """
    from secretaria.models import MembroCargo
    return MembroCargo.objects.filter(
        membro=membro,
        cargo__is_ebd=True,
        cargo__nome__icontains='professor',
        data_fim__isnull=True
    ).exists()


def get_faixa_semana_anterior(data_base=None):
    base = data_base or datetime.date.today()
    fim = base - datetime.timedelta(days=base.weekday() + 1)
    inicio = fim - datetime.timedelta(days=6)
    return inicio, fim


def build_resumo_semanal_ebd(
    ministerio, data_inicio, data_fim, *, igrejas=None, ano_letivo=None,
):
    """Monta o resumo semanal, opcionalmente limitado ao escopo exibido."""
    from django.db.models import Q, Sum

    from .models import Aluno, Frequencia, OfertaClasse, Turma

    turmas_qs = Turma.objects.filter(igreja__ministerio=ministerio)
    if igrejas is not None:
        turmas_qs = turmas_qs.filter(igreja__in=igrejas)
    if ano_letivo is not None:
        turmas_qs = turmas_qs.filter(ano_letivo=ano_letivo)
    turmas_qs = turmas_qs.distinct()
    turmas_ids = list(turmas_qs.values_list('id', flat=True))
    turmas_previstas = len(turmas_ids)

    frequencias_qs = Frequencia.objects.filter(
        aluno__turma_id__in=turmas_ids,
        data__gte=data_inicio,
        data__lte=data_fim,
    )

    chamadas_total = frequencias_qs.count()
    presencas_total = frequencias_qs.filter(presente=True).count()
    frequencia_media = round((presencas_total / chamadas_total) * 100, 1) if chamadas_total else 0.0

    turmas_com_chamada = frequencias_qs.values_list('aluno__turma_id', flat=True).distinct().count()
    turmas_sem_chamada = max(turmas_previstas - turmas_com_chamada, 0)

    ofertas_qs = OfertaClasse.objects.filter(
        data__gte=data_inicio,
        data__lte=data_fim,
    ).filter(
        Q(turma__in=turmas_qs)
        | Q(turma__isnull=True, classe__igreja__ministerio=ministerio)
    )
    if igrejas is not None:
        ofertas_qs = ofertas_qs.filter(
            Q(turma__in=turmas_qs)
            | Q(turma__isnull=True, classe__igreja__in=igrejas)
        )
    total_ofertas = float(ofertas_qs.aggregate(total=Sum('valor'))['total'] or 0)

    alunos_novos = Aluno.objects.filter(
        turma__in=turmas_qs,
        created_at__date__gte=data_inicio,
        created_at__date__lte=data_fim,
    ).count()

    recomendacoes = []
    if turmas_sem_chamada > 0:
        recomendacoes.append(
            f'Priorizar fechamento de chamada em {turmas_sem_chamada} turma(s) pendente(s).'
        )
    if frequencia_media < 70:
        recomendacoes.append('Frequência média abaixo de 70%. Planejar ação de recuperação com professores.')
    if total_ofertas <= 0:
        recomendacoes.append('Sem registro de ofertas no período. Validar lançamentos das turmas/classe.')
    if not recomendacoes:
        recomendacoes.append('Operação estável na semana. Manter rotina de acompanhamento e fechamento.')

    return {
        'ministerio_id': ministerio.id,
        'ministerio_nome': ministerio.nome_fantasia,
        'inicio': data_inicio,
        'fim': data_fim,
        'turmas_previstas': turmas_previstas,
        'turmas_com_chamada': turmas_com_chamada,
        'turmas_sem_chamada': turmas_sem_chamada,
        'chamadas_total': chamadas_total,
        'presencas_total': presencas_total,
        'frequencia_media': frequencia_media,
        'total_ofertas': total_ofertas,
        'alunos_novos': alunos_novos,
        'recomendacoes': recomendacoes,
    }


def formatar_resumo_semanal_ebd(resumo):
    linhas = [
        f"Período: {resumo['inicio'].strftime('%d/%m/%Y')} a {resumo['fim'].strftime('%d/%m/%Y')}",
        f"Turmas com chamada: {resumo['turmas_com_chamada']}/{resumo['turmas_previstas']}",
        f"Turmas pendentes: {resumo['turmas_sem_chamada']}",
        f"Frequência média: {resumo['frequencia_media']:.1f}%",
        f"Total de ofertas: R$ {resumo['total_ofertas']:.2f}",
        f"Novos alunos: {resumo['alunos_novos']}",
        '',
        'Recomendações da semana:',
    ]
    for idx, rec in enumerate(resumo['recomendacoes'], start=1):
        linhas.append(f'{idx}. {rec}')
    return '\n'.join(linhas)
