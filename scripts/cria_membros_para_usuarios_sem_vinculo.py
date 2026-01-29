from django.contrib.auth import get_user_model
from secretaria.models import Membro, Igreja, StatusPessoa, TipoPessoa
from django.db import transaction

User = get_user_model()
usuarios = User.objects.all()


# Busca status padrão "Ativo"
status_padrao = StatusPessoa.objects.filter(nome__iexact='Ativo').first()
if not status_padrao:
    print('Status padrão "Ativo" não encontrado! Corrija antes de rodar o script.')
    exit()

# Busca tipo_pessoa padrão "Membro"
tipo_padrao = TipoPessoa.objects.filter(nome__iexact='Membro').first()
if not tipo_padrao:
    print('TipoPessoa padrão "Membro" não encontrado! Corrija antes de rodar o script.')
    exit()

print('--- CRIAÇÃO AUTOMÁTICA DE MEMBROS PARA USUÁRIOS SEM VÍNCULO ---')
with transaction.atomic():
    for user in usuarios:
        membro = Membro.objects.filter(usuario=user).first()
        if membro:
            print(f'Usuário {user.username} já possui membro: {membro.nome}')
            continue
        # Tenta obter o ministério do usuário via PerfilUsuario
        perfil = getattr(user, 'perfil', None)
        ministerio = getattr(perfil, 'ministerio', None) if perfil else None
        igreja = None
        if ministerio:
            igrejas = Igreja.objects.filter(ministerio=ministerio).order_by('id')
            if igrejas.exists():
                igreja = igrejas.first()
        if not igreja:
            print(f'Não foi possível determinar igreja para usuário {user.username}. Ignorado.')
            continue
        nome = user.get_full_name() or user.username
        novo_membro = Membro(
            nome=nome,
            email=user.email,
            usuario=user,
            igreja=igreja,
            status_pessoa=status_padrao,
            tipo_pessoa=tipo_padrao
        )
        novo_membro.save()
        print(f'Criado membro para usuário {user.username}: {nome} | Igreja: {igreja.nome_igreja} | Tipo: {tipo_padrao.nome}')
print('--- FIM DA CRIAÇÃO ---')
