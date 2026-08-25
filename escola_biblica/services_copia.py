"""Regras de copia anual de dados da Escola Biblica."""

from .models import Aluno, Classe, Turma


def obter_ou_criar_classe_destino(*, classe_origem):
    """Retorna a classe equivalente na igreja, criando-a quando necessário."""
    classe_destino, criada = Classe.objects.get_or_create(
        nome=classe_origem.nome,
        igreja=classe_origem.igreja,
        defaults={
            'departamento': classe_origem.departamento,
            'faixa_etaria': classe_origem.faixa_etaria,
            'descricao': classe_origem.descricao,
        },
    )
    return classe_destino, criada


def obter_ou_criar_turma_destino(*, turma_origem, ano_letivo_destino):
    """Retorna a turma correspondente no ano destino, sem cruzar igrejas."""
    igreja = turma_origem.igreja or turma_origem.classe.igreja
    turma_destino, criada = Turma.objects.get_or_create(
        nome=turma_origem.nome,
        igreja=igreja,
        ano_letivo=ano_letivo_destino,
        defaults={'classe': turma_origem.classe},
    )
    return turma_destino, criada


def obter_turma_destino(*, turma_origem, ano_letivo_destino):
    """Localiza a turma equivalente no destino sem criar novos registros."""
    igreja = turma_origem.igreja or turma_origem.classe.igreja
    return Turma.objects.filter(
        nome=turma_origem.nome,
        igreja=igreja,
        ano_letivo=ano_letivo_destino,
    ).first()


def copiar_turmas_para_ano(*, turmas_origem, ano_letivo_destino, incluir_membros=False):
    """Cria ou reutiliza turmas no ano destino e opcionalmente replica a equipe."""
    if hasattr(turmas_origem, 'select_related'):
        turmas_origem = turmas_origem.select_related(
            'igreja',
            'classe',
            'classe__igreja',
        )
        if incluir_membros:
            turmas_origem = turmas_origem.prefetch_related('membros')

    resultado = {
        'turmas_criadas': 0,
        'membros_copiados': 0,
        'turmas_destino_por_origem_id': {},
    }
    for turma_origem in turmas_origem:
        turma_destino, criada = obter_ou_criar_turma_destino(
            turma_origem=turma_origem,
            ano_letivo_destino=ano_letivo_destino,
        )
        resultado['turmas_destino_por_origem_id'][turma_origem.id] = turma_destino
        if criada:
            resultado['turmas_criadas'] += 1

        if not incluir_membros:
            continue

        membros_existentes_ids = set(turma_destino.membros.values_list('pk', flat=True))
        for membro in turma_origem.membros.all():
            if membro.pk in membros_existentes_ids:
                continue
            turma_destino.membros.add(membro)
            membros_existentes_ids.add(membro.pk)
            resultado['membros_copiados'] += 1

    return resultado


def copiar_ano_anterior_completo(*, turmas_origem, ano_letivo_destino):
    """Replica classes, turmas e alunos ativos para o ano letivo de destino."""
    classes_origem = Classe.objects.filter(turma__in=turmas_origem).distinct()
    for classe in classes_origem:
        obter_ou_criar_classe_destino(classe_origem=classe)

    copia_turmas = copiar_turmas_para_ano(
        turmas_origem=turmas_origem,
        ano_letivo_destino=ano_letivo_destino,
    )
    alunos_copiados = 0
    for turma_origem in turmas_origem:
        turma_destino = copia_turmas['turmas_destino_por_origem_id'][turma_origem.id]
        for aluno in turma_origem.alunos.filter(ativo=True):
            alunos_copiados += int(copiar_aluno_para_turma(
                aluno=aluno,
                turma_destino=turma_destino,
            ))

    return {
        'turmas_criadas': copia_turmas['turmas_criadas'],
        'alunos_copiados': alunos_copiados,
    }


def copiar_dados_selecionados_para_ano(
    *, turmas_origem, classes_origem, alunos_origem, turmas_ids, classes_ids,
    alunos_ids, ano_letivo_destino,
):
    """Replica apenas os dados selecionados para o ano letivo de destino."""
    classes_criadas = 0
    for classe in classes_origem.filter(id__in=classes_ids):
        _, criada = obter_ou_criar_classe_destino(classe_origem=classe)
        classes_criadas += int(criada)

    copia_turmas = copiar_turmas_para_ano(
        turmas_origem=turmas_origem.filter(id__in=turmas_ids),
        ano_letivo_destino=ano_letivo_destino,
        incluir_membros=True,
    )
    alunos_copiados = 0
    for aluno in alunos_origem.filter(id__in=alunos_ids):
        turma_destino = (
            copia_turmas['turmas_destino_por_origem_id'].get(aluno.turma_id)
            or obter_turma_destino(
                turma_origem=aluno.turma,
                ano_letivo_destino=ano_letivo_destino,
            )
        )
        if turma_destino is not None:
            alunos_copiados += int(copiar_aluno_para_turma(
                aluno=aluno,
                turma_destino=turma_destino,
            ))

    return {
        'classes_criadas': classes_criadas,
        'turmas_criadas': copia_turmas['turmas_criadas'],
        'membros_copiados': copia_turmas['membros_copiados'],
        'alunos_copiados': alunos_copiados,
        'turmas_destino': list(copia_turmas['turmas_destino_por_origem_id'].values()),
    }


def consolidar_resultado_copia_seletiva(*, resultado_copia, licoes_geradas):
    """Padroniza os dados de retorno e auditoria da copia seletiva anual."""
    resultado = {
        'classes_criadas': resultado_copia['classes_criadas'],
        'turmas_criadas': resultado_copia['turmas_criadas'],
        'membros_copiados': resultado_copia['membros_copiados'],
        'alunos_copiados': resultado_copia['alunos_copiados'],
        'licoes_geradas': licoes_geradas,
    }
    resultado['tem_novidades'] = any(resultado.values())
    return resultado


def copiar_aluno_para_turma(*, aluno, turma_destino):
    """Matricula o mesmo cadastro na turma de destino sem duplicar registros."""
    if Aluno.objects.filter(cadastro=aluno.cadastro, turma=turma_destino).exists():
        return False

    Aluno.objects.create(
        cadastro=aluno.cadastro,
        nome=aluno.nome,
        data_nascimento=aluno.data_nascimento,
        turma=turma_destino,
        responsavel=aluno.responsavel,
        telefone_responsavel=aluno.telefone_responsavel,
        observacoes=aluno.observacoes,
        ativo=True,
    )
    return True
