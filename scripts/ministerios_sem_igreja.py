from django.contrib.auth import get_user_model
from secretaria.models import Igreja

User = get_user_model()
usuarios = User.objects.all()
ministerios_sem_igreja = set()
for user in usuarios:
    perfil = getattr(user, 'perfil', None)
    ministerio = getattr(perfil, 'ministerio', None) if perfil else None
    if ministerio:
        igrejas = Igreja.objects.filter(ministerio=ministerio)
        if not igrejas.exists():
            ministerios_sem_igreja.add(str(ministerio))

print('MINISTÉRIOS SEM IGREJA:')
for m in sorted(ministerios_sem_igreja):
    print(m)
