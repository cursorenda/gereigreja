from django.contrib.auth import get_user_model
from secretaria.models import Membro

# Substitua pelo email correto da Maryellen
EMAIL_MARYELLEN = 'maryellenbarbosa16@gmail.com'

User = get_user_model()
user = User.objects.filter(email=EMAIL_MARYELLEN).first()
if not user:
    print(f'Usuário com email {EMAIL_MARYELLEN} não encontrado.')
else:
    membro = Membro.objects.filter(nome__icontains='Maryellen').first()
    if not membro:
        print('Membro Maryellen não encontrado.')
    else:
        membro.usuario = user
        membro.save()
        print(f'Vinculado membro {membro.nome} ao usuário {user.username}.')
