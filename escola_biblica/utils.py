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
    domingos = []
    atual = data_inicio
    # Avança até o primeiro domingo
    while atual.weekday() != 6:
        atual += datetime.timedelta(days=1)
    while atual <= data_fim:
        domingos.append(atual)
        atual += datetime.timedelta(days=7)
    return domingos


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
            professor = turma.get_professor_nome() if hasattr(turma, 'get_professor_nome') else ''
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
