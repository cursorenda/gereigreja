from django.contrib.auth import get_user_model
from secretaria.models import Membro, MembroCargo
from escola_biblica.utils import is_professor_ebd

User = get_user_model()
usuarios = User.objects.all()
print('--- AUDITORIA DE VÍNCULOS USUÁRIO <-> MEMBRO E CARGOS ATIVOS ---')
for user in usuarios:
    membro = Membro.objects.filter(usuario=user).first()
    if not membro:
        print(f'Usuário: {user.username} | NOME: {user.get_full_name()} | NÃO VINCULADO a membro')
    else:
        cargos_ativos = MembroCargo.objects.filter(membro=membro, data_fim__isnull=True)
        cargos_nomes = [mc.cargo.nome for mc in cargos_ativos]
        eh_professor = is_professor_ebd(membro)
        print(f'Usuário: {user.username} | Membro: {membro.nome} | Cargos Ativos: {cargos_nomes if cargos_nomes else "Nenhum"} | Professor EBD: {eh_professor}')

print('--- FIM DA AUDITORIA ---')
