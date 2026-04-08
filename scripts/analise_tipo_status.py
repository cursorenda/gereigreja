import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from secretaria.models import Membro
from django.db.models import Count

print('=' * 70)
print('ANÁLISE: Combinações de Tipo de Pessoa x Status no Banco de Dados')
print('=' * 70)

combos = Membro.objects.values('tipo_pessoa__nome', 'status_pessoa__nome').annotate(count=Count('id')).order_by('tipo_pessoa__nome', 'status_pessoa__nome')

for combo in combos:
    tipo = combo['tipo_pessoa__nome'] or 'Sem tipo'
    status = combo['status_pessoa__nome'] or 'Sem status'
    qtd = combo['count']
    print(f'{tipo:20} + {status:20} = {qtd:3} pessoas')

print('\n' + '=' * 70)
print('ANÁLISE POR TIPO:')
print('=' * 70)

tipos = ['Congregado', 'Membro', 'Novo Convertido', 'Obreiro', 'Visitante']
status_lista = ['Ativo', 'Inativo', 'Desligado', 'Em Disciplina']

for tipo in tipos:
    print(f'\n{tipo}:')
    for status in status_lista:
        count = Membro.objects.filter(tipo_pessoa__nome=tipo, status_pessoa__nome=status).count()
        if count > 0:
            print(f'  • {status}: {count} pessoa(s)')
