from django.contrib.auth import get_user_model
from secretaria.models import Pessoa

User = get_user_model()
count = 0
sem_match = []

for u in User.objects.filter(membro_secretaria__isnull=True):
    m = Pessoa.objects.filter(email=u.email).first()
    if m:
        m.usuario = u
        m.save()
        count += 1
        print(f'Vinculado: {u.username} -> {m.nome}')
    else:
        sem_match.append(f'{u.username} | {u.email}')

print(f'Total de vínculos criados: {count}')
if sem_match:
    print('Usuários sem match de e-mail para Pessoa:')
    for s in sem_match:
        print('-', s)
