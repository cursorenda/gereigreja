from django.db import transaction
from .models import Despesas, CategoriaDespesa


def fix_despesas_categories():
    """
    Atualiza a tabela Despesas para converter os valores antigos de texto em ForeignKey
    para a tabela CategoriaDespesa.
    """
    with transaction.atomic():
        # Criar um dicionario para as categorias
        categorias = {
        'aluguel': 'Aluguel',
        'agua': 'Água',
        'luz': 'Luz',
        'telefone': 'Telefone',
        'internet': 'Internet',
        'combustivel': 'Combustível',
        'manutencao': 'Manutenção',
        'material_limpeza': 'Material de Limpeza',
        'material_escritorio': 'Material de Escritório',
        'gratificacao': 'Gratificação',
        'inss': 'INSS',
        'outros': 'Outros',
         }
        # Criar as categorias
        for key, value in categorias.items():
          CategoriaDespesa.objects.get_or_create(nome=value)

        # Iterar sobre todas as despesas que ainda não foram corrigidas
        for despesa in Despesas.objects.all():
            # Pega a categoria pelo nome
            nome_categoria = despesa.categoria
            if nome_categoria:
                categoria_obj = CategoriaDespesa.objects.get(nome=nome_categoria)
                # Atualiza a categoria_id na Despesa
                despesa.categoria = categoria_obj
                despesa.save()
