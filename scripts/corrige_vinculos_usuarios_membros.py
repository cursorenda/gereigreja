from django.contrib.auth import get_user_model
from secretaria.models import Membro

User = get_user_model()
usuarios = User.objects.all()
print('--- CORREÇÃO AUTOMÁTICA DE VÍNCULOS USUÁRIO <-> MEMBRO POR EMAIL ---')
for user in usuarios:
    if not user.email:
        print(f'Usuário: {user.username} não possui email. Ignorado.')
        continue
    membro = Membro.objects.filter(usuario=user).first()
    if membro:
        print(f'Usuário: {user.username} já está vinculado ao membro: {membro.nome}')
        continue
    membro_email = Membro.objects.filter(email__iexact=user.email).first()
    if membro_email:
        membro_email.usuario = user
        membro_email.save()
        print(f'VINCULADO: Usuário {user.username} ao membro {membro_email.nome} (email: {user.email})')
    else:
        print(f'Usuário: {user.username} (email: {user.email}) não possui membro correspondente para vincular.')
print('--- FIM DA CORREÇÃO ---')
