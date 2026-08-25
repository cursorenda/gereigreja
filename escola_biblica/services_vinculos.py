"""Busca segura de candidatos para vínculos entre EBD e Secretaria."""

from django.db.models import Case, IntegerField, Q, Value, When

from secretaria.models import Pessoa

from .models import CadastroAluno


def obter_pessoas_base_mesma_igreja(cadastro):
    return Pessoa.objects.filter(igreja_id=cadastro.igreja_id).select_related(
        'tipo_pessoa',
        'status_pessoa',
    )


def listar_candidatos_vinculo_secretaria(cadastro, *, busca='', limite=30):
    pessoas = obter_pessoas_base_mesma_igreja(cadastro)
    if busca:
        pessoas = pessoas.filter(nome__icontains=busca)
    else:
        primeiro_nome = ((cadastro.nome or '').strip().split() or [''])[0]
        if cadastro.data_nascimento and primeiro_nome:
            pessoas = pessoas.filter(
                Q(nascimento=cadastro.data_nascimento) | Q(nome__icontains=primeiro_nome),
            )
        elif cadastro.data_nascimento:
            pessoas = pessoas.filter(nascimento=cadastro.data_nascimento)
        elif primeiro_nome:
            pessoas = pessoas.filter(nome__icontains=primeiro_nome)

    return pessoas.annotate(
        prioridade_nome=Case(
            When(nome__iexact=cadastro.nome, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
        prioridade_data=Case(
            When(nascimento=cadastro.data_nascimento, then=Value(0)),
            default=Value(1),
            output_field=IntegerField(),
        ),
    ).order_by('prioridade_nome', 'prioridade_data', 'nome')[:limite]


def tentar_vinculos_em_lote(cadastros):
    """Tenta vincular cadastros elegíveis e retorna um resumo para a interface."""
    vinculados = 0
    sem_correspondencia = 0
    detalhes = []
    for cadastro in cadastros:
        pessoa = cadastro.tentar_vincular_pessoa(force=True)
        if pessoa is None:
            sem_correspondencia += 1
            continue
        cadastro.save()
        vinculados += 1
        nome_cadastro = (cadastro.nome or '').strip() or 'Sem nome'
        nome_pessoa = (pessoa.nome or '').strip()
        detalhes.append(
            f'{nome_cadastro} -> {nome_pessoa}'
            if nome_pessoa and nome_pessoa != nome_cadastro
            else nome_cadastro
        )
    return {
        'vinculados': vinculados,
        'sem_correspondencia': sem_correspondencia,
        'detalhes': detalhes,
    }


def aplicar_vinculos_selecionados_em_lote(
    *, cadastros, pessoa_ids_por_cadastro, buscar_pessoa=None,
):
    """Aplica apenas vinculos selecionados e pertencentes a igreja do cadastro."""
    buscar_pessoa = buscar_pessoa or (
        lambda pessoa_id, igreja_id: Pessoa.objects.filter(
            pk=pessoa_id,
            igreja_id=igreja_id,
        ).first()
    )
    vinculos_realizados = []
    for cadastro in cadastros:
        pessoa_id = pessoa_ids_por_cadastro.get(cadastro.id)
        if not pessoa_id:
            continue
        pessoa = buscar_pessoa(pessoa_id, cadastro.igreja_id)
        if pessoa is None:
            continue
        cadastro.pessoa = pessoa
        cadastro.save()
        vinculos_realizados.append(f'{cadastro.nome} -> {pessoa.nome}')
    return {
        'vinculos_realizados': vinculos_realizados,
        'total_vinculos': len(vinculos_realizados),
    }


def tentar_vinculos_listagem_alunos(alunos):
    """Executa o vinculo em lote somente para os cadastros exibidos na listagem."""
    cadastro_ids = alunos.values_list('cadastro_id', flat=True).distinct()
    cadastros_sem_vinculo = CadastroAluno.objects.filter(
        id__in=cadastro_ids,
        pessoa__isnull=True,
    )
    return tentar_vinculos_em_lote(cadastros_sem_vinculo)
