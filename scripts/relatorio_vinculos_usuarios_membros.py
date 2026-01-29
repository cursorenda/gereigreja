from django.contrib.auth import get_user_model
from secretaria.models import Membro

User = get_user_model()
usuarios = User.objects.all()

print('USUÁRIO	EMAIL	VÍNCULO	IGREJA')
for user in usuarios:
    membro = Membro.objects.filter(usuario=user).first()
    if membro:
        igreja = getattr(membro.igreja, 'nome_igreja', '---') if hasattr(membro, 'igreja') else '---'
        print(f'{user.username}\t{user.email}\tVINCULADO: {membro.nome}\t{igreja}')
    else:
        print(f'{user.username}\t{user.email}\tNÃO VINCULADO\t---')
